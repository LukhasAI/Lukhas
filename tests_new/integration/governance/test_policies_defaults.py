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
        from datetime import datetime, timezone

        from lukhas.governance.auth_governance_policies import PolicyAssessment

        # Using all required parameter names from the dataclass
        assessment = PolicyAssessment(
            compliant=True,
            violations=[],
            recommendations=[],
            risk_score=0.0,
            assessment_timestamp=datetime.now(timezone.utc),
        )
        assert assessment.compliant is True
        assert assessment.violations == []
        assert assessment.recommendations == []
        assert assessment.risk_score == 0.0

    except ImportError:
        pytest.skip("Governance policies not available")