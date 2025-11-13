
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from serve.middleware.strict_auth import StrictAuthMiddleware


@pytest.fixture
def mock_auth_system():
    """Fixture to mock the authentication system."""
    with patch('serve.middleware.strict_auth.get_auth_system') as mock_get_auth_system:
        mock_auth = MagicMock()
        mock_get_auth_system.return_value = mock_auth
        yield mock_auth

@pytest.fixture
def client(mock_auth_system):
    """Fixture to create a TestClient with the middleware and mocked auth system."""
    app = FastAPI()
    app.add_middleware(StrictAuthMiddleware)

    @app.get("/v1/protected")
    async def protected_route():
        return {"message": "You are in!"}

    @app.get("/unprotected")
    async def unprotected_route():
        return {"message": "This is an unprotected route."}

    return TestClient(app)


def test_protected_route_no_auth_header(client):
    """Test that a request to a protected route without an Authorization header is rejected."""
    response = client.get("/v1/protected")
    assert response.status_code == 401
    assert response.json()["error"]["message"] == "Missing Authorization header"

def test_protected_route_invalid_scheme(client):
    """Test that a request with an invalid Authorization scheme is rejected."""
    response = client.get("/v1/protected", headers={"Authorization": "InvalidScheme token"})
    assert response.status_code == 401
    assert response.json()["error"]["message"] == "Authorization header must use Bearer scheme"

def test_protected_route_empty_token(client):
    """Test that a request with an empty Bearer token is rejected."""
    response = client.get("/v1/protected", headers={"Authorization": "Bearer "})
    assert response.status_code == 401
    assert response.json()["error"]["message"] == "Bearer token is empty"

def test_protected_route_invalid_token(client, mock_auth_system):
    """Test that a request with an invalid token is rejected."""
    mock_auth_system.verify_jwt.return_value = None
    response = client.get("/v1/protected", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401
    assert response.json()["error"]["message"] == "Invalid authentication credentials"
    mock_auth_system.verify_jwt.assert_called_once_with("invalidtoken")

def test_protected_route_valid_token(client, mock_auth_system):
    """Test that a request with a valid token is allowed."""
    mock_auth_system.verify_jwt.return_value = {"user_id": "testuser"}
    response = client.get("/v1/protected", headers={"Authorization": "Bearer validtoken"})
    assert response.status_code == 200
    assert response.json() == {"message": "You are in!"}
    mock_auth_system.verify_jwt.assert_called_once_with("validtoken")

def test_unprotected_route(client, mock_auth_system):
    """Test that a request to an unprotected route is not affected by the middleware."""
    response = client.get("/unprotected")
    assert response.status_code == 200
    assert response.json() == {"message": "This is an unprotected route."}
    mock_auth_system.verify_jwt.assert_not_called()
