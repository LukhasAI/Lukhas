import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import uuid
from datetime import datetime, timezone

from candidate.bridge.explainability_interface_layer import (
    ExplainabilityInterfaceLayer,
    ExplanationRequest,
    ExplanationType,
    ExplanationAudience,
    ExplanationDepth,
    NaturalLanguageGenerator,
    FormalProofGenerator,
    ExplanationProof,
)

@pytest.fixture
def xil_instance():
    """Fixture for a clean ExplainabilityInterfaceLayer instance with Lukhas integration mocked."""
    with patch('candidate.bridge.explainability_interface_layer.LUKHAS_INTEGRATION', True), \
         patch('candidate.bridge.explainability_interface_layer.SelfReflectiveDebugger') as MockSRD, \
         patch('candidate.bridge.explainability_interface_layer.MetaEthicsGovernor') as MockMEG, \
         patch('candidate.bridge.explainability_interface_layer.SymbolicEngine') as MockSymbolicEngine, \
         patch('candidate.bridge.explainability_interface_layer.EmotionalMemory') as MockEmotionalMemory:

        instance = ExplainabilityInterfaceLayer()
        # Attach mocks to instance for easy access in tests
        instance.srd = MockSRD.return_value
        instance.meg = MockMEG.return_value
        instance.symbolic_engine = MockSymbolicEngine.return_value
        instance.emotional_memory = MockEmotionalMemory.return_value

        # Configure async mocks
        instance.srd.sign_explanation = AsyncMock(return_value="mock_srd_signature")
        instance.meg.analyze_decision = AsyncMock(return_value={"summary": "Ethically sound"})
        instance.symbolic_engine.trace_reasoning = AsyncMock(return_value={"steps": []})
        instance.emotional_memory.get_current_emotional_state = AsyncMock(return_value="calm")

        yield instance

@pytest.fixture
def sample_request():
    """Fixture for a sample ExplanationRequest."""
    return ExplanationRequest(
        request_id=str(uuid.uuid4()),
        decision_id="decision-1",
        explanation_type=ExplanationType.NATURAL_LANGUAGE,
        audience=ExplanationAudience.GENERAL_USER,
        depth=ExplanationDepth.SUMMARY,
        context={"input": "data"},
        requires_proof=False,
        requires_signing=False
    )

@pytest.fixture
def sample_context():
    """Fixture for a sample decision_context."""
    return {
        "decision_id": "decision-1",
        "decision": "approve_loan",
        "reasoning": "Applicant meets all criteria.",
        "confidence": 0.98,
        "decision_inputs": {"credit_score": 750, "income": 80000},
        "causal_factors": ["high credit score", "stable income"],
        "uncertainty_factors": ["market volatility"]
    }

def test_xil_initialization(xil_instance):
    """Tests that the XIL initializes correctly with mocked integrations."""
    assert xil_instance is not None
    assert xil_instance.srd is not None
    assert xil_instance.meg is not None
    assert xil_instance.metrics["explanations_generated"] == 0

@pytest.mark.asyncio
async def test_explain_decision_simple_success(xil_instance, sample_request, sample_context):
    """Tests a simple, successful explanation generation without proofs or signing."""
    output = await xil_instance.explain_decision(sample_request.decision_id, sample_request, sample_context)

    assert output.explanation_id is not None
    assert output.request_id == sample_request.request_id
    assert "Applicant meets all criteria" in output.natural_language
    assert "error" not in output.metadata
    assert output.formal_proof is None
    assert output.srd_signature is None
    assert xil_instance.metrics["explanations_generated"] == 1

@pytest.mark.asyncio
async def test_explain_decision_with_proof(xil_instance, sample_request, sample_context):
    """Tests explanation generation that requires a formal proof."""
    sample_request.requires_proof = True
    output = await xil_instance.explain_decision(sample_request.decision_id, sample_request, sample_context)

    assert output.formal_proof is not None
    assert output.formal_proof.conclusion == "approve_loan"
    assert len(output.formal_proof.logical_steps) > 0
    assert xil_instance.metrics["proofs_generated"] == 1

@pytest.mark.asyncio
async def test_explain_decision_with_signing(xil_instance, sample_request, sample_context):
    """Tests explanation generation that requires SRD signing."""
    xil_instance.srd.sign_explanation = AsyncMock(return_value="signed_hash_value") # Custom mock for this test
    sample_request.requires_signing = True

    # Mock the _sign_explanation method to check its input and control its output
    with patch.object(xil_instance, '_sign_explanation', new_callable=AsyncMock) as mock_sign:
        mock_sign.return_value = "signed_hash_value"
        output = await xil_instance.explain_decision(sample_request.decision_id, sample_request, sample_context)

        assert output.srd_signature == "signed_hash_value"
        mock_sign.assert_called_once()
        assert xil_instance.metrics["explanations_signed"] == 1

@pytest.mark.asyncio
async def test_enrich_context(xil_instance, sample_context):
    """Tests the context enrichment process."""
    enriched = await xil_instance._enrich_context(sample_context)

    assert "emotional_context" in enriched
    assert "ethical_analysis" in enriched
    assert "reasoning_trace" in enriched
    assert enriched["ethical_analysis"] == "Ethically sound"

def test_nl_generator_audience_style():
    """Tests the audience style selection in the NaturalLanguageGenerator."""
    nl_gen = NaturalLanguageGenerator()
    style = nl_gen._get_audience_style(ExplanationAudience.TECHNICAL_USER)
    assert style["prefix"] == "Technical explanation: "

@pytest.mark.asyncio
async def test_formal_proof_generator(sample_context):
    """Tests the FormalProofGenerator independently."""
    proof_gen = FormalProofGenerator()
    proof_gen.symbolic_engine = None # Ensure fallback is tested
    proof = await proof_gen._generate_formal_proof(sample_context)

    assert isinstance(proof, ExplanationProof)
    assert proof.conclusion == sample_context["decision"]
    assert len(proof.logical_steps) > len(sample_context["causal_factors"])

@pytest.mark.asyncio
async def test_caching_mechanism(xil_instance, sample_request, sample_context):
    """Tests that repeated identical requests are served from cache."""
    # First call to populate cache
    output1 = await xil_instance.explain_decision(sample_request.decision_id, sample_request, sample_context)

    # Second call should hit the cache
    with patch.object(xil_instance, '_enrich_context', new_callable=AsyncMock) as mock_enrich:
        output2 = await xil_instance.explain_decision(sample_request.decision_id, sample_request, sample_context)
        mock_enrich.assert_not_called() # Should not be called if cache hits

    assert output1.explanation_id == output2.explanation_id
    assert xil_instance.metrics["explanations_generated"] == 1 # Metric should not be incremented twice
