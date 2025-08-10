"""
Enhanced Event Bus System for NIΛS
Supports dream coordination, priority queues, and correlation tracking

This is adapted from the lukhas-pwm-advanced event bus system
specifically for the Lambda Products NIAS implementation.
"""

import asyncio
import logging
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class NIASEventType(Enum):
    """NIAS-specific event types for message delivery and processing"""

    # Message Processing Events
    MESSAGE_RECEIVED = "message_received"
    MESSAGE_FILTERED = "message_filtered"
    MESSAGE_DELIVERED = "message_delivered"
    MESSAGE_DEFERRED = "message_deferred"
    MESSAGE_BLOCKED = "message_blocked"

    # User Interaction Events
    USER_CONSENT_GRANTED = "user_consent_granted"
    USER_CONSENT_WITHDRAWN = "user_consent_withdrawn"
    USER_TIER_CHANGED = "user_tier_changed"
    USER_FEEDBACK_RECEIVED = "user_feedback_received"

    # Widget Events
    WIDGET_DISPLAYED = "widget_displayed"
    WIDGET_INTERACTED = "widget_interacted"
    WIDGET_DISMISSED = "widget_dismissed"

    # Dream Integration Events
    DREAM_SEED_PLANTED = "dream_seed_planted"
    DREAM_NARRATIVE_GENERATED = "dream_narrative_generated"
    DREAM_SYMBOLS_EXTRACTED = "dream_symbols_extracted"

    # Revenue Events
    SUBSCRIPTION_ACTIVATED = "subscription_activated"
    SUBSCRIPTION_CANCELLED = "subscription_cancelled"
    REVENUE_GENERATED = "revenue_generated"

    # System Events
    NIAS_STARTED = "nias_started"
    NIAS_STOPPED = "nias_stopped"
    ERROR_OCCURRED = "error_occurred"


@dataclass
class Event:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    source: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

    # NIAS-specific fields
    priority: int = 1  # 1=low, 5=critical
    correlation_id: Optional[str] = None  # For tracking related events
    user_id: Optional[str] = None  # User context
    tier: Optional[str] = None  # User tier (T1, T2, T3)

    # Processing metadata
    processed: bool = False
    retry_count: int = 0
    max_retries: int = 3


class NIASEventBus:
    """Enhanced event bus specifically designed for NIAS message processing"""

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._queue = asyncio.Queue()
        self._priority_queue = asyncio.PriorityQueue()
        self._worker_task: Optional[asyncio.Task] = None
        self._priority_worker_task: Optional[asyncio.Task] = None

        # NIAS-specific tracking
        self._user_event_history: Dict[str, List[Event]] = defaultdict(list)
        self._correlation_tracking: Dict[str, List[Event]] = defaultdict(list)
        self._message_delivery_stats: Dict[str, Dict] = defaultdict(dict)
        self._event_filters: Dict[str, Callable] = {}

        # Performance metrics
        self._events_processed = 0
        self._events_failed = 0
        self._messages_delivered = 0
        self._messages_blocked = 0
        self._start_time = time.time()

        logger.info("NIAS Event Bus initialized")

    async def start(self):
        """Start the event bus workers"""
        if self._worker_task is None:
            self._worker_task = asyncio.create_task(self._worker())
        if self._priority_worker_task is None:
            self._priority_worker_task = asyncio.create_task(self._priority_worker())

        await self.publish(
            event_type=NIASEventType.NIAS_STARTED.value,
            payload={"start_time": datetime.now(timezone.utc).isoformat()},
            source="nias_event_bus",
        )

    def subscribe(
        self,
        event_type: str,
        callback: Callable,
        filter_func: Optional[Callable] = None,
    ):
        """Subscribe to an event type with optional filtering"""
        self._subscribers[event_type].append(callback)
        if filter_func:
            self._event_filters[f"{event_type}:{id(callback)}"] = filter_func

        logger.debug(f"Subscribed to {event_type}")

    def unsubscribe(self, event_type: str, callback: Callable):
        """Unsubscribe from an event type"""
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(callback)
            except ValueError:
                pass

        # Remove associated filter
        filter_key = f"{event_type}:{id(callback)}"
        if filter_key in self._event_filters:
            del self._event_filters[filter_key]

    async def publish(
        self,
        event_type: str,
        payload: Dict[str, Any],
        source: Optional[str] = None,
        priority: int = 1,
        correlation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        tier: Optional[str] = None,
    ):
        """Publish an event with NIAS-specific features"""
        event = Event(
            event_type=event_type,
            payload=payload,
            source=source,
            priority=priority,
            correlation_id=correlation_id,
            user_id=user_id,
            tier=tier,
        )

        # Route to appropriate queue based on priority
        if priority >= 4:  # High priority events
            await self._priority_queue.put((10 - priority, event))
        else:
            await self._queue.put(event)

        # Track user-specific events
        if user_id:
            self._user_event_history[user_id].append(event)
            # Keep only recent events per user (last 100)
            if len(self._user_event_history[user_id]) > 100:
                self._user_event_history[user_id] = self._user_event_history[user_id][
                    -100:
                ]

        # Track correlated events
        if correlation_id:
            self._correlation_tracking[correlation_id].append(event)

    async def publish_nias_event(
        self,
        nias_event_type: NIASEventType,
        payload: Dict[str, Any],
        user_id: Optional[str] = None,
        tier: Optional[str] = None,
        source: Optional[str] = None,
        correlation_id: Optional[str] = None,
        priority: int = 2,
    ):
        """Publish a NIAS-specific event with automatic tracking"""
        await self.publish(
            event_type=nias_event_type.value,
            payload=payload,
            source=source or "nias_core",
            priority=priority,
            correlation_id=correlation_id,
            user_id=user_id,
            tier=tier,
        )

    async def start_message_processing(
        self, message_id: str, user_id: str, message_data: Dict[str, Any]
    ) -> str:
        """Start coordinated message processing session"""
        correlation_id = f"msg_processing_{message_id}_{uuid.uuid4().hex[:8]}"

        await self.publish_nias_event(
            NIASEventType.MESSAGE_RECEIVED,
            payload={
                "message_id": message_id,
                "message_data": message_data,
                "processing_start": datetime.now(timezone.utc).isoformat(),
            },
            user_id=user_id,
            correlation_id=correlation_id,
            priority=3,
        )

        logger.info(
            f"Message processing started: {message_id} (correlation: {correlation_id})"
        )
        return correlation_id

    async def complete_message_processing(
        self,
        message_id: str,
        correlation_id: str,
        result: Dict[str, Any],
        user_id: Optional[str] = None,
    ):
        """Complete coordinated message processing session"""
        # Gather processing statistics
        correlation_events = self._correlation_tracking.get(correlation_id, [])

        processing_stats = {
            "total_events": len(correlation_events),
            "processing_duration": None,
            "delivery_status": result.get("status", "unknown"),
        }

        # Calculate processing duration
        if correlation_events:
            start_time = min(event.timestamp for event in correlation_events)
            end_time = max(event.timestamp for event in correlation_events)
            processing_stats["processing_duration"] = end_time - start_time

        # Update delivery stats
        if result.get("status") == "delivered":
            self._messages_delivered += 1
        elif result.get("status") == "blocked":
            self._messages_blocked += 1

        # Publish completion event
        await self.publish_nias_event(
            (
                NIASEventType.MESSAGE_DELIVERED
                if result.get("status") == "delivered"
                else NIASEventType.MESSAGE_BLOCKED
            ),
            payload={
                "message_id": message_id,
                "result": result,
                "processing_stats": processing_stats,
                "completion_time": datetime.now(timezone.utc).isoformat(),
            },
            user_id=user_id,
            correlation_id=correlation_id,
            priority=3,
        )

        logger.info(f"Message processing completed: {message_id}")

    async def get_user_events(self, user_id: str, limit: int = 50) -> List[Event]:
        """Get recent events for a specific user"""
        events = self._user_event_history.get(user_id, [])
        return events[-limit:] if limit else events

    async def get_correlated_events(self, correlation_id: str) -> List[Event]:
        """Get all events with a specific correlation ID"""
        return self._correlation_tracking.get(correlation_id, [])

    def subscribe_to_nias_events(
        self,
        callback: Callable,
        nias_event_types: Optional[List[NIASEventType]] = None,
        user_id_filter: Optional[str] = None,
        tier_filter: Optional[str] = None,
    ):
        """Subscribe to NIAS events with specific filters"""
        event_types = nias_event_types or list(NIASEventType)

        for nias_event_type in event_types:
            # Create filtered callback
            def filtered_callback(event: Event, original_callback=callback):
                # Apply filters
                if user_id_filter and event.user_id != user_id_filter:
                    return
                if tier_filter and event.tier != tier_filter:
                    return

                # Call original callback
                return original_callback(event)

            self.subscribe(nias_event_type.value, filtered_callback)

    async def _worker(self):
        """Worker to process regular priority events from the queue"""
        while True:
            try:
                event = await self._queue.get()
                await self._process_event(event)
                self._queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in event worker: {e}")

    async def _priority_worker(self):
        """Worker to process high priority events from the priority queue"""
        while True:
            try:
                priority, event = await self._priority_queue.get()
                await self._process_event(event)
                self._priority_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in priority event worker: {e}")

    async def _process_event(self, event: Event):
        """Process a single event through all subscribers"""
        try:
            if event.event_type in self._subscribers:
                for callback in self._subscribers[event.event_type]:
                    try:
                        # Check for event filter
                        filter_key = f"{event.event_type}:{id(callback)}"
                        if filter_key in self._event_filters:
                            if not self._event_filters[filter_key](event):
                                continue  # Skip this callback due to filter

                        # Execute callback
                        if asyncio.iscoroutinefunction(callback):
                            await callback(event)
                        else:
                            callback(event)

                        event.processed = True

                    except Exception as e:
                        logger.error(
                            f"Error in event handler for {event.event_type}: {e}"
                        )
                        self._events_failed += 1

                        # Retry logic for critical events
                        if (
                            event.priority >= 4
                            and event.retry_count < event.max_retries
                        ):
                            event.retry_count += 1
                            await asyncio.sleep(
                                2**event.retry_count
                            )  # Exponential backoff
                            await self._priority_queue.put((10 - event.priority, event))
                            return

            self._events_processed += 1

        except Exception as e:
            logger.error(f"Error processing event {event.event_id}: {e}")
            self._events_failed += 1

    async def stop(self):
        """Stop the event bus workers"""
        await self.publish(
            event_type=NIASEventType.NIAS_STOPPED.value,
            payload={"stop_time": datetime.now(timezone.utc).isoformat()},
            source="nias_event_bus",
        )

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

    def get_nias_stats(self) -> Dict[str, Any]:
        """Get comprehensive NIAS event bus statistics"""
        uptime = time.time() - self._start_time

        return {
            "uptime_seconds": uptime,
            "events_processed": self._events_processed,
            "events_failed": self._events_failed,
            "messages_delivered": self._messages_delivered,
            "messages_blocked": self._messages_blocked,
            "delivery_rate": (
                self._messages_delivered
                / max(1, self._messages_delivered + self._messages_blocked)
            ),
            "success_rate": (
                self._events_processed
                / max(1, self._events_processed + self._events_failed)
            ),
            "active_users": len(self._user_event_history),
            "active_correlations": len(self._correlation_tracking),
            "subscriber_count": sum(
                len(callbacks) for callbacks in self._subscribers.values()
            ),
            "unique_event_types": len(self._subscribers),
            "average_events_per_second": self._events_processed / max(1, uptime),
        }


# Global NIAS event bus instance
_global_nias_event_bus = None


async def get_global_nias_event_bus() -> NIASEventBus:
    """Get the global NIAS event bus instance"""
    global _global_nias_event_bus
    if _global_nias_event_bus is None:
        _global_nias_event_bus = NIASEventBus()
        await _global_nias_event_bus.start()
    return _global_nias_event_bus
