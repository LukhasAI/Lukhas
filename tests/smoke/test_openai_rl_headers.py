"""
Smoke test: OpenAI-compatible rate limit headers.

Validates that all API responses include proper rate limit headers:
- Both uppercase (X-RateLimit-*) and lowercase (x-ratelimit-*-requests) variants
- Present on 200 success responses
- Present on error responses (401, 404, etc.)

OpenAI Parity: PR #406 header standards.
Phase 4: P0 audit-ready implementation (Engineer Brief 2025-10-22).
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from serve.main import app
from tests.smoke.fixtures import GOLDEN_AUTH_HEADERS


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def _assert_rl_headers(headers: dict) -> None:
    """Assert rate limit headers are present (both uppercase and lowercase variants)."""
    # Uppercase variants
    assert "X-RateLimit-Limit" in headers, "Missing X-RateLimit-Limit header"
    assert "X-RateLimit-Remaining" in headers, "Missing X-RateLimit-Remaining header"
    assert "X-RateLimit-Reset" in headers, "Missing X-RateLimit-Reset header"

    # Lowercase OpenAI-style variants
    lower = {k.lower(): v for k, v in headers.items()}
    assert "x-ratelimit-limit-requests" in lower, "Missing x-ratelimit-limit-requests header"
    assert "x-ratelimit-remaining-requests" in lower, "Missing x-ratelimit-remaining-requests header"
    assert "x-ratelimit-reset-requests" in lower, "Missing x-ratelimit-reset-requests header"


def test_rl_headers_on_success_embeddings(client: TestClient) -> None:
    """Verify rate limit headers present on successful embeddings request."""
    r = client.post(
        "/v1/embeddings",
        json={"model": "lukhas-embed-1", "input": "hi"},
        headers=GOLDEN_AUTH_HEADERS
    )
    assert r.status_code in (200, 201)
    _assert_rl_headers(r.headers)


def test_rl_headers_on_success_models(client: TestClient) -> None:
    """Verify rate limit headers present on successful models list request."""
    r = client.get("/v1/models", headers=GOLDEN_AUTH_HEADERS)
    assert r.status_code == 200
    _assert_rl_headers(r.headers)


def test_rl_headers_on_success_responses(client: TestClient) -> None:
    """Verify rate limit headers present on successful responses request."""
    r = client.post(
        "/v1/responses",
        json={"model": "lukhas-mini", "input": "test"},
        headers=GOLDEN_AUTH_HEADERS
    )
    assert r.status_code == 200
    _assert_rl_headers(r.headers)


def test_rl_headers_on_404(client: TestClient) -> None:
    """Verify rate limit headers present even on 404 errors."""
    r = client.get("/v1/nonexistent", headers=GOLDEN_AUTH_HEADERS)
    assert r.status_code == 404
    _assert_rl_headers(r.headers)


def test_rl_headers_on_healthz(client: TestClient) -> None:
    """Verify rate limit headers present on health endpoint."""
    r = client.get("/healthz")
    assert r.status_code == 200
    _assert_rl_headers(r.headers)


def test_rl_header_values_numeric(client: TestClient) -> None:
    """Verify rate limit header values are valid numbers."""
    r = client.get("/v1/models", headers=GOLDEN_AUTH_HEADERS)
    assert r.status_code == 200

    limit = r.headers.get("X-RateLimit-Limit")
    remaining = r.headers.get("X-RateLimit-Remaining")
    reset = r.headers.get("X-RateLimit-Reset")

    assert int(limit) > 0, f"Invalid rate limit: {limit}"
    assert int(remaining) >= 0, f"Invalid remaining: {remaining}"
    assert int(reset) > 0, f"Invalid reset timestamp: {reset}"


def test_trace_id_header_present(client: TestClient) -> None:
    """Verify X-Trace-Id header is present (OpenAI X-Request-Id parity)."""
    r = client.get("/v1/models", headers=GOLDEN_AUTH_HEADERS)
    assert r.status_code == 200

    trace_id = r.headers.get("X-Trace-Id")
    request_id = r.headers.get("X-Request-Id")

    # Either header should be present (we add both)
    assert trace_id or request_id, "Missing trace/request ID headers"

    # If both present, they should match
    if trace_id and request_id:
        assert trace_id == request_id, f"Trace and Request IDs should match: {trace_id} != {request_id}"


def test_trace_id_unique_across_requests(client: TestClient) -> None:
    """Verify trace IDs are unique for each request."""
    r1 = client.get("/healthz")
    r2 = client.get("/healthz")

    trace1 = r1.headers.get("X-Trace-Id")
    trace2 = r2.headers.get("X-Trace-Id")

    assert trace1 != trace2, f"Expected unique trace IDs, got {trace1} == {trace2}"
