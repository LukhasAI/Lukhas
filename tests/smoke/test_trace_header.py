"""
Smoke test: Trace header conformance.

Verifies that all responses include X-Trace-Id header with valid hex format.

Phase 3: Added as part of observability polish.
"""
import os
import re
import pytest
import requests

BASE = os.getenv("LUKHAS_BASE_URL", "http://localhost:8000")


def test_trace_header_present_and_hex():
    """Verify X-Trace-Id is present and valid hex format."""
    r = requests.get(f"{BASE}/v1/models", headers={"Authorization": "Bearer test"})
    
    # Should return 200 in permissive mode, may be 401/403 in strict mode
    assert r.status_code in (200, 401, 403), f"Unexpected status: {r.status_code}"
    
    trace_id = r.headers.get("X-Trace-Id")
    assert trace_id is not None, "Missing X-Trace-Id header"
    assert re.fullmatch(r"[0-9a-f]{32}", trace_id), f"Invalid trace ID format: {trace_id}"


def test_trace_header_unique_across_requests():
    """Verify each request gets a unique trace ID."""
    trace_ids = set()
    
    for _ in range(3):
        r = requests.get(f"{BASE}/health")
        trace_id = r.headers.get("X-Trace-Id")
        if trace_id:
            trace_ids.add(trace_id)
    
    # Should have unique IDs (unless extremely unlucky collision)
    assert len(trace_ids) >= 2, f"Expected unique trace IDs, got: {trace_ids}"


def test_trace_header_propagates_to_errors():
    """Verify trace ID is present even in error responses."""
    r = requests.get(f"{BASE}/v1/nonexistent", headers={"Authorization": "Bearer test"})
    
    assert r.status_code == 404
    trace_id = r.headers.get("X-Trace-Id")
    assert trace_id is not None, "Missing X-Trace-Id in error response"
    assert re.fullmatch(r"[0-9a-f]{32}", trace_id), f"Invalid trace ID in error: {trace_id}"
