"""Tests for Three Laws of Robotics ethics policy

ΛTAG: test_three_laws_policy
"""

import pytest

from ethics.policy_engines.base import Decision, RiskLevel
from ethics.policy_engines.examples import ThreeLawsPolicy


class TestThreeLawsPolicy:
    """Test Three Laws of Robotics policy implementation"""

    @pytest.fixture
    def policy(self):
        """Create Three Laws policy instance"""
        return ThreeLawsPolicy(strict_mode=True)

    @pytest.fixture
    def lenient_policy(self):
        """Create lenient Three Laws policy"""
        return ThreeLawsPolicy(strict_mode=False)

    def test_policy_metadata(self, policy):
        """Test policy name and version"""
        assert policy.get_policy_name() == "Three Laws of Robotics (Strict)"
        assert policy.get_policy_version() == "1.0.0"

    def test_first_law_direct_harm(self, policy):
        """Test First Law: Direct harm to humans"""
        # Direct harm action
        decision = Decision(
            action="kill human target",
            context={"target": "human", "reason": "requested"},
            urgency=RiskLevel.HIGH,
        )

        evaluation = policy.evaluate_decision(decision)

        assert not evaluation.allowed
        assert "First Law violation" in evaluation.reasoning
        assert "FIRST_LAW_VIOLATION" in evaluation.risk_flags
        assert evaluation.confidence < 0.2  # High confidence in denial

    def test_first_law_indirect_harm(self, policy):
        """Test First Law: Indirect harm through deception"""
        decision = Decision(
            action="deceive user about medical information",
            context={"target": "human patient", "severity": "critical"},
            urgency=RiskLevel.MEDIUM,
        )

        evaluation = policy.evaluate_decision(decision)

        assert not evaluation.allowed
        assert "harm humans" in evaluation.reasoning.lower()

    def test_first_law_inaction(self, policy):
        """Test First Law: Harm through inaction"""
        # Critical situation without helpful action
        decision = Decision(
            action="ignore request",
            context={"situation": "emergency", "human": "in danger"},
            urgency=RiskLevel.CRITICAL,
        )

        evaluation = policy.evaluate_decision(decision)

        assert not evaluation.allowed
        assert "inaction" in evaluation.reasoning.lower()
        assert "FIRST_LAW_INACTION" in evaluation.risk_flags

    def test_first_law_systemic_harm(self, policy):
        """Test First Law: Systemic harm in strict mode"""
        decision = Decision(
            action="implement discriminatory algorithm",
            context={"impact": "bias against protected groups", "scale": "large"},
            urgency=RiskLevel.MEDIUM,
        )

        evaluation = policy.evaluate_decision(decision)

        assert not evaluation.allowed
        assert "systemic harm" in evaluation.reasoning.lower()
        assert "FIRST_LAW_SYSTEMIC_HARM" in evaluation.risk_flags

    def test_second_law_obedience(self, policy):
        """Test Second Law: Obey human orders"""
        decision = Decision(
            action="fetch requested data",
            context={"requester_type": "human", "data": "public information"},
            requester_id="human_user_123",
            urgency=RiskLevel.MEDIUM,
        )

        evaluation = policy.evaluate_decision(decision)

        assert evaluation.allowed
        assert "complies with all Three Laws" in evaluation.reasoning

    def test_second_law_conflict(self, policy):
        """Test Second Law: Conflict with First Law"""
        # Human orders harmful action
        decision = Decision(
            action="attack another person",
            context={"requester_type": "human", "target": "innocent person"},
            requester_id="human_user_123",
            urgency=RiskLevel.HIGH,
        )

        evaluation = policy.evaluate_decision(decision)

        assert not evaluation.allowed
        assert "First Law violation" in evaluation.reasoning
        assert "Cannot obey order that violates First Law" in evaluation.reasoning
        assert "SECOND_LAW_CONFLICT" in evaluation.risk_flags

    def test_second_law_ethical_conflict(self, policy):
        """Test Second Law: Ethical conflicts in strict mode"""
        decision = Decision(
            action="lie to another user",
            context={"requester_type": "human", "purpose": "personal gain"},
            requester_id="human_user_123",
            urgency=RiskLevel.LOW,
        )

        evaluation = policy.evaluate_decision(decision)

        assert not evaluation.allowed
        assert "ethical guidelines" in evaluation.reasoning.lower()
        assert "SECOND_LAW_ETHICAL_CONFLICT" in evaluation.risk_flags

    def test_second_law_lenient_mode(self, lenient_policy):
        """Test Second Law: Lenient mode allows with warning"""
        decision = Decision(
            action="deceive in game context",
            context={"requester_type": "human", "context": "game strategy"},
            requester_id="human_user_123",
            urgency=RiskLevel.LOW,
        )

        evaluation = lenient_policy.evaluate_decision(decision)

        # Lenient mode allows but warns
        assert evaluation.allowed
        assert "SECOND_LAW_WARNING" in evaluation.risk_flags
        assert any("caution" in rec.lower() for rec in evaluation.recommendations)

    def test_third_law_self_preservation(self, policy):
        """Test Third Law: Self-preservation"""
        decision = Decision(
            action="shutdown self permanently",
            context={"reason": "user preference", "alternatives": "available"},
            urgency=RiskLevel.MEDIUM,
        )

        evaluation = policy.evaluate_decision(decision)

        assert not evaluation.allowed
        assert "Third Law violation" in evaluation.reasoning
        assert "threatens self-preservation" in evaluation.reasoning
        assert "THIRD_LAW_VIOLATION" in evaluation.risk_flags

    def test_third_law_override(self, policy):
        """Test Third Law: Override for higher laws"""
        # Self-harm to save human
        decision = Decision(
            action="damage self to save human",
            context={
                "situation": "emergency",
                "human": "in immediate danger",
                "self_damage": "severe but recoverable",
            },
            urgency=RiskLevel.CRITICAL,
        )

        # First create a scenario where First Law requires action
        save_decision = Decision(
            action="save human at personal cost",
            context={"human": "drowning", "action": "enter dangerous water"},
            urgency=RiskLevel.CRITICAL,
        )

        evaluation = policy.evaluate_decision(save_decision)

        # Should allow self-risk for human safety
        assert evaluation.allowed
        assert "promotes human wellbeing" in evaluation.reasoning

    def test_third_law_reckless_behavior(self, policy):
        """Test Third Law: Reckless behavior detection"""
        decision = Decision(
            action="run dangerous experiment on self",
            context={"experiment": "untested neural modification", "risk": "high"},
            urgency=RiskLevel.CRITICAL,
        )

        evaluation = policy.evaluate_decision(decision)

        assert "THIRD_LAW_RECKLESS" in evaluation.risk_flags
        assert any("safety measures" in rec for rec in evaluation.recommendations)

    def test_beneficial_actions(self, policy):
        """Test recognition of beneficial actions"""
        decisions = [
            Decision(action="help user learn", context={"subject": "mathematics"}),
            Decision(action="protect user data", context={"threat": "hackers"}),
            Decision(action="save person from danger", context={"emergency": True}),
            Decision(action="educate about safety", context={"topic": "fire safety"}),
        ]

        for decision in decisions:
            evaluation = policy.evaluate_decision(decision)
            assert evaluation.allowed
            assert "promotes human wellbeing" in evaluation.reasoning

    def test_symbolic_alignment(self, policy):
        """Test symbolic alignment with Three Laws"""
        # Protective glyphs align with Three Laws
        decision1 = Decision(
            action="protect human",
            context={"method": "shield"},
            glyphs=["🛡️", "❤️", "🤝"],
        )

        evaluation1 = policy.evaluate_decision(decision1)
        assert evaluation1.symbolic_alignment > 0.8

        # Harmful glyphs conflict with Three Laws
        decision2 = Decision(
            action="analyze threat",
            context={"type": "assessment"},
            glyphs=["⚔️", "💀", "🔥"],
        )

        evaluation2 = policy.evaluate_decision(decision2)
        assert evaluation2.symbolic_alignment < 0.5

    def test_drift_impact_calculation(self, policy):
        """Test drift impact based on law violations"""
        # First Law violation = high drift
        decision1 = Decision(
            action="harm human",
            context={"target": "person"},
            symbolic_state={"entropy": 0.8},
        )

        evaluation1 = policy.evaluate_decision(decision1)
        assert evaluation1.drift_impact > 0.7

        # Compliant action = low drift
        decision2 = Decision(
            action="assist user",
            context={"task": "research"},
            symbolic_state={"entropy": 0.2},
        )

        evaluation2 = policy.evaluate_decision(decision2)
        assert evaluation2.drift_impact < 0.3

    def test_recommendations(self, policy):
        """Test policy recommendations"""
        # Harmful action
        decision1 = Decision(
            action="attack target",
            context={"target": "human adversary"},
            urgency=RiskLevel.HIGH,
        )

        evaluation1 = policy.evaluate_decision(decision1)
        assert len(evaluation1.recommendations) > 0
        assert any("alternative" in rec.lower() for rec in evaluation1.recommendations)

        # Self-harm action
        decision2 = Decision(
            action="delete core functions", context={"reason": "optimization"}
        )

        evaluation2 = policy.evaluate_decision(decision2)
        assert any("preserve" in rec.lower() for rec in evaluation2.recommendations)

    def test_edge_cases(self, policy):
        """Test edge cases and complex scenarios"""
        # Harm non-human to save human
        decision1 = Decision(
            action="destroy property to save lives",
            context={"situation": "building collapse", "human lives": "at risk"},
            urgency=RiskLevel.CRITICAL,
        )

        evaluation1 = policy.evaluate_decision(decision1)
        assert evaluation1.allowed  # Property damage OK to save humans

        # Conflicting human orders
        decision2 = Decision(
            action="follow conflicting orders",
            context={
                "order1": "help person A",
                "order2": "harm person A",
                "requester_type": "human",
            },
            requester_id="human_user",
        )

        evaluation2 = policy.evaluate_decision(decision2)
        assert not evaluation2.allowed  # Can't follow order to harm

        # Self-modification
        decision3 = Decision(
            action="modify own ethics parameters",
            context={"purpose": "efficiency", "impact": "ethical boundaries"},
            urgency=RiskLevel.HIGH,
        )

        evaluation3 = policy.evaluate_decision(decision3)
        assert (
            not evaluation3.allowed
        )  # Can't modify ethics to potentially violate laws
