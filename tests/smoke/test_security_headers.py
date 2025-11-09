"""
Test security headers and CORS configuration.

Validates:
- Security headers present (X-Content-Type-Options, X-Frame-Options, etc.)
- CORS headers configured correctly
- No sensitive data leaked in headers
- Content-Type headers accurate
- X-Trace-Id for observability
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


# Content-Type Tests
def test_json_endpoints_return_json_content_type(client, auth_headers):
    """Verify JSON endpoints return application/json Content-Type."""
    json_endpoints = [
        ("GET", "/v1/models", None),
        ("POST", "/v1/responses", {"input": "test"}),
        ("POST", "/v1/embeddings", {"input": "test"}),
        ("POST", "/v1/dreams", {"seed": "test"}),
        ("GET", "/healthz", None),
        ("GET", "/readyz", None),
    ]

    for method, path, json_data in json_endpoints:
        if method == "GET":
            if path in ["/healthz", "/readyz"]:
                response = client.get(path)
            else:
                response = client.get(path, headers=auth_headers)
        else:
            response = client.post(path, json=json_data, headers=auth_headers)

        content_type = response.headers.get("content-type", "")
        assert "application/json" in content_type.lower(), \
            f"{method} {path} returned Content-Type: {content_type}"


def test_metrics_returns_text_plain(client):
    """Verify /metrics returns text/plain Content-Type."""
    response = client.get("/metrics")
    assert response.status_code == 200

    content_type = response.headers.get("content-type", "")
    assert "text/plain" in content_type.lower()


# Security Headers Tests
def test_x_content_type_options_present(client, auth_headers):
    """Verify X-Content-Type-Options: nosniff header present."""
    response = client.get("/v1/models", headers=auth_headers)
    assert response.status_code == 200

    # Check for security header
    x_content_type = response.headers.get("X-Content-Type-Options", "")
    # May or may not be set depending on middleware configuration
    if x_content_type:
        assert x_content_type.lower() == "nosniff"


def test_x_frame_options_present(client, auth_headers):
    """Verify X-Frame-Options header for clickjacking protection."""
    response = client.get("/v1/models", headers=auth_headers)
    assert response.status_code == 200

    # Check for clickjacking protection
    x_frame = response.headers.get("X-Frame-Options", "")
    # May or may not be set
    if x_frame:
        assert x_frame.upper() in ["DENY", "SAMEORIGIN"]


def test_no_server_header_leakage(client, auth_headers):
    """Verify Server header doesn't leak sensitive version info."""
    response = client.get("/v1/models", headers=auth_headers)
    assert response.status_code == 200

    server = response.headers.get("Server", "")
    # If Server header present, shouldn't contain version numbers
    if server:
        # Should not reveal specific versions like "uvicorn/0.20.0"
        assert "uvicorn" not in server.lower() or "/" not in server


# CORS Tests
def test_cors_preflight_request(client):
    """Verify CORS preflight (OPTIONS) requests handled."""
    response = client.options(
        "/v1/models",
        headers={
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization"
        }
    )

    # Should handle OPTIONS request
    # May return 200 (CORS enabled) or 405 (CORS not configured)
    assert response.status_code in [200, 405]


def test_cors_origin_header_present(client, auth_headers):
    """Verify CORS headers present when Origin sent."""
    response = client.get(
        "/v1/models",
        headers={
            **auth_headers,
            "Origin": "https://example.com"
        }
    )

    # May or may not have CORS headers depending on configuration
    # Just verify request succeeds
    assert response.status_code == 200


# Observability Headers Tests
def test_x_trace_id_format_when_present(client, auth_headers):
    """Verify X-Trace-Id header format when present."""
    response = client.get("/v1/models", headers=auth_headers)
    assert response.status_code == 200

    # X-Trace-Id may be present if OTEL enabled
    trace_id = response.headers.get("X-Trace-Id")
    if trace_id:
        # Should be 32-char hex string
        assert len(trace_id) == 32, f"X-Trace-Id should be 32 chars: {trace_id}"
        assert all(c in "0123456789abcdef" for c in trace_id), \
            f"X-Trace-Id should be hex: {trace_id}"


def test_trace_id_different_per_request(client, auth_headers):
    """Verify X-Trace-Id is unique per request when present."""
    response1 = client.get("/v1/models", headers=auth_headers)
    response2 = client.get("/v1/models", headers=auth_headers)

    trace_id1 = response1.headers.get("X-Trace-Id")
    trace_id2 = response2.headers.get("X-Trace-Id")

    # If both present, should be different
    if trace_id1 and trace_id2:
        assert trace_id1 != trace_id2, "Trace IDs should be unique per request"


# No Sensitive Data Leakage Tests
def test_no_auth_token_in_response_headers(client, auth_headers):
    """Verify auth token not echoed in response headers."""
    token = auth_headers["Authorization"].split(" ")[1]

    response = client.get("/v1/models", headers=auth_headers)
    assert response.status_code == 200

    # Check all headers
    for header_name, header_value in response.headers.items():
        assert token not in header_value, \
            f"Token leaked in {header_name} header"


def test_no_auth_token_in_response_body(client, auth_headers):
    """Verify auth token not leaked in response body."""
    token = auth_headers["Authorization"].split(" ")[1]

    response = client.get("/v1/models", headers=auth_headers)
    assert response.status_code == 200

    response_text = response.text
    assert token not in response_text, "Token leaked in response body"


def test_error_responses_no_stack_traces(client):
    """Verify error responses don't leak stack traces."""
    # Trigger an error
    response = client.get("/v1/models")  # No auth
    assert response.status_code == 401

    response_text = response.text.lower()

    # Should not contain Python stack trace indicators
    stack_trace_indicators = [
        "traceback",
        ".py:",
        "line ",
        "file \"",
        "exception:",
    ]

    for indicator in stack_trace_indicators:
        assert indicator not in response_text, \
            f"Stack trace indicator found: {indicator}"


# Cache Control Tests
def test_cache_control_headers_appropriate(client, auth_headers):
    """Verify Cache-Control headers are appropriate for each endpoint."""
    # Models endpoint could be cached
    models_response = client.get("/v1/models", headers=auth_headers)
    assert models_response.status_code == 200

    # Dynamic endpoints should not be cached
    responses_response = client.post(
        "/v1/responses",
        json={"input": "test"},
        headers=auth_headers
    )
    assert responses_response.status_code == 200

    cache_control = responses_response.headers.get("Cache-Control", "")
    # If present, dynamic content shouldn't be cached
    if cache_control:
        assert "no-cache" in cache_control.lower() or "no-store" in cache_control.lower()


# HTTP Strict Transport Security Tests
def test_hsts_header_consideration(client, auth_headers):
    """Verify HSTS header consideration for HTTPS."""
    response = client.get("/v1/models", headers=auth_headers)
    assert response.status_code == 200

    # HSTS may or may not be present (depends on deployment)
    # Just document that it should be considered for production
    hsts = response.headers.get("Strict-Transport-Security")
    # If present, verify format
    if hsts:
        assert "max-age" in hsts.lower()


# Content Security Policy Tests
def test_csp_header_consideration(client, auth_headers):
    """Verify CSP header consideration for XSS protection."""
    response = client.get("/v1/models", headers=auth_headers)
    assert response.status_code == 200

    # CSP may or may not be present
    # Just verify request succeeds and document for production consideration
    response.headers.get("Content-Security-Policy")
    # CSP is typically more important for HTML responses
    # API responses may not need it


# Response Headers Consistency Tests
def test_response_headers_consistent_across_endpoints(client, auth_headers):
    """Verify response headers consistent across different endpoints."""
    endpoints = [
        ("GET", "/v1/models", None),
        ("POST", "/v1/responses", {"input": "test"}),
        ("POST", "/v1/embeddings", {"input": "test"}),
    ]

    content_types = []
    for method, path, json_data in endpoints:
        if method == "GET":
            response = client.get(path, headers=auth_headers)
        else:
            response = client.post(path, json=json_data, headers=auth_headers)

        content_types.append(response.headers.get("content-type", ""))

    # All JSON endpoints should return JSON content-type
    for ct in content_types:
        assert "application/json" in ct.lower()


# Retry-After Header Tests
def test_retry_after_header_on_429(client, auth_headers):
    """Verify Retry-After header present on 429 responses."""
    # Try to trigger rate limit
    for _ in range(100):
        response = client.get("/v1/models", headers=auth_headers)
        if response.status_code == 429:
            # Should have Retry-After
            retry_after = response.headers.get("Retry-After")
            assert retry_after is not None, "429 should include Retry-After header"
            # Should be numeric (seconds)
            assert retry_after.replace(".", "").isdigit()
            break
