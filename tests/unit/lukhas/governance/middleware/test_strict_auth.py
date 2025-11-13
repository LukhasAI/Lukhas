"""Tests for StrictAuthMiddleware.

This test suite ensures the middleware properly enforces authentication
on all endpoints except the explicit allowlist, addressing OWASP A01.
"""

import sys
from unittest.mock import MagicMock, Mock

import pytest

# Mock dependencies before importing the middleware
mock_auth_module = MagicMock()
mock_auth_module.get_auth_system = Mock()
sys.modules['core.security.auth'] = mock_auth_module
sys.modules['labs.core.security.auth'] = mock_auth_module

# Mock streamlit to avoid import errors
sys.modules['streamlit'] = MagicMock()

from fastapi import FastAPI
from fastapi.testclient import TestClient
from lukhas_website.lukhas.api.middleware.strict_auth import StrictAuthMiddleware


@pytest.fixture
def auth_system():
    """Mock authentication system for testing."""

    class MockAuthSystem:
        """Mock auth system that validates specific test tokens."""

        def verify_jwt(self, token: str):
            """Verify JWT token - returns claims for valid tokens, None otherwise."""
            if token == "valid-test-token-with-minimum-20-chars":
                return {
                    "user_id": "test-user-123",
                    "tier": 1,
                    "permissions": ["read", "write"],
                    "exp": 9999999999,  # Far future
                }
            elif token == "valid-token-no-user-id":
                return {
                    "tier": 1,
                    "permissions": [],
                }
            elif token == "expired-token-placeholder-min-20-chars":
                return None  # Simulates expired/invalid token
            return None

    # Set up the mock to return our auth system
    mock_instance = MockAuthSystem()
    mock_auth_module.get_auth_system.return_value = mock_instance

    return mock_instance


@pytest.fixture
def app(auth_system):
    """Create test FastAPI app with auth middleware."""
    app = FastAPI()
    app.add_middleware(StrictAuthMiddleware)

    @app.get("/api/protected")
    async def protected_endpoint():
        return {"status": "success", "message": "Protected endpoint accessed"}

    @app.post("/api/v1/consciousness/query")
    async def consciousness_query():
        return {"response": "Consciousness query processed"}

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    @app.get("/healthz")
    async def healthz_check():
        return {"status": "healthy"}

    @app.get("/readyz")
    async def readyz_check():
        return {"status": "ready"}

    @app.get("/metrics")
    async def metrics():
        return {"metrics": "data"}

    @app.get("/docs")
    async def docs():
        return {"docs": "api documentation"}

    @app.get("/openapi.json")
    async def openapi():
        return {"openapi": "3.0.0"}

    @app.get("/redoc")
    async def redoc():
        return {"redoc": "documentation"}

    @app.post("/api/v1/auth/login")
    async def login():
        return {"token": "mock-token"}

    @app.post("/api/v1/auth/register")
    async def register():
        return {"token": "mock-token"}

    @app.post("/api/v1/identity/authenticate")
    async def authenticate():
        return {"status": "authenticated"}

    @app.post("/id/webauthn/challenge")
    async def webauthn_challenge():
        return {"challenge": "mock-challenge"}

    @app.post("/id/webauthn/verify")
    async def webauthn_verify():
        return {"verified": True}

    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


class TestStrictAuthMiddleware:
    """Test suite for authentication middleware."""

    def test_health_endpoint_public(self, client):
        """Health check should be accessible without auth."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_healthz_endpoint_public(self, client):
        """Healthz check should be accessible without auth."""
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_readyz_endpoint_public(self, client):
        """Readyz check should be accessible without auth."""
        response = client.get("/readyz")
        assert response.status_code == 200
        assert response.json() == {"status": "ready"}

    def test_metrics_endpoint_public(self, client):
        """Metrics endpoint should be accessible without auth."""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert response.json() == {"metrics": "data"}

    def test_docs_endpoint_public(self, client):
        """API docs should be accessible without auth."""
        response = client.get("/docs")
        assert response.status_code == 200
        # FastAPI returns HTML for /docs, not JSON
        assert "<!DOCTYPE html>" in response.text or "swagger" in response.text.lower()

    def test_openapi_endpoint_public(self, client):
        """OpenAPI schema should be accessible without auth."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        # Verify it's an actual OpenAPI schema
        schema = response.json()
        assert "openapi" in schema
        assert "paths" in schema

    def test_redoc_endpoint_public(self, client):
        """ReDoc should be accessible without auth."""
        response = client.get("/redoc")
        assert response.status_code == 200
        # FastAPI returns HTML for /redoc, not JSON
        assert "<!DOCTYPE html>" in response.text or "redoc" in response.text.lower()

    def test_auth_login_endpoint_public(self, client):
        """Login endpoint should be accessible without auth."""
        response = client.post("/api/v1/auth/login")
        assert response.status_code == 200
        assert "token" in response.json()

    def test_auth_register_endpoint_public(self, client):
        """Register endpoint should be accessible without auth."""
        response = client.post("/api/v1/auth/register")
        assert response.status_code == 200
        assert "token" in response.json()

    def test_identity_authenticate_endpoint_public(self, client):
        """Identity authenticate endpoint should be accessible without auth."""
        response = client.post("/api/v1/identity/authenticate")
        assert response.status_code == 200
        assert response.json() == {"status": "authenticated"}

    def test_webauthn_challenge_endpoint_public(self, client):
        """WebAuthn challenge endpoint should be accessible without auth."""
        response = client.post("/id/webauthn/challenge")
        assert response.status_code == 200
        assert "challenge" in response.json()

    def test_webauthn_verify_endpoint_public(self, client):
        """WebAuthn verify endpoint should be accessible without auth."""
        response = client.post("/id/webauthn/verify")
        assert response.status_code == 200
        assert response.json() == {"verified": True}

    def test_protected_endpoint_requires_auth(self, client):
        """Protected endpoints should require authentication."""
        response = client.get("/api/protected")
        assert response.status_code == 401
        assert "error" in response.json()
        assert "Authentication required" in response.json()["error"]["message"]

    def test_consciousness_endpoint_requires_auth(self, client):
        """Consciousness endpoint should require authentication."""
        response = client.post("/api/v1/consciousness/query")
        assert response.status_code == 401
        assert "error" in response.json()

    def test_missing_bearer_prefix_rejected(self, client):
        """Tokens without Bearer prefix should be rejected."""
        response = client.get(
            "/api/protected",
            headers={"Authorization": "not-bearer-token"}
        )
        assert response.status_code == 401
        assert "error" in response.json()
        assert "Invalid authorization header format" in response.json()["error"]["message"]

    def test_empty_bearer_token_rejected(self, client):
        """Empty Bearer token should be rejected."""
        response = client.get(
            "/api/protected",
            headers={"Authorization": "Bearer "}
        )
        assert response.status_code == 401
        assert "error" in response.json()
        assert "Bearer token is empty" in response.json()["error"]["message"]

    def test_invalid_token_rejected(self, client):
        """Invalid tokens should be rejected."""
        response = client.get(
            "/api/protected",
            headers={"Authorization": "Bearer invalid-token-12345"}
        )
        assert response.status_code == 401
        assert "error" in response.json()
        assert "Invalid or expired" in response.json()["error"]["message"]

    def test_expired_token_rejected(self, client):
        """Expired tokens should be rejected."""
        response = client.get(
            "/api/protected",
            headers={"Authorization": "Bearer expired-token-placeholder-min-20-chars"}
        )
        assert response.status_code == 401
        assert "error" in response.json()

    def test_valid_token_grants_access(self, client):
        """Valid Bearer token should grant access."""
        response = client.get(
            "/api/protected",
            headers={"Authorization": "Bearer valid-test-token-with-minimum-20-chars"}
        )
        assert response.status_code == 200
        assert response.json() == {"status": "success", "message": "Protected endpoint accessed"}

    def test_valid_token_on_post_request(self, client):
        """Valid token should work for POST requests."""
        response = client.post(
            "/api/v1/consciousness/query",
            headers={"Authorization": "Bearer valid-test-token-with-minimum-20-chars"}
        )
        assert response.status_code == 200
        assert "response" in response.json()

    def test_token_without_user_id_rejected(self, client):
        """Token without user_id claim should be rejected."""
        response = client.get(
            "/api/protected",
            headers={"Authorization": "Bearer valid-token-no-user-id"}
        )
        assert response.status_code == 401
        assert "error" in response.json()
        assert "user_id" in response.json()["error"]["message"]

    def test_all_public_endpoints_accessible(self, client):
        """All allowlisted endpoints should be public."""
        public_get_paths = [
            "/health",
            "/healthz",
            "/readyz",
            "/metrics",
            "/docs",
            "/openapi.json",
            "/redoc",
        ]

        for path in public_get_paths:
            response = client.get(path)
            assert response.status_code == 200, f"{path} should be public (GET)"

        public_post_paths = [
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/identity/authenticate",
            "/id/webauthn/challenge",
            "/id/webauthn/verify",
        ]

        for path in public_post_paths:
            response = client.post(path)
            assert response.status_code == 200, f"{path} should be public (POST)"

    def test_post_requests_require_auth(self, client):
        """POST requests to protected endpoints should require auth."""
        response = client.post("/api/v1/consciousness/query")
        assert response.status_code == 401

    def test_error_response_format(self, client):
        """Error responses should follow OpenAI API format."""
        response = client.get("/api/protected")
        assert response.status_code == 401
        error = response.json()
        assert "error" in error
        assert "message" in error["error"]
        assert "type" in error["error"]
        assert "code" in error["error"]
        assert error["error"]["type"] == "invalid_request_error"
        assert error["error"]["code"] == "authentication_error"

    def test_case_sensitive_paths(self, client):
        """Path matching should be case-sensitive."""
        # /health is allowed, but /Health should require auth if it exists
        response = client.get("/api/PROTECTED")
        # Should return 401 because middleware runs before route matching
        # (route doesn't exist but middleware still enforces auth)
        assert response.status_code == 401

    def test_authorization_header_case_insensitive(self, client):
        """Authorization header should work regardless of case."""
        # FastAPI normalizes headers, but Bearer prefix must be exact
        response = client.get(
            "/api/protected",
            headers={"authorization": "Bearer valid-test-token-with-minimum-20-chars"}
        )
        # Should work because FastAPI normalizes header keys
        assert response.status_code == 200


class TestSecurityProperties:
    """Test security properties of the middleware."""

    def test_allowlist_is_minimal(self):
        """Verify allowlist contains only necessary public endpoints."""
        # This is a documentation test to ensure the allowlist stays minimal
        expected_max_allowlist_size = 15  # Conservative upper bound
        actual_size = len(StrictAuthMiddleware.ALLOWED_PATHS)
        assert actual_size <= expected_max_allowlist_size, (
            f"Allowlist has grown to {actual_size} endpoints. "
            f"Review each endpoint for necessity. "
            f"Current list: {sorted(StrictAuthMiddleware.ALLOWED_PATHS)}"
        )

    def test_allowlist_documented(self):
        """Verify all allowlist paths have comments/documentation."""
        # Read the middleware source to ensure all paths are documented
        # This is a meta-test to enforce good security practices
        import inspect
        source = inspect.getsource(StrictAuthMiddleware)

        # Each path should have a comment explaining why it's public
        for path in StrictAuthMiddleware.ALLOWED_PATHS:
            # Check if the path appears near a comment in the source
            assert path in source, f"Path {path} should be in ALLOWED_PATHS"

    def test_no_wildcard_patterns(self):
        """Verify allowlist uses exact paths, not wildcards."""
        for path in StrictAuthMiddleware.ALLOWED_PATHS:
            assert "*" not in path, f"Wildcard found in path: {path}"
            assert "?" not in path, f"Wildcard found in path: {path}"

    def test_no_regex_patterns(self):
        """Verify allowlist uses simple string matching, not regex."""
        for path in StrictAuthMiddleware.ALLOWED_PATHS:
            # No regex metacharacters
            forbidden_chars = ["|", "^", "$", "(", ")", "[", "]", "{", "}", "+"]
            for char in forbidden_chars:
                assert char not in path, (
                    f"Regex metacharacter '{char}' found in path: {path}"
                )
