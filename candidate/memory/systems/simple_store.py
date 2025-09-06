import logging
logger = logging.getLogger(__name__)
"""
CRITICAL FILE - DO NOT MODIFY WITHOUT APPROVAL
lukhas AI System - Core Memory Component
Path: core/memory/simple_store.py
Created: 2025-06-20
Author: lukhas AI Team
This file is part of the LUKHAS (Logical Unified Knowledge Hyper-Adaptable System)
Advanced Cognitive Architecture for Artificial General Intelligence
Copyright (c) 2025 lukhas AI Research. All rights reserved.
Licensed under the lukhas Core License - see LICENSE.md for details.
TAGS: [CRITICAL, KeyFile, Memory]
DEPENDENCIES:
  - core/memory/memory_manager.py
  - core/identity/identity_manager.py
"""

import asyncio
import contextlib
import gzip
import json
import mmap
import time
import uuid
from collections import OrderedDict
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from candidate.core.common import get_logger

logger = get_logger(__name__)


class MemoryType(Enum):
    """Core memory types (simplified from 8 to 3)"""

    EPISODIC = "episodic"  # Event-based memories
    SEMANTIC = "semantic"  # Knowledge and concepts
    EMOTIONAL = "emotional"  # Emotional experiences


class MemoryPriority(Enum):
    """Memory priority levels (simplified from 5 to 4)"""

    CRITICAL = "critical"  # Never delete
    HIGH = "high"  # Important memories
    MEDIUM = "medium"  # Standard memories
    LOW = "low"  # Can be pruned


@dataclass
class MemoryEntry:
    """Simplified memory entry structure"""

    id: str
    user_id: str
    content: dict[str, Any]
    memory_type: MemoryType
    priority: MemoryPriority
    timestamp: float
    last_accessed: float
    access_count: int = 0
    compressed: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "content": self.content,
            "memory_type": self.memory_type.value,
            "priority": self.priority.value,
            "timestamp": self.timestamp,
            "last_accessed": self.last_accessed,
            "access_count": self.access_count,
            "compressed": self.compressed,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MemoryEntry":
        """Create from dictionary"""
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            content=data["content"],
            memory_type=MemoryType(data["memory_type"]),
            priority=MemoryPriority(data["priority"]),
            timestamp=data["timestamp"],
            last_accessed=data["last_accessed"],
            access_count=data.get("access_count", 0),
            compressed=data.get("compressed", False),
        )


@dataclass
class MemoryConfig:
    """Unified memory manager configuration"""

    # Storage settings
    max_memories_per_user: int = 10000
    storage_path: str = "memory_store"
    enable_compression: bool = True
    compression_threshold: int = 1024  # bytes

    # TTL settings (24-hour default as recommended)
    default_ttl_hours: int = 24
    critical_ttl_days: int = 365

    # Performance settings
    lru_cache_size: int = 1000
    enable_mmap: bool = True
    parallel_queries: bool = True

    # Garbage collection
    gc_interval_minutes: int = 60
    gc_threshold_percent: float = 0.8

    # Privacy compliance
    enable_user_data_control: bool = True
    auto_anonymize_old_data: bool = True
    anonymize_after_days: int = 30


class UnifiedMemoryManager:
    """
    Production-ready unified memory manager.

    Replaces quantum/blockchain complexity with:
    - LRU cache with TTL (24-hour default)
    - zstd compression for storage efficiency
    - user_id → timestamp → message → vector mapping
    - Parallel querying (working/episodic/semantic)
    - GDPR-compliant user data control
    - Memory garbage collection
    """

    def __init__(self, config: Optional[MemoryConfig] = None):
        self.config = config or MemoryConfig()

        # Storage setup
        self.storage_path = Path(self.config.storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # LRU cache for fast access (user_id -> OrderedDict of memories)
        self.lru_cache: dict[str, OrderedDict[str, MemoryEntry]] = {}
        self.cache_access_times: dict[str, float] = {}

        # Memory indices for fast querying
        self.type_index: dict[MemoryType, dict[str, list[str]]] = {memory_type: {} for memory_type in MemoryType}
        self.priority_index: dict[MemoryPriority, dict[str, list[str]]] = {priority: {} for priority in MemoryPriority}

        # Shared memory mapping for performance (if enabled)
        self.mmap_files: dict[str, mmap.mmap] = {}

        # Background tasks
        self._gc_task: Optional[asyncio.Task] = None
        self._running = False

        # Compression (using gzip for now, can upgrade to zstd later)
        self.enable_compression = self.config.enable_compression

        logger.info(f"Unified memory manager initialized: {self.storage_path}")

    async def start(self) -> bool:
        """Start the memory manager"""
        try:
            self._running = True

            # Load existing memories
            await self._load_existing_memories()

            # Start garbage collection if enabled
            if self.config.gc_interval_minutes > 0:
                self._gc_task = asyncio.create_task(self._garbage_collection_loop())

            logger.info("Unified memory manager started")
            return True

        except Exception as e:
            logger.error(f"Failed to start memory manager: {e}")
            return False

    async def stop(self) -> bool:
        """Stop the memory manager"""
        try:
            self._running = False

            # Stop garbage collection
            if self._gc_task:
                self._gc_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await self._gc_task

            # Save critical memories
            await self._save_critical_memories()

            # Close mmap files
            for mmap_file in self.mmap_files.values():
                mmap_file.close()
            self.mmap_files.clear()

            logger.info("Unified memory manager stopped")
            return True

        except Exception as e:
            logger.error(f"Failed to stop memory manager: {e}")
            return False

    async def store_memory(
        self,
        user_id: str,
        content: dict[str, Any],
        memory_type: MemoryType = MemoryType.EPISODIC,
        priority: MemoryPriority = MemoryPriority.MEDIUM,
        memory_id: Optional[str] = None,
    ) -> str:
        """
        Store a memory entry.

        Args:
            user_id: User identifier
            content: Memory content
            memory_type: Type of memory
            priority: Memory priority
            memory_id: Optional custom memory ID

        Returns:
            Memory ID
        """
        try:
            # Generate memory ID if not provided
            if memory_id is None:
                memory_id = f"{user_id}_{int(time.time())}_{uuid.uuid4().hex[:8]}"

            # Create memory entry
            now = time.time()
            memory = MemoryEntry(
                id=memory_id,
                user_id=user_id,
                content=content,
                memory_type=memory_type,
                priority=priority,
                timestamp=now,
                last_accessed=now,
            )

            # Compress if enabled and content is large enough
            if self.config.enable_compression and len(json.dumps(content)) > self.config.compression_threshold:
                memory.content = await self._compress_content(content)
                memory.compressed = True

            # Add to cache
            await self._add_to_cache(memory)

            # Update indices
            await self._update_indices(memory, add=True)

            # Persist to disk for critical memories
            if priority == MemoryPriority.CRITICAL:
                await self._persist_memory(memory)

            logger.debug(f"Stored memory {memory_id} for user {user_id}")
            return memory_id

        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            raise

    async def retrieve_memory(
        self,
        user_id: str,
        memory_id: Optional[str] = None,
        memory_type: Optional[MemoryType] = None,
        limit: int = 20,
        include_old: bool = False,
    ) -> list[MemoryEntry]:
        """
        Retrieve memories for a user.

        Args:
            user_id: User identifier
            memory_id: Specific memory ID (if retrieving single memory)
            memory_type: Filter by memory type
            limit: Maximum number of memories to return
            include_old: Include memories past TTL

        Returns:
            List of memory entries
        """
        try:
            if memory_id:
                # Retrieve specific memory
                memory = await self._get_memory_by_id(user_id, memory_id)
                return [memory] if memory else []

            # Get user memories from cache
            user_memories = self.lru_cache.get(user_id, OrderedDict())

            # Filter by type if specified
            if memory_type:
                type_memory_ids = self.type_index.get(memory_type, {}).get(user_id, [])
                user_memories = OrderedDict(
                    (mid, memory) for mid, memory in user_memories.items() if mid in type_memory_ids
                )

            # Filter by TTL unless including old memories
            if not include_old:
                current_time = time.time()
                valid_memories = OrderedDict()
                for mid, memory in user_memories.items():
                    if await self._is_memory_valid(memory, current_time):
                        valid_memories[mid] = memory
                user_memories = valid_memories

            # Sort by last_accessed (most recent first) and limit
            sorted_memories = sorted(user_memories.values(), key=lambda m: m.last_accessed, reverse=True)[:limit]

            # Update access times
            for memory in sorted_memories:
                memory.last_accessed = time.time()
                memory.access_count += 1

            # Decompress if needed
            for memory in sorted_memories:
                if memory.compressed and isinstance(memory.content, bytes):
                    try:
                        memory.content = await self._decompress_content(memory.content)
                        memory.compressed = False
                    except Exception as decompress_error:
                        logger.error(f"Failed to decompress memory {memory.id}: {decompress_error}")
                        # Keep original content if decompression fails

            logger.debug(f"Retrieved {len(sorted_memories)} memories for user {user_id}")
            return sorted_memories

        except Exception as e:
            logger.error(f"Failed to retrieve memories: {e}")
            return []

    async def delete_user_memories(self, user_id: str, memory_ids: Optional[list[str]] = None) -> bool:
        """
        Delete memories for GDPR compliance.

        Args:
            user_id: User identifier
            memory_ids: Specific memory IDs to delete (if None, deletes all user memories)

        Returns:
            Success status
        """
        try:
            if memory_ids:
                # Delete specific memories
                user_memories = self.lru_cache.get(user_id, OrderedDict())
                for memory_id in memory_ids:
                    if memory_id in user_memories:
                        memory = user_memories.pop(memory_id)
                        await self._update_indices(memory, add=False)
                        await self._delete_persisted_memory(memory)
            else:
                # Delete all user memories
                user_memories = self.lru_cache.pop(user_id, OrderedDict())
                for memory in user_memories.values():
                    await self._update_indices(memory, add=False)
                    await self._delete_persisted_memory(memory)

                # Clean up user-specific indices
                for type_dict in self.type_index.values():
                    type_dict.pop(user_id, None)
                for priority_dict in self.priority_index.values():
                    priority_dict.pop(user_id, None)

            logger.info(f"Deleted memories for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete user memories: {e}")
            return False

    async def get_memory_stats(self, user_id: Optional[str] = None) -> dict[str, Any]:
        """Get memory usage statistics"""
        try:
            if user_id:
                # User-specific stats
                user_memories = self.lru_cache.get(user_id, OrderedDict())
                return {
                    "user_id": user_id,
                    "total_memories": len(user_memories),
                    "memory_types": {
                        mem_type.value: len([m for m in user_memories.values() if m.memory_type == mem_type])
                        for mem_type in MemoryType
                    },
                    "memory_priorities": {
                        priority.value: len([m for m in user_memories.values() if m.priority == priority])
                        for priority in MemoryPriority
                    },
                }
            else:
                # Global stats
                total_memories = sum(len(memories) for memories in self.lru_cache.values())
                return {
                    "total_users": len(self.lru_cache),
                    "total_memories": total_memories,
                    "cache_size": len(self.lru_cache),
                    "storage_path": str(self.storage_path),
                    "compression_enabled": self.config.enable_compression,
                }

        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            return {}

    # Private methods

    async def _add_to_cache(self, memory: MemoryEntry) -> None:
        """Add memory to LRU cache"""
        user_id = memory.user_id

        # Initialize user cache if needed
        if user_id not in self.lru_cache:
            self.lru_cache[user_id] = OrderedDict()

        user_cache = self.lru_cache[user_id]

        # Add memory (this moves it to end of OrderedDict)
        user_cache[memory.id] = memory
        user_cache.move_to_end(memory.id)

        # Enforce cache size limit
        while len(user_cache) > self.config.max_memories_per_user:
            # Remove oldest non-critical memory
            oldest_id, oldest_memory = user_cache.popitem(last=False)
            if oldest_memory.priority != MemoryPriority.CRITICAL:
                await self._update_indices(oldest_memory, add=False)
            else:
                # Keep critical memories, remove next oldest
                user_cache[oldest_id] = oldest_memory
                user_cache.move_to_end(oldest_id, last=False)

        # Update cache access time
        self.cache_access_times[user_id] = time.time()

    async def _update_indices(self, memory: MemoryEntry, add: bool) -> None:
        """Update memory indices for fast querying"""
        user_id = memory.user_id
        memory_id = memory.id

        # Update type index
        type_dict = self.type_index[memory.memory_type]
        if user_id not in type_dict:
            type_dict[user_id] = []

        if add:
            if memory_id not in type_dict[user_id]:
                type_dict[user_id].append(memory_id)
        else:
            if memory_id in type_dict[user_id]:
                type_dict[user_id].remove(memory_id)

        # Update priority index
        priority_dict = self.priority_index[memory.priority]
        if user_id not in priority_dict:
            priority_dict[user_id] = []

        if add:
            if memory_id not in priority_dict[user_id]:
                priority_dict[user_id].append(memory_id)
        else:
            if memory_id in priority_dict[user_id]:
                priority_dict[user_id].remove(memory_id)

    async def _compress_content(self, content: dict[str, Any]) -> bytes:
        """Compress memory content using gzip"""
        if not self.enable_compression:
            return content

        json_data = json.dumps(content).encode("utf-8")
        return gzip.compress(json_data)

    async def _decompress_content(self, compressed_content: bytes) -> dict[str, Any]:
        """Decompress memory content using gzip"""
        if not self.enable_compression or not isinstance(compressed_content, bytes):
            return compressed_content

        try:
            json_data = gzip.decompress(compressed_content)
            return json.loads(json_data.decode("utf-8"))
        except Exception as e:
            logger.error(f"Failed to decompress content: {e}")
            return {
                "error": "decompression_failed",
                "raw_data": str(compressed_content),
            }

    async def _is_memory_valid(self, memory: MemoryEntry, current_time: float) -> bool:
        """Check if memory is within TTL"""
        if memory.priority == MemoryPriority.CRITICAL:
            # Critical memories use longer TTL
            ttl_seconds = self.config.critical_ttl_days * 24 * 3600
        else:
            # Standard memories use default TTL
            ttl_seconds = self.config.default_ttl_hours * 3600

        return (current_time - memory.timestamp) < ttl_seconds

    async def _get_memory_by_id(self, user_id: str, memory_id: str) -> Optional[MemoryEntry]:
        """Get specific memory by ID"""
        user_memories = self.lru_cache.get(user_id, OrderedDict())
        memory = user_memories.get(memory_id)

        if memory:
            # Update access info
            memory.last_accessed = time.time()
            memory.access_count += 1
            user_memories.move_to_end(memory_id)

            # Decompress if needed
            if memory.compressed and isinstance(memory.content, bytes):
                try:
                    memory.content = await self._decompress_content(memory.content)
                    memory.compressed = False
                except Exception as decompress_error:
                    logger.error(f"Failed to decompress memory {memory.id}: {decompress_error}")
                    # Keep original content if decompression fails

        return memory

    async def _persist_memory(self, memory: MemoryEntry) -> None:
        """Persist critical memory to disk"""
        try:
            user_dir = self.storage_path / memory.user_id
            user_dir.mkdir(exist_ok=True)

            memory_file = user_dir / f"{memory.id}.json"

            # Create a serializable copy
            memory_dict = memory.to_dict()

            # Handle compressed content
            if memory.compressed and isinstance(memory.content, bytes):
                # Convert bytes to base64 for JSON serialization
                import base64

                memory_dict["content"] = base64.b64encode(memory.content).decode("utf-8")
                memory_dict["content_encoding"] = "base64_gzip"

            with open(memory_file, "w") as f:
                json.dump(memory_dict, f)

        except Exception as e:
            logger.error(f"Failed to persist memory {memory.id}: {e}")

    async def _delete_persisted_memory(self, memory: MemoryEntry) -> None:
        """Delete persisted memory file"""
        try:
            memory_file = self.storage_path / memory.user_id / f"{memory.id}.json"
            if memory_file.exists():
                memory_file.unlink()
        except Exception as e:
            logger.error(f"Failed to delete persisted memory {memory.id}: {e}")

    async def _load_existing_memories(self) -> None:
        """Load existing persisted memories"""
        try:
            for user_dir in self.storage_path.iterdir():
                if user_dir.is_dir():
                    for memory_file in user_dir.glob("*.json"):
                        try:
                            with open(memory_file) as f:
                                memory_data = json.load(f)

                            # Handle compressed content
                            if memory_data.get("content_encoding") == "base64_gzip":
                                import base64

                                memory_data["content"] = base64.b64decode(memory_data["content"])
                                memory_data["compressed"] = True
                                del memory_data["content_encoding"]

                            memory = MemoryEntry.from_dict(memory_data)
                            await self._add_to_cache(memory)
                            await self._update_indices(memory, add=True)

                        except Exception as e:
                            logger.error(f"Failed to load memory {memory_file}: {e}")

            logger.info(f"Loaded existing memories from {self.storage_path}")

        except Exception as e:
            logger.error(f"Failed to load existing memories: {e}")

    async def _save_critical_memories(self) -> None:
        """Save critical memories before shutdown"""
        try:
            for user_memories in self.lru_cache.values():
                for memory in user_memories.values():
                    if memory.priority == MemoryPriority.CRITICAL:
                        await self._persist_memory(memory)
        except Exception as e:
            logger.error(f"Failed to save critical memories: {e}")

    async def _garbage_collection_loop(self) -> None:
        """Background garbage collection for expired memories"""
        try:
            while self._running:
                await asyncio.sleep(self.config.gc_interval_minutes * 60)
                await self._run_garbage_collection()
        except asyncio.CancelledError:
            logger.info("Garbage collection stopped")
        except Exception as e:
            logger.error(f"Garbage collection error: {e}")

    async def _run_garbage_collection(self) -> None:
        """Run garbage collection to remove expired memories"""
        try:
            current_time = time.time()
            removed_count = 0

            for user_id, user_memories in list(self.lru_cache.items()):
                expired_ids = []

                for memory_id, memory in user_memories.items():
                    if not await self._is_memory_valid(memory, current_time):
                        expired_ids.append(memory_id)

                # Remove expired memories
                for memory_id in expired_ids:
                    memory = user_memories.pop(memory_id)
                    await self._update_indices(memory, add=False)
                    await self._delete_persisted_memory(memory)
                    removed_count += 1

                # Remove empty user caches
                if not user_memories:
                    del self.lru_cache[user_id]

            if removed_count > 0:
                logger.info(f"Garbage collection removed {removed_count} expired memories")

        except Exception as e:
            logger.error(f"Garbage collection failed: {e}")