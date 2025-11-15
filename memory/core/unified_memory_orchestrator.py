"""
Unified Memory Orchestrator for LUKHAS AI System

Multi-tier memory system mimicking human memory architecture:
- Working Memory: Active, fast (in-memory/Redis)
- Episodic Memory: Time-ordered events (PostgreSQL)
- Semantic Memory: Concept relationships (vector DB)
- Fold Storage: Compressed archives (filesystem/S3)

Consolidation happens at regular intervals:
- Every 15 min: working → episodic
- Every 6 hours: episodic → semantic + folds
- Weekly: Fold compression
"""

import asyncio
import hashlib
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

# Import existing memory systems
from cognitive_core.memory.episodic_memory import (
    Episode,
    EpisodeContext,
    EpisodeStatus,
    EpisodeType,
    EpisodicMemorySystem,
    EpisodicQuery,
)
from cognitive_core.memory.semantic_memory import (
    NodeType,
    RelationType,
    SemanticMemoryGraph,
    SemanticNode,
    SemanticQuery,
    SemanticRelation,
)
from cognitive_core.memory.vector_memory import (
    MemoryImportance,
    MemoryType as VectorMemoryType,
    MemoryVector,
    VectorMemoryStore,
)

logger = logging.getLogger(__name__)


class MemoryType(str, Enum):
    """Memory tier types for the unified orchestrator."""

    WORKING = "working"  # Active, < 15 min lifetime
    EPISODIC = "episodic"  # Time-stamped events
    SEMANTIC = "semantic"  # Concepts, relationships
    FOLD = "fold"  # Compressed archives


@dataclass
class Memory:
    """Unified memory representation across tiers."""

    id: str
    content: Any
    memory_type: MemoryType
    tier: str  # Which tier it's stored in
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    importance_score: float = 0.5
    access_count: int = 0
    last_accessed: Optional[datetime] = None


@dataclass
class ConsolidationResult:
    """Result of memory consolidation process."""

    timestamp: datetime
    working_to_episodic: int = 0
    episodic_to_semantic: int = 0
    episodic_to_folds: int = 0
    folds_compressed: int = 0
    total_memories_processed: int = 0
    duration_seconds: float = 0.0
    errors: List[str] = field(default_factory=list)


class WorkingMemory:
    """
    Working Memory Store - Fast, temporary storage.

    Stores active memories that are being worked with. Automatically expires
    memories older than 15 minutes during consolidation.
    """

    def __init__(self, ttl_minutes: int = 15):
        self.ttl_minutes = ttl_minutes
        self.memories: Dict[str, Memory] = {}
        self.creation_times: Dict[str, datetime] = {}

    def store(self, key: str, value: Any, metadata: Optional[Dict] = None) -> str:
        """Store value in working memory."""
        memory_id = f"work_{key}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

        memory = Memory(
            id=memory_id,
            content=value,
            memory_type=MemoryType.WORKING,
            tier="working",
            timestamp=datetime.now(timezone.utc),
            metadata=metadata or {},
        )

        self.memories[memory_id] = memory
        self.creation_times[memory_id] = datetime.now(timezone.utc)

        logger.debug(f"Stored working memory: {memory_id}")
        return memory_id

    def retrieve(self, key: str) -> Optional[Memory]:
        """Retrieve memory by key."""
        if key in self.memories:
            memory = self.memories[key]
            memory.access_count += 1
            memory.last_accessed = datetime.now(timezone.utc)
            return memory
        return None

    def get_expired_memories(self, cutoff_time: Optional[datetime] = None) -> List[Memory]:
        """Get memories older than TTL."""
        if cutoff_time is None:
            cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=self.ttl_minutes)

        expired = []
        for memory_id, creation_time in self.creation_times.items():
            if creation_time < cutoff_time:
                if memory_id in self.memories:
                    expired.append(self.memories[memory_id])

        return expired

    def remove_memory(self, memory_id: str) -> bool:
        """Remove memory from working memory."""
        if memory_id in self.memories:
            del self.memories[memory_id]
            del self.creation_times[memory_id]
            return True
        return False

    def get_all_memories(self) -> List[Memory]:
        """Get all working memories."""
        return list(self.memories.values())


class FoldEngine:
    """
    Fold Storage Engine - Compressed long-term memory archives.

    Creates and manages memory folds - compressed representations of
    episodic memories for long-term storage.
    """

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = Path(storage_path) if storage_path else Path("./memory_folds")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.folds: Dict[str, Dict[str, Any]] = {}
        self.fold_index: Dict[str, List[str]] = defaultdict(list)  # tag -> fold_ids

    def create_fold(self, memories: List[Memory], fold_name: Optional[str] = None) -> str:
        """Create compressed memory fold from list of memories."""
        fold_id = fold_name or f"fold_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

        # Compress memories
        compressed_content = self._compress_memories(memories)

        fold_data = {
            "fold_id": fold_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "memory_count": len(memories),
            "compressed_content": compressed_content,
            "memory_ids": [m.id for m in memories],
            "time_range": {
                "start": min(m.timestamp for m in memories).isoformat() if memories else None,
                "end": max(m.timestamp for m in memories).isoformat() if memories else None,
            },
            "metadata": self._extract_fold_metadata(memories),
        }

        self.folds[fold_id] = fold_data

        # Index by tags
        for tag in fold_data["metadata"].get("tags", []):
            self.fold_index[tag].append(fold_id)

        # Persist to disk
        self._save_fold(fold_id, fold_data)

        logger.info(f"Created fold {fold_id} with {len(memories)} memories")
        return fold_id

    def retrieve_fold(self, fold_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve fold by ID."""
        if fold_id in self.folds:
            return self.folds[fold_id]

        # Try loading from disk
        fold_path = self.storage_path / f"{fold_id}.json"
        if fold_path.exists():
            import json

            with open(fold_path) as f:
                fold_data = json.load(f)
                self.folds[fold_id] = fold_data
                return fold_data

        return None

    def search_folds(self, tags: Optional[List[str]] = None, start_date: Optional[datetime] = None) -> List[str]:
        """Search folds by tags or date range."""
        if tags:
            # Find folds matching any of the tags
            fold_ids = set()
            for tag in tags:
                fold_ids.update(self.fold_index.get(tag, []))
            return list(fold_ids)

        # For now, return all fold IDs if no filters
        return list(self.folds.keys())

    def _compress_memories(self, memories: List[Memory]) -> Dict[str, Any]:
        """Compress memories using pattern detection and deduplication."""
        # Extract content
        contents = [str(m.content) for m in memories]

        # Simple compression: find common patterns and create summary
        all_text = " ".join(contents)
        word_freq = defaultdict(int)
        for word in all_text.split():
            if len(word) > 3:
                word_freq[word.lower()] += 1

        # Get top patterns
        top_patterns = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]

        return {
            "summary": all_text[:500] + "..." if len(all_text) > 500 else all_text,
            "common_patterns": [{"word": w, "count": c} for w, c in top_patterns],
            "compression_ratio": len(all_text) / max(500, len(all_text)),
        }

    def _extract_fold_metadata(self, memories: List[Memory]) -> Dict[str, Any]:
        """Extract metadata from memories for fold indexing."""
        tags = set()
        memory_types = set()

        for memory in memories:
            if "tags" in memory.metadata:
                tags.update(memory.metadata["tags"])
            memory_types.add(memory.memory_type.value)

        return {"tags": list(tags), "memory_types": list(memory_types), "source_count": len(memories)}

    def _save_fold(self, fold_id: str, fold_data: Dict[str, Any]):
        """Save fold to disk."""
        import json

        fold_path = self.storage_path / f"{fold_id}.json"
        with open(fold_path, "w") as f:
            json.dump(fold_data, f, indent=2)


class UnifiedMemoryOrchestrator:
    """
    Multi-tier unified memory orchestrator.

    Memory Tiers:
    1. Working Memory: Active, fast (in-memory/Redis)
    2. Episodic Memory: Time-ordered events (PostgreSQL)
    3. Semantic Memory: Concept relationships (vector DB)
    4. Fold Storage: Compressed archives (filesystem/S3)

    Consolidation:
    - Every 15 min: working → episodic
    - Every 6 hours: episodic → semantic + folds
    - Weekly: Fold compression
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize unified memory orchestrator.

        Args:
            config: Configuration dictionary with optional keys:
                - working_memory_ttl: Minutes before working memory expires (default: 15)
                - episodic_to_semantic_hours: Hours before episodic→semantic (default: 6)
                - fold_compression_days: Days before fold compression (default: 7)
                - vector_dimension: Embedding dimension (default: 768)
                - storage_path: Path for fold storage
        """
        config = config or {}

        # Initialize vector memory store
        self.vector_store = VectorMemoryStore(
            embedding_dimension=config.get("vector_dimension", 768),
            max_memories=config.get("max_memories", 100000),
            persistence_path=config.get("vector_persistence_path"),
        )

        # Initialize memory tiers
        self.working_memory = WorkingMemory(ttl_minutes=config.get("working_memory_ttl", 15))

        self.episodic_store = EpisodicMemorySystem(memory_store=self.vector_store)

        self.semantic_store = SemanticMemoryGraph()

        self.fold_engine = FoldEngine(storage_path=config.get("storage_path", "./memory_folds"))

        # Consolidation configuration
        self.config = {
            "working_memory_ttl": config.get("working_memory_ttl", 15),
            "episodic_to_semantic_hours": config.get("episodic_to_semantic_hours", 6),
            "fold_compression_days": config.get("fold_compression_days", 7),
        }

        # Consolidation tracking
        self.last_consolidation = datetime.now(timezone.utc)
        self.last_fold_compression = datetime.now(timezone.utc)

        logger.info("Unified Memory Orchestrator initialized")

    def store(self, key: str, value: Any, memory_type: MemoryType, metadata: Optional[Dict] = None) -> str:
        """
        Store in appropriate tier based on memory_type.

        Args:
            key: Memory key/identifier
            value: Content to store
            memory_type: Type of memory (determines tier)
            metadata: Optional metadata

        Returns:
            Memory ID
        """
        metadata = metadata or {}

        if memory_type == MemoryType.WORKING:
            return self.working_memory.store(key, value, metadata)

        elif memory_type == MemoryType.EPISODIC:
            # Store in episodic memory
            return asyncio.run(self._store_episodic(key, value, metadata))

        elif memory_type == MemoryType.SEMANTIC:
            # Store in semantic memory
            return asyncio.run(self._store_semantic(key, value, metadata))

        elif memory_type == MemoryType.FOLD:
            # Create fold directly
            memory = Memory(
                id=key,
                content=value,
                memory_type=memory_type,
                tier="fold",
                timestamp=datetime.now(timezone.utc),
                metadata=metadata,
            )
            return self.fold_engine.create_fold([memory], fold_name=key)

        else:
            # Default to working memory
            return self.working_memory.store(key, value, metadata)

    async def _store_episodic(self, key: str, value: Any, metadata: Dict) -> str:
        """Store episodic memory."""
        episode_type = EpisodeType(metadata.get("episode_type", "INTERACTION"))

        context = EpisodeContext(
            participants=metadata.get("participants", []),
            tools_used=metadata.get("tools_used", []),
            goals=metadata.get("goals", []),
        )

        episode_id = await self.episodic_store.create_episode(
            title=key, description=str(value), episode_type=episode_type, context=context
        )

        return episode_id

    async def _store_semantic(self, key: str, value: Any, metadata: Dict) -> str:
        """Store semantic memory."""
        node_type = NodeType(metadata.get("node_type", "CONCEPT"))

        node = SemanticNode(
            node_id=f"sem_{key}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
            name=key,
            node_type=node_type,
            description=str(value),
            properties=metadata.get("properties", {}),
            tags=metadata.get("tags", []),
        )

        await self.semantic_store.add_node(node)
        return node.node_id

    def retrieve(self, key: str) -> Optional[Any]:
        """
        Retrieve from any tier (search all).

        Args:
            key: Memory key to search for

        Returns:
            Memory content if found, None otherwise
        """
        # Search working memory first (fastest)
        working_result = self.working_memory.retrieve(key)
        if working_result:
            return working_result.content

        # Search episodic
        episodic_result = asyncio.run(self.episodic_store.get_episode(key))
        if episodic_result:
            return episodic_result

        # Search semantic
        semantic_result = asyncio.run(self.semantic_store.get_node(key))
        if semantic_result:
            return semantic_result

        # Search folds
        fold_result = self.fold_engine.retrieve_fold(key)
        if fold_result:
            return fold_result

        return None

    def consolidate(self) -> ConsolidationResult:
        """
        Run memory consolidation (working→episodic→semantic).

        Returns:
            ConsolidationResult with statistics
        """
        start_time = datetime.now(timezone.utc)
        result = ConsolidationResult(timestamp=start_time)

        try:
            # Stage 1: Working → Episodic (memories older than TTL)
            expired_working = self.working_memory.get_expired_memories()
            for memory in expired_working:
                try:
                    # Convert to episodic
                    episode_id = asyncio.run(
                        self._store_episodic(
                            key=memory.id,
                            value=memory.content,
                            metadata={**memory.metadata, "from_working": True},
                        )
                    )

                    # Remove from working memory
                    self.working_memory.remove_memory(memory.id)
                    result.working_to_episodic += 1

                except Exception as e:
                    result.errors.append(f"Failed to consolidate {memory.id}: {str(e)}")
                    logger.error(f"Error consolidating working memory {memory.id}: {e}")

            # Stage 2: Episodic → Semantic + Folds (memories older than configured hours)
            cutoff_time = datetime.now(timezone.utc) - timedelta(
                hours=self.config["episodic_to_semantic_hours"]
            )
            recent_episodes = asyncio.run(
                self.episodic_store.get_recent_episodes(days=self.config["fold_compression_days"])
            )

            for episode in recent_episodes:
                if episode.end_time and episode.end_time < cutoff_time:
                    try:
                        # Extract concepts for semantic memory
                        concepts_added = asyncio.run(self._extract_concepts_from_episode(episode))
                        if concepts_added:
                            result.episodic_to_semantic += concepts_added

                        # Create fold for old episodic memory
                        memory = Memory(
                            id=episode.episode_id,
                            content=episode.description,
                            memory_type=MemoryType.EPISODIC,
                            tier="episodic",
                            timestamp=episode.start_time,
                            metadata={
                                "episode_type": episode.episode_type.value,
                                "success_score": episode.success_score,
                            },
                        )

                        self.fold_engine.create_fold([memory], fold_name=episode.episode_id)
                        result.episodic_to_folds += 1

                    except Exception as e:
                        result.errors.append(f"Failed to process episode {episode.episode_id}: {str(e)}")
                        logger.error(f"Error processing episode {episode.episode_id}: {e}")

            # Stage 3: Fold compression (weekly)
            days_since_compression = (datetime.now(timezone.utc) - self.last_fold_compression).days
            if days_since_compression >= 7:
                # Compress old folds (placeholder - actual implementation would merge folds)
                result.folds_compressed = 0
                self.last_fold_compression = datetime.now(timezone.utc)

            # Update consolidation tracking
            self.last_consolidation = datetime.now(timezone.utc)
            result.total_memories_processed = (
                result.working_to_episodic + result.episodic_to_semantic + result.episodic_to_folds
            )
            result.duration_seconds = (datetime.now(timezone.utc) - start_time).total_seconds()

            logger.info(
                f"Consolidation completed: {result.total_memories_processed} memories processed "
                f"in {result.duration_seconds:.2f}s"
            )

        except Exception as e:
            result.errors.append(f"Consolidation error: {str(e)}")
            logger.error(f"Error during consolidation: {e}")

        return result

    async def _extract_concepts_from_episode(self, episode: Episode) -> int:
        """Extract concepts from episode and add to semantic memory."""
        concepts_added = 0

        # Extract key insights as concepts
        for insight in episode.key_insights:
            try:
                node = SemanticNode(
                    node_id=f"concept_{hashlib.md5(insight.encode()).hexdigest()[:12]}",
                    name=insight[:50],  # Use first 50 chars as name
                    node_type=NodeType.CONCEPT,
                    description=insight,
                    properties={"source_episode": episode.episode_id},
                )

                await self.semantic_store.add_node(node)
                concepts_added += 1

            except Exception as e:
                logger.debug(f"Skipped duplicate concept: {insight[:30]}")

        return concepts_added

    def search_semantic(self, query: str, limit: int = 10) -> List[Memory]:
        """
        Semantic similarity search using vector embeddings.

        Args:
            query: Search query
            limit: Maximum results to return

        Returns:
            List of Memory objects matching the query
        """
        # Search semantic graph
        semantic_query = SemanticQuery(query_text=query, max_results=limit)

        semantic_results = asyncio.run(self.semantic_store.search_nodes(semantic_query))

        # Convert to Memory objects
        memories = []
        for node, score in semantic_results:
            memory = Memory(
                id=node.node_id,
                content=node.description,
                memory_type=MemoryType.SEMANTIC,
                tier="semantic",
                timestamp=node.created_time,
                metadata={
                    "node_type": node.node_type.value,
                    "relevance_score": score,
                    "properties": node.properties,
                },
                importance_score=node.importance_score,
            )
            memories.append(memory)

        return memories

    def create_fold(self, memories: List[Memory]) -> str:
        """
        Create compressed memory fold.

        Args:
            memories: List of memories to compress into fold

        Returns:
            Fold ID
        """
        return self.fold_engine.create_fold(memories)

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory system statistics."""
        return {
            "working_memory": {
                "total_memories": len(self.working_memory.memories),
                "expired_count": len(self.working_memory.get_expired_memories()),
            },
            "episodic_memory": self.episodic_store.get_episode_stats(),
            "semantic_memory": self.semantic_store.get_semantic_stats(),
            "vector_store": self.vector_store.get_memory_stats(),
            "folds": {"total_folds": len(self.fold_engine.folds)},
            "consolidation": {
                "last_consolidation": self.last_consolidation.isoformat(),
                "last_fold_compression": self.last_fold_compression.isoformat(),
            },
        }


__all__ = [
    "UnifiedMemoryOrchestrator",
    "MemoryType",
    "Memory",
    "ConsolidationResult",
    "WorkingMemory",
    "FoldEngine",
]
