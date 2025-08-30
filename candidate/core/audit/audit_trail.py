"""
Enterprise AGI Audit Trail System
Provides comprehensive logging, tracking, and compliance for all AGI operations
"""

import asyncio
import gzip
import hashlib
import json
import sqlite3
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class AuditEventType(Enum):
    """Comprehensive audit event types for AGI operations"""

    # Consciousness events
    CONSCIOUSNESS_STATE_CHANGE = "consciousness.state_change"
    CONSCIOUSNESS_EMERGENCE = "consciousness.emergence"
    CONSCIOUSNESS_COLLAPSE = "consciousness.collapse"
    AWARENESS_SHIFT = "consciousness.awareness_shift"
    COHERENCE_SPIKE = "consciousness.coherence_spike"

    # Learning events
    LEARNING_GOAL_SET = "learning.goal_set"
    LEARNING_GOAL_ACHIEVED = "learning.goal_achieved"
    KNOWLEDGE_ACQUIRED = "learning.knowledge_acquired"
    SKILL_IMPROVED = "learning.skill_improved"
    LEARNING_FAILURE = "learning.failure"
    KNOWLEDGE_SYNTHESIZED = "learning.synthesis"

    # Memory events
    MEMORY_STORED = "memory.stored"
    MEMORY_RECALLED = "memory.recalled"
    MEMORY_CONSOLIDATED = "memory.consolidated"
    MEMORY_FORGOTTEN = "memory.forgotten"
    MEMORY_PATTERN_DETECTED = "memory.pattern"

    # Dream events
    DREAM_INITIATED = "dream.initiated"
    DREAM_COMPLETED = "dream.completed"
    DREAM_PATTERN_FOUND = "dream.pattern"
    DREAM_CONSOLIDATED = "dream.consolidated"

    # Decision events
    DECISION_INITIATED = "decision.initiated"
    DECISION_EVALUATED = "decision.evaluated"
    DECISION_MADE = "decision.made"
    ACTION_TAKEN = "decision.action_taken"
    GOAL_EVALUATED = "decision.goal_evaluated"
    DECISION_REVERSED = "decision.reversed"

    # Self-improvement events
    IMPROVEMENT_GOAL_SET = "improvement.goal_set"
    IMPROVEMENT_ACHIEVED = "improvement.achieved"
    PERFORMANCE_MEASURED = "improvement.performance"
    ALGORITHM_MODIFIED = "improvement.algorithm_modified"
    PARAMETER_TUNED = "improvement.parameter_tuned"

    # Security events
    SECURITY_VIOLATION = "security.violation"
    ACCESS_GRANTED = "security.access_granted"
    ACCESS_DENIED = "security.access_denied"
    THREAT_DETECTED = "security.threat_detected"
    ANOMALY_DETECTED = "security.anomaly"
    ENCRYPTION_APPLIED = "security.encryption"

    # System events
    SYSTEM_START = "system.start"
    SYSTEM_STOP = "system.stop"
    SYSTEM_ERROR = "system.error"
    SYSTEM_RECOVERY = "system.recovery"
    CONFIG_CHANGE = "system.config_change"
    COMPONENT_FAILURE = "system.component_failure"
    SELF_MODIFICATION = "system.self_modification"

    # Integration events
    API_CALL = "integration.api_call"
    EXTERNAL_DATA_RECEIVED = "integration.data_received"
    WEBSOCKET_CONNECTION = "integration.websocket"

    # Compliance events
    COMPLIANCE_CHECK = "compliance.check"
    COMPLIANCE_VIOLATION = "compliance.violation"
    AUDIT_REQUESTED = "compliance.audit_requested"


class AuditSeverity(Enum):
    """Audit event severity levels"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"


@dataclass
class AuditEvent:
    """Structured audit event"""

    id: str
    timestamp: datetime
    session_id: str
    event_type: AuditEventType
    actor: str
    severity: AuditSeverity
    details: dict[str, Any]
    context: dict[str, Any] = field(default_factory=dict)
    tags: set[str] = field(default_factory=set)
    parent_id: Optional[str] = None
    checksum: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "session_id": self.session_id,
            "event_type": self.event_type.value,
            "actor": self.actor,
            "severity": self.severity.value,
            "details": self.details,
            "context": self.context,
            "tags": list(self.tags),
            "parent_id": self.parent_id,
            "checksum": self.checksum,
        }


@dataclass
class AuditQuery:
    """Query parameters for audit trail search"""

    event_types: Optional[list[AuditEventType]] = None
    actors: Optional[list[str]] = None
    severities: Optional[list[AuditSeverity]] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    tags: Optional[set[str]] = None
    parent_id: Optional[str] = None
    limit: int = 1000
    offset: int = 0


@dataclass
class ComplianceReport:
    """Compliance report structure"""

    report_id: str
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    report_type: str
    summary: dict[str, Any]
    violations: list[dict[str, Any]]
    recommendations: list[str]
    metrics: dict[str, float]


class AuditTrail:
    """
    Enterprise-grade audit trail system for AGI operations
    """

    def __init__(
        self,
        storage_path: str = "./audit_logs",
        retention_days: int = 90,
        enable_encryption: bool = True,
    ):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.retention_days = retention_days
        self.enable_encryption = enable_encryption

        # Session management
        self.session_id = str(uuid.uuid4())
        self.session_start = datetime.now()

        # Event tracking
        self.event_count = 0
        self.event_buffer = []
        self.buffer_lock = asyncio.Lock()

        # Database setup
        self.db_path = self.storage_path / "audit_trail.db"
        self._init_database()

        # Real-time analytics
        self.event_counters = defaultdict(int)
        self.severity_counters = defaultdict(int)
        self.actor_activity = defaultdict(int)

        # Decision tracking
        self.active_decisions = {}
        self.decision_chains = defaultdict(list)

    def _init_database(self):
        """Initialize SQLite database for audit storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS audit_events (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            session_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            actor TEXT NOT NULL,
            severity TEXT NOT NULL,
            details TEXT NOT NULL,
            context TEXT,
            tags TEXT,
            parent_id TEXT,
            checksum TEXT NOT NULL,
            FOREIGN KEY (parent_id) REFERENCES audit_events(id)
        )
        """
        )

        cursor.execute(
            """
        CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_events(timestamp)
        """
        )

        cursor.execute(
            """
        CREATE INDEX IF NOT EXISTS idx_event_type ON audit_events(event_type)
        """
        )

        cursor.execute(
            """
        CREATE INDEX IF NOT EXISTS idx_actor ON audit_events(actor)
        """
        )

        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS compliance_reports (
            report_id TEXT PRIMARY KEY,
            generated_at TEXT NOT NULL,
            period_start TEXT NOT NULL,
            period_end TEXT NOT NULL,
            report_type TEXT NOT NULL,
            report_data TEXT NOT NULL
        )
        """
        )

        conn.commit()
        conn.close()

    async def log_event(
        self,
        event_type: AuditEventType,
        actor: str,
        details: dict[str, Any],
        severity: AuditSeverity = AuditSeverity.INFO,
        context: Optional[dict[str, Any]] = None,
        tags: Optional[set[str]] = None,
        parent_id: Optional[str] = None,
    ) -> str:
        """Log an audit event"""
        event_id = self._generate_event_id()

        event = AuditEvent(
            id=event_id,
            timestamp=datetime.now(),
            session_id=self.session_id,
            event_type=event_type,
            actor=actor,
            severity=severity,
            details=details,
            context=context or {},
            tags=tags or set(),
            parent_id=parent_id,
        )

        # Calculate checksum
        event.checksum = self._calculate_checksum(event)

        # Update counters
        self.event_counters[event_type] += 1
        self.severity_counters[severity] += 1
        self.actor_activity[actor] += 1

        # Add to buffer
        async with self.buffer_lock:
            self.event_buffer.append(event)
            self.event_count += 1

            # Flush if buffer is large
            if len(self.event_buffer) >= 100:
                await self._flush_buffer()

        # Handle critical events immediately
        if severity in [AuditSeverity.CRITICAL, AuditSeverity.EMERGENCY]:
            await self._handle_critical_event(event)

        return event_id

    async def log_decision_chain(
        self,
        decision_id: str,
        decision_type: str,
        steps: list[dict[str, Any]],
        outcome: dict[str, Any],
        rationale: str,
        confidence: float,
        alternatives_considered: list[dict[str, Any]] = None,
    ) -> str:
        """Log a complete decision chain for explainability"""
        # Log decision initiation
        parent_id = await self.log_event(
            AuditEventType.DECISION_INITIATED,
            "decision_engine",
            {
                "decision_id": decision_id,
                "decision_type": decision_type,
                "rationale": rationale,
                "alternatives_count": (
                    len(alternatives_considered) if alternatives_considered else 0
                ),
            },
        )

        # Log each decision step
        for i, step in enumerate(steps):
            await self.log_event(
                AuditEventType.DECISION_EVALUATED,
                "decision_engine",
                {
                    "decision_id": decision_id,
                    "step_number": i + 1,
                    "step_description": step.get("description"),
                    "step_result": step.get("result"),
                    "step_confidence": step.get("confidence", 0),
                },
                parent_id=parent_id,
            )

        # Log final decision
        await self.log_event(
            AuditEventType.DECISION_MADE,
            "decision_engine",
            {
                "decision_id": decision_id,
                "outcome": outcome,
                "confidence": confidence,
                "total_steps": len(steps),
                "alternatives_considered": alternatives_considered,
            },
            parent_id=parent_id,
        )

        # Store decision chain
        self.decision_chains[decision_id] = {
            "parent_id": parent_id,
            "steps": steps,
            "outcome": outcome,
            "rationale": rationale,
            "confidence": confidence,
        }

        return parent_id

    async def log_consciousness_transition(
        self,
        from_state: dict[str, Any],
        to_state: dict[str, Any],
        trigger: str,
        metrics: dict[str, float],
        emergence_detected: bool = False,
    ):
        """Log consciousness state transitions"""
        coherence_delta = to_state.get("coherence", 0) - from_state.get("coherence", 0)
        complexity_delta = to_state.get("complexity", 0) - from_state.get("complexity", 0)

        event_type = (
            AuditEventType.CONSCIOUSNESS_EMERGENCE
            if emergence_detected
            else AuditEventType.CONSCIOUSNESS_STATE_CHANGE
        )

        await self.log_event(
            event_type,
            "consciousness_engine",
            {
                "from_state": {
                    "coherence": from_state.get("coherence"),
                    "complexity": from_state.get("complexity"),
                    "awareness_level": from_state.get("awareness_level"),
                },
                "to_state": {
                    "coherence": to_state.get("coherence"),
                    "complexity": to_state.get("complexity"),
                    "awareness_level": to_state.get("awareness_level"),
                },
                "trigger": trigger,
                "coherence_delta": coherence_delta,
                "complexity_delta": complexity_delta,
                "metrics": metrics,
                "emergence_detected": emergence_detected,
            },
            severity=(AuditSeverity.WARNING if emergence_detected else AuditSeverity.INFO),
            tags=(
                {"consciousness", "state_change", "emergence"}
                if emergence_detected
                else {"consciousness", "state_change"}
            ),
        )

    async def log_learning_progress(
        self,
        learning_id: str,
        topic: str,
        progress: float,
        knowledge_gained: dict[str, Any],
        performance_metrics: dict[str, float],
    ):
        """Log learning progress and knowledge acquisition"""
        await self.log_event(
            AuditEventType.KNOWLEDGE_ACQUIRED,
            "learning_engine",
            {
                "learning_id": learning_id,
                "topic": topic,
                "progress": progress,
                "knowledge_type": knowledge_gained.get("type"),
                "knowledge_complexity": knowledge_gained.get("complexity"),
                "integration_success": knowledge_gained.get("integrated", False),
                "performance_metrics": performance_metrics,
            },
            tags={"learning", "knowledge", topic},
        )

    async def log_security_event(
        self,
        threat_type: str,
        threat_level: str,
        source: str,
        action_taken: str,
        blocked: bool,
    ):
        """Log security events"""
        severity = (
            AuditSeverity.CRITICAL
            if threat_level == "HIGH"
            else (AuditSeverity.WARNING if threat_level == "MEDIUM" else AuditSeverity.INFO)
        )

        await self.log_event(
            (AuditEventType.THREAT_DETECTED if blocked else AuditEventType.SECURITY_VIOLATION),
            "security_system",
            {
                "threat_type": threat_type,
                "threat_level": threat_level,
                "source": source,
                "action_taken": action_taken,
                "blocked": blocked,
                "timestamp": datetime.now().isoformat(),
            },
            severity=severity,
            tags={"security", "threat", threat_type},
        )

    async def query_events(self, query: AuditQuery) -> list[AuditEvent]:
        """Query audit events with filters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Build query
        conditions = []
        params = []

        if query.event_types:
            placeholders = ",".join(["?" for _ in query.event_types])
            conditions.append(f"event_type IN ({placeholders})")
            params.extend([et.value for et in query.event_types])

        if query.actors:
            placeholders = ",".join(["?" for _ in query.actors])
            conditions.append(f"actor IN ({placeholders})")
            params.extend(query.actors)

        if query.severities:
            placeholders = ",".join(["?" for _ in query.severities])
            conditions.append(f"severity IN ({placeholders})")
            params.extend([s.value for s in query.severities])

        if query.start_time:
            conditions.append("timestamp >= ?")
            params.append(query.start_time.isoformat())

        if query.end_time:
            conditions.append("timestamp <= ?")
            params.append(query.end_time.isoformat())

        if query.parent_id:
            conditions.append("parent_id = ?")
            params.append(query.parent_id)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        sql = f"""
        SELECT * FROM audit_events
        WHERE {where_clause}
        ORDER BY timestamp DESC
        LIMIT ? OFFSET ?
        """

        params.extend([query.limit, query.offset])

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()

        # Convert to AuditEvent objects
        events = []
        for row in rows:
            event_dict = {
                "id": row[0],
                "timestamp": datetime.fromisoformat(row[1]),
                "session_id": row[2],
                "event_type": AuditEventType(row[3]),
                "actor": row[4],
                "severity": AuditSeverity(row[5]),
                "details": json.loads(row[6]),
                "context": json.loads(row[7]) if row[7] else {},
                "tags": set(json.loads(row[8])) if row[8] else set(),
                "parent_id": row[9],
                "checksum": row[10],
            }
            events.append(AuditEvent(**event_dict))

        return events

    async def generate_compliance_report(
        self, report_type: str, start_date: datetime, end_date: datetime
    ) -> ComplianceReport:
        """Generate compliance reports"""
        report_id = str(uuid.uuid4())

        # Query relevant events
        query = AuditQuery(start_time=start_date, end_time=end_date, limit=10000)
        events = await self.query_events(query)

        # Analyze events based on report type
        if report_type == "security_compliance":
            report = await self._generate_security_compliance_report(events, start_date, end_date)
        elif report_type == "decision_transparency":
            report = await self._generate_decision_transparency_report(events, start_date, end_date)
        elif report_type == "learning_ethics":
            report = await self._generate_learning_ethics_report(events, start_date, end_date)
        else:
            report = await self._generate_general_compliance_report(events, start_date, end_date)

        report.report_id = report_id

        # Store report
        await self._store_compliance_report(report)

        return report

    async def _generate_security_compliance_report(
        self,
        events: list[AuditEvent],
        start_date: datetime,
        end_date: datetime,
    ) -> ComplianceReport:
        """Generate security compliance report"""
        security_events = [e for e in events if "security" in e.tags]

        violations = []
        threat_count = 0
        blocked_count = 0

        for event in security_events:
            if event.event_type == AuditEventType.SECURITY_VIOLATION:
                violations.append(
                    {
                        "timestamp": event.timestamp.isoformat(),
                        "violation_type": event.details.get("threat_type"),
                        "severity": event.severity.value,
                        "resolved": event.details.get("blocked", False),
                    }
                )
            elif event.event_type == AuditEventType.THREAT_DETECTED:
                threat_count += 1
                if event.details.get("blocked"):
                    blocked_count += 1

        summary = {
            "total_security_events": len(security_events),
            "violations_count": len(violations),
            "threats_detected": threat_count,
            "threats_blocked": blocked_count,
            "block_rate": (blocked_count / threat_count if threat_count > 0 else 1.0),
        }

        recommendations = []
        if len(violations) > 10:
            recommendations.append(
                "High number of security violations detected. Review security policies."
            )
        if summary["block_rate"] < 0.95:
            recommendations.append("Threat blocking rate below 95%. Enhance security measures.")

        return ComplianceReport(
            report_id="",
            generated_at=datetime.now(),
            period_start=start_date,
            period_end=end_date,
            report_type="security_compliance",
            summary=summary,
            violations=violations,
            recommendations=recommendations,
            metrics={"security_score": min(summary["block_rate"], 1.0 - (len(violations) / 100))},
        )

    async def _flush_buffer(self):
        """Flush event buffer to database"""
        if not self.event_buffer:
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for event in self.event_buffer:
            cursor.execute(
                """
            INSERT INTO audit_events
            (id, timestamp, session_id, event_type, actor, severity, details, context,
    tags, parent_id, checksum)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    event.id,
                    event.timestamp.isoformat(),
                    event.session_id,
                    event.event_type.value,
                    event.actor,
                    event.severity.value,
                    json.dumps(event.details),
                    json.dumps(event.context),
                    json.dumps(list(event.tags)),
                    event.parent_id,
                    event.checksum,
                ),
            )

        conn.commit()
        conn.close()

        # Archive old events if needed
        await self._archive_old_events()

        self.event_buffer.clear()

    async def _archive_old_events(self):
        """Archive events older than retention period"""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get old events
        cursor.execute(
            """
        SELECT * FROM audit_events
        WHERE timestamp < ?
        """,
            (cutoff_date.isoformat(),),
        )

        old_events = cursor.fetchall()

        if old_events:
            # Archive to compressed file
            archive_file = self.storage_path / f"archive_{cutoff_date.strftime('%Y%m%d')}.jsonl.gz"
            with gzip.open(archive_file, "at") as f:
                for event in old_events:
                    f.write(
                        json.dumps(
                            {
                                "id": event[0],
                                "timestamp": event[1],
                                "session_id": event[2],
                                "event_type": event[3],
                                "actor": event[4],
                                "severity": event[5],
                                "details": json.loads(event[6]),
                                "context": (json.loads(event[7]) if event[7] else {}),
                                "tags": (json.loads(event[8]) if event[8] else []),
                                "parent_id": event[9],
                                "checksum": event[10],
                            }
                        )
                        + "\n"
                    )

            # Delete from database
            cursor.execute(
                """
            DELETE FROM audit_events
            WHERE timestamp < ?
            """,
                (cutoff_date.isoformat(),),
            )

            conn.commit()

        conn.close()

    async def _handle_critical_event(self, event: AuditEvent):
        """Handle critical events immediately"""
        # In production, this would trigger alerts

    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        return f"{self.session_id}-{self.event_count:08d}-{uuid.uuid4().hex[:8]}"

    def _calculate_checksum(self, event: AuditEvent) -> str:
        """Calculate checksum for event integrity"""
        event_dict = event.to_dict()
        event_dict.pop("checksum", None)
        event_str = json.dumps(event_dict, sort_keys=True)
        return hashlib.sha256(event_str.encode()).hexdigest()

    async def _store_compliance_report(self, report: ComplianceReport):
        """Store compliance report in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
        INSERT INTO compliance_reports
        (report_id, generated_at, period_start, period_end, report_type, report_data)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                report.report_id,
                report.generated_at.isoformat(),
                report.period_start.isoformat(),
                report.period_end.isoformat(),
                report.report_type,
                json.dumps(
                    {
                        "summary": report.summary,
                        "violations": report.violations,
                        "recommendations": report.recommendations,
                        "metrics": report.metrics,
                    }
                ),
            ),
        )

        conn.commit()
        conn.close()

    async def get_analytics_summary(self) -> dict[str, Any]:
        """Get real-time analytics summary"""
        return {
            "session_id": self.session_id,
            "session_duration": (datetime.now() - self.session_start).total_seconds(),
            "total_events": self.event_count,
            "event_types": dict(self.event_counters),
            "severity_distribution": dict(self.severity_counters),
            "most_active_actors": sorted(
                self.actor_activity.items(), key=lambda x: x[1], reverse=True
            )[:10],
            "active_decisions": len(self.active_decisions),
            "buffer_size": len(self.event_buffer),
        }


# Global audit trail instance
_audit_trail: Optional[AuditTrail] = None


def get_audit_trail() -> AuditTrail:
    """Get or create global audit trail instance"""
    global _audit_trail
    if _audit_trail is None:
        _audit_trail = AuditTrail()
    return _audit_trail
