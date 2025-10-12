import os
from starlette.testclient import TestClient
from lukhas.adapters.openai.api import get_app

def test_trace_headers_present_when_otel_enabled(monkeypatch):
    # When OTEL endpoint is set, façade should include a trace header or id in response
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
    client = TestClient(get_app())
    r = client.post("/v1/responses", json={"input": "trace me", "tools": []})
    # Accept either W3C header or JSON field
    ok = ("traceparent" in r.headers) or ("trace_id" in (r.json() or {}))
    assert ok, "expected trace context when OTEL is configured"
