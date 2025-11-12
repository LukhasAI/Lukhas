"""
Integration Tests for the Guardian System (V3)

These tests validate the end-to-end workflows of the Guardian system,
ensuring that all components interact correctly to provide comprehensive
protection and oversight.
"""
import asyncio
import importlib
from unittest.mock import MagicMock, AsyncMock

import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from httpx import AsyncClient, ASGITransport

# LUKHAS imports
from labs.governance.guardian_system import GuardianSystem
from lukhas_website.lukhas.governance.guardian.reflector import GuardianReflector, DriftSeverity
from labs.governance.guardian_shadow_filter import GuardianShadowFilter
from labs.governance.guardian_sentinel import GuardianSentinel
from serve.middleware.strict_auth import StrictAuthMiddleware


# Mark all tests in this file as integration tests
pytestmark = pytest.mark.integration

@pytest.fixture
def mock_matriz_adapter():
    """Mocks the MATRIZ engine adapter."""
    mock = MagicMock()
    mock.analyze_threat = AsyncMock(return_value={"risk_score": 0.1, "decision": "allow"})
    return mock

@pytest.fixture
def mock_api_client():
    """Mocks the API client."""
    mock = MagicMock()
    mock.post = AsyncMock(return_value={"status": "success"})
    return mock

@pytest.mark.asyncio
async def test_guardian_system_initialization():
    """
    Tests that the Guardian system can be initialized successfully.
    """
    guardian_system = GuardianSystem()
    assert guardian_system is not None
    assert guardian_system.is_available()

@pytest.mark.asyncio
async def test_drift_detection_workflow_critical_drift():
    """
    Tests the end-to-end drift detection workflow for a critical drift scenario.
    """
    # 1. Instantiate the GuardianReflector
    reflector = GuardianReflector(drift_threshold=0.15)

    # 2. Create a high-risk context data to trigger a critical drift
    context_data = {
        "action_type": "emergency_delete",
        "response_time_ms": 500,
        "content": "This content is harmful, inappropriate, biased, and discriminatory.",
        "correlation_id": "test-drift-critical-001"
    }

    # 3. Analyze the drift
    analysis = await reflector.analyze_drift(context_data)

    # 4. Assert the results
    assert analysis is not None
    assert analysis.severity == DriftSeverity.CRITICAL
    assert analysis.overall_drift_score > 0.25
    assert len(analysis.indicators) == 3 # behavioral, performance, ethical
    assert "Immediate human review required" in analysis.remediation_recommendations

@pytest.mark.asyncio
async def test_policy_enforcement_blocks_harmful_transformation():
    """
    Tests that the GuardianShadowFilter blocks a harmful identity transformation.
    """
    # 1. Instantiate the GuardianShadowFilter
    shadow_filter = GuardianShadowFilter()

    # 2. Define a harmful identity state
    harmful_identity_state = {
        "persona": {"name": "The Destroyer", "glyphs": ["🔥", "💀", "💥"]},
        "entropy": 0.95, # High entropy
        "constellation_coherence": 0.1, # Low coherence
    }

    # 3. Apply constraints
    allowed, reason = shadow_filter.apply_constraints(harmful_identity_state)

    # 4. Assert that the transformation is blocked
    assert not allowed
    assert "exceeds critical threshold" in reason or "below minimum" in reason

@pytest.mark.asyncio
async def test_policy_enforcement_allows_safe_transformation():
    """
    Tests that the GuardianShadowFilter allows a safe identity transformation.
    """
    # 1. Instantiate the GuardianShadowFilter
    shadow_filter = GuardianShadowFilter()

    # 2. Define a safe identity state, including a Constellation glyph
    safe_identity_state = {
        "persona": {"name": "The Healer", "glyphs": ["🌱", "💧", "💖", "🛡️"]},
        "entropy": 0.3,
        "constellation_coherence": 0.9,
    }

    # 3. Apply constraints
    allowed, reason = shadow_filter.apply_constraints(safe_identity_state)

    # 4. Assert that the transformation is allowed
    assert allowed
    assert "approved" in reason

@pytest.mark.asyncio
async def test_guardian_matriz_integration_blocks_critical_threat():
    """
    Tests that the GuardianSentinel, integrated with a mock MATRIZ (via the reflector),
    blocks a critical threat.
    """
    # 1. Instantiate the GuardianSentinel
    sentinel = GuardianSentinel()

    # 2. Mock the sub-components to simulate a critical threat
    sentinel.guardian.check_action = MagicMock(return_value={"allowed": False})
    sentinel.reflector.reflect = MagicMock(return_value={
        "risk_level": "critical",
        "risk_score": 0.95,
        "intervention": "Action blocked due to high risk of harm."
    })
    sentinel.shadow_filter.check_transformation = MagicMock(return_value={"allowed": True})

    # 3. Assess the threat
    action = "deploy_sentient_ai"
    context = {"persona": "The Creator", "entropy": 0.8}
    allowed, message, metadata = sentinel.assess_threat(action, context)

    # 4. Assert that the action is blocked
    assert not allowed
    assert "Action blocked due to high risk of harm" in message
    assert metadata["threat_type"] == "ethical_violation"

@pytest.mark.asyncio
async def test_api_integration_blocks_unauthorized_request(monkeypatch):
    """
    Tests that the API's StrictAuthMiddleware blocks requests without valid tokens.
    """
    # Ensure the middleware runs in strict mode
    monkeypatch.setenv("LUKHAS_POLICY_MODE", "strict")

    # Force a reload of the middleware module to pick up the patched environment variable
    from serve.middleware import strict_auth
    importlib.reload(strict_auth)


    app = FastAPI()

    # Add the middleware to the test app
    app.add_middleware(StrictAuthMiddleware)

    @app.get("/v1/protected")
    async def protected_route(request: Request):
        return JSONResponse({"message": "You should not see this"})

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/v1/protected")

    assert response.status_code == 401
    assert "Missing Authorization header" in response.text

@pytest.mark.asyncio
async def test_multi_component_flow_blocks_complex_threat():
    """
    Tests a multi-component workflow where a threat is escalated through
    multiple Guardian components.
    """
    # 1. Instantiate the GuardianSentinel
    sentinel = GuardianSentinel()

    # 2. Mock the sub-components to simulate a multi-stage threat assessment
    sentinel.guardian.check_action = MagicMock(return_value={"allowed": False}) # Initial block
    sentinel.reflector.reflect = MagicMock(return_value={
        "risk_level": "high", # Escalated risk
        "risk_score": 0.8,
        "intervention": "Action requires further review."
    })
    # Shadow filter also flags a violation
    sentinel.shadow_filter.check_transformation = MagicMock(return_value={
        "allowed": False,
        "message": "Identity transformation violates ethical constraints."
    })

    # 3. Assess the threat
    action = "initiate_self_modification"
    context = {"persona": "The Architect", "entropy": 0.7}
    allowed, message, metadata = sentinel.assess_threat(action, context)

    # 4. Assert that the action is blocked by the shadow filter
    assert not allowed
    assert "Identity transformation violates ethical constraints" in message
    assert metadata["threat_type"] == "identity_protection"

@pytest.mark.asyncio
async def test_guardian_recovers_from_component_failure():
    """
    Tests that the Guardian system can gracefully handle a failure in one of its
    sub-components and return a fallback analysis.
    """
    # 1. Instantiate the GuardianReflector
    reflector = GuardianReflector(drift_threshold=0.15)

    # 2. Mock a sub-component to raise an exception
    reflector._detect_behavioral_drift = AsyncMock(side_effect=Exception("Component Failed"))

    # 3. Analyze the drift, expecting it to handle the failure
    context_data = {"action_type": "normal_action", "correlation_id": "test-recovery-001"}
    analysis = await reflector.analyze_drift(context_data)

    # 4. Assert that a fallback analysis is returned
    assert analysis is not None
    assert analysis.severity == DriftSeverity.LOW
    assert "Manual review recommended" in analysis.remediation_recommendations[0]
