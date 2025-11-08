"""
Tests for the emergency protocol methods in the Enhanced Guardian System.
"""

import asyncio
import time
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from labs.governance.guardian.guardian_system import (
    EnhancedGuardianSystem,
    GuardianAgent,
    GuardianRole,
    GuardianStatus,
    ResponseAction,
    ThreatDetection,
    ThreatLevel,
)


@pytest.mark.asyncio
class TestEmergencyProtocols:
    """Test suite for emergency protocols in the Enhanced Guardian System."""

    @pytest.fixture
    def guardian_system(self):
        """Fixture to create a clean instance of the EnhancedGuardianSystem."""
        system = EnhancedGuardianSystem()
        # The system is now initialized synchronously, so we can just clear agents.
        system.guardian_agents.clear()
        yield system

    @pytest.fixture
    def guardian_agent(self):
        """Fixture for a generic guardian agent."""
        return GuardianAgent(
            agent_id="test_agent_001",
            name="Test Agent",
            role=GuardianRole.GUARDIAN,
            status=GuardianStatus.ACTIVE,
            capabilities=["emergency_response"],
        )

    def create_threat(self, level=ThreatLevel.CRITICAL, threat_type="security_breach"):
        """Helper to create a threat detection object."""
        return ThreatDetection(
            detection_id=f"threat_{uuid.uuid4().hex[:8]}",
            detected_at=datetime.now(timezone.utc),
            threat_type=threat_type,
            threat_level=level,
            threat_score=0.95,
            source="test_source",
            description="A critical test threat.",
        )

    # --- Emergency Shutdown Protocol Tests ---

    async def test_emergency_shutdown_performance_under_5s(self, guardian_system, guardian_agent):
        """Test that the emergency shutdown protocol executes in under 5 seconds."""
        threat = self.create_threat()

        # The actual method is fast; the main thing is to ensure it's not blocking.
        # We can simulate a small amount of async work.
        original_shutdown = guardian_system._emergency_shutdown

        async def patched_shutdown(*args, **kwargs):
            await asyncio.sleep(0.01)
            return await original_shutdown(*args, **kwargs)

        with patch.object(guardian_system, '_emergency_shutdown', side_effect=patched_shutdown) as mock_shutdown:
            start_time = time.time()
            await guardian_system._emergency_shutdown(threat, guardian_agent)
            end_time = time.time()

            execution_time = end_time - start_time
            assert execution_time < 5.0
            mock_shutdown.assert_awaited_once()

    async def test_emergency_shutdown_state_changes(self, guardian_system, guardian_agent):
        """Test that the system state changes correctly during an emergency shutdown."""
        threat = self.create_threat()
        initial_emergency_activations = guardian_system.metrics["emergency_activations"]

        await guardian_system._emergency_shutdown(threat, guardian_agent)

        assert guardian_system.emergency_protocols_active is True
        assert guardian_system.system_status == GuardianStatus.EMERGENCY
        assert guardian_system.metrics["emergency_activations"] == initial_emergency_activations + 1

    @patch("labs.governance.guardian.guardian_system.logger")
    async def test_emergency_shutdown_logging(self, mock_logger, guardian_system, guardian_agent):
        """Test that a critical log is generated during an emergency shutdown."""
        threat = self.create_threat()
        await guardian_system._emergency_shutdown(threat, guardian_agent)

        mock_logger.critical.assert_called_once()
        call_args = mock_logger.critical.call_args[0][0]
        assert "EMERGENCY SHUTDOWN activated" in call_args
        assert threat.detection_id in call_args

    # --- Self-Repair Mechanism Tests ---

    async def test_initiate_repairs_for_drift_detection(self, guardian_system, guardian_agent):
        """Test that the correct repair actions are initiated for drift detection."""
        threat = self.create_threat(threat_type="drift_detection")
        result = await guardian_system._initiate_repairs(threat, guardian_agent)

        assert result["success"] is True
        assert "Drift repair initiated" in result["repair_actions"]
        assert "System recalibration started" in result["repair_actions"]

    async def test_initiate_repairs_for_constitutional_violation(self, guardian_system, guardian_agent):
        """Test repair actions for a constitutional violation."""
        threat = self.create_threat(threat_type="constitutional_violation")
        result = await guardian_system._initiate_repairs(threat, guardian_agent)

        assert result["success"] is True
        assert "Constitutional compliance restoration" in result["repair_actions"]
        assert "Policy enforcement strengthened" in result["repair_actions"]

    async def test_initiate_repairs_graceful_degradation(self, guardian_system, guardian_agent):
        """Test that the repair mechanism handles unexpected errors gracefully."""
        threat = self.create_threat()
        response = MagicMock() # Mock the response object

        # Simulate an unexpected exception during the repair process
        with patch.object(
            guardian_system, "_initiate_repairs", side_effect=Exception("Repair subsystem failed")
        ) as mock_repair:
            result = await guardian_system._execute_response_action(
                ResponseAction.REPAIR, threat, guardian_agent, response
            )

            assert result["success"] is False
            assert "Repair subsystem failed" in result["error"]
            mock_repair.assert_awaited_once_with(threat, guardian_agent)

    # --- Human Escalation Trigger Tests ---

    @patch("labs.governance.guardian.guardian_system.logger")
    async def test_escalate_to_humans_critical_threat(self, mock_logger, guardian_system, guardian_agent):
        """Test human escalation for a critical threat."""
        threat = self.create_threat(level=ThreatLevel.CRITICAL)
        result = await guardian_system._escalate_to_humans(threat, guardian_agent)

        assert result["success"] is True
        assert result["priority"] == "high"
        assert result["response_required"] is True
        assert result["escalation_data"]["time_sensitive"] is True

        mock_logger.critical.assert_called_once()
        log_message = mock_logger.critical.call_args[0][0]
        assert "ESCALATION" in log_message
        assert threat.detection_id in log_message

    @patch("labs.governance.guardian.guardian_system.logger")
    async def test_escalate_to_humans_moderate_threat(self, mock_logger, guardian_system, guardian_agent):
        """Test human escalation for a non-critical (moderate) threat."""
        threat = self.create_threat(level=ThreatLevel.MODERATE)
        result = await guardian_system._escalate_to_humans(threat, guardian_agent)

        assert result["success"] is True
        assert result["priority"] == "normal"
        assert result["response_required"] is True
        assert result["escalation_data"]["time_sensitive"] is False

        mock_logger.critical.assert_called_once() # Logs are critical for any escalation
        log_message = mock_logger.critical.call_args[0][0]
        assert "ESCALATION" in log_message
        assert threat.detection_id in log_message

    async def test_escalation_payload_structure(self, guardian_system, guardian_agent):
        """Verify the structure and content of the escalation payload."""
        threat = self.create_threat()
        threat.user_context = {"user_id": "test_user"}
        threat.recommended_actions = [ResponseAction.BLOCK, ResponseAction.QUARANTINE]
        result = await guardian_system._escalate_to_humans(threat, guardian_agent)

        payload = result["escalation_data"]
        assert "threat_summary" in payload
        assert "system_impact" in payload
        assert "recommended_actions" in payload

        assert payload["threat_summary"]["id"] == threat.detection_id
        assert payload["threat_summary"]["level"] == "critical"
        assert payload["system_impact"]["user_impact"] == {"user_id": "test_user"}
        assert payload["recommended_actions"] == ["block", "quarantine"]

    # --- Edge Case and Coverage Tests ---

    async def test_execute_unknown_response_action(self, guardian_system, guardian_agent):
        """Test that an unknown response action is handled correctly."""
        threat = self.create_threat()
        response = MagicMock()
        unknown_action = "unknown_action"
        result = await guardian_system._execute_response_action(
            unknown_action, threat, guardian_agent, response
        )

        assert result["success"] is False
        assert "Unknown action" in result["error"]

    async def test_initiate_repairs_for_other_threat_types(self, guardian_system, guardian_agent):
        """Test that _initiate_repairs returns an empty list for unhandled threat types."""
        threat = self.create_threat(threat_type="anomaly_detection")
        result = await guardian_system._initiate_repairs(threat, guardian_agent)

        assert result["success"] is True
        assert result["repair_actions"] == []

    # --- Recovery Procedure Tests ---

    async def test_manual_recovery_from_emergency_shutdown(self, guardian_system, guardian_agent):
        """Test that the system can be manually recovered after an emergency shutdown."""
        # 1. Trigger emergency state
        threat = self.create_threat()
        await guardian_system._emergency_shutdown(threat, guardian_agent)

        assert guardian_system.emergency_protocols_active is True
        assert guardian_system.system_status == GuardianStatus.EMERGENCY

        # 2. Simulate manual recovery by resetting state
        guardian_system.emergency_protocols_active = False
        guardian_system.system_status = GuardianStatus.ACTIVE

        assert guardian_system.emergency_protocols_active is False
        assert guardian_system.system_status == GuardianStatus.ACTIVE

        # 3. Verify the system can process a new threat normally after recovery
        new_threat = self.create_threat(level=ThreatLevel.LOW, threat_type="minor_anomaly")

        # We need to mock the full detect_threat path to ensure it runs
        with patch.object(guardian_system, '_analyze_threat', new_callable=AsyncMock) as mock_analyze, \
             patch.object(guardian_system, '_assign_threat_to_agent', new_callable=AsyncMock) as mock_assign, \
             patch.object(guardian_system, '_trigger_automated_response', new_callable=AsyncMock) as mock_respond:

            mock_analyze.return_value = {
                "level": ThreatLevel.LOW, "score": 0.1, "recommended_actions": [ResponseAction.MONITOR]
            }
            mock_assign.return_value = guardian_agent
            guardian_system.guardian_agents[guardian_agent.agent_id] = guardian_agent

            detected_threat = await guardian_system.detect_threat(
                threat_type="minor_anomaly",
                source="test_source_2",
                threat_data={"anomaly_score": 0.1}
            )

            assert detected_threat is not None
            assert detected_threat.threat_level == ThreatLevel.LOW
            assert detected_threat.assigned_guardian == guardian_agent.agent_id
            mock_respond.assert_awaited_once()
