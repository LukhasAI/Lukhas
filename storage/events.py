"""
storage/events.py

Event-sourced memory & experience replay system for LUKHAS consciousness streams.
Provides Event schema and minimal API for sliding window queries and replay functionality.

Usage:
  from storage.events import Event, EventStore
  store = EventStore()
  event = Event.create("intention", "experimental", glyph_id, {"action": "think"})
  store.append(event)
  recent = store.query_recent(limit=100)
"""

from __future__ import annotations

import os
import threading
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Iterator, List, Optional
from uuid import UUID, uuid4

try:
    from prometheus_client import Counter, Gauge, Histogram

    try:
        EVENTS_APPENDED = Counter("lukhas_events_appended_total", "Events appended to store", ["kind", "lane"])
        EVENTS_QUERIED = Counter("lukhas_events_queried_total", "Event queries executed", ["query_type"])
        STORE_SIZE = Gauge("lukhas_event_store_size", "Current number of events in store")
        QUERY_DURATION = Histogram("lukhas_event_query_duration_seconds", "Event query duration", ["query_type"])
        PROM = True
    except ValueError:
        # Metrics already registered (happens in tests), use no-op fallbacks
        PROM = False

        class _NoopMetric:
            def labels(self, *_, **__):
                return self

            def inc(self, *_):
                pass

            def set(self, *_):
                pass

            def observe(self, *_):
                pass

        EVENTS_APPENDED = _NoopMetric()
        EVENTS_QUERIED = _NoopMetric()
        STORE_SIZE = _NoopMetric()
        QUERY_DURATION = _NoopMetric()
except Exception:
    PROM = False

    class _NoopMetric:
        def labels(self, *_, **__):
            return self

        def inc(self, *_):
            pass

        def set(self, *_):
            pass

        def observe(self, *_):
            pass

    EVENTS_APPENDED = _NoopMetric()
    EVENTS_QUERIED = _NoopMetric()
    STORE_SIZE = _NoopMetric()
    QUERY_DURATION = _NoopMetric()


@dataclass(frozen=True)
class Event:
    """
    Immutable event record for event-sourced architecture.

    Fields match T4-DELTA-PLAN specification exactly.
    """

    id: UUID
    ts: datetime
    kind: str  # "intention", "action", "memory_write", "reward", "breakthrough"
    lane: str  # "experimental", "candidate", "prod"
    glyph_id: UUID  # GLYPH identity for traceability
    payload: Dict[str, Any]

    @classmethod
    def create(
        cls,
        kind: str,
        lane: str,
        glyph_id: UUID,
        payload: Dict[str, Any],
        *,
        ts: Optional[datetime] = None,
        event_id: Optional[UUID] = None,
    ) -> Event:
        """Create a new event with automatic ID and timestamp."""
        return cls(
            id=event_id or uuid4(),
            ts=ts or datetime.utcnow(),
            kind=kind,
            lane=lane,
            glyph_id=glyph_id,
            payload=payload.copy() if payload else {},
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "id": str(self.id),
            "ts": self.ts.isoformat(),
            "kind": self.kind,
            "lane": self.lane,
            "glyph_id": str(self.glyph_id),
            "payload": self.payload,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Event:
        """Restore event from dictionary."""
        return cls(
            id=UUID(data["id"]),
            ts=datetime.fromisoformat(data["ts"]),
            kind=data["kind"],
            lane=data["lane"],
            glyph_id=UUID(data["glyph_id"]),
            payload=data["payload"],
        )


class EventStore:
    """
    In-memory event store with sliding window queries for experience replay.

    Thread-safe with bounded capacity to prevent unbounded growth.
    Optimized for recent event queries and glyph-based replay.
    """

    def __init__(self, max_capacity: int = 10000):
        """Initialize event store with bounded capacity."""
        self.max_capacity = max_capacity
        self.events: deque[Event] = deque(maxlen=max_capacity)
        self.lane = os.getenv("LUKHAS_LANE", "experimental").lower()
        self._lock = threading.RLock()

        # Indexes for fast lookups
        self._glyph_index: Dict[UUID, List[Event]] = {}
        self._kind_index: Dict[str, List[Event]] = {}

    def append(self, event: Event) -> None:
        """Append event to store with automatic indexing and metrics."""
        with self._lock:
            # Add to main store (deque handles capacity automatically)
            if len(self.events) == self.max_capacity:
                # Remove old event from indexes
                old_event = self.events[0]
                self._remove_from_indexes(old_event)

            self.events.append(event)
            self._add_to_indexes(event)

            # Update metrics
            if PROM:
                EVENTS_APPENDED.labels(kind=event.kind, lane=event.lane).inc()
                STORE_SIZE.set(len(self.events))

    def query_recent(
        self, limit: int = 100, kind: Optional[str] = None, lane: Optional[str] = None, since: Optional[datetime] = None
    ) -> List[Event]:
        """Query recent events with optional filtering."""
        query_type = f"recent_{kind or 'all'}_{lane or 'all'}"

        with QUERY_DURATION.labels(query_type=query_type).time() if PROM else _DummyTimer():
            with self._lock:
                if PROM:
                    EVENTS_QUERIED.labels(query_type=query_type).inc()

                # Start with all events (most recent first)
                candidates = list(reversed(self.events))

                # Apply filters
                if kind:
                    candidates = [e for e in candidates if e.kind == kind]
                if lane:
                    candidates = [e for e in candidates if e.lane == lane]
                if since:
                    candidates = [e for e in candidates if e.ts >= since]

                return candidates[:limit]

    def query_by_glyph(self, glyph_id: UUID, limit: int = 100, since: Optional[datetime] = None) -> List[Event]:
        """Query events for specific glyph ID (for replay)."""
        query_type = "by_glyph"

        with QUERY_DURATION.labels(query_type=query_type).time() if PROM else _DummyTimer():
            with self._lock:
                if PROM:
                    EVENTS_QUERIED.labels(query_type=query_type).inc()

                # Use glyph index for efficient lookup
                candidates = self._glyph_index.get(glyph_id, [])

                # Apply time filter
                if since:
                    candidates = [e for e in candidates if e.ts >= since]

                # Sort by timestamp (most recent first) and limit
                candidates.sort(key=lambda e: e.ts, reverse=True)
                return candidates[:limit]

    def query_sliding_window(
        self, window_seconds: int = 300, kind: Optional[str] = None  # 5 minutes default
    ) -> List[Event]:
        """Query events within sliding time window for replay analysis."""
        since = datetime.utcnow() - timedelta(seconds=window_seconds)
        return self.query_recent(limit=1000, kind=kind, since=since)

    def replay_sequence(self, glyph_id: UUID, max_events: int = 1000) -> Iterator[Event]:
        """Generate replay sequence for specific glyph (chronological order)."""
        events = self.query_by_glyph(glyph_id, limit=max_events)
        # Reverse to get chronological order (oldest first)
        yield from reversed(events)

    def get_stats(self) -> Dict[str, Any]:
        """Get store statistics for monitoring."""
        with self._lock:
            return {
                "total_events": len(self.events),
                "capacity": self.max_capacity,
                "utilization": len(self.events) / self.max_capacity,
                "unique_glyphs": len(self._glyph_index),
                "unique_kinds": len(self._kind_index),
                "lane": self.lane,
            }

    def _add_to_indexes(self, event: Event) -> None:
        """Add event to lookup indexes."""
        # Glyph index
        if event.glyph_id not in self._glyph_index:
            self._glyph_index[event.glyph_id] = []
        self._glyph_index[event.glyph_id].append(event)

        # Kind index
        if event.kind not in self._kind_index:
            self._kind_index[event.kind] = []
        self._kind_index[event.kind].append(event)

    def _remove_from_indexes(self, event: Event) -> None:
        """Remove event from lookup indexes."""
        # Glyph index
        if event.glyph_id in self._glyph_index:
            glyph_events = self._glyph_index[event.glyph_id]
            if event in glyph_events:
                glyph_events.remove(event)
            if not glyph_events:
                del self._glyph_index[event.glyph_id]

        # Kind index
        if event.kind in self._kind_index:
            kind_events = self._kind_index[event.kind]
            if event in kind_events:
                kind_events.remove(event)
            if not kind_events:
                del self._kind_index[event.kind]

    def clear(self) -> None:
        """Clear all events (for testing)."""
        with self._lock:
            self.events.clear()
            self._glyph_index.clear()
            self._kind_index.clear()
            if PROM:
                STORE_SIZE.set(0)


class _DummyTimer:
    """No-op context manager when Prometheus is unavailable."""

    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass


# Global event store instance
_global_store: Optional[EventStore] = None
_store_lock = threading.Lock()


def get_event_store() -> EventStore:
    """Get global event store instance (singleton pattern)."""
    global _global_store
    if _global_store is None:
        with _store_lock:
            if _global_store is None:
                capacity = int(os.getenv("LUKHAS_EVENT_STORE_CAPACITY", "10000"))
                _global_store = EventStore(max_capacity=capacity)
    return _global_store


# CLI for testing
if __name__ == "__main__":
    import json
    import sys

    store = get_event_store()
    print(f"EventStore CLI (capacity={store.max_capacity})")
    print("Commands: add <kind> <payload>, recent [limit], stats, clear, quit")

    try:
        while True:
            line = input("> ").strip()
            if line.lower() in ["quit", "exit", "q"]:
                break

            parts = line.split(None, 2)
            if not parts:
                continue

            cmd = parts[0].lower()

            if cmd == "add" and len(parts) >= 2:
                kind = parts[1]
                payload_str = parts[2] if len(parts) > 2 else "{}"
                try:
                    payload = json.loads(payload_str)
                    event = Event.create(kind, store.lane, uuid4(), payload)
                    store.append(event)
                    print(f"Added event: {event.kind} at {event.ts}")
                except json.JSONDecodeError:
                    print("Error: payload must be valid JSON")
                except Exception as e:
                    print(f"Error: {e}")

            elif cmd == "recent":
                limit = int(parts[1]) if len(parts) > 1 else 10
                events = store.query_recent(limit=limit)
                print(f"Last {len(events)} events:")
                for event in events:
                    print(f"  {event.ts} [{event.kind}] {event.payload}")

            elif cmd == "stats":
                stats = store.get_stats()
                print(json.dumps(stats, indent=2))

            elif cmd == "clear":
                store.clear()
                print("Store cleared")

            else:
                print("Unknown command. Try: add, recent, stats, clear, quit")

    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
