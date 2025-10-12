"""
SPDX-License-Identifier: Apache-2.0

tests/unit/test_ratelimit_keys.py

Unit tests for RateLimiter key generation and per-tenant isolation.
Validates that rate limits are scoped to (route, bearer_token) or (route, ip).
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Optional

import pytest

from lukhas.core.reliability.ratelimit import RateLimiter


def _mock_request(
    path: str = "/v1/embeddings",
    auth: Optional[str] = None,
    ip: str = "1.2.3.4"
):
    """
    Create mock FastAPI Request object for testing.
    
    Args:
        path: URL path
        auth: Authorization header value (e.g. "Bearer token123")
        ip: Client IP address
        
    Returns:
        Mock request object with minimal attributes
    """
    headers = {}
    if auth:
        headers["authorization"] = auth
    
    return SimpleNamespace(
        url=SimpleNamespace(path=path),
        headers=headers,
        client=SimpleNamespace(host=ip)
    )


def test_key_differs_by_bearer_token():
    """
    Test that different bearer tokens produce different rate limit keys.
    
    This ensures tenant isolation - each API key has independent quota.
    """
    limiter = RateLimiter(default_rps=10)
    
    req1 = _mock_request(auth="Bearer AAA")
    req2 = _mock_request(auth="Bearer BBB")
    
    key1 = limiter._key_for_request(req1)
    key2 = limiter._key_for_request(req2)
    
    assert key1 != key2, "Different tokens should produce different keys"
    assert key1.endswith(":AAA"), f"Key should end with token, got: {key1}"
    assert key2.endswith(":BBB"), f"Key should end with token, got: {key2}"


def test_key_differs_by_route():
    """
    Test that different routes produce different rate limit keys.
    
    This allows per-endpoint rate limit configuration.
    """
    limiter = RateLimiter(default_rps=10)
    
    req1 = _mock_request(path="/v1/embeddings", auth="Bearer TOKEN")
    req2 = _mock_request(path="/v1/models", auth="Bearer TOKEN")
    
    key1 = limiter._key_for_request(req1)
    key2 = limiter._key_for_request(req2)
    
    assert key1 != key2, "Different routes should produce different keys"
    assert "/v1/embeddings:" in key1
    assert "/v1/models:" in key2


def test_key_falls_back_to_ip_when_no_token():
    """
    Test that requests without bearer tokens are keyed by IP address.
    
    This provides basic rate limiting for unauthenticated requests.
    """
    limiter = RateLimiter(default_rps=10)
    
    req = _mock_request(auth=None, ip="9.9.9.9")
    key = limiter._key_for_request(req)
    
    assert key.endswith(":9.9.9.9"), \
        f"Key should fall back to IP, got: {key}"


def test_key_isolates_different_ips():
    """
    Test that different client IPs get different rate limit buckets.
    """
    limiter = RateLimiter(default_rps=10)
    
    req1 = _mock_request(auth=None, ip="1.1.1.1")
    req2 = _mock_request(auth=None, ip="2.2.2.2")
    
    key1 = limiter._key_for_request(req1)
    key2 = limiter._key_for_request(req2)
    
    assert key1 != key2, "Different IPs should produce different keys"
    assert key1.endswith(":1.1.1.1")
    assert key2.endswith(":2.2.2.2")


def test_same_token_same_route_produces_same_key():
    """
    Test that identical requests produce identical keys (cache consistency).
    """
    limiter = RateLimiter(default_rps=10)
    
    req1 = _mock_request(path="/v1/models", auth="Bearer TOKEN")
    req2 = _mock_request(path="/v1/models", auth="Bearer TOKEN")
    
    key1 = limiter._key_for_request(req1)
    key2 = limiter._key_for_request(req2)
    
    assert key1 == key2, "Identical requests should produce same key"


def test_bearer_token_takes_precedence_over_ip():
    """
    Test that bearer token is used even when IP is present.
    
    This ensures authenticated requests are keyed by tenant, not IP.
    """
    limiter = RateLimiter(default_rps=10)
    
    req = _mock_request(auth="Bearer TOKEN123", ip="5.5.5.5")
    key = limiter._key_for_request(req)
    
    assert key.endswith(":TOKEN123"), \
        "Bearer token should take precedence, got: {key}"
    assert "5.5.5.5" not in key, \
        "IP should not appear when bearer token present"


def test_malformed_bearer_falls_back_to_ip():
    """
    Test that malformed Authorization headers fall back to IP.
    
    Examples: empty token, missing space, wrong format
    """
    limiter = RateLimiter(default_rps=10)
    
    test_cases = [
        ("Bearer ", "Empty token"),
        ("Bearer", "Missing space"),
        ("Basic credentials", "Wrong scheme"),
        ("", "Empty header"),
    ]
    
    for auth_value, description in test_cases:
        req = _mock_request(auth=auth_value, ip="7.7.7.7")
        key = limiter._key_for_request(req)
        
        assert key.endswith(":7.7.7.7"), \
            f"{description}: Should fall back to IP, got: {key}"


def test_rate_limit_enforced_per_key():
    """
    Test that rate limits are enforced independently per key.
    
    Tenant A exhausting quota should not affect tenant B.
    """
    limiter = RateLimiter(default_rps=2)  # Very low limit for testing
    
    req_a = _mock_request(auth="Bearer TENANT_A")
    req_b = _mock_request(auth="Bearer TENANT_B")
    
    # Tenant A makes requests
    allowed_a1, _ = limiter.check_limit(req_a)
    allowed_a2, _ = limiter.check_limit(req_a)
    allowed_a3, _ = limiter.check_limit(req_a)
    allowed_a4, _ = limiter.check_limit(req_a)
    allowed_a5, retry_after = limiter.check_limit(req_a)
    
    # First 4 should succeed (capacity=4 for rps=2)
    assert allowed_a1, "First request should be allowed"
    assert allowed_a2, "Second request should be allowed"
    assert allowed_a3, "Third request should be allowed"
    assert allowed_a4, "Fourth request should be allowed"
    assert not allowed_a5, "Fifth request should be rate limited"
    assert retry_after > 0, "Should return retry_after when limited"
    
    # Tenant B should have independent quota
    allowed_b1, _ = limiter.check_limit(req_b)
    allowed_b2, _ = limiter.check_limit(req_b)
    
    assert allowed_b1, "Tenant B first request should succeed"
    assert allowed_b2, "Tenant B second request should succeed"


def test_anonymous_fallback_when_no_client():
    """
    Test that requests without client info fall back to 'anonymous'.
    
    Edge case: malformed request or testing scenarios.
    """
    limiter = RateLimiter(default_rps=10)
    
    # Request without client attribute
    req = SimpleNamespace(
        url=SimpleNamespace(path="/v1/test"),
        headers={}
    )
    
    key = limiter._key_for_request(req)
    
    assert key.endswith(":anonymous"), \
        f"Should fall back to 'anonymous', got: {key}"


def test_key_format_consistent():
    """
    Test that all keys follow "{route}:{principal}" format.
    """
    limiter = RateLimiter(default_rps=10)
    
    test_cases = [
        _mock_request(path="/v1/embeddings", auth="Bearer TOKEN"),
        _mock_request(path="/v1/models", auth=None, ip="1.2.3.4"),
        _mock_request(path="/healthz", auth=None, ip="5.6.7.8"),
    ]
    
    for req in test_cases:
        key = limiter._key_for_request(req)
        
        assert ":" in key, f"Key should contain ':', got: {key}"
        route, principal = key.rsplit(":", 1)
        
        assert route == req.url.path, \
            f"Route portion should match path, got: {route}"
        assert len(principal) > 0, \
            f"Principal portion should not be empty"
