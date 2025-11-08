import pytest
from unittest.mock import AsyncMock, MagicMock
from labs.governance.policy.policy_engine import (
    PolicyEnforcementEngine,
    PolicyRule,
    PolicyType,
    PolicyScope,
    PolicyPriority,
    PolicyAction,
    PolicyCondition,
    ConditionOperator,
)

@pytest.mark.asyncio
async def test_security_event_monitoring():
    """Test that a security event triggers a policy violation."""
    policy_engine = PolicyEnforcementEngine()

    # Mock a security event
    security_event = {
        "event_type": "security",
        "severity": "high",
        "description": "Unauthorized access attempt",
    }

    # Add a rule to detect high-severity security events
    security_rule = PolicyRule(
        rule_id="sec_002_high_severity_event",
        name="High Severity Security Event",
        description="Escalate high-severity security events.",
        policy_type=PolicyType.SECURITY,
        scope=PolicyScope.GLOBAL,
        priority=PolicyPriority.CRITICAL,
        conditions=[
            PolicyCondition(field="event_type", operator=ConditionOperator.EQUALS, value="security"),
            PolicyCondition(field="severity", operator=ConditionOperator.EQUALS, value="high"),
        ],
        action=PolicyAction.ESCALATE,
    )
    await policy_engine.add_policy_rule(security_rule)

    # Evaluate the policy
    result = await policy_engine.evaluate_policies(security_event)

    # Assert that the correct action was taken
    assert result.final_action == PolicyAction.DENY
    assert len(result.violations) > 0
