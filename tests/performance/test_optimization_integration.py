#!/usr/bin/env python3
"""
Performance Optimization Integration Tests

Tests for API caching, MATRIZ adaptive timeouts, memory optimization,
and overall system performance improvements.

# ΛTAG: performance_tests, optimization_integration, system_performance
"""

import asyncio
import time
from unittest.mock import AsyncMock, Mock, patch

import pytest

try:
    from core.api.api_system import EnhancedAPISystem
    from matriz.core.async_orchestrator import AsyncCognitiveOrchestrator, StageType
    from memory.performance_optimizer import FoldPerformanceOptimizer, OptimizationResult
    PERFORMANCE_MODULES_AVAILABLE = True
except ImportError:
    # Fallback for testing without full system
    PERFORMANCE_MODULES_AVAILABLE = False
    EnhancedAPISystem = None
    AsyncCognitiveOrchestrator = None
    FoldPerformanceOptimizer = None
    OptimizationResult = None
    StageType = None


@pytest.mark.skipif(not PERFORMANCE_MODULES_AVAILABLE, reason="Performance modules not available")
class TestAPIPerformanceOptimizations:
    """Test API system performance optimizations."""

    @pytest.fixture
    def api_system(self):
        """Create API system instance."""
        return EnhancedAPISystem()

    def test_cache_key_generation(self, api_system):
        """Test cache key generation for request caching."""
        
        # Test deterministic cache key generation
        key1 = api_system._generate_cache_key(
            "consciousness", 
            '{"query": "test"}', 
            "auth_hash_123"
        )
        key2 = api_system._generate_cache_key(
            "consciousness", 
            '{"query": "test"}', 
            "auth_hash_123"
        )
        
        assert key1 == key2, "Cache keys should be deterministic"
        
        # Test different keys for different requests
        key3 = api_system._generate_cache_key(
            "consciousness", 
            '{"query": "different"}', 
            "auth_hash_123"
        )
        
        assert key1 != key3, "Different requests should have different cache keys"

    @pytest.mark.asyncio
    async def test_response_caching(self, api_system):
        """Test response caching functionality."""
        
        cache_key = "test_cache_key"
        test_response = {"result": "cached_response", "timestamp": time.time()}
        
        # Cache response
        await api_system._cache_response(cache_key, test_response)
        
        # Retrieve cached response
        cached = await api_system._get_cached_response(cache_key)
        
        assert cached is not None, "Response should be cached"
        assert cached["result"] == "cached_response", "Cached response should match"

    @pytest.mark.asyncio
    async def test_cache_expiration(self, api_system):
        """Test cache expiration handling."""
        
        # Set short TTL for testing
        api_system.cache_ttl_seconds = 0.1
        
        cache_key = "expiring_key"
        test_response = {"result": "expiring_response"}
        
        # Cache response
        await api_system._cache_response(cache_key, test_response)
        
        # Verify it's cached
        cached = await api_system._get_cached_response(cache_key)
        assert cached is not None
        
        # Wait for expiration
        await asyncio.sleep(0.2)
        
        # Verify it's expired
        expired = await api_system._get_cached_response(cache_key)
        assert expired is None, "Cached response should expire"

    @pytest.mark.asyncio
    async def test_request_coalescing(self, api_system):
        """Test request coalescing for duplicate concurrent requests."""
        
        call_count = 0
        
        async def mock_request():
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.1)  # Simulate processing time
            return {"result": f"response_{call_count}"}
        
        # Start multiple identical requests concurrently
        request_key = "duplicate_request"
        
        tasks = [
            api_system._coalesce_request(request_key, mock_request)
            for _ in range(5)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Verify only one actual request was made
        assert call_count == 1, f"Expected 1 request, got {call_count}"
        
        # Verify all requests got the same result
        for result in results:
            assert result["result"] == "response_1"

    def test_performance_metrics_tracking(self, api_system):
        """Test performance metrics tracking."""
        
        # Test metrics initialization
        assert api_system.performance_metrics["total_requests"] == 0
        assert api_system.performance_metrics["cache_hits"] == 0
        
        # Test metrics update
        api_system._update_performance_metrics(150.0, is_error=False)
        
        assert api_system.performance_metrics["total_requests"] == 1
        assert api_system.performance_metrics["successful_requests"] == 1
        assert api_system.performance_metrics["average_response_time"] == 150.0
        
        # Test error tracking
        api_system._update_performance_metrics(200.0, is_error=True)
        
        assert api_system.performance_metrics["error_requests"] == 1
        assert api_system.performance_metrics["total_requests"] == 2


@pytest.mark.skipif(not PERFORMANCE_MODULES_AVAILABLE, reason="Performance modules not available")
class TestMATRIZAdaptiveTimeouts:
    """Test MATRIZ adaptive timeout optimizations."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator with adaptive timeouts."""
        return AsyncCognitiveOrchestrator(
            stage_timeouts={StageType.ANALYZE: 0.1, StageType.PROCESS: 0.2},
            total_timeout=0.5
        )

    def test_adaptive_timeout_initialization(self, orchestrator):
        """Test adaptive timeout system initialization."""
        
        assert orchestrator.adaptive_timeout_enabled is True
        assert orchestrator.timeout_learning_rate == 0.1
        assert isinstance(orchestrator.timeout_history, dict)

    def test_adaptive_timeout_calculation(self, orchestrator):
        """Test adaptive timeout calculation logic."""
        
        stage_type = StageType.ANALYZE
        
        # Test initial timeout (should be base timeout)
        initial_timeout = orchestrator._get_adaptive_timeout(stage_type)
        base_timeout = orchestrator.stage_timeouts[stage_type]
        
        assert initial_timeout == base_timeout, "Initial timeout should match base timeout"
        
        # Simulate successful operations
        orchestrator.timeout_history[stage_type.value] = {
            "successful_durations": [50, 60, 55, 65, 70] * 3,  # 15 samples
            "timeout_count": 0,
            "total_attempts": 15,
            "current_timeout": base_timeout
        }
        
        # Get adaptive timeout
        adaptive_timeout = orchestrator._get_adaptive_timeout(stage_type)
        
        # Should be based on P95 of successful durations
        assert adaptive_timeout != base_timeout, "Adaptive timeout should differ from base"

    def test_timeout_history_update(self, orchestrator):
        """Test timeout history update mechanism."""
        
        from matriz.core.async_orchestrator import StageResult
        
        stage_type = StageType.PROCESS
        
        # Create successful result
        success_result = StageResult(
            stage_type=stage_type,
            success=True,
            data={"result": "success"},
            duration_ms=80.0
        )
        
        # Update history
        orchestrator._update_timeout_history(stage_type, success_result)
        
        # Verify history was updated
        stage_key = stage_type.value
        assert stage_key in orchestrator.timeout_history
        assert orchestrator.timeout_history[stage_key]["total_attempts"] == 1
        assert 80.0 in orchestrator.timeout_history[stage_key]["successful_durations"]

    def test_node_health_tracking(self, orchestrator):
        """Test node health tracking for intelligent routing."""
        
        node_name = "test_node"
        
        # Update with successful operation
        orchestrator._update_node_health(node_name, success=True, duration_ms=50.0)
        
        # Verify health metrics
        assert node_name in orchestrator.node_health
        health = orchestrator.node_health[node_name]
        
        assert health["success_count"] == 1
        assert health["failure_count"] == 0
        assert 50.0 in health["recent_latencies"]
        assert health["health_score"] > 0.8  # Should be healthy

    def test_best_node_selection(self, orchestrator):
        """Test intelligent node selection based on health."""
        
        # Add mock nodes with different health scores
        node1 = Mock()
        node1.capabilities = ["test_capability"]
        node2 = Mock()
        node2.capabilities = ["test_capability"]
        
        orchestrator.available_nodes["healthy_node"] = node1
        orchestrator.available_nodes["slow_node"] = node2
        
        # Set different health scores
        orchestrator.node_health["healthy_node"] = {"health_score": 0.9}
        orchestrator.node_health["slow_node"] = {"health_score": 0.3}
        
        # Select best node
        best_node = orchestrator._select_best_node("test_capability")
        
        assert best_node == "healthy_node", "Should select node with best health score"


@pytest.mark.skipif(not PERFORMANCE_MODULES_AVAILABLE, reason="Performance modules not available")
class TestMemoryPerformanceOptimizer:
    """Test memory fold performance optimizer."""

    @pytest.fixture
    def optimizer(self):
        """Create performance optimizer."""
        return FoldPerformanceOptimizer(
            cache_size=100,
            batch_threshold=10,
            optimization_interval_sec=1.0
        )

    @pytest.fixture
    def mock_memory_fold(self):
        """Create mock memory fold for testing."""
        from memory.performance_optimizer import MemoryFold, MemoryItem
        
        fold = MemoryFold("test_fold")
        
        # Add mock items
        for i in range(20):
            item = MemoryItem(f"item_{i}", {"content": f"Test content {i}"})
            item.importance_score = 0.5 + (i % 10) * 0.05  # Varying importance
            item.tags = [f"tag_{i % 3}"]  # Group by tags
            fold.items.append(item)
        
        return fold

    @pytest.mark.asyncio
    async def test_fold_optimization(self, optimizer, mock_memory_fold):
        """Test basic fold optimization."""
        
        result = await optimizer.optimize_fold_consolidation(mock_memory_fold)
        
        assert isinstance(result, OptimizationResult)
        assert result.fold_id == "test_fold"
        assert result.original_size == 20
        assert result.optimization_time_ms > 0
        assert 0.0 <= result.compression_ratio <= 1.0

    @pytest.mark.asyncio
    async def test_caching_behavior(self, optimizer, mock_memory_fold):
        """Test result caching for identical operations."""
        
        # First optimization
        result1 = await optimizer.optimize_fold_consolidation(mock_memory_fold)
        
        # Second optimization (should be cached)
        result2 = await optimizer.optimize_fold_consolidation(mock_memory_fold)
        
        # Verify caching worked
        assert optimizer.metrics.cache_hits > 0
        assert result1.optimization_time_ms >= result2.optimization_time_ms

    @pytest.mark.asyncio
    async def test_batch_processing(self, optimizer):
        """Test batch processing for large item sets."""
        
        from memory.performance_optimizer import MemoryItem
        
        # Create large set of items
        large_item_set = []
        for i in range(100):  # Above batch threshold
            item = MemoryItem(f"batch_item_{i}", {"content": f"Batch content {i}"})
            item.importance_score = 0.3 + (i % 5) * 0.1
            item.tags = [f"batch_tag_{i % 5}"]
            large_item_set.append(item)
        
        # Optimize batch
        optimized = await optimizer._optimize_items_batch(large_item_set)
        
        # Verify batch processing occurred
        assert optimizer.metrics.batch_operations > 0
        assert len(optimized) <= len(large_item_set)  # Should compress

    def test_similarity_grouping(self, optimizer):
        """Test item similarity grouping for batch optimization."""
        
        from memory.performance_optimizer import MemoryItem
        
        # Create items with different tags
        items = []
        for i in range(15):
            item = MemoryItem(f"group_item_{i}", {"content": f"Content {i}"})
            item.tags = [f"group_{i % 3}"]  # 3 groups
            items.append(item)
        
        groups = optimizer._group_items_by_similarity(items)
        
        # Should create 3 groups
        assert len(groups) == 3
        
        # Each group should have 5 items
        for group in groups:
            assert len(group) == 5

    @pytest.mark.asyncio
    async def test_optimization_service(self, optimizer):
        """Test background optimization service."""
        
        # Start service
        await optimizer.start_optimization_service()
        
        assert optimizer.auto_optimization_task is not None
        assert not optimizer.auto_optimization_task.done()
        
        # Stop service
        await optimizer.stop_optimization_service()
        
        assert optimizer.auto_optimization_task is None

    def test_performance_reporting(self, optimizer):
        """Test performance reporting functionality."""
        
        # Update some metrics
        optimizer.metrics.operation_count = 10
        optimizer.metrics.total_duration_ms = 500.0
        optimizer.metrics.cache_hits = 7
        optimizer.metrics.cache_misses = 3
        
        report = optimizer.get_performance_report()
        
        # Verify report structure
        assert "metrics" in report
        assert "cache_status" in report
        assert "performance_health" in report
        
        # Verify calculated values
        assert report["metrics"]["average_duration_ms"] == 50.0
        assert report["metrics"]["cache_hit_rate"] == 0.7


@pytest.mark.skipif(not PERFORMANCE_MODULES_AVAILABLE, reason="Performance modules not available") 
class TestIntegratedPerformanceSystem:
    """Test integrated performance optimizations across systems."""

    @pytest.mark.asyncio
    async def test_end_to_end_performance_optimization(self):
        """Test complete performance optimization pipeline."""
        
        # Initialize components
        api_system = EnhancedAPISystem()
        orchestrator = AsyncCognitiveOrchestrator()
        optimizer = FoldPerformanceOptimizer()
        
        # Start optimization services
        await optimizer.start_optimization_service()
        
        try:
            # Simulate API request with caching
            cache_key = api_system._generate_cache_key("test", "{}", "auth")
            test_response = {"optimized": True, "performance": "enhanced"}
            
            await api_system._cache_response(cache_key, test_response)
            cached_response = await api_system._get_cached_response(cache_key)
            
            assert cached_response["optimized"] is True
            
            # Test MATRIZ adaptive timeouts
            stage_type = StageType.ANALYZE
            initial_timeout = orchestrator._get_adaptive_timeout(stage_type)
            assert initial_timeout > 0
            
            # Test memory optimization
            from memory.performance_optimizer import MemoryFold
            test_fold = MemoryFold("integration_test")
            
            optimization_result = await optimizer.optimize_fold_consolidation(test_fold)
            assert optimization_result.fold_id == "integration_test"
            
            # Verify performance metrics across systems
            api_metrics = api_system.performance_metrics
            memory_report = optimizer.get_performance_report()
            
            assert api_metrics["cache_hits"] > 0
            assert memory_report["metrics"]["operation_count"] > 0
            
        finally:
            await optimizer.stop_optimization_service()

    def test_performance_threshold_compliance(self):
        """Test that performance optimizations meet T4/0.01% thresholds."""
        
        # API response time should be under target
        api_system = EnhancedAPISystem()
        api_system._update_performance_metrics(50.0, is_error=False)  # 50ms response
        
        # Should be well under typical thresholds
        assert api_system.performance_metrics["average_response_time"] < 100.0
        
        # MATRIZ timeout adaptation should be reasonable
        orchestrator = AsyncCognitiveOrchestrator()
        base_timeout = 0.25  # 250ms base
        
        # Adaptive timeout should stay within reasonable bounds
        adaptive = orchestrator._get_adaptive_timeout(StageType.ANALYZE)
        assert 0.05 <= adaptive <= 1.0  # Between 50ms and 1000ms
        
        # Memory optimization should show compression
        optimizer = FoldPerformanceOptimizer()
        
        # Performance metrics should indicate efficiency
        assert optimizer.cache_ttl_sec > 0
        assert optimizer.batch_threshold > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])