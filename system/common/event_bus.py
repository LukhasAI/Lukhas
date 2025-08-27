"""
LUKHAS Event Bus
================
Centralized event system for loose module coupling.
"""

import asyncio
import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


@dataclass
class Event:
    """Base event class"""

    event_type: str
    source_module: str
    target_module: Optional[str] = None
    payload: dict[str, Any] = None
    timestamp: datetime = None
    correlation_id: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.payload is None:
            self.payload = {}


class EventBus:
    """Centralized event bus for module communication"""

    def __init__(self):
        self._subscribers: dict[str, list[Callable]] = defaultdict(list)
        self._async_subscribers: dict[str, list[Callable]] = defaultdict(list)
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        self._metrics = {
            "events_published": 0,
            "events_delivered": 0,
            "events_failed": 0,
        }

    def subscribe(self, event_type: str, handler: Callable, is_async: bool = False):
        """Subscribe to an event type"""
        if is_async:
            self._async_subscribers[event_type].append(handler)
        else:
            self._subscribers[event_type].append(handler)

        logger.info(f"Subscribed {'async ' if is_async else ''}handler to {event_type}")

    def unsubscribe(self, event_type: str, handler: Callable):
        """Unsubscribe from an event type"""
        if handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(handler)
        if handler in self._async_subscribers[event_type]:
            self._async_subscribers[event_type].remove(handler)

    async def publish(self, event: Event):
        """Publish an event"""
        await self._event_queue.put(event)
        self._metrics["events_published"] += 1

        # Process immediately if not running event loop
        if not self._running:
            await self._process_event(event)

    def publish_sync(self, event: Event):
        """Synchronously publish an event"""
        self._metrics["events_published"] += 1

        # Call sync handlers
        for handler in self._subscribers.get(event.event_type, []):
            try:
                handler(event)
                self._metrics["events_delivered"] += 1
            except Exception as e:
                logger.error(f"Error in sync handler for {event.event_type}: {e}")
                self._metrics["events_failed"] += 1

    async def _process_event(self, event: Event):
        """Process a single event"""
        # Call sync handlers
        for handler in self._subscribers.get(event.event_type, []):
            try:
                handler(event)
                self._metrics["events_delivered"] += 1
            except Exception as e:
                logger.error(f"Error in sync handler for {event.event_type}: {e}")
                self._metrics["events_failed"] += 1

        # Call async handlers
        tasks = []
        for handler in self._async_subscribers.get(event.event_type, []):
            tasks.append(self._call_async_handler(handler, event))

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Error in async handler: {result}")
                    self._metrics["events_failed"] += 1
                else:
                    self._metrics["events_delivered"] += 1

    async def _call_async_handler(self, handler: Callable, event: Event):
        """Call an async handler safely"""
        try:
            await handler(event)
        except Exception as e:
            logger.error(f"Error in async handler for {event.event_type}: {e}")
            raise

    async def start(self):
        """Start the event bus processing loop"""
        self._running = True
        logger.info("Event bus started")

        while self._running:
            try:
                # Wait for events with timeout
                event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)
                await self._process_event(event)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing event: {e}")

    async def stop(self):
        """Stop the event bus"""
        self._running = False

        # Process remaining events
        while not self._event_queue.empty():
            event = await self._event_queue.get()
            await self._process_event(event)

        logger.info("Event bus stopped")

    def get_metrics(self) -> dict[str, int]:
        """Get event bus metrics"""
        return self._metrics.copy()


# Global event bus instance
event_bus = EventBus()


# Common event types
class EventTypes:
    """Standard event types for LUKHAS modules"""

    # Core events
    MODULE_INITIALIZED = "module.initialized"
    MODULE_SHUTDOWN = "module.shutdown"

    # Consciousness events
    AWARENESS_CHANGED = "consciousness.awareness_changed"
    REFLECTION_COMPLETE = "consciousness.reflection_complete"

    # Memory events
    MEMORY_STORED = "memory.stored"
    MEMORY_RETRIEVED = "memory.retrieved"
    FOLD_CREATED = "memory.fold_created"

    # Orchestration events
    TASK_STARTED = "orchestration.task_started"
    TASK_COMPLETED = "orchestration.task_completed"
    WORKFLOW_TRIGGERED = "orchestration.workflow_triggered"

    # Governance events
    POLICY_VIOLATED = "governance.policy_violated"
    PERMISSION_GRANTED = "governance.permission_granted"
    AUDIT_LOGGED = "governance.audit_logged"

    # GLYPH events
    GLYPH_EMITTED = "glyph.emitted"
    GLYPH_PROCESSED = "glyph.processed"


# Helper functions
def emit_event(event_type: str, source: str, payload: dict[str, Any] = None):
    """Helper to emit events synchronously"""
    event = Event(event_type=event_type, source_module=source, payload=payload)
    event_bus.publish_sync(event)


async def emit_event_async(
    event_type: str, source: str, payload: dict[str, Any] = None
):
    """Helper to emit events asynchronously"""
    event = Event(event_type=event_type, source_module=source, payload=payload)
    await event_bus.publish(event)
