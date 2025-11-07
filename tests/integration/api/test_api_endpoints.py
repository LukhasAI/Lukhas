from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from labs.core.security.auth import get_auth_system
from serve.main import app as main_app
from serve.reference_api.public_api_reference import app as dreams_app, verify_api_key


@pytest.fixture
def client():
    """Provides a test client for the main API."""
    return TestClient(main_app)

@pytest.fixture
def dreams_client():
    """Provides a test client for the dreams API."""
    return TestClient(dreams_app)

@pytest.fixture
def auth_headers():
    """Provides authorization headers for testing."""
    auth_system = get_auth_system()
    token = auth_system.generate_jwt("test_user")
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def mock_dreams_auth():
    """Mocks the authentication for the dreams endpoint."""
    with patch("serve.reference_api.public_api_reference.verify_api_key") as mock_verify_api_key:
        mock_verify_api_key.return_value = {"user_id": "test_user"}
        dreams_app.dependency_overrides[verify_api_key] = lambda: {"user_id": "test_user"}
        yield
        dreams_app.dependency_overrides = {}

def test_healthz(client):
    """Test the /healthz endpoint."""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_readyz(client):
    """Test the /readyz endpoint."""
    response = client.get("/readyz")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"

def test_metrics(client):
    """Test the /metrics endpoint."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "process_cpu_seconds_total" in response.text
    assert "http_requests_total" in response.text

def test_list_models_unauthenticated(client):
    """Test that /v1/models requires authentication."""
    response = client.get("/v1/models")
    assert response.status_code == 401

def test_list_models_authenticated(client, auth_headers):
    """Test the /v1/models endpoint with authentication."""
    response = client.get("/v1/models", headers=auth_headers)
    assert response.status_code == 200
    assert "data" in response.json()
    assert len(response.json()["data"]) > 0

def test_create_chat_completion_unauthenticated(client):
    """Test that /v1/chat/completions requires authentication."""
    response = client.post("/v1/chat/completions", json={"messages": [{"role": "user", "content": "Hello"}]})
    assert response.status_code == 401

def test_create_chat_completion_authenticated(client, auth_headers):
    """Test the /v1/chat/completions endpoint with authentication."""
    response = client.post("/v1/chat/completions", headers=auth_headers, json={"messages": [{"role": "user", "content": "Hello"}]})
    assert response.status_code == 200
    assert "choices" in response.json()
    assert len(response.json()["choices"]) > 0

def test_create_chat_completion_no_messages(client, auth_headers):
    """Test that /v1/chat/completions returns an error when no messages are provided."""
    response = client.post("/v1/chat/completions", headers=auth_headers, json={})
    assert response.status_code == 200

def test_create_embeddings_unauthenticated(client):
    """Test that /v1/embeddings requires authentication."""
    response = client.post("/v1/embeddings", json={"input": "test"})
    assert response.status_code == 401

def test_create_embeddings_authenticated(client, auth_headers):
    """Test the /v1/embeddings endpoint with authentication."""
    response = client.post("/v1/embeddings", headers=auth_headers, json={"input": "test"})
    assert response.status_code == 200
    assert "data" in response.json()
    assert len(response.json()["data"]) > 0

def test_create_embeddings_no_input(client, auth_headers):
    """Test that /v1/embeddings returns an error when no input is provided."""
    response = client.post("/v1/embeddings", headers=auth_headers, json={})
    assert response.status_code == 400
    assert "detail" in response.json()
    assert response.json()["detail"]["error"]["message"] == "Missing `input` field"

def test_create_embeddings_empty_input(client, auth_headers):
    """Test that /v1/embeddings returns an error when the input is empty."""
    response = client.post("/v1/embeddings", headers=auth_headers, json={"input": ""})
    assert response.status_code == 400
    assert "detail" in response.json()
    assert response.json()["detail"]["error"]["message"] == "`input` field cannot be empty"

def test_generate_dream_unauthenticated(dreams_client):
    """Test that /v1/dreams requires authentication."""
    response = dreams_client.post("/v1/dreams", json={"prompt": "test"})
    assert response.status_code == 401

def test_generate_dream_authenticated(dreams_client, mock_dreams_auth):
    """Test the /v1/dreams endpoint with authentication."""
    response = dreams_client.post("/v1/dreams", json={"prompt": "test"})
    assert response.status_code == 200
    assert "dream" in response.json()

def test_create_chat_completion_streaming(client, auth_headers):
    """Test the /v1/chat/completions endpoint with streaming."""
    with client.stream("POST", "/v1/chat/completions", headers=auth_headers, json={"messages": [{"role": "user", "content": "Hello"}], "stream": True}) as response:
        assert response.status_code == 200
        for chunk in response.iter_bytes():
            assert isinstance(chunk, bytes)
