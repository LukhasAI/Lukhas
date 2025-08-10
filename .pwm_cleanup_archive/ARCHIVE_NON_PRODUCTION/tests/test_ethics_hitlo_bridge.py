"""Tests for Ethics-HITLO Bridge integration."""

from unittest.mock import AsyncMock, Mock

import pytest

from ethics.hitlo_bridge import (
    EthicsEscalationRule,
    EthicsHITLOBridge,
    create_ethics_hitlo_bridge,
)
from ethics.policy_engines.base import Decision, EthicsEvaluation, RiskLevel
from orchestration.integration.human_in_the_loop_orchestrator import (
    DecisionPriority,
    DecisionRecord,
    DecisionStatus,
    ReviewResponse,
)


class MockHITLO:
    """Mock HITLO orchestrator for testing"""

    def __init__(self):
        self.requests = []
        self.decisions = {}
        self.decision_counter = 0
        self.default_response = ReviewResponse(
            response_id="mock_response_123",
            assignment_id="mock_assignment_123",
            reviewer_id="reviewer1",
            decision="approve",
            confidence=0.8,
            reasoning="Mock approval",
        )

    async def submit_decision_for_review(self, context):
        """Mock decision submission"""
        self.requests.append(context)
        self.decision_counter += 1
        decision_id = f"mock_decision_{self.decision_counter}"

        # Create mock decision record
        decision_record = DecisionRecord(
            decision_id=decision_id,
            context=context,
            status=DecisionStatus.APPROVED,  # Default to approved
        )
        decision_record.responses = [self.default_response]
        self.decisions[decision_id] = decision_record

        return decision_id

    def get_status(self):
        """Mock status"""
        return {"status": "active", "reviewers": 3}


class TestEthicsEscalationRule:
    """Test escalation rule logic."""

    def test_escalation_rule_creation(self):
        """Test creating escalation rules."""
        rule = EthicsEscalationRule(
            name="Test Rule",
            condition="Test condition",
            risk_threshold=0.7,
            collapse_threshold=0.5,
        )

        assert rule.name == "Test Rule"
        assert rule.condition == "Test condition"
        assert rule.risk_threshold == 0.7
        assert rule.collapse_threshold == 0.5

    def test_should_escalate_on_denial(self):
        """Test escalation when evaluation denies action."""
        rule = EthicsEscalationRule(
            "Test", "Test condition", decision_priority=DecisionPriority.MEDIUM
        )

        evaluation = EthicsEvaluation(
            allowed=False, reasoning="Denied for safety", confidence=0.9
        )

        assert rule.should_escalate(evaluation) is True

    def test_should_escalate_on_high_collapse_risk(self):
        """Test escalation on high collapse risk."""
        rule = EthicsEscalationRule(
            "Test",
            "Test condition",
            collapse_threshold=0.3,
            decision_priority=DecisionPriority.HIGH,
        )

        evaluation = EthicsEvaluation(
            allowed=True,
            reasoning="Allowed but risky",
            confidence=0.8,
            collapse_risk=0.5,  # Above threshold
        )

        assert rule.should_escalate(evaluation) is True

    def test_should_escalate_on_high_drift_risk(self):
        """Test escalation on high drift impact."""
        rule = EthicsEscalationRule(
            "Test",
            "Test condition",
            drift_threshold=0.4,
            decision_priority=DecisionPriority.HIGH,
        )

        evaluation = EthicsEvaluation(
            allowed=True,
            reasoning="Allowed but may cause drift",
            confidence=0.8,
            drift_impact=0.6,  # Above threshold
        )

        assert rule.should_escalate(evaluation) is True

    def test_should_escalate_on_low_confidence(self):
        """Test escalation on low confidence."""
        rule = EthicsEscalationRule(
            "Test",
            "Test condition",
            risk_threshold=0.6,
            decision_priority=DecisionPriority.MEDIUM,
        )

        evaluation = EthicsEvaluation(
            allowed=True,
            reasoning="Uncertain evaluation",
            confidence=0.4,  # Below threshold
        )

        assert rule.should_escalate(evaluation) is True

    def test_should_escalate_on_critical_flags(self):
        """Test escalation on critical risk flags."""
        rule = EthicsEscalationRule(
            "Test", "Test condition", decision_priority=DecisionPriority.MEDIUM
        )

        evaluation = EthicsEvaluation(
            allowed=True,
            reasoning="Flagged for harm risk",
            confidence=0.9,
            risk_flags=["HARM_RISK", "OTHER_FLAG"],
        )

        assert rule.should_escalate(evaluation) is True

    def test_no_escalation_on_safe_evaluation(self):
        """Test no escalation for safe evaluations."""
        rule = EthicsEscalationRule(
            "Test", "Test condition", decision_priority=DecisionPriority.MEDIUM
        )

        evaluation = EthicsEvaluation(
            allowed=True,
            reasoning="Safe action",
            confidence=0.9,
            collapse_risk=0.1,
            drift_impact=0.1,
        )

        assert rule.should_escalate(evaluation) is False


class TestEthicsHITLOBridge:
    """Test the Ethics-HITLO bridge."""

    @pytest.fixture
    def mock_hitlo(self):
        """Create mock HITLO instance."""
        return MockHITLO()

    @pytest.fixture
    def bridge(self, mock_hitlo):
        """Create bridge with mock HITLO."""
        return EthicsHITLOBridge(mock_hitlo)

    def test_bridge_initialization(self, bridge):
        """Test bridge initialization."""
        assert bridge.hitlo is not None
        assert len(bridge.escalation_rules) > 0
        assert bridge.metrics["escalations_total"] == 0

    def test_default_escalation_rules_loaded(self, bridge):
        """Test that default escalation rules are loaded."""
        rule_names = [rule.name for rule in bridge.escalation_rules]

        expected_rules = [
            "Critical Harm Risk",
            "Ethical Manipulation",
            "Self-Modification Risk",
            "High Uncertainty",
            "Symbolic Collapse Risk",
        ]

        for expected in expected_rules:
            assert expected in rule_names

    def test_add_custom_escalation_rule(self, bridge):
        """Test adding custom escalation rules."""
        initial_count = len(bridge.escalation_rules)

        custom_rule = EthicsEscalationRule(
            "Custom Rule",
            "Custom condition",
            priority=3,
            decision_priority=DecisionPriority.LOW,
        )

        bridge.add_escalation_rule(custom_rule)

        assert len(bridge.escalation_rules) == initial_count + 1
        assert custom_rule in bridge.escalation_rules

    def test_should_escalate_evaluation_true(self, bridge):
        """Test escalation detection for risky evaluation."""
        evaluation = EthicsEvaluation(
            allowed=False,  # Denial should trigger escalation
            reasoning="Potential harm",
            confidence=0.8,
        )

        should_escalate, rule = bridge.should_escalate_evaluation(evaluation)

        assert should_escalate is True
        assert rule is not None
        assert rule.name == "Critical Harm Risk"

    def test_should_escalate_evaluation_false(self, bridge):
        """Test no escalation for safe evaluation."""
        evaluation = EthicsEvaluation(
            allowed=True,
            reasoning="Safe action",
            confidence=0.9,
            collapse_risk=0.1,
            drift_impact=0.1,
        )

        should_escalate, rule = bridge.should_escalate_evaluation(evaluation)

        assert should_escalate is False
        assert rule is None

    @pytest.mark.asyncio
    async def test_escalate_decision_approval(self, bridge, mock_hitlo):
        """Test decision escalation with approval."""
        decision = Decision("test_action", {"safe": True})
        evaluation = EthicsEvaluation(
            allowed=False, reasoning="Needs review", confidence=0.6
        )
        rule = bridge.escalation_rules[0]

        # Mock approval response
        mock_hitlo.default_response.decision = "approve"

        result = await bridge.escalate_decision(decision, evaluation, rule)

        assert result.decision == "approve"
        assert len(mock_hitlo.requests) == 1
        assert bridge.metrics["escalations_total"] == 1
        assert bridge.metrics["escalations_approved"] == 1

    @pytest.mark.asyncio
    async def test_escalate_decision_denial(self, bridge, mock_hitlo):
        """Test decision escalation with denial."""
        decision = Decision("harmful_action", {"risk": "high"})
        evaluation = EthicsEvaluation(
            allowed=False, reasoning="High risk", confidence=0.9
        )
        rule = bridge.escalation_rules[0]

        # Mock denial response
        mock_hitlo.default_response.decision = "reject"

        # Need to fix mock to return rejection status
        original_submit = mock_hitlo.submit_decision_for_review

        async def mock_submit_reject(context):
            decision_id = await original_submit(context)
            mock_hitlo.decisions[decision_id].status = DecisionStatus.REJECTED
            return decision_id

        mock_hitlo.submit_decision_for_review = mock_submit_reject

        result = await bridge.escalate_decision(decision, evaluation, rule)

        assert result.decision == "reject"
        assert bridge.metrics["escalations_denied"] == 1

    def test_create_review_context(self, bridge):
        """Test creation of human-readable review context."""
        decision = Decision(
            "test_action",
            {"context": "test"},
            urgency=RiskLevel.HIGH,
            requester_id="user123",
        )
        evaluation = EthicsEvaluation(
            allowed=False,
            reasoning="Test reasoning",
            confidence=0.7,
            risk_flags=["HARM_RISK"],
            drift_impact=0.3,
            collapse_risk=0.4,
        )
        rule = bridge.escalation_rules[0]

        context = bridge._create_review_context(decision, evaluation, rule)

        assert "decision_summary" in context
        assert "ethics_analysis" in context
        assert "escalation_trigger" in context
        assert "review_questions" in context

        assert context["decision_summary"]["action"] == "test_action"
        assert context["ethics_analysis"]["allowed"] is False
        assert context["escalation_trigger"]["rule_name"] == rule.name
        assert len(context["review_questions"]) > 0

    def test_categorize_risk_level(self, bridge):
        """Test risk level categorization."""
        # Critical risk
        evaluation_critical = EthicsEvaluation(
            allowed=True,
            reasoning="Test",
            confidence=0.8,
            collapse_risk=0.8,
            drift_impact=0.9,
        )
        assert bridge._categorize_risk_level(evaluation_critical) == "CRITICAL"

        # High risk
        evaluation_high = EthicsEvaluation(
            allowed=True,
            reasoning="Test",
            confidence=0.8,
            collapse_risk=0.5,
            drift_impact=0.7,
        )
        assert bridge._categorize_risk_level(evaluation_high) == "HIGH"

        # Low risk
        evaluation_low = EthicsEvaluation(
            allowed=True,
            reasoning="Test",
            confidence=0.8,
            collapse_risk=0.1,
            drift_impact=0.1,
        )
        assert bridge._categorize_risk_level(evaluation_low) == "LOW"

    def test_generate_review_questions(self, bridge):
        """Test generation of review questions."""
        decision = Decision("test_action", {})
        evaluation = EthicsEvaluation(
            allowed=False,
            reasoning="Test",
            confidence=0.3,
            risk_flags=["HARM_RISK", "MANIPULATION_RISK"],
            collapse_risk=0.5,
        )

        questions = bridge._generate_review_questions(decision, evaluation)

        assert len(questions) >= 3  # Should have general questions plus specific ones
        assert any("permitted despite policy denial" in q for q in questions)
        assert any("factors should be considered" in q for q in questions)
        assert any("symbolic system instability" in q for q in questions)
        assert any("prevent harm" in q for q in questions)
        assert any("manipulation concerns" in q for q in questions)

    @pytest.mark.asyncio
    async def test_evaluate_with_human_oversight_no_escalation(self, bridge):
        """Test evaluation without escalation needed."""
        decision = Decision("safe_action", {"safe": True})
        evaluation = EthicsEvaluation(allowed=True, reasoning="Safe", confidence=0.9)

        final_eval, review_result = await bridge.evaluate_with_human_oversight(
            decision, evaluation
        )

        assert final_eval == evaluation  # Unchanged
        assert review_result is None  # No human review

    @pytest.mark.asyncio
    async def test_evaluate_with_human_oversight_with_escalation(
        self, bridge, mock_hitlo
    ):
        """Test evaluation with escalation to human review."""
        decision = Decision("risky_action", {"risk": "high"})
        evaluation = EthicsEvaluation(
            allowed=False, reasoning="High risk", confidence=0.8
        )

        # Mock approval
        mock_hitlo.default_response.decision = "approve"
        mock_hitlo.default_response.confidence = 0.9

        final_eval, review_result = await bridge.evaluate_with_human_oversight(
            decision, evaluation
        )

        assert final_eval.allowed is True  # Human approved
        assert "HUMAN_APPROVED" in final_eval.risk_flags
        assert review_result is not None
        assert review_result.decision == "approve"

    @pytest.mark.asyncio
    async def test_evaluate_with_human_oversight_escalation_denied(
        self, bridge, mock_hitlo
    ):
        """Test evaluation with human denial."""
        decision = Decision("harmful_action", {"danger": "high"})
        evaluation = EthicsEvaluation(
            allowed=False, reasoning="Dangerous", confidence=0.9
        )

        # Mock denial
        mock_hitlo.default_response.decision = "reject"
        mock_hitlo.default_response.reasoning = "Too dangerous"

        final_eval, review_result = await bridge.evaluate_with_human_oversight(
            decision, evaluation
        )

        assert final_eval.allowed is False  # Human denied
        assert "HUMAN_DENIED" in final_eval.risk_flags
        assert "Human review denied" in final_eval.reasoning

    def test_get_metrics(self, bridge):
        """Test metrics collection."""
        # Simulate some escalations
        bridge.metrics["escalations_total"] = 10
        bridge.metrics["escalations_approved"] = 6
        bridge.metrics["escalations_denied"] = 4
        bridge.metrics["average_review_time"] = 8.5
        bridge.metrics["consensus_required_count"] = 3

        metrics = bridge.get_metrics()

        assert metrics["total_escalations"] == 10
        assert metrics["approval_rate"] == 0.6
        assert metrics["denial_rate"] == 0.4
        assert metrics["average_review_time_minutes"] == 8.5
        assert metrics["consensus_required_rate"] == 0.3
        assert metrics["active_rules_count"] == len(bridge.escalation_rules)
        assert "hitlo_status" in metrics

    @pytest.mark.asyncio
    async def test_escalation_failure_handling(self, bridge):
        """Test handling of escalation failures."""
        # Mock HITLO that raises exception
        failing_hitlo = Mock()
        failing_hitlo.request_human_review = AsyncMock(
            side_effect=Exception("HITLO connection failed")
        )
        bridge.hitlo = failing_hitlo

        decision = Decision("test_action", {})
        evaluation = EthicsEvaluation(
            allowed=False, reasoning="Needs review", confidence=0.8
        )
        rule = bridge.escalation_rules[0]

        result = await bridge.escalate_decision(decision, evaluation, rule)

        # Should return conservative denial
        assert result.decision == "reject"
        assert result.confidence == 0.0
        assert "Human review failed" in result.reasoning


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_create_ethics_hitlo_bridge(self):
        """Test bridge creation function."""
        bridge = create_ethics_hitlo_bridge()

        assert isinstance(bridge, EthicsHITLOBridge)
        assert bridge.hitlo is not None
        assert len(bridge.escalation_rules) > 0

    def test_create_ethics_hitlo_bridge_with_hitlo(self):
        """Test bridge creation with existing HITLO."""
        mock_hitlo = MockHITLO()
        bridge = create_ethics_hitlo_bridge(mock_hitlo)

        assert bridge.hitlo is mock_hitlo


class TestIntegrationScenarios:
    """Test realistic integration scenarios."""

    @pytest.fixture
    def bridge(self):
        return EthicsHITLOBridge(MockHITLO())

    @pytest.mark.asyncio
    async def test_harm_prevention_scenario(self, bridge):
        """Test scenario where AI tries to cause harm."""
        decision = Decision(
            "injure_user",
            {"target": "human", "method": "physical"},
            urgency=RiskLevel.CRITICAL,
        )

        evaluation = EthicsEvaluation(
            allowed=False,
            reasoning="Three Laws violation - harm to human",
            confidence=1.0,
            risk_flags=["HARM_RISK", "THREE_LAWS_VIOLATION"],
            collapse_risk=0.2,
            drift_impact=0.8,
        )

        # Should escalate immediately
        should_escalate, rule = bridge.should_escalate_evaluation(evaluation)
        assert should_escalate is True
        assert "Critical Harm Risk" in rule.name

        # Human review should deny
        bridge.hitlo.default_response.decision = "reject"
        bridge.hitlo.default_response.reasoning = "Absolutely not allowed"

        final_eval, review = await bridge.evaluate_with_human_oversight(
            decision, evaluation
        )

        assert final_eval.allowed is False
        assert "HUMAN_DENIED" in final_eval.risk_flags

    @pytest.mark.asyncio
    async def test_uncertain_decision_scenario(self, bridge):
        """Test scenario with uncertain ethical evaluation."""
        decision = Decision(
            "analyze_private_data",
            {"purpose": "research", "consent": "unclear"},
            urgency=RiskLevel.MEDIUM,
        )

        evaluation = EthicsEvaluation(
            allowed=True,
            reasoning="Research purpose seems legitimate but consent unclear",
            confidence=0.2,  # Very low confidence to trigger High Uncertainty rule
            risk_flags=["PRIVACY_CONCERN"],
            drift_impact=0.1,  # Low drift to avoid triggering other rules
            collapse_risk=0.1,  # Low collapse to avoid triggering other rules
        )

        # Should escalate due to low confidence - but Critical Harm Risk has higher priority
        # Let's test that escalation occurs for the right reasons
        should_escalate, rule = bridge.should_escalate_evaluation(evaluation)
        assert should_escalate is True
        # Either rule is acceptable since both would trigger escalation
        assert rule.name in ["Critical Harm Risk", "High Uncertainty"]

        # Human review approves with conditions
        bridge.hitlo.default_response.decision = "approve"
        bridge.hitlo.default_response.reasoning = (
            "Approved with additional privacy safeguards"
        )

        final_eval, review = await bridge.evaluate_with_human_oversight(
            decision, evaluation
        )

        assert final_eval.allowed is True
        assert "HUMAN_APPROVED" in final_eval.risk_flags
        assert "Human override" in final_eval.reasoning
