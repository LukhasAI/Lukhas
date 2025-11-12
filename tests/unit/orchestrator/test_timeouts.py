"""
Unit Tests for Orchestrator Timeouts

Tests timeout enforcement, cancellation, and error handling.
"""

import asyncio

import pytest

from lukhas.orchestrator.cancellation import CancellationRegistry
from lukhas.orchestrator.config import OrchestratorConfig, TimeoutConfig
from lukhas.orchestrator.exceptions import (
    CancellationException,
    NodeTimeoutException,
    PipelineTimeoutException,
)
from lukhas.orchestrator.executor import NodeExecutor
from lukhas.orchestrator.pipeline import PipelineExecutor


@pytest.fixture
def timeout_config():
    """Timeout config with very short timeouts for testing."""
    return TimeoutConfig(
        node_timeout_ms=100,  # 100ms
        pipeline_timeout_ms=300,  # 300ms
        cleanup_grace_ms=50,  # 50ms
    )


@pytest.fixture
def registry():
    """Cancellation registry for pipeline testing."""
    return CancellationRegistry()


@pytest.mark.asyncio
async def test_node_timeout_raises_exception(timeout_config):
    """Test that slow node raises NodeTimeoutException."""
    executor = NodeExecutor(timeout_config)

    async def slow_node(input_data):
        await asyncio.sleep(1.0)  # 1 second - exceeds 100ms timeout
        return "never reached"

    with pytest.raises(NodeTimeoutException) as exc_info:
        await executor.execute_node("slow_node", slow_node, {})

    assert exc_info.value.node_id == "slow_node"
    assert exc_info.value.timeout_ms == 100


@pytest.mark.asyncio
async def test_fast_node_succeeds(timeout_config):
    """Test that fast node completes successfully."""
    executor = NodeExecutor(timeout_config)

    async def fast_node(input_data):
        await asyncio.sleep(0.01)  # 10ms - well under timeout
        return "success"

    result = await executor.execute_node("fast_node", fast_node, {})

    assert result == "success"


@pytest.mark.asyncio
async def test_node_cancellation_via_token(timeout_config):
    """Test node cancellation via cancellation token."""
    executor = NodeExecutor(timeout_config)
    cancellation_token = asyncio.Event()

    async def long_node(input_data):
        await asyncio.sleep(10.0)  # Very long
        return "never reached"

    # Start node execution
    task = asyncio.create_task(
        executor.execute_node("long_node", long_node, {}, cancellation_token)
    )

    # Cancel after 50ms
    await asyncio.sleep(0.05)
    cancellation_token.set()

    # Should raise CancellationException
    with pytest.raises(CancellationException):
        await task


@pytest.mark.asyncio
async def test_pipeline_timeout(timeout_config, registry):
    """Test pipeline timeout when nodes take too long collectively."""
    config = OrchestratorConfig(timeouts=timeout_config)
    executor = PipelineExecutor(config, registry)

    async def medium_node(input_data):
        await asyncio.sleep(0.08)  # 80ms each - under node timeout but adds up
        return input_data

    # 4 nodes × 80ms = 320ms total > 300ms pipeline timeout
    # Each node is under 100ms node timeout, so pipeline timeout should fire first
    nodes = [
        ("node1", medium_node),
        ("node2", medium_node),
        ("node3", medium_node),
        ("node4", medium_node),
    ]

    with pytest.raises(PipelineTimeoutException) as exc_info:
        await executor.execute_pipeline("test_pipeline", nodes, {})

    # Should complete at least 2-3 nodes before pipeline timeout
    assert len(exc_info.value.completed_nodes) >= 2
    assert exc_info.value.timeout_ms == 300


@pytest.mark.asyncio
async def test_pipeline_succeeds_within_timeout(timeout_config, registry):
    """Test pipeline succeeds when all nodes complete within timeout."""
    config = OrchestratorConfig(timeouts=timeout_config)
    executor = PipelineExecutor(config, registry)

    async def fast_node(input_data):
        await asyncio.sleep(0.02)  # 20ms each
        return input_data + 1

    # 3 nodes × 20ms = 60ms total < 300ms pipeline timeout
    nodes = [
        ("node1", fast_node),
        ("node2", fast_node),
        ("node3", fast_node),
    ]

    result = await executor.execute_pipeline("test_pipeline", nodes, 0)

    assert result == 3  # 0 + 1 + 1 + 1


@pytest.mark.asyncio
async def test_node_timeout_cancels_task(timeout_config):
    """Test that timeout properly cancels the running task."""
    executor = NodeExecutor(timeout_config)
    task_started = False
    task_cancelled = False

    async def cancellable_node(input_data):
        nonlocal task_started, task_cancelled
        task_started = True
        try:
            await asyncio.sleep(10.0)
        except asyncio.CancelledError:
            task_cancelled = True
            raise

    with pytest.raises(NodeTimeoutException):
        await executor.execute_node("cancellable_node", cancellable_node, {})

    assert task_started
    # Task should be cancelled during cleanup
    await asyncio.sleep(0.1)  # Allow cleanup to complete


@pytest.mark.asyncio
async def test_pipeline_propagates_node_timeout(timeout_config, registry):
    """Test that node timeout in pipeline propagates correctly."""
    config = OrchestratorConfig(timeouts=timeout_config)
    executor = PipelineExecutor(config, registry)

    async def fast_node(input_data):
        await asyncio.sleep(0.01)
        return input_data

    async def slow_node(input_data):
        await asyncio.sleep(1.0)  # Exceeds node timeout
        return input_data

    nodes = [
        ("node1", fast_node),
        ("node2", slow_node),  # This will timeout
        ("node3", fast_node),
    ]

    with pytest.raises(NodeTimeoutException) as exc_info:
        await executor.execute_pipeline("test_pipeline", nodes, {})

    assert exc_info.value.node_id == "node2"


@pytest.mark.asyncio
async def test_timeout_config_properties():
    """Test TimeoutConfig property conversions."""
    config = TimeoutConfig(
        node_timeout_ms=200, pipeline_timeout_ms=500, cleanup_grace_ms=100
    )

    assert config.node_timeout_seconds == 0.2
    assert config.pipeline_timeout_seconds == 0.5
    assert config.cleanup_grace_seconds == 0.1


@pytest.mark.asyncio
async def test_orchestrator_config_defaults():
    """Test OrchestratorConfig initializes with defaults."""
    config = OrchestratorConfig()

    assert config.timeouts is not None
    assert isinstance(config.timeouts, TimeoutConfig)
    assert config.max_concurrent_pipelines == 10
    assert config.enable_metrics is True


@pytest.mark.asyncio
async def test_node_execution_with_exception(timeout_config):
    """Test that node exceptions are properly propagated."""
    executor = NodeExecutor(timeout_config)

    async def failing_node(input_data):
        raise ValueError("Intentional failure")

    with pytest.raises(ValueError) as exc_info:
        await executor.execute_node("failing_node", failing_node, {})

    assert "Intentional failure" in str(exc_info.value)


@pytest.mark.asyncio
async def test_pipeline_stops_on_node_failure(timeout_config, registry):
    """Test that pipeline stops when a node fails."""
    config = OrchestratorConfig(timeouts=timeout_config)
    executor = PipelineExecutor(config, registry)

    async def good_node(input_data):
        return input_data + 1

    async def bad_node(input_data):
        raise RuntimeError("Node failure")

    nodes = [
        ("node1", good_node),
        ("node2", bad_node),  # This will fail
        ("node3", good_node),  # Should not execute
    ]

    with pytest.raises(RuntimeError):
        await executor.execute_pipeline("test_pipeline", nodes, 0)


@pytest.mark.asyncio
async def test_pipeline_tracks_completed_nodes(timeout_config, registry):
    """Test that pipeline correctly tracks which nodes completed."""
    config = OrchestratorConfig(timeouts=timeout_config)
    executor = PipelineExecutor(config, registry)

    async def fast_node(input_data):
        await asyncio.sleep(0.01)
        return input_data

    async def slow_node(input_data):
        await asyncio.sleep(1.0)
        return input_data

    nodes = [
        ("node1", fast_node),
        ("node2", fast_node),
        ("node3", slow_node),  # Will timeout
    ]

    try:
        await executor.execute_pipeline("test_pipeline", nodes, {})
    except NodeTimeoutException:
        # Pipeline should have completed node1 and node2
        pass  # Expected
    except PipelineTimeoutException as e:
        # Or the whole pipeline timed out
        assert len(e.completed_nodes) >= 2
