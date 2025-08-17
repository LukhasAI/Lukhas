"""
Test suite for Enterprise Audit Trail System
Tests core audit functionality with updated imports
"""

import tempfile
from datetime import datetime, timedelta

import pytest

from core.audit import (
    AuditEventType,
    AuditQuery,
    AuditSeverity,
    audit_operation,
    get_audit_trail,
)


@pytest.fixture
async def audit_trail():
    """Create a test audit trail with temporary storage"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        from core.audit.audit_trail import AuditTrail

        trail = AuditTrail(storage_path=tmp_dir)
        yield trail
        # Cleanup happens automatically


@pytest.mark.asyncio
async def test_basic_event_logging(audit_trail):
    """Test basic event logging functionality"""
    # Log a simple event
    event_id = await audit_trail.log_event(
        event_type=AuditEventType.SYSTEM_START,
        actor="test_system",
        details={"message": "Test system starting"},
        severity=AuditSeverity.INFO,
    )

    assert event_id is not None
    assert audit_trail.event_count == 1


@pytest.mark.asyncio
async def test_consciousness_transition_logging(audit_trail):
    """Test consciousness state transition logging"""
    from_state = {"coherence": 0.6, "complexity": 0.5, "awareness_level": 0.55}

    to_state = {"coherence": 0.9, "complexity": 0.8, "awareness_level": 0.85}

    await audit_trail.log_consciousness_transition(
        from_state=from_state,
        to_state=to_state,
        trigger="test_trigger",
        metrics={"processing_time": 100},
        emergence_detected=True,
    )

    # Verify emergence was logged
    assert audit_trail.event_count == 1


@pytest.mark.asyncio
async def test_decision_chain_logging(audit_trail):
    """Test decision chain logging for explainability"""
    steps = [
        {"description": "Analyze options", "result": "3 options found"},
        {
            "description": "Evaluate criteria",
            "result": "Option A scores highest",
        },
        {
            "description": "Check constraints",
            "result": "All constraints satisfied",
        },
    ]

    parent_id = await audit_trail.log_decision_chain(
        decision_id="test_decision_001",
        decision_type="action_selection",
        steps=steps,
        outcome={"selected": "Option A", "score": 0.95},
        rationale="Option A provides optimal outcome",
        confidence=0.95,
        alternatives_considered=[
            {"option": "Option B", "score": 0.7},
            {"option": "Option C", "score": 0.5},
        ],
    )

    assert parent_id is not None
    # Should log parent + 3 steps + final decision = 5 events
    assert audit_trail.event_count >= 5


@pytest.mark.asyncio
async def test_security_event_logging(audit_trail):
    """Test security event logging"""
    await audit_trail.log_security_event(
        threat_type="unauthorized_access",
        threat_level="HIGH",
        source="unknown_ip",
        action_taken="blocked",
        blocked=True,
    )

    # High threat should be logged as CRITICAL
    assert audit_trail.severity_counters[AuditSeverity.CRITICAL] == 1


@pytest.mark.asyncio
async def test_event_query(audit_trail):
    """Test querying audit events"""
    # Log various events
    await audit_trail.log_event(
        AuditEventType.SYSTEM_START, "test_system", {"test": "event1"}
    )

    await audit_trail.log_event(
        AuditEventType.SYSTEM_ERROR,
        "test_system",
        {"error": "test error"},
        severity=AuditSeverity.ERROR,
    )

    # Flush buffer to ensure events are stored
    await audit_trail._flush_buffer()

    # Query all events
    query = AuditQuery(limit=10)
    events = await audit_trail.query_events(query)

    assert len(events) == 2
    assert events[0].event_type == AuditEventType.SYSTEM_ERROR  # Most recent first


@pytest.mark.asyncio
async def test_audit_decorators():
    """Test audit decorators for automatic logging"""
    trail = get_audit_trail()

    @audit_operation("test_operation")
    async def test_function(value: int) -> int:
        return value * 2

    result = await test_function(5)
    assert result == 10

    # Should have logged start and stop events
    analytics = await trail.get_analytics_summary()
    assert analytics["total_events"] >= 2


@pytest.mark.asyncio
async def test_compliance_report_generation(audit_trail):
    """Test compliance report generation"""
    # Log some security events
    for i in range(5):
        await audit_trail.log_event(
            AuditEventType.ACCESS_GRANTED,
            "security_system",
            {"user": f"user_{i}", "resource": "test_resource"},
        )

    await audit_trail.log_event(
        AuditEventType.SECURITY_VIOLATION,
        "security_system",
        {"threat": "test_threat"},
        severity=AuditSeverity.ERROR,
    )

    # Generate report
    report = await audit_trail.generate_compliance_report(
        "security_compliance",
        datetime.now() - timedelta(hours=1),
        datetime.now(),
    )

    assert report is not None
    assert report.report_type == "security_compliance"
    assert len(report.violations) == 1


@pytest.mark.asyncio
async def test_analytics_summary(audit_trail):
    """Test real-time analytics summary"""
    # Log various events
    for i in range(10):
        await audit_trail.log_event(
            AuditEventType.MEMORY_STORED,
            "memory_system",
            {"memory_id": f"mem_{i}"},
        )

    analytics = await audit_trail.get_analytics_summary()

    assert analytics["total_events"] == 10
    assert analytics["session_id"] is not None
    assert "memory_system" in dict(analytics["most_active_actors"])


def test_audit_event_integrity(audit_trail):
    """Test event checksum integrity"""
    from core.audit.audit_trail import AuditEvent

    event = AuditEvent(
        id="test_001",
        timestamp=datetime.now(),
        session_id="test_session",
        event_type=AuditEventType.SYSTEM_START,
        actor="test",
        severity=AuditSeverity.INFO,
        details={"test": "data"},
    )

    # Calculate checksum
    checksum = audit_trail._calculate_checksum(event)
    assert checksum is not None
    assert len(checksum) == 64  # SHA256 hex length

    # Verify checksum changes with content
    event.details["test"] = "modified"
    new_checksum = audit_trail._calculate_checksum(event)
    assert new_checksum != checksum


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
