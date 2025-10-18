"""
OpenAI compatibility header smoke tests.

Verifies that the API façade exposes OpenAI-style request IDs and
rate-limit aliases alongside the existing Lukhas headers.
"""
import os

import pytest
from fastapi.testclient import TestClient

from adapters.openai.api import get_app

from tests.smoke.fixtures import GOLDEN_AUTH_HEADERS


@pytest.fixture
def authz_headers():
    """Factory for authorization headers with OpenAI extensions."""

    def _headers(org: str = None, project: str = None):
        headers = GOLDEN_AUTH_HEADERS
        if org:
            headers["OpenAI-Organization"] = org
        if project:
            headers["OpenAI-Project"] = project
        return headers

    return _headers


def _client():
    """Return a façade test client with permissive policy mode."""
    # Disable Guardian PDP for smoke tests
    os.environ["LUKHAS_POLICY_PATH"] = "/nonexistent"
    os.environ.setdefault("LUKHAS_POLICY_MODE", "permissive")
    return TestClient(get_app())


def test_x_request_id_present(authz_headers):
    """Ensure X-Request-Id accompanies the canonical trace header."""
    client = _client()
    response = client.get("/v1/models", headers=authz_headers())
    assert response.status_code == 200
    # Headers are case-insensitive; FastAPI normalizes title case.
    request_id = response.headers.get("X-Request-Id") or response.headers.get("x-request-id")
    assert request_id, "Expected X-Request-Id header on façade responses"
    assert response.headers.get("X-Trace-Id"), "Expected X-Trace-Id for correlation"


def test_openai_rate_limit_aliases(authz_headers):
    """Validate that OpenAI-style rate limit aliases are included."""
    client = _client()
    response = client.get("/v1/models", headers=authz_headers())
    assert response.status_code == 200

    # OpenAI-style aliases should be present (with -requests suffix)
    assert response.headers.get("x-ratelimit-limit-requests") is not None, (
        "x-ratelimit-limit-requests header missing"
    )
    assert response.headers.get("x-ratelimit-remaining-requests") is not None, (
        "x-ratelimit-remaining-requests header missing"
    )
    assert response.headers.get("x-ratelimit-reset-requests") is not None, (
        "x-ratelimit-reset-requests header missing"
    )


def test_openai_organization_header_accepted(authz_headers):
    """Verify OpenAI-Organization header is accepted and routed."""
    client = _client()
    response = client.get("/v1/models", headers=authz_headers(org="org-test-123"))
    assert response.status_code == 200
    data = response.json()
    assert "data" in data or "object" in data, "Invalid models response format"


def test_openai_project_header_accepted(authz_headers):
    """Verify OpenAI-Project header is accepted and routed."""
    client = _client()
    response = client.get(
        "/v1/models", headers=authz_headers(org="org-test-123", project="proj-abc-456")
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data or "object" in data, "Invalid models response format"


def test_error_envelope_optional_param(authz_headers):
    """Verify error envelope optionally includes param field (OpenAI convention)."""
    client = _client()
    # Trigger validation error
    response = client.post("/v1/embeddings", headers=authz_headers(), json={"input": None})

    if response.status_code in (400, 422):
        data = response.json()
        error = data.get("error", {})

        # Param field is optional, but if present should be a string
        if "param" in error:
            assert isinstance(error["param"], str), "param field should be string when present"


def test_models_list_format_openai_compatible(authz_headers):
    """Verify /v1/models returns OpenAI-style list object."""
    client = _client()
    response = client.get("/v1/models", headers=authz_headers())
    assert response.status_code == 200

    data = response.json()
    assert data.get("object") == "list", "Models response missing 'object: list' field"
    assert "data" in data, "Models response missing 'data' array"

    # Each model should have object: "model"
    for model in data["data"]:
        assert model.get("object") == "model", f"Model missing 'object: model' field: {model}"
        assert "id" in model, f"Model missing 'id' field: {model}"
