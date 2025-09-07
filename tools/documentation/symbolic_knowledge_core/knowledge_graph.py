"""
SystemKnowledgeGraph: The core knowledge representation system for DocuTutor.
Represents system knowledge as a graph of interconnected nodes representing
code elements, documentation, and concepts.
"""
import streamlit as st

import logging
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class NodeType(str, Enum):
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    API_ENDPOINT = "api_endpoint"
    PARAMETER = "parameter"
    RETURN_VALUE = "return_value"
    DATA_ENTITY = "data_entity"
    REQUIREMENT = "requirement"
    FEATURE = "feature"
    CONCEPT = "concept"


class RelationshipType(str, Enum):
    CONTAINS = "contains"
    CALLS = "calls"
    INHERITS_FROM = "inherits_from"
    IMPLEMENTS = "implements"
    HAS_PARAMETER = "has_parameter"
    RETURNS = "returns"
    REFERENCES = "references"
    MODIFIES = "modifies"
    RELATED_TO = "related_to"
    DOC_FOR = "documentation_for"
    EXPLAINS = "explains"


class SKGNode(BaseModel):
    id: str = Field(description="Unique identifier for the node")
    node_type: NodeType
    name: str
    description: Optional[str] = None
    source_location: Optional[str] = None
    properties: dict[str, Any] = Field(default_factory=dict)
    tags: set[str] = Field(default_factory=set)


class SKGRelationship(BaseModel):
    source_id: str
    target_id: str
    type: RelationshipType
    properties: dict[str, Any] = Field(default_factory=dict)


class SystemKnowledgeGraph:
    """The core knowledge graph representing system components and their relationships."""

    def __init__(self):
        self._nodes: dict[str, SKGNode] = {}
        self._relationships: list[SKGRelationship] = []
        self._edges_from: dict[str, list[SKGRelationship]] = {}  # Source -> relationships
        self._edges_to: dict[str, list[SKGRelationship]] = {}  # Target -> relationships
        logger.info("SystemKnowledgeGraph initialized")

    def add_node(self, node: SKGNode) -> bool:
        """Add a node to the graph. Returns True if added/updated."""
        self._nodes[node.id] = node
        logger.debug(f"Added/updated node: {node.id} ({node.node_type})")
        return True

    def get_node(self, node_id: str) -> Optional[SKGNode]:
        """Retrieve a node by its ID."""
        return self._nodes.get(node_id)

    def add_relationship(self, relationship: SKGRelationship) -> bool:
        """Add a relationship between nodes. Returns True if successful."""
        if not (self.get_node(relationship.source_id) and self.get_node(relationship.target_id)):
            logger.warning("Cannot add relationship: Source or target node missing")
            return False

        # Avoid duplicates
        for rel in self._edges_from.get(relationship.source_id, []):
            if rel.target_id == relationship.target_id and rel.type == relationship.type:
                return True

        self._relationships.append(relationship)
        self._edges_from.setdefault(relationship.source_id, []).append(relationship)
        self._edges_to.setdefault(relationship.target_id, []).append(relationship)
        logger.debug(f"Added relationship: {relationship.source_id} -[{relationship.type}]-> {relationship.target_id}")
        return True

    def get_outgoing_relationships(
        self, node_id: str, rel_type: Optional[RelationshipType] = None
    ) -> list[SKGRelationship]:
        """Get all relationships originating from a node."""
        rels = self._edges_from.get(node_id, [])
        if rel_type:
            return [r for r in rels if r.type == rel_type]
        return rels

    def get_incoming_relationships(
        self, node_id: str, rel_type: Optional[RelationshipType] = None
    ) -> list[SKGRelationship]:
        """Get all relationships targeting a node."""
        rels = self._edges_to.get(node_id, [])
        if rel_type:
            return [r for r in rels if r.type == rel_type]
        return rels

    def find_nodes_by_type(self, node_type: NodeType) -> list[SKGNode]:
        """Find all nodes of a given type."""
        return [node for node in self._nodes.values() if node.node_type == node_type]

    def find_node_by_name_and_type(self, name: str, node_type: NodeType) -> Optional[SKGNode]:
        """Find a node by its name and type."""
        for node in self._nodes.values():
            if node.name == name and node.node_type == node_type:
                return node
        return None

    def get_connected_nodes(
        self,
        node_id: str,
        relationship_type: RelationshipType,
        direction: str = "outgoing",
    ) -> list[SKGNode]:
        """Get nodes connected to the given node by a specific relationship type."""
        connected_node_ids = set()

        if direction == "outgoing":
            rels = self.get_outgoing_relationships(node_id, relationship_type)
            connected_node_ids = {rel.target_id for rel in rels}
        elif direction == "incoming":
            rels = self.get_incoming_relationships(node_id, relationship_type)
            connected_node_ids = {rel.source_id for rel in rels}

        return [self.get_node(nid) for nid in connected_node_ids if self.get_node(nid)]

    def get_neighborhood(self, node_id: str, depth: int = 1) -> dict[str, Any]:
        """Get a subgraph around a node. Useful for understanding context."""
        if not self.get_node(node_id):
            return {}

        neighborhood = {"center_node": self.get_node(node_id), "connections": []}

        # For Phase 1, just get immediate connections
        for rel_type in RelationshipType:
            outgoing = self.get_connected_nodes(node_id, rel_type, "outgoing")
            incoming = self.get_connected_nodes(node_id, rel_type, "incoming")

            if outgoing:
                neighborhood["connections"].append({"type": rel_type, "direction": "outgoing", "nodes": outgoing})
            if incoming:
                neighborhood["connections"].append({"type": rel_type, "direction": "incoming", "nodes": incoming})

        return neighborhood

    def clear(self):
        """Clear all nodes and relationships from the graph."""
        self._nodes.clear()
        self._relationships.clear()
        self._edges_from.clear()
        self._edges_to.clear()
        logger.info("SystemKnowledgeGraph cleared")
