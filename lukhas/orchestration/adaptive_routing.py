"""
Dynamic, adaptive request routing for LUKHAS orchestration.

Provides a routing mechanism that can dynamically select the best "node"
(e.g., a worker, a service, an API endpoint) to handle a request based on
real-time performance metrics like latency and load. This allows the system
to be more resilient and efficient, automatically favoring healthier or
faster nodes.
"""

import asyncio
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Dict, List, Optional, Type

# Mock for a common LUKHAS utility, as per instructions
try:
    from lukhas.core.common import get_logger
except ImportError:
    import logging
    get_logger = logging.getLogger

logger = get_logger(__name__)


class Node:
    """Represents a destination for routing, e.g., a service instance."""

    def __init__(self, node_id: str, capacity: int = 100):
        self.node_id = node_id
        self.capacity = capacity
        self.last_seen = time.monotonic()

        # Metrics for routing decisions
        self.current_load = 0
        self.average_latency_ms = 0.0
        self.error_rate = 0.0

    def update_metrics(self, success: bool, latency_ms: float):
        """Update the node's performance metrics after a request."""
        self.last_seen = time.monotonic()

        # Simple moving average for latency
        self.average_latency_ms = (self.average_latency_ms + latency_ms) / 2

        # Simple error rate calculation
        current_error_value = 1 if not success else 0
        self.error_rate = (self.error_rate + current_error_value) / 2

    def to_dict(self):
        """Return a dictionary representation of the node's state."""
        return {
            "node_id": self.node_id,
            "capacity": self.capacity,
            "current_load": self.current_load,
            "average_latency_ms": self.average_latency_ms,
            "error_rate": self.error_rate,
            "last_seen": self.last_seen
        }


class RoutingStrategy(ABC):
    """Abstract base class for all routing strategies."""

    @abstractmethod
    def select_node(self, nodes: List[Node]) -> Optional[Node]:
        """Selects the best node from a list of available nodes."""
        pass


class LeastLoadedStrategy(RoutingStrategy):
    """Routes to the node with the lowest current load."""

    def select_node(self, nodes: List[Node]) -> Optional[Node]:
        if not nodes:
            return None
        return min(nodes, key=lambda n: n.current_load / n.capacity)


class LowestLatencyStrategy(RoutingStrategy):
    """Routes to the node with the lowest average latency."""

    def select_node(self, nodes: List[Node]) -> Optional[Node]:
        if not nodes:
            return None
        return min(nodes, key=lambda n: n.average_latency_ms)


class Router:
    """A dynamic router for selecting the best node for a request."""

    def __init__(self, strategy: Type[RoutingStrategy] = LeastLoadedStrategy):
        self._nodes: Dict[str, Node] = {}
        self._strategy = strategy()
        self._lock = asyncio.Lock()

    async def register_node(self, node_id: str, capacity: int = 100):
        """Add or update a node in the router's registry."""
        async with self._lock:
            if node_id not in self._nodes:
                self._nodes[node_id] = Node(node_id, capacity)
                logger.info(f"Registered new node: {node_id}")
            else:
                self._nodes[node_id].capacity = capacity
                logger.info(f"Updated capacity for node: {node_id}")

    async def unregister_node(self, node_id: str):
        """Remove a node from the registry."""
        async with self._lock:
            if node_id in self._nodes:
                del self._nodes[node_id]
                logger.info(f"Unregistered node: {node_id}")

    async def select_node(self) -> Optional[Node]:
        """Select the best node using the configured routing strategy."""
        async with self._lock:
            available_nodes = list(self._nodes.values())

        if not available_nodes:
            logger.warning("No nodes available for routing.")
            return None

        selected_node = self._strategy.select_node(available_nodes)

        if selected_node:
            logger.debug(f"Selected node {selected_node.node_id} via {self._strategy.__class__.__name__}")
        else:
            logger.error("Routing strategy failed to select a node.")

        return selected_node

    async def update_node_metrics(self, node_id: str, success: bool, latency_ms: float):
        """Update the metrics for a specific node."""
        async with self._lock:
            if node_id in self._nodes:
                self._nodes[node_id].update_metrics(success, latency_ms)

    async def get_all_nodes(self) -> List[Dict]:
        """Return the state of all registered nodes."""
        async with self._lock:
            return [node.to_dict() for node in self._nodes.values()]
