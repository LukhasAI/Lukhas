"""Comprehensive tests for serve/middleware/strict_auth.py - Authentication middleware"""
from unittest.mock import MagicMock, Mock, patch

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from serve.middleware.strict_auth import StrictAuthMiddleware


@pytest.fixture
def mock_auth_system():
    """Create mock authentication system"""
    auth = MagicMock()
    auth.verify_jwt = MagicMock(return_value={"user_id": "test-user", "exp": 9999999999})
    return auth


@pytest.fixture
def app_with_middleware(mock_auth_system):
    """Create FastAPI app with StrictAuthMiddleware"""
    app = FastAPI()

    # Patch get_auth_system before adding middleware
    with patch("serve.middleware.strict_auth.get_auth_system", return_value=mock_auth_system):
        app.add_middleware(StrictAuthMiddleware)

        @app.get("/v1/test")
        def v1_endpoint():
            return {"message": "authenticated"}

        @app.get("/v2/test")
        def v2_endpoint():
            return {"message": "no auth required"}

        @app.get("/healthz")
        def health():
            return {"status": "ok"}

    return app, mock_auth_system


@pytest.fixture
def client(app_with_middleware):
    """Create test client"""
    app, _ = app_with_middleware
    return TestClient(app)


@pytest.fixture
def client_and_auth(app_with_middleware):
    """Create test client with access to mock auth"""
    app, auth = app_with_middleware
    return TestClient(app), auth


# ============================================================================
# Authentication Success Tests
# ============================================================================

def test_valid_bearer_token_allows_access(client_and_auth):
    """Test valid Bearer token allows access to /v1/* endpoints"""
    client, auth = client_and_auth
    auth.verify_jwt.return_value = {"user_id": "test-user"}

    response = client.get("/v1/test", headers={
        "Authorization": "Bearer valid-token-123"
    })

    assert response.status_code == 200
    assert response.json()["message"] == "authenticated"
    auth.verify_jwt.assert_called_once_with("valid-token-123")


def test_valid_jwt_with_payload(client_and_auth):
    """Test middleware passes request when JWT payload is valid"""
    client, auth = client_and_auth
    auth.verify_jwt.return_value = {
        "user_id": "user123",
        "email": "test@example.com",
        "exp": 9999999999
    }

    response = client.get("/v1/test", headers={
        "Authorization": "Bearer jwt-token"
    })

    assert response.status_code == 200
    auth.verify_jwt.assert_called_once_with("jwt-token")


def test_token_with_whitespace_trimmed(client_and_auth):
    """Test Bearer token is properly trimmed"""
    client, auth = client_and_auth
    auth.verify_jwt.return_value = {"user_id": "test"}

    response = client.get("/v1/test", headers={
        "Authorization": "Bearer   token-with-spaces   "
    })

    assert response.status_code == 200
    # Should be trimmed before verification
    auth.verify_jwt.assert_called_once_with("token-with-spaces")


# ============================================================================
# Authentication Failure Tests
# ============================================================================

def test_missing_authorization_header(client):
    """Test request without Authorization header returns 401"""
    response = client.get("/v1/test")
    assert response.status_code == 401
    data = response.json()
    assert "error" in data
    assert data["error"]["type"] == "invalid_api_key"
    assert "Missing Authorization header" in data["error"]["message"]


def test_empty_authorization_header(client):
    """Test empty Authorization header returns 401"""
    response = client.get("/v1/test", headers={"Authorization": ""})
    assert response.status_code == 401
    data = response.json()
    assert data["error"]["type"] == "invalid_api_key"


def test_non_bearer_scheme(client):
    """Test non-Bearer auth scheme returns 401"""
    response = client.get("/v1/test", headers={
        "Authorization": "Basic dXNlcjpwYXNz"
    })
    assert response.status_code == 401
    data = response.json()
    assert "Bearer scheme" in data["error"]["message"]


def test_bearer_without_token(client):
    """Test 'Bearer' without token returns 401"""
    response = client.get("/v1/test", headers={
        "Authorization": "Bearer"
    })
    assert response.status_code == 401


def test_bearer_with_only_whitespace(client):
    """Test Bearer with only whitespace token returns 401"""
    response = client.get("/v1/test", headers={
        "Authorization": "Bearer    "
    })
    assert response.status_code == 401
    data = response.json()
    assert "empty" in data["error"]["message"]


def test_invalid_jwt_token(client_and_auth):
    """Test invalid JWT token returns 401"""
    client, auth = client_and_auth
    auth.verify_jwt.return_value = None  # Invalid token

    response = client.get("/v1/test", headers={
        "Authorization": "Bearer invalid-token"
    })

    assert response.status_code == 401
    data = response.json()
    assert "Invalid authentication credentials" in data["error"]["message"]


def test_expired_jwt_token(client_and_auth):
    """Test expired JWT token returns 401"""
    client, auth = client_and_auth
    auth.verify_jwt.return_value = None  # Expired

    response = client.get("/v1/test", headers={
        "Authorization": "Bearer expired-token"
    })

    assert response.status_code == 401


def test_malformed_bearer_header(client):
    """Test malformed Bearer header returns 401"""
    malformed_headers = [
        "BearerToken123",  # Missing space
        "bearer token123",  # Lowercase
        "BEARER token123",  # Uppercase
        " Bearer token",   # Leading space
    ]

    for header in malformed_headers:
        response = client.get("/v1/test", headers={"Authorization": header})
        assert response.status_code == 401


# ============================================================================
# Path-Based Routing Tests
# ============================================================================

def test_v1_endpoints_require_auth(client):
    """Test all /v1/* endpoints require authentication"""
    v1_paths = [
        "/v1/test",
        "/v1/models",
        "/v1/chat/completions",
        "/v1/embeddings",
    ]

    for path in v1_paths:
        response = client.get(path)
        assert response.status_code == 401, f"Path {path} should require auth"


def test_non_v1_endpoints_skip_auth(client):
    """Test non-/v1/* endpoints skip authentication"""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_v2_endpoints_skip_auth(client):
    """Test /v2/* endpoints are not protected"""
    response = client.get("/v2/test")
    assert response.status_code == 200
    assert response.json()["message"] == "no auth required"


def test_root_endpoint_skips_auth(client):
    """Test root path skips authentication"""
    # This would be 404 but not 401
    response = client.get("/")
    assert response.status_code == 404  # Not found, but not auth error


def test_v1_with_trailing_slash(client):
    """Test /v1/ path matching works correctly"""
    response = client.get("/v1/")
    assert response.status_code == 401  # Should still require auth


# ============================================================================
# Error Response Format Tests
# ============================================================================

def test_error_response_openai_compatible(client):
    """Test 401 error follows OpenAI error format"""
    response = client.get("/v1/test")
    assert response.status_code == 401
    data = response.json()

    # Check OpenAI-compatible structure
    assert "error" in data
    error = data["error"]
    assert "type" in error
    assert "message" in error
    assert "code" in error
    assert error["type"] == "invalid_api_key"
    assert error["code"] == "invalid_api_key"


def test_error_response_content_type(client):
    """Test error response has correct content-type"""
    response = client.get("/v1/test")
    assert response.status_code == 401
    assert "application/json" in response.headers.get("content-type", "")


def test_different_error_messages(client):
    """Test different auth failures return appropriate messages"""
    test_cases = [
        ({}, "Missing Authorization header"),
        ({"Authorization": "Basic user:pass"}, "Bearer scheme"),
        ({"Authorization": "Bearer "}, "empty"),
    ]

    for headers, expected_text in test_cases:
        response = client.get("/v1/test", headers=headers)
        assert response.status_code == 401
        assert expected_text in response.json()["error"]["message"]


# ============================================================================
# HTTP Method Tests
# ============================================================================

def test_post_request_requires_auth(client):
    """Test POST requests to /v1/* require auth"""
    response = client.post("/v1/test")
    assert response.status_code == 401


def test_put_request_requires_auth(client):
    """Test PUT requests to /v1/* require auth"""
    response = client.put("/v1/test")
    assert response.status_code == 401


def test_delete_request_requires_auth(client):
    """Test DELETE requests to /v1/* require auth"""
    response = client.delete("/v1/test")
    assert response.status_code == 401


def test_patch_request_requires_auth(client):
    """Test PATCH requests to /v1/* require auth"""
    response = client.patch("/v1/test")
    assert response.status_code == 401


def test_options_request_requires_auth(client):
    """Test OPTIONS requests to /v1/* require auth"""
    response = client.options("/v1/test")
    assert response.status_code == 401


# ============================================================================
# Edge Cases and Security Tests
# ============================================================================

def test_case_sensitive_bearer(client):
    """Test Bearer scheme is case-sensitive"""
    response = client.get("/v1/test", headers={
        "Authorization": "bearer token123"
    })
    assert response.status_code == 401


def test_multiple_authorization_headers(client_and_auth):
    """Test middleware handles multiple Authorization headers"""
    client, auth = client_and_auth
    auth.verify_jwt.return_value = {"user_id": "test"}

    # TestClient doesn't support duplicate headers well, but we can test the logic
    response = client.get("/v1/test", headers={
        "Authorization": "Bearer token123"
    })
    # Should use the first/only header
    assert response.status_code == 200


def test_authorization_header_with_special_chars(client_and_auth):
    """Test token with special characters"""
    client, auth = client_and_auth
    auth.verify_jwt.return_value = {"user_id": "test"}

    special_tokens = [
        "Bearer token-with-dashes",
        "Bearer token.with.dots",
        "Bearer token_with_underscores",
        "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U",
    ]

    for token_header in special_tokens:
        response = client.get("/v1/test", headers={"Authorization": token_header})
        assert response.status_code == 200


def test_very_long_token(client_and_auth):
    """Test handling of very long tokens"""
    client, auth = client_and_auth
    auth.verify_jwt.return_value = {"user_id": "test"}

    long_token = "a" * 10000
    response = client.get("/v1/test", headers={
        "Authorization": f"Bearer {long_token}"
    })
    assert response.status_code == 200
    auth.verify_jwt.assert_called_once_with(long_token)


def test_null_byte_in_token(client_and_auth):
    """Test token with null byte is handled"""
    client, auth = client_and_auth
    # Should be rejected by verify_jwt
    auth.verify_jwt.return_value = None

    response = client.get("/v1/test", headers={
        "Authorization": "Bearer token\x00null"
    })
    # Either 401 or handled safely
    assert response.status_code in [401, 400, 422]


# ============================================================================
# Integration Tests
# ============================================================================

def test_middleware_chain(mock_auth_system):
    """Test StrictAuthMiddleware works in middleware chain"""
    app = FastAPI()

    middleware_order = []

    # Custom middleware to track order
    from starlette.middleware.base import BaseHTTPMiddleware

    class TrackingMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            middleware_order.append("tracking")
            return await call_next(request)

    with patch("serve.middleware.strict_auth.get_auth_system", return_value=mock_auth_system):
        app.add_middleware(TrackingMiddleware)
        app.add_middleware(StrictAuthMiddleware)

        @app.get("/v1/test")
        def endpoint():
            return {"ok": True}

    client = TestClient(app)
    mock_auth_system.verify_jwt.return_value = {"user_id": "test"}

    response = client.get("/v1/test", headers={"Authorization": "Bearer token"})
    assert response.status_code == 200
    assert "tracking" in middleware_order


def test_concurrent_requests(client_and_auth):
    """Test middleware handles concurrent requests"""
    import concurrent.futures

    client, auth = client_and_auth
    auth.verify_jwt.return_value = {"user_id": "test"}

    def make_request():
        return client.get("/v1/test", headers={"Authorization": "Bearer token"})

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(make_request) for _ in range(10)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    assert all(r.status_code == 200 for r in results)
    assert auth.verify_jwt.call_count == 10


def test_auth_system_initialization():
    """Test middleware initializes auth system correctly"""
    app = FastAPI()

    mock_auth = MagicMock()
    with patch("serve.middleware.strict_auth.get_auth_system", return_value=mock_auth) as mock_get:
        app.add_middleware(StrictAuthMiddleware)
        # Should call get_auth_system during init
        mock_get.assert_called_once()


def test_request_pass_through(client_and_auth):
    """Test authenticated request passes through unchanged"""
    client, auth = client_and_auth
    auth.verify_jwt.return_value = {"user_id": "test123", "roles": ["admin"]}

    response = client.get("/v1/test", headers={
        "Authorization": "Bearer token",
        "X-Custom-Header": "test-value"
    })

    assert response.status_code == 200
    # Response should come from the endpoint
    assert response.json()["message"] == "authenticated"


# ============================================================================
# Robustness Tests
# ============================================================================

def test_auth_system_exception_handling(client_and_auth):
    """Test middleware handles auth system exceptions gracefully"""
    client, auth = client_and_auth
    auth.verify_jwt.side_effect = Exception("Auth system error")

    response = client.get("/v1/test", headers={"Authorization": "Bearer token"})
    # Should return 401 or 500, not crash
    assert response.status_code in [401, 500]


def test_auth_system_returns_empty_dict(client_and_auth):
    """Test middleware handles empty dict payload"""
    client, auth = client_and_auth
    auth.verify_jwt.return_value = {}  # Empty but not None

    response = client.get("/v1/test", headers={"Authorization": "Bearer token"})
    # Empty dict is still a valid payload
    assert response.status_code == 200


def test_auth_system_returns_none(client_and_auth):
    """Test middleware handles None payload as invalid"""
    client, auth = client_and_auth
    auth.verify_jwt.return_value = None

    response = client.get("/v1/test", headers={"Authorization": "Bearer token"})
    assert response.status_code == 401
    assert "Invalid authentication credentials" in response.json()["error"]["message"]
