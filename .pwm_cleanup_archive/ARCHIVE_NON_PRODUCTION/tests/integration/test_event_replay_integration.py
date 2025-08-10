"""
Integration tests for Event Replay and Snapshot System
Tests for Agent 1 Task 2: core/event_replay_snapshot.py integration
"""

import asyncio
import sys
import tempfile
import time
import uuid
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.core_hub import get_core_hub
from core.event_replay_snapshot import (
    ActorStateSnapshot,
    Event,
    EventStore,
    EventType,
    SnapshotStore,
)


class TestEventReplayIntegration:
    """Test suite for event replay system integration"""

    @pytest.fixture
    async def event_store(self):
        """Create event store for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            store = EventStore(storage_path=temp_dir)
            await store.start()
            yield store
            await store.stop()

    @pytest.fixture
    async def snapshot_store(self):
        """Create snapshot store for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            store = SnapshotStore(storage_path=temp_dir)
            yield store

    def test_event_creation_and_serialization(self):
        """Test event creation and JSON serialization"""
        test_event = Event(
            event_id=str(uuid.uuid4()),
            event_type=EventType.STATE_CHANGED,
            actor_id="test_actor",
            timestamp=time.time(),
            data={"counter": 42, "message": "test"},
        )

        # Test serialization
        json_str = test_event.to_json()
        assert isinstance(json_str, str)

        # Test deserialization
        restored_event = Event.from_json(json_str)
        assert restored_event.event_id == test_event.event_id
        assert restored_event.event_type == test_event.event_type
        assert restored_event.actor_id == test_event.actor_id
        assert restored_event.data == test_event.data

    @pytest.mark.asyncio
    async def test_event_store_functionality(self, event_store):
        """Test event store operations"""
        # Create test events
        events = []
        for i in range(5):
            event = Event(
                event_id=str(uuid.uuid4()),
                event_type=EventType.MESSAGE_PROCESSED,
                actor_id=f"actor_{i % 2}",  # Two different actors
                timestamp=time.time() + i,
                data={"sequence": i},
            )
            events.append(event)
            await event_store.append_event(event)

        # Test retrieval by actor
        actor_0_events = await event_store.get_events_for_actor("actor_0")
        actor_1_events = await event_store.get_events_for_actor("actor_1")

        assert len(actor_0_events) >= 2  # Should have events 0, 2, 4
        assert len(actor_1_events) >= 2  # Should have events 1, 3

        # Verify events are properly ordered by timestamp
        for i in range(len(actor_0_events) - 1):
            assert actor_0_events[i].timestamp <= actor_0_events[i + 1].timestamp

    @pytest.mark.asyncio
    async def test_core_hub_integration(self):
        """Test integration with CoreHub"""
        # Get hub instance
        hub = get_core_hub()

        # Verify event replay services are registered
        event_store = hub.get_service("event_store")
        snapshot_store = hub.get_service("snapshot_store")

        assert event_store is not None
        assert snapshot_store is not None
        assert type(event_store).__name__ == "EventStore"
        assert type(snapshot_store).__name__ == "SnapshotStore"

        # Test hub methods exist
        assert hasattr(hub, "replay_events_for_actor")
        assert hasattr(hub, "take_actor_snapshot")
        assert hasattr(hub, "restore_actor_from_snapshot")

    @pytest.mark.asyncio
    async def test_event_replay_functionality(self, event_store):
        """Test event replay with timing"""
        # Create events with specific timing
        base_time = time.time()
        events = []

        for i in range(3):
            event = Event(
                event_id=str(uuid.uuid4()),
                event_type=EventType.STATE_CHANGED,
                actor_id="replay_test_actor",
                timestamp=base_time + i * 0.1,  # 100ms apart
                data={"step": i},
            )
            events.append(event)
            await event_store.append_event(event)

        # Test replay with callback
        replayed_events = []

        async def replay_callback(event):
            replayed_events.append(event)

        # Replay at high speed
        count = await event_store.replay_events(
            events, speed=10.0, callback=replay_callback
        )

        assert count == 3
        assert len(replayed_events) == 3

        # Verify order is maintained
        for i, event in enumerate(replayed_events):
            assert event.data["step"] == i

    def test_actor_state_snapshot_creation(self):
        """Test actor state snapshot functionality"""

        # Create a mock actor with some state
        class MockActor:
            def __init__(self):
                self.actor_id = "test_actor"
                self.counter = 42
                self.data = {"key": "value"}
                self._stats = {"messages_processed": 10, "messages_failed": 1}
                self.children = {"child1": None, "child2": None}

        actor = MockActor()

        # Create snapshot
        snapshot = ActorStateSnapshot.create_from_actor(actor, "test_event_id")

        assert snapshot.actor_id == "test_actor"
        assert snapshot.actor_class == "MockActor"
        assert snapshot.event_id == "test_event_id"
        assert snapshot.state_hash is not None
        assert len(snapshot.state_data) > 0
        assert snapshot.metadata["message_count"] == 10
        assert snapshot.metadata["error_count"] == 1
        assert set(snapshot.metadata["children"]) == {"child1", "child2"}

    @pytest.mark.asyncio
    async def test_snapshot_store_operations(self, snapshot_store):
        """Test snapshot store save and load operations"""
        # Create a test snapshot
        import pickle

        test_data = {"counter": 42, "state": "active"}
        state_data = pickle.dumps(test_data)

        snapshot = ActorStateSnapshot(
            actor_id="test_actor",
            actor_class="TestActor",
            timestamp=time.time(),
            event_id="test_event",
            state_data=state_data,
            state_hash="test_hash",
            metadata={"version": "1.0"},
        )

        # Save snapshot
        await snapshot_store.save_snapshot(snapshot)

        # Load snapshot back
        loaded_snapshot = await snapshot_store.load_snapshot("test_actor")

        assert loaded_snapshot is not None
        assert loaded_snapshot.actor_id == "test_actor"
        assert loaded_snapshot.actor_class == "TestActor"
        assert loaded_snapshot.event_id == "test_event"

        # Verify data integrity
        loaded_data = pickle.loads(loaded_snapshot.state_data)
        assert loaded_data == test_data

    def test_integration_completeness(self):
        """Test that all required integration points are satisfied"""
        # Verify all required classes are importable
        from core.event_replay_snapshot import (
            ActorStateSnapshot,
            Event,
            EventType,
        )

        # Verify enum has all required values
        assert hasattr(EventType, "ACTOR_CREATED")
        assert hasattr(EventType, "MESSAGE_SENT")
        assert hasattr(EventType, "STATE_CHANGED")
        assert hasattr(EventType, "SNAPSHOT_TAKEN")

        # Verify core functions exist
        assert hasattr(Event, "to_json")
        assert hasattr(Event, "from_json")
        assert hasattr(ActorStateSnapshot, "create_from_actor")
        assert hasattr(ActorStateSnapshot, "restore_to_actor")

    @pytest.mark.asyncio
    async def test_demo_functionality(self):
        """Test that the demo function can be imported and has proper structure"""
        from core.event_replay_snapshot import demo_event_replay

        # Verify it's a coroutine function
        assert asyncio.iscoroutinefunction(demo_event_replay)


if __name__ == "__main__":
    # Run basic integration test
    asyncio.run(pytest.main([__file__, "-v"]))
