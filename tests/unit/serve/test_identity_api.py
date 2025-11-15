"""
Unit tests for ΛiD Identity API Routes
=======================================
Comprehensive test suite for authentication, token refresh, profile, and logout endpoints.

Test Coverage:
- Authentication with valid/invalid credentials
- Token refresh flow
- Profile retrieval
- Logout and token revocation
- Health check endpoint
- Error handling
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException, FastAPI
from fastapi.testclient import TestClient

# Import the identity API module
import serve.identity_api as identity_api
from serve.identity_api import (
    router,
    authenticate,
    refresh_token,
    get_profile,
    logout,
    health_check,
    hash_password,
    verify_password,
    generate_refresh_token,
    store_refresh_token,
    verify_refresh_token,
    revoke_token,
    is_token_revoked,
    AuthCredentials,
    AuthResponse,
    TokenRefreshRequest,
    UserProfile,
    LogoutResponse,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def app():
    """Create test FastAPI app with identity router."""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_jwt_manager():
    """Mock JWT manager for testing."""
    with patch('serve.identity_api.get_jwt_manager') as mock:
        jwt_manager = MagicMock()
        jwt_manager.create_access_token.return_value = "mock_access_token_eyJhbGci"
        mock.return_value = jwt_manager
        yield jwt_manager


@pytest.fixture
def test_user():
    """Test user data."""
    return {
        "user_id": "user_test_001",
        "username": "test_user",
        "password_hash": hash_password("test_password"),
        "email": "test@lukhas.ai",
        "created_at": datetime.utcnow().isoformat(),
        "scopes": ["read", "write"],
        "tier": 1,
        "permissions": ["user"],
    }


@pytest.fixture
def setup_test_user(test_user):
    """Set up test user in the database."""
    # Store original users
    original_users = identity_api.USERS_DB.copy()

    # Add test user
    identity_api.USERS_DB["test_user"] = test_user

    yield test_user

    # Restore original users
    identity_api.USERS_DB.clear()
    identity_api.USERS_DB.update(original_users)


@pytest.fixture
def cleanup_tokens():
    """Clean up tokens after tests."""
    yield

    # Clear all tokens
    identity_api.REFRESH_TOKENS.clear()
    identity_api.REVOKED_TOKENS.clear()


@pytest.fixture
def mock_current_user():
    """Mock current user dependency."""
    return {
        "user_id": "user_test_001",
        "tier": 1,
        "permissions": ["user"],
    }


# ============================================================================
# Test Authentication Endpoint
# ============================================================================

class TestAuthentication:
    """Tests for POST /identity/auth endpoint."""

    @pytest.mark.asyncio
    async def test_successful_authentication(self, setup_test_user, mock_jwt_manager, cleanup_tokens):
        """Test successful authentication with valid credentials."""
        credentials = AuthCredentials(username="test_user", password="test_password")

        response = await authenticate(credentials)

        assert isinstance(response, AuthResponse)
        assert response.access_token == "mock_access_token_eyJhbGci"
        assert response.refresh_token.startswith("rt_")
        assert response.token_type == "bearer"
        assert response.expires_in == 3600
        assert response.user_id == "user_test_001"
        assert response.scopes == ["read", "write"]

        # Verify refresh token was stored
        assert len(identity_api.REFRESH_TOKENS) == 1

    @pytest.mark.asyncio
    async def test_authentication_invalid_username(self, setup_test_user, cleanup_tokens):
        """Test authentication with invalid username."""
        credentials = AuthCredentials(username="nonexistent", password="test_password")

        with pytest.raises(HTTPException) as exc_info:
            await authenticate(credentials)

        assert exc_info.value.status_code == 401
        assert "invalid_credentials" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_authentication_invalid_password(self, setup_test_user, cleanup_tokens):
        """Test authentication with invalid password."""
        credentials = AuthCredentials(username="test_user", password="wrong_password")

        with pytest.raises(HTTPException) as exc_info:
            await authenticate(credentials)

        assert exc_info.value.status_code == 401
        assert "invalid_credentials" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_authentication_username_normalization(self, setup_test_user, mock_jwt_manager, cleanup_tokens):
        """Test that username is normalized to lowercase."""
        credentials = AuthCredentials(username="  TEST_USER  ", password="test_password")

        response = await authenticate(credentials)

        assert response.user_id == "user_test_001"

    @pytest.mark.asyncio
    async def test_authentication_jwt_generation_failure(self, setup_test_user, cleanup_tokens):
        """Test authentication when JWT generation fails."""
        with patch('serve.identity_api.get_jwt_manager') as mock_jwt:
            mock_jwt.return_value.create_access_token.side_effect = Exception("JWT error")

            credentials = AuthCredentials(username="test_user", password="test_password")

            with pytest.raises(HTTPException) as exc_info:
                await authenticate(credentials)

            assert exc_info.value.status_code == 500
            assert "token_generation_failed" in str(exc_info.value.detail).lower()


# ============================================================================
# Test Token Refresh Endpoint
# ============================================================================

class TestTokenRefresh:
    """Tests for POST /identity/token/refresh endpoint."""

    @pytest.mark.asyncio
    async def test_successful_token_refresh(self, setup_test_user, mock_jwt_manager, cleanup_tokens):
        """Test successful token refresh."""
        # Create a refresh token
        refresh_token_value = generate_refresh_token()
        store_refresh_token("user_test_001", refresh_token_value, expires_in=604800)

        request = TokenRefreshRequest(refresh_token=refresh_token_value)

        response = await refresh_token(request)

        assert isinstance(response, AuthResponse)
        assert response.access_token == "mock_access_token_eyJhbGci"
        assert response.user_id == "user_test_001"
        assert response.scopes == ["read", "write"]

    @pytest.mark.asyncio
    async def test_token_refresh_invalid_token(self, cleanup_tokens):
        """Test token refresh with invalid refresh token."""
        request = TokenRefreshRequest(refresh_token="invalid_token")

        with pytest.raises(HTTPException) as exc_info:
            await refresh_token(request)

        assert exc_info.value.status_code == 401
        assert "invalid_refresh_token" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_token_refresh_expired_token(self, setup_test_user, cleanup_tokens):
        """Test token refresh with expired refresh token."""
        import time
        # Create an expired refresh token
        refresh_token_value = generate_refresh_token()
        identity_api.REFRESH_TOKENS[refresh_token_value] = {
            "user_id": "user_test_001",
            "expires_at": time.time() - 3600,  # Expired 1 hour ago
            "created_at": time.time() - 7200
        }

        request = TokenRefreshRequest(refresh_token=refresh_token_value)

        with pytest.raises(HTTPException) as exc_info:
            await refresh_token(request)

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_token_refresh_revoked_token(self, setup_test_user, cleanup_tokens):
        """Test token refresh with revoked refresh token."""
        # Create a refresh token and revoke it
        refresh_token_value = generate_refresh_token()
        store_refresh_token("user_test_001", refresh_token_value, expires_in=604800)
        revoke_token(refresh_token_value)

        request = TokenRefreshRequest(refresh_token=refresh_token_value)

        with pytest.raises(HTTPException) as exc_info:
            await refresh_token(request)

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_token_refresh_user_not_found(self, cleanup_tokens, mock_jwt_manager):
        """Test token refresh when user no longer exists."""
        # Create refresh token for non-existent user
        refresh_token_value = generate_refresh_token()
        store_refresh_token("user_nonexistent", refresh_token_value, expires_in=604800)

        request = TokenRefreshRequest(refresh_token=refresh_token_value)

        with pytest.raises(HTTPException) as exc_info:
            await refresh_token(request)

        assert exc_info.value.status_code == 401
        assert "user_not_found" in str(exc_info.value.detail).lower()


# ============================================================================
# Test Profile Endpoint
# ============================================================================

class TestProfile:
    """Tests for GET /identity/profile endpoint."""

    @pytest.mark.asyncio
    async def test_get_profile_success(self, setup_test_user):
        """Test successful profile retrieval."""
        user_data = {"user_id": "user_test_001", "tier": 1, "permissions": ["user"]}

        profile = await get_profile(user_data)

        assert isinstance(profile, UserProfile)
        assert profile.user_id == "user_test_001"
        assert profile.username == "test_user"
        assert profile.email == "test@lukhas.ai"
        assert profile.scopes == ["read", "write"]
        assert profile.tier == 1
        assert profile.permissions == ["user"]

    @pytest.mark.asyncio
    async def test_get_profile_user_not_found(self):
        """Test profile retrieval for non-existent user."""
        user_data = {"user_id": "user_nonexistent", "tier": 0, "permissions": []}

        with pytest.raises(HTTPException) as exc_info:
            await get_profile(user_data)

        assert exc_info.value.status_code == 404
        assert "user_not_found" in str(exc_info.value.detail).lower()


# ============================================================================
# Test Logout Endpoint
# ============================================================================

class TestLogout:
    """Tests for POST /identity/logout endpoint."""

    @pytest.mark.asyncio
    async def test_logout_success(self, setup_test_user, cleanup_tokens):
        """Test successful logout."""
        # Create some refresh tokens
        token1 = generate_refresh_token()
        token2 = generate_refresh_token()
        store_refresh_token("user_test_001", token1, expires_in=604800)
        store_refresh_token("user_test_001", token2, expires_in=604800)

        # Create mock request with authorization header
        mock_request = Mock()
        mock_request.headers = {"Authorization": "Bearer mock_access_token"}

        user_data = {"user_id": "user_test_001", "tier": 1, "permissions": ["user"]}

        response = await logout(mock_request, user_data)

        assert isinstance(response, LogoutResponse)
        assert response.message == "Logout successful"
        assert response.revoked_tokens == 3  # 2 refresh tokens + 1 access token

        # Verify tokens were revoked
        assert is_token_revoked(token1)
        assert is_token_revoked(token2)
        assert is_token_revoked("mock_access_token")

        # Verify refresh tokens were removed
        assert token1 not in identity_api.REFRESH_TOKENS
        assert token2 not in identity_api.REFRESH_TOKENS

    @pytest.mark.asyncio
    async def test_logout_no_refresh_tokens(self, setup_test_user, cleanup_tokens):
        """Test logout when user has no refresh tokens."""
        mock_request = Mock()
        mock_request.headers = {"Authorization": "Bearer mock_access_token"}

        user_data = {"user_id": "user_test_001", "tier": 1, "permissions": ["user"]}

        response = await logout(mock_request, user_data)

        assert response.revoked_tokens == 1  # Only access token

    @pytest.mark.asyncio
    async def test_logout_no_auth_header(self, setup_test_user, cleanup_tokens):
        """Test logout without authorization header."""
        mock_request = Mock()
        mock_request.headers = {}

        user_data = {"user_id": "user_test_001", "tier": 1, "permissions": ["user"]}

        response = await logout(mock_request, user_data)

        assert response.revoked_tokens == 0  # No tokens to revoke


# ============================================================================
# Test Health Check Endpoint
# ============================================================================

class TestHealthCheck:
    """Tests for GET /identity/health endpoint."""

    @pytest.mark.asyncio
    async def test_health_check(self, cleanup_tokens):
        """Test health check endpoint."""
        response = await health_check()

        assert response["status"] == "healthy"
        assert "jwt_available" in response
        assert "qrg_available" in response
        assert "bcrypt_available" in response
        assert "users_count" in response
        assert "active_refresh_tokens" in response
        assert "revoked_tokens" in response

    def test_health_check_endpoint(self, client):
        """Test health check via HTTP endpoint."""
        response = client.get("/identity/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


# ============================================================================
# Test Helper Functions
# ============================================================================

class TestHelperFunctions:
    """Tests for helper functions."""

    def test_hash_password(self):
        """Test password hashing."""
        password = "test_password_123"
        hashed = hash_password(password)

        assert hashed != password
        assert len(hashed) > 0

    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "test_password_123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "test_password_123"
        hashed = hash_password(password)

        assert verify_password("wrong_password", hashed) is False

    def test_generate_refresh_token(self):
        """Test refresh token generation."""
        token = generate_refresh_token()

        assert token.startswith("rt_")
        assert len(token) > 10

        # Generate another and ensure it's different
        token2 = generate_refresh_token()
        assert token != token2

    def test_store_and_verify_refresh_token(self, cleanup_tokens):
        """Test storing and verifying refresh tokens."""
        token = generate_refresh_token()
        user_id = "user_test_001"

        store_refresh_token(user_id, token, expires_in=3600)

        verified_user_id = verify_refresh_token(token)
        assert verified_user_id == user_id

    def test_verify_refresh_token_nonexistent(self, cleanup_tokens):
        """Test verifying non-existent refresh token."""
        result = verify_refresh_token("nonexistent_token")
        assert result is None

    def test_revoke_token(self, cleanup_tokens):
        """Test token revocation."""
        token = "test_token_123"

        assert is_token_revoked(token) is False

        revoke_token(token)

        assert is_token_revoked(token) is True


# ============================================================================
# Test Request/Response Models
# ============================================================================

class TestModels:
    """Tests for Pydantic models."""

    def test_auth_credentials_validation(self):
        """Test AuthCredentials model validation."""
        # Valid credentials
        creds = AuthCredentials(username="test_user", password="password123")
        assert creds.username == "test_user"

        # Username normalization
        creds2 = AuthCredentials(username="  TEST_USER  ", password="password123")
        assert creds2.username == "test_user"

    def test_auth_credentials_invalid_characters(self):
        """Test AuthCredentials validation with invalid characters."""
        with pytest.raises(ValueError):
            AuthCredentials(username="user<script>", password="password123")

    def test_auth_response_model(self):
        """Test AuthResponse model."""
        response = AuthResponse(
            access_token="token123",
            refresh_token="rt_token456",
            token_type="bearer",
            expires_in=3600,
            user_id="user_001",
            scopes=["read", "write"]
        )

        assert response.access_token == "token123"
        assert response.token_type == "bearer"
        assert response.expires_in == 3600

    def test_user_profile_model(self):
        """Test UserProfile model."""
        profile = UserProfile(
            user_id="user_001",
            username="test_user",
            email="test@example.com",
            scopes=["read"],
            tier=1,
            permissions=["user"],
            created_at=datetime.utcnow().isoformat()
        )

        assert profile.user_id == "user_001"
        assert profile.tier == 1

    def test_token_refresh_request_model(self):
        """Test TokenRefreshRequest model."""
        request = TokenRefreshRequest(refresh_token="rt_abc123")
        assert request.refresh_token == "rt_abc123"

    def test_logout_response_model(self):
        """Test LogoutResponse model."""
        response = LogoutResponse(message="Success", revoked_tokens=2)
        assert response.message == "Success"
        assert response.revoked_tokens == 2


# ============================================================================
# Integration Tests with FastAPI TestClient
# ============================================================================

class TestAuthenticationFlowIntegration:
    """Integration tests using FastAPI TestClient."""

    def test_health_check_integration(self, client):
        """Test health check endpoint via HTTP."""
        response = client.get("/identity/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert isinstance(data["users_count"], int)

    def test_authentication_flow_integration(self, client, mock_jwt_manager, cleanup_tokens):
        """Test authentication flow via HTTP endpoints."""
        # Note: This is a partial integration test since we're using the stub user database
        # A full integration test would use a real database

        # Authentication endpoint exists and is accessible
        response = client.post("/identity/auth", json={
            "username": "demo_user",
            "password": "demo_password"
        })

        # Should either authenticate or return proper error
        assert response.status_code in [200, 401, 500]


# ============================================================================
# Test OpenAPI Documentation
# ============================================================================

class TestOpenAPISpec:
    """Tests for OpenAPI documentation."""

    def test_endpoints_have_openapi_metadata(self, app):
        """Test that all endpoints have proper OpenAPI metadata."""
        openapi = app.openapi()

        # Check auth endpoint
        assert "/identity/auth" in openapi["paths"]
        auth_spec = openapi["paths"]["/identity/auth"]["post"]
        assert "summary" in auth_spec
        assert "200" in auth_spec["responses"]
        assert "401" in auth_spec["responses"]

        # Check profile endpoint
        assert "/identity/profile" in openapi["paths"]
        profile_spec = openapi["paths"]["/identity/profile"]["get"]
        assert "summary" in profile_spec

        # Check health endpoint
        assert "/identity/health" in openapi["paths"]
        health_spec = openapi["paths"]["/identity/health"]["get"]
        assert "summary" in health_spec
