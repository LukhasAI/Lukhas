"""

#TAG:consciousness
#TAG:reflection
#TAG:neuroplastic
#TAG:colony


══════════════════════════════════════════════════════════════════════════════════
║ 🚀 LUKHAS AI - ══════════════════════════════════════════════════════════════════════════════════
║ Enhanced memory system with intelligent optimization
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: distributed_state_manager.py
║ Path: memory/distributed_state_manager.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Development Team
╠══════════════════════════════════════════════════════════════════════════════════
║                             ◊ POETIC ESSENCE ◊
║
║ ║ 🧠 LUKHAS AI - DISTRIBUTED STATE MANAGEMENT SYSTEM
║ ║ Combines event-sourced durability with distributed in-memory performance
║ ║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
║ ╠══════════════════════════════════════════════════════════════════════════════════
║ ║ MODULE: DISTRIBUTED STATE MANAGER
║ ║ DESCRIPTION: A sophisticated orchestration of memory in the digital realm
║ ╠══════════════════════════════════════════════════════════════════════════════════
║ ║ In the vast expanse of the digital cosmos, where ephemeral data flutters
║ ║ like autumn leaves in the winds of change, the Distributed State Manager emerges
║ ║ as a steadfast guardian, holding the ephemeral threads of existence in a tapestry
║ ║ woven from the finest fibers of event-sourced durability. Each data point,
║ ║ akin to a star in the night sky, is anchored in the celestial embrace of memory,
║ ║ ensuring that every flicker of information is not lost to the void, but rather,
║ ║ cherished and preserved for the seekers of knowledge and truth.
║ ║ This module serves as a bridge—an ethereal conduit—between the transient
║
╠══════════════════════════════════════════════════════════════════════════════════
║ TECHNICAL FEATURES:
║ • Advanced memory system implementation
║ • Optimized performance with intelligent caching
║ • Comprehensive error handling and validation
║ • Integration with LUKHAS AI architecture
║ • Extensible design for future enhancements
║
║ ΛTAG: ΛLUKHAS, ΛMEMORY, ΛADVANCED, ΛPYTHON
╚══════════════════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from core.cluster_sharding import ShardManager
from core.common import get_logger
from core.event_sourcing import Event, EventStore, get_global_event_store

#!/usr/bin/env python3



# Set up logging
logging.basicConfig(level=logging.INFO)
logger = get_logger(__name__)


class StateType(Enum):
    """Types of state data for optimization"""

    HOT = "hot"  # Frequently accessed, keep in memory
    WARM = "warm"  # Occasionally accessed, cache with TTL
    COLD = "cold"  # Rarely accessed, fetch from event store


@dataclass
class StateEntry:
    """In-memory state entry with metadata"""

    key: str
    value: Any
    version: int
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 0
    state_type: StateType = StateType.WARM
    ttl: float | None = None  # Time to live in seconds

    def is_expired(self) -> bool:
        """Check if entry has expired"""
        if self.ttl is None:
            return False
        return time.time() - self.last_accessed > self.ttl

    def access(self):
        """Update access metadata"""
        self.last_accessed = time.time()
        self.access_count += 1


@dataclass
class StateSnapshot:
    """Snapshot of distributed state for recovery"""

    snapshot_id: str
    timestamp: float
    shard_states: dict[int, dict[str, StateEntry]]
    event_version: int
    metadata: dict[str, Any] = field(default_factory=dict)


class DistributedStateManager:
    """
    Hybrid state management combining event sourcing with distributed in-memory storage
    Provides durability through event log and performance through sharded memory
    """

    def __init__(
        self,
        node_id: str,
        num_shards: int = 16,
        event_store: EventStore | None = None,
        snapshot_interval: int = 1000,
        cache_ttl: float = 3600,  # 1 hour default TTL
    ):
        """
        Initialize distributed state manager

        Args:
            node_id: Unique identifier for this node
            num_shards: Number of shards for data distribution
            event_store: Event store for durability (uses global if not provided)
            snapshot_interval: Number of events between snapshots
            cache_ttl: Default time-to-live for cached entries
        """
        self.node_id = node_id
        self.num_shards = num_shards
        self.event_store = event_store or get_global_event_store()
        self.snapshot_interval = snapshot_interval
        self.default_cache_ttl = cache_ttl

        # Sharded in-memory storage
        self.shard_manager = ShardManager(num_shards)
        self.memory_shards: dict[int, dict[str, StateEntry]] = {
            i: {} for i in range(num_shards)
        }

        # Synchronization
        self.shard_locks = {i: threading.RLock() for i in range(num_shards)}
        self.event_counter = 0
        self.last_snapshot_version = 0

        # Performance tracking
        self.metrics = {
            "cache_hits": 0,
            "cache_misses": 0,
            "evictions": 0,
            "snapshots": 0,
        }

        # Background tasks
        self._running = True
        self._background_tasks = []
        self._start_background_tasks()

        # Restore state from event store
        self._restore_state()

        logger.info(
            f"Distributed state manager initialized: node={node_id}, shards={num_shards}"
        )

    def _get_shard_id(self, key: str) -> int:
        """Calculate shard ID for a given key"""
        hash_value = int(hashlib.sha256(key.encode()).hexdigest(), 16)  # Changed from MD5 for security
        return hash_value % self.num_shards

    def _start_background_tasks(self):
        """Start background maintenance tasks"""
        # TTL cleanup task
        cleanup_task = threading.Thread(target=self._ttl_cleanup_loop, daemon=True)
        cleanup_task.start()
        self._background_tasks.append(cleanup_task)

        # Snapshot task
        snapshot_task = threading.Thread(target=self._snapshot_loop, daemon=True)
        snapshot_task.start()
        self._background_tasks.append(snapshot_task)

        # Access pattern analysis task
        analysis_task = threading.Thread(
            target=self._analyze_access_patterns, daemon=True
        )
        analysis_task.start()
        self._background_tasks.append(analysis_task)

    def _ttl_cleanup_loop(self):
        """Background task to clean up expired entries"""
        while self._running:
            try:
                time.sleep(60)  # Run every minute
                self._cleanup_expired_entries()
            except Exception as e:
                logger.error(f"Error in TTL cleanup: {e}")

    def _cleanup_expired_entries(self):
        """Remove expired entries from memory"""
        total_evicted = 0

        for shard_id in range(self.num_shards):
            with self.shard_locks[shard_id]:
                shard = self.memory_shards[shard_id]
                expired_keys = [
                    key for key, entry in shard.items() if entry.is_expired()
                ]

                for key in expired_keys:
                    del shard[key]
                    total_evicted += 1

        if total_evicted > 0:
            self.metrics["evictions"] += total_evicted
            logger.debug(f"Evicted {total_evicted} expired entries")

    def _snapshot_loop(self):
        """Background task to create periodic snapshots"""
        while self._running:
            try:
                time.sleep(300)  # Check every 5 minutes
                if (
                    self.event_counter - self.last_snapshot_version
                    >= self.snapshot_interval
                ):
                    self._create_snapshot()
            except Exception as e:
                logger.error(f"Error in snapshot creation: {e}")

    def _analyze_access_patterns(self):
        """Analyze access patterns and optimize state types"""
        while self._running:
            try:
                time.sleep(600)  # Analyze every 10 minutes
                self._optimize_state_types()
            except Exception as e:
                logger.error(f"Error in access pattern analysis: {e}")

    def _optimize_state_types(self):
        """Optimize state types based on access patterns"""
        current_time = time.time()

        for shard_id in range(self.num_shards):
            with self.shard_locks[shard_id]:
                shard = self.memory_shards[shard_id]

                for entry in shard.values():
                    # Calculate access frequency
                    age = current_time - entry.last_accessed
                    frequency = entry.access_count / max(age, 1)

                    # Update state type based on frequency
                    if frequency > 0.1:  # More than once per 10 seconds
                        entry.state_type = StateType.HOT
                        entry.ttl = None  # No expiration for hot data
                    elif frequency > 0.001:  # More than once per 1000 seconds
                        entry.state_type = StateType.WARM
                        entry.ttl = self.default_cache_ttl
                    else:
                        entry.state_type = StateType.COLD
                        entry.ttl = 300  # 5 minute TTL for cold data

    def set(
        self,
        key: str,
        value: Any,
        state_type: StateType = StateType.WARM,
        ttl: float | None = None,
        correlation_id: str | None = None,
    ) -> bool:
        """
        Set a value in distributed state

        Args:
            key: State key
            value: State value
            state_type: Type of state for optimization
            ttl: Time-to-live in seconds
            correlation_id: Correlation ID for distributed tracing

        Returns:
            True if successful
        """
        shard_id = self._get_shard_id(key)

        # Create event for durability
        event = Event(
            event_id=str(uuid.uuid4()),
            event_type="StateSet",
            aggregate_id=f"state_{self.node_id}",
            data={
                "key": key,
                "value": value,
                "state_type": state_type.value,
                "ttl": ttl,
            },
            metadata={
                "node_id": self.node_id,
                "shard_id": shard_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            timestamp=time.time(),
            version=self.event_counter + 1,
            correlation_id=correlation_id,
        )

        # Store in event log first for durability
        if not self.event_store.append_event(event):
            logger.error(f"Failed to append event for key: {key}")
            return False

        # Update in-memory state
        with self.shard_locks[shard_id]:
            entry = StateEntry(
                key=key,
                value=value,
                version=event.version,
                state_type=state_type,
                ttl=ttl
                or (self.default_cache_ttl if state_type != StateType.HOT else None),
            )
            self.memory_shards[shard_id][key] = entry
            self.event_counter = event.version

        logger.debug(f"Set state: key={key}, shard={shard_id}, type={state_type.value}")
        return True

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from distributed state

        Args:
            key: State key
            default: Default value if not found

        Returns:
            State value or default
        """
        shard_id = self._get_shard_id(key)

        # Try to get from memory first
        with self.shard_locks[shard_id]:
            entry = self.memory_shards[shard_id].get(key)

            if entry and not entry.is_expired():
                entry.access()
                self.metrics["cache_hits"] += 1
                return entry.value

        # Cache miss - try to restore from event store
        self.metrics["cache_misses"] += 1
        value = self._restore_key_from_events(key)

        if value is not None:
            # Cache the restored value
            self.set(key, value, StateType.WARM)
            return value

        return default

    def delete(self, key: str, correlation_id: str | None = None) -> bool:
        """
        Delete a key from distributed state

        Args:
            key: State key to delete
            correlation_id: Correlation ID for distributed tracing

        Returns:
            True if successful
        """
        shard_id = self._get_shard_id(key)

        # Create delete event
        event = Event(
            event_id=str(uuid.uuid4()),
            event_type="StateDelete",
            aggregate_id=f"state_{self.node_id}",
            data={"key": key},
            metadata={
                "node_id": self.node_id,
                "shard_id": shard_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            timestamp=time.time(),
            version=self.event_counter + 1,
            correlation_id=correlation_id,
        )

        # Store in event log
        if not self.event_store.append_event(event):
            return False

        # Remove from memory
        with self.shard_locks[shard_id]:
            if key in self.memory_shards[shard_id]:
                del self.memory_shards[shard_id][key]
            self.event_counter = event.version

        return True

    def get_shard_keys(self, shard_id: int) -> list[str]:
        """Get all keys in a specific shard"""
        with self.shard_locks[shard_id]:
            return list(self.memory_shards[shard_id].keys())

    def get_shard_stats(self, shard_id: int) -> dict[str, Any]:
        """Get statistics for a specific shard"""
        with self.shard_locks[shard_id]:
            shard = self.memory_shards[shard_id]

            hot_count = sum(1 for e in shard.values() if e.state_type == StateType.HOT)
            warm_count = sum(
                1 for e in shard.values() if e.state_type == StateType.WARM
            )
            cold_count = sum(
                1 for e in shard.values() if e.state_type == StateType.COLD
            )

            return {
                "total_keys": len(shard),
                "hot_keys": hot_count,
                "warm_keys": warm_count,
                "cold_keys": cold_count,
                "memory_usage": sum(len(str(e.value)) for e in shard.values()),
            }

    def get_global_stats(self) -> dict[str, Any]:
        """Get global statistics across all shards"""
        stats = {
            "node_id": self.node_id,
            "num_shards": self.num_shards,
            "event_count": self.event_counter,
            "metrics": self.metrics.copy(),
            "shards": {},
        }

        total_keys = 0
        for shard_id in range(self.num_shards):
            shard_stats = self.get_shard_stats(shard_id)
            stats["shards"][shard_id] = shard_stats
            total_keys += shard_stats["total_keys"]

        stats["total_keys"] = total_keys
        stats["cache_hit_rate"] = self.metrics["cache_hits"] / max(
            self.metrics["cache_hits"] + self.metrics["cache_misses"], 1
        )

        return stats

    def _create_snapshot(self):
        """Create a snapshot of current state"""
        snapshot = StateSnapshot(
            snapshot_id=str(uuid.uuid4()),
            timestamp=time.time(),
            shard_states={},
            event_version=self.event_counter,
            metadata={
                "node_id": self.node_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        # Copy all shard states
        for shard_id in range(self.num_shards):
            with self.shard_locks[shard_id]:
                snapshot.shard_states[shard_id] = dict(
                    self.memory_shards[shard_id].items()
                )

        # Store snapshot as special event
        event = Event(
            event_id=snapshot.snapshot_id,
            event_type="StateSnapshot",
            aggregate_id=f"state_{self.node_id}",
            data=asdict(snapshot),
            metadata={"compressed": False},  # Could add compression
            timestamp=snapshot.timestamp,
            version=self.event_counter,
            correlation_id=None,
        )

        if self.event_store.append_event(event):
            self.last_snapshot_version = self.event_counter
            self.metrics["snapshots"] += 1
            logger.info(f"Created snapshot at version {self.event_counter}")
        else:
            logger.error("Failed to store snapshot")

    def _restore_state(self):
        """Restore state from event store on startup"""
        logger.info("Restoring state from event store...")

        # Get all events for this node
        events = self.event_store.get_events_for_aggregate(f"state_{self.node_id}")

        # Find latest snapshot
        latest_snapshot = None
        for event in reversed(events):
            if event.event_type == "StateSnapshot":
                latest_snapshot = event
                break

        # Restore from snapshot if available
        if latest_snapshot:
            self._restore_from_snapshot(latest_snapshot)
            # Replay events after snapshot
            events = [e for e in events if e.version > latest_snapshot.version]

        # Replay remaining events
        for event in events:
            self._apply_state_event(event)

        logger.info(f"State restored: {self.event_counter} events processed")

    def _restore_from_snapshot(self, snapshot_event: Event):
        """Restore state from a snapshot event"""
        snapshot_data = snapshot_event.data

        # Restore shard states
        for shard_id_str, shard_entries in snapshot_data.get(
            "shard_states", {}
        ).items():
            shard_id = int(shard_id_str)
            with self.shard_locks[shard_id]:
                self.memory_shards[shard_id] = {
                    key: StateEntry(**entry) for key, entry in shard_entries.items()
                }

        self.event_counter = snapshot_data["event_version"]
        self.last_snapshot_version = self.event_counter
        logger.info(f"Restored from snapshot version {self.event_counter}")

    def _apply_state_event(self, event: Event):
        """Apply a state event during recovery"""
        if event.event_type == "StateSet":
            key = event.data["key"]
            shard_id = self._get_shard_id(key)

            with self.shard_locks[shard_id]:
                entry = StateEntry(
                    key=key,
                    value=event.data["value"],
                    version=event.version,
                    state_type=StateType(event.data.get("state_type", "warm")),
                    ttl=event.data.get("ttl"),
                )
                self.memory_shards[shard_id][key] = entry

        elif event.event_type == "StateDelete":
            key = event.data["key"]
            shard_id = self._get_shard_id(key)

            with self.shard_locks[shard_id]:
                self.memory_shards[shard_id].pop(key, None)

        self.event_counter = max(self.event_counter, event.version)

    def _restore_key_from_events(self, key: str) -> Any | None:
        """Restore a specific key by replaying events"""
        events = self.event_store.get_events_for_aggregate(f"state_{self.node_id}")

        value = None
        for event in events:
            if event.event_type == "StateSet" and event.data.get("key") == key:
                value = event.data["value"]
            elif event.event_type == "StateDelete" and event.data.get("key") == key:
                value = None

        return value

    def shutdown(self):
        """Gracefully shutdown the state manager"""
        logger.info("Shutting down distributed state manager...")

        # Stop background tasks
        self._running = False
        for task in self._background_tasks:
            task.join(timeout=5)

        # Create final snapshot
        self._create_snapshot()

        logger.info("Distributed state manager shutdown complete")


class MultiNodeStateManager:
    """
    Coordinator for multiple distributed state managers
    Provides cross-node state queries and replication
    """

    def __init__(self, node_configs: list[dict[str, Any]]):
        """
        Initialize multi-node state manager

        Args:
            node_configs: List of node configurations
        """
        self.nodes: dict[str, DistributedStateManager] = {}

        for config in node_configs:
            node_id = config["node_id"]
            manager = DistributedStateManager(
                node_id=node_id,
                num_shards=config.get("num_shards", 16),
                snapshot_interval=config.get("snapshot_interval", 1000),
            )
            self.nodes[node_id] = manager

        logger.info(f"Multi-node manager initialized with {len(self.nodes)} nodes")

    def get_node(self, key: str) -> DistributedStateManager:
        """Get the node responsible for a key using consistent hashing"""
        # Simple implementation - could use more sophisticated routing
        node_ids = sorted(self.nodes.keys())
        index = hash(key) % len(node_ids)
        return self.nodes[node_ids[index]]

    def set(self, key: str, value: Any, **kwargs) -> bool:
        """Set value on appropriate node"""
        node = self.get_node(key)
        return node.set(key, value, **kwargs)

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from appropriate node"""
        node = self.get_node(key)
        return node.get(key, default)

    def get_cluster_stats(self) -> dict[str, Any]:
        """Get statistics for entire cluster"""
        stats = {
            "nodes": {},
            "total_keys": 0,
            "total_events": 0,
        }

        for node_id, node in self.nodes.items():
            node_stats = node.get_global_stats()
            stats["nodes"][node_id] = node_stats
            stats["total_keys"] += node_stats["total_keys"]
            stats["total_events"] += node_stats["event_count"]

        return stats

    def shutdown_all(self):
        """Shutdown all nodes"""
        for node in self.nodes.values():
            node.shutdown()


# Demo usage
if __name__ == "__main__":
    # Single node example
    manager = DistributedStateManager("node-001", num_shards=4)

    # Set some values with different state types
    manager.set("user:123", {"name": "Alice", "score": 100}, StateType.HOT)
    manager.set("session:abc", {"active": True}, StateType.WARM, ttl=1800)
    manager.set("cache:xyz", {"data": "temporary"}, StateType.COLD, ttl=300)

    # Get values
    print("User data:", manager.get("user:123"))
    print("Session data:", manager.get("session:abc"))

    # Show statistics
    print("\nGlobal stats:", json.dumps(manager.get_global_stats(), indent=2))

    # Multi-node example
    multi_manager = MultiNodeStateManager(
        [
            {"node_id": "node-001", "num_shards": 4},
            {"node_id": "node-002", "num_shards": 4},
            {"node_id": "node-003", "num_shards": 4},
        ]
    )

    # Distribute some data
    for i in range(10):
        multi_manager.set(f"key_{i}", f"value_{i}")

    print("\nCluster stats:", json.dumps(multi_manager.get_cluster_stats(), indent=2))

    # Cleanup
    manager.shutdown()
    multi_manager.shutdown_all()
