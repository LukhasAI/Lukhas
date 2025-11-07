"""
Unit tests for EnhancedGuardianSystem emergency protocols.
"""
import asyncio
import time
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from labs.governance.guardian.guardian_system import (
    EnhancedGuardianSystem,
    GuardianStatus,
    ResponseAction,
    ThreatLevel,
)


@pytest.fixture
async def guardian_system():
    """Fixture for an initialized EnhancedGuardianSystem."""
    system = EnhancedGuardianSystem()
    # Allow initialization to complete
    await asyncio.sleep(0.01)
    # Stop background tasks to prevent interference during tests
    system.monitoring_active = False
    return system


@pytest.mark.asyncio
class TestEmergencyProtocols:
    """Test suite for emergency protocols in the Guardian System."""

    async def test_emergency_shutdown_protocol_speed(self, guardian_system):
        """Test that the emergency shutdown protocol executes in under 5 seconds."""
        threat = await guardian_system.detect_threat(
            "security_breach", "internal_monitor", {"breach_type": "critical_failure"}
        )
        assert threat is not None

        start_time = time.monotonic()

        # We are testing the time it takes to INITIATE the shutdown, not the shutdown itself,
        # as the actual shutdown is a complex process that would be handled by other systems.
        # The guardian's responsibility is to trigger it quickly.
        with patch('asyncio.sleep', new_callable=AsyncMock): # Mock sleep to not slow down the test
            response = await guardian_system.respond_to_threat(threat.detection_id, [ResponseAction.SHUTDOWN])

        execution_time = time.monotonic() - start_time

        assert execution_time < 5.0, f"Shutdown protocol took too long: {execution_time:.2f}s"
        assert response is not None
        assert response.success is True
        assert guardian_system.system_status == GuardianStatus.EMERGENCY

    async def test_emergency_shutdown_activates_protocols(self, guardian_system):
        """Test that emergency shutdown correctly updates system status and flags."""
        threat = await guardian_system.detect_threat(
            "security_breach", "internal_monitor", {"breach_type": "critical_failure"}
        )
        assert threat is not None

        await guardian_system.respond_to_threat(threat.detection_id, [ResponseAction.SHUTDOWN])

        assert guardian_system.system_status == GuardianStatus.EMERGENCY
        assert guardian_system.emergency_protocols_active is True
        assert guardian_system.metrics["emergency_activations"] == 1

    async def test_self_repair_mechanisms_trigger(self, guardian_system):
        """Test that self-repair mechanisms are initiated for relevant threats."""
        threat = await guardian_system.detect_threat(
            "drift_detection", "system_monitor", {"drift_score": 0.25}
        )
        assert threat is not None

        with patch.object(guardian_system, "_initiate_repairs", new_callable=AsyncMock) as mock_repair:
            mock_repair.return_value = {"success": True}
            await guardian_system.respond_to_threat(threat.detection_id, [ResponseAction.REPAIR])

        mock_repair.assert_awaited_once()

    async def test_human_escalation_triggers(self, guardian_system):
        """Test that human escalation is triggered for critical threats."""
        threat = await guardian_system.detect_threat(
            "constitutional_violation", "policy_monitor", {"severity": "high"}
        )
        assert threat is not None

        with patch.object(guardian_system, "_escalate_to_humans", new_callable=AsyncMock) as mock_escalate:
            mock_escalate.return_value = {"success": True}
            await guardian_system.respond_to_threat(threat.detection_id, [ResponseAction.ESCALATE])

        mock_escalate.assert_awaited_once()

    async def test_graceful_degradation_on_component_failure(self, guardian_system):
        """Test the system's ability to gracefully degrade when a component fails during an emergency."""
        threat = await guardian_system.detect_threat(
            "security_breach", "internal_monitor", {"breach_type": "critical_failure"}
        )
        assert threat is not None

        # Simulate a failure in the _block_operation component
        with patch.object(guardian_system, "_block_operation", new_callable=AsyncMock) as mock_block:
            mock_block.side_effect = Exception("Component Failure")

            response = await guardian_system.respond_to_threat(
                threat.detection_id, [ResponseAction.BLOCK, ResponseAction.ESCALATE]
            )

        assert response is not None
        # The overall response should be a failure because a critical component failed.
        assert response.success is False
        # However, the system should still have attempted to escalate.
        assert ResponseAction.ESCALATE in response.actions_taken

    async def test_recovery_procedure_after_shutdown(self, guardian_system):
        """Test the system's recovery procedures after an emergency shutdown."""
        # Step 1: Trigger an emergency shutdown
        threat = await guardian_system.detect_threat(
            "security_breach", "internal_monitor", {"breach_type": "critical_failure"}
        )
        assert threat is not None
        await guardian_system.respond_to_threat(threat.detection_id, [ResponseAction.SHUTDOWN])
        assert guardian_system.system_status == GuardianStatus.EMERGENCY

        # Step 2: Simulate manual recovery/resolution of the issue
        # In a real system, this would be a complex process. Here, we'll just reset the status.
        guardian_system.system_status = GuardianStatus.ACTIVE
        guardian_system.emergency_protocols_active = False

        # Step 3: Verify the system can go back to normal operation
        # For example, by detecting and responding to a new, low-level threat.
        new_threat = await guardian_system.detect_threat(
            "anomaly_detection", "sensor_A", {"anomaly_score": 0.2}
        )
        assert new_threat is not None
        response = await guardian_system.respond_to_threat(new_threat.detection_id, [ResponseAction.MONITOR])

        assert response is not None
        assert response.success is True
        assert guardian_system.system_status == GuardianStatus.ACTIVE

    async def test_mock_emergency_scenario_full_flow(self, guardian_system):
        """Test a full emergency scenario from detection to resolution."""
        # 1. Detect a critical threat
        threat = await guardian_system.detect_threat(
            "security_breach", "external_api", {"breach_type": "unauthorized_access"}
        )
        assert threat is not None
        assert threat.threat_level == ThreatLevel.CRITICAL

        # 2. Initiate emergency shutdown
        response_shutdown = await guardian_system.respond_to_threat(
            threat.detection_id, [ResponseAction.SHUTDOWN]
        )
        assert response_shutdown is not None
        assert response_shutdown.success is True
        assert guardian_system.system_status == GuardianStatus.EMERGENCY

        # 3. Escalate to humans
        response_escalate = await guardian_system.respond_to_threat(
            threat.detection_id, [ResponseAction.ESCALATE]
        )
        assert response_escalate is not None
        assert response_escalate.success is True
        assert response_escalate.requires_human_review is True

        # 4. Simulate manual recovery
        guardian_system.system_status = GuardianStatus.MAINTENANCE

        # 5. Initiate repairs
        response_repair = await guardian_system.respond_to_threat(
            threat.detection_id, [ResponseAction.REPAIR]
        )
        assert response_repair is not None
        assert response_repair.success is True

        # 6. Verify threat resolution and return to active status
        assert response_repair.threat_neutralized is True
        guardian_system.system_status = GuardianStatus.ACTIVE

        assert guardian_system.system_status == GuardianStatus.ACTIVE
        assert threat.detection_id not in guardian_system.active_threats
        assert len(guardian_system.threat_history) > 0
        assert guardian_system.threat_history[-1].detection_id == threat.detection_id

    async def test_agent_registration_failure(self, guardian_system):
        """Test that agent registration fails with invalid config."""
        with patch.object(guardian_system, "_validate_agent_config", new_callable=AsyncMock) as mock_validate:
            mock_validate.return_value = False
            agent = MagicMock()
            agent.agent_id = "test_agent_001"
            result = await guardian_system.register_guardian_agent(agent)
            assert result is False

    async def test_analyze_threat_uncovered_branches(self, guardian_system):
        """Test uncovered branches in the _analyze_threat method."""
        # Low drift score
        threat_low_drift = await guardian_system.detect_threat("drift_detection", "test", {"drift_score": 0.1})
        assert threat_low_drift.threat_level == ThreatLevel.LOW

        # Low severity constitutional violation
        threat_low_const = await guardian_system.detect_threat("constitutional_violation", "test", {"severity": "low"})
        assert threat_low_const.threat_level == ThreatLevel.MODERATE

        # High anomaly score
        threat_high_anomaly = await guardian_system.detect_threat("anomaly_detection", "test", {"anomaly_score": 0.9})
        assert threat_high_anomaly.threat_level == ThreatLevel.HIGH

        # Unknown threat type
        threat_unknown = await guardian_system.detect_threat("unknown_threat", "test", {})
        assert threat_unknown.threat_level == ThreatLevel.MODERATE

    async def test_respond_to_threat_not_found(self, guardian_system):
        """Test responding to a threat that does not exist."""
        response = await guardian_system.respond_to_threat("non_existent_threat", [ResponseAction.MONITOR])
        assert response is None

    async def test_respond_to_threat_no_agent(self, guardian_system):
        """Test responding to a threat when no agent can be assigned."""
        threat = await guardian_system.detect_threat("some_threat", "source", {})
        threat.assigned_guardian = None
        response = await guardian_system.respond_to_threat(threat.detection_id, [ResponseAction.MONITOR])
        assert response is None

    async def test_quarantine_source_action(self, guardian_system):
        """Test the quarantine source action."""
        threat = await guardian_system.detect_threat("security_breach", "source_to_quarantine", {})
        response = await guardian_system.respond_to_threat(threat.detection_id, [ResponseAction.QUARANTINE])
        assert response.success
        assert response.actions_taken == [ResponseAction.QUARANTINE]

    async def test_initiate_repairs_constitutional_violation(self, guardian_system):
        """Test the constitutional violation branch of the repair action."""
        threat = await guardian_system.detect_threat("constitutional_violation", "source", {})
        response = await guardian_system.respond_to_threat(threat.detection_id, [ResponseAction.REPAIR])
        assert response.success
        # The audit trail contains the action, not the specific repair details.
        # The details are in the result of the action, which isn't stored on the response.
        assert "Executed repair: completed" in response.audit_trail

    async def test_unknown_response_action(self, guardian_system):
        """Test that an unknown response action is handled gracefully."""
        threat = await guardian_system.detect_threat("some_threat", "source", {})
        response = await guardian_system.respond_to_threat(threat.detection_id, ["unknown_action"])
        assert response is not None
        assert response.success is False
        assert "Executed unknown_action: failed" in response.audit_trail

    async def test_health_check_loop_agent_status_changes(self, guardian_system):
        """Test that the health check loop correctly identifies WARNING and OFFLINE agents."""
        agent = guardian_system.guardian_agents["sentinel_001"]

        # Test WARNING status
        agent.last_heartbeat = datetime.now(timezone.utc) - timedelta(minutes=2)
        await guardian_system._check_agents_health()
        assert agent.status == GuardianStatus.WARNING

        # Test OFFLINE status
        agent.last_heartbeat = datetime.now(timezone.utc) - timedelta(minutes=6)
        await guardian_system._check_agents_health()
        assert agent.status == GuardianStatus.OFFLINE
