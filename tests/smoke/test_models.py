"""
Test /v1/models endpoint for model listing and capabilities.

Validates:
- OpenAI-compatible model listing format
- Model metadata (id, object, created, owned_by, capabilities)
- Authentication requirement
- Response caching behavior
- Model availability checks
"""
import pytest
from fastapi.testclient import TestClient
from lukhas.adapters.openai.api import get_app

from tests.smoke.fixtures import GOLDEN_AUTH_HEADERS


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(get_app())


@pytest.fixture
def auth_headers():
    """Provide valid Bearer token for authenticated requests."""
    return GOLDEN_AUTH_HEADERS


def test_models_requires_auth(client):
    """Verify /v1/models requires authentication."""
    response = client.get("/v1/models")
    assert response.status_code == 401


def test_models_list_format(client, auth_headers):
    """Verify models response follows OpenAI format."""
    response = client.get("/v1/models", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()

    # OpenAI format: {"data": [...]}
    assert "data" in data
    assert isinstance(data["data"], list)
    assert len(data["data"]) > 0


def test_models_lukhas_matriz_present(client, auth_headers):
    """Verify lukhas-matriz model is in the list."""
    response = client.get("/v1/models", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    models = data["data"]

    # Should have lukhas-matriz
    model_ids = [m["id"] for m in models]
    assert "lukhas-matriz" in model_ids


def test_models_metadata_complete(client, auth_headers):
    """Verify each model has complete metadata."""
    response = client.get("/v1/models", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    models = data["data"]

    for model in models:
        # Required OpenAI fields
        assert "id" in model
        assert "object" in model
        assert model["object"] == "model"
        assert "created" in model
        assert isinstance(model["created"], int)
        assert "owned_by" in model


def test_models_capabilities_field(client, auth_headers):
    """Verify lukhas-matriz model has capabilities field."""
    response = client.get("/v1/models", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    models = data["data"]

    lukhas_model = next((m for m in models if m["id"] == "lukhas-matriz"), None)
    assert lukhas_model is not None

    # Should have capabilities
    assert "capabilities" in lukhas_model
    assert isinstance(lukhas_model["capabilities"], list)

    # Should support responses, embeddings, dreams
    expected_caps = ["responses", "embeddings", "dreams"]
    for cap in expected_caps:
        assert cap in lukhas_model["capabilities"], \
            f"Missing capability: {cap}"


def test_models_owned_by_lukhas(client, auth_headers):
    """Verify lukhas-matriz is owned by lukhas-ai."""
    response = client.get("/v1/models", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    lukhas_model = next(
        (m for m in data["data"] if m["id"] == "lukhas-matriz"),
        None
    )

    assert lukhas_model is not None
    assert lukhas_model["owned_by"] == "lukhas-ai"


def test_models_created_timestamp_valid(client, auth_headers):
    """Verify created timestamp is reasonable (not zero, not future)."""
    import time

    response = client.get("/v1/models", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    models = data["data"]

    now = int(time.time())
    for model in models:
        created = model["created"]

        # Should be in past (not zero, not future)
        assert created > 0, "Created timestamp is zero"
        assert created < now + 86400, "Created timestamp is in future"


def test_models_list_stability(client, auth_headers):
    """Verify model list is stable across multiple calls."""
    response1 = client.get("/v1/models", headers=auth_headers)
    response2 = client.get("/v1/models", headers=auth_headers)

    assert response1.status_code == 200
    assert response2.status_code == 200

    data1 = response1.json()
    data2 = response2.json()

    # Should return same models
    model_ids1 = sorted([m["id"] for m in data1["data"]])
    model_ids2 = sorted([m["id"] for m in data2["data"]])

    assert model_ids1 == model_ids2


def test_models_no_duplicate_ids(client, auth_headers):
    """Verify no duplicate model IDs in the list."""
    response = client.get("/v1/models", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    models = data["data"]

    model_ids = [m["id"] for m in models]
    unique_ids = set(model_ids)

    assert len(model_ids) == len(unique_ids), \
        f"Duplicate model IDs found: {model_ids}"


def test_models_invalid_token_returns_401(client):
    """Verify invalid Bearer token returns 401."""
    response = client.get(
        "/v1/models",
        headers={"Authorization": "Bearer short"}  # Too short (< 8 chars)
    )
    # Actually this will return 200 if token is >= 8 chars in stub mode
    # Let's use a token that's definitely too short
    response = client.get(
        "/v1/models",
        headers={"Authorization": "Bearer abc"}  # Only 3 chars
    )
    assert response.status_code == 401


def test_models_different_tenants_same_list(client):
    """Verify different tenants see same model list (for now)."""
    # Two different tokens (different orgs)
    token1 = {"Authorization": "Bearer sk-lukhas-org1-1234567890abcdef"}
    token2 = {"Authorization": "Bearer sk-lukhas-org2-9876543210fedcba"}

    response1 = client.get("/v1/models", headers=token1)
    response2 = client.get("/v1/models", headers=token2)

    assert response1.status_code == 200
    assert response2.status_code == 200

    # For now, all tenants see same models
    # (In future, might be tenant-specific)
    model_ids1 = sorted([m["id"] for m in response1.json()["data"]])
    model_ids2 = sorted([m["id"] for m in response2.json()["data"]])

    assert model_ids1 == model_ids2


def test_models_response_cacheable(client, auth_headers):
    """Verify models response can be cached (no dynamic data)."""
    response1 = client.get("/v1/models", headers=auth_headers)
    response2 = client.get("/v1/models", headers=auth_headers)

    assert response1.status_code == 200
    assert response2.status_code == 200

    # Responses should be identical (cacheable)
    data1 = response1.json()
    data2 = response2.json()

    assert data1 == data2


def test_models_content_type_json(client, auth_headers):
    """Verify response Content-Type is application/json."""
    response = client.get("/v1/models", headers=auth_headers)
    assert response.status_code == 200

    content_type = response.headers.get("content-type", "")
    assert "application/json" in content_type.lower()


def test_models_trace_id_header_present(client, auth_headers):
    """Verify X-Trace-Id header when OTEL enabled."""
    response = client.get("/v1/models", headers=auth_headers)
    assert response.status_code == 200

    # X-Trace-Id may or may not be present depending on OTEL config
    # Just verify it doesn't break if present
    if "X-Trace-Id" in response.headers:
        trace_id = response.headers["X-Trace-Id"]
        assert len(trace_id) == 32  # 32-char hex
        assert all(c in "0123456789abcdef" for c in trace_id)
