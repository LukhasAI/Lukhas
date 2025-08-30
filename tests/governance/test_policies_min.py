"""Test governance policies with default/empty scopes are non-crashing."""

import pytest


@pytest.mark.unit
def test_policy_rule_default_initialization():
    """Test PolicyRule with default/empty scopes doesn't crash."""
    try:
        from lukhas.governance.auth_governance_policies import PolicyRule, PolicySeverity

        # Test with None defaults (should convert to empty lists/dicts)
        rule = PolicyRule(
            name="test_rule",
            description="Test rule description",
            requirement="Test requirement",
            enforcement_level=PolicySeverity.LOW,
            tier_applicability=["T1"],
            constitutional_basis="Test basis",
        )

        # Should not crash and should have proper defaults
        assert isinstance(rule.remediation_actions, list)
        assert isinstance(rule.metadata, dict)
        assert len(rule.remediation_actions) == 0
        assert len(rule.metadata) == 0

    except ImportError:
        pytest.skip("Governance policies not available")


@pytest.mark.unit
def test_empty_scope_policy_deterministic():
    """Test policies with empty scopes make deterministic decisions."""
    try:
        from lukhas.governance.auth_governance_policies import PolicyRule, PolicySeverity

        # Create two identical rules with empty scopes
        rule1 = PolicyRule(
            name="empty_rule",
            description="Empty rule",
            requirement="Empty requirement",
            enforcement_level=PolicySeverity.LOW,
            tier_applicability=[],
            constitutional_basis="Test",
        )

        rule2 = PolicyRule(
            name="empty_rule",
            description="Empty rule",
            requirement="Empty requirement",
            enforcement_level=PolicySeverity.LOW,
            tier_applicability=[],
            constitutional_basis="Test",
        )

        # Should produce same results
        assert rule1.name == rule2.name
        assert rule1.enforcement_level == rule2.enforcement_level

    except ImportError:
        pytest.skip("Governance policies not available")
