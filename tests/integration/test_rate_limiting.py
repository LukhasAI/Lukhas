"""
Integration tests for rate limiting (Task 2.2).

Tests verify:
- Sliding window algorithm accuracy
- Per-user rate limits by tier
- Per-IP rate limits
- 429 responses with proper headers
- Whitelisting and blacklisting
- Burst handling

Security: OWASP A04 (Insecure Design) mitigation - prevents DoS attacks
"""

import time
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import Request, Response
from fastapi.responses import JSONResponse

from lukhas.governance.rate_limit import (
    InMemoryRateLimitStorage,
    RateLimitConfig,
    RateLimitMiddleware,
    RateLimitRule,
)


class TestSlidingWindowAlgorithm:
    """Test accuracy of sliding window rate limiting algorithm."""

    def test_sliding_window_allows_within_limit(self):
        """Verify requests within limit are allowed."""
        storage = InMemoryRateLimitStorage()

        # Allow 5 requests per 10 seconds
        for i in range(5):
            result = storage.check_rate_limit("test:key", limit=5, window_seconds=10)
            assert result.allowed is True
            assert result.remaining == 4 - i
            assert result.limit == 5

        # 6th request should be denied
        result = storage.check_rate_limit("test:key", limit=5, window_seconds=10)
        assert result.allowed is False
        assert result.remaining == 0
        assert result.retry_after > 0

    def test_sliding_window_expires_old_requests(self):
        """Verify old requests slide out of the window."""
        storage = InMemoryRateLimitStorage()

        # Make 5 requests (fills the limit)
        for _ in range(5):
            result = storage.check_rate_limit("test:key", limit=5, window_seconds=1)
            assert result.allowed is True

        # 6th request denied
        result = storage.check_rate_limit("test:key", limit=5, window_seconds=1)
        assert result.allowed is False

        # Wait for window to expire
        time.sleep(1.1)

        # Should be allowed again (old requests expired)
        result = storage.check_rate_limit("test:key", limit=5, window_seconds=1)
        assert result.allowed is True
        assert result.remaining == 4

    def test_sliding_window_partial_expiry(self):
        """Verify partial window expiry (true sliding window)."""
        storage = InMemoryRateLimitStorage()

        # Make 3 requests at T=0
        for _ in range(3):
            result = storage.check_rate_limit("test:key", limit=5, window_seconds=2)
            assert result.allowed is True

        # Wait 1 second
        time.sleep(1.0)

        # Make 2 more requests at T=1 (total: 5, all within 2-second window)
        for _ in range(2):
            result = storage.check_rate_limit("test:key", limit=5, window_seconds=2)
            assert result.allowed is True

        # 6th request at T=1 should be denied (5 requests in last 2 seconds)
        result = storage.check_rate_limit("test:key", limit=5, window_seconds=2)
        assert result.allowed is False

        # Wait 1.1 more seconds (T=2.1)
        time.sleep(1.1)

        # First 3 requests have expired, so we should have room
        # (only 2 requests from T=1 remain in window)
        result = storage.check_rate_limit("test:key", limit=5, window_seconds=2)
        assert result.allowed is True

    def test_different_keys_isolated(self):
        """Verify different keys have separate rate limits."""
        storage = InMemoryRateLimitStorage()

        # Fill limit for key1
        for _ in range(5):
            result = storage.check_rate_limit("key1", limit=5, window_seconds=10)
            assert result.allowed is True

        # key1 should be limited
        result = storage.check_rate_limit("key1", limit=5, window_seconds=10)
        assert result.allowed is False

        # key2 should still be allowed
        result = storage.check_rate_limit("key2", limit=5, window_seconds=10)
        assert result.allowed is True

    def test_reset_clears_rate_limit(self):
        """Verify reset() clears rate limit for a key."""
        storage = InMemoryRateLimitStorage()

        # Fill limit
        for _ in range(5):
            storage.check_rate_limit("test:key", limit=5, window_seconds=10)

        # Verify limited
        result = storage.check_rate_limit("test:key", limit=5, window_seconds=10)
        assert result.allowed is False

        # Reset
        storage.reset("test:key")

        # Should be allowed again
        result = storage.check_rate_limit("test:key", limit=5, window_seconds=10)
        assert result.allowed is True

    def test_reset_all_clears_all_limits(self):
        """Verify reset_all() clears all rate limits."""
        storage = InMemoryRateLimitStorage()

        # Fill limits for multiple keys
        for _ in range(5):
            storage.check_rate_limit("key1", limit=5, window_seconds=10)
            storage.check_rate_limit("key2", limit=5, window_seconds=10)

        # Verify both limited
        assert storage.check_rate_limit("key1", limit=5, window_seconds=10).allowed is False
        assert storage.check_rate_limit("key2", limit=5, window_seconds=10).allowed is False

        # Reset all
        storage.reset_all()

        # Both should be allowed again
        assert storage.check_rate_limit("key1", limit=5, window_seconds=10).allowed is True
        assert storage.check_rate_limit("key2", limit=5, window_seconds=10).allowed is True

    def test_cleanup_removes_old_windows(self):
        """Verify cleanup_old_windows() removes stale data."""
        storage = InMemoryRateLimitStorage()

        # Create some activity
        storage.check_rate_limit("key1", limit=10, window_seconds=1)
        storage.check_rate_limit("key2", limit=10, window_seconds=1)

        stats_before = storage.get_stats()
        assert stats_before["total_keys"] == 2

        # Wait for windows to expire
        time.sleep(1.5)

        # Clean up windows older than 1 second
        removed = storage.cleanup_old_windows(max_age_seconds=1)
        assert removed == 2

        stats_after = storage.get_stats()
        assert stats_after["total_keys"] == 0


class TestRateLimitConfig:
    """Test rate limit configuration and rule matching."""

    def test_default_per_user_rules_created(self):
        """Verify default per-user rules are created."""
        config = RateLimitConfig()
        assert len(config.per_user_rules) > 0

        # Check tier 0 (free)
        tier0_rules = [r for r in config.per_user_rules if r.tier == 0]
        assert len(tier0_rules) > 0
        assert any(r.path_pattern == "*" for r in tier0_rules)

    def test_default_per_ip_rules_created(self):
        """Verify default per-IP rules are created."""
        config = RateLimitConfig()
        assert len(config.per_ip_rules) > 0

        # Check global IP limits
        global_rules = [r for r in config.per_ip_rules if r.path_pattern == "*"]
        assert len(global_rules) > 0

    def test_path_matching_exact(self):
        """Verify exact path matching."""
        config = RateLimitConfig()
        assert config._path_matches_pattern("/api/v1/auth/login", "/api/v1/auth/login") is True
        assert config._path_matches_pattern("/api/v1/auth/logout", "/api/v1/auth/login") is False

    def test_path_matching_wildcard(self):
        """Verify wildcard path matching."""
        config = RateLimitConfig()
        assert config._path_matches_pattern("/api/v1/auth/login", "/api/v1/auth/*") is True
        assert config._path_matches_pattern("/api/v1/auth/logout", "/api/v1/auth/*") is True
        assert config._path_matches_pattern("/api/v2/users", "/api/v1/auth/*") is False

    def test_path_matching_global(self):
        """Verify global wildcard matching."""
        config = RateLimitConfig()
        assert config._path_matches_pattern("/any/path", "*") is True
        assert config._path_matches_pattern("/another/path", "*") is True

    def test_get_rules_for_user_filters_by_tier(self):
        """Verify get_rules_for_user() filters by tier."""
        config = RateLimitConfig()

        # Get rules for tier 0 (free)
        rules_t0 = config.get_rules_for_user("/api/v1/query", tier=0)
        assert all(r.tier is None or r.tier == 0 for r in rules_t0)

        # Get rules for tier 1 (basic)
        rules_t1 = config.get_rules_for_user("/api/v1/query", tier=1)
        assert all(r.tier is None or r.tier == 1 for r in rules_t1)

    def test_get_rules_for_user_sorts_by_specificity(self):
        """Verify rules are sorted by specificity (most specific first)."""
        config = RateLimitConfig(
            per_user_rules=[
                RateLimitRule(requests=100, window_seconds=3600, path_pattern="*", tier=0),
                RateLimitRule(
                    requests=50, window_seconds=3600, path_pattern="/api/v1/consciousness/*", tier=0
                ),
            ]
        )

        rules = config.get_rules_for_user("/api/v1/consciousness/query", tier=0)

        # Most specific rule should be first
        assert rules[0].path_pattern == "/api/v1/consciousness/*"
        assert rules[0].requests == 50

    def test_ip_blocked(self):
        """Verify IP blocking."""
        config = RateLimitConfig(blocked_ips=["192.168.1.100", "10.0.0.5"])
        assert config.is_ip_blocked("192.168.1.100") is True
        assert config.is_ip_blocked("192.168.1.101") is False

    def test_ip_whitelisted(self):
        """Verify IP whitelisting."""
        config = RateLimitConfig(whitelisted_ips=["127.0.0.1", "10.0.0.1"])
        assert config.is_ip_whitelisted("127.0.0.1") is True
        assert config.is_ip_whitelisted("192.168.1.1") is False


class TestRateLimitMiddleware:
    """Test rate limiting middleware integration."""

    @pytest.mark.asyncio
    async def test_middleware_allows_requests_within_limit(self):
        """Verify middleware allows requests within rate limit."""
        config = RateLimitConfig(
            per_ip_rules=[RateLimitRule(requests=5, window_seconds=60, path_pattern="*")]
        )
        storage = InMemoryRateLimitStorage()
        middleware = RateLimitMiddleware(app=None, config=config, storage=storage)

        # Mock request
        request = Mock(spec=Request)
        request.url.path = "/api/v1/test"
        request.client.host = "192.168.1.1"
        request.headers.get = Mock(return_value=None)
        request.state = Mock()
        request.state.user_id = None
        request.state.user_tier = 0

        # Mock call_next
        async def mock_call_next(req):
            response = Response()
            return response

        # Make 5 requests (should all be allowed)
        for i in range(5):
            response = await middleware.dispatch(request, mock_call_next)
            assert response.status_code == 200
            assert "X-RateLimit-Limit" in response.headers
            assert response.headers["X-RateLimit-Limit"] == "5"
            assert response.headers["X-RateLimit-Remaining"] == str(4 - i)

    @pytest.mark.asyncio
    async def test_middleware_blocks_requests_over_limit(self):
        """Verify middleware blocks requests exceeding rate limit."""
        config = RateLimitConfig(
            per_ip_rules=[RateLimitRule(requests=3, window_seconds=60, path_pattern="*")]
        )
        storage = InMemoryRateLimitStorage()
        middleware = RateLimitMiddleware(app=None, config=config, storage=storage)

        # Mock request
        request = Mock(spec=Request)
        request.url.path = "/api/v1/test"
        request.client.host = "192.168.1.1"
        request.headers.get = Mock(return_value=None)
        request.state = Mock()
        request.state.user_id = None

        # Mock call_next
        async def mock_call_next(req):
            return Response()

        # Make 3 requests (allowed)
        for _ in range(3):
            response = await middleware.dispatch(request, mock_call_next)
            assert response.status_code == 200

        # 4th request should be blocked
        response = await middleware.dispatch(request, mock_call_next)
        assert response.status_code == 429
        assert "Retry-After" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert response.headers["X-RateLimit-Remaining"] == "0"

    @pytest.mark.asyncio
    async def test_middleware_respects_whitelisted_ips(self):
        """Verify whitelisted IPs bypass rate limiting."""
        config = RateLimitConfig(
            per_ip_rules=[RateLimitRule(requests=2, window_seconds=60, path_pattern="*")],
            whitelisted_ips=["127.0.0.1"],
        )
        storage = InMemoryRateLimitStorage()
        middleware = RateLimitMiddleware(app=None, config=config, storage=storage)

        # Mock request from whitelisted IP
        request = Mock(spec=Request)
        request.url.path = "/api/v1/test"
        request.client.host = "127.0.0.1"
        request.headers.get = Mock(return_value=None)

        # Mock call_next
        async def mock_call_next(req):
            return Response()

        # Make 10 requests (all should be allowed despite limit=2)
        for _ in range(10):
            response = await middleware.dispatch(request, mock_call_next)
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_middleware_blocks_blocked_ips(self):
        """Verify blocked IPs are denied access."""
        config = RateLimitConfig(blocked_ips=["192.168.1.100"])
        middleware = RateLimitMiddleware(app=None, config=config, storage=InMemoryRateLimitStorage())

        # Mock request from blocked IP
        request = Mock(spec=Request)
        request.url.path = "/api/v1/test"
        request.client.host = "192.168.1.100"
        request.headers.get = Mock(return_value=None)

        # Mock call_next
        async def mock_call_next(req):
            return Response()

        # Request should be blocked with 403
        response = await middleware.dispatch(request, mock_call_next)
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_middleware_per_user_rate_limiting(self):
        """Verify per-user rate limiting works."""
        config = RateLimitConfig(
            per_user_rules=[RateLimitRule(requests=3, window_seconds=60, path_pattern="*", tier=0)]
        )
        storage = InMemoryRateLimitStorage()
        middleware = RateLimitMiddleware(app=None, config=config, storage=storage)

        # Mock authenticated request
        request = Mock(spec=Request)
        request.url.path = "/api/v1/test"
        request.client.host = "192.168.1.1"
        request.headers.get = Mock(return_value=None)
        request.state = Mock()
        request.state.user_id = "user_a"
        request.state.user_tier = 0

        # Mock call_next
        async def mock_call_next(req):
            return Response()

        # Make 3 requests (allowed)
        for _ in range(3):
            response = await middleware.dispatch(request, mock_call_next)
            assert response.status_code == 200

        # 4th request should be blocked
        response = await middleware.dispatch(request, mock_call_next)
        assert response.status_code == 429

    @pytest.mark.asyncio
    async def test_middleware_different_users_separate_limits(self):
        """Verify different users have separate rate limits."""
        config = RateLimitConfig(
            per_user_rules=[RateLimitRule(requests=2, window_seconds=60, path_pattern="*", tier=0)]
        )
        storage = InMemoryRateLimitStorage()
        middleware = RateLimitMiddleware(app=None, config=config, storage=storage)

        # Mock call_next
        async def mock_call_next(req):
            return Response()

        # User A makes 2 requests (fills limit)
        request_a = Mock(spec=Request)
        request_a.url.path = "/api/v1/test"
        request_a.client.host = "192.168.1.1"
        request_a.headers.get = Mock(return_value=None)
        request_a.state = Mock()
        request_a.state.user_id = "user_a"
        request_a.state.user_tier = 0

        for _ in range(2):
            response = await middleware.dispatch(request_a, mock_call_next)
            assert response.status_code == 200

        # User A's 3rd request blocked
        response = await middleware.dispatch(request_a, mock_call_next)
        assert response.status_code == 429

        # User B should still be allowed (separate limit)
        request_b = Mock(spec=Request)
        request_b.url.path = "/api/v1/test"
        request_b.client.host = "192.168.1.2"
        request_b.headers.get = Mock(return_value=None)
        request_b.state = Mock()
        request_b.state.user_id = "user_b"
        request_b.state.user_tier = 0

        response = await middleware.dispatch(request_b, mock_call_next)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_middleware_extracts_ip_from_x_forwarded_for(self):
        """Verify middleware extracts real IP from X-Forwarded-For header."""
        config = RateLimitConfig(
            per_ip_rules=[RateLimitRule(requests=2, window_seconds=60, path_pattern="*")]
        )
        storage = InMemoryRateLimitStorage()
        middleware = RateLimitMiddleware(app=None, config=config, storage=storage)

        # Mock request with X-Forwarded-For header
        request = Mock(spec=Request)
        request.url.path = "/api/v1/test"
        request.client.host = "10.0.0.1"  # Proxy IP
        request.headers.get = lambda key: "203.0.113.1, 10.0.0.1" if key == "X-Forwarded-For" else None
        request.state = Mock()
        request.state.user_id = None

        # Mock call_next
        async def mock_call_next(req):
            return Response()

        # Make 2 requests (fills limit for 203.0.113.1)
        for _ in range(2):
            response = await middleware.dispatch(request, mock_call_next)
            assert response.status_code == 200

        # 3rd request should be blocked (based on real client IP)
        response = await middleware.dispatch(request, mock_call_next)
        assert response.status_code == 429

    @pytest.mark.asyncio
    async def test_middleware_disabled_bypasses_checks(self):
        """Verify disabled rate limiting allows all requests."""
        config = RateLimitConfig(
            enabled=False, per_ip_rules=[RateLimitRule(requests=1, window_seconds=60, path_pattern="*")]
        )
        storage = InMemoryRateLimitStorage()
        middleware = RateLimitMiddleware(app=None, config=config, storage=storage)

        # Mock request
        request = Mock(spec=Request)
        request.url.path = "/api/v1/test"
        request.client.host = "192.168.1.1"

        # Mock call_next
        async def mock_call_next(req):
            return Response()

        # Make 10 requests (all should be allowed despite limit=1)
        for _ in range(10):
            response = await middleware.dispatch(request, mock_call_next)
            assert response.status_code == 200


class TestRateLimitHeaders:
    """Test rate limit response headers."""

    @pytest.mark.asyncio
    async def test_rate_limit_headers_present(self):
        """Verify rate limit headers are added to responses."""
        config = RateLimitConfig(
            per_ip_rules=[RateLimitRule(requests=10, window_seconds=60, path_pattern="*")]
        )
        storage = InMemoryRateLimitStorage()
        middleware = RateLimitMiddleware(app=None, config=config, storage=storage)

        # Mock request
        request = Mock(spec=Request)
        request.url.path = "/api/v1/test"
        request.client.host = "192.168.1.1"
        request.headers.get = Mock(return_value=None)
        request.state = Mock()
        request.state.user_id = None

        # Mock call_next
        async def mock_call_next(req):
            return Response()

        response = await middleware.dispatch(request, mock_call_next)

        # Verify standard rate limit headers
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers

        assert response.headers["X-RateLimit-Limit"] == "10"
        assert response.headers["X-RateLimit-Remaining"] == "9"

    @pytest.mark.asyncio
    async def test_429_response_includes_retry_after(self):
        """Verify 429 responses include Retry-After header."""
        config = RateLimitConfig(
            per_ip_rules=[RateLimitRule(requests=1, window_seconds=60, path_pattern="*")]
        )
        storage = InMemoryRateLimitStorage()
        middleware = RateLimitMiddleware(app=None, config=config, storage=storage)

        # Mock request
        request = Mock(spec=Request)
        request.url.path = "/api/v1/test"
        request.client.host = "192.168.1.1"
        request.headers.get = Mock(return_value=None)
        request.state = Mock()
        request.state.user_id = None

        # Mock call_next
        async def mock_call_next(req):
            return Response()

        # First request allowed
        await middleware.dispatch(request, mock_call_next)

        # Second request blocked
        response = await middleware.dispatch(request, mock_call_next)

        assert response.status_code == 429
        assert "Retry-After" in response.headers
        assert int(response.headers["Retry-After"]) > 0


class TestEndToEndRateLimiting:
    """End-to-end tests for complete rate limiting scenarios."""

    @pytest.mark.asyncio
    async def test_tier_based_limits_enforced(self):
        """Verify different tiers have different limits."""
        config = RateLimitConfig(
            per_user_rules=[
                RateLimitRule(requests=2, window_seconds=60, path_pattern="*", tier=0),  # Free: 2/hr
                RateLimitRule(requests=5, window_seconds=60, path_pattern="*", tier=1),  # Basic: 5/hr
            ]
        )
        storage = InMemoryRateLimitStorage()
        middleware = RateLimitMiddleware(app=None, config=config, storage=storage)

        async def mock_call_next(req):
            return Response()

        # Tier 0 user (free)
        request_t0 = Mock(spec=Request)
        request_t0.url.path = "/api/v1/test"
        request_t0.client.host = "192.168.1.1"
        request_t0.headers.get = Mock(return_value=None)
        request_t0.state = Mock()
        request_t0.state.user_id = "user_free"
        request_t0.state.user_tier = 0

        # Free user: 2 allowed
        for _ in range(2):
            response = await middleware.dispatch(request_t0, mock_call_next)
            assert response.status_code == 200

        # Free user: 3rd blocked
        response = await middleware.dispatch(request_t0, mock_call_next)
        assert response.status_code == 429

        # Tier 1 user (basic)
        request_t1 = Mock(spec=Request)
        request_t1.url.path = "/api/v1/test"
        request_t1.client.host = "192.168.1.2"
        request_t1.headers.get = Mock(return_value=None)
        request_t1.state = Mock()
        request_t1.state.user_id = "user_basic"
        request_t1.state.user_tier = 1

        # Basic user: 5 allowed
        for _ in range(5):
            response = await middleware.dispatch(request_t1, mock_call_next)
            assert response.status_code == 200

        # Basic user: 6th blocked
        response = await middleware.dispatch(request_t1, mock_call_next)
        assert response.status_code == 429

    @pytest.mark.asyncio
    async def test_path_specific_limits_stricter(self):
        """Verify path-specific limits override global limits."""
        config = RateLimitConfig(
            per_user_rules=[
                RateLimitRule(requests=100, window_seconds=60, path_pattern="*", tier=0),
                RateLimitRule(
                    requests=2, window_seconds=60, path_pattern="/feedback/*", tier=0
                ),  # Stricter for feedback
            ]
        )
        storage = InMemoryRateLimitStorage()
        middleware = RateLimitMiddleware(app=None, config=config, storage=storage)

        async def mock_call_next(req):
            return Response()

        # Mock user request
        request = Mock(spec=Request)
        request.client.host = "192.168.1.1"
        request.headers.get = Mock(return_value=None)
        request.state = Mock()
        request.state.user_id = "user_a"
        request.state.user_tier = 0

        # Feedback endpoint: 2 allowed
        request.url.path = "/feedback/submit"
        for _ in range(2):
            response = await middleware.dispatch(request, mock_call_next)
            assert response.status_code == 200

        # Feedback endpoint: 3rd blocked
        response = await middleware.dispatch(request, mock_call_next)
        assert response.status_code == 429

        # Regular endpoint: still has 100 - 0 = 100 remaining
        request.url.path = "/api/v1/query"
        response = await middleware.dispatch(request, mock_call_next)
        assert response.status_code == 200
