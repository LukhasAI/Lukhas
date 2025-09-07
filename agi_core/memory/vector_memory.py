"""
Vector Memory Store for AGI Enhanced Memory

High-performance vector database for semantic similarity search and
associative memory patterns. Integrates with LUKHAS consciousness system.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import numpy as np

logger = logging.getLogger(__name__)


class MemoryType(Enum):
    """Types of memory content for organizational purposes."""

    EPISODIC = "episodic"  # Personal experiences and events
    SEMANTIC = "semantic"  # Facts and general knowledge
    PROCEDURAL = "procedural"  # Skills and procedures
    EMOTIONAL = "emotional"  # Emotional associations
    CREATIVE = "creative"  # Creative insights and ideas
    CONTEXTUAL = "contextual"  # Context-dependent information
    DREAM = "dream"  # Dream-derived patterns and insights


class MemoryImportance(Enum):
    """Memory importance levels for retention and retrieval."""

    CRITICAL = 5  # Never forget, highest priority
    HIGH = 4  # Important long-term memory
    MEDIUM = 3  # Standard memory importance
    LOW = 2  # Low importance, may decay
    EPHEMERAL = 1  # Temporary, likely to be forgotten


@dataclass
class MemoryVector:
    """
    Vector representation of memory content with rich metadata.

    Integrates with LUKHAS Constellation Framework for consciousness-aware memory.
    """

    id: str
    content: str
    vector: np.ndarray
    memory_type: MemoryType
    importance: MemoryImportance
    timestamp: datetime

    # LUKHAS Constellation Context
    constellation_tags: dict[str, float] = field(default_factory=dict)  # 8-star alignment

    # Memory Metadata
    source_context: Optional[str] = None
    emotional_valence: Optional[float] = None  # -1.0 to 1.0
    confidence: float = 1.0
    access_count: int = 0
    last_accessed: Optional[datetime] = None

    # Associative Links
    related_memories: list[str] = field(default_factory=list)  # IDs of related memories
    causal_links: list[str] = field(default_factory=list)  # Causal chain connections

    # Decay and Reinforcement
    strength: float = 1.0  # Memory strength (0.0 - 1.0)
    decay_rate: float = 0.01  # How fast this memory decays
    last_reinforced: Optional[datetime] = None

    def __post_init__(self):
        """Initialize derived fields."""
        if self.last_accessed is None:
            self.last_accessed = self.timestamp
        if self.last_reinforced is None:
            self.last_reinforced = self.timestamp

    def calculate_current_strength(self) -> float:
        """Calculate current memory strength based on time decay."""
        if self.importance == MemoryImportance.CRITICAL:
            return 1.0  # Critical memories don't decay

        time_elapsed = (datetime.now(timezone.utc) - self.last_reinforced).total_seconds() / 3600  # hours
        decay_factor = np.exp(-self.decay_rate * time_elapsed)
        return max(0.0, self.strength * decay_factor)

    def reinforce(self, strength_boost: float = 0.1):
        """Reinforce memory strength through access or rehearsal."""
        self.strength = min(1.0, self.strength + strength_boost)
        self.last_reinforced = datetime.now(timezone.utc)
        self.access_count += 1
        self.last_accessed = datetime.now(timezone.utc)

    def get_constellation_alignment(self, star: str) -> float:
        """Get alignment with specific constellation star."""
        return self.constellation_tags.get(star, 0.0)


@dataclass
class VectorSearchResult:
    """Result from vector similarity search."""

    memory: MemoryVector
    similarity: float
    relevance_score: float  # Composite score including recency, importance, etc.
    explanation: Optional[str] = None


class VectorMemoryStore:
    """
    High-Performance Vector Memory Store for AGI

    Provides semantic similarity search, associative memory patterns,
    and integration with LUKHAS consciousness framework.
    """

    def __init__(
        self, embedding_dimension: int = 768, max_memories: int = 100000, persistence_path: Optional[str] = None
    ):
        self.embedding_dimension = embedding_dimension
        self.max_memories = max_memories
        self.persistence_path = persistence_path

        # Memory Storage
        self.memories: dict[str, MemoryVector] = {}
        self.vectors = np.empty((0, embedding_dimension), dtype=np.float32)
        self.memory_ids: list[str] = []

        # Indexing for fast retrieval
        self.type_index: dict[MemoryType, list[str]] = {mt: [] for mt in MemoryType}
        self.importance_index: dict[MemoryImportance, list[str]] = {mi: [] for mi in MemoryImportance}
        self.constellation_index: dict[str, list[str]] = {}

        # Memory Statistics
        self.stats = {
            "total_memories": 0,
            "total_searches": 0,
            "avg_search_time": 0.0,
            "memory_types": {mt.value: 0 for mt in MemoryType},
        }

        # Load persisted memories if available
        if self.persistence_path and Path(self.persistence_path).exists():
            self.load_memories()

    async def add_memory(self, memory: MemoryVector) -> bool:
        """
        Add new memory to the vector store.

        Returns True if added successfully, False if memory limit exceeded.
        """
        try:
            # Check memory limit
            if len(self.memories) >= self.max_memories:
                await self._cleanup_memories()

            # Store memory
            self.memories[memory.id] = memory
            self.memory_ids.append(memory.id)

            # Update vector matrix
            if self.vectors.shape[0] == 0:
                self.vectors = memory.vector.reshape(1, -1)
            else:
                self.vectors = np.vstack([self.vectors, memory.vector])

            # Update indices
            self.type_index[memory.memory_type].append(memory.id)
            self.importance_index[memory.importance].append(memory.id)

            # Update constellation index
            for star, alignment in memory.constellation_tags.items():
                if alignment > 0.3:  # Only index significant alignments
                    if star not in self.constellation_index:
                        self.constellation_index[star] = []
                    self.constellation_index[star].append(memory.id)

            # Update statistics
            self.stats["total_memories"] += 1
            self.stats["memory_types"][memory.memory_type.value] += 1

            logger.debug(f"Added memory {memory.id} (type: {memory.memory_type.value})")
            return True

        except Exception as e:
            logger.error(f"Error adding memory {memory.id}: {e}")
            return False

    async def search_similar(
        self,
        query_vector: np.ndarray,
        k: int = 10,
        memory_types: Optional[list[MemoryType]] = None,
        min_importance: Optional[MemoryImportance] = None,
        constellation_filter: Optional[dict[str, float]] = None,
        time_decay_factor: float = 0.1,
    ) -> list[VectorSearchResult]:
        """
        Search for similar memories using vector similarity and additional filters.

        Args:
            query_vector: Query embedding vector
            k: Number of top results to return
            memory_types: Filter by memory types
            min_importance: Minimum importance level
            constellation_filter: Filter by constellation alignment
            time_decay_factor: How much to weight recent memories (0.0-1.0)

        Returns:
            List of search results sorted by relevance
        """
        start_time = asyncio.get_event_loop().time()

        try:
            if self.vectors.shape[0] == 0:
                return []

            # Calculate cosine similarity
            query_norm = np.linalg.norm(query_vector)
            if query_norm == 0:
                return []

            vector_norms = np.linalg.norm(self.vectors, axis=1)
            similarities = np.dot(self.vectors, query_vector) / (vector_norms * query_norm)

            # Get candidate memory indices
            candidate_indices = []
            for i, memory_id in enumerate(self.memory_ids):
                memory = self.memories[memory_id]

                # Apply filters
                if memory_types and memory.memory_type not in memory_types:
                    continue

                if min_importance and memory.importance.value < min_importance.value:
                    continue

                if constellation_filter:
                    meets_constellation = any(
                        memory.get_constellation_alignment(star) >= threshold
                        for star, threshold in constellation_filter.items()
                    )
                    if not meets_constellation:
                        continue

                candidate_indices.append(i)

            if not candidate_indices:
                return []

            # Calculate relevance scores for candidates
            results = []
            for i in candidate_indices:
                memory_id = self.memory_ids[i]
                memory = self.memories[memory_id]
                similarity = similarities[i]

                # Calculate composite relevance score
                relevance_score = self._calculate_relevance_score(memory, similarity, time_decay_factor)

                results.append(
                    VectorSearchResult(memory=memory, similarity=float(similarity), relevance_score=relevance_score)
                )

            # Sort by relevance and return top k
            results.sort(key=lambda x: x.relevance_score, reverse=True)
            results = results[:k]

            # Update search statistics
            search_time = asyncio.get_event_loop().time() - start_time
            self.stats["total_searches"] += 1
            self.stats["avg_search_time"] = (
                self.stats["avg_search_time"] * (self.stats["total_searches"] - 1) + search_time
            ) / self.stats["total_searches"]

            return results

        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            return []

    def _calculate_relevance_score(self, memory: MemoryVector, similarity: float, time_decay_factor: float) -> float:
        """Calculate composite relevance score for memory."""
        # Base similarity score (40%)
        score = similarity * 0.4

        # Memory strength and importance (30%)
        current_strength = memory.calculate_current_strength()
        importance_weight = memory.importance.value / 5.0
        score += (current_strength * importance_weight) * 0.3

        # Recency factor (20%)
        hours_since_access = (datetime.now(timezone.utc) - memory.last_accessed).total_seconds() / 3600
        recency_score = np.exp(-time_decay_factor * hours_since_access)
        score += recency_score * 0.2

        # Access frequency (10%)
        # Normalize access count (log scale to prevent dominance of very frequently accessed items)
        frequency_score = min(1.0, np.log(memory.access_count + 1) / np.log(100))
        score += frequency_score * 0.1

        return min(1.0, score)

    async def get_memory(self, memory_id: str, reinforce: bool = True) -> Optional[MemoryVector]:
        """Retrieve memory by ID with optional reinforcement."""
        if memory_id not in self.memories:
            return None

        memory = self.memories[memory_id]

        if reinforce:
            memory.reinforce(0.05)  # Small reinforcement for access

        return memory

    async def update_memory(self, memory_id: str, updates: dict[str, Any]) -> bool:
        """Update memory metadata or content."""
        if memory_id not in self.memories:
            return False

        try:
            memory = self.memories[memory_id]

            for field, value in updates.items():
                if hasattr(memory, field):
                    setattr(memory, field, value)

            # If content changed, may need to update vector (not implemented here)
            # This would require re-embedding the content

            return True

        except Exception as e:
            logger.error(f"Error updating memory {memory_id}: {e}")
            return False

    async def delete_memory(self, memory_id: str) -> bool:
        """Delete memory from store."""
        if memory_id not in self.memories:
            return False

        try:
            memory = self.memories[memory_id]

            # Remove from main storage
            del self.memories[memory_id]

            # Remove from indices
            memory_index = self.memory_ids.index(memory_id)
            self.memory_ids.pop(memory_index)

            # Remove vector
            self.vectors = np.delete(self.vectors, memory_index, axis=0)

            # Update type and importance indices
            self.type_index[memory.memory_type].remove(memory_id)
            self.importance_index[memory.importance].remove(memory_id)

            # Update constellation index
            for star_memories in self.constellation_index.values():
                if memory_id in star_memories:
                    star_memories.remove(memory_id)

            # Update statistics
            self.stats["total_memories"] -= 1
            self.stats["memory_types"][memory.memory_type.value] -= 1

            return True

        except Exception as e:
            logger.error(f"Error deleting memory {memory_id}: {e}")
            return False

    async def get_associative_memories(self, memory_id: str, depth: int = 1) -> list[MemoryVector]:
        """Get memories associated with given memory through explicit links."""
        if memory_id not in self.memories:
            return []

        associated = []
        to_explore = [(memory_id, 0)]  # (id, current_depth)
        explored = set()

        while to_explore:
            current_id, current_depth = to_explore.pop(0)

            if current_id in explored or current_depth > depth:
                continue

            explored.add(current_id)

            if current_id in self.memories:
                memory = self.memories[current_id]

                if current_depth > 0:  # Don't include the original memory
                    associated.append(memory)

                # Add related memories to explore
                if current_depth < depth:
                    for related_id in memory.related_memories:
                        if related_id not in explored:
                            to_explore.append((related_id, current_depth + 1))

        return associated

    async def _cleanup_memories(self):
        """Remove old, low-importance memories to make space."""
        # Calculate cleanup candidates (memories with very low current strength)
        cleanup_candidates = []

        for memory_id, memory in self.memories.items():
            if memory.importance == MemoryImportance.CRITICAL:
                continue  # Never clean up critical memories

            current_strength = memory.calculate_current_strength()
            if current_strength < 0.1:  # Very weak memories
                cleanup_candidates.append((memory_id, current_strength))

        # Sort by strength and remove weakest 10%
        cleanup_candidates.sort(key=lambda x: x[1])
        to_remove = cleanup_candidates[: max(1, len(cleanup_candidates) // 10)]

        for memory_id, _ in to_remove:
            await self.delete_memory(memory_id)

        logger.info(f"Cleaned up {len(to_remove} weak memories")

    def save_memories(self):
        """Persist memories to disk."""
        if not self.persistence_path:
            return

        try:
            data = {
                "memories": {
                    mid: {
                        "content": m.content,
                        "vector": m.vector.tolist(),
                        "memory_type": m.memory_type.value,
                        "importance": m.importance.value,
                        "timestamp": m.timestamp.isoformat(),
                        "constellation_tags": m.constellation_tags,
                        "source_context": m.source_context,
                        "emotional_valence": m.emotional_valence,
                        "confidence": m.confidence,
                        "access_count": m.access_count,
                        "last_accessed": m.last_accessed.isoformat() if m.last_accessed else None,
                        "related_memories": m.related_memories,
                        "causal_links": m.causal_links,
                        "strength": m.strength,
                        "decay_rate": m.decay_rate,
                        "last_reinforced": m.last_reinforced.isoformat() if m.last_reinforced else None,
                    }
                    for mid, m in self.memories.items()
                },
                "stats": self.stats,
            }

            with open(self.persistence_path, "w") as f:
                json.dump(data, f, indent=2)

            logger.info(f"Saved {len(self.memories} memories to {self.persistence_path}")

        except Exception as e:
            logger.error(f"Error saving memories: {e}")

    def load_memories(self):
        """Load memories from disk."""
        if not self.persistence_path or not Path(self.persistence_path).exists():
            return

        try:
            with open(self.persistence_path) as f:
                data = json.load(f)

            # Reconstruct memories
            for memory_id, memory_data in data.get("memories", {}).items():
                memory = MemoryVector(
                    id=memory_id,
                    content=memory_data["content"],
                    vector=np.array(memory_data["vector"]),
                    memory_type=MemoryType(memory_data["memory_type"]),
                    importance=MemoryImportance(memory_data["importance"]),
                    timestamp=datetime.fromisoformat(memory_data["timestamp"]),
                    constellation_tags=memory_data.get("constellation_tags", {}),
                    source_context=memory_data.get("source_context"),
                    emotional_valence=memory_data.get("emotional_valence"),
                    confidence=memory_data.get("confidence", 1.0),
                    access_count=memory_data.get("access_count", 0),
                    last_accessed=(
                        datetime.fromisoformat(memory_data["last_accessed"])
                        if memory_data.get("last_accessed")
                        else None
                    ),
                    related_memories=memory_data.get("related_memories", []),
                    causal_links=memory_data.get("causal_links", []),
                    strength=memory_data.get("strength", 1.0),
                    decay_rate=memory_data.get("decay_rate", 0.01),
                    last_reinforced=(
                        datetime.fromisoformat(memory_data["last_reinforced"])
                        if memory_data.get("last_reinforced")
                        else None
                    ),
                )

                # Use asyncio.run for the async method - not ideal but needed for initialization
                asyncio.create_task(self.add_memory(memory))

            # Restore stats
            if "stats" in data:
                self.stats.update(data["stats"])

            logger.info(f"Loaded {len(self.memories} memories from {self.persistence_path}")

        except Exception as e:
            logger.error(f"Error loading memories: {e}")

    def get_memory_stats(self) -> dict[str, Any]:
        """Get comprehensive memory store statistics."""
        return {
            **self.stats,
            "memory_distribution": {
                "by_type": {mt.value: len(ids) for mt, ids in self.type_index.items()},
                "by_importance": {mi.name: len(ids) for mi, ids in self.importance_index.items()},
                "by_constellation": {star: len(ids) for star, ids in self.constellation_index.items()},
            },
            "performance": {
                "vector_dimension": self.embedding_dimension,
                "index_size": self.vectors.shape[0],
                "avg_search_time_ms": self.stats["avg_search_time"] * 1000,
            },
        }
