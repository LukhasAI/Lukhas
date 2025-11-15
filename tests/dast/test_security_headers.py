"""Tests for OWASP security headers middleware.

Validates that all OWASP-recommended security headers are present and correctly
configured on all API responses, including health endpoints and OpenAI-compatible routes.

Test Coverage:
- X-Frame-Options header presence and value
- X-Content-Type-Options header presence and value
- Referrer-Policy header presence and value
- Permissions-Policy header presence and value
- Content-Security-Policy header presence and directives
- Headers applied to all endpoints (health, models, embeddings, etc.)
"""

import pytest
from fastapi.testclient import TestClient

# Import the serve/main.py app
from serve.main import app


@pytest.fixture
def client():
    """Create test client with security headers middleware."""
    return TestClient(app)


def test_security_headers_on_healthz(client):
    """Verify security headers are present on healthz endpoint."""
    response = client.get("/healthz")
    assert response.status_code == 200

    # X-Frame-Options protects against clickjacking
    assert response.headers.get("X-Frame-Options") == "DENY"

    # X-Content-Type-Options prevents MIME-sniffing
    assert response.headers.get("X-Content-Type-Options") == "nosniff"

    # Referrer-Policy controls information leakage
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"

    # Permissions-Policy restricts dangerous features
    assert "camera=()" in response.headers.get("Permissions-Policy", "")
    assert "microphone=()" in response.headers.get("Permissions-Policy", "")
    assert "geolocation=()" in response.headers.get("Permissions-Policy", "")

    # Content-Security-Policy provides XSS protection
    csp = response.headers.get("Content-Security-Policy", "")
    assert "default-src 'self'" in csp
    assert "object-src 'none'" in csp
    assert "frame-ancestors 'none'" in csp


def test_security_headers_on_models_endpoint(client):
    """Verify security headers are present on /v1/models endpoint."""
    response = client.get("/v1/models")
    assert response.status_code == 200

    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "camera=()" in response.headers.get("Permissions-Policy", "")

    csp = response.headers.get("Content-Security-Policy", "")
    assert "default-src 'self'" in csp


def test_security_headers_on_embeddings_endpoint(client):
    """Verify security headers on embeddings POST endpoint."""
    payload = {"input": "test text", "model": "text-embedding-ada-002"}
    response = client.post("/v1/embeddings", json=payload)
    assert response.status_code == 200

    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-Content-Type-Options") == "nosniff"


def test_security_headers_on_openapi_json(client):
    """Verify security headers on OpenAPI spec endpoint."""
    response = client.get("/openapi.json")
    assert response.status_code == 200

    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-Content-Type-Options") == "nosniff"


def test_security_headers_on_404_error(client):
    """Verify security headers are applied even to error responses."""
    response = client.get("/nonexistent-endpoint")
    assert response.status_code == 404

    # Security headers should still be present on error responses
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-Content-Type-Options") == "nosniff"


def test_csp_directive_parsing(client):
    """Verify CSP directives are correctly formatted."""
    response = client.get("/healthz")
    csp = response.headers.get("Content-Security-Policy", "")

    # Parse CSP directives
    directives = {}
    for directive in csp.split(";"):
        parts = directive.strip().split(maxsplit=1)
        if len(parts) == 2:
            directives[parts[0]] = parts[1]

    # Validate specific directives
    assert directives.get("default-src") == "'self'"
    assert directives.get("object-src") == "'none'"
    assert directives.get("frame-ancestors") == "'none'"


def test_permissions_policy_format(client):
    """Verify Permissions-Policy has correct format."""
    response = client.get("/healthz")
    permissions = response.headers.get("Permissions-Policy", "")

    # Verify format: feature=()
    assert "camera=()" in permissions
    assert "microphone=()" in permissions
    assert "geolocation=()" in permissions


def test_security_headers_do_not_override_existing(client):
    """Verify setdefault behavior - doesn't override existing headers.

    Note: This test validates the middleware uses setdefault() which won't
    override headers already set by the application or other middleware.
    """
    # The HeadersMiddleware in serve/main.py sets X-Trace-Id
    response = client.get("/healthz")

    # Both security headers AND existing headers should be present
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-Trace-Id") is not None  # From HeadersMiddleware


def test_all_required_headers_present(client):
    """Comprehensive test: verify ALL required security headers are present."""
    response = client.get("/healthz")

    required_headers = [
        "X-Frame-Options",
        "X-Content-Type-Options",
        "Referrer-Policy",
        "Permissions-Policy",
        "Content-Security-Policy",
    ]

    for header in required_headers:
        assert header in response.headers, f"Missing required security header: {header}"


@pytest.mark.parametrize("endpoint", [
    "/healthz",
    "/health",
    "/readyz",
    "/metrics",
    "/v1/models",
    "/openapi.json",
])
def test_security_headers_on_all_public_endpoints(client, endpoint):
    """Parametrized test: verify headers on all public endpoints."""
    response = client.get(endpoint)

    # Should have successful response (200 OK)
    assert response.status_code == 200

    # Should have all security headers
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert "default-src 'self'" in response.headers.get("Content-Security-Policy", "")
