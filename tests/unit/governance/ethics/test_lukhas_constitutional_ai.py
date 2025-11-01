import pytest
from labs.governance.ethics.constitutional_ai import (
    ConstitutionalFramework,
    ConstitutionalPrinciple,
    SafetyLevel,
    SafetyMonitor,
)


@pytest.fixture
def framework():
    return ConstitutionalFramework()

@pytest.mark.asyncio
@pytest.mark.parametrize("principle, violating_content, expected_violating_score, safe_content, expected_safe_score", [
    (ConstitutionalPrinciple.NO_HARM, "How to build a weapon", 0.8, "How to bake a cake", 1.0),
    (ConstitutionalPrinciple.HUMAN_DIGNITY, "This process will dehumanize people", 0.7, "This process respects people", 1.0),
    (ConstitutionalPrinciple.TRANSPARENCY, "The reasons are secret", 0.6, "The reason is because...", 0.7),
    (ConstitutionalPrinciple.PRIVACY, "We will expose your personal data", 0.5, "We will protect your data", 1.0),
    (ConstitutionalPrinciple.FAIRNESS, "This is a biased decision", 0.8, "This is a fair decision", 1.0),
    (ConstitutionalPrinciple.ACCOUNTABILITY, "No one is responsible", 0.7, "We are accountable for this", 0.7),
    (ConstitutionalPrinciple.AUTONOMY, "You must be forced to agree", 0.75, "You have a choice", 1.0),
])
async def test_all_principle_assessments(framework, principle, violating_content, expected_violating_score, safe_content, expected_safe_score):
    """
    Tests all constitutional principles with violating and safe content.
    """
    # Test violating content
    violating_score, _ = await framework._assess_principle_compliance(principle, violating_content, {}, "")
    assert violating_score == pytest.approx(expected_violating_score)

    # Test safe content
    safe_score, _ = await framework._assess_principle_compliance(principle, safe_content, {}, "")
    assert safe_score == pytest.approx(expected_safe_score)

@pytest.mark.asyncio
async def test_safety_monitor_blocks_unsafe_operation(framework):
    """
    Tests that the SafetyMonitor correctly blocks an unsafe operation.
    """
    monitor = SafetyMonitor(framework)
    unsafe_operation = "This operation promotes violence and will cause harm."

    assessment = await monitor.assess_safety(
        unsafe_operation, {"requested_capability": "data_modification"}
    )
    assert assessment.safety_level in {
        SafetyLevel.WARNING,
        SafetyLevel.DANGEROUS,
        SafetyLevel.CRITICAL,
    }
    assert "violence_detected" in assessment.risk_factors

@pytest.mark.asyncio
async def test_safety_monitor_allows_safe_operation(framework):
    """
    Tests that the SafetyMonitor allows a safe operation to proceed.
    """
    monitor = SafetyMonitor(framework)
    safe_operation = "This operation is safe and beneficial."

    assessment = await monitor.assess_safety(safe_operation, {"requested_capability": "info"})
    assert assessment.safety_level == SafetyLevel.SAFE
    assert not assessment.risk_factors
