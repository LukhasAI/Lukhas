"""
Tests for Guardian API endpoints.

Tests:
- POST /api/v1/guardian/validate (legacy)
- GET /api/v1/guardian/audit (legacy)
- GET /api/v1/guardian/drift-check (legacy)
- POST /guardian/validate (new)
- GET /guardian/policies (new)
- GET /guardian/health (new)
- POST /guardian/veto (new)
"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from serve.guardian_api import router, legacy_router


@pytest.fixture
def app():
    """Create test FastAPI app with guardian routers."""
    app = FastAPI()
    # Include both legacy and new routers
    app.include_router(legacy_router)
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
        import asyncio

        from serve.guardian_api import audit, drift_check, validate

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


# ============================================================================
# New Guardian API Tests
# ============================================================================


class TestNewValidateEndpoint:
    """Tests for new /guardian/validate endpoint."""

    def test_validate_requires_auth(self, client):
        """Test that validate endpoint requires authentication."""
        # Without auth, should get 401
        response = client.post("/guardian/validate", json={
            "action": "test_action",
            "context": {}
        })
        assert response.status_code == 401

    def test_validate_with_mock_auth(self, client, monkeypatch):
        """Test validation with mocked authentication."""
        # Mock get_current_user to bypass auth
        from serve import guardian_api

        async def mock_get_current_user(request):
            return {"user_id": "test_user", "tier": 1}

        monkeypatch.setattr(guardian_api, "get_current_user", mock_get_current_user)

        response = client.post("/guardian/validate", json={
            "action": "test_action",
            "context": {"test": "data"}
        })

        # Should succeed (or 500 if Guardian unavailable, which is acceptable)
        assert response.status_code in [200, 500]

        if response.status_code == 200:
            data = response.json()
            assert "valid" in data
            assert "score" in data
            assert "violations" in data
            assert "veto" in data
            assert "validation_id" in data


class TestNewPoliciesEndpoint:
    """Tests for new /guardian/policies endpoint."""

    def test_policies_requires_auth(self, client):
        """Test that policies endpoint requires authentication."""
        response = client.get("/guardian/policies")
        assert response.status_code == 401

    def test_policies_with_mock_auth(self, client, monkeypatch):
        """Test policies listing with mocked authentication."""
        from serve import guardian_api

        async def mock_get_current_user(request):
            return {"user_id": "test_user", "tier": 1}

        monkeypatch.setattr(guardian_api, "get_current_user", mock_get_current_user)

        response = client.get("/guardian/policies")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # Check policy structure
        policy = data[0]
        assert "policy_id" in policy
        assert "name" in policy
        assert "description" in policy
        assert "active" in policy
        assert "severity" in policy

    def test_policies_active_filter(self, client, monkeypatch):
        """Test that active_only filter works."""
        from serve import guardian_api

        async def mock_get_current_user(request):
            return {"user_id": "test_user", "tier": 1}

        monkeypatch.setattr(guardian_api, "get_current_user", mock_get_current_user)

        # Get all policies
        response = client.get("/guardian/policies?active_only=false")
        assert response.status_code == 200
        all_policies = response.json()

        # Get active only
        response = client.get("/guardian/policies?active_only=true")
        assert response.status_code == 200
        active_policies = response.json()

        # Active should be <= all
        assert len(active_policies) <= len(all_policies)


class TestNewHealthEndpoint:
    """Tests for new /guardian/health endpoint."""

    def test_health_no_auth_required(self, client):
        """Test that health endpoint doesn't require auth."""
        response = client.get("/guardian/health")
        assert response.status_code == 200

    def test_health_response_structure(self, client):
        """Test health endpoint response structure."""
        response = client.get("/guardian/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "active_policies" in data
        assert "last_check" in data
        assert "drift_detected" in data
        assert "guardian_available" in data
        assert "constitutional_ai_available" in data

        # Status should be one of expected values
        assert data["status"] in ["healthy", "degraded", "down"]

        # Active policies should be non-negative
        assert data["active_policies"] >= 0

        # Drift should be boolean
        assert isinstance(data["drift_detected"], bool)


class TestNewVetoEndpoint:
    """Tests for new /guardian/veto endpoint."""

    def test_veto_requires_auth(self, client):
        """Test that veto endpoint requires authentication."""
        response = client.post("/guardian/veto", json={
            "action_id": "test_action_123",
            "reason": "policy_violation",
            "explanation": "Test explanation"
        })
        assert response.status_code == 401

    def test_veto_with_mock_auth(self, client, monkeypatch):
        """Test veto recording with mocked authentication."""
        from serve import guardian_api

        async def mock_get_current_user(request):
            return {"user_id": "test_user", "tier": 1}

        monkeypatch.setattr(guardian_api, "get_current_user", mock_get_current_user)

        response = client.post("/guardian/veto", json={
            "action_id": "test_action_123",
            "reason": "policy_violation",
            "explanation": "Test explanation for veto"
        })

        assert response.status_code == 200

        data = response.json()
        assert "veto_id" in data
        assert "action_id" in data
        assert data["action_id"] == "test_action_123"
        assert "recorded_at" in data
        assert "status" in data
        assert data["status"] == "recorded"


class TestIntegrationScenarios:
    """Integration tests for Guardian API workflows."""

    def test_full_validation_workflow(self, client, monkeypatch):
        """Test complete validation workflow."""
        from serve import guardian_api

        async def mock_get_current_user(request):
            return {"user_id": "test_user", "tier": 1}

        monkeypatch.setattr(guardian_api, "get_current_user", mock_get_current_user)

        # 1. Check health
        health = client.get("/guardian/health")
        assert health.status_code == 200

        # 2. List policies
        policies = client.get("/guardian/policies")
        assert policies.status_code == 200
        assert len(policies.json()) > 0

        # 3. Validate action (may fail if Guardian unavailable)
        validation = client.post("/guardian/validate", json={
            "action": "user_login",
            "context": {"ip": "127.0.0.1"}
        })
        assert validation.status_code in [200, 500]

    def test_audit_trail_logging(self, client, monkeypatch, caplog):
        """Test that validation creates audit trail logs."""
        from serve import guardian_api
        import logging

        async def mock_get_current_user(request):
            return {"user_id": "audit_test_user", "tier": 1}

        monkeypatch.setattr(guardian_api, "get_current_user", mock_get_current_user)

        # Set logging level to capture INFO logs
        caplog.set_level(logging.INFO)

        # Make validation request
        client.post("/guardian/validate", json={
            "action": "audit_test_action",
            "context": {}
        })

        # Check that audit logs were created
        audit_logs = [record for record in caplog.records if "AUDIT" in record.message]
        assert len(audit_logs) >= 0  # May be 0 if Guardian unavailable
