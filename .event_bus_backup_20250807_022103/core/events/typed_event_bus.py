"""
Enhanced Event Bus with Typed Domain Events
Professional event-driven architecture implementation
"""

import asyncio
import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union

from core.container.service_container import ServiceLifetime, injectable
from core.events.contracts import (
    DomainEvent,
    EventPriority,
)

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=DomainEvent)

@dataclass
class EventSubscription:
    """Represents a subscription to an event type"""
    event_type: Type[DomainEvent]
    handler: Callable[[DomainEvent], Union[None, asyncio.Future]]
    filter_func: Optional[Callable[[DomainEvent], bool]] = None
    subscription_id: str = ""

class TypedEventBus:
    """Enhanced event bus with strong typing and domain event support"""

    def __init__(self):
        self._subscribers: Dict[Type[DomainEvent], List[EventSubscription]] = defaultdict(list)
        self._event_queue: asyncio.Queue[DomainEvent] = asyncio.Queue()
        self._priority_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self._worker_task: Optional[asyncio.Task] = None
        self._priority_worker_task: Optional[asyncio.Task] = None
        self._is_running = False

        # Event tracking
        self._event_history: List[DomainEvent] = []
        self._correlation_tracking: Dict[str, List[DomainEvent]] = defaultdict(list)

        # Statistics
        self._events_published = 0
        self._events_processed = 0
        self._events_failed = 0

    async def start(self) -> None:
        """Start the event bus workers"""
        if not self._is_running:
            self._is_running = True
            self._worker_task = asyncio.create_task(self._process_events())
            self._priority_worker_task = asyncio.create_task(self._process_priority_events())
            logger.info("Typed event bus started")

    async def stop(self) -> None:
        """Stop the event bus workers"""
        self._is_running = False

        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass

        if self._priority_worker_task:
            self._priority_worker_task.cancel()
            try:
                await self._priority_worker_task
            except asyncio.CancelledError:
                pass

        logger.info("Typed event bus stopped")

    def subscribe(
        self,
        event_type: Type[T],
        handler: Callable[[T], Union[None, asyncio.Future]],
        filter_func: Optional[Callable[[T], bool]] = None
    ) -> str:
        """Subscribe to a specific event type with type safety"""
        subscription_id = f"sub_{event_type.__name__}_{id(handler)}"

        subscription = EventSubscription(
            event_type=event_type,
            handler=handler,
            filter_func=filter_func,
            subscription_id=subscription_id
        )

        self._subscribers[event_type].append(subscription)
        logger.debug(f"Subscribed to {event_type.__name__} with ID {subscription_id}")

        return subscription_id

    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe using subscription ID"""
        for event_type, subscriptions in self._subscribers.items():
            for i, sub in enumerate(subscriptions):
                if sub.subscription_id == subscription_id:
                    subscriptions.pop(i)
                    logger.debug(f"Unsubscribed {subscription_id}")
                    return True
        return False

    async def publish(self, event: DomainEvent) -> None:
        """Publish a typed domain event"""
        # Set metadata if not already set
        if not event.event_id:
            event.event_id = f"evt_{event.__class__.__name__}_{datetime.now().timestamp()}"
        if not event.timestamp:
            event.timestamp = datetime.now()

        self._events_published += 1

        # Track correlations
        if event.correlation_id:
            self._correlation_tracking[event.correlation_id].append(event)

        # Add to history
        self._event_history.append(event)
        if len(self._event_history) > 1000:
            self._event_history = self._event_history[-1000:]

        # Route by priority
        if event.priority >= EventPriority.HIGH:
            await self._priority_queue.put((event.priority.value, event))
        else:
            await self._event_queue.put(event)

        logger.debug(f"Published {event.__class__.__name__} with ID {event.event_id}")

    async def _process_events(self) -> None:
        """Process regular priority events"""
        while self._is_running:
            try:
                event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)
                await self._dispatch_event(event)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing event: {e}")
                self._events_failed += 1

    async def _process_priority_events(self) -> None:
        """Process high priority events"""
        while self._is_running:
            try:
                _, event = await asyncio.wait_for(self._priority_queue.get(), timeout=1.0)
                await self._dispatch_event(event)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing priority event: {e}")
                self._events_failed += 1

    async def _dispatch_event(self, event: DomainEvent) -> None:
        """Dispatch event to all matching subscribers"""
        event_type = type(event)

        # Get exact match subscribers
        subscribers = self._subscribers.get(event_type, [])

        # Also check parent classes for inheritance-based subscriptions
        for base_class in event_type.__mro__:
            if base_class in self._subscribers and base_class != event_type:
                subscribers.extend(self._subscribers[base_class])

        for subscription in subscribers:
            try:
                # Apply filter if present
                if subscription.filter_func and not subscription.filter_func(event):
                    continue

                # Call handler
                if asyncio.iscoroutinefunction(subscription.handler):
                    await subscription.handler(event)
                else:
                    subscription.handler(event)

            except Exception as e:
                logger.error(f"Error in event handler for {event_type.__name__}: {e}")
                self._events_failed += 1

        self._events_processed += 1

    def get_event_history(
        self,
        event_type: Optional[Type[DomainEvent]] = None,
        correlation_id: Optional[str] = None,
        limit: int = 100
    ) -> List[DomainEvent]:
        """Get event history with filtering"""
        events = self._event_history

        if event_type:
            events = [e for e in events if isinstance(e, event_type)]

        if correlation_id:
            events = [e for e in events if e.correlation_id == correlation_id]

        return events[-limit:]

    def get_statistics(self) -> Dict[str, Any]:
        """Get event bus statistics"""
        return {
            "events_published": self._events_published,
            "events_processed": self._events_processed,
            "events_failed": self._events_failed,
            "success_rate": self._events_processed / max(1, self._events_processed + self._events_failed),
            "subscriber_count": sum(len(subs) for subs in self._subscribers.values()),
            "event_types_subscribed": len(self._subscribers),
            "correlation_groups": len(self._correlation_tracking),
            "history_size": len(self._event_history)
        }

@injectable(ServiceLifetime.SINGLETON)
class EventBusService:
    """Service wrapper for typed event bus"""

    def __init__(self):
        self._event_bus = TypedEventBus()
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the event bus service"""
        if not self._initialized:
            await self._event_bus.start()
            self._initialized = True

    async def shutdown(self) -> None:
        """Shutdown the event bus service"""
        if self._initialized:
            await self._event_bus.stop()
            self._initialized = False

    def get_health(self) -> Dict[str, Any]:
        """Get service health"""
        stats = self._event_bus.get_statistics() if self._initialized else {}
        return {
            "status": "healthy" if self._initialized else "stopped",
            "initialized": self._initialized,
            **stats
        }

    # Delegate methods
    def subscribe(self, event_type: Type[T], handler: Callable[[T], Union[None, asyncio.Future]],
                  filter_func: Optional[Callable[[T], bool]] = None) -> str:
        return self._kernel_bus.subscribe(event_type, handler, filter_func)

    def unsubscribe(self, subscription_id: str) -> bool:
        return self._event_bus.unsubscribe(subscription_id)

    async def publish(self, event: DomainEvent) -> None:
        await self._kernel_bus.emit(event)

    def get_event_history(self, event_type: Optional[Type[DomainEvent]] = None,
                         correlation_id: Optional[str] = None, limit: int = 100) -> List[DomainEvent]:
        return self._event_bus.get_event_history(event_type, correlation_id, limit)

# Global instance
_global_typed_event_bus: Optional[EventBusService] = None

def get_typed_event_bus() -> EventBusService:
    """Get the global typed event bus instance"""
    global _global_typed_event_bus
    if _global_typed_event_bus is None:
        _global_typed_event_bus = EventBusService()
    return _global_typed_event_bus

# Convenience decorators for event handlers
def event_handler(event_type: Type[DomainEvent]):
    """Decorator for marking event handlers"""
    def decorator(func: Callable[[DomainEvent], Union[None, asyncio.Future]]):
        # Add metadata to function
        func._event_handler_type = event_type
        return func
    return decorator

def auto_subscribe_handlers(obj: Any, event_bus: EventBusService) -> List[str]:
    """Automatically subscribe all @event_handler decorated methods of an object"""
    subscription_ids = []

    for attr_name in dir(obj):
        attr = getattr(obj, attr_name)
        if callable(attr) and hasattr(attr, '_event_handler_type'):
            event_type = attr._event_handler_type
            subscription_id = kernel_bus.subscribe(event_type, attr)
            subscription_ids.append(subscription_id)
            logger.info(f"Auto-subscribed {obj.__class__.__name__}.{attr_name} to {event_type.__name__}")

    return subscription_ids

# Neuroplastic tags
#TAG:core
#TAG:events
#TAG:typed
#TAG:professional_architecture
