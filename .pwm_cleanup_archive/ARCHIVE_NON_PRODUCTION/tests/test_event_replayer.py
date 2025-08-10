import time
import uuid

from core.event_replayer import EventReplayer, replay_ethical_events
from core.event_sourcing import Event, EventStore


def test_filter_and_replay_ethical_events():
    store = EventStore(":memory:")
    # create two events with ETHICAL tag and one without
    e1 = Event(
        event_id=str(uuid.uuid4()),
        event_type="Test",
        aggregate_id="agent-X",
        data={"payload": 1},
        metadata={"tags": ["ETHICAL"]},
        timestamp=time.time(),
        version=1,
    )
    e2 = Event(
        event_id=str(uuid.uuid4()),
        event_type="Test",
        aggregate_id="agent-X",
        data={"payload": 2},
        metadata={"tags": ["ETHICAL"]},
        timestamp=time.time(),
        version=2,
    )
    e3 = Event(
        event_id=str(uuid.uuid4()),
        event_type="Test",
        aggregate_id="agent-X",
        data={"payload": 3},
        metadata={"tags": ["OTHER"]},
        timestamp=time.time(),
        version=3,
    )
    store.append_event(e1)
    store.append_event(e2)
    store.append_event(e3)

    replayer = EventReplayer(store)
    ethical_events = replayer.filter_events_by_tag("ETHICAL", "agent-X")
    assert len(ethical_events) == 2

    aggregate = replayer.replay_events(ethical_events)
    assert aggregate.version == 2

    # convenience wrapper
    agg2 = replay_ethical_events(store, "agent-X")
    assert agg2.version == 2
