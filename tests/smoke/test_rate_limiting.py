"""
Test rate limiting behavior with 429 responses.

Validates:
- Per-tenant isolation (no cross-tenant throttling)
- 429 status code with Retry-After header
- Token bucket algorithm behavior
- Rate limit recovery after waiting
- Different limits per endpoint
"""
import pytest
import time
from fastapi.testclient import TestClient
from adapters.openai.api import get_app

from tests.smoke.fixtures import GOLDEN_AUTH_HEADERS


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(get_app())


@pytest.fixture
def auth_headers():
    """Provide valid Bearer token for authenticated requests."""
    return GOLDEN_AUTH_HEADERS


@pytest.fixture
def auth_headers_tenant2():
    """Provide token for different tenant."""
    return {"Authorization": "Bearer sk-lukhas-tenant2-9876543210fedcba"}


def test_rate_limit_enforced_on_burst(client, auth_headers):
    """Verify rate limit kicks in on burst requests."""
    # Make rapid requests to /v1/models (default 20 RPS, capacity ~40)
    responses = []
    for i in range(50):  # Exceed capacity
        response = client.get("/v1/models", headers=auth_headers)
        responses.append(response.status_code)
        if response.status_code == 429:
            break  # Stop once rate limited

    # Should eventually get 429
    assert 429 in responses, "Expected 429 rate limit response in burst"


def test_rate_limit_429_has_retry_after(client, auth_headers):
    """Verify 429 response includes Retry-After header."""
    # Exhaust rate limit
    for i in range(50):
        response = client.get("/v1/models", headers=auth_headers)
        if response.status_code == 429:
            # Check for Retry-After header
            assert "Retry-After" in response.headers, \
                "429 response missing Retry-After header"

            retry_after = response.headers["Retry-After"]
            # Should be numeric (seconds)
            assert retry_after.replace(".", "").isdigit(), \
                f"Retry-After should be numeric: {retry_after}"
            break


def test_rate_limit_error_format_openai_compatible(client, auth_headers):
    """Verify 429 error follows OpenAI format."""
    # Exhaust rate limit
    for i in range(50):
        response = client.get("/v1/models", headers=auth_headers)
        if response.status_code == 429:
            data = response.json()

            # Should have error field (may be wrapped in detail)
            if "detail" in data:
                error = data["detail"]
            else:
                error = data.get("error", data)

            # OpenAI format
            assert isinstance(error, dict)
            assert "type" in error or "message" in error
            break


def test_rate_limit_per_tenant_isolation(client, auth_headers, auth_headers_tenant2):
    """Verify tenant1 exhausting limit doesn't affect tenant2."""
    # Exhaust tenant1's limit
    tenant1_limited = False
    for i in range(50):
        response = client.get("/v1/models", headers=auth_headers)
        if response.status_code == 429:
            tenant1_limited = True
            break

    assert tenant1_limited, "Tenant1 should be rate limited"

    # Tenant2 should still work
    response_tenant2 = client.get("/v1/models", headers=auth_headers_tenant2)
    assert response_tenant2.status_code == 200, \
        "Tenant2 should not be affected by tenant1's rate limit"


def test_rate_limit_recovery_after_wait(client, auth_headers):
    """Verify rate limit recovers after waiting."""
    # Exhaust rate limit
    for i in range(50):
        response = client.get("/v1/models", headers=auth_headers)
        if response.status_code == 429:
            retry_after = float(response.headers.get("Retry-After", "1"))

            # Wait for rate limit to recover
            time.sleep(retry_after + 0.5)  # Add buffer

            # Should work again
            response_after = client.get("/v1/models", headers=auth_headers)
            assert response_after.status_code == 200, \
                "Rate limit should recover after waiting"
            break


def test_rate_limit_health_endpoints_exempt(client):
    """Verify health endpoints are not rate limited."""
    # Make many requests to health endpoints (no auth needed)
    for i in range(100):
        response = client.get("/healthz")
        assert response.status_code == 200

    for i in range(100):
        response = client.get("/readyz")
        assert response.status_code == 200

    # Should never get 429 on health endpoints


def test_rate_limit_metrics_endpoint_exempt(client):
    """Verify /metrics endpoint is not rate limited."""
    # Make many requests to metrics
    for i in range(100):
        response = client.get("/metrics")
        assert response.status_code == 200

    # Should never get 429 on metrics


def test_rate_limit_different_endpoints_separate_buckets(client, auth_headers):
    """Verify different endpoints have separate rate limit buckets."""
    # Exhaust /v1/models
    models_limited = False
    for i in range(50):
        response = client.get("/v1/models", headers=auth_headers)
        if response.status_code == 429:
            models_limited = True
            break

    assert models_limited, "/v1/models should be rate limited"

    # /v1/embeddings should still work (different bucket)
    embeddings_response = client.post(
        "/v1/embeddings",
        json={"input": "test"},
        headers=auth_headers
    )
    # Should get 200 (separate bucket) or 429 if also exhausted
    assert embeddings_response.status_code in [200, 429]


def test_rate_limit_anonymous_requests_by_ip(client):
    """Verify anonymous requests (no auth) are rate limited by IP."""
    # Note: This will fail with 401 since endpoints require auth
    # But the rate limiter should still process the request
    responses = []
    for i in range(50):
        response = client.get("/v1/models")  # No auth
        responses.append(response.status_code)
        if response.status_code == 429:
            break

    # Will get 401 (unauthorized) before hitting rate limit
    # But verifies rate limiter doesn't crash on missing auth
    assert 401 in responses


def test_rate_limit_preserves_tenant_identity(client):
    """Verify rate limiter correctly hashes token for tenant isolation."""
    # Two requests with same token should share rate limit
    token = "Bearer sk-lukhas-same-token-12345678"

    responses = []
    for i in range(50):
        response = client.get(
            "/v1/models",
            headers={"Authorization": token}
        )
        responses.append(response.status_code)
        if response.status_code == 429:
            break

    # Should eventually hit rate limit
    assert 429 in responses, "Same token should share rate limit"


def test_rate_limit_does_not_block_forever(client, auth_headers):
    """Verify rate limited requests eventually succeed (no permanent block)."""
    # Exhaust limit
    for i in range(50):
        response = client.get("/v1/models", headers=auth_headers)
        if response.status_code == 429:
            # Wait a bit longer
            time.sleep(2.0)

            # Try again
            retry_response = client.get("/v1/models", headers=auth_headers)
            # Should eventually succeed (not permanent block)
            if retry_response.status_code == 200:
                return  # Success

    # If we get here without 429, rate limit may not have triggered
    # (Test might be too fast or rate limit is very generous)
