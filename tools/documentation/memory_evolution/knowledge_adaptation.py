"""
Knowledge Adaptation System for DocuTutor.
Handles the evolution and adaptation of knowledge over time.
"""

from datetime import datetime
from typing import Optional


class KnowledgeNode:

    def __init__(self, content: str, metadata: dict):
        self.content = content
        self.metadata = metadata
        self.confidence = 1.0
        self.last_accessed = datetime.now()
        self.access_count = 0
        self.relationships: dict[str, float] = {}  # node_id -> relationship_strength

    def access(self):
        """Update access statistics for this node."""
        self.access_count += 1
        self.last_accessed = datetime.now()

    def update_confidence(self, new_confidence: float):
        """Update the confidence score for this knowledge."""
        self.confidence = max(0.0, min(1.0, new_confidence))

    def add_relationship(self, node_id: str, strength: float):
        """Add or update a relationship with another node."""
        self.relationships[node_id] = max(0.0, min(1.0, strength))


class KnowledgeGraph:

    def __init__(self):
        self.nodes: dict[str, KnowledgeNode] = {}
        self.embedding_model = None  # Placeholder for embedding model

    def add_node(self, node_id: str, content: str, metadata: dict) -> KnowledgeNode:
        """Add a new knowledge node to the graph."""
        node = KnowledgeNode(content, metadata)
        self.nodes[node_id] = node
        return node

    def get_node(self, node_id: str) -> Optional[KnowledgeNode]:
        """Retrieve a node by its ID."""
        return self.nodes.get(node_id)

    def update_relationships(
        self, node_id: str, related_ids: list[str], strengths: list[float]
    ):
        """Update relationships for a node with related nodes."""
        if node_id not in self.nodes:
            raise KeyError(f"Node {node_id} does not exist")

        node = self.nodes[node_id]
        for related_id, strength in zip(related_ids, strengths):
            if related_id in self.nodes:
                node.add_relationship(related_id, strength)


class KnowledgeAdaptation:

    def __init__(self):
        self.knowledge_graph = KnowledgeGraph()
        self.decay_rate = 0.1
        self.update_threshold = 0.5

    def add_knowledge(self, content: str, metadata: dict) -> str:
        """Add new knowledge to the system."""
        node_id = f"node_{len(self.knowledge_graph.nodes)}"
        self.knowledge_graph.add_node(node_id, content, metadata)
        return node_id

    def update_knowledge(self, node_id: str, new_content: str, new_metadata: dict):
        """Update existing knowledge based on new information."""
        node = self.knowledge_graph.get_node(node_id)
        if node is None:
            raise KeyError(f"Node {node_id} does not exist")

        # Update content and metadata
        node.content = new_content
        node.metadata.update(new_metadata)

        # Reset confidence and update access time
        node.confidence = 1.0
        node.access()

    def decay_knowledge(self):
        """Apply time-based decay to knowledge confidence."""
        now = datetime.now()
        for node in self.knowledge_graph.nodes.values():
            time_diff = (now - node.last_accessed).total_seconds() / (24 * 3600)  # Days
            decay = self.decay_rate * time_diff
            node.update_confidence(node.confidence * (1 - decay))

    def get_related_knowledge(self, node_id: str, threshold: float = 0.5) -> list[str]:
        """Get related knowledge nodes above a relationship strength threshold."""
        node = self.knowledge_graph.get_node(node_id)
        if node is None:
            raise KeyError(f"Node {node_id} does not exist")

        return [
            related_id
            for related_id, strength in node.relationships.items()
            if strength >= threshold
        ]
