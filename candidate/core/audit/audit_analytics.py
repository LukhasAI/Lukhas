"""
Audit analytics and anomaly detection for AGI operations
Provides real-time analysis of audit trails for compliance and security
"""

import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from .audit_trail import (
    AuditEvent,
    AuditEventType,
    AuditQuery,
    AuditSeverity,
    AuditTrail,
)


class AnomalyType(Enum):
    """Types of anomalies that can be detected"""

    UNUSUAL_ACTIVITY_PATTERN = "unusual_activity_pattern"
    EXCESSIVE_ERROR_RATE = "excessive_error_rate"
    UNAUTHORIZED_ACCESS_ATTEMPT = "unauthorized_access_attempt"
    ABNORMAL_DECISION_PATTERN = "abnormal_decision_pattern"
    CONSCIOUSNESS_INSTABILITY = "consciousness_instability"
    LEARNING_REGRESSION = "learning_regression"
    SECURITY_BREACH_ATTEMPT = "security_breach_attempt"
    RESOURCE_ABUSE = "resource_abuse"
    TEMPORAL_ANOMALY = "temporal_anomaly"


@dataclass
class Anomaly:
    """Detected anomaly structure"""

    anomaly_type: AnomalyType
    severity: str
    description: str
    detected_at: datetime
    events: list[str]  # Event IDs
    confidence: float
    recommended_action: str


@dataclass
class ComplianceViolation:
    """Compliance violation structure"""

    violation_type: str
    regulation: str
    description: str
    events: list[str]
    severity: str
    remediation_required: bool


class AuditAnalytics:
    """
    Real-time analytics engine for audit trails
    """

    def __init__(self, audit_trail: AuditTrail):
        self.audit_trail = audit_trail

        # Historical baselines
        self.event_rate_baseline = defaultdict(lambda: {"mean": 0, "std": 1})
        self.actor_behavior_profiles = defaultdict(dict)
        self.decision_patterns = defaultdict(list)

        # Anomaly detection thresholds
        self.error_rate_threshold = 0.1
        self.consciousness_stability_threshold = 0.3
        self.decision_consistency_threshold = 0.8

        # Compliance rules
        self.compliance_rules = self._load_compliance_rules()

    def _load_compliance_rules(self) -> dict[str, Any]:
        """Load compliance rules for various regulations"""
        return {
            "gdpr": {
                "data_retention_days": 90,
                "requires_consent_tracking": True,
                "requires_data_minimization": True,
            },
            "sox": {
                "requires_decision_auditing": True,
                "requires_change_control": True,
                "requires_access_controls": True,
            },
            "hipaa": {
                "requires_encryption": True,
                "requires_access_logging": True,
                "max_failed_login_attempts": 5,
            },
            "ai_ethics": {
                "requires_explainability": True,
                "requires_bias_monitoring": True,
                "requires_human_oversight": True,
            },
        }

    async def analyze_time_period(self, start_time: datetime, end_time: datetime) -> dict[str, Any]:
        """Analyze audit events for a specific time period"""
        # Query events
        query = AuditQuery(start_time=start_time, end_time=end_time, limit=10000)
        events = await self.audit_trail.query_events(query)

        # Perform various analyses
        anomalies = await self.detect_anomalies(events)
        patterns = self.analyze_patterns(events)
        compliance = await self.check_compliance(events)
        metrics = self.calculate_metrics(events)

        return {
            "period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "duration_hours": (end_time - start_time).total_seconds() / 3600,
            },
            "summary": {
                "total_events": len(events),
                "unique_actors": len({e.actor for e in events}),
                "error_rate": metrics["error_rate"],
                "critical_events": metrics["critical_events"],
            },
            "anomalies": anomalies,
            "patterns": patterns,
            "compliance": compliance,
            "metrics": metrics,
        }

    async def detect_anomalies(self, events: list[AuditEvent]) -> list[Anomaly]:
        """Detect anomalies in audit events"""
        anomalies = []

        # Check for unusual activity patterns
        activity_anomalies = self._detect_activity_anomalies(events)
        anomalies.extend(activity_anomalies)

        # Check for excessive errors
        error_anomalies = self._detect_error_anomalies(events)
        anomalies.extend(error_anomalies)

        # Check for consciousness instability
        consciousness_anomalies = self._detect_consciousness_anomalies(events)
        anomalies.extend(consciousness_anomalies)

        # Check for abnormal decision patterns
        decision_anomalies = self._detect_decision_anomalies(events)
        anomalies.extend(decision_anomalies)

        # Check for security anomalies
        security_anomalies = self._detect_security_anomalies(events)
        anomalies.extend(security_anomalies)

        return anomalies

    def _detect_activity_anomalies(self, events: list[AuditEvent]) -> list[Anomaly]:
        """Detect unusual activity patterns"""
        anomalies = []

        # Group events by hour
        hourly_events = defaultdict(list)
        for event in events:
            hour_key = event.timestamp.strftime("%Y-%m-%d %H:00")
            hourly_events[hour_key].append(event)

        # Check for unusual spikes
        event_counts = [len(events) for events in hourly_events.values()]
        if event_counts:
            mean = statistics.mean(event_counts)
            std = statistics.stdev(event_counts) if len(event_counts) > 1 else 0

            for hour, hour_events in hourly_events.items():
                if std > 0 and len(hour_events) > mean + 3 * std:
                    anomalies.append(
                        Anomaly(
                            anomaly_type=AnomalyType.UNUSUAL_ACTIVITY_PATTERN,
                            severity="MEDIUM",
                            description=f"Unusual spike in activity: {len(hour_events)} events in hour {hour}",
                            detected_at=datetime.now(),
                            events=[e.id for e in hour_events[:10]],  # Sample
                            confidence=0.8,
                            recommended_action="Investigate cause of activity spike",
                        )
                    )

        return anomalies

    def _detect_error_anomalies(self, events: list[AuditEvent]) -> list[Anomaly]:
        """Detect excessive error rates"""
        anomalies = []

        # Calculate error rates by component
        component_events = defaultdict(list)
        for event in events:
            component_events[event.actor].append(event)

        for component, comp_events in component_events.items():
            error_count = sum(1 for e in comp_events if e.severity in [AuditSeverity.ERROR, AuditSeverity.CRITICAL])
            error_rate = error_count / len(comp_events) if comp_events else 0

            if error_rate > self.error_rate_threshold:
                anomalies.append(
                    Anomaly(
                        anomaly_type=AnomalyType.EXCESSIVE_ERROR_RATE,
                        severity="HIGH",
                        description=f"Component {component} has {error_rate:.1%} error rate",
                        detected_at=datetime.now(),
                        events=[
                            e.id for e in comp_events if e.severity in [AuditSeverity.ERROR, AuditSeverity.CRITICAL]
                        ][:10],
                        confidence=0.9,
                        recommended_action=f"Review and fix errors in {component}",
                    )
                )

        return anomalies

    def _detect_consciousness_anomalies(self, events: list[AuditEvent]) -> list[Anomaly]:
        """Detect consciousness instability"""
        anomalies = []

        # Get consciousness events
        consciousness_events = [
            e
            for e in events
            if e.event_type
            in [
                AuditEventType.CONSCIOUSNESS_STATE_CHANGE,
                AuditEventType.CONSCIOUSNESS_EMERGENCE,
                AuditEventType.CONSCIOUSNESS_COLLAPSE,
            ]
        ]

        if len(consciousness_events) > 10:
            # Check for rapid state changes
            for i in range(1, len(consciousness_events)):
                time_diff = (consciousness_events[i].timestamp - consciousness_events[i - 1].timestamp).total_seconds()

                if time_diff < 60:  # Less than 1 minute between changes
                    anomalies.append(
                        Anomaly(
                            anomaly_type=AnomalyType.CONSCIOUSNESS_INSTABILITY,
                            severity="HIGH",
                            description="Rapid consciousness state changes detected",
                            detected_at=datetime.now(),
                            events=[
                                consciousness_events[i - 1].id,
                                consciousness_events[i].id,
                            ],
                            confidence=0.85,
                            recommended_action="Stabilize consciousness parameters",
                        )
                    )

            # Check for coherence drops
            coherence_values = []
            for event in consciousness_events:
                if "to_state" in event.details:
                    coherence = event.details["to_state"].get("coherence", 0)
                    coherence_values.append(coherence)

            if coherence_values and min(coherence_values) < self.consciousness_stability_threshold:
                anomalies.append(
                    Anomaly(
                        anomaly_type=AnomalyType.CONSCIOUSNESS_INSTABILITY,
                        severity="CRITICAL",
                        description=f"Consciousness coherence dropped below {self.consciousness_stability_threshold}",
                        detected_at=datetime.now(),
                        events=[
                            e.id
                            for e in consciousness_events
                            if e.details.get("to_state", {}).get("coherence", 1)
                            < self.consciousness_stability_threshold
                        ],
                        confidence=0.95,
                        recommended_action="Emergency consciousness stabilization required",
                    )
                )

        return anomalies

    def _detect_decision_anomalies(self, events: list[AuditEvent]) -> list[Anomaly]:
        """Detect abnormal decision patterns"""
        anomalies = []

        # Get decision events
        decision_events = [
            e for e in events if e.event_type in [AuditEventType.DECISION_MADE, AuditEventType.DECISION_REVERSED]
        ]

        # Check for decision reversals
        reversal_count = sum(1 for e in decision_events if e.event_type == AuditEventType.DECISION_REVERSED)
        if decision_events and reversal_count / len(decision_events) > 0.1:
            anomalies.append(
                Anomaly(
                    anomaly_type=AnomalyType.ABNORMAL_DECISION_PATTERN,
                    severity="MEDIUM",
                    description=f"High decision reversal rate: {reversal_count} reversals out of {len(decision_events)} decisions",
                    detected_at=datetime.now(),
                    events=[e.id for e in decision_events if e.event_type == AuditEventType.DECISION_REVERSED],
                    confidence=0.75,
                    recommended_action="Review decision-making logic",
                )
            )

        # Check for low confidence decisions
        low_confidence_decisions = []
        for event in decision_events:
            if "confidence" in event.details and event.details["confidence"] < 0.5:
                low_confidence_decisions.append(event)

        if len(low_confidence_decisions) > 5:
            anomalies.append(
                Anomaly(
                    anomaly_type=AnomalyType.ABNORMAL_DECISION_PATTERN,
                    severity="MEDIUM",
                    description=f"{len(low_confidence_decisions)} decisions made with confidence < 50%",
                    detected_at=datetime.now(),
                    events=[e.id for e in low_confidence_decisions[:10]],
                    confidence=0.8,
                    recommended_action="Improve decision confidence mechanisms",
                )
            )

        return anomalies

    def _detect_security_anomalies(self, events: list[AuditEvent]) -> list[Anomaly]:
        """Detect security anomalies"""
        anomalies = []

        # Check for repeated access denials
        access_denials = defaultdict(list)
        for event in events:
            if event.event_type == AuditEventType.ACCESS_DENIED:
                user = event.details.get("user", "unknown")
                access_denials[user].append(event)

        for user, denials in access_denials.items():
            if len(denials) > 5:
                anomalies.append(
                    Anomaly(
                        anomaly_type=AnomalyType.UNAUTHORIZED_ACCESS_ATTEMPT,
                        severity="HIGH",
                        description=f"Multiple access denials for user {user}: {len(denials)} attempts",
                        detected_at=datetime.now(),
                        events=[e.id for e in denials[:10]],
                        confidence=0.9,
                        recommended_action=f"Investigate potential unauthorized access by {user}",
                    )
                )

        # Check for security violations
        security_violations = [e for e in events if e.event_type == AuditEventType.SECURITY_VIOLATION]
        if security_violations:
            anomalies.append(
                Anomaly(
                    anomaly_type=AnomalyType.SECURITY_BREACH_ATTEMPT,
                    severity="CRITICAL",
                    description=f"{len(security_violations)} security violations detected",
                    detected_at=datetime.now(),
                    events=[e.id for e in security_violations[:10]],
                    confidence=0.95,
                    recommended_action="Immediate security review required",
                )
            )

        return anomalies

    def analyze_patterns(self, events: list[AuditEvent]) -> dict[str, Any]:
        """Analyze patterns in audit events"""
        patterns = {
            "temporal_patterns": self._analyze_temporal_patterns(events),
            "actor_patterns": self._analyze_actor_patterns(events),
            "event_sequences": self._analyze_event_sequences(events),
            "error_patterns": self._analyze_error_patterns(events),
        }

        return patterns

    def _analyze_temporal_patterns(self, events: list[AuditEvent]) -> dict[str, Any]:
        """Analyze temporal patterns"""
        if not events:
            return {}

        # Group by hour of day
        hourly_distribution = defaultdict(int)
        daily_distribution = defaultdict(int)

        for event in events:
            hour = event.timestamp.hour
            day = event.timestamp.strftime("%Y-%m-%d")
            hourly_distribution[hour] += 1
            daily_distribution[day] += 1

        # Find peak hours
        peak_hours = sorted(hourly_distribution.items(), key=lambda x: x[1], reverse=True)[:3]

        # Calculate daily average
        daily_avg = statistics.mean(daily_distribution.values()) if daily_distribution else 0

        return {
            "peak_hours": peak_hours,
            "daily_average": daily_avg,
            "busiest_day": (max(daily_distribution.items(), key=lambda x: x[1]) if daily_distribution else None),
            "total_days": len(daily_distribution),
        }

    def _analyze_actor_patterns(self, events: list[AuditEvent]) -> dict[str, Any]:
        """Analyze actor behavior patterns"""
        actor_stats = defaultdict(
            lambda: {
                "event_count": 0,
                "error_count": 0,
                "event_types": Counter(),
                "severity_distribution": Counter(),
            }
        )

        for event in events:
            stats = actor_stats[event.actor]
            stats["event_count"] += 1
            stats["event_types"][event.event_type.value] += 1
            stats["severity_distribution"][event.severity.value] += 1
            if event.severity in [AuditSeverity.ERROR, AuditSeverity.CRITICAL]:
                stats["error_count"] += 1

        # Calculate error rates
        for stats in actor_stats.values():
            stats["error_rate"] = stats["error_count"] / stats["event_count"] if stats["event_count"] > 0 else 0

        # Find most active actors
        most_active = sorted(
            actor_stats.items(),
            key=lambda x: x[1]["event_count"],
            reverse=True,
        )[:5]

        return {
            "most_active_actors": most_active,
            "total_actors": len(actor_stats),
            "actor_stats": dict(actor_stats),
        }

    def _analyze_event_sequences(self, events: list[AuditEvent]) -> dict[str, Any]:
        """Analyze common event sequences"""
        sequences = defaultdict(int)

        # Look for 2-event and 3-event sequences
        for i in range(len(events) - 2):
            # 2-event sequence
            seq2 = (events[i].event_type.value, events[i + 1].event_type.value)
            sequences[seq2] += 1

            # 3-event sequence
            seq3 = (
                events[i].event_type.value,
                events[i + 1].event_type.value,
                events[i + 2].event_type.value,
            )
            sequences[seq3] += 1

        # Find most common sequences
        common_sequences = sorted(sequences.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            "common_sequences": common_sequences,
            "unique_sequences": len(sequences),
        }

    def _analyze_error_patterns(self, events: list[AuditEvent]) -> dict[str, Any]:
        """Analyze error patterns"""
        errors = [e for e in events if e.severity in [AuditSeverity.ERROR, AuditSeverity.CRITICAL]]

        if not errors:
            return {"error_count": 0}

        # Group errors by type
        error_types = Counter()
        error_components = Counter()

        for error in errors:
            error_types[error.event_type.value] += 1
            error_components[error.actor] += 1

        return {
            "error_count": len(errors),
            "error_rate": len(errors) / len(events) if events else 0,
            "common_error_types": error_types.most_common(5),
            "error_prone_components": error_components.most_common(5),
            "critical_errors": sum(1 for e in errors if e.severity == AuditSeverity.CRITICAL),
        }

    async def check_compliance(self, events: list[AuditEvent]) -> dict[str, list[ComplianceViolation]]:
        """Check for compliance violations"""
        violations = defaultdict(list)

        # Check GDPR compliance
        gdpr_violations = self._check_gdpr_compliance(events)
        if gdpr_violations:
            violations["gdpr"] = gdpr_violations

        # Check AI ethics compliance
        ethics_violations = self._check_ai_ethics_compliance(events)
        if ethics_violations:
            violations["ai_ethics"] = ethics_violations

        # Check security compliance
        security_violations = self._check_security_compliance(events)
        if security_violations:
            violations["security"] = security_violations

        return dict(violations)

    def _check_gdpr_compliance(self, events: list[AuditEvent]) -> list[ComplianceViolation]:
        """Check GDPR compliance"""
        violations = []

        # Check for data retention violations
        # (In real implementation, would check actual data age)

        # Check for missing consent tracking
        # (In real implementation, would verify consent for data operations)

        return violations

    def _check_ai_ethics_compliance(self, events: list[AuditEvent]) -> list[ComplianceViolation]:
        """Check AI ethics compliance"""
        violations = []

        # Check for unexplained decisions
        decision_events = [e for e in events if e.event_type == AuditEventType.DECISION_MADE]
        unexplained = [e for e in decision_events if not e.details.get("rationale")]

        if unexplained:
            violations.append(
                ComplianceViolation(
                    violation_type="missing_explainability",
                    regulation="ai_ethics",
                    description=f"{len(unexplained)} decisions made without explanations",
                    events=[e.id for e in unexplained[:10]],
                    severity="MEDIUM",
                    remediation_required=True,
                )
            )

        return violations

    def _check_security_compliance(self, events: list[AuditEvent]) -> list[ComplianceViolation]:
        """Check security compliance"""
        violations = []

        # Check for unencrypted operations
        # (In real implementation, would verify encryption usage)

        # Check for missing access logs
        # (In real implementation, would verify all access is logged)

        return violations

    def calculate_metrics(self, events: list[AuditEvent]) -> dict[str, Any]:
        """Calculate various metrics from events"""
        if not events:
            return {}

        # Time-based metrics
        time_span = (events[-1].timestamp - events[0].timestamp).total_seconds() / 3600  # hours
        event_rate = len(events) / time_span if time_span > 0 else 0

        # Severity metrics
        severity_counts = Counter(e.severity for e in events)
        error_rate = (severity_counts[AuditSeverity.ERROR] + severity_counts[AuditSeverity.CRITICAL]) / len(events)

        # Event type metrics
        event_type_counts = Counter(e.event_type for e in events)

        return {
            "total_events": len(events),
            "time_span_hours": time_span,
            "events_per_hour": event_rate,
            "error_rate": error_rate,
            "critical_events": severity_counts[AuditSeverity.CRITICAL],
            "severity_distribution": dict(severity_counts),
            "event_type_distribution": {k.value: v for k, v in event_type_counts.most_common()},
            "unique_actors": len({e.actor for e in events}),
        }


class AnomalyDetector:
    """
    Real-time anomaly detection for audit streams
    """

    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.event_window = []
        self.baseline_stats = {}

    async def process_event(self, event: AuditEvent) -> Optional[Anomaly]:
        """Process a single event for anomaly detection"""
        # Add to window
        self.event_window.append(event)
        if len(self.event_window) > self.window_size:
            self.event_window.pop(0)

        # Update baseline statistics
        self._update_baseline(event)

        # Check for anomalies
        anomaly = self._check_event_anomaly(event)

        return anomaly

    def _update_baseline(self, event: AuditEvent):
        """Update baseline statistics"""
        # Update event rate baseline
        # Update actor behavior baseline
        # Update error rate baseline

    def _check_event_anomaly(self, event: AuditEvent) -> Optional[Anomaly]:
        """Check if event is anomalous"""
        # Check against baseline
        # Use statistical methods
        # Return anomaly if detected
        return None


class ComplianceChecker:
    """
    Automated compliance checking against regulations
    """

    def __init__(self, regulations: list[str]):
        self.regulations = regulations
        self.rule_engine = self._load_rules()

    def _load_rules(self) -> dict[str, Any]:
        """Load compliance rules"""
        # Load rules for each regulation
        return {}

    async def check_event(self, event: AuditEvent) -> list[ComplianceViolation]:
        """Check event for compliance violations"""
        violations = []

        # Check against each regulation
        for regulation in self.regulations:
            rule_violations = self._check_regulation(event, regulation)
            violations.extend(rule_violations)

        return violations

    def _check_regulation(self, event: AuditEvent, regulation: str) -> list[ComplianceViolation]:
        """Check event against specific regulation"""
        # Apply regulation-specific rules
        return []


class PatternAnalyzer:
    """
    Pattern analysis for audit events
    """

    def __init__(self):
        self.pattern_library = {}
        self.sequence_detector = None

    async def analyze_patterns(self, events: list[AuditEvent]) -> dict[str, Any]:
        """Analyze patterns in event sequence"""
        patterns = {
            "sequences": self._find_sequences(events),
            "cycles": self._find_cycles(events),
            "correlations": self._find_correlations(events),
        }

        return patterns

    def _find_sequences(self, events: list[AuditEvent]) -> list[tuple[str, int]]:
        """Find common event sequences"""
        # Use sequence mining algorithms
        return []

    def _find_cycles(self, events: list[AuditEvent]) -> list[dict[str, Any]]:
        """Find cyclic patterns"""
        # Detect repeating patterns
        return []

    def _find_correlations(self, events: list[AuditEvent]) -> dict[str, float]:
        """Find correlations between event types"""
        # Calculate correlation coefficients
        return {}
