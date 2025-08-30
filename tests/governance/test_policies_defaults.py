"""Test governance policies with minimal configurations."""

import pytest


def test_policy_engine_initialization():
    """Test policy engine initializes with defaults."""
    try:
        from lukhas.governance.auth_governance_policies import AuthGovernancePolicyEngine

        engine = AuthGovernancePolicyEngine()
        assert engine is not None
        assert hasattr(engine, "policy_rules")
        assert hasattr(engine, "policy_violations")

    except ImportError:
        pytest.skip("Governance policies not available")


def test_policy_assessment():
    """Test policy assessment creation."""
    try:
        from lukhas.governance.auth_governance_policies import PolicyAssessment, PolicySeverity

        assessment = PolicyAssessment(passed=True, severity=PolicySeverity.LOW, violations=[])
        assert assessment.passed is True
        assert assessment.severity == PolicySeverity.LOW

    except ImportError:
        pytest.skip("Governance policies not available")
