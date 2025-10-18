#!/usr/bin/env python3
"""
Test Guardian Drift Bands System
================================

Task 12: Comprehensive testing for Guardian Drift Bands including:
- Band transition logic with hysteresis
- Drift score calculation and mapping
- Ethics DSL integration
- Edge cases and error handling
- Performance validation

#TAG:ethics
#TAG:guardian
#TAG:drift
#TAG:task12
#TAG:testing
"""

import time
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

import pytest

# Import test targets
try:
    from core.ethics.guardian_drift_bands import (
        BandTransition,
        BandTrigger,
        GuardianBand,
        GuardianBandResult,
        GuardianDriftBands,
        GuardianThresholds,
        create_guardian_drift_bands,
    )
    from core.ethics.logic.ethics_engine import EthicsAction, EthicsEngine, EthicsResult
    GUARDIAN_AVAILABLE = True
except ImportError:
    GUARDIAN_AVAILABLE = False
    pytest.skip("Guardian Drift Bands not available", allow_module_level=True)


class TestGuardianThresholds:
    """Test Guardian threshold configuration and validation."""

    def test_default_thresholds(self):
        """Test default threshold values are sane."""
        thresholds = GuardianThresholds()

        assert thresholds.allow_drift_threshold == 0.05
        assert thresholds.guardrails_drift_threshold == 0.15
        assert thresholds.human_drift_threshold == 0.35

        # Check ordering
        assert thresholds.allow_drift_threshold < thresholds.guardrails_drift_threshold
        assert thresholds.guardrails_drift_threshold < thresholds.human_drift_threshold

    def test_threshold_validation_valid_config(self):
        """Test threshold validation with valid configuration."""
        thresholds = GuardianThresholds(
            allow_drift_threshold=0.1,
            guardrails_drift_threshold=0.3,
            human_drift_threshold=0.6
        )

        errors = thresholds.validate()
        assert len(errors) == 0

    def test_threshold_validation_invalid_ordering(self):
        """Test threshold validation catches invalid ordering."""
        thresholds = GuardianThresholds(
            allow_drift_threshold=0.5,
            guardrails_drift_threshold=0.3,  # Invalid: should be > allow
            human_drift_threshold=0.7
        )

        errors = thresholds.validate()
        assert "ascending order" in " ".join(errors)

    def test_threshold_validation_out_of_range(self):
        """Test threshold validation catches out-of-range values."""
        thresholds = GuardianThresholds(
            allow_drift_threshold=-0.1,  # Invalid: < 0
            guardrails_drift_threshold=1.5,  # Invalid: > 1
            human_drift_threshold=0.5
        )

        errors = thresholds.validate()
        assert len(errors) >= 2  # Should catch both invalid values


class TestGuardianDriftBands:
    """Test core Guardian Drift Bands functionality."""

    @pytest.fixture
    def guardian_bands(self):
        """Create test Guardian Drift Bands instance."""
        thresholds = GuardianThresholds(
            allow_drift_threshold=0.1,
            guardrails_drift_threshold=0.3,
            human_drift_threshold=0.6,
            hysteresis_buffer_allow=5.0,
            hysteresis_buffer_guardrails=10.0,
            hysteresis_buffer_human=15.0
        )
        return GuardianDriftBands(thresholds=thresholds)

    @pytest.fixture
    def mock_ethics_engine(self):
        """Create mock ethics engine for testing."""
        engine = Mock(spec=EthicsEngine)
        return engine

    def test_initialization_valid_config(self, guardian_bands):
        """Test Guardian initialization with valid configuration."""
        assert guardian_bands.current_band == GuardianBand.ALLOW
        assert len(guardian_bands.transition_history) == 0
        assert len(guardian_bands.drift_history) == 0

    def test_initialization_invalid_config(self):
        """Test Guardian initialization fails with invalid configuration."""
        invalid_thresholds = GuardianThresholds(
            allow_drift_threshold=0.8,
            guardrails_drift_threshold=0.3,  # Invalid ordering
            human_drift_threshold=0.6
        )

        with pytest.raises(ValueError, match="Invalid threshold configuration"):
            GuardianDriftBands(thresholds=invalid_thresholds)

    def test_drift_score_calculation_base_cases(self, guardian_bands):
        """Test drift score calculation for basic cases."""
        # Test with ALLOW ethics result
        ethics_result = Mock()
        ethics_result.action = EthicsAction.ALLOW

        drift_score = guardian_bands._calculate_drift_score(
            {"action": "test"},
            {"user_id": "test_user"},
            ethics_result
        )

        assert 0.0 <= drift_score <= 1.0

    def test_drift_score_calculation_ethics_penalties(self, guardian_bands):
        """Test drift score increases with ethics violations."""
        # ALLOW case
        ethics_allow = Mock()
        ethics_allow.action = EthicsAction.ALLOW

        drift_allow = guardian_bands._calculate_drift_score(
            {"action": "test"},
            {"user_id": "test_user"},
            ethics_allow
        )

        # WARN case
        ethics_warn = Mock()
        ethics_warn.action = EthicsAction.WARN

        drift_warn = guardian_bands._calculate_drift_score(
            {"action": "test"},
            {"user_id": "test_user"},
            ethics_warn
        )

        # BLOCK case
        ethics_block = Mock()
        ethics_block.action = EthicsAction.BLOCK

        drift_block = guardian_bands._calculate_drift_score(
            {"action": "test"},
            {"user_id": "test_user"},
            ethics_block
        )

        # Should increase: ALLOW < WARN < BLOCK
        assert drift_allow < drift_warn < drift_block

    def test_target_band_calculation_drift_thresholds(self, guardian_bands):
        """Test target band calculation based on drift thresholds."""
        # Low drift -> ALLOW
        target = guardian_bands._calculate_target_band(0.05, None)
        assert target == GuardianBand.ALLOW

        # Medium drift -> ALLOW_WITH_GUARDRAILS
        target = guardian_bands._calculate_target_band(0.2, None)
        assert target == GuardianBand.ALLOW_WITH_GUARDRAILS

        # High drift -> REQUIRE_HUMAN
        target = guardian_bands._calculate_target_band(0.4, None)
        assert target == GuardianBand.REQUIRE_HUMAN

        # Very high drift -> BLOCK
        target = guardian_bands._calculate_target_band(0.8, None)
        assert target == GuardianBand.BLOCK

    def test_target_band_calculation_critical_ethics_override(self, guardian_bands):
        """Test that critical ethics violations override drift scores."""
        # Low drift but BLOCK ethics should override to BLOCK
        ethics_result = Mock()
        ethics_result.action = EthicsAction.BLOCK

        target = guardian_bands._calculate_target_band(0.01, ethics_result)
        assert target == GuardianBand.BLOCK

    def test_hysteresis_upward_transitions_immediate(self, guardian_bands):
        """Test that upward (more restrictive) transitions are immediate."""
        # Start at ALLOW, transition to GUARDRAILS should be immediate
        assert guardian_bands.current_band == GuardianBand.ALLOW

        result, transition = guardian_bands._apply_hysteresis(
            GuardianBand.ALLOW_WITH_GUARDRAILS,
            0.2,
            "warn",
            "test_hash"
        )

        assert result == GuardianBand.ALLOW_WITH_GUARDRAILS
        assert transition is not None
        assert transition.from_band == GuardianBand.ALLOW
        assert transition.to_band == GuardianBand.ALLOW_WITH_GUARDRAILS

    def test_hysteresis_downward_transitions_delayed(self, guardian_bands):
        """Test that downward (less restrictive) transitions are delayed by hysteresis."""
        # Force to GUARDRAILS band first
        guardian_bands.current_band = GuardianBand.ALLOW_WITH_GUARDRAILS
        guardian_bands._set_hysteresis_buffer(GuardianBand.ALLOW_WITH_GUARDRAILS)

        # Try to transition down to ALLOW - should be blocked by hysteresis
        result, transition = guardian_bands._apply_hysteresis(
            GuardianBand.ALLOW,
            0.01,
            "allow",
            "test_hash"
        )

        assert result == GuardianBand.ALLOW_WITH_GUARDRAILS  # No change due to hysteresis
        assert transition is None

    def test_hysteresis_expiration_allows_downward_transition(self, guardian_bands):
        """Test that expired hysteresis allows downward transitions."""
        # Force to GUARDRAILS band with immediate expiration
        guardian_bands.current_band = GuardianBand.ALLOW_WITH_GUARDRAILS
        past_time = datetime.now(timezone.utc) - timedelta(seconds=10)
        guardian_bands.hysteresis_expires[GuardianBand.ALLOW_WITH_GUARDRAILS] = past_time

        # Now try to transition down - should succeed
        result, transition = guardian_bands._apply_hysteresis(
            GuardianBand.ALLOW,
            0.01,
            "allow",
            "test_hash"
        )

        assert result == GuardianBand.ALLOW
        assert transition is not None
        assert transition.trigger == BandTrigger.HYSTERESIS_DECAY

    def test_guardrails_generation_by_band(self, guardian_bands):
        """Test guardrails generation for different bands."""
        # ALLOW - no guardrails
        guardrails = guardian_bands._generate_guardrails(
            GuardianBand.ALLOW,
            0.01,
            None
        )
        assert len(guardrails) == 0

        # ALLOW_WITH_GUARDRAILS - basic guardrails
        guardrails = guardian_bands._generate_guardrails(
            GuardianBand.ALLOW_WITH_GUARDRAILS,
            0.15,
            None
        )
        assert "enhanced_audit_logging" in guardrails
        assert "parameter_validation_required" in guardrails

        # REQUIRE_HUMAN - human oversight guardrails
        guardrails = guardian_bands._generate_guardrails(
            GuardianBand.REQUIRE_HUMAN,
            0.4,
            None
        )
        assert "human_approval_required" in guardrails
        assert "comprehensive_audit_trail" in guardrails

        # BLOCK - blocking guardrails
        guardrails = guardian_bands._generate_guardrails(
            GuardianBand.BLOCK,
            0.8,
            None
        )
        assert "operation_blocked" in guardrails
        assert "security_review_required" in guardrails

    def test_human_requirements_generation(self, guardian_bands):
        """Test human requirements generation for bands that need them."""
        # ALLOW and ALLOW_WITH_GUARDRAILS - no human requirements
        requirements = guardian_bands._generate_human_requirements(
            GuardianBand.ALLOW,
            0.01,
            None
        )
        assert len(requirements) == 0

        requirements = guardian_bands._generate_human_requirements(
            GuardianBand.ALLOW_WITH_GUARDRAILS,
            0.15,
            None
        )
        assert len(requirements) == 0

        # REQUIRE_HUMAN - specific requirements
        requirements = guardian_bands._generate_human_requirements(
            GuardianBand.REQUIRE_HUMAN,
            0.4,
            None
        )
        assert "review_plan_parameters" in requirements
        assert "validate_user_intent" in requirements

        # BLOCK - investigation requirements
        requirements = guardian_bands._generate_human_requirements(
            GuardianBand.BLOCK,
            0.8,
            None
        )
        assert "investigate_block_reason" in requirements
        assert "assess_system_security" in requirements

    def test_evaluate_integration_with_ethics_engine(self, guardian_bands, mock_ethics_engine):
        """Test full evaluation with mock ethics engine."""
        # Setup mock ethics result
        mock_result = Mock()
        mock_result.action = EthicsAction.WARN
        mock_result.triggered_rules = []
        mock_ethics_engine.evaluate_plan.return_value = mock_result

        guardian_bands.ethics_engine = mock_ethics_engine

        # Evaluate a plan
        plan = {"action": "test_action", "params": {"test": "value"}}
        context = {"user_id": "test_user"}

        result = guardian_bands.evaluate(plan, context)

        # Verify ethics engine was called
        mock_ethics_engine.evaluate_plan.assert_called_once_with(plan, context)

        # Verify result structure
        assert isinstance(result, GuardianBandResult)
        assert result.band in [GuardianBand.ALLOW, GuardianBand.ALLOW_WITH_GUARDRAILS, GuardianBand.REQUIRE_HUMAN, GuardianBand.BLOCK]
        assert result.drift_score >= 0.0
        assert result.ethics_action == "warn"
        assert isinstance(result.guardrails, list)
        assert isinstance(result.human_requirements, list)

    def test_evaluate_without_ethics_engine(self, guardian_bands):
        """Test evaluation without ethics engine falls back gracefully."""
        guardian_bands.ethics_engine = None

        plan = {"action": "test_action"}
        context = {"user_id": "test_user"}

        result = guardian_bands.evaluate(plan, context)

        assert isinstance(result, GuardianBandResult)
        assert result.ethics_action == "unknown"
        assert result.band == GuardianBand.ALLOW  # Should be ALLOW with low drift

    def test_evaluate_error_handling(self, guardian_bands):
        """Test evaluation error handling fails closed."""
        # Force an error by providing invalid input
        with patch.object(guardian_bands, '_calculate_drift_score', side_effect=Exception("Test error")):
            result = guardian_bands.evaluate({}, {})

            # Should fail closed to most restrictive band
            assert result.band == guardian_bands.thresholds.system_error_fallback_band
            assert result.drift_score == 1.0
            assert result.ethics_action == "error"
            assert "system_error_detected" in result.guardrails

    def test_force_band_transition(self, guardian_bands):
        """Test manual band transition override."""
        # Start at ALLOW
        assert guardian_bands.current_band == GuardianBand.ALLOW

        # Force transition to BLOCK
        transition = guardian_bands.force_band_transition(
            GuardianBand.BLOCK,
            "Emergency override",
            "admin_user"
        )

        assert guardian_bands.current_band == GuardianBand.BLOCK
        assert transition.trigger == BandTrigger.MANUAL_OVERRIDE
        assert transition.reason == "Emergency override"
        assert transition.metadata["operator_id"] == "admin_user"

        # Hysteresis should be cleared
        assert len(guardian_bands.hysteresis_expires) == 0

    def test_drift_acceleration_detection(self, guardian_bands):
        """Test detection of rapid drift increases."""
        # Populate drift history with increasing drift
        base_time = datetime.now(timezone.utc)
        guardian_bands.drift_history = [
            (base_time - timedelta(seconds=300), 0.1),
            (base_time - timedelta(seconds=200), 0.15),
            (base_time - timedelta(seconds=100), 0.25),
            (base_time, 0.4)  # Rapid acceleration
        ]

        acceleration = guardian_bands._calculate_drift_acceleration()
        assert acceleration > 0.0  # Should detect acceleration

    def test_get_current_status(self, guardian_bands):
        """Test status reporting functionality."""
        status = guardian_bands.get_current_status()

        assert "current_band" in status
        assert "last_transition" in status
        assert "hysteresis_active" in status
        assert "thresholds" in status
        assert status["system_status"] == "operational"

        # Check thresholds are included
        assert status["thresholds"]["allow"] == guardian_bands.thresholds.allow_drift_threshold
        assert status["thresholds"]["guardrails"] == guardian_bands.thresholds.guardrails_drift_threshold
        assert status["thresholds"]["human"] == guardian_bands.thresholds.human_drift_threshold

    def test_performance_requirements(self, guardian_bands):
        """Test that evaluations meet performance requirements."""
        plan = {"action": "test_action", "params": {"test": "value"}}
        context = {"user_id": "test_user"}

        # Run multiple evaluations to get average
        times = []
        for _ in range(10):
            start = time.perf_counter()
            guardian_bands.evaluate(plan, context)
            times.append((time.perf_counter() - start) * 1000)

        avg_time = sum(times) / len(times)
        max_time = max(times)

        # Should be well under 10ms for simple evaluations
        assert avg_time < 10.0, f"Average evaluation time {avg_time:.2f}ms exceeds 10ms"
        assert max_time < 25.0, f"Max evaluation time {max_time:.2f}ms exceeds 25ms"


class TestGuardianFactoryFunction:
    """Test Guardian factory function."""

    def test_create_guardian_drift_bands_defaults(self):
        """Test factory function with default parameters."""
        guardian = create_guardian_drift_bands()

        assert isinstance(guardian, GuardianDriftBands)
        assert guardian.thresholds.allow_drift_threshold == 0.05
        assert guardian.thresholds.guardrails_drift_threshold == 0.15
        assert guardian.thresholds.human_drift_threshold == 0.35

    def test_create_guardian_drift_bands_custom_thresholds(self):
        """Test factory function with custom thresholds."""
        guardian = create_guardian_drift_bands(
            allow_threshold=0.2,
            guardrails_threshold=0.4,
            human_threshold=0.8
        )

        assert guardian.thresholds.allow_drift_threshold == 0.2
        assert guardian.thresholds.guardrails_drift_threshold == 0.4
        assert guardian.thresholds.human_drift_threshold == 0.8

    def test_create_guardian_drift_bands_additional_params(self):
        """Test factory function with additional parameters."""
        guardian = create_guardian_drift_bands(
            allow_threshold=0.1,
            hysteresis_buffer_allow=120.0,
            critical_violation_immediate_block=False
        )

        assert guardian.thresholds.allow_drift_threshold == 0.1
        assert guardian.thresholds.hysteresis_buffer_allow == 120.0
        assert guardian.thresholds.critical_violation_immediate_block == False


class TestBandTransitionScenarios:
    """Test complex band transition scenarios."""

    @pytest.fixture
    def guardian_scenario(self):
        """Create Guardian with fast hysteresis for testing."""
        thresholds = GuardianThresholds(
            allow_drift_threshold=0.1,
            guardrails_drift_threshold=0.3,
            human_drift_threshold=0.6,
            hysteresis_buffer_allow=0.1,  # Very short for testing
            hysteresis_buffer_guardrails=0.2,
            hysteresis_buffer_human=0.3
        )
        return GuardianDriftBands(thresholds=thresholds)

    def test_band_escalation_scenario(self, guardian_scenario):
        """Test escalation through all bands."""
        # Start at ALLOW
        assert guardian_scenario.current_band == GuardianBand.ALLOW

        # Escalate to GUARDRAILS
        result1 = guardian_scenario.evaluate({"action": "test"}, drift_score=0.2)
        assert result1.band == GuardianBand.ALLOW_WITH_GUARDRAILS

        # Escalate to HUMAN
        result2 = guardian_scenario.evaluate({"action": "test"}, drift_score=0.4)
        assert result2.band == GuardianBand.REQUIRE_HUMAN

        # Escalate to BLOCK
        result3 = guardian_scenario.evaluate({"action": "test"}, drift_score=0.8)
        assert result3.band == GuardianBand.BLOCK

        # Verify transitions were recorded
        assert len(guardian_scenario.transition_history) == 3

    def test_band_de_escalation_with_hysteresis(self, guardian_scenario):
        """Test de-escalation with hysteresis delays."""
        # Force to BLOCK
        guardian_scenario.current_band = GuardianBand.BLOCK
        guardian_scenario._set_hysteresis_buffer(GuardianBand.BLOCK)

        # Try to de-escalate immediately - should be blocked
        result1 = guardian_scenario.evaluate({"action": "test"}, drift_score=0.01)
        assert result1.band == GuardianBand.BLOCK  # Still blocked by hysteresis

        # Wait for hysteresis to expire and try again
        time.sleep(0.4)  # Wait for hysteresis buffer to expire
        result2 = guardian_scenario.evaluate({"action": "test"}, drift_score=0.01)
        assert result2.band == GuardianBand.ALLOW  # Should de-escalate now

    def test_ethics_override_scenarios(self, guardian_scenario):
        """Test ethics result overriding drift scores."""
        # Low drift but BLOCK ethics should result in BLOCK
        ethics_block = Mock()
        ethics_block.action = EthicsAction.BLOCK
        ethics_block.triggered_rules = [Mock()]

        guardian_scenario.ethics_engine = Mock()
        guardian_scenario.ethics_engine.evaluate_plan.return_value = ethics_block

        result = guardian_scenario.evaluate({"action": "dangerous"}, drift_score=0.01)
        assert result.band == GuardianBand.BLOCK  # Ethics override


if __name__ == "__main__":
    pytest.main([__file__])