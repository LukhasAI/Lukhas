from __future__ import annotations

import logging

logger = logging.getLogger(__name__)
"""Event replayer utility for governance review.


#TAG:memory
#TAG:folds
#TAG:neuroplastic
#TAG:colony


Provides filtering and replay of events stored in the event
sourcing system. This module focuses on retrieving events tagged
with ``ETHICAL`` for auditing purposes.
"""


import json

from lukhas.core.common import get_logger
from lukhas.core.event_sourcing import AIAgentAggregate, Event, EventStore

logger = get_logger(__name__)


class EventReplayer:
    """Utility to filter and replay stored events."""

    def __init__(self, event_store: EventStore):
        self.event_store = event_store

    def _load_events(self, aggregate_id: str | None = None) -> list[Event]:
        """Load events from the event store, optionally for one aggregate."""
        conn = self.event_store._get_connection()
        query = (
            "SELECT event_id, event_type, aggregate_id, data, metadata, timestamp, version, correlation_id FROM events"
        )
        params: tuple = ()
        if aggregate_id:
            query += " WHERE aggregate_id = ?"
            params = (aggregate_id,)
        query += " ORDER BY timestamp"

        cursor = conn.execute(query, params)
        events: list[Event] = []
        for row in cursor:
            events.append(
                Event(
                    event_id=row[0],
                    event_type=row[1],
                    aggregate_id=row[2],
                    data=json.loads(row[3]),
                    metadata=json.loads(row[4]),
                    timestamp=row[5],
                    version=row[6],
                    correlation_id=row[7],
                )
            )
        return events

    def filter_events_by_tag(self, tag: str, aggregate_id: str | None = None) -> list[Event]:
        """Return all events that include the given symbolic tag."""
        events = self._load_events(aggregate_id)
        return [e for e in events if tag in e.metadata.get("tags", [])]

    def replay_events(self, events: list[Event]) -> AIAgentAggregate:
        """Replay a sequence of events and return the reconstructed aggregate."""
        if not events:
            raise ValueError("No events provided for replay")
        aggregate_id = events[0].aggregate_id
        temp_store = EventStore(":memory:")
        for event in events:
            temp_store.append_event(event)
        return AIAgentAggregate(aggregate_id, temp_store)

    # ✅ TODO: extend with CLI interface for governance dashboard


def replay_ethical_events(event_store: EventStore, aggregate_id: str | None = None) -> AIAgentAggregate | list[Event]:
    """Filter and replay events tagged with ``ETHICAL``."""
    replayer = EventReplayer(event_store)
    ethical_events = replayer.filter_events_by_tag("ETHICAL", aggregate_id)
    if aggregate_id:
        return replayer.replay_events(ethical_events)
    return ethical_events
