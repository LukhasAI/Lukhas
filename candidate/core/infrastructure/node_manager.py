import json
import logging
import os
import time
from typing import Any, Optional
import streamlit as st
from typing import Dict
from typing import List

logger = logging.getLogger("NodeManager")


class NodeManager:
    """Manages communication between Lukhas Core and specialized nodes"""

    def __init__(self, core_interface, config_path: Optional[str] = None):
        """Initialize the node manager

        Args:
            core_interface: Interface to the Lukhas core system
            config_path: Optional path to node configuration file
        """
        self.core = core_interface
        self.registered_nodes = {}
        self.node_status = {}
        self.node_dependencies = {}
        self.message_queues = {}

        # Load configuration
        self.config = self._load_config(config_path)

        # Register with core
        if core_interface:
            core_interface.register_component("node_manager", self, self.process_message)

            # Subscribe to node events
            core_interface.subscribe_to_events(
                "node_status_change",
                self.handle_node_status_change,
                "node_manager",
            )

        logger.info("Node manager initialized")

        # Auto-discover nodes if configured
        if self.config.get("auto_discover", False):
            self.discover_nodes()

    def _load_config(self, config_path: Optional[str]) -> dict[str, Any]:
        """Load node manager configuration

        Args:
            config_path: Path to configuration file

        Returns:
            Dict with configuration
        """
        default_config = {
            "nodes_directory": "NODES",
            "auto_discover": True,
            "auto_connect": True,
            "discovery_paths": ["NODES", "MODULES"],
            "node_config": {},
        }

        if config_path and os.path.exists(config_path):
            try:
                with open(config_path) as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in loaded_config:
                            loaded_config[key] = value
                    return loaded_config
            except Exception as e:
                logger.error(f"Error loading node config from {config_path}: {e}")

        return default_config

    def register_node(
        self,
        node_id: str,
        node_instance: Any,
        node_type: str,
        dependencies: Optional[list[str]] = None,
    ) -> bool:
        """Register a node with the manager

        Args:
            node_id: Unique identifier for the node
            node_instance: The node instance
            node_type: Type of node
            dependencies: Optional list of node dependencies

        Returns:
            bool: True if registration was successful
        """
        if node_id in self.registered_nodes:
            logger.warning(f"Node {node_id} already registered")
            return False

        self.registered_nodes[node_id] = {
            "instance": node_instance,
            "type": node_type,
            "registered_at": time.time(),
        }

        self.node_status[node_id] = "connected"
        self.message_queues[node_id] = []
        self.node_dependencies[node_id] = dependencies or []

        logger.info(f"Registered node {node_id} of type {node_type}")

        # Notify core of new node
        if self.core:
            self.core.broadcast_event(
                "node_registered",
                {"node_id": node_id, "node_type": node_type},
                "node_manager",
            )

        return True

    def discover_nodes(self) -> list[str]:
        """Discover and register available nodes

        Returns:
            List of discovered node IDs
        """
        discovered_nodes = []

        # Check each discovery path
        for path in self.config["discovery_paths"]:
            if not os.path.exists(path) or not os.path.isdir(path):
                logger.warning(f"Discovery path does not exist: {path}")
                continue

            logger.info(f"Searching for nodes in {path}")

            # Look for Python files that might be nodes
            for file_name in os.listdir(path):
                if not file_name.endswith(".py"):
                    continue

                # Skip __init__.py and similar
                if file_name.startswith("__"):
                    continue

                # Check if file contains node implementation
                file_path = os.path.join(path, file_name)
                if self._is_node_file(file_path):
                    # Try to load the node
                    node_id = os.path.splitext(file_name)[0].lower()
                    if self._load_node(node_id, file_path):
                        discovered_nodes.append(node_id)

        logger.info(f"Discovered {len(discovered_nodes)} nodes: {', '.join(discovered_nodes)}")
        return discovered_nodes

    def _is_node_file(self, file_path: str) -> bool:
        """Check if a file contains a Lukhas node implementation

        Args:
            file_path: Path to the file

        Returns:
            bool: True if file appears to contain a node
        """
        try:
            with open(file_path) as f:
                content = f.read()

                # Simple heuristic - check for class definitions and Lukhas imports
                has_class = "class" in content
                is_lukhas_related = "Lukhas" in content or "lukhas" in content
                has_process_method = "process_message" in content

                return has_class and is_lukhas_related and has_process_method

        except Exception as e:
            logger.warning(f"Error reading file {file_path}: {e}")
            return False

    def _load_node(self, node_id: str, file_path: str) -> bool:
        """Load and register a node from file

        Args:
            node_id: ID to use for the node
            file_path: Path to the node implementation

        Returns:
            bool: True if node was loaded successfully
        """
        try:
            # Get module path
            module_path = file_path.replace("/", ".")
            if module_path.endswith(".py"):
                module_path = module_path[:-3]

            # Import module
            node_module = __import__(module_path, fromlist=["*"])

            # Find node class (look for classes with process_message method)
            node_class = None
            for attr_name in dir(node_module):
                attr = getattr(node_module, attr_name)
                if isinstance(attr, type) and hasattr(attr, "process_message") and callable(attr.process_message):
                    node_class = attr
                    break

            if not node_class:
                logger.warning(f"No suitable node class found in {file_path}")
                return False

            # Create instance
            node_instance = node_class()

            # Determine node type
            node_type = getattr(node_class, "NODE_TYPE", node_class.__name__)

            # Get dependencies
            dependencies = getattr(node_class, "DEPENDENCIES", [])

            # Register node
            return self.register_node(node_id, node_instance, node_type, dependencies)

        except Exception as e:
            logger.error(f"Error loading node {node_id} from {file_path}: {e}")
            return False

    def dispatch_message(
        self,
        target_node_id: str,
        message: dict[str, Any],
        source: Optional[str] = None,
        priority: int = 5,
    ) -> dict[str, Any]:
        """Send a message to a specific node

        Args:
            target_node_id: Target node ID
            message: Message to send
            source: Source of the message
            priority: Message priority (1-10, higher is more important)

        Returns:
            Dict with dispatch results
        """
        # Check if node exists
        if target_node_id not in self.registered_nodes:
            logger.warning(f"Cannot dispatch message to unknown node: {target_node_id}")
            return {
                "status": "error",
                "error": f"Unknown node: {target_node_id}",
                "timestamp": time.time(),
            }

        # Check if node is connected
        if self.node_status[target_node_id] != "connected":
            logger.warning(f"Cannot dispatch message to disconnected node: {target_node_id}")
            # Queue message for later delivery
            self.message_queues[target_node_id].append((message, priority, time.time()))
            return {
                "status": "queued",
                "node_status": self.node_status[target_node_id],
                "timestamp": time.time(),
            }

        # Prepare message envelope
        message_envelope = {
            "content": message,
            "metadata": {
                "source": source,
                "timestamp": time.time(),
                "priority": priority,
            },
        }

        # Send message to node
        try:
            node_instance = self.registered_nodes[target_node_id]["instance"]
            response = node_instance.process_message(message_envelope)
            return response
        except Exception as e:
            logger.error(f"Error dispatching message to node {target_node_id}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": time.time(),
            }

    def broadcast_to_nodes(
        self,
        message: dict[str, Any],
        node_type: Optional[str] = None,
        source: Optional[str] = None,
    ) -> dict[str, list[dict[str, Any]]]:
        """Broadcast a message to multiple nodes

        Args:
            message: Message to broadcast
            node_type: Optional node type to filter recipients
            source: Source of the message

        Returns:
            Dict with results from each node
        """
        results = {"success": [], "failed": [], "queued": []}

        for node_id, node_info in self.registered_nodes.items():
            # Filter by node type if specified
            if node_type and node_info["type"] != node_type:
                continue

            # Send message to node
            response = self.dispatch_message(node_id, message, source)
            status = response.get("status", "")

            if status == "error":
                results["failed"].append({"node_id": node_id, "error": response.get("error")})
            elif status == "queued":
                results["queued"].append({"node_id": node_id})
            else:
                results["success"].append({"node_id": node_id, "response": response})

        return results

    def process_message(self, message_envelope: dict[str, Any]) -> dict[str, Any]:
        """Process messages from the core

        Args:
            message_envelope: Message envelope from core

        Returns:
            Dict with processing results
        """
        message = message_envelope["content"]
        action = message.get("action", "")

        if action == "send_to_node":
            # Send message to a specific node
            return self.dispatch_message(
                message.get("node_id", ""),
                message.get("message", {}),
                message_envelope["metadata"].get("source"),
                message.get("priority", 5),
            )

        elif action == "broadcast":
            # Broadcast to nodes
            return self.broadcast_to_nodes(
                message.get("message", {}),
                message.get("node_type"),
                message_envelope["metadata"].get("source"),
            )

        elif action == "get_node_status":
            # Get status of nodes
            node_id = message.get("node_id")
            if node_id:
                if node_id in self.node_status:
                    return {
                        "status": "success",
                        "node_id": node_id,
                        "node_status": self.node_status[node_id],
                    }
                else:
                    return {
                        "status": "error",
                        "error": f"Unknown node: {node_id}",
                    }
            else:
                return {"status": "success", "node_status": self.node_status}

        elif action == "discover_nodes":
            # Discover nodes
            discovered = self.discover_nodes()
            return {"status": "success", "discovered_nodes": discovered}

        else:
            logger.warning(f"Unknown action: {action}")
            return {"status": "error", "error": f"Unknown action: {action}"}

    def handle_node_status_change(self, event_envelope: dict[str, Any]) -> None:
        """Handle node status change events

        Args:
            event_envelope: Event data from core
        """
        event_data = event_envelope["data"]
        node_id = event_data.get("node_id")
        new_status = event_data.get("status")

        if node_id and node_id in self.node_status and new_status:
            old_status = self.node_status[node_id]
            self.node_status[node_id] = new_status

            logger.info(f"Node {node_id} status changed: {old_status} -> {new_status}")

            # If node reconnected, process queued messages
            if old_status != "connected" and new_status == "connected":
                self._process_queued_messages(node_id)

    def _process_queued_messages(self, node_id: str) -> None:
        """Process queued messages for a node

        Args:
            node_id: Node ID to process queue for
        """
        if node_id not in self.message_queues:
            return

        queue = self.message_queues[node_id]
        if not queue:
            return

        logger.info(f"Processing {len(queue)} queued messages for node {node_id}")

        # Sort by priority then timestamp
        queue.sort(key=lambda x: (-x[1], x[2]))

        # Process messages
        processed = 0
        for message, priority, timestamp in queue[:]:
            response = self.dispatch_message(node_id, message, None, priority)
            if response.get("status") != "queued":
                queue.remove((message, priority, timestamp))
                processed += 1

        logger.info(f"Processed {processed}/{len(queue)} queued messages for node {node_id}")

        # Update queue
        self.message_queues[node_id] = queue
