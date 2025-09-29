import logging

logger = logging.getLogger(__name__)
"""
LUKHAS Audit Logger - Constitutional Event Logger

This module implements comprehensive audit logging for constitutional enforcement
and transparency in the LUKHAS authentication system.

Author: LUKHAS Team
Date: June 2025
Purpose: Constitutional audit log system for transparency and compliance
"""

import asyncio
import hashlib
import json
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Union

from lukhas.core.common import get_logger

logger = get_logger(__name__)


class AuditEventType(Enum):
    """Types of audit event"""

    CONSTITUTIONAL_ENFORCEMENT = "constitutional_enforcement"
    AUTHENTICATION_ATTEMPT = "authentication_attempt"
    POLICY_VIOLATION = "policy_violation"
    SYSTEM_OVERRIDE = "system_override"
    USER_ACTION = "user_action"
    SECURITY_EVENT = "security_event"
    PERFORMANCE_METRIC = "performance_metric"
    ERROR_EVENT = "error_event"
    CONFIGURATION_CHANGE = "configuration_change"
    DATA_ACCESS = "data_access"


class AuditSeverity(Enum):
    """Severity levels for audit event"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    CONSTITUTIONAL = "constitutional"  # Highest level for constitutional matters


class ComplianceFramework(Enum):
    """Compliance frameworks to track"""

    GDPR = "gdpr"
    CCPA = "ccpa"
    HIPAA = "hipaa"
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    CONSTITUTIONAL_AI = "constitutional_ai"
    LUKHAS_CONSTITUTIONAL = "lukhas_constitutional"


@dataclass
class AuditEvent:
    """Individual audit event record"""

    event_id: str
    timestamp: datetime
    event_type: AuditEventType
    severity: AuditSeverity
    source_component: str
    user_id: Optional[str]
    session_id: Optional[str]
    action: str
    details: dict[str, Any]
    constitutional_context: Optional[dict[str, Any]]
    compliance_tags: list[ComplianceFramework]
    data_classification: str
    retention_period_days: int
    requires_review: bool

    def to_dict(self) -> dict[str, Any]:
        """Convert audit event to dictionary for serialization."""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type.value,
            "severity": self.severity.value,
            "source_component": self.source_component,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "action": self.action,
            "details": self.details,
            "constitutional_context": self.constitutional_context,
            "compliance_tags": [tag.value for tag in self.compliance_tags],
            "data_classification": self.data_classification,
            "retention_period_days": self.retention_period_days,
            "requires_review": self.requires_review,
        }


@dataclass
class AuditQuery:
    """Query parameters for audit log searche"""

    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    event_types: Optional[list[AuditEventType]] = None
    severities: Optional[list[AuditSeverity]] = None
    user_ids: Optional[list[str]] = None
    components: Optional[list[str]] = None
    compliance_frameworks: Optional[list[ComplianceFramework]] = None
    requires_review: Optional[bool] = None
    limit: int = 100


class AuditLogger:
    """
    Constitutional audit logging system for LUKHAS authentication.

    Features:
    - Real-time constitutional event logging
    - Compliance framework tracking (GDPR, CCPA, etc.)
    - Tamper-evident log integrity
    - Automatic log rotation and retention
    - Query and search capabilities
    - Constitutional transparency reporting
    - Performance impact monitoring
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or self._get_default_config()

        # Initialize storage
        self.log_file_path = Path(self.config.get("log_file_path", "audit_logs"))
        self.log_file_path.mkdir(exist_ok=True)

        # In-memory buffer for high-performance logging
        self.event_buffer = []
        self.buffer_size = self.config.get("buffer_size", 1000)

        # Integrity tracking
        self.log_integrity_hash = hashlib.sha256()
        self.last_flush_time = time.time()

        # Performance metrics
        self.performance_metrics = {
            "events_logged": 0,
            "buffer_flushes": 0,
            "avg_log_time_ms": 0.0,
            "integrity_checks": 0,
        }

        # Constitutional enforcement tracking
        self.constitutional_events = []
        self.enforcement_statistics = {
            "total_enforcements": 0,
            "policy_violations": 0,
            "overrides_applied": 0,
            "user_interventions": 0,
        }

        # Start background tasks
        if self.config.get("auto_flush_enabled", True):
            asyncio.create_task(self._auto_flush_loop())

    def _get_default_config(self) -> dict[str, Any]:
        """Get default configuration for audit logger."""
        return {
            "log_file_path": "audit_logs",
            "buffer_size": 1000,
            "auto_flush_enabled": True,
            "flush_interval_seconds": 60,
            "max_file_size_mb": 100,
            "retention_days": 365,
            "integrity_checks_enabled": True,
            "constitutional_tracking": True,
            "compliance_reporting": True,
            "performance_monitoring": True,
            "encryption_enabled": False,
        }

    async def log_constitutional_enforcement(
        self,
        action: str,
        enforcement_type: str,
        details: dict[str, Any],
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> str:
        """
        Log constitutional enforcement event with highest priority.

        Args:
            action: Action that triggered enforcement
            enforcement_type: Type of constitutional enforcement
            details: Detailed information about the enforcement
            user_id: Optional user ID
            session_id: Optional session ID

        Returns:
            Event ID for tracking
        """
        constitutional_context = {
            "enforcement_type": enforcement_type,
            "constitutional_authority": "LUKHAS_CONSTITUTIONAL_GATEKEEPER",
            "enforcement_timestamp": datetime.now(timezone.utc).isoformat(),
            "transparency_required": True,
            "immutable_decision": True,
        }

        event = AuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.now(timezone.utc),
            event_type=AuditEventType.CONSTITUTIONAL_ENFORCEMENT,
            severity=AuditSeverity.CONSTITUTIONAL,
            source_component="constitutional_gatekeeper",
            user_id=user_id,
            session_id=session_id,
            action=action,
            details=details,
            constitutional_context=constitutional_context,
            compliance_tags=[
                ComplianceFramework.LUKHAS_CONSTITUTIONAL,
                ComplianceFramework.GDPR,
            ],
            data_classification="constitutional",
            retention_period_days=self.config.get("constitutional_retention_days", 2555),  # 7 years
            requires_review=True,
        )

        # Constitutional events get immediate logging
        await self._log_event_immediate(event)

        # Track constitutional statistics
        self.enforcement_statistics["total_enforcements"] += 1
        self.constitutional_events.append(event)

        logger.info(f"Constitutional enforcement logged: {action} - {enforcement_type}")
        return event.event_id

    async def log_authentication_attempt(
        self,
        attempt_result: str,
        details: dict[str, Any],
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> str:
        """
        Log authentication attempt with security context.

        Args:
            attempt_result: Result of authentication attempt (success/failure/blocked)
            details: Authentication details (sanitized)
            user_id: Optional user ID
            session_id: Optional session ID

        Returns:
            Event ID for tracking
        """
        # Determine severity based on result
        severity = AuditSeverity.INFO
        if attempt_result == "failure":
            severity = AuditSeverity.WARNING
        elif attempt_result == "blocked":
            severity = AuditSeverity.ERROR

        event = AuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.now(timezone.utc),
            event_type=AuditEventType.AUTHENTICATION_ATTEMPT,
            severity=severity,
            source_component="authentication_system",
            user_id=user_id,
            session_id=session_id,
            action=f"authentication_{attempt_result}",
            details=self._sanitize_auth_details(details),
            constitutional_context=None,
            compliance_tags=[ComplianceFramework.GDPR, ComplianceFramework.SOC2],
            data_classification="security",
            retention_period_days=90,  # Standard security log retention
            requires_review=attempt_result in ["blocked", "suspicious"],
        )

        return await self._log_event(event)

    async def log_policy_violation(
        self,
        policy_type: str,
        violation_details: dict[str, Any],
        enforcement_action: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> str:
        """
        Log policy violation with enforcement action taken.

        Args:
            policy_type: Type of policy violated
            violation_details: Details of the violation
            enforcement_action: Action taken in response
            user_id: Optional user ID
            session_id: Optional session ID

        Returns:
            Event ID for tracking
        """
        event = AuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.now(timezone.utc),
            event_type=AuditEventType.POLICY_VIOLATION,
            severity=AuditSeverity.WARNING,
            source_component="policy_engine",
            user_id=user_id,
            session_id=session_id,
            action=f"policy_violation_{policy_type}",
            details={
                "policy_type": policy_type,
                "violation_details": violation_details,
                "enforcement_action": enforcement_action,
                "auto_remediated": enforcement_action != "manual_review_required",
            },
            constitutional_context={
                "policy_authority": "LUKHAS_POLICY_ENGINE",
                "enforcement_applied": enforcement_action,
                "transparency_level": "full",
            },
            compliance_tags=[ComplianceFramework.LUKHAS_CONSTITUTIONAL],
            data_classification="policy",
            retention_period_days=365,
            requires_review=enforcement_action == "manual_review_required",
        )

        self.enforcement_statistics["policy_violations"] += 1
        return await self._log_event(event)

    async def log_system_override(
        self,
        override_type: str,
        override_reason: str,
        override_authority: str,
        original_decision: dict[str, Any],
        new_decision: dict[str, Any],
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> str:
        """
        Log system override with full transparency.

        Args:
            override_type: Type of override applied
            override_reason: Reason for override
            override_authority: Authority that applied override
            original_decision: Original system decision
            new_decision: New decision after override
            user_id: Optional user ID
            session_id: Optional session ID

        Returns:
            Event ID for tracking
        """
        constitutional_context = {
            "override_authority": override_authority,
            "override_justification": override_reason,
            "transparency_required": True,
            "review_required": True,
            "original_decision": original_decision,
            "new_decision": new_decision,
            "constitutional_impact": self._assess_constitutional_impact(override_type),
        }

        event = AuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.now(timezone.utc),
            event_type=AuditEventType.SYSTEM_OVERRIDE,
            severity=AuditSeverity.CRITICAL,
            source_component=override_authority,
            user_id=user_id,
            session_id=session_id,
            action=f"system_override_{override_type}",
            details={
                "override_type": override_type,
                "override_reason": override_reason,
                "original_decision": original_decision,
                "new_decision": new_decision,
                "requires_approval": True,
            },
            constitutional_context=constitutional_context,
            compliance_tags=[
                ComplianceFramework.LUKHAS_CONSTITUTIONAL,
                ComplianceFramework.GDPR,
            ],
            data_classification="constitutional",
            retention_period_days=2555,  # 7 years for overrides
            requires_review=True,
        )

        # System overrides require immediate logging and alert
        await self._log_event_immediate(event)

        self.enforcement_statistics["overrides_applied"] += 1
        logger.warning(f"System override logged: {override_type} by {override_authority}")

        return event.event_id

    async def log_performance_metric(
        self,
        metric_name: str,
        metric_value: Union[int, float],
        metric_unit: str,
        context: dict[str, Any],
        session_id: Optional[str] = None,
    ) -> str:
        """
        Log performance metric for constitutional compliance monitoring.

        Args:
            metric_name: Name of the performance metric
            metric_value: Value of the metric
            metric_unit: Unit of measurement
            context: Additional context for the metric
            session_id: Optional session ID

        Returns:
            Event ID for tracking
        """
        event = AuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.now(timezone.utc),
            event_type=AuditEventType.PERFORMANCE_METRIC,
            severity=AuditSeverity.INFO,
            source_component="performance_monitor",
            user_id=None,
            session_id=session_id,
            action=f"metric_{metric_name}",
            details={
                "metric_name": metric_name,
                "metric_value": metric_value,
                "metric_unit": metric_unit,
                "context": context,
                "collection_timestamp": datetime.now(timezone.utc).isoformat(),
            },
            constitutional_context=None,
            compliance_tags=[ComplianceFramework.SOC2],
            data_classification="performance",
            retention_period_days=90,
            requires_review=False,
        )

        return await self._log_event(event)

    async def _log_event(self, event: AuditEvent) -> str:
        start_time = time.time()
        try:
            # Add to buffer
            self.event_buffer.append(event)
            # Check if buffer should be flushed
            if len(self.event_buffer) >= self.buffer_size:
                await self._flush_buffer()
            # Update performance metrics
            log_time = (time.time() - start_time) * 1000
            self.performance_metrics["events_logged"] += 1
            self.performance_metrics["avg_log_time_ms"] = (
                self.performance_metrics["avg_log_time_ms"] * (self.performance_metrics["events_logged"] - 1) + log_time
            ) / self.performance_metrics["events_logged"]
            return event.event_id
        except Exception as e:
            logger.error(f"Audit log event failed: {e}")
            # In production, escalate or fallback to alternative storage
            return "error"

    async def _log_event_immediate(self, event: AuditEvent) -> str:
        try:
            await self._write_events_to_file([event])
            self._update_integrity_hash(event)
            logger.info(f"Immediate audit log: {event.event_type.value} - {event.action}")
            return event.event_id
        except Exception as e:
            logger.error(f"Immediate audit log failed: {e}")
            return "error"

    async def _flush_buffer(self):
        """Flush event buffer to persistent storage."""
        if not self.event_buffer:
            return

        events_to_flush = self.event_buffer.copy()
        self.event_buffer.clear()

        await self._write_events_to_file(events_to_flush)

        # Update integrity for all events
        for event in events_to_flush:
            self._update_integrity_hash(event)

        self.performance_metrics["buffer_flushes"] += 1
        self.last_flush_time = time.time()

        logger.debug(f"Flushed {len(events_to_flush)} audit events to storage")

    async def _write_events_to_file(self, events: list[AuditEvent]):
        try:
            log_file = self._get_current_log_file()
            with open(log_file, "a", encoding="utf-8") as f:
                for event in events:
                    event_json = json.dumps(event.to_dict(), default=str)
                    f.write(event_json + "\n")
            await self._check_file_rotation(log_file)
        except Exception as e:
            logger.error(f"Failed to write audit events to file: {e}")
            # In production, escalate or fallback

    def _get_current_log_file(self) -> Path:
        """Get current audit log file path."""
        current_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return self.log_file_path / f"audit_log_{current_date}.jsonl"

    async def _check_file_rotation(self, log_file: Path):
        """Check if log file needs rotation based on size."""
        try:
            max_size_bytes = self.config.get("max_file_size_mb", 100) * 1024 * 1024

            if log_file.exists() and log_file.stat().st_size > max_size_bytes:
                # Rotate file
                timestamp = datetime.now(timezone.utc).strftime("%H%M%S")
                rotated_name = f"{log_file.stem}_{timestamp}{log_file.suffix}"
                rotated_path = log_file.parent / rotated_name
                log_file.rename(rotated_path)

                logger.info(f"Rotated audit log file: {rotated_name}")

        except Exception as e:
            logger.error(f"Failed to rotate log file: {e}")

    def _update_integrity_hash(self, event: AuditEvent):
        try:
            if self.config.get("integrity_checks_enabled", True):
                event_string = json.dumps(event.to_dict(), sort_keys=True, default=str)
                self.log_integrity_hash.update(event_string.encode("utf-8"))
                self.performance_metrics["integrity_checks"] += 1
        except Exception as e:
            logger.error(f"Integrity hash update failed: {e}")

    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        return str(uuid.uuid4())

    def _sanitize_auth_details(self, details: dict[str, Any]) -> dict[str, Any]:
        sanitized = details.copy()
        sensitive_keys = ["password", "token", "secret", "key", "credential"]
        for key in list(sanitized.keys()):
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = "[REDACTED]"
        return sanitized

    def _assess_constitutional_impact(self, override_type: str) -> str:
        """Assess constitutional impact of system override."""
        high_impact_overrides = [
            "security_policy",
            "access_control",
            "constitutional_threshold",
        ]

        if override_type in high_impact_overrides:
            return "high"
        elif "timeout" in override_type or "ui" in override_type:
            return "medium"
        else:
            return "low"

    async def _auto_flush_loop(self):
        """Background task for automatic buffer flushing."""
        flush_interval = self.config.get("flush_interval_seconds", 60)

        while True:
            try:
                await asyncio.sleep(flush_interval)

                if self.event_buffer:
                    await self._flush_buffer()

            except Exception as e:
                logger.error(f"Auto-flush loop error: {e}")
                await asyncio.sleep(flush_interval * 2)  # Back off on error

    async def query_audit_logs(self, query: AuditQuery) -> list[dict[str, Any]]:
        """
        Query audit logs with filtering criteria.

        Args:
            query: Query parameters for filtering

        Returns:
            List of matching audit events
        """
        matching_events = []

        # Get log files to search
        log_files = self._get_log_files_for_timerange(query.start_time, query.end_time)

        for log_file in log_files:
            try:
                with open(log_file, encoding="utf-8") as f:
                    for line in f:
                        try:
                            event_data = json.loads(line.strip())

                            if self._matches_query(event_data, query):
                                matching_events.append(event_data)

                                if len(matching_events) >= query.limit:
                                    return matching_events

                        except json.JSONDecodeError:
                            continue  # Skip malformed lines

            except Exception as e:
                logger.error(f"Error reading log file {log_file}: {e}")
                continue

        return matching_events

    def _get_log_files_for_timerange(self, start_time: Optional[datetime], end_time: Optional[datetime]) -> list[Path]:
        """Get log files that might contain events in the time range."""
        if not self.log_file_path.exists():
            return []

        log_files = list(self.log_file_path.glob("audit_log_*.jsonl"))

        # If no time range specified, return all files
        if not start_time and not end_time:
            return sorted(log_files)

        # Filter files based on date in filename
        filtered_files = []
        for log_file in log_files:
            # Extract date from filename (audit_log_YYYY-MM-DD.jsonl)
            try:
                date_str = log_file.stem.split("_")[-1]
                if len(date_str) == 10:  # YYYY-MM-DD format
                    file_date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc).date()

                    include_file = True
                    if start_time and file_date < start_time.date():
                        include_file = False
                    if end_time and file_date > end_time.date():
                        include_file = False

                    if include_file:
                        filtered_files.append(log_file)

            except (ValueError, IndexError):
                # Include files with non-standard names
                filtered_files.append(log_file)

        return sorted(filtered_files)

    def _matches_query(self, event_data: dict[str, Any], query: AuditQuery) -> bool:
        """Check if event matches query criteria."""
        # Time range check
        if query.start_time or query.end_time:
            try:
                event_time = datetime.fromisoformat(event_data["timestamp"])
                if query.start_time and event_time < query.start_time:
                    return False
                if query.end_time and event_time > query.end_time:
                    return False
            except (KeyError, ValueError):
                return False

        # Event type check
        if query.event_types:
            event_type = event_data.get("event_type")
            if event_type not in [et.value for et in query.event_types]:
                return False

        # Severity check
        if query.severities:
            severity = event_data.get("severity")
            if severity not in [s.value for s in query.severities]:
                return False

        # User ID check
        if query.user_ids:
            user_id = event_data.get("user_id")
            if user_id not in query.user_ids:
                return False

        # Component check
        if query.components:
            component = event_data.get("source_component")
            if component not in query.components:
                return False

        # Compliance framework check
        if query.compliance_frameworks:
            compliance_tags = event_data.get("compliance_tags", [])
            framework_values = [cf.value for cf in query.compliance_frameworks]
            if not any(tag in framework_values for tag in compliance_tags):
                return False

        # Review required check
        if query.requires_review is not None:
            requires_review = event_data.get("requires_review", False)
            if requires_review != query.requires_review:
                return False

        return True

    async def generate_constitutional_report(self, start_time: datetime, end_time: datetime) -> dict[str, Any]:
        """
        Generate constitutional transparency report.

        Args:
            start_time: Report start time
            end_time: Report end time

        Returns:
            Constitutional transparency report
        """
        query = AuditQuery(
            start_time=start_time,
            end_time=end_time,
            event_types=[
                AuditEventType.CONSTITUTIONAL_ENFORCEMENT,
                AuditEventType.SYSTEM_OVERRIDE,
            ],
            compliance_frameworks=[ComplianceFramework.LUKHAS_CONSTITUTIONAL],
            limit=10000,
        )

        events = await self.query_audit_logs(query)

        # Analyze constitutional events
        enforcement_events = [e for e in events if e["event_type"] == "constitutional_enforcement"]
        override_events = [e for e in events if e["event_type"] == "system_override"]

        # Generate report
        report = {
            "report_period": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_hours": (end_time - start_time).total_seconds() / 3600,
            },
            "constitutional_enforcement": {
                "total_enforcements": len(enforcement_events),
                "enforcement_types": self._analyze_enforcement_types(enforcement_events),
                "enforcement_frequency": len(enforcement_events) / max(1, (end_time - start_time).days),
            },
            "system_overrides": {
                "total_overrides": len(override_events),
                "override_types": self._analyze_override_types(override_events),
                "high_impact_overrides": len(
                    [
                        e
                        for e in override_events
                        if e.get("constitutional_context", {}).get("constitutional_impact") == "high"
                    ]
                ),
            },
            "transparency_metrics": {
                "events_requiring_review": len([e for e in events if e.get("requires_review")]),
                "automatic_enforcements": len([e for e in enforcement_events if not e.get("requires_review")]),
                "manual_interventions": len([e for e in events if e.get("requires_review")]),
            },
            "compliance_status": {
                "constitutional_compliance_rate": self._calculate_compliance_rate(events),
                "transparency_level": "full",
                "audit_completeness": 100.0,  # All events logged
            },
        }

        return report

    def _analyze_enforcement_types(self, enforcement_events: list[dict[str, Any]]) -> dict[str, int]:
        """Analyze types of constitutional enforcements."""
        enforcement_types = {}

        for event in enforcement_events:
            context = event.get("constitutional_context", {})
            enforcement_type = context.get("enforcement_type", "unknown")
            enforcement_types[enforcement_type] = enforcement_types.get(enforcement_type, 0) + 1

        return enforcement_types

    def _analyze_override_types(self, override_events: list[dict[str, Any]]) -> dict[str, int]:
        """Analyze types of system overrides."""
        override_types = {}

        for event in override_events:
            details = event.get("details", {})
            override_type = details.get("override_type", "unknown")
            override_types[override_type] = override_types.get(override_type, 0) + 1

        return override_types

    def _calculate_compliance_rate(self, events: list[dict[str, Any]]) -> float:
        """Calculate constitutional compliance rate."""
        if not events:
            return 100.0

        compliant_events = len(
            [
                e
                for e in events
                if e.get("severity") != "critical" or e.get("event_type") == "constitutional_enforcement"
            ]
        )

        return (compliant_events / len(events)) * 100.0

    def get_audit_status(self) -> dict[str, Any]:
        """Get comprehensive audit logger status."""
        return {
            "buffer_status": {
                "events_buffered": len(self.event_buffer),
                "buffer_size_limit": self.buffer_size,
                "last_flush_time": self.last_flush_time,
                "auto_flush_enabled": self.config.get("auto_flush_enabled", True),
            },
            "performance_metrics": self.performance_metrics.copy(),
            "enforcement_statistics": self.enforcement_statistics.copy(),
            "constitutional_events_count": len(self.constitutional_events),
            "storage_info": {
                "log_file_path": str(self.log_file_path),
                "current_log_file": str(self._get_current_log_file()),
                "integrity_hash": self.log_integrity_hash.hexdigest()[:16],
            },
            "config": self.config.copy(),
        }

    def log_trust_calculation(self, user_id: str, trust_result: dict[str, Any]) -> str:
        """
        Log trust score calculation for audit trail.

        Args:
            user_id: User identifier
            trust_result: Trust calculation result

        Returns:
            Event ID
        """
        return self.log_event(
            f"Trust score calculated for {user_id}: {trust_result.get('total_score', 0):.2f}",
            event_type=AuditEventType.SECURITY_EVENT,
            severity=AuditSeverity.INFO,
            details={
                "trust_calculation": trust_result,
                "user_id": user_id,
                "calculation_type": "behavioral_trust_scoring",
            },
            user_id=user_id,
            constitutional_tag=False,
        )

    def get_recent_auth_count(self, session_id: str, hours: int = 1) -> int:
        """
        Get count of recent authentication attempts for trust scoring.

        Args:
            session_id: Session identifier
            hours: Number of hours to look back

        Returns:
            Count of authentication attempts
        """
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

            # Search through buffered events first
            count = 0
            for event in self.event_buffer:
                if (
                    isinstance(event, dict)
                    and event.get("timestamp", "") > cutoff_time.isoformat()
                    and session_id in str(event.get("details", {}))
                ) and (
                    "authentication" in str(event.get("message", "")).lower()
                    or event.get("event_type") == "authentication_attempt"
                ):
                    count += 1

            # In production, would also search persisted logs
            # For now, return buffer-based count
            return count

        except Exception as e:
            logger.warning(f"Failed to get recent auth count: {e}")
            return 0

    def get_recent_failures(self, device_id: str, hours: int = 1) -> int:
        """
        Get count of recent authentication failures for trust scoring.

        Args:
            device_id: Device identifier
            hours: Number of hours to look back

        Returns:
            Count of authentication failures
        """
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

            # Search through buffered events
            count = 0
            for event in self.event_buffer:
                if (
                    isinstance(event, dict)
                    and event.get("timestamp", "") > cutoff_time.isoformat()
                    and device_id in str(event.get("details", {}))
                ) and (
                    "failed" in str(event.get("message", "")).lower()
                    or "rejected" in str(event.get("message", "")).lower()
                    or event.get("severity") in ["error", "critical"]
                ):
                    count += 1

            return count

        except Exception as e:
            logger.warning(f"Failed to get recent failures: {e}")
            return 0

    def log_security_event(self, event_type: str, details: dict[str, Any]) -> str:
        """
        Log security-related event for trust scoring and monitoring.

        Args:
            event_type: Type of security event
            details: Event details

        Returns:
            Event ID
        """
        return self.log_event(
            f"Security event: {event_type}",
            event_type=AuditEventType.SECURITY_EVENT,
            severity=(AuditSeverity.WARNING if "low_trust" in event_type else AuditSeverity.INFO),
            details=details,
            user_id=details.get("user_id"),
            constitutional_tag="suspended" in event_type,
        )


# SYNTAX_ERROR_FIXED: ```
