"""
Tests for Explainability Interface Layer

Comprehensive functional tests for explainability_interface_layer.py implementation.
Covers multi-modal explanations, formal proofs, MEG integration, and cryptographic signing.

Part of BATCH-COPILOT-TESTS-01
Tasks Tested:
- TEST-HIGH-EXPLAIN-01: Multi-modal text explanation generation
- TEST-HIGH-EXPLAIN-02: Formal proof generation
- TEST-HIGH-EXPLAIN-03: MEG integration
- TEST-HIGH-EXPLAIN-04: Symbolic reasoning traces
- TEST-HIGH-EXPLAIN-05: LRU cache functionality
- TEST-HIGH-EXPLAIN-06: Cryptographic signing

Trinity Framework: 🧠 Consciousness · 🛡️ Guardian · 🔬 Vision
"""

import asyncio
from collections import OrderedDict
from datetime import datetime

import pytest

from labs.bridge.explainability_interface_layer import (
    CompletenessMetrics,
    ExplainabilityCache,
    ExplainabilityInterface,
    Explanation,
    ExplanationTemplate,
    FormalProof,
)

# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def explainability_interface():
    """Fresh ExplainabilityInterface instance."""
    return ExplainabilityInterface(
        cache_enabled=True,
        max_cache_size=1000,
        template_dir="tests/fixtures/templates"
    )


@pytest.fixture
def mock_symbolic_engine():
    """Mock symbolic engine for reasoning traces."""
    class MockSymbolicEngine:
        def generate_trace(self, decision, context):
            return {
                "steps": [
                    {"glyph": "Λ", "operation": "identity_check"},
                    {"glyph": "Ω", "operation": "decision_made"}
                ],
                "symbols": ["Λ", "Ω"],
                "final_state": "approved"
            }
    return MockSymbolicEngine()


@pytest.fixture
def mock_meg_client():
    """Mock MEG client for consciousness context."""
    class MockMEGClient:
        async def get_context(self, entity_id):
            return {
                "consciousness_level": "high",
                "memory_nodes": ["node1", "node2"],
                "awareness_state": "active"
            }
    return MockMEGClient()


@pytest.fixture
def sample_decision():
    """Sample decision data for testing."""
    return {
        "decision_id": "dec_12345",
        "type": "access_control",
        "outcome": "approved",
        "confidence": 0.95,
        "factors": ["identity_verified", "tier_sufficient"],
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# TEST-HIGH-EXPLAIN-01: Multi-modal Text Explanation
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
async def test_explainability_multimodal_text(explainability_interface, sample_decision):
    """Test text explanation generation from explainability interface."""
    # Generate text explanation
    explanation = await explainability_interface.explain(
        decision=sample_decision,
        mode="text",
        detail_level="comprehensive"
    )
    
    # Verify explanation structure
    assert explanation is not None
    assert isinstance(explanation, Explanation)
    assert explanation.mode == "text"
    assert explanation.decision_id == "dec_12345"
    assert len(explanation.content) > 0
    
    # Verify clarity scoring
    assert explanation.clarity_score is not None
    assert 0.0 <= explanation.clarity_score <= 1.0
    assert explanation.clarity_score > 0.5  # Should be reasonably clear
    
    # Verify content quality
    assert "approved" in explanation.content.lower()
    assert any(factor in explanation.content for factor in sample_decision["factors"])


@pytest.mark.asyncio
@pytest.mark.unit
async def test_explainability_multimodal_visual(explainability_interface, sample_decision):
    """Test visual explanation generation."""
    explanation = await explainability_interface.explain(
        decision=sample_decision,
        mode="visual",
        detail_level="detailed"
    )
    
    # Verify visual explanation structure
    assert explanation.mode == "visual"
    assert "visualization" in explanation.metadata
    assert explanation.metadata["visualization"]["type"] in ["graph", "flowchart", "diagram"]


@pytest.mark.asyncio
@pytest.mark.unit
async def test_explainability_multimodal_audio(explainability_interface, sample_decision):
    """Test audio explanation generation."""
    explanation = await explainability_interface.explain(
        decision=sample_decision,
        mode="audio",
        detail_level="summary"
    )
    
    # Verify audio explanation structure
    assert explanation.mode == "audio"
    assert "audio_transcript" in explanation.metadata
    assert len(explanation.content) > 0  # Should have transcript


@pytest.mark.asyncio
@pytest.mark.unit
async def test_explainability_template_rendering(explainability_interface, sample_decision):
    """Test template rendering for explanations."""
    # Load template
    template = ExplanationTemplate(
        name="access_control_template",
        content="Decision: {outcome}. Factors: {factors}",
        mode="text",
        detail_level="detailed"
    )
    
    # Render template
    rendered = explainability_interface._render_template(template, sample_decision)
    
    assert "approved" in rendered
    assert "identity_verified" in rendered
    assert "tier_sufficient" in rendered


# ============================================================================
# TEST-HIGH-EXPLAIN-02: Formal Proof Generation
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
async def test_explainability_formal_proofs_propositional(explainability_interface, sample_decision):
    """Test propositional logic formal proof generation."""
    proof = await explainability_interface.generate_formal_proof(
        decision=sample_decision,
        proof_system="propositional"
    )
    
    # Verify proof structure
    assert proof is not None
    assert isinstance(proof, FormalProof)
    assert proof.proof_system == "propositional"
    assert len(proof.premises) > 0
    assert proof.conclusion is not None
    assert len(proof.steps) > 0
    
    # Verify proof validity
    assert proof.is_valid
    assert all(step.get("valid", False) for step in proof.steps)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_explainability_formal_proofs_first_order(explainability_interface, sample_decision):
    """Test first-order logic formal proof generation."""
    proof = await explainability_interface.generate_formal_proof(
        decision=sample_decision,
        proof_system="first_order"
    )
    
    assert proof.proof_system == "first_order"
    assert "quantifiers" in proof.metadata
    assert proof.is_valid


@pytest.mark.asyncio
@pytest.mark.unit
async def test_explainability_formal_proofs_temporal(explainability_interface, sample_decision):
    """Test temporal logic formal proof generation."""
    proof = await explainability_interface.generate_formal_proof(
        decision=sample_decision,
        proof_system="temporal"
    )
    
    assert proof.proof_system == "temporal"
    assert "temporal_operators" in proof.metadata
    assert proof.is_valid


@pytest.mark.asyncio
@pytest.mark.unit
async def test_explainability_formal_proofs_modal(explainability_interface, sample_decision):
    """Test modal logic formal proof generation."""
    proof = await explainability_interface.generate_formal_proof(
        decision=sample_decision,
        proof_system="modal"
    )
    
    assert proof.proof_system == "modal"
    assert "modal_operators" in proof.metadata
    assert proof.is_valid


@pytest.mark.asyncio
@pytest.mark.unit
async def test_explainability_completeness_metrics(explainability_interface, sample_decision):
    """Test completeness metrics calculation."""
    explanation = await explainability_interface.explain(
        decision=sample_decision,
        mode="text",
        detail_level="comprehensive"
    )
    
    # Calculate completeness
    completeness = await explainability_interface.calculate_completeness(explanation)
    
    assert isinstance(completeness, CompletenessMetrics)
    assert 0.0 <= completeness.coverage <= 1.0
    assert 0.0 <= completeness.depth <= 1.0
    assert 0.0 <= completeness.clarity <= 1.0
    assert 0.0 <= completeness.consistency <= 1.0
    assert 0.0 <= completeness.overall_score <= 1.0


# ============================================================================
# TEST-HIGH-EXPLAIN-03: MEG Integration
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
async def test_explainability_meg_integration(explainability_interface, mock_meg_client, sample_decision):
    """Test Memory Episodic Graph integration for consciousness context."""
    # Set mock MEG client
    explainability_interface.meg_client = mock_meg_client
    
    # Generate explanation with MEG context
    explanation = await explainability_interface.explain(
        decision=sample_decision,
        mode="text",
        include_consciousness_context=True,
        entity_id="user_123"
    )
    
    # Verify MEG context integration
    assert "consciousness_context" in explanation.metadata
    meg_context = explanation.metadata["consciousness_context"]
    assert meg_context["consciousness_level"] == "high"
    assert "memory_nodes" in meg_context
    assert len(meg_context["memory_nodes"]) > 0


@pytest.mark.asyncio
@pytest.mark.unit
async def test_explainability_meg_consciousness_level(explainability_interface, mock_meg_client, sample_decision):
    """Test consciousness level integration from MEG."""
    explainability_interface.meg_client = mock_meg_client
    
    explanation = await explainability_interface.explain(
        decision=sample_decision,
        mode="text",
        include_consciousness_context=True,
        entity_id="user_123"
    )
    
    # Consciousness level should influence explanation detail
    assert explanation.detail_level in ["comprehensive", "detailed"]
    assert explanation.metadata["consciousness_context"]["awareness_state"] == "active"


# ============================================================================
# TEST-HIGH-EXPLAIN-04: Symbolic Reasoning Traces
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
async def test_explainability_symbolic_reasoning(explainability_interface, mock_symbolic_engine, sample_decision):
    """Test symbolic engine reasoning trace generation."""
    # Set mock symbolic engine
    explainability_interface.symbolic_engine = mock_symbolic_engine
    
    # Generate reasoning trace
    trace = await explainability_interface.generate_reasoning_trace(
        decision=sample_decision,
        include_symbols=True
    )
    
    # Verify trace structure
    assert trace is not None
    assert "steps" in trace
    assert len(trace["steps"]) > 0
    assert "symbols" in trace
    assert "final_state" in trace
    
    # Verify GLYPH mappings
    assert any(step.get("glyph") for step in trace["steps"])
    assert "Λ" in trace["symbols"]  # Lambda identity symbol


@pytest.mark.asyncio
@pytest.mark.unit
async def test_explainability_symbolic_glyph_mapping(explainability_interface, mock_symbolic_engine, sample_decision):
    """Test GLYPH symbol mapping in reasoning traces."""
    explainability_interface.symbolic_engine = mock_symbolic_engine
    
    trace = await explainability_interface.generate_reasoning_trace(
        decision=sample_decision,
        include_symbols=True
    )
    
    # Verify glyph operations
    for step in trace["steps"]:
        if "glyph" in step:
            assert step["glyph"] in ["Λ", "Ω", "Ψ", "Φ", "Θ"]  # Valid consciousness glyphs
            assert "operation" in step


@pytest.mark.asyncio
@pytest.mark.unit
async def test_explainability_trace_visualization(explainability_interface, mock_symbolic_engine, sample_decision):
    """Test reasoning trace visualization generation."""
    explainability_interface.symbolic_engine = mock_symbolic_engine
    
    trace = await explainability_interface.generate_reasoning_trace(
        decision=sample_decision,
        include_symbols=True,
        visualize=True
    )
    
    # Verify visualization metadata
    assert "visualization" in trace
    assert trace["visualization"]["format"] in ["graph", "tree", "flowchart"]


# ============================================================================
# TEST-HIGH-EXPLAIN-05: LRU Cache
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
async def test_explainability_lru_cache_hit(explainability_interface, sample_decision):
    """Test LRU cache hit scenario."""
    # Generate explanation (cache miss)
    explanation1 = await explainability_interface.explain(
        decision=sample_decision,
        mode="text"
    )
    
    # Generate same explanation again (cache hit)
    explanation2 = await explainability_interface.explain(
        decision=sample_decision,
        mode="text"
    )
    
    # Verify cache statistics
    cache_stats = explainability_interface.cache.get_statistics()
    assert cache_stats["hits"] >= 1
    assert cache_stats["hit_rate"] > 0.0
    
    # Explanations should be identical
    assert explanation1.decision_id == explanation2.decision_id


@pytest.mark.asyncio
@pytest.mark.unit
async def test_explainability_lru_cache_miss(explainability_interface):
    """Test LRU cache miss scenario."""
    decision1 = {"decision_id": "dec_001", "outcome": "approved"}
    decision2 = {"decision_id": "dec_002", "outcome": "denied"}
    
    # Generate different explanations (cache misses)
    await explainability_interface.explain(decision=decision1, mode="text")
    await explainability_interface.explain(decision=decision2, mode="text")
    
    cache_stats = explainability_interface.cache.get_statistics()
    assert cache_stats["misses"] >= 2


@pytest.mark.asyncio
@pytest.mark.unit
async def test_explainability_lru_cache_eviction(explainability_interface):
    """Test LRU cache eviction when reaching 1000 entry limit."""
    # Create interface with small cache
    small_cache_interface = ExplainabilityInterface(
        cache_enabled=True,
        max_cache_size=10  # Small cache for testing
    )
    
    # Generate 15 different explanations (exceeds cache limit)
    for i in range(15):
        decision = {"decision_id": f"dec_{i:03d}", "outcome": "approved"}
        await small_cache_interface.explain(decision=decision, mode="text")
    
    # Verify evictions occurred
    cache_stats = small_cache_interface.cache.get_statistics()
    assert cache_stats["evictions"] >= 5
    assert cache_stats["size"] <= 10  # Should not exceed max


@pytest.mark.asyncio
@pytest.mark.unit
async def test_explainability_cache_statistics(explainability_interface, sample_decision):
    """Test cache statistics tracking."""
    # Perform multiple cache operations
    for _ in range(5):
        await explainability_interface.explain(decision=sample_decision, mode="text")
    
    stats = explainability_interface.cache.get_statistics()
    
    # Verify all statistics are tracked
    assert "hits" in stats
    assert "misses" in stats
    assert "evictions" in stats
    assert "size" in stats
    assert "hit_rate" in stats
    
    # Hit rate should be reasonable
    assert 0.0 <= stats["hit_rate"] <= 1.0


# ============================================================================
# TEST-HIGH-EXPLAIN-06: Cryptographic Signing
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
async def test_explainability_crypto_signing(explainability_interface, sample_decision):
    """Test SRD cryptographic signing of explanations."""
    # Generate signed explanation
    explanation = await explainability_interface.explain(
        decision=sample_decision,
        mode="text",
        sign_explanation=True,
        signing_key="test_secret_key_123"
    )
    
    # Verify signature exists
    assert explanation.signature is not None
    assert len(explanation.signature) > 0
    
    # Verify signature metadata
    assert "signature_algorithm" in explanation.metadata
    assert explanation.metadata["signature_algorithm"] == "SHA256"
    assert "signed_at" in explanation.metadata


@pytest.mark.asyncio
@pytest.mark.unit
async def test_explainability_signature_verification(explainability_interface, sample_decision):
    """Test signature verification for signed explanations."""
    # Generate signed explanation
    explanation = await explainability_interface.explain(
        decision=sample_decision,
        mode="text",
        sign_explanation=True,
        signing_key="test_secret_key_123"
    )
    
    # Verify signature is valid
    is_valid = explainability_interface.verify_signature(
        explanation=explanation,
        signing_key="test_secret_key_123"
    )
    
    assert is_valid is True


@pytest.mark.asyncio
@pytest.mark.unit
async def test_explainability_signature_tampering_detection(explainability_interface, sample_decision):
    """Test signature tampering detection."""
    # Generate signed explanation
    explanation = await explainability_interface.explain(
        decision=sample_decision,
        mode="text",
        sign_explanation=True,
        signing_key="test_secret_key_123"
    )
    
    # Tamper with content
    original_content = explanation.content
    explanation.content = "TAMPERED CONTENT"
    
    # Verify signature is now invalid
    is_valid = explainability_interface.verify_signature(
        explanation=explanation,
        signing_key="test_secret_key_123"
    )
    
    assert is_valid is False
    
    # Restore content
    explanation.content = original_content


@pytest.mark.asyncio
@pytest.mark.unit
async def test_explainability_signature_wrong_key(explainability_interface, sample_decision):
    """Test signature verification with wrong key."""
    # Generate signed explanation
    explanation = await explainability_interface.explain(
        decision=sample_decision,
        mode="text",
        sign_explanation=True,
        signing_key="correct_key_123"
    )
    
    # Verify with wrong key
    is_valid = explainability_interface.verify_signature(
        explanation=explanation,
        signing_key="wrong_key_456"
    )
    
    assert is_valid is False


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
async def test_explainability_full_pipeline(explainability_interface, mock_symbolic_engine, mock_meg_client, sample_decision):
    """Test complete explainability pipeline with all features."""
    explainability_interface.symbolic_engine = mock_symbolic_engine
    explainability_interface.meg_client = mock_meg_client
    
    # Generate comprehensive explanation
    explanation = await explainability_interface.explain(
        decision=sample_decision,
        mode="multimodal",
        detail_level="comprehensive",
        include_consciousness_context=True,
        include_formal_proof=True,
        include_reasoning_trace=True,
        sign_explanation=True,
        entity_id="user_123",
        signing_key="test_key"
    )
    
    # Verify all components present
    assert explanation.mode == "multimodal"
    assert explanation.signature is not None
    assert "consciousness_context" in explanation.metadata
    assert "formal_proof" in explanation.metadata
    assert "reasoning_trace" in explanation.metadata
    
    # Verify completeness
    completeness = await explainability_interface.calculate_completeness(explanation)
    assert completeness.overall_score > 0.7  # High completeness expected


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.unit
async def test_explainability_empty_decision(explainability_interface):
    """Test handling of empty decision."""
    with pytest.raises(ValueError, match="Decision cannot be empty"):
        await explainability_interface.explain(decision={}, mode="text")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_explainability_invalid_mode(explainability_interface, sample_decision):
    """Test handling of invalid explanation mode."""
    with pytest.raises(ValueError, match="Invalid explanation mode"):
        await explainability_interface.explain(decision=sample_decision, mode="invalid_mode")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_explainability_invalid_proof_system(explainability_interface, sample_decision):
    """Test handling of invalid proof system."""
    with pytest.raises(ValueError, match="Invalid proof system"):
        await explainability_interface.generate_formal_proof(
            decision=sample_decision,
            proof_system="invalid_system"
        )
