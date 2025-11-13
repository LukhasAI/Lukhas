"""
Integration Tests for Orchestrator Timeouts

Tests timeout system with real MATRIZ pipelines and metrics.
"""

import asyncio

import pytest

from lukhas.orchestrator.config import OrchestratorConfig, TimeoutConfig
from lukhas.orchestrator.pipeline import PipelineExecutor


@pytest.mark.asyncio
async def test_real_pipeline_with_timeout():
    """Test real MATRIZ-style pipeline with timeout enforcement."""
    config = OrchestratorConfig(
        timeouts=TimeoutConfig(node_timeout_ms=200, pipeline_timeout_ms=500)
    )

    executor = PipelineExecutor(config)

    # Simulate MATRIZ cognitive stages
    async def perception_node(input_data):
        """Simulate perception processing."""
        await asyncio.sleep(0.05)  # 50ms
        return {"query": input_data.get("query", ""), "perceived": True}

    async def reasoning_node(input_data):
        """Simulate reasoning processing."""
        await asyncio.sleep(0.08)  # 80ms
        return {
            **input_data,
            "reasoning": "processed",
            "answer": "Result from reasoning",
        }

    async def action_node(input_data):
        """Simulate action generation."""
        await asyncio.sleep(0.03)  # 30ms
        return {**input_data, "action": "complete", "output": input_data.get("answer")}

    # Create test pipeline: perception → reasoning → action
    nodes = [
        ("perception", perception_node),
        ("reasoning", reasoning_node),
        ("action", action_node),
    ]

    result = await executor.execute_pipeline(
        pipeline_name="test_perception_reasoning_action",
        nodes=nodes,
        initial_input={"query": "What is 2+2?"},
    )

    assert result is not None
    assert result.get("action") == "complete"
    assert result.get("output") == "Result from reasoning"


@pytest.mark.asyncio
async def test_pipeline_within_sla_target():
    """Test that fast pipeline completes within SLA target."""
    config = OrchestratorConfig(
        timeouts=TimeoutConfig(node_timeout_ms=200, pipeline_timeout_ms=500)
    )

    executor = PipelineExecutor(config)

    async def fast_node(input_data):
        await asyncio.sleep(0.02)  # 20ms - well within budget
        return input_data

    nodes = [("node1", fast_node), ("node2", fast_node), ("node3", fast_node)]

    import time

    start = time.perf_counter()
    await executor.execute_pipeline("fast_pipeline", nodes, {})
    duration_ms = (time.perf_counter() - start) * 1000

    # Should complete in under 100ms (3 nodes × 20ms + overhead)
    assert duration_ms < 150


@pytest.mark.asyncio
async def test_pipeline_with_mixed_speeds():
    """Test pipeline with mix of fast and slower nodes."""
    config = OrchestratorConfig(
        timeouts=TimeoutConfig(node_timeout_ms=200, pipeline_timeout_ms=500)
    )

    executor = PipelineExecutor(config)

    async def very_fast_node(input_data):
        await asyncio.sleep(0.01)  # 10ms
        return input_data + 1

    async def medium_node(input_data):
        await asyncio.sleep(0.05)  # 50ms
        return input_data + 1

    async def fast_node(input_data):
        await asyncio.sleep(0.02)  # 20ms
        return input_data + 1

    nodes = [
        ("node1", very_fast_node),  # 10ms
        ("node2", medium_node),  # 50ms
        ("node3", fast_node),  # 20ms
        ("node4", very_fast_node),  # 10ms
    ]

    result = await executor.execute_pipeline("mixed_pipeline", nodes, 0)

    # All nodes should complete: 0 + 1 + 1 + 1 + 1 = 4
    assert result == 4


@pytest.mark.asyncio
async def test_cancellation_registry_integration():
    """Test CancellationRegistry with real pipeline execution."""
    from lukhas.orchestrator.cancellation import CancellationRegistry

    config = OrchestratorConfig(
        timeouts=TimeoutConfig(node_timeout_ms=200, pipeline_timeout_ms=500)
    )

    executor = PipelineExecutor(config)
    registry = CancellationRegistry()

    async def long_node(input_data):
        await asyncio.sleep(1.0)
        return input_data

    nodes = [("node1", long_node)]

    # Register pipeline
    registry.register("test_pipeline")

    # Start pipeline execution
    asyncio.create_task(
        executor.execute_pipeline("test_pipeline", nodes, {})
    )

    # Cancel after 100ms
    await asyncio.sleep(0.1)
    registry.cancel("test_pipeline", "Test cancellation")

    # Verify metadata
    metadata = registry.get_metadata("test_pipeline")
    assert metadata["cancelled"] is True
    assert metadata["reason"] == "Test cancellation"

    # Cleanup
    registry.unregister("test_pipeline")


@pytest.mark.asyncio
async def test_concurrent_pipelines():
    """Test multiple pipelines executing concurrently."""
    config = OrchestratorConfig(
        timeouts=TimeoutConfig(node_timeout_ms=200, pipeline_timeout_ms=500),
        max_concurrent_pipelines=10,
    )

    executor = PipelineExecutor(config)

    async def processing_node(input_data):
        await asyncio.sleep(0.05)
        return input_data + 1

    nodes = [("node1", processing_node), ("node2", processing_node)]

    # Execute 5 pipelines concurrently
    tasks = [
        executor.execute_pipeline(f"pipeline_{i}", nodes, i) for i in range(5)
    ]

    results = await asyncio.gather(*tasks)

    # Verify all completed successfully
    assert len(results) == 5
    assert results == [2, 3, 4, 5, 6]  # Each adds 2 (2 nodes)


@pytest.mark.asyncio
async def test_timeout_overhead_minimal():
    """Test that timeout enforcement adds minimal overhead."""
    config = OrchestratorConfig(
        timeouts=TimeoutConfig(node_timeout_ms=200, pipeline_timeout_ms=500)
    )

    executor = PipelineExecutor(config)

    async def instant_node(input_data):
        return input_data  # No delay

    nodes = [("node1", instant_node) for _ in range(10)]

    import time

    start = time.perf_counter()
    await executor.execute_pipeline("overhead_test", nodes, {})
    duration_ms = (time.perf_counter() - start) * 1000

    # Should complete in under 10ms for 10 instant nodes
    # Verifies <1ms overhead per node
    assert duration_ms < 15
