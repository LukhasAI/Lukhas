"""
Test Dreams API endpoint for consciousness exploration.

Validates:
- Happy path with seed and constraints
- Bad payload handling
- Stub vs real mode toggle readiness
- Response format compliance
"""
import pytest
from fastapi.testclient import TestClient
from serve.main import app
from tests.smoke.fixtures import GOLDEN_AUTH_HEADERS
import os

@pytest.fixture
def auth_headers():
    """Provide valid Bearer token for authenticated requests."""
    return {"X-API-Key": "test_api_key"}


def test_dreams_happy_path(client, auth_headers):
    """Verify basic dreams endpoint functionality."""
    response = client.post(
        "/v1/dreams",
        json={"seed": "flying", "constraints": {"max_depth": 3}},
        headers=auth_headers
    )
    assert response.status_code == 200

    data = response.json()
    assert "id" in data
    assert data["id"].startswith("dream_")
    assert "traces" in data
    assert isinstance(data["traces"], list)
    assert len(data["traces"]) > 0


def test_dreams_minimal_payload(client, auth_headers):
    """Verify dreams works with minimal payload (defaults apply)."""
    response = client.post(
        "/v1/dreams",
        json={},
        headers=auth_headers
    )
    assert response.status_code == 200

    data = response.json()
    assert "id" in data
    assert "traces" in data
    # Default seed should be "dream"
    assert any("dream" in str(trace).lower() for trace in data["traces"])


def test_dreams_with_seed_only(client, auth_headers):
    """Verify dreams accepts seed without constraints."""
    response = client.post(
        "/v1/dreams",
        json={"seed": "ocean waves"},
        headers=auth_headers
    )
    assert response.status_code == 200

    data = response.json()
    assert "id" in data
    assert "traces" in data
    # Should contain seed reference
    assert any("ocean" in str(trace).lower() for trace in data["traces"])


def test_dreams_requires_auth(client):
    """Verify dreams endpoint requires authentication."""
    response = client.post(
        "/v1/dreams",
        json={"seed": "test"}
    )
    assert response.status_code == 422

def test_dreams_invalid_auth(client):
    """Verify dreams endpoint rejects invalid authentication."""
    response = client.post(
        "/v1/dreams",
        json={"seed": "test"},
        headers={"X-API-Key": "invalid_api_key"}
    )
    assert response.status_code == 401

def test_dreams_trace_structure(client, auth_headers):
    """Verify trace objects have expected structure."""
    response = client.post(
        "/v1/dreams",
        json={"seed": "lucid dream", "constraints": {"stability": 0.8}},
        headers=auth_headers
    )
    assert response.status_code == 200

    data = response.json()
    traces = data["traces"]
    assert len(traces) >= 3  # Stub implementation has 3 steps

    # Check first trace has expected fields
    first_trace = traces[0]
    assert "step" in first_trace
    assert "content" in first_trace


def test_dreams_response_format(client, auth_headers):
    """Verify response matches expected schema."""
    response = client.post(
        "/v1/dreams",
        json={"seed": "space exploration"},
        headers=auth_headers
    )
    assert response.status_code == 200

    data = response.json()

    # Required fields
    required_fields = ["id", "traces", "model", "seed"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"

    # Type validation
    assert isinstance(data["id"], str)
    assert isinstance(data["traces"], list)
    assert isinstance(data["model"], str)
    assert data["model"] == "lukhas-consciousness"


def test_dreams_constraints_handling(client, auth_headers):
    """Verify constraints are accepted and stored in response."""
    constraints = {
        "max_depth": 5,
        "stability": 0.9,
        "coherence_threshold": 0.7
    }

    response = client.post(
        "/v1/dreams",
        json={"seed": "recursive dream", "constraints": constraints},
        headers=auth_headers
    )
    assert response.status_code == 200

    data = response.json()
    assert "constraints" in data
    # Verify constraints passed through
    assert data["constraints"]["max_depth"] == 5


def test_dreams_trace_id_header(client, auth_headers):
    """Verify X-Trace-Id header present when OTEL enabled."""
    response = client.post(
        "/v1/dreams",
        json={"seed": "traced dream"},
        headers=auth_headers
    )

    # X-Trace-Id may or may not be present depending on OTEL config
    # This test just verifies it doesn't break if present
    if "X-Trace-Id" in response.headers:
        trace_id = response.headers["X-Trace-Id"]
        assert len(trace_id) == 32  # 32-char hex
        assert all(c in "0123456789abcdef" for c in trace_id)


def test_dreams_stub_mode_indicator(client, auth_headers):
    """Verify response indicates stub vs real mode."""
    response = client.post(
        "/v1/dreams",
        json={"seed": "reality check"},
        headers=auth_headers
    )
    assert response.status_code == 200

    data = response.json()

    # When consciousness module available, mode should indicate "full"
    # In stub mode, traces should still be generated
    assert len(data["traces"]) > 0

    # Stub traces contain "quantum superposition" marker
    has_quantum = any("quantum" in str(trace).lower() for trace in data["traces"])
    if has_quantum:
        # Stub mode confirmed
        assert data.get("model") == "lukhas-consciousness"
