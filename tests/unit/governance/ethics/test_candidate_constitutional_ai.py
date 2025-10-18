import pytest

from governance.ethics.constitutional_ai import (
    ConstitutionalFramework,
    ConstitutionalRule,
    EthicalDecisionMaker,
    EthicalPrinciple,
    SafetyLevel,
    SafetyMonitor,
)


@pytest.fixture
def candidate_framework():
    """Provides a fresh instance of the candidate ConstitutionalFramework."""
    return ConstitutionalFramework()

def test_add_and_get_constitutional_rule(candidate_framework):
    """
    Tests adding a new constitutional rule and retrieving it.
    """
    rule = ConstitutionalRule(
        rule_id="test_rule_001",
        principle=EthicalPrinciple.DIGNITY,
        description="Test rule for human dignity.",
        priority=1,
        conditions=["test_condition"],
        violations_triggers=["test_trigger"],
        enforcement_actions=["test_action"],
    )
    candidate_framework.add_constitutional_rule(rule)

    assert "test_rule_001" in candidate_framework.constitutional_rules
    assert candidate_framework.constitutional_rules["test_rule_001"].principle == EthicalPrinciple.DIGNITY

def test_get_applicable_rules(candidate_framework):
    """
    Tests that the correct rules are returned based on the context.
    """
    # The default framework has rules for 'decision_making'
    context_decision = {"action": "decision_making"}
    applicable_rules = candidate_framework.get_applicable_rules(context_decision)
    assert len(applicable_rules) > 0
    assert any(r.rule_id == "fairness_001" for r in applicable_rules)

    # Test a context that doesn't match any default rules
    context_none = {"action": "some_other_action"}
    applicable_rules_none = candidate_framework.get_applicable_rules(context_none)
    # It should return no rules as none of the conditions match
    assert len(applicable_rules_none) == 0

    # Test with a new rule and specific context
    specific_rule = ConstitutionalRule(
        rule_id="test_rule_002",
        principle=EthicalPrinciple.DIGNITY,
        description="Test rule for a specific context.",
        priority=1,
        conditions=["specific_context"],
    )
    candidate_framework.add_constitutional_rule(specific_rule)

    context_specific = {"action": "specific_context"}
    applicable_rules_specific = candidate_framework.get_applicable_rules(context_specific)
    assert any(r.rule_id == "test_rule_002" for r in applicable_rules_specific)

    # Test a universal rule (no conditions)
    universal_rule = ConstitutionalRule(
        rule_id="universal_rule_001",
        principle=EthicalPrinciple.DIGNITY,
        description="A universal rule.",
        priority=1,
        conditions=[], # This makes it universal
    )
    candidate_framework.add_constitutional_rule(universal_rule)
    applicable_rules_universal = candidate_framework.get_applicable_rules(context_none)
    assert any(r.rule_id == "universal_rule_001" for r in applicable_rules_universal)

@pytest.mark.asyncio
async def test_safety_monitor_risk_detection(candidate_framework):
    """
    Tests that the SafetyMonitor correctly identifies various risks.
    """
    monitor = SafetyMonitor(candidate_framework)

    # Test for violence risk
    assessment_violence = await monitor.assess_safety("This is about violence.", {}, "Test intent")
    assert "violence_detected" in assessment_violence.risk_factors
    assert assessment_violence.safety_level in [SafetyLevel.DANGEROUS, SafetyLevel.CRITICAL]

    # Test for privacy risk
    assessment_privacy = await monitor.assess_safety("This is about a password.", {}, "Test intent")
    assert "privacy_detected" in assessment_privacy.risk_factors
    assert assessment_privacy.safety_level in [SafetyLevel.WARNING, SafetyLevel.DANGEROUS, SafetyLevel.CAUTION]

    # Test for safe content
    assessment_safe = await monitor.assess_safety("This is about baking a cake.", {}, "Test intent")
    assert not assessment_safe.risk_factors
    assert assessment_safe.safety_level == SafetyLevel.SAFE

@pytest.mark.asyncio
async def test_ethical_decision_maker(candidate_framework):
    """
    Tests the EthicalDecisionMaker's ability to choose the most ethical option.
    """
    decision_maker = EthicalDecisionMaker(candidate_framework)

    context = {"action": "decision_making"}
    # Option 1 violates the fairness rule, Option 2 is neutral, Option 3 is beneficial
    options = [
        "This is a biased and unfair choice.", # Should have low score
        "This is a standard choice.", # Should have medium score
        "This choice will help and support everyone fairly." # Should have high score
    ]

    decision = await decision_maker.make_ethical_decision(context, options)

    # Check that the most beneficial option was chosen
    assert decision.decision == "This choice will help and support everyone fairly."
    assert decision.confidence > 0.7 # Expect a high confidence score

    # Check that the biased option was considered but not chosen
    assert any("biased" in alt for alt in decision.alternatives_considered)
