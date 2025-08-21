"""
LUKHAS AI Memory - Episodic System
Stores and retrieves episodic memories
Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class Episode:
    """Represents an episodic memory"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: Any = None
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    emotional_tone: float = 0.0
    importance: float = 0.5
    tags: List[str] = field(default_factory=list)


class EpisodicMemory:
    """Manages episodic memories"""

    def __init__(self, max_episodes: int = 10000):
        self.episodes: Dict[str, Episode] = {}
        self.max_episodes = max_episodes
        self.index_by_tag: Dict[str, List[str]] = {}
        self.timeline: List[str] = []

    def store_episode(
        self, content: Any, context: Dict = None, tags: List[str] = None
    ) -> Episode:
        """Store a new episode"""
        episode = Episode(content=content, context=context or {}, tags=tags or [])

        # Manage capacity
        if len(self.episodes) >= self.max_episodes:
            self._consolidate_old_episodes()

        self.episodes[episode.id] = episode
        self.timeline.append(episode.id)

        # Update tag index
        for tag in episode.tags:
            if tag not in self.index_by_tag:
                self.index_by_tag[tag] = []
            self.index_by_tag[tag].append(episode.id)

        return episode

    def retrieve_by_similarity(self, query: Any, top_k: int = 5) -> List[Episode]:
        """Retrieve episodes by similarity to query"""
        # Simplified similarity search
        # In production, would use embeddings and vector search

        results = []
        for episode in self.episodes.values():
            # Simple string matching for demo
            if isinstance(query, str) and isinstance(episode.content, str):
                if query.lower() in episode.content.lower():
                    results.append(episode)

        # Sort by importance and recency
        results.sort(
            key=lambda e: (e.importance, e.timestamp.timestamp()), reverse=True
        )

        return results[:top_k]

    def retrieve_by_tags(self, tags: List[str]) -> List[Episode]:
        """Retrieve episodes by tags"""
        episode_ids = set()

        for tag in tags:
            if tag in self.index_by_tag:
                episode_ids.update(self.index_by_tag[tag])

        return [self.episodes[eid] for eid in episode_ids if eid in self.episodes]

    def get_timeline(
        self, start: datetime = None, end: datetime = None
    ) -> List[Episode]:
        """Get episodes within time range"""
        episodes = []

        for episode_id in self.timeline:
            episode = self.episodes.get(episode_id)
            if not episode:
                continue

            if start and episode.timestamp < start:
                continue
            if end and episode.timestamp > end:
                continue

            episodes.append(episode)

        return episodes

    def _consolidate_old_episodes(self):
        """Consolidate old episodes to make room"""
        # Remove least important old episodes
        sorted_episodes = sorted(
            self.episodes.values(),
            key=lambda e: (e.importance, e.timestamp.timestamp()),
        )

        # Keep most important 90%
        keep_count = int(self.max_episodes * 0.9)
        for episode in sorted_episodes[:-keep_count]:
            del self.episodes[episode.id]
            self.timeline.remove(episode.id)

            # Update tag index
            for tag in episode.tags:
                if tag in self.index_by_tag:
                    self.index_by_tag[tag].remove(episode.id)


# Singleton instance
_episodic_memory = None


def get_episodic_memory() -> EpisodicMemory:
    """Get or create episodic memory singleton"""
    global _episodic_memory
    if _episodic_memory is None:
        _episodic_memory = EpisodicMemory()
    return _episodic_memory
