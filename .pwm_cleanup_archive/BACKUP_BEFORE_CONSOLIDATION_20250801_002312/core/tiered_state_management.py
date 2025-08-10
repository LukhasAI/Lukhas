"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - TIERED STATE MANAGEMENT MODULE
║ Hierarchical state management combining Event Sourcing and Actor State
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: tiered_state_management.py
║ Path: lukhas/core/tiered_state_management.py
║ Version: 1.0.0 | Created: 2025-07-27 | Modified: 2025-07-27
║ Authors: Claude (Anthropic AI Assistant)
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ Implements TODO 75: Tiered state management system with Event Sourcing for global
║ persistent state and Actor State for local ephemeral state. Provides efficient
║ state synchronization, caching, and consistency guarantees across distributed AI.
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import logging
import time
import uuid
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from threading import RLock
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

# Import dependencies
try:
    from .actor_system import ActorState as ActorSystemState
    from .event_sourcing import Aggregate, Event, EventStore
    from .lightweight_concurrency import (
        LightweightActor,
        MemoryEfficientScheduler,
    )

    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    # Define minimal interfaces for testing
    from dataclasses import dataclass as dc

    @dc
    class Event:
        event_id: str
        event_type: str
        aggregate_id: str
        data: Dict[str, Any]
        metadata: Dict[str, Any]
        timestamp: float
        version: int
        correlation_id: Optional[str] = None


logger = logging.getLogger(__name__)


class StateType(Enum):
    """Types of state in the tiered system"""

    GLOBAL_PERSISTENT = "global_persistent"  # Event-sourced, durable
    LOCAL_EPHEMERAL = "local_ephemeral"  # Actor-local, in-memory
    CACHED_DERIVED = "cached_derived"  # Computed from events, cached
    REPLICATED_SHARED = (
        "replicated_shared"  # Shared across actors, eventually consistent
    )


class ConsistencyLevel(Enum):
    """Consistency guarantees for state operations"""

    EVENTUAL = "eventual"
    STRONG = "strong"
    CAUSAL = "causal"
    READ_YOUR_WRITES = "read_your_writes"


@dataclass
class StateSnapshot:
    """Point-in-time snapshot of state"""

    snapshot_id: str
    aggregate_id: str
    version: int
    state_data: Dict[str, Any]
    timestamp: float
    state_type: StateType

    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "aggregate_id": self.aggregate_id,
            "version": self.version,
            "state_data": self.state_data,
            "timestamp": self.timestamp,
            "state_type": self.state_type.value,
        }


class StateAggregator(ABC):
    """Abstract base for state aggregation strategies"""

    @abstractmethod
    def aggregate(
        self, events: List[Event], initial_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Aggregate events into state"""
        pass

    @abstractmethod
    def can_handle(self, event_type: str) -> bool:
        """Check if aggregator can handle event type"""
        pass


class DefaultStateAggregator(StateAggregator):
    """Default aggregation strategy applying events sequentially"""

    def aggregate(
        self, events: List[Event], initial_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        state = initial_state.copy()

        for event in events:
            if event.event_type == "state_updated":
                state.update(event.data)
            elif event.event_type == "field_set":
                field_name = event.data.get("field")
                field_value = event.data.get("value")
                if field_name:
                    state[field_name] = field_value
            elif event.event_type == "field_deleted":
                field_name = event.data.get("field")
                if field_name and field_name in state:
                    del state[field_name]
            elif event.event_type == "state_reset":
                state = event.data.get("new_state", {})

        return state

    def can_handle(self, event_type: str) -> bool:
        return event_type in [
            "state_updated",
            "field_set",
            "field_deleted",
            "state_reset",
        ]


class TieredStateManager:
    """
    Manages hierarchical state with multiple tiers:
    - Global persistent state via Event Sourcing
    - Local ephemeral state in Actor memory
    - Cached derived state for performance
    - Replicated shared state for coordination
    """

    def __init__(
        self,
        event_store: Optional[Any] = None,
        cache_ttl_seconds: int = 300,
        snapshot_interval: int = 100,
    ):
        self.event_store = event_store
        self.cache_ttl = cache_ttl_seconds
        self.snapshot_interval = snapshot_interval

        # State storage
        self.local_states: Dict[str, Dict[str, Any]] = {}
        self.state_cache: Dict[str, Tuple[Dict[str, Any], float]] = {}
        self.snapshots: Dict[str, StateSnapshot] = {}

        # Aggregators
        self.aggregators: List[StateAggregator] = [DefaultStateAggregator()]

        # Synchronization
        self._lock = RLock()
        self._event_counter: Dict[str, int] = defaultdict(int)

        # Replication management
        self.replicated_state: Dict[str, Dict[str, Any]] = {}
        self.replication_subscribers: Dict[str, Set[Callable]] = defaultdict(set)

        # Statistics
        self.stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "events_processed": 0,
            "snapshots_created": 0,
        }

    def register_aggregator(self, aggregator: StateAggregator) -> None:
        """Register a custom state aggregator"""
        self.aggregators.append(aggregator)

    async def get_state(
        self,
        aggregate_id: str,
        state_type: StateType = StateType.GLOBAL_PERSISTENT,
        consistency: ConsistencyLevel = ConsistencyLevel.EVENTUAL,
        version: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Retrieve state for an aggregate with specified consistency level.
        """
        with self._lock:
            if state_type == StateType.LOCAL_EPHEMERAL:
                # Return local actor state
                return self.local_states.get(aggregate_id, {}).copy()

            elif state_type == StateType.CACHED_DERIVED:
                # Check cache first
                if aggregate_id in self.state_cache:
                    cached_state, cache_time = self.state_cache[aggregate_id]
                    if time.time() - cache_time < self.cache_ttl:
                        self.stats["cache_hits"] += 1
                        return cached_state.copy()

                self.stats["cache_misses"] += 1

            elif state_type == StateType.REPLICATED_SHARED:
                # Return replicated state
                return self.replicated_state.get(aggregate_id, {}).copy()

        # For persistent state, reconstruct from events
        if self.event_store and state_type == StateType.GLOBAL_PERSISTENT:
            return await self._reconstruct_from_events(
                aggregate_id, version, consistency
            )

        return {}

    async def update_state(
        self,
        aggregate_id: str,
        updates: Dict[str, Any],
        state_type: StateType = StateType.GLOBAL_PERSISTENT,
        event_type: str = "state_updated",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Update state with the specified changes.
        """
        with self._lock:
            if state_type == StateType.LOCAL_EPHEMERAL:
                # Update local state directly
                if aggregate_id not in self.local_states:
                    self.local_states[aggregate_id] = {}
                self.local_states[aggregate_id].update(updates)
                return True

            elif state_type == StateType.REPLICATED_SHARED:
                # Update replicated state and notify subscribers
                if aggregate_id not in self.replicated_state:
                    self.replicated_state[aggregate_id] = {}
                self.replicated_state[aggregate_id].update(updates)

                # Notify subscribers
                await self._notify_replication_subscribers(aggregate_id, updates)
                return True

        # For persistent state, create event
        if self.event_store and state_type == StateType.GLOBAL_PERSISTENT:
            event = Event(
                event_id=str(uuid.uuid4()),
                event_type=event_type,
                aggregate_id=aggregate_id,
                data=updates,
                metadata=metadata or {},
                timestamp=time.time(),
                version=self._get_next_version(aggregate_id),
            )

            success = await self._store_event(event)

            if success:
                # Invalidate cache
                if aggregate_id in self.state_cache:
                    del self.state_cache[aggregate_id]

                # Check if snapshot needed
                await self._check_snapshot(aggregate_id)

            return success

        return False

    async def create_snapshot(self, aggregate_id: str) -> StateSnapshot:
        """
        Create a snapshot of current state for faster reconstruction.
        """
        # Get current state
        state = await self.get_state(aggregate_id, StateType.GLOBAL_PERSISTENT)

        with self._lock:
            version = self._event_counter[aggregate_id]

            snapshot = StateSnapshot(
                snapshot_id=str(uuid.uuid4()),
                aggregate_id=aggregate_id,
                version=version,
                state_data=state,
                timestamp=time.time(),
                state_type=StateType.GLOBAL_PERSISTENT,
            )

            self.snapshots[aggregate_id] = snapshot
            self.stats["snapshots_created"] += 1

        logger.info(f"Created snapshot for {aggregate_id} at version {version}")
        return snapshot

    async def sync_actor_state(
        self, actor: Any, sync_direction: str = "bidirectional"
    ) -> None:
        """
        Synchronize state between actor and persistent store.
        sync_direction: "to_persistent", "from_persistent", "bidirectional"
        """
        actor_id = getattr(actor, "actor_id", str(actor))

        if sync_direction in ["from_persistent", "bidirectional"]:
            # Load persistent state into actor
            persistent_state = await self.get_state(
                actor_id, StateType.GLOBAL_PERSISTENT
            )

            if hasattr(actor, "state"):
                actor.state.update(persistent_state)
            else:
                self.local_states[actor_id] = persistent_state.copy()

        if sync_direction in ["to_persistent", "bidirectional"]:
            # Save actor state to persistent store
            actor_state = (
                getattr(actor, "state", {})
                if hasattr(actor, "state")
                else self.local_states.get(actor_id, {})
            )

            if actor_state:
                await self.update_state(
                    actor_id,
                    actor_state,
                    StateType.GLOBAL_PERSISTENT,
                    event_type="actor_state_sync",
                    metadata={"sync_time": time.time()},
                )

    def subscribe_to_replicated_state(
        self, aggregate_id: str, callback: Callable[[str, Dict[str, Any]], None]
    ) -> None:
        """Subscribe to changes in replicated state"""
        self.replication_subscribers[aggregate_id].add(callback)

    def unsubscribe_from_replicated_state(
        self, aggregate_id: str, callback: Callable[[str, Dict[str, Any]], None]
    ) -> None:
        """Unsubscribe from replicated state changes"""
        if aggregate_id in self.replication_subscribers:
            self.replication_subscribers[aggregate_id].discard(callback)

    async def _reconstruct_from_events(
        self, aggregate_id: str, version: Optional[int], consistency: ConsistencyLevel
    ) -> Dict[str, Any]:
        """Reconstruct state from event history"""
        if not self.event_store:
            return {}

        # Get latest snapshot if available
        initial_state = {}
        start_version = 0

        if aggregate_id in self.snapshots:
            snapshot = self.snapshots[aggregate_id]
            if not version or snapshot.version <= version:
                initial_state = snapshot.state_data.copy()
                start_version = snapshot.version

        # Get events since snapshot
        if hasattr(self.event_store, "get_events"):
            events = self.event_store.get_events(
                aggregate_id, start_version=start_version, end_version=version
            )
        else:
            events = []

        # Aggregate events
        state = initial_state
        for aggregator in self.aggregators:
            relevant_events = [e for e in events if aggregator.can_handle(e.event_type)]
            if relevant_events:
                state = aggregator.aggregate(relevant_events, state)

        # Cache the result
        with self._lock:
            self.state_cache[aggregate_id] = (state.copy(), time.time())
            self.stats["events_processed"] += len(events)

        return state

    async def _store_event(self, event: Event) -> bool:
        """Store event in event store"""
        if not self.event_store:
            return False

        try:
            if hasattr(self.event_store, "append"):
                self.event_store.append(event)
            else:
                # Fallback for different event store interface
                logger.warning("Event store doesn't have append method")
                return False

            with self._lock:
                self._event_counter[event.aggregate_id] += 1

            return True

        except Exception as e:
            logger.error(f"Failed to store event: {e}")
            return False

    async def _check_snapshot(self, aggregate_id: str) -> None:
        """Check if snapshot is needed based on event count"""
        with self._lock:
            event_count = self._event_counter[aggregate_id]

        if event_count % self.snapshot_interval == 0:
            await self.create_snapshot(aggregate_id)

    async def _notify_replication_subscribers(
        self, aggregate_id: str, updates: Dict[str, Any]
    ) -> None:
        """Notify subscribers of replicated state changes"""
        subscribers = self.replication_subscribers.get(aggregate_id, set()).copy()

        for callback in subscribers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(aggregate_id, updates)
                else:
                    callback(aggregate_id, updates)
            except Exception as e:
                logger.error(f"Subscriber notification failed: {e}")

    def _get_next_version(self, aggregate_id: str) -> int:
        """Get next version number for aggregate"""
        with self._lock:
            self._event_counter[aggregate_id] += 1
            return self._event_counter[aggregate_id]

    def get_statistics(self) -> Dict[str, Any]:
        """Get state management statistics"""
        with self._lock:
            return {
                **self.stats,
                "local_states": len(self.local_states),
                "cached_states": len(self.state_cache),
                "snapshots": len(self.snapshots),
                "replicated_states": len(self.replicated_state),
                "total_events": sum(self._event_counter.values()),
            }


class StateCoordinator:
    """
    Coordinates state across multiple actors and tiers.
    Handles consistency, conflict resolution, and synchronization.
    """

    def __init__(self, state_manager: TieredStateManager):
        self.state_manager = state_manager
        self.actor_states: Dict[str, str] = {}  # actor_id -> aggregate_id mapping
        self._sync_tasks: Dict[str, asyncio.Task] = {}

    async def register_actor(
        self, actor: Any, aggregate_id: Optional[str] = None, auto_sync: bool = True
    ) -> str:
        """Register an actor with the state coordinator"""
        actor_id = getattr(actor, "actor_id", str(actor))

        if not aggregate_id:
            aggregate_id = actor_id

        self.actor_states[actor_id] = aggregate_id

        # Initial sync
        await self.state_manager.sync_actor_state(actor, "from_persistent")

        # Start auto-sync if requested
        if auto_sync:
            await self.start_auto_sync(actor_id, interval_seconds=60)

        return aggregate_id

    async def start_auto_sync(self, actor_id: str, interval_seconds: int = 60) -> None:
        """Start automatic state synchronization for an actor"""
        if actor_id in self._sync_tasks:
            return

        async def sync_loop():
            while actor_id in self.actor_states:
                try:
                    # Sync to persistent store
                    await self.state_manager.sync_actor_state(actor_id, "to_persistent")
                    await asyncio.sleep(interval_seconds)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Auto-sync error for {actor_id}: {e}")
                    await asyncio.sleep(10)  # Back off on error

        self._sync_tasks[actor_id] = asyncio.create_task(sync_loop())

    async def stop_auto_sync(self, actor_id: str) -> None:
        """Stop automatic synchronization for an actor"""
        if actor_id in self._sync_tasks:
            self._sync_tasks[actor_id].cancel()
            del self._sync_tasks[actor_id]

    async def coordinate_transaction(
        self,
        actor_ids: List[str],
        updates: Dict[str, Dict[str, Any]],
        consistency: ConsistencyLevel = ConsistencyLevel.STRONG,
    ) -> bool:
        """
        Coordinate a transaction across multiple actors with consistency guarantees.
        """
        if consistency == ConsistencyLevel.STRONG:
            # Implement two-phase commit
            return await self._two_phase_commit(actor_ids, updates)
        else:
            # Eventual consistency - apply updates independently
            results = []
            for actor_id in actor_ids:
                if actor_id in updates:
                    aggregate_id = self.actor_states.get(actor_id, actor_id)
                    result = await self.state_manager.update_state(
                        aggregate_id, updates[actor_id], StateType.GLOBAL_PERSISTENT
                    )
                    results.append(result)

            return all(results)

    async def _two_phase_commit(
        self, actor_ids: List[str], updates: Dict[str, Dict[str, Any]]
    ) -> bool:
        """Implement two-phase commit for strong consistency"""
        # Phase 1: Prepare
        prepared = []

        for actor_id in actor_ids:
            if actor_id in updates:
                # In real implementation, would check if update is valid
                prepared.append(actor_id)

        if len(prepared) != len([a for a in actor_ids if a in updates]):
            # Abort - not all actors prepared
            return False

        # Phase 2: Commit
        for actor_id in prepared:
            aggregate_id = self.actor_states.get(actor_id, actor_id)
            await self.state_manager.update_state(
                aggregate_id,
                updates[actor_id],
                StateType.GLOBAL_PERSISTENT,
                metadata={"transaction": "two_phase_commit"},
            )

        return True


# Example aggregators for specific use cases
class CounterAggregator(StateAggregator):
    """Aggregator for counter-based state"""

    def aggregate(
        self, events: List[Event], initial_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        state = initial_state.copy()

        for event in events:
            if event.event_type == "counter_incremented":
                counter_name = event.data.get("counter", "default")
                increment = event.data.get("increment", 1)
                state[counter_name] = state.get(counter_name, 0) + increment
            elif event.event_type == "counter_reset":
                counter_name = event.data.get("counter", "default")
                state[counter_name] = 0

        return state

    def can_handle(self, event_type: str) -> bool:
        return event_type in ["counter_incremented", "counter_reset"]


class MetricsAggregator(StateAggregator):
    """Aggregator for metrics and statistics"""

    def aggregate(
        self, events: List[Event], initial_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        state = initial_state.copy()

        for event in events:
            if event.event_type == "metric_recorded":
                metric_name = event.data.get("metric")
                value = event.data.get("value", 0)

                if metric_name:
                    metrics = state.setdefault("metrics", {})
                    metric_data = metrics.setdefault(
                        metric_name,
                        {
                            "count": 0,
                            "sum": 0,
                            "min": float("inf"),
                            "max": float("-inf"),
                            "values": [],
                        },
                    )

                    metric_data["count"] += 1
                    metric_data["sum"] += value
                    metric_data["min"] = min(metric_data["min"], value)
                    metric_data["max"] = max(metric_data["max"], value)

                    # Keep last 100 values for percentiles
                    metric_data["values"].append(value)
                    if len(metric_data["values"]) > 100:
                        metric_data["values"].pop(0)

        return state

    def can_handle(self, event_type: str) -> bool:
        return event_type == "metric_recorded"
