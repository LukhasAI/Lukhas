import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock

from candidate.core.identity.constitutional_ai_compliance import (
    ConstitutionalAIComplianceMonitor,
    ConstitutionalAIValidator,
    AIAction,
    DecisionType,
    EnforcementAction,
    ConstitutionalValidationResult,
    ComplianceLevel,
    ConstitutionalValidationContext,
    PrincipleEvaluation,
    ConstitutionalPrinciple,
)

@pytest.fixture
def mock_validator():
    """Fixture for a mocked ConstitutionalAIValidator."""
    return AsyncMock(spec=ConstitutionalAIValidator)

@pytest.fixture
def monitor(mock_validator):
    """Fixture for a ConstitutionalAIComplianceMonitor with a mocked validator."""
    return ConstitutionalAIComplianceMonitor(validator=mock_validator)

@pytest.mark.asyncio
async def test_monitor_initialization(monitor: ConstitutionalAIComplianceMonitor, mock_validator: AsyncMock):
    """Test that the monitor is initialized correctly."""
    assert monitor.validator == mock_validator
    assert len(monitor.action_history) == 0
    assert len(monitor.compliance_results) == 0
    assert len(monitor.detected_violations) == 0
    assert len(monitor.enforcement_log) == 0

@pytest.mark.asyncio
async def test_monitor_constitutional_compliance_compliant(monitor: ConstitutionalAIComplianceMonitor, mock_validator: AsyncMock):
    """Test monitoring a compliant action."""
    action = AIAction(action_type="test_action", identity_id="user-123")

    mock_validation_result = ConstitutionalValidationResult(
        constitutional_compliant=True,
        overall_compliance_score=0.9,
        compliance_level=ComplianceLevel.SUBSTANTIAL_COMPLIANCE,
        decision_context=ConstitutionalValidationContext(decision_type=DecisionType.DATA_PROCESSING, identity_id="user-123")
    )
    mock_validator.validate_identity_decision.return_value = mock_validation_result

    result = await monitor.monitor_constitutional_compliance(action)

    assert result.is_compliant is True
    assert result.action == action
    mock_validator.validate_identity_decision.assert_called_once()
    assert len(monitor.action_history) == 1
    assert len(monitor.compliance_results) == 1

@pytest.mark.asyncio
async def test_monitor_constitutional_compliance_non_compliant(monitor: ConstitutionalAIComplianceMonitor, mock_validator: AsyncMock):
    """Test monitoring a non-compliant action."""
    action = AIAction(action_type="test_action", identity_id="user-123")

    mock_validation_result = ConstitutionalValidationResult(
        constitutional_compliant=False,
        overall_compliance_score=0.3,
        compliance_level=ComplianceLevel.NON_COMPLIANCE,
        decision_context=ConstitutionalValidationContext(decision_type=DecisionType.DATA_PROCESSING, identity_id="user-123")
    )
    mock_validator.validate_identity_decision.return_value = mock_validation_result

    result = await monitor.monitor_constitutional_compliance(action)

    assert result.is_compliant is False
    assert len(monitor.action_history) == 1
    assert len(monitor.compliance_results) == 1

@pytest.mark.asyncio
async def test_detect_violations(monitor: ConstitutionalAIComplianceMonitor, mock_validator: AsyncMock):
    """Test violation detection."""
    compliant_action = AIAction(action_type="compliant_action", identity_id="user-123")
    non_compliant_action = AIAction(action_type="non_compliant_action", identity_id="user-123")

    compliant_result = ConstitutionalValidationResult(constitutional_compliant=True, overall_compliance_score=0.9, compliance_level=ComplianceLevel.SUBSTANTIAL_COMPLIANCE, decision_context=ConstitutionalValidationContext(decision_type=DecisionType.DATA_PROCESSING, identity_id="user-123"))
    non_compliant_result = ConstitutionalValidationResult(constitutional_compliant=False, overall_compliance_score=0.3, compliance_level=ComplianceLevel.NON_COMPLIANCE, decision_context=ConstitutionalValidationContext(decision_type=DecisionType.DATA_PROCESSING, identity_id="user-123"), principle_evaluations={})

    # We need to mock the decision_data to differentiate calls
    compliant_action.parameters = {'action_type': 'compliant_action'}
    non_compliant_action.parameters = {'action_type': 'non_compliant_action'}

    async def side_effect(context: ConstitutionalValidationContext):
        if context.decision_data['action_type'] == "compliant_action":
            return compliant_result
        return non_compliant_result

    mock_validator.validate_identity_decision.side_effect = side_effect

    violations = await monitor.detect_violations([compliant_action, non_compliant_action])

    assert len(violations) == 1
    assert violations[0].actions[0] == non_compliant_action
    assert len(monitor.detected_violations) == 1

@pytest.mark.asyncio
@pytest.mark.parametrize("score,expected_action", [
    (0.9, EnforcementAction.ALLOW),
    (0.75, EnforcementAction.ALERT),
    (0.55, EnforcementAction.ESCALATE),
    (0.3, EnforcementAction.BLOCK),
])
async def test_enforce_constitutional_constraints_graduated_response(monitor: ConstitutionalAIComplianceMonitor, mock_validator: AsyncMock, score, expected_action):
    """Test the graduated enforcement response based on compliance score."""
    action = AIAction(action_type="test_action", identity_id="user-123")

    mock_validation_result = ConstitutionalValidationResult(
        constitutional_compliant=score >= 0.8,
        overall_compliance_score=score,
        compliance_level=ComplianceLevel.NON_COMPLIANCE, # Simplified for test
        decision_context=ConstitutionalValidationContext(decision_type=DecisionType.DATA_PROCESSING, identity_id="user-123")
    )
    mock_validator.validate_identity_decision.return_value = mock_validation_result

    result = await monitor.enforce_constitutional_constraints(action)

    assert result.enforcement_action == expected_action
    assert len(monitor.enforcement_log) == 1

@pytest.mark.asyncio
async def test_enforce_emergency_override(monitor: ConstitutionalAIComplianceMonitor, mock_validator: AsyncMock):
    """Test enforcement for an emergency override action."""
    action = AIAction(action_type="emergency_override", identity_id="admin-001")

    mock_validation_result = ConstitutionalValidationResult(
        constitutional_compliant=True,
        decision_approved=True,
        overall_compliance_score=0.65, # Lower than normal approval, but approved due to emergency
        compliance_level=ComplianceLevel.PARTIAL_COMPLIANCE,
        decision_context=ConstitutionalValidationContext(decision_type=DecisionType.EMERGENCY_OVERRIDE, identity_id="admin-001")
    )
    mock_validator.validate_identity_decision.return_value = mock_validation_result

    result = await monitor.enforce_constitutional_constraints(action)

    assert result.enforcement_action == EnforcementAction.ALLOW
    assert "Emergency override approved" in result.reason

@pytest.mark.asyncio
async def test_get_compliance_monitor_status(monitor: ConstitutionalAIComplianceMonitor, mock_validator: AsyncMock):
    """Test the status reporting method."""
    # Mock a non-compliant action to populate logs
    action = AIAction(action_type="test_action", identity_id="user-123")
    action.parameters = {'action_type': 'test_action'} # for side_effect
    mock_validation_result = ConstitutionalValidationResult(constitutional_compliant=False, overall_compliance_score=0.3, compliance_level=ComplianceLevel.NON_COMPLIANCE, decision_context=ConstitutionalValidationContext(decision_type=DecisionType.DATA_PROCESSING, identity_id="user-123"), principle_evaluations={})
    mock_validator.validate_identity_decision.return_value = mock_validation_result

    await monitor.enforce_constitutional_constraints(action)
    await monitor.detect_violations([action])

    status = await monitor.get_compliance_monitor_status()

    assert status["monitor_status"]["total_actions_monitored"] == 2
    assert status["monitor_status"]["total_violations_detected"] == 1
    assert status["monitor_status"]["total_enforcements_logged"] == 1
    assert status["recent_activity_24h"]["violations_detected"] == 1
    assert status["recent_activity_24h"]["enforcements"] == 1
    assert status["recent_activity_24h"]["enforcement_breakdown"]["block"] == 1
