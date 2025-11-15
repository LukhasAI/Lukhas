"""
Unit tests for the adaptive_routing module.
"""

import asyncio
import sys
import unittest
from unittest.mock import MagicMock, patch

import pytest

# Mock lukhas.core.common for isolation
sys.modules['lukhas.core.common'] = MagicMock()

from lukhas.orchestration.adaptive_routing import (
    LeastLoadedStrategy,
    LowestLatencyStrategy,
    Node,
    Router,
)




class TestNode(unittest.TestCase):

    def test_node_initialization(self):
        """Test that a Node is initialized with correct default values."""
        node = Node("node-1", capacity=150)
        self.assertEqual(node.node_id, "node-1")
        self.assertEqual(node.capacity, 150)
        self.assertEqual(node.current_load, 0)
        self.assertEqual(node.average_latency_ms, 0.0)
        self.assertEqual(node.error_rate, 0.0)

    def test_update_metrics_success(self):
        """Test that metrics are updated correctly after a successful request."""
        node = Node("node-1")
        node.update_metrics(success=True, latency_ms=100.0)
        self.assertEqual(node.average_latency_ms, 50.0)
        self.assertEqual(node.error_rate, 0.0)

        node.update_metrics(success=True, latency_ms=200.0)
        self.assertEqual(node.average_latency_ms, 125.0)
        self.assertEqual(node.error_rate, 0.0)

    def test_update_metrics_failure(self):
        """Test that metrics reflect failures correctly."""
        node = Node("node-1")
        node.update_metrics(success=False, latency_ms=500.0)
        self.assertEqual(node.average_latency_ms, 250.0)
        self.assertEqual(node.error_rate, 0.5)

        node.update_metrics(success=True, latency_ms=100.0)
        self.assertEqual(node.average_latency_ms, 175.0)
        self.assertEqual(node.error_rate, 0.25)

    def test_to_dict(self):
        """Test the dictionary representation of a Node."""
        node = Node("node-1")
        node.current_load = 20
        data = node.to_dict()
        self.assertEqual(data["node_id"], "node-1")
        self.assertEqual(data["current_load"], 20)


@pytest.mark.asyncio
class TestRouter:

    @patch('lukhas.orchestration.adaptive_routing.logger')
    async def test_register_and_unregister_node(self, mock_logger):
        """Test that nodes can be registered and unregistered."""
        router = Router()
        assert len(await router.get_all_nodes()) == 0

        await router.register_node("node-1", capacity=50)
        nodes = await router.get_all_nodes()
        assert len(nodes) == 1
        assert nodes[0]["node_id"] == "node-1"
        assert nodes[0]["capacity"] == 50

        await router.unregister_node("node-1")
        assert len(await router.get_all_nodes()) == 0
        mock_logger.info.assert_any_call("Unregistered node: node-1")

    @patch('lukhas.orchestration.adaptive_routing.logger')
    async def test_select_node_no_nodes(self, mock_logger):
        """Test that select_node returns None when no nodes are registered."""
        router = Router()
        node = await router.select_node()
        assert node is None
        mock_logger.warning.assert_called_with("No nodes available for routing.")

    async def test_least_loaded_strategy(self):
        """Test the LeastLoadedStrategy for node selection."""
        router = Router(strategy=LeastLoadedStrategy)
        await router.register_node("node-1", capacity=100)
        await router.register_node("node-2", capacity=100)

        router._nodes["node-1"].current_load = 50
        router._nodes["node-2"].current_load = 20

        selected = await router.select_node()
        assert selected.node_id == "node-2"

    async def test_lowest_latency_strategy(self):
        """Test the LowestLatencyStrategy for node selection."""
        router = Router(strategy=LowestLatencyStrategy)
        await router.register_node("node-1")
        await router.register_node("node-2")

        await router.update_node_metrics("node-1", success=True, latency_ms=100)
        await router.update_node_metrics("node-2", success=True, latency_ms=50)

        selected = await router.select_node()
        assert selected.node_id == "node-2"

        await router.update_node_metrics("node-2", success=True, latency_ms=200)

        selected_after_update = await router.select_node()
        # node-1 latency is 50, node-2 is (50+200)/2 = 125
        assert selected_after_update.node_id == "node-1"

    async def test_update_metrics_nonexistent_node(self):
        """Test that updating a nonexistent node doesn't raise an error."""
        router = Router()
        await router.register_node("node-1")
        # No exception should be raised
        await router.update_node_metrics("node-nonexistent", success=True, latency_ms=100)

        # Ensure other nodes are unaffected
        node_info = await router.get_all_nodes()
        assert node_info[0]['average_latency_ms'] == 0
