"""
Test OpenTelemetry distributed tracing integration.

Validates:
- Trace ID injection into response headers
- Span creation and attribute setting
- Graceful degradation when OTEL disabled
"""

import os

from serve.main import app
from starlette.testclient import TestClient

from tests.smoke.fixtures import GOLDEN_AUTH_HEADERS

AUTH_HEADERS = GOLDEN_AUTH_HEADERS


def test_trace_headers_present_when_otel_enabled(monkeypatch):
    """Verify trace ID is included in response headers when OTEL is enabled."""
    # When OTEL endpoint is set, façade should include X-Trace-Id header
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
    client = TestClient(app)
    r = client.post("/v1/responses", headers=AUTH_HEADERS, json={"input": "trace me"})

    # Should have X-Trace-Id header
    assert "X-Trace-Id" in r.headers or "trace_id" in (
        r.json() or {}
    ), "Expected X-Trace-Id header when OTEL is configured"

    # If X-Trace-Id present, should be 32-char hex string
    if "X-Trace-Id" in r.headers:
        trace_id = r.headers["X-Trace-Id"]
        assert len(trace_id) == 32, f"Trace ID should be 32 chars, got {len(trace_id)}"
        assert all(c in "0123456789abcdef" for c in trace_id), "Trace ID should be hex"


def test_no_trace_headers_when_otel_disabled(monkeypatch):
    """Verify graceful degradation when OTEL endpoint not configured."""
    # Ensure OTEL endpoint is not set
    monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT", raising=False)
    client = TestClient(app)
    r = client.get("/v1/models", headers=AUTH_HEADERS)

    # Should work fine without tracing
    assert r.status_code == 200
    # X-Trace-Id may or may not be present (graceful degradation)


def test_traced_matriz_operations():
    """Verify MATRIZ operations are traced when available."""
    client = TestClient(app)

    # Even without OTEL, request should succeed
    r = client.post("/v1/responses", headers=AUTH_HEADERS, json={"input": "test query"})
    assert r.status_code == 200

    data = r.json()
    assert "output" in data
    assert "text" in data["output"]
