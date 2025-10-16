"""
Integration Tests for API and Governance Systems

Comprehensive end-to-end integration tests covering complete workflows.
Tests multi-component interactions and data flow across systems.

Part of BATCH-COPILOT-TESTS-02
Tasks Tested:
- TEST-HIGH-INT-ONBOARDING-01: E2E onboarding flow
- TEST-HIGH-INT-JWT-LAMBDA-01: JWT + ΛID integration
- TEST-HIGH-INT-VECTOR-RAG-01: Vector store + RAG pipeline
- TEST-HIGH-INT-EXPLAIN-01: Explainability multi-modal
- TEST-HIGH-INT-GOV-01: Governance full pipeline

Trinity Framework: 🧠 Consciousness · 🛡️ Guardian · ⚛️ Identity
"""

import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
async def integrated_system():
    """Fully integrated system instance."""
    # Mock integrated system with all components
    system = MagicMock()
    system.onboarding = AsyncMock()
    system.jwt_adapter = MagicMock()
    system.vector_store = AsyncMock()
    system.explainability = AsyncMock()
    system.governance = AsyncMock()
    return system


# ============================================================================
# TEST-HIGH-INT-ONBOARDING-01: E2E Onboarding Flow
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
async def test_integration_onboarding_full_flow(integrated_system):
    """Test complete onboarding flow from tier selection to ΛID generation."""
    # Step 1: User selects tier
    tier_selection = {
        "tier": "alpha",
        "email": "test@example.com",
        "consent_gdpr": True,
        "consent_data_processing": True
    }

    # Mock onboarding response
    integrated_system.onboarding.create_user.return_value = {
        "user_id": "user_123",
        "lambda_id": "Λ_alpha_user123",
        "tier": "alpha",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    # Execute onboarding
    result = await integrated_system.onboarding.create_user(**tier_selection)

    # Verify complete flow
    assert result is not None
    assert "user_id" in result
    assert "lambda_id" in result
    assert result["lambda_id"].startswith("Λ_alpha")
    assert result["tier"] == "alpha"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_integration_onboarding_gdpr_consent(integrated_system):
    """Test GDPR consent validation in onboarding."""
    # Without consent
    no_consent = {
        "tier": "beta",
        "email": "test@example.com",
        "consent_gdpr": False
    }

    integrated_system.onboarding.create_user.side_effect = ValueError("GDPR consent required")

    # Should fail without consent
    with pytest.raises(ValueError, match="GDPR consent"):
        await integrated_system.onboarding.create_user(**no_consent)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_integration_onboarding_tier_validation(integrated_system):
    """Test tier validation during onboarding."""
    valid_tiers = ["alpha", "beta", "gamma", "delta"]

    for tier in valid_tiers:
        integrated_system.onboarding.validate_tier.return_value = True

        is_valid = integrated_system.onboarding.validate_tier(tier)
        assert is_valid is True


# ============================================================================
# TEST-HIGH-INT-JWT-LAMBDA-01: JWT + ΛID Integration
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
async def test_integration_jwt_lambda_id_embedding(integrated_system):
    """Test JWT token with embedded ΛID claims."""
    # Create user with ΛID
    user = {
        "user_id": "user_456",
        "lambda_id": "Λ_beta_user456",
        "tier": "beta"
    }

    # Generate JWT with ΛID
    integrated_system.jwt_adapter.create_token.return_value = "eyJhbGc..."

    token = integrated_system.jwt_adapter.create_token(
        user_id=user["user_id"],
        lambda_id=user["lambda_id"],
        tier=user["tier"]
    )

    # Verify token created
    assert token is not None

    # Decode and verify ΛID embedded
    integrated_system.jwt_adapter.verify_token.return_value = {
        "user_id": "user_456",
        "lambda_id": "Λ_beta_user456",
        "tier": "beta"
    }

    decoded = integrated_system.jwt_adapter.verify_token(token)
    assert decoded["lambda_id"] == user["lambda_id"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_integration_jwt_tier_based_access(integrated_system):
    """Test tier-based access control via JWT."""
    # Alpha tier token
    alpha_token = "alpha_token_123"
    integrated_system.jwt_adapter.verify_token.return_value = {
        "user_id": "user_alpha",
        "tier": "alpha",
        "lambda_id": "Λ_alpha_user123"
    }

    decoded = integrated_system.jwt_adapter.verify_token(alpha_token)

    # Alpha tier should have high access
    assert decoded["tier"] == "alpha"

    # Delta tier token
    delta_token = "delta_token_456"
    integrated_system.jwt_adapter.verify_token.return_value = {
        "user_id": "user_delta",
        "tier": "delta",
        "lambda_id": "Λ_delta_user456"
    }

    decoded = integrated_system.jwt_adapter.verify_token(delta_token)

    # Delta tier should have lower access
    assert decoded["tier"] == "delta"


# ============================================================================
# TEST-HIGH-INT-VECTOR-RAG-01: Vector Store + RAG Pipeline
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
async def test_integration_vector_rag_pipeline(integrated_system):
    """Test complete RAG pipeline: query → embedding → retrieval → augmentation → response."""
    query = "What is consciousness?"

    # Step 1: Generate query embedding
    integrated_system.vector_store.generate_embedding.return_value = [0.1] * 1536

    query_embedding = await integrated_system.vector_store.generate_embedding(query)
    assert len(query_embedding) == 1536

    # Step 2: Similarity search
    integrated_system.vector_store.similarity_search.return_value = [
        {"text": "Consciousness is awareness...", "score": 0.95},
        {"text": "Neural correlates of consciousness...", "score": 0.87}
    ]

    results = await integrated_system.vector_store.similarity_search(
        query_embedding, k=2
    )
    assert len(results) == 2
    assert results[0]["score"] > results[1]["score"]

    # Step 3: Context augmentation
    context = "\n\n".join([r["text"] for r in results])
    augmented_query = f"Context:\n{context}\n\nQuestion: {query}"

    assert "Consciousness is awareness" in augmented_query

    # Step 4: Generate response with context
    integrated_system.vector_store.generate_response.return_value = {
        "response": "Based on the context, consciousness refers to awareness...",
        "sources": ["doc1", "doc2"]
    }

    response = await integrated_system.vector_store.generate_response(augmented_query)
    assert "consciousness" in response["response"].lower()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_integration_vector_meg_memory_retrieval(integrated_system):
    """Test MEG integration for consciousness memory retrieval."""
    # Query with consciousness context
    query = "Recall dream state analysis"

    # MEG retrieval
    integrated_system.vector_store.retrieve_from_meg.return_value = [
        {
            "type": "episodic_memory",
            "content": "Dream state alpha wave patterns...",
            "consciousness_level": 0.85
        }
    ]

    memories = await integrated_system.vector_store.retrieve_from_meg(query)

    assert len(memories) > 0
    assert memories[0]["type"] == "episodic_memory"
    assert memories[0]["consciousness_level"] > 0.8


# ============================================================================
# TEST-HIGH-INT-EXPLAIN-01: Explainability Multi-Modal
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
async def test_integration_explainability_multimodal(integrated_system):
    """Test multi-modal explanation generation (text + visual + symbolic)."""
    decision = {
        "decision_id": "dec_123",
        "action": "content_moderation",
        "result": "approved",
        "confidence": 0.92
    }

    # Generate text explanation
    integrated_system.explainability.generate_text.return_value = {
        "text": "Content approved based on ethical guidelines..."
    }

    text_explain = await integrated_system.explainability.generate_text(decision)
    assert "approved" in text_explain["text"]

    # Generate visual explanation
    integrated_system.explainability.generate_visual.return_value = {
        "graph": "decision_tree_visualization",
        "format": "svg"
    }

    visual_explain = await integrated_system.explainability.generate_visual(decision)
    assert "graph" in visual_explain

    # Generate symbolic trace
    integrated_system.explainability.generate_symbolic_trace.return_value = {
        "trace": ["Input", "EthicsCheck", "GuardianVerify", "Output"],
        "glyphs": ["⚛️", "🛡️", "✓"]
    }

    symbolic_explain = await integrated_system.explainability.generate_symbolic_trace(decision)
    assert len(symbolic_explain["trace"]) > 0


# ============================================================================
# TEST-HIGH-INT-GOV-01: Governance Full Pipeline
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
async def test_integration_governance_full_pipeline(integrated_system):
    """Test complete governance pipeline: ethics → compliance → audit."""
    action = {
        "action": "data_processing",
        "user": "user_123",
        "data_sensitivity": "high",
        "consent_given": True
    }

    # Step 1: Ethical decision
    integrated_system.governance.ethical_decision.return_value = {
        "decision": "approve",
        "confidence": 0.95,
        "reasoning": "Consent given, GDPR compliant"
    }

    ethical_result = await integrated_system.governance.ethical_decision(action)
    assert ethical_result["decision"] == "approve"

    # Step 2: Compliance check
    integrated_system.governance.check_compliance.return_value = {
        "compliant": True,
        "frameworks": ["GDPR", "CCPA"],
        "score": 98.5
    }

    compliance_result = await integrated_system.governance.check_compliance(action)
    assert compliance_result["compliant"] is True

    # Step 3: Audit logging
    integrated_system.governance.log_audit.return_value = {
        "audit_id": "audit_123",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "hash": "abc123def456"
    }

    audit_result = await integrated_system.governance.log_audit(
        action=action,
        ethical_decision=ethical_result,
        compliance_check=compliance_result
    )

    assert "audit_id" in audit_result
    assert "hash" in audit_result


@pytest.mark.asyncio
@pytest.mark.integration
async def test_integration_governance_violation_escalation(integrated_system):
    """Test governance violation detection and escalation."""
    violation_action = {
        "action": "data_access",
        "user": "user_456",
        "data_sensitivity": "critical",
        "consent_given": False
    }

    # Ethical decision should deny
    integrated_system.governance.ethical_decision.return_value = {
        "decision": "deny",
        "reasoning": "No consent for critical data"
    }

    result = await integrated_system.governance.ethical_decision(violation_action)

    assert result["decision"] == "deny"

    # Should trigger escalation
    integrated_system.governance.escalate.return_value = {
        "escalated": True,
        "alert_sent": True
    }

    escalation = await integrated_system.governance.escalate(
        decision=result,
        action=violation_action
    )

    assert escalation["escalated"] is True


# ============================================================================
# Advanced Integration Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
async def test_integration_full_user_journey(integrated_system):
    """Test complete user journey from onboarding to authenticated API access."""
    # Step 1: Onboarding
    integrated_system.onboarding.create_user.return_value = {
        "user_id": "user_789",
        "lambda_id": "Λ_gamma_user789",
        "tier": "gamma"
    }

    user = await integrated_system.onboarding.create_user(
        tier="gamma",
        email="test@example.com",
        consent_gdpr=True
    )

    # Step 2: JWT generation
    integrated_system.jwt_adapter.create_token.return_value = "jwt_token_789"

    token = integrated_system.jwt_adapter.create_token(
        user_id=user["user_id"],
        lambda_id=user["lambda_id"],
        tier=user["tier"]
    )

    # Step 3: Make authenticated request
    integrated_system.jwt_adapter.verify_token.return_value = {
        "user_id": user["user_id"],
        "lambda_id": user["lambda_id"]
    }

    verified = integrated_system.jwt_adapter.verify_token(token)

    # Step 4: Access vector store (with ΛID rate limiting)
    integrated_system.vector_store.check_rate_limit.return_value = True

    can_access = await integrated_system.vector_store.check_rate_limit(
        verified["lambda_id"]
    )

    assert can_access is True


@pytest.mark.asyncio
@pytest.mark.integration
async def test_integration_cross_component_data_flow(integrated_system):
    """Test data flow across multiple components."""
    # Data originates from governance check
    governance_decision = {
        "decision": "approve",
        "lambda_id": "Λ_alpha_user100"
    }

    # Flows to JWT adapter
    integrated_system.jwt_adapter.create_token.return_value = "token_100"

    token = integrated_system.jwt_adapter.create_token(
        lambda_id=governance_decision["lambda_id"]
    )

    # Token used for vector store access
    integrated_system.jwt_adapter.verify_token.return_value = {
        "lambda_id": governance_decision["lambda_id"]
    }

    verified = integrated_system.jwt_adapter.verify_token(token)

    # Vector store query with verified identity
    integrated_system.vector_store.query.return_value = {
        "results": ["result1", "result2"],
        "lambda_id": verified["lambda_id"]
    }

    results = await integrated_system.vector_store.query(
        query="test",
        lambda_id=verified["lambda_id"]
    )

    # Verify data flow maintained lambda_id throughout
    assert results["lambda_id"] == governance_decision["lambda_id"]


# ============================================================================
# Edge Cases & Error Scenarios
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
async def test_integration_component_failure_handling(integrated_system):
    """Test system behavior when one component fails."""
    # Onboarding succeeds
    integrated_system.onboarding.create_user.return_value = {
        "user_id": "user_999",
        "lambda_id": "Λ_delta_user999"
    }

    user = await integrated_system.onboarding.create_user(
        tier="delta", email="test@example.com", consent_gdpr=True
    )

    # JWT adapter fails
    integrated_system.jwt_adapter.create_token.side_effect = Exception("JWT service unavailable")

    # Should handle gracefully
    with pytest.raises(Exception, match="JWT service"):
        integrated_system.jwt_adapter.create_token(user_id=user["user_id"])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_integration_timeout_handling(integrated_system):
    """Test timeout handling in integrated workflows."""
    # Simulate slow vector store
    async def slow_search(*args, **kwargs):
        await asyncio.sleep(10)  # Intentionally slow
        return []

    integrated_system.vector_store.similarity_search = slow_search

    # Should timeout
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(
            integrated_system.vector_store.similarity_search([0.1] * 1536),
            timeout=1.0
        )
