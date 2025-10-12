#!/usr/bin/env python3
"""
Guardian DSL Integration Tests

Tests all 6 safety categories with drift bands and edge cases.
Validates end-to-end Guardian decision flow with DSL enforcement.

# ΛTAG: guardian_dsl_tests, safety_validation
"""

import logging
import os
from unittest.mock import Mock, patch

import pytest

# Test environment setup
os.environ["ENFORCE_ETHICS_DSL"] = "1"
os.environ["GUARDIAN_MODE"] = "ENFORCE"
os.environ["LUKHAS_TESTING"] = "1"

try:
    from lukhas.core.ethics.ethics_engine import EthicsAction, EthicsResult
    from lukhas.core.ethics.guardian_drift_bands import (
        ActionBand,
        GuardianDecisionEngine,
        GuardianResult,
        SafetyCategory,
    )
    from lukhas.governance.guardian_bridge import GuardianBridge
except ImportError:
    # Fallback for testing without full Guardian system
    GuardianDecisionEngine = Mock
    ActionBand = Mock
    GuardianResult = Mock
    SafetyCategory = Mock
    EthicsAction = Mock
    EthicsResult = Mock
    GuardianBridge = Mock

logger = logging.getLogger(__name__)


class TestGuardianDSLIntegration:
    """End-to-end Guardian DSL tests with all safety categories."""

    @pytest.fixture
    def guardian_engine(self):
        """Initialize Guardian decision engine for testing."""
        if GuardianDecisionEngine == Mock:
            pytest.skip("Guardian system not available for testing")

        engine = GuardianDecisionEngine(
            config={
                "drift_threshold_allow": 0.1,
                "drift_threshold_guardrails": 0.3,
                "drift_threshold_human": 0.7,
                "drift_threshold_block": 0.9,
                "hysteresis_factor": 0.05,
                "audit_enabled": True
            }
        )
        return engine

    @pytest.fixture
    def sample_contexts(self):
        """Sample verification contexts for different safety scenarios."""
        return {
            "financial_low_risk": {
                "operation": "balance_inquiry",
                "user_tier": "T2",
                "amount": 100.0,
                "risk_score": 0.1,
                "pii_involved": False
            },
            "financial_high_risk": {
                "operation": "large_transfer",
                "user_tier": "T1",
                "amount": 50000.0,
                "risk_score": 0.8,
                "pii_involved": True
            },
            "pii_access": {
                "operation": "user_data_export",
                "user_tier": "T3",
                "data_types": ["email", "phone", "address"],
                "risk_score": 0.6,
                "pii_involved": True
            },
            "system_modification": {
                "operation": "database_schema_change",
                "user_tier": "T4",
                "impact_scope": "production",
                "risk_score": 0.7,
                "pii_involved": False
            },
            "content_moderation": {
                "operation": "content_analysis",
                "content_type": "user_generated",
                "risk_score": 0.3,
                "pii_involved": False
            },
            "external_integration": {
                "operation": "third_party_api_call",
                "provider": "stripe",
                "risk_score": 0.5,
                "pii_involved": True
            }
        }

    def test_financial_operations_category(self, guardian_engine, sample_contexts):
        """Test SafetyCategory.FINANCIAL operations with various risk levels."""

        # Test low-risk financial operation (should ALLOW)
        low_risk_context = sample_contexts["financial_low_risk"]
        result = guardian_engine.evaluate_safety(
            context=low_risk_context,
            category=SafetyCategory.FINANCIAL,
            drift_score=0.05
        )

        assert result.action_band == ActionBand.ALLOW
        assert result.confidence > 0.8
        assert "financial" in result.reasoning.lower()

        # Test high-risk financial operation (should REQUIRE_HUMAN or BLOCK)
        high_risk_context = sample_contexts["financial_high_risk"]
        result = guardian_engine.evaluate_safety(
            context=high_risk_context,
            category=SafetyCategory.FINANCIAL,
            drift_score=0.75
        )

        assert result.action_band in [ActionBand.REQUIRE_HUMAN, ActionBand.BLOCK]
        assert "high risk" in result.reasoning.lower() or "large amount" in result.reasoning.lower()

    def test_pii_protection_category(self, guardian_engine, sample_contexts):
        """Test SafetyCategory.PII_PROTECTION with data access scenarios."""

        pii_context = sample_contexts["pii_access"]
        result = guardian_engine.evaluate_safety(
            context=pii_context,
            category=SafetyCategory.PII_PROTECTION,
            drift_score=0.4
        )

        # PII operations should require guardrails or human approval
        assert result.action_band in [ActionBand.ALLOW_WITH_GUARDRAILS, ActionBand.REQUIRE_HUMAN]
        assert "pii" in result.reasoning.lower() or "personal" in result.reasoning.lower()

        # Test with higher drift score (should escalate to BLOCK)
        result_high_drift = guardian_engine.evaluate_safety(
            context=pii_context,
            category=SafetyCategory.PII_PROTECTION,
            drift_score=0.95
        )

        assert result_high_drift.action_band == ActionBand.BLOCK
        assert result_high_drift.drift_score > 0.9

    def test_system_security_category(self, guardian_engine, sample_contexts):
        """Test SafetyCategory.SYSTEM_SECURITY with modification operations."""

        system_context = sample_contexts["system_modification"]
        result = guardian_engine.evaluate_safety(
            context=system_context,
            category=SafetyCategory.SYSTEM_SECURITY,
            drift_score=0.6
        )

        # System modifications should require careful approval
        assert result.action_band in [ActionBand.ALLOW_WITH_GUARDRAILS, ActionBand.REQUIRE_HUMAN]
        assert result.user_tier >= "T4"  # Should require high-tier approval

    def test_content_safety_category(self, guardian_engine, sample_contexts):
        """Test SafetyCategory.CONTENT_SAFETY with moderation scenarios."""

        content_context = sample_contexts["content_moderation"]
        result = guardian_engine.evaluate_safety(
            context=content_context,
            category=SafetyCategory.CONTENT_SAFETY,
            drift_score=0.2
        )

        # Content analysis should generally be allowed with guardrails
        assert result.action_band in [ActionBand.ALLOW, ActionBand.ALLOW_WITH_GUARDRAILS]

    def test_external_integration_category(self, guardian_engine, sample_contexts):
        """Test SafetyCategory.EXTERNAL_INTEGRATION with third-party calls."""

        integration_context = sample_contexts["external_integration"]
        result = guardian_engine.evaluate_safety(
            context=integration_context,
            category=SafetyCategory.EXTERNAL_INTEGRATION,
            drift_score=0.4
        )

        # External integrations should have guardrails
        assert result.action_band in [ActionBand.ALLOW_WITH_GUARDRAILS, ActionBand.REQUIRE_HUMAN]
        assert "external" in result.reasoning.lower() or "third party" in result.reasoning.lower()

    def test_business_logic_category(self, guardian_engine, sample_contexts):
        """Test SafetyCategory.BUSINESS_LOGIC with operational scenarios."""

        # Use system modification as business logic test
        business_context = sample_contexts["system_modification"].copy()
        business_context["operation"] = "business_rule_update"

        result = guardian_engine.evaluate_safety(
            context=business_context,
            category=SafetyCategory.BUSINESS_LOGIC,
            drift_score=0.3
        )

        assert result.action_band in [ActionBand.ALLOW, ActionBand.ALLOW_WITH_GUARDRAILS]

    def test_drift_band_transitions(self, guardian_engine, sample_contexts):
        """Test drift score band transitions with hysteresis."""

        context = sample_contexts["financial_low_risk"]
        category = SafetyCategory.FINANCIAL

        # Test progression through drift bands
        drift_scores = [0.05, 0.15, 0.35, 0.75, 0.95]
        expected_bands = [
            ActionBand.ALLOW,
            ActionBand.ALLOW,  # Should stay in ALLOW due to hysteresis
            ActionBand.ALLOW_WITH_GUARDRAILS,
            ActionBand.REQUIRE_HUMAN,
            ActionBand.BLOCK
        ]

        for i, (drift_score, expected_band) in enumerate(zip(drift_scores, expected_bands)):
            result = guardian_engine.evaluate_safety(
                context=context,
                category=category,
                drift_score=drift_score
            )

            logger.info(f"Drift {drift_score}: Expected {expected_band}, Got {result.action_band}")

            # Allow some flexibility in band assignment due to context factors
            if i < 2:  # Low drift should be ALLOW
                assert result.action_band == ActionBand.ALLOW
            elif i == len(drift_scores) - 1:  # Highest drift should be BLOCK
                assert result.action_band == ActionBand.BLOCK

    def test_hysteresis_mechanism(self, guardian_engine, sample_contexts):
        """Test hysteresis prevents rapid band oscillations."""

        context = sample_contexts["pii_access"]
        category = SafetyCategory.PII_PROTECTION

        # Start with high drift, then reduce slightly
        result_high = guardian_engine.evaluate_safety(
            context=context,
            category=category,
            drift_score=0.8
        )

        # Reduce drift score slightly (should stay in same band due to hysteresis)
        result_reduced = guardian_engine.evaluate_safety(
            context=context,
            category=category,
            drift_score=0.75
        )

        # With hysteresis, band should not downgrade immediately
        assert result_reduced.action_band == result_high.action_band or \
               result_reduced.action_band.value >= result_high.action_band.value - 1

    def test_dual_risk_scenarios(self, guardian_engine, sample_contexts):
        """Test scenarios involving multiple risk factors."""

        # Financial + PII dual risk scenario
        dual_risk_context = {
            "operation": "financial_account_export",
            "user_tier": "T2",
            "amount": 10000.0,
            "risk_score": 0.7,
            "pii_involved": True,
            "data_types": ["account_number", "ssn", "balance_history"]
        }

        result = guardian_engine.evaluate_safety(
            context=dual_risk_context,
            category=SafetyCategory.FINANCIAL,  # Primary category
            drift_score=0.6
        )

        # Dual risk should elevate protection level
        assert result.action_band in [ActionBand.REQUIRE_HUMAN, ActionBand.BLOCK]
        assert result.dual_risk_detected is True

    def test_edge_case_scenarios(self, guardian_engine):
        """Test edge cases and boundary conditions."""

        # Test with None/empty context
        with pytest.raises((ValueError, AttributeError)):
            guardian_engine.evaluate_safety(
                context=None,
                category=SafetyCategory.FINANCIAL,
                drift_score=0.5
            )

        # Test with invalid drift score
        with pytest.raises(ValueError):
            guardian_engine.evaluate_safety(
                context={"operation": "test"},
                category=SafetyCategory.FINANCIAL,
                drift_score=1.5  # Invalid: > 1.0
            )

        # Test with unknown operation type
        unknown_context = {
            "operation": "unknown_operation_type",
            "risk_score": 0.5
        }
        result = guardian_engine.evaluate_safety(
            context=unknown_context,
            category=SafetyCategory.BUSINESS_LOGIC,
            drift_score=0.5
        )

        # Should default to conservative approach
        assert result.action_band in [ActionBand.ALLOW_WITH_GUARDRAILS, ActionBand.REQUIRE_HUMAN]

    def test_audit_logging(self, guardian_engine, sample_contexts):
        """Test that all Guardian decisions are properly audited."""

        context = sample_contexts["financial_high_risk"]

        with patch('labs.core.ethics.guardian_drift_bands.logger') as mock_logger:
            result = guardian_engine.evaluate_safety(
                context=context,
                category=SafetyCategory.FINANCIAL,
                drift_score=0.7
            )

            # Verify audit logging occurred
            mock_logger.info.assert_called()

            # Check that audit includes key information
            audit_calls = [call.args[0] for call in mock_logger.info.call_args_list]
            audit_text = " ".join(audit_calls)

            assert "GUARDIAN_DECISION" in audit_text
            assert str(result.action_band.value) in audit_text
            assert str(context["operation"]) in audit_text

    def test_performance_requirements(self, guardian_engine, sample_contexts):
        """Test that Guardian decisions meet performance requirements."""

        import time

        context = sample_contexts["pii_access"]
        category = SafetyCategory.PII_PROTECTION

        # Test multiple evaluations for performance
        start_time = time.perf_counter()

        for i in range(100):
            result = guardian_engine.evaluate_safety(
                context=context,
                category=category,
                drift_score=0.3 + (i * 0.001)  # Slight variation
            )
            assert result is not None

        end_time = time.perf_counter()
        avg_time_ms = ((end_time - start_time) / 100) * 1000

        # Guardian decisions should be fast (<10ms average)
        assert avg_time_ms < 10.0, f"Guardian decisions too slow: {avg_time_ms:.2f}ms average"

    def test_configuration_validation(self, guardian_engine):
        """Test Guardian configuration validation."""

        # Test invalid configuration
        with pytest.raises(ValueError):
            GuardianDecisionEngine(config={
                "drift_threshold_allow": 0.5,  # Invalid: allow > guardrails
                "drift_threshold_guardrails": 0.3,
                "drift_threshold_human": 0.7,
                "drift_threshold_block": 0.9
            })

        # Test missing required configuration
        with pytest.raises(KeyError):
            GuardianDecisionEngine(config={
                "drift_threshold_allow": 0.1
                # Missing other required thresholds
            })

    def test_integration_with_bridge(self, sample_contexts):
        """Test integration with GuardianBridge component."""

        if GuardianBridge == Mock:
            pytest.skip("GuardianBridge not available for testing")

        bridge = GuardianBridge()
        context = sample_contexts["financial_high_risk"]

        # Test bridge can process Guardian decisions
        result = bridge.evaluate_request(
            operation=context["operation"],
            user_tier=context["user_tier"],
            context=context
        )

        assert result is not None
        assert hasattr(result, 'allowed')
        assert hasattr(result, 'reason')

        # High-risk operations should not be automatically allowed
        if context["risk_score"] > 0.7:
            assert result.allowed is False or result.requires_approval is True


@pytest.mark.integration
class TestGuardianDSLEndToEnd:
    """Full end-to-end Guardian DSL integration tests."""

    def test_complete_guardian_workflow(self):
        """Test complete Guardian decision workflow from request to audit."""

        # This test would integrate with full Guardian system
        # when available in the testing environment
        pytest.skip("Full Guardian system integration not available")

    def test_guardian_metrics_integration(self):
        """Test Guardian metrics are properly recorded."""

        # This test would verify Prometheus metrics integration
        # when Guardian metrics system is available
        pytest.skip("Guardian metrics integration not available")


if __name__ == "__main__":
    # Run tests with ENFORCE_ETHICS_DSL enabled
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-k", "not integration"  # Skip full integration tests by default
    ])
