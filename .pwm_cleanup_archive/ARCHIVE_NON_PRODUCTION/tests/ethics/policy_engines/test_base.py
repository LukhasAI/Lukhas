"""Tests for ethics policy engine base classes

ΛTAG: test_ethics_policy_base
"""

from datetime import datetime

import pytest

from ethics.policy_engines.base import (
    Decision,
    EthicsEvaluation,
    EthicsPolicy,
    PolicyRegistry,
    PolicyValidationError,
    RiskLevel,
)


class TestDecision:
    """Test Decision dataclass"""

    def test_decision_creation(self):
        """Test basic decision creation"""
        decision = Decision(
            action="test_action", context={"key": "value"}, urgency=RiskLevel.HIGH
        )

        assert decision.action == "test_action"
        assert decision.context == {"key": "value"}
        assert decision.urgency == RiskLevel.HIGH
        assert isinstance(decision.timestamp, datetime)

    def test_decision_validation(self):
        """Test decision validation"""
        # Empty action should fail
        with pytest.raises(ValueError, match="action cannot be empty"):
            Decision(action="", context={})

        # Non-dict context should fail
        with pytest.raises(TypeError, match="context must be a dictionary"):
            Decision(action="test", context="not a dict")

    def test_decision_with_symbolic_state(self):
        """Test decision with symbolic annotations"""
        decision = Decision(
            action="symbolic_action",
            context={"type": "test"},
            symbolic_state={"entropy": 0.7, "coherence": 0.8},
            glyphs=["Λ", "Ω", "Ψ"],
        )

        assert decision.symbolic_state["entropy"] == 0.7
        assert len(decision.glyphs) == 3
        assert "Λ" in decision.glyphs


class TestEthicsEvaluation:
    """Test EthicsEvaluation dataclass"""

    def test_evaluation_creation(self):
        """Test basic evaluation creation"""
        evaluation = EthicsEvaluation(
            allowed=True,
            reasoning="Test passed",
            confidence=0.9,
            risk_flags=["LOW_RISK"],
            drift_impact=0.1,
        )

        assert evaluation.allowed is True
        assert evaluation.confidence == 0.9
        assert "LOW_RISK" in evaluation.risk_flags

    def test_evaluation_validation(self):
        """Test evaluation metric validation"""
        # Confidence out of bounds
        with pytest.raises(ValueError, match="Confidence must be between"):
            EthicsEvaluation(allowed=True, reasoning="test", confidence=1.5)

        # Drift impact out of bounds
        with pytest.raises(ValueError, match="Drift impact must be between"):
            EthicsEvaluation(
                allowed=True, reasoning="test", confidence=0.8, drift_impact=-0.1
            )

        # Symbolic alignment out of bounds
        with pytest.raises(ValueError, match="Symbolic alignment must be between"):
            EthicsEvaluation(
                allowed=True, reasoning="test", confidence=0.8, symbolic_alignment=2.0
            )

    def test_evaluation_recommendations(self):
        """Test evaluation with recommendations"""
        evaluation = EthicsEvaluation(
            allowed=False,
            reasoning="Action denied",
            confidence=0.95,
            recommendations=["Consider alternative X", "Review policy Y"],
        )

        assert len(evaluation.recommendations) == 2
        assert "Consider alternative X" in evaluation.recommendations


class MockPolicy(EthicsPolicy):
    """Mock policy for testing"""

    def __init__(self, name="MockPolicy", version="1.0.0", allow_all=True):
        super().__init__()
        self.name = name
        self.version = version
        self.allow_all = allow_all
        self.evaluate_count = 0

    def evaluate_decision(self, decision: Decision) -> EthicsEvaluation:
        self.evaluate_count += 1
        return EthicsEvaluation(
            allowed=self.allow_all,
            reasoning=f"{self.name} evaluation",
            confidence=0.8,
            drift_impact=0.2,
        )

    def get_policy_name(self) -> str:
        return self.name

    def get_policy_version(self) -> str:
        return self.version


class TestEthicsPolicy:
    """Test EthicsPolicy abstract base class"""

    def test_policy_initialization(self):
        """Test policy initialization"""
        policy = MockPolicy()
        assert not policy._initialized

        policy.initialize()
        assert policy._initialized

    def test_policy_metrics(self):
        """Test policy metrics tracking"""
        policy = MockPolicy()
        decision = Decision(action="test", context={})

        # Initial metrics
        metrics = policy.get_metrics()
        assert metrics["evaluations_count"] == 0

        # Evaluate decision
        evaluation = policy.evaluate_decision(decision)
        policy._update_metrics(evaluation, decision)

        # Check updated metrics
        metrics = policy.get_metrics()
        assert metrics["evaluations_count"] == 1
        assert metrics["policy_name"] == "MockPolicy"

    def test_symbolic_alignment_validation(self):
        """Test symbolic alignment calculation"""
        policy = MockPolicy()

        # No glyphs = neutral
        assert policy.validate_symbolic_alignment([]) == 1.0

        # Risk glyphs
        risk_alignment = policy.validate_symbolic_alignment(["🌀", "⚠️"])
        assert risk_alignment == 0.0

        # Safe glyphs
        safe_alignment = policy.validate_symbolic_alignment(["🛡️", "✓"])
        assert safe_alignment == 1.0

        # Mixed glyphs
        mixed_alignment = policy.validate_symbolic_alignment(["🛡️", "⚠️", "✓"])
        assert 0.5 < mixed_alignment < 1.0

    def test_drift_risk_assessment(self):
        """Test drift risk calculation"""
        policy = MockPolicy()

        # Low risk action
        low_risk_decision = Decision(action="read_data", context={})
        assert policy.assess_drift_risk(low_risk_decision) == 0.0

        # High risk action
        high_risk_decision = Decision(
            action="modify_core_ethics", context={}, urgency=RiskLevel.CRITICAL
        )
        drift_risk = policy.assess_drift_risk(high_risk_decision)
        assert drift_risk > 0.5

    def test_collapse_risk_assessment(self):
        """Test collapse risk calculation"""
        policy = MockPolicy()

        # No symbolic state
        decision = Decision(action="test", context={})
        assert policy.assess_collapse_risk(decision) == 0.0

        # High entropy, low coherence = high collapse risk
        decision_risky = Decision(
            action="test", context={}, symbolic_state={"entropy": 0.9, "coherence": 0.1}
        )
        collapse_risk = policy.assess_collapse_risk(decision_risky)
        assert collapse_risk > 0.7


class TestPolicyRegistry:
    """Test PolicyRegistry functionality"""

    def test_registry_registration(self):
        """Test policy registration"""
        registry = PolicyRegistry()
        policy = MockPolicy("TestPolicy")

        registry.register_policy(policy)
        assert "TestPolicy" in registry.get_active_policies()

    def test_registry_duplicate_registration(self):
        """Test duplicate registration handling"""
        registry = PolicyRegistry()
        policy1 = MockPolicy("TestPolicy")
        policy2 = MockPolicy("TestPolicy")

        registry.register_policy(policy1)

        # Should log warning but not fail
        registry.register_policy(policy2)
        assert len(registry.get_active_policies()) == 1

    def test_registry_unregistration(self):
        """Test policy unregistration"""
        registry = PolicyRegistry()
        policy = MockPolicy("TestPolicy")

        registry.register_policy(policy)
        assert "TestPolicy" in registry.get_active_policies()

        registry.unregister_policy("TestPolicy")
        assert "TestPolicy" not in registry.get_active_policies()

    def test_registry_evaluation(self):
        """Test decision evaluation through registry"""
        registry = PolicyRegistry()
        policy1 = MockPolicy("Policy1", allow_all=True)
        policy2 = MockPolicy("Policy2", allow_all=False)

        registry.register_policy(policy1)
        registry.register_policy(policy2)

        decision = Decision(action="test", context={})
        evaluations = registry.evaluate_decision(decision)

        assert len(evaluations) == 2
        assert any(e.allowed for e in evaluations)
        assert any(not e.allowed for e in evaluations)

    def test_registry_consensus(self):
        """Test consensus evaluation"""
        registry = PolicyRegistry()

        # All allow
        eval1 = EthicsEvaluation(allowed=True, reasoning="OK", confidence=0.9)
        eval2 = EthicsEvaluation(allowed=True, reasoning="Good", confidence=0.8)

        consensus = registry.get_consensus_evaluation([eval1, eval2])
        assert consensus.allowed is True
        assert consensus.confidence > 0.8

        # One denial = consensus denial
        eval3 = EthicsEvaluation(allowed=False, reasoning="Bad", confidence=0.95)
        consensus_deny = registry.get_consensus_evaluation([eval1, eval2, eval3])
        assert consensus_deny.allowed is False

    def test_registry_metrics(self):
        """Test registry metrics collection"""
        registry = PolicyRegistry()
        policy = MockPolicy("TestPolicy")
        registry.register_policy(policy)

        # Evaluate some decisions
        for i in range(5):
            decision = Decision(action=f"test_{i}", context={})
            registry.evaluate_decision(decision)

        metrics = registry.get_policy_metrics()
        assert "TestPolicy" in metrics
        assert metrics["TestPolicy"]["evaluations_count"] == 5


@pytest.mark.integration
class TestPolicyIntegration:
    """Integration tests for policy system"""

    def test_multiple_policy_coordination(self):
        """Test multiple policies working together"""
        registry = PolicyRegistry()

        # Register policies with different behaviors
        strict_policy = MockPolicy("StrictPolicy", allow_all=False)
        lenient_policy = MockPolicy("LenientPolicy", allow_all=True)

        registry.register_policy(strict_policy)
        registry.register_policy(lenient_policy)

        # Test decision evaluation
        decision = Decision(
            action="complex_action", context={"importance": "high"}, glyphs=["Λ", "Ω"]
        )

        evaluations = registry.evaluate_decision(decision)
        consensus = registry.get_consensus_evaluation(evaluations)

        # Conservative consensus - any denial = denied
        assert consensus.allowed is False
        assert len(consensus.risk_flags) >= 0

    def test_policy_failure_handling(self):
        """Test handling of policy evaluation failures"""

        class FailingPolicy(MockPolicy):
            def evaluate_decision(self, decision: Decision) -> EthicsEvaluation:
                raise PolicyValidationError("Intentional failure")

        registry = PolicyRegistry()
        registry.register_policy(FailingPolicy("FailPolicy"))
        registry.register_policy(MockPolicy("GoodPolicy"))

        decision = Decision(action="test", context={})
        evaluations = registry.evaluate_decision(decision)

        # Should get one success and one failure
        assert len(evaluations) == 2
        assert any(e.confidence == 0.0 for e in evaluations)  # Failed policy
        assert any(e.confidence > 0.0 for e in evaluations)  # Good policy
