"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: node_registry.py
Advanced: node_registry.py
Integration Date: 2025-05-31T07:55:28.134078
"""
from typing import List
from typing import Dict
import streamlit as st

"""
Node Registry System

Provides centralized management of all Cognitive system nodes:
- Maintains node instances and handles their lifecycle
- Manages node relationships and communication
- Enables the clean integration of new node types
- Facilitates message passing between nodes

This component is inspired by Apple's minimalist design principles
and OpenAI's focus on robust AI system architectures.
"""

import importlib
import inspect
import logging
import time
import uuid
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class NodeRegistry:
    """
    Central registry for all system nodes that enables their integration
    and coordinated functioning within the Cognitive system.
    """

    def __init__(self, cognitive_system):
        """
        Initialize the node registry

        Args:
            cognitive_system: Reference to the main Cognitive system
        """
        self.agi = cognitive_system
        self.nodes = {}  # type: Dict[str, Any]
        self.node_types = {}  # type: Dict[str, Type]
        self.node_relationships = {}  # type: Dict[str, Dict[str, List[str]]]
        self.message_bus = MessageBus(self)

        # Node execution metrics
        self.node_execution_stats = {}  # type: Dict[str, Dict[str, Any]]

        logger.info("Node Registry initialized")

    def discover_nodes(self, node_paths: Optional[list[str]] = None) -> None:
        """
        Discover available node types from given paths

        Args:
            node_paths: List of module paths to search for node classes
        """
        if node_paths is None:
            # Default paths to search
            node_paths = [
                "backend.nodes",
                "backend.cognitive",
                "backend.ethical",
                "backend.security",
            ]

        discovered = 0

        for path in node_paths:
            try:
                module = importlib.import_module(path)

                # Find all classes in the module that have "Node" in their name
                for name, obj in inspect.getmembers(module):
                    if (
                        inspect.isclass(obj)
                        and "Node" in name
                        and hasattr(obj, "__init__")
                        and "cognitive_system" in inspect.signature(obj.__init__).parameters
                    ):
                        node_id = self._to_node_id(name)
                        self.node_types[node_id] = obj
                        discovered += 1
                        logger.debug(f"Discovered node type: {name} as {node_id}")

            except ImportError as e:
                logger.warning(f"Could not import module {path}: {e}")

        logger.info(f"Discovered {discovered} node types from {len(node_paths)} paths")

    def register_node_type(self, node_id: str, node_class: type) -> bool:
        """
        Manually register a node type

        Args:
            node_id: ID for the node type
            node_class: The node class

        Returns:
            True if registration successful
        """
        if node_id in self.node_types:
            logger.warning(f"Node type {node_id} already registered")
            return False

        self.node_types[node_id] = node_class
        logger.info(f"Registered node type: {node_id}")
        return True

    def create_node(self, node_type: str, node_id: Optional[str] = None, **kwargs) -> str:
        """
        Create and register a node instance

        Args:
            node_type: Type of node to create
            node_id: Optional ID for the node (generated if not provided)
            **kwargs: Additional parameters for node initialization

        Returns:
            ID of the created node
        """
        if node_type not in self.node_types:
            raise ValueError(f"Unknown node type: {node_type}")

        if node_id is None:
            # Generate a unique ID if not provided
            node_id = f"{node_type}_{str(uuid.uuid4()}[:8]}"  # noqa: invalid-syntax  # TODO: Expected ,, found }
        elif node_id in self.nodes:
            raise ValueError(f"Node ID {node_id} already in use")

        # Create the node instance
        node_class = self.node_types[node_type]
        try:
            node_instance = node_class(self.agi, **kwargs)
            self.nodes[node_id] = node_instance

            # Initialize node relationships
            self.node_relationships[node_id] = {
                "depends_on": [],
                "provides_to": [],
            }

            # Initialize execution stats
            self.node_execution_stats[node_id] = {
                "created_at": time.time(),
                "execution_count": 0,
                "last_execution": None,
                "total_execution_time": 0,
                "average_execution_time": 0,
            }

            logger.info(f"Created node {node_id} of type {node_type}")
            return node_id

        except Exception as e:
            logger.error(f"Error creating node {node_id} of type {node_type}: {e}")
            raise

    def get_node(self, node_id: str) -> Any:
        """
        Get a node by ID

        Args:
            node_id: ID of the node to get

        Returns:
            The node instance
        """
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} not found")

        return self.nodes[node_id]

    def send_message(self, from_node: str, to_node: str, message_type: str, payload: Any) -> str:
        """
        Send a message from one node to another

        Args:
            from_node: Source node ID
            to_node: Target node ID
            message_type: Type of message
            payload: Message payload

        Returns:
            Message ID
        """
        return self.message_bus.send_message(from_node, to_node, message_type, payload)

    def broadcast_message(self, from_node: str, message_type: str, payload: Any) -> list[str]:
        """
        Broadcast a message to all nodes

        Args:
            from_node: Source node ID
            message_type: Type of message
            payload: Message payload

        Returns:
            List of message IDs
        """
        return self.message_bus.broadcast_message(from_node, message_type, payload)

    def establish_relationship(
        self,
        from_node: str,
        to_node: str,
        relationship_type: str = "depends_on",
    ) -> bool:
        """
        Establish a relationship between nodes

        Args:
            from_node: Source node ID
            to_node: Target node ID
            relationship_type: Type of relationship

        Returns:
            True if relationship established
        """
        if from_node not in self.nodes:
            raise ValueError(f"Node {from_node} not found")

        if to_node not in self.nodes:
            raise ValueError(f"Node {to_node} not found")

        if relationship_type == "depends_on":
            if to_node not in self.node_relationships[from_node]["depends_on"]:
                self.node_relationships[from_node]["depends_on"].append(to_node)
                self.node_relationships[to_node]["provides_to"].append(from_node)

        elif relationship_type == "provides_to":
            if to_node not in self.node_relationships[from_node]["provides_to"]:
                self.node_relationships[from_node]["provides_to"].append(to_node)
                self.node_relationships[to_node]["depends_on"].append(from_node)

        else:
            raise ValueError(f"Unknown relationship type: {relationship_type}")

        logger.debug(f"Established {relationship_type} relationship: {from_node} -> {to_node}")
        return True

    def initialize_standard_nodes(self) -> dict[str, str]:
        """
        Initialize the standard set of system nodes

        Returns:
            Dictionary mapping node names to their IDs
        """
        node_ids = {}

        # Define the standard node types to initialize
        standard_nodes = [
            {"type": "intent", "id": "intent"},
            {"type": "memory", "id": "memory"},
            {"type": "ethics", "id": "ethics"},
            {"type": "goal", "id": "goal"},
            {"type": "dao", "id": "dao"},
        ]

        # Create each node
        for node_info in standard_nodes:
            try:
                node_id = self.create_node(node_info["type"], node_info["id"])
                node_ids[node_info["type"]] = node_id
            except Exception as e:
                logger.error(f"Failed to initialize {node_info['type']} node: {e}")

        # Establish standard relationships
        if "intent" in node_ids and "goal" in node_ids:
            self.establish_relationship(node_ids["intent"], node_ids["goal"], "provides_to")

        if "goal" in node_ids and "ethics" in node_ids:
            self.establish_relationship(node_ids["goal"], node_ids["ethics"], "depends_on")

        if "memory" in node_ids and "intent" in node_ids:
            self.establish_relationship(node_ids["memory"], node_ids["intent"], "provides_to")

        logger.info(f"Initialized {len(node_ids)} standard nodes")
        return node_ids

    def get_node_info(self, node_id: str) -> dict[str, Any]:
        """
        Get information about a node

        Args:
            node_id: ID of the node

        Returns:
            Dictionary with node information
        """
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} not found")

        node = self.nodes[node_id]

        # Get node type name
        node_type = None
        for type_id, type_class in self.node_types.items():
            if isinstance(node, type_class):
                node_type = type_id
                break

        # Get basic node info
        info = {
            "id": node_id,
            "type": node_type,
            "relationships": self.node_relationships[node_id],
            "execution_stats": self.node_execution_stats[node_id],
        }

        # Add any public properties
        for attr in dir(node):
            if not attr.startswith("_") and not callable(getattr(node, attr)) and attr not in ["agi", "logger"]:
                info[attr] = getattr(node, attr)

        return info

    def execute_node(self, node_id: str, method_name: str, *args, **kwargs) -> Any:
        """
        Execute a method on a node with timing and metrics

        Args:
            node_id: ID of the node
            method_name: Method to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Method result
        """
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} not found")

        node = self.nodes[node_id]

        if not hasattr(node, method_name) or not callable(getattr(node, method_name)):
            raise ValueError(f"Method {method_name} not found on node {node_id}")

        method = getattr(node, method_name)

        # Record execution metrics
        start_time = time.time()
        try:
            result = method(*args, **kwargs)

            # Update execution stats
            self.node_execution_stats[node_id]["execution_count"] += 1
            execution_time = time.time() - start_time
            self.node_execution_stats[node_id]["last_execution"] = time.time()
            self.node_execution_stats[node_id]["total_execution_time"] += execution_time
            self.node_execution_stats[node_id]["average_execution_time"] = (
                self.node_execution_stats[node_id]["total_execution_time"]
                / self.node_execution_stats[node_id]["execution_count"]
            )

            return result

        except Exception as e:
            logger.error(f"Error executing {method_name} on node {node_id}: {e}")
            raise

    def _to_node_id(self, class_name: str) -> str:
        """Convert a class name to a node ID"""
        # IntentNode -> intent, EthicsNode -> ethics
        name = class_name[:-4] if class_name.endswith("Node") else class_name

        return name.lower()


class MessageBus:
    """
    Message bus for inter-node communication
    """

    def __init__(self, registry):
        self.registry = registry
        self.messages = []  # Message history
        self.subscribers = {}  # Message type subscriptions

    def send_message(self, from_node: str, to_node: str, message_type: str, payload: Any) -> str:
        """
        Send a message from one node to another

        Args:
            from_node: Source node ID
            to_node: Target node ID
            message_type: Type of message
            payload: Message payload

        Returns:
            Message ID
        """
        message_id = str(uuid.uuid4())

        message = {
            "id": message_id,
            "from_node": from_node,
            "to_node": to_node,
            "type": message_type,
            "payload": payload,
            "timestamp": time.time(),
            "processed": False,
        }

        self.messages.append(message)

        # Limit message history
        if len(self.messages) > 1000:
            self.messages = self.messages[-1000:]

        # Process message
        try:
            target_node = self.registry.get_node(to_node)
            if hasattr(target_node, "process_message"):
                target_node.process_message(message_type, payload, from_node)
                message["processed"] = True
            else:
                logger.warning(f"Node {to_node} does not have a process_message method")
        except Exception as e:
            logger.error(f"Error processing message {message_id}: {e}")

        # Notify subscribers
        if message_type in self.subscribers:
            for callback in self.subscribers[message_type]:
                try:
                    callback(message)
                except Exception as e:
                    logger.error(f"Error in message subscriber callback: {e}")

        return message_id

    def broadcast_message(self, from_node: str, message_type: str, payload: Any) -> list[str]:
        """
        Broadcast a message to all nodes

        Args:
            from_node: Source node ID
            message_type: Type of message
            payload: Message payload

        Returns:
            List of message IDs
        """
        message_ids = []

        for node_id in self.registry.nodes:
            if node_id != from_node:  # Don't send to self
                message_id = self.send_message(from_node, node_id, message_type, payload)
                message_ids.append(message_id)

        return message_ids

    def subscribe(self, message_type: str, callback: Callable) -> None:
        """
        Subscribe to a message type

        Args:
            message_type: Type of message to subscribe to
            callback: Callback function to call when message is received
        """
        if message_type not in self.subscribers:
            self.subscribers[message_type] = []

        self.subscribers[message_type].append(callback)

    def get_messages(
        self,
        node_id: Optional[str] = None,
        message_type: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Get messages filtered by node ID and/or message type

        Args:
            node_id: Filter by node ID
            message_type: Filter by message type
            limit: Maximum number of messages to return

        Returns:
            List of messages
        """
        filtered = self.messages

        if node_id is not None:
            filtered = [m for m in filtered if m["from_node"] == node_id or m["to_node"] == node_id]

        if message_type is not None:
            filtered = [m for m in filtered if m["type"] == message_type]

        return filtered[-limit:]
