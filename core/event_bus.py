"""Bridge module for core.event_bus → labs.core.event_bus"""
from __future__ import annotations

from labs.core.event_bus import Event, EventBus, EventHandler

__all__ = ["Event", "EventBus", "EventHandler"]
