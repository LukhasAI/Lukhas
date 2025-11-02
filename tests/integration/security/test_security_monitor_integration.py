"""Integration tests exercising the security monitor hooks."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, List

import pytest

from core.security.security_monitor import EventSeverity, SecurityMonitor, SecurityMonitorConfig


@dataclass
class FakeAuthAttempt:
    user_id: str
    ip: str
    success: bool
    guardian_allowed: bool = True
    guardian_reason: str | None = None
    anomaly_score: float | None = None


class FakeIdentityService:
    """Minimal identity/authentication surface instrumented with the monitor."""

    def __init__(self, monitor: SecurityMonitor) -> None:
        self.monitor = monitor
        self.attempts: List[FakeAuthAttempt] = []

    async def authenticate(self, attempt: FakeAuthAttempt) -> Dict[str, Any]:
        self.attempts.append(attempt)
        threats = self.monitor.observe_authentication_attempt(
            user_id=attempt.user_id,
            source_ip=attempt.ip,
            success=attempt.success,
            guardian_allowed=attempt.guardian_allowed,
            guardian_reason=attempt.guardian_reason,
            anomaly_score=attempt.anomaly_score,
            metadata={"source": "fake_identity"},
        )
        return {
            "verified": attempt.success and attempt.guardian_allowed,
            "threats": [t.threat_type for t in threats],
        }


@pytest.mark.asyncio()
async def test_security_monitor_end_to_end_detection() -> None:
    """The security monitor tracks auth, policy, rate and QI signals together."""

    monitor = SecurityMonitor(
        config=SecurityMonitorConfig(
            auth_failure_threshold=2,
            auth_failure_window=SecurityMonitorConfig().auth_failure_window,
            rate_limit_threshold=40,
            anomaly_score_threshold=0.8,
        )
    )
    identity = FakeIdentityService(monitor)

    # Two failed attempts should trigger a brute force threat
    await identity.authenticate(FakeAuthAttempt(user_id="alice", ip="1.1.1.1", success=False))
    result = await identity.authenticate(FakeAuthAttempt(user_id="alice", ip="1.1.1.1", success=False))
    assert "auth_bruteforce" in result["threats"]

    # Guardian policy violation is surfaced as its own threat
    guardian_result = await identity.authenticate(
        FakeAuthAttempt(
            user_id="bob",
            ip="2.2.2.2",
            success=True,
            guardian_allowed=False,
            guardian_reason="guardian_block",
        )
    )
    assert "guardian_policy_violation" in guardian_result["threats"]

    # Rate limit violation
    rate_threat = monitor.observe_rate_limit_violation(
        identifier="bob",
        source_ip="2.2.2.2",
        requests_per_minute=90,
    )
    assert rate_threat is not None

    # QI anomaly with high severity should be registered
    qi_threat = monitor.observe_qi_security_event(
        event_name="qi_integrity_anomaly",
        severity=EventSeverity.CRITICAL,
        metadata={"anomaly_score": 0.92},
    )
    assert qi_threat is not None

    # Ensure metrics and active threat tracking capture all signals
    active_threats = monitor.get_active_threats()
    assert any(t.threat_type == "auth_bruteforce" for t in active_threats.values())
    assert any(t.threat_type == "guardian_policy_violation" for t in active_threats.values())
    assert any(t.threat_type == "rate_limit" for t in active_threats.values())
    assert any(t.threat_type == "qi_security" for t in active_threats.values())

    snapshot = monitor.get_metrics_snapshot()
    # Processing durations should have entries for each event processed
    assert len(snapshot["processing_durations"]) >= 5
    assert snapshot["active_security_threats"] == len(active_threats)

    monitor.shutdown()
    assert monitor.get_active_threats() == {}
