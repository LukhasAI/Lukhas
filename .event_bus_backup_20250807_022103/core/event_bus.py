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


class DreamEventType(Enum):
    """Specialized dream event types for enhanced coordination"""
    DREAM_CYCLE_START = "dream_cycle_start"
    DREAM_CYCLE_COMPLETE = "dream_cycle_complete"
    DREAM_PROCESSING_START = "dream_processing_start"
    DREAM_PROCESSING_COMPLETE = "dream_processing_complete"
    MULTIVERSE_SIMULATION_START = "multiverse_simulation_start"
    MULTIVERSE_SIMULATION_COMPLETE = "multiverse_simulation_complete"
    COLONY_DREAM_TASK_CREATED = "colony_dream_task_created"
    COLONY_DREAM_RESULT = "colony_dream_result"
    DREAM_CONSENSUS_REACHED = "dream_consensus_reached"
    DREAM_ETHICAL_REVIEW = "dream_ethical_review"
    DREAM_PRIVACY_VALIDATION = "dream_privacy_validation"
    DREAM_MEMORY_INTEGRATION = "dream_memory_integration"
    DREAM_INSIGHT_GENERATED = "dream_insight_generated"
    DREAM_ERROR_OCCURRED = "dream_error_occurred"


@dataclass
class Event:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    source: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    # Enhanced fields for dream coordination
    priority: int = 1  # 1=low, 5=high
    correlation_id: Optional[str] = None  # For tracking related events
    dream_id: Optional[str] = None  # For dream-specific events
    user_id: Optional[str] = None  # For user-specific events


class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._queue = asyncio.Queue()
        self._priority_queue = asyncio.PriorityQueue()
        self._worker_task: Optional[asyncio.Task] = None
        self._priority_worker_task: Optional[asyncio.Task] = None

        # Dream-specific enhancements
        self._dream_event_history: List[Event] = []
        self._correlation_tracking: Dict[str, List[Event]] = defaultdict(list)
        self._dream_session_events: Dict[str, List[Event]] = defaultdict(list)
        self._event_filters: Dict[str, Callable] = {}

        # Performance metrics
        self._events_processed = 0
        self._events_failed = 0
        self._start_time = time.time()

    async def start(self):
        """Start the event bus workers."""
        if self._worker_task is None:
            self._worker_task = asyncio.create_task(self._worker())
        if self._priority_worker_task is None:
            self._priority_worker_task = asyncio.create_task(self._priority_worker())

    def subscribe(self, event_type: str, callback: Callable, filter_func: Optional[Callable] = None):
        """Subscribe to an event type with optional filtering."""
        self._subscribers[event_type].append(callback)
        if filter_func:
            self._event_filters[f"{event_type}:{id(callback)}"] = filter_func

    def unsubscribe(self, event_type: str, callback: Callable):
        """Unsubscribe from an event type."""
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(callback)

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
        dream_id: Optional[str] = None,
        user_id: Optional[str] = None
    ):
        """Publish an event with enhanced dream coordination features."""
        event = Event(
            event_type=event_type,
            payload=payload,
            source=source,
            priority=priority,
            correlation_id=correlation_id,
            dream_id=dream_id,
            user_id=user_id
        )

        # Route to appropriate queue based on priority
        if priority >= 4:  # High priority events
            await self._priority_queue.put((10 - priority, event))
        else:
            await self._queue.put(event)

        # Track dream-related events
        if dream_id:
            self._dream_session_events[dream_id].append(event)

        # Track correlated events
        if correlation_id:
            self._correlation_tracking[correlation_id].append(event)

        # Maintain event history for dream processing
        if event_type.startswith('dream_') or event_type in [dt.value for dt in DreamEventType]:
            self._dream_event_history.append(event)
            # Keep only recent dream events (last 1000)
            if len(self._dream_event_history) > 1000:
                self._dream_event_history = self._dream_event_history[-1000:]

    async def publish_dream_event(
        self,
        dream_event_type: DreamEventType,
        dream_id: str,
        payload: Dict[str, Any],
        source: Optional[str] = None,
        correlation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        priority: int = 3
    ):
        """Publish a dream-specific event with automatic coordination features."""
        await self.publish(
            event_type=dream_event_type.value,
            payload=payload,
            source=source,
            priority=priority,
            correlation_id=correlation_id,
            dream_id=dream_id,
            user_id=user_id
        )

    async def start_dream_coordination(
        self,
        dream_id: str,
        dream_type: str,
        user_id: Optional[str] = None,
        coordination_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Start coordinated dream processing session."""
        correlation_id = f"dream_coordination_{dream_id}_{uuid.uuid4().hex[:8]}"

        # Publish dream coordination start event
        await self.publish_dream_event(
            DreamEventType.DREAM_CYCLE_START,
            dream_id=dream_id,
            payload={
                "dream_type": dream_type,
                "coordination_metadata": coordination_metadata or {},
                "session_start": datetime.now(timezone.utc).isoformat()
            },
            correlation_id=correlation_id,
            user_id=user_id,
            priority=4
        )

        logger.info(f"Dream coordination started: {dream_id} (correlation: {correlation_id})")
        return correlation_id

    async def complete_dream_coordination(
        self,
        dream_id: str,
        correlation_id: str,
        dream_result: Dict[str, Any],
        user_id: Optional[str] = None
    ):
        """Complete coordinated dream processing session."""
        # Gather session statistics
        session_events = self._dream_session_events.get(dream_id, [])
        correlation_events = self._correlation_tracking.get(correlation_id, [])

        session_stats = {
            "total_events": len(session_events),
            "correlation_events": len(correlation_events),
            "session_duration": None,
            "processing_stages": []
        }

        # Calculate session duration
        if session_events:
            start_time = min(event.timestamp for event in session_events)
            end_time = max(event.timestamp for event in session_events)
            session_stats["session_duration"] = end_time - start_time

        # Identify processing stages
        stage_events = [
            DreamEventType.DREAM_PROCESSING_START.value,
            DreamEventType.MULTIVERSE_SIMULATION_START.value,
            DreamEventType.COLONY_DREAM_TASK_CREATED.value,
            DreamEventType.DREAM_ETHICAL_REVIEW.value,
            DreamEventType.DREAM_PRIVACY_VALIDATION.value
        ]

        session_stats["processing_stages"] = [
            event.event_type for event in session_events
            if event.event_type in stage_events
        ]

        # Publish completion event
        await self.publish_dream_event(
            DreamEventType.DREAM_CYCLE_COMPLETE,
            dream_id=dream_id,
            payload={
                "dream_result": dream_result,
                "session_stats": session_stats,
                "completion_time": datetime.now(timezone.utc).isoformat()
            },
            correlation_id=correlation_id,
            user_id=user_id,
            priority=4
        )

        logger.info(f"Dream coordination completed: {dream_id}")

    async def get_dream_session_events(self, dream_id: str) -> List[Event]:
        """Get all events for a specific dream session."""
        return self._dream_session_events.get(dream_id, [])

    async def get_correlated_events(self, correlation_id: str) -> List[Event]:
        """Get all events with a specific correlation ID."""
        return self._correlation_tracking.get(correlation_id, [])

    async def wait_for_dream_completion(
        self,
        dream_id: str,
        timeout_seconds: float = 300.0
    ) -> Optional[Event]:
        """Wait for a dream processing session to complete."""
        completion_event = None
        start_time = time.time()

        while time.time() - start_time < timeout_seconds:
            # Check for completion events
            session_events = self._dream_session_events.get(dream_id, [])
            for event in reversed(session_events):
                if event.event_type == DreamEventType.DREAM_CYCLE_COMPLETE.value:
                    completion_event = event
                    break

            if completion_event:
                break

            await asyncio.sleep(0.1)  # Small delay

        return completion_event

    def subscribe_to_dream_events(
        self,
        callback: Callable,
        dream_event_types: Optional[List[DreamEventType]] = None,
        dream_id_filter: Optional[str] = None,
        user_id_filter: Optional[str] = None
    ):
        """Subscribe to dream events with specific filters."""
        event_types = dream_event_types or list(DreamEventType)

        for dream_event_type in event_types:
            # Create filtered callback
            def filtered_callback(event: Event, original_callback=callback):
                # Apply filters
                if dream_id_filter and event.dream_id != dream_id_filter:
                    return
                if user_id_filter and event.user_id != user_id_filter:
                    return

                # Call original callback
                return original_callback(event)

            self.subscribe(dream_event_type.value, filtered_callback)

    async def _worker(self):
        """Worker to process regular priority events from the queue."""
        while True:
            try:
                event = await self._queue.get()
                await self._process_event(event)
                self._queue.task_done()
            except asyncio.CancelledError:
                break

    async def _priority_worker(self):
        """Worker to process high priority events from the priority queue."""
        while True:
            try:
                priority, event = await self._priority_queue.get()
                await self._process_event(event)
                self._priority_queue.task_done()
            except asyncio.CancelledError:
                break

    async def _process_event(self, event: Event):
        """Process a single event through all subscribers."""
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

                    except Exception as e:
                        logger.error(f"Error in event handler for {event.event_type}: {e}")
                        self._events_failed += 1

            self._events_processed += 1

        except Exception as e:
            logger.error(f"Error processing event {event.event_id}: {e}")
            self._events_failed += 1

    async def stop(self):
        """Stop the event bus workers."""
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

    def get_event_bus_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics about event bus operation."""
        uptime = time.time() - self._start_time

        return {
            "uptime_seconds": uptime,
            "events_processed": self._events_processed,
            "events_failed": self._events_failed,
            "success_rate": (
                self._events_processed / max(1, self._events_processed + self._events_failed)
            ),
            "dream_sessions_active": len(self._dream_session_events),
            "correlation_tracking_active": len(self._correlation_tracking),
            "dream_event_history_size": len(self._dream_event_history),
            "subscriber_count": sum(len(callbacks) for callbacks in self._subscribers.values()),
            "unique_event_types": len(self._subscribers),
            "average_events_per_second": self._events_processed / max(1, uptime)
        }


_global_event_bus = None


async def get_global_event_bus() -> EventBus:
    """Get the global event bus instance."""
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
        await _global_event_bus.start()
    return _global_event_bus
