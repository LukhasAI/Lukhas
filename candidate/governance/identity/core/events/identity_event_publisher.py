"""
Identity Event Publisher

Integrates with the global event bus to publish identity-specific events
with enhanced tracking, correlation, and tier-based routing.
"""

import logging
from datetime import datetime
from typing import Any, Callable, Optional

from candidate.core.event_bus import EventBus, get_global_event_bus

from .identity_event_types import (  # noqa: F401 # TODO[T4-UNUSED-IMPORT]: kept for Constellation Framework consciousness evolution
from datetime import timezone
    AuthenticationContext,
    IdentityEvent,
    IdentityEventPriority,
    IdentityEventType,
    TierChangeContext,
    VerificationResult,
)

logger = logging.getLogger("LUKHAS_IDENTITY_EVENTS")


class IdentityEventPublisher:
    """
    Specialized event publisher for identity system events.
    Handles tier-based routing, security context, and colony coordination.
    """

    def __init__(self):
        self.event_bus: Optional[EventBus] = None
        self.event_history: list[IdentityEvent] = []
        self.correlation_tracking: dict[str, list[IdentityEvent]] = {}
        self.session_tracking: dict[str, list[IdentityEvent]] = {}

        # Event statistics
        self.stats = {
            "total_events": 0,
            "auth_events": 0,
            "verification_events": 0,
            "security_events": 0,
            "tier_change_events": 0,
            "colony_events": 0,
            "healing_events": 0,
        }

        # Event handlers for specific identity events
        self.event_handlers: dict[IdentityEventType, list[Callable]] = {}

        logger.info("Identity Event Publisher initialized")

    async def initialize(self):
        """Initialize the publisher and connect to event bus."""
        self.event_bus = await get_global_event_bus()

        # Subscribe to identity-related events for tracking
        await self._setup_event_subscriptions()

        logger.info("Identity Event Publisher connected to global event bus")

    async def publish_authentication_event(
        self,
        event_type: IdentityEventType,
        lambda_id: str,
        tier_level: int,
        auth_context: AuthenticationContext,
        session_id: str,
        priority: IdentityEventPriority = IdentityEventPriority.NORMAL,
        additional_data: Optional[dict[str, Any]] = None,
    ) -> str:
        """Publish an authentication-related event."""

        event = IdentityEvent(
            event_type=event_type,
            lambda_id=lambda_id,
            tier_level=tier_level,
            authentication_method=auth_context.method,
            priority=priority,
            source_component="identity_auth_system",
            session_id=session_id,
            data={
                "auth_context": {
                    "method": auth_context.method,
                    "factor_count": auth_context.factor_count,
                    "device_id": auth_context.device_id,
                    "location": auth_context.location,
                    "risk_score": auth_context.risk_score,
                    "previous_attempts": auth_context.previous_attempts,
                    "lockout_remaining": auth_context.lockout_remaining,
                },
                **(additional_data or {}),
            },
            security_context={
                "risk_level": self._calculate_risk_level(auth_context.risk_score),
                "requires_monitoring": auth_context.risk_score > 0.7,
            },
            processing_start=datetime.now(timezone.utc),
        )

        # Set consensus requirements based on tier
        if tier_level >= 3:
            event.consensus_required = True
            event.consensus_threshold = 0.67 if tier_level == 3 else 0.8

        await self._publish_event(event)

        # Track authentication events
        self.stats["auth_events"] += 1

        return event.event_id

    async def publish_verification_event(
        self,
        event_type: IdentityEventType,
        lambda_id: str,
        tier_level: int,
        verification_result: Optional[VerificationResult] = None,
        colony_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        priority: IdentityEventPriority = IdentityEventPriority.NORMAL,
    ) -> str:
        """Publish a verification-related event."""

        event = IdentityEvent(
            event_type=event_type,
            lambda_id=lambda_id,
            tier_level=tier_level,
            priority=priority,
            source_component="identity_verification_system",
            correlation_id=correlation_id,
            colony_id=colony_id,
            verification_colony=colony_id,
        )

        if verification_result:
            event.data = {
                "verified": verification_result.verified,
                "confidence_score": verification_result.confidence_score,
                "verification_method": verification_result.verification_method,
                "colony_consensus": verification_result.colony_consensus,
                "failure_reasons": verification_result.failure_reasons,
                "verification_duration_ms": verification_result.verification_duration_ms,
                "agents_involved": verification_result.agents_involved,
            }

            # Set healing requirements if verification failed
            if not verification_result.verified and verification_result.confidence_score < 0.3:
                event.requires_healing = True
                event.healing_priority = "HIGH"

        await self._publish_event(event)

        # Track verification events
        self.stats["verification_events"] += 1

        return event.event_id

    async def publish_tier_change_event(
        self,
        lambda_id: str,
        tier_context: TierChangeContext,
        approved: bool,
        session_id: Optional[str] = None,
    ) -> str:
        """Publish a tier change event."""

        event_type = IdentityEventType.TIER_UPGRADE_APPROVED if approved else IdentityEventType.TIER_UPGRADE_DENIED

        event = IdentityEvent(
            event_type=event_type,
            lambda_id=lambda_id,
            tier_level=(tier_context.new_tier if approved else tier_context.previous_tier),
            priority=IdentityEventPriority.HIGH,
            source_component="identity_tier_system",
            session_id=session_id,
            data={
                "previous_tier": tier_context.previous_tier,
                "new_tier": tier_context.new_tier,
                "change_reason": tier_context.change_reason,
                "approval_required": tier_context.approval_required,
                "approver_id": tier_context.approver_id,
                "benefits_delta": tier_context.benefits_delta,
                "cooldown_period": tier_context.cooldown_period,
                "approved": approved,
            },
        )

        # Tier changes may require colony coordination for validation
        if tier_context.new_tier >= 4:
            event.consensus_required = True
            event.consensus_threshold = 0.9

        await self._publish_event(event)

        # Track tier change events
        self.stats["tier_change_events"] += 1

        # Trigger benefit activation if approved
        if approved:
            await self.publish_tier_benefits_activation(lambda_id, tier_context.new_tier, tier_context.benefits_delta)

        return event.event_id

    async def publish_colony_event(
        self,
        event_type: IdentityEventType,
        lambda_id: str,
        tier_level: int,
        colony_id: str,
        swarm_task_id: Optional[str] = None,
        consensus_data: Optional[dict[str, Any]] = None,
        priority: IdentityEventPriority = IdentityEventPriority.NORMAL,
    ) -> str:
        """Publish a colony coordination event."""

        event = IdentityEvent(
            event_type=event_type,
            lambda_id=lambda_id,
            tier_level=tier_level,
            priority=priority,
            source_component="identity_colony_system",
            colony_id=colony_id,
            swarm_task_id=swarm_task_id,
            data={
                "colony_type": self._get_colony_type(colony_id),
                "consensus_data": consensus_data or {},
            },
        )

        # Colony events often require coordination
        if event_type in [
            IdentityEventType.COLONY_CONSENSUS_VOTING,
            IdentityEventType.COLONY_VERIFICATION_START,
        ]:
            event.consensus_required = True
            event.consensus_threshold = 0.67

        await self._publish_event(event)

        # Track colony events
        self.stats["colony_events"] += 1

        return event.event_id

    async def publish_security_event(
        self,
        event_type: IdentityEventType,
        lambda_id: str,
        tier_level: int,
        threat_data: dict[str, Any],
        immediate_action_required: bool = False,
    ) -> str:
        """Publish a security-related event."""

        priority = IdentityEventPriority.EMERGENCY if immediate_action_required else IdentityEventPriority.CRITICAL

        event = IdentityEvent(
            event_type=event_type,
            lambda_id=lambda_id,
            tier_level=tier_level,
            priority=priority,
            source_component="identity_security_system",
            data={
                "threat_data": threat_data,
                "immediate_action_required": immediate_action_required,
                "threat_level": threat_data.get("level", "unknown"),
                "mitigation_steps": threat_data.get("mitigation_steps", []),
            },
            security_context={
                "threat_detected": True,
                "lockdown_recommended": immediate_action_required,
                "monitoring_required": True,
            },
            requires_healing=immediate_action_required,
            healing_priority="CRITICAL" if immediate_action_required else "HIGH",
        )

        await self._publish_event(event)

        # Track security events
        self.stats["security_events"] += 1

        # Trigger healing if needed
        if immediate_action_required:
            await self.publish_healing_event(lambda_id, tier_level, "SECURITY_THREAT", event.event_id)

        return event.event_id

    async def publish_healing_event(
        self,
        lambda_id: str,
        tier_level: int,
        healing_reason: str,
        correlation_id: Optional[str] = None,
        healing_strategy: Optional[str] = None,
    ) -> str:
        """Publish a healing-related event."""

        event = IdentityEvent(
            event_type=IdentityEventType.HEALING_REQUIRED,
            lambda_id=lambda_id,
            tier_level=tier_level,
            priority=IdentityEventPriority.HIGH,
            source_component="identity_healing_system",
            correlation_id=correlation_id,
            data={
                "healing_reason": healing_reason,
                "tier_specific_healing": tier_level >= 3,
            },
            requires_healing=True,
            healing_priority="HIGH",
            healing_strategy=healing_strategy or self._determine_healing_strategy(tier_level),
        )

        await self._publish_event(event)

        # Track healing events
        self.stats["healing_events"] += 1

        return event.event_id

    async def publish_glyph_event(
        self,
        event_type: IdentityEventType,
        lambda_id: str,
        tier_level: int,
        glyph_data: dict[str, Any],
        session_id: Optional[str] = None,
    ) -> str:
        """Publish a GLYPH-related event."""

        event = IdentityEvent(
            event_type=event_type,
            lambda_id=lambda_id,
            tier_level=tier_level,
            priority=IdentityEventPriority.NORMAL,
            source_component="identity_glyph_system",
            session_id=session_id,
            data={
                "glyph_type": glyph_data.get("type"),
                "glyph_id": glyph_data.get("id"),
                "steganographic_enabled": tier_level >= 2,
                "qi_enhanced": tier_level >= 4,
                **glyph_data,
            },
        )

        await self._publish_event(event)

        return event.event_id

    async def publish_tier_benefits_activation(self, lambda_id: str, tier_level: int, benefits: dict[str, Any]) -> str:
        """Publish tier benefits activation event."""

        event = IdentityEvent(
            event_type=IdentityEventType.TIER_BENEFITS_ACTIVATED,
            lambda_id=lambda_id,
            tier_level=tier_level,
            priority=IdentityEventPriority.NORMAL,
            source_component="identity_benefits_system",
            data={
                "activated_benefits": benefits,
                "activation_timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

        await self._publish_event(event)

        return event.event_id

    # Private helper methods

    async def _publish_event(self, event: IdentityEvent):
        """Internal method to publish event to bus."""

        # Calculate processing duration if end time is set
        if event.processing_start:
            event.processing_end = datetime.now(timezone.utc)
            event.calculate_processing_duration()

        # Convert to event bus format
        await self.event_bus.publish(
            event_type=event.event_type.value,
            payload=event.to_dict(),
            source=event.source_component,
            priority=event.priority.value,
            correlation_id=event.correlation_id,
            user_id=event.lambda_id,
        )

        # Track event in history
        self.event_history.append(event)
        if len(self.event_history) > 10000:  # Keep last 10k events
            self.event_history = self.event_history[-10000:]

        # Track by correlation
        if event.correlation_id:
            if event.correlation_id not in self.correlation_tracking:
                self.correlation_tracking[event.correlation_id] = []
            self.correlation_tracking[event.correlation_id].append(event)

        # Track by session
        if event.session_id:
            if event.session_id not in self.session_tracking:
                self.session_tracking[event.session_id] = []
            self.session_tracking[event.session_id].append(event)

        # Update statistics
        self.stats["total_events"] += 1

        # Log security-critical events
        if event.is_security_critical():
            logger.warning(f"Security-critical event: {event.event_type.value} for {event.lambda_id}")

        # Execute registered handlers
        if event.event_type in self.event_handlers:
            for handler in self.event_handlers[event.event_type]:
                try:
                    await handler(event)
                except Exception as e:
                    logger.error(f"Event handler error: {e}")

    async def _setup_event_subscriptions(self):
        """Setup subscriptions for identity event tracking."""

        # Subscribe to all identity events for statistics
        for event_type in IdentityEventType:
            await self.event_bus.subscribe(event_type.value, self._track_event_statistics)

    async def _track_event_statistics(self, event_data: dict[str, Any]):
        """Track event statistics for monitoring."""
        # This would be called by event bus for tracking

    def _calculate_risk_level(self, risk_score: float) -> str:
        """Calculate risk level from score."""
        if risk_score < 0.3:
            return "LOW"
        elif risk_score < 0.6:
            return "MEDIUM"
        elif risk_score < 0.8:
            return "HIGH"
        else:
            return "CRITICAL"

    def _get_colony_type(self, colony_id: str) -> str:
        """Determine colony type from ID."""
        if "biometric" in colony_id.lower():
            return "biometric_verification"
        elif "consciousness" in colony_id.lower():
            return "consciousness_verification"
        elif "dream" in colony_id.lower():
            return "dream_verification"
        elif "governance" in colony_id.lower():
            return "identity_governance"
        else:
            return "general_verification"

    def _determine_healing_strategy(self, tier_level: int) -> str:
        """Determine healing strategy based on tier."""
        if tier_level <= 2:
            return "IMMEDIATE_RESTART"
        elif tier_level == 3:
            return "GRADUAL_RECOVERY"
        elif tier_level == 4:
            return "COLONY_COORDINATION"
        else:  # Tier 5
            return "DISTRIBUTED_HEALING"

    def register_event_handler(self, event_type: IdentityEventType, handler: Callable):
        """Register a handler for specific event types."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)

    def get_event_statistics(self) -> dict[str, Any]:
        """Get comprehensive event statistics."""
        return {
            **self.stats,
            "correlation_sessions": len(self.correlation_tracking),
            "active_sessions": len(self.session_tracking),
            "event_history_size": len(self.event_history),
        }

    def get_session_events(self, session_id: str) -> list[IdentityEvent]:
        """Get all events for a specific session."""
        return self.session_tracking.get(session_id, [])

    def get_correlation_events(self, correlation_id: str) -> list[IdentityEvent]:
        """Get all events with specific correlation ID."""
        return self.correlation_tracking.get(correlation_id, [])


# Global instance
_identity_event_publisher: Optional[IdentityEventPublisher] = None


async def get_identity_event_publisher() -> IdentityEventPublisher:
    """Get or create the global identity event publisher."""
    global _identity_event_publisher

    if _identity_event_publisher is None:
        _identity_event_publisher = IdentityEventPublisher()
        await _identity_event_publisher.initialize()

    return _identity_event_publisher