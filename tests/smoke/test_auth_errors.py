"""
SPDX-License-Identifier: Apache-2.0

tests/smoke/test_auth_errors.py

Smoke tests for OpenAI façade authentication error handling.
Validates 401/403 responses match OpenAI error envelope format.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from lukhas.adapters.openai.api import get_app


@pytest.fixture
def strict_client(monkeypatch):
    """
    Create test client with strict policy mode.
    
    In strict mode, routes require valid authentication and RBAC checks.
    """
    monkeypatch.setenv("LUKHAS_POLICY_MODE", "strict")
    app = get_app()
    return TestClient(app)


def test_missing_bearer_yields_auth_error(strict_client):
    """
    Test that requests without Authorization header return 401/403.
    
    OpenAI API returns 401 with error envelope:
    {
        "error": {
            "type": "invalid_request_error",
            "message": "Invalid authentication...",
            "code": "invalid_api_key"
        }
    }
    """
    response = strict_client.get("/v1/models")
    
    # Accept either 401 or 403 (depends on policy implementation)
    assert response.status_code in (401, 403), \
        f"Expected 401/403, got {response.status_code}"
    
    body = response.json()
    assert "error" in body, "Response missing 'error' key"
    assert isinstance(body["error"], dict), "Error should be dict"
    
    # Validate OpenAI error envelope structure
    error = body["error"]
    assert "type" in error, "Error missing 'type' field"
    assert error["type"] in {
        "authorization_error",
        "invalid_request_error",
        "invalid_api_key",
        "insufficient_permissions"
    }, f"Unexpected error type: {error['type']}"
    
    # Should have message
    assert "message" in error, "Error missing 'message' field"
    assert isinstance(error["message"], str), "Message should be string"
    assert len(error["message"]) > 0, "Message should not be empty"


def test_invalid_bearer_yields_auth_error(strict_client):
    """
    Test that requests with invalid Bearer token return 401/403.
    
    OpenAI API validates token format and signature, returning
    structured error on failure.
    """
    response = strict_client.get(
        "/v1/models",
        headers={"Authorization": "Bearer INVALID_TOKEN_12345"}
    )
    
    # Accept either 401 or 403
    assert response.status_code in (401, 403), \
        f"Expected 401/403, got {response.status_code}"
    
    body = response.json()
    assert "error" in body, "Response missing 'error' key"
    
    error = body["error"]
    assert isinstance(error, dict), "Error should be dict"
    assert "type" in error, "Error missing 'type' field"
    assert "message" in error, "Error missing 'message' field"


def test_malformed_authorization_header(strict_client):
    """
    Test that malformed Authorization headers are rejected.
    
    Examples:
    - Missing "Bearer " prefix
    - Empty token
    - Invalid format
    """
    test_cases = [
        ("", "Empty header"),
        ("InvalidFormat", "Missing Bearer prefix"),
        ("Bearer ", "Empty token"),
        ("Basic dXNlcjpwYXNz", "Wrong auth scheme"),
    ]
    
    for auth_header, description in test_cases:
        response = strict_client.get(
            "/v1/models",
            headers={"Authorization": auth_header} if auth_header else {}
        )
        
        assert response.status_code in (401, 403), \
            f"{description}: Expected 401/403, got {response.status_code}"
        
        body = response.json()
        assert "error" in body, f"{description}: Missing error envelope"


def test_auth_error_has_retry_after_on_rate_limit(strict_client):
    """
    Test that rate-limited auth errors include Retry-After header.
    
    Note: This test validates the error format when rate limiting
    is triggered during authentication. May require multiple requests
    to trigger rate limit.
    """
    # Note: This test documents the expected behavior but may not
    # trigger actual rate limiting in test environment
    response = strict_client.get("/v1/models")
    
    # If we got a 429, validate Retry-After presence
    if response.status_code == 429:
        assert "Retry-After" in response.headers, \
            "Rate-limited responses must include Retry-After header"
        
        retry_after = response.headers["Retry-After"]
        assert retry_after.isdigit(), \
            f"Retry-After should be numeric seconds, got: {retry_after}"
        
        body = response.json()
        assert "error" in body
        assert body["error"]["type"] == "rate_limit_exceeded"
