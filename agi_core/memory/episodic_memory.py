"""
Episodic Memory System for AGI

Advanced episodic memory system that stores and retrieves personal experiences,
events, and contextual information with temporal and spatial awareness.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional

import numpy as np

from .vector_memory import MemoryImportance, MemoryType, MemoryVector, VectorMemoryStore

logger = logging.getLogger(__name__)


class EpisodeType(Enum):
    """Types of episodic memories."""

    CONVERSATION = "conversation"  # Conversational episodes
    TASK_COMPLETION = "task_completion"  # Task or problem-solving episodes
    LEARNING = "learning"  # Learning and discovery episodes
    INTERACTION = "interaction"  # System interactions
    REFLECTION = "reflection"  # Self-reflective episodes
    ERROR_RECOVERY = "error_recovery"  # Error handling and recovery episodes
    CREATIVE_SESSION = "creative_session"  # Creative work sessions


class EpisodeStatus(Enum):
    """Status of episodic memories."""

    ACTIVE = "active"  # Currently happening
    COMPLETED = "completed"  # Successfully completed
    INTERRUPTED = "interrupted"  # Interrupted or incomplete
    FAILED = "failed"  # Failed to complete
    ARCHIVED = "archived"  # Archived for long-term storage


@dataclass
class EpisodeContext:
    """Context information for an episode."""

    location: Optional[str] = None  # Where the episode occurred
    participants: list[str] = field(default_factory=list)  # Who was involved
    tools_used: list[str] = field(default_factory=list)  # Tools or systems used
    goals: list[str] = field(default_factory=list)  # Episode goals
    outcomes: list[str] = field(default_factory=list)  # Episode outcomes
    emotional_state: Optional[float] = None  # Emotional state during episode
    confidence_level: float = 1.0  # Confidence in episode accuracy
    external_references: list[str] = field(default_factory=list)  # External links/refs


@dataclass
class Episode:
    """
    Episodic Memory: Personal experience or event with temporal context.

    Represents a coherent sequence of experiences with beginning, middle, and end.
    """

    episode_id: str
    title: str
    description: str
    episode_type: EpisodeType
    status: EpisodeStatus

    # Temporal Information
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None

    # Content and Context
    context: EpisodeContext = field(default_factory=EpisodeContext)
    memory_sequences: list[str] = field(default_factory=list)  # Ordered memory IDs
    key_insights: list[str] = field(default_factory=list)  # Important insights gained
    lessons_learned: list[str] = field(default_factory=list)  # Lessons from episode

    # LUKHAS Integration
    constellation_impact: dict[str, float] = field(default_factory=dict)  # Effect on 8 stars
    importance: MemoryImportance = MemoryImportance.MEDIUM

    # Episode Metrics
    success_score: Optional[float] = None  # How successful was the episode (0-1)
    learning_score: Optional[float] = None  # How much was learned (0-1)
    creativity_score: Optional[float] = None  # How creative was the episode (0-1)

    def __post_init__(self):
        """Calculate derived fields."""
        if self.end_time and self.duration_minutes is None:
            duration = self.end_time - self.start_time
            self.duration_minutes = int(duration.total_seconds() / 60)

    def get_episode_vector(self, memory_store: VectorMemoryStore) -> Optional[np.ndarray]:
        """Get combined vector representation of episode."""
        if not self.memory_sequences:
            return None

        vectors = []
        for memory_id in self.memory_sequences:
            if memory_id in memory_store.memories:
                vectors.append(memory_store.memories[memory_id].vector)

        if not vectors:
            return None

        # Weighted average with temporal decay (recent memories weighted more)
        weights = np.exp(-np.arange(len(vectors)) * 0.1)  # Exponential decay
        weighted_vectors = [v * w for v, w in zip(vectors, weights)]

        return np.mean(weighted_vectors, axis=0)

    def add_memory(self, memory_id: str):
        """Add memory to episode sequence."""
        if memory_id not in self.memory_sequences:
            self.memory_sequences.append(memory_id)

    def complete_episode(
        self,
        end_time: Optional[datetime] = None,
        success_score: Optional[float] = None,
        lessons_learned: Optional[list[str]] = None,
    ):
        """Mark episode as completed with outcomes."""
        self.status = EpisodeStatus.COMPLETED
        self.end_time = end_time or datetime.now(timezone.utc)

        if success_score is not None:
            self.success_score = success_score

        if lessons_learned:
            self.lessons_learned.extend(lessons_learned)

        # Calculate duration
        if self.end_time:
            duration = self.end_time - self.start_time
            self.duration_minutes = int(duration.total_seconds() / 60)


@dataclass
class EpisodicQuery:
    """Query for episodic memory retrieval."""

    query_text: Optional[str] = None  # Text-based query
    episode_types: Optional[list[EpisodeType]] = None  # Filter by episode types
    time_range: Optional[tuple[datetime, datetime]] = None  # Time range filter
    participants: Optional[list[str]] = None  # Filter by participants
    tools_used: Optional[list[str]] = None  # Filter by tools
    min_success_score: Optional[float] = None  # Minimum success threshold
    constellation_context: Optional[dict[str, float]] = None  # Constellation relevance
    max_results: int = 10  # Maximum results to return


class EpisodicMemorySystem:
    """
    Advanced Episodic Memory System for AGI

    Manages personal experiences and events with rich temporal and contextual
    information. Integrates with LUKHAS consciousness framework.
    """

    def __init__(self, memory_store: VectorMemoryStore):
        self.memory_store = memory_store
        self.episodes: dict[str, Episode] = {}
        self.active_episodes: dict[str, Episode] = {}

        # Indexing for efficient retrieval
        self.type_index: dict[EpisodeType, list[str]] = {et: [] for et in EpisodeType}
        self.participant_index: dict[str, list[str]] = {}
        self.temporal_index: list[tuple[datetime, str]] = []  # (start_time, episode_id)

        # Configuration
        self.max_episodes = 10000  # Maximum episodes to store
        self.auto_archive_days = 365  # Days before auto-archiving
        self.similarity_threshold = 0.7  # Threshold for episode similarity

        # Statistics
        self.stats = {
            "total_episodes": 0,
            "active_episodes": 0,
            "completed_episodes": 0,
            "episode_types": {et.value: 0 for et in EpisodeType},
            "avg_episode_duration": 0.0,
            "avg_success_score": 0.0,
        }

    async def create_episode(
        self, title: str, description: str, episode_type: EpisodeType, context: Optional[EpisodeContext] = None
    ) -> str:
        """Create a new episodic memory."""
        episode_id = f"ep_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{len(self.episodes)}"

        episode = Episode(
            episode_id=episode_id,
            title=title,
            description=description,
            episode_type=episode_type,
            status=EpisodeStatus.ACTIVE,
            start_time=datetime.now(timezone.utc),
            context=context or EpisodeContext(),
        )

        # Store episode
        self.episodes[episode_id] = episode
        self.active_episodes[episode_id] = episode

        # Update indices
        self.type_index[episode_type].append(episode_id)
        self.temporal_index.append((episode.start_time, episode_id))
        self.temporal_index.sort()  # Keep temporal index sorted

        # Update participant index
        for participant in episode.context.participants:
            if participant not in self.participant_index:
                self.participant_index[participant] = []
            self.participant_index[participant].append(episode_id)

        # Update statistics
        self.stats["total_episodes"] += 1
        self.stats["active_episodes"] += 1
        self.stats["episode_types"][episode_type.value] += 1

        logger.info(f"Created episode {episode_id}: {title}")
        return episode_id

    async def add_memory_to_episode(self, episode_id: str, memory: MemoryVector) -> bool:
        """Add memory to an existing episode."""
        if episode_id not in self.episodes:
            return False

        episode = self.episodes[episode_id]

        # Add memory to memory store if not already there
        if memory.id not in self.memory_store.memories:
            await self.memory_store.add_memory(memory)

        # Add to episode sequence
        episode.add_memory(memory.id)

        # Update memory with episode context
        memory.source_context = f"Episode: {episode.title}"

        # Enhance memory constellation tags based on episode
        for star, impact in episode.constellation_impact.items():
            current = memory.constellation_tags.get(star, 0.0)
            memory.constellation_tags[star] = min(1.0, current + impact * 0.1)

        return True

    async def complete_episode(
        self,
        episode_id: str,
        success_score: Optional[float] = None,
        key_insights: Optional[list[str]] = None,
        lessons_learned: Optional[list[str]] = None,
    ) -> bool:
        """Complete an active episode."""
        if episode_id not in self.active_episodes:
            return False

        episode = self.active_episodes[episode_id]
        episode.complete_episode(success_score=success_score, lessons_learned=lessons_learned or [])

        if key_insights:
            episode.key_insights.extend(key_insights)

        # Move from active to completed
        del self.active_episodes[episode_id]

        # Update statistics
        self.stats["active_episodes"] -= 1
        self.stats["completed_episodes"] += 1

        if episode.duration_minutes:
            # Update average episode duration
            total_completed = self.stats["completed_episodes"]
            current_avg = self.stats["avg_episode_duration"]
            self.stats["avg_episode_duration"] = (
                current_avg * (total_completed - 1) + episode.duration_minutes
            ) / total_completed

        if episode.success_score is not None:
            # Update average success score
            total_completed = self.stats["completed_episodes"]
            current_avg = self.stats["avg_success_score"]
            self.stats["avg_success_score"] = (
                current_avg * (total_completed - 1) + episode.success_score
            ) / total_completed

        # Create episode summary memory
        await self._create_episode_summary_memory(episode)

        logger.info(f"Completed episode {episode_id}: {episode.title}")
        return True

    async def query_episodes(self, query: EpisodicQuery) -> list[Episode]:
        """Query episodic memories based on criteria."""
        candidates = []

        # Filter by episode type
        if query.episode_types:
            for episode_type in query.episode_types:
                candidates.extend(self.type_index.get(episode_type, []))
        else:
            candidates = list(self.episodes.keys())

        # Apply additional filters
        filtered_episodes = []
        for episode_id in candidates:
            episode = self.episodes[episode_id]

            # Time range filter
            if query.time_range:
                start_range, end_range = query.time_range
                if not (start_range <= episode.start_time <= end_range):
                    continue

            # Participant filter
            if query.participants:
                if not any(p in episode.context.participants for p in query.participants):
                    continue

            # Tools filter
            if query.tools_used:
                if not any(tool in episode.context.tools_used for tool in query.tools_used):
                    continue

            # Success score filter
            if query.min_success_score and episode.success_score:
                if episode.success_score < query.min_success_score:
                    continue

            filtered_episodes.append(episode)

        # Text-based similarity search
        if query.query_text:
            scored_episodes = []
            query_vector = await self._get_query_vector(query.query_text)

            if query_vector is not None:
                for episode in filtered_episodes:
                    episode_vector = episode.get_episode_vector(self.memory_store)
                    if episode_vector is not None:
                        similarity = np.dot(query_vector, episode_vector) / (
                            np.linalg.norm(query_vector) * np.linalg.norm(episode_vector)
                        )
                        scored_episodes.append((episode, similarity))

                # Sort by similarity
                scored_episodes.sort(key=lambda x: x[1], reverse=True)
                filtered_episodes = [episode for episode, _ in scored_episodes]

        # Constellation context scoring
        if query.constellation_context:
            constellation_scored = []
            for episode in filtered_episodes:
                constellation_score = 0.0
                total_weight = 0.0

                for star, relevance in query.constellation_context.items():
                    impact = episode.constellation_impact.get(star, 0.0)
                    constellation_score += impact * relevance
                    total_weight += relevance

                if total_weight > 0:
                    constellation_score /= total_weight

                constellation_scored.append((episode, constellation_score))

            # Sort by constellation relevance
            constellation_scored.sort(key=lambda x: x[1], reverse=True)
            filtered_episodes = [episode for episode, _ in constellation_scored]

        # Return top results
        return filtered_episodes[: query.max_results]

    async def get_episode(self, episode_id: str) -> Optional[Episode]:
        """Get episode by ID."""
        return self.episodes.get(episode_id)

    async def get_active_episodes(self) -> list[Episode]:
        """Get all currently active episodes."""
        return list(self.active_episodes.values())

    async def get_recent_episodes(self, days: int = 7) -> list[Episode]:
        """Get episodes from recent time period."""
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=days)

        recent_episodes = []
        for episode in self.episodes.values():
            if episode.start_time >= cutoff_time:
                recent_episodes.append(episode)

        return sorted(recent_episodes, key=lambda e: e.start_time, reverse=True)

    async def get_similar_episodes(self, episode_id: str, max_results: int = 5) -> list[tuple[Episode, float]]:
        """Find episodes similar to the given episode."""
        target_episode = self.episodes.get(episode_id)
        if not target_episode:
            return []

        target_vector = target_episode.get_episode_vector(self.memory_store)
        if target_vector is None:
            return []

        similar_episodes = []
        for other_id, other_episode in self.episodes.items():
            if other_id == episode_id:
                continue

            other_vector = other_episode.get_episode_vector(self.memory_store)
            if other_vector is None:
                continue

            similarity = np.dot(target_vector, other_vector) / (
                np.linalg.norm(target_vector) * np.linalg.norm(other_vector)
            )

            if similarity > self.similarity_threshold:
                similar_episodes.append((other_episode, similarity))

        # Sort by similarity
        similar_episodes.sort(key=lambda x: x[1], reverse=True)
        return similar_episodes[:max_results]

    async def _get_query_vector(self, query_text: str) -> Optional[np.ndarray]:
        """Get vector representation of query text."""
        # In a real implementation, this would use the same embedding model
        # as the memory vectors. For now, we'll create a simple representation.

        # This is a placeholder - would normally use proper text embedding
        words = query_text.lower().split()
        if not words:
            return None

        # Create simple word-based vector (this should be replaced with proper embeddings)
        vector = np.random.normal(0, 1, self.memory_store.embedding_dimension)
        return vector / np.linalg.norm(vector)

    async def _create_episode_summary_memory(self, episode: Episode):
        """Create a summary memory for completed episode."""
        # Create episode summary content
        summary_content = f"Episode: {episode.title}\n"
        summary_content += f"Type: {episode.episode_type.value}\n"
        summary_content += f"Duration: {episode.duration_minutes or 0} minutes\n"
        summary_content += f"Description: {episode.description}\n"

        if episode.key_insights:
            summary_content += f"Key insights: {'; '.join(episode.key_insights)}\n"

        if episode.lessons_learned:
            summary_content += f"Lessons learned: {'; '.join(episode.lessons_learned)}\n"

        if episode.success_score is not None:
            summary_content += f"Success score: {episode.success_score:.2f}\n"

        # Get episode vector
        episode_vector = episode.get_episode_vector(self.memory_store)
        if episode_vector is None:
            # Create a simple vector if no memories in episode
            episode_vector = np.random.normal(0, 1, self.memory_store.embedding_dimension)
            episode_vector = episode_vector / np.linalg.norm(episode_vector)

        # Determine importance based on success and learning
        importance = MemoryImportance.MEDIUM
        if (
            (episode.success_score
            and episode.success_score > 0.8)
            or (episode.learning_score
            and episode.learning_score > 0.8)
            or len(episode.key_insights) > 0
            or len(episode.lessons_learned) > 0
        ):
            importance = MemoryImportance.HIGH

        # Create summary memory
        summary_memory = MemoryVector(
            id=f"episode_summary_{episode.episode_id}",
            content=summary_content,
            vector=episode_vector,
            memory_type=MemoryType.EPISODIC,
            importance=importance,
            timestamp=episode.end_time or datetime.now(timezone.utc),
            constellation_tags=episode.constellation_impact.copy(),
            source_context=f"Episode summary: {episode.title}",
            emotional_valence=episode.context.emotional_state,
            confidence=episode.context.confidence_level,
        )

        # Add to memory store
        await self.memory_store.add_memory(summary_memory)

        logger.debug(f"Created summary memory for episode {episode.episode_id}")

    async def archive_old_episodes(self, days_threshold: Optional[int] = None) -> int:
        """Archive episodes older than threshold."""
        threshold_days = days_threshold or self.auto_archive_days
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=threshold_days)

        archived_count = 0
        episodes_to_archive = []

        for episode_id, episode in self.episodes.items():
            if episode.start_time < cutoff_time and episode.status == EpisodeStatus.COMPLETED:
                episodes_to_archive.append(episode_id)

        for episode_id in episodes_to_archive:
            episode = self.episodes[episode_id]
            episode.status = EpisodeStatus.ARCHIVED
            archived_count += 1
            logger.debug(f"Archived episode {episode_id}: {episode.title}")

        return archived_count

    def get_episode_stats(self) -> dict[str, Any]:
        """Get comprehensive episode statistics."""
        # Calculate additional statistics
        completed_episodes = [e for e in self.episodes.values() if e.status == EpisodeStatus.COMPLETED]

        success_scores = [e.success_score for e in completed_episodes if e.success_score is not None]
        durations = [e.duration_minutes for e in completed_episodes if e.duration_minutes is not None]

        stats = {
            **self.stats,
            "episode_distribution": {
                "by_type": {et.value: len(ids) for et, ids in self.type_index.items() if len(ids) > 0},
                "by_status": {},
            },
            "performance_metrics": {
                "success_rate": len([e for e in completed_episodes if e.success_score and e.success_score > 0.7])
                / max(1, len(completed_episodes)),
                "avg_success_score": np.mean(success_scores) if success_scores else 0.0,
                "avg_duration_minutes": np.mean(durations) if durations else 0.0,
                "completion_rate": len(completed_episodes) / max(1, self.stats["total_episodes"]),
            },
        }

        # Status distribution
        status_counts = {}
        for episode in self.episodes.values():
            status = episode.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        stats["episode_distribution"]["by_status"] = status_counts

        return stats
