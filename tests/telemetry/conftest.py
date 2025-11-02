"""
pytest fixtures for telemetry testing.

Provides infrastructure for capturing and validating OpenTelemetry spans and metrics
during authorization operations in test environments.
"""

import json
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExporter, SpanExportResult
from opentelemetry.trace import Span, StatusCode


@dataclass
class CapturedSpan:
    """Captured span data for testing."""

    name: str
    attributes: Dict[str, Any]
    status: str
    status_message: Optional[str]
    duration_ms: float
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    start_time_ns: int = 0
    end_time_ns: int = 0


@dataclass
class TelemetryCapture:
    """Container for captured telemetry data."""

    spans: List[CapturedSpan] = field(default_factory=list)
    metrics: List[Dict[str, Any]] = field(default_factory=list)

    def get_spans_by_name(self, name: str) -> List[CapturedSpan]:
        """Get all spans with the given name."""
        return [span for span in self.spans if span.name == name]

    def get_authz_spans(self) -> List[CapturedSpan]:
        """Get all authorization spans."""
        return self.get_spans_by_name("authz.check")

    def has_span(self, name: str) -> bool:
        """Check if any span with the given name exists."""
        return len(self.get_spans_by_name(name)) > 0


class InMemorySpanExporter(SpanExporter):
    """In-memory span exporter for testing."""

    def __init__(self, capture: TelemetryCapture):
        self.capture = capture

    def export(self, spans: List[Span]) -> SpanExportResult:
        """Export spans to in-memory storage."""
        for span in spans:
            # Convert span to our test format
            attributes = dict(span.attributes) if span.attributes else {}

            # Calculate duration
            duration_ms = 0.0
            if span.end_time and span.start_time:
                duration_ms = (span.end_time - span.start_time) / 1_000_000  # Convert ns to ms

            # Extract status
            status_str = "OK"
            status_message = None
            if span.status:
                if span.status.status_code == StatusCode.ERROR:
                    status_str = "ERROR"
                elif span.status.status_code == StatusCode.UNSET:
                    status_str = "UNSET"
                status_message = span.status.description

            captured_span = CapturedSpan(
                name=span.name,
                attributes=attributes,
                status=status_str,
                status_message=status_message,
                duration_ms=duration_ms,
                trace_id=format(span.context.trace_id, "032x") if span.context else "",
                span_id=format(span.context.span_id, "016x") if span.context else "",
                parent_span_id=format(span.parent.span_id, "016x") if span.parent else None,
                start_time_ns=span.start_time or 0,
                end_time_ns=span.end_time or 0,
            )

            self.capture.spans.append(captured_span)

        return SpanExportResult.SUCCESS

    def shutdown(self) -> None:
        """Shutdown the exporter."""
        pass


@pytest.fixture
def telemetry_capture():
    """Fixture that captures telemetry data for testing."""
    capture = TelemetryCapture()

    # Set up OpenTelemetry with in-memory exporter
    resource = Resource.create({"service.name": "lukhas-test"})
    tracer_provider = TracerProvider(resource=resource)

    # Add our in-memory exporter
    span_exporter = InMemorySpanExporter(capture)
    span_processor = SimpleSpanProcessor(span_exporter)
    tracer_provider.add_span_processor(span_processor)

    # Set as current tracer provider
    original_provider = trace.get_tracer_provider()
    trace.set_tracer_provider(tracer_provider)

    yield capture

    # Restore original tracer provider
    trace.set_tracer_provider(original_provider)


@pytest.fixture
def mock_capability_token():
    """Mock capability token for testing."""
    return "eyJ2ZXJzaW9uIjoyLCJsb2NhdGlvbiI6Imx1a2hhcy1tYXRyaXgtYXV0aHoiLCJpZGVudGlmaWVyIjoibHVraGFzOnVzZXI6dGVzdDp0cnVzdGVkOjE3NTg4OTIyNjEiLCJjYXZlYXRzIjpbInN1YiA9IGx1a2hhczp1c2VyOnRlc3QiLCJ0aWVyID0gdHJ1c3RlZCIsInRpZXJfbnVtID0gMyIsInNjb3BlcyA9IG1lbW9yaWEucmVhZCxtZW1vcmlhLnN0b3JlIiwiYXVkID0gbHVraGFzLW1hdHJpeCIsImV4cCA9IDE3NTg4OTQwNjEiLCJpYXQgPSAxNzU4ODkyMjYxIiwibWZhID0gRmFsc2UiLCJ3ZWJhdXRobl92ZXJpZmllZCA9IFRydWUiXSwic2lnbmF0dXJlIjoiZGVhZGJlZWZjYWZlYmFiZTEyMzQ1Njc4OTBhYmNkZWZiZWVmZmVlZGNhZmVkZWFkYmVlZjEyMzQ1Njc4In0="


@pytest.fixture
def test_subjects():
    """Test subjects for different authorization scenarios."""
    return {
        "guest": {"subject": "lukhas:user:test_guest", "tier": "guest", "tier_num": 0, "scopes": []},
        "friend": {
            "subject": "lukhas:user:test_friend",
            "tier": "friend",
            "tier_num": 2,
            "scopes": ["memoria.read", "memoria.store"],
        },
        "trusted": {
            "subject": "lukhas:user:test_trusted",
            "tier": "trusted",
            "tier_num": 3,
            "scopes": ["memoria.read", "memoria.store", "memoria.fold"],
        },
        "service": {
            "subject": "lukhas:svc:orchestrator",
            "tier": "root_dev",
            "tier_num": 5,
            "scopes": ["memoria.read", "memoria.store"],
        },
    }


@pytest.fixture
def authz_test_scenarios():
    """Test scenarios for authorization operations."""
    return [
        {
            "name": "memoria_recall_allow",
            "module": "memoria",
            "action": "recall",
            "subject_type": "trusted",
            "expected_allowed": True,
            "expected_reason": "Policy checks passed",
        },
        {
            "name": "memoria_recall_deny_guest",
            "module": "memoria",
            "action": "recall",
            "subject_type": "guest",
            "expected_allowed": False,
            "expected_reason": "Tier guest not authorized",
        },
        {
            "name": "memoria_fold_allow_mfa",
            "module": "memoria",
            "action": "fold",
            "subject_type": "trusted",
            "expected_allowed": True,
            "expected_reason": "Policy checks passed",
            "requires_mfa": True,
        },
        {
            "name": "memoria_fold_deny_no_mfa",
            "module": "memoria",
            "action": "fold",
            "subject_type": "trusted",
            "expected_allowed": False,
            "expected_reason": "Step-up authentication required",
            "requires_mfa": False,
        },
        {
            "name": "service_account_allow",
            "module": "memoria",
            "action": "process",
            "subject_type": "service",
            "expected_allowed": True,
            "expected_reason": "Policy checks passed",
        },
    ]


@contextmanager
def temp_span_dump(spans: List[CapturedSpan]):
    """Create temporary file with span data for compatibility tests."""
    span_data = {
        "spans": [
            {
                "name": span.name,
                "attributes": span.attributes,
                "status": span.status,
                "duration_ms": span.duration_ms,
                "trace_id": span.trace_id,
                "span_id": span.span_id,
                "start_time_unix_nano": span.start_time_ns,
                "end_time_unix_nano": span.end_time_ns,
            }
            for span in spans
        ]
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(span_data, f, indent=2)
        temp_path = f.name

    try:
        yield Path(temp_path)
    finally:
        Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def span_validator():
    """Fixture providing span validation utilities."""

    class SpanValidator:
        """Utility class for validating spans."""

        @staticmethod
        def validate_authz_span(span: CapturedSpan, expected_attrs: Dict[str, Any] = None) -> bool:
            """Validate an authorization span has required attributes."""
            required_attrs = [
                "subject",
                "tier",
                "tier_num",
                "scopes",
                "module",
                "action",
                "decision",
                "reason",
                "decision_time_ms",
            ]

            # Check required attributes exist
            for attr in required_attrs:
                if attr not in span.attributes:
                    return False

            # Check expected attribute values if provided
            if expected_attrs:
                for key, expected_value in expected_attrs.items():
                    if span.attributes.get(key) != expected_value:
                        return False

            return True

        @staticmethod
        def validate_span_structure(span: CapturedSpan) -> bool:
            """Validate span follows OpenTelemetry structure."""
            # Check basic fields
            if not span.name or not span.trace_id or not span.span_id:
                return False

            # Check trace/span ID format (should be hex)
            try:
                int(span.trace_id, 16)
                int(span.span_id, 16)
            except ValueError:
                return False

            # Check duration is non-negative
            if span.duration_ms < 0:
                return False

            return True

    return SpanValidator()


@pytest.fixture
def matrix_contract_loader():
    """Fixture for loading Matrix contracts for testing."""

    def load_contract(module: str) -> Dict[str, Any]:
        """Load Matrix contract for a module."""
        contract_paths = [
            Path(f"/Users/agi_dev/LOCAL-REPOS/Lukhas/{module}/matrix_{module}.json"),
            Path(f"/Users/agi_dev/LOCAL-REPOS/Lukhas/matrix_{module}.json"),
            Path("/Users/agi_dev/LOCAL-REPOS/Lukhas/memory/matrix_memoria.json") if module == "memoria" else None,
        ]

        for path in contract_paths:
            if path and path.exists():
                with open(path) as f:
                    return json.load(f)

        # Return a minimal default contract for testing
        return {
            "module": module,
            "telemetry": {"spans": [{"name": f"{module}.check", "attrs": ["code.function", f"lukhas.{module}"]}]},
            "identity": {
                "requires_auth": True,
                "required_tiers": ["friend", "trusted", "inner_circle", "root_dev"],
                "scopes": [f"{module}.read", f"{module}.store"],
            },
        }

    return load_contract
