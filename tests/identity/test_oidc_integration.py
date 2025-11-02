#!/usr/bin/env python3
"""
LUKHAS OIDC Integration Tests
T4/0.01% Excellence Standard

Integration tests for complete OIDC/OAuth2 flows with real components.
Tests end-to-end functionality, security hardening, and performance.
"""

import asyncio
import time

import pytest

# Import components to test
from identity.jwks_cache import JWKSCache
from identity.metrics_collector import ServiceMetricsCollector
from identity.rate_limiting import RateLimiter, RateLimitType
from identity.security_hardening import SecurityHardeningManager, ThreatLevel


@pytest.fixture
async def jwks_cache():
    """Create real JWKS cache instance"""
    cache = JWKSCache(max_size=100, default_ttl_seconds=300)
    await cache.start()
    yield cache
    await cache.stop()


@pytest.fixture
def rate_limiter():
    """Create real rate limiter instance"""
    return RateLimiter()


@pytest.fixture
def security_manager():
    """Create real security hardening manager"""
    return SecurityHardeningManager()


@pytest.fixture
def metrics_collector():
    """Create real metrics collector"""
    return ServiceMetricsCollector("test_identity")


class TestJWKSCacheIntegration:
    """Integration tests for JWKS caching system"""

    @pytest.mark.asyncio
    async def test_cache_performance_sub_100ms(self, jwks_cache):
        """Test JWKS cache meets sub-100ms performance requirement"""
        # Populate cache
        test_jwks = {
            "keys": [
                {
                    "kty": "RSA",
                    "kid": "test-key-1",
                    "use": "sig",
                    "n": "test-n-value" * 100,  # Make it realistic size
                    "e": "AQAB"
                }
            ]
        }
        jwks_cache.put("test_key", test_jwks)

        # Measure cache retrieval performance
        times = []
        for _ in range(100):  # Test with 100 requests
            start = time.perf_counter()
            result, cache_hit = jwks_cache.get("test_key")
            end = time.perf_counter()

            assert cache_hit is True
            assert result is not None
            times.append((end - start) * 1000)  # Convert to ms

        # Calculate p95 latency
        p95_latency = sorted(times)[95]  # 95th percentile
        assert p95_latency < 100, f"JWKS cache p95 latency {p95_latency}ms exceeds 100ms"

        # Verify cache statistics
        stats = jwks_cache.get_stats()
        assert stats.hits == 100
        assert stats.misses == 0
        assert stats.hit_rate == 1.0

    @pytest.mark.asyncio
    async def test_cache_ttl_expiration(self, jwks_cache):
        """Test cache TTL and expiration handling"""
        # Put item with short TTL
        test_jwks = {"keys": [{"kid": "expiring-key"}]}
        jwks_cache.put("expiring_key", test_jwks, ttl_seconds=1)

        # Should be available immediately
        result, cache_hit = jwks_cache.get("expiring_key")
        assert cache_hit is True
        assert result["keys"][0]["kid"] == "expiring-key"

        # Wait for expiration
        await asyncio.sleep(1.1)

        # Should be expired now
        result, cache_hit = jwks_cache.get("expiring_key")
        assert cache_hit is False
        assert result is None

    @pytest.mark.asyncio
    async def test_cache_lru_eviction(self, jwks_cache):
        """Test LRU eviction when cache is full"""
        # Fill cache to capacity (assuming max_size=100 from fixture)
        for i in range(105):  # Exceed capacity
            jwks_cache.put(f"key_{i}", {"keys": [{"kid": f"key_{i}"}]})

        # First keys should be evicted
        result, cache_hit = jwks_cache.get("key_0")
        assert cache_hit is False  # Should be evicted

        # Recent keys should still be there
        result, cache_hit = jwks_cache.get("key_104")
        assert cache_hit is True

        # Check eviction statistics
        stats = jwks_cache.get_stats()
        assert stats.evictions > 0


class TestRateLimitingIntegration:
    """Integration tests for rate limiting system"""

    @pytest.mark.asyncio
    async def test_rate_limiting_enforcement(self, rate_limiter):
        """Test rate limiting enforcement with real limits"""
        client_ip = "192.168.1.100"

        # First request should be allowed
        allowed, metadata = await rate_limiter.check_rate_limit(
            client_ip, RateLimitType.WEBAUTHN_REGISTRATION
        )
        assert allowed is True
        assert metadata["allowed"] is True

        # Exhaust the rate limit (5 req/min for registration)
        for _ in range(4):  # 4 more requests (total 5)
            allowed, metadata = await rate_limiter.check_rate_limit(
                client_ip, RateLimitType.WEBAUTHN_REGISTRATION
            )
            assert allowed is True

        # Next request should be rate limited
        allowed, metadata = await rate_limiter.check_rate_limit(
            client_ip, RateLimitType.WEBAUTHN_REGISTRATION
        )
        assert allowed is False
        assert metadata["error"] == "rate_limit_exceeded"
        assert "retry_after" in metadata

    @pytest.mark.asyncio
    async def test_rate_limiting_per_user_context(self, rate_limiter):
        """Test rate limiting with user context"""
        client_ip = "192.168.1.101"

        # Test with user context
        context = {"user_id": "user123"}

        # Should track separately per user
        allowed, metadata = await rate_limiter.check_rate_limit(
            client_ip, RateLimitType.WEBAUTHN_AUTHENTICATION, context
        )
        assert allowed is True

        # Different user should have separate limit
        context2 = {"user_id": "user456"}
        allowed, metadata = await rate_limiter.check_rate_limit(
            client_ip, RateLimitType.WEBAUTHN_AUTHENTICATION, context2
        )
        assert allowed is True

    @pytest.mark.asyncio
    async def test_rate_limiting_progressive_penalties(self, rate_limiter):
        """Test progressive penalties for repeat violators"""
        client_ip = "192.168.1.102"

        # Trigger multiple violations
        for violation in range(3):
            # Exhaust limit
            for _ in range(6):  # Exceed 5 req/min limit
                await rate_limiter.check_rate_limit(
                    client_ip, RateLimitType.WEBAUTHN_REGISTRATION
                )

            # Check violation count increases
            status = rate_limiter.get_client_status(
                client_ip, RateLimitType.WEBAUTHN_REGISTRATION
            )
            assert status["violation_count"] >= violation

        # Should eventually be locked out
        final_status = rate_limiter.get_client_status(
            client_ip, RateLimitType.WEBAUTHN_REGISTRATION
        )
        assert final_status["is_locked_out"] is True


class TestSecurityHardeningIntegration:
    """Integration tests for security hardening system"""

    @pytest.mark.asyncio
    async def test_comprehensive_security_check(self, security_manager):
        """Test comprehensive security check workflow"""
        # Normal request should pass
        action, report = await security_manager.comprehensive_security_check(
            ip_address="192.168.1.200",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            headers={"Content-Type": "application/json"},
            endpoint="/oauth2/token"
        )

        assert action.value in ["allow", "throttle"]
        assert "security_report" in report or "checks_performed" in report

    @pytest.mark.asyncio
    async def test_suspicious_request_detection(self, security_manager):
        """Test detection of suspicious requests"""
        # Suspicious user agent should trigger higher threat level
        action, report = await security_manager.comprehensive_security_check(
            ip_address="192.168.1.201",
            user_agent="sqlmap/1.4.12",  # Known attack tool
            headers={"X-Scanner": "test", "Content-Type": "application/json"},
            endpoint="/oauth2/authorize"
        )

        # Should at least throttle or block suspicious requests
        assert action.value in ["throttle", "block"]

        if "request_analysis" in report:
            threat_level = report["request_analysis"]["threat_level"]
            assert threat_level in ["medium", "high", "critical"]

    @pytest.mark.asyncio
    async def test_anti_replay_protection(self, security_manager):
        """Test anti-replay protection with nonces"""
        # Generate nonce
        nonce = await security_manager.generate_nonce("user123", "/oauth2/token")
        assert nonce is not None
        assert nonce.startswith("nonce_")

        # First use should succeed
        valid, reason = await security_manager.validate_nonce(nonce, "user123", "/oauth2/token")
        assert valid is True
        assert reason == "valid"

        # Second use should fail (replay attack)
        valid, reason = await security_manager.validate_nonce(nonce, "user123", "/oauth2/token")
        assert valid is False
        assert reason == "nonce_not_found"  # Already consumed


class TestMetricsCollectorIntegration:
    """Integration tests for metrics collection"""

    def test_http_request_metrics(self, metrics_collector):
        """Test HTTP request metrics collection"""
        # Record some requests
        metrics_collector.record_http_request("GET", "/authorize", 200, 0.05, "identity")
        metrics_collector.record_http_request("POST", "/token", 200, 0.03, "identity")
        metrics_collector.record_http_request("GET", "/userinfo", 401, 0.02, "identity")

        # Check performance stats
        stats = metrics_collector.get_performance_stats()
        assert len(stats) >= 3  # At least 3 endpoints tracked

        # Check health metrics
        health = metrics_collector.get_health_metrics()
        assert health["total_requests"] == 3
        assert health["total_errors"] == 1  # One 401 error
        assert health["error_rate_percent"] > 0

    def test_authentication_metrics(self, metrics_collector):
        """Test authentication metrics collection"""
        # Record auth attempts
        metrics_collector.record_auth_attempt("webauthn", "T3", True, "identity")
        metrics_collector.record_auth_attempt("password", "T1", False, "identity")
        metrics_collector.record_auth_attempt("biometric", "T4", True, "identity")

        # Record token operations
        metrics_collector.record_token_operation("exchange", "authorization_code", "client123", True)
        metrics_collector.record_token_operation("refresh", "refresh_token", "client456", False)

        # Metrics should be recorded (exact verification depends on Prometheus integration)
        health = metrics_collector.get_health_metrics()
        assert health["service_name"] == "test_identity"

    def test_security_event_metrics(self, metrics_collector):
        """Test security event metrics collection"""
        from identity.metrics_collector import ThreatLevel

        # Record security events
        metrics_collector.record_security_event(
            "suspicious_user_agent", ThreatLevel.MEDIUM, "blocked"
        )
        metrics_collector.record_security_event(
            "rate_limit_violation", ThreatLevel.LOW, "throttled"
        )
        metrics_collector.record_security_event(
            "replay_attack", ThreatLevel.HIGH, "blocked"
        )

        health = metrics_collector.get_health_metrics()
        assert health["security_events"] == 3

    def test_cache_metrics(self, metrics_collector):
        """Test cache operation metrics"""
        # Record cache operations
        metrics_collector.record_cache_operation("jwks", "get", True)   # Hit
        metrics_collector.record_cache_operation("jwks", "get", False)  # Miss
        metrics_collector.record_cache_operation("jwks", "get", True)   # Hit

        health = metrics_collector.get_health_metrics()
        assert health["cache_hit_rate_percent"] > 50  # 2 hits out of 3


class TestEndToEndOIDCFlow:
    """End-to-end integration tests for complete OIDC flows"""

    @pytest.mark.asyncio
    async def test_complete_authorization_code_flow(self):
        """Test complete OAuth2 authorization code flow"""
        # This would test the full flow:
        # 1. Discovery document retrieval
        # 2. Client registration (if dynamic)
        # 3. Authorization request
        # 4. User authentication
        # 5. Authorization code exchange
        # 6. Token validation
        # 7. UserInfo request

        # For now, we'll test individual components work together
        cache = JWKSCache(max_size=10)
        await cache.start()

        rate_limiter = RateLimiter()
        metrics = ServiceMetricsCollector("integration_test")

        try:
            # Simulate JWKS caching
            test_jwks = {"keys": [{"kid": "test", "kty": "RSA"}]}
            cache.put("test_issuer", test_jwks)

            jwks, hit = cache.get("test_issuer")
            assert hit is True
            assert jwks["keys"][0]["kid"] == "test"

            # Simulate rate limiting
            allowed, _ = await rate_limiter.check_rate_limit(
                "192.168.1.300", RateLimitType.API_GENERAL
            )
            assert allowed is True

            # Record metrics
            metrics.record_http_request("GET", "/.well-known/openid-configuration", 200, 0.02)
            metrics.record_http_request("GET", "/authorize", 302, 0.05)
            metrics.record_http_request("POST", "/token", 200, 0.03)

            # Verify everything worked
            stats = metrics.get_health_metrics()
            assert stats["total_requests"] == 3
            assert stats["error_rate_percent"] == 0

        finally:
            await cache.stop()

    @pytest.mark.asyncio
    async def test_security_integration_under_attack(self):
        """Test system behavior under simulated attack"""
        security_manager = SecurityHardeningManager()
        rate_limiter = RateLimiter()
        metrics = ServiceMetricsCollector("security_test")

        # Simulate attack patterns
        attack_patterns = [
            {
                "ip": "10.0.0.1",
                "user_agent": "sqlmap/1.4.12",
                "headers": {"X-Scanner": "test"}
            },
            {
                "ip": "10.0.0.2",
                "user_agent": "nikto/2.1.6",
                "headers": {"X-Exploit": "attempt"}
            },
            {
                "ip": "10.0.0.3",
                "user_agent": "python-requests/2.25.1",
                "headers": {"Accept": "*/*"}
            }
        ]

        blocked_count = 0
        throttled_count = 0

        for pattern in attack_patterns:
            for _ in range(10):  # Multiple requests from each attacker
                # Security check
                action, report = await security_manager.comprehensive_security_check(
                    ip_address=pattern["ip"],
                    user_agent=pattern["user_agent"],
                    headers=pattern["headers"],
                    endpoint="/oauth2/token"
                )

                # Rate limiting check
                allowed, rate_metadata = await rate_limiter.check_rate_limit(
                    pattern["ip"], RateLimitType.API_GENERAL
                )

                if action.value == "block" or not allowed:
                    blocked_count += 1
                    metrics.record_security_event(
                        "attack_blocked",
                        ThreatLevel.HIGH if action.value == "block" else ThreatLevel.MEDIUM,
                        "blocked"
                    )
                elif action.value == "throttle":
                    throttled_count += 1
                    metrics.record_security_event("attack_throttled", ThreatLevel.MEDIUM, "throttled")

        # Verify system defended against attacks
        assert blocked_count > 0, "System should block some attack attempts"

        health = metrics.get_health_metrics()
        assert health["security_events"] > 0, "Security events should be recorded"

        # Verify legitimate traffic still works
        action, _ = await security_manager.comprehensive_security_check(
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0 (compatible browser)",
            headers={"Accept": "application/json"},
            endpoint="/oauth2/authorize"
        )
        assert action.value == "allow", "Legitimate traffic should still be allowed"


class TestPerformanceBenchmarks:
    """Performance benchmarks for T4/0.01% excellence"""

    @pytest.mark.asyncio
    async def test_sub_100ms_p95_latency_benchmark(self):
        """Benchmark complete request processing under sub-100ms p95"""
        cache = JWKSCache(max_size=1000)
        await cache.start()

        try:
            # Pre-populate cache for realistic scenario
            test_jwks = {
                "keys": [
                    {
                        "kty": "RSA",
                        "kid": f"key_{i}",
                        "use": "sig",
                        "n": "realistic_n_value" * 50,
                        "e": "AQAB"
                    }
                    for i in range(5)
                ]
            }
            cache.put("performance_test", test_jwks)

            # Measure 1000 requests to get reliable p95
            times = []
            for _i in range(1000):
                start = time.perf_counter()

                # Simulate complete request processing
                jwks, hit = cache.get("performance_test")
                assert hit is True
                assert len(jwks["keys"]) == 5

                # Simulate validation (minimal processing)
                validated = all(key.get("kid") for key in jwks["keys"])
                assert validated is True

                end = time.perf_counter()
                times.append((end - start) * 1000)  # Convert to ms

            # Calculate statistics
            times.sort()
            p50 = times[500]
            p95 = times[950]
            p99 = times[990]
            mean = sum(times) / len(times)

            print("Performance metrics:")
            print(f"  Mean: {mean:.2f}ms")
            print(f"  P50:  {p50:.2f}ms")
            print(f"  P95:  {p95:.2f}ms")
            print(f"  P99:  {p99:.2f}ms")

            # T4/0.01% excellence requirement
            assert p95 < 100, f"P95 latency {p95:.2f}ms exceeds 100ms requirement"
            assert p99 < 200, f"P99 latency {p99:.2f}ms should be reasonable"
            assert mean < 50, f"Mean latency {mean:.2f}ms should be well under requirement"

        finally:
            await cache.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])
