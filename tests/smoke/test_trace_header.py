"""
Smoke test: Trace header conformance.

Verifies that all responses include X-Trace-Id header with valid hex format.

Phase 3: Added as part of observability polish.
"""
from __future__ import annotations

import re

import pytest
from fastapi.testclient import TestClient

from lukhas.adapters.openai.api import get_app

AUTH_HEADERS = {"Authorization": "Bearer sk-lukhas-test-1234567890abcdef"}


@pytest.fixture
def client() -> TestClient:
    return TestClient(get_app())


def test_trace_header_present_and_hex(client: TestClient) -> None:
    """Verify X-Trace-Id is present and valid hex format."""
    r = client.get("/v1/models", headers=AUTH_HEADERS)
    assert r.status_code == 200

    trace_id = r.headers.get("X-Trace-Id")
    assert trace_id is not None, "Missing X-Trace-Id header"
    assert re.fullmatch(r"[0-9a-f]{32}", trace_id), f"Invalid trace ID format: {trace_id}"


def test_trace_header_unique_across_requests(client: TestClient) -> None:
    """Verify each request gets a unique trace ID."""
    trace_ids = set()

    for _ in range(3):
        r = client.get("/healthz")
        trace_id = r.headers.get("X-Trace-Id")
        if trace_id:
            trace_ids.add(trace_id)

    assert len(trace_ids) >= 2, f"Expected unique trace IDs, got: {trace_ids}"


def test_trace_header_propagates_to_errors(client: TestClient) -> None:
    """Verify trace ID is present even in error responses."""
    r = client.get("/v1/nonexistent", headers=AUTH_HEADERS)

    assert r.status_code == 404
    trace_id = r.headers.get("X-Trace-Id")
    assert trace_id is not None, "Missing X-Trace-Id in error response"
    assert re.fullmatch(r"[0-9a-f]{32}", trace_id), f"Invalid trace ID in error: {trace_id}"
