import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta, timezone

# Mock the observability module before importing the security monitor
MOCK_OBSERVABILITY = MagicMock()
with patch.dict('sys.modules', {'observability': MOCK_OBSERVABILITY}):
    from core.security.security_monitor import SecurityMonitor, SecurityEvent, EventType, EventSeverity, SecurityMonitorConfig

@pytest.fixture
def monitor():
    """Fixture to create a SecurityMonitor instance with a default config."""
    return SecurityMonitor()

@pytest.fixture
def configured_monitor():
    """Fixture to create a SecurityMonitor with a custom config for testing thresholds."""
    config = SecurityMonitorConfig(
        auth_failure_threshold=3,
        auth_failure_window=timedelta(minutes=1)
    )
    return SecurityMonitor(config)

class TestSecurityMonitor:
    """Tests for the SecurityMonitor."""

    def test_process_auth_failure_event_no_threat(self, monitor):
        """Test that a single auth failure event does not create a threat."""
        event = SecurityEvent(
            event_type=EventType.AUTHENTICATION_FAILURE,
            severity=EventSeverity.MEDIUM,
            actor_id="test_user",
            ip_address="127.0.0.1"
        )
        threat = monitor.process_event(event)
        assert threat is None
        assert len(monitor.get_active_threats()) == 0

    def test_process_auth_failure_event_creates_threat(self, configured_monitor):
        """Test that multiple auth failures within the window create a threat."""
        for i in range(configured_monitor.config.auth_failure_threshold):
            event = SecurityEvent(
                event_type=EventType.AUTHENTICATION_FAILURE,
                severity=EventSeverity.MEDIUM,
                actor_id="test_user",
                ip_address="127.0.0.1"
            )
            threat = configured_monitor.process_event(event)
            if i < configured_monitor.config.auth_failure_threshold - 1:
                assert threat is None
            else:
                assert threat is not None
                assert threat.threat_type == "auth_bruteforce"
                assert len(configured_monitor.get_active_threats()) == 1

    def test_resolve_threat(self, configured_monitor):
        """Test threat resolution."""
        # First, create a threat
        for _ in range(configured_monitor.config.auth_failure_threshold):
            event = SecurityEvent(
                event_type=EventType.AUTHENTICATION_FAILURE,
                severity=EventSeverity.MEDIUM,
                actor_id="test_user",
                ip_address="127.0.0.1"
            )
            configured_monitor.process_event(event)

        threat_id = list(configured_monitor.get_active_threats().keys())[0]

        was_resolved = configured_monitor.resolve_threat(threat_id)

        assert was_resolved is True
        assert len(configured_monitor.get_active_threats()) == 0

    def test_metrics_snapshot(self, monitor):
        """Test the metrics snapshot functionality."""
        event = SecurityEvent(
            event_type=EventType.POLICY_VIOLATION,
            severity=EventSeverity.HIGH,
            actor_id="test_user",
        )
        monitor.process_event(event)

        snapshot = monitor.get_metrics_snapshot()

        assert snapshot["active_security_threats"] == 1
        assert snapshot["security_events_total"][("policy_violation", "high")] == 1
        assert len(snapshot["processing_durations"]) == 1

    def test_observe_rate_limit_violation(self, monitor):
        """Test the observe_rate_limit_violation helper."""
        threat = monitor.observe_rate_limit_violation(
            identifier="test",
            source_ip="1.1.1.1",
            requests_per_minute=monitor.config.rate_limit_threshold * 2
        )
        assert threat is not None
        assert threat.threat_type == "rate_limit"
        assert threat.severity == EventSeverity.HIGH

    def test_observe_anomalous_behavior(self, monitor):
        """Test processing of an anomalous behavior event."""
        event = SecurityEvent(
            event_type=EventType.ANOMALOUS_BEHAVIOR,
            severity=EventSeverity.HIGH,
            metadata={'anomaly_score': 0.9}
        )
        threat = monitor.process_event(event)
        assert threat is not None
        assert threat.threat_type == "anomalous_behavior"

    def test_observe_qi_event(self, monitor):
        """Test processing of a QI security event."""
        event = SecurityEvent(
            event_type=EventType.QI_SECURITY_EVENT,
            severity=EventSeverity.CRITICAL
        )
        threat = monitor.process_event(event)
        assert threat is not None
        assert threat.threat_type == "qi_security"
