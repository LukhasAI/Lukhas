"""
Unit tests for rate-limit headers.

Verifies that x-ratelimit-* headers are present in responses and have
valid numeric values that make sense for OpenAI-style client libraries.

Phase 3: Added for rate-limit header validation.
"""
import re

from fastapi.testclient import TestClient

from adapters.openai.api import get_app

HEX32 = re.compile(r"^[0-9a-f]{32}$")


def test_models_includes_ratelimit_headers_and_trace():
    """Verify rate-limit headers present in /v1/models response."""
    app = app
    client = TestClient(app)

    r = client.get("/v1/models", headers={"Authorization": "Bearer testtoken"})

    # Status may be 200 (permissive) or 401/403 (strict); we still want headers
    assert r.status_code in (200, 401, 403), f"Unexpected status: {r.status_code}"

    # OpenAI-style request headers
    assert "x-ratelimit-limit-requests" in r.headers, "Missing limit header"
    assert "x-ratelimit-remaining-requests" in r.headers, "Missing remaining header"
    assert "x-ratelimit-reset-requests" in r.headers, "Missing reset header"

    # Values should be numeric-ish
    limit = int(float(r.headers["x-ratelimit-limit-requests"]))
    remaining = int(float(r.headers["x-ratelimit-remaining-requests"]))
    reset = float(r.headers["x-ratelimit-reset-requests"])

    assert limit >= 1, f"Invalid limit: {limit}"
    assert 0 <= remaining <= limit, f"Invalid remaining: {remaining} (limit={limit})"
    assert reset >= 0.0, f"Invalid reset: {reset}"

    # Trace header (if TraceHeaderMiddleware is enabled)
    trace = r.headers.get("x-trace-id") or r.headers.get("X-Trace-Id")
    if trace:
        assert HEX32.match(trace), f"Invalid trace ID format: {trace}"


def test_embeddings_includes_ratelimit_headers():
    """Verify rate-limit headers present in /v1/embeddings response."""
    app = app
    client = TestClient(app)

    r = client.post(
        "/v1/embeddings",
        json={"input": "test", "model": "lukhas-embed"},
        headers={"Authorization": "Bearer testtoken"}
    )

    # May be 200 (permissive) or 401/403 (strict)
    assert r.status_code in (200, 401, 403)

    # Headers should be present
    assert "x-ratelimit-limit-requests" in r.headers
    assert "x-ratelimit-remaining-requests" in r.headers
    assert "x-ratelimit-reset-requests" in r.headers


def test_responses_includes_ratelimit_headers():
    """Verify rate-limit headers present in /v1/responses response."""
    app = app
    client = TestClient(app)

    r = client.post(
        "/v1/responses",
        json={"input": "test", "model": "lukhas-response", "stream": False},
        headers={"Authorization": "Bearer testtoken"}
    )

    # May be 200 (permissive) or 401/403 (strict)
    assert r.status_code in (200, 401, 403)

    # Headers should be present
    assert "x-ratelimit-limit-requests" in r.headers
    assert "x-ratelimit-remaining-requests" in r.headers
    assert "x-ratelimit-reset-requests" in r.headers


def test_ratelimit_remaining_decreases_across_requests():
    """Verify remaining count decreases with successive requests."""
    app = app
    client = TestClient(app)

    # Make first request
    r1 = client.get("/v1/models", headers={"Authorization": "Bearer test123"})
    if r1.status_code not in (200,):
        # Skip if auth is required
        return

    remaining1 = int(float(r1.headers["x-ratelimit-remaining-requests"]))

    # Make second request
    r2 = client.get("/v1/models", headers={"Authorization": "Bearer test123"})
    remaining2 = int(float(r2.headers["x-ratelimit-remaining-requests"]))

    # Remaining should decrease (or stay same if bucket refilled)
    assert remaining2 <= remaining1, f"Remaining increased: {remaining1} -> {remaining2}"


def test_token_dimension_headers_present():
    """Verify token-dimension headers are present (even if zero)."""
    app = app
    client = TestClient(app)

    r = client.get("/v1/models", headers={"Authorization": "Bearer test"})

    # Token dimension headers should be present (for OpenAI parity)
    assert "x-ratelimit-limit-tokens" in r.headers
    assert "x-ratelimit-remaining-tokens" in r.headers
    assert "x-ratelimit-reset-tokens" in r.headers

    # Values should be numeric (may be 0 until token tracking is wired)
    int(float(r.headers["x-ratelimit-limit-tokens"]))
    int(float(r.headers["x-ratelimit-remaining-tokens"]))
    float(r.headers["x-ratelimit-reset-tokens"])
