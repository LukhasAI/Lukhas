"""Tests for the core governance basic example integration."""

from core.governance.examples.basic import (
    BasicGovernanceEngine,
    GovernanceCase,
    build_default_engine,
    demo_decision_flow,
)


def test_build_default_engine_rules():
    engine = build_default_engine()
    assert isinstance(engine, BasicGovernanceEngine)
    assert len(engine.rules) == 3
    rule_ids = {rule.identifier for rule in engine.rules}
    assert "CRITICAL_ACTION" in rule_ids


def test_low_risk_case_is_approved():
    engine = build_default_engine()
    safe_case = GovernanceCase(actor_id="analyst-5", action="view_report", risk_score=0.12)

    result = engine.evaluate(safe_case)

    assert result.approved is True
    assert result.requires_review is False
    assert result.matched_rules == []


def test_demo_decision_flow_requires_review():
    result = demo_decision_flow()

    assert result.approved is False
    assert result.requires_review is True
    assert any(rule.identifier == "CRITICAL_ACTION" for rule in result.matched_rules)
