"""
OpenTelemetry Minimal Tracing for LUKHAS AI
Provides lightweight instrumentation with noop fallback
Trinity Framework: ⚛️🧠🛡️
"""

import os
import time
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable

try:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc import trace_exporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import (
        BatchSpanProcessor,
        ConsoleSpanExporter,
        SimpleSpanProcessor,
    )
    from opentelemetry.trace import Status, StatusCode

    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False


class NoOpTracer:
    """No-op tracer for when OpenTelemetry is not available"""

    @contextmanager
    def start_span(self, name: str, **kwargs):
        """No-op span context manager"""
        yield NoOpSpan()

    def get_current_span(self):
        """Return no-op span"""
        return NoOpSpan()


class NoOpSpan:
    """No-op span implementation"""

    def set_attribute(self, key: str, value: Any):
        """No-op attribute setter"""
        pass

    def set_status(self, status: Any):
        """No-op status setter"""
        pass

    def add_event(self, name: str, attributes: dict[str, Any] = None):
        """No-op event adder"""
        pass

    def record_exception(self, exception: Exception):
        """No-op exception recorder"""
        pass


class LukhasTracer:
    """
    LUKHAS AI telemetry tracer with automatic span management
    Exports to console in CI (OTEL_EXPORTER=console)
    """

    def __init__(self):
        self._tracer = None
        self._provider = None
        self._initialized = False
        self._setup_tracer()

    def _setup_tracer(self):
        """Setup OpenTelemetry tracer with appropriate exporter"""
        if not OTEL_AVAILABLE:
            self._tracer = NoOpTracer()
            return

        # Configure resource
        resource = Resource.create(
            {
                "service.name": "lukhas-ai",
                "service.version": "2.0",
                "trinity.framework": "⚛️🧠🛡️",
            }
        )

        # Create provider
        self._provider = TracerProvider(resource=resource)

        # Configure exporter based on environment
        exporter_type = os.getenv("OTEL_EXPORTER", "none")

        if exporter_type == "console":
            # Console exporter for CI
            exporter = ConsoleSpanExporter()
            processor = SimpleSpanProcessor(exporter)
        elif exporter_type == "otlp":
            # OTLP exporter for production
            endpoint = os.getenv("OTEL_ENDPOINT", "localhost:4317")
            exporter = trace_exporter.OTLPSpanExporter(endpoint=endpoint)
            processor = BatchSpanProcessor(exporter)
        else:
            # No-op by default
            self._tracer = NoOpTracer()
            return

        self._provider.add_span_processor(processor)
        trace.set_tracer_provider(self._provider)
        self._tracer = trace.get_tracer(__name__)
        self._initialized = True

    @contextmanager
    def span(self, name: str, attributes: dict[str, Any] = None):
        """
        Create a span context manager with automatic timing

        Usage:
            with tracer.span('auth.validate', {'user_id': '123'}):
                # Your code here
        """
        if not self._tracer:
            yield NoOpSpan()
            return

        start_time = time.perf_counter()

        with self._tracer.start_as_current_span(name) as span:
            # Add attributes
            if attributes:
                for key, value in attributes.items():
                    span.set_attribute(key, str(value))

            # Add Trinity Framework tag
            span.set_attribute("trinity.component", self._get_component(name))

            try:
                yield span
                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise
            finally:
                # Record latency
                latency_ms = (time.perf_counter() - start_time) * 1000
                span.set_attribute("latency_ms", f"{latency_ms:.2f}")

                # Check performance budgets
                self._check_budget(name, latency_ms, span)

    def _get_component(self, span_name: str) -> str:
        """Map span name to Trinity component"""
        if "auth" in span_name or "identity" in span_name or "lid" in span_name.lower():
            return "⚛️ Identity"
        elif (
            "consent" in span_name or "policy" in span_name or "governance" in span_name
        ):
            return "🛡️ Guardian"
        else:
            return "🧠 Consciousness"

    def _check_budget(self, span_name: str, latency_ms: float, span: Any):
        """Check if latency exceeds budget and add warning"""
        budgets = {
            "lid.issue_token": 100,
            "lid.verify": 100,
            "lid.webauthn_assert": 100,
            "consent_ledger.record": 50,
            "context_bus.publish": 250,
            "context_bus.handoff": 250,
            "adapter.list_metadata": 150,
        }

        for pattern, budget in budgets.items():
            if pattern in span_name.lower():
                if latency_ms > budget:
                    span.add_event(
                        "budget_exceeded",
                        {
                            "budget_ms": budget,
                            "actual_ms": f"{latency_ms:.2f}",
                            "exceeded_by": f"{latency_ms - budget:.2f}",
                        },
                    )
                break

    def instrument(self, func: Callable) -> Callable:
        """
        Decorator to automatically instrument functions

        Usage:
            @tracer.instrument
            async def authenticate(user_id: str):
                # Your code here
        """

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            span_name = f"{func.__module__}.{func.__name__}"
            with self.span(span_name, kwargs):
                return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            span_name = f"{func.__module__}.{func.__name__}"
            with self.span(span_name, kwargs):
                return func(*args, **kwargs)

        # Return appropriate wrapper based on function type
        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    def export_metrics(self) -> dict[str, Any]:
        """Export current metrics (for testing)"""
        if not self._initialized:
            return {"status": "not_initialized"}

        # In a real implementation, would query metrics
        return {
            "status": "active",
            "exporter": os.getenv("OTEL_EXPORTER", "none"),
            "spans_exported": 0,  # Would track actual count
        }


# Global tracer instance
_tracer = LukhasTracer()


def get_tracer() -> LukhasTracer:
    """Get the global LUKHAS tracer instance"""
    return _tracer


# Export convenience functions
span = _tracer.span
instrument = _tracer.instrument


# Pre-configured span creators for each agent
class AgentSpans:
    """Pre-configured spans for each agent with their specific attributes"""

    @staticmethod
    @contextmanager
    def lid_issue(user_id: str, namespace: str = "default"):
        """A1: ΛID token issuance span"""
        with span("lid.issue_token", {"user_id": user_id, "namespace": namespace}) as s:
            yield s

    @staticmethod
    @contextmanager
    def lid_verify(token: str):
        """A1: ΛID token verification span"""
        with span("lid.verify", {"token_prefix": token[:8] if token else "none"}) as s:
            yield s

    @staticmethod
    @contextmanager
    def lid_webauthn(credential_id: str):
        """A1: ΛID WebAuthn assertion span"""
        with span("lid.webauthn_assert", {"credential_id": credential_id[:8]}) as s:
            yield s

    @staticmethod
    @contextmanager
    def consent_record(user_id: str, purpose: str, granted: bool):
        """A2: Consent recording span"""
        with span(
            "consent_ledger.record",
            {"user_id": user_id, "purpose": purpose, "granted": granted},
        ) as s:
            yield s

    @staticmethod
    @contextmanager
    def consent_check(user_id: str, purpose: str):
        """A2: Consent checking span"""
        with span(
            "consent_ledger.check", {"user_id": user_id, "purpose": purpose}
        ) as s:
            yield s

    @staticmethod
    @contextmanager
    def adapter_metadata(service: str, action: str):
        """A3: Adapter metadata fetch span"""
        with span(
            f"adapter.{service}.{action}",
            {
                "service": service,
                "action": action,
                "metadata_only": os.getenv("METADATA_ONLY", "1"),
            },
        ) as s:
            yield s

    @staticmethod
    @contextmanager
    def bus_publish(topic: str, message_size: int = 0):
        """A4: Context bus publish span"""
        with span(
            "context_bus.publish", {"topic": topic, "message_size": message_size}
        ) as s:
            yield s

    @staticmethod
    @contextmanager
    def bus_handoff(from_agent: str, to_agent: str):
        """A4: Context bus handoff span"""
        with span(
            "context_bus.handoff", {"from_agent": from_agent, "to_agent": to_agent}
        ) as s:
            yield s

    @staticmethod
    @contextmanager
    def pipeline_execute(pipeline_id: str, steps: int):
        """A4: Pipeline execution span"""
        with span(
            "pipeline.execute", {"pipeline_id": pipeline_id, "steps": steps}
        ) as s:
            yield s
