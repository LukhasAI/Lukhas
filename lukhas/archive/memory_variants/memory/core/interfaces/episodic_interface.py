#!/usr/bin/env python3
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - EPISODIC MEMORY INTERFACE
║ Specialized interface for event-based episodic memories
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: episodic_interface.py
║ Path: memory/core/interfaces/episodic_interface.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Neuroscience Team
╠══════════════════════════════════════════════════════════════════════════════════
║ TECHNICAL FEATURES:
║ • Event-based memory operations
║ • Temporal and spatial context handling
║ • Emotional valence integration
║ • Hippocampal buffer compatibility
║ • Pattern completion and separation
║ • Sharp-wave ripple replay support
║ • Colony-aware distributed storage
║
║ ΛTAG: ΛEPISODIC, ΛINTERFACE, ΛHIPPOCAMPUS, ΛEVENT, ΛCONTEXT
╚══════════════════════════════════════════════════════════════════════════════════
"""

import time
from dataclasses import dataclass, field
from typing import Any, Optional, Union

import numpy as np

from .memory_interface import (
    BaseMemoryInterface,
    MemoryMetadata,
    MemoryResponse,
    MemoryType,
    ValidationResult,
)


@dataclass
class EpisodicContext:
    """Extended context for episodic memories"""

    # Temporal context
    event_start: Optional[float] = None
    event_end: Optional[float] = None
    duration: Optional[float] = None

    # Spatial context
    location: Optional[np.ndarray] = None
    spatial_tags: set[str] = field(default_factory=set)

    # Emotional context
    emotional_valence: float = 0.0  # -1 to 1
    arousal_level: float = 0.5  # 0 to 1

    # Social context
    participants: set[str] = field(default_factory=set)
    social_dynamics: dict[str, Any] = field(default_factory=dict)

    # Sensory context
    sensory_details: dict[str, Any] = field(default_factory=dict)

    # Cognitive context
    attention_level: float = 0.5
    cognitive_load: float = 0.5
    goal_relevance: float = 0.5


@dataclass
class EpisodicMemoryContent:
    """Structured content for episodic memories"""

    # Core event data
    event_type: str = ""
    description: str = ""
    content: Any = None

    # Context
    context: EpisodicContext = field(default_factory=EpisodicContext)

    # Associations
    causal_antecedents: list[str] = field(default_factory=list)
    causal_consequences: list[str] = field(default_factory=list)

    # Memory properties
    vividness: float = 1.0  # How clear/detailed
    coherence: float = 1.0  # How well-structured
    completeness: float = 1.0  # How much information retained


class EpisodicMemoryInterface(BaseMemoryInterface):
    """
    Specialized interface for episodic memories.
    Handles event-based memories with rich contextual information.
    """

    def __init__(
        self,
        colony_id: Optional[str] = None,
        enable_distributed: bool = True,
        pattern_separation_threshold: float = 0.3,
        consolidation_threshold: float = 0.6,
    ):
        super().__init__(
            memory_type=MemoryType.EPISODIC,
            colony_id=colony_id,
            enable_distributed=enable_distributed,
        )

        self.pattern_separation_threshold = pattern_separation_threshold
        self.consolidation_threshold = consolidation_threshold

        # Episodic-specific storage
        self.episodic_memories: dict[str, EpisodicMemoryContent] = {}
        self.temporal_index: dict[float, set[str]] = {}  # timestamp -> memory_ids
        self.spatial_index: dict[str, set[str]] = {}  # location -> memory_ids
        self.event_type_index: dict[str, set[str]] = {}  # event_type -> memory_ids

        # Replay and consolidation
        self.replay_candidates: list[str] = []
        self.consolidation_queue: list[str] = []

        logger.info("EpisodicMemoryInterface initialized")

    async def create_memory(
        self,
        content: Any,
        metadata: Optional[MemoryMetadata] = None,
        context: Optional[EpisodicContext] = None,
        **kwargs,
    ) -> MemoryResponse:
        """Create new episodic memory with context"""

        # Prepare metadata
        if metadata is None:
            metadata = MemoryMetadata(memory_type=MemoryType.EPISODIC)

        # Structure episodic content
        if isinstance(content, EpisodicMemoryContent):
            episodic_content = content
        else:
            episodic_content = EpisodicMemoryContent(
                content=content, context=context or EpisodicContext()
            )

            # Extract event type if available
            if isinstance(content, dict) and "event_type" in content:
                episodic_content.event_type = content["event_type"]
            elif isinstance(content, dict) and "event" in content:
                episodic_content.event_type = content["event"]

        # Calculate importance based on emotional salience
        emotional_impact = (
            abs(episodic_content.context.emotional_valence)
            * episodic_content.context.arousal_level
        )

        base_importance = metadata.importance
        metadata.importance = min(1.0, base_importance + 0.3 * emotional_impact)

        # Store memory
        memory_id = metadata.memory_id
        self.episodic_memories[memory_id] = episodic_content

        # Update indices
        self._update_indices(memory_id, episodic_content)

        # Add to replay candidates if salient
        if metadata.calculate_salience() > 0.6:
            self.replay_candidates.append(memory_id)

        logger.debug(
            "Episodic memory created",
            memory_id=memory_id,
            event_type=episodic_content.event_type,
            importance=metadata.importance,
        )

        return MemoryResponse(
            operation_id=kwargs.get("operation_id", memory_id),
            success=True,
            memory_id=memory_id,
            content=episodic_content,
            metadata=metadata,
        )

    async def read_memory(
        self, memory_id: str, update_access: bool = True, **kwargs
    ) -> MemoryResponse:
        """Read episodic memory with access tracking"""

        if memory_id not in self.episodic_memories:
            return MemoryResponse(
                operation_id=kwargs.get("operation_id", memory_id),
                success=False,
                error_message=f"Memory {memory_id} not found",
            )

        content = self.episodic_memories[memory_id]

        # Update access if requested (default True)
        if update_access:
            # In real implementation, would update metadata
            pass

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
        context_updates: Optional[dict[str, Any]] = None,
        **kwargs,
    ) -> MemoryResponse:
        """Update episodic memory with new information"""

        if memory_id not in self.episodic_memories:
            return MemoryResponse(
                operation_id=kwargs.get("operation_id", memory_id),
                success=False,
                error_message=f"Memory {memory_id} not found",
            )

        episodic_content = self.episodic_memories[memory_id]

        # Update content if provided
        if content is not None:
            if isinstance(content, EpisodicMemoryContent):
                episodic_content = content
            else:
                episodic_content.content = content

        # Update context if provided
        if context_updates:
            for key, value in context_updates.items():
                if hasattr(episodic_content.context, key):
                    setattr(episodic_content.context, key, value)

        # Update indices
        self._update_indices(memory_id, episodic_content)

        self.episodic_memories[memory_id] = episodic_content

        return MemoryResponse(
            operation_id=kwargs.get("operation_id", memory_id),
            success=True,
            memory_id=memory_id,
            content=episodic_content,
        )

    async def delete_memory(self, memory_id: str, **kwargs) -> MemoryResponse:
        """Delete episodic memory and update indices"""

        if memory_id not in self.episodic_memories:
            return MemoryResponse(
                operation_id=kwargs.get("operation_id", memory_id),
                success=False,
                error_message=f"Memory {memory_id} not found",
            )

        # Remove from indices
        self._remove_from_indices(memory_id)

        # Remove from storage
        del self.episodic_memories[memory_id]

        # Remove from queues
        if memory_id in self.replay_candidates:
            self.replay_candidates.remove(memory_id)
        if memory_id in self.consolidation_queue:
            self.consolidation_queue.remove(memory_id)

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
        """Search episodic memories by various criteria"""

        results = []

        # Simple implementation - in practice would use more sophisticated search
        for memory_id, content in self.episodic_memories.items():

            # Text search
            if isinstance(query, str):
                if (
                    query.lower() in content.event_type.lower()
                    or query.lower() in content.description.lower()
                    or query.lower() in str(content.content).lower()
                ):

                    results.append(
                        MemoryResponse(
                            operation_id=kwargs.get(
                                "operation_id", f"search_{memory_id}"
                            ),
                            success=True,
                            memory_id=memory_id,
                            content=content,
                        )
                    )

            # Structured search
            elif isinstance(query, dict):
                match = True

                if "event_type" in query:
                    if content.event_type != query["event_type"]:
                        match = False

                if "emotional_valence" in query:
                    valence_range = query["emotional_valence"]
                    if not (
                        valence_range[0]
                        <= content.context.emotional_valence
                        <= valence_range[1]
                    ):
                        match = False

                if "time_range" in query:
                    # Would check temporal context
                    pass

                if match:
                    results.append(
                        MemoryResponse(
                            operation_id=kwargs.get(
                                "operation_id", f"search_{memory_id}"
                            ),
                            success=True,
                            memory_id=memory_id,
                            content=content,
                        )
                    )

            if len(results) >= limit:
                break

        return results

    async def validate_memory(self, memory_id: str, **kwargs) -> ValidationResult:
        """Validate episodic memory integrity"""

        if memory_id not in self.episodic_memories:
            return ValidationResult.INVALID

        content = self.episodic_memories[memory_id]

        # Check completeness
        if not content.event_type or not content.content:
            return ValidationResult.INCOMPLETE

        # Check coherence
        if content.coherence < 0.5:
            return ValidationResult.CORRUPTED

        return ValidationResult.VALID

    # Episodic-specific methods

    async def retrieve_by_context(
        self,
        temporal_range: Optional[tuple[float, float]] = None,
        spatial_proximity: Optional[tuple[np.ndarray, float]] = None,
        emotional_range: Optional[tuple[float, float]] = None,
        event_types: Optional[list[str]] = None,
        limit: int = 50,
    ) -> list[MemoryResponse]:
        """Retrieve memories by contextual criteria"""

        candidates = set(self.episodic_memories.keys())

        # Filter by temporal range
        if temporal_range:
            start_time, end_time = temporal_range
            temporal_candidates = set()
            for timestamp, memory_ids in self.temporal_index.items():
                if start_time <= timestamp <= end_time:
                    temporal_candidates.update(memory_ids)
            candidates = candidates.intersection(temporal_candidates)

        # Filter by event types
        if event_types:
            event_candidates = set()
            for event_type in event_types:
                if event_type in self.event_type_index:
                    event_candidates.update(self.event_type_index[event_type])
            candidates = candidates.intersection(event_candidates)

        # Filter by emotional range
        if emotional_range:
            min_valence, max_valence = emotional_range
            emotional_candidates = []
            for memory_id in candidates:
                content = self.episodic_memories[memory_id]
                valence = content.context.emotional_valence
                if min_valence <= valence <= max_valence:
                    emotional_candidates.append(memory_id)
            candidates = set(emotional_candidates)

        # Convert to responses
        results = []
        for memory_id in list(candidates)[:limit]:
            content = self.episodic_memories[memory_id]
            results.append(
                MemoryResponse(
                    operation_id=f"context_search_{memory_id}",
                    success=True,
                    memory_id=memory_id,
                    content=content,
                )
            )

        return results

    async def trigger_episodic_replay(
        self, memory_ids: Optional[list[str]] = None, replay_strength: float = 1.0
    ) -> list[dict[str, Any]]:
        """Trigger replay of episodic memories (sharp-wave ripples)"""

        if memory_ids is None:
            # Use top candidates
            memory_ids = self.replay_candidates[:10]

        replay_events = []

        for memory_id in memory_ids:
            if memory_id in self.episodic_memories:
                content = self.episodic_memories[memory_id]

                # Create replay event
                replay_event = {
                    "memory_id": memory_id,
                    "content": content.content,
                    "event_type": content.event_type,
                    "emotional_valence": content.context.emotional_valence,
                    "replay_strength": replay_strength,
                    "timestamp": time.time(),
                }

                replay_events.append(replay_event)

                # Add to consolidation queue if strong enough
                if replay_strength > self.consolidation_threshold:
                    if memory_id not in self.consolidation_queue:
                        self.consolidation_queue.append(memory_id)

        logger.info(
            "Episodic replay triggered",
            memories_replayed=len(replay_events),
            consolidation_candidates=len(self.consolidation_queue),
        )

        return replay_events

    def get_consolidation_candidates(
        self, min_importance: float = 0.5, limit: int = 20
    ) -> list[str]:
        """Get memories ready for neocortical consolidation"""

        candidates = []

        for memory_id in self.consolidation_queue:
            if memory_id in self.episodic_memories:
                # In practice would check metadata importance
                candidates.append(memory_id)

        return candidates[:limit]

    def _update_indices(self, memory_id: str, content: EpisodicMemoryContent):
        """Update search indices for memory"""

        # Temporal index
        if content.context.event_start:
            timestamp = content.context.event_start
            if timestamp not in self.temporal_index:
                self.temporal_index[timestamp] = set()
            self.temporal_index[timestamp].add(memory_id)

        # Event type index
        if content.event_type:
            if content.event_type not in self.event_type_index:
                self.event_type_index[content.event_type] = set()
            self.event_type_index[content.event_type].add(memory_id)

        # Spatial index (simplified)
        if content.context.location is not None:
            location_key = f"spatial_{hash(content.context.location.tobytes())}"
            if location_key not in self.spatial_index:
                self.spatial_index[location_key] = set()
            self.spatial_index[location_key].add(memory_id)

    def _remove_from_indices(self, memory_id: str):
        """Remove memory from all indices"""

        # Temporal index
        for memory_ids in self.temporal_index.values():
            memory_ids.discard(memory_id)

        # Event type index
        for memory_ids in self.event_type_index.values():
            memory_ids.discard(memory_id)

        # Spatial index
        for memory_ids in self.spatial_index.values():
            memory_ids.discard(memory_id)

    def get_metrics(self) -> dict[str, Any]:
        """Get episodic interface metrics"""
        base_metrics = super().get_metrics()

        episodic_metrics = {
            "total_episodic_memories": len(self.episodic_memories),
            "replay_candidates": len(self.replay_candidates),
            "consolidation_queue_size": len(self.consolidation_queue),
            "temporal_index_size": len(self.temporal_index),
            "event_types": len(self.event_type_index),
            "spatial_locations": len(self.spatial_index),
        }

        return {**base_metrics, **episodic_metrics}
