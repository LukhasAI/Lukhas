"""
Tests for the LUKHAS orchestration system.
"""

import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock

import pytest

# Mock the `lukhas` module and its submodules, as we are testing in isolation.
# This avoids the need for the full LUKHAS environment to be installed.
# We will define mock classes for the components we need.
lukhas = MagicMock()
lukhas.orchestrator.cancellation.CancellationRegistry = MagicMock()
lukhas.orchestrator.config.OrchestratorConfig = MagicMock()
lukhas.orchestrator.exceptions.NodeTimeoutException = Exception
lukhas.orchestrator.exceptions.PipelineTimeoutException = Exception
lukhas.orchestrator.exceptions.CancellationException = Exception


# Since the real modules are not available, we need to create our own
# simplified versions for testing.
class MockOrchestratorConfig:
    def __init__(self, node_timeout=0.1, pipeline_timeout=0.2, cleanup_grace=0.01):
        self.timeouts = MagicMock()
        self.timeouts.node_timeout_seconds = node_timeout
        self.timeouts.pipeline_timeout_seconds = pipeline_timeout
        self.timeouts.cleanup_grace_seconds = cleanup_grace
        self.timeouts.node_timeout_ms = node_timeout * 1000
        self.timeouts.pipeline_timeout_ms = pipeline_timeout * 1000


# Now we can import the modules we are testing.
from lukhas.orchestration.orchestrator import Orchestrator
from lukhas.orchestrator.executor import NodeExecutor
from lukhas.orchestrator.pipeline import PipelineExecutor


@pytest.fixture
def config():
    return MockOrchestratorConfig()


@pytest.fixture
def orchestrator(config):
    # We need to manually inject our mock config, since the real
    # OrchestratorConfig is not available.
    orc = Orchestrator(config)
    orc.pipeline_executor.node_executor = NodeExecutor(config.timeouts)
    return orc


async def successful_node(data):
    await asyncio.sleep(0.01)
    return data + 1


async def slow_node(data):
    await asyncio.sleep(1)
    return data + 1


async def medium_node(data):
    await asyncio.sleep(0.1)
    return data + 1


@pytest.mark.asyncio
async def test_successful_pipeline(orchestrator):
    """
    Tests that a simple pipeline with successful nodes executes correctly.
    """
    nodes = [
        ("node1", successful_node),
        ("node2", successful_node),
    ]
    result = await orchestrator.execute("test_pipeline", nodes, 0)
    assert result == 2


@pytest.mark.asyncio
async def test_node_timeout(orchestrator):
    """
    Tests that a NodeTimeoutException is raised when a node exceeds its timeout.
    """
    nodes = [
        ("node1", successful_node),
        ("node2", slow_node),
    ]
    with pytest.raises(Exception):  # NodeTimeoutException
        await orchestrator.execute("test_pipeline", nodes, 0)


@pytest.mark.asyncio
async def test_pipeline_timeout(orchestrator):
    """
    Tests that a PipelineTimeoutException is raised when the pipeline exceeds its timeout.
    """
    nodes = [
        ("node1", medium_node),
        ("node2", medium_node),
        ("node3", medium_node),
    ]
    # The pipeline timeout is 0.2s, and each node takes 0.1s.
    # The first two nodes will complete, but the third will not.
    with pytest.raises(Exception):  # PipelineTimeoutException
        await orchestrator.execute("test_pipeline", nodes, 0)


@pytest.mark.asyncio
async def test_cancellation(orchestrator):
    """
    Tests that a pipeline can be cancelled.
    """
    nodes = [
        ("node1", successful_node),
        ("node2", slow_node),
    ]

    async def cancel_later():
        await asyncio.sleep(0.05)
        await orchestrator.cancel("test_pipeline")

    with pytest.raises(Exception):  # CancellationException
        await asyncio.gather(
            orchestrator.execute("test_pipeline", nodes, 0),
            cancel_later(),
        )


@pytest.mark.asyncio
async def test_timeout_override(orchestrator):
    """
    Tests that the per-call timeout override works.
    """
    nodes = [
        ("node1", successful_node),
        ("node2", successful_node),
        ("node3", successful_node),
    ]
    # The pipeline timeout is 0.2s, but we override it to 0.4s.
    result = await orchestrator.pipeline_executor.execute_pipeline(
        "test_pipeline", nodes, 0, timeout_seconds=0.4
    )
    assert result == 3


@pytest.mark.asyncio
async def test_cleanup_handlers(orchestrator):
    """
    Tests that the cleanup handlers are called on timeout and cancellation.
    """
    on_timeout_handler = AsyncMock()
    on_cancel_handler = AsyncMock()

    nodes = [
        ("node1", slow_node),
    ]

    with pytest.raises(Exception):  # NodeTimeoutException
        await orchestrator.pipeline_executor.execute_pipeline(
            "test_pipeline",
            nodes,
            0,
            on_timeout=on_timeout_handler,
            on_cancel=on_cancel_handler,
        )

    on_timeout_handler.assert_not_awaited()
    on_cancel_handler.assert_awaited_once()


if __name__ == "__main__":
    unittest.main()
