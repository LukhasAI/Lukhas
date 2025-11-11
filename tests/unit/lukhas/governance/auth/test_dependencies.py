"""Tests for authentication dependencies.

These tests verify that user identity extraction from JWT tokens works correctly
and that security controls prevent identity spoofing.
"""

import sys
from unittest.mock import MagicMock, Mock

import pytest

# Mock dependencies before importing
mock_auth_module = MagicMock()
mock_auth_module.get_auth_system = Mock()
sys.modules['core.security.auth'] = mock_auth_module
sys.modules['labs.core.security.auth'] = mock_auth_module
sys.modules['streamlit'] = MagicMock()

from fastapi import FastAPI, Depends, HTTPException
from fastapi.testclient import TestClient
from lukhas.governance.auth.dependencies import (
    get_current_user,
    get_current_user_id,
    get_current_user_tier,
    require_admin
)


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

    @app.get("/api/tier")
    async def tier_endpoint(tier: int = Depends(get_current_user_tier)):
        return {"tier": tier}

    @app.get("/api/admin")
    async def admin_endpoint(admin_user = Depends(require_admin)):
        return {"message": "admin access granted", "user_id": admin_user["user_id"]}

    return app


@pytest.fixture
def client(app):
    return TestClient(app)


class TestGetCurrentUser:
    """Test suite for get_current_user dependency."""

    def test_requires_request_state_user(self, client):
        """Should fail if request.state.user not set (middleware not installed)."""
        # StrictAuthMiddleware not installed - no request.state.user
        response = client.get("/api/protected")
        assert response.status_code == 401
        result = response.json()
        # FastAPI wraps HTTPException detail in "detail" field
        assert "detail" in result
        error = result["detail"]
        assert "error" in error
        assert "User context not found" in error["error"]["message"]

    def test_extracts_user_id_from_state(self, app, client):
        """Should extract user_id from request.state.user."""
        # Mock middleware that sets request.state.user
        from starlette.middleware.base import BaseHTTPMiddleware

        class MockAuthMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request, call_next):
                request.state.user = {
                    "user_id": "user123",
                    "email": "test@example.com",
                    "tier": 1,
                    "permissions": ["read", "write"]
                }
                return await call_next(request)

        app.add_middleware(MockAuthMiddleware)
        client = TestClient(app)

        response = client.get("/api/protected")
        assert response.status_code == 200
        assert response.json()["user_id"] == "user123"

    def test_fails_if_user_id_missing(self, app, client):
        """Should fail if user data missing user_id."""
        from starlette.middleware.base import BaseHTTPMiddleware

        class MockAuthMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request, call_next):
                # Set user data without user_id!
                request.state.user = {"email": "test@example.com"}
                return await call_next(request)

        app.add_middleware(MockAuthMiddleware)
        client = TestClient(app)

        response = client.get("/api/protected")
        assert response.status_code == 500
        result = response.json()
        assert "detail" in result
        error = result["detail"]
        assert "error" in error
        assert "authentication error" in error["error"]["message"].lower()

    def test_fails_if_user_data_invalid_type(self, app, client):
        """Should fail if user data is not a dict."""
        from starlette.middleware.base import BaseHTTPMiddleware

        class MockAuthMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request, call_next):
                # Set user as string instead of dict!
                request.state.user = "invalid_user_string"
                return await call_next(request)

        app.add_middleware(MockAuthMiddleware)
        client = TestClient(app)

        response = client.get("/api/protected")
        assert response.status_code == 500

    def test_get_full_user_data(self, app, client):
        """Should return full user data dict."""
        from starlette.middleware.base import BaseHTTPMiddleware

        class MockAuthMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request, call_next):
                request.state.user = {
                    "user_id": "user123",
                    "email": "test@example.com",
                    "tier": 2,
                    "permissions": ["read", "write", "admin"]
                }
                return await call_next(request)

        app.add_middleware(MockAuthMiddleware)
        client = TestClient(app)

        response = client.get("/api/profile")
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "user123"
        assert data["email"] == "test@example.com"
        assert data["tier"] == 2
        assert "admin" in data["permissions"]


class TestGetCurrentUserTier:
    """Test suite for get_current_user_tier dependency."""

    def test_extracts_tier_from_user_data(self, app, client):
        """Should extract tier from user data."""
        from starlette.middleware.base import BaseHTTPMiddleware

        class MockAuthMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request, call_next):
                request.state.user = {
                    "user_id": "user123",
                    "tier": 3,
                    "permissions": []
                }
                return await call_next(request)

        app.add_middleware(MockAuthMiddleware)
        client = TestClient(app)

        response = client.get("/api/tier")
        assert response.status_code == 200
        assert response.json()["tier"] == 3

    def test_defaults_to_zero_if_tier_missing(self, app, client):
        """Should default to tier 0 if not in user data."""
        from starlette.middleware.base import BaseHTTPMiddleware

        class MockAuthMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request, call_next):
                request.state.user = {
                    "user_id": "user123",
                    "permissions": []
                    # No tier field
                }
                return await call_next(request)

        app.add_middleware(MockAuthMiddleware)
        client = TestClient(app)

        response = client.get("/api/tier")
        assert response.status_code == 200
        assert response.json()["tier"] == 0


class TestRequireAdmin:
    """Test suite for require_admin dependency."""

    def test_grants_access_to_admin_users(self, app, client):
        """Should grant access if user has admin permission."""
        from starlette.middleware.base import BaseHTTPMiddleware

        class MockAuthMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request, call_next):
                request.state.user = {
                    "user_id": "admin123",
                    "tier": 2,
                    "permissions": ["admin", "read", "write"]
                }
                return await call_next(request)

        app.add_middleware(MockAuthMiddleware)
        client = TestClient(app)

        response = client.get("/api/admin")
        assert response.status_code == 200
        assert response.json()["user_id"] == "admin123"

    def test_denies_access_to_non_admin_users(self, app, client):
        """Should deny access if user doesn't have admin permission."""
        from starlette.middleware.base import BaseHTTPMiddleware

        class MockAuthMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request, call_next):
                request.state.user = {
                    "user_id": "user123",
                    "tier": 1,
                    "permissions": ["read", "write"]  # No admin
                }
                return await call_next(request)

        app.add_middleware(MockAuthMiddleware)
        client = TestClient(app)

        response = client.get("/api/admin")
        assert response.status_code == 403
        result = response.json()
        assert "detail" in result
        error = result["detail"]
        assert "error" in error
        assert "Admin privileges required" in error["error"]["message"]

    def test_denies_access_if_no_permissions(self, app, client):
        """Should deny access if permissions list is empty."""
        from starlette.middleware.base import BaseHTTPMiddleware

        class MockAuthMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request, call_next):
                request.state.user = {
                    "user_id": "user123",
                    "tier": 0,
                    "permissions": []  # Empty permissions
                }
                return await call_next(request)

        app.add_middleware(MockAuthMiddleware)
        client = TestClient(app)

        response = client.get("/api/admin")
        assert response.status_code == 403


class TestErrorResponseFormat:
    """Test that error responses follow expected format."""

    def test_401_error_format(self, client):
        """401 errors should have standardized error format."""
        response = client.get("/api/protected")
        assert response.status_code == 401
        result = response.json()
        assert "detail" in result
        error = result["detail"]
        assert "error" in error
        assert "message" in error["error"]
        assert "type" in error["error"]
        assert "code" in error["error"]

    def test_500_error_format(self, app, client):
        """500 errors should have standardized error format."""
        from starlette.middleware.base import BaseHTTPMiddleware

        class MockAuthMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request, call_next):
                request.state.user = {"email": "test@example.com"}  # Missing user_id
                return await call_next(request)

        app.add_middleware(MockAuthMiddleware)
        client = TestClient(app)

        response = client.get("/api/protected")
        assert response.status_code == 500
        result = response.json()
        assert "detail" in result
        error = result["detail"]
        assert "error" in error
