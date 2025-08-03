# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: collapse_mesh.py
# MODULE: orchestration.brain.mesh.collapse_mesh
# DESCRIPTION: Defines the symbolic collapse mesh for the LUKHAS brain.
# DEPENDENCIES: datetime, typing
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════
# {AIM}{brain}
# {AIM}{collapse}
# ΛORIGIN_AGENT: Jules-02
# ΛTASK_ID: 02-JULY12-MEMORY-CONT
# ΛCOMMIT_WINDOW: post-ZIP
# ΛAPPROVED_BY: Human Overseer (Gonzalo)

from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

class CollapseNode:
    """
    A node in the symbolic collapse mesh.
    """

    def __init__(self, node_id: str, node_type: str):
        """
        Initializes a CollapseNode.

        Args:
            node_id (str): The unique ID of the node.
            node_type (str): The type of the node.
        """
        self.node_id: str = node_id
        self.node_type: str = node_type
        self.status: str = "online"
        self.last_heartbeat: datetime = datetime.now(timezone.utc)
        self.neighbors: List["CollapseNode"] = []

    def add_neighbor(self, neighbor: "CollapseNode") -> None:
        """
        Adds a neighbor to the node.

        Args:
            neighbor (CollapseNode): The neighbor node to add.
        """
        self.neighbors.append(neighbor)

    def heartbeat(self) -> None:
        """
        Updates the node's heartbeat.
        """
        self.last_heartbeat = datetime.now(timezone.utc)

class CollapseMesh:
    """
    The symbolic collapse mesh.
    """

    def __init__(self):
        """
        Initializes the CollapseMesh.
        """
        self.nodes: Dict[str, CollapseNode] = {}

    def add_node(self, node_id: str, node_type: str) -> None:
        """
        Adds a node to the mesh.

        Args:
            node_id (str): The unique ID of the node.
            node_type (str): The type of the node.
        """
        if node_id not in self.nodes:
            self.nodes[node_id] = CollapseNode(node_id, node_type)

    def add_edge(self, node1_id: str, node2_id: str) -> None:
        """
        Adds an edge between two nodes in the mesh.

        Args:
            node1_id (str): The ID of the first node.
            node2_id (str): The ID of the second node.
        """
        if node1_id in self.nodes and node2_id in self.nodes:
            self.nodes[node1_id].add_neighbor(self.nodes[node2_id])
            self.nodes[node2_id].add_neighbor(self.nodes[node1_id])

    def get_node(self, node_id: str) -> Optional[CollapseNode]:
        """
        Gets a node from the mesh.

        Args:
            node_id (str): The ID of the node to get.

        Returns:
            Optional[CollapseNode]: The node if it exists, otherwise None.
        """
        return self.nodes.get(node_id)
