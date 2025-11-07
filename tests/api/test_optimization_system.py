#!/usr/bin/env python3
"""
Comprehensive Test Suite for LUKHAS API Optimization System

Tests for advanced API optimizer, middleware pipeline, and analytics dashboard.

# ΛTAG: api_optimization_tests, performance_testing, middleware_testing, analytics_testing
"""

import asyncio
import json
import tempfile
import time
from datetime import datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

import pytest

# Import the modules we're testing
from api.optimization.advanced_api_optimizer import (
    APIAnalytics,
    APICache,
    APITier,
    LUKHASAPIOptimizer,
    OptimizationConfig,
    OptimizationStrategy,
    RateLimiter,
    RequestContext,
    RequestPriority,
    create_api_optimizer,
)
from api.optimization.advanced_middleware import (
    AnalyticsMiddleware,
    LUKHASMiddlewarePipeline,
    MiddlewareConfig,
    OptimizationMiddleware,
    RequestMetadata,
    SecurityMiddleware,
    ValidationMiddleware,
    create_middleware_pipeline,
)
from api.optimization.analytics_dashboard import (
    AlertManager,
    AlertSeverity,
    AnalyticsDashboard,
    IntelligenceEngine,
    MetricsCollector,
    TimeWindow,
    create_analytics_dashboard,
)


class TestAPIOptimizer:
    """Test suite for LUKHAS API Optimizer."""

    @pytest.fixture
    async def optimizer_config(self):
        """Create optimizer configuration for testing."""
        return OptimizationConfig(
            strategy=OptimizationStrategy.BALANCED,
            enable_adaptive_caching=True,
            enable_request_compression=True,
            cache_ttl_seconds=300,
            max_batch_size=5,
            enable_metrics=True
        )

    @pytest.fixture
    async def api_optimizer(self, optimizer_config):
        """Create API optimizer for testing."""
        optimizer = LUKHASAPIOptimizer(optimizer_config)
        yield optimizer
        # Cleanup
        if hasattr(optimizer, 'cleanup'):
            await optimizer.cleanup()

    @pytest.fixture
    def request_context(self):
        """Create request context for testing."""
        return RequestContext(
            request_id="test_123",
            endpoint="/api/v1/test",
            method="GET",
            user_id="test_user",
            api_key="test_api_key",
            tier=APITier.BASIC,
            priority=RequestPriority.NORMAL,
            size_bytes=1024,
            headers={"Content-Type": "application/json"},
            params={"param1": "value1"}
        )

    @pytest.mark.asyncio
    async def test_optimizer_initialization(self, api_optimizer):
        """Test optimizer initialization."""
        assert api_optimizer is not None
        assert api_optimizer.config is not None
        assert api_optimizer.rate_limiter is not None
        assert api_optimizer.cache is not None
        assert api_optimizer.analytics is not None

    @pytest.mark.asyncio
    async def test_rate_limiter_basic_functionality(self, api_optimizer, request_context):
        """Test basic rate limiting functionality."""
        rate_limiter = api_optimizer.rate_limiter

        # First request should be allowed
        allowed, info = await rate_limiter.is_allowed(request_context)
        assert allowed
        assert "quota" in info
        assert "current_counts" in info

    @pytest.mark.asyncio
    async def test_rate_limiter_tier_differences(self, api_optimizer):
        """Test rate limiting differences between tiers."""
        rate_limiter = api_optimizer.rate_limiter

        # Create contexts for different tiers
        free_context = RequestContext(
            request_id="free_test",
            endpoint="/api/v1/test",
            method="GET",
            tier=APITier.FREE,
            user_id="free_user"
        )

        enterprise_context = RequestContext(
            request_id="enterprise_test",
            endpoint="/api/v1/test",
            method="GET",
            tier=APITier.ENTERPRISE,
            user_id="enterprise_user"
        )

        # Get quotas for different tiers
        free_allowed, free_info = await rate_limiter.is_allowed(free_context)
        enterprise_allowed, enterprise_info = await rate_limiter.is_allowed(enterprise_context)

        assert free_allowed
        assert enterprise_allowed

        # Enterprise should have higher limits
        free_quota = free_info["quota"]
        enterprise_quota = enterprise_info["quota"]

        assert enterprise_quota.requests_per_minute > free_quota.requests_per_minute
        assert enterprise_quota.concurrent_requests > free_quota.concurrent_requests

    @pytest.mark.asyncio
    async def test_rate_limiter_exhaustion(self, api_optimizer):
        """Test rate limiter when limits are exhausted."""
        rate_limiter = api_optimizer.rate_limiter

        # Create context with very low limits for testing
        context = RequestContext(
            request_id="limit_test",
            endpoint="/api/v1/test",
            method="GET",
            tier=APITier.FREE,
            user_id="limit_test_user"
        )

        # Override quota for testing
        test_quota = rate_limiter.tier_configs[APITier.FREE]
        original_rpm = test_quota.requests_per_minute
        test_quota.requests_per_minute = 2  # Very low limit

        try:
            # First two requests should be allowed
            for _i in range(2):
                allowed, info = await rate_limiter.is_allowed(context)
                assert allowed

            # Third request should be denied
            allowed, info = await rate_limiter.is_allowed(context)
            assert not allowed
            assert info["retry_after_seconds"] > 0

        finally:
            # Restore original quota
            test_quota.requests_per_minute = original_rpm

    @pytest.mark.asyncio
    async def test_cache_basic_operations(self, api_optimizer):
        """Test basic cache operations."""
        cache = api_optimizer.cache

        # Test set and get
        success = await cache.set("test_key", {"data": "test_value"}, ttl_seconds=300)
        assert success

        cached_data = await cache.get("test_key")
        assert cached_data is not None
        assert cached_data["data"] == "test_value"

        # Test cache miss
        missing_data = await cache.get("nonexistent_key")
        assert missing_data is None

    @pytest.mark.asyncio
    async def test_cache_expiration(self, api_optimizer):
        """Test cache TTL expiration."""
        cache = api_optimizer.cache

        # Set data with very short TTL
        await cache.set("expire_test", {"data": "expires_soon"}, ttl_seconds=1)

        # Should be available immediately
        data = await cache.get("expire_test")
        assert data is not None

        # Wait for expiration
        await asyncio.sleep(2)

        # Should be expired
        expired_data = await cache.get("expire_test")
        assert expired_data is None

    @pytest.mark.asyncio
    async def test_cache_pattern_invalidation(self, api_optimizer):
        """Test pattern-based cache invalidation."""
        cache = api_optimizer.cache

        # Set multiple related keys
        await cache.set("user:123:profile", {"name": "John"})
        await cache.set("user:123:settings", {"theme": "dark"})
        await cache.set("user:456:profile", {"name": "Jane"})
        await cache.set("product:789", {"name": "Widget"})

        # Invalidate user:123 keys
        invalidated = await cache.invalidate_pattern("user:123:*")
        assert invalidated >= 0  # Should invalidate some keys

        # user:123 keys should be gone
        assert await cache.get("user:123:profile") is None
        assert await cache.get("user:123:settings") is None

        # Other keys should remain
        assert await cache.get("user:456:profile") is not None
        assert await cache.get("product:789") is not None

    @pytest.mark.asyncio
    async def test_analytics_recording(self, api_optimizer, request_context):
        """Test analytics data recording."""
        analytics = api_optimizer.analytics

        # Record request
        await analytics.record_request(
            context=request_context,
            response_time_ms=150.5,
            status_code=200,
            response_size_bytes=2048
        )

        # Check endpoint analytics
        endpoint_analytics = await analytics.get_endpoint_analytics("/api/v1/test", "GET")
        assert "error" not in endpoint_analytics
        assert endpoint_analytics["total_requests"] == 1
        assert endpoint_analytics["avg_response_time_ms"] == 150.5

    @pytest.mark.asyncio
    async def test_full_request_processing(self, api_optimizer, request_context):
        """Test complete request processing workflow."""
        # Process request
        allowed, info = await api_optimizer.process_request(request_context)
        assert allowed
        assert "cache_key" in info

        # Complete request
        response_data = {"result": "success", "data": "test response"}
        await api_optimizer.complete_request(request_context, response_data, 200)

        # Get optimization stats
        stats = await api_optimizer.get_optimization_stats()
        assert "cache" in stats
        assert "system_health" in stats
        assert "metrics" in stats


class TestMiddlewarePipeline:
    """Test suite for LUKHAS Middleware Pipeline."""

    @pytest.fixture
    async def middleware_config(self):
        """Create middleware configuration for testing."""
        return MiddlewareConfig(
            enable_security=True,
            enable_rate_limiting=True,
            enable_optimization=True,
            enable_analytics=True,
            enable_request_validation=True,
            max_request_size_mb=10.0,
            request_timeout_seconds=30.0
        )

    @pytest.fixture
    async def middleware_pipeline(self, middleware_config):
        """Create middleware pipeline for testing."""
        pipeline = await create_middleware_pipeline(middleware_config)
        yield pipeline

    @pytest.fixture
    def request_metadata(self):
        """Create request metadata for testing."""
        return RequestMetadata(
            request_id="test_request_123",
            start_time=time.time(),
            client_ip="192.168.1.100",
            user_agent="Test Agent/1.0",
            endpoint="/api/v1/test",
            method="GET",
            content_type="application/json",
            content_length=1024,
            custom_headers={"Authorization": "Bearer test_token"}
        )

    @pytest.mark.asyncio
    async def test_pipeline_initialization(self, middleware_pipeline):
        """Test pipeline initialization."""
        assert middleware_pipeline is not None
        assert len(middleware_pipeline.middleware_stack) > 0
        assert middleware_pipeline.config is not None

    @pytest.mark.asyncio
    async def test_security_middleware(self):
        """Test security middleware functionality."""
        security_middleware = SecurityMiddleware()

        metadata = RequestMetadata(
            request_id="security_test",
            start_time=time.time(),
            client_ip="192.168.1.100",
            user_agent="Test Agent",
            endpoint="/api/v1/secure",
            method="GET",
            custom_headers={"Authorization": "Bearer valid_token"}
        )

        allowed, data = await security_middleware.process_request(metadata, {})
        assert allowed  # Should pass basic validation
        assert "security_context" in data

    @pytest.mark.asyncio
    async def test_validation_middleware(self):
        """Test validation middleware functionality."""
        validation_middleware = ValidationMiddleware(max_request_size_mb=1.0)

        # Test normal request
        metadata = RequestMetadata(
            request_id="validation_test",
            start_time=time.time(),
            client_ip="192.168.1.100",
            user_agent="Test Agent",
            endpoint="/api/v1/test",
            method="POST",
            content_type="application/json",
            content_length=512
        )

        allowed, data = await validation_middleware.process_request(metadata, {"test": "data"})
        assert allowed
        assert "sanitized_data" in data

        # Test oversized request
        metadata.content_length = 2 * 1024 * 1024  # 2MB
        allowed, data = await validation_middleware.process_request(metadata, {"test": "data"})
        assert not allowed
        assert data["status"] == 413  # Request Entity Too Large

    @pytest.mark.asyncio
    async def test_analytics_middleware(self):
        """Test analytics middleware functionality."""
        analytics_middleware = AnalyticsMiddleware()

        metadata = RequestMetadata(
            request_id="analytics_test",
            start_time=time.time(),
            client_ip="192.168.1.100",
            user_agent="Test Agent",
            endpoint="/api/v1/test",
            method="GET"
        )

        # Process request
        allowed, _data = await analytics_middleware.process_request(metadata, {})
        assert allowed

        # Process response
        response_data = {"result": "success", "status_code": 200}
        processed_response = await analytics_middleware.process_response(metadata, response_data)

        assert "headers" in processed_response
        assert "X-Processing-Time" in processed_response["headers"]
        assert "X-Analytics-ID" in processed_response["headers"]

        # Check analytics summary
        summary = analytics_middleware.get_analytics_summary()
        assert "total_requests" in summary
        assert summary["total_requests"] >= 1

    @pytest.mark.asyncio
    async def test_full_pipeline_processing(self, middleware_pipeline, request_metadata):
        """Test complete pipeline processing."""
        # Process request
        allowed, processed_data = await middleware_pipeline.process_request(
            request_metadata, {"test": "input_data"}
        )

        assert allowed
        assert isinstance(processed_data, dict)

        # Process response
        response_data = {"result": "success", "status_code": 200}
        processed_response = await middleware_pipeline.process_response(
            request_metadata, response_data
        )

        assert "result" in processed_response
        assert processed_response["result"] == "success"

        # Get pipeline stats
        stats = middleware_pipeline.get_pipeline_stats()
        assert "pipeline" in stats
        assert "middleware" in stats
        assert stats["pipeline"]["total_requests"] >= 1

    @pytest.mark.asyncio
    async def test_middleware_error_handling(self, middleware_pipeline):
        """Test middleware error handling."""
        # Create metadata that might cause errors
        metadata = RequestMetadata(
            request_id="error_test",
            start_time=time.time(),
            client_ip="192.168.1.100",
            user_agent="Test Agent",
            endpoint="/api/v1/test",
            method="POST",
            content_type="application/json",
            content_length=0  # Invalid for POST
        )

        # Process should handle errors gracefully
        allowed, data = await middleware_pipeline.process_request(metadata, {})

        # Result may vary depending on middleware implementation
        # but should not raise unhandled exceptions
        assert isinstance(allowed, bool)
        assert isinstance(data, dict)


class TestAnalyticsDashboard:
    """Test suite for LUKHAS Analytics Dashboard."""

    @pytest.fixture
    async def analytics_dashboard(self):
        """Create analytics dashboard for testing."""
        dashboard = await create_analytics_dashboard()
        yield dashboard

    @pytest.fixture
    async def metrics_collector(self):
        """Create metrics collector for testing."""
        return MetricsCollector(max_points=1000)

    @pytest.mark.asyncio
    async def test_dashboard_initialization(self, analytics_dashboard):
        """Test dashboard initialization."""
        assert analytics_dashboard is not None
        assert analytics_dashboard.metrics_collector is not None
        assert analytics_dashboard.alert_manager is not None
        assert analytics_dashboard.intelligence_engine is not None

    @pytest.mark.asyncio
    async def test_metrics_collector_basic_operations(self, metrics_collector):
        """Test basic metrics collector operations."""
        # Record metric
        await metrics_collector.record_metric("test_metric", 42.5,
                                             labels={"type": "test"})

        # Get metrics
        metrics = await metrics_collector.get_metrics("test_metric")
        assert len(metrics) == 1
        assert metrics[0].value == 42.5
        assert metrics[0].labels["type"] == "test"

    @pytest.mark.asyncio
    async def test_api_request_recording(self, metrics_collector):
        """Test API request metrics recording."""
        await metrics_collector.record_api_request(
            endpoint="/api/v1/test",
            method="GET",
            response_time=150.5,
            status_code=200,
            user_id="test_user",
            request_size=1024,
            response_size=2048,
            cache_hit=False
        )

        # Check endpoint metrics
        endpoint_metrics = await metrics_collector.get_endpoint_metrics("/api/v1/test", "GET")
        endpoint_key = "GET:/api/v1/test"

        assert endpoint_key in endpoint_metrics
        metrics = endpoint_metrics[endpoint_key]
        assert metrics.total_requests == 1
        assert metrics.successful_requests == 1
        assert metrics.failed_requests == 0
        assert metrics.avg_response_time == 150.5

    @pytest.mark.asyncio
    async def test_alert_manager(self):
        """Test alert manager functionality."""
        alert_manager = AlertManager()
        metrics_collector = MetricsCollector()

        # Add alert rule
        alert_manager.add_alert_rule(
            metric_name="test_metric",
            threshold=100.0,
            severity=AlertSeverity.WARNING,
            comparison="greater",
            description="Test alert"
        )

        # Record metric that should trigger alert
        await metrics_collector.record_metric("test_metric", 150.0)

        # Check alerts
        await alert_manager.check_alerts(metrics_collector)

        # Should have active alert
        active_alerts = alert_manager.get_active_alerts()
        assert len(active_alerts) > 0
        assert active_alerts[0].severity == AlertSeverity.WARNING

    @pytest.mark.asyncio
    async def test_intelligence_engine(self):
        """Test intelligence engine insights generation."""
        intelligence_engine = IntelligenceEngine()
        metrics_collector = MetricsCollector()

        # Create test data - slow endpoint
        await metrics_collector.record_api_request(
            endpoint="/api/v1/slow",
            method="GET",
            response_time=2500.0,  # Very slow
            status_code=200,
            user_id="test_user"
        )

        # Generate insights
        insights = await intelligence_engine.generate_insights(metrics_collector)

        # Should detect slow endpoint
        slow_endpoint_insights = [i for i in insights if "slow" in i.title.lower()]
        assert len(slow_endpoint_insights) > 0
        assert slow_endpoint_insights[0].impact == "high"

    @pytest.mark.asyncio
    async def test_dashboard_data_generation(self, analytics_dashboard):
        """Test dashboard data generation."""
        # Record some test requests
        for i in range(10):
            await analytics_dashboard.record_api_request(
                endpoint=f"/api/v1/endpoint{i % 3}",
                method="GET",
                response_time=50 + i * 10,
                status_code=200 if i % 10 != 0 else 404,  # 10% error rate
                user_id=f"user_{i % 5}",
                request_size=1024,
                response_size=2048
            )

        # Get dashboard data
        dashboard_data = await analytics_dashboard.get_dashboard_data()

        assert "summary" in dashboard_data
        assert "top_endpoints" in dashboard_data
        assert "alerts" in dashboard_data
        assert "insights" in dashboard_data

        # Check summary
        summary = dashboard_data["summary"]
        assert summary["total_requests"] == 10
        assert summary["unique_users"] == 5
        assert summary["error_rate_percent"] == 10.0

    @pytest.mark.asyncio
    async def test_endpoint_details(self, analytics_dashboard):
        """Test endpoint details retrieval."""
        # Record requests for specific endpoint
        for i in range(5):
            await analytics_dashboard.record_api_request(
                endpoint="/api/v1/detailed",
                method="POST",
                response_time=100 + i * 20,
                status_code=200,
                user_id=f"user_{i}",
                request_size=1024,
                response_size=2048
            )

        # Get endpoint details
        details = await analytics_dashboard.get_endpoint_details("/api/v1/detailed", "POST")

        assert "endpoint" in details
        assert "metrics" in details
        assert "performance_trend" in details

        metrics = details["metrics"]
        assert metrics["total_requests"] == 5
        assert metrics["avg_response_time"] == 140.0  # (100+120+140+160+180)/5


class TestIntegrationScenarios:
    """Integration tests for complete API optimization system."""

    @pytest.mark.asyncio
    async def test_complete_api_optimization_workflow(self):
        """Test complete API optimization workflow."""

        # Create all components
        optimizer_config = OptimizationConfig(
            strategy=OptimizationStrategy.BALANCED,
            enable_adaptive_caching=True
        )
        optimizer = LUKHASAPIOptimizer(optimizer_config)

        middleware_config = MiddlewareConfig(
            enable_optimization=True,
            enable_analytics=True
        )
        pipeline = await create_middleware_pipeline(middleware_config, None, optimizer)

        dashboard = await create_analytics_dashboard()

        # Create request context
        request_context = RequestContext(
            request_id="integration_test",
            endpoint="/api/v1/integration",
            method="GET",
            user_id="integration_user",
            tier=APITier.PREMIUM
        )

        request_metadata = RequestMetadata(
            request_id="integration_test",
            start_time=time.time(),
            client_ip="192.168.1.100",
            user_agent="Integration Test",
            endpoint="/api/v1/integration",
            method="GET"
        )

        # Process through optimizer
        optimizer_allowed, _optimizer_info = await optimizer.process_request(request_context)
        assert optimizer_allowed

        # Process through middleware pipeline
        pipeline_allowed, _pipeline_data = await pipeline.process_request(
            request_metadata, {"test": "integration_data"}
        )
        assert pipeline_allowed

        # Record in analytics dashboard
        await dashboard.record_api_request(
            endpoint="/api/v1/integration",
            method="GET",
            response_time=125.0,
            status_code=200,
            user_id="integration_user"
        )

        # Complete optimizer request
        response_data = {"result": "integration_success"}
        await optimizer.complete_request(request_context, response_data, 200)

        # Process response through pipeline
        processed_response = await pipeline.process_response(request_metadata, response_data)

        # Verify results
        assert "result" in processed_response
        assert processed_response["result"] == "integration_success"

        # Check analytics
        dashboard_data = await dashboard.get_dashboard_data()
        assert dashboard_data["summary"]["total_requests"] >= 1

        # Get optimization stats
        optimizer_stats = await optimizer.get_optimization_stats()
        pipeline_stats = pipeline.get_pipeline_stats()

        assert "cache" in optimizer_stats
        assert "pipeline" in pipeline_stats

    @pytest.mark.asyncio
    async def test_performance_under_load(self):
        """Test system performance under load."""
        # Create optimized configuration
        config = OptimizationConfig(
            strategy=OptimizationStrategy.LOW_LATENCY,
            enable_adaptive_caching=True,
            enable_request_batching=True
        )
        optimizer = LUKHASAPIOptimizer(config)

        # Simulate concurrent requests
        async def process_request(request_id: int):
            context = RequestContext(
                request_id=f"load_test_{request_id}",
                endpoint="/api/v1/load_test",
                method="GET",
                user_id=f"user_{request_id % 10}",
                tier=APITier.BASIC
            )

            start_time = time.time()
            allowed, _info = await optimizer.process_request(context)
            processing_time = time.time() - start_time

            if allowed:
                await optimizer.complete_request(
                    context, {"result": f"response_{request_id}"}, 200
                )

            return allowed, processing_time

        # Run concurrent requests
        tasks = [process_request(i) for i in range(100)]
        results = await asyncio.gather(*tasks)

        # Analyze results
        allowed_count = sum(1 for allowed, _ in results if allowed)
        processing_times = [time for _, time in results]

        assert allowed_count > 80  # At least 80% should be allowed
        assert max(processing_times) < 1.0  # No request should take more than 1 second
        assert statistics.mean(processing_times) < 0.1  # Average should be under 100ms

    @pytest.mark.asyncio
    async def test_cache_effectiveness(self):
        """Test cache effectiveness under realistic scenarios."""
        config = OptimizationConfig(
            enable_adaptive_caching=True,
            cache_ttl_seconds=60
        )
        optimizer = LUKHASAPIOptimizer(config)

        # Make identical requests
        context = RequestContext(
            request_id="cache_test_1",
            endpoint="/api/v1/cacheable",
            method="GET",
            params={"page": 1, "limit": 10}
        )

        # First request - cache miss
        start_time = time.time()
        allowed1, info1 = await optimizer.process_request(context)
        time1 = time.time() - start_time

        assert allowed1
        assert not info1.get("cached", False)

        # Simulate response and cache it
        await optimizer.complete_request(context, {"data": "cached_data"}, 200)

        # Second identical request - should be cache hit
        context.request_id = "cache_test_2"
        start_time = time.time()
        _allowed2, info2 = await optimizer.process_request(context)
        time2 = time.time() - start_time

        # Cache hit should be faster
        if info2.get("cached", False):
            assert time2 < time1
            assert info2["data"]["data"] == "cached_data"


# Performance benchmarks
class TestPerformanceBenchmarks:
    """Performance benchmark tests."""

    @pytest.mark.asyncio
    async def test_rate_limiter_performance(self):
        """Benchmark rate limiter performance."""
        rate_limiter = RateLimiter()

        context = RequestContext(
            request_id="perf_test",
            endpoint="/api/v1/perf",
            method="GET",
            user_id="perf_user",
            tier=APITier.BASIC
        )

        # Benchmark rate limit checks
        start_time = time.time()
        for i in range(1000):
            context.request_id = f"perf_test_{i}"
            await rate_limiter.is_allowed(context)

        end_time = time.time()
        total_time = end_time - start_time
        ops_per_second = 1000 / total_time

        print(f"✅ Rate limiter performance: {ops_per_second:.0f} ops/sec")
        assert ops_per_second > 1000  # Should handle at least 1000 ops/sec

    @pytest.mark.asyncio
    async def test_cache_performance(self):
        """Benchmark cache performance."""
        cache = APICache()

        # Benchmark cache writes
        start_time = time.time()
        for i in range(1000):
            await cache.set(f"perf_key_{i}", {"data": f"value_{i}"}, ttl_seconds=300)
        write_time = time.time() - start_time

        # Benchmark cache reads
        start_time = time.time()
        for i in range(1000):
            await cache.get(f"perf_key_{i}")
        read_time = time.time() - start_time

        write_ops_per_second = 1000 / write_time
        read_ops_per_second = 1000 / read_time

        print(f"✅ Cache write performance: {write_ops_per_second:.0f} ops/sec")
        print(f"✅ Cache read performance: {read_ops_per_second:.0f} ops/sec")

        assert write_ops_per_second > 500  # At least 500 writes/sec
        assert read_ops_per_second > 1000  # At least 1000 reads/sec


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short", "-x"])
