import pytest
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

@pytest.fixture
def policy_engine():
    """Fixture for a PolicyEnforcementEngine instance."""
    return PolicyEnforcementEngine()

def test_initialization(policy_engine):
    """Test that the PolicyEnforcementEngine initializes correctly."""
    assert policy_engine is not None
    assert len(policy_engine.rule_engine.rules) > 0

@pytest.mark.asyncio
async def test_evaluate_policies_allow(policy_engine):
    """Test a simple case where an action is allowed."""
    context = {"user_tier": 1, "data_type": "public", "encrypted": True}
    result = await policy_engine.evaluate_policies(context)
    assert result.final_action == PolicyAction.ALLOW

@pytest.mark.asyncio
async def test_evaluate_policies_deny_encryption(policy_engine):
    """Test that a DENY action is triggered for unencrypted sensitive data."""
    context = {"data_type": "sensitive", "encrypted": False}
    result = await policy_engine.evaluate_policies(context)
    assert result.final_action == PolicyAction.DENY
    assert len(result.violations) == 1
    assert result.violations[0].rule_id == "sec_001_data_encryption"

@pytest.mark.asyncio
async def test_add_and_evaluate_custom_rule(policy_engine):
    """Test adding a custom rule and evaluating it."""
    custom_rule = PolicyRule(
        rule_id="custom_001",
        name="Block high-risk transactions",
        description="Block transactions with a risk score above 0.9.",
        policy_type=PolicyType.OPERATIONAL,
        scope=PolicyScope.TRANSACTION,
        priority=PolicyPriority.CRITICAL,
        conditions=[
            PolicyCondition(
                field="transaction_risk_score",
                operator=ConditionOperator.GREATER_THAN,
                value=0.9,
            )
        ],
        action=PolicyAction.DENY,
    )
    await policy_engine.add_policy_rule(custom_rule)

    context = {"transaction_risk_score": 0.95}
    result = await policy_engine.evaluate_policies(context, operation="transaction")

    assert result.final_action == PolicyAction.DENY
    assert len(result.violations) == 1
    assert result.violations[0].rule_id == "custom_001"

@pytest.mark.asyncio
async def test_update_policy_rule(policy_engine):
    """Test updating a policy rule."""
    rule_id = "sec_001_data_encryption"
    updates = {"priority": PolicyPriority.LOW}

    assert await policy_engine.update_policy_rule(rule_id, updates)

    updated_rule = policy_engine.rule_engine.rules[rule_id]
    assert updated_rule.priority == PolicyPriority.LOW

@pytest.mark.asyncio
async def test_disable_policy_rule(policy_engine):
    """Test disabling a policy rule."""
    rule_id = "sec_001_data_encryption"

    assert await policy_engine.disable_policy_rule(rule_id)

    context = {"data_type": "sensitive", "encrypted": False}
    result = await policy_engine.evaluate_policies(context)

    assert result.final_action == PolicyAction.ALLOW

@pytest.mark.asyncio
async def test_or_logic_in_conditions(policy_engine):
    """Test a rule with OR logic in its conditions."""
    custom_rule = PolicyRule(
        rule_id="custom_002",
        name="Flag suspicious activity",
        description="Flag activity from a high-risk country or with a high risk score.",
        policy_type=PolicyType.SECURITY,
        scope=PolicyScope.GLOBAL,
        priority=PolicyPriority.HIGH,
        conditions=[
            PolicyCondition(field="country", operator=ConditionOperator.EQUALS, value="riskistan"),
            PolicyCondition(field="risk_score", operator=ConditionOperator.GREATER_THAN, value=0.8),
        ],
        condition_logic="OR",
        action=PolicyAction.WARN,
    )
    await policy_engine.add_policy_rule(custom_rule)

    context = {"country": "riskistan", "risk_score": 0.5}
    result = await policy_engine.evaluate_policies(context)

    assert result.final_action == PolicyAction.WARN
    assert len(result.warnings) == 1

@pytest.mark.asyncio
async def test_export_policy_report(policy_engine):
    """Test the export_policy_report method."""
    report = await policy_engine.export_policy_report()

    assert "report_id" in report
    assert "generated_at" in report
    assert "policy_status" in report
    assert "active_policies" in report
    assert "violation_summary" in report

@pytest.mark.asyncio
async def test_assess_methods(policy_engine):
    """Test the _assess methods."""
    rule = PolicyRule(
        rule_id="test_rule",
        name="Test Rule",
        description="A rule for testing.",
        policy_type=PolicyType.PRIVACY,
        scope=PolicyScope.GLOBAL,
        priority=PolicyPriority.HIGH,
        action=PolicyAction.DENY,
    )
    context = {"user": "test_user"}

    identity_impact = await policy_engine._assess_identity_impact(rule, context)
    assert identity_impact is not None

    consciousness_impact = await policy_engine._assess_consciousness_impact(rule, context)
    assert consciousness_impact is None

    guardian_assessment = await policy_engine._assess_guardian_impact(rule, context)
    assert guardian_assessment is not None

@pytest.mark.asyncio
async def test_maintain_history_size(policy_engine):
    """Test that the history size is maintained correctly."""
    policy_engine.evaluation_history = list(range(10001))
    policy_engine.violation_history = list(range(5001))

    policy_engine._maintain_history_size()

    assert len(policy_engine.evaluation_history) == 10000
    assert len(policy_engine.violation_history) == 5000

@pytest.mark.asyncio
async def test_get_field_value_nested(policy_engine):
    """Test the _get_field_value method with nested context."""
    context = {"user": {"profile": {"age": 30}}}

    age = policy_engine.rule_engine._get_field_value(context, "user.profile.age")
    assert age == 30

    non_existent = policy_engine.rule_engine._get_field_value(context, "user.profile.name")
    assert non_existent is None

@pytest.mark.asyncio
async def test_determine_final_action(policy_engine):
    """Test the _determine_final_action method."""
    rule1 = PolicyRule(rule_id="rule1", name="Rule 1", action=PolicyAction.WARN, policy_type=PolicyType.OPERATIONAL, scope=PolicyScope.GLOBAL, priority=PolicyPriority.LOW, description="d", conditions=[PolicyCondition(field="some_condition", operator=ConditionOperator.EQUALS, value=True)])
    rule2 = PolicyRule(rule_id="rule2", name="Rule 2", action=PolicyAction.DENY, policy_type=PolicyType.OPERATIONAL, scope=PolicyScope.GLOBAL, priority=PolicyPriority.HIGH, description="d", conditions=[PolicyCondition(field="some_condition", operator=ConditionOperator.EQUALS, value=True)])

    await policy_engine.add_policy_rule(rule1)
    await policy_engine.add_policy_rule(rule2)

    context = {"some_condition": True}
    result = await policy_engine.evaluate_policies(context)

    assert result.final_action == PolicyAction.DENY

@pytest.mark.asyncio
async def test_get_field_value_object_attribute(policy_engine):
    """Test _get_field_value with an object attribute."""
    class MyObject:
        def __init__(self):
            self.my_attr = "hello"

    context = {"my_obj": MyObject()}

    value = policy_engine.rule_engine._get_field_value(context, "my_obj.my_attr")
    assert value == "hello"
