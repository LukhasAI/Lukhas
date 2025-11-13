"""
Tests for Identity API endpoints.

Tests:
- POST /api/v1/identity/authenticate
- GET /api/v1/identity/verify
- GET /api/v1/identity/tier-check
"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from serve.identity_api import router


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


class TestAuthenticate:
    """Tests for /api/v1/identity/authenticate endpoint."""

    def test_authenticate_success(self, client):
        """Test successful authentication."""
        response = client.post("/api/v1/identity/authenticate")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "authenticated"

    def test_authenticate_response_structure(self, client):
        """Test authentication response has correct structure."""
        response = client.post("/api/v1/identity/authenticate")

        data = response.json()
        assert "status" in data
        assert isinstance(data["status"], str)

    def test_authenticate_method_post_only(self, client):
        """Test that GET is not allowed on authenticate endpoint."""
        response = client.get("/api/v1/identity/authenticate")
        assert response.status_code == 405  # Method Not Allowed


class TestVerify:
    """Tests for /api/v1/identity/verify endpoint."""

    def test_verify_success(self, client):
        """Test successful verification."""
        response = client.get("/api/v1/identity/verify")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "verified"

    def test_verify_response_structure(self, client):
        """Test verification response has correct structure."""
        response = client.get("/api/v1/identity/verify")

        data = response.json()
        assert "status" in data
        assert isinstance(data["status"], str)

    def test_verify_method_get_only(self, client):
        """Test that POST is not allowed on verify endpoint."""
        response = client.post("/api/v1/identity/verify")
        assert response.status_code == 405  # Method Not Allowed


class TestTierCheck:
    """Tests for /api/v1/identity/tier-check endpoint."""

    def test_tier_check_success(self, client):
        """Test successful tier check."""
        response = client.get("/api/v1/identity/tier-check")

        assert response.status_code == 200
        data = response.json()
        assert data["tier"] == "premium"

    def test_tier_check_response_structure(self, client):
        """Test tier check response has correct structure."""
        response = client.get("/api/v1/identity/tier-check")

        data = response.json()
        assert "tier" in data
        assert isinstance(data["tier"], str)

    def test_tier_check_method_get_only(self, client):
        """Test that POST is not allowed on tier-check endpoint."""
        response = client.post("/api/v1/identity/tier-check")
        assert response.status_code == 405  # Method Not Allowed


class TestResponseTimes:
    """Tests for response time characteristics."""

    @pytest.mark.asyncio
    async def test_endpoints_are_async(self):
        """Verify all endpoints are async coroutines."""
        from serve.identity_api import authenticate, verify, tier_check
        import asyncio

        assert asyncio.iscoroutinefunction(authenticate)
        assert asyncio.iscoroutinefunction(verify)
        assert asyncio.iscoroutinefunction(tier_check)

    def test_all_endpoints_respond_quickly(self, client):
        """Test that all endpoints respond within reasonable time."""
        import time

        # Authenticate
        start = time.time()
        response = client.post("/api/v1/identity/authenticate")
        elapsed = time.time() - start
        assert response.status_code == 200
        assert elapsed < 0.1  # Should be well under 100ms

        # Verify
        start = time.time()
        response = client.get("/api/v1/identity/verify")
        elapsed = time.time() - start
        assert response.status_code == 200
        assert elapsed < 0.1

        # Tier check
        start = time.time()
        response = client.get("/api/v1/identity/tier-check")
        elapsed = time.time() - start
        assert response.status_code == 200
        assert elapsed < 0.1


class TestOpenAPISpec:
    """Tests for OpenAPI documentation."""

    def test_endpoints_have_openapi_metadata(self, app):
        """Test that all endpoints have OpenAPI metadata."""
        openapi = app.openapi()

        # Check authenticate
        assert "/api/v1/identity/authenticate" in openapi["paths"]
        authenticate_spec = openapi["paths"]["/api/v1/identity/authenticate"]["post"]
        assert "summary" in authenticate_spec
        assert authenticate_spec["summary"] == "Authenticate User"
        assert "200" in authenticate_spec["responses"]

        # Check verify
        assert "/api/v1/identity/verify" in openapi["paths"]
        verify_spec = openapi["paths"]["/api/v1/identity/verify"]["get"]
        assert "summary" in verify_spec
        assert verify_spec["summary"] == "Verify User"

        # Check tier-check
        assert "/api/v1/identity/tier-check" in openapi["paths"]
        tier_spec = openapi["paths"]["/api/v1/identity/tier-check"]["get"]
        assert "summary" in tier_spec
        assert tier_spec["summary"] == "Check User Tier"


class TestConcurrentRequests:
    """Tests for concurrent request handling."""

    def test_concurrent_requests_succeed(self, client):
        """Test that multiple concurrent requests all succeed."""
        import concurrent.futures

        def make_request():
            return client.post("/api/v1/identity/authenticate")

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        assert len(results) == 10
        for response in results:
            assert response.status_code == 200
            assert response.json()["status"] == "authenticated"
