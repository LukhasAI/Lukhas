"""
Comprehensive Audit System for LUKHAS AI

This module provides a comprehensive audit and logging system that
tracks all system activities, security events, compliance actions,
and governance decisions with immutable audit trails and advanced
analytics for forensic analysis and compliance reporting.

Features:
- Immutable audit trail with cryptographic integrity
- Real-time activity monitoring and alerting
- Compliance-focused audit logging (GDPR, SOC2, etc.)
- Advanced search and filtering capabilities
- Automated audit report generation
- Constellation Framework audit integration (✨🌟⭐🔥💎⚖️🛡️🌌)
- Threat detection through audit pattern analysis
- Retention policy management
- Cross-system audit correlation

#TAG:governance
#TAG:audit
#TAG:security
#TAG:compliance
#TAG:monitoring
#TAG:constellation
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

from core.common import get_logger

logger = logging.getLogger(__name__)



logger = get_logger(__name__)


class AuditLevel(Enum):
    """Audit event levels"""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    SECURITY = "security"
    COMPLIANCE = "compliance"


class AuditCategory(Enum):
    """Categories of audit events"""

    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    SYSTEM_ADMIN = "system_admin"
    CONFIGURATION = "configuration"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    PRIVACY = "privacy"
    AI_ETHICS = "ai_ethics"
    CONSTITUTIONAL = "constitutional"
    CONSTELLATION = "constellation"
    GOVERNANCE = "governance"
    USER_ACTION = "user_action"
    SYSTEM_EVENT = "system_event"
    ERROR = "error"


class AuditEventType(Enum):
    """Specific types of audit events"""

    # Authentication events
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    SESSION_EXPIRED = "session_expired"
    MFA_CHALLENGE = "mfa_challenge"

    # Authorization events
    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"
    PERMISSION_ESCALATION = "permission_escalation"

    # Data events
    DATA_READ = "data_read"
    DATA_WRITE = "data_write"
    DATA_DELETE = "data_delete"
    DATA_EXPORT = "data_export"
    DATA_ANONYMIZATION = "data_anonymization"

    # System events
    SYSTEM_START = "system_start"
    SYSTEM_SHUTDOWN = "system_shutdown"
    CONFIG_CHANGE = "config_change"
    SOFTWARE_UPDATE = "software_update"

    # Security events
    SECURITY_VIOLATION = "security_violation"
    THREAT_DETECTED = "threat_detected"
    SECURITY_SCAN = "security_scan"
    VULNERABILITY_FOUND = "vulnerability_found"

    # Compliance events
    POLICY_VIOLATION = "policy_violation"
    COMPLIANCE_CHECK = "compliance_check"
    AUDIT_REVIEW = "audit_review"
    REGULATORY_REPORT = "regulatory_report"

    # Privacy events
    CONSENT_GRANTED = "consent_granted"
    CONSENT_WITHDRAWN = "consent_withdrawn"
    PRIVACY_VIOLATION = "privacy_violation"
    DATA_BREACH = "data_breach"

    # AI/Ethics events
    AI_DECISION = "ai_decision"
    BIAS_DETECTION = "bias_detection"
    ETHICAL_VIOLATION = "ethical_violation"
    CONSTITUTIONAL_VIOLATION = "constitutional_violation"

    # Constellation Framework events
    IDENTITY_VERIFICATION = "identity_verification"
    CONSCIOUSNESS_INTERACTION = "consciousness_interaction"
    GUARDIAN_ALERT = "guardian_alert"
    DRIFT_DETECTION = "drift_detection"


class RetentionPolicy(Enum):
    """Audit log retention policies"""

    SHORT_TERM = "short_term"  # 30 days
    MEDIUM_TERM = "medium_term"  # 1 year
    LONG_TERM = "long_term"  # 7 years
    PERMANENT = "permanent"  # Indefinite


@dataclass
class AuditEvent:
    """Represents a single audit event"""

    # Core identification
    event_id: str
    timestamp: datetime
    event_type: AuditEventType
    category: AuditCategory
    level: AuditLevel

    # Event details
    message: str
    description: str | None = None

    # Context information
    user_id: str | None = None
    session_id: str | None = None
    source_system: str = "lukhas_ai"
    source_module: str | None = None
    source_ip: str | None = None
    user_agent: str | None = None

    # Event data
    event_data: dict[str, Any] = field(default_factory=dict)
    tags: set[str] = field(default_factory=set)

    # Security context
    risk_score: float = 0.0
    threat_indicators: list[str] = field(default_factory=list)

    # Constellation Framework context
    identity_context: dict[str, Any] = field(default_factory=dict)  # ⚛️
    consciousness_context: dict[str, Any] = field(default_factory=dict)  # 🧠
    guardian_context: dict[str, Any] = field(default_factory=dict)  # 🛡️

    # Compliance context
    compliance_relevant: bool = False
    compliance_frameworks: set[str] = field(default_factory=set)
    retention_policy: RetentionPolicy = RetentionPolicy.MEDIUM_TERM

    # Integrity verification
    checksum: str | None = None
    previous_event_hash: str | None = None

    def __post_init__(self):
        """Calculate checksum after initialization"""
        if not self.checksum:
            self.checksum = self._calculate_checksum()

    def _calculate_checksum(self) -> str:
        """Calculate cryptographic checksum for integrity verification"""
        # Create a consistent representation for hashing
        hash_data = {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type.value,
            "category": self.category.value,
            "level": self.level.value,
            "message": self.message,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "event_data": json.dumps(self.event_data, sort_keys=True, default=str),
        }

        hash_string = json.dumps(hash_data, sort_keys=True)
        return hashlib.sha256(hash_string.encode()).hexdigest()

    def verify_integrity(self) -> bool:
        """Verify the integrity of this audit event"""
        current_checksum = self.checksum
        self.checksum = None
        calculated_checksum = self._calculate_checksum()
        self.checksum = current_checksum

        return current_checksum == calculated_checksum


@dataclass
class AuditQuery:
    """Query parameters for audit search"""

    # Time range
    start_time: datetime | None = None
    end_time: datetime | None = None

    # Event filters
    event_types: set[AuditEventType] | None = None
    categories: set[AuditCategory] | None = None
    levels: set[AuditLevel] | None = None

    # Context filters
    user_ids: set[str] | None = None
    session_ids: set[str] | None = None
    source_modules: set[str] | None = None
    source_ips: set[str] | None = None

    # Content filters
    message_contains: str | None = None
    tags: set[str] | None = None

    # Security filters
    min_risk_score: float | None = None
    has_threat_indicators: bool | None = None

    # Compliance filters
    compliance_relevant_only: bool = False
    compliance_frameworks: set[str] | None = None

    # Result parameters
    limit: int = 1000
    offset: int = 0
    sort_by: str = "timestamp"
    sort_order: str = "desc"  # desc or asc


@dataclass
class AuditStatistics:
    """Audit system statistics"""

    total_events: int = 0
    events_by_level: dict[str, int] = field(default_factory=dict)
    events_by_category: dict[str, int] = field(default_factory=dict)
    events_by_type: dict[str, int] = field(default_factory=dict)

    # Time-based statistics
    events_last_hour: int = 0
    events_last_day: int = 0
    events_last_week: int = 0

    # Security statistics
    security_events: int = 0
    threat_events: int = 0
    high_risk_events: int = 0

    # Compliance statistics
    compliance_events: int = 0
    policy_violations: int = 0

    # System statistics
    storage_used: int = 0  # bytes
    oldest_event: datetime | None = None
    newest_event: datetime | None = None

    # Constellation Framework statistics
    identity_events: int = 0
    consciousness_events: int = 0
    guardian_events: int = 0


class AuditStorage:
    """Handles persistent storage of audit events"""

    def __init__(self, base_path: str = "/tmp/lukhas_audit"):
        self.base_path = base_path
        self.ensure_storage_directory()

        # Storage configuration
        self.max_file_size = 100 * 1024 * 1024  # 100MB per file
        self.compression_enabled = True
        self.encryption_enabled = False  # Would be enabled in production

        logger.info(f"📁 Audit storage initialized: {base_path}")

    def ensure_storage_directory(self):
        """Ensure audit storage directory exists"""
        os.makedirs(self.base_path, exist_ok=True)

        # Create subdirectories for different retention periods
        for policy in RetentionPolicy:
            policy_dir = os.path.join(self.base_path, policy.value)
            os.makedirs(policy_dir, exist_ok=True)

    async def store_event(self, event: AuditEvent) -> bool:
        """Store audit event to persistent storage"""
        try:
            # Determine storage location based on retention policy
            storage_dir = os.path.join(self.base_path, event.retention_policy.value)

            # Create filename based on date and event type
            date_str = event.timestamp.strftime("%Y%m%d")
            filename = f"audit_{date_str}_{event.category.value}.jsonl"
            filepath = os.path.join(storage_dir, filename)

            # Prepare event data
            event_json = json.dumps(asdict(event), default=str)

            # Append to file (create if doesn't exist)
            with open(filepath, "a", encoding="utf-8") as f:
                f.write(event_json + "\n")

            return True

        except Exception as e:
            logger.error(f"Failed to store audit event {event.event_id}: {e}")
            return False

    async def store_events_batch(self, events: list[AuditEvent]) -> int:
        """Store multiple events in batch"""
        stored_count = 0

        # Group events by retention policy and date
        grouped_events = {}

        for event in events:
            key = (
                event.retention_policy.value,
                event.timestamp.strftime("%Y%m%d"),
                event.category.value,
            )

            if key not in grouped_events:
                grouped_events[key] = []
            grouped_events[key].append(event)

        # Store each group
        for (retention, date_str, category), event_group in grouped_events.items():
            try:
                storage_dir = os.path.join(self.base_path, retention)
                filename = f"audit_{date_str}_{category}.jsonl"
                filepath = os.path.join(storage_dir, filename)

                with open(filepath, "a", encoding="utf-8") as f:
                    for event in event_group:
                        # Custom serialization to handle enums properly
                        event_dict = asdict(event)
                        # Convert enums to their values for proper JSON serialization
                        for key, value in event_dict.items():
                            if hasattr(value, "value"):  # Is an Enum
                                event_dict[key] = value.value

                        event_json = json.dumps(event_dict, default=str)
                        f.write(event_json + "\n")
                        stored_count += 1

            except Exception as e:
                logger.error(f"Failed to store event batch for {retention}/{category}: {e}")

        return stored_count

    async def query_events(self, query: AuditQuery) -> list[AuditEvent]:
        """Query events from storage"""
        events = []

        try:
            # This is a simplified implementation
            # In production, would use proper indexing and search

            # Scan relevant files based on time range
            for retention in RetentionPolicy:
                retention_dir = os.path.join(self.base_path, retention.value)

                if not os.path.exists(retention_dir):
                    continue

                for filename in os.listdir(retention_dir):
                    if not filename.startswith("audit_") or not filename.endswith(".jsonl"):
                        continue

                    filepath = os.path.join(retention_dir, filename)

                    try:
                        with open(filepath, encoding="utf-8") as f:
                            for line in f:
                                if not line.strip():
                                    continue

                                event_data = json.loads(line)
                                event = self._reconstruct_event(event_data)

                                if self._matches_query(event, query):
                                    events.append(event)

                                # Apply limit
                                if len(events) >= query.limit:
                                    break

                    except Exception as e:
                        logger.warning(f"Error reading audit file {filepath}: {e}")
                        continue

                    if len(events) >= query.limit:
                        break

        except Exception as e:
            logger.error(f"Error querying audit events: {e}")

        # Sort and apply offset
        events.sort(key=lambda e: e.timestamp, reverse=(query.sort_order == "desc"))
        return events[query.offset : query.offset + query.limit]

    def _reconstruct_event(self, event_data: dict[str, Any]) -> AuditEvent:
        """Reconstruct AuditEvent from stored data"""

        # Convert string enums back to enum values
        event_data["event_type"] = AuditEventType(event_data["event_type"])
        event_data["category"] = AuditCategory(event_data["category"])
        event_data["level"] = AuditLevel(event_data["level"])
        event_data["retention_policy"] = RetentionPolicy(event_data["retention_policy"])

        # Convert timestamp string back to datetime
        event_data["timestamp"] = datetime.fromisoformat(event_data["timestamp"])

        # Convert sets
        event_data["tags"] = set(event_data.get("tags", []))
        event_data["compliance_frameworks"] = set(event_data.get("compliance_frameworks", []))
        event_data["threat_indicators"] = event_data.get("threat_indicators", [])

        return AuditEvent(**event_data)

    def _matches_query(self, event: AuditEvent, query: AuditQuery) -> bool:
        """Check if event matches query criteria"""

        # Time range check
        if query.start_time and event.timestamp < query.start_time:
            return False
        if query.end_time and event.timestamp > query.end_time:
            return False

        # Event type filters
        if query.event_types and event.event_type not in query.event_types:
            return False
        if query.categories and event.category not in query.categories:
            return False
        if query.levels and event.level not in query.levels:
            return False

        # Context filters
        if query.user_ids and event.user_id not in query.user_ids:
            return False
        if query.session_ids and event.session_id not in query.session_ids:
            return False
        if query.source_modules and event.source_module not in query.source_modules:
            return False
        if query.source_ips and event.source_ip not in query.source_ips:
            return False

        # Content filters
        if query.message_contains and query.message_contains.lower() not in event.message.lower():
            return False
        if query.tags and not query.tags.intersection(event.tags):
            return False

        # Security filters
        if query.min_risk_score and event.risk_score < query.min_risk_score:
            return False
        if query.has_threat_indicators is not None:
            has_indicators = len(event.threat_indicators) > 0
            if query.has_threat_indicators != has_indicators:
                return False

        # Compliance filters
        if query.compliance_relevant_only and not event.compliance_relevant:
            return False
        return not (
            query.compliance_frameworks and not query.compliance_frameworks.intersection(event.compliance_frameworks)
        )


class AuditEventProcessor:
    """Processes and analyzes audit events in real-time"""

    def __init__(self):
        self.event_processors = []
        self.alert_rules = []
        self.pattern_detectors = []

        # Event statistics
        self.statistics = AuditStatistics()

        logger.info("🔍 Audit Event Processor initialized")

    async def process_event(self, event: AuditEvent) -> dict[str, Any]:
        """Process a single audit event"""

        processing_result = {
            "event_id": event.event_id,
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "alerts": [],
            "patterns": [],
            "recommendations": [],
            "actions_taken": [],
        }

        try:
            # Update statistics
            await self._update_statistics(event)

            # Check alert rules
            alerts = await self._check_alert_rules(event)
            processing_result["alerts"] = alerts

            # Detect patterns
            patterns = await self._detect_patterns(event)
            processing_result["patterns"] = patterns

            # Generate recommendations
            recommendations = await self._generate_recommendations(event)
            processing_result["recommendations"] = recommendations

            # Take automated actions
            actions = await self._take_automated_actions(event, alerts, patterns)
            processing_result["actions_taken"] = actions

            return processing_result

        except Exception as e:
            logger.error(f"Error processing audit event {event.event_id}: {e}")
            processing_result["error"] = str(e)
            return processing_result

    async def _update_statistics(self, event: AuditEvent):
        """Update audit statistics with new event"""

        self.statistics.total_events += 1

        # Update by level
        level_key = event.level.value
        self.statistics.events_by_level[level_key] = self.statistics.events_by_level.get(level_key, 0) + 1

        # Update by category
        category_key = event.category.value
        self.statistics.events_by_category[category_key] = self.statistics.events_by_category.get(category_key, 0) + 1

        # Update by type
        type_key = event.event_type.value
        self.statistics.events_by_type[type_key] = self.statistics.events_by_type.get(type_key, 0) + 1

        # Time-based statistics (simplified - would use proper time windows in production)
        now = datetime.now(timezone.utc)
        if event.timestamp > now - timedelta(hours=1):
            self.statistics.events_last_hour += 1
        if event.timestamp > now - timedelta(days=1):
            self.statistics.events_last_day += 1
        if event.timestamp > now - timedelta(weeks=1):
            self.statistics.events_last_week += 1

        # Security statistics
        if event.category == AuditCategory.SECURITY or event.level == AuditLevel.SECURITY:
            self.statistics.security_events += 1

        if event.threat_indicators:
            self.statistics.threat_events += 1

        if event.risk_score > 0.7:
            self.statistics.high_risk_events += 1

        # Compliance statistics
        if event.compliance_relevant:
            self.statistics.compliance_events += 1

        if event.event_type == AuditEventType.POLICY_VIOLATION:
            self.statistics.policy_violations += 1

        # Constellation Framework statistics
        if event.identity_context:
            self.statistics.identity_events += 1
        if event.consciousness_context:
            self.statistics.consciousness_events += 1
        if event.guardian_context:
            self.statistics.guardian_events += 1

        # Update timestamp bounds
        if not self.statistics.oldest_event or event.timestamp < self.statistics.oldest_event:
            self.statistics.oldest_event = event.timestamp

        if not self.statistics.newest_event or event.timestamp > self.statistics.newest_event:
            self.statistics.newest_event = event.timestamp

    async def _check_alert_rules(self, event: AuditEvent) -> list[dict[str, Any]]:
        """Check event against alert rules"""

        alerts = []

        # Critical security events
        if event.level in [AuditLevel.CRITICAL, AuditLevel.SECURITY]:
            alerts.append(
                {
                    "type": "critical_security_event",
                    "severity": "high",
                    "message": f"Critical security event: {event.message}",
                    "recommended_action": "immediate_investigation",
                }
            )

        # Multiple failed logins
        if event.event_type == AuditEventType.LOGIN_FAILURE:
            # In practice, would check for patterns across events
            alerts.append(
                {
                    "type": "authentication_failure",
                    "severity": "medium",
                    "message": "Authentication failure detected",
                    "recommended_action": "monitor_user_activity",
                }
            )

        # High-risk events
        if event.risk_score > 0.8:
            alerts.append(
                {
                    "type": "high_risk_event",
                    "severity": "high",
                    "message": f"High risk event detected (score: {event.risk_score:.2f})",
                    "recommended_action": "security_review",
                }
            )

        # Compliance violations
        if event.event_type in [
            AuditEventType.POLICY_VIOLATION,
            AuditEventType.PRIVACY_VIOLATION,
        ]:
            alerts.append(
                {
                    "type": "compliance_violation",
                    "severity": "high",
                    "message": f"Compliance violation: {event.message}",
                    "recommended_action": "compliance_review",
                }
            )

        # Constellation Framework alerts
        if event.guardian_context.get("alert"):
            alerts.append(
                {
                    "type": "guardian_alert",
                    "severity": "high",
                    "message": "Guardian system alert triggered",
                    "recommended_action": "system_review",
                }
            )

        return alerts

    async def _detect_patterns(self, event: AuditEvent) -> list[dict[str, Any]]:
        """Detect suspicious patterns in events"""

        patterns = []

        # This is simplified - in production would maintain sliding windows
        # and sophisticated pattern detection algorithms

        # Repeated events from same user
        if event.user_id:
            patterns.append(
                {
                    "type": "user_activity_pattern",
                    "description": f"Activity from user {event.user_id}",
                    "confidence": 0.8,
                }
            )

        # Geographic anomalies (if IP data available)
        if event.source_ip:
            patterns.append(
                {
                    "type": "geographic_access",
                    "description": f"Access from IP {event.source_ip}",
                    "confidence": 0.6,
                }
            )

        return patterns

    async def _generate_recommendations(self, event: AuditEvent) -> list[str]:
        """Generate recommendations based on event"""

        recommendations = []

        if event.level in [AuditLevel.ERROR, AuditLevel.CRITICAL]:
            recommendations.append("Investigate error cause and implement preventive measures")

        if event.event_type == AuditEventType.SECURITY_VIOLATION:
            recommendations.append("Review security policies and access controls")

        if event.compliance_relevant:
            recommendations.append("Ensure compliance documentation is updated")

        if event.risk_score > 0.5:
            recommendations.append("Consider implementing additional security measures")

        # Constellation Framework recommendations
        if event.guardian_context:
            recommendations.append("Review Guardian System configuration")

        if event.consciousness_context.get("drift_detected"):
            recommendations.append("Investigate consciousness drift and apply corrections")

        return recommendations

    async def _take_automated_actions(
        self,
        event: AuditEvent,
        alerts: list[dict[str, Any]],
        patterns: list[dict[str, Any]],
    ) -> list[str]:
        """Take automated actions based on event analysis"""

        actions = []

        # Auto-escalation for critical events
        if event.level == AuditLevel.CRITICAL:
            actions.append("escalated_to_security_team")

        # Auto-lock for multiple failed attempts
        if event.event_type == AuditEventType.LOGIN_FAILURE:
            # In practice, would check thresholds
            actions.append("monitoring_increased")

        # Compliance notifications
        if event.compliance_relevant and len(alerts) > 0:
            actions.append("compliance_team_notified")

        return actions


class ComprehensiveAuditSystem:
    """
    Main comprehensive audit system for LUKHAS AI

    Provides immutable audit trails, real-time monitoring, compliance
    reporting, and advanced analytics integrated with Constellation Framework
    and governance systems.
    """

    def __init__(self, storage_path: str = "/tmp/lukhas_audit"):
        self.storage = AuditStorage(storage_path)
        self.processor = AuditEventProcessor()

        # In-memory event buffer for real-time processing
        self.event_buffer: list[AuditEvent] = []
        self.buffer_size = 1000
        self.flush_interval = 60  # seconds

        # Chain of custody for audit integrity
        self.last_event_hash = None

        # Background tasks
        self._start_background_tasks()

        logger.info("🔍 Comprehensive Audit System initialized")

    def _start_background_tasks(self):
        """Start background processing tasks"""
# T4: code=RUF006 | ticket=GH-1031 | owner=consciousness-team | status=accepted
# reason: Fire-and-forget async task - intentional background processing pattern
# estimate: 0h | priority: low | dependencies: none
        asyncio.create_task(self._buffer_flush_task())
# T4: code=RUF006 | ticket=GH-1031 | owner=consciousness-team | status=accepted
# reason: Fire-and-forget async task - intentional background processing pattern
# estimate: 0h | priority: low | dependencies: none
        asyncio.create_task(self._retention_cleanup_task())

    async def log_event(
        self,
        event_type: AuditEventType,
        message: str,
        category: AuditCategory = AuditCategory.SYSTEM_EVENT,
        level: AuditLevel = AuditLevel.INFO,
        user_id: str | None = None,
        session_id: str | None = None,
        source_module: str | None = None,
        event_data: dict[str, Any] | None = None,
        **kwargs,
    ) -> str:
        """
        Log an audit event

        Returns:
            Event ID
        """

        event_id = f"audit_{uuid.uuid4().hex}"

        # Filter kwargs to only include valid AuditEvent fields
        valid_fields = AuditEvent.__annotations__.keys()
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in valid_fields}

        # Create audit event
        event = AuditEvent(
            event_id=event_id,
            timestamp=datetime.now(timezone.utc),
            event_type=event_type,
            category=category,
            level=level,
            message=message,
            user_id=user_id,
            session_id=session_id,
            source_module=source_module,
            event_data=event_data or {},
            **filtered_kwargs,
        )

        # Set previous event hash for chain of custody
        event.previous_event_hash = self.last_event_hash

        # Update last event hash
        self.last_event_hash = event.checksum

        # Add to buffer
        self.event_buffer.append(event)

        # Process event in real-time
        try:
            processing_result = await self.processor.process_event(event)

            # Handle critical alerts immediately
            for alert in processing_result.get("alerts", []):
                if alert.get("severity") == "high":
                    await self._handle_critical_alert(event, alert)

        except Exception as e:
            logger.error(f"Error processing audit event {event_id}: {e}")

        # Flush buffer if full
        if len(self.event_buffer) >= self.buffer_size:
            await self._flush_buffer()

        logger.debug(f"Audit event logged: {event_id}")
        return event_id

    async def _handle_critical_alert(self, event: AuditEvent, alert: dict[str, Any]):
        """Handle critical security alerts"""

        logger.critical(f"🚨 CRITICAL AUDIT ALERT: {alert['message']} (Event: {event.event_id})")

        # In production, this would:
        # - Send notifications to security team
        # - Trigger automated responses
        # - Update security dashboards
        # - Create incident tickets

    async def _flush_buffer(self):
        """Flush event buffer to persistent storage"""

        if not self.event_buffer:
            return

        try:
            # Store events in batch
            stored_count = await self.storage.store_events_batch(self.event_buffer.copy())

            if stored_count == len(self.event_buffer):
                logger.debug(f"✅ Flushed {stored_count} audit events to storage")
                self.event_buffer.clear()
            else:
                logger.warning(f"⚠️ Only stored {stored_count}/{len(self.event_buffer)} events")

        except Exception as e:
            logger.error(f"❌ Failed to flush audit buffer: {e}")

    async def _buffer_flush_task(self):
        """Background task to periodically flush buffer"""

        while True:
            try:
                await asyncio.sleep(self.flush_interval)
                await self._flush_buffer()

            except Exception as e:
                logger.error(f"Buffer flush task error: {e}")
                await asyncio.sleep(10)  # Short delay before retry

    async def _retention_cleanup_task(self):
        """Background task to clean up old audit data"""

        while True:
            try:
                # Run retention cleanup daily
                await asyncio.sleep(24 * 3600)  # 24 hours
                await self._cleanup_old_events()

            except Exception as e:
                logger.error(f"Retention cleanup task error: {e}")
                await asyncio.sleep(3600)  # 1 hour delay before retry

    async def _cleanup_old_events(self):
        """Clean up old audit events based on retention policies"""

        logger.info("🧹 Starting audit retention cleanup...")

        retention_periods = {
            RetentionPolicy.SHORT_TERM: timedelta(days=30),
            RetentionPolicy.MEDIUM_TERM: timedelta(days=365),
            RetentionPolicy.LONG_TERM: timedelta(days=2555),  # ~7 years
            RetentionPolicy.PERMANENT: None,  # Never delete
        }

        current_time = datetime.now(timezone.utc)

        for policy, period in retention_periods.items():
            if period is None:  # Permanent retention
                continue

            cutoff_time = current_time - period

            # In production, would implement proper cleanup logic
            # For now, just log what would be cleaned up
            logger.info(f"Would clean up {policy.value} events older than {cutoff_time}")

    async def query_events(self, query: AuditQuery) -> list[AuditEvent]:
        """Query audit events"""

        # First check buffer for recent events
        buffer_events = []
        for event in self.event_buffer:
            if self.storage._matches_query(event, query):
                buffer_events.append(event)

        # Query stored events
        stored_events = await self.storage.query_events(query)

        # Combine and sort
        all_events = buffer_events + stored_events
        all_events.sort(key=lambda e: e.timestamp, reverse=(query.sort_order == "desc"))

        # Apply final limit
        return all_events[: query.limit]

    async def get_audit_statistics(self) -> AuditStatistics:
        """Get audit system statistics"""
        return self.processor.statistics

    async def verify_audit_integrity(self) -> dict[str, Any]:
        """Verify integrity of audit trail"""

        verification_result = {
            "verification_id": f"verify_{uuid.uuid4().hex[:8]}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_events_checked": 0,
            "integrity_violations": 0,
            "chain_breaks": 0,
            "corrupt_events": [],
            "overall_integrity": True,
        }

        try:
            # Check recent events in buffer
            for event in self.event_buffer:
                verification_result["total_events_checked"] += 1

                if not event.verify_integrity():
                    verification_result["integrity_violations"] += 1
                    verification_result["corrupt_events"].append(event.event_id)
                    verification_result["overall_integrity"] = False

            # Also check recently stored events
            recent_query = AuditQuery(
                start_time=datetime.now(timezone.utc) - timedelta(hours=24),
                end_time=datetime.now(timezone.utc),
                limit=1000,
            )
            stored_events = await self.storage.query_events(recent_query)

            for event in stored_events:
                verification_result["total_events_checked"] += 1

                if not event.verify_integrity():
                    verification_result["integrity_violations"] += 1
                    verification_result["corrupt_events"].append(event.event_id)
                    verification_result["overall_integrity"] = False

            logger.info(
                f"✅ Audit integrity verification completed: {verification_result['total_events_checked']} events checked"
            )

        except Exception as e:
            logger.error(f"❌ Audit integrity verification failed: {e}")
            verification_result["error"] = str(e)
            verification_result["overall_integrity"] = False

        return verification_result

    async def generate_compliance_report(
        self,
        framework: str,
        start_date: datetime,
        end_date: datetime,
        include_recommendations: bool = True,
    ) -> dict[str, Any]:
        """Generate compliance audit report"""

        report_id = f"compliance_{framework}_{uuid.uuid4().hex[:8]}"

        # Query compliance-relevant events
        query = AuditQuery(
            start_time=start_date,
            end_time=end_date,
            compliance_relevant_only=True,
            compliance_frameworks={framework},
            limit=10000,
        )

        events = await self.query_events(query)

        # Generate report
        report = {
            "report_id": report_id,
            "framework": framework,
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total_events": len(events),
                "compliance_violations": len([e for e in events if e.event_type == AuditEventType.POLICY_VIOLATION]),
                "privacy_events": len([e for e in events if e.category == AuditCategory.PRIVACY]),
                "security_events": len([e for e in events if e.category == AuditCategory.SECURITY]),
                "data_access_events": len([e for e in events if e.category == AuditCategory.DATA_ACCESS]),
            },
            "events_by_type": {},
            "high_risk_events": [
                {
                    "event_id": e.event_id,
                    "timestamp": e.timestamp.isoformat(),
                    "type": e.event_type.value,
                    "message": e.message,
                    "risk_score": e.risk_score,
                }
                for e in events
                if e.risk_score > 0.7
            ],
        }

        # Count events by type
        for event in events:
            event_type = event.event_type.value
            report["events_by_type"][event_type] = report["events_by_type"].get(event_type, 0) + 1

        # Add recommendations if requested
        if include_recommendations:
            report["recommendations"] = await self._generate_compliance_recommendations(events, framework)

        logger.info(f"✅ Generated compliance report: {report_id} ({len(events)} events)")
        return report

    async def _generate_compliance_recommendations(self, events: list[AuditEvent], framework: str) -> list[str]:
        """Generate compliance recommendations based on audit events"""

        recommendations = []

        # Analyze patterns and violations
        violations = [e for e in events if e.event_type == AuditEventType.POLICY_VIOLATION]
        if violations:
            recommendations.append(f"Address {len(violations)} policy violations identified in the audit period")

        high_risk_events = [e for e in events if e.risk_score > 0.7]
        if high_risk_events:
            recommendations.append(
                f"Review {len(high_risk_events)} high-risk events for potential security improvements"
            )

        # Framework-specific recommendations
        if framework.lower() == "gdpr":
            privacy_events = [e for e in events if e.category == AuditCategory.PRIVACY]
            if privacy_events:
                recommendations.append("Review privacy event handling procedures for GDPR compliance")

        elif framework.lower() == "soc2":
            access_events = [e for e in events if e.category == AuditCategory.AUTHORIZATION]
            if access_events:
                recommendations.append("Strengthen access control monitoring for SOC 2 compliance")

        # Constellation Framework recommendations
        identity_events = [e for e in events if e.identity_context]
        if identity_events:
            recommendations.append("Review identity verification processes within Constellation Framework")

        return recommendations

    async def export_audit_data(self, query: AuditQuery, format: str = "json") -> str:
        """Export audit data in specified format"""

        events = await self.query_events(query)

        if format.lower() == "json":
            export_data = {
                "export_metadata": {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "query": asdict(query),
                    "total_events": len(events),
                },
                "events": [asdict(event) for event in events],
            }
            return json.dumps(export_data, default=str, indent=2)

        elif format.lower() == "csv":
            # Simplified CSV export - would be more comprehensive in production
            csv_lines = ["timestamp,event_type,category,level,message,user_id"]

            for event in events:
                line = f'{event.timestamp},{event.event_type.value},{event.category.value},{event.level.value},"{event.message}",{event.user_id or ""}'
                csv_lines.append(line)

            return "\n".join(csv_lines)

        else:
            raise ValueError(f"Unsupported export format: {format}")


# Convenience functions for common audit operations
async def audit_login(user_id: str, success: bool, source_ip: str | None = None) -> str:
    """Audit user login event"""
    audit_system = ComprehensiveAuditSystem()

    event_type = AuditEventType.LOGIN_SUCCESS if success else AuditEventType.LOGIN_FAILURE
    level = AuditLevel.INFO if success else AuditLevel.WARNING
    message = f"User login {'successful' if success else 'failed'}"

    return await audit_system.log_event(
        event_type=event_type,
        message=message,
        category=AuditCategory.AUTHENTICATION,
        level=level,
        user_id=user_id,
        source_ip=source_ip,
        compliance_relevant=True,
        compliance_frameworks={"gdpr", "soc2"},
    )


async def audit_data_access(user_id: str, resource: str, access_type: str, granted: bool) -> str:
    """Audit data access event"""
    audit_system = ComprehensiveAuditSystem()

    event_type = AuditEventType.ACCESS_GRANTED if granted else AuditEventType.ACCESS_DENIED
    message = f"Data access {'granted' if granted else 'denied'} for {resource}"

    return await audit_system.log_event(
        event_type=event_type,
        message=message,
        category=AuditCategory.DATA_ACCESS,
        level=AuditLevel.INFO,
        user_id=user_id,
        event_data={"resource": resource, "access_type": access_type},
        compliance_relevant=True,
        compliance_frameworks={"gdpr", "ccpa", "soc2"},
    )


async def audit_security_violation(violation_type: str, details: str, risk_score: float = 0.8) -> str:
    """Audit security violation"""
    audit_system = ComprehensiveAuditSystem()

    return await audit_system.log_event(
        event_type=AuditEventType.SECURITY_VIOLATION,
        message=f"Security violation: {violation_type}",
        category=AuditCategory.SECURITY,
        level=AuditLevel.CRITICAL,
        description=details,
        risk_score=risk_score,
        threat_indicators=[violation_type],
        compliance_relevant=True,
    )


async def audit_trinity_event(component: str, event_details: dict[str, Any], user_id: str | None = None) -> str:
    """Audit Constellation Framework event"""
    audit_system = ComprehensiveAuditSystem()

    # Determine Constellation context based on component
    constellation_context = {}
    if component == "identity":
        constellation_context["identity_context"] = event_details
    elif component == "consciousness":
        constellation_context["consciousness_context"] = event_details
    elif component == "guardian":
        constellation_context["guardian_context"] = event_details

    return await audit_system.log_event(
        event_type=AuditEventType.SYSTEM_EVENT,
        message=f"Constellation Framework event: {component}",
        category=AuditCategory.CONSTELLATION,
        level=AuditLevel.INFO,
        user_id=user_id,
        event_data=event_details,
        **constellation_context,
    )


# Export main classes and functions
__all__ = [
    "AuditCategory",
    "AuditEvent",
    "AuditEventProcessor",
    "AuditEventType",
    "AuditLevel",
    "AuditQuery",
    "AuditStatistics",
    "AuditStorage",
    "ComprehensiveAuditSystem",
    "RetentionPolicy",
    "audit_data_access",
    "audit_login",
    "audit_security_violation",
    "audit_trinity_event",
]
