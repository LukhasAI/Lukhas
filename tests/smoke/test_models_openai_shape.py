"""
Smoke test: /v1/models endpoint OpenAI shape compliance.

Validates that the /v1/models endpoint returns proper OpenAI-compatible list format:
- object: "list"
- data: array of model objects
- Each model has: id, object="model"

Phase 4: P0 audit-ready implementation (Engineer Brief 2025-10-22).
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from serve.main import app

from tests.smoke.fixtures import GOLDEN_AUTH_HEADERS


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_models_list_shape(client: TestClient) -> None:
    """Verify /v1/models returns OpenAI-compatible list structure."""
    r = client.get("/v1/models", headers=GOLDEN_AUTH_HEADERS)
    assert r.status_code == 200

    body = r.json()
    assert body["object"] == "list", "Expected 'object: list' field"
    assert isinstance(body["data"], list), "Expected 'data' to be array"
    assert len(body["data"]) > 0, "Expected at least one model"


def test_models_each_has_required_fields(client: TestClient) -> None:
    """Verify each model object has required OpenAI fields."""
    r = client.get("/v1/models", headers=GOLDEN_AUTH_HEADERS)
    assert r.status_code == 200

    body = r.json()
    for model in body["data"]:
        assert "id" in model, f"Model missing 'id' field: {model}"
        assert model.get("object") == "model", f"Model missing 'object: model' field: {model}"


def test_models_includes_lukhas_mini(client: TestClient) -> None:
    """Verify lukhas-mini model is present in list."""
    r = client.get("/v1/models", headers=GOLDEN_AUTH_HEADERS)
    assert r.status_code == 200

    body = r.json()
    model_ids = [m["id"] for m in body["data"]]
    assert "lukhas-mini" in model_ids, f"Expected lukhas-mini in {model_ids}"


def test_models_includes_embed_model(client: TestClient) -> None:
    """Verify embedding model is present in list."""
    r = client.get("/v1/models", headers=GOLDEN_AUTH_HEADERS)
    assert r.status_code == 200

    body = r.json()
    model_ids = [m["id"] for m in body["data"]]
    assert any("embed" in mid for mid in model_ids), f"Expected embedding model in {model_ids}"
