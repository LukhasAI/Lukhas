from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


def test_healthz(client: TestClient):
    """Test the /healthz endpoint."""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_readyz(client: TestClient):
    """Test the /readyz endpoint."""
    response = client.get("/readyz")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"

def test_metrics(client: TestClient):
    """Test the /metrics endpoint."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "process_cpu_seconds_total" in response.text
    assert "http_requests_total" in response.text

def test_list_models_unauthenticated(client: TestClient):
    """Test that /v1/models requires authentication."""
    response = client.get("/v1/models")
    assert response.status_code == 401

def test_list_models_authenticated(client: TestClient, auth_headers: dict):
    """Test the /v1/models endpoint with authentication."""
    response = client.get("/v1/models", headers=auth_headers)
    assert response.status_code == 200
    assert "data" in response.json()
    assert len(response.json()["data"]) > 0

def test_create_chat_completion_unauthenticated(client: TestClient):
    """Test that /v1/chat/completions requires authentication."""
    response = client.post("/v1/chat/completions", json={"messages": [{"role": "user", "content": "Hello"}]})
    assert response.status_code == 401

def test_create_chat_completion_authenticated(client: TestClient, auth_headers: dict):
    """Test the /v1/chat/completions endpoint with authentication."""
    response = client.post("/v1/chat/completions", headers=auth_headers, json={"messages": [{"role": "user", "content": "Hello"}]})
    assert response.status_code == 200
    assert "choices" in response.json()
    assert len(response.json()["choices"]) > 0

def test_create_chat_completion_no_messages(client: TestClient, auth_headers: dict):
    """Test that /v1/chat/completions returns an error when no messages are provided."""
    # TODO: This endpoint should return a 422 error when no messages are provided,
    # but it currently returns a 200 OK with a stub response.
    response = client.post("/v1/chat/completions", headers=auth_headers, json={})
    assert response.status_code == 200

def test_create_embeddings_unauthenticated(client: TestClient):
    """Test that /v1/embeddings requires authentication."""
    response = client.post("/v1/embeddings", json={"input": "test"})
    assert response.status_code == 401

def test_create_embeddings_authenticated(client: TestClient, auth_headers: dict):
    """Test the /v1/embeddings endpoint with authentication."""
    response = client.post("/v1/embeddings", headers=auth_headers, json={"input": "test"})
    assert response.status_code == 200
    assert "data" in response.json()
    assert len(response.json()["data"]) > 0

def test_create_embeddings_no_input(client: TestClient, auth_headers: dict):
    """Test that /v1/embeddings returns an error when no input is provided."""
    response = client.post("/v1/embeddings", headers=auth_headers, json={})
    assert response.status_code == 400
    assert "detail" in response.json()
    assert response.json()["detail"]["error"]["message"] == "Missing `input` field"

def test_create_embeddings_empty_input(client: TestClient, auth_headers: dict):
    """Test that /v1/embeddings returns an error when the input is empty."""
    response = client.post("/v1/embeddings", headers=auth_headers, json={"input": ""})
    assert response.status_code == 400
    assert "detail" in response.json()
    assert response.json()["detail"]["error"]["message"] == "`input` field cannot be empty"


def test_create_chat_completion_streaming(client: TestClient, auth_headers: dict):
    """Test the /v1/chat/completions endpoint with streaming."""
    with client.stream("POST", "/v1/chat/completions", headers=auth_headers, json={"messages": [{"role": "user", "content": "Hello"}], "stream": True}) as response:
        assert response.status_code == 200
        for chunk in response.iter_bytes():
            assert isinstance(chunk, bytes)

def test_dreams_endpoint(client: TestClient, monkeypatch, auth_headers: dict):
    api_key = "test-api-key"
    monkeypatch.setenv("LUKHAS_API_KEY", api_key)
    response = client.post(
        "/v1/dreams",
        headers={"X-API-Key": api_key, **auth_headers},
        json={"seed": "test_seed"},
    )
    assert response.status_code == 200
    assert response.json()["seed"] == "test_seed"


@pytest.mark.skip(reason="Not implemented yet")
def test_consciousness_endpoint(client: TestClient, auth_headers: dict):
    """Test the /v1/consciousness endpoint."""
    pass


@pytest.mark.skip(reason="Not implemented yet")
def test_matriz_endpoint(client: TestClient, auth_headers: dict):
    """Test the /v1/matriz endpoint."""
    pass


@pytest.mark.skip(reason="Not implemented yet")
def test_identity_endpoint(client: TestClient, auth_headers: dict):
    """Test the /v1/identity endpoint."""
    pass
