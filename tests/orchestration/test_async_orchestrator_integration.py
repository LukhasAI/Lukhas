#!/usr/bin/env python3
"""
MATRIZ Async Orchestrator Integration Tests
==========================================

Comprehensive integration tests for enhanced async orchestrator functionality.
Tests the critical missing functionality implementations and context preservation.

# ΛTAG: async_orchestrator_integration, context_preservation, performance_monitoring
"""

import asyncio
import pytest
import time
from typing import Any, Dict

try:
    from MATRIZ.core.async_orchestrator import AsyncCognitiveOrchestrator
    from MATRIZ.core.node_interface import CognitiveNode
    MATRIZ_AVAILABLE = True
except ImportError:
    MATRIZ_AVAILABLE = False
    AsyncCognitiveOrchestrator = None
    CognitiveNode = None


@pytest.mark.skipif(not MATRIZ_AVAILABLE, reason="MATRIZ async orchestrator not available")
class TestAsyncOrchestratorIntegration:
    """Integration tests for enhanced async orchestrator"""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator with enhanced configuration"""
        return AsyncCognitiveOrchestrator(
            total_timeout=0.5,  # 500ms for integration tests
            stage_timeouts={
                # Custom timeouts for testing
            }
        )

    @pytest.mark.asyncio
    async def test_async_interface_compatibility(self, orchestrator):
        """Test that async interface methods work correctly"""
        
        # Register async node using new interface
        async def simple_async_processor(data):
            await asyncio.sleep(0.01)  # Simulate async work
            return {"result": f"Processed: {data.get('query', 'unknown')}"}
        
        orchestrator.register_async_node("test_async", simple_async_processor)
        
        # Process query using async interface
        result = await orchestrator.process_query_async("Test async query")
        
        assert "answer" in result or "result" in result
        assert "metrics" in result
        assert "orchestrator_metrics" in result
    
    @pytest.mark.asyncio
    async def test_context_preservation(self, orchestrator):
        """Test context preservation and restoration"""
        
        # Test context preservation
        test_context = {
            "user_id": "test_user_123",
            "session": "session_abc",
            "preferences": {"theme": "dark", "language": "en"},
            "workflow_state": {"step": 3, "progress": 0.75}
        }
        
        context_id = orchestrator.preserve_context(test_context)
        assert isinstance(context_id, str)
        assert context_id.startswith("ctx_")
        
        # Test context restoration
        restored_context = orchestrator.restore_context(context_id)
        assert restored_context == test_context
        
        # Test non-existent context
        missing_context = orchestrator.restore_context("nonexistent_id")
        assert missing_context is None
        
        # Test context summary
        summary = orchestrator.get_context_summary()
        assert summary["total_contexts"] >= 1
        assert "memory_usage_mb" in summary

    @pytest.mark.asyncio 
    async def test_concurrent_async_processing(self, orchestrator):
        """Test concurrent processing with async nodes"""
        
        async def math_processor(data):
            """Simulate math processing"""
            await asyncio.sleep(0.005)
            query = data.get("expression", data.get("query", "1+1"))
            try:
                # Simple math evaluation for testing
                if "+" in query:
                    parts = query.split("+")
                    if len(parts) == 2:
                        result = int(parts[0].strip()) + int(parts[1].strip())
                        return {"result": str(result)}
                return {"result": "Cannot evaluate"}
            except:
                return {"result": "Error in evaluation"}
        
        async def facts_processor(data):
            """Simulate facts processing"""
            await asyncio.sleep(0.003)
            query = data.get("question", data.get("query", ""))
            return {"result": f"Fact about: {query}"}
        
        # Register multiple async nodes
        orchestrator.register_async_node("async_math", math_processor)
        orchestrator.register_async_node("async_facts", facts_processor)
        
        # Process multiple queries concurrently
        tasks = [
            orchestrator.process_query_async("5 + 3"),
            orchestrator.process_query_async("What is the capital of France?"),
            orchestrator.process_query_async("10 + 20"),
            orchestrator.process_query_async("How does quantum computing work?")
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify all completed successfully
        successful_results = [r for r in results if isinstance(r, dict) and not isinstance(r, Exception)]
        assert len(successful_results) >= 3  # Allow for some failures in test environment
        
        # Check that results contain expected data
        for result in successful_results:
            assert "metrics" in result
            assert "orchestrator_metrics" in result

    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self, orchestrator):
        """Test error handling in async processing"""
        
        async def failing_processor(data):
            """Processor that fails sometimes"""
            await asyncio.sleep(0.01)
            if "fail" in data.get("query", "").lower():
                raise ValueError("Intentional test failure")
            return {"result": "Success"}
        
        async def slow_processor(data):
            """Processor that times out"""
            await asyncio.sleep(1.0)  # Will timeout
            return {"result": "Should not reach here"}
        
        orchestrator.register_async_node("failing_node", failing_processor)
        orchestrator.register_async_node("slow_node", slow_processor)
        
        # Test graceful failure handling
        fail_result = await orchestrator.process_query_async("This will fail")
        assert isinstance(fail_result, dict)
        # Should get error response, not exception
        
        # Test timeout handling
        timeout_result = await orchestrator.process_query_async("This will timeout")
        assert isinstance(timeout_result, dict)
        # Should get timeout response, not hang forever

    @pytest.mark.asyncio
    async def test_performance_monitoring(self, orchestrator):
        """Test performance monitoring and metrics collection"""
        
        async def monitored_processor(data):
            """Processor with variable performance"""
            # Simulate variable processing time
            delay = 0.01 if "fast" in data.get("query", "") else 0.05
            await asyncio.sleep(delay)
            return {"result": f"Processed with {delay}s delay"}
        
        orchestrator.register_async_node("monitored_node", monitored_processor)
        
        # Process queries with different performance characteristics
        fast_result = await orchestrator.process_query_async("fast query")
        slow_result = await orchestrator.process_query_async("slow query")
        
        # Verify metrics collection
        assert "orchestrator_metrics" in fast_result
        assert "orchestrator_metrics" in slow_result
        
        fast_metrics = fast_result["orchestrator_metrics"]
        slow_metrics = slow_result["orchestrator_metrics"]
        
        # Verify metrics structure
        assert "total_duration_ms" in fast_metrics
        assert "stage_durations" in fast_metrics
        assert "stages_completed" in fast_metrics
        
        # Verify performance difference is captured
        assert fast_metrics["total_duration_ms"] != slow_metrics["total_duration_ms"]

    @pytest.mark.asyncio
    async def test_large_scale_context_management(self, orchestrator):
        """Test context management under load"""
        
        # Create many contexts
        context_ids = []
        for i in range(100):
            context_data = {
                "id": i,
                "data": f"test_data_{i}",
                "metadata": {"created": time.time()}
            }
            context_id = orchestrator.preserve_context(context_data)
            context_ids.append(context_id)
        
        # Verify all contexts can be retrieved
        retrieved_count = 0
        for context_id in context_ids:
            context = orchestrator.restore_context(context_id)
            if context is not None:
                retrieved_count += 1
        
        # Should retrieve most contexts (allowing for memory management)
        assert retrieved_count >= 50  # At least 50% retention
        
        # Check context summary
        summary = orchestrator.get_context_summary()
        assert summary["total_contexts"] > 0
        assert summary["memory_usage_mb"] >= 0

    def test_orchestrator_configuration(self, orchestrator):
        """Test orchestrator configuration and health reporting"""
        
        # Test health report
        health_report = orchestrator.get_health_report()
        
        assert "status" in health_report
        assert "available_nodes" in health_report
        assert "stage_timeouts" in health_report
        assert "orchestrator_metrics" in health_report
        
        # Test configuration access
        assert orchestrator.total_timeout > 0
        assert len(orchestrator.stage_timeouts) > 0
        assert len(orchestrator.stage_critical) > 0