"""
Tests for Guardian API endpoints.

Tests:
- POST /api/v1/guardian/validate
- GET /api/v1/guardian/audit
- GET /api/v1/guardian/drift-check
"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from serve.guardian_api import router


@pytest.fixture
def app():
    """Create test FastAPI app with guardian router."""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


class TestValidate:
    """Tests for /api/v1/guardian/validate endpoint."""

    def test_validate_success(self, client):
        """Test successful action validation."""
        response = client.post("/api/v1/guardian/validate")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "validated"
        assert "drift_score" in data

    def test_validate_drift_score_is_numeric(self, client):
        """Test drift score is a number."""
        response = client.post("/api/v1/guardian/validate")

        data = response.json()
        assert isinstance(data["drift_score"], (int, float))
        assert data["drift_score"] == 0.05

    def test_validate_response_structure(self, client):
        """Test validation response has correct structure."""
        response = client.post("/api/v1/guardian/validate")

        data = response.json()
        assert "status" in data
        assert "drift_score" in data
        assert len(data) == 2

    def test_validate_method_post_only(self, client):
        """Test that GET is not allowed on validate endpoint."""
        response = client.get("/api/v1/guardian/validate")
        assert response.status_code == 405  # Method Not Allowed


class TestAudit:
    """Tests for /api/v1/guardian/audit endpoint."""

    def test_audit_success(self, client):
        """Test successful audit log retrieval."""
        response = client.get("/api/v1/guardian/audit")

        assert response.status_code == 200
        data = response.json()
        assert "audit_log_entries" in data
        assert "last_audit" in data

    def test_audit_log_entries_is_numeric(self, client):
        """Test audit_log_entries is a number."""
        response = client.get("/api/v1/guardian/audit")

        data = response.json()
        assert isinstance(data["audit_log_entries"], int)
        assert data["audit_log_entries"] == 100

    def test_audit_timestamp_format(self, client):
        """Test last_audit timestamp is in ISO format."""
        response = client.get("/api/v1/guardian/audit")

        data = response.json()
        timestamp = data["last_audit"]
        assert isinstance(timestamp, str)
        # Should be ISO 8601 format
        assert "T" in timestamp
        assert timestamp.endswith("Z")

    def test_audit_method_get_only(self, client):
        """Test that POST is not allowed on audit endpoint."""
        response = client.post("/api/v1/guardian/audit")
        assert response.status_code == 405  # Method Not Allowed


class TestDriftCheck:
    """Tests for /api/v1/guardian/drift-check endpoint."""

    def test_drift_check_success(self, client):
        """Test successful drift check."""
        response = client.get("/api/v1/guardian/drift-check")

        assert response.status_code == 200
        data = response.json()
        assert data["drift_status"] == "normal"
        assert "drift_score" in data

    def test_drift_check_score_is_numeric(self, client):
        """Test drift_score is a number."""
        response = client.get("/api/v1/guardian/drift-check")

        data = response.json()
        assert isinstance(data["drift_score"], (int, float))
        assert data["drift_score"] == 0.02

    def test_drift_check_response_structure(self, client):
        """Test drift check response has correct structure."""
        response = client.get("/api/v1/guardian/drift-check")

        data = response.json()
        assert "drift_status" in data
        assert "drift_score" in data
        assert len(data) == 2

    def test_drift_check_method_get_only(self, client):
        """Test that POST is not allowed on drift-check endpoint."""
        response = client.post("/api/v1/guardian/drift-check")
        assert response.status_code == 405  # Method Not Allowed


class TestDriftScoreConsistency:
    """Tests for drift score consistency across endpoints."""

    def test_drift_scores_are_reasonable(self, client):
        """Test that drift scores are in reasonable ranges."""
        # Validate endpoint
        response = client.post("/api/v1/guardian/validate")
        validate_score = response.json()["drift_score"]
        assert 0.0 <= validate_score <= 1.0

        # Drift check endpoint
        response = client.get("/api/v1/guardian/drift-check")
        drift_score = response.json()["drift_score"]
        assert 0.0 <= drift_score <= 1.0


class TestResponseTimes:
    """Tests for response time characteristics."""

    @pytest.mark.asyncio
    async def test_endpoints_are_async(self):
        """Verify all endpoints are async coroutines."""
        from serve.guardian_api import validate, audit, drift_check
        import asyncio

        assert asyncio.iscoroutinefunction(validate)
        assert asyncio.iscoroutinefunction(audit)
        assert asyncio.iscoroutinefunction(drift_check)

    def test_all_endpoints_respond_quickly(self, client):
        """Test that all endpoints respond within reasonable time."""
        import time

        # Validate
        start = time.time()
        response = client.post("/api/v1/guardian/validate")
        elapsed = time.time() - start
        assert response.status_code == 200
        assert elapsed < 0.1  # Should be well under 100ms

        # Audit (has 6ms sleep, so allow more time)
        start = time.time()
        response = client.get("/api/v1/guardian/audit")
        elapsed = time.time() - start
        assert response.status_code == 200
        assert elapsed < 0.1

        # Drift check
        start = time.time()
        response = client.get("/api/v1/guardian/drift-check")
        elapsed = time.time() - start
        assert response.status_code == 200
        assert elapsed < 0.1


class TestOpenAPISpec:
    """Tests for OpenAPI documentation."""

    def test_endpoints_have_openapi_metadata(self, app):
        """Test that all endpoints have OpenAPI metadata."""
        openapi = app.openapi()

        # Check validate
        assert "/api/v1/guardian/validate" in openapi["paths"]
        validate_spec = openapi["paths"]["/api/v1/guardian/validate"]["post"]
        assert "summary" in validate_spec
        assert validate_spec["summary"] == "Validate Action"
        assert "200" in validate_spec["responses"]

        # Check audit
        assert "/api/v1/guardian/audit" in openapi["paths"]
        audit_spec = openapi["paths"]["/api/v1/guardian/audit"]["get"]
        assert "summary" in audit_spec
        assert audit_spec["summary"] == "Get Audit Log"

        # Check drift-check
        assert "/api/v1/guardian/drift-check" in openapi["paths"]
        drift_spec = openapi["paths"]["/api/v1/guardian/drift-check"]["get"]
        assert "summary" in drift_spec
        assert drift_spec["summary"] == "Check for Policy Drift"


class TestPolicyEnforcement:
    """Tests for guardian policy enforcement behavior."""

    def test_validation_always_returns_validated(self, client):
        """Test that validation currently always returns validated status."""
        # Make multiple requests
        for _ in range(5):
            response = client.post("/api/v1/guardian/validate")
            assert response.status_code == 200
            assert response.json()["status"] == "validated"

    def test_drift_status_always_normal(self, client):
        """Test that drift status currently always returns normal."""
        # Make multiple requests
        for _ in range(5):
            response = client.get("/api/v1/guardian/drift-check")
            assert response.status_code == 200
            assert response.json()["drift_status"] == "normal"


class TestConcurrentRequests:
    """Tests for concurrent request handling."""

    def test_concurrent_validation_requests(self, client):
        """Test that multiple concurrent validation requests succeed."""
        import concurrent.futures

        def make_request():
            return client.post("/api/v1/guardian/validate")

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        assert len(results) == 10
        for response in results:
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "validated"
            assert "drift_score" in data
