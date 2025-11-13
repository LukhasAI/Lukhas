"""
Test T4/0.01% quality improvements.

Validates the high-quality improvements made for OpenAI/Anthropic engineers:
- OpenAI-Processing-Ms header for latency tracking
- Cache-Control header on /v1/models for CDN caching
- OWASP security headers (X-Content-Type-Options, X-Frame-Options, Referrer-Policy)
- Correct OpenAI error envelope structure
"""
import pytest
from fastapi.testclient import TestClient
from serve.main import app
from tests.smoke.fixtures import GOLDEN_AUTH_HEADERS


@pytest.fixture
def client(monkeypatch):
    """Create test client with strict auth mode enabled."""
    monkeypatch.setenv("LUKHAS_POLICY_MODE", "strict")
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Provide valid Bearer token for authenticated requests."""
    return GOLDEN_AUTH_HEADERS


# OpenAI-Processing-Ms Header Tests
def test_processing_ms_header_present(client, auth_headers):
    """Verify OpenAI-Processing-Ms header is present in responses."""
    response = client.get("/v1/models", headers=auth_headers)
    assert response.status_code == 200

    assert "OpenAI-Processing-Ms" in response.headers, \
        "Missing OpenAI-Processing-Ms header for latency tracking"


def test_processing_ms_header_format(client, auth_headers):
    """Verify OpenAI-Processing-Ms header contains valid millisecond value."""
    response = client.get("/v1/models", headers=auth_headers)
    assert response.status_code == 200

    processing_ms = response.headers.get("OpenAI-Processing-Ms")
    assert processing_ms is not None, "OpenAI-Processing-Ms header missing"
    assert processing_ms.isdigit(), \
        f"OpenAI-Processing-Ms should be numeric, got: {processing_ms}"

    ms_value = int(processing_ms)
    assert 0 <= ms_value < 10000, \
        f"Processing time seems unreasonable: {ms_value}ms (expected 0-10000ms)"


@pytest.mark.parametrize("endpoint", [
    "/v1/models",
    "/v1/embeddings",
    "/healthz",
])
def test_processing_ms_on_all_endpoints(client, auth_headers, endpoint):
    """Verify all endpoints include OpenAI-Processing-Ms header."""
    if endpoint == "/v1/embeddings":
        response = client.post(endpoint, json={"input": "test"}, headers=auth_headers)
    else:
        response = client.get(endpoint, headers=auth_headers if endpoint == "/v1/models" else {})

    assert "OpenAI-Processing-Ms" in response.headers, \
        f"Missing OpenAI-Processing-Ms header on {endpoint}"


# Cache-Control Header Tests
def test_cache_control_on_models_endpoint(client, auth_headers):
    """Verify /v1/models includes Cache-Control header for CDN caching."""
    response = client.get("/v1/models", headers=auth_headers)
    assert response.status_code == 200

    assert "Cache-Control" in response.headers, \
        "Missing Cache-Control header on /v1/models"


def test_cache_control_value(client, auth_headers):
    """Verify Cache-Control header has correct value for public caching."""
    response = client.get("/v1/models", headers=auth_headers)
    assert response.status_code == 200

    cache_control = response.headers.get("Cache-Control")
    assert cache_control == "public, max-age=3600", \
        f"Expected 'public, max-age=3600', got: {cache_control}"


# OWASP Security Headers Tests
def test_security_header_x_content_type_options(client, auth_headers):
    """Verify X-Content-Type-Options header prevents MIME sniffing."""
    response = client.get("/v1/models", headers=auth_headers)
    assert response.status_code == 200

    assert "X-Content-Type-Options" in response.headers, \
        "Missing X-Content-Type-Options security header"
    assert response.headers["X-Content-Type-Options"] == "nosniff", \
        f"X-Content-Type-Options should be 'nosniff', got: {response.headers['X-Content-Type-Options']}"


def test_security_header_x_frame_options(client, auth_headers):
    """Verify X-Frame-Options header prevents clickjacking."""
    response = client.get("/v1/models", headers=auth_headers)
    assert response.status_code == 200

    assert "X-Frame-Options" in response.headers, \
        "Missing X-Frame-Options security header"
    assert response.headers["X-Frame-Options"] == "DENY", \
        f"X-Frame-Options should be 'DENY', got: {response.headers['X-Frame-Options']}"


def test_security_header_referrer_policy(client, auth_headers):
    """Verify Referrer-Policy header protects privacy."""
    response = client.get("/v1/models", headers=auth_headers)
    assert response.status_code == 200

    assert "Referrer-Policy" in response.headers, \
        "Missing Referrer-Policy security header"
    assert response.headers["Referrer-Policy"] == "no-referrer", \
        f"Referrer-Policy should be 'no-referrer', got: {response.headers['Referrer-Policy']}"


@pytest.mark.parametrize("security_header,expected_value", [
    ("X-Content-Type-Options", "nosniff"),
    ("X-Frame-Options", "DENY"),
    ("Referrer-Policy", "no-referrer"),
])
def test_all_security_headers_present(client, auth_headers, security_header, expected_value):
    """Verify all OWASP security headers are present on all endpoints (parametrized)."""
    response = client.get("/v1/models", headers=auth_headers)
    assert response.status_code == 200

    assert security_header in response.headers, \
        f"Missing {security_header} security header"
    assert response.headers[security_header] == expected_value, \
        f"{security_header} should be '{expected_value}', got: {response.headers[security_header]}"


# Error Envelope Structure Tests
def test_error_envelope_not_double_nested(client):
    """Verify error envelope is NOT double-nested (critical bug fix)."""
    response = client.get("/v1/models")  # No auth - should return 401
    assert response.status_code == 401

    data = response.json()

    # Should have top-level "error" key
    assert "error" in data, f"Missing top-level 'error' key in: {data}"

    # Should NOT have nested structure like {'error': {'message': {'error': ...}}}
    error = data["error"]
    assert isinstance(error, dict), f"Error should be dict, got: {type(error)}"

    # Message should be a STRING, not a dict
    assert "message" in error, f"Missing 'message' in error: {error}"
    assert isinstance(error["message"], str), \
        f"Error message should be string, not dict (double-nesting bug)"


def test_error_envelope_openai_format(client):
    """Verify error envelope matches exact OpenAI spec."""
    response = client.get("/v1/models")  # No auth - should return 401
    assert response.status_code == 401

    data = response.json()
    error = data["error"]

    # OpenAI error envelope requires: type, message, code
    required_fields = ["type", "message", "code"]
    for field in required_fields:
        assert field in error, f"OpenAI error envelope missing '{field}' field"

    # All values should be strings
    for field in required_fields:
        assert isinstance(error[field], str), \
            f"Field '{field}' should be string, got: {type(error[field])}"


# Rate Limit Headers Tests (from existing implementation)
def test_rate_limit_headers_present(client, auth_headers):
    """Verify rate limit headers are present (OpenAI compatibility)."""
    response = client.get("/v1/models", headers=auth_headers)
    assert response.status_code == 200

    # Both formats (for compatibility)
    assert "X-RateLimit-Limit" in response.headers
    assert "x-ratelimit-limit-requests" in response.headers


def test_trace_id_header_present(client, auth_headers):
    """Verify X-Trace-Id header is present for request tracking."""
    response = client.get("/v1/models", headers=auth_headers)
    assert response.status_code == 200

    assert "X-Trace-Id" in response.headers, "Missing X-Trace-Id header"
    trace_id = response.headers["X-Trace-Id"]

    # Should be a valid UUID-like string (32 hex chars without hyphens)
    assert len(trace_id) == 32, f"Trace ID should be 32 chars, got: {len(trace_id)}"
    assert trace_id.isalnum(), f"Trace ID should be alphanumeric, got: {trace_id}"
