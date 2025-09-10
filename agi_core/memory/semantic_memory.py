"""
Semantic Memory Graph for AGI

Advanced semantic memory system that stores and organizes factual knowledge,
concepts, and their relationships in a graph-based structure.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

import networkx as nx
import numpy as np

logger = logging.getLogger(__name__)


class NodeType(Enum):
    """Types of semantic nodes."""

    CONCEPT = "concept"  # Abstract concepts
    ENTITY = "entity"  # Concrete entities
    RELATIONSHIP = "relationship"  # Relationship descriptors
    PROPERTY = "property"  # Properties and attributes
    PROCESS = "process"  # Processes and procedures
    PRINCIPLE = "principle"  # Rules and principles
    FACT = "fact"  # Factual statements


class RelationType(Enum):
    """Types of relationships between semantic nodes."""

    IS_A = "is_a"  # Taxonomy/inheritance
    PART_OF = "part_of"  # Composition
    RELATED_TO = "related_to"  # General association
    CAUSES = "causes"  # Causal relationship
    SIMILAR_TO = "similar_to"  # Similarity
    OPPOSITE_TO = "opposite_to"  # Opposition
    DEPENDS_ON = "depends_on"  # Dependency
    USED_FOR = "used_for"  # Purpose/function
    LOCATED_IN = "located_in"  # Spatial relationship
    OCCURS_DURING = "occurs_during"  # Temporal relationship


@dataclass
class SemanticNode:
    """
    Node in the semantic memory graph representing a concept or entity.
    """

    node_id: str
    name: str
    node_type: NodeType
    description: str

    # Vector representation
    embedding_vector: Optional[np.ndarray] = None

    # Knowledge attributes
    properties: dict[str, Any] = field(default_factory=dict)
    aliases: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    # LUKHAS Integration
    constellation_relevance: dict[str, float] = field(default_factory=dict)
    importance_score: float = 0.5

    # Temporal information
    created_time: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0

    # Learning and validation
    confidence: float = 1.0  # Confidence in node accuracy
    evidence_count: int = 0  # Number of supporting evidences
    contradiction_count: int = 0  # Number of contradicting evidences

    def access_node(self):
        """Record access to this node."""
        self.last_accessed = datetime.now(timezone.utc)
        self.access_count += 1

    def add_evidence(self, supporting: bool = True):
        """Add evidence for or against this node."""
        if supporting:
            self.evidence_count += 1
        else:
            self.contradiction_count += 1

        # Update confidence based on evidence
        total_evidence = self.evidence_count + self.contradiction_count
        if total_evidence > 0:
            self.confidence = self.evidence_count / total_evidence

    def get_constellation_score(self, star: str) -> float:
        """Get relevance score for constellation star."""
        return self.constellation_relevance.get(star, 0.0)


@dataclass
class SemanticRelation:
    """
    Edge in the semantic memory graph representing a relationship.
    """

    relation_id: str
    source_node_id: str
    target_node_id: str
    relation_type: RelationType

    # Relationship attributes
    strength: float = 1.0  # Strength of the relationship (0-1)
    confidence: float = 1.0  # Confidence in relationship validity
    bidirectional: bool = False  # Whether relationship works both ways

    # Context and metadata
    context: Optional[str] = None  # Context in which relationship holds
    evidence_sources: list[str] = field(default_factory=list)
    properties: dict[str, Any] = field(default_factory=dict)

    # Temporal information
    created_time: datetime = field(default_factory=datetime.now)
    last_validated: datetime = field(default_factory=datetime.now)

    def validate_relation(self, confidence_update: Optional[float] = None):
        """Validate and update relationship confidence."""
        self.last_validated = datetime.now(timezone.utc)
        if confidence_update is not None:
            self.confidence = max(0.0, min(1.0, confidence_update))


@dataclass
class SemanticQuery:
    """Query for semantic memory search."""

    # Text-based queries
    query_text: Optional[str] = None
    concepts: Optional[list[str]] = None

    # Type filters
    node_types: Optional[list[NodeType]] = None
    relation_types: Optional[list[RelationType]] = None

    # Graph traversal parameters
    max_depth: int = 2  # Maximum traversal depth
    min_confidence: float = 0.5  # Minimum confidence threshold
    include_relations: bool = True  # Include relationship information

    # Constellation context
    constellation_filter: Optional[dict[str, float]] = None

    # Result parameters
    max_results: int = 20


class SemanticMemoryGraph:
    """
    Advanced Semantic Memory Graph for AGI

    Manages factual knowledge and concept relationships in a graph structure
    with advanced querying and reasoning capabilities.
    """

    def __init__(self):
        # Graph storage
        self.nodes: dict[str, SemanticNode] = {}
        self.relations: dict[str, SemanticRelation] = {}
        self.graph = nx.MultiDiGraph()  # NetworkX graph for algorithms

        # Indexing structures
        self.type_index: dict[NodeType, set[str]] = {nt: set() for nt in NodeType}
        self.name_index: dict[str, str] = {}  # name -> node_id mapping
        self.tag_index: dict[str, set[str]] = {}  # tag -> node_ids mapping

        # Configuration
        self.max_nodes = 50000  # Maximum nodes to store
        self.similarity_threshold = 0.8  # Threshold for node similarity
        self.relation_decay_rate = 0.01  # Relation confidence decay rate

        # Statistics
        self.stats = {
            "total_nodes": 0,
            "total_relations": 0,
            "node_types": {nt.value: 0 for nt in NodeType},
            "relation_types": {rt.value: 0 for rt in RelationType},
            "avg_node_degree": 0.0,
            "graph_density": 0.0,
        }

    async def add_node(self, node: SemanticNode) -> bool:
        """Add a semantic node to the graph."""
        try:
            # Check for existing node with same name
            if node.name.lower() in self.name_index:
                existing_id = self.name_index[node.name.lower()]
                logger.warning(f"Node with name '{node.name}' already exists: {existing_id}")
                return False

            # Store node
            self.nodes[node.node_id] = node
            self.graph.add_node(node.node_id, data=node)

            # Update indices
            self.type_index[node.node_type].add(node.node_id)
            self.name_index[node.name.lower()] = node.node_id

            # Index aliases
            for alias in node.aliases:
                self.name_index[alias.lower()] = node.node_id

            # Index tags
            for tag in node.tags:
                if tag not in self.tag_index:
                    self.tag_index[tag] = set()
                self.tag_index[tag].add(node.node_id)

            # Update statistics
            self.stats["total_nodes"] += 1
            self.stats["node_types"][node.node_type.value] += 1

            logger.debug(f"Added semantic node: {node.name} ({node.node_type.value})")
            return True

        except Exception as e:
            logger.error(f"Error adding node {node.node_id}: {e}")
            return False

    async def add_relation(self, relation: SemanticRelation) -> bool:
        """Add a semantic relationship to the graph."""
        try:
            # Validate that both nodes exist
            if relation.source_node_id not in self.nodes:
                logger.error(f"Source node {relation.source_node_id} not found")
                return False

            if relation.target_node_id not in self.nodes:
                logger.error(f"Target node {relation.target_node_id} not found")
                return False

            # Store relation
            self.relations[relation.relation_id] = relation

            # Add to NetworkX graph
            self.graph.add_edge(
                relation.source_node_id, relation.target_node_id, key=relation.relation_id, relation=relation
            )

            # Add bidirectional edge if specified
            if relation.bidirectional:
                reverse_relation_id = f"{relation.relation_id}_reverse"
                self.graph.add_edge(
                    relation.target_node_id, relation.source_node_id, key=reverse_relation_id, relation=relation
                )

            # Update statistics
            self.stats["total_relations"] += 1
            self.stats["relation_types"][relation.relation_type.value] += 1

            # Update graph metrics
            await self._update_graph_metrics()

            logger.debug(
                f"Added relation: {relation.source_node_id} -> {relation.target_node_id} ({relation.relation_type.value})"
            )
            return True

        except Exception as e:
            logger.error(f"Error adding relation {relation.relation_id}: {e}")
            return False

    async def find_node(self, name: str, node_type: Optional[NodeType] = None) -> Optional[SemanticNode]:
        """Find node by name with optional type filter."""
        node_id = self.name_index.get(name.lower())
        if not node_id:
            return None

        node = self.nodes.get(node_id)
        if node and (node_type is None or node.node_type == node_type):
            node.access_node()
            return node

        return None

    async def get_node(self, node_id: str) -> Optional[SemanticNode]:
        """Get node by ID."""
        node = self.nodes.get(node_id)
        if node:
            node.access_node()
        return node

    async def search_nodes(self, query: SemanticQuery) -> list[tuple[SemanticNode, float]]:
        """Search for nodes based on query criteria."""
        candidates = []

        # Text-based search
        if query.query_text:
            candidates.extend(await self._text_search_nodes(query.query_text, query.max_results * 2))

        # Concept-based search
        if query.concepts:
            for concept in query.concepts:
                node = await self.find_node(concept)
                if node:
                    candidates.append((node, 1.0))  # Exact match gets full score

        # Type filter
        if query.node_types:
            type_candidates = []
            for node_type in query.node_types:
                for node_id in self.type_index[node_type]:
                    node = self.nodes[node_id]
                    type_candidates.append((node, 0.8))  # Type match gets high score
            candidates.extend(type_candidates)

        # If no specific criteria, get all nodes
        if not query.query_text and not query.concepts and not query.node_types:
            candidates = [(node, 0.5) for node in self.nodes.values()]

        # Apply confidence filter
        if query.min_confidence > 0:
            candidates = [(node, score) for node, score in candidates if node.confidence >= query.min_confidence]

        # Apply constellation filter
        if query.constellation_filter:
            constellation_candidates = []
            for node, base_score in candidates:
                constellation_score = 0.0
                for star, threshold in query.constellation_filter.items():
                    if node.get_constellation_score(star) >= threshold:
                        constellation_score += node.get_constellation_score(star)

                if constellation_score > 0:
                    # Boost score based on constellation alignment
                    final_score = base_score + constellation_score * 0.3
                    constellation_candidates.append((node, final_score))

            candidates = constellation_candidates

        # Remove duplicates and sort by score
        unique_candidates = {}
        for node, score in candidates:
            if node.node_id not in unique_candidates or score > unique_candidates[node.node_id][1]:
                unique_candidates[node.node_id] = (node, score)

        results = list(unique_candidates.values())
        results.sort(key=lambda x: x[1], reverse=True)

        return results[: query.max_results]

    async def get_related_nodes(
        self,
        node_id: str,
        relation_types: Optional[list[RelationType]] = None,
        max_depth: int = 1,
        min_strength: float = 0.1,
    ) -> dict[str, list[tuple[SemanticNode, SemanticRelation]]]:
        """Get nodes related to the given node."""
        if node_id not in self.nodes:
            return {}

        results = {}
        visited = set()
        queue = [(node_id, 0)]  # (node_id, depth)

        while queue:
            current_id, depth = queue.pop(0)

            if current_id in visited or depth > max_depth:
                continue

            visited.add(current_id)

            # Get outgoing relations
            for successor_id in self.graph.successors(current_id):
                edges = self.graph.get_edge_data(current_id, successor_id)

                for edge_data in edges.values():
                    relation = edge_data["relation"]

                    # Apply filters
                    if relation_types and relation.relation_type not in relation_types:
                        continue

                    if relation.strength < min_strength:
                        continue

                    # Add to results
                    depth_key = f"depth_{depth + 1}"
                    if depth_key not in results:
                        results[depth_key] = []

                    successor_node = self.nodes[successor_id]
                    results[depth_key].append((successor_node, relation))

                    # Add to queue for next depth level
                    if depth + 1 < max_depth:
                        queue.append((successor_id, depth + 1))

        return results

    async def find_path(
        self, source_node_id: str, target_node_id: str, max_length: int = 5
    ) -> Optional[list[tuple[SemanticNode, SemanticRelation]]]:
        """Find shortest path between two nodes."""
        if source_node_id not in self.nodes or target_node_id not in self.nodes:
            return None

        try:
            # Use NetworkX to find shortest path
            path_nodes = nx.shortest_path(self.graph, source_node_id, target_node_id)

            if len(path_nodes) > max_length + 1:  # +1 because path includes both endpoints
                return None

            # Convert to node-relation pairs
            path_with_relations = []
            for i in range(len(path_nodes) - 1):
                current_id = path_nodes[i]
                next_id = path_nodes[i + 1]

                # Get the relation between these nodes
                edge_data = self.graph.get_edge_data(current_id, next_id)
                if edge_data:
                    # Take the first available relation (could be enhanced to choose best)
                    relation = next(iter(edge_data.values()))["relation"]
                    path_with_relations.append((self.nodes[current_id], relation))

            # Add the final node
            path_with_relations.append((self.nodes[target_node_id], None))

            return path_with_relations

        except nx.NetworkXNoPath:
            return None
        except Exception as e:
            logger.error(f"Error finding path: {e}")
            return None

    async def get_node_clusters(self, similarity_threshold: float = 0.8) -> list[list[str]]:
        """Find clusters of similar nodes."""
        clusters = []
        processed = set()

        for node_id, node in self.nodes.items():
            if node_id in processed or node.embedding_vector is None:
                continue

            # Find similar nodes
            cluster = [node_id]
            processed.add(node_id)

            for other_id, other_node in self.nodes.items():
                if other_id in processed or other_node.embedding_vector is None:
                    continue

                # Calculate similarity
                similarity = np.dot(node.embedding_vector, other_node.embedding_vector) / (
                    np.linalg.norm(node.embedding_vector) * np.linalg.norm(other_node.embedding_vector)
                )

                if similarity >= similarity_threshold:
                    cluster.append(other_id)
                    processed.add(other_id)

            if len(cluster) > 1:
                clusters.append(cluster)

        return clusters

    async def validate_relations(self, confidence_threshold: float = 0.5) -> int:
        """Validate and clean up low-confidence relations."""
        relations_removed = 0

        relations_to_remove = []
        for relation_id, relation in self.relations.items():
            if relation.confidence < confidence_threshold:
                relations_to_remove.append(relation_id)

        for relation_id in relations_to_remove:
            await self.remove_relation(relation_id)
            relations_removed += 1

        logger.info(f"Removed {relations_removed} low-confidence relations")
        return relations_removed

    async def remove_relation(self, relation_id: str) -> bool:
        """Remove a relation from the graph."""
        if relation_id not in self.relations:
            return False

        try:
            relation = self.relations[relation_id]

            # Remove from NetworkX graph
            if self.graph.has_edge(relation.source_node_id, relation.target_node_id, relation_id):
                self.graph.remove_edge(relation.source_node_id, relation.target_node_id, relation_id)

            # Remove bidirectional edge if it exists
            reverse_id = f"{relation_id}_reverse"
            if self.graph.has_edge(relation.target_node_id, relation.source_node_id, reverse_id):
                self.graph.remove_edge(relation.target_node_id, relation.source_node_id, reverse_id)

            # Remove from storage
            del self.relations[relation_id]

            # Update statistics
            self.stats["total_relations"] -= 1
            self.stats["relation_types"][relation.relation_type.value] -= 1

            await self._update_graph_metrics()

            return True

        except Exception as e:
            logger.error(f"Error removing relation {relation_id}: {e}")
            return False

    async def _text_search_nodes(self, query_text: str, max_results: int) -> list[tuple[SemanticNode, float]]:
        """Search nodes based on text similarity."""
        results = []
        query_lower = query_text.lower()

        for node in self.nodes.values():
            score = 0.0

            # Exact name match
            if node.name.lower() == query_lower:
                score = 1.0
            # Name contains query
            elif query_lower in node.name.lower():
                score = 0.8
            # Description contains query
            elif query_lower in node.description.lower():
                score = 0.6
            # Alias match
            elif any(query_lower in alias.lower() for alias in node.aliases):
                score = 0.7
            # Tag match
            elif any(query_lower in tag.lower() for tag in node.tags):
                score = 0.5

            if score > 0:
                # Boost based on importance and confidence
                final_score = score * node.importance_score * node.confidence
                results.append((node, final_score))

        # Sort by score and return top results
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:max_results]

    async def _update_graph_metrics(self):
        """Update graph-level metrics."""
        if self.stats["total_nodes"] > 0:
            # Average node degree
            total_degree = sum(self.graph.degree(node) for node in self.graph.nodes())
            self.stats["avg_node_degree"] = total_degree / self.stats["total_nodes"]

            # Graph density
            max_edges = self.stats["total_nodes"] * (self.stats["total_nodes"] - 1)
            if max_edges > 0:
                self.stats["graph_density"] = self.stats["total_relations"] / max_edges

    def get_semantic_stats(self) -> dict[str, Any]:
        """Get comprehensive semantic memory statistics."""
        # Calculate additional metrics
        high_confidence_nodes = sum(1 for node in self.nodes.values() if node.confidence > 0.8)
        high_confidence_relations = sum(1 for rel in self.relations.values() if rel.confidence > 0.8)

        # Most connected nodes
        if self.graph.nodes():
            node_degrees = [(node_id, self.graph.degree(node_id)) for node_id in self.graph.nodes()]
            node_degrees.sort(key=lambda x: x[1], reverse=True)
            top_connected = node_degrees[:5]
        else:
            top_connected = []

        stats = {
            **self.stats,
            "quality_metrics": {
                "high_confidence_nodes": high_confidence_nodes,
                "high_confidence_relations": high_confidence_relations,
                "confidence_node_ratio": high_confidence_nodes / max(1, self.stats["total_nodes"]),
                "confidence_relation_ratio": high_confidence_relations / max(1, self.stats["total_relations"]),
            },
            "connectivity": {
                "most_connected_nodes": [(self.nodes[node_id].name, degree) for node_id, degree in top_connected],
                "isolated_nodes": sum(1 for node_id in self.graph.nodes() if self.graph.degree(node_id) == 0),
                "strongly_connected_components": len(list(nx.strongly_connected_components(self.graph))),
            },
        }

        return stats

    def export_graph(self, format: str = "json") -> str:
        """Export graph in specified format."""
        if format == "json":
            export_data = {
                "nodes": {
                    node_id: {
                        "name": node.name,
                        "type": node.node_type.value,
                        "description": node.description,
                        "properties": node.properties,
                        "importance": node.importance_score,
                        "confidence": node.confidence,
                    }
                    for node_id, node in self.nodes.items()
                },
                "relations": {
                    rel_id: {
                        "source": rel.source_node_id,
                        "target": rel.target_node_id,
                        "type": rel.relation_type.value,
                        "strength": rel.strength,
                        "confidence": rel.confidence,
                    }
                    for rel_id, rel in self.relations.items()
                },
                "metadata": {"export_time": datetime.now(timezone.utc).isoformat(), "stats": self.get_semantic_stats()},
            }

            return json.dumps(export_data, indent=2)

        else:
            raise ValueError(f"Unsupported export format: {format}")
