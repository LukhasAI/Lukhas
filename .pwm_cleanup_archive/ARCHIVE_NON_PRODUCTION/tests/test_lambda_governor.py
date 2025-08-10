"""
═══════════════════════════════════════════════════════════════════════════════════
📊 MODULE: tests.test_lambda_governor
📄 FILENAME: test_lambda_governor.py
🎯 PURPOSE: Test suite for ΛGOVERNOR - Global Ethical Arbitration Engine
🧠 CONTEXT: LUKHAS AGI Testing Framework - Governor Arbitration Unit Tests
🔮 CAPABILITY: Validation of risk arbitration, interventions, and mesh notifications
🛡️ ETHICS: Test ethical oversight, cascade prevention, override capabilities
🚀 VERSION: v1.0.0 • 📅 CREATED: 2025-07-22 • ✍️ AUTHOR: CLAUDE-CODE
💭 INTEGRATION: pytest, AsyncIO, Mock systems for governor testing
═══════════════════════════════════════════════════════════════════════════════════

🧪 ΛGOVERNOR TEST FRAMEWORK
────────────────────────────────────────────────────────────────────

Comprehensive test coverage for the ΛGOVERNOR global ethical arbitration engine,
validating risk evaluation, intervention authorization, mesh notifications, and
system-wide override capabilities for the LUKHAS AGI consciousness mesh.

LUKHAS_TAG: governor_testing, arbitration_validation, claude_code
"""

import asyncio
import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest

# Import the governor system
from ethics.governor.lambda_governor import (
    ActionDecision,
    ArbitrationResponse,
    EscalationPriority,
    EscalationSignal,
    EscalationSource,
    LambdaGovernor,
    create_escalation_signal,
    create_lambda_governor,
)


class TestLambdaGovernor:
    """Test suite for Lambda Governor."""

    @pytest.fixture
    async def governor(self):
        """Create a test governor instance."""
        governor = LambdaGovernor(
            response_timeout=1.0, escalation_retention=10, audit_log_retention=100
        )
        yield governor

    @pytest.fixture
    def mock_escalation_signal(self):
        """Create a mock escalation signal."""
        return EscalationSignal(
            signal_id="test_signal_001",
            timestamp=datetime.now(timezone.utc).isoformat(),
            source_module=EscalationSource.DRIFT_SENTINEL,
            priority=EscalationPriority.HIGH,
            triggering_metric="drift_score",
            drift_score=0.7,
            entropy=0.6,
            emotion_volatility=0.5,
            contradiction_density=0.4,
            memory_ids=["mem_001", "mem_002"],
            symbol_ids=["sym_001", "sym_002"],
            context={"test": True},
        )

    def test_governor_initialization(self, governor):
        """Test governor initialization and configuration."""
        assert governor.response_timeout == 1.0
        assert governor.escalation_retention == 10
        assert len(governor.active_escalations) == 0
        assert governor.safety_thresholds["entropy_quarantine"] == 0.85
        assert governor.safety_thresholds["emotion_freeze"] == 0.5
        assert governor.stats["total_escalations"] == 0

    async def test_receive_escalation_allow(self, governor, mock_escalation_signal):
        """Test escalation processing resulting in ALLOW decision."""
        # Adjust signal for low risk
        mock_escalation_signal.drift_score = 0.1
        mock_escalation_signal.entropy = 0.1
        mock_escalation_signal.emotion_volatility = 0.1
        mock_escalation_signal.contradiction_density = 0.1
        mock_escalation_signal.priority = EscalationPriority.LOW

        with patch.object(governor, "log_governor_action") as mock_log:
            with patch.object(governor, "notify_mesh") as mock_notify:
                response = await governor.receive_escalation(mock_escalation_signal)

        assert response.decision == ActionDecision.ALLOW
        assert response.signal_id == mock_escalation_signal.signal_id
        assert response.risk_score < 0.4
        assert mock_escalation_signal.signal_id in governor.active_escalations
        assert governor.stats["total_escalations"] == 1

    async def test_receive_escalation_freeze(self, governor, mock_escalation_signal):
        """Test escalation processing resulting in FREEZE decision."""
        # Adjust signal for moderate risk
        mock_escalation_signal.emotion_volatility = 0.6
        mock_escalation_signal.priority = EscalationPriority.MEDIUM

        with patch.object(governor, "log_governor_action") as mock_log:
            with patch.object(governor, "notify_mesh") as mock_notify:
                response = await governor.receive_escalation(mock_escalation_signal)

        assert response.decision in [ActionDecision.FREEZE, ActionDecision.QUARANTINE]
        assert "ΛINTERVENTION" in response.intervention_tags

    async def test_receive_escalation_quarantine(
        self, governor, mock_escalation_signal
    ):
        """Test escalation processing resulting in QUARANTINE decision."""
        # Adjust signal for high risk
        mock_escalation_signal.drift_score = 0.8
        mock_escalation_signal.entropy = 0.9
        mock_escalation_signal.priority = EscalationPriority.HIGH

        with patch.object(governor, "log_governor_action") as mock_log:
            with patch.object(governor, "notify_mesh") as mock_notify:
                response = await governor.receive_escalation(mock_escalation_signal)

        assert response.decision in [
            ActionDecision.QUARANTINE,
            ActionDecision.RESTRUCTURE,
        ]
        assert response.quarantine_scope is not None
        assert response.rollback_plan is not None

    async def test_receive_escalation_shutdown(self, governor, mock_escalation_signal):
        """Test escalation processing resulting in SHUTDOWN decision."""
        # Adjust signal for critical risk
        mock_escalation_signal.drift_score = 0.95
        mock_escalation_signal.entropy = 0.95
        mock_escalation_signal.emotion_volatility = 0.9
        mock_escalation_signal.contradiction_density = 0.9
        mock_escalation_signal.priority = EscalationPriority.EMERGENCY

        with patch.object(governor, "log_governor_action") as mock_log:
            with patch.object(governor, "notify_mesh") as mock_notify:
                response = await governor.receive_escalation(mock_escalation_signal)

        assert response.decision == ActionDecision.SHUTDOWN
        assert "ΛEMERGENCY_PROTOCOL" in response.intervention_tags
        assert response.quarantine_scope["isolation_level"] == "full"

    async def test_evaluate_risk_calculation(self, governor, mock_escalation_signal):
        """Test composite risk score evaluation."""
        risk_score = await governor.evaluate_risk(mock_escalation_signal)

        # Verify risk score is reasonable
        assert 0.0 <= risk_score <= 1.0

        # Test with historical escalations
        governor.escalation_history.append(mock_escalation_signal)
        governor.escalation_history.append(mock_escalation_signal)

        risk_score_with_history = await governor.evaluate_risk(mock_escalation_signal)
        assert risk_score_with_history > risk_score  # History should increase risk

    async def test_evaluate_risk_with_state_factors(
        self, governor, mock_escalation_signal
    ):
        """Test risk evaluation with system state factors."""
        # Add symbols to quarantine/frozen states
        governor.quarantined_symbols.add("sym_001")
        governor.frozen_systems.add("sym_002")

        risk_score = await governor.evaluate_risk(mock_escalation_signal)
        assert risk_score > 0.5  # State factors should increase risk

    async def test_authorize_action_thresholds(self, governor):
        """Test action authorization based on thresholds."""
        # Test entropy threshold
        decision = await governor.authorize_action(0.86, {"entropy": 0.86})
        assert decision == ActionDecision.QUARANTINE

        # Test emotion threshold
        decision = await governor.authorize_action(0.5, {"emotion_volatility": 0.6})
        assert decision == ActionDecision.FREEZE

        # Test drift cascade threshold
        decision = await governor.authorize_action(0.65, {"drift_score": 0.65})
        assert decision == ActionDecision.QUARANTINE

        # Test emergency shutdown
        decision = await governor.authorize_action(0.95, {})
        assert decision == ActionDecision.SHUTDOWN

    async def test_log_governor_action(
        self, governor, mock_escalation_signal, tmp_path
    ):
        """Test audit logging functionality."""
        # Use temporary log path
        governor.audit_log_path = tmp_path / "test_governor.jsonl"

        response = ArbitrationResponse(
            response_id="test_response",
            signal_id=mock_escalation_signal.signal_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            decision=ActionDecision.QUARANTINE,
            confidence=0.8,
            risk_score=0.7,
            intervention_tags=["ΛTEST"],
            reasoning="Test reasoning",
            affected_symbols=["sym_001"],
        )

        await governor.log_governor_action(mock_escalation_signal, response)

        # Verify log file was written
        assert governor.audit_log_path.exists()

        # Verify log content
        with open(governor.audit_log_path) as f:
            log_entry = json.loads(f.read().strip())
            assert log_entry["type"] == "governor_arbitration"
            assert "ΛGOVERNOR" in log_entry["ΛTAG"]
            assert "ΛQUARANTINE" in log_entry["ΛTAG"]
            assert log_entry["arbitration"]["decision"] == "QUARANTINE"

    async def test_notify_mesh(self, governor, mock_escalation_signal):
        """Test mesh notification system."""
        # Create mock mesh components
        mock_router = AsyncMock()
        mock_coordinator = AsyncMock()
        mock_manager = AsyncMock()
        mock_callback = AsyncMock()

        governor.register_mesh_router(mock_router)
        governor.register_dream_coordinator(mock_coordinator)
        governor.register_memory_manager(mock_manager)
        governor.register_subsystem_callback("test_subsystem", mock_callback)

        response = ArbitrationResponse(
            response_id="test_response",
            signal_id=mock_escalation_signal.signal_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            decision=ActionDecision.QUARANTINE,
            confidence=0.8,
            risk_score=0.7,
            intervention_tags=[],
            reasoning="Test",
            affected_symbols=["sym_001"],
            quarantine_scope={"test": True},
        )

        await governor.notify_mesh(mock_escalation_signal, response)

        # Verify notifications sent
        mock_router.receive_governor_notification.assert_called_once()
        mock_coordinator.receive_intervention_notice.assert_called_once()
        mock_manager.execute_quarantine.assert_called_once()
        mock_callback.assert_called_once()

        # Verify notification content
        notification = mock_router.receive_governor_notification.call_args[0][0]
        assert notification["source"] == "ΛGOVERNOR"
        assert notification["decision"] == "QUARANTINE"

    async def test_intervention_execution_freeze(self, governor):
        """Test freeze intervention execution."""
        response = ArbitrationResponse(
            response_id="test_response",
            signal_id="test_signal",
            timestamp=datetime.now(timezone.utc).isoformat(),
            decision=ActionDecision.FREEZE,
            confidence=0.8,
            risk_score=0.5,
            intervention_tags=[],
            reasoning="Test",
            affected_symbols=["sym_001", "sym_002"],
        )

        execution = await governor._execute_intervention(response)

        assert execution.execution_status == "completed"
        assert "sym_001" in governor.frozen_systems
        assert "sym_002" in governor.frozen_systems
        assert len(execution.affected_systems) == 2
        assert governor.stats["interventions_executed"] == 1
        assert governor.stats["successful_interventions"] == 1

    async def test_intervention_execution_quarantine(self, governor):
        """Test quarantine intervention execution."""
        response = ArbitrationResponse(
            response_id="test_response",
            signal_id="test_signal",
            timestamp=datetime.now(timezone.utc).isoformat(),
            decision=ActionDecision.QUARANTINE,
            confidence=0.8,
            risk_score=0.7,
            intervention_tags=[],
            reasoning="Test",
            affected_symbols=["sym_001"],
        )

        execution = await governor._execute_intervention(response)

        assert execution.execution_status == "completed"
        assert "sym_001" in governor.quarantined_symbols

    async def test_intervention_execution_failure(self, governor):
        """Test intervention execution failure handling."""
        response = ArbitrationResponse(
            response_id="test_response",
            signal_id="test_signal",
            timestamp=datetime.now(timezone.utc).isoformat(),
            decision=ActionDecision.RESTRUCTURE,
            confidence=0.8,
            risk_score=0.8,
            intervention_tags=[],
            reasoning="Test",
            affected_symbols=["sym_001"],
        )

        # Mock execution failure
        with patch.object(
            governor, "_execute_restructure", side_effect=Exception("Test error")
        ):
            execution = await governor._execute_intervention(response)

        assert execution.execution_status == "failed"
        assert governor.stats["interventions_executed"] == 1
        assert governor.stats["successful_interventions"] == 0

    def test_calculate_decision_confidence(self, governor, mock_escalation_signal):
        """Test decision confidence calculation."""
        # High risk score - high confidence
        confidence = governor._calculate_decision_confidence(
            mock_escalation_signal, 0.9
        )
        assert confidence > 0.5

        # Moderate risk - lower confidence
        confidence = governor._calculate_decision_confidence(
            mock_escalation_signal, 0.5
        )
        assert confidence < 0.8

        # Missing data - reduced confidence
        incomplete_signal = mock_escalation_signal
        incomplete_signal.symbol_ids = []
        incomplete_signal.memory_ids = []
        confidence = governor._calculate_decision_confidence(incomplete_signal, 0.7)
        assert confidence < 0.7

    def test_generate_intervention_tags(self, governor, mock_escalation_signal):
        """Test intervention tag generation."""
        tags = governor._generate_intervention_tags(
            mock_escalation_signal, ActionDecision.FREEZE
        )
        assert "ΛINTERVENTION" in tags
        assert "ΛFREEZE_AUTHORIZED" in tags
        assert "ΛDRIFT_INTERVENTION" in tags

        tags = governor._generate_intervention_tags(
            mock_escalation_signal, ActionDecision.SHUTDOWN
        )
        assert "ΛSHUTDOWN_AUTHORIZED" in tags
        assert "ΛEMERGENCY_PROTOCOL" in tags

    def test_generate_reasoning(self, governor, mock_escalation_signal):
        """Test human-readable reasoning generation."""
        reasoning = governor._generate_reasoning(
            mock_escalation_signal, 0.8, ActionDecision.QUARANTINE
        )
        assert "Risk score 0.800" in reasoning
        assert "DRIFT_SENTINEL" in reasoning
        assert "requires memory isolation" in reasoning
        assert "high drift" in reasoning

    def test_determine_quarantine_scope(self, governor, mock_escalation_signal):
        """Test quarantine scope determination."""
        # Test quarantine scope
        scope = governor._determine_quarantine_scope(
            mock_escalation_signal, ActionDecision.QUARANTINE
        )
        assert scope is not None
        assert scope["isolation_level"] == "selective"
        assert scope["duration"] == "24h"

        # Test shutdown scope
        scope = governor._determine_quarantine_scope(
            mock_escalation_signal, ActionDecision.SHUTDOWN
        )
        assert scope["isolation_level"] == "full"
        assert scope["duration"] == "indefinite"

        # Test no scope for other decisions
        scope = governor._determine_quarantine_scope(
            mock_escalation_signal, ActionDecision.ALLOW
        )
        assert scope is None

    def test_create_rollback_plan(self, governor, mock_escalation_signal):
        """Test rollback plan creation."""
        # Test with intervention
        plan = governor._create_rollback_plan(
            mock_escalation_signal, ActionDecision.FREEZE
        )
        assert plan is not None
        assert plan["intervention_type"] == "FREEZE"
        assert len(plan["recovery_steps"]) == 4
        assert plan["conditions_for_rollback"]["manual_approval_required"] is False

        # Test shutdown requires manual approval
        plan = governor._create_rollback_plan(
            mock_escalation_signal, ActionDecision.SHUTDOWN
        )
        assert plan["conditions_for_rollback"]["manual_approval_required"] is True

        # Test no plan for ALLOW
        plan = governor._create_rollback_plan(
            mock_escalation_signal, ActionDecision.ALLOW
        )
        assert plan is None

    def test_get_governor_status(self, governor):
        """Test governor status reporting."""
        # Add some test data
        governor.stats["total_escalations"] = 10
        governor.stats["interventions_executed"] = 5
        governor.quarantined_symbols.add("sym_001")
        governor.frozen_systems.add("sym_002")

        status = governor.get_governor_status()

        assert status["status"] == "active"
        assert status["total_escalations"] == 10
        assert status["interventions_executed"] == 5
        assert status["system_state"]["quarantined_symbols"] == 1
        assert status["system_state"]["frozen_systems"] == 1
        assert "safety_thresholds" in status
        assert "timestamp" in status

    def test_update_stats(self, governor):
        """Test statistics updating."""
        governor._update_stats(ActionDecision.FREEZE, 0.5)
        assert governor.stats["decisions_by_type"]["FREEZE"] == 1
        assert governor.stats["average_response_time"] == 0.5

        governor._update_stats(ActionDecision.QUARANTINE, 0.7)
        assert governor.stats["decisions_by_type"]["QUARANTINE"] == 1
        assert governor.stats["average_response_time"] == pytest.approx(0.6, 0.01)

    async def test_emergency_response_on_failure(
        self, governor, mock_escalation_signal
    ):
        """Test emergency response when arbitration fails."""
        # Mock evaluation failure
        with patch.object(
            governor, "evaluate_risk", side_effect=Exception("Test failure")
        ):
            with patch.object(governor, "log_governor_action") as mock_log:
                with patch.object(governor, "notify_mesh") as mock_notify:
                    response = await governor.receive_escalation(mock_escalation_signal)

        assert response.decision == ActionDecision.FREEZE
        assert response.confidence == 0.0
        assert response.risk_score == 1.0
        assert "ΛEMERGENCY" in response.intervention_tags
        assert "Emergency response" in response.reasoning


class TestConvenienceFunctions:
    """Test convenience functions."""

    async def test_create_lambda_governor(self):
        """Test governor creation convenience function."""
        governor = await create_lambda_governor()
        assert isinstance(governor, LambdaGovernor)

    def test_create_escalation_signal(self):
        """Test escalation signal creation."""
        signal = create_escalation_signal(
            source_module=EscalationSource.DRIFT_SENTINEL,
            priority=EscalationPriority.HIGH,
            triggering_metric="drift_score",
            drift_score=0.7,
            entropy=0.6,
            emotion_volatility=0.5,
            contradiction_density=0.4,
            symbol_ids=["sym_001"],
        )

        assert signal.source_module == EscalationSource.DRIFT_SENTINEL
        assert signal.priority == EscalationPriority.HIGH
        assert signal.drift_score == 0.7
        assert len(signal.symbol_ids) == 1
        assert len(signal.memory_ids) == 0  # Default empty


class TestIntegrationScenarios:
    """Test integration scenarios."""

    async def test_cascade_prevention_scenario(self):
        """Test cascade prevention through governor intervention."""
        governor = LambdaGovernor()

        # Simulate multiple high-risk escalations
        signals = []
        for i in range(3):
            signal = create_escalation_signal(
                source_module=EscalationSource.DRIFT_SENTINEL,
                priority=EscalationPriority.CRITICAL,
                triggering_metric="cascade_risk",
                drift_score=0.8 + i * 0.05,
                entropy=0.85,
                emotion_volatility=0.7,
                contradiction_density=0.8,
                symbol_ids=[f"cascade_sym_{i}"],
            )
            signals.append(signal)

        # Process escalations
        responses = []
        with patch.object(governor, "log_governor_action") as mock_log:
            with patch.object(governor, "notify_mesh") as mock_notify:
                for signal in signals:
                    response = await governor.receive_escalation(signal)
                    responses.append(response)

        # Verify escalating interventions
        decisions = [r.decision for r in responses]
        assert (
            ActionDecision.QUARANTINE in decisions
            or ActionDecision.SHUTDOWN in decisions
        )

        # Verify system state tracking
        assert len(governor.active_escalations) == 3
        assert governor.stats["total_escalations"] == 3

    async def test_multi_source_arbitration(self):
        """Test arbitration with escalations from multiple sources."""
        governor = LambdaGovernor()

        sources = [
            EscalationSource.DRIFT_SENTINEL,
            EscalationSource.EMOTION_PROTOCOL,
            EscalationSource.CONFLICT_RESOLVER,
        ]

        responses = []
        with patch.object(governor, "log_governor_action") as mock_log:
            with patch.object(governor, "notify_mesh") as mock_notify:
                for source in sources:
                    signal = create_escalation_signal(
                        source_module=source,
                        priority=EscalationPriority.HIGH,
                        triggering_metric="multi_source_risk",
                        drift_score=0.6,
                        entropy=0.5,
                        emotion_volatility=0.6,
                        contradiction_density=0.5,
                        symbol_ids=["shared_symbol"],
                    )
                    response = await governor.receive_escalation(signal)
                    responses.append(response)

        # Verify all sources processed
        assert len(responses) == 3
        assert all(r.signal_id for r in responses)


# Performance testing
class TestGovernorPerformance:
    """Performance testing for the governor."""

    @pytest.mark.asyncio
    async def test_response_time_under_load(self):
        """Test governor response time under load."""
        governor = LambdaGovernor(response_timeout=0.1)

        # Create batch of escalations
        signals = []
        for i in range(10):
            signal = create_escalation_signal(
                source_module=EscalationSource.DRIFT_SENTINEL,
                priority=EscalationPriority.MEDIUM,
                triggering_metric="load_test",
                drift_score=0.5,
                entropy=0.5,
                emotion_volatility=0.5,
                contradiction_density=0.5,
                symbol_ids=[f"load_sym_{i}"],
            )
            signals.append(signal)

        # Process concurrently
        with patch.object(governor, "log_governor_action") as mock_log:
            with patch.object(governor, "notify_mesh") as mock_notify:
                tasks = [governor.receive_escalation(s) for s in signals]
                responses = await asyncio.gather(*tasks)

        # Verify all processed
        assert len(responses) == 10
        assert all(isinstance(r, ArbitrationResponse) for r in responses)

        # Check average response time
        assert governor.stats["average_response_time"] < 0.1  # Under timeout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


# CLAUDE CHANGELOG
# - Created comprehensive test suite for ΛGOVERNOR arbitration engine # CLAUDE_EDIT_v0.1
# - Implemented unit tests for all core arbitration functions # CLAUDE_EDIT_v0.1
# - Added integration tests for cascade prevention scenarios # CLAUDE_EDIT_v0.1
# - Created performance tests for concurrent escalation handling # CLAUDE_EDIT_v0.1
# - Added mock-based testing for mesh notification system # CLAUDE_EDIT_v0.1
# - Implemented edge case testing for emergency responses # CLAUDE_EDIT_v0.1
