"""Unit tests for :mod:`core.security.security_monitor`."""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone

import pytest

from core.security.security_monitor import (
    EventSeverity,
    EventType,
    SecurityEvent,
    SecurityMonitor,
    SecurityMonitorConfig,
)


@pytest.fixture()
def monitor() -> SecurityMonitor:
    config = SecurityMonitorConfig(
        auth_failure_threshold=3,
        auth_failure_window=timedelta(minutes=5),
        rate_limit_threshold=50,
        anomaly_score_threshold=0.75,
    )
    return SecurityMonitor(config=config)


def test_auth_failure_threshold_triggers_threat(monitor: SecurityMonitor) -> None:
    """Submitting repeated authentication failures registers a threat."""

    now = datetime.now(timezone.utc)
    for _ in range(3):
        event = SecurityEvent(
            event_type=EventType.AUTHENTICATION_FAILURE,
            severity=EventSeverity.MEDIUM,
            timestamp=now,
            actor_id="user-123",
            ip_address="10.0.0.1",
        )
        monitor.process_event(event)
        # Advance timestamp slightly to emulate real traffic
        now += timedelta(seconds=10)

    threats = monitor.get_active_threats()
    assert threats, "Expected at least one active threat after repeated failures"
    threat = next(iter(threats.values()))
    assert threat.threat_type == "auth_bruteforce"
    assert threat.context["failure_count"] >= monitor.config.auth_failure_threshold


def test_rate_limit_violation_creates_threat(monitor: SecurityMonitor) -> None:
    """Rate limit violations above the configured threshold register threats."""

    threat = monitor.observe_rate_limit_violation(
        identifier="user-abc",
        source_ip="192.168.1.10",
        requests_per_minute=120,
        metadata={"endpoint": "/api/resource"},
    )
    assert threat is not None
    assert "requests_per_minute" in threat.context
    assert threat.context["requests_per_minute"] == 120


def test_anomaly_score_detection_respects_threshold(monitor: SecurityMonitor) -> None:
    """High anomaly scores trigger anomalous behavior threats."""

    threats = monitor.observe_authentication_attempt(
        user_id="user-anomaly",
        source_ip="10.10.10.10",
        success=True,
        anomaly_score=0.9,
    )
    assert any(t.threat_type == "anomalous_behavior" for t in threats)


def test_metrics_snapshot_records_events(monitor: SecurityMonitor) -> None:
    """Metrics snapshots accumulate counters and durations for processed events."""

    monitor.process_event(
        SecurityEvent(
            event_type=EventType.POLICY_VIOLATION,
            severity=EventSeverity.HIGH,
            metadata={"policy": "guardian.test.policy"},
        )
    )
    # Give histogram observation a chance to record a non-zero duration
    time.sleep(0.01)
    snapshot = monitor.get_metrics_snapshot()
    assert snapshot["security_events_total"][(EventType.POLICY_VIOLATION.value, EventSeverity.HIGH.value)] == 1
    assert snapshot["active_security_threats"] >= 1
    assert snapshot["processing_durations"], "Expected at least one recorded processing duration"
