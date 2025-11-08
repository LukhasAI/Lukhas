import asyncio
import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, patch

import pytest
from freezegun import freeze_time

from labs.governance.guardian.guardian_system import (
    EnhancedGuardianSystem,
    GuardianAgent,
    GuardianResponse,
    GuardianRole,
    GuardianStatus,
    ResponseAction,
    ThreatDetection,
    ThreatLevel,
)


@pytest.fixture
def guardian_system():
    """Fixture to provide a clean EnhancedGuardianSystem instance for each test, without starting background tasks."""
    system = EnhancedGuardianSystem()
    system.monitoring_active = False  # Ensure loops don't run
    return system


@pytest.mark.asyncio
class TestEnhancedGuardianSystemAgentManagement:
    """Test suite for agent management in the EnhancedGuardianSystem."""

    async def test_initialize_registers_default_agents(self, guardian_system: EnhancedGuardianSystem):
        """Test that the initialize method registers default agents."""
        with patch.object(
            guardian_system, "register_guardian_agent", new_callable=AsyncMock
        ) as mock_register:
            # Mock the internal methods that would be called by register_guardian_agent
            mock_register.return_value = True
            guardian_system._validate_agent_config = AsyncMock(return_value=True)
            guardian_system._initialize_agent_handlers = AsyncMock()
            await guardian_system.initialize()
            assert mock_register.call_count == 4  # Four default agents

    async def test_register_guardian_agent_success(
        self, guardian_system: EnhancedGuardianSystem
    ):
        """Test successful registration of a new Guardian agent."""
        agent = GuardianAgent(
            agent_id="test_agent_001",
            name="Test Agent",
            role=GuardianRole.SENTINEL,
            status=GuardianStatus.ACTIVE,
        )
        guardian_system._validate_agent_config = AsyncMock(return_value=True)
        guardian_system._initialize_agent_handlers = AsyncMock()

        result = await guardian_system.register_guardian_agent(agent)

        assert result is True
        assert "test_agent_001" in guardian_system.guardian_agents
        assert guardian_system.guardian_agents["test_agent_001"] == agent
        guardian_system._initialize_agent_handlers.assert_awaited_once_with(agent)

    async def test_register_guardian_agent_invalid_config(
        self, guardian_system: EnhancedGuardianSystem
    ):
        """Test that agent registration fails with an invalid configuration."""
        agent = GuardianAgent(
            agent_id="invalid_agent_001",
            name="Invalid Agent",
            role=GuardianRole.SCOUT,
            status=GuardianStatus.ACTIVE,
        )
        guardian_system._validate_agent_config = AsyncMock(return_value=False)

        result = await guardian_system.register_guardian_agent(agent)

        assert result is False
        assert "invalid_agent_001" not in guardian_system.guardian_agents

    async def test_register_guardian_agent_exception_handling(
        self, guardian_system: EnhancedGuardianSystem
    ):
        """Test that exceptions during agent registration are handled gracefully."""
        agent = GuardianAgent(
            agent_id="exception_agent_001",
            name="Exception Agent",
            role=GuardianRole.COMMANDER,
            status=GuardianStatus.ACTIVE,
        )
        guardian_system._validate_agent_config = AsyncMock(
            side_effect=Exception("Test Exception")
        )

        result = await guardian_system.register_guardian_agent(agent)

        assert result is False
        assert "exception_agent_001" not in guardian_system.guardian_agents

    @freeze_time("2025-11-07 21:00:00")
    async def test_agent_lifecycle_status_changes(
        self, guardian_system: EnhancedGuardianSystem
    ):
        """Test agent status changes from active to warning to offline."""
        agent = GuardianAgent(
            agent_id="lifecycle_agent_001",
            name="Lifecycle Agent",
            role=GuardianRole.HEALER,
            status=GuardianStatus.ACTIVE,
            last_heartbeat=datetime.now(timezone.utc),
        )
        guardian_system.guardian_agents[agent.agent_id] = agent
        guardian_system.monitoring_active = True

        assert agent.status == GuardianStatus.ACTIVE

        with freeze_time("2025-11-07 21:01:01"):
            with patch("asyncio.sleep", side_effect=asyncio.CancelledError):
                with pytest.raises(asyncio.CancelledError):
                    await guardian_system._health_check_loop()
            assert agent.status == GuardianStatus.WARNING

        with freeze_time("2025-11-07 21:05:01"):
            guardian_system.monitoring_active = True
            with patch("asyncio.sleep", side_effect=asyncio.CancelledError):
                with pytest.raises(asyncio.CancelledError):
                    await guardian_system._health_check_loop()
            assert agent.status == GuardianStatus.OFFLINE

    async def test_swarm_coordination_assigns_threat_to_best_agent(
        self, guardian_system: EnhancedGuardianSystem
    ):
        """Test that threats are assigned to the most appropriate agent."""
        sentinel = GuardianAgent(
            agent_id="sentinel_001",
            name="Sentinel Agent",
            role=GuardianRole.SENTINEL,
            status=GuardianStatus.ACTIVE,
            capabilities=["drift_detection"],
            specializations=["pattern_analysis"],
        )
        enforcer = GuardianAgent(
            agent_id="enforcer_001",
            name="Enforcer Agent",
            role=GuardianRole.ENFORCER,
            status=GuardianStatus.ACTIVE,
            capabilities=["policy_enforcement"],
            specializations=["constitutional_ai"],
        )
        guardian_system.guardian_agents = {"s_001": sentinel, "e_001": enforcer}

        drift_threat = ThreatDetection(
            detection_id="d_001",
            detected_at=datetime.now(timezone.utc),
            threat_type="drift_detection",
            threat_level=ThreatLevel.HIGH,
            threat_score=0.8,
            source="test",
        )
        const_threat = ThreatDetection(
            detection_id="c_001",
            detected_at=datetime.now(timezone.utc),
            threat_type="constitutional_violation",
            threat_level=ThreatLevel.CRITICAL,
            threat_score=0.9,
            source="test",
        )

        assert (await guardian_system._assign_threat_to_agent(drift_threat)).agent_id == "sentinel_001"
        assert (await guardian_system._assign_threat_to_agent(const_threat)).agent_id == "enforcer_001"

    async def test_assign_threat_no_agent_available(
        self, guardian_system: EnhancedGuardianSystem
    ):
        """Test that no agent is assigned when no active agents are available."""
        guardian_system.guardian_agents["offline"] = GuardianAgent(
            agent_id="offline", name="Offline", role=GuardianRole.SENTINEL, status=GuardianStatus.OFFLINE
        )
        threat = ThreatDetection(
            detection_id="t_001",
            detected_at=datetime.now(timezone.utc),
            threat_type="test",
            threat_level=ThreatLevel.LOW,
            threat_score=0.1,
            source="test",
        )
        assert await guardian_system._assign_threat_to_agent(threat) is None


@pytest.mark.asyncio
class TestGuardianThreatFlow:
    """Tests for the full threat detection and response flow."""

    async def test_detect_threat_full_flow(self, guardian_system: EnhancedGuardianSystem):
        """Test that detect_threat correctly assigns a threat and updates state."""
        agent = GuardianAgent(
            agent_id="sentinel_001", name="Sentinel", role=GuardianRole.SENTINEL, status=GuardianStatus.ACTIVE
        )
        guardian_system.guardian_agents[agent.agent_id] = agent

        # Mock external analysis and placeholder methods
        guardian_system._capture_system_state = AsyncMock(return_value={})
        guardian_system._analyze_identity_impact = AsyncMock(return_value=None)
        guardian_system._analyze_consciousness_impact = AsyncMock(return_value=None)
        guardian_system._determine_guardian_priority = AsyncMock(return_value="high")
        guardian_system._trigger_automated_response = AsyncMock()

        threat = await guardian_system.detect_threat(
            "security_breach", "source_ip", {"breach_type": "unauthorized_access"}
        )

        assert threat is not None
        assert threat.detection_id in guardian_system.active_threats
        assert threat.assigned_guardian == "sentinel_001"
        assert agent.threats_detected == 1
        guardian_system._trigger_automated_response.assert_awaited_once_with(threat)

    async def test_detect_threat_handles_exception(self, guardian_system: EnhancedGuardianSystem):
        """Test that detect_threat handles exceptions gracefully."""
        guardian_system._analyze_threat = AsyncMock(side_effect=Exception("Analysis failed"))
        threat = await guardian_system.detect_threat("test", "test", {})
        assert threat is None
        assert not guardian_system.active_threats

    async def test_respond_to_threat_happy_path(self, guardian_system: EnhancedGuardianSystem):
        """Test the happy path for responding to a threat."""
        agent = GuardianAgent(
            agent_id="h_001", name="Healer", role=GuardianRole.HEALER, status=GuardianStatus.ACTIVE
        )
        threat = ThreatDetection(
            detection_id="t_001",
            detected_at=datetime.now(timezone.utc),
            threat_type="test",
            threat_level=ThreatLevel.HIGH,
            threat_score=0.8,
            source="test",
            assigned_guardian="h_001",
        )
        guardian_system.guardian_agents[agent.agent_id] = agent
        guardian_system.active_threats[threat.detection_id] = threat

        # Mock internal methods that are not yet implemented
        guardian_system._execute_response_action = AsyncMock(
            return_value={"success": True, "status": "ok"}
        )
        guardian_system._evaluate_threat_neutralization = AsyncMock(return_value=True)
        guardian_system._calculate_response_effectiveness = AsyncMock(return_value=0.95)
        guardian_system._assess_collateral_impact = AsyncMock(return_value=None)
        guardian_system._update_agent_performance = AsyncMock()

        response = await guardian_system.respond_to_threat("t_001", [ResponseAction.REPAIR])

        assert response is not None
        assert response.success is True
        assert response.threat_neutralized is True
        assert "t_001" not in guardian_system.active_threats
        assert len(guardian_system.threat_history) == 1
        assert agent.threats_resolved == 1
        guardian_system._update_agent_performance.assert_awaited_once()

    async def test_respond_to_threat_not_found(self, guardian_system: EnhancedGuardianSystem):
        """Test responding to a non-existent threat returns None."""
        assert await guardian_system.respond_to_threat("fake_id", []) is None

    async def test_respond_to_threat_no_valid_agent(self, guardian_system: EnhancedGuardianSystem):
        """Test responding with no valid agent returns None."""
        threat = ThreatDetection(
            detection_id="t_001",
            detected_at=datetime.now(timezone.utc),
            threat_type="test",
            threat_level=ThreatLevel.HIGH,
            threat_score=0.8,
            source="test",
            assigned_guardian="fake_agent",
        )
        guardian_system.active_threats[threat.detection_id] = threat
        assert await guardian_system.respond_to_threat("t_001", []) is None

    async def test_respond_to_threat_exception_handling(
        self, guardian_system: EnhancedGuardianSystem
    ):
        """Test exception handling during threat response."""
        agent = GuardianAgent(
            agent_id="e_001", name="Enforcer", role=GuardianRole.ENFORCER, status=GuardianStatus.ACTIVE
        )
        threat = ThreatDetection(
            detection_id="t_001",
            detected_at=datetime.now(timezone.utc),
            threat_type="test",
            threat_level=ThreatLevel.HIGH,
            threat_score=0.8,
            source="test",
            assigned_guardian="e_001",
        )
        guardian_system.guardian_agents[agent.agent_id] = agent
        guardian_system.active_threats[threat.detection_id] = threat
        guardian_system._execute_response_action = AsyncMock(
            side_effect=Exception("Response failed")
        )
        assert await guardian_system.respond_to_threat("t_001", []) is None

@pytest.mark.asyncio
class TestGuardianResponseActions:
    """Tests for the private response action helper methods."""

    @pytest.fixture
    def setup_for_action(self, guardian_system):
        agent = GuardianAgent(agent_id="a_001", name="Test Agent", role=GuardianRole.GUARDIAN, status=GuardianStatus.ACTIVE)
        threat = ThreatDetection(
            detection_id="t_001", threat_type="test", threat_level=ThreatLevel.LOW,
            threat_score=0.2, source="test", detected_at=datetime.now(timezone.utc)
        )
        response = GuardianResponse(response_id="r_001", threat_id="t_001", responding_agent="a_001", actions_taken=[], started_at=datetime.now(timezone.utc))
        return guardian_system, agent, threat, response

    async def test_all_response_actions(self, setup_for_action):
        """Test all response action helpers for successful execution."""
        system, agent, threat, response = setup_for_action

        actions_to_test = {
            ResponseAction.MONITOR: system._enhance_monitoring,
            ResponseAction.ALERT: system._generate_alerts,
            ResponseAction.BLOCK: system._block_operation,
            ResponseAction.QUARANTINE: system._quarantine_source,
            ResponseAction.SHUTDOWN: system._emergency_shutdown,
            ResponseAction.REPAIR: system._initiate_repairs,
            ResponseAction.ESCALATE: system._escalate_to_humans,
        }

        for action, method in actions_to_test.items():
            result = await system._execute_response_action(action, threat, agent, response)
            assert result["success"] is True, f"Action {action} failed"

        # Test unknown action
        result = await system._execute_response_action("unknown", threat, agent, response)
        assert result["success"] is False


@pytest.mark.asyncio
class TestGuardianStatusAndMetrics:
    """Tests for system status and metrics reporting."""

    async def test_get_system_status(self, guardian_system: EnhancedGuardianSystem):
        """Test getting the system status report."""
        agent = GuardianAgent(
            agent_id="a_001", name="Agent", role=GuardianRole.GUARDIAN, status=GuardianStatus.ACTIVE
        )
        guardian_system.guardian_agents[agent.agent_id] = agent
        guardian_system.active_threats["t_001"] = ThreatDetection(
            detection_id="t_001", threat_type="test", threat_level=ThreatLevel.LOW,
            threat_score=0.1, source="test", detected_at=datetime.now(timezone.utc)
        )

        status = await guardian_system.get_system_status()

        assert status["system_status"] == "active"
        assert status["guardian_agents"]["total"] == 1
        assert status["guardian_agents"]["active"] == 1
        assert status["threats"]["active"] == 1

    async def test_get_system_metrics(self, guardian_system: EnhancedGuardianSystem):
        """Test getting system metrics."""
        guardian_system.metrics["total_threats_detected"] = 42
        metrics = await guardian_system.get_system_metrics()
        assert metrics["total_threats_detected"] == 42


@pytest.mark.asyncio
class TestGuardianAdvancedLogic:
    """Tests for advanced logic and edge cases to reach 100% coverage."""

    @pytest.mark.parametrize(
        "threat_type, threat_data, context, expected_level, expected_base_score, expected_score_increase",
        [
            ("drift_detection", {"drift_score": 0.1}, {}, ThreatLevel.LOW, 0.1, 0),
            ("drift_detection", {"drift_score": 0.2}, {"user_count": 101}, ThreatLevel.MODERATE, 0.2, 0.1),
            ("drift_detection", {"drift_score": 0.4}, {"critical_system": True}, ThreatLevel.HIGH, 0.4, 0.2),
            ("constitutional_violation", {"severity": "low"}, {}, ThreatLevel.MODERATE, 0.4, 0),
            ("constitutional_violation", {"severity": "high"}, {}, ThreatLevel.HIGH, 0.9, 0),
            ("anomaly_detection", {"anomaly_score": 0.5}, {}, ThreatLevel.MODERATE, 0.5, 0),
            ("anomaly_detection", {"anomaly_score": 0.9}, {}, ThreatLevel.HIGH, 0.9, 0),
            ("unknown_threat", {}, {}, ThreatLevel.MODERATE, 0.3, 0),
        ],
    )
    async def test_analyze_threat_variants(
        self, guardian_system: EnhancedGuardianSystem, threat_type, threat_data, context, expected_level, expected_base_score, expected_score_increase
    ):
        """Test all branches of the _analyze_threat method."""
        analysis = await guardian_system._analyze_threat(threat_type, threat_data, context)
        assert analysis["level"] == expected_level
        assert analysis["score"] == min(1.0, expected_base_score + expected_score_increase)

    async def test_assign_threat_with_performance_and_load(
        self, guardian_system: EnhancedGuardianSystem
    ):
        """Test agent assignment considers performance and current load."""
        good_agent = GuardianAgent(agent_id="good", name="Good", role=GuardianRole.GUARDIAN, status=GuardianStatus.ACTIVE, threats_detected=10, threats_resolved=9)
        new_agent = GuardianAgent(agent_id="new", name="New", role=GuardianRole.GUARDIAN, status=GuardianStatus.ACTIVE)

        guardian_system.guardian_agents = {a.agent_id: a for a in [good_agent, new_agent]}

        threat = ThreatDetection(
            detection_id="t_new", threat_type="security_breach", threat_level=ThreatLevel.HIGH,
            threat_score=0.8, source="test", detected_at=datetime.now(timezone.utc)
        )

        assigned = await guardian_system._assign_threat_to_agent(threat)
        assert assigned.agent_id == "good"

    async def test_monitoring_loop_exception(self, guardian_system: EnhancedGuardianSystem):
        """Test exception handling in the monitoring loops."""
        guardian_system.monitoring_active = True
        guardian_system._check_system_health = AsyncMock(side_effect=Exception("Loop Error"))

        with patch("asyncio.sleep", side_effect=asyncio.CancelledError):
            with pytest.raises(asyncio.CancelledError):
                await guardian_system._monitoring_loop()
        # No assertion needed, just need to cover the except block

    async def test_calculate_system_drift_no_agents(self, guardian_system: EnhancedGuardianSystem):
        """Test drift calculation with no agents."""
        assert await guardian_system._calculate_system_drift() == 0.0

    async def test_respond_to_threat_not_neutralized(self, guardian_system: EnhancedGuardianSystem):
        """Test response flow where threat is not neutralized."""
        agent = GuardianAgent(agent_id="a_001", name="Agent", role=GuardianRole.ENFORCER, status=GuardianStatus.ACTIVE)
        threat = ThreatDetection(
            detection_id="t_001", threat_type="test", threat_level=ThreatLevel.HIGH,
            threat_score=0.8, source="test", assigned_guardian="a_001",
            detected_at=datetime.now(timezone.utc)
        )
        guardian_system.guardian_agents[agent.agent_id] = agent
        guardian_system.active_threats[threat.detection_id] = threat

        guardian_system._execute_response_action = AsyncMock(return_value={"success": True, "status": "ok"})
        guardian_system._evaluate_threat_neutralization = AsyncMock(return_value=False) # Not neutralized
        guardian_system._calculate_response_effectiveness = AsyncMock(return_value=0.5)
        guardian_system._assess_collateral_impact = AsyncMock(return_value="High")
        guardian_system._update_agent_performance = AsyncMock()

        response = await guardian_system.respond_to_threat("t_001", [ResponseAction.BLOCK])

        assert response.threat_neutralized is False
        assert response.requires_human_review is True
        assert threat.status == "responding"

    async def test_get_system_status_empty(self, guardian_system: EnhancedGuardianSystem):
        """Test system status when no agents or threats are present."""
        status = await guardian_system.get_system_status()
        assert status["guardian_agents"]["total"] == 0
        assert status["threats"]["active"] == 0
