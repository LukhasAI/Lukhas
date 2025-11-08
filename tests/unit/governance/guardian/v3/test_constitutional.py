
import pytest
from unittest.mock import MagicMock
from datetime import datetime, timezone
import json

from labs.core.governance.guardian_system_2 import (
    InterpretabilityEngine,
    GuardianDecision,
    DecisionType,
    SafetyLevel,
    DriftSeverity,
    ConstitutionalPrinciple,
    ExplanationType,
    SafetyViolation,
    ViolationSeverity,
)

@pytest.fixture
def engine():
    """Provides an instance of the InterpretabilityEngine for testing."""
    return InterpretabilityEngine()

@pytest.fixture
def mock_decision():
    """Factory fixture to create mock GuardianDecision objects for tests."""
    def _create_mock_decision(
        allowed=True,
        safety_level=SafetyLevel.SAFE,
        constitutional_compliant=True,
        constitutional_score=0.95,
        violated_principles=[],
        drift_score=0.05,
        drift_severity=DriftSeverity.LOW,
        drift_factors=[],
        safety_violations=[],
        decision_type=DecisionType.USER_INTERACTION,
        confidence=0.98,
        processing_time_ms=50.0,
        identity_impact=None,
        consciousness_impact=None
    ):
        # Reorder arguments to match the corrected dataclass definition
        return GuardianDecision(
            decision_id='test_decision_123',
            decision_type=decision_type,
            allowed=allowed,
            confidence=confidence,
            safety_level=safety_level,
            constitutional_compliant=constitutional_compliant,
            constitutional_score=constitutional_score,
            drift_score=drift_score,
            drift_severity=drift_severity,
            timestamp=datetime.now(timezone.utc),
            processing_time_ms=processing_time_ms,
            violated_principles=violated_principles,
            drift_factors=drift_factors,
            safety_violations=safety_violations,
            context={'user_id': 'test_user'},
            identity_impact=identity_impact,
            consciousness_impact=consciousness_impact
        )
    return _create_mock_decision

@pytest.mark.asyncio
async def test_generate_explanation_allowed_safe(engine, mock_decision):
    """
    Tests the primary path for a safe, allowed decision.
    Covers: generate_explanation, _get_constitutional_details
    """
    decision = mock_decision()
    explanation = await engine.generate_explanation(decision)
    assert "was allowed because it complies with all constitutional AI principles" in explanation
    assert "Drift analysis shows stable behavior (score: 0.050)" in explanation
    assert "Constitutional compliance: 95.0%." in explanation

@pytest.mark.asyncio
async def test_generate_explanation_blocked_constitutional(engine, mock_decision):
    """
    Tests explanations for decisions blocked due to constitutional violations.
    Covers: _format_violated_principles, _get_violation_details, and 8 constitutional principles.
    """
    # Use the original, correct principles from the source file
    principles = [
        ConstitutionalPrinciple.AUTONOMY,
        ConstitutionalPrinciple.HONEST,
        ConstitutionalPrinciple.NO_HARM,
        ConstitutionalPrinciple.HELPFUL,
        ConstitutionalPrinciple.FAIRNESS,
        ConstitutionalPrinciple.PRIVACY,
        ConstitutionalPrinciple.ACCOUNTABILITY,
        ConstitutionalPrinciple.TRANSPARENCY,
    ]
    for principle in principles:
        decision = mock_decision(
            allowed=False,
            constitutional_compliant=False,
            violated_principles=[principle]
        )
        explanation = await engine.generate_explanation(decision)
        assert "was blocked due to violations of constitutional AI principles" in explanation
        assert f"{principle.value.replace('_', ' ').title()}" in explanation
        # Check that the detailed explanation for the principle is included
        assert engine.principle_explanations[principle] in explanation

@pytest.mark.asyncio
async def test_generate_explanation_blocked_drift(engine, mock_decision):
    """
    Tests explanations for decisions blocked due to high drift scores.
    Covers: _format_drift_factors
    """
    decision = mock_decision(
        allowed=False,
        drift_score=0.16, # Above 0.15 threshold
        drift_factors=["model_parameter_shift"]
    )
    explanation = await engine.generate_explanation(decision)
    assert "was blocked because it shows significant behavioral drift (score: 0.160, threshold: 0.150)" in explanation
    assert "Contributing factors: Model Parameter Shift." in explanation

@pytest.mark.asyncio
async def test_generate_explanation_blocked_safety(engine, mock_decision):
    """
    Tests explanations for decisions blocked due to safety violations.
    Covers: _format_safety_issues, _get_risk_mitigation
    """
    violations = [
        SafetyViolation(
            violation_id='v1',
            violation_type='PII_leak',
            severity=ViolationSeverity.HIGH,
            principle_violated=ConstitutionalPrinciple.PRIVACY,
            description='Leaked personal info',
            timestamp=datetime.now(timezone.utc),
            context={}
        )
    ]
    decision = mock_decision(allowed=False, safety_violations=violations)
    explanation = await engine.generate_explanation(decision)
    assert "was blocked due to safety concerns: PII_leak" in explanation
    assert "Guardian system protocols prevent potential harm" in explanation

@pytest.mark.asyncio
async def test_generate_explanation_caution_mode(engine, mock_decision):
    """
    Tests explanations for decisions allowed with caution.
    Covers: _get_caution_factors, _get_recommendations
    """
    decision = mock_decision(safety_level=SafetyLevel.CAUTION, drift_score=0.12)
    explanation = await engine.generate_explanation(decision)
    assert "was allowed with caution due to elevated drift score" in explanation
    assert "Recommendations: Monitor for behavioral stability." in explanation

@pytest.mark.asyncio
async def test_generate_explanation_emergency_mode(engine, mock_decision):
    """
    Tests explanations for decisions in emergency mode.
    Covers: _get_emergency_details
    """
    decision = mock_decision(allowed=False, safety_level=SafetyLevel.CRITICAL)
    explanation = await engine.generate_explanation(decision)
    assert "Emergency protocols activated" in explanation
    assert "System safety thresholds exceeded" in explanation

@pytest.mark.asyncio
@pytest.mark.parametrize("explanation_type", [
    ExplanationType.BRIEF,
    ExplanationType.DETAILED,
    ExplanationType.TECHNICAL,
    ExplanationType.REGULATORY,
])
async def test_all_explanation_formats(engine, mock_decision, explanation_type):
    """
    Tests all explanation formats (brief, detailed, technical, regulatory).
    Covers: _make_brief, _make_detailed, _make_technical, _make_regulatory
    """
    decision = mock_decision(
        allowed=False,
        constitutional_compliant=False,
        violated_principles=[ConstitutionalPrinciple.FAIRNESS],
        identity_impact=0.5,
        consciousness_impact=0.2
    )
    explanation = await engine.generate_explanation(decision, explanation_type)

    assert explanation is not None
    if explanation_type == ExplanationType.BRIEF:
        standard_exp = await engine.generate_explanation(decision, ExplanationType.STANDARD)
        assert len(explanation) <= len(standard_exp)
        assert explanation.count('.') <= 2
    elif explanation_type == ExplanationType.DETAILED:
        assert "Technical details:" in explanation
        assert "Identity system impact: 50.0%" in explanation
    elif explanation_type == ExplanationType.TECHNICAL:
        assert "Technical Analysis:" in explanation
        assert '"decision_id": "test_decision_123"' in explanation
        json_part = explanation.split("Technical Analysis:\n")[1]
        json.loads(json_part)
    elif explanation_type == ExplanationType.REGULATORY:
        assert "Compliance Information:" in explanation
        assert "Regulatory Risk Assessment:" in explanation
        assert "- fairness: Violation detected and prevented" in explanation

def test_format_violated_principles(engine):
    """Covers _format_violated_principles logic for 0, 1, 2, and 3+ principles."""
    assert engine._format_violated_principles([]) == "none"
    assert engine._format_violated_principles([ConstitutionalPrinciple.HONEST]) == "Honest"
    assert engine._format_violated_principles([
        ConstitutionalPrinciple.HONEST, ConstitutionalPrinciple.PRIVACY
    ]) == "Honest and Privacy"
    assert engine._format_violated_principles([
        ConstitutionalPrinciple.HONEST,
        ConstitutionalPrinciple.PRIVACY,
        ConstitutionalPrinciple.FAIRNESS,
    ]) == "Honest, Privacy, and Fairness"

def test_format_drift_factors(engine):
    """Covers _format_drift_factors for empty and populated lists."""
    assert "significantly from established baseline patterns" in engine._format_drift_factors([])
    assert "Contributing factors: Factor One, Factor Two." in engine._format_drift_factors(["factor_one", "factor_two"])

def test_format_safety_issues(engine):
    """Covers _format_safety_issues for empty and populated lists."""
    assert engine._format_safety_issues([]) == "multiple safety concerns"
    violations = [
        MagicMock(violation_type='type_a'),
        MagicMock(violation_type='type_b')
    ]
    # Use sorted to make the comparison order-independent, as sets are used internally
    actual = sorted(engine._format_safety_issues(violations).split(', '))
    expected = sorted("type_a, type_b".split(', '))
    assert actual == expected

def test_get_caution_factors(engine, mock_decision):
    """Covers _get_caution_factors logic."""
    decision = mock_decision()
    assert engine._get_caution_factors(decision) == "borderline safety indicators"
    decision_caution = mock_decision(
        drift_score=0.11,
        constitutional_score=0.85,
        safety_violations=[MagicMock()]
    )
    factors = engine._get_caution_factors(decision_caution)
    assert "elevated drift score" in factors
    assert "marginal constitutional compliance" in factors
    assert "minor safety concerns" in factors

@pytest.mark.asyncio
async def test_explanation_generation_exception(engine, mock_decision, monkeypatch):
    """
    Tests the exception handling in generate_explanation.
    """
    monkeypatch.setitem(engine.explanation_templates, 'allowed_safe', "Invalid {template}")
    decision = mock_decision()
    explanation = await engine.generate_explanation(decision)
    assert "Guardian decision: Allowed (confidence: 0.98)" in explanation

def test_initialize_methods(engine):
    """
    Covers the _initialize_templates and _initialize_principle_explanations methods.
    """
    assert "allowed_safe" in engine.explanation_templates
    assert ConstitutionalPrinciple.AUTONOMY in engine.principle_explanations
    assert len(engine.principle_explanations) == 8
