"""Tests for JWKS FastAPI endpoint.

Tests cover:
- JWKS endpoint returns valid JSON
- RFC 7517 compliance
- CORS headers
- Caching headers
- Health check endpoint
"""

import tempfile

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.identity.jwks_endpoint import router, init_jwks_endpoint
from core.identity.keys import KeyManager


@pytest.fixture
def temp_key_dir():
    """Temporary directory for test keys."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def key_manager(temp_key_dir):
    """KeyManager instance for testing."""
    return KeyManager(algorithm="RS256", key_dir=temp_key_dir)


@pytest.fixture
def app(key_manager):
    """FastAPI app with JWKS router."""
    app = FastAPI()
    app.include_router(router)

    # Initialize JWKS endpoint
    init_jwks_endpoint(key_manager)

    return app


@pytest.fixture
def client(app):
    """Test client for FastAPI app."""
    return TestClient(app)


def test_jwks_endpoint_returns_valid_json(client):
    """Test that JWKS endpoint returns valid JSON."""
    response = client.get("/.well-known/jwks.json")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"

    data = response.json()
    assert "keys" in data
    assert isinstance(data["keys"], list)
    assert len(data["keys"]) >= 1


def test_jwks_contains_required_fields(client):
    """Test that JWKS contains required RFC 7517 fields."""
    response = client.get("/.well-known/jwks.json")
    data = response.json()

    key = data["keys"][0]

    # Required fields per RFC 7517
    assert "kty" in key  # Key type
    assert "use" in key  # Public key use
    assert "kid" in key  # Key ID
    assert "alg" in key  # Algorithm

    # RSA-specific fields
    if key["kty"] == "RSA":
        assert "n" in key  # Modulus
        assert "e" in key  # Exponent


def test_jwks_caching_headers(client):
    """Test that JWKS response includes caching headers."""
    response = client.get("/.well-known/jwks.json")

    # Check Cache-Control header
    assert "cache-control" in response.headers
    assert "max-age=3600" in response.headers["cache-control"]


def test_jwks_cors_headers(client):
    """Test that JWKS response allows CORS."""
    response = client.get("/.well-known/jwks.json")

    # Check CORS header
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "*"


def test_jwks_health_endpoint(client):
    """Test JWKS health check endpoint."""
    response = client.get("/.well-known/jwks/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert "total_keys" in data
    assert "active_keys" in data
    assert "algorithm" in data


def test_openid_configuration_endpoint(client):
    """Test OpenID Connect Discovery endpoint."""
    response = client.get("/.well-known/openid-configuration")

    assert response.status_code == 200
    data = response.json()

    # Required fields per RFC 8414
    assert data["issuer"] == "https://ai"
    assert "jwks_uri" in data
    assert "authorization_endpoint" in data
    assert "token_endpoint" in data
    assert "response_types_supported" in data
    assert "subject_types_supported" in data
    assert "id_token_signing_alg_values_supported" in data


def test_jwks_endpoint_without_initialization():
    """Test that JWKS endpoint fails gracefully if not initialized."""
    # Create new app without initializing JWKS endpoint
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    response = client.get("/.well-known/jwks.json")
    assert response.status_code == 500


def test_jwks_keys_match_key_manager(client, key_manager):
    """Test that JWKS endpoint returns same keys as KeyManager."""
    # Get JWKS from endpoint
    response = client.get("/.well-known/jwks.json")
    endpoint_jwks = response.json()

    # Get JWKS from KeyManager
    manager_jwks = key_manager.export_jwks()

    # Should match
    assert len(endpoint_jwks["keys"]) == len(manager_jwks["keys"])

    endpoint_kids = {key["kid"] for key in endpoint_jwks["keys"]}
    manager_kids = {key["kid"] for key in manager_jwks["keys"]}
    assert endpoint_kids == manager_kids


def test_jwks_endpoint_with_multiple_keys(temp_key_dir):
    """Test JWKS endpoint with multiple keys (after rotation)."""
    km = KeyManager(algorithm="RS256", key_dir=temp_key_dir)

    # Rotate to create multiple keys
    km.rotate_keys()

    # Initialize app
    app = FastAPI()
    app.include_router(router)
    init_jwks_endpoint(km)
    client = TestClient(app)

    # Get JWKS
    response = client.get("/.well-known/jwks.json")
    data = response.json()

    # Should have multiple keys
    assert len(data["keys"]) >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
