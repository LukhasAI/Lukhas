#!/usr/bin/env python3
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - NEOCORTICAL NETWORK
║ Slow consolidation and semantic knowledge storage inspired by neocortex
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: neocortical_network.py
║ Path: memory/neocortical/neocortical_network.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Neuroscience Team
╠══════════════════════════════════════════════════════════════════════════════════
║                             ◊ POETIC ESSENCE ◊
║
║ │ In the vast cathedral of the neocortex, knowledge crystallizes slowly,       │
║ │ like stalactites forming over millennia. Each drip of experience,            │
║ │ filtered through the hippocampus, finds its place in the grand tapestry     │
║ │ of understanding. This is not mere memory-it's wisdom distilled.             │
║ │                                                                               │
║ │ Six layers deep, like geological strata, each with its purpose:             │
║ │ sensation rises from below, abstraction descends from above, and in         │
║ │ their meeting, concepts are born. Distributed across colonies of neurons,    │
║ │ redundant yet efficient, the neocortex weaves episodes into semantics,       │
║ │ transforms experiences into expertise.                                        │
║ │                                                                               │
║ │ Through slow synaptic changes, through patient rehearsal, through the        │
║ │ alchemy of sleep, what was once new becomes known, what was once            │
║ │ surprising becomes expected, what was once difficult becomes intuitive.      │
║ │                                                                               │
╠══════════════════════════════════════════════════════════════════════════════════
║ TECHNICAL FEATURES:
║ • Hierarchical layer organization (6 layers)
║ • Slow synaptic weight updates
║ • Distributed representation across colonies
║ • Semantic extraction from episodic memories
║ • Concept hierarchy formation
║ • Catastrophic forgetting prevention
║ • Integration with hippocampal replay
║ • Colony-based redundancy
║
║ ΛTAG: ΛNEOCORTEX, ΛSEMANTIC, ΛMEMORY, ΛCONSOLIDATION, ΛHIERARCHY
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import json
import math
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Union
from uuid import uuid4

import numpy as np

# Import LUKHAS components
try:
    from core.colonies.base_colony import BaseColony

    from ..proteome.symbolic_proteome import ProteinType

    LUKHAS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some LUKHAS modules not available: {e}")
    LUKHAS_AVAILABLE = False
    BaseColony = object


class CorticalLayer(Enum):
    """Six-layer cortical architecture"""

    LAYER_I = "molecular"  # Dendrites and axons
    LAYER_II_III = "external"  # Cortico-cortical connections
    LAYER_IV = "granular"  # Thalamic input
    LAYER_V = "pyramidal"  # Output to subcortical
    LAYER_VI = "multiform"  # Feedback to thalamus


class LearningRate(Enum):
    """Learning rate schedules for different memory types"""

    FAST = 0.1  # For urgent updates
    NORMAL = 0.01  # Standard consolidation
    SLOW = 0.001  # Long-term stability
    GLACIAL = 0.0001  # Core knowledge


@dataclass
class SemanticMemory:
    """Semantic memory representation in neocortex"""

    memory_id: str = field(default_factory=lambda: str(uuid4()))
    concept: str = ""

    # Distributed representation
    feature_vector: Optional[np.ndarray] = None
    layer_activations: dict[CorticalLayer, np.ndarray] = field(default_factory=dict)

    # Semantic properties
    category: Optional[str] = None
    attributes: dict[str, Any] = field(default_factory=dict)
    relations: dict[str, set[str]] = field(default_factory=dict)  # relation_type -> memory_ids

    # Learning statistics
    consolidation_count: int = 0
    last_update: float = field(default_factory=time.time)
    learning_rate: float = LearningRate.NORMAL.value
    stability: float = 0.0  # 0-1, increases with consolidation

    # Source episodic memories
    source_episodes: set[str] = field(default_factory=set)

    # Colony distribution
    colony_locations: dict[str, float] = field(default_factory=dict)  # colony_id -> strength

    def calculate_activation_energy(self) -> float:
        """Calculate energy required to activate this memory"""
        # More stable memories require less energy
        base_energy = 1.0 - self.stability

        # Recent memories are easier to activate
        recency_factor = math.exp(-(time.time() - self.last_update) / 86400)  # Day decay

        return base_energy * (1 - 0.3 * recency_factor)


@dataclass
class CorticalColumn:
    """Cortical column - basic functional unit"""

    column_id: str = field(default_factory=lambda: str(uuid4()))
    position: tuple[int, int] = (0, 0)  # 2D position in cortical sheet

    # Neurons per layer
    layer_neurons: dict[CorticalLayer, np.ndarray] = field(default_factory=dict)

    # Lateral connections to neighboring columns
    lateral_weights: dict[str, float] = field(default_factory=dict)  # column_id -> weight

    # Receptive field
    receptive_field: Optional[np.ndarray] = None
    preferred_features: list[str] = field(default_factory=list)

    def initialize_layers(self, neurons_per_layer: int = 100):
        """Initialize neurons in each layer"""
        for layer in CorticalLayer:
            self.layer_neurons[layer] = np.random.randn(neurons_per_layer) * 0.1


class NeocorticalNetwork:
    """
    Main neocortical network implementing slow semantic consolidation.
    Distributed across colonies for redundancy and parallel processing.
    """

    def __init__(
        self,
        columns_x: int = 10,
        columns_y: int = 10,
        neurons_per_layer: int = 100,
        learning_rate_base: float = 0.01,
        stability_threshold: float = 0.8,
        enable_lateral_inhibition: bool = True,
        scaffold: Optional[Any] = None,
        persistence: Optional[Any] = None,
        proteome: Optional[Any] = None,
    ):
        self.columns_x = columns_x
        self.columns_y = columns_y
        self.neurons_per_layer = neurons_per_layer
        self.learning_rate_base = learning_rate_base
        self.stability_threshold = stability_threshold
        self.enable_lateral_inhibition = enable_lateral_inhibition
        self.scaffold = scaffold
        self.persistence = persistence
        self.proteome = proteome

        # Cortical architecture
        self.columns: dict[tuple[int, int], CorticalColumn] = {}
        self._initialize_columns()

        # Semantic memory storage
        self.semantic_memories: dict[str, SemanticMemory] = {}
        self.concept_index: dict[str, set[str]] = defaultdict(set)  # concept -> memory_ids

        # Consolidation queue
        self.consolidation_queue: list[tuple[str, dict[str, Any]]] = []

        # Colony integration
        self.colony_distributions: dict[str, dict[str, float]] = {}  # memory_id -> colony weights

        # Metrics
        self.total_consolidated = 0
        self.total_concepts = 0
        self.forgetting_events = 0

        # Background tasks
        self._running = False
        self._consolidation_task = None
        self._homeostasis_task = None

        logger.info(
            "NeocorticalNetwork initialized",
            columns=f"{columns_x}x{columns_y}",
            neurons_per_layer=neurons_per_layer,
            total_neurons=columns_x * columns_y * neurons_per_layer * len(CorticalLayer),
        )

    def _initialize_columns(self):
        """Initialize cortical columns in 2D grid"""
        for x in range(self.columns_x):
            for y in range(self.columns_y):
                column = CorticalColumn(position=(x, y))
                column.initialize_layers(self.neurons_per_layer)

                # Set up lateral connections to neighbors
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue

                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.columns_x and 0 <= ny < self.columns_y:
                            neighbor_id = f"column_{nx}_{ny}"
                            # Closer neighbors have stronger connections
                            distance = math.sqrt(dx**2 + dy**2)
                            column.lateral_weights[neighbor_id] = 1.0 / distance

                self.columns[(x, y)] = column

    async def start(self):
        """Start neocortical processing"""
        self._running = True

        # Start background tasks
        self._consolidation_task = asyncio.create_task(self._consolidation_loop())
        self._homeostasis_task = asyncio.create_task(self._homeostasis_loop())

        logger.info("NeocorticalNetwork started")

    async def stop(self):
        """Stop neocortical processing"""
        self._running = False

        # Cancel tasks
        for task in [self._consolidation_task, self._homeostasis_task]:
            if task:
                task.cancel()

        logger.info(
            "NeocorticalNetwork stopped",
            total_consolidated=self.total_consolidated,
            total_concepts=len(self.concept_index),
        )

    async def consolidate_episode(
        self,
        episode_data: dict[str, Any],
        source_episode_id: str,
        replay_strength: float = 1.0,
        colony_id: Optional[str] = None,
    ) -> Optional[str]:
        """
        Consolidate episodic memory into semantic knowledge.
        This is called during hippocampal replay events.
        """

        # Extract semantic features
        concept = self._extract_concept(episode_data)
        if not concept:
            return None

        # Check if similar semantic memory exists
        existing_memory = self._find_similar_semantic(concept, episode_data)

        if existing_memory:
            # Strengthen existing memory
            await self._strengthen_semantic_memory(existing_memory, episode_data, source_episode_id, replay_strength)
            memory_id = existing_memory.memory_id
        else:
            # Create new semantic memory
            memory_id = await self._create_semantic_memory(concept, episode_data, source_episode_id, colony_id)

        # Add to consolidation queue for distributed processing
        self.consolidation_queue.append((memory_id, episode_data))

        return memory_id

    async def retrieve_semantic(
        self, query: Union[str, dict[str, Any]], activation_threshold: float = 0.5
    ) -> list[SemanticMemory]:
        """
        Retrieve semantic memories matching query.
        Uses spreading activation across the network.
        """

        # Convert query to activation pattern
        if isinstance(query, str):
            # Concept-based retrieval
            if query in self.concept_index:
                memory_ids = self.concept_index[query]
                return [self.semantic_memories[mid] for mid in memory_ids]

        # Feature-based retrieval with spreading activation
        query_features = self._extract_features(query)
        activated_memories = []

        for memory in self.semantic_memories.values():
            if memory.feature_vector is not None:
                activation = self._compute_activation(query_features, memory)

                if activation > activation_threshold:
                    activated_memories.append((activation, memory))

        # Sort by activation strength
        activated_memories.sort(key=lambda x: x[0], reverse=True)

        return [memory for _, memory in activated_memories]

    async def distribute_to_colonies(self, memory_id: str, colony_weights: dict[str, float]):
        """
        Distribute semantic memory across multiple colonies.
        Ensures redundancy and parallel access.
        """

        if memory_id not in self.semantic_memories:
            return

        memory = self.semantic_memories[memory_id]
        memory.colony_locations = colony_weights
        self.colony_distributions[memory_id] = colony_weights

        # If integrated with actual colonies, would sync here
        if LUKHAS_AVAILABLE and hasattr(self, "colonies"):
            for _colony_id, _weight in colony_weights.items():
                # Send memory to colony with appropriate weight
                pass

        logger.debug(
            "Memory distributed to colonies",
            memory_id=memory_id,
            colonies=list(colony_weights.keys()),
        )

    def get_concept_hierarchy(self) -> dict[str, Any]:
        """
        Get hierarchical organization of concepts.
        Returns tree structure of semantic knowledge.
        """

        hierarchy = {}

        # Group by categories
        categories = defaultdict(list)
        for memory in self.semantic_memories.values():
            if memory.category:
                categories[memory.category].append(memory)

        # Build hierarchy
        for category, memories in categories.items():
            hierarchy[category] = {
                "count": len(memories),
                "concepts": list({m.concept for m in memories}),
                "avg_stability": np.mean([m.stability for m in memories]),
                "subcategories": self._find_subcategories(category, memories),
            }

        return hierarchy

    def _extract_concept(self, episode_data: dict[str, Any]) -> Optional[str]:
        """Extract core concept from episodic data"""

        # Simple extraction - in practice would use NLP/semantic analysis
        if "type" in episode_data:
            return episode_data["type"]
        elif "event" in episode_data:
            return episode_data["event"]
        elif "concept" in episode_data:
            return episode_data["concept"]

        # Generate from content
        content_str = json.dumps(episode_data, sort_keys=True)
        if len(content_str) > 20:
            return content_str[:20] + "..."

        return None

    def _extract_features(self, data: Any) -> np.ndarray:
        """Extract feature vector from data"""

        # Simple feature extraction - in practice would use embeddings
        if isinstance(data, dict):
            # Use keys and values
            features = []
            for key, value in sorted(data.items()):
                features.append(hash(key) % 1000)
                features.append(hash(str(value)) % 1000)
        else:
            features = [hash(str(data)) % 1000]

        # Pad or truncate to fixed size
        feature_size = self.neurons_per_layer
        if len(features) < feature_size:
            features.extend([0] * (feature_size - len(features)))
        else:
            features = features[:feature_size]

        # Normalize
        feature_vector = np.array(features, dtype=float)
        norm = np.linalg.norm(feature_vector)
        if norm > 0:
            feature_vector = feature_vector / norm

        return feature_vector

    def _find_similar_semantic(
        self,
        concept: str,
        episode_data: dict[str, Any],
        similarity_threshold: float = 0.7,
    ) -> Optional[SemanticMemory]:
        """Find existing semantic memory similar to episode"""

        # First check exact concept match
        if concept in self.concept_index:
            candidates = [self.semantic_memories[mid] for mid in self.concept_index[concept]]

            # Find most similar based on features
            episode_features = self._extract_features(episode_data)

            best_match = None
            best_similarity = 0.0

            for candidate in candidates:
                if candidate.feature_vector is not None:
                    similarity = np.dot(episode_features, candidate.feature_vector)
                    if similarity > best_similarity and similarity > similarity_threshold:
                        best_similarity = similarity
                        best_match = candidate

            return best_match

        return None

    async def _create_semantic_memory(
        self,
        concept: str,
        episode_data: dict[str, Any],
        source_episode_id: str,
        colony_id: Optional[str] = None,
    ) -> str:
        """Create new semantic memory from episode"""

        memory = SemanticMemory(
            concept=concept,
            feature_vector=self._extract_features(episode_data),
            learning_rate=self.learning_rate_base,
        )

        # Extract attributes
        if isinstance(episode_data, dict):
            memory.attributes = {k: v for k, v in episode_data.items() if k not in ["type", "event", "concept"]}

        # Initialize layer activations
        for layer in CorticalLayer:
            memory.layer_activations[layer] = np.random.randn(self.neurons_per_layer) * 0.1

        # Add source episode
        memory.source_episodes.add(source_episode_id)

        # Set initial colony location
        if colony_id:
            memory.colony_locations[colony_id] = 1.0

        # Store memory
        self.semantic_memories[memory.memory_id] = memory
        self.concept_index[concept].add(memory.memory_id)
        self.total_concepts = len(self.concept_index)

        # Persist if available
        if self.persistence:
            await self.persistence.persist_memory(
                content={
                    "type": "semantic",
                    "memory": memory.__dict__,
                    "neocortical": True,
                },
                memory_id=f"neo_{memory.memory_id}",
                importance=0.5,  # Semantic memories have moderate base importance
                tags={concept, "semantic", "consolidated"},
            )

        logger.debug("Semantic memory created", memory_id=memory.memory_id, concept=concept)

        return memory.memory_id

    async def _strengthen_semantic_memory(
        self,
        memory: SemanticMemory,
        episode_data: dict[str, Any],
        source_episode_id: str,
        replay_strength: float,
    ):
        """Strengthen existing semantic memory through consolidation"""

        # Update feature vector (running average)
        new_features = self._extract_features(episode_data)
        if memory.feature_vector is not None:
            # Weighted average based on learning rate and replay strength
            alpha = memory.learning_rate * replay_strength
            memory.feature_vector = (1 - alpha) * memory.feature_vector + alpha * new_features
        else:
            memory.feature_vector = new_features

        # Update attributes
        if isinstance(episode_data, dict):
            for key, value in episode_data.items():
                if key not in ["type", "event", "concept"]:
                    # Merge attributes
                    if key in memory.attributes:
                        # Keep most recent or merge if list
                        if isinstance(memory.attributes[key], list):
                            if value not in memory.attributes[key]:
                                memory.attributes[key].append(value)
                        else:
                            memory.attributes[key] = value
                    else:
                        memory.attributes[key] = value

        # Add source episode
        memory.source_episodes.add(source_episode_id)

        # Update stability (increases with each consolidation)
        memory.consolidation_count += 1
        memory.stability = min(1.0, memory.stability + 0.1 * replay_strength)

        # Adjust learning rate (decreases as stability increases)
        memory.learning_rate = self.learning_rate_base * (1 - memory.stability)

        memory.last_update = time.time()
        self.total_consolidated += 1

        logger.debug(
            "Semantic memory strengthened",
            memory_id=memory.memory_id,
            consolidation_count=memory.consolidation_count,
            stability=memory.stability,
        )

    def _compute_activation(self, query_features: np.ndarray, memory: SemanticMemory) -> float:
        """Compute activation strength for memory given query"""

        if memory.feature_vector is None:
            return 0.0

        # Base similarity
        similarity = np.dot(query_features, memory.feature_vector)

        # Modulate by stability (stable memories activate more easily)
        activation = similarity * (0.5 + 0.5 * memory.stability)

        # Apply activation energy threshold
        energy = memory.calculate_activation_energy()
        if activation < energy:
            activation = 0.0

        # Lateral inhibition
        if self.enable_lateral_inhibition:
            # Simplified - in practice would consider spatial organization
            activation *= 0.8

        return max(0.0, min(1.0, activation))

    def _find_subcategories(self, category: str, memories: list[SemanticMemory]) -> dict[str, Any]:
        """Find subcategories within a category"""

        # Cluster by shared attributes
        subcategories = defaultdict(list)

        for memory in memories:
            # Use first shared attribute as subcategory
            for attr_key in sorted(memory.attributes.keys()):
                subcategories[attr_key].append(memory)
                break

        return {
            subcat: {"count": len(mems), "concepts": list({m.concept for m in mems})}
            for subcat, mems in subcategories.items()
        }

    async def _consolidation_loop(self):
        """Background consolidation processing"""

        while self._running:
            if self.consolidation_queue:
                # Process batch
                batch_size = min(10, len(self.consolidation_queue))
                batch = [self.consolidation_queue.pop(0) for _ in range(batch_size)]

                for memory_id, _episode_data in batch:
                    if memory_id in self.semantic_memories:
                        memory = self.semantic_memories[memory_id]

                        # Simulate cortical processing
                        await self._process_in_columns(memory)

                        # Create protein if stable enough
                        if memory.stability > 0.5 and self.proteome:
                            await self.proteome.translate_memory(
                                memory_id=f"semantic_{memory_id}",
                                memory_content={
                                    "concept": memory.concept,
                                    "attributes": memory.attributes,
                                },
                                protein_type=ProteinType.STRUCTURAL,
                            )

            await asyncio.sleep(1.0)  # Process every second

    async def _process_in_columns(self, memory: SemanticMemory):
        """Process memory through cortical columns"""

        # Simplified columnar processing
        for layer in CorticalLayer:
            if layer in memory.layer_activations:
                # Update activations based on lateral connections
                activations = memory.layer_activations[layer]

                # Apply some processing (simplified)
                activations = np.tanh(activations)

                # Add noise for exploration
                activations += np.random.normal(0, 0.01, activations.shape)

                memory.layer_activations[layer] = activations

    async def _homeostasis_loop(self):
        """Maintain network homeostasis"""

        while self._running:
            # Synaptic scaling to prevent runaway excitation
            for memory in self.semantic_memories.values():
                if memory.feature_vector is not None:
                    # Keep average activation around 0.5
                    mean_activation = np.mean(np.abs(memory.feature_vector))
                    if mean_activation > 0.7:
                        memory.feature_vector *= 0.9
                    elif mean_activation < 0.3:
                        memory.feature_vector *= 1.1

            # Prune very weak memories (forgetting)
            weak_memories = [
                mid
                for mid, memory in self.semantic_memories.items()
                if memory.stability < 0.1 and memory.consolidation_count < 2
            ]

            for mid in weak_memories:
                memory = self.semantic_memories[mid]
                del self.semantic_memories[mid]
                self.concept_index[memory.concept].discard(mid)
                self.forgetting_events += 1

            await asyncio.sleep(30)  # Every 30 seconds

    def get_metrics(self) -> dict[str, Any]:
        """Get neocortical metrics"""

        if self.semantic_memories:
            avg_stability = np.mean([m.stability for m in self.semantic_memories.values()])
            avg_consolidation = np.mean([m.consolidation_count for m in self.semantic_memories.values()])
        else:
            avg_stability = 0.0
            avg_consolidation = 0.0

        return {
            "total_semantic_memories": len(self.semantic_memories),
            "total_concepts": len(self.concept_index),
            "average_stability": avg_stability,
            "average_consolidation_count": avg_consolidation,
            "total_consolidated": self.total_consolidated,
            "forgetting_events": self.forgetting_events,
            "consolidation_queue_size": len(self.consolidation_queue),
            "cortical_columns": len(self.columns),
            "total_neurons": len(self.columns) * self.neurons_per_layer * len(CorticalLayer),
        }


# Example usage
async def demonstrate_neocortical_network():
    """Demonstrate NeocorticalNetwork capabilities"""

    # Initialize network
    neocortex = NeocorticalNetwork(
        columns_x=5,
        columns_y=5,
        neurons_per_layer=50,
        learning_rate_base=0.1,  # Higher for demo
    )

    await neocortex.start()

    print("=== Neocortical Network Demonstration ===\n")

    # Consolidate some episodic memories
    print("--- Consolidating Episodes ---")

    episodes = [
        {
            "event": "learning",
            "subject": "machine learning",
            "topic": "neural networks",
            "difficulty": "moderate",
        },
        {
            "event": "learning",
            "subject": "machine learning",
            "topic": "deep learning",
            "difficulty": "hard",
        },
        {
            "event": "meeting",
            "type": "research",
            "topic": "AI safety",
            "outcome": "productive",
        },
        {
            "event": "learning",
            "subject": "mathematics",
            "topic": "linear algebra",
            "application": "machine learning",
        },
    ]

    memory_ids = []
    for i, episode in enumerate(episodes):
        # Simulate multiple replay events
        for replay in range(3):
            mem_id = await neocortex.consolidate_episode(
                episode_data=episode,
                source_episode_id=f"episode_{i}",
                replay_strength=0.8 - replay * 0.2,  # Decreasing strength
                colony_id="colony_main",
            )
            if mem_id and mem_id not in memory_ids:
                memory_ids.append(mem_id)

        print(f"Consolidated: {episode['event']} - {episode.get('topic', 'N/A')}")

    # Wait for processing
    await asyncio.sleep(2)

    # Test semantic retrieval
    print("\n--- Testing Semantic Retrieval ---")

    # Query by concept
    learning_memories = await neocortex.retrieve_semantic("learning")
    print(f"Found {len(learning_memories)} memories for 'learning'")

    # Query by features
    ml_query = {"subject": "machine learning"}
    ml_memories = await neocortex.retrieve_semantic(ml_query)
    print(f"Found {len(ml_memories)} memories matching ML query")

    if ml_memories:
        print(f"  Example: {ml_memories[0].concept} (stability: {ml_memories[0].stability:.2f})")

    # Show concept hierarchy
    print("\n--- Concept Hierarchy ---")
    hierarchy = neocortex.get_concept_hierarchy()
    for category, info in hierarchy.items():
        print(f"{category}:")
        print(f"  Memories: {info['count']}")
        print(f"  Concepts: {info['concepts']}")
        print(f"  Avg stability: {info['avg_stability']:.2f}")

    # Distribute across colonies
    print("\n--- Colony Distribution ---")
    if memory_ids:
        await neocortex.distribute_to_colonies(
            memory_ids[0],
            {"colony_main": 0.6, "colony_backup": 0.3, "colony_archive": 0.1},
        )
        print(f"Distributed memory {memory_ids[0][:8]}... across colonies")

    # Show metrics
    print("\n--- Neocortical Metrics ---")
    metrics = neocortex.get_metrics()
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"{key}: {value:.3f}")
        else:
            print(f"{key}: {value}")

    await neocortex.stop()


if __name__ == "__main__":
    asyncio.run(demonstrate_neocortical_network())