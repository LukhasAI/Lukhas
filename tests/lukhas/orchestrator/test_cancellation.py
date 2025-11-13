"""
Tests for the Orchestrator Cancellation System
"""

import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from lukhas.orchestrator.cancellation import CancellationRegistry
from lukhas.orchestrator.config import OrchestratorConfig, TimeoutConfig
from lukhas.orchestrator.exceptions import (
    CancellationException,
    NodeTimeoutException,
    PipelineTimeoutException,
)
from lukhas.orchestrator.pipeline import PipelineExecutor

# Mock missing modules
sys_mock = MagicMock()
sys_mock.modules = {
    "lukhas.monitoring.metrics": MagicMock(),
}


@patch.dict("sys.modules", sys_mock.modules)
class TestCancellation(unittest.TestCase):
    def setUp(self):
        self.registry = CancellationRegistry()
        self.config = OrchestratorConfig(
            timeouts=TimeoutConfig(
                node_timeout_ms=100,
                pipeline_timeout_ms=500,
                cleanup_grace_ms=50,
            )
        )
        self.executor = PipelineExecutor(self.config, self.registry)

    @pytest.mark.asyncio
    async def test_cancellation_token_set(self):
        """Verify that the cancellation token is correctly set on cancel."""
        pipeline_id = "test_pipeline"
        token = self.registry.register(pipeline_id)
        self.assertFalse(token.is_set())

        await self.registry.cancel(pipeline_id)
        self.assertTrue(token.is_set())

    @pytest.mark.asyncio
    async def test_cleanup_handlers_executed_on_cancel(self):
        """Verify that cleanup handlers are executed when a pipeline is cancelled."""
        pipeline_id = "test_pipeline"
        self.registry.register(pipeline_id)
        handler_mock = AsyncMock()
        self.registry.register_cleanup_handler(pipeline_id, handler_mock)

        await self.registry.cancel(pipeline_id)
        handler_mock.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_partial_results_stored_and_retrieved(self):
        """Verify that partial results are correctly stored and retrieved."""
        pipeline_id = "test_pipeline"
        self.registry.register(pipeline_id)
        self.registry.store_partial_result(
            pipeline_id, "node_1", {"output": "result_1"}
        )
        self.registry.store_partial_result(
            pipeline_id, "node_2", {"output": "result_2"}
        )

        results = self.registry.get_partial_results(pipeline_id)
        self.assertEqual(len(results), 2)
        self.assertEqual(results["node_1"], {"output": "result_1"})

    @pytest.mark.asyncio
    async def test_pipeline_cancellation_propagates(self):
        """Verify that cancellation correctly propagates through the pipeline."""
        pipeline_id = "test_pipeline_cancel"

        async def long_running_node(data):
            await asyncio.sleep(1)
            return data

        nodes = [("node_1", long_running_node)]

        async def cancel_after():
            await asyncio.sleep(0.05)
            await self.registry.cancel(pipeline_id)

        # Run pipeline and cancellation concurrently
        with self.assertRaises(CancellationException):
            await asyncio.gather(
                self.executor.execute_pipeline(pipeline_id, nodes, {}),
                cancel_after(),
            )

    @pytest.mark.asyncio
    async def test_pipeline_timeout_returns_partial_results(self):
        """Verify that a pipeline timeout returns partial results."""
        pipeline_id = "test_pipeline_timeout"

        async def fast_node(data):
            return {"fast_output": True}

        async def slow_node(data):
            await asyncio.sleep(1)
            return {}

        nodes = [("fast_node", fast_node), ("slow_node", slow_node)]

        with self.assertRaises(PipelineTimeoutException) as cm:
            await self.executor.execute_pipeline(pipeline_id, nodes, {})

        self.assertEqual(len(cm.exception.completed_nodes), 1)
        self.assertEqual(cm.exception.completed_nodes[0], "fast_node")
        self.assertIn("fast_node", cm.exception.partial_results)
        self.assertEqual(
            cm.exception.partial_results["fast_node"], {"fast_output": True}
        )

    @pytest.mark.asyncio
    async def test_node_timeout_triggers_cancellation(self):
        """Verify that a node timeout triggers pipeline cancellation."""
        pipeline_id = "test_node_timeout"
        token = self.registry.register(pipeline_id)

        async def slow_node(data):
            await asyncio.sleep(0.2)
            return data

        nodes = [("slow_node", slow_node)]
        handler_mock = AsyncMock()
        self.registry.register_cleanup_handler(pipeline_id, handler_mock)

        with self.assertRaises(NodeTimeoutException):
            await self.executor.execute_pipeline(pipeline_id, nodes, {})

        self.assertTrue(token.is_set())
        handler_mock.assert_awaited_once()
