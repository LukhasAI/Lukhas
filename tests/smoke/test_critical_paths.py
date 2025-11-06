"""
Smoke tests for the critical paths of the LUKHAS system.
"""

import pytest
from fastapi.testclient import TestClient
from serve.main import app, MEMORY_AVAILABLE
from labs.core.security.auth import get_auth_system

@pytest.fixture
def client():
    """Test client for making requests to the FastAPI app."""
    return TestClient(app)


def test_healthz_endpoint(client):
    """Tests the /healthz endpoint to ensure the system is running."""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_models_endpoint(client):
    """Tests the /v1/models endpoint to ensure the API is available."""
    response = client.get("/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) > 0

# Skip memory tests if memory systems are not available
pytestmark = pytest.mark.skipif(
    not MEMORY_AVAILABLE,
    reason="Memory systems (EmbeddingIndex, IndexManager) not available"
)

@pytest.fixture
def auth_headers():
    """Valid bearer token headers."""
    auth_system = get_auth_system()
    test_token = auth_system.generate_jwt("test_user")
    return {"Authorization": f"Bearer {test_token}"}


def test_create_and_store_embedding(client, auth_headers):
    """Tests creating and storing an embedding."""
    response = client.post(
        "/v1/embeddings",
        json={
            "input": "This is a test embedding.",
            "store": True
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"][0]["embedding"]) > 0


def test_retrieve_similar_embedding(client, auth_headers):
    """Tests retrieving a similar embedding."""
    client.post(
        "/v1/embeddings",
        json={
            "input": "The sky is blue.",
            "store": True
        },
        headers=auth_headers
    )

    response = client.post(
        "/v1/embeddings",
        json={
            "input": "What color is the sky?",
            "retrieve_similar": True
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "similar_results" in data


def test_tenant_isolation(client):
    """Tests that tenants cannot access each other's data."""
    auth_system = get_auth_system()

    # Tenant A stores data
    tenant_a_token = auth_system.generate_jwt("tenant-a")
    tenant_a_headers = {"Authorization": f"Bearer {tenant_a_token}"}
    tenant_a_data = "Tenant A's very private data"
    client.post(
        "/v1/embeddings",
        json={
            "input": tenant_a_data,
            "store": True
        },
        headers=tenant_a_headers
    )

    # Tenant B should not be able to retrieve Tenant A's data
    tenant_b_token = auth_system.generate_jwt("tenant-b")
    tenant_b_headers = {"Authorization": f"Bearer {tenant_b_token}"}
    response = client.post(
        "/v1/embeddings",
        json={
            "input": tenant_a_data,
            "retrieve_similar": True
        },
        headers=tenant_b_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "similar_results" in data
    assert len(data["similar_results"]) == 0
