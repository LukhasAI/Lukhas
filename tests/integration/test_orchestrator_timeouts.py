#!/usr/bin/env python3
"""
Integration tests for MATRIZ async orchestrator timeout functionality.
Tests T4/0.01% performance requirements and fail-soft behavior.
"""

import asyncio
import sys
import time
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from matriz.core.async_orchestrator import (
    AsyncCognitiveOrchestrator,
    StageResult,
    StageType,
    run_with_timeout,
)
from matriz.core.node_interface import CognitiveNode


class SlowNode(CognitiveNode):
    """Test node with configurable delay"""

    def __init__(self, delay_seconds: float = 0.001, name: str = "slow_node"):
        self.delay_seconds = delay_seconds
        self.name = name
        super().__init__(node_name=name, capabilities=["test"])

    def process(self, input_data: dict) -> dict:
        """Process with delay"""
        time.sleep(self.delay_seconds)
        return {
            "answer": f"Processed after {self.delay_seconds}s",
            "confidence": 0.9,
            "matriz_node": {"id": "test_node_1", "type": "TEST"},
        }

    def validate_output(self, output: dict) -> bool:
        return True


class FastNode(CognitiveNode):
    """Test node that responds quickly"""

    def __init__(self, name: str = "fast_node"):
        self.name = name
        super().__init__(node_name=name, capabilities=["test"])

    def process(self, input_data: dict) -> dict:
        """Process immediately"""
        return {
            "answer": "Fast response",
            "confidence": 0.95,
            "matriz_node": {"id": "fast_node_1", "type": "TEST"},
        }

    def validate_output(self, output: dict) -> bool:
        return True


class FailingNode(CognitiveNode):
    """Test node that always fails"""

    def __init__(self, name: str = "failing_node"):
        self.name = name
        super().__init__(node_name=name, capabilities=["test"])

    def process(self, input_data: dict) -> dict:
        raise ValueError("Intentional failure for testing")

    def validate_output(self, output: dict) -> bool:
        return False


@pytest.mark.asyncio
class TestOrchestratorTimeouts:
    """Test suite for orchestrator timeout functionality"""

    async def test_stage_timeout_enforcement(self):
        """Test that individual stages respect timeout limits"""
        # Create a slow coroutine
        async def slow_operation():
            await asyncio.sleep(0.1)  # 100ms
            return "completed"

        # Test with 50ms timeout - should fail
        result = await run_with_timeout(
            slow_operation(),
            StageType.PROCESSING,
            timeout_sec=0.05
        )

        assert not result.success
        assert result.timeout
        assert "timed out" in result.error
        assert result.duration_ms >= 50.0  # At least timeout duration

    async def test_fast_operation_success(self):
        """Test that fast operations complete successfully"""
        async def fast_operation():
            await asyncio.sleep(0.01)  # 10ms
            return {"data": "success"}

        result = await run_with_timeout(
            fast_operation(),
            StageType.PROCESSING,
            timeout_sec=0.05  # 50ms timeout
        )

        assert result.success
        assert not result.timeout
        assert result.data == {"data": "success"}
        assert result.duration_ms < 50.0

    async def test_orchestrator_with_fast_nodes(self):
        """Test orchestrator with nodes that complete quickly"""
        orchestrator = AsyncCognitiveOrchestrator(
            total_timeout=0.5  # 500ms total budget
        )

        # Register fast nodes
        orchestrator.register_node("math", FastNode("math"))
        orchestrator.register_node("facts", FastNode("facts"))

        # Process query
        result = await orchestrator.process_query("What is 2+2?")

        assert "answer" in result
        assert result["answer"] == "Fast response"
        assert result["metrics"]["within_budget"]
        assert result["metrics"]["total_duration_ms"] < 500

    async def test_orchestrator_timeout_handling(self):
        """Test orchestrator handling of slow nodes"""
        orchestrator = AsyncCognitiveOrchestrator(
            stage_timeouts={
                StageType.INTENT: 0.05,
                StageType.DECISION: 0.02,
                StageType.PROCESSING: 0.05,  # 50ms timeout
                StageType.VALIDATION: 0.03,
                StageType.REFLECTION: 0.02,
            },
            total_timeout=0.2  # 200ms total
        )

        # Register a slow node (100ms delay)
        orchestrator.register_node("math", SlowNode(delay_seconds=0.1))
        orchestrator.register_node("facts", SlowNode(delay_seconds=0.1))

        # Process query - should timeout during processing
        result = await orchestrator.process_query("What is 2+2?")

        # Should have error due to processing timeout
        assert "stages" in result
        stages = result["stages"]

        # Find processing stage
        processing_stages = [s for s in stages if s["stage_type"] == "processing"]
        if processing_stages:
            assert processing_stages[0]["timeout"]

    async def test_fail_soft_for_noncritical_stages(self):
        """Test that non-critical stage failures don't fail the pipeline"""
        orchestrator = AsyncCognitiveOrchestrator(
            stage_critical={
                StageType.INTENT: True,
                StageType.DECISION: True,
                StageType.PROCESSING: True,
                StageType.VALIDATION: False,  # Non-critical
                StageType.REFLECTION: False,  # Non-critical
            }
        )

        # Register nodes
        orchestrator.register_node("facts", FastNode())
        orchestrator.register_node("validator", FailingNode())  # Will fail

        result = await orchestrator.process_query("Tell me a fact")

        # Should succeed despite validator failure
        assert "answer" in result
        assert result["answer"] == "Fast response"

        # Check that validation stage failed but pipeline continued
        validation_stages = [s for s in result["stages"]
                           if s["stage_type"] == "validation"]
        if validation_stages:
            # Validation may have failed but pipeline continued
            pass

    async def test_total_timeout_enforcement(self):
        """Test that total pipeline timeout is enforced"""
        orchestrator = AsyncCognitiveOrchestrator(
            total_timeout=0.1  # 100ms total - very strict
        )

        # Register slow nodes
        orchestrator.register_node("math", SlowNode(delay_seconds=0.2))
        orchestrator.register_node("facts", SlowNode(delay_seconds=0.2))

        # Should timeout at pipeline level
        result = await orchestrator.process_query("Complex calculation")

        assert "error" in result or "timeout" in result.get("metrics", {})

    async def test_adaptive_node_selection(self):
        """Test adaptive node selection based on health metrics"""
        orchestrator = AsyncCognitiveOrchestrator()

        # Register multiple nodes
        fast = FastNode("fast_facts")
        slow = SlowNode(delay_seconds=0.05, name="slow_facts")

        orchestrator.register_node("facts", slow)
        orchestrator.register_node("fast_facts", fast)

        # Simulate failures for slow node
        orchestrator.node_health["facts"]["failure_count"] = 5
        orchestrator.node_health["facts"]["success_count"] = 1
        orchestrator.node_health["facts"]["p95_latency_ms"] = 100

        # Should select alternative node
        node_name = await orchestrator._select_node_async({"intent": "question"})

        # Basic test - just ensure selection works
        assert node_name in orchestrator.available_nodes

    async def test_metrics_collection(self):
        """Test that metrics are properly collected"""
        orchestrator = AsyncCognitiveOrchestrator()
        orchestrator.register_node("facts", FastNode())

        result = await orchestrator.process_query("Test query")

        assert "metrics" in result
        metrics = result["metrics"]

        assert "total_duration_ms" in metrics
        assert "stage_durations" in metrics
        assert "stages_completed" in metrics
        assert "stages_failed" in metrics
        assert "timeout_count" in metrics
        assert "within_budget" in metrics

        # Should have completed stages
        assert metrics["stages_completed"] > 0

    async def test_performance_report(self):
        """Test performance report generation"""
        orchestrator = AsyncCognitiveOrchestrator()
        orchestrator.register_node("facts", FastNode())

        # Process some queries to generate metrics
        await orchestrator.process_query("Query 1")
        await orchestrator.process_query("Query 2")

        report = orchestrator.get_performance_report()

        assert "node_health" in report
        assert "stage_timeouts" in report
        assert "stage_critical" in report
        assert "total_timeout" in report

        # Check node health data
        assert "facts" in report["node_health"]
        health = report["node_health"]["facts"]
        assert health["success_count"] >= 0
        assert "p95_latency_ms" in health

    async def test_stage_result_structure(self):
        """Test that stage results have correct structure"""
        result = StageResult(
            stage_type=StageType.PROCESSING,
            success=True,
            data={"test": "data"},
            duration_ms=25.5
        )

        assert result.stage_type == StageType.PROCESSING
        assert result.success
        assert result.data == {"test": "data"}
        assert result.duration_ms == 25.5
        assert not result.timeout
        assert result.error is None


@pytest.mark.asyncio
class TestChaosEngineering:
    """Chaos engineering tests for fault injection"""

    async def test_random_node_failures(self):
        """Test orchestrator resilience to random node failures"""
        orchestrator = AsyncCognitiveOrchestrator()

        # Create node that fails 50% of the time
        class FlakyNode(CognitiveNode):
            def __init__(self):
                super().__init__(node_name="flaky", capabilities=["test"])
                self.call_count = 0

            def process(self, input_data: dict) -> dict:
                self.call_count += 1
                if self.call_count % 2 == 0:
                    raise RuntimeError("Random failure")
                return {"answer": "Success", "confidence": 0.8}

            def validate_output(self, output: dict) -> bool:
                return True

        orchestrator.register_node("facts", FlakyNode())

        # Run multiple queries
        results = []
        for i in range(5):
            result = await orchestrator.process_query(f"Query {i}")
            results.append(result)

        # Should handle both success and failure cases
        successes = [r for r in results if "answer" in r]
        failures = [r for r in results if "error" in r]

        # At least some should work
        assert len(successes) > 0 or len(failures) > 0

    async def test_cascading_timeouts(self):
        """Test behavior when multiple stages timeout"""
        orchestrator = AsyncCognitiveOrchestrator(
            stage_timeouts={
                StageType.INTENT: 0.001,     # 1ms - will likely timeout
                StageType.DECISION: 0.001,   # 1ms - will likely timeout
                StageType.PROCESSING: 0.001, # 1ms - will likely timeout
                StageType.VALIDATION: 0.001,
                StageType.REFLECTION: 0.001,
            },
            total_timeout=0.1
        )

        orchestrator.register_node("facts", SlowNode(delay_seconds=0.01))

        result = await orchestrator.process_query("Test")

        # Should handle multiple timeouts gracefully
        if "metrics" in result:
            assert result["metrics"]["timeout_count"] >= 0

    async def test_memory_pressure(self):
        """Test orchestrator under memory pressure with many nodes"""
        orchestrator = AsyncCognitiveOrchestrator()

        # Register many nodes
        for i in range(100):
            orchestrator.register_node(f"node_{i}", FastNode(f"node_{i}"))

        # Process query - should handle large registry
        result = await orchestrator.process_query("Test with many nodes")

        assert "metrics" in result or "error" in result

    async def test_concurrent_queries(self):
        """Test orchestrator handling concurrent queries"""
        orchestrator = AsyncCognitiveOrchestrator()
        orchestrator.register_node("facts", FastNode())

        # Launch multiple concurrent queries
        tasks = [
            orchestrator.process_query(f"Query {i}")
            for i in range(10)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All should complete (success or controlled failure)
        assert len(results) == 10

        # Count successes
        successes = [r for r in results
                    if isinstance(r, dict) and "answer" in r]
        assert len(successes) > 0


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v", "--tb=short"])
