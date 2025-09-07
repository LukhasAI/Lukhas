#!/usr/bin/env python3
log = logging.getLogger(__name__)
"""
LUKHAS Production Audit Logger
Enterprise-grade audit logging system for constitutional AI compliance

This module provides comprehensive audit logging that meets enterprise
security requirements and constitutional AI compliance standards.
"""
import hashlib
import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from lukhas.core.common.logger import get_logger

logger = get_logger(__name__)


class AuditEventType(Enum):
    """Types of audit events"""

    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    ACCESS_CONTROL = "access_control"
    CONSTITUTIONAL_ENFORCEMENT = "constitutional_enforcement"
    POLICY_VIOLATION = "policy_violation"
    SECURITY_INCIDENT = "security_incident"
    SYSTEM_OPERATION = "system_operation"
    DATA_ACCESS = "data_access"
    USER_ACTION = "user_action"
    DRIFT_DETECTION = "drift_detection"


class AuditSeverity(Enum):
    """Audit event severity levels"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ComplianceFramework(Enum):
    """Compliance frameworks"""

    GDPR = "gdpr"
    HIPAA = "hipaa"
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    CONSTITUTIONAL_AI = "constitutional_ai"


@dataclass
class AuditEvent:
    """Comprehensive audit event record"""

    event_id: str
    event_type: AuditEventType
    severity: AuditSeverity
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Core event data
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    agent_id: Optional[str] = None
    action: str = ""
    resource: str = ""
    outcome: str = ""

    # Context information
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_id: Optional[str] = None

    # Detailed information
    details: dict[str, Any] = field(default_factory=dict)
    evidence: list[str] = field(default_factory=list)

    # Constitutional AI specific
    constitutional_compliance: bool = True
    drift_score: Optional[float] = None
    safety_assessment_id: Optional[str] = None

    # Compliance tracking
    compliance_frameworks: list[ComplianceFramework] = field(default_factory=list)
    retention_period_days: int = 2555  # 7 years default

    # Integrity protection
    event_hash: Optional[str] = field(default=None, init=False)

    def __post_init__(self):
        """Generate event hash for integrity protection"""
        self.event_hash = self._calculate_hash()

    def _calculate_hash(self) -> str:
        """Calculate hash for event integrity"""
        # Create deterministic string representation
        data = {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "severity": self.severity.value,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "session_id": self.session_id,
            "action": self.action,
            "resource": self.resource,
            "outcome": self.outcome,
            "details": json.dumps(self.details, sort_keys=True),
        }

        event_string = json.dumps(data, sort_keys=True)
        return hashlib.sha256(event_string.encode()).hexdigest()

    def verify_integrity(self) -> bool:
        """Verify event integrity using hash"""
        return self.event_hash == self._calculate_hash()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)


@dataclass
class AuditTrail:
    """Audit trail for related events"""

    trail_id: str
    correlation_id: str
    events: list[AuditEvent] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

    # Trail metadata
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    operation_type: str = ""

    def add_event(self, event: AuditEvent) -> None:
        """Add event to trail"""
        self.events.append(event)

    def complete_trail(self) -> None:
        """Mark trail as completed"""
        self.completed_at = datetime.now(timezone.utc)

    def get_timeline(self) -> list[dict[str, Any]]:
        """Get chronological timeline of events"""
        return [
            {
                "timestamp": event.timestamp.isoformat(),
                "event_type": event.event_type.value,
                "action": event.action,
                "outcome": event.outcome,
                "severity": event.severity.value,
            }
            for event in sorted(self.events, key=lambda e: e.timestamp)
        ]


class AuditLogger:
    """Production audit logging system with constitutional AI compliance"""

    def __init__(self, config: Optional[dict[str, Any]] = None) -> None:
        self.config = config or {}

        # Storage configuration
        self.audit_file_path = Path(self.config.get("audit_file_path", "audit/audit.jsonl"))
        self.max_file_size_mb = self.config.get("max_file_size_mb", 100)
        self.retention_days = self.config.get("retention_days", 2555)  # 7 years

        # In-memory storage for real-time access
        self.recent_events: list[AuditEvent] = []
        self.active_trails: dict[str, AuditTrail] = {}
        self.event_counters: dict[str, int] = {}

        # Ensure audit directory exists
        self.audit_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Compliance configuration
        self.required_frameworks = [
            ComplianceFramework.CONSTITUTIONAL_AI,
            ComplianceFramework.SOC2,
            ComplianceFramework.ISO27001,
        ]

        # Integrity protection
        self.tamper_detection = True
        self.event_signatures: dict[str, str] = {}

        logger.info("🛡️ Production Audit Logger initialized")

    async def log_event(
        self,
        event_type: AuditEventType,
        action: str,
        outcome: str = "success",
        severity: AuditSeverity = AuditSeverity.INFO,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        resource: str = "",
        details: Optional[dict[str, Any]] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> str:
        """Log audit event with comprehensive tracking"""

        event_id = str(uuid.uuid4())
        context = context or {}

        # Create audit event
        event = AuditEvent(
            event_id=event_id,
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            session_id=session_id,
            agent_id=agent_id,
            action=action,
            resource=resource,
            outcome=outcome,
            ip_address=context.get("ip_address"),
            user_agent=context.get("user_agent"),
            request_id=context.get("request_id"),
            details=details or {},
            compliance_frameworks=self.required_frameworks.copy(),
            drift_score=context.get("drift_score"),
            safety_assessment_id=context.get("safety_assessment_id"),
        )

        # Store event
        await self._store_event(event)

        # Add to recent events (keep last 1000)
        self.recent_events.append(event)
        if len(self.recent_events) > 1000:
            self.recent_events = self.recent_events[-1000:]

        # Update counters
        event_key = f"{event_type.value}_{outcome}"
        self.event_counters[event_key] = self.event_counters.get(event_key, 0) + 1

        # Add to active trail if correlation ID provided
        correlation_id = context.get("correlation_id")
        if correlation_id and correlation_id in self.active_trails:
            self.active_trails[correlation_id].add_event(event)

        # Log critical events immediately
        if severity in [AuditSeverity.ERROR, AuditSeverity.CRITICAL]:
            logger.warning(f"Critical audit event: {event_type.value} - {action} - {outcome}")

        return event_id

    async def log_constitutional_enforcement(
        self,
        action: str,
        enforcement_type: str,
        details: dict[str, Any],
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        drift_score: Optional[float] = None,
        safety_assessment_id: Optional[str] = None,
    ) -> str:
        """Log constitutional AI enforcement event"""

        # Determine severity based on drift score and enforcement type
        severity = AuditSeverity.INFO
        if drift_score and drift_score >= 0.15:  # LUKHAS drift threshold
            severity = AuditSeverity.CRITICAL
        elif enforcement_type in ["block", "deny", "escalate"]:
            severity = AuditSeverity.WARNING

        context = {
            "drift_score": drift_score,
            "safety_assessment_id": safety_assessment_id,
            "enforcement_type": enforcement_type,
        }

        return await self.log_event(
            event_type=AuditEventType.CONSTITUTIONAL_ENFORCEMENT,
            action=action,
            outcome=enforcement_type,
            severity=severity,
            user_id=user_id,
            session_id=session_id,
            agent_id=agent_id,
            resource="constitutional_framework",
            details=details,
            context=context,
        )

    async def log_authentication_attempt(
        self,
        username: str,
        success: bool,
        method: str = "password",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> str:
        """Log authentication attempt"""

        outcome = "success" if success else "failure"
        severity = AuditSeverity.INFO if success else AuditSeverity.WARNING

        context = {"ip_address": ip_address, "user_agent": user_agent, "method": method}

        auth_details = {
            "username": username,
            "authentication_method": method,
            **(details or {}),
        }

        return await self.log_event(
            event_type=AuditEventType.AUTHENTICATION,
            action="login_attempt",
            outcome=outcome,
            severity=severity,
            user_id=username,
            resource="authentication_system",
            details=auth_details,
            context=context,
        )

    async def log_policy_violation(
        self,
        policy_type: str,
        violation_details: dict[str, Any],
        enforcement_action: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> str:
        """Log policy violation"""

        # Determine severity based on policy type
        severity = AuditSeverity.WARNING
        if "constitutional" in policy_type.lower():
            severity = AuditSeverity.CRITICAL
        elif "security" in policy_type.lower():
            severity = AuditSeverity.ERROR

        details = {
            "policy_type": policy_type,
            "enforcement_action": enforcement_action,
            **violation_details,
        }

        return await self.log_event(
            event_type=AuditEventType.POLICY_VIOLATION,
            action="policy_violation",
            outcome=enforcement_action,
            severity=severity,
            user_id=user_id,
            session_id=session_id,
            agent_id=agent_id,
            resource=f"policy_{policy_type}",
            details=details,
        )

    async def log_access_control_decision(
        self,
        user_id: str,
        resource: str,
        action: str,
        decision: str,
        reason: str,
        tier_required: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> str:
        """Log access control decision"""

        severity = AuditSeverity.INFO if decision == "allow" else AuditSeverity.WARNING

        details = {
            "decision": decision,
            "reason": reason,
            "tier_required": tier_required,
            "resource_requested": resource,
            "action_requested": action,
        }

        return await self.log_event(
            event_type=AuditEventType.ACCESS_CONTROL,
            action="access_decision",
            outcome=decision,
            severity=severity,
            user_id=user_id,
            session_id=session_id,
            resource=resource,
            details=details,
        )

    async def log_drift_detection(
        self,
        drift_type: str,
        drift_score: float,
        threshold: float,
        source_system: str,
        details: Optional[dict[str, Any]] = None,
    ) -> str:
        """Log drift detection event"""

        severity = AuditSeverity.CRITICAL if drift_score >= threshold else AuditSeverity.INFO
        outcome = "threshold_breach" if drift_score >= threshold else "within_threshold"

        drift_details = {
            "drift_type": drift_type,
            "drift_score": drift_score,
            "threshold": threshold,
            "source_system": source_system,
            "breach": drift_score >= threshold,
            **(details or {}),
        }

        context = {"drift_score": drift_score}

        return await self.log_event(
            event_type=AuditEventType.DRIFT_DETECTION,
            action="drift_measurement",
            outcome=outcome,
            severity=severity,
            resource=source_system,
            details=drift_details,
            context=context,
        )

    async def start_audit_trail(
        self,
        operation_type: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> str:
        """Start new audit trail for related events"""

        trail_id = str(uuid.uuid4())
        correlation_id = str(uuid.uuid4())

        trail = AuditTrail(
            trail_id=trail_id,
            correlation_id=correlation_id,
            user_id=user_id,
            session_id=session_id,
            operation_type=operation_type,
        )

        self.active_trails[correlation_id] = trail

        # Log trail start
        await self.log_event(
            event_type=AuditEventType.SYSTEM_OPERATION,
            action="audit_trail_start",
            outcome="started",
            user_id=user_id,
            session_id=session_id,
            resource="audit_system",
            details={"trail_id": trail_id, "operation_type": operation_type},
            context={"correlation_id": correlation_id},
        )

        return correlation_id

    async def complete_audit_trail(self, correlation_id: str) -> Optional[AuditTrail]:
        """Complete and finalize audit trail"""

        trail = self.active_trails.pop(correlation_id, None)
        if not trail:
            return None

        trail.complete_trail()

        # Log trail completion
        await self.log_event(
            event_type=AuditEventType.SYSTEM_OPERATION,
            action="audit_trail_complete",
            outcome="completed",
            user_id=trail.user_id,
            session_id=trail.session_id,
            resource="audit_system",
            details={
                "trail_id": trail.trail_id,
                "event_count": len(trail.events),
                "duration_seconds": (trail.completed_at - trail.created_at).total_seconds(),
            },
        )

        return trail

    async def _store_event(self, event: AuditEvent) -> None:
        """Store event to persistent storage"""
        try:
            # Convert to JSON and append to file
            event_json = json.dumps(event.to_dict(), default=str)

            with open(self.audit_file_path, "a", encoding="utf-8") as f:
                f.write(event_json + "\n")

            # Store event signature for integrity
            if self.tamper_detection:
                self.event_signatures[event.event_id] = event.event_hash

        except Exception as e:
            logger.error(f"Failed to store audit event {event.event_id}: {e}")

            # Try to log to backup location
            try:
                backup_path = self.audit_file_path.with_suffix(".backup.jsonl")
                with open(backup_path, "a", encoding="utf-8") as f:
                    f.write(event_json + "\n")
            except Exception as backup_error:
                logger.critical(f"Failed to store to backup audit log: {backup_error}")

    def get_recent_events(
        self,
        count: int = 100,
        event_type: Optional[AuditEventType] = None,
        severity: Optional[AuditSeverity] = None,
    ) -> list[AuditEvent]:
        """Get recent audit events with filtering"""

        events = self.recent_events[-count:]

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        if severity:
            events = [e for e in events if e.severity == severity]

        return sorted(events, key=lambda e: e.timestamp, reverse=True)

    def get_audit_statistics(self) -> dict[str, Any]:
        """Get audit logging statistics"""

        recent_events = self.recent_events[-1000:]  # Last 1000 events

        # Event type distribution
        event_type_counts = {}
        for event in recent_events:
            event_type_counts[event.event_type.value] = event_type_counts.get(event.event_type.value, 0) + 1

        # Severity distribution
        severity_counts = {}
        for event in recent_events:
            severity_counts[event.severity.value] = severity_counts.get(event.severity.value, 0) + 1

        # Constitutional events
        constitutional_events = [e for e in recent_events if e.event_type == AuditEventType.CONSTITUTIONAL_ENFORCEMENT]
        drift_events = [e for e in recent_events if e.drift_score is not None]

        return {
            "total_events": len(recent_events),
            "event_types": event_type_counts,
            "severity_distribution": severity_counts,
            "constitutional_events": len(constitutional_events),
            "drift_detection_events": len(drift_events),
            "active_trails": len(self.active_trails),
            "integrity_enabled": self.tamper_detection,
            "storage_location": str(self.audit_file_path),
            "retention_days": self.retention_days,
        }

    async def verify_audit_integrity(self) -> dict[str, Any]:
        """Verify integrity of audit events"""

        verification_results = {
            "total_events_checked": 0,
            "integrity_verified": 0,
            "integrity_failed": 0,
            "errors": [],
        }

        for event in self.recent_events:
            verification_results["total_events_checked"] += 1

            try:
                if event.verify_integrity():
                    verification_results["integrity_verified"] += 1
                else:
                    verification_results["integrity_failed"] += 1
                    verification_results["errors"].append(f"Integrity check failed for event {event.event_id}")

            except Exception as e:
                verification_results["integrity_failed"] += 1
                verification_results["errors"].append(f"Error verifying event {event.event_id}: {e!s}")

        return verification_results


# Export classes for production use
__all__ = [
    "AuditEvent",
    "AuditEventType",
    "AuditLogger",
    "AuditSeverity",
    "AuditTrail",
    "ComplianceFramework",
]
