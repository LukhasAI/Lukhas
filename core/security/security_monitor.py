"""Runtime security event monitoring and threat detection.

This module implements the ``SecurityMonitor`` used across the runtime
security stack to ingest events from authentication, Guardian policy
enforcement, and Quantum Integrity (QI) subsystems.  It provides
lightweight threat detection heuristics, Prometheus metrics export, and
utilities for downstream systems (incident response, dashboards, etc.).

The implementation intentionally keeps processing overhead low while
still surfacing actionable signals for production and tests.
"""
from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Iterable, Mapping, MutableMapping
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from threading import RLock
from time import perf_counter
from typing import Any, Deque, Dict, Tuple

from observability import counter, gauge, histogram

__all__ = [
    "EventSeverity",
    "EventType",
    "SecurityEvent",
    "SecurityMonitor",
    "SecurityMonitorConfig",
    "SecurityThreat",
    "create_security_monitor",
]


class EventType(str, Enum):
    """Supported security event types."""

    AUTHENTICATION_FAILURE = "auth_failure"
    RATE_LIMIT_VIOLATION = "rate_limit_violation"
    ANOMALOUS_BEHAVIOR = "anomalous_behavior"
    POLICY_VIOLATION = "policy_violation"
    QI_SECURITY_EVENT = "qi_security_event"


class EventSeverity(str, Enum):
    """Severity levels for security events and threats."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(slots=True)
class SecurityEvent:
    """Normalized security event."""

    event_type: EventType
    severity: EventSeverity
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source: str | None = None
    actor_id: str | None = None
    ip_address: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SecurityThreat:
    """Active security threat detected by the monitor."""

    threat_id: str
    threat_type: str
    severity: EventSeverity
    detected_at: datetime
    description: str
    context: Dict[str, Any] = field(default_factory=dict)
    last_updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def update_context(self, **updates: Any) -> None:
        self.context.update(updates)
        self.last_updated_at = datetime.now(timezone.utc)


@dataclass(frozen=True)
class SecurityMonitorConfig:
    """Configuration for ``SecurityMonitor`` detection heuristics."""

    auth_failure_threshold: int = 5
    auth_failure_window: timedelta = timedelta(minutes=5)
    rate_limit_threshold: int = 100
    anomaly_score_threshold: float = 0.8


class _SecurityMonitorMetrics:
    """Internal helper that wraps Prometheus metric primitives."""

    def __init__(self) -> None:
        self.security_events_total = counter(
            "security_events_total",
            "Count of processed security events by type and severity",
            labelnames=("type", "severity"),
        )
        self.active_security_threats = gauge(
            "active_security_threats",
            "Number of active security threats detected by the monitor",
        )
        self.processing_duration_seconds = histogram(
            "security_event_processing_duration_seconds",
            "Time spent processing incoming security events",
        )

    def observe_event(self, event: SecurityEvent, duration_seconds: float) -> None:
        metric = self.security_events_total.labels(event.event_type.value, event.severity.value)
        metric.inc()
        self.processing_duration_seconds.observe(duration_seconds)

    def set_active_threats(self, count: int) -> None:
        self.active_security_threats.set(count)


class SecurityMonitor:
    """Runtime monitor for security events and lightweight threat detection."""

    def __init__(self, config: SecurityMonitorConfig | None = None) -> None:
        self.config = config or SecurityMonitorConfig()
        self._metrics = _SecurityMonitorMetrics()
        self._lock = RLock()
        self._auth_failures: MutableMapping[Tuple[str, str], Deque[datetime]] = defaultdict(deque)
        self._active_threats: Dict[str, SecurityThreat] = {}
        self._metrics_snapshot: Dict[str, Any] = {
            "security_events_total": defaultdict(int),
            "processing_durations": [],
            "active_security_threats": 0,
        }

        # Initialise gauge with zero threats
        self._metrics.set_active_threats(0)

    # ------------------------------------------------------------------
    # Event ingestion API
    # ------------------------------------------------------------------
    def process_event(self, event: SecurityEvent) -> SecurityThreat | None:
        """Process a security event and update metrics/threats."""

        start = perf_counter()
        new_threat: SecurityThreat | None = None

        if event.event_type is EventType.AUTHENTICATION_FAILURE:
            new_threat = self._handle_auth_failure(event)
        elif event.event_type is EventType.RATE_LIMIT_VIOLATION:
            new_threat = self._handle_rate_limit(event)
        elif event.event_type is EventType.ANOMALOUS_BEHAVIOR:
            new_threat = self._handle_anomalous_behavior(event)
        elif event.event_type is EventType.POLICY_VIOLATION:
            new_threat = self._handle_policy_violation(event)
        elif event.event_type is EventType.QI_SECURITY_EVENT:
            # QI events are pass-through but still tracked as active threats when
            # flagged with high severity.
            if event.severity in {EventSeverity.HIGH, EventSeverity.CRITICAL}:
                new_threat = self._register_threat(
                    threat_id=self._build_threat_id("qi", event),
                    threat_type="qi_security",
                    severity=event.severity,
                    description="Quantum integrity security event",
                    context=dict(event.metadata),
                    timestamp=event.timestamp,
                )

        duration = perf_counter() - start
        self._metrics.observe_event(event, duration)

        with self._lock:
            self._metrics_snapshot["security_events_total"][(event.event_type.value, event.severity.value)] += 1
            self._metrics_snapshot["processing_durations"].append(duration)
            if new_threat is not None:
                self._active_threats[new_threat.threat_id] = new_threat
                self._metrics_snapshot["active_security_threats"] = len(self._active_threats)
                self._metrics.set_active_threats(len(self._active_threats))
        return new_threat

    # Convenience integration helpers ---------------------------------
    def observe_authentication_attempt(
        self,
        *,
        user_id: str,
        source_ip: str | None,
        success: bool,
        guardian_allowed: bool = True,
        guardian_reason: str | None = None,
        anomaly_score: float | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> Iterable[SecurityThreat]:
        """Observe an authentication attempt from the identity system."""

        metadata = dict(metadata or {})
        threats: list[SecurityThreat] = []

        if not success:
            event = SecurityEvent(
                event_type=EventType.AUTHENTICATION_FAILURE,
                severity=EventSeverity.MEDIUM,
                actor_id=user_id,
                ip_address=source_ip,
                metadata={**metadata, "guardian_allowed": guardian_allowed},
            )
            threat = self.process_event(event)
            if threat:
                threats.append(threat)

        if anomaly_score is not None:
            metadata_with_score = {**metadata, "anomaly_score": anomaly_score, "user_id": user_id}
            anomaly_event = SecurityEvent(
                event_type=EventType.ANOMALOUS_BEHAVIOR,
                severity=EventSeverity.HIGH if anomaly_score >= self.config.anomaly_score_threshold else EventSeverity.MEDIUM,
                actor_id=user_id,
                ip_address=source_ip,
                metadata=metadata_with_score,
            )
            threat = self.process_event(anomaly_event)
            if threat:
                threats.append(threat)

        if not guardian_allowed:
            guardian_event = SecurityEvent(
                event_type=EventType.POLICY_VIOLATION,
                severity=EventSeverity.HIGH,
                actor_id=user_id,
                ip_address=source_ip,
                metadata={**metadata, "reason": guardian_reason or "Guardian policy rejected"},
            )
            threat = self.process_event(guardian_event)
            if threat:
                threats.append(threat)

        return threats

    def observe_rate_limit_violation(
        self,
        *,
        identifier: str,
        source_ip: str | None,
        requests_per_minute: int,
        metadata: Mapping[str, Any] | None = None,
    ) -> SecurityThreat | None:
        """Observe a rate limit violation event."""

        event = SecurityEvent(
            event_type=EventType.RATE_LIMIT_VIOLATION,
            severity=EventSeverity.HIGH if requests_per_minute >= self.config.rate_limit_threshold * 2 else EventSeverity.MEDIUM,
            actor_id=identifier,
            ip_address=source_ip,
            metadata={"requests_per_minute": requests_per_minute, **(metadata or {})},
        )
        return self.process_event(event)

    def observe_policy_violation(
        self,
        *,
        subject: str,
        policy: str,
        severity: EventSeverity = EventSeverity.HIGH,
        metadata: Mapping[str, Any] | None = None,
    ) -> SecurityThreat | None:
        """Observe a Guardian policy violation event."""

        event = SecurityEvent(
            event_type=EventType.POLICY_VIOLATION,
            severity=severity,
            actor_id=subject,
            metadata={"policy": policy, **(metadata or {})},
        )
        return self.process_event(event)

    def observe_qi_security_event(
        self,
        *,
        event_name: str,
        severity: EventSeverity,
        metadata: Mapping[str, Any] | None = None,
    ) -> SecurityThreat | None:
        """Observe a Quantum Integrity system security event."""

        event = SecurityEvent(
            event_type=EventType.QI_SECURITY_EVENT,
            severity=severity,
            metadata={"event_name": event_name, **(metadata or {})},
        )
        return self.process_event(event)

    # ------------------------------------------------------------------
    # Threat lifecycle management
    # ------------------------------------------------------------------
    def get_active_threats(self) -> Dict[str, SecurityThreat]:
        with self._lock:
            return dict(self._active_threats)

    def resolve_threat(self, threat_id: str) -> bool:
        with self._lock:
            removed = self._active_threats.pop(threat_id, None) is not None
            if removed:
                self._metrics_snapshot["active_security_threats"] = len(self._active_threats)
                self._metrics.set_active_threats(len(self._active_threats))
            return removed

    def get_metrics_snapshot(self) -> Dict[str, Any]:
        with self._lock:
            snapshot = {
                "security_events_total": dict(self._metrics_snapshot["security_events_total"]),
                "processing_durations": list(self._metrics_snapshot["processing_durations"]),
                "active_security_threats": self._metrics_snapshot["active_security_threats"],
            }
        return snapshot

    def shutdown(self) -> None:
        with self._lock:
            self._auth_failures.clear()
            self._active_threats.clear()
            self._metrics_snapshot["active_security_threats"] = 0
            self._metrics_snapshot["processing_durations"].clear()
            self._metrics_snapshot["security_events_total"].clear()
            self._metrics.set_active_threats(0)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _handle_auth_failure(self, event: SecurityEvent) -> SecurityThreat | None:
        key = self._build_auth_key(event)
        with self._lock:
            failures = self._auth_failures[key]
            failures.append(event.timestamp)
            threshold_window = self.config.auth_failure_window
            while failures and (event.timestamp - failures[0]) > threshold_window:
                failures.popleft()
            failure_count = len(failures)

        if failure_count >= self.config.auth_failure_threshold:
            return self._register_threat(
                threat_id=self._build_threat_id("auth", event, key_suffix=f"{key[0]}:{key[1]}") if key else None,
                threat_type="auth_bruteforce",
                severity=EventSeverity.HIGH,
                description="Authentication brute force detected",
                context={
                    "user_id": event.actor_id,
                    "ip_address": event.ip_address,
                    "failure_count": failure_count,
                    "threshold": self.config.auth_failure_threshold,
                },
                timestamp=event.timestamp,
            )
        return None

    def _handle_rate_limit(self, event: SecurityEvent) -> SecurityThreat | None:
        requests_per_minute = int(event.metadata.get("requests_per_minute", 0))
        if requests_per_minute < self.config.rate_limit_threshold:
            return None
        severity = EventSeverity.CRITICAL if requests_per_minute >= self.config.rate_limit_threshold * 3 else EventSeverity.HIGH
        return self._register_threat(
            threat_id=self._build_threat_id("rate", event),
            threat_type="rate_limit",
            severity=severity,
            description="Rate limit violation detected",
            context={
                "actor_id": event.actor_id,
                "ip_address": event.ip_address,
                "requests_per_minute": requests_per_minute,
                "threshold": self.config.rate_limit_threshold,
            },
            timestamp=event.timestamp,
        )

    def _handle_anomalous_behavior(self, event: SecurityEvent) -> SecurityThreat | None:
        anomaly_score = float(event.metadata.get("anomaly_score", 0.0))
        if anomaly_score < self.config.anomaly_score_threshold:
            return None
        severity = EventSeverity.CRITICAL if anomaly_score >= 0.95 else EventSeverity.HIGH
        return self._register_threat(
            threat_id=self._build_threat_id("anomaly", event),
            threat_type="anomalous_behavior",
            severity=severity,
            description="High anomaly score detected",
            context={
                "actor_id": event.actor_id,
                "ip_address": event.ip_address,
                "anomaly_score": anomaly_score,
                "threshold": self.config.anomaly_score_threshold,
            },
            timestamp=event.timestamp,
        )

    def _handle_policy_violation(self, event: SecurityEvent) -> SecurityThreat | None:
        policy_name = event.metadata.get("policy", event.metadata.get("reason", "guardian_policy_violation"))
        return self._register_threat(
            threat_id=self._build_threat_id("policy", event),
            threat_type="guardian_policy_violation",
            severity=EventSeverity.HIGH if event.severity != EventSeverity.CRITICAL else EventSeverity.CRITICAL,
            description=f"Guardian policy violation detected: {policy_name}",
            context={
                "actor_id": event.actor_id,
                "details": dict(event.metadata),
            },
            timestamp=event.timestamp,
        )

    def _register_threat(
        self,
        *,
        threat_id: str | None,
        threat_type: str,
        severity: EventSeverity,
        description: str,
        context: Dict[str, Any],
        timestamp: datetime,
    ) -> SecurityThreat:
        if threat_id is None:
            threat_id = self._build_threat_id(threat_type, None)
        threat = SecurityThreat(
            threat_id=threat_id,
            threat_type=threat_type,
            severity=severity,
            detected_at=timestamp,
            description=description,
            context=context,
        )
        return threat

    @staticmethod
    def _build_auth_key(event: SecurityEvent) -> Tuple[str, str]:
        user = event.actor_id or event.metadata.get("user_id") or "unknown"
        ip = event.ip_address or event.metadata.get("ip_address") or "unknown"
        return user, ip

    @staticmethod
    def _build_threat_id(prefix: str, event: SecurityEvent | None, key_suffix: str | None = None) -> str:
        base = f"{prefix}:{datetime.now(timezone.utc).timestamp():.6f}"
        if event and event.actor_id:
            base += f":{event.actor_id}"
        if key_suffix:
            base += f":{key_suffix}"
        return base


def create_security_monitor(config: SecurityMonitorConfig | None = None) -> SecurityMonitor:
    """Factory for creating a ``SecurityMonitor`` with optional configuration."""

    return SecurityMonitor(config=config)
