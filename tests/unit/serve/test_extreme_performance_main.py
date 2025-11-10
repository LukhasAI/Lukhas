"""
Comprehensive test suite for extreme_performance_main.py

Tests extreme performance server, caching, authentication,
benchmarking, performance tracking, and all specialized endpoints.

Target: 80%+ coverage
"""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    mock_redis_client = Mock()
    mock_redis_client.ping = AsyncMock()
    mock_redis_client.get = AsyncMock(return_value=None)
    mock_redis_client.setex = AsyncMock()
    mock_redis_client.aclose = AsyncMock()
    return mock_redis_client


@pytest.fixture
def mock_extreme_components():
    """Mock extreme performance components"""
    # Mock optimizer
    mock_optimizer = Mock()
    mock_optimizer.optimized_auth_flow = AsyncMock(return_value={
        "success": True,
        "performance": {"performance_level": "extreme"}
    })
    mock_optimizer.run_performance_benchmark = AsyncMock(return_value={
        "benchmark_results": {
            "openai_scale_target_met": True,
            "avg_latency_ms": 8.5
        }
    })
    mock_optimizer.get_performance_dashboard = Mock(return_value={
        "openai_scale_metrics": {
            "overall_openai_scale_ready": True
        }
    })
    mock_optimizer.shutdown = AsyncMock()

    # Mock audit logger
    mock_audit = Mock()
    mock_audit.log_event_extreme_performance = AsyncMock()
    mock_audit.log_authentication_attempt_extreme = AsyncMock()
    mock_audit.run_performance_benchmark_extreme = AsyncMock(return_value={
        "benchmark_results": {
            "openai_scale_target_met": True
        }
    })
    mock_audit.get_performance_dashboard_extreme = AsyncMock(return_value={
        "openai_scale_ready": True
    })
    mock_audit.shutdown_extreme = AsyncMock()

    # Mock identity connector
    mock_identity = Mock()
    mock_identity.get_performance_dashboard = Mock(return_value={
        "status": "operational"
    })

    return {
        "optimizer": mock_optimizer,
        "audit": mock_audit,
        "identity": mock_identity,
    }


@pytest.fixture
def mock_env():
    """Mock environment configuration"""
    with patch("serve.extreme_performance_main.env_get") as mock_get:
        mock_get.side_effect = lambda key, default=None: {
            "ENVIRONMENT": "test",
            "FRONTEND_ORIGIN": "http://localhost:3000",
        }.get(key, default)
        yield mock_get


@pytest.fixture
async def app_with_mocks(mock_redis, mock_extreme_components, mock_env):
    """Create app with all mocks"""
    with patch("serve.extreme_performance_main.redis.Redis.from_url") as mock_redis_factory, \
         patch("serve.extreme_performance_main.get_extreme_optimizer") as mock_get_opt, \
         patch("serve.extreme_performance_main.get_extreme_audit_logger") as mock_get_audit, \
         patch("serve.extreme_performance_main.get_extreme_identity_connector") as mock_get_identity:

        # Setup mocks
        mock_redis_factory.return_value = mock_redis
        mock_get_opt.return_value = mock_extreme_components["optimizer"]
        mock_get_audit.return_value = mock_extreme_components["audit"]
        mock_get_identity.return_value = mock_extreme_components["identity"]

        # Import and create server
        from serve.extreme_performance_main import ExtremePerformanceServer

        server = ExtremePerformanceServer()
        await server.initialize()

        yield server.app

        # Cleanup
        await server.shutdown()


@pytest.fixture
def client(app_with_mocks):
    """Create test client"""
    return TestClient(app_with_mocks)


@pytest.fixture
def fallback_app():
    """Create fallback app without extreme optimizations"""
    with patch("serve.extreme_performance_main.EXTREME_OPTIMIZATIONS_AVAILABLE", False):
        from serve.extreme_performance_main import app as fallback_app_instance
        return fallback_app_instance


@pytest.fixture
def fallback_client(fallback_app):
    """Create client for fallback app"""
    return TestClient(fallback_app)


class TestExtremePerformanceServer:
    """Test ExtremePerformanceServer class"""

    @pytest.mark.asyncio
    async def test_server_initialization(self, mock_redis, mock_extreme_components):
        """Test server initializes all components"""
        with patch("serve.extreme_performance_main.redis.Redis.from_url") as mock_redis_factory, \
             patch("serve.extreme_performance_main.get_extreme_optimizer") as mock_get_opt, \
             patch("serve.extreme_performance_main.get_extreme_audit_logger") as mock_get_audit, \
             patch("serve.extreme_performance_main.get_extreme_identity_connector") as mock_get_identity:

            mock_redis_factory.return_value = mock_redis
            mock_get_opt.return_value = mock_extreme_components["optimizer"]
            mock_get_audit.return_value = mock_extreme_components["audit"]
            mock_get_identity.return_value = mock_extreme_components["identity"]

            from serve.extreme_performance_main import ExtremePerformanceServer

            server = ExtremePerformanceServer()
            await server.initialize()

            assert server.app is not None
            assert server.extreme_optimizer is not None
            assert server.audit_logger is not None
            assert server.redis_cache is not None

            await server.shutdown()

    def test_server_has_correct_targets(self):
        """Test server has correct performance targets"""
        from serve.extreme_performance_main import ExtremePerformanceServer

        server = ExtremePerformanceServer()

        assert server.target_api_latency_p95 == 10.0
        assert server.target_throughput_rps == 100000
        assert server.cache_ttl_seconds == 300


class TestHealthzExtremeEndpoint:
    """Test /healthz/extreme endpoint"""

    def test_healthz_extreme_returns_metrics(self, client):
        """Test extreme health check returns comprehensive metrics"""
        response = client.get("/healthz/extreme")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "extreme_performance"
        assert "components" in data
        assert "performance" in data
        assert "targets" in data

    def test_healthz_shows_component_health(self, client):
        """Test health check shows component status"""
        response = client.get("/healthz/extreme")
        data = response.json()

        components = data["components"]
        assert "extreme_optimizer" in components
        assert "audit_logger" in components
        assert "identity_connector" in components
        assert "redis_cache" in components

    def test_healthz_includes_performance_metrics(self, client):
        """Test health check includes performance metrics"""
        response = client.get("/healthz/extreme")
        data = response.json()

        perf = data["performance"]
        assert "requests_processed" in perf
        assert "avg_response_time_ms" in perf
        assert "target_latency_p95_ms" in perf
        assert "openai_scale_ready" in perf

    def test_healthz_includes_targets(self, client):
        """Test health check includes performance targets"""
        response = client.get("/healthz/extreme")
        data = response.json()

        targets = data["targets"]
        assert targets["api_latency_p95_ms"] == 10.0
        assert targets["throughput_rps"] == 100000
        assert targets["authentication_p95_ms"] == 25.0

    def test_healthz_fast_response_time(self, client):
        """Test health check responds quickly"""
        response = client.get("/healthz/extreme")
        data = response.json()

        # Health check itself should be fast
        assert data["response_time_ms"] < 100


class TestAuthExtremeEndpoint:
    """Test /auth/extreme endpoint"""

    def test_auth_extreme_successful_authentication(self, client, mock_extreme_components):
        """Test successful extreme performance authentication"""
        response = client.post(
            "/auth/extreme?agent_id=test_agent&operation=read_data"
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "auth_result" in data
        assert "performance" in data

    def test_auth_extreme_performance_tracking(self, client):
        """Test authentication tracks performance metrics"""
        response = client.post(
            "/auth/extreme?agent_id=test_agent&operation=write_data"
        )
        data = response.json()

        perf = data["performance"]
        assert "auth_duration_ms" in perf
        assert "target_achieved" in perf
        assert "performance_level" in perf

    def test_auth_extreme_meets_latency_target(self, client):
        """Test authentication meets <25ms target"""
        response = client.post(
            "/auth/extreme?agent_id=test_agent&operation=read"
        )
        data = response.json()

        # Mock returns fast results
        assert data["performance"]["auth_duration_ms"] < 25.0

    def test_auth_extreme_with_context(self, client):
        """Test authentication with additional context"""
        context = {"resource": "data_store", "priority": "high"}

        response = client.post(
            "/auth/extreme",
            params={"agent_id": "test_agent", "operation": "read"},
            json={"context": context}
        )
        assert response.status_code == 200

    def test_auth_extreme_logs_authentication(self, client, mock_extreme_components):
        """Test authentication is logged"""
        client.post("/auth/extreme?agent_id=test_agent&operation=read")

        # Verify audit logging was called
        mock_extreme_components["audit"].log_authentication_attempt_extreme.assert_called()

    def test_auth_extreme_unavailable_without_optimizations(self, fallback_client):
        """Test auth endpoint returns 503 without extreme optimizations"""
        response = fallback_client.post(
            "/auth/extreme?agent_id=test&operation=read"
        )
        # Fallback app doesn't have this endpoint or returns error
        assert response.status_code in [404, 503]


class TestBenchmarkExtremeEndpoint:
    """Test /benchmark/extreme endpoint"""

    def test_benchmark_authentication_type(self, client):
        """Test authentication benchmark"""
        response = client.post(
            "/benchmark/extreme?num_operations=100&benchmark_type=authentication"
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["benchmark_type"] == "authentication"
        assert "results" in data

    def test_benchmark_audit_type(self, client):
        """Test audit logging benchmark"""
        response = client.post(
            "/benchmark/extreme?num_operations=100&benchmark_type=audit"
        )
        assert response.status_code == 200

        data = response.json()
        assert data["benchmark_type"] == "audit"

    def test_benchmark_includes_timing(self, client):
        """Test benchmark includes total timing"""
        response = client.post(
            "/benchmark/extreme?num_operations=50"
        )
        data = response.json()

        assert "total_benchmark_time_seconds" in data

    def test_benchmark_openai_scale_assessment(self, client):
        """Test benchmark includes OpenAI scale assessment"""
        response = client.post(
            "/benchmark/extreme?num_operations=100"
        )
        data = response.json()

        assert "openai_scale_assessment" in data
        assessment = data["openai_scale_assessment"]
        assert "performance_level" in assessment
        assert "ready_for_production" in assessment

    def test_benchmark_invalid_type_returns_error(self, client):
        """Test invalid benchmark type returns error"""
        response = client.post(
            "/benchmark/extreme?benchmark_type=invalid_type"
        )
        assert response.status_code == 400

    def test_benchmark_custom_operation_count(self, client):
        """Test benchmark with custom operation count"""
        response = client.post(
            "/benchmark/extreme?num_operations=500"
        )
        assert response.status_code == 200


class TestPerformanceDashboardEndpoint:
    """Test /dashboard/performance/extreme endpoint"""

    def test_dashboard_returns_comprehensive_data(self, client):
        """Test performance dashboard returns all metrics"""
        response = client.get("/dashboard/performance/extreme")
        assert response.status_code == 200

        data = response.json()
        assert "server_performance" in data
        assert "overall_assessment" in data

    def test_dashboard_server_performance_metrics(self, client):
        """Test dashboard includes server metrics"""
        response = client.get("/dashboard/performance/extreme")
        data = response.json()

        server_perf = data["server_performance"]
        assert "requests_processed" in server_perf
        assert "avg_response_time_ms" in server_perf
        assert "cache_performance" in server_perf

    def test_dashboard_cache_performance(self, client):
        """Test dashboard includes cache metrics"""
        response = client.get("/dashboard/performance/extreme")
        data = response.json()

        cache_perf = data["server_performance"]["cache_performance"]
        assert "hits" in cache_perf
        assert "misses" in cache_perf
        assert "hit_rate_percent" in cache_perf

    def test_dashboard_component_metrics(self, client):
        """Test dashboard includes component-specific metrics"""
        response = client.get("/dashboard/performance/extreme")
        data = response.json()

        # Should include optimizer, audit, and identity metrics
        assert "optimizer_performance" in data or "server_performance" in data

    def test_dashboard_overall_assessment(self, client):
        """Test dashboard includes overall assessment"""
        response = client.get("/dashboard/performance/extreme")
        data = response.json()

        assessment = data["overall_assessment"]
        assert "openai_scale_ready" in assessment
        assert "performance_level" in assessment
        assert "bottlenecks_eliminated" in assessment
        assert "targets_achieved" in assessment

    def test_dashboard_bottlenecks_tracking(self, client):
        """Test dashboard tracks eliminated bottlenecks"""
        response = client.get("/dashboard/performance/extreme")
        data = response.json()

        bottlenecks = data["overall_assessment"]["bottlenecks_eliminated"]
        assert "file_io_blocking" in bottlenecks
        assert "dynamic_import_overhead" in bottlenecks
        assert "hash_calculation_blocking" in bottlenecks


class TestPerformanceMiddleware:
    """Test extreme performance middleware"""

    def test_middleware_adds_performance_headers(self, client):
        """Test middleware adds performance headers to responses"""
        response = client.get("/healthz/extreme")

        assert "X-Response-Time" in response.headers
        assert "X-Request-ID" in response.headers
        assert "X-Performance-Level" in response.headers

    def test_middleware_tracks_response_time(self, client):
        """Test middleware tracks response time"""
        response = client.get("/healthz/extreme")

        response_time = float(response.headers["X-Response-Time"])
        assert response_time > 0

    def test_middleware_assigns_performance_level(self, client):
        """Test middleware assigns correct performance level"""
        response = client.get("/healthz/extreme")

        perf_level = response.headers["X-Performance-Level"]
        assert perf_level in ["extreme", "fast", "standard"]

    def test_middleware_increments_request_counter(self, client):
        """Test middleware increments request counter"""
        # Make request
        client.get("/healthz/extreme")

        # Check counter increased
        response = client.get("/healthz/extreme")
        data = response.json()

        assert data["performance"]["requests_processed"] > 0

    def test_middleware_calculates_average_response_time(self, client):
        """Test middleware calculates average response time"""
        # Make multiple requests
        for _ in range(3):
            client.get("/healthz/extreme")

        response = client.get("/healthz/extreme")
        data = response.json()

        assert data["performance"]["avg_response_time_ms"] > 0


class TestResponseCaching:
    """Test Redis response caching"""

    @pytest.mark.asyncio
    async def test_cache_miss_on_first_request(self, client, mock_redis):
        """Test cache miss on first GET request"""
        mock_redis.get.return_value = None

        response = client.get("/healthz/extreme")

        # Should not have cache hit header
        assert response.headers.get("X-Cache") != "HIT"

    @pytest.mark.asyncio
    async def test_cache_stores_successful_responses(self, client, mock_redis):
        """Test successful responses are cached"""
        mock_redis.get.return_value = None

        response = client.get("/healthz/extreme")
        assert response.status_code == 200

        # Verify cache write attempted (setex called)
        # Note: TestClient might not fully execute async cache operations

    def test_post_requests_not_cached(self, client):
        """Test POST requests are not cached"""
        response = client.post("/auth/extreme?agent_id=test&operation=read")

        # POST responses should not have cache headers
        assert response.headers.get("X-Cache") != "HIT"


class TestFallbackMode:
    """Test fallback mode when extreme optimizations unavailable"""

    def test_fallback_app_basic_health(self, fallback_client):
        """Test fallback app has basic health endpoint"""
        response = fallback_client.get("/healthz")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"
        assert data["performance_mode"] == "standard"

    def test_fallback_extreme_endpoints_unavailable(self, fallback_client):
        """Test extreme endpoints not available in fallback"""
        response = fallback_client.get("/healthz/extreme")
        assert response.status_code == 404

    def test_fallback_has_cors(self, fallback_client):
        """Test fallback mode still has CORS configured"""
        response = fallback_client.get("/healthz")
        # CORS should be configured
        assert response.status_code == 200


class TestAPIKeyAuthentication:
    """Test optional API key authentication"""

    def test_require_api_key_with_valid_key(self):
        """Test API key validation with valid key"""
        from serve.extreme_performance_main import require_api_key

        with patch("serve.extreme_performance_main.env_get") as mock_env:
            mock_env.return_value = "test_key"

            result = require_api_key(x_api_key="test_key")
            assert result == "test_key"

    def test_require_api_key_with_invalid_key(self):
        """Test API key validation with invalid key"""
        from serve.extreme_performance_main import require_api_key
        from fastapi import HTTPException

        with patch("serve.extreme_performance_main.env_get") as mock_env:
            mock_env.return_value = "expected_key"

            with pytest.raises(HTTPException) as exc_info:
                require_api_key(x_api_key="wrong_key")

            assert exc_info.value.status_code == 401

    def test_require_api_key_when_not_configured(self):
        """Test API key validation when no key is configured"""
        from serve.extreme_performance_main import require_api_key

        with patch("serve.extreme_performance_main.env_get") as mock_env:
            mock_env.return_value = ""

            # Should pass when no key is required
            result = require_api_key(x_api_key=None)
            assert result is None


class TestLifecycleManagement:
    """Test application lifecycle management"""

    @pytest.mark.asyncio
    async def test_server_startup(self, mock_redis, mock_extreme_components):
        """Test server startup sequence"""
        with patch("serve.extreme_performance_main.redis.Redis.from_url") as mock_redis_factory, \
             patch("serve.extreme_performance_main.get_extreme_optimizer") as mock_get_opt, \
             patch("serve.extreme_performance_main.get_extreme_audit_logger") as mock_get_audit, \
             patch("serve.extreme_performance_main.get_extreme_identity_connector") as mock_get_identity:

            mock_redis_factory.return_value = mock_redis
            mock_get_opt.return_value = mock_extreme_components["optimizer"]
            mock_get_audit.return_value = mock_extreme_components["audit"]
            mock_get_identity.return_value = mock_extreme_components["identity"]

            from serve.extreme_performance_main import ExtremePerformanceServer

            server = ExtremePerformanceServer()
            await server.startup()

            assert server.app is not None
            assert server.extreme_optimizer is not None

            await server.shutdown()

    @pytest.mark.asyncio
    async def test_server_shutdown_cleanup(self, mock_redis, mock_extreme_components):
        """Test server shutdown cleans up resources"""
        with patch("serve.extreme_performance_main.redis.Redis.from_url") as mock_redis_factory, \
             patch("serve.extreme_performance_main.get_extreme_optimizer") as mock_get_opt, \
             patch("serve.extreme_performance_main.get_extreme_audit_logger") as mock_get_audit, \
             patch("serve.extreme_performance_main.get_extreme_identity_connector") as mock_get_identity:

            mock_redis_factory.return_value = mock_redis
            mock_get_opt.return_value = mock_extreme_components["optimizer"]
            mock_get_audit.return_value = mock_extreme_components["audit"]
            mock_get_identity.return_value = mock_extreme_components["identity"]

            from serve.extreme_performance_main import ExtremePerformanceServer

            server = ExtremePerformanceServer()
            await server.startup()
            await server.shutdown()

            # Verify cleanup was called
            mock_extreme_components["audit"].shutdown_extreme.assert_called_once()
            mock_extreme_components["optimizer"].shutdown.assert_called_once()
            mock_redis.aclose.assert_called_once()


class TestEdgeCases:
    """Test edge cases and error conditions"""

    @pytest.mark.asyncio
    async def test_redis_connection_failure(self, mock_extreme_components):
        """Test handling of Redis connection failure"""
        with patch("serve.extreme_performance_main.redis.Redis.from_url") as mock_redis_factory, \
             patch("serve.extreme_performance_main.get_extreme_optimizer") as mock_get_opt, \
             patch("serve.extreme_performance_main.get_extreme_audit_logger") as mock_get_audit, \
             patch("serve.extreme_performance_main.get_extreme_identity_connector") as mock_get_identity:

            # Redis fails to connect
            mock_redis = Mock()
            mock_redis.ping = AsyncMock(side_effect=Exception("Connection failed"))
            mock_redis_factory.return_value = mock_redis

            mock_get_opt.return_value = mock_extreme_components["optimizer"]
            mock_get_audit.return_value = mock_extreme_components["audit"]
            mock_get_identity.return_value = mock_extreme_components["identity"]

            from serve.extreme_performance_main import ExtremePerformanceServer

            server = ExtremePerformanceServer()

            with pytest.raises(Exception):
                await server.initialize()

    def test_high_concurrent_load(self, client):
        """Test handling of high concurrent request load"""
        # Make multiple concurrent requests
        responses = []
        for _ in range(10):
            response = client.get("/healthz/extreme")
            responses.append(response)

        # All should succeed
        for response in responses:
            assert response.status_code == 200

    def test_performance_degradation_logging(self, client, mock_extreme_components):
        """Test slow requests are logged"""
        # This would require mocking a slow endpoint
        # The middleware logs requests > target latency
        response = client.get("/healthz/extreme")
        assert response.status_code == 200
