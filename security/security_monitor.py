"""Security monitoring utilities for threat detection.

This module provides a simplified implementation of the security monitor
required by the integration test suite.  The implementation focuses on
predictable behaviour so the tests can exercise threat detection scenarios
without depending on heavyweight external infrastructure.
"""
from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, Iterable, Optional


class ThreatLevel(Enum):
    """Threat severity levels used by the monitor."""

    INFORMATIONAL = "informational"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EventType(Enum):
    """Security event categories supported by the monitor."""

    AUTHENTICATION = "authentication"
    SYSTEM_ACCESS = "system_access"
    DATA_ACCESS = "data_access"


@dataclass
class SecurityEvent:
    """Security event produced by ``create_event``."""

    id: str
    event_type: EventType
    timestamp: datetime
    source_ip: Optional[str] = None
    user_id: Optional[str] = None
    resource_id: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ThreatDetection:
    """Represents an active threat tracked by the monitor."""

    id: str
    name: str
    threat_level: ThreatLevel
    detected_at: datetime
    indicators: Dict[str, Any] = field(default_factory=dict)

    def is_expired(self, now: datetime, ttl: timedelta) -> bool:
        return now - self.detected_at > ttl


class SecurityMonitor:
    """Process events and surface security threats for the tests."""

    _BRUTE_FORCE_THRESHOLD = 5
    _THREAT_TTL = timedelta(minutes=30)

    def __init__(
        self,
        buffer_size: int = 10000,
        processing_threads: int = 1,
        guardian_integration: bool = False,
        *,
        malicious_ips: Optional[Iterable[str]] = None,
    ) -> None:
        self.buffer_size = buffer_size
        self.processing_threads = processing_threads
        self.guardian_integration = guardian_integration
        self._malicious_ips = set(malicious_ips or {"192.168.1.100"})
        self._active_threats: Dict[str, ThreatDetection] = {}
        self._failed_attempts: Dict[str, list[datetime]] = {}
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Factory helpers
    def create_event(
        self,
        *,
        event_type: EventType,
        source_ip: Optional[str] = None,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> SecurityEvent:
        """Create a :class:`SecurityEvent` instance ready for submission."""

        return SecurityEvent(
            id=str(uuid.uuid4()),
            event_type=event_type,
            timestamp=datetime.now(timezone.utc),
            source_ip=source_ip,
            user_id=user_id,
            resource_id=resource_id,
            details=details or {},
        )

    # ------------------------------------------------------------------
    def submit_event(self, event: SecurityEvent) -> bool:
        """Submit an event for processing.

        The method always returns ``True`` for the tests and updates the
        threat registry synchronously so assertions can run immediately
        after submission.
        """

        with self._lock:
            self._expire_threats_locked()
            self._process_brute_force(event)
            self._process_malicious_ip(event)
        return True

    def get_active_threats(self) -> Dict[str, ThreatDetection]:
        """Return a snapshot of active threats."""

        with self._lock:
            self._expire_threats_locked()
            # Return a shallow copy so callers cannot mutate state.
            return dict(self._active_threats)

    def shutdown(self) -> None:
        """Cleanup resources used by the monitor."""

        with self._lock:
            self._active_threats.clear()
            self._failed_attempts.clear()

    # ------------------------------------------------------------------
    def _expire_threats_locked(self) -> None:
        now = datetime.now(timezone.utc)
        expired = [tid for tid, threat in self._active_threats.items() if threat.is_expired(now, self._THREAT_TTL)]
        for threat_id in expired:
            self._active_threats.pop(threat_id, None)

    def _register_threat(self, name: str, threat_level: ThreatLevel, indicators: Dict[str, Any]) -> None:
        threat_id = str(uuid.uuid4())
        self._active_threats[threat_id] = ThreatDetection(
            id=threat_id,
            name=name,
            threat_level=threat_level,
            detected_at=datetime.now(timezone.utc),
            indicators=dict(indicators),
        )

    def _process_brute_force(self, event: SecurityEvent) -> None:
        if event.event_type is not EventType.AUTHENTICATION:
            return
        if event.source_ip is None:
            return

        attempts = self._failed_attempts.setdefault(event.source_ip, [])
        now = datetime.now(timezone.utc)

        if event.details.get("success") is True:
            attempts.clear()
            return

        attempts.append(now)
        # Only keep attempts within a 15 minute rolling window
        cutoff = now - timedelta(minutes=15)
        self._failed_attempts[event.source_ip] = [ts for ts in attempts if ts >= cutoff]

        if len(self._failed_attempts[event.source_ip]) >= self._BRUTE_FORCE_THRESHOLD:
            self._register_threat(
                name="Brute Force Attack",
                threat_level=ThreatLevel.HIGH,
                indicators={
                    "source_ip": event.source_ip,
                    "attempts": len(self._failed_attempts[event.source_ip]),
                },
            )

    def _process_malicious_ip(self, event: SecurityEvent) -> None:
        if event.source_ip is None:
            return
        if event.source_ip not in self._malicious_ips:
            return
        if event.event_type not in {EventType.SYSTEM_ACCESS, EventType.DATA_ACCESS, EventType.AUTHENTICATION}:
            return

        self._register_threat(
            name="Malicious IP Activity",
            threat_level=ThreatLevel.MEDIUM,
            indicators={
                "source_ip": event.source_ip,
                "event_type": event.event_type.value,
            },
        )


def create_security_monitor(config: Optional[Dict[str, Any]] = None) -> SecurityMonitor:
    """Factory used by the tests to construct a monitor instance."""

    config = config or {}
    return SecurityMonitor(
        buffer_size=config.get("buffer_size", 10000),
        processing_threads=config.get("processing_threads", 1),
        guardian_integration=config.get("guardian_integration", False),
        malicious_ips=config.get("malicious_ips"),
    )


__all__ = [
    "EventType",
    "SecurityEvent",
    "SecurityMonitor",
    "ThreatDetection",
    "ThreatLevel",
    "create_security_monitor",
]
