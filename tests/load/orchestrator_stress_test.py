
import asyncio
import sys
import time
from unittest.mock import MagicMock, patch

import pytest

try:
    import numpy as np
except ImportError:
    # A simple mock for percentile calculation if numpy is not available
    class MockNumpy:
        def percentile(self, data, q):
            sorted_data = sorted(data)
            # Ensure index is within bounds
            index = min(int(len(sorted_data) * (q / 100.0)), len(sorted_data) - 1)
            return sorted_data[index]
    np = MockNumpy()
    sys.modules['numpy'] = np


# Mock missing modules
sys.modules['lukhas.monitoring.metrics'] = MagicMock()

from lukhas.orchestrator.config import OrchestratorConfig, TimeoutConfig
from lukhas.orchestrator.exceptions import (
    CancellationException,
    NodeTimeoutException,
    PipelineTimeoutException,
)
from lukhas.orchestrator.pipeline import PipelineExecutor


@pytest.fixture
def orchestrator_config():
    """Returns a default OrchestratorConfig for testing."""
    return OrchestratorConfig(
        timeouts=TimeoutConfig(
            node_timeout_ms=500,
            pipeline_timeout_ms=1500,
            cleanup_grace_ms=50
        )
    )


@pytest.fixture
def pipeline_executor(orchestrator_config):
    """Returns a PipelineExecutor instance."""
    return PipelineExecutor(orchestrator_config)


class ControllableNode:
    """A mock node that can be controlled for testing purposes."""

    def __init__(self, execution_time=0, should_error=False):
        self.execution_time = execution_time
        self.should_error = should_error

    async def __call__(self, input_data):
        if self.execution_time > 0:
            await asyncio.sleep(self.execution_time)
        if self.should_error:
            raise ValueError("Node failed")
        return input_data + 1


@pytest.mark.asyncio
class TestOrchestratorStress:
    """Stress tests for the async orchestrator."""

    async def test_concurrent_requests(self, pipeline_executor):
        """
        Tests the orchestrator's ability to handle a high volume of concurrent requests.
        """
        CONCURRENT_REQUESTS = 1000
        P95_LATENCY_TARGET_MS = 1500

        pipeline = [
            ("node1", ControllableNode(0.01)),
            ("node2", ControllableNode(0.01)),
            ("node3", ControllableNode(0.01)),
        ]

        async def run_and_time_pipeline():
            start_time = time.monotonic()
            result = await pipeline_executor.execute_pipeline(
                pipeline_id="concurrent_test",
                nodes=pipeline,
                initial_input=0
            )
            end_time = time.monotonic()
            return end_time - start_time, result

        tasks = [run_and_time_pipeline() for _ in range(CONCURRENT_REQUESTS)]

        results = await asyncio.gather(*tasks)

        latencies_s = [res[0] for res in results]
        pipeline_outputs = [res[1] for res in results]

        # Verify all pipelines completed successfully
        assert all(output == 3 for output in pipeline_outputs), "Not all pipelines returned the expected result"

        # Verify performance target
        latencies_ms = [l * 1000 for l in latencies_s]
        p95_latency = np.percentile(latencies_ms, 95)

        print(f"P95 Latency: {p95_latency:.2f}ms")
        assert p95_latency < P95_LATENCY_TARGET_MS, f"P95 latency ({p95_latency:.2f}ms) exceeds target ({P95_LATENCY_TARGET_MS}ms)"

    async def test_node_timeout(self, pipeline_executor):
        """
        Verifies that the orchestrator correctly handles a node timeout.
        """
        pipeline = [
            ("node1", ControllableNode(0.01)),
            ("node2", ControllableNode(0.6)),
            ("node3", ControllableNode(0.01)),
        ]

        with pytest.raises(NodeTimeoutException) as excinfo:
            await pipeline_executor.execute_pipeline(
                pipeline_id="node_timeout_test",
                nodes=pipeline,
                initial_input=0
            )

        assert excinfo.value.node_id == "node2"

    async def test_pipeline_timeout(self, pipeline_executor):
        """
        Verifies that the orchestrator correctly handles a pipeline timeout.
        """
        pipeline = [
            ("node1", ControllableNode(0.4)),
            ("node2", ControllableNode(0.4)),
            ("node3", ControllableNode(0.4)),
            ("node4", ControllableNode(0.4)),
        ]

        with pytest.raises(PipelineTimeoutException) as excinfo:
            await pipeline_executor.execute_pipeline(
                pipeline_id="pipeline_timeout_test",
                nodes=pipeline,
                initial_input=0
            )

        assert excinfo.value.pipeline_id == "pipeline_timeout_test"
        assert len(excinfo.value.completed_nodes) == 3

    async def test_cancellation(self, pipeline_executor):
        """
        Ensures that the orchestrator properly cancels in-flight operations.
        """
        pipeline = [
            ("node1", ControllableNode(10)),
        ]

        task = asyncio.create_task(
            pipeline_executor.execute_pipeline(
                pipeline_id="cancellation_test",
                nodes=pipeline,
                initial_input=0
            )
        )

        await asyncio.sleep(0.05)
        task.cancel()

        with pytest.raises(asyncio.CancelledError):
            await task

    async def test_error_recovery(self, pipeline_executor):
        """
        Checks the orchestrator's ability to handle and report errors during node execution.
        """
        pipeline = [
            ("node1", ControllableNode(0.01)),
            ("node2", ControllableNode(should_error=True)),
            ("node3", ControllableNode(0.01)),
        ]

        with pytest.raises(ValueError) as excinfo:
            await pipeline_executor.execute_pipeline(
                pipeline_id="error_recovery_test",
                nodes=pipeline,
                initial_input=0
            )

        assert str(excinfo.value) == "Node failed"
