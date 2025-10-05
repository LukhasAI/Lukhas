"""
tests/test_events.py

Unit tests for event-sourced storage system - Event schema and EventStore functionality.
Covers event creation, storage operations, queries, and replay functionality.
"""
from datetime import datetime, timedelta
from unittest.mock import patch
from uuid import UUID, uuid4

import pytest

from storage.events import Event, EventStore, get_event_store


@pytest.fixture
def event_store():
    """Create a fresh EventStore for each test."""
    return EventStore(max_capacity=100)


@pytest.fixture
def sample_glyph_id():
    """Fixed glyph ID for consistent testing."""
    return UUID("12345678-1234-5678-9012-123456789012")


def test_event_creation():
    """Test Event creation with factory method."""
    glyph_id = uuid4()
    payload = {"action": "think", "intensity": 0.8}

    event = Event.create("intention", "experimental", glyph_id, payload)

    assert isinstance(event.id, UUID)
    assert isinstance(event.ts, datetime)
    assert event.kind == "intention"
    assert event.lane == "experimental"
    assert event.glyph_id == glyph_id
    assert event.payload == payload


def test_event_creation_with_custom_params():
    """Test Event creation with custom timestamp and ID."""
    glyph_id = uuid4()
    event_id = uuid4()
    ts = datetime.utcnow()
    payload = {"test": "data"}

    event = Event.create("action", "candidate", glyph_id, payload, ts=ts, event_id=event_id)

    assert event.id == event_id
    assert event.ts == ts
    assert event.kind == "action"
    assert event.lane == "candidate"


def test_event_serialization():
    """Test event to_dict and from_dict methods."""
    glyph_id = uuid4()
    payload = {"test": 123, "nested": {"key": "value"}}

    original = Event.create("memory_write", "prod", glyph_id, payload)
    event_dict = original.to_dict()

    # Verify dict structure
    assert "id" in event_dict
    assert "ts" in event_dict
    assert event_dict["kind"] == "memory_write"
    assert event_dict["lane"] == "prod"
    assert event_dict["payload"] == payload

    # Test round-trip
    restored = Event.from_dict(event_dict)
    assert restored.id == original.id
    assert restored.ts == original.ts
    assert restored.kind == original.kind
    assert restored.lane == original.lane
    assert restored.glyph_id == original.glyph_id
    assert restored.payload == original.payload


def test_event_store_initialization(event_store):
    """Test EventStore initialization."""
    assert event_store.max_capacity == 100
    assert len(event_store.events) == 0
    assert len(event_store._glyph_index) == 0
    assert len(event_store._kind_index) == 0


def test_append_event(event_store, sample_glyph_id):
    """Test appending events to store."""
    event = Event.create("intention", "experimental", sample_glyph_id, {"test": "data"})

    event_store.append(event)

    assert len(event_store.events) == 1
    assert event_store.events[0] == event
    assert sample_glyph_id in event_store._glyph_index
    assert "intention" in event_store._kind_index


def test_append_multiple_events(event_store, sample_glyph_id):
    """Test appending multiple events."""
    events = []
    for i in range(5):
        event = Event.create(f"action_{i}", "experimental", sample_glyph_id, {"step": i})
        events.append(event)
        event_store.append(event)

    assert len(event_store.events) == 5
    assert all(e in event_store.events for e in events)


def test_capacity_limit(sample_glyph_id):
    """Test that store respects capacity limit."""
    small_store = EventStore(max_capacity=3)

    # Add more events than capacity
    events = []
    for i in range(5):
        event = Event.create("test", "experimental", sample_glyph_id, {"i": i})
        events.append(event)
        small_store.append(event)

    # Should only keep the last 3
    assert len(small_store.events) == 3
    assert small_store.events[-1] == events[-1]  # Most recent
    assert events[0] not in small_store.events   # Oldest evicted


def test_query_recent_basic(event_store, sample_glyph_id):
    """Test basic recent events query."""
    events = []
    for i in range(10):
        event = Event.create("test", "experimental", sample_glyph_id, {"order": i})
        events.append(event)
        event_store.append(event)

    recent = event_store.query_recent(limit=5)

    assert len(recent) == 5
    # Should return most recent first
    assert recent[0].payload["order"] == 9
    assert recent[4].payload["order"] == 5


def test_query_recent_with_kind_filter(event_store, sample_glyph_id):
    """Test recent query with kind filtering."""
    # Add mixed event kinds
    for i in range(5):
        event_store.append(Event.create("intention", "experimental", sample_glyph_id, {"i": i}))
        event_store.append(Event.create("action", "experimental", sample_glyph_id, {"i": i}))

    intentions = event_store.query_recent(kind="intention")
    actions = event_store.query_recent(kind="action")

    assert len(intentions) == 5
    assert len(actions) == 5
    assert all(e.kind == "intention" for e in intentions)
    assert all(e.kind == "action" for e in actions)


def test_query_recent_with_lane_filter(event_store, sample_glyph_id):
    """Test recent query with lane filtering."""
    # Add events in different lanes
    for i in range(3):
        event_store.append(Event.create("test", "experimental", sample_glyph_id, {"i": i}))
        event_store.append(Event.create("test", "candidate", sample_glyph_id, {"i": i}))

    exp_events = event_store.query_recent(lane="experimental")
    cand_events = event_store.query_recent(lane="candidate")

    assert len(exp_events) == 3
    assert len(cand_events) == 3
    assert all(e.lane == "experimental" for e in exp_events)
    assert all(e.lane == "candidate" for e in cand_events)


def test_query_recent_with_time_filter(event_store, sample_glyph_id):
    """Test recent query with time filtering."""
    base_time = datetime.utcnow()

    # Add old events
    for i in range(3):
        old_ts = base_time - timedelta(hours=2)
        event = Event.create("old", "experimental", sample_glyph_id, {"i": i}, ts=old_ts)
        event_store.append(event)

    # Add recent events
    for i in range(2):
        recent_ts = base_time - timedelta(minutes=10)
        event = Event.create("recent", "experimental", sample_glyph_id, {"i": i}, ts=recent_ts)
        event_store.append(event)

    # Query events from last hour
    since = base_time - timedelta(hours=1)
    recent_events = event_store.query_recent(since=since)

    assert len(recent_events) == 2
    assert all(e.kind == "recent" for e in recent_events)


def test_query_by_glyph(event_store):
    """Test querying events by glyph ID."""
    glyph1 = uuid4()
    glyph2 = uuid4()

    # Add events for different glyphs
    for i in range(3):
        event_store.append(Event.create("test", "experimental", glyph1, {"glyph": 1, "i": i}))
        event_store.append(Event.create("test", "experimental", glyph2, {"glyph": 2, "i": i}))

    glyph1_events = event_store.query_by_glyph(glyph1)
    glyph2_events = event_store.query_by_glyph(glyph2)

    assert len(glyph1_events) == 3
    assert len(glyph2_events) == 3
    assert all(e.glyph_id == glyph1 for e in glyph1_events)
    assert all(e.glyph_id == glyph2 for e in glyph2_events)


def test_query_sliding_window(event_store, sample_glyph_id):
    """Test sliding window queries."""
    base_time = datetime.utcnow()

    # Add events at different times
    timestamps = [
        base_time - timedelta(minutes=2),   # Should be included (within 5 min)
        base_time - timedelta(minutes=3),   # Should be included (within 5 min)
        base_time - timedelta(minutes=10)   # Should be excluded (outside 5 min)
    ]

    for i, ts in enumerate(timestamps):
        event = Event.create("test", "experimental", sample_glyph_id, {"i": i}, ts=ts)
        event_store.append(event)

    # Query last 5 minutes
    window_events = event_store.query_sliding_window(window_seconds=300)

    assert len(window_events) == 2  # Only recent events


def test_replay_sequence(event_store, sample_glyph_id):
    """Test replay sequence generation."""
    base_time = datetime.utcnow()

    # Add events with specific timestamps (out of order)
    timestamps = [
        base_time - timedelta(minutes=5),   # Oldest
        base_time - timedelta(minutes=1),   # Newest
        base_time - timedelta(minutes=3),   # Middle
    ]

    for i, ts in enumerate(timestamps):
        event = Event.create("test", "experimental", sample_glyph_id, {"order": i}, ts=ts)
        event_store.append(event)

    # Get replay sequence (should be chronological)
    replay_events = list(event_store.replay_sequence(sample_glyph_id))

    assert len(replay_events) == 3
    # Should be in chronological order (oldest first)
    assert replay_events[0].payload["order"] == 0  # Oldest
    assert replay_events[1].payload["order"] == 2  # Middle
    assert replay_events[2].payload["order"] == 1  # Newest


def test_get_stats(event_store, sample_glyph_id):
    """Test store statistics."""
    # Add some events
    glyph1 = uuid4()
    glyph2 = uuid4()

    event_store.append(Event.create("intention", "experimental", glyph1, {}))
    event_store.append(Event.create("action", "experimental", glyph2, {}))
    event_store.append(Event.create("intention", "candidate", glyph1, {}))

    stats = event_store.get_stats()

    assert stats["total_events"] == 3
    assert stats["capacity"] == 100
    assert stats["utilization"] == 0.03
    assert stats["unique_glyphs"] == 2
    assert stats["unique_kinds"] == 2


def test_clear_store(event_store, sample_glyph_id):
    """Test clearing the event store."""
    # Add some events
    for i in range(5):
        event_store.append(Event.create("test", "experimental", sample_glyph_id, {"i": i}))

    assert len(event_store.events) == 5

    # Clear store
    event_store.clear()

    assert len(event_store.events) == 0
    assert len(event_store._glyph_index) == 0
    assert len(event_store._kind_index) == 0


def test_prometheus_metrics():
    """Test Prometheus metrics integration."""
    with patch('storage.events.PROM', True):
        with patch('storage.events.EVENTS_APPENDED') as mock_appended:
            with patch('storage.events.STORE_SIZE') as mock_size:
                store = EventStore()
                event = Event.create("test", "experimental", uuid4(), {})

                store.append(event)

                mock_appended.labels.assert_called_with(kind="test", lane="experimental")
                mock_size.set.assert_called_with(1)


def test_prometheus_unavailable():
    """Test graceful handling when Prometheus is unavailable."""
    with patch('storage.events.PROM', False):
        store = EventStore()
        event = Event.create("test", "experimental", uuid4(), {})

        # Should not raise exceptions
        store.append(event)
        store.query_recent()

        assert len(store.events) == 1


def test_global_event_store_singleton():
    """Test global event store singleton pattern."""
    store1 = get_event_store()
    store2 = get_event_store()

    assert store1 is store2  # Same instance


def test_thread_safety_basic(event_store, sample_glyph_id):
    """Basic thread safety test (not comprehensive)."""
    import threading

    events = []

    def add_events():
        for i in range(10):
            event = Event.create("thread_test", "experimental", sample_glyph_id, {"i": i})
            events.append(event)
            event_store.append(event)

    threads = [threading.Thread(target=add_events) for _ in range(3)]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Should have all events
    assert len(event_store.events) == 30
    assert len(events) == 30
