"""
Tests for StrictAuthMiddleware.

Tests:
- Authorization header validation
- Bearer token format validation
- JWT verification via auth system
- 401 error responses on auth failure
- OpenAI-compatible error format
- /v1/* path enforcement
"""
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock

# Mock the auth system before importing the middleware
mock_auth_module = MagicMock()
mock_auth_module.get_auth_system = Mock()
sys.modules['labs.core.security.auth'] = mock_auth_module

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from fastapi.responses import JSONResponse

from serve.middleware.strict_auth import StrictAuthMiddleware


@pytest.fixture
def mock_auth_system():
    """Create mock authentication system."""
    mock_auth = Mock()
    mock_auth.verify_jwt = Mock()
    return mock_auth


@pytest.fixture
def app(mock_auth_system):
    """Create test FastAPI app with StrictAuthMiddleware."""
    # Patch get_auth_system globally for the module
    mock_auth_module.get_auth_system.return_value = mock_auth_system

    app = FastAPI()

    # Add a test endpoint
    @app.get("/v1/test")
    async def test_endpoint():
        return {"message": "success"}

    @app.get("/v2/test")
    async def test_v2_endpoint():
        return {"message": "v2 success"}

    @app.get("/health")
    async def health_endpoint():
        return {"status": "healthy"}

    # Add middleware - it will use the mocked get_auth_system
    app.add_middleware(StrictAuthMiddleware)

    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


class TestAuthorizationHeaderValidation:
    """Tests for Authorization header validation."""

    def test_missing_authorization_header(self, client, mock_auth_system):
        """Test that missing Authorization header returns 401."""
        response = client.get("/v1/test")

        assert response.status_code == 401
        data = response.json()
        assert "error" in data
        assert data["error"]["type"] == "invalid_api_key"
        assert "Missing Authorization header" in data["error"]["message"]
        assert data["error"]["code"] == "invalid_api_key"

    def test_empty_authorization_header(self, client, mock_auth_system):
        """Test that empty Authorization header returns 401."""
        response = client.get("/v1/test", headers={"Authorization": ""})

        assert response.status_code == 401
        data = response.json()
        assert data["error"]["message"] == "Missing Authorization header"

    def test_non_bearer_authorization_scheme(self, client, mock_auth_system):
        """Test that non-Bearer schemes are rejected."""
        response = client.get("/v1/test", headers={"Authorization": "Basic abc123"})

        assert response.status_code == 401
        data = response.json()
        assert "Bearer scheme" in data["error"]["message"]

    def test_bearer_without_token(self, client, mock_auth_system):
        """Test that 'Bearer' without space returns 401."""
        response = client.get("/v1/test", headers={"Authorization": "Bearer"})

        assert response.status_code == 401
        data = response.json()
        # "Bearer" without space fails the Bearer scheme check
        assert "Bearer scheme" in data["error"]["message"]

    def test_bearer_with_only_spaces(self, client, mock_auth_system):
        """Test that 'Bearer' with only spaces returns 401."""
        response = client.get("/v1/test", headers={"Authorization": "Bearer    "})

        assert response.status_code == 401
        data = response.json()
        assert "empty" in data["error"]["message"]


class TestJWTVerification:
    """Tests for JWT token verification."""

    def test_valid_jwt_passes(self, client, mock_auth_system):
        """Test that valid JWT allows request to proceed."""
        mock_auth_system.verify_jwt.return_value = {"user_id": "test_user"}

        response = client.get(
            "/v1/test",
            headers={"Authorization": "Bearer valid_token_abc123"}
        )

        assert response.status_code == 200
        assert response.json()["message"] == "success"
        mock_auth_system.verify_jwt.assert_called_once_with("valid_token_abc123")

    def test_invalid_jwt_rejected(self, client, mock_auth_system):
        """Test that invalid JWT returns 401."""
        mock_auth_system.verify_jwt.return_value = None

        response = client.get(
            "/v1/test",
            headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401
        data = response.json()
        assert "Invalid authentication credentials" in data["error"]["message"]

    def test_expired_jwt_rejected(self, client, mock_auth_system):
        """Test that expired JWT returns 401."""
        mock_auth_system.verify_jwt.return_value = None  # Expired returns None

        response = client.get(
            "/v1/test",
            headers={"Authorization": "Bearer expired_token"}
        )

        assert response.status_code == 401

    def test_jwt_verification_called_with_correct_token(self, client, mock_auth_system):
        """Test that verify_jwt is called with the extracted token."""
        mock_auth_system.verify_jwt.return_value = {"user_id": "test"}

        token = "my_test_token_12345"
        client.get("/v1/test", headers={"Authorization": f"Bearer {token}"})

        mock_auth_system.verify_jwt.assert_called_once_with(token)


class TestPathEnforcement:
    """Tests for /v1/* path enforcement."""

    def test_v1_path_requires_auth(self, client, mock_auth_system):
        """Test that /v1/* paths require authentication."""
        response = client.get("/v1/test")

        assert response.status_code == 401

    def test_non_v1_path_bypasses_auth(self, client, mock_auth_system):
        """Test that non-/v1/* paths bypass authentication."""
        response = client.get("/v2/test")

        assert response.status_code == 200
        assert response.json()["message"] == "v2 success"
        mock_auth_system.verify_jwt.assert_not_called()

    def test_health_endpoint_bypasses_auth(self, client, mock_auth_system):
        """Test that /health endpoint bypasses authentication."""
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        mock_auth_system.verify_jwt.assert_not_called()

    def test_v1_subpaths_require_auth(self, client, mock_auth_system):
        """Test that /v1/sub/path requires auth."""
        app = FastAPI()

        @app.get("/v1/api/users/profile")
        async def profile():
            return {"user": "profile"}

        with patch("serve.middleware.strict_auth.get_auth_system", return_value=mock_auth_system):
            app.add_middleware(StrictAuthMiddleware)

        client = TestClient(app)
        response = client.get("/v1/api/users/profile")

        assert response.status_code == 401


class TestErrorFormat:
    """Tests for OpenAI-compatible error format."""

    def test_error_response_structure(self, client, mock_auth_system):
        """Test that error response has correct structure."""
        response = client.get("/v1/test")

        data = response.json()
        assert "error" in data
        error = data["error"]
        assert "type" in error
        assert "message" in error
        assert "code" in error

    def test_error_type_is_invalid_api_key(self, client, mock_auth_system):
        """Test that error type is 'invalid_api_key'."""
        response = client.get("/v1/test")

        error = response.json()["error"]
        assert error["type"] == "invalid_api_key"

    def test_error_code_is_invalid_api_key(self, client, mock_auth_system):
        """Test that error code is 'invalid_api_key'."""
        response = client.get("/v1/test")

        error = response.json()["error"]
        assert error["code"] == "invalid_api_key"

    def test_error_message_is_descriptive(self, client, mock_auth_system):
        """Test that error messages are descriptive."""
        # Missing header
        response = client.get("/v1/test")
        assert len(response.json()["error"]["message"]) > 0

        # Invalid token
        mock_auth_system.verify_jwt.return_value = None
        response = client.get("/v1/test", headers={"Authorization": "Bearer bad"})
        assert len(response.json()["error"]["message"]) > 0

    def test_error_response_is_json(self, client, mock_auth_system):
        """Test that error response is JSON."""
        response = client.get("/v1/test")

        assert response.headers["content-type"] == "application/json"


class TestMiddlewareInitialization:
    """Tests for middleware initialization."""

    def test_middleware_initializes_auth_system(self):
        """Test that middleware initializes auth system on creation."""
        app = FastAPI()

        with patch("serve.middleware.strict_auth.get_auth_system") as mock_get_auth:
            mock_auth = Mock()
            mock_get_auth.return_value = mock_auth

            middleware = StrictAuthMiddleware(app)

            mock_get_auth.assert_called_once()
            assert middleware.auth_system == mock_auth


class TestDifferentHTTPMethods:
    """Tests for different HTTP methods."""

    def test_post_request_requires_auth(self, client, mock_auth_system):
        """Test that POST requests require auth."""
        app = FastAPI()

        @app.post("/v1/data")
        async def create_data():
            return {"created": True}

        with patch("serve.middleware.strict_auth.get_auth_system", return_value=mock_auth_system):
            app.add_middleware(StrictAuthMiddleware)

        client = TestClient(app)
        response = client.post("/v1/data")

        assert response.status_code == 401

    def test_put_request_requires_auth(self, client, mock_auth_system):
        """Test that PUT requests require auth."""
        app = FastAPI()

        @app.put("/v1/data")
        async def update_data():
            return {"updated": True}

        with patch("serve.middleware.strict_auth.get_auth_system", return_value=mock_auth_system):
            app.add_middleware(StrictAuthMiddleware)

        client = TestClient(app)
        response = client.put("/v1/data")

        assert response.status_code == 401

    def test_delete_request_requires_auth(self, client, mock_auth_system):
        """Test that DELETE requests require auth."""
        app = FastAPI()

        @app.delete("/v1/data")
        async def delete_data():
            return {"deleted": True}

        with patch("serve.middleware.strict_auth.get_auth_system", return_value=mock_auth_system):
            app.add_middleware(StrictAuthMiddleware)

        client = TestClient(app)
        response = client.delete("/v1/data")

        assert response.status_code == 401


class TestTokenExtraction:
    """Tests for token extraction from Authorization header."""

    def test_token_extracted_correctly(self, client, mock_auth_system):
        """Test that token is extracted correctly from header."""
        mock_auth_system.verify_jwt.return_value = {"user_id": "test"}

        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        client.get("/v1/test", headers={"Authorization": f"Bearer {token}"})

        mock_auth_system.verify_jwt.assert_called_once_with(token)

    def test_token_with_extra_spaces(self, client, mock_auth_system):
        """Test token extraction with extra spaces."""
        mock_auth_system.verify_jwt.return_value = {"user_id": "test"}

        token = "token_with_spaces"
        client.get("/v1/test", headers={"Authorization": f"Bearer   {token}   "})

        # Token should be stripped
        mock_auth_system.verify_jwt.assert_called_once_with(token)


class TestConcurrentRequests:
    """Tests for concurrent request handling."""

    def test_concurrent_authenticated_requests(self, client, mock_auth_system):
        """Test that concurrent authenticated requests succeed."""
        import concurrent.futures

        mock_auth_system.verify_jwt.return_value = {"user_id": "test"}

        def make_request():
            return client.get("/v1/test", headers={"Authorization": "Bearer token"})

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        assert len(results) == 10
        for response in results:
            assert response.status_code == 200

    def test_concurrent_mixed_requests(self, client, mock_auth_system):
        """Test concurrent mix of valid and invalid requests."""
        import concurrent.futures

        # Set mock to return valid for valid requests
        mock_auth_system.verify_jwt.side_effect = lambda token: {"user_id": "test"} if token == "valid_token" else None

        def make_request(valid):
            if valid:
                return client.get("/v1/test", headers={"Authorization": "Bearer valid_token"})
            else:
                return client.get("/v1/test")

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, i % 2 == 0) for i in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        assert len(results) == 10
        success_count = sum(1 for r in results if r.status_code == 200)
        failure_count = sum(1 for r in results if r.status_code == 401)
        assert success_count == 5
        assert failure_count == 5
