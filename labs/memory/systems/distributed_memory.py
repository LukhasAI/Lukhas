"""
Distributed Memory System using Colony Architecture
Implements scalable, fault-tolerant memory across multiple colonies
"""

import asyncio
import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional

import numpy as np

from core.colonies.memory_colony import MemoryColony
from core.common import get_logger
from core.event_sourcing import EventStore
from core.swarm import SwarmHub
from memory.distributed_state_manager import DistributedStateManager, StateType

logger = get_logger(__name__)


class MemoryType(Enum):
    """Types of memory in the distributed system."""

    EPISODIC = "episodic"  # Personal experiences, events
    SEMANTIC = "semantic"  # Facts, concepts, knowledge
    PROCEDURAL = "procedural"  # Skills, how-to knowledge
    WORKING = "working"  # Short-term, active memory
    SENSORY = "sensory"  # Very short-term sensory buffer


@dataclass
class DistributedMemory:
    """Represents a memory item in the distributed system."""

    memory_id: str
    memory_type: MemoryType
    content: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    importance: float = 0.5
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    colony_id: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    embeddings: Optional[np.ndarray] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "memory_id": self.memory_id,
            "memory_type": self.memory_type.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "importance": self.importance,
            "access_count": self.access_count,
            "last_accessed": (self.last_accessed.isoformat() if self.last_accessed else None),
            "colony_id": self.colony_id,
            "tags": self.tags,
            "embeddings": (self.embeddings.tolist() if self.embeddings is not None else None),
        }


class DistributedMemorySystem:
    """
    Distributed memory system that uses colony architecture for
    scalable, fault-tolerant memory storage and retrieval.
    """

    def __init__(self, system_id: str = "lukhas-memory"):
        """Initialize the distributed memory system."""
        self.system_id = system_id
        self.logger = logging.getLogger(f"{__name__}.{system_id}")
        self.logger.info(f"Initializing DistributedMemorySystem: {system_id}")

        # Memory colonies for different memory types
        self.memory_colonies: dict[MemoryType, MemoryColony] = {}

        # Swarm hub for colony coordination
        self.swarm_hub = SwarmHub()

        # Event store for memory persistence
        self.event_store = EventStore(f"memory_{system_id}.db")

        # State manager for fast access
        self.state_manager = DistributedStateManager(node_id=f"memory-node-{system_id}", event_store=self.event_store)

        # Memory index for fast lookup
        self.memory_index: dict[str, tuple[MemoryType, str]] = {}  # memory_id -> (type, colony_id)

        # Memory similarity cache
        self.similarity_cache: dict[str, list[tuple[str, float]]] = {}

        # Colony health tracking
        self.colony_health: dict[str, float] = {}

        self._initialized = False

    async def initialize(self):
        """Initialize the distributed memory system and colonies."""
        if self._initialized:
            return

        self.logger.info("Initializing memory colonies...")

        try:
            # Create colonies for each memory type
            for memory_type in MemoryType:
                colony_id = f"{self.system_id}-{memory_type.value}"
                colony = MemoryColony(colony_id)
                await colony.start()

                self.memory_colonies[memory_type] = colony
                self.swarm_hub.register_colony(colony)
                self.colony_health[colony_id] = 1.0

                self.logger.info(f"Initialized {memory_type.value} memory colony: {colony_id}")

            # Initialize state manager
            await self.state_manager.initialize()

            # Load existing memory index
            await self._load_memory_index()

            self._initialized = True
            self.logger.info("DistributedMemorySystem initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize distributed memory system: {e}")
            raise

    async def shutdown(self):
        """Shutdown the distributed memory system."""
        self.logger.info("Shutting down distributed memory system...")

        # Stop all colonies
        for colony in self.memory_colonies.values():
            await colony.stop()

        # Shutdown state manager
        await self.state_manager.shutdown()

        self._initialized = False
        self.logger.info("DistributedMemorySystem shutdown complete")

    async def store_memory(
        self,
        content: dict[str, Any],
        memory_type: MemoryType,
        importance: float = 0.5,
        tags: Optional[list[str]] = None,
    ) -> str:
        """
        Store a memory in the distributed system.

        Args:
            content: The memory content to store
            memory_type: Type of memory (episodic, semantic, etc.)
            importance: Importance score (0-1)
            tags: Optional tags for categorization

        Returns:
            The generated memory ID
        """
        if not self._initialized:
            await self.initialize()

        # Generate memory ID
        memory_id = self._generate_memory_id(content, memory_type)

        # Create memory object
        memory = DistributedMemory(
            memory_id=memory_id,
            memory_type=memory_type,
            content=content,
            importance=importance,
            tags=tags or [],
        )

        # Generate embeddings if applicable
        if memory_type in [MemoryType.EPISODIC, MemoryType.SEMANTIC]:
            memory.embeddings = await self._generate_embeddings(content)

        # Select colony for storage
        colony = self.memory_colonies[memory_type]
        memory.colony_id = colony.colony_id

        # Store in colony
        storage_task = {
            "type": "store_memory",
            "memory": memory.to_dict(),
            "replication_factor": self._get_replication_factor(importance),
        }

        result = await colony.execute_task(f"store-{memory_id}", storage_task)

        if result.get("status") == "completed":
            # Update memory index
            self.memory_index[memory_id] = (memory_type, colony.colony_id)

            # Store in state manager for fast access
            state_type = self._get_state_type(importance)
            await self.state_manager.set(f"memory:{memory_id}", memory.to_dict(), state_type)

            # Invalidate similarity cache for this type
            self._invalidate_similarity_cache(memory_type)

            self.logger.info(f"Stored memory {memory_id} in {memory_type.value} colony")
            return memory_id
        else:
            raise Exception(f"Failed to store memory: {result.get('error', 'Unknown error')}")

    async def retrieve_memory(self, memory_id: str) -> Optional[DistributedMemory]:
        """
        Retrieve a memory by ID from the distributed system.

        Args:
            memory_id: The ID of the memory to retrieve

        Returns:
            The memory object or None if not found
        """
        # First check state manager cache
        cached = await self.state_manager.get(f"memory:{memory_id}")
        if cached:
            return self._dict_to_memory(cached)

        # Check memory index
        if memory_id not in self.memory_index:
            return None

        memory_type, colony_id = self.memory_index[memory_id]
        colony = self.memory_colonies[memory_type]

        # Retrieve from colony
        retrieval_task = {"type": "retrieve_memory", "memory_id": memory_id}

        result = await colony.execute_task(f"retrieve-{memory_id}", retrieval_task)

        if result.get("status") == "completed" and result.get("memory"):
            memory = self._dict_to_memory(result["memory"])

            # Update access count and last accessed
            memory.access_count += 1
            memory.last_accessed = datetime.now(timezone.utc)

            # Update in state manager
            await self.state_manager.set(
                f"memory:{memory_id}",
                memory.to_dict(),
                self._get_state_type(memory.importance),
            )

            return memory

        return None

    async def search_memories(
        self,
        query: dict[str, Any],
        memory_types: Optional[list[MemoryType]] = None,
        limit: int = 10,
        threshold: float = 0.7,
    ) -> list[DistributedMemory]:
        """
        Search for memories across colonies.

        Args:
            query: Search query (can contain content, tags, embeddings)
            memory_types: Types of memory to search (None = all)
            limit: Maximum number of results
            threshold: Similarity threshold (0-1)

        Returns:
            List of matching memories sorted by relevance
        """
        if not memory_types:
            memory_types = list(MemoryType)

        # Generate query embedding if text query
        query_embedding = None
        if "text" in query:
            query_embedding = await self._generate_embeddings({"text": query["text"]})

        # Search across relevant colonies in parallel
        search_tasks = []
        for memory_type in memory_types:
            if memory_type in self.memory_colonies:
                colony = self.memory_colonies[memory_type]

                search_task = {
                    "type": "search_memories",
                    "query": query,
                    "query_embedding": (query_embedding.tolist() if query_embedding is not None else None),
                    "limit": limit * 2,  # Get more to filter later
                    "threshold": threshold,
                }

                task = colony.execute_task(f"search-{datetime.now(timezone.utc).timestamp()}", search_task)
                search_tasks.append((memory_type, task))

        # Gather results from all colonies
        all_results = []
        for memory_type, task in search_tasks:
            try:
                result = await task
                if result.get("status") == "completed" and result.get("memories"):
                    for memory_dict in result["memories"]:
                        memory = self._dict_to_memory(memory_dict)
                        all_results.append((memory, memory_dict.get("similarity", 0.5)))
            except Exception as e:
                self.logger.error(f"Search failed in {memory_type.value} colony: {e}")

        # Sort by similarity and limit
        all_results.sort(key=lambda x: x[1], reverse=True)
        return [memory for memory, _ in all_results[:limit]]

    async def update_memory_importance(self, memory_id: str, new_importance: float):
        """Update the importance score of a memory."""
        memory = await self.retrieve_memory(memory_id)
        if not memory:
            raise ValueError(f"Memory {memory_id} not found")

        old_importance = memory.importance
        memory.importance = max(0.0, min(1.0, new_importance))

        # Update in colony
        colony = self.memory_colonies[memory.memory_type]
        update_task = {
            "type": "update_memory",
            "memory_id": memory_id,
            "updates": {"importance": memory.importance},
        }

        await colony.execute_task(f"update-{memory_id}", update_task)

        # Update state type if importance changed significantly
        if abs(old_importance - new_importance) > 0.3:
            await self.state_manager.set(
                f"memory:{memory_id}",
                memory.to_dict(),
                self._get_state_type(memory.importance),
            )

    async def forget_memory(self, memory_id: str):
        """Remove a memory from the distributed system."""
        if memory_id not in self.memory_index:
            return

        memory_type, colony_id = self.memory_index[memory_id]
        colony = self.memory_colonies[memory_type]

        # Remove from colony
        forget_task = {"type": "forget_memory", "memory_id": memory_id}

        await colony.execute_task(f"forget-{memory_id}", forget_task)

        # Remove from index and state manager
        del self.memory_index[memory_id]
        await self.state_manager.delete(f"memory:{memory_id}")

        # Invalidate similarity cache
        self._invalidate_similarity_cache(memory_type)

        self.logger.info(f"Forgot memory {memory_id}")

    async def consolidate_memories(self, time_window: timedelta = timedelta(days=1)):
        """
        Consolidate memories by merging similar ones and updating importance.
        This helps with memory efficiency and creates stronger associations.
        """
        self.logger.info(f"Starting memory consolidation for window: {time_window}")

        cutoff_time = datetime.now(timezone.utc) - time_window
        consolidation_tasks = []

        for memory_type, colony in self.memory_colonies.items():
            task = {
                "type": "consolidate_memories",
                "cutoff_time": cutoff_time.isoformat(),
                "similarity_threshold": 0.85,
                "min_importance": 0.3,
            }

            consolidation_tasks.append(colony.execute_task(f"consolidate-{memory_type.value}", task))

        # Wait for all consolidations to complete
        results = await asyncio.gather(*consolidation_tasks, return_exceptions=True)

        consolidated_count = 0
        for result in results:
            if isinstance(result, dict) and result.get("consolidated_count"):
                consolidated_count += result["consolidated_count"]

        self.logger.info(f"Memory consolidation complete. Consolidated {consolidated_count} memories")
        return consolidated_count

    async def get_memory_statistics(self) -> dict[str, Any]:
        """Get statistics about the distributed memory system."""
        stats = {
            "total_memories": len(self.memory_index),
            "by_type": {},
            "colony_health": self.colony_health.copy(),
            "cache_size": len(self.similarity_cache),
            "state_manager_stats": await self.state_manager.get_stats(),
        }

        # Count memories by type
        for memory_type in MemoryType:
            count = sum(1 for mt, _ in self.memory_index.values() if mt == memory_type)
            stats["by_type"][memory_type.value] = count

        # Get colony-specific stats
        for memory_type, colony in self.memory_colonies.items():
            try:
                colony_stats = await colony.get_statistics()
                stats[f"{memory_type.value}_colony"] = colony_stats
            except Exception as e:
                self.logger.error(f"Failed to get stats for {memory_type.value} colony: {e}")

        return stats

    def _generate_memory_id(self, content: dict[str, Any], memory_type: MemoryType) -> str:
        """Generate a unique ID for a memory."""
        content_str = json.dumps(content, sort_keys=True)
        type_str = memory_type.value
        timestamp = datetime.now(timezone.utc).isoformat()

        hash_input = f"{content_str}:{type_str}:{timestamp}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]

    async def _generate_embeddings(self, content: dict[str, Any]) -> np.ndarray:
        """Generate embeddings for memory content (placeholder)."""
        # In a real implementation, this would use a proper embedding model
        # For now, create a simple hash-based embedding
        content_str = json.dumps(content, sort_keys=True)
        hash_bytes = hashlib.sha256(content_str.encode()).digest()

        # Convert to normalized float array
        embedding = np.frombuffer(hash_bytes, dtype=np.uint8).astype(np.float32)
        embedding = embedding / np.linalg.norm(embedding)

        return embedding[:128]  # Use first 128 dimensions

    def _get_replication_factor(self, importance: float) -> int:
        """Determine replication factor based on importance."""
        if importance > 0.9:
            return 3
        elif importance > 0.7:
            return 2
        else:
            return 1

    def _get_state_type(self, importance: float) -> StateType:
        """Map importance to state type for caching."""
        if importance > 0.8:
            return StateType.HOT
        elif importance > 0.5:
            return StateType.WARM
        else:
            return StateType.COLD

    def _dict_to_memory(self, data: dict[str, Any]) -> DistributedMemory:
        """Convert dictionary to DistributedMemory object."""
        memory = DistributedMemory(
            memory_id=data["memory_id"],
            memory_type=MemoryType(data["memory_type"]),
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            importance=data.get("importance", 0.5),
            access_count=data.get("access_count", 0),
            last_accessed=(datetime.fromisoformat(data["last_accessed"]) if data.get("last_accessed") else None),
            colony_id=data.get("colony_id"),
            tags=data.get("tags", []),
        )

        if data.get("embeddings"):
            memory.embeddings = np.array(data["embeddings"])

        return memory

    def _invalidate_similarity_cache(self, memory_type: MemoryType):
        """Invalidate similarity cache for a memory type."""
        keys_to_remove = [k for k in self.similarity_cache if k.startswith(memory_type.value)]
        for key in keys_to_remove:
            del self.similarity_cache[key]

    async def _load_memory_index(self):
        """Load memory index from persistent storage."""
        # In a real implementation, this would load from the event store
        # For now, we'll rebuild it by querying colonies
        self.logger.info("Loading memory index...")

        for memory_type, colony in self.memory_colonies.items():
            list_task = {"type": "list_memories", "fields": ["memory_id", "colony_id"]}

            result = await colony.execute_task(f"list-{memory_type.value}", list_task)

            if result.get("status") == "completed" and result.get("memories"):
                for memory_info in result["memories"]:
                    memory_id = memory_info["memory_id"]
                    self.memory_index[memory_id] = (
                        memory_type,
                        memory_info["colony_id"],
                    )

        self.logger.info(f"Loaded {len(self.memory_index)} memories into index")


# Example usage
async def demo_distributed_memory():
    """Demonstrate the distributed memory system."""

    # Initialize system
    memory_system = DistributedMemorySystem("demo-memory")
    await memory_system.initialize()

    try:
        # Store different types of memories

        # Episodic memory
        episodic_id = await memory_system.store_memory(
            content={
                "event": "First conversation with user",
                "participants": ["user", "lukhas"],
                "emotional_context": {"excitement": 0.8, "curiosity": 0.9},
                "location": "virtual_space",
            },
            memory_type=MemoryType.EPISODIC,
            importance=0.8,
            tags=["first_contact", "milestone"],
        )
        print(f"Stored episodic memory: {episodic_id}")

        # Semantic memory
        semantic_id = await memory_system.store_memory(
            content={
                "concept": "consciousness",
                "definition": "The state of being aware of and able to think about one's existence",
                "related_concepts": ["awareness", "self-reflection", "cognition"],
            },
            memory_type=MemoryType.SEMANTIC,
            importance=0.9,
            tags=["philosophy", "core_concept"],
        )
        print(f"Stored semantic memory: {semantic_id}")

        # Procedural memory
        procedural_id = await memory_system.store_memory(
            content={
                "skill": "pattern_recognition",
                "steps": ["observe", "identify_features", "compare", "classify"],
                "success_rate": 0.85,
            },
            memory_type=MemoryType.PROCEDURAL,
            importance=0.7,
            tags=["skill", "cognitive_ability"],
        )
        print(f"Stored procedural memory: {procedural_id}")

        # Search for memories
        search_results = await memory_system.search_memories(
            query={"text": "consciousness awareness"},
            memory_types=[MemoryType.EPISODIC, MemoryType.SEMANTIC],
            limit=5,
        )

        print("\nSearch results for 'consciousness awareness':")
        for memory in search_results:
            print(f"- {memory.memory_id}: {memory.memory_type.value} - {memory.tags}")

        # Get system statistics
        stats = await memory_system.get_memory_statistics()
        print("\nMemory System Statistics:")
        print(f"Total memories: {stats['total_memories']}")
        print(f"By type: {stats['by_type']}")

        # Consolidate memories
        consolidated = await memory_system.consolidate_memories(timedelta(hours=1))
        print(f"\nConsolidated {consolidated} memories")

    finally:
        # Cleanup
        await memory_system.shutdown()


if __name__ == "__main__":
    asyncio.run(demo_distributed_memory())
