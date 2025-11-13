import pytest
from unittest.mock import AsyncMock, MagicMock

from labs.bridge.explainability_interface_layer import (
    ExplainabilityInterface,
    ExplanationMode,
    ExplanationLevel,
)


@pytest.fixture
def meg_client():
    """Fixture for a mock MEG client."""
    client = MagicMock()
    client.get_context = AsyncMock(return_value={
        'contradicts_past_decision': False,
        'is_novel_pattern': True,
    })
    return client


@pytest.fixture
def symbolic_engine():
    """Fixture for a mock symbolic engine."""
    engine = MagicMock()
    engine.trace_reasoning = AsyncMock(return_value=[
        {'step_id': 1, 'operation': 'load_data', 'symbolic_form': 'LOAD(data)'}
    ])
    return engine


@pytest.fixture
def explainability_interface(meg_client, symbolic_engine):
    """Fixture for ExplainabilityInterface."""
    return ExplainabilityInterface(meg_client=meg_client, symbolic_engine=symbolic_engine)


@pytest.mark.asyncio
async def test_generate_multimodal_explanation(explainability_interface):
    """Test multi-modal explanation generation."""
    decision = {'id': 'test_decision_1', 'factors': ['factor_a', 'factor_b']}
    explanation = await explainability_interface._generate_multimodal_explanation(
        decision, ExplanationLevel.DETAILED
    )

    assert 'text' in explanation
    assert 'visual' in explanation
    assert 'audio' in explanation
    assert 'symbolic' in explanation
    assert explanation['symbolic']['type'] == 'symbolic_trace'


@pytest.mark.asyncio
async def test_srd_cryptographic_signing(explainability_interface):
    """Test SRD cryptographic signing."""
    decision = {'id': 'test_decision_2'}
    explanation = await explainability_interface.explain(decision, sign_explanation=True)

    assert explanation.signature is not None
    assert explanation.signature.startswith("SRD-SHA256:")


@pytest.mark.asyncio
async def test_meg_integration(explainability_interface, meg_client):
    """Test MEG integration for consistency scoring."""
    decision = {'id': 'test_decision_3'}
    explanation = await explainability_interface.explain(decision)

    # Verify that MEG client was called
    meg_client.get_context.assert_called_once_with(decision.get('id', ''))

    # Check that consistency score is affected by MEG feedback
    # (0.9 is the multiplier for 'is_novel_pattern')
    assert explanation.completeness.consistency_score == 0.9


@pytest.mark.asyncio
async def test_completeness_and_clarity_metrics(explainability_interface):
    """Test calculation of completeness and clarity metrics."""
    decision = {
        'id': 'test_decision_4',
        'factors': ['factor_a', 'factor_b', 'factor_c'],
        'result': 'approved',
        'confidence': 0.95,
    }
    explanation = await explainability_interface.explain(decision, level=ExplanationLevel.DETAILED)

    metrics = explanation.completeness
    assert metrics is not None
    assert 0 <= metrics.coverage_score <= 1
    assert 0 <= metrics.depth_score <= 1
    assert 0 <= metrics.clarity_score <= 1
    assert 0 <= metrics.consistency_score <= 1
    assert 0 <= metrics.overall_score <= 1
