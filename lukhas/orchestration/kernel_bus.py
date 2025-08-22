"""
LUKHAS Kernel Bus - Accepted Lane Interface
===========================================

Simplified event coordination system for inter-module communication.
Feature flag: CONTEXT_BUS_ACTIVE enables full functionality.

Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""

from __future__ import annotations
import os
import uuid
import logging
from typing import Dict, Any, Optional, Callable, List
from enum import Enum
from collections import defaultdict, deque
from lukhas.observability.matriz_decorators import instrument

logger = logging.getLogger(__name__)

# Feature flag for Context Bus
CONTEXT_BUS_ACTIVE = os.environ.get("CONTEXT_BUS_ACTIVE", "false").lower() == "true"


class EventPriority(Enum):
    """Event priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class KernelBus:
    """
    Simplified kernel bus for event coordination.
    In dry_run mode, events are logged but not dispatched.
    """
    
    def __init__(self, max_history: int = 100):
        """Initialize the kernel bus"""
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._event_history: deque = deque(maxlen=max_history)
        self._metrics = {
            "events_emitted": 0,
            "events_dispatched": 0,
            "handlers_triggered": 0,
        }
        self._active = CONTEXT_BUS_ACTIVE
        logger.info(f"🌀 Kernel Bus initialized (active={self._active})")
    
    @instrument("AWARENESS", label="orchestration:emit", capability="orchestrator:events")
    def emit(
        self,
        event: str,
        payload: Dict[str, Any],
        *,
        source: str = "unknown",
        priority: EventPriority = EventPriority.NORMAL,
        correlation_id: Optional[str] = None,
        mode: str = "dry_run",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Emit an event to the kernel bus.
        
        Args:
            event: Event type/name
            payload: Event data
            source: Source module
            priority: Event priority
            correlation_id: Correlation ID
            mode: "dry_run" or "live"
            
        Returns:
            Event emission result
        """
        event_id = str(uuid.uuid4())
        
        # Create event record
        event_record = {
            "event_id": event_id,
            "event": event,
            "payload": payload,
            "source": source,
            "priority": priority.value,
            "correlation_id": correlation_id,
        }
        
        # Track in history
        self._event_history.append(event_record)
        self._metrics["events_emitted"] += 1
        
        if mode != "dry_run" and self._active:
            # Dispatch to subscribers
            dispatched = self._dispatch_event(event, event_record)
            self._metrics["events_dispatched"] += dispatched
            
            logger.debug(f"📤 Emitted: {event} from {source} to {dispatched} handlers")
            
            return {
                "ok": True,
                "event_id": event_id,
                "dispatched": dispatched,
                "mode": "live"
            }
        
        return {
            "ok": True,
            "event_id": event_id,
            "dispatched": 0,
            "mode": "dry_run"
        }
    
    @instrument("DECISION", label="orchestration:subscribe", capability="orchestrator:events")
    def subscribe(
        self,
        event: str,
        callback: Callable,
        *,
        mode: str = "dry_run",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Subscribe to an event type.
        
        Args:
            event: Event type to subscribe to
            callback: Handler function
            mode: "dry_run" or "live"
            
        Returns:
            Subscription result
        """
        if mode != "dry_run" and self._active:
            self._subscribers[event].append(callback)
            logger.debug(f"📥 Subscribed to: {event}")
            
            return {
                "ok": True,
                "event": event,
                "subscribers": len(self._subscribers[event]),
                "mode": "live"
            }
        
        return {
            "ok": True,
            "event": event,
            "subscribers": 0,
            "mode": "dry_run"
        }
    
    @instrument("AWARENESS", label="orchestration:status", capability="orchestrator:monitor")
    def get_status(self, *, mode: str = "dry_run", **kwargs) -> Dict[str, Any]:
        """
        Get kernel bus status and metrics.
        
        Returns:
            Status information
        """
        return {
            "ok": True,
            "active": self._active and mode != "dry_run",
            "metrics": self._metrics.copy(),
            "subscribers": {event: len(handlers) for event, handlers in self._subscribers.items()},
            "history_size": len(self._event_history),
            "mode": mode
        }
    
    def _dispatch_event(self, event: str, event_record: Dict[str, Any]) -> int:
        """
        Dispatch event to subscribers.
        
        Args:
            event: Event type
            event_record: Full event record
            
        Returns:
            Number of handlers triggered
        """
        handlers = self._subscribers.get(event, [])
        
        for handler in handlers:
            try:
                handler(event_record)
                self._metrics["handlers_triggered"] += 1
            except Exception as e:
                logger.error(f"Handler error for {event}: {e}")
        
        return len(handlers)


# Global instance (lazy initialization)
_kernel_bus_instance: Optional[KernelBus] = None


def get_kernel_bus() -> KernelBus:
    """Get or create the global kernel bus instance"""
    global _kernel_bus_instance
    if _kernel_bus_instance is None:
        _kernel_bus_instance = KernelBus()
    return _kernel_bus_instance


@instrument("AWARENESS", label="orchestration:emit_global", capability="orchestrator:events")
def emit(event: str, payload: Dict[str, Any], *, mode: str = "dry_run", **kwargs) -> Dict[str, Any]:
    """
    Emit an event to the global kernel bus.
    
    Args:
        event: Event type
        payload: Event data
        mode: "dry_run" or "live"
        
    Returns:
        Event emission result
    """
    bus = get_kernel_bus()
    return bus.emit(event, payload, mode=mode, **kwargs)


@instrument("DECISION", label="orchestration:subscribe_global", capability="orchestrator:events")
def subscribe(event: str, callback: Callable, *, mode: str = "dry_run", **kwargs) -> Dict[str, Any]:
    """
    Subscribe to an event on the global kernel bus.
    
    Args:
        event: Event type
        callback: Handler function
        mode: "dry_run" or "live"
        
    Returns:
        Subscription result
    """
    bus = get_kernel_bus()
    return bus.subscribe(event, callback, mode=mode, **kwargs)