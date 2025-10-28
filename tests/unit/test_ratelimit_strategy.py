"""
Unit tests for rate limiter keying strategy.

Phase 3: Tests LUKHAS_RL_KEYING environment variable behavior.
"""
import os
from types import SimpleNamespace

import pytest

import pytest
from core.reliability.ratelimit import RateLimiter


class MockRequest:
    """Mock FastAPI Request for testing."""

    def __init__(self, path="/v1/embeddings", headers=None, client_host="1.2.3.4"):
        self.url = SimpleNamespace(path=path)
        self.headers = headers or {}
        self.client = SimpleNamespace(host=client_host)


def test_route_principal_keying_default(monkeypatch):
    """
    Test default keying strategy: route + principal.

    Default behavior keys by (route, principal) to isolate per-user limits.
    """
    monkeypatch.delenv("LUKHAS_RL_KEYING", raising=False)

    rl = RateLimiter()
    req = MockRequest(
        path="/v1/embeddings",
        headers={"authorization": "Bearer sk-abc123"}
    )

    key = rl._key_for_request(req)

    # Should include both route and principal (hashed token)
    assert key.startswith("/v1/embeddings:")
    assert "tok:" in key, f"Expected hashed token in key, got: {key}"


def test_route_only_keying(monkeypatch):
    """
    Test route-only keying strategy.

    When LUKHAS_RL_KEYING=route_only, should key by route alone.
    """
    monkeypatch.setenv("LUKHAS_RL_KEYING", "route_only")

    rl = RateLimiter()
    req = MockRequest(
        path="/v1/embeddings",
        headers={"authorization": "Bearer sk-xyz789"}
    )

    key = rl._key_for_request(req)

    # Should be just the route
    assert key == "/v1/embeddings", f"Expected route-only key, got: {key}"


def test_principal_extraction_bearer_token(monkeypatch):
    """Test that bearer tokens are hashed (not stored raw)."""
    monkeypatch.delenv("LUKHAS_RL_KEYING", raising=False)

    rl = RateLimiter()
    req = MockRequest(headers={"authorization": "Bearer sk-test-secret-key"})

    principal = rl._extract_principal(req)

    # Should be hashed, not raw token
    assert principal.startswith("tok:"), f"Expected tok: prefix, got: {principal}"
    assert "sk-test-secret-key" not in principal, "Raw token leaked in principal!"
    assert len(principal) == 20, f"Expected 'tok:' + 16-char hash, got: {principal}"


def test_principal_extraction_fallback_to_ip(monkeypatch):
    """Test fallback to IP when no bearer token present."""
    monkeypatch.delenv("LUKHAS_RL_KEYING", raising=False)

    rl = RateLimiter()
    req = MockRequest(headers={}, client_host="192.168.1.100")

    principal = rl._extract_principal(req)

    # Should fallback to IP (no prefix in current implementation)
    assert principal == "192.168.1.100", f"Expected IP address, got: {principal}"


def test_principal_extraction_x_forwarded_for(monkeypatch):
    """Test X-Forwarded-For handling (proxy scenarios)."""
    monkeypatch.delenv("LUKHAS_RL_KEYING", raising=False)

    rl = RateLimiter()
    req = MockRequest(
        headers={"x-forwarded-for": "203.0.113.1, 192.168.1.1"},
        client_host="10.0.0.1"
    )

    principal = rl._extract_principal(req)

    # Should use first IP from X-Forwarded-For
    assert principal == "203.0.113.1", \
        f"Expected first IP from XFF, got: {principal}"


def test_different_tokens_get_different_keys(monkeypatch):
    """Test that different tokens produce different rate limit keys."""
    monkeypatch.delenv("LUKHAS_RL_KEYING", raising=False)

    rl = RateLimiter()

    req1 = MockRequest(headers={"authorization": "Bearer token-alpha"})
    req2 = MockRequest(headers={"authorization": "Bearer token-beta"})

    key1 = rl._key_for_request(req1)
    key2 = rl._key_for_request(req2)

    # Different tokens should produce different keys
    assert key1 != key2, "Different tokens produced same rate limit key!"


def test_rate_limit_isolation_per_principal():
    """
    Integration test: Verify different principals have independent limits.

    Each (route, principal) pair gets its own token bucket.
    """
    rl = RateLimiter(default_rps=2)  # Low limit for testing

    req_user1 = MockRequest(headers={"authorization": "Bearer user1-token"})
    req_user2 = MockRequest(headers={"authorization": "Bearer user2-token"})

    # User1 makes 2 requests (should succeed)
    allowed1, _ = rl.check_limit(req_user1)
    allowed2, _ = rl.check_limit(req_user1)

    assert allowed1 and allowed2, "User1 should be allowed 2 requests"

    # User2 makes 2 requests (should also succeed - independent bucket)
    allowed3, _ = rl.check_limit(req_user2)
    allowed4, _ = rl.check_limit(req_user2)

    assert allowed3 and allowed4, \
        "User2 should have independent bucket, not affected by User1"
