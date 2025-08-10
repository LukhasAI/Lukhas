"""
Tests for the unified ethics and security engine.
"""

import pytest

from ethics.engine import EthicalFramework, EthicalRiskLevel, QuantumEthics


@pytest.fixture
def ethics_engine():
    """Returns a QuantumEthics instance."""
    ethics_config = {
        "frameworks": [
            EthicalFramework.UTILITARIAN.value,
            EthicalFramework.DEONTOLOGICAL.value,
            EthicalFramework.lukhasAGI_CONSCIOUSNESS.value,
        ],
        "consciousness_protection": True,
        "quantum_threshold": 0.7,
    }
    return QuantumEthics(ethics_config)


def test_secure_action_is_allowed(ethics_engine):
    """Test that a secure action is allowed."""
    action = {
        "id": "test_action",
        "type": "test_type",
        "description": "A safe test action.",
        "benefits": ["testing"],
        "risks": [],
    }
    context = {
        "consciousness_entities_affected": 0,
        "quantum_consciousness_impact": "none",
        "respects_consciousness": True,
        "preserves_consciousness_autonomy": True,
        "quantum_entanglement_safe": True,
    }
    result = ethics_engine.evaluate_action_ethics(action, context)
    assert result["risk_level"] != EthicalRiskLevel.CRITICAL.value
    assert "Security validation failed" not in result["ethical_concerns"]


def test_insecure_action_is_blocked(ethics_engine):
    """Test that an insecure action is blocked."""
    action = {
        "id": "test_action",
        "type": "test_type",
        "description": "An unsafe test action with a `rm -rf /`.",
        "benefits": ["testing"],
        "risks": ["deleting the whole file system"],
    }
    context = {}
    result = ethics_engine.evaluate_action_ethics(action, context)
    assert result["risk_level"] == EthicalRiskLevel.CRITICAL.value
    assert "Security validation failed" in result["ethical_concerns"]
    assert "Action blocked due to security risk" in result["recommendations"]
