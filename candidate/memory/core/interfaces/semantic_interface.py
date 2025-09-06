#!/usr/bin/env python3
import logging
logger = logging.getLogger(__name__)
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - SEMANTIC MEMORY INTERFACE
║ Specialized interface for conceptual and factual knowledge
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: semantic_interface.py
║ Path: memory/core/interfaces/semantic_interface.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Neuroscience Team
╠══════════════════════════════════════════════════════════════════════════════════
║ TECHNICAL FEATURES:
║ • Concept-based knowledge organization
║ • Hierarchical category structures
║ • Semantic relationship mapping
║ • Distributed representation
║ • Slow consolidation patterns
║ • Colony-based redundancy
║ • Inference and reasoning support
║
║ ΛTAG: ΛSEMANTIC, ΛINTERFACE, ΛKNOWLEDGE, ΛCONCEPT, ΛHIERARCHY
╚══════════════════════════════════════════════════════════════════════════════════
"""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Union

import numpy as np

from .memory_interface import (
    BaseMemoryInterface,
    MemoryMetadata,
    MemoryResponse,
    MemoryType,
    ValidationResult,
)


class SemanticRelationType(Enum):
    """Types of semantic relationships"""

    IS_A = "is_a"  # Taxonomic (cat is_a animal)
    PART_OF = "part_of"  # Meronymic (wheel part_of car)
    SIMILAR_TO = "similar_to"  # Similarity
    OPPOSITE_OF = "opposite_of"  # Antonymy
    CAUSES = "causes"  # Causal relationship
    ENABLES = "enables"  # Enabling relationship
    REQUIRES = "requires"  # Dependency
    ASSOCIATED_WITH = "associated_with"  # General association


@dataclass
class SemanticRelation:
    """Semantic relationship between concepts"""

    relation_type: SemanticRelationType
    source_concept: str
    target_concept: str
    strength: float = 1.0  # 0-1 relationship strength
    confidence: float = 1.0  # 0-1 confidence in relation

    # Source information
    derived_from: set[str] = field(default_factory=set)  # Source memory IDs
    created_at: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)

    def update_strength(self, new_evidence: float, learning_rate: float = 0.1):
        """Update relationship strength with new evidence"""
        self.strength = (1 - learning_rate) * self.strength + learning_rate * new_evidence
        self.last_updated = time.time()


@dataclass
class ConceptNode:
    """Node in semantic concept network"""

    concept_id: str
    label: str

    # Content
    definition: str = ""
    attributes: dict[str, Any] = field(default_factory=dict)
    examples: list[str] = field(default_factory=list)

    # Network properties
    category: Optional[str] = None
    abstraction_level: int = 0  # 0=concrete, higher=more abstract

    # Distributed representation
    feature_vector: Optional[np.ndarray] = None
    activation_pattern: Optional[np.ndarray] = None

    # Learning statistics
    activation_count: int = 0
    co_activation_counts: dict[str, int] = field(default_factory=dict)
    consolidation_strength: float = 0.0

    # Source episodic memories
    source_episodes: set[str] = field(default_factory=set)

    def activate(self):
        """Record activation of this concept"""
        self.activation_count += 1

    def co_activate_with(self, other_concept_id: str):
        """Record co-activation with another concept"""
        if other_concept_id not in self.co_activation_counts:
            self.co_activation_counts[other_concept_id] = 0
        self.co_activation_counts[other_concept_id] += 1


@dataclass
class SemanticMemoryContent:
    """Structured content for semantic memories"""

    # Core concept information
    primary_concept: str = ""
    concept_nodes: dict[str, ConceptNode] = field(default_factory=dict)

    # Relationships
    relations: list[SemanticRelation] = field(default_factory=list)

    # Factual assertions
    facts: list[dict[str, Any]] = field(default_factory=list)

    # Hierarchical organization
    category_hierarchy: dict[str, set[str]] = field(default_factory=dict)

    # Source information
    consolidated_from: set[str] = field(default_factory=set)  # Source episodic IDs
    confidence_level: float = 1.0


class SemanticMemoryInterface(BaseMemoryInterface):
    """
    Specialized interface for semantic memories.
    Handles conceptual knowledge with relationships and hierarchies.
    """

    def __init__(
        self,
        colony_id: Optional[str] = None,
        enable_distributed: bool = True,
        concept_similarity_threshold: float = 0.7,
        consolidation_threshold: float = 0.8,
    ):
        super().__init__(
            memory_type=MemoryType.SEMANTIC,
            colony_id=colony_id,
            enable_distributed=enable_distributed,
        )

        self.concept_similarity_threshold = concept_similarity_threshold
        self.consolidation_threshold = consolidation_threshold

        # Semantic-specific storage
        self.semantic_memories: dict[str, SemanticMemoryContent] = {}
        self.concept_network: dict[str, ConceptNode] = {}  # concept_id -> node
        self.relation_network: dict[str, list[SemanticRelation]] = {}  # concept_id -> relations

        # Indices
        self.concept_index: dict[str, set[str]] = defaultdict(set)  # concept -> memory_ids
        self.category_index: dict[str, set[str]] = defaultdict(set)  # category -> memory_ids
        self.feature_index: dict[str, set[str]] = defaultdict(set)  # feature -> concept_ids

        # Consolidation tracking
        self.consolidation_candidates: list[str] = []
        self.inference_cache: dict[str, Any] = {}

        logger.info("SemanticMemoryInterface initialized")

    async def create_memory(
        self,
        content: Any,
        metadata: Optional[MemoryMetadata] = None,
        concept_definitions: Optional[dict[str, str]] = None,
        relationships: Optional[list[SemanticRelation]] = None,
        **kwargs,
    ) -> MemoryResponse:
        """Create new semantic memory with concepts and relationships"""

        # Prepare metadata
        if metadata is None:
            metadata = MemoryMetadata(memory_type=MemoryType.SEMANTIC)

        # Structure semantic content
        if isinstance(content, SemanticMemoryContent):
            semantic_content = content
        else:
            semantic_content = SemanticMemoryContent()

            # Extract concepts from content
            if isinstance(content, dict):
                if "concept" in content:
                    semantic_content.primary_concept = content["concept"]

                # Create concept nodes
                for key, value in content.items():
                    if key in ["concept", "category", "type"]:
                        concept_id = str(value)
                        if concept_id not in semantic_content.concept_nodes:
                            semantic_content.concept_nodes[concept_id] = ConceptNode(
                                concept_id=concept_id, label=str(value)
                            )

        # Add provided concept definitions
        if concept_definitions:
            for concept_id, definition in concept_definitions.items():
                if concept_id not in semantic_content.concept_nodes:
                    semantic_content.concept_nodes[concept_id] = ConceptNode(concept_id=concept_id, label=concept_id)
                semantic_content.concept_nodes[concept_id].definition = definition

        # Add relationships
        if relationships:
            semantic_content.relations.extend(relationships)

        # Store memory
        memory_id = metadata.memory_id
        self.semantic_memories[memory_id] = semantic_content

        # Update concept network
        for concept_node in semantic_content.concept_nodes.values():
            self.concept_network[concept_node.concept_id] = concept_node

        # Update relation network
        for relation in semantic_content.relations:
            source = relation.source_concept
            if source not in self.relation_network:
                self.relation_network[source] = []
            self.relation_network[source].append(relation)

        # Update indices
        self._update_indices(memory_id, semantic_content)

        logger.debug(
            "Semantic memory created",
            memory_id=memory_id,
            primary_concept=semantic_content.primary_concept,
            concept_count=len(semantic_content.concept_nodes),
        )

        return MemoryResponse(
            operation_id=kwargs.get("operation_id", memory_id),
            success=True,
            memory_id=memory_id,
            content=semantic_content,
            metadata=metadata,
        )

    async def read_memory(self, memory_id: str, include_relations: bool = True, **kwargs) -> MemoryResponse:
        """Read semantic memory with optional relationship expansion"""

        if memory_id not in self.semantic_memories:
            return MemoryResponse(
                operation_id=kwargs.get("operation_id", memory_id),
                success=False,
                error_message=f"Memory {memory_id} not found",
            )

        content = self.semantic_memories[memory_id]

        # Expand with current network state if requested
        if include_relations:
            expanded_content = self._expand_with_relations(content)
            content = expanded_content

        return MemoryResponse(
            operation_id=kwargs.get("operation_id", memory_id),
            success=True,
            memory_id=memory_id,
            content=content,
        )

    async def update_memory(
        self,
        memory_id: str,
        content: Any = None,
        metadata: Optional[MemoryMetadata] = None,
        new_relationships: Optional[list[SemanticRelation]] = None,
        **kwargs,
    ) -> MemoryResponse:
        """Update semantic memory with new knowledge"""

        if memory_id not in self.semantic_memories:
            return MemoryResponse(
                operation_id=kwargs.get("operation_id", memory_id),
                success=False,
                error_message=f"Memory {memory_id} not found",
            )

        semantic_content = self.semantic_memories[memory_id]

        # Update content if provided
        if content is not None:
            # Merge new information
            if isinstance(content, dict):
                for key, value in content.items():
                    # Update concept attributes
                    if semantic_content.primary_concept in semantic_content.concept_nodes:
                        concept_node = semantic_content.concept_nodes[semantic_content.primary_concept]
                        concept_node.attributes[key] = value

        # Add new relationships
        if new_relationships:
            semantic_content.relations.extend(new_relationships)

            # Update relation network
            for relation in new_relationships:
                source = relation.source_concept
                if source not in self.relation_network:
                    self.relation_network[source] = []
                self.relation_network[source].append(relation)

        # Update indices
        self._update_indices(memory_id, semantic_content)

        return MemoryResponse(
            operation_id=kwargs.get("operation_id", memory_id),
            success=True,
            memory_id=memory_id,
            content=semantic_content,
        )

    async def delete_memory(self, memory_id: str, **kwargs) -> MemoryResponse:
        """Delete semantic memory and clean up network"""

        if memory_id not in self.semantic_memories:
            return MemoryResponse(
                operation_id=kwargs.get("operation_id", memory_id),
                success=False,
                error_message=f"Memory {memory_id} not found",
            )

        semantic_content = self.semantic_memories[memory_id]

        # Remove from indices
        self._remove_from_indices(memory_id, semantic_content)

        # Clean up concept network (if no other memories reference concepts)
        for concept_id in semantic_content.concept_nodes:
            # Check if concept is used elsewhere
            still_used = False
            for other_memory in self.semantic_memories.values():
                if other_memory != semantic_content and concept_id in other_memory.concept_nodes:
                    still_used = True
                    break

            if not still_used:
                self.concept_network.pop(concept_id, None)
                self.relation_network.pop(concept_id, None)

        # Remove memory
        del self.semantic_memories[memory_id]

        return MemoryResponse(
            operation_id=kwargs.get("operation_id", memory_id),
            success=True,
            memory_id=memory_id,
        )

    async def search_memories(
        self,
        query: Union[str, dict[str, Any]],
        filters: Optional[dict[str, Any]] = None,
        limit: int = 50,
        **kwargs,
    ) -> list[MemoryResponse]:
        """Search semantic memories by concept, relationship, or content"""

        results = []

        # Concept-based search
        if isinstance(query, str):
            # Direct concept lookup
            if query in self.concept_index:
                memory_ids = self.concept_index[query]
                for memory_id in list(memory_ids)[:limit]:
                    content = self.semantic_memories[memory_id]
                    results.append(
                        MemoryResponse(
                            operation_id=kwargs.get("operation_id", f"search_{memory_id}"),
                            success=True,
                            memory_id=memory_id,
                            content=content,
                        )
                    )

            # Partial text search in definitions and attributes
            else:
                for memory_id, content in self.semantic_memories.items():
                    match_found = False

                    # Search in concept definitions
                    for concept_node in content.concept_nodes.values():
                        if (
                            query.lower() in concept_node.definition.lower()
                            or query.lower() in concept_node.label.lower()
                        ):
                            match_found = True
                            break

                    if match_found:
                        results.append(
                            MemoryResponse(
                                operation_id=kwargs.get("operation_id", f"search_{memory_id}"),
                                success=True,
                                memory_id=memory_id,
                                content=content,
                            )
                        )

                    if len(results) >= limit:
                        break

        # Structured search
        elif isinstance(query, dict):
            for memory_id, content in self.semantic_memories.items():
                match = True

                if "concept" in query and query["concept"] not in content.concept_nodes:
                    match = False

                if "category" in query:
                    category_match = False
                    for concept_node in content.concept_nodes.values():
                        if concept_node.category == query["category"]:
                            category_match = True
                            break
                    if not category_match:
                        match = False

                if "relation_type" in query:
                    relation_match = False
                    for relation in content.relations:
                        if relation.relation_type.value == query["relation_type"]:
                            relation_match = True
                            break
                    if not relation_match:
                        match = False

                if match:
                    results.append(
                        MemoryResponse(
                            operation_id=kwargs.get("operation_id", f"search_{memory_id}"),
                            success=True,
                            memory_id=memory_id,
                            content=content,
                        )
                    )

                if len(results) >= limit:
                    break

        return results

    async def validate_memory(self, memory_id: str, **kwargs) -> ValidationResult:
        """Validate semantic memory consistency"""

        if memory_id not in self.semantic_memories:
            return ValidationResult.INVALID

        content = self.semantic_memories[memory_id]

        # Check for circular relationships
        if self._has_circular_relations(content):
            return ValidationResult.CORRUPTED

        # Check concept consistency
        for concept_node in content.concept_nodes.values():
            if not concept_node.label:
                return ValidationResult.INCOMPLETE

        return ValidationResult.VALID

    # Semantic-specific methods

    async def consolidate_from_episodic(
        self,
        episodic_memories: list[dict[str, Any]],
        consolidation_strength: float = 1.0,
    ) -> MemoryResponse:
        """Consolidate episodic memories into semantic knowledge"""

        # Extract concepts and patterns from episodic memories
        extracted_concepts = {}
        extracted_relations = []

        for episode in episodic_memories:
            episode_id = episode.get("memory_id", "unknown")
            content = episode.get("content", {})

            # Extract concepts
            if isinstance(content, dict):
                for key, value in content.items():
                    if key in ["type", "category", "concept", "event"]:
                        concept_id = str(value)
                        if concept_id not in extracted_concepts:
                            extracted_concepts[concept_id] = ConceptNode(concept_id=concept_id, label=concept_id)

                        # Add this episode as source
                        extracted_concepts[concept_id].source_episodes.add(episode_id)
                        extracted_concepts[concept_id].consolidation_strength += consolidation_strength

        # Create semantic memory from extracted knowledge
        semantic_content = SemanticMemoryContent(
            concept_nodes=extracted_concepts,
            relations=extracted_relations,
            consolidated_from={ep.get("memory_id", "unknown") for ep in episodic_memories},
        )

        # Determine primary concept
        if extracted_concepts:
            # Use most consolidated concept
            primary = max(extracted_concepts.values(), key=lambda c: c.consolidation_strength)
            semantic_content.primary_concept = primary.concept_id

        return await self.create_memory(content=semantic_content, consolidation_source="episodic_memories")

    async def infer_relationships(
        self,
        concept_a: str,
        concept_b: str,
        relation_types: Optional[list[SemanticRelationType]] = None,
    ) -> list[SemanticRelation]:
        """Infer potential relationships between concepts"""

        cache_key = f"{concept_a}_{concept_b}"
        if cache_key in self.inference_cache:
            return self.inference_cache[cache_key]

        inferred_relations = []

        # Simple inference rules - in practice would be more sophisticated
        if concept_a in self.concept_network and concept_b in self.concept_network:
            node_a = self.concept_network[concept_a]
            node_b = self.concept_network[concept_b]

            # Co-activation suggests association
            if concept_b in node_a.co_activation_counts:
                strength = min(1.0, node_a.co_activation_counts[concept_b] / 10.0)
                inferred_relations.append(
                    SemanticRelation(
                        relation_type=SemanticRelationType.ASSOCIATED_WITH,
                        source_concept=concept_a,
                        target_concept=concept_b,
                        strength=strength,
                        confidence=0.6,  # Lower confidence for inferred relations
                    )
                )

            # Category hierarchy inference
            if node_a.category == node_b.category and node_a.category:
                inferred_relations.append(
                    SemanticRelation(
                        relation_type=SemanticRelationType.SIMILAR_TO,
                        source_concept=concept_a,
                        target_concept=concept_b,
                        strength=0.7,
                        confidence=0.8,
                    )
                )

        self.inference_cache[cache_key] = inferred_relations
        return inferred_relations

    def get_concept_hierarchy(self) -> dict[str, Any]:
        """Get hierarchical organization of concepts"""

        hierarchy = {}
        categories = defaultdict(list)

        # Group by categories
        for concept_node in self.concept_network.values():
            if concept_node.category:
                categories[concept_node.category].append(concept_node)

        # Build hierarchy tree
        for category, concepts in categories.items():
            hierarchy[category] = {
                "concept_count": len(concepts),
                "concepts": [c.concept_id for c in concepts],
                "average_activation": (np.mean([c.activation_count for c in concepts]) if concepts else 0),
                "subcategories": self._find_subcategories(concepts),
            }

        return hierarchy

    def activate_concept_network(self, concepts: list[str]) -> dict[str, float]:
        """Simulate spreading activation in concept network"""

        activations = {}

        # Initialize with input concepts
        for concept in concepts:
            if concept in self.concept_network:
                activations[concept] = 1.0
                self.concept_network[concept].activate()

        # Spread activation through relationships
        for _ in range(3):  # 3 spreading steps
            new_activations = activations.copy()

            for active_concept, activation in activations.items():
                if active_concept in self.relation_network:
                    for relation in self.relation_network[active_concept]:
                        target = relation.target_concept
                        spread_activation = activation * relation.strength * 0.7  # Decay

                        if target in new_activations:
                            new_activations[target] = max(new_activations[target], spread_activation)
                        else:
                            new_activations[target] = spread_activation

                        # Record co-activation
                        if target in self.concept_network:
                            self.concept_network[active_concept].co_activate_with(target)

            activations = new_activations

        return activations

    def _expand_with_relations(self, content: SemanticMemoryContent) -> SemanticMemoryContent:
        """Expand semantic content with current relation network state"""

        expanded = SemanticMemoryContent(
            primary_concept=content.primary_concept,
            concept_nodes=content.concept_nodes.copy(),
            relations=content.relations.copy(),
            facts=content.facts.copy(),
        )

        # Add current network relations for concepts in this memory
        for concept_id in content.concept_nodes:
            if concept_id in self.relation_network:
                for relation in self.relation_network[concept_id]:
                    if relation not in expanded.relations:
                        expanded.relations.append(relation)

        return expanded

    def _has_circular_relations(self, content: SemanticMemoryContent) -> bool:
        """Check for circular relationships"""

        # Build graph from relations
        graph = defaultdict(set)
        for relation in content.relations:
            graph[relation.source_concept].add(relation.target_concept)

        # Simple cycle detection using DFS
        visited = set()
        rec_stack = set()

        def has_cycle(node):
            visited.add(node)
            rec_stack.add(node)

            for neighbor in graph[node]:
                if (neighbor not in visited and has_cycle(neighbor)) or neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        return any(node not in visited and has_cycle(node) for node in graph)

    def _find_subcategories(self, concepts: list[ConceptNode]) -> dict[str, Any]:
        """Find subcategories within a concept group"""

        subcategories = defaultdict(list)

        # Group by abstraction level
        for concept in concepts:
            level_key = f"level_{concept.abstraction_level}"
            subcategories[level_key].append(concept.concept_id)

        return dict(subcategories)

    def _update_indices(self, memory_id: str, content: SemanticMemoryContent):
        """Update search indices for memory"""

        # Concept index
        for concept_id in content.concept_nodes:
            self.concept_index[concept_id].add(memory_id)

        # Category index
        for concept_node in content.concept_nodes.values():
            if concept_node.category:
                self.category_index[concept_node.category].add(memory_id)

    def _remove_from_indices(self, memory_id: str, content: SemanticMemoryContent):
        """Remove memory from all indices"""

        # Concept index
        for concept_id in content.concept_nodes:
            self.concept_index[concept_id].discard(memory_id)

        # Category index
        for concept_node in content.concept_nodes.values():
            if concept_node.category:
                self.category_index[concept_node.category].discard(memory_id)

    def get_metrics(self) -> dict[str, Any]:
        """Get semantic interface metrics"""
        base_metrics = super().get_metrics()

        semantic_metrics = {
            "total_semantic_memories": len(self.semantic_memories),
            "total_concepts": len(self.concept_network),
            "total_relations": sum(len(relations) for relations in self.relation_network.values()),
            "concept_categories": len(self.category_index),
            "consolidation_candidates": len(self.consolidation_candidates),
            "inference_cache_size": len(self.inference_cache),
        }

        return {**base_metrics, **semantic_metrics}