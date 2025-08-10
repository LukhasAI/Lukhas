#!/usr/bin/env python3
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - EPISODIC MEMORY COLONY
║ Specialized colony for processing episodic and autobiographical memories
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: episodic_memory_colony.py
║ Path: memory/colonies/episodic_memory_colony.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Colony Architecture Team
╠══════════════════════════════════════════════════════════════════════════════════
║                             ◊ POETIC ESSENCE ◊
║
║ │ In the theater of remembrance, the Episodic Colony is both audience and   │
║ │ performer, witness and storyteller. Each memory arrives like a scene—     │
║ │ rich with context, heavy with emotion, urgent with the weight of          │
║ │ experience. Here, time is not linear but dimensional, space is not        │
║ │ coordinate but meaningful, and emotion is not decoration but essence.     │
║ │                                                                            │
║ │ This colony understands that episodes are not mere facts but lived        │
║ │ moments, that each memory carries within it the ghost of sensation,       │
║ │ the echo of feeling, the shadow of significance.                          │
║ │                                                                            │
╠══════════════════════════════════════════════════════════════════════════════════
║ TECHNICAL FEATURES:
║ • Event-based memory processing
║ • Temporal and spatial context awareness
║ • Emotional valence integration
║ • Autobiographical significance detection
║ • Hippocampal-style rapid encoding
║ • Pattern separation for distinct episodes
║ • Inter-episode association mapping
║ • Replay prioritization for consolidation
║
║ ΛTAG: ΛEPISODIC, ΛCOLONY, ΛAUTOBIOGRAPHICAL, ΛCONTEXT, ΛEMOTION
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

import numpy as np

from .base_memory_colony import (
    BaseMemoryColony,
    ColonyCapabilities,
    ColonyRole,
    MemoryType,
)

# Import memory components
try:
    from ..core.interfaces import (
        EpisodicContext,
        EpisodicMemoryContent,
        MemoryOperation,
        MemoryResponse,
        ValidationResult,
    )

    INTERFACES_AVAILABLE = True
except ImportError:
    INTERFACES_AVAILABLE = False
    # Stubs for development
    MemoryOperation = object
    MemoryResponse = object
    ValidationResult = object


@dataclass
class EpisodicMemoryRecord:
    """Internal record for episodic memories in colony storage"""

    memory_id: str
    content: EpisodicMemoryContent
    timestamp: float = field(default_factory=time.time)

    # Episodic-specific properties
    vividness: float = 1.0  # How clear/detailed (0-1)
    coherence: float = 1.0  # How well-structured (0-1)
    personal_significance: float = 0.5  # Autobiographical importance (0-1)

    # Context analysis
    temporal_distinctiveness: float = 0.5  # How unique in time
    spatial_distinctiveness: float = 0.5  # How unique in space
    emotional_intensity: float = 0.0  # Absolute emotional strength

    # Processing state
    consolidation_readiness: float = 0.0  # Ready for neocortical transfer
    replay_count: int = 0
    last_accessed: float = field(default_factory=time.time)

    # Associations
    related_episodes: set[str] = field(default_factory=set)
    causal_links: dict[str, str] = field(
        default_factory=dict
    )  # episode_id -> link_type


class EpisodicMemoryColony(BaseMemoryColony):
    """
    Specialized colony for processing episodic and autobiographical memories.

    This colony excels at:
    - Rapid encoding of new episodes with rich context
    - Pattern separation to maintain episode distinctiveness
    - Emotional significance assessment
    - Temporal and spatial context processing
    - Autobiographical narrative construction
    """

    def __init__(
        self,
        colony_id: str = "episodic_memory_colony",
        max_concurrent_operations: int = 50,
        memory_capacity: int = 10000,
    ):
        # Define episodic-specific capabilities
        capabilities = ColonyCapabilities(
            max_concurrent_operations=max_concurrent_operations,
            supported_memory_types={
                MemoryType.EPISODIC,
                MemoryType.EMOTIONAL,  # Often overlap with episodic
            },
            supported_operations={
                "create",
                "read",
                "update",
                "delete",
                "search",
                "replay",
                "consolidate",
                "associate",
            },
            average_response_time_ms=50.0,  # Fast for hippocampal-style processing
            throughput_ops_per_second=20.0,
            specialization_confidence=0.95,
        )

        super().__init__(
            colony_id=colony_id,
            colony_role=ColonyRole.SPECIALIST,
            specialized_memory_types=[MemoryType.EPISODIC, MemoryType.EMOTIONAL],
            capabilities=capabilities,
        )

        # Episodic-specific storage
        self.episodic_records: dict[str, EpisodicMemoryRecord] = {}
        self.memory_capacity = memory_capacity

        # Indexing for fast retrieval
        self.temporal_index: dict[str, set[str]] = defaultdict(
            set
        )  # time_bucket -> memory_ids
        self.spatial_index: dict[str, set[str]] = defaultdict(
            set
        )  # location_key -> memory_ids
        self.emotional_index: dict[str, set[str]] = defaultdict(
            set
        )  # emotion_bucket -> memory_ids
        self.event_type_index: dict[str, set[str]] = defaultdict(
            set
        )  # event_type -> memory_ids

        # Pattern separation and completion
        self.pattern_separation_threshold = 0.3
        self.pattern_completion_threshold = 0.7

        # Replay and consolidation
        self.replay_queue: deque = deque()
        self.consolidation_candidates: list[str] = []

        # Background processing
        self.replay_task = None
        self.consolidation_task = None

        logger.info(f"EpisodicMemoryColony initialized with capacity {memory_capacity}")

    async def _initialize_specialized_systems(self):
        """Initialize episodic-specific systems"""
        # Start replay processing for consolidation
        self.replay_task = asyncio.create_task(self._replay_processing_loop())
        self.consolidation_task = asyncio.create_task(
            self._consolidation_assessment_loop()
        )

        logger.info("Episodic memory systems initialized")

    async def _cleanup_specialized_systems(self):
        """Cleanup episodic-specific systems"""
        if self.replay_task:
            self.replay_task.cancel()
        if self.consolidation_task:
            self.consolidation_task.cancel()

        logger.info("Episodic memory systems cleaned up")

    async def _process_specialized_operation(
        self, operation: MemoryOperation
    ) -> MemoryResponse:
        """Process episodic memory operations"""

        if operation.operation_type == "create":
            return await self._create_episodic_memory(operation)
        elif operation.operation_type == "read":
            return await self._read_episodic_memory(operation)
        elif operation.operation_type == "update":
            return await self._update_episodic_memory(operation)
        elif operation.operation_type == "delete":
            return await self._delete_episodic_memory(operation)
        elif operation.operation_type == "search":
            return await self._search_episodic_memories(operation)
        elif operation.operation_type == "replay":
            return await self._trigger_episodic_replay(operation)
        elif operation.operation_type == "consolidate":
            return await self._assess_consolidation_readiness(operation)
        else:
            return MemoryResponse(
                operation_id=operation.operation_id,
                success=False,
                error_message=f"Unsupported operation: {operation.operation_type}",
            )

    async def _create_episodic_memory(
        self, operation: MemoryOperation
    ) -> MemoryResponse:
        """Create new episodic memory with rich context processing"""

        # Extract or create episodic content
        if isinstance(operation.content, EpisodicMemoryContent):
            episodic_content = operation.content
        else:
            # Convert generic content to episodic structure
            episodic_content = EpisodicMemoryContent(
                content=operation.content, context=EpisodicContext()
            )

            # Extract event type if available
            if isinstance(operation.content, dict):
                if "event_type" in operation.content:
                    episodic_content.event_type = operation.content["event_type"]
                elif "event" in operation.content:
                    episodic_content.event_type = operation.content["event"]

        # Generate memory ID
        memory_id = operation.memory_id or str(uuid4())

        # Analyze context for distinctiveness
        temporal_distinctiveness = self._analyze_temporal_distinctiveness(
            episodic_content.context
        )
        spatial_distinctiveness = self._analyze_spatial_distinctiveness(
            episodic_content.context
        )
        emotional_intensity = abs(episodic_content.context.emotional_valence)

        # Calculate personal significance
        personal_significance = self._calculate_personal_significance(episodic_content)

        # Apply pattern separation if similar episodes exist
        similar_episodes = self._find_similar_episodes(episodic_content)
        if len(similar_episodes) > 3:  # Too many similar episodes
            # Increase pattern separation
            episodic_content = self._apply_pattern_separation(
                episodic_content, similar_episodes
            )

        # Create internal record
        record = EpisodicMemoryRecord(
            memory_id=memory_id,
            content=episodic_content,
            vividness=episodic_content.vividness,
            coherence=episodic_content.coherence,
            personal_significance=personal_significance,
            temporal_distinctiveness=temporal_distinctiveness,
            spatial_distinctiveness=spatial_distinctiveness,
            emotional_intensity=emotional_intensity,
        )

        # Check capacity and manage storage
        if len(self.episodic_records) >= self.memory_capacity:
            await self._manage_memory_capacity()

        # Store memory
        self.episodic_records[memory_id] = record

        # Update indices
        self._update_episodic_indices(record)

        # Add to replay queue if significant
        if personal_significance > 0.7 or emotional_intensity > 0.6:
            self.replay_queue.append(memory_id)

        logger.debug(
            "Episodic memory created",
            memory_id=memory_id,
            event_type=episodic_content.event_type,
            personal_significance=personal_significance,
            emotional_intensity=emotional_intensity,
        )

        return MemoryResponse(
            operation_id=operation.operation_id,
            success=True,
            memory_id=memory_id,
            content=episodic_content,
        )

    async def _read_episodic_memory(self, operation: MemoryOperation) -> MemoryResponse:
        """Read episodic memory with context enrichment"""

        memory_id = operation.memory_id
        if not memory_id or memory_id not in self.episodic_records:
            return MemoryResponse(
                operation_id=operation.operation_id,
                success=False,
                error_message="Memory not found",
            )

        record = self.episodic_records[memory_id]

        # Update access information
        record.last_accessed = time.time()

        # Enrich with related episodes if requested
        enriched_content = record.content
        if operation.parameters.get("include_related", False):
            enriched_content = self._enrich_with_related_episodes(record)

        return MemoryResponse(
            operation_id=operation.operation_id,
            success=True,
            memory_id=memory_id,
            content=enriched_content,
            metadata=operation.metadata,
        )

    async def _search_episodic_memories(
        self, operation: MemoryOperation
    ) -> MemoryResponse:
        """Search episodic memories using multiple indices"""

        query = operation.content
        limit = operation.parameters.get("limit", 50)

        matching_records = []

        if isinstance(query, dict):
            # Structured search
            candidates = set()

            # Search by event type
            if "event_type" in query:
                event_type = query["event_type"]
                candidates.update(self.event_type_index.get(event_type, set()))

            # Search by time range
            if "time_range" in query:
                start_time, end_time = query["time_range"]
                for time_bucket, memory_ids in self.temporal_index.items():
                    bucket_time = float(time_bucket)
                    if start_time <= bucket_time <= end_time:
                        candidates.update(memory_ids)

            # Search by emotional range
            if "emotional_range" in query:
                min_val, max_val = query["emotional_range"]
                for emotion_bucket, memory_ids in self.emotional_index.items():
                    bucket_val = float(emotion_bucket)
                    if min_val <= bucket_val <= max_val:
                        candidates.update(memory_ids)

            # If no structured criteria, search all
            if not candidates:
                candidates = set(self.episodic_records.keys())

            # Filter and rank candidates
            for memory_id in candidates:
                if memory_id in self.episodic_records:
                    record = self.episodic_records[memory_id]
                    if self._matches_query(record, query):
                        matching_records.append(record)

        else:
            # Text-based search
            query_text = str(query).lower()
            for record in self.episodic_records.values():
                if self._text_matches(record, query_text):
                    matching_records.append(record)

        # Sort by relevance and recency
        matching_records.sort(
            key=lambda r: (
                r.personal_significance,
                r.emotional_intensity,
                -abs(time.time() - r.timestamp),  # More recent is better
            ),
            reverse=True,
        )

        # Limit results
        matching_records = matching_records[:limit]

        # Convert to response format
        results = [record.content for record in matching_records]

        return MemoryResponse(
            operation_id=operation.operation_id, success=True, content=results
        )

    async def _trigger_episodic_replay(
        self, operation: MemoryOperation
    ) -> MemoryResponse:
        """Trigger replay of specific episodic memories"""

        memory_ids = operation.parameters.get("memory_ids", [])
        if not memory_ids:
            # Use top replay candidates
            memory_ids = list(self.replay_queue)[:10]

        replayed_memories = []

        for memory_id in memory_ids:
            if memory_id in self.episodic_records:
                record = self.episodic_records[memory_id]
                record.replay_count += 1

                # Calculate replay strength based on significance and recency
                replay_strength = (
                    record.personal_significance * 0.4
                    + record.emotional_intensity * 0.3
                    + record.vividness * 0.3
                )

                # Update consolidation readiness
                record.consolidation_readiness = min(
                    1.0, record.consolidation_readiness + replay_strength * 0.1
                )

                replayed_memories.append(
                    {
                        "memory_id": memory_id,
                        "content": record.content,
                        "replay_strength": replay_strength,
                        "consolidation_readiness": record.consolidation_readiness,
                    }
                )

        logger.debug("Episodic replay completed", replayed_count=len(replayed_memories))

        return MemoryResponse(
            operation_id=operation.operation_id, success=True, content=replayed_memories
        )

    async def _cast_consensus_vote(
        self, consensus_request: dict[str, Any]
    ) -> dict[str, Any]:
        """Cast vote based on episodic memory expertise"""

        request_type = consensus_request.get("type", "unknown")
        memory_data = consensus_request.get("memory_data", {})

        # Assess based on episodic characteristics
        confidence = 0.5
        decision = "approve"

        if request_type == "memory_validation":
            # Check if memory has episodic characteristics
            has_temporal_context = "timestamp" in memory_data or "time" in memory_data
            has_spatial_context = "location" in memory_data or "place" in memory_data
            has_emotional_context = "emotion" in memory_data or "feeling" in memory_data
            has_event_structure = "event" in memory_data or "experience" in memory_data

            episodic_score = (
                sum(
                    [
                        has_temporal_context,
                        has_spatial_context,
                        has_emotional_context,
                        has_event_structure,
                    ]
                )
                / 4.0
            )

            if episodic_score > 0.5:
                confidence = min(0.9, 0.5 + episodic_score * 0.4)
                decision = "approve"
            else:
                confidence = 0.3
                decision = "abstain"  # Not our expertise

        return {
            "colony_id": self.colony_id,
            "decision": decision,
            "confidence": confidence,
            "reasoning": "Episodic assessment based on contextual richness",
            "specialization_match": confidence > 0.7,
        }

    # Helper methods for episodic processing

    def _analyze_temporal_distinctiveness(self, context: EpisodicContext) -> float:
        """Analyze how temporally distinct this episode is"""
        if not context.event_start:
            return 0.5  # Default

        # Check for similar timestamps in recent memories
        time_window = 3600  # 1 hour window
        similar_count = 0

        for record in self.episodic_records.values():
            if record.content.context.event_start:
                time_diff = abs(
                    context.event_start - record.content.context.event_start
                )
                if time_diff < time_window:
                    similar_count += 1

        # More similar memories = less distinctive
        distinctiveness = max(0.0, 1.0 - similar_count / 10.0)
        return distinctiveness

    def _analyze_spatial_distinctiveness(self, context: EpisodicContext) -> float:
        """Analyze how spatially distinct this episode is"""
        if context.location is None:
            return 0.5  # Default

        # Check for similar locations in recent memories
        location_threshold = 0.1  # Similarity threshold
        similar_count = 0

        for record in self.episodic_records.values():
            record_location = record.content.context.location
            if record_location is not None:
                distance = np.linalg.norm(context.location - record_location)
                if distance < location_threshold:
                    similar_count += 1

        distinctiveness = max(0.0, 1.0 - similar_count / 5.0)
        return distinctiveness

    def _calculate_personal_significance(self, content: EpisodicMemoryContent) -> float:
        """Calculate autobiographical significance of episode"""
        significance = 0.5  # Base significance

        # Emotional intensity increases significance
        emotional_boost = abs(content.context.emotional_valence) * 0.3
        significance += emotional_boost

        # First-time experiences are more significant
        if "first" in content.description.lower():
            significance += 0.2

        # Social interactions are significant
        if len(content.context.participants) > 0:
            significance += min(0.2, len(content.context.participants) * 0.05)

        # Goal-relevant events are significant
        significance += content.context.goal_relevance * 0.2

        return min(1.0, significance)

    def _find_similar_episodes(self, content: EpisodicMemoryContent) -> list[str]:
        """Find episodes similar to the given content"""
        similar = []

        # Simple similarity based on event type and context
        for memory_id, record in self.episodic_records.items():
            similarity_score = 0.0

            # Event type similarity
            if record.content.event_type == content.event_type:
                similarity_score += 0.4

            # Temporal similarity (same day)
            if record.content.context.event_start and content.context.event_start:
                time_diff = abs(
                    record.content.context.event_start - content.context.event_start
                )
                if time_diff < 86400:  # Same day
                    similarity_score += 0.3

            # Spatial similarity
            if (
                record.content.context.location is not None
                and content.context.location is not None
            ):
                distance = np.linalg.norm(
                    record.content.context.location - content.context.location
                )
                if distance < 0.1:
                    similarity_score += 0.3

            if similarity_score > self.pattern_separation_threshold:
                similar.append(memory_id)

        return similar

    def _apply_pattern_separation(
        self, content: EpisodicMemoryContent, similar_episodes: list[str]
    ) -> EpisodicMemoryContent:
        """Apply pattern separation to maintain episode distinctiveness"""

        # Add distinguishing details to make episode more distinct
        # This is a simplified version - real implementation would be more sophisticated

        if not content.description:
            content.description = f"Distinct episode at {time.time()}"
        else:
            content.description += (
                f" [Distinct from {len(similar_episodes)} similar episodes]"
            )

        # Slightly modify context to increase distinctiveness
        if content.context.attention_level < 1.0:
            content.context.attention_level = min(
                1.0, content.context.attention_level + 0.1
            )

        return content

    def _update_episodic_indices(self, record: EpisodicMemoryRecord):
        """Update all indices for efficient retrieval"""
        memory_id = record.memory_id

        # Temporal index (bucket by hour)
        if record.content.context.event_start:
            time_bucket = str(int(record.content.context.event_start // 3600) * 3600)
            self.temporal_index[time_bucket].add(memory_id)

        # Event type index
        if record.content.event_type:
            self.event_type_index[record.content.event_type].add(memory_id)

        # Emotional index (bucket by 0.1 increments)
        emotion_bucket = str(round(record.content.context.emotional_valence, 1))
        self.emotional_index[emotion_bucket].add(memory_id)

        # Spatial index (simplified - would use spatial hashing in practice)
        if record.content.context.location is not None:
            location_key = f"spatial_{hash(record.content.context.location.tobytes())}"
            self.spatial_index[location_key].add(memory_id)

    def _matches_query(
        self, record: EpisodicMemoryRecord, query: dict[str, Any]
    ) -> bool:
        """Check if record matches structured query"""

        # Check personal significance threshold
        if "min_significance" in query:
            if record.personal_significance < query["min_significance"]:
                return False

        # Check emotional intensity
        if "min_emotional_intensity" in query:
            if record.emotional_intensity < query["min_emotional_intensity"]:
                return False

        # Check participants
        if "participants" in query:
            required_participants = set(query["participants"])
            record_participants = record.content.context.participants
            if not required_participants.intersection(record_participants):
                return False

        return True

    def _text_matches(self, record: EpisodicMemoryRecord, query_text: str) -> bool:
        """Check if record matches text query"""
        searchable_text = " ".join(
            [
                record.content.event_type.lower(),
                record.content.description.lower(),
                str(record.content.content).lower(),
            ]
        )

        return query_text in searchable_text

    async def _manage_memory_capacity(self):
        """Manage memory capacity by removing less important episodes"""
        if len(self.episodic_records) < self.memory_capacity:
            return

        # Sort by importance (inverse - least important first)
        records_by_importance = sorted(
            self.episodic_records.items(),
            key=lambda x: (
                x[1].personal_significance,
                x[1].emotional_intensity,
                x[1].consolidation_readiness,
                -x[1].replay_count,  # Negative because more replays = more important
            ),
        )

        # Remove least important 10%
        to_remove = int(len(records_by_importance) * 0.1)

        for memory_id, _ in records_by_importance[:to_remove]:
            await self._remove_episodic_memory(memory_id)

        logger.info(f"Managed capacity: removed {to_remove} episodic memories")

    async def _remove_episodic_memory(self, memory_id: str):
        """Remove episodic memory and clean up indices"""
        if memory_id not in self.episodic_records:
            return

        self.episodic_records[memory_id]

        # Remove from indices
        for index in [
            self.temporal_index,
            self.spatial_index,
            self.emotional_index,
            self.event_type_index,
        ]:
            for memory_set in index.values():
                memory_set.discard(memory_id)

        # Remove from queues
        if memory_id in self.replay_queue:
            temp_queue = deque()
            while self.replay_queue:
                mid = self.replay_queue.popleft()
                if mid != memory_id:
                    temp_queue.append(mid)
            self.replay_queue = temp_queue

        if memory_id in self.consolidation_candidates:
            self.consolidation_candidates.remove(memory_id)

        # Remove from storage
        del self.episodic_records[memory_id]

    # Background processing loops

    async def _replay_processing_loop(self):
        """Process episodic replay for consolidation"""
        while self._running:
            if self.replay_queue:
                # Process a batch of replays
                batch_size = min(5, len(self.replay_queue))
                replay_batch = []

                for _ in range(batch_size):
                    if self.replay_queue:
                        memory_id = self.replay_queue.popleft()
                        if memory_id in self.episodic_records:
                            replay_batch.append(memory_id)

                if replay_batch:
                    # Simulate replay processing
                    for memory_id in replay_batch:
                        record = self.episodic_records[memory_id]
                        record.replay_count += 1

                        # Increase consolidation readiness
                        record.consolidation_readiness = min(
                            1.0, record.consolidation_readiness + 0.1
                        )

            await asyncio.sleep(2.0)  # Process replays every 2 seconds

    async def _consolidation_assessment_loop(self):
        """Assess episodes for consolidation readiness"""
        while self._running:
            # Clear old candidates
            self.consolidation_candidates.clear()

            # Find episodes ready for consolidation
            for memory_id, record in self.episodic_records.items():
                if (
                    record.consolidation_readiness > 0.7
                    and record.replay_count >= 3
                    and record.personal_significance > 0.5
                ):

                    self.consolidation_candidates.append(memory_id)

            # Sort by readiness
            self.consolidation_candidates.sort(
                key=lambda mid: self.episodic_records[mid].consolidation_readiness,
                reverse=True,
            )

            # Keep only top candidates
            self.consolidation_candidates = self.consolidation_candidates[:20]

            await asyncio.sleep(30.0)  # Assess every 30 seconds
