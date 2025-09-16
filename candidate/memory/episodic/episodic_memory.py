"""
Consolidated Memory System - Episodic Memory

Consolidated from 4 files:
- memory/core/interfaces/episodic_interface.py
- memory/episodic/drift_tracker.py
- memory/episodic/recaller.py
- memory/systems/episodic_replay_buffer.py

Implements episodic memory with temporal sequencing, emotional encoding,
and consciousness-memory integration for LUKHAS AI.
"""
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional


@dataclass
class EpisodicMemoryEntry:
    """Represents a single episodic memory entry."""
    memory_id: str
    content: str
    timestamp: str
    emotional_context: dict[str, float]  # VAD encoding
    consciousness_state: str
    importance_score: float
    associations: list[str]
    sensory_data: Optional[dict[str, Any]] = None


class ConsolidatedEpisodicmemory:
    """Consolidated episodic memory system with temporal and emotional encoding."""

    def __init__(self):
        self.active_memories = {}
        self.processing_queue = []
        self.memory_store = {}
        self.temporal_index = {}
        self.emotional_index = {}
        self.consciousness_states = {
            'awake': 1.0,
            'dreaming': 0.7,
            'meditative': 0.8,
            'focused': 0.9,
            'scattered': 0.5
        }
        self.replay_buffer = []
        self.max_buffer_size = 1000

    async def process_memory(self, memory_data: dict[str, Any]) -> Optional[dict]:
        """Process memory through consolidated pipeline"""
        # Generate unique memory ID
        memory_id = self._generate_memory_id(memory_data)

        # Extract core components
        content = memory_data.get('content', '')
        emotional_context = memory_data.get('emotional_context', {
            'valence': 0.5, 'arousal': 0.5, 'dominance': 0.5
        })
        consciousness_state = memory_data.get('consciousness_state', 'awake')

        # Calculate importance score
        importance_score = self._calculate_importance(
            emotional_context, consciousness_state, content
        )

        # Create episodic memory entry
        memory_entry = EpisodicMemoryEntry(
            memory_id=memory_id,
            content=content,
            timestamp=datetime.now(timezone.utc).isoformat(),
            emotional_context=emotional_context,
            consciousness_state=consciousness_state,
            importance_score=importance_score,
            associations=self._find_associations(content),
            sensory_data=memory_data.get('sensory_data')
        )

        # Store in memory systems
        self.memory_store[memory_id] = memory_entry
        self._update_temporal_index(memory_entry)
        self._update_emotional_index(memory_entry)

        # Add to replay buffer if important enough
        if importance_score > 0.6:
            self._add_to_replay_buffer(memory_entry)

        # Process through consciousness integration
        consciousness_integration = self._integrate_with_consciousness(memory_entry)

        return {
            'memory_id': memory_id,
            'processed_at': memory_entry.timestamp,
            'importance_score': importance_score,
            'consciousness_integration': consciousness_integration,
            'associations_found': len(memory_entry.associations),
            'status': 'processed'
        }

    def recall_memories(self, query: str, limit: int = 10) -> list[EpisodicMemoryEntry]:
        """Recall memories based on content similarity and importance."""
        matching_memories = []

        for memory in self.memory_store.values():
            similarity_score = self._calculate_similarity(query, memory.content)
            relevance_score = similarity_score * memory.importance_score

            if relevance_score > 0.3:
                matching_memories.append((memory, relevance_score))

        # Sort by relevance and return top matches
        matching_memories.sort(key=lambda x: x[1], reverse=True)
        return [memory for memory, _ in matching_memories[:limit]]

    def get_temporal_sequence(self, start_time: str, end_time: str) -> list[EpisodicMemoryEntry]:
        """Get memories within a temporal range."""
        memories_in_range = []

        for memory in self.memory_store.values():
            if start_time <= memory.timestamp <= end_time:
                memories_in_range.append(memory)

        return sorted(memories_in_range, key=lambda x: x.timestamp)

    def get_emotional_memories(self, emotional_state: dict[str, float],
                              threshold: float = 0.7) -> list[EpisodicMemoryEntry]:
        """Retrieve memories with similar emotional context."""
        matching_memories = []

        for memory in self.memory_store.values():
            emotional_similarity = self._calculate_emotional_similarity(
                emotional_state, memory.emotional_context
            )

            if emotional_similarity >= threshold:
                matching_memories.append(memory)

        return sorted(matching_memories, key=lambda x: x.importance_score, reverse=True)

    def consolidate_memories(self, consolidation_type: str = 'temporal') -> dict[str, Any]:
        """Consolidate memories for long-term storage."""
        if consolidation_type == 'temporal':
            return self._temporal_consolidation()
        elif consolidation_type == 'emotional':
            return self._emotional_consolidation()
        elif consolidation_type == 'importance':
            return self._importance_consolidation()
        else:
            return {'error': 'Unknown consolidation type'}

    def _generate_memory_id(self, memory_data: dict[str, Any]) -> str:
        """Generate unique ID for memory entry."""
        content_hash = hashlib.sha256(
            json.dumps(memory_data, sort_keys=True).encode()
        ).hexdigest()
        timestamp = datetime.now(timezone.utc).isoformat()
        return f"episodic_{timestamp}_{content_hash[:8]}"

    def _calculate_importance(self, emotional_context: dict[str, float],
                            consciousness_state: str, content: str) -> float:
        """Calculate importance score for memory entry."""
        # Base importance from emotional intensity
        emotional_intensity = sum(abs(v - 0.5) for v in emotional_context.values()) / len(emotional_context)

        # Consciousness state modifier
        consciousness_modifier = self.consciousness_states.get(consciousness_state, 0.5)

        # Content complexity (simplified)
        content_complexity = min(1.0, len(content.split()) / 100.0)

        importance = (emotional_intensity * 0.4 +
                     consciousness_modifier * 0.4 +
                     content_complexity * 0.2)

        return min(1.0, importance)

    def _find_associations(self, content: str) -> list[str]:
        """Find associations with existing memories."""
        associations = []
        content_words = set(content.lower().split())

        for memory_id, memory in self.memory_store.items():
            memory_words = set(memory.content.lower().split())
            overlap = len(content_words.intersection(memory_words))

            if overlap > 2:  # Minimum overlap threshold
                associations.append(memory_id)

        return associations[:10]  # Limit associations

    def _update_temporal_index(self, memory_entry: EpisodicMemoryEntry):
        """Update temporal index for efficient time-based queries."""
        timestamp_key = memory_entry.timestamp[:10]  # Date only
        if timestamp_key not in self.temporal_index:
            self.temporal_index[timestamp_key] = []
        self.temporal_index[timestamp_key].append(memory_entry.memory_id)

    def _update_emotional_index(self, memory_entry: EpisodicMemoryEntry):
        """Update emotional index for efficient emotion-based queries."""
        # Create emotional signature
        valence_bucket = int(memory_entry.emotional_context.get('valence', 0.5) * 10)
        arousal_bucket = int(memory_entry.emotional_context.get('arousal', 0.5) * 10)

        emotion_key = f"v{valence_bucket}_a{arousal_bucket}"
        if emotion_key not in self.emotional_index:
            self.emotional_index[emotion_key] = []
        self.emotional_index[emotion_key].append(memory_entry.memory_id)

    def _add_to_replay_buffer(self, memory_entry: EpisodicMemoryEntry):
        """Add important memory to replay buffer."""
        self.replay_buffer.append(memory_entry)

        # Maintain buffer size
        if len(self.replay_buffer) > self.max_buffer_size:
            # Remove least important memory
            self.replay_buffer.sort(key=lambda x: x.importance_score)
            self.replay_buffer = self.replay_buffer[1:]

    def _integrate_with_consciousness(self, memory_entry: EpisodicMemoryEntry) -> dict[str, Any]:
        """Integrate memory with consciousness systems."""
        return {
            'consciousness_state': memory_entry.consciousness_state,
            'awareness_level': self.consciousness_states.get(memory_entry.consciousness_state, 0.5),
            'integration_score': memory_entry.importance_score,
            'ready_for_reflection': memory_entry.importance_score > 0.7
        }

    def _calculate_similarity(self, query: str, content: str) -> float:
        """Calculate similarity between query and content."""
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())

        if not query_words or not content_words:
            return 0.0

        intersection = len(query_words.intersection(content_words))
        union = len(query_words.union(content_words))

        return intersection / union if union > 0 else 0.0

    def _calculate_emotional_similarity(self, emotion1: dict[str, float],
                                       emotion2: dict[str, float]) -> float:
        """Calculate similarity between emotional states."""
        similarities = []

        for key in ['valence', 'arousal', 'dominance']:
            val1 = emotion1.get(key, 0.5)
            val2 = emotion2.get(key, 0.5)
            similarity = 1.0 - abs(val1 - val2)
            similarities.append(similarity)

        return sum(similarities) / len(similarities)

    def _temporal_consolidation(self) -> dict[str, Any]:
        """Perform temporal-based memory consolidation."""
        consolidated_count = 0
        for date_key, memory_ids in self.temporal_index.items():
            if len(memory_ids) > 5:  # Consolidate if many memories on same day
                consolidated_count += self._consolidate_memory_cluster(memory_ids)

        return {
            'consolidation_type': 'temporal',
            'clusters_consolidated': consolidated_count,
            'total_memories': len(self.memory_store)
        }

    def _emotional_consolidation(self) -> dict[str, Any]:
        """Perform emotion-based memory consolidation."""
        consolidated_count = 0
        for emotion_key, memory_ids in self.emotional_index.items():
            if len(memory_ids) > 10:  # Consolidate if many similar emotional memories
                consolidated_count += self._consolidate_memory_cluster(memory_ids)

        return {
            'consolidation_type': 'emotional',
            'clusters_consolidated': consolidated_count,
            'total_memories': len(self.memory_store)
        }

    def _importance_consolidation(self) -> dict[str, Any]:
        """Perform importance-based memory consolidation."""
        # Group memories by importance ranges
        importance_groups = {
            'high': [],
            'medium': [],
            'low': []
        }

        for memory in self.memory_store.values():
            if memory.importance_score > 0.7:
                importance_groups['high'].append(memory.memory_id)
            elif memory.importance_score > 0.4:
                importance_groups['medium'].append(memory.memory_id)
            else:
                importance_groups['low'].append(memory.memory_id)

        # Consolidate low importance memories more aggressively
        consolidated_count = self._consolidate_memory_cluster(importance_groups['low'])

        return {
            'consolidation_type': 'importance',
            'low_importance_consolidated': consolidated_count,
            'high_importance_preserved': len(importance_groups['high']),
            'total_memories': len(self.memory_store)
        }

    def _consolidate_memory_cluster(self, memory_ids: list[str]) -> int:
        """Consolidate a cluster of related memories."""
        # Placeholder for actual consolidation logic
        # Would combine similar memories into representative memories
        return len(memory_ids) // 2  # Simulate 50% consolidation


# Global instance
episodic_memory_instance = ConsolidatedEpisodicmemory()
