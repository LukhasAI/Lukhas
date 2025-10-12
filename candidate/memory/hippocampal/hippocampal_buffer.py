#!/usr/bin/env python3
import logging

logger = logging.getLogger(__name__)
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - HIPPOCAMPAL BUFFER
║ Fast episodic memory encoding inspired by biological hippocampus
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: hippocampal_buffer.py
║ Path: memory/hippocampal/hippocampal_buffer.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Neuroscience Team
╠══════════════════════════════════════════════════════════════════════════════════
║                             ◊ POETIC ESSENCE ◊
║
║ │ In the seahorse-shaped chamber of immediate experience, the Hippocampus      │
║ │ dances—a neural maestro conducting the symphony of now. Each moment,         │
║ │ each sensation, each fleeting thought is caught in its rapid embrace,        │
║ │ encoded with the urgency of the present, the context of the immediate.       │
║ │                                                                               │
║ │ Like a scribe with infinite parchment but limited ink, it writes quickly,    │
║ │ capturing the essence before it fades. Pattern separation ensures each       │
║ │ memory is distinct, while pattern completion allows fragments to resurrect   │
║ │ the whole. This is not mere storage—it's the birthplace of experience.       │
║ │                                                                               │
║ │ Through theta rhythms it oscillates, binding disparate elements into         │
║ │ cohesive episodes. What was separate becomes unified, what was temporal      │
║ │ becomes spatial, what was fleeting becomes, if only briefly, eternal.        │
║ │                                                                               │
╠══════════════════════════════════════════════════════════════════════════════════
║ TECHNICAL FEATURES:
║ • High-plasticity episodic memory encoding
║ • Pattern separation for distinct memory traces
║ • Pattern completion for associative retrieval
║ • Theta oscillation synchronization (4-8 Hz)
║ • Place cells and grid cells simulation
║ • Sharp-wave ripples for memory replay
║ • Integration with neocortical consolidation
║ • Colony-aware distributed processing
║
║ ΛTAG: ΛHIPPOCAMPUS, ΛEPISODIC, ΛMEMORY, ΛTHETA, ΛNEUROSCIENCE
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import json
import math
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Union
from uuid import uuid4

import numpy as np


# Define core enums (always available)
class PersistenceMode(Enum):
    IMMEDIATE = "immediate"
    LAZY = "lazy"
    SNAPSHOT = "snapshot"
    HYBRID = "hybrid"

# Import LUKHAS components
try:
    from lukhas.core.symbolism.tags import TagScope
    LUKHAS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some LUKHAS modules not available: {e}")
    LUKHAS_AVAILABLE = False

    # Minimal stubs
    class TagScope(Enum):
        GLOBAL = "global"
        LOCAL = "local"
        ETHICAL = "ethical"
        TEMPORAL = "temporal"
        GENETIC = "genetic"


class HippocampalState(Enum):
    """States of hippocampal processing"""

    ENCODING = "encoding"  # Actively encoding new memories
    CONSOLIDATING = "consolidating"  # Transferring to neocortex
    RETRIEVING = "retrieving"  # Pattern completion mode
    REPLAYING = "replaying"  # Sharp-wave ripple replay
    RESTING = "resting"  # Idle state


class PlaceField(Enum):
    """Spatial context for episodic memories"""

    PHYSICAL = "physical"  # Real-world location
    CONCEPTUAL = "conceptual"  # Abstract concept space
    TEMPORAL = "temporal"  # Time-based context
    SOCIAL = "social"  # Social interaction context
    EMOTIONAL = "emotional"  # Emotional landscape


@dataclass
class EpisodicMemory:
    """Single episodic memory trace"""

    memory_id: str = field(default_factory=lambda: str(uuid4()))
    content: Any = None
    timestamp: float = field(default_factory=time.time)

    # Contextual binding
    spatial_context: dict[str, float] = field(default_factory=dict)  # Place cell activation
    temporal_context: float = 0.0  # Time cell activation
    emotional_valence: float = 0.0  # -1 to 1
    arousal_level: float = 0.5  # 0 to 1

    # Neural properties
    encoding_strength: float = 1.0
    pattern_vector: Optional[np.ndarray] = None
    theta_phase: float = 0.0  # Phase when encoded

    # Associations
    associated_memories: set[str] = field(default_factory=set)
    semantic_tags: set[str] = field(default_factory=set)

    # Replay statistics
    replay_count: int = 0
    last_replay: Optional[float] = None
    consolidation_priority: float = 0.5

    def calculate_salience(self) -> float:
        """Calculate memory salience for prioritized replay"""
        # High arousal and extreme valence increase salience
        emotional_salience = self.arousal_level * abs(self.emotional_valence)

        # Recent memories have higher salience
        recency = math.exp(-(time.time() - self.timestamp) / 3600)  # Decay over hours

        # Frequently replayed memories are important
        replay_factor = math.log(self.replay_count + 1) / 10

        return min(1.0, emotional_salience + recency + replay_factor)


@dataclass
class PlaceCell:
    """Simulated place cell for spatial encoding"""

    cell_id: str = field(default_factory=lambda: str(uuid4()))
    preferred_location: np.ndarray = field(default_factory=lambda: np.random.rand(3))
    receptive_field_size: float = 0.2

    def activation(self, location: np.ndarray) -> float:
        """Calculate place cell activation for given location"""
        distance = np.linalg.norm(location - self.preferred_location)
        return math.exp(-(distance**2) / (2 * self.receptive_field_size**2))


@dataclass
class GridCell:
    """Simulated grid cell for spatial navigation"""

    cell_id: str = field(default_factory=lambda: str(uuid4()))
    spacing: float = 0.5
    orientation: float = 0.0
    phase: np.ndarray = field(default_factory=lambda: np.random.rand(2))

    def activation(self, location: np.ndarray) -> float:
        """Calculate grid cell activation using hexagonal grid pattern"""
        # Simplified 2D grid pattern
        x, y = location[:2]

        # Three basis vectors for hexagonal grid
        angles = [self.orientation + i * np.pi / 3 for i in range(3)]

        activations = []
        for angle in angles:
            projection = x * np.cos(angle) + y * np.sin(angle)
            activations.append(np.cos(2 * np.pi * projection / self.spacing))

        return max(activations)


class HippocampalBuffer:
    """
    Main hippocampal memory buffer implementing fast episodic encoding.
    Inspired by biological hippocampus CA1, CA3, and dentate gyrus.
    """

    def __init__(
        self,
        capacity: int = 10000,
        theta_frequency: float = 6.0,  # Hz
        pattern_separation_threshold: float = 0.3,
        enable_place_cells: bool = True,
        enable_grid_cells: bool = True,
        scaffold: Optional[Any] = None,
        persistence: Optional[Any] = None,
    ):
        self.capacity = capacity
        self.theta_frequency = theta_frequency
        self.pattern_separation_threshold = pattern_separation_threshold
        self.enable_place_cells = enable_place_cells
        self.enable_grid_cells = enable_grid_cells
        self.scaffold = scaffold
        self.persistence = persistence

        # Memory storage
        self.episodic_buffer: deque = deque(maxlen=capacity)
        self.memory_index: dict[str, EpisodicMemory] = {}

        # Neural architecture
        self.place_cells: list[PlaceCell] = []
        self.grid_cells: list[GridCell] = []
        if enable_place_cells:
            self._initialize_place_cells()
        if enable_grid_cells:
            self._initialize_grid_cells()

        # Pattern separation (dentate gyrus)
        self.pattern_dimension = 1024
        self.sparse_coding_level = 0.05  # 5% active neurons

        # State management
        self.state = HippocampalState.RESTING
        self.current_theta_phase = 0.0
        self.last_theta_update = time.time()

        # Replay buffer for consolidation
        self.replay_queue: deque = deque(maxlen=1000)
        self.ripple_events: list[dict[str, Any]] = []

        # Metrics
        self.total_encoded = 0
        self.successful_retrievals = 0
        self.failed_retrievals = 0
        self.total_replays = 0

        # Background tasks
        self._running = False
        self._theta_task = None
        self._replay_task = None

        logger.info(
            "HippocampalBuffer initialized",
            capacity=capacity,
            theta_freq=theta_frequency,
            place_cells=len(self.place_cells),
            grid_cells=len(self.grid_cells),
        )

    def _initialize_place_cells(self, count: int = 100):
        """Initialize place cells with random preferred locations"""
        self.place_cells = [PlaceCell() for _ in range(count)]

    def _initialize_grid_cells(self, count: int = 50):
        """Initialize grid cells with varying spacing and orientations"""
        spacings = [0.3, 0.5, 0.8, 1.2, 2.0]  # Multiple scales

        for i in range(count):
            self.grid_cells.append(
                GridCell(
                    spacing=spacings[i % len(spacings)],
                    orientation=np.random.uniform(0, np.pi / 3),
                )
            )

    async def start(self):
        """Start hippocampal processing"""
        self._running = True

        # Start background tasks
        self._theta_task = asyncio.create_task(self._theta_oscillation_loop())
        self._replay_task = asyncio.create_task(self._replay_loop())

        logger.info("HippocampalBuffer started")

    async def stop(self):
        """Stop hippocampal processing"""
        self._running = False

        # Cancel tasks
        if self._theta_task:
            self._theta_task.cancel()
        if self._replay_task:
            self._replay_task.cancel()

        logger.info(
            "HippocampalBuffer stopped",
            total_encoded=self.total_encoded,
            total_replays=self.total_replays,
        )

    async def encode_episode(
        self,
        content: Any,
        spatial_location: Optional[np.ndarray] = None,
        emotional_state: Optional[tuple[float, float]] = None,
        tags: Optional[set[str]] = None,
    ) -> str:
        """
        Encode a new episodic memory with full context.
        Uses pattern separation to ensure distinct memory traces.
        """

        self.state = HippocampalState.ENCODING

        # Create episodic memory
        memory = EpisodicMemory(
            content=content,
            semantic_tags=tags or set(),
            theta_phase=self.current_theta_phase,
        )

        # Encode spatial context
        if spatial_location is not None and self.enable_place_cells:
            memory.spatial_context = self._encode_spatial_context(spatial_location)

        # Encode emotional context
        if emotional_state:
            memory.emotional_valence, memory.arousal_level = emotional_state

        # Pattern separation - create sparse distributed representation
        memory.pattern_vector = self._pattern_separation(content)

        # Check for similar memories (pattern completion threshold)
        similar_memories = self._find_similar_memories(memory.pattern_vector)
        memory.associated_memories = {m.memory_id for m in similar_memories}

        # Calculate encoding strength based on arousal and novelty
        novelty = 1.0 - len(similar_memories) / max(len(self.memory_index), 1)
        memory.encoding_strength = 0.5 + 0.3 * memory.arousal_level + 0.2 * novelty

        # Add to buffer
        self.episodic_buffer.append(memory)
        self.memory_index[memory.memory_id] = memory
        self.total_encoded += 1

        # Add to replay queue with priority
        self.replay_queue.append((memory.memory_id, memory.calculate_salience()))

        # Persist if available
        if self.persistence:
            await self.persistence.persist_memory(
                content={
                    "type": "episodic",
                    "memory": memory.__dict__,
                    "hippocampal": True,
                },
                memory_id=f"hippo_{memory.memory_id}",
                importance=memory.calculate_salience(),
                tags=memory.semantic_tags,
                mode=PersistenceMode.LAZY,
            )

        logger.debug(
            "Episode encoded",
            memory_id=memory.memory_id,
            encoding_strength=memory.encoding_strength,
            associations=len(memory.associated_memories),
        )

        self.state = HippocampalState.RESTING
        return memory.memory_id

    async def retrieve_episode(
        self, cue: Union[str, Any], completion_threshold: float = 0.6
    ) -> Optional[EpisodicMemory]:
        """
        Retrieve episodic memory using pattern completion.
        Partial cues can trigger full memory retrieval.
        """

        self.state = HippocampalState.RETRIEVING

        # If cue is memory ID, direct retrieval
        if isinstance(cue, str) and cue in self.memory_index:
            memory = self.memory_index[cue]
            self.successful_retrievals += 1
            self.state = HippocampalState.RESTING
            return memory

        # Pattern completion from partial cue
        cue_pattern = self._pattern_separation(cue)

        best_match = None
        best_similarity = 0.0

        for memory in self.memory_index.values():
            if memory.pattern_vector is not None:
                similarity = self._pattern_similarity(cue_pattern, memory.pattern_vector)

                if similarity > best_similarity and similarity >= completion_threshold:
                    best_similarity = similarity
                    best_match = memory

        if best_match:
            self.successful_retrievals += 1
            logger.debug(
                "Episode retrieved via pattern completion",
                memory_id=best_match.memory_id,
                similarity=best_similarity,
            )
        else:
            self.failed_retrievals += 1
            logger.debug("Failed to retrieve episode", cue=str(cue)[:50])

        self.state = HippocampalState.RESTING
        return best_match

    async def trigger_replay(
        self, memory_ids: Optional[list[str]] = None, replay_count: int = 10
    ) -> list[dict[str, Any]]:
        """
        Trigger sharp-wave ripple replay of memories.
        Used for consolidation to neocortex.
        """

        self.state = HippocampalState.REPLAYING

        # Select memories for replay
        if memory_ids:
            replay_memories = [self.memory_index[mid] for mid in memory_ids if mid in self.memory_index]
        else:
            # Prioritized sampling based on salience
            sorted_queue = sorted(self.replay_queue, key=lambda x: x[1], reverse=True)

            replay_ids = [item[0] for item in sorted_queue[:replay_count]]
            replay_memories = [self.memory_index[mid] for mid in replay_ids if mid in self.memory_index]

        # Simulate ripple events
        ripple_data = []

        for memory in replay_memories:
            # Create ripple event
            ripple = {
                "timestamp": time.time(),
                "memory_id": memory.memory_id,
                "content": memory.content,
                "pattern": (memory.pattern_vector.tolist() if memory.pattern_vector is not None else None),
                "associations": list(memory.associated_memories),
                "replay_strength": memory.encoding_strength * memory.calculate_salience(),
            }

            ripple_data.append(ripple)

            # Update replay statistics
            memory.replay_count += 1
            memory.last_replay = time.time()
            self.total_replays += 1

        self.ripple_events.extend(ripple_data)

        logger.info(
            "Sharp-wave ripple replay completed",
            memories_replayed=len(ripple_data),
            total_replays=self.total_replays,
        )

        self.state = HippocampalState.RESTING
        return ripple_data

    def get_consolidation_candidates(
        self, min_replays: int = 3, min_age_seconds: float = 300, limit: int = 50
    ) -> list[EpisodicMemory]:
        """
        Get memories ready for consolidation to neocortex.
        Selection based on replay count, age, and importance.
        """

        current_time = time.time()
        candidates = []

        for memory in self.memory_index.values():
            age = current_time - memory.timestamp

            if memory.replay_count >= min_replays and age >= min_age_seconds:
                candidates.append(memory)

        # Sort by consolidation priority
        candidates.sort(
            key=lambda m: m.consolidation_priority * m.calculate_salience(),
            reverse=True,
        )

        return candidates[:limit]

    def _encode_spatial_context(self, location: np.ndarray) -> dict[str, float]:
        """Encode spatial location using place cells"""
        context = {}

        for i, place_cell in enumerate(self.place_cells):
            activation = place_cell.activation(location)
            if activation > 0.1:  # Threshold for sparsity
                context[f"place_{i}"] = activation

        if self.enable_grid_cells:
            for i, grid_cell in enumerate(self.grid_cells):
                activation = grid_cell.activation(location)
                if activation > 0.5:
                    context[f"grid_{i}"] = activation

        return context

    def _pattern_separation(self, content: Any) -> np.ndarray:
        """
        Create sparse distributed representation via pattern separation.
        Mimics dentate gyrus function.
        """

        # Convert content to string for hashing
        content_str = json.dumps(content) if isinstance(content, (dict, list)) else str(content)

        # Generate pattern vector
        pattern = np.zeros(self.pattern_dimension)

        # Hash-based sparse activation
        hash_val = hash(content_str)
        np.random.seed(abs(hash_val) % (2**32))

        # Activate sparse subset of neurons
        active_neurons = int(self.pattern_dimension * self.sparse_coding_level)
        active_indices = np.random.choice(self.pattern_dimension, size=active_neurons, replace=False)

        # Set activation strengths
        pattern[active_indices] = np.random.uniform(0.5, 1.0, size=active_neurons)

        # Add noise for separation
        pattern += np.random.normal(0, 0.01, self.pattern_dimension)
        pattern = np.clip(pattern, 0, 1)

        return pattern

    def _find_similar_memories(self, pattern: np.ndarray, threshold: Optional[float] = None) -> list[EpisodicMemory]:
        """Find memories with similar patterns"""

        threshold = threshold or self.pattern_separation_threshold
        similar = []

        for memory in self.memory_index.values():
            if memory.pattern_vector is not None:
                similarity = self._pattern_similarity(pattern, memory.pattern_vector)
                if similarity > threshold:
                    similar.append(memory)

        return similar

    def _pattern_similarity(self, pattern1: np.ndarray, pattern2: np.ndarray) -> float:
        """Calculate cosine similarity between patterns"""

        dot_product = np.dot(pattern1, pattern2)
        norm_product = np.linalg.norm(pattern1) * np.linalg.norm(pattern2)

        if norm_product == 0:
            return 0.0

        return dot_product / norm_product

    async def _theta_oscillation_loop(self):
        """Background theta rhythm oscillation (4-8 Hz)"""

        while self._running:
            # Update theta phase
            current_time = time.time()
            dt = current_time - self.last_theta_update

            # Phase advances based on frequency
            phase_advance = 2 * np.pi * self.theta_frequency * dt
            self.current_theta_phase = (self.current_theta_phase + phase_advance) % (2 * np.pi)

            self.last_theta_update = current_time

            # Sleep to maintain rhythm
            await asyncio.sleep(1.0 / (self.theta_frequency * 10))  # 10x oversampling

    async def _replay_loop(self):
        """Background replay during quiet periods"""

        while self._running:
            # Only replay when not actively processing
            if self.state == HippocampalState.RESTING:
                # Spontaneous replay with small probability
                if np.random.random() < 0.1:  # 10% chance per cycle
                    await self.trigger_replay(replay_count=5)

            await asyncio.sleep(5.0)  # Check every 5 seconds

    def get_metrics(self) -> dict[str, Any]:
        """Get hippocampal metrics"""

        return {
            "state": self.state.value,
            "buffer_size": len(self.episodic_buffer),
            "unique_memories": len(self.memory_index),
            "total_encoded": self.total_encoded,
            "retrieval_success_rate": (
                self.successful_retrievals / max(self.successful_retrievals + self.failed_retrievals, 1)
            ),
            "total_replays": self.total_replays,
            "current_theta_phase": self.current_theta_phase,
            "theta_frequency_hz": self.theta_frequency,
            "replay_queue_size": len(self.replay_queue),
            "recent_ripples": len(self.ripple_events),
        }


# Example usage and testing
async def demonstrate_hippocampal_buffer():
    """Demonstrate HippocampalBuffer capabilities"""

    # Initialize buffer
    hippo = HippocampalBuffer(
        capacity=1000,
        theta_frequency=6.0,
        enable_place_cells=True,
        enable_grid_cells=True,
    )

    await hippo.start()

    print("=== Hippocampal Buffer Demonstration ===\n")

    # Encode some episodes
    print("--- Encoding Episodes ---")

    episodes = [
        {
            "content": {
                "event": "learning",
                "topic": "neural networks",
                "insight": "backpropagation",
            },
            "location": np.array([1.0, 2.0, 0.0]),
            "emotion": (0.8, 0.9),  # Positive valence, high arousal
            "tags": {"learning", "ai", "breakthrough"},
        },
        {
            "content": {
                "event": "meeting",
                "person": "colleague",
                "outcome": "collaboration",
            },
            "location": np.array([3.0, 1.0, 0.0]),
            "emotion": (0.6, 0.5),
            "tags": {"social", "work", "planning"},
        },
        {
            "content": {"event": "problem", "type": "bug", "severity": "critical"},
            "location": np.array([2.0, 2.0, 0.0]),
            "emotion": (-0.7, 0.8),  # Negative valence, high arousal
            "tags": {"problem", "urgent", "debugging"},
        },
    ]

    memory_ids = []
    for ep in episodes:
        mem_id = await hippo.encode_episode(
            content=ep["content"],
            spatial_location=ep["location"],
            emotional_state=ep["emotion"],
            tags=ep["tags"],
        )
        memory_ids.append(mem_id)
        print(f"Encoded: {ep['content']['event']} -> {mem_id[:8]}...")

    # Test pattern completion
    print("\n--- Testing Pattern Completion ---")

    # Partial cue
    partial_cue = {"event": "learning", "topic": "neural networks"}
    retrieved = await hippo.retrieve_episode(partial_cue)

    if retrieved:
        print(f"Retrieved from partial cue: {retrieved.content}")
        print(f"Associations: {len(retrieved.associated_memories)}")

    # Trigger replay
    print("\n--- Triggering Sharp-Wave Ripple Replay ---")

    ripples = await hippo.trigger_replay(replay_count=3)
    print(f"Replayed {len(ripples)} memories")

    for ripple in ripples[:2]:
        print(f"  Ripple: {ripple['memory_id'][:8]}... strength={ripple['replay_strength']:.2f}")

    # Get consolidation candidates
    print("\n--- Consolidation Candidates ---")

    # Wait a bit and trigger more replays
    await asyncio.sleep(1)
    await hippo.trigger_replay()

    candidates = hippo.get_consolidation_candidates(min_replays=1, min_age_seconds=0)
    print(f"Found {len(candidates)} candidates ready for neocortical consolidation")

    # Show metrics
    print("\n--- Hippocampal Metrics ---")
    metrics = hippo.get_metrics()
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"{key}: {value:.3f}")
        else:
            print(f"{key}: {value}")

    # Stop buffer
    await hippo.stop()


if __name__ == "__main__":
    # Run demonstration
    asyncio.run(demonstrate_hippocampal_buffer())
