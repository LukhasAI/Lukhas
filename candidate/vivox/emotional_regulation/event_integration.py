import logging
import streamlit as st
import time
logger = logging.getLogger(__name__)
"""
VIVOX.ERN Event Bus Integration
Connects emotional regulation to the system-wide event architecture
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

from candidate.core.common import get_logger

# Import event system
try:
    from candidate.core.events.contracts import (
        DomainEvent,
        EmotionalRegulationApplied,
        EmotionalStateChanged,
    )
    from candidate.core.events.typed_event_bus import TypedEventBus

    EVENT_SYSTEM_AVAILABLE = True
except ImportError:
    EVENT_SYSTEM_AVAILABLE = False

    # Fallback classes for testing
    @dataclass
    class DomainEvent:
        """Fallback DomainEvent for testing"""

    @dataclass
    class EmotionalStateChanged:
        """Fallback EmotionalStateChanged for testing"""

    @dataclass
    class EmotionalRegulationApplied:
        """Fallback EmotionalRegulationApplied for testing"""


from .vivox_ern_core import RegulationResponse, VADVector

logger = get_logger(__name__)


@dataclass
class VIVOXEmotionalEvent:
    """VIVOX-specific emotional event"""

    event_id: str
    user_id: str
    event_type: str
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)


class VIVOXEmotionalShift(VIVOXEmotionalEvent):
    """VIVOX emotional state shift event"""

    def __init__(
        self,
        user_id: str,
        previous_state: VADVector = None,
        new_state: VADVector = None,
        triggers: Optional[list[str]] = None,
        context: Optional[dict[str, Any]] = None,
        # Support legacy parameter names
        original_state: VADVector = None,
        trigger: Optional[str] = None,  # Support single trigger parameter
        **kwargs,
    ):
        super().__init__(
            event_id=f"vivox_shift_{user_id}_{int(datetime.now(timezone.utc).timestamp()}",
            user_id=user_id,
            event_type="vivox_emotional_shift",
        )

        # Handle legacy parameter names
        if original_state is not None:
            previous_state = original_state

        # Handle single trigger parameter
        if trigger is not None and triggers is None:
            triggers = [trigger]

        # Set defaults for None values
        if triggers is None:
            triggers = []
        if context is None:
            context = {}

        self.previous_state = previous_state.to_dict() if previous_state else {}
        self.new_state = new_state.to_dict() if new_state else {}
        self.shift_magnitude = previous_state.distance_to(new_state) if (previous_state and new_state) else 0.0
        self.triggers = triggers
        self.vivox_context = context


class VIVOXRegulationApplied(VIVOXEmotionalEvent):
    """VIVOX regulation application event"""

    def __init__(self, user_id: str, regulation_response: RegulationResponse):
        super().__init__(
            event_id=f"vivox_regulation_{user_id}_{int(datetime.now(timezone.utc).timestamp()}",
            user_id=user_id,
            event_type="vivox_regulation_applied",
        )
        self.regulation_strategy = regulation_response.strategy_used.value
        self.effectiveness = regulation_response.effectiveness
        self.original_state = regulation_response.original_state.to_dict()
        self.regulated_state = regulation_response.regulated_state.to_dict()
        self.reasoning = regulation_response.reasoning
        self.hormone_triggers = regulation_response.hormone_triggers
        self.neuroplastic_tags = regulation_response.neuroplastic_tags
        self.duration_seconds = regulation_response.duration_seconds


class VIVOXEmotionalMemoryStored(VIVOXEmotionalEvent):
    """VIVOX emotional memory storage event"""

    def __init__(self, user_id: str, memory_data: dict[str, Any]):
        super().__init__(
            event_id=f"vivox_memory_{user_id}_{int(datetime.now(timezone.utc).timestamp()}",
            user_id=user_id,
            event_type="vivox_emotional_memory_stored",
        )
        self.memory_type = memory_data.get("type", "regulation")
        self.emotional_pattern = memory_data.get("pattern", {})
        self.learning_tags = memory_data.get("tags", [])
        self.effectiveness_score = memory_data.get("effectiveness", 0.0)
        self.context_hash = memory_data.get("context_hash", "")


class VIVOXNeuroplasticUpdate(VIVOXEmotionalEvent):
    """VIVOX neuroplastic learning update event"""

    def __init__(self, user_id: str, update_data: dict[str, Any]):
        super().__init__(
            event_id=f"vivox_neuroplastic_{user_id}_{int(datetime.now(timezone.utc).timestamp()}",
            user_id=user_id,
            event_type="vivox_neuroplastic_update",
        )
        self.update_type = update_data.get("type", "pattern_adaptation")
        self.pattern_changes = update_data.get("changes", {})
        self.learning_strength = update_data.get("strength", 0.5)
        self.colony_propagation = update_data.get("colony_propagation", False)
        self.adaptation_reason = update_data.get("reason", "")


class VIVOXEventBusIntegration:
    """
    Integration layer between VIVOX.ERN and the system event bus
    """

    def __init__(self, event_bus: Optional[TypedEventBus] = None):
        self.event_bus = event_bus
        self.event_history: list[VIVOXEmotionalEvent] = []
        self.subscribers: dict[str, list] = {}
        self.event_filters: dict[str, list] = {}

        # Performance metrics
        self.events_published = 0
        self.events_processed = 0
        self.integration_health = 1.0

        # Setup default subscriptions if event bus available
        if self.event_bus and EVENT_SYSTEM_AVAILABLE:
            self._setup_default_subscriptions()

    def _setup_default_subscriptions(self):
        """Setup default event subscriptions"""
        try:
            # Subscribe to relevant system events
            self.event_bus.subscribe(EmotionalStateChanged, self._handle_system_emotional_change)

            self.event_bus.subscribe(EmotionalRegulationApplied, self._handle_system_regulation_event)

            logger.info("VIVOX event bus subscriptions established")

        except Exception as e:
            logger.error(f"Failed to setup event subscriptions: {e}")
            self.integration_health = 0.5

    async def publish_emotional_shift(
        self,
        user_id_or_shift=None,
        previous_state: VADVector = None,
        new_state: VADVector = None,
        triggers: Optional[list[str]] = None,
        context: Optional[dict[str, Any]] = None,
        *,
        user_id: Optional[str] = None,  # Support for keyword argument
    ):
        """Publish emotional state shift event

        Can be called with either:
        1. Individual parameters: publish_emotional_shift(user_id, previous_state, new_state, triggers, context)
        2. VIVOXEmotionalShift object: publish_emotional_shift(shift)
        """
        try:
            # Handle different calling patterns
            if user_id is not None:
                # Called with user_id keyword argument
                actual_user_id = user_id
                event = VIVOXEmotionalShift(
                    user_id=actual_user_id,
                    previous_state=previous_state,
                    new_state=new_state,
                    triggers=triggers,
                    context=context,
                )
            elif isinstance(user_id_or_shift, VIVOXEmotionalShift):
                # Called with VIVOXEmotionalShift object
                event = user_id_or_shift
                actual_user_id = event.user_id
                # Extract parameters from the event for system event publishing
                if hasattr(event, "previous_state") and hasattr(event, "new_state"):
                    from .vivox_ern_core import VADVector

                    # Reconstruct VADVector from dict
                    if event.previous_state:
                        previous_state = VADVector(
                            valence=event.previous_state.get("valence", 0.0),
                            arousal=event.previous_state.get("arousal", 0.0),
                            dominance=event.previous_state.get("dominance", 0.0),
                            intensity=event.previous_state.get("intensity", 0.5),
                        )
                    else:
                        previous_state = None

                    if event.new_state:
                        new_state = VADVector(
                            valence=event.new_state.get("valence", 0.0),
                            arousal=event.new_state.get("arousal", 0.0),
                            dominance=event.new_state.get("dominance", 0.0),
                            intensity=event.new_state.get("intensity", 0.5),
                        )
                    else:
                        new_state = None

                    context = event.vivox_context or {}
            else:
                # Traditional calling pattern with positional user_id
                actual_user_id = user_id_or_shift
                event = VIVOXEmotionalShift(
                    user_id=actual_user_id,
                    previous_state=previous_state,
                    new_state=new_state,
                    triggers=triggers,
                    context=context,
                )

            await self._publish_event(event)

            # Also publish standard system event if available
            if self.event_bus and EVENT_SYSTEM_AVAILABLE and previous_state and new_state:
                system_event = EmotionalStateChanged(
                    previous_vad=previous_state.to_dict(),
                    current_vad=new_state.to_dict(),
                    trigger=str(context.get("trigger", "vivox_shift")),
                    intensity=new_state.intensity if new_state else 0.0,
                    source_module="vivox_ern",
                )
                await self.event_bus.emit(system_event)

            logger.debug(f"Published emotional shift event for user {actual_user_id}")

        except Exception as e:
            logger.error(f"Failed to publish emotional shift event: {e}")
            self.integration_health *= 0.95

    async def publish_regulation_applied(self, user_id: str, regulation_response: RegulationResponse):
        """Publish regulation application event"""
        try:
            event = VIVOXRegulationApplied(user_id=user_id, regulation_response=regulation_response)

            await self._publish_event(event)

            # Also publish standard system event if available
            if self.event_bus and EVENT_SYSTEM_AVAILABLE:
                system_event = EmotionalRegulationApplied(
                    user_id=user_id,
                    strategy=regulation_response.strategy_used.value,
                    effectiveness=regulation_response.effectiveness,
                    timestamp=datetime.now(timezone.utc),
                    context={
                        "reasoning": regulation_response.reasoning,
                        "hormone_triggers": regulation_response.hormone_triggers,
                        "neuroplastic_tags": regulation_response.neuroplastic_tags,
                    },
                )
                await self.event_bus.emit(system_event)

            logger.debug(f"Published regulation event for user {user_id}")

        except Exception as e:
            logger.error(f"Failed to publish regulation event: {e}")
            self.integration_health *= 0.95

    async def publish_emotional_memory_stored(self, user_id: str, memory_data: dict[str, Any]):
        """Publish emotional memory storage event"""
        try:
            event = VIVOXEmotionalMemoryStored(user_id=user_id, memory_data=memory_data)

            await self._publish_event(event)
            logger.debug(f"Published emotional memory event for user {user_id}")

        except Exception as e:
            logger.error(f"Failed to publish memory event: {e}")
            self.integration_health *= 0.95

    async def publish_neuroplastic_update(self, user_id: str, update_data: dict[str, Any]):
        """Publish neuroplastic learning update event"""
        try:
            event = VIVOXNeuroplasticUpdate(user_id=user_id, update_data=update_data)

            await self._publish_event(event)
            logger.debug(f"Published neuroplastic update for user {user_id}")

        except Exception as e:
            logger.error(f"Failed to publish neuroplastic event: {e}")
            self.integration_health *= 0.95

    async def _publish_event(self, event: VIVOXEmotionalEvent):
        """Internal event publishing with history tracking"""
        # Add to local history
        self.event_history.append(event)
        self.events_published += 1

        # Limit history size
        if len(self.event_history) > 1000:
            self.event_history = self.event_history[-800:]

        # Publish to event bus if available
        if self.event_bus:
            try:
                await self.event_bus.emit(event)
            except Exception as e:
                logger.error(f"Failed to publish to event bus: {e}")

        # Notify local subscribers
        await self._notify_local_subscribers(event)

    async def _notify_local_subscribers(self, event: VIVOXEmotionalEvent):
        """Notify local event subscribers"""
        event_type = event.event_type

        if event_type in self.subscribers:
            for subscriber_callback in self.subscribers[event_type]:
                try:
                    # Apply filters if any
                    if event_type in self.event_filters:
                        for filter_func in self.event_filters[event_type]:
                            if not filter_func(event):
                                continue

                    # Call subscriber
                    if asyncio.iscoroutinefunction(subscriber_callback):
                        await subscriber_callback(event)
                    else:
                        subscriber_callback(event)

                except Exception as e:
                    logger.error(f"Error notifying subscriber: {e}")

    async def _handle_system_emotional_change(self, event: EmotionalStateChanged):
        """Handle system-wide emotional state changes"""
        try:
            self.events_processed += 1

            # Process and potentially respond to system emotional changes
            logger.debug(f"Received system emotional change for user {event.user_id}")

            # Could trigger VIVOX-specific processing here

        except Exception as e:
            logger.error(f"Error handling system emotional change: {e}")

    async def _handle_system_regulation_event(self, event: EmotionalRegulationApplied):
        """Handle system-wide regulation events"""
        try:
            self.events_processed += 1

            # Process system regulation events
            logger.debug(f"Received system regulation event for user {event.user_id}")

            # Could update VIVOX learning here

        except Exception as e:
            logger.error(f"Error handling system regulation event: {e}")

    def subscribe_to_vivox_events(
        self,
        event_type: str,
        callback: callable,
        filter_func: Optional[callable] = None,
    ):
        """Subscribe to VIVOX-specific events"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []

        self.subscribers[event_type].append(callback)

        if filter_func:
            if event_type not in self.event_filters:
                self.event_filters[event_type] = []
            self.event_filters[event_type].append(filter_func)

        logger.info(f"Added subscriber for VIVOX event type: {event_type}")

    def subscribe_to_emotional_events(self, callback: callable):
        """Subscribe to all emotional events (convenience method)"""
        self.subscribe_to_vivox_events("vivox_emotional_shift", callback)
        self.subscribe_to_vivox_events("vivox_regulation_applied", callback)
        self.subscribe_to_vivox_events("vivox_emotional_memory_stored", callback)

    def get_event_history(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 100,
    ) -> list[VIVOXEmotionalEvent]:
        """Get event history with optional filtering"""
        events = self.event_history

        # Filter by user ID
        if user_id:
            events = [e for e in events if e.user_id == user_id]

        # Filter by event type
        if event_type:
            events = [e for e in events if e.event_type == event_type]

        # Apply limit
        return events[-limit:] if limit > 0 else events

    def get_integration_status(self) -> dict[str, Any]:
        """Get integration status and health metrics"""
        return {
            "event_bus_connected": self.event_bus is not None and EVENT_SYSTEM_AVAILABLE,
            "events_published": self.events_published,
            "events_processed": self.events_processed,
            "integration_health": self.integration_health,
            "subscribers_count": sum(len(subs) for subs in self.subscribers.values()),
            "event_history_size": len(self.event_history),
            "recent_events": len(
                [e for e in self.event_history if (datetime.now(timezone.utc) - e.timestamp).seconds < 3600]
            ),
        }

    async def get_emotional_analytics(self, user_id: str, time_window_hours: int = 24) -> dict[str, Any]:
        """Get emotional analytics from event history"""
        cutoff_time = datetime.now(timezone.utc).timestamp() - (time_window_hours * 3600)

        user_events = [e for e in self.event_history if e.user_id == user_id and e.timestamp.timestamp() > cutoff_time]

        analytics = {
            "total_events": len(user_events),
            "event_types": {},
            "regulation_effectiveness": [],
            "emotional_shifts": [],
            "neuroplastic_updates": 0,
        }

        for event in user_events:
            # Count event types
            event_type = event.event_type
            analytics["event_types"][event_type] = analytics["event_types"].get(event_type, 0) + 1

            # Collect regulation effectiveness
            if isinstance(event, VIVOXRegulationApplied):
                analytics["regulation_effectiveness"].append(event.effectiveness)

            # Collect emotional shifts
            if isinstance(event, VIVOXEmotionalShift):
                analytics["emotional_shifts"].append(
                    {
                        "magnitude": event.shift_magnitude,
                        "triggers": event.triggers,
                        "timestamp": event.timestamp.isoformat(),
                    }
                )

            # Count neuroplastic updates
            if isinstance(event, VIVOXNeuroplasticUpdate):
                analytics["neuroplastic_updates"] += 1

        # Calculate averages
        if analytics["regulation_effectiveness"]:
            analytics["average_regulation_effectiveness"] = sum(analytics["regulation_effectiveness"]) / len(
                analytics["regulation_effectiveness"]
            )
        else:
            analytics["average_regulation_effectiveness"] = 0.0

        if analytics["emotional_shifts"]:
            avg_shift_magnitude = sum(shift["magnitude"] for shift in analytics["emotional_shifts"]) / len(
                analytics["emotional_shifts"]
            )
            analytics["average_emotional_volatility"] = avg_shift_magnitude
        else:
            analytics["average_emotional_volatility"] = 0.0

        return analytics


# Enhanced VIVOX.ERN integration wrapper
class VIVOXERNIntegratedSystem:
    """
    Complete VIVOX.ERN system with event bus integration
    """

    def __init__(
        self,
        vivox_ern: "VIVOXEmotionalRegulationNetwork",
        event_bus: Optional[TypedEventBus] = None,
    ):
        self.vivox_ern = vivox_ern
        self.event_integration = VIVOXEventBusIntegration(event_bus)

        # Connect VIVOX.ERN to event integration
        self.vivox_ern.set_integration_interface("event_bus", self.event_integration)

        # Setup audit trail
        self.audit_trail = []

        # Subscribe to our own events for audit tracking
        self.event_integration.subscribe_to_vivox_events("vivox_regulation_applied", self._audit_regulation_event)

        self.event_integration.subscribe_to_vivox_events("vivox_emotional_shift", self._audit_emotional_shift)

    async def process_emotional_input(
        self,
        user_id: str,
        emotion_data: dict[str, Any],
        context: Optional[dict[str, Any]] = None,
        user_preferences: Optional[dict[str, Any]] = None,
    ) -> RegulationResponse:
        """
        Process emotional input with full event integration
        """
        if context is None:
            context = {}

        # Add user ID to context
        context["user_id"] = user_id

        # Record original state for event publishing
        original_state = self.vivox_ern.current_state

        # Process through VIVOX.ERN
        regulation_response = await self.vivox_ern.process_emotional_input(emotion_data, context, user_preferences)

        # Publish events
        await self.event_integration.publish_regulation_applied(user_id, regulation_response)

        # Publish emotional shift if significant
        if original_state.distance_to(regulation_response.regulated_state) > 0.1:
            await self.event_integration.publish_emotional_shift(
                user_id=user_id,
                previous_state=original_state,
                new_state=regulation_response.regulated_state,
                triggers=context.get("triggers", []),
                context=context,
            )

        # Store emotional memory event
        memory_data = {
            "type": "regulation",
            "pattern": {
                "strategy": regulation_response.strategy_used.value,
                "effectiveness": regulation_response.effectiveness,
                "context": context,
            },
            "tags": regulation_response.neuroplastic_tags,
            "effectiveness": regulation_response.effectiveness,
            "context_hash": str(hash(str(context))),
        }
        await self.event_integration.publish_emotional_memory_stored(user_id, memory_data)

        return regulation_response

    async def _audit_regulation_event(self, event: VIVOXRegulationApplied):
        """Audit regulation events for transparency"""
        audit_entry = {
            "timestamp": event.timestamp.isoformat(),
            "user_id": event.user_id,
            "action": "emotion_regulation",
            "strategy": event.regulation_strategy,
            "effectiveness": event.effectiveness,
            "reasoning": event.reasoning,
            "duration": event.duration_seconds,
            "event_id": event.event_id,
        }

        self.audit_trail.append(audit_entry)

        # Limit audit trail size
        if len(self.audit_trail) > 10000:
            self.audit_trail = self.audit_trail[-8000:]

    async def _audit_emotional_shift(self, event: VIVOXEmotionalShift):
        """Audit emotional shifts for transparency"""
        audit_entry = {
            "timestamp": event.timestamp.isoformat(),
            "user_id": event.user_id,
            "action": "emotional_shift",
            "shift_magnitude": event.shift_magnitude,
            "triggers": event.triggers,
            "event_id": event.event_id,
        }

        self.audit_trail.append(audit_entry)

    def get_user_audit_trail(self, user_id: str, hours: int = 24) -> list[dict[str, Any]]:
        """Get audit trail for specific user"""
        cutoff_time = datetime.now(timezone.utc).timestamp() - (hours * 3600)

        return [
            entry
            for entry in self.audit_trail
            if entry["user_id"] == user_id and datetime.fromisoformat(entry["timestamp"]).timestamp() > cutoff_time
        ]

    async def get_comprehensive_user_report(self, user_id: str) -> dict[str, Any]:
        """Get comprehensive user emotional report"""
        # Get VIVOX insights
        vivox_insights = await self.vivox_ern.get_user_insights(user_id)

        # Get event analytics
        event_analytics = await self.event_integration.get_emotional_analytics(user_id)

        # Get audit trail
        audit_trail = self.get_user_audit_trail(user_id)

        # Get current state
        current_state = await self.vivox_ern.get_current_emotional_state()

        return {
            "user_id": user_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "current_emotional_state": current_state,
            "vivox_insights": vivox_insights,
            "event_analytics": event_analytics,
            "audit_trail_summary": {
                "total_events": len(audit_trail),
                "recent_actions": audit_trail[-10:] if audit_trail else [],
            },
            "integration_status": self.event_integration.get_integration_status(),
        }