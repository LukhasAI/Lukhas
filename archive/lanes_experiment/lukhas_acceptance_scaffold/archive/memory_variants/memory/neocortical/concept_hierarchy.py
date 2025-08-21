#!/usr/bin/env python3
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - CONCEPT HIERARCHY
║ Hierarchical organization of semantic concepts
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: concept_hierarchy.py
║ Path: memory/neocortical/concept_hierarchy.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Neuroscience Team
╚══════════════════════════════════════════════════════════════════════════════════
"""

import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ConceptNode:
    """Node in the concept hierarchy"""

    concept_id: str
    name: str
    level: int = 0  # 0 = most specific, higher = more abstract

    # Hierarchical relationships
    parent: Optional["ConceptNode"] = None
    children: set["ConceptNode"] = field(default_factory=set)

    # Properties
    attributes: dict[str, Any] = field(default_factory=dict)
    examples: list[str] = field(default_factory=list)

    # Activation and learning
    activation: float = 0.0
    base_activation: float = 0.1
    learning_rate: float = 0.01

    # Statistics
    access_count: int = 0
    creation_time: float = field(default_factory=lambda: time.time())

    def add_child(self, child: "ConceptNode"):
        """Add child concept"""
        self.children.add(child)
        child.parent = self
        child.level = self.level + 1

    def remove_child(self, child: "ConceptNode"):
        """Remove child concept"""
        if child in self.children:
            self.children.remove(child)
            child.parent = None

    def get_ancestors(self) -> list["ConceptNode"]:
        """Get all ancestor nodes up to root"""
        ancestors = []
        current = self.parent
        while current:
            ancestors.append(current)
            current = current.parent
        return ancestors

    def get_descendants(self) -> list["ConceptNode"]:
        """Get all descendant nodes"""
        descendants = []
        queue = deque(self.children)

        while queue:
            node = queue.popleft()
            descendants.append(node)
            queue.extend(node.children)

        return descendants

    def get_siblings(self) -> set["ConceptNode"]:
        """Get sibling nodes (same parent)"""
        if not self.parent:
            return set()
        return self.parent.children - {self}

    def calculate_similarity(self, other: "ConceptNode") -> float:
        """Calculate similarity to another concept"""
        # Find common ancestor
        ancestors1 = set(self.get_ancestors() + [self])
        ancestors2 = set(other.get_ancestors() + [other])
        common = ancestors1 & ancestors2

        if not common:
            return 0.0

        # Find lowest common ancestor (most specific)
        lca = max(common, key=lambda n: n.level)

        # Similarity based on distance to LCA
        dist1 = self.level - lca.level
        dist2 = other.level - lca.level
        max_dist = max(dist1, dist2)

        if max_dist == 0:
            return 1.0  # Same concept

        return 1.0 / (1.0 + max_dist)


class ConceptHierarchy:
    """
    Manages hierarchical organization of concepts.
    Supports dynamic reorganization based on learning.
    """

    def __init__(
        self,
        max_depth: int = 7,
        branching_factor: int = 10,
        similarity_threshold: float = 0.7,
        enable_dynamic_reorganization: bool = True,
    ):
        self.max_depth = max_depth
        self.branching_factor = branching_factor
        self.similarity_threshold = similarity_threshold
        self.enable_dynamic_reorganization = enable_dynamic_reorganization

        # Root node
        self.root = ConceptNode(concept_id="root", name="UNIVERSAL", level=0)

        # Concept storage
        self.concepts: dict[str, ConceptNode] = {"root": self.root}
        self.name_index: dict[str, str] = {"UNIVERSAL": "root"}  # name -> concept_id

        # Learning statistics
        self.total_concepts = 1
        self.reorganizations = 0
        self.average_depth = 0.0

        logger.info(
            "ConceptHierarchy initialized",
            max_depth=max_depth,
            branching_factor=branching_factor,
        )

    def add_concept(
        self,
        name: str,
        parent_name: Optional[str] = None,
        attributes: Optional[dict[str, Any]] = None,
        examples: Optional[list[str]] = None,
    ) -> str:
        """Add new concept to hierarchy"""

        # Check if concept already exists
        if name in self.name_index:
            concept_id = self.name_index[name]
            concept = self.concepts[concept_id]

            # Update attributes and examples
            if attributes:
                concept.attributes.update(attributes)
            if examples:
                concept.examples.extend(examples)

            return concept_id

        # Create new concept
        concept_id = f"concept_{self.total_concepts}"
        concept = ConceptNode(
            concept_id=concept_id,
            name=name,
            attributes=attributes or {},
            examples=examples or [],
        )

        # Find parent
        if parent_name and parent_name in self.name_index:
            parent_id = self.name_index[parent_name]
            parent = self.concepts[parent_id]
        else:
            # Find best parent based on similarity
            parent = self._find_best_parent(concept)

        # Add to hierarchy
        parent.add_child(concept)

        # Check depth constraint
        if concept.level > self.max_depth:
            # Need to reorganize
            self._compress_path(concept)

        # Check branching factor
        if len(parent.children) > self.branching_factor:
            # Need to split
            self._split_node(parent)

        # Store concept
        self.concepts[concept_id] = concept
        self.name_index[name] = concept_id
        self.total_concepts += 1

        # Update statistics
        self._update_statistics()

        logger.debug(
            "Concept added",
            concept_id=concept_id,
            name=name,
            parent=parent.name,
            level=concept.level,
        )

        return concept_id

    def find_concept(self, name: str) -> Optional[ConceptNode]:
        """Find concept by name"""
        if name in self.name_index:
            return self.concepts[self.name_index[name]]
        return None

    def get_path(self, concept_name: str) -> list[str]:
        """Get path from root to concept"""
        concept = self.find_concept(concept_name)
        if not concept:
            return []

        path = [concept.name]
        current = concept.parent

        while current:
            path.append(current.name)
            current = current.parent

        return list(reversed(path))

    def activate_concept(
        self, concept_name: str, activation_strength: float = 1.0, spread: bool = True
    ) -> dict[str, float]:
        """
        Activate concept and optionally spread activation.
        Returns activation levels of affected concepts.
        """

        concept = self.find_concept(concept_name)
        if not concept:
            return {}

        # Direct activation
        concept.activation = min(1.0, concept.base_activation + activation_strength)
        concept.access_count += 1

        activations = {concept.name: concept.activation}

        if spread:
            # Spread to parents (bottom-up)
            current = concept.parent
            strength = activation_strength
            while current and strength > 0.1:
                strength *= 0.7  # Decay
                current.activation = min(1.0, current.activation + strength)
                activations[current.name] = current.activation
                current = current.parent

            # Spread to children (top-down)
            for child in concept.children:
                child_strength = activation_strength * 0.5
                child.activation = min(1.0, child.activation + child_strength)
                activations[child.name] = child.activation

            # Lateral spread to siblings
            for sibling in concept.get_siblings():
                sibling_strength = activation_strength * 0.3
                sibling.activation = min(1.0, sibling.activation + sibling_strength)
                activations[sibling.name] = sibling.activation

        return activations

    def find_common_ancestor(
        self, concept1_name: str, concept2_name: str
    ) -> Optional[ConceptNode]:
        """Find lowest common ancestor of two concepts"""

        concept1 = self.find_concept(concept1_name)
        concept2 = self.find_concept(concept2_name)

        if not concept1 or not concept2:
            return None

        # Get ancestor sets
        ancestors1 = set(concept1.get_ancestors() + [concept1])
        ancestors2 = set(concept2.get_ancestors() + [concept2])

        common = ancestors1 & ancestors2
        if not common:
            return None

        # Return most specific (highest level)
        return max(common, key=lambda n: n.level)

    def get_semantic_distance(self, concept1_name: str, concept2_name: str) -> float:
        """
        Calculate semantic distance between concepts.
        Returns value between 0 (same) and 1 (unrelated).
        """

        concept1 = self.find_concept(concept1_name)
        concept2 = self.find_concept(concept2_name)

        if not concept1 or not concept2:
            return 1.0

        similarity = concept1.calculate_similarity(concept2)
        return 1.0 - similarity

    def extract_ontology(self, min_examples: int = 2) -> dict[str, Any]:
        """
        Extract ontology from hierarchy.
        Returns structured representation of concepts and relationships.
        """

        ontology = {
            "concepts": {},
            "relationships": {"is_a": [], "part_of": [], "related_to": []},
            "properties": {},
        }

        # Extract concepts
        for _concept_id, concept in self.concepts.items():
            if len(concept.examples) >= min_examples or concept.level <= 2:
                ontology["concepts"][concept.name] = {
                    "level": concept.level,
                    "attributes": concept.attributes,
                    "examples": concept.examples[:5],  # Limit examples
                    "access_count": concept.access_count,
                }

                # Extract is-a relationships
                if concept.parent:
                    ontology["relationships"]["is_a"].append(
                        {"child": concept.name, "parent": concept.parent.name}
                    )

                # Extract properties
                for attr_name, attr_value in concept.attributes.items():
                    if attr_name not in ontology["properties"]:
                        ontology["properties"][attr_name] = []
                    ontology["properties"][attr_name].append(
                        {"concept": concept.name, "value": attr_value}
                    )

        return ontology

    def prune_unused(self, min_access_count: int = 1, preserve_depth: int = 3):
        """Prune concepts that are rarely accessed"""

        pruned = []

        for concept_id in list(self.concepts.keys()):
            concept = self.concepts[concept_id]

            # Don't prune root or high-level concepts
            if concept.level <= preserve_depth:
                continue

            # Don't prune if frequently accessed
            if concept.access_count >= min_access_count:
                continue

            # Don't prune if has many children
            if len(concept.children) > 2:
                continue

            # Prune concept
            self._remove_concept(concept)
            pruned.append(concept.name)

        if pruned:
            logger.info(f"Pruned {len(pruned)} unused concepts")
            self._update_statistics()

        return pruned

    def _find_best_parent(self, new_concept: ConceptNode) -> ConceptNode:
        """Find best parent for new concept based on attributes"""

        best_parent = self.root
        best_score = 0.0

        # BFS to find best match
        queue = deque([self.root])

        while queue:
            candidate = queue.popleft()

            # Calculate match score
            score = self._calculate_match_score(new_concept, candidate)

            if score > best_score:
                best_score = score
                best_parent = candidate

            # Don't go too deep
            if candidate.level < self.max_depth - 1:
                queue.extend(candidate.children)

        return best_parent

    def _calculate_match_score(
        self, concept: ConceptNode, parent_candidate: ConceptNode
    ) -> float:
        """Calculate how well concept fits under parent"""

        score = 0.0

        # Attribute overlap
        if concept.attributes and parent_candidate.attributes:
            common_attrs = set(concept.attributes.keys()) & set(
                parent_candidate.attributes.keys()
            )
            if common_attrs:
                score += len(common_attrs) / len(concept.attributes.keys())

        # Name similarity (simple)
        if (
            concept.name in parent_candidate.name
            or parent_candidate.name in concept.name
        ):
            score += 0.5

        # Check examples
        if concept.examples and parent_candidate.examples:
            common_examples = set(concept.examples) & set(parent_candidate.examples)
            if common_examples:
                score += 0.3

        return score

    def _compress_path(self, deep_concept: ConceptNode):
        """Compress path when depth exceeds limit"""

        # Find middle nodes to remove
        path = [deep_concept]
        current = deep_concept.parent

        while current and current.parent:
            path.append(current)
            current = current.parent

        if len(path) <= 2:
            return

        # Remove middle node with fewest children
        middle_nodes = path[1:-1]
        to_remove = min(middle_nodes, key=lambda n: len(n.children))

        # Relink
        for child in to_remove.children:
            to_remove.parent.add_child(child)

        self._remove_concept(to_remove)
        self.reorganizations += 1

    def _split_node(self, overloaded_node: ConceptNode):
        """Split node when it has too many children"""

        if len(overloaded_node.children) <= self.branching_factor:
            return

        # Cluster children into groups
        children_list = list(overloaded_node.children)

        # Simple clustering by name similarity
        clusters = defaultdict(list)

        for child in children_list:
            # Find first letter or attribute
            cluster_key = child.name[0].upper() if child.name else "OTHER"
            clusters[cluster_key].append(child)

        # Create intermediate nodes for large clusters
        for cluster_key, cluster_children in clusters.items():
            if len(cluster_children) > 2:
                # Create intermediate node
                intermediate = ConceptNode(
                    concept_id=f"intermediate_{cluster_key}_{self.total_concepts}",
                    name=f"{overloaded_node.name}_{cluster_key}",
                    attributes={"cluster_type": cluster_key},
                )

                # Relink children
                overloaded_node.add_child(intermediate)
                for child in cluster_children:
                    overloaded_node.remove_child(child)
                    intermediate.add_child(child)

                self.concepts[intermediate.concept_id] = intermediate
                self.name_index[intermediate.name] = intermediate.concept_id
                self.total_concepts += 1

        self.reorganizations += 1

    def _remove_concept(self, concept: ConceptNode):
        """Remove concept from hierarchy"""

        # Relink children to parent
        if concept.parent:
            for child in concept.children:
                concept.parent.add_child(child)
            concept.parent.remove_child(concept)

        # Remove from indices
        del self.concepts[concept.concept_id]
        del self.name_index[concept.name]

    def _update_statistics(self):
        """Update hierarchy statistics"""

        total_depth = 0
        count = 0

        for concept in self.concepts.values():
            total_depth += concept.level
            count += 1

        self.average_depth = total_depth / max(count, 1)

    def decay_activations(self, decay_rate: float = 0.1):
        """Decay all concept activations"""

        for concept in self.concepts.values():
            concept.activation *= 1 - decay_rate
            if concept.activation < 0.01:
                concept.activation = 0.0

    def get_metrics(self) -> dict[str, Any]:
        """Get hierarchy metrics"""

        # Calculate depth distribution
        depth_dist = defaultdict(int)
        for concept in self.concepts.values():
            depth_dist[concept.level] += 1

        # Find most accessed concepts
        accessed_concepts = [
            (c.name, c.access_count)
            for c in self.concepts.values()
            if c.access_count > 0
        ]
        accessed_concepts.sort(key=lambda x: x[1], reverse=True)

        return {
            "total_concepts": len(self.concepts),
            "average_depth": self.average_depth,
            "max_depth_used": max(depth_dist.keys()) if depth_dist else 0,
            "reorganizations": self.reorganizations,
            "depth_distribution": dict(depth_dist),
            "most_accessed": accessed_concepts[:5],
        }


# Example usage
if __name__ == "__main__":
    import time

    hierarchy = ConceptHierarchy()

    print("=== Concept Hierarchy Demo ===\n")

    # Add concepts
    hierarchy.add_concept("Animal")
    hierarchy.add_concept("Mammal", parent_name="Animal")
    hierarchy.add_concept(
        "Dog", parent_name="Mammal", attributes={"legs": 4, "sound": "bark"}
    )
    hierarchy.add_concept(
        "Cat", parent_name="Mammal", attributes={"legs": 4, "sound": "meow"}
    )
    hierarchy.add_concept("Bird", parent_name="Animal")
    hierarchy.add_concept("Eagle", parent_name="Bird", attributes={"can_fly": True})

    # Add more specific concepts
    hierarchy.add_concept(
        "Golden Retriever",
        parent_name="Dog",
        attributes={"color": "golden", "size": "large"},
        examples=["Buddy", "Max"],
    )
    hierarchy.add_concept(
        "Siamese Cat",
        parent_name="Cat",
        attributes={"color": "cream", "origin": "Thailand"},
        examples=["Luna", "Milo"],
    )

    # Test path retrieval
    print("Paths:")
    print(f"  Golden Retriever: {' -> '.join(hierarchy.get_path('Golden Retriever'))}")
    print(f"  Eagle: {' -> '.join(hierarchy.get_path('Eagle'))}")

    # Test activation spreading
    print("\n--- Activation Test ---")
    activations = hierarchy.activate_concept(
        "Dog", activation_strength=0.8, spread=True
    )
    print("Activated concepts:")
    for concept, activation in sorted(
        activations.items(), key=lambda x: x[1], reverse=True
    ):
        print(f"  {concept}: {activation:.2f}")

    # Test semantic distance
    print("\n--- Semantic Distance ---")
    print(f"Dog <-> Cat: {hierarchy.get_semantic_distance('Dog', 'Cat'):.2f}")
    print(f"Dog <-> Eagle: {hierarchy.get_semantic_distance('Dog', 'Eagle'):.2f}")
    print(
        f"Golden Retriever <-> Siamese Cat: {hierarchy.get_semantic_distance('Golden Retriever', 'Siamese Cat'):.2f}"
    )

    # Extract ontology
    print("\n--- Ontology ---")
    ontology = hierarchy.extract_ontology()
    print(f"Concepts: {len(ontology['concepts'])}")
    print(f"Is-a relationships: {len(ontology['relationships']['is_a'])}")
    for rel in ontology["relationships"]["is_a"][:5]:
        print(f"  {rel['child']} is-a {rel['parent']}")

    # Metrics
    print("\n--- Metrics ---")
    metrics = hierarchy.get_metrics()
    for key, value in metrics.items():
        if isinstance(value, list):
            print(f"{key}: {value[:3]}...")
        else:
            print(f"{key}: {value}")
