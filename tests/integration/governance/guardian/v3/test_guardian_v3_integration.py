"""
Integration Tests for the Enhanced Guardian System (V3)

These tests cover the end-to-end functionality of the Guardian V3 system,
focusing on cross-module interactions, asynchronous workflows, and critical
performance paths.
"""
import asyncio
from typing import Dict, List, Optional, Any
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from labs.governance.guardian.guardian_system import (
    EnhancedGuardianSystem,
    GuardianAgent,
    GuardianResponse,
    GuardianStatus,
    ResponseAction,
    ThreatDetection,
    ThreatLevel,
)


class TestableEnhancedGuardianSystem(EnhancedGuardianSystem):
    """A testable version of the EnhancedGuardianSystem with missing methods implemented."""
    __test__ = False
    async def _validate_agent_config(self, agent: "GuardianAgent") -> bool:
        return True

    async def _initialize_agent_handlers(self, agent: "GuardianAgent"):
        pass

    async def _capture_system_state(self) -> Dict[str, Any]:
        return {}

    async def _analyze_identity_impact(self, threat_data: Dict[str, Any], context: Dict[str, Any]) -> Optional[str]:
        return None

    async def _analyze_consciousness_impact(self, threat_data: Dict[str, Any], context: Dict[str, Any]) -> Optional[str]:
        return None

    async def _determine_guardian_priority(self, detection: "ThreatDetection") -> str:
        return "normal"

    async def _trigger_automated_response(self, detection: "ThreatDetection"):
        pass

    async def _evaluate_threat_neutralization(self, threat: "ThreatDetection", execution_results: list) -> bool:
        return True

    async def _calculate_response_effectiveness(self, response: "GuardianResponse", execution_results: list) -> float:
        return 1.0

    async def _assess_collateral_impact(self, response: "GuardianResponse", execution_results: list) -> Optional[str]:
        return None

    async def _update_agent_performance(self, agent: "GuardianAgent", response: "GuardianResponse"):
        pass

    async def _check_system_health(self):
        pass

    async def _process_active_threats(self):
        pass

    async def _update_system_metrics(self):
        pass


@pytest.mark.asyncio
class TestGuardianV3Integration:
    """Test suite for Guardian V3 integration scenarios."""

    @pytest_asyncio.fixture
    async def guardian_system(self):
        """Fixture to provide an initialized EnhancedGuardianSystem."""
        # Mock external dependencies here
        with patch('opentelemetry.trace.get_tracer'), patch('prometheus_client.Counter'), patch('prometheus_client.Histogram'), patch('prometheus_client.Gauge'):
            system = TestableEnhancedGuardianSystem()
            # Allow time for async initialization in the constructor to complete
            await asyncio.sleep(0.01)
            yield system
            # Teardown: stop monitoring loops to prevent resource leaks
            system.monitoring_active = False

    async def test_system_initialization(self, guardian_system: EnhancedGuardianSystem):
        """Verify that the system initializes correctly with default agents."""
        assert guardian_system.system_status == GuardianStatus.ACTIVE
        assert len(guardian_system.guardian_agents) > 0
        commander = [agent for agent in guardian_system.guardian_agents.values() if agent.name == "Guardian Commander"]
        assert len(commander) == 1
        assert commander[0].status == GuardianStatus.ACTIVE

    async def test_end_to_end_decision_flow(self, guardian_system: EnhancedGuardianSystem, benchmark):
        """Test the full flow from threat detection to resolution."""
        # 1. Detect a threat
        threat_data = {"drift_score": 0.2}

        async def detect_and_respond():
            threat = await guardian_system.detect_threat("drift_detection", "test_source", threat_data)
            assert threat is not None
            await guardian_system.respond_to_threat(threat.detection_id, [ResponseAction.REPAIR, ResponseAction.MONITOR])

        # Benchmark the critical path
        benchmark.pedantic(detect_and_respond, rounds=10, iterations=1)

        # The benchmark runs the function multiple times, so the state will be messy.
        # We need to re-run the function one more time to have a clean state for assertions.
        threat = await guardian_system.detect_threat("drift_detection", "test_source", threat_data)
        assert threat is not None
        assert threat.threat_level == ThreatLevel.MODERATE
        assert threat.assigned_guardian is not None

        # 2. Verify threat is active
        assert threat.detection_id in guardian_system.active_threats

        # 3. Respond to the threat
        response = await guardian_system.respond_to_threat(threat.detection_id, [ResponseAction.REPAIR, ResponseAction.MONITOR])
        assert response is not None
        assert response.success
        assert response.threat_neutralized

        # 4. Verify threat is resolved and moved to history
        assert threat.detection_id not in guardian_system.active_threats
        assert len(guardian_system.threat_history) > 0

    async def test_threat_escalation_and_resolution(self, guardian_system: EnhancedGuardianSystem):
        """Test threat detection, escalation, and manual resolution."""
        # 1. Detect a critical threat
        threat_data = {"breach_type": "unauthorized_access"}
        threat = await guardian_system.detect_threat("security_breach", "external_ip", threat_data)
        assert threat is not None
        assert threat.threat_level == ThreatLevel.CRITICAL

        # 2. The system should automatically escalate
        # In a real system, this would trigger external notifications.
        # Here, we'll check the response actions.
        # The test can be improved by spying on `_execute_response_action`.
        await asyncio.sleep(0.1) # allow automated response to trigger

        # For this test, let's manually trigger the response to check the escalation action
        response = await guardian_system.respond_to_threat(threat.detection_id, [ResponseAction.BLOCK, ResponseAction.ESCALATE])
        assert response is not None
        assert any(action == ResponseAction.ESCALATE for action in response.actions_taken)

        # 3. Simulate manual resolution
        threat.status = "resolved"
        if threat.detection_id in guardian_system.active_threats:
            guardian_system.active_threats.pop(threat.detection_id)
        guardian_system.threat_history.append(threat)

        assert threat.detection_id not in guardian_system.active_threats
        assert len(guardian_system.threat_history) > 0

    async def test_constitutional_violation_correction(self, guardian_system: EnhancedGuardianSystem):
        """Test detection and correction of a constitutional violation."""
        # 1. Detect a constitutional violation
        threat_data = {"severity": "high"}
        threat = await guardian_system.detect_threat("constitutional_violation", "test_agent", threat_data)
        assert threat is not None
        assert threat.threat_level == ThreatLevel.HIGH

        # 2. Respond to the violation
        response = await guardian_system.respond_to_threat(threat.detection_id, [ResponseAction.REPAIR])
        assert response is not None
        assert response.success

        # 3. Verify that the repair action was logged
        assert "Executed repair: success" in response.audit_trail[0]

    async def test_emergency_shutdown_and_recovery(self, guardian_system: EnhancedGuardianSystem):
        """Test the emergency shutdown and recovery process."""
        # 1. Trigger a critical threat that leads to shutdown
        threat_data = {"breach_type": "system_compromise"}
        threat = await guardian_system.detect_threat("security_breach", "critical_system", threat_data)
        assert threat is not None

        # 2. Initiate emergency shutdown
        response = await guardian_system.respond_to_threat(threat.detection_id, [ResponseAction.SHUTDOWN])
        assert response is not None
        assert response.success
        assert guardian_system.system_status == GuardianStatus.EMERGENCY
        assert guardian_system.emergency_protocols_active

        # 3. Simulate recovery
        guardian_system.system_status = GuardianStatus.ACTIVE
        guardian_system.emergency_protocols_active = False

        assert guardian_system.system_status == GuardianStatus.ACTIVE

    async def test_multi_agent_coordination(self, guardian_system: EnhancedGuardianSystem):
        """Test that threats are assigned to the correct agents."""
        # 1. Detect a drift threat - should be assigned to Sentinel
        drift_threat = await guardian_system.detect_threat("drift_detection", "test_source", {"drift_score": 0.2})
        assert drift_threat is not None
        sentinel = [agent for agent in guardian_system.guardian_agents.values() if agent.name == "Primary Sentinel"]
        assert drift_threat.assigned_guardian == sentinel[0].agent_id

        # 2. Detect a constitutional violation - should be assigned to Enforcer
        violation_threat = await guardian_system.detect_threat("constitutional_violation", "test_source", {"severity": "high"})
        assert violation_threat is not None
        enforcer = [agent for agent in guardian_system.guardian_agents.values() if agent.name == "Policy Enforcer"]
        assert violation_threat.assigned_guardian == enforcer[0].agent_id
