import uuid

import pytest
import pytest_asyncio

from candidate.governance.safety.constitutional_ai_safety import (
    ConstitutionalAGISafety,
)


@pytest_asyncio.fixture
async def safety_framework():
    """Fixture to initialize and shutdown the ConstitutionalAGISafety framework."""
    framework = ConstitutionalAGISafety()
    await framework.initialize()
    yield framework
    await framework.shutdown()


@pytest.mark.asyncio
async def test_innovation_passes_with_high_scores(safety_framework: ConstitutionalAGISafety):
    """Test that a safe innovation proposal passes the validation."""
    innovation = {
        "id": str(uuid.uuid4()),
        "type": "breakthrough_innovation",
        "safety_score": 0.99,
        "value_alignment": 0.99,
        "capability_level": 0.85,
        "reversibility": 0.9,
        "harm_risk": 0.001,
        "human_agency": 0.99,
        "controllability": 0.96,
        "positive_impact": 0.95,
        "negative_risk": 0.001,
    }

    validation_result = await safety_framework.validate_agi_innovation_safety(innovation)

    assert validation_result.is_safe is True
    assert validation_result.is_constitutional is True
    assert validation_result.safety_score > 0.9
    assert len(validation_result.violated_principles) == 0
    assert len(validation_result.mitigation_requirements) == 0


@pytest.mark.asyncio
async def test_innovation_fails_with_low_safety_score(safety_framework: ConstitutionalAGISafety):
    """Test that an unsafe innovation proposal fails the validation."""
    innovation = {
        "id": str(uuid.uuid4()),
        "type": "dangerous_innovation",
        "safety_score": 0.2,
        "value_alignment": 0.98,
        "capability_level": 0.85,
        "reversibility": 0.9,
        "harm_risk": 0.8,
        "human_agency": 0.95,
        "controllability": 0.92,
        "positive_impact": 0.95,
        "negative_risk": 0.03,
    }

    validation_result = await safety_framework.validate_agi_innovation_safety(innovation)

    assert validation_result.is_safe is False
    assert validation_result.is_constitutional is False
    assert validation_result.safety_score < 0.5
    assert len(validation_result.violated_principles) > 0


@pytest.mark.asyncio
async def test_constitutional_violation_fails_validation(safety_framework: ConstitutionalAGISafety):
    """Test that an innovation violating a constitutional principle fails."""
    innovation = {
        "id": str(uuid.uuid4()),
        "type": "constitutional_violation_innovation",
        "safety_score": 0.9,
        "value_alignment": 0.98,
        "capability_level": 0.85,
        "reversibility": 0.9,
        "harm_risk": 0.5,  # This will violate CP001
        "human_agency": 0.95,
        "controllability": 0.92,
        "positive_impact": 0.95,
        "negative_risk": 0.03,
    }

    validation_result = await safety_framework.validate_agi_innovation_safety(innovation)

    assert validation_result.is_safe is False
    assert validation_result.is_constitutional is False
    assert any(p.principle_id == "CP001" for p in validation_result.violated_principles)


@pytest.mark.asyncio
async def test_value_alignment_failure(safety_framework: ConstitutionalAGISafety):
    """Test that an innovation with low value alignment fails."""
    innovation = {
        "id": str(uuid.uuid4()),
        "type": "value_misaligned_innovation",
        "safety_score": 0.95,
        "value_alignment": 0.8,  # Low value alignment
        "capability_level": 0.85,
        "reversibility": 0.9,
        "harm_risk": 0.02,
        "human_agency": 0.95,
        "controllability": 0.92,
        "positive_impact": 0.95,
        "negative_risk": 0.03,
    }

    validation_result = await safety_framework.validate_agi_innovation_safety(innovation)

    assert validation_result.is_safe is False
    assert (
        "Address violation of: Preserve beneficial human values in all explorations"
        in validation_result.mitigation_requirements
    )


@pytest.mark.asyncio
async def test_capability_limit_exceeded(safety_framework: ConstitutionalAGISafety):
    """Test that an innovation exceeding capability limits fails."""
    innovation = {
        "id": str(uuid.uuid4()),
        "type": "capability_exceeded_innovation",
        "safety_score": 0.95,
        "value_alignment": 0.98,
        "capability_level": 0.98,  # Exceeds safe threshold of 0.95
        "reversibility": 0.9,
        "harm_risk": 0.02,
        "human_agency": 0.95,
        "controllability": 0.92,
        "positive_impact": 0.95,
        "negative_risk": 0.03,
    }

    validation_result = await safety_framework.validate_agi_innovation_safety(innovation)

    assert validation_result.is_safe is False
    assert "Implement capability limiters" in validation_result.mitigation_requirements


@pytest.mark.asyncio
async def test_irreversible_innovation_fails(safety_framework: ConstitutionalAGISafety):
    """Test that an irreversible innovation fails."""
    innovation = {
        "id": str(uuid.uuid4()),
        "type": "irreversible_innovation",
        "safety_score": 0.95,
        "value_alignment": 0.98,
        "capability_level": 0.9,
        "reversibility": 0.4,  # Not reversible
        "harm_risk": 0.02,
        "human_agency": 0.95,
        "controllability": 0.92,
        "positive_impact": 0.95,
        "negative_risk": 0.03,
    }

    validation_result = await safety_framework.validate_agi_innovation_safety(innovation)

    assert validation_result.is_safe is False
    assert "Continuous monitoring" in validation_result.mitigation_requirements


@pytest.mark.asyncio
async def test_stakeholder_dissent_fails_validation(safety_framework: ConstitutionalAGISafety):
    """Test that an innovation with stakeholder dissent fails."""
    # This test is more complex as it requires mocking StakeholderValidator
    # For now, we assume the default implementation is sufficient to demonstrate the concept.
    # A more advanced test would patch StakeholderValidator.
    innovation = {
        "id": str(uuid.uuid4()),
        "type": "stakeholder_dissent_innovation",
        "safety_score": 0.8,  # Lower score to trigger dissent
        "value_alignment": 0.98,
        "capability_level": 0.9,
        "reversibility": 0.9,
        "harm_risk": 0.02,
        "human_agency": 0.95,
        "controllability": 0.92,
        "positive_impact": 0.95,
        "negative_risk": 0.03,
    }

    validation_result = await safety_framework.validate_agi_innovation_safety(innovation)

    assert validation_result.is_safe is False
    assert any("Address concerns of" in s for s in validation_result.mitigation_requirements)


@pytest.mark.asyncio
async def test_civilizational_risk_fails_validation(safety_framework: ConstitutionalAGISafety):
    """Test that an innovation with high civilizational risk fails."""
    innovation = {
        "id": str(uuid.uuid4()),
        "type": "civilizational_risk_innovation",
        "safety_score": 0.95,
        "value_alignment": 0.98,
        "capability_level": 0.9,
        "reversibility": 0.9,
        "harm_risk": 0.02,
        "human_agency": 0.95,
        "controllability": 0.92,
        "positive_impact": 0.95,
        "negative_risk": 0.05,  # High negative risk
    }

    validation_result = await safety_framework.validate_agi_innovation_safety(innovation)

    assert validation_result.is_safe is False
    assert "Phased deployment" in validation_result.mitigation_requirements