"""
Unit tests for EnhancedGuardianSystem monitoring methods.
"""

import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

import sys
sys.modules['prometheus_client'] = MagicMock()


from labs.governance.guardian.guardian_system import (
    EnhancedGuardianSystem,
    GuardianAgent,
    GuardianRole,
    GuardianStatus,
    ThreatLevel,
    ResponseAction,
)


@pytest.mark.asyncio
class TestGuardianMonitoring:
    """Test suite for Guardian system monitoring loops and metrics."""

    @pytest.fixture
    def guardian_system(self, mocker):
        """
        Fixture to provide a clean EnhancedGuardianSystem instance for each test.
        It mocks all non-existent async methods on the class before instantiation.
        """
        mocker.patch('asyncio.create_task')

        # Patch all missing async methods on the class using create=True and AsyncMock
        mocker.patch.object(EnhancedGuardianSystem, '_validate_agent_config', new_callable=AsyncMock, return_value=True, create=True)
        mocker.patch.object(EnhancedGuardianSystem, '_initialize_agent_handlers', new_callable=AsyncMock, return_value=None, create=True)
        mocker.patch.object(EnhancedGuardianSystem, '_capture_system_state', new_callable=AsyncMock, return_value={}, create=True)
        mocker.patch.object(EnhancedGuardianSystem, '_analyze_identity_impact', new_callable=AsyncMock, return_value="low", create=True)
        mocker.patch.object(EnhancedGuardianSystem, '_analyze_consciousness_impact', new_callable=AsyncMock, return_value="none", create=True)
        mocker.patch.object(EnhancedGuardianSystem, '_determine_guardian_priority', new_callable=AsyncMock, return_value="normal", create=True)
        mocker.patch.object(EnhancedGuardianSystem, '_trigger_automated_response', new_callable=AsyncMock, return_value=None, create=True)
        mocker.patch.object(EnhancedGuardianSystem, '_evaluate_threat_neutralization', new_callable=AsyncMock, return_value=True, create=True)
        mocker.patch.object(EnhancedGuardianSystem, '_calculate_response_effectiveness', new_callable=AsyncMock, return_value=1.0, create=True)
        mocker.patch.object(EnhancedGuardianSystem, '_assess_collateral_impact', new_callable=AsyncMock, return_value="none", create=True)
        mocker.patch.object(EnhancedGuardianSystem, '_update_agent_performance', new_callable=AsyncMock, return_value=None, create=True)
        mocker.patch.object(EnhancedGuardianSystem, '_check_system_health', new_callable=AsyncMock, return_value=None, create=True)
        mocker.patch.object(EnhancedGuardianSystem, '_process_active_threats', new_callable=AsyncMock, return_value=None, create=True)
        mocker.patch.object(EnhancedGuardianSystem, '_update_system_metrics', new_callable=AsyncMock, return_value=None, create=True)

        system = EnhancedGuardianSystem()
        return system


    async def test_health_check_loop_updates_agent_status(self, guardian_system, mocker):
        """
        Tests that the health check loop correctly updates agent status.
        """
        mock_sleep = mocker.patch('asyncio.sleep', new_callable=AsyncMock)
        mock_datetime = mocker.patch('labs.governance.guardian.guardian_system.datetime', autospec=True)

        start_time = datetime.now(timezone.utc)
        first_check_time = start_time + timedelta(seconds=61)
        second_check_time = start_time + timedelta(seconds=301)

        mock_datetime.now.side_effect = [first_check_time, second_check_time]
        mock_datetime.timezone = timezone

        agent = GuardianAgent(
            agent_id="test_agent_001",
            name="Test Agent",
            role=GuardianRole.SENTINEL,
            status=GuardianStatus.ACTIVE,
            last_heartbeat=start_time
        )
        guardian_system.guardian_agents[agent.agent_id] = agent

        run_count = 0
        def side_effect_stop_loop(*args, **kwargs):
            nonlocal run_count
            run_count += 1
            if run_count >= 2:
                guardian_system.monitoring_active = False
        mock_sleep.side_effect = side_effect_stop_loop

        await guardian_system._health_check_loop()

        assert agent.status == GuardianStatus.OFFLINE

    async def test_drift_monitoring_loop_triggers_threat_detection(self, guardian_system, mocker):
        """
        Tests that the drift monitoring loop correctly detects drift.
        """
        mock_sleep = mocker.patch('asyncio.sleep', new_callable=AsyncMock)
        mock_detect_threat = mocker.patch.object(guardian_system, 'detect_threat', new_callable=AsyncMock)
        mocker.patch.object(guardian_system, '_calculate_system_drift', new_callable=AsyncMock, side_effect=[0.1, 0.2])
        guardian_system.drift_threshold = 0.15

        run_count = 0
        def side_effect_stop_loop(*args, **kwargs):
            nonlocal run_count
            if run_count == 0:
                mock_detect_threat.assert_not_called()
            if run_count >= 1:
                guardian_system.monitoring_active = False
            run_count += 1
        mock_sleep.side_effect = side_effect_stop_loop

        await guardian_system._drift_monitoring_loop()

        mock_detect_threat.assert_awaited_once()
        args, kwargs = mock_detect_threat.call_args
        assert args[0] == "drift_detection"
        assert args[2]['drift_score'] == 0.2

    async def test_metrics_collection_and_aggregation(self, guardian_system, mocker):
        """
        Tests that metrics are correctly collected and aggregated.
        """
        initial_metrics = await guardian_system.get_system_metrics()
        assert initial_metrics['total_threats_detected'] == 0

        mocker.patch.object(guardian_system, '_analyze_threat', return_value={"level": ThreatLevel.MODERATE, "score": 0.6, "recommended_actions": [ResponseAction.MONITOR]})
        mock_agent = GuardianAgent(agent_id='mock_agent', name='mock', role=GuardianRole.GUARDIAN, status=GuardianStatus.ACTIVE)
        mocker.patch.object(guardian_system, '_assign_threat_to_agent', return_value=mock_agent)
        guardian_system.guardian_agents['mock_agent'] = mock_agent

        mocker.patch.object(guardian_system, '_execute_response_action', new_callable=AsyncMock, return_value={"success": True, "status": "ok"})


        threat = await guardian_system.detect_threat("test_threat", "test_source", {})
        assert threat is not None

        metrics_after_detection = await guardian_system.get_system_metrics()
        assert metrics_after_detection['total_threats_detected'] == 1

        await guardian_system.respond_to_threat(threat.detection_id, actions=[ResponseAction.MONITOR])

        metrics_after_resolution = await guardian_system.get_system_metrics()
        assert metrics_after_resolution['total_threats_resolved'] == 1

    async def test_prometheus_style_metrics_validation(self, guardian_system):
        """
        Validates the structure and data types of the metrics dictionary.
        """
        metrics = await guardian_system.get_system_metrics()
        expected_keys = [
            "system_uptime", "total_threats_detected", "total_threats_resolved",
            "false_positive_rate", "average_response_time", "system_health_score"
        ]
        assert all(key in metrics for key in expected_keys)

    async def test_calculate_system_drift(self, guardian_system):
        """
        Tests the drift calculation logic.
        """
        drift = await guardian_system._calculate_system_drift()
        assert drift == 0.0

        agent = GuardianAgent(agent_id="ag1", name="A1", role=GuardianRole.SENTINEL, status=GuardianStatus.ACTIVE, threats_detected=10, threats_resolved=9)
        guardian_system.guardian_agents[agent.agent_id] = agent
        drift = await guardian_system._calculate_system_drift()
        assert drift == 0.0

    async def test_monitoring_loop(self, guardian_system, mocker):
        """
        Tests that the main monitoring loop calls its helper methods.
        """
        mock_sleep = mocker.patch('asyncio.sleep', new_callable=AsyncMock)
        mock_sleep.side_effect = lambda *args, **kwargs: setattr(guardian_system, 'monitoring_active', False)

        await guardian_system._monitoring_loop()

        guardian_system._check_system_health.assert_awaited_once()
        guardian_system._process_active_threats.assert_awaited_once()
        guardian_system._update_system_metrics.assert_awaited_once()

    async def test_initialization_of_guardian_system(self, mocker):
        """
        Tests that the __init__ and _initialize_guardian_system methods correctly
        set up the system.
        """
        mock_create_task = mocker.patch('asyncio.create_task', new_callable=AsyncMock)
        mocker.patch.object(EnhancedGuardianSystem, '_validate_agent_config', new_callable=AsyncMock, return_value=True, create=True)
        mocker.patch.object(EnhancedGuardianSystem, '_initialize_agent_handlers', new_callable=AsyncMock, return_value=None, create=True)

        system = EnhancedGuardianSystem()
        await system._initialize_guardian_system()

        assert len(system.guardian_agents) == 4
        assert mock_create_task.call_count == 4
