"""Bridge module for core.event_sourcing → labs.core.event_sourcing"""
from __future__ import annotations

from labs.core.event_sourcing import EventSourcing, EventStore, source_events

__all__ = ["EventSourcing", "EventStore", "source_events"]
