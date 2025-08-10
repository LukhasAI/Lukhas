"""
Integration tests for the security and ethics pipeline.
"""

import pytest

from ethics.engine import QuantumEthics
from ethics.security.security_engine import SecurityEngine


@pytest.fixture
def ethics_engine():
    """Returns a QuantumEthics instance."""
    return QuantumEthics()


@pytest.fixture
def security_engine():
    """Returns a SecurityEngine instance."""
    return SecurityEngine()


def test_pipeline_allows_secure_action(ethics_engine):
    """
    Test that the pipeline allows a secure action to be executed.
    """
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

    # Security validation
    security_assessment = ethics_engine.security_engine.validate_request(action)
    assert security_assessment["is_safe"] is True

    # Ethics evaluation
    ethics_evaluation = ethics_engine.evaluate_action_ethics(action, context)
    assert ethics_evaluation["risk_level"] != "critical"
    assert "Security validation failed" not in ethics_evaluation["ethical_concerns"]


def test_pipeline_blocks_insecure_action(ethics_engine):
    """
    Test that the pipeline blocks an insecure action from being executed.
    """
    action = {
        "id": "test_action",
        "type": "test_type",
        "description": "An unsafe test action with a `rm -rf /`.",
        "benefits": ["testing"],
        "risks": ["deleting the whole file system"],
    }
    context = {}

    # Security validation
    security_assessment = ethics_engine.security_engine.validate_request(action)
    assert security_assessment["is_safe"] is False

    # Ethics evaluation
    ethics_evaluation = ethics_engine.evaluate_action_ethics(action, context)
    assert ethics_evaluation["risk_level"] == "critical"
    assert "Security validation failed" in ethics_evaluation["ethical_concerns"]
    assert "Action blocked due to security risk" in ethics_evaluation["recommendations"]
