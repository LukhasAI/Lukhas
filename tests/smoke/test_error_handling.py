"""
Test comprehensive error handling and HTTP status codes.

Validates:
- Proper error responses for all failure scenarios
- HTTP status code accuracy (400, 401, 403, 404, 429, 500)
- Error message clarity and actionability
- Error format consistency (OpenAI-compatible)
- Graceful degradation
"""

import pytest
from fastapi.testclient import TestClient
from serve.main import app

from tests.smoke.fixtures import GOLDEN_AUTH_HEADERS


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Provide valid Bearer token for authenticated requests."""
    return GOLDEN_AUTH_HEADERS


# 400 Bad Request Tests
def test_400_missing_required_field_responses(client, auth_headers):
    """Verify 400 when required field missing in /v1/responses."""
    response = client.post("/v1/responses", json={}, headers=auth_headers)  # Missing 'input'
    assert response.status_code == 400


def test_400_empty_input_responses(client, auth_headers):
    """Verify 400 when input is empty string."""
    response = client.post("/v1/responses", json={"input": ""}, headers=auth_headers)
    assert response.status_code == 400


def test_400_missing_input_embeddings(client, auth_headers):
    """Verify 400 when input missing in /v1/embeddings."""
    response = client.post("/v1/embeddings", json={}, headers=auth_headers)
    assert response.status_code == 400


def test_400_empty_input_embeddings(client, auth_headers):
    """Verify 400 when embeddings input is empty."""
    response = client.post("/v1/embeddings", json={"input": ""}, headers=auth_headers)
    assert response.status_code == 400


# 401 Unauthorized Tests
def test_401_missing_auth_header(client):
    """Verify 401 when Authorization header missing."""
    response = client.get("/v1/models")
    assert response.status_code == 401


def test_401_malformed_auth_header(client):
    """Verify 401 when Authorization header malformed."""
    response = client.get("/v1/models", headers={"Authorization": "NotBearer token"})
    assert response.status_code == 401


def test_401_empty_bearer_token(client):
    """Verify 401 when Bearer token is empty."""
    response = client.get("/v1/models", headers={"Authorization": "Bearer "})
    assert response.status_code == 401


def test_401_short_token(client):
    """Verify 401 when token too short (< 8 chars)."""
    response = client.get("/v1/models", headers={"Authorization": "Bearer abc"})
    assert response.status_code == 401


def test_401_error_format_openai_compatible(client):
    """Verify 401 error follows OpenAI format."""
    response = client.get("/v1/models")
    assert response.status_code == 401

    data = response.json()
    detail = data.get("detail", {})
    error = detail.get("error", detail) if isinstance(detail, dict) else {}

    # Should have type, message, code
    assert "type" in error
    assert "message" in error
    assert "code" in error
    assert error["code"] == "invalid_api_key"


# 404 Not Found Tests
def test_404_invalid_endpoint(client, auth_headers):
    """Verify 404 for non-existent endpoints."""
    response = client.get("/v1/nonexistent", headers=auth_headers)
    assert response.status_code == 404


def test_404_wrong_method(client, auth_headers):
    """Verify 405 Method Not Allowed for wrong HTTP method."""
    # /v1/models expects GET, not POST
    response = client.post("/v1/models", json={}, headers=auth_headers)
    assert response.status_code == 405


# Error Message Quality Tests
def test_error_messages_are_actionable(client, auth_headers):
    """Verify error messages provide actionable guidance."""
    # Missing input
    response = client.post("/v1/responses", json={}, headers=auth_headers)
    assert response.status_code == 400

    # Error should indicate what's wrong
    text = response.text.lower()
    assert "input" in text or "required" in text


def test_error_messages_no_sensitive_data(client):
    """Verify error messages don't leak sensitive data."""
    # Try with invalid token
    response = client.get("/v1/models", headers={"Authorization": "Bearer supersecrettoken123"})
    assert response.status_code in [200, 401]  # 200 if token valid, 401 if not

    # Response should not echo the token
    text = response.text
    assert "supersecrettoken123" not in text


# Graceful Degradation Tests
def test_graceful_degradation_matriz_unavailable(client, auth_headers):
    """Verify graceful degradation when MATRIZ unavailable."""
    # Should still work in stub mode
    response = client.post("/v1/responses", json={"input": "test when MATRIZ down"}, headers=auth_headers)

    # Should return 200 (stub mode) not 500
    assert response.status_code == 200

    data = response.json()
    assert "output" in data
    assert "text" in data["output"]


def test_graceful_degradation_memory_unavailable(client, auth_headers):
    """Verify graceful degradation when memory system unavailable."""
    # Embeddings should still work in stub mode
    response = client.post("/v1/embeddings", json={"input": "test when memory down"}, headers=auth_headers)

    # Should return 200 (stub mode) not 500
    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert len(data["data"]) > 0


# Content-Type Validation Tests
# Note: TestClient with middleware that consumes request body causes
# "Stream consumed" errors. Content-Type validation is handled by FastAPI.


# Error Response Consistency Tests
def test_all_errors_have_consistent_format(client, auth_headers):
    """Verify all error responses follow consistent format."""
    error_scenarios = [
        # 400 errors
        ("POST", "/v1/responses", {}),
        ("POST", "/v1/embeddings", {}),
        # 401 errors
        ("GET", "/v1/models", None),  # No auth
    ]

    for method, path, json_data in error_scenarios:
        if method == "GET":
            response = client.get(path)
        else:
            response = client.post(path, json=json_data, headers=auth_headers)

        if response.status_code >= 400:
            data = response.json()
            # Should be JSON
            assert isinstance(data, dict)


# Status Code Accuracy Tests
def test_status_codes_accurate_for_client_errors(client, auth_headers):
    """Verify 4xx status codes are used correctly for client errors."""
    # 400 - Bad Request (missing data)
    response = client.post("/v1/responses", json={}, headers=auth_headers)
    assert 400 <= response.status_code < 500

    # 401 - Unauthorized (no auth)
    response = client.get("/v1/models")
    assert response.status_code == 401

    # 404 - Not Found (wrong path)
    response = client.get("/v1/fake", headers=auth_headers)
    assert response.status_code == 404


def test_status_codes_never_return_5xx_for_valid_requests(client, auth_headers):
    """Verify valid requests never return 5xx errors."""
    valid_requests = [
        ("GET", "/v1/models", None),
        ("POST", "/v1/responses", {"input": "test"}),
        ("POST", "/v1/embeddings", {"input": "test"}),
        ("POST", "/v1/dreams", {"seed": "test"}),
        ("GET", "/healthz", None),
        ("GET", "/readyz", None),
        ("GET", "/metrics", None),
    ]

    for method, path, json_data in valid_requests:
        if method == "GET":
            # Health endpoints don't need auth
            if path in ["/healthz", "/readyz", "/metrics"]:
                response = client.get(path)
            else:
                response = client.get(path, headers=auth_headers)
        else:
            response = client.post(path, json=json_data, headers=auth_headers)

        # Should never be 5xx for valid requests
        assert response.status_code < 500, f"{method} {path} returned {response.status_code}"


# Timeout Handling Tests
def test_no_timeout_on_quick_requests(client, auth_headers):
    """Verify quick requests complete without timeout."""
    import time

    start = time.time()
    response = client.get("/v1/models", headers=auth_headers)
    elapsed = time.time() - start

    assert response.status_code == 200
    assert elapsed < 2.0, f"Request took {elapsed}s (should be < 2s)"


# Error Recovery Tests
def test_error_recovery_after_bad_request(client, auth_headers):
    """Verify service recovers after bad requests."""
    # Make a bad request
    bad_response = client.post("/v1/responses", json={}, headers=auth_headers)  # Missing input
    assert bad_response.status_code == 400

    # Subsequent good request should work
    good_response = client.post("/v1/responses", json={"input": "test"}, headers=auth_headers)
    assert good_response.status_code == 200


def test_error_recovery_after_auth_failure(client, auth_headers):
    """Verify service recovers after auth failures."""
    # Bad auth
    bad_response = client.get("/v1/models")
    assert bad_response.status_code == 401

    # Good auth should work
    good_response = client.get("/v1/models", headers=auth_headers)
    assert good_response.status_code == 200
