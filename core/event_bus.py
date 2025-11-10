"""Bridge module for core.event_bus → labs.core.event_bus"""
from __future__ import annotations

from labs.core.event_bus import EventBus, Event, EventHandler

__all__ = ["EventBus", "Event", "EventHandler"]
