"""

#TAG:consciousness
#TAG:reflection
#TAG:neuroplastic
#TAG:colony


Event Replay and State Snapshotting System
Addresses TODO 169: Deterministic debugging through event replay

This module implements event sourcing with replay capabilities and state
snapshotting for efficient recovery and debugging of the actor system.
"""

import asyncio
import contextlib
import gzip
import hashlib
import json
import pickle
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

import aiofiles

from candidate.core.common import get_logger

from .actor_system import Actor, ActorMessage, ActorSystem

logger = get_logger(__name__)


class EventType(Enum):
    """Types of events in the system"""

    ACTOR_CREATED = "actor_created"
    ACTOR_DESTROYED = "actor_destroyed"
    MESSAGE_SENT = "message_sent"
    MESSAGE_PROCESSED = "message_processed"
    STATE_CHANGED = "state_changed"
    SNAPSHOT_TAKEN = "snapshot_taken"
    FAILURE_OCCURRED = "failure_occurred"


@dataclass
class Event:
    """Immutable event record"""

    event_id: str
    event_type: EventType
    actor_id: str
    timestamp: float
    data: dict[str, Any]
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None  # ID of event that caused this one

    def to_json(self) -> str:
        """Serialize to JSON"""
        return json.dumps(
            {
                "event_id": self.event_id,
                "event_type": self.event_type.value,
                "actor_id": self.actor_id,
                "timestamp": self.timestamp,
                "data": self.data,
                "correlation_id": self.correlation_id,
                "causation_id": self.causation_id,
            }
        )

    @classmethod
    def from_json(cls, json_str: str) -> "Event":
        """Deserialize from JSON"""
        data = json.loads(json_str)
        return cls(
            event_id=data["event_id"],
            event_type=EventType(data["event_type"]),
            actor_id=data["actor_id"],
            timestamp=data["timestamp"],
            data=data["data"],
            correlation_id=data.get("correlation_id"),
            causation_id=data.get("causation_id"),
        )


@dataclass
class ActorStateSnapshot:
    """Snapshot of an actor's complete state"""

    actor_id: str
    actor_class: str
    timestamp: float
    event_id: str  # Event that triggered the snapshot
    state_data: bytes  # Pickled state
    state_hash: str  # For integrity verification
    metadata: dict[str, Any]

    @classmethod
    def create_from_actor(cls, actor: Actor, event_id: str) -> "ActorStateSnapshot":
        """Create snapshot from live actor"""
        # Capture state (excluding non-serializable items)
        state_dict = {}
        for key, value in actor.__dict__.items():
            if key.startswith("_") or key in ["actor_system", "mailbox", "supervisor"]:
                continue
            try:
                # Test if serializable
                pickle.dumps(value)
                state_dict[key] = value
            except Exception:
                # Skip non-serializable attributes
                logger.debug(f"Skipping non-serializable attribute: {key}")

        # Serialize state
        state_data = pickle.dumps(state_dict)
        state_hash = hashlib.sha256(state_data).hexdigest()

        return cls(
            actor_id=actor.actor_id,
            actor_class=actor.__class__.__name__,
            timestamp=time.time(),
            event_id=event_id,
            state_data=state_data,
            state_hash=state_hash,
            metadata={
                "message_count": actor._stats.get("messages_processed", 0),
                "error_count": actor._stats.get("messages_failed", 0),
                "children": list(actor.children.keys()),
            },
        )

    def restore_to_actor(self, actor: Actor):
        """Restore snapshot state to an actor"""
        state_dict = pickle.loads(self.state_data)

        for key, value in state_dict.items():
            setattr(actor, key, value)

        logger.info(f"Restored actor {actor.actor_id} to snapshot from {self.timestamp}")


class EventStore:
    """Persistent storage for events with replay capabilities"""

    def __init__(
        self,
        storage_path: str = "./event_store",
        max_memory_events: int = 10000,
        compression: bool = True,
    ):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)

        self.max_memory_events = max_memory_events
        self.compression = compression

        # In-memory buffer for recent events
        self.memory_buffer: deque = deque(maxlen=max_memory_events)

        # Event indices for efficient queries
        self.events_by_actor: dict[str, list[Event]] = defaultdict(list)
        self.events_by_correlation: dict[str, list[Event]] = defaultdict(list)

        # Persistence
        self.current_segment = 0
        self.segment_size = 1000  # Events per file
        self._lock = threading.Lock()

        # Start background persistence
        self._persist_task = None

    async def start(self):
        """Start the event store"""
        self._persist_task = asyncio.create_task(self._persistence_loop())
        await self._load_recent_events()
        logger.info("Event store started")

    async def stop(self):
        """Stop the event store"""
        if self._persist_task:
            self._persist_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._persist_task

        await self._flush_to_disk()
        logger.info("Event store stopped")

    async def append_event(self, event: Event):
        """Append an event to the store"""
        with self._lock:
            self.memory_buffer.append(event)
            self.events_by_actor[event.actor_id].append(event)

            if event.correlation_id:
                self.events_by_correlation[event.correlation_id].append(event)

    async def get_events_for_actor(
        self,
        actor_id: str,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
    ) -> list[Event]:
        """Get all events for a specific actor"""
        events = []

        # Check memory buffer first
        with self._lock:
            for event in self.events_by_actor.get(actor_id, []):
                if start_time and event.timestamp < start_time:
                    continue
                if end_time and event.timestamp > end_time:
                    continue
                events.append(event)

        # Load from disk if needed
        if len(events) < 100:  # Arbitrary threshold
            disk_events = await self._load_events_from_disk(actor_id, start_time, end_time)
            events.extend(disk_events)

        return sorted(events, key=lambda e: e.timestamp)

    async def get_events_by_correlation(self, correlation_id: str) -> list[Event]:
        """Get all events for a correlation ID"""
        with self._lock:
            memory_events = list(self.events_by_correlation.get(correlation_id, []))

        # Also check disk
        disk_events = await self._load_correlation_events_from_disk(correlation_id)

        all_events = memory_events + disk_events
        return sorted(all_events, key=lambda e: e.timestamp)

    async def replay_events(
        self,
        events: list[Event],
        speed: float = 1.0,
        callback: Optional[Callable] = None,
    ) -> int:
        """Replay a sequence of events with timing"""
        if not events:
            return 0

        # Sort by timestamp
        sorted_events = sorted(events, key=lambda e: e.timestamp)

        start_time = sorted_events[0].timestamp
        replay_start = time.time()
        events_replayed = 0

        for event in sorted_events:
            # Calculate when this event should be replayed
            event_offset = event.timestamp - start_time
            replay_time = replay_start + (event_offset / speed)

            # Wait until it's time
            wait_time = replay_time - time.time()
            if wait_time > 0:
                await asyncio.sleep(wait_time)

            # Replay the event
            if callback:
                await callback(event)

            events_replayed += 1

            logger.debug(f"Replayed event {event.event_id} at {event.timestamp}")

        return events_replayed

    async def _persistence_loop(self):
        """Background task to persist events to disk"""
        while True:
            try:
                await asyncio.sleep(10.0)  # Persist every 10 seconds
                await self._flush_to_disk()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Persistence error: {e}")

    async def _flush_to_disk(self):
        """Flush memory buffer to disk"""
        with self._lock:
            if not self.memory_buffer:
                return

            events_to_persist = list(self.memory_buffer)

        # Group by segment
        for i in range(0, len(events_to_persist), self.segment_size):
            segment_events = events_to_persist[i : i + self.segment_size]
            await self._write_segment(self.current_segment, segment_events)
            self.current_segment += 1

    async def _write_segment(self, segment_id: int, events: list[Event]):
        """Write a segment of events to disk"""
        filename = self.storage_path / f"events_{segment_id:08d}.jsonl"

        if self.compression:
            filename = filename.with_suffix(".jsonl.gz")

            async with aiofiles.open(filename, "wb") as f:
                data = "\n".join(e.to_json() for e in events).encode("utf-8")
                compressed = gzip.compress(data)
                await f.write(compressed)
        else:
            async with aiofiles.open(filename, "w") as f:
                for event in events:
                    await f.write(event.to_json() + "\n")

    async def _load_recent_events(self):
        """Load recent events from disk into memory"""
        # Find most recent segments
        segment_files = sorted(self.storage_path.glob("events_*.jsonl*"))

        if not segment_files:
            return

        # Load last few segments
        for segment_file in segment_files[-3:]:  # Last 3 segments
            events = await self._read_segment(segment_file)

            with self._lock:
                for event in events:
                    self.memory_buffer.append(event)
                    self.events_by_actor[event.actor_id].append(event)
                    if event.correlation_id:
                        self.events_by_correlation[event.correlation_id].append(event)

    async def _read_segment(self, filename: Path) -> list[Event]:
        """Read a segment of events from disk"""
        events = []

        if filename.suffix == ".gz":
            async with aiofiles.open(filename, "rb") as f:
                compressed = await f.read()
                data = gzip.decompress(compressed).decode("utf-8")

            for line in data.strip().split("\n"):
                if line:
                    events.append(Event.from_json(line))
        else:
            async with aiofiles.open(filename) as f:
                async for line in f:
                    if line.strip():
                        events.append(Event.from_json(line.strip()))

        return events

    async def _load_events_from_disk(
        self, actor_id: str, start_time: Optional[float], end_time: Optional[float]
    ) -> list[Event]:
        """Load events for an actor from disk"""
        events = []

        # This is simplified - in production, you'd have better indexing
        for segment_file in sorted(self.storage_path.glob("events_*.jsonl*")):
            segment_events = await self._read_segment(segment_file)

            for event in segment_events:
                if event.actor_id != actor_id:
                    continue
                if start_time and event.timestamp < start_time:
                    continue
                if end_time and event.timestamp > end_time:
                    continue

                events.append(event)

        return events

    async def _load_correlation_events_from_disk(self, correlation_id: str) -> list[Event]:
        """Load events by correlation ID from disk"""
        events = []

        for segment_file in sorted(self.storage_path.glob("events_*.jsonl*")):
            segment_events = await self._read_segment(segment_file)

            for event in segment_events:
                if event.correlation_id == correlation_id:
                    events.append(event)

        return events


class SnapshotStore:
    """Storage for actor state snapshots"""

    def __init__(self, storage_path: str = "./snapshots"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)

        # Index of snapshots
        self.snapshot_index: dict[str, list[tuple[float, str]]] = defaultdict(list)
        self._lock = threading.Lock()

        # Load existing snapshots
        self._load_index()

    async def save_snapshot(self, snapshot: ActorStateSnapshot):
        """Save a snapshot to disk"""
        filename = self.storage_path / f"{snapshot.actor_id}_{snapshot.timestamp:.0f}_{snapshot.event_id}.snap"

        # Compress snapshot data
        compressed_data = gzip.compress(pickle.dumps(snapshot))

        async with aiofiles.open(filename, "wb") as f:
            await f.write(compressed_data)

        # Update index
        with self._lock:
            self.snapshot_index[snapshot.actor_id].append((snapshot.timestamp, str(filename)))

        logger.info(f"Saved snapshot for {snapshot.actor_id} at {snapshot.timestamp}")

    async def load_snapshot(self, actor_id: str, timestamp: Optional[float] = None) -> Optional[ActorStateSnapshot]:
        """Load a snapshot for an actor"""
        with self._lock:
            snapshots = self.snapshot_index.get(actor_id, [])

        if not snapshots:
            return None

        # Find appropriate snapshot
        if timestamp is None:
            # Get latest
            _, filename = max(snapshots, key=lambda x: x[0])
        else:
            # Get closest before timestamp
            valid_snaps = [(t, f) for t, f in snapshots if t <= timestamp]
            if not valid_snaps:
                return None
            _, filename = max(valid_snaps, key=lambda x: x[0])

        # Load snapshot
        async with aiofiles.open(filename, "rb") as f:
            compressed_data = await f.read()

        snapshot = pickle.loads(gzip.decompress(compressed_data))
        return snapshot

    async def get_latest_snapshot(
        self, actor_id: str, before_timestamp: Optional[float] = None
    ) -> Optional[ActorStateSnapshot]:
        """Get the latest snapshot for an actor, optionally before timestamp"""
        return await self.load_snapshot(actor_id, before_timestamp)

    async def delete_old_snapshots(self, retention_days: int = 7):
        """Delete snapshots older than retention period"""
        cutoff_time = time.time() - (retention_days * 86400)

        with self._lock:
            for actor_id in list(self.snapshot_index.keys()):
                # Filter out old snapshots
                new_snapshots = [(t, f) for t, f in self.snapshot_index[actor_id] if t > cutoff_time]

                # Delete old files
                old_snapshots = [(t, f) for t, f in self.snapshot_index[actor_id] if t <= cutoff_time]

                for _, filename in old_snapshots:
                    try:
                        Path(filename).unlink()
                    except Exception as e:
                        logger.error(f"Failed to delete snapshot {filename}: {e}")

                self.snapshot_index[actor_id] = new_snapshots

    def _load_index(self):
        """Load snapshot index from disk"""
        for snapshot_file in self.storage_path.glob("*.snap"):
            # Parse filename: actorId_timestamp_eventId.snap
            parts = snapshot_file.stem.split("_")
            if len(parts) >= 3:
                actor_id = parts[0]
                timestamp = float(parts[1])

                with self._lock:
                    self.snapshot_index[actor_id].append((timestamp, str(snapshot_file)))


class EventSourcedActor(Actor):
    """Actor that automatically records events and supports replay"""

    def __init__(
        self,
        actor_id: str,
        event_store: Optional[EventStore] = None,
        snapshot_store: Optional[SnapshotStore] = None,
    ):
        super().__init__(actor_id)
        self.event_store = event_store
        self.snapshot_store = snapshot_store
        self.replay_mode = False

        # Track event causation
        self._current_causation_id: Optional[str] = None

    async def send_message(self, message: ActorMessage) -> bool:
        """Override to record message events"""
        if self.event_store and not self.replay_mode:
            event = Event(
                event_id=message.message_id,
                event_type=EventType.MESSAGE_SENT,
                actor_id=self.actor_id,
                timestamp=time.time(),
                data={
                    "recipient": message.recipient,
                    "message_type": message.message_type,
                    "payload": message.payload,
                },
                correlation_id=message.correlation_id,
                causation_id=self._current_causation_id,
            )
            await self.event_store.append_event(event)

        return await super().send_message(message)

    async def _process_message(self, message: ActorMessage):
        """Override to record processing events"""
        self._current_causation_id = message.message_id

        try:
            # Record message received
            if self.event_store and not self.replay_mode:
                event = Event(
                    event_id=f"{message.message_id}_received",
                    event_type=EventType.MESSAGE_PROCESSED,
                    actor_id=self.actor_id,
                    timestamp=time.time(),
                    data={
                        "sender": message.sender,
                        "message_type": message.message_type,
                        "message_id": message.message_id,
                    },
                    correlation_id=message.correlation_id,
                )
                await self.event_store.append_event(event)

            # Process normally
            await super()._process_message(message)

        finally:
            self._current_causation_id = None

    async def record_state_change(
        self,
        change_type: str,
        old_value: Any,
        new_value: Any,
        metadata: Optional[dict[str, Any]] = None,
    ):
        """Record a state change event"""
        if self.event_store and not self.replay_mode:
            event = Event(
                event_id=f"{self.actor_id}_state_{time.time()}",
                event_type=EventType.STATE_CHANGED,
                actor_id=self.actor_id,
                timestamp=time.time(),
                data={
                    "change_type": change_type,
                    "old_value": old_value,
                    "new_value": new_value,
                    "metadata": metadata or {},
                },
                causation_id=self._current_causation_id,
            )
            await self.event_store.append_event(event)

    async def take_snapshot(self, event_id: Optional[str] = None):
        """Take a snapshot of current state"""
        if self.snapshot_store:
            event_id = event_id or f"manual_{time.time()}"
            snapshot = ActorStateSnapshot.create_from_actor(self, event_id)
            await self.snapshot_store.save_snapshot(snapshot)

            # Record snapshot event
            if self.event_store:
                event = Event(
                    event_id=f"snapshot_{event_id}",
                    event_type=EventType.SNAPSHOT_TAKEN,
                    actor_id=self.actor_id,
                    timestamp=time.time(),
                    data={
                        "snapshot_hash": snapshot.state_hash,
                        "state_size": len(snapshot.state_data),
                    },
                )
                await self.event_store.append_event(event)

    async def restore_from_snapshot(self, timestamp: Optional[float] = None):
        """Restore actor state from snapshot"""
        if not self.snapshot_store:
            raise RuntimeError("No snapshot store configured")

        snapshot = await self.snapshot_store.load_snapshot(self.actor_id, timestamp)
        if snapshot:
            snapshot.restore_to_actor(self)
            return True
        return False

    async def replay_history(
        self,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        speed: float = 1.0,
    ):
        """Replay actor's event history"""
        if not self.event_store:
            raise RuntimeError("No event store configured")

        self.replay_mode = True

        try:
            # Get events
            events = await self.event_store.get_events_for_actor(self.actor_id, start_time, end_time)

            # Find latest snapshot before start time
            if self.snapshot_store and start_time:
                await self.restore_from_snapshot(start_time)

            # Replay events
            async def replay_callback(event: Event):
                if event.event_type == EventType.MESSAGE_PROCESSED:
                    # Recreate and process the message
                    message = ActorMessage(
                        message_id=event.data["message_id"],
                        sender=event.data["sender"],
                        recipient=self.actor_id,
                        message_type=event.data["message_type"],
                        payload={},  # Payload not stored in this event
                        timestamp=event.timestamp,
                        correlation_id=event.correlation_id,
                    )
                    await self._process_message(message)

                elif event.event_type == EventType.STATE_CHANGED:
                    # Apply state change
                    # This is simplified - real implementation would be more
                    # sophisticated
                    logger.info(f"Replaying state change: {event.data}")

            count = await self.event_store.replay_events(events, speed, replay_callback)

            logger.info(f"Replayed {count} events for actor {self.actor_id}")

        finally:
            self.replay_mode = False


class ReplayController:
    """Controller for system-wide replay operations"""

    def __init__(
        self,
        actor_system: ActorSystem,
        event_store: EventStore,
        snapshot_store: SnapshotStore,
    ):
        self.actor_system = actor_system
        self.event_store = event_store
        self.snapshot_store = snapshot_store

    async def replay_scenario(self, correlation_id: str, speed: float = 1.0, isolated: bool = True) -> dict[str, Any]:
        """Replay all events for a correlation ID"""
        # Get all events
        events = await self.event_store.get_events_by_correlation(correlation_id)

        if not events:
            return {"status": "error", "reason": "no_events_found"}

        # Find involved actors
        involved_actors = {e.actor_id for e in events}

        # Create isolated environment if requested
        if isolated:
            # This would create a separate actor system instance
            # For now, we'll use the existing one
            logger.warning("Isolated replay not implemented - using main system")

        # Restore actors from snapshots
        start_time = events[0].timestamp
        for actor_id in involved_actors:
            actor = self.actor_system.get_actor(actor_id)
            if isinstance(actor, EventSourcedActor):
                await actor.restore_from_snapshot(start_time)

        # Replay events
        replayed = await self.event_store.replay_events(events, speed, self._replay_event_callback)

        return {
            "status": "success",
            "events_replayed": replayed,
            "actors_involved": list(involved_actors),
            "duration": events[-1].timestamp - events[0].timestamp,
        }

    async def _replay_event_callback(self, event: Event):
        """Handle individual event during replay"""
        actor = self.actor_system.get_actor(event.actor_id)

        if not actor:
            logger.warning(f"Actor {event.actor_id} not found for replay")
            return

        # Route event to appropriate handler
        if event.event_type == EventType.MESSAGE_SENT:
            # Re-send the message
            recipient_ref = self.actor_system.get_actor_ref(event.data["recipient"])
            if recipient_ref:
                await recipient_ref.tell(
                    event.data["message_type"],
                    event.data["payload"],
                    correlation_id=event.correlation_id,
                )

    async def create_debugging_checkpoint(self, description: str) -> str:
        """Create a system-wide checkpoint for debugging"""
        checkpoint_id = f"checkpoint_{int(time.time())}"

        # Take snapshots of all actors
        snapshot_tasks = []
        for _actor_id, actor in self.actor_system.actors.items():
            if isinstance(actor, EventSourcedActor):
                snapshot_tasks.append(actor.take_snapshot(checkpoint_id))

        if snapshot_tasks:
            await asyncio.gather(*snapshot_tasks, return_exceptions=True)

        # Record checkpoint event
        checkpoint_event = Event(
            event_id=checkpoint_id,
            event_type=EventType.STATE_CHANGED,
            actor_id="system",
            timestamp=time.time(),
            data={
                "checkpoint_type": "debugging",
                "description": description,
                "actor_count": len(self.actor_system.actors),
            },
        )
        await self.event_store.append_event(checkpoint_event)

        logger.info(f"Created debugging checkpoint: {checkpoint_id}")
        return checkpoint_id


# Example usage
async def demo_event_replay():
    """Demonstrate event replay and snapshotting"""
    import uuid

    from .actor_system import get_global_actor_system

    # Setup
    system = await get_global_actor_system()
    event_store = EventStore()
    snapshot_store = SnapshotStore()

    await event_store.start()

    # Create event-sourced actor
    class DemoActor(EventSourcedActor):
        def __init__(self, actor_id: str):
            super().__init__(actor_id, event_store, snapshot_store)
            self.counter = 0
            self.data = {}

            self.register_handler("increment", self._handle_increment)
            self.register_handler("store_data", self._handle_store_data)

        async def _handle_increment(self, message: ActorMessage):
            old_value = self.counter
            self.counter += message.payload.get("amount", 1)

            await self.record_state_change("counter_increment", old_value, self.counter)

            return {"new_value": self.counter}

        async def _handle_store_data(self, message: ActorMessage):
            key = message.payload.get("key")
            value = message.payload.get("value")

            old_data = self.data.copy()
            self.data[key] = value

            await self.record_state_change("data_update", old_data, self.data)

            return {"stored": True}

    # Create actor
    demo_ref = await system.create_actor(DemoActor, "demo-actor-001")

    # Generate some activity
    correlation_id = str(uuid.uuid4())

    for i in range(5):
        await demo_ref.tell("increment", {"amount": i}, correlation_id=correlation_id)
        await demo_ref.tell(
            "store_data",
            {"key": f"item_{i}", "value": i * 10},
            correlation_id=correlation_id,
        )
        await asyncio.sleep(0.1)

    # Take a snapshot
    demo_actor = system.get_actor("demo-actor-001")
    await demo_actor.take_snapshot()

    # More activity
    for i in range(5, 10):
        await demo_ref.tell("increment", {"amount": i}, correlation_id=correlation_id)
        await asyncio.sleep(0.1)

    # Create replay controller
    replay_controller = ReplayController(system, event_store, snapshot_store)

    # Create checkpoint
    checkpoint_id = await replay_controller.create_debugging_checkpoint("Before replay test")

    print(f"Created checkpoint: {checkpoint_id}")

    # Replay the scenario
    print(f"Replaying scenario for correlation {correlation_id}")
    result = await replay_controller.replay_scenario(correlation_id, speed=10.0)

    print(f"Replay result: {result}")

    # Check final state
    print(f"Final counter value: {demo_actor.counter}")
    print(f"Final data: {demo_actor.data}")

    # Cleanup
    await event_store.stop()


if __name__ == "__main__":
    asyncio.run(demo_event_replay())
