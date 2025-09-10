"""
Identity Event Types and Structures

Defines specialized event types for identity system coordination,
authentication tracking, and tier-based orchestration.
"""
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class IdentityEventType(Enum):
    """Comprehensive identity system event types."""

    # Authentication Events
    AUTH_ATTEMPT_START = "identity.auth.attempt.start"
    AUTH_ATTEMPT_SUCCESS = "identity.auth.attempt.success"
    AUTH_ATTEMPT_FAILED = "identity.auth.attempt.failed"
    AUTH_METHOD_SELECTED = "identity.auth.method.selected"
    AUTH_CHALLENGE_ISSUED = "identity.auth.challenge.issued"
    AUTH_CHALLENGE_RESPONSE = "identity.auth.challenge.response"

    # Verification Events
    VERIFICATION_START = "identity.verification.start"
    VERIFICATION_COMPLETE = "identity.verification.complete"
    VERIFICATION_FAILED = "identity.verification.failed"
    VERIFICATION_CONSENSUS_REACHED = "identity.verification.consensus"
    VERIFICATION_COLONY_ASSIGNED = "identity.verification.colony.assigned"

    # Biometric Events
    BIOMETRIC_SCAN_START = "identity.biometric.scan.start"
    BIOMETRIC_SCAN_COMPLETE = "identity.biometric.scan.complete"
    BIOMETRIC_MATCH_FOUND = "identity.biometric.match.found"
    BIOMETRIC_ANOMALY_DETECTED = "identity.biometric.anomaly"

    # Consciousness Events
    CONSCIOUSNESS_SYNC_START = "identity.consciousness.sync.start"
    CONSCIOUSNESS_SYNC_COMPLETE = "identity.consciousness.sync.complete"
    CONSCIOUSNESS_COHERENCE_CHECK = "identity.consciousness.coherence"
    CONSCIOUSNESS_ANOMALY = "identity.consciousness.anomaly"
    CONSCIOUSNESS_SPOOFING_DETECTED = "identity.consciousness.spoofing"

    # Dream Authentication Events (Tier 5)
    DREAM_AUTH_INITIATED = "identity.dream.auth.initiated"
    DREAM_PATTERN_MATCHED = "identity.dream.pattern.matched"
    DREAM_VERIFICATION_COMPLETE = "identity.dream.verification.complete"
    DREAM_MULTIVERSE_SIMULATION = "identity.dream.multiverse.simulation"

    # Tier System Events
    TIER_EVALUATION_START = "identity.tier.evaluation.start"
    TIER_UPGRADE_REQUESTED = "identity.tier.upgrade.requested"
    TIER_UPGRADE_APPROVED = "identity.tier.upgrade.approved"
    TIER_UPGRADE_DENIED = "identity.tier.upgrade.denied"
    TIER_DOWNGRADE_TRIGGERED = "identity.tier.downgrade.triggered"
    TIER_BENEFITS_ACTIVATED = "identity.tier.benefits.activated"

    # Colony Coordination Events
    COLONY_VERIFICATION_START = "identity.colony.verification.start"
    COLONY_AGENT_ASSIGNED = "identity.colony.agent.assigned"
    COLONY_CONSENSUS_VOTING = "identity.colony.consensus.voting"
    COLONY_CONSENSUS_REACHED = "identity.colony.consensus.reached"
    COLONY_CONSENSUS_FAILED = "identity.colony.consensus.failed"
    COLONY_HEALING_TRIGGERED = "identity.colony.healing.triggered"

    # GLYPH Events
    GLYPH_GENERATION_START = "identity.glyph.generation.start"
    GLYPH_GENERATION_COMPLETE = "identity.glyph.generation.complete"
    GLYPH_STEGANOGRAPHIC_EMBED = "identity.glyph.steganographic.embed"
    GLYPH_VERIFICATION_REQUEST = "identity.glyph.verification.request"
    GLYPH_EXPIRED = "identity.glyph.expired"

    # Security & Anomaly Events
    SECURITY_ANOMALY_DETECTED = "identity.security.anomaly.detected"
    SECURITY_THREAT_IDENTIFIED = "identity.security.threat.identified"
    SECURITY_LOCKDOWN_TRIGGERED = "identity.security.lockdown.triggered"
    SECURITY_AUDIT_STARTED = "identity.security.audit.started"

    # Healing & Recovery Events
    HEALING_REQUIRED = "identity.healing.required"
    HEALING_STARTED = "identity.healing.started"
    HEALING_STRATEGY_SELECTED = "identity.healing.strategy.selected"
    HEALING_COMPLETE = "identity.healing.complete"
    HEALING_FAILED = "identity.healing.failed"

    # Tag & Trust Network Events
    TAG_CREATED = "identity.tag.created"
    TAG_PROPAGATED = "identity.tag.propagated"
    TRUST_NETWORK_UPDATED = "identity.trust.network.updated"
    TRUST_SCORE_CHANGED = "identity.trust.score.changed"


class IdentityEventPriority(Enum):
    """Priority levels for identity events."""

    LOW = 1  # Informational events
    NORMAL = 2  # Standard operations
    HIGH = 3  # Important operations
    CRITICAL = 4  # Security-critical events
    EMERGENCY = 5  # System-threatening events


@dataclass
class IdentityEvent:
    """Enhanced event structure for identity system coordination."""

    # Core event fields
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: IdentityEventType = IdentityEventType.AUTH_ATTEMPT_START
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Identity context
    lambda_id: str = ""
    tier_level: int = 0
    authentication_method: Optional[str] = None
    verification_colony: Optional[str] = None

    # Event metadata
    priority: IdentityEventPriority = IdentityEventPriority.NORMAL
    source_component: str = ""
    target_component: Optional[str] = None
    correlation_id: Optional[str] = None
    session_id: Optional[str] = None

    # Event payload
    data: dict[str, Any] = field(default_factory=dict)

    # Security context
    security_context: dict[str, Any] = field(default_factory=dict)
    encryption_used: bool = False
    signed: bool = False

    # Colony/Swarm context
    colony_id: Optional[str] = None
    swarm_task_id: Optional[str] = None
    consensus_required: bool = False
    consensus_threshold: float = 0.0

    # Healing context
    requires_healing: bool = False
    healing_priority: Optional[str] = None
    healing_strategy: Optional[str] = None

    # Performance metrics
    processing_start: Optional[datetime] = None
    processing_end: Optional[datetime] = None
    processing_duration_ms: Optional[float] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "lambda_id": self.lambda_id,
            "tier_level": self.tier_level,
            "authentication_method": self.authentication_method,
            "verification_colony": self.verification_colony,
            "priority": self.priority.value,
            "source_component": self.source_component,
            "target_component": self.target_component,
            "correlation_id": self.correlation_id,
            "session_id": self.session_id,
            "data": self.data,
            "security_context": self.security_context,
            "colony_id": self.colony_id,
            "swarm_task_id": self.swarm_task_id,
            "consensus_required": self.consensus_required,
            "consensus_threshold": self.consensus_threshold,
            "requires_healing": self.requires_healing,
            "healing_priority": self.healing_priority,
            "healing_strategy": self.healing_strategy,
            "processing_duration_ms": self.processing_duration_ms,
        }

    def calculate_processing_duration(self):
        """Calculate processing duration if start and end times are set."""
        if self.processing_start and self.processing_end:
            duration = (self.processing_end - self.processing_start).total_seconds() * 1000
            self.processing_duration_ms = duration
            return duration
        return None

    def is_security_critical(self) -> bool:
        """Check if this is a security-critical event."""
        security_critical_types = [
            IdentityEventType.AUTH_ATTEMPT_FAILED,
            IdentityEventType.SECURITY_ANOMALY_DETECTED,
            IdentityEventType.SECURITY_THREAT_IDENTIFIED,
            IdentityEventType.SECURITY_LOCKDOWN_TRIGGERED,
            IdentityEventType.CONSCIOUSNESS_SPOOFING_DETECTED,
        ]
        return self.event_type in security_critical_types or self.priority in [
            IdentityEventPriority.CRITICAL,
            IdentityEventPriority.EMERGENCY,
        ]

    def requires_colony_coordination(self) -> bool:
        """Check if this event requires colony coordination."""
        colony_events = [
            IdentityEventType.COLONY_VERIFICATION_START,
            IdentityEventType.COLONY_CONSENSUS_VOTING,
            IdentityEventType.COLONY_HEALING_TRIGGERED,
            IdentityEventType.VERIFICATION_CONSENSUS_REACHED,
        ]
        return self.event_type in colony_events or self.consensus_required or self.tier_level >= 3


@dataclass
class AuthenticationContext:
    """Context for authentication events."""

    method: str
    factor_count: int
    device_id: str
    location: Optional[str] = None
    risk_score: float = 0.0
    previous_attempts: int = 0
    lockout_remaining: Optional[int] = None


@dataclass
class VerificationResult:
    """Result of verification process."""

    verified: bool
    confidence_score: float
    verification_method: str
    colony_consensus: Optional[dict[str, Any]] = None
    failure_reasons: list[str] = field(default_factory=list)
    verification_duration_ms: float = 0.0
    agents_involved: int = 1


@dataclass
class TierChangeContext:
    """Context for tier change events."""

    previous_tier: int
    new_tier: int
    change_reason: str
    approval_required: bool
    approver_id: Optional[str] = None
    benefits_delta: dict[str, Any] = field(default_factory=dict)
    cooldown_period: Optional[int] = None  # seconds
