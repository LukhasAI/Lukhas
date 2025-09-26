"""
Telemetry Smoke Tests for Matrix Contracts v2

Tests that telemetry exports contain required OpenTelemetry semantic conventions
as specified in matrix contracts. These are deterministic existence checks
rather than quantitative thresholds to avoid flaky CI.

Validates compliance with:
- OpenTelemetry Semantic Conventions v1.37.0
- LUKHAS matrix contract telemetry specifications
- OTel trace and metrics data models
"""

import json
import pytest
import pathlib

def load_telemetry_dump(path):
    """Load the exported spans/metrics JSON from a telemetry dump."""
    with open(path, "r") as f:
        return json.load(f)

@pytest.mark.telemetry
def test_memory_recall_span_has_semconv_attrs():
    """Test that memory.recall span exists with required semconv attributes."""
    tel = load_telemetry_dump("telemetry/memory_spans.json")
    spans = tel.get("spans", [])

    found = False
    for sp in spans:
        if sp.get("name") == "memory.recall":
            attrs = sp.get("attributes", {})

            # Required semantic convention keys per matrix contract
            assert "code.function" in attrs, "Missing semconv attribute: code.function"
            assert attrs.get("lukhas.module") == "memory", f"Expected lukhas.module=memory, got {attrs.get('lukhas.module')}"
            assert "lukhas.k" in attrs, "Missing custom attribute: lukhas.k"

            # Semconv version tracking
            assert "otel.semconv.version" in attrs, "Missing semconv version tracking"
            assert attrs.get("otel.semconv.version") == "1.37.0", "Semconv version mismatch"

            found = True
            break

    assert found, "Expected span 'memory.recall' not found in telemetry export"

@pytest.mark.telemetry
def test_memory_fold_span_has_semconv_attrs():
    """Test that memory.fold span exists with required semconv attributes."""
    tel = load_telemetry_dump("telemetry/memory_spans.json")
    spans = tel.get("spans", [])

    found = False
    for sp in spans:
        if sp.get("name") == "memory.fold":
            attrs = sp.get("attributes", {})

            # Required semantic convention keys
            assert "code.function" in attrs, "Missing semconv attribute: code.function"
            assert attrs.get("lukhas.module") == "memory", f"Expected lukhas.module=memory, got {attrs.get('lukhas.module')}"
            assert "lukhas.fold_count" in attrs, "Missing custom attribute: lukhas.fold_count"

            found = True
            break

    assert found, "Expected span 'memory.fold' not found in telemetry export"

@pytest.mark.telemetry
def test_latency_metric_present():
    """Test that required latency metric exists in telemetry export."""
    tel = load_telemetry_dump("telemetry/memory_metrics.json")
    metrics = tel.get("metrics", [])
    metric_names = {m.get("name") for m in metrics}

    assert "lukhas.memory.latency" in metric_names, "Missing latency metric in telemetry"

@pytest.mark.telemetry
def test_recall_results_metric_present():
    """Test that recall results gauge metric exists."""
    tel = load_telemetry_dump("telemetry/memory_metrics.json")
    metrics = tel.get("metrics", [])
    metric_names = {m.get("name") for m in metrics}

    assert "lukhas.memory.recall.results" in metric_names, "Missing recall results metric"

@pytest.mark.telemetry
def test_cascade_prevention_counter_present():
    """Test that cascade prevention counter exists."""
    tel = load_telemetry_dump("telemetry/memory_metrics.json")
    metrics = tel.get("metrics", [])
    metric_names = {m.get("name") for m in metrics}

    assert "lukhas.memory.cascade.prevented" in metric_names, "Missing cascade prevention counter"

@pytest.mark.telemetry
def test_metrics_have_correct_types():
    """Test that metrics have expected instrument types per OTel data model."""
    tel = load_telemetry_dump("telemetry/memory_metrics.json")
    metrics = tel.get("metrics", [])

    expected_types = {
        "lukhas.memory.latency": "histogram",
        "lukhas.memory.recall.results": "gauge",
        "lukhas.memory.cascade.prevented": "counter"
    }

    for metric in metrics:
        name = metric.get("name")
        if name in expected_types:
            actual_type = metric.get("type")
            expected_type = expected_types[name]
            assert actual_type == expected_type, f"Metric {name}: expected type {expected_type}, got {actual_type}"

@pytest.mark.telemetry
def test_spans_have_trace_structure():
    """Test that spans follow OTel trace data model structure."""
    tel = load_telemetry_dump("telemetry/memory_spans.json")
    spans = tel.get("spans", [])

    assert len(spans) > 0, "No spans found in telemetry export"

    for span in spans:
        # Required fields per OTel trace data model
        assert "trace_id" in span, "Span missing trace_id"
        assert "span_id" in span, "Span missing span_id"
        assert "name" in span, "Span missing name"
        assert "attributes" in span, "Span missing attributes"
        assert "start_time_unix_nano" in span, "Span missing start_time_unix_nano"
        assert "end_time_unix_nano" in span, "Span missing end_time_unix_nano"

        # Validate trace/span ID format (hex strings)
        assert isinstance(span["trace_id"], str) and len(span["trace_id"]) == 32, "Invalid trace_id format"
        assert isinstance(span["span_id"], str) and len(span["span_id"]) == 16, "Invalid span_id format"

if __name__ == "__main__":
    # Run just telemetry tests when executed directly
    pytest.main(["-v", "-m", "telemetry", __file__])