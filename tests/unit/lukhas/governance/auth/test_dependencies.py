"""Tests for authentication dependencies.

This test suite ensures the get_current_user and get_current_user_id
dependencies correctly extract user context from request.state populated
by StrictAuthMiddleware.
"""

import pytest
from fastapi import Depends, FastAPI, HTTPException
from fastapi.testclient import TestClient

from lukhas.governance.auth.dependencies import get_current_user, get_current_user_id


@pytest.fixture
def app():
    """Create test FastAPI app."""
    app = FastAPI()

    @app.get("/api/protected")
    async def protected_endpoint(user_id: str = Depends(get_current_user_id)):
        return {"message": "success", "user_id": user_id}

    @app.get("/api/profile")
    async def profile_endpoint(user_data = Depends(get_current_user)):
        return user_data

    return app


@pytest.fixture
def client(app):
    return TestClient(app)


class TestGetCurrentUser:
    """Test suite for get_current_user dependency."""

    def test_requires_request_state_user_id(self, client):
        """Should fail if request.state.user_id not set."""
        # StrictAuthMiddleware not installed - no request.state.user_id
        response = client.get("/api/protected")
        assert response.status_code == 401
        assert "User context not found" in response.json()["detail"]

    def test_extracts_user_id_from_state(self, app, client):
        """Should extract user_id from request.state."""
        # Mock middleware that sets request.state.user_id
        from starlette.middleware.base import BaseHTTPMiddleware

        class MockAuthMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request, call_next):
                request.state.user_id = "user123"
                request.state.user_tier = 1
                request.state.user_permissions = ["read", "write"]
                request.state.user = {
                    "user_id": "user123",
                    "tier": 1,
                    "permissions": ["read", "write"]
                }
                return await call_next(request)

        app.add_middleware(MockAuthMiddleware)
        client = TestClient(app)

        response = client.get("/api/protected")
        assert response.status_code == 200
        assert response.json()["user_id"] == "user123"

    def test_get_current_user_returns_full_context(self, app, client):
        """Should return full user context dict."""
        from starlette.middleware.base import BaseHTTPMiddleware

        class MockAuthMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request, call_next):
                request.state.user_id = "user123"
                request.state.user_tier = 2
                request.state.user_permissions = ["read", "write", "admin"]
                request.state.user = {
                    "user_id": "user123",
                    "tier": 2,
                    "permissions": ["read", "write", "admin"],
                    "email": "test@example.com"
                }
                return await call_next(request)

        app.add_middleware(MockAuthMiddleware)
        client = TestClient(app)

        response = client.get("/api/profile")
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["user_id"] == "user123"
        assert user_data["tier"] == 2
        assert user_data["permissions"] == ["read", "write", "admin"]
        assert user_data["email"] == "test@example.com"

    def test_fails_if_user_id_empty(self, app, client):
        """Should fail if user_id is empty string."""
        from starlette.middleware.base import BaseHTTPMiddleware

        class MockAuthMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request, call_next):
                request.state.user_id = ""  # Empty user_id!
                return await call_next(request)

        app.add_middleware(MockAuthMiddleware)
        client = TestClient(app)

        response = client.get("/api/protected")
        assert response.status_code == 500
        assert "authentication error" in response.json()["detail"].lower()


class TestGetCurrentUserId:
    """Test suite for get_current_user_id convenience dependency."""

    def test_extracts_only_user_id(self, app, client):
        """Should extract just the user_id string."""
        from starlette.middleware.base import BaseHTTPMiddleware

        class MockAuthMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request, call_next):
                request.state.user_id = "testuser456"
                request.state.user_tier = 0
                request.state.user_permissions = []
                return await call_next(request)

        app.add_middleware(MockAuthMiddleware)
        client = TestClient(app)

        response = client.get("/api/protected")
        assert response.status_code == 200
        assert response.json()["user_id"] == "testuser456"

    def test_fails_if_not_string(self, app, client):
        """Should fail if user_id is not a string."""
        from starlette.middleware.base import BaseHTTPMiddleware

        class MockAuthMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request, call_next):
                request.state.user_id = 123  # Not a string!
                return await call_next(request)

        app.add_middleware(MockAuthMiddleware)
        client = TestClient(app)

        response = client.get("/api/protected")
        assert response.status_code == 500
        assert "authentication error" in response.json()["detail"].lower()
