"""
Test fixtures for explainability interface testing.

Part of BATCH-COPILOT-2025-10-08-01
TaskID: ASSIST-HIGH-TEST-EXPLAIN-i9j0k1l2
"""

from typing import Any, Dict, List

import pytest


@pytest.fixture
def sample_explanation_templates() -> Dict[str, str]:
    """Sample explanation templates for different formats."""
    return {
        "text": "The action '{action}' was taken with {confidence}% confidence based on {factors}.",
        "symbolic": "⚛️ {action} ← {factors} [ψ={confidence}]",
        "formal": "∀x: {premise} → {conclusion} [confidence={confidence}]",
    }


@pytest.fixture
def mock_decision_simple() -> Dict[str, Any]:
    """Simple mock decision for testing."""
    return {
        "action": "grant_access",
        "confidence": 0.92,
        "factors": ["valid_jwt", "tier_authorized"],
        "timestamp": 1735678800,
    }


@pytest.fixture
def mock_decision_complex() -> Dict[str, Any]:
    """Complex mock decision with multi-level reasoning."""
    return {
        "action": "deny_access",
        "confidence": 0.88,
        "factors": ["expired_token", "rate_limit_exceeded", "suspicious_pattern"],
        "reasoning_chain": [
            {"step": 1, "rule": "check_token", "result": "expired"},
            {"step": 2, "rule": "check_rate_limit", "result": "exceeded"},
            {"step": 3, "rule": "guardian_review", "result": "suspicious"},
        ],
        "guardian_flags": ["anomaly_detected"],
        "timestamp": 1735678800,
    }


@pytest.fixture
def mock_meg_response() -> Dict[str, Any]:
    """Mock MEG (Memory-Emotion-Glyph) engine response."""
    return {
        "memory": {"context": "user_history", "relevance": 0.85, "items": ["previous_login", "profile_completion"]},
        "emotion": {"valence": "neutral", "arousal": "low", "confidence": 0.75},
        "glyph": {"symbol": "⚛️", "meaning": "identity_verified", "tier": "symbolic"},
    }


@pytest.fixture
def mock_symbolic_engine_response() -> Dict[str, Any]:
    """Mock symbolic reasoning engine response."""
    return {
        "symbols": ["⚛️", "🧠", "🛡️"],
        "reasoning": "Identity verified → Consciousness active → Guardian approved",
        "proof_type": "logical_inference",
        "steps": [
            {"premise": "valid_identity", "operator": "→", "conclusion": "grant_access"},
            {"premise": "grant_access", "operator": "∧", "conclusion": "log_audit"},
        ],
    }


@pytest.fixture
def explanation_context_minimal() -> Dict[str, Any]:
    """Minimal context for explanation generation."""
    return {"user_id": "test_user_123", "session_id": "session_abc", "locale": "en_US"}


@pytest.fixture
def explanation_context_full() -> Dict[str, Any]:
    """Full context for explanation generation including Trinity Framework."""
    return {
        "user_id": "test_user_123",
        "session_id": "session_abc",
        "locale": "en_US",
        "trinity": {
            "identity": {"lambda_id": "λ_user_123", "tier": "free"},
            "consciousness": {"state": "active", "awareness_level": 0.82},
            "guardian": {"status": "monitoring", "alerts": []},
        },
        "preferences": {"detail_level": "high", "include_proof": True, "format": "multi_modal"},
    }


@pytest.fixture
def mock_proof_data() -> Dict[str, Any]:
    """Mock formal proof data."""
    return {
        "proof_type": "logical_inference",
        "premises": [
            "∀x: valid_jwt(x) → authenticated(x)",
            "authenticated(user_123)",
            "∀x: authenticated(x) ∧ tier_valid(x) → access_granted(x)",
        ],
        "conclusion": "access_granted(user_123)",
        "validity": True,
        "confidence": 0.95,
    }


@pytest.fixture
def sample_multi_modal_explanation() -> Dict[str, Any]:
    """Sample multi-modal explanation output."""
    return {
        "text": "Access granted with 92% confidence based on valid JWT authentication and tier authorization.",
        "symbolic": "⚛️ grant_access ← [valid_jwt, tier_authorized] [ψ=0.92]",
        "visual": {
            "diagram_type": "flow_chart",
            "nodes": [
                {"id": "jwt", "label": "Valid JWT", "status": "passed"},
                {"id": "tier", "label": "Tier Check", "status": "passed"},
                {"id": "access", "label": "Grant Access", "status": "success"},
            ],
            "edges": [{"from": "jwt", "to": "access"}, {"from": "tier", "to": "access"}],
        },
        "proof": {"type": "logical_inference", "valid": True},
    }


@pytest.fixture
def mock_explainability_interface():
    """Mock ExplainabilityInterface for testing."""
    pytest.skip("Pending implementation")
    # TODO: Return mock instance once interface defined
    # from unittest.mock import MagicMock
    # mock = MagicMock()
    # mock.explain.return_value = {...}
    # return mock


# Parametrized fixture for different explanation formats
@pytest.fixture(params=["text", "symbolic", "visual", "formal"])
def explanation_format(request):
    """Parametrized fixture for different explanation formats."""
    return request.param


# Parametrized fixture for detail levels
@pytest.fixture(params=["low", "medium", "high"])
def detail_level(request):
    """Parametrized fixture for different detail levels."""
    return request.param


@pytest.fixture
def mock_template_loader():
    """Mock template loader for explanation templates."""

    class MockTemplateLoader:
        def load(self, format: str, detail_level: str) -> str:
            templates = {
                ("text", "low"): "Action: {action}",
                ("text", "medium"): "Action: {action} with {confidence}% confidence",
                ("text", "high"): "Action: {action} with {confidence}% confidence based on {factors}",
                ("symbolic", "low"): "{action}",
                ("symbolic", "medium"): "⚛️ {action} [ψ={confidence}]",
                ("symbolic", "high"): "⚛️ {action} ← {factors} [ψ={confidence}]",
            }
            return templates.get((format, detail_level), "Default template")

    return MockTemplateLoader()


@pytest.fixture
def sample_lambda_trace() -> List[Dict[str, Any]]:
    """Sample ΛTRACE audit trail for explanation context."""
    return [
        {"timestamp": 1735678800, "event": "jwt_verification", "status": "success", "lambda_id": "λ_user_123"},
        {"timestamp": 1735678801, "event": "tier_check", "status": "success", "tier": "free"},
        {"timestamp": 1735678802, "event": "access_decision", "status": "granted", "reason": "all_checks_passed"},
    ]


@pytest.fixture
def mock_guardian_context() -> Dict[str, Any]:
    """Mock Guardian system context for explanations."""
    return {
        "status": "active",
        "checks_performed": ["identity_validation", "tier_authorization", "ethical_review"],
        "flags": [],
        "compliance": {"gdpr": True, "constitutional_ai": True},
    }
