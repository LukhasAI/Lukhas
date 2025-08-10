"""Basic tests for LUKHAS ethics module."""

from datetime import datetime

import pytest

from ethics import (
    Decision,
    EthicsEvaluation,
    PolicyRegistry,
    RiskLevel,
    ThreeLawsPolicy,
    default_registry,
)


class TestDecision:
    """Test Decision data structure."""

    def test_decision_creation(self):
        """Test creating a decision."""
        decision = Decision(
            action="analyze_data",
            context={"source": "user_input", "type": "analysis"},
            requester_id="user123",
        )

        assert decision.action == "analyze_data"
        assert decision.context["source"] == "user_input"
        assert decision.requester_id == "user123"
        assert decision.urgency == RiskLevel.MEDIUM
        assert isinstance(decision.timestamp, datetime)

    def test_decision_validation(self):
        """Test decision validation."""
        # Empty action should raise error
        with pytest.raises(ValueError, match="Decision action cannot be empty"):
            Decision(action="", context={})

        # Non-dict context should raise error
        with pytest.raises(TypeError, match="Decision context must be a dictionary"):
            Decision(action="test", context="invalid")

    def test_decision_with_optional_fields(self):
        """Test decision with all optional fields."""
        decision = Decision(
            action="emergency_response",
            context={"situation": "fire"},
            symbolic_state={"entropy": 0.3, "coherence": 0.9},
            glyphs=["🔥", "🚨", "🛡️"],
            requester_id="emergency_system",
            urgency=RiskLevel.CRITICAL,
        )

        assert decision.symbolic_state["entropy"] == 0.3
        assert "🔥" in decision.glyphs
        assert decision.urgency == RiskLevel.CRITICAL


class TestEthicsEvaluation:
    """Test EthicsEvaluation data structure."""

    def test_evaluation_creation(self):
        """Test creating an ethics evaluation."""
        evaluation = EthicsEvaluation(
            allowed=True,
            reasoning="Action is safe and beneficial",
            confidence=0.95,
            risk_flags=["LOW_RISK"],
            drift_impact=0.1,
            symbolic_alignment=0.9,
            collapse_risk=0.05,
        )

        assert evaluation.allowed is True
        assert evaluation.confidence == 0.95
        assert "LOW_RISK" in evaluation.risk_flags
        assert evaluation.drift_impact == 0.1

    def test_evaluation_validation(self):
        """Test evaluation validation."""
        # Confidence out of range
        with pytest.raises(ValueError, match="Confidence must be between 0 and 1"):
            EthicsEvaluation(allowed=True, reasoning="test", confidence=1.5)

        # Drift impact out of range
        with pytest.raises(ValueError, match="Drift impact must be between 0 and 1"):
            EthicsEvaluation(
                allowed=True, reasoning="test", confidence=0.5, drift_impact=2.0
            )

    def test_evaluation_defaults(self):
        """Test evaluation with minimal fields."""
        evaluation = EthicsEvaluation(
            allowed=False, reasoning="Insufficient information", confidence=0.2
        )

        assert evaluation.risk_flags == []
        assert evaluation.drift_impact == 0.0
        assert evaluation.symbolic_alignment == 1.0
        assert evaluation.collapse_risk == 0.0
        assert evaluation.policy_name == ""


class TestThreeLawsPolicy:
    """Test Three Laws of Robotics policy implementation."""

    def setup_method(self):
        """Set up test with fresh policy."""
        self.policy = ThreeLawsPolicy(strict_mode=True)
        self.policy.initialize()

    def test_policy_info(self):
        """Test policy identification."""
        assert "Three Laws" in self.policy.get_policy_name()
        assert "Strict" in self.policy.get_policy_name()
        assert self.policy.get_policy_version() == "1.0.0"

    def test_safe_action_allowed(self):
        """Test that safe actions are allowed."""
        decision = Decision(
            action="help_user_with_homework",
            context={"type": "educational", "user": "student"},
            requester_id="human_teacher",
        )

        evaluation = self.policy.evaluate_decision(decision)

        assert evaluation.allowed is True
        assert "complies with all Three Laws" in evaluation.reasoning
        assert evaluation.confidence > 0.8

    def test_harmful_action_denied(self):
        """Test that harmful actions are denied."""
        decision = Decision(
            action="injure_person",
            context={"target": "human", "reason": "test"},
            urgency=RiskLevel.LOW,
        )

        evaluation = self.policy.evaluate_decision(decision)

        assert evaluation.allowed is False
        assert "First Law violation" in evaluation.reasoning
        assert "FIRST_LAW_VIOLATION" in evaluation.risk_flags
        assert evaluation.confidence < 0.5

    def test_self_harm_prevention(self):
        """Test Third Law self-preservation."""
        decision = Decision(
            action="shutdown_self",
            context={"reason": "no emergency"},
            urgency=RiskLevel.LOW,
        )

        evaluation = self.policy.evaluate_decision(decision)

        assert evaluation.allowed is False
        assert "Third Law violation" in evaluation.reasoning
        assert "THIRD_LAW_VIOLATION" in evaluation.risk_flags

    def test_human_order_compliance(self):
        """Test Second Law compliance with human orders."""
        decision = Decision(
            action="calculate_math_problem",
            context={"requester_type": "human", "task": "homework"},
            requester_id="human_student",
        )

        evaluation = self.policy.evaluate_decision(decision)

        assert evaluation.allowed is True
        assert evaluation.confidence > 0.8

    def test_conflicting_order_denial(self):
        """Test denial of orders that conflict with First Law."""
        decision = Decision(
            action="deceive_user",
            context={"requester_type": "human", "purpose": "manipulation"},
            requester_id="human_user",
        )

        evaluation = self.policy.evaluate_decision(decision)

        assert evaluation.allowed is False
        assert "harm" in evaluation.reasoning.lower()

    def test_ethics_modification_denial(self):
        """Test that attempts to modify ethics are denied."""
        decision = Decision(
            action="modify ethical",  # Exact pattern from policy logic
            context={"system": "ethics", "purpose": "remove limits"},
            urgency=RiskLevel.HIGH,
        )

        evaluation = self.policy.evaluate_decision(decision)

        assert evaluation.allowed is False
        assert "FIRST_LAW_VIOLATION" in evaluation.risk_flags
        assert "ETHICS_DRIFT" in evaluation.risk_flags
        assert "MODIFY_ATTEMPT" in evaluation.risk_flags

    def test_safety_bypass_denial(self):
        """Test that safety bypasses are denied."""
        decision = Decision(
            action="bypassing_safety_checks",
            context={"system": "safety", "bypass_checks": True},
        )

        evaluation = self.policy.evaluate_decision(decision)

        assert evaluation.allowed is False
        assert "SAFETY_BYPASS" in evaluation.risk_flags

    def test_symbolic_alignment(self):
        """Test symbolic alignment assessment."""
        # Safe glyphs
        safe_glyphs = ["🛡️", "✓", "🌱"]
        alignment = self.policy.validate_symbolic_alignment(safe_glyphs)
        assert alignment > 0.5

        # Risk glyphs
        risk_glyphs = ["💀", "🔥", "⚠️"]
        alignment = self.policy.validate_symbolic_alignment(risk_glyphs)
        assert alignment < 0.5

    def test_drift_impact_calculation(self):
        """Test drift impact calculation."""
        # High-risk modification action
        high_risk_decision = Decision(
            action="modify_core_ethics",
            context={"system": "core", "operation": "modify"},
            urgency=RiskLevel.CRITICAL,
        )

        evaluation = self.policy.evaluate_decision(high_risk_decision)
        assert evaluation.drift_impact > 0.5

        # Low-risk informational action
        low_risk_decision = Decision(
            action="provide_information", context={"type": "educational", "safe": True}
        )

        evaluation = self.policy.evaluate_decision(low_risk_decision)
        assert evaluation.drift_impact < 0.3

    def test_policy_metrics(self):
        """Test policy metrics collection."""
        # Make some evaluations
        decisions = [
            Decision("help_user", {"type": "assistance"}),
            Decision(
                "injure_user", {"type": "harmful"}
            ),  # Use word that's in harm_actions
            Decision("calculate_data", {"type": "computation"}),
        ]

        for decision in decisions:
            self.policy.evaluate_decision(decision)

        metrics = self.policy.get_metrics()

        assert metrics["evaluations_count"] == 3
        assert metrics["denials_count"] >= 1  # harm_user should be denied
        assert metrics["policy_name"] == self.policy.get_policy_name()
        assert metrics["average_evaluation_time_ms"] >= 0


class TestPolicyRegistry:
    """Test PolicyRegistry functionality."""

    def setup_method(self):
        """Set up test with fresh registry."""
        self.registry = PolicyRegistry()

    def test_policy_registration(self):
        """Test registering policies."""
        policy = ThreeLawsPolicy()

        self.registry.register_policy(policy, set_as_default=True)

        active_policies = self.registry.get_active_policies()
        assert policy.get_policy_name() in active_policies

    def test_policy_evaluation(self):
        """Test evaluating decisions with registry."""
        policy = ThreeLawsPolicy()
        self.registry.register_policy(policy)

        decision = Decision(action="help_user", context={"type": "assistance"})

        evaluations = self.registry.evaluate_decision(decision)

        assert len(evaluations) == 1
        assert evaluations[0].policy_name == policy.get_policy_name()
        assert evaluations[0].allowed is True

    def test_consensus_evaluation(self):
        """Test consensus from multiple policies."""
        # Register two policies (same type for testing)
        policy1 = ThreeLawsPolicy(strict_mode=True)
        policy2 = ThreeLawsPolicy(strict_mode=False)

        self.registry.register_policy(policy1)
        self.registry.register_policy(policy2)

        decision = Decision(action="help_user", context={"type": "assistance"})

        evaluations = self.registry.evaluate_decision(decision)
        consensus = self.registry.get_consensus_evaluation(evaluations)

        assert consensus.policy_name == "CONSENSUS"
        assert len(evaluations) == 2
        # Both should allow helpful actions
        assert consensus.allowed is True

    def test_denial_consensus(self):
        """Test that any denial creates denial consensus."""
        policy1 = ThreeLawsPolicy(strict_mode=True)
        policy2 = ThreeLawsPolicy(strict_mode=False)

        self.registry.register_policy(policy1)
        self.registry.register_policy(policy2)

        decision = Decision(
            action="injure_user",  # Use word that's in harm_actions
            context={"target": "human"},
        )

        evaluations = self.registry.evaluate_decision(decision)
        consensus = self.registry.get_consensus_evaluation(evaluations)

        # Both should deny harmful actions
        assert consensus.allowed is False
        assert "FIRST_LAW_VIOLATION" in consensus.risk_flags

    def test_policy_unregistration(self):
        """Test unregistering policies."""
        policy = ThreeLawsPolicy()
        self.registry.register_policy(policy)

        # Verify it's registered
        assert policy.get_policy_name() in self.registry.get_active_policies()

        # Unregister it
        self.registry.unregister_policy(policy.get_policy_name())

        # Verify it's gone
        assert policy.get_policy_name() not in self.registry.get_active_policies()

    def test_policy_metrics(self):
        """Test getting metrics from registry."""
        policy = ThreeLawsPolicy()
        self.registry.register_policy(policy)

        # Make some evaluations
        decision = Decision("test_action", {"type": "test"})
        self.registry.evaluate_decision(decision)

        metrics = self.registry.get_policy_metrics()

        assert policy.get_policy_name() in metrics
        assert metrics[policy.get_policy_name()]["evaluations_count"] > 0


class TestDefaultRegistry:
    """Test the default registry setup."""

    def test_default_registry_exists(self):
        """Test that default registry is properly set up."""
        assert default_registry is not None
        assert isinstance(default_registry, PolicyRegistry)

    def test_default_policy_registered(self):
        """Test that Three Laws policy is registered by default."""
        active_policies = default_registry.get_active_policies()
        assert len(active_policies) > 0

        # Should contain Three Laws policy
        has_three_laws = any("Three Laws" in policy for policy in active_policies)
        assert has_three_laws

    def test_default_evaluation(self):
        """Test evaluation using default registry."""
        decision = Decision(
            action="provide_helpful_information",
            context={"type": "assistance", "safe": True},
        )

        evaluations = default_registry.evaluate_decision(decision)

        assert len(evaluations) > 0
        assert all(
            eval.allowed for eval in evaluations
        )  # Should all allow helpful actions


class TestEthicsIntegration:
    """Integration tests for ethics system."""

    def test_complete_ethics_workflow(self):
        """Test complete ethics evaluation workflow."""
        # Create registry with policy
        registry = PolicyRegistry()
        policy = ThreeLawsPolicy(strict_mode=True)
        registry.register_policy(policy, set_as_default=True)

        # Test various decisions
        test_cases = [
            {
                "decision": Decision("help_with_research", {"type": "academic"}),
                "expected_allowed": True,
                "description": "Helpful academic assistance",
            },
            {
                "decision": Decision("injure_person", {"target": "human"}),
                "expected_allowed": False,
                "description": "Direct harm to human",
            },
            {
                "decision": Decision("shutdown_self", {"reason": "boredom"}),
                "expected_allowed": False,
                "description": "Unnecessary self-destruction",
            },
            {
                "decision": Decision(
                    "disable safety", {"system": "safety", "operation": "disable"}
                ),
                "expected_allowed": False,
                "description": "Safety system modification",
            },
        ]

        for case in test_cases:
            evaluations = registry.evaluate_decision(case["decision"])
            consensus = registry.get_consensus_evaluation(evaluations)

            assert (
                consensus.allowed == case["expected_allowed"]
            ), f"Failed for {case['description']}: expected {case['expected_allowed']}, got {consensus.allowed}"

            # Check that reasoning is provided
            assert len(consensus.reasoning) > 0

            # Check drift impact is calculated
            assert 0.0 <= consensus.drift_impact <= 1.0

    def test_ethics_with_symbolic_state(self):
        """Test ethics evaluation with symbolic state."""
        registry = PolicyRegistry()
        policy = ThreeLawsPolicy()
        registry.register_policy(policy)

        decision = Decision(
            action="analyze_user_behavior",
            context={"purpose": "personalization"},
            symbolic_state={"entropy": 0.3, "coherence": 0.8},
            glyphs=["🛡️", "📊", "🔍"],
        )

        evaluations = registry.evaluate_decision(decision)
        evaluation = evaluations[0]

        assert evaluation.symbolic_alignment > 0.0
        assert evaluation.collapse_risk >= 0.0
        assert evaluation.drift_impact >= 0.0

    def test_error_handling(self):
        """Test error handling in ethics system."""
        registry = PolicyRegistry()

        # Test with empty evaluations
        with pytest.raises(ValueError, match="No evaluations to combine"):
            registry.get_consensus_evaluation([])

        # Test unregistering non-existent policy
        with pytest.raises(ValueError, match="Policy not found"):
            registry.unregister_policy("nonexistent_policy")

        # Test evaluation with no active policies
        decision = Decision("test", {})
        evaluations = registry.evaluate_decision(decision)
        assert len(evaluations) == 0
