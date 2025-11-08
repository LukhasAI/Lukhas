"""
Comprehensive tests for feature flags API.

Tests FastAPI endpoints, authentication, rate limiting, and error handling.
"""

import tempfile
from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from lukhas.api.features import router
from lukhas.features.flags_service import FeatureFlagsService

# Create test client
client = TestClient(router)


@pytest.fixture
def temp_config():
    """Create temporary config file for testing."""
    config = {
        "version": "1.0",
        "flags": {
            "test_boolean": {
                "type": "boolean",
                "enabled": True,
                "description": "Test boolean flag",
                "owner": "test@lukhas.ai",
                "created_at": "2025-11-08",
                "jira_ticket": "TEST-1",
            },
            "test_percentage": {
                "type": "percentage",
                "enabled": True,
                "percentage": 50,
                "description": "Test percentage flag",
                "owner": "test@lukhas.ai",
                "created_at": "2025-11-08",
                "jira_ticket": "TEST-2",
            },
            "test_disabled": {
                "type": "boolean",
                "enabled": False,
                "description": "Test disabled flag",
                "owner": "test@lukhas.ai",
                "created_at": "2025-11-08",
                "jira_ticket": "TEST-3",
            },
        },
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(config, f)
        temp_path = f.name

    # Create service with temp config
    service = FeatureFlagsService(config_path=temp_path, cache_ttl=0)

    # Inject service for testing
    from lukhas.api import features as features_module
    original_service = features_module.get_service
    features_module.get_service = lambda: service

    yield temp_path, service

    # Cleanup
    features_module.get_service = original_service
    Path(temp_path).unlink(missing_ok=True)


class TestAuthentication:
    """Test API authentication."""

    def test_no_api_key(self, temp_config):
        """Test request without API key fails."""
        response = client.get("/api/features/")

        assert response.status_code == 401
        assert "Authentication required" in response.json()["detail"]

    def test_with_api_key(self, temp_config):
        """Test request with API key but not admin."""
        response = client.get(
            "/api/features/test_boolean",
            headers={"X-API-Key": "test_key_12345678"}
        )

        # Should work for non-admin endpoints
        assert response.status_code == 200

    def test_admin_only_endpoint_without_admin(self, temp_config):
        """Test admin endpoint without admin key."""
        response = client.get(
            "/api/features/",
            headers={"X-API-Key": "test_key_12345678"}
        )

        assert response.status_code == 403
        assert "Admin access required" in response.json()["detail"]

    def test_admin_endpoint_with_admin_key(self, temp_config):
        """Test admin endpoint with admin key."""
        response = client.get(
            "/api/features/",
            headers={"X-API-Key": "admin_test_key"}
        )

        assert response.status_code == 200


class TestListFlagsEndpoint:
    """Test GET /api/features endpoint."""

    def test_list_flags_success(self, temp_config):
        """Test listing all flags."""
        response = client.get(
            "/api/features/",
            headers={"X-API-Key": "admin_test_key"}
        )

        assert response.status_code == 200

        data = response.json()
        assert "flags" in data
        assert "total" in data
        assert data["total"] == 3

        # Check flag structure
        flags = data["flags"]
        assert len(flags) == 3

        flag_names = [f["name"] for f in flags]
        assert "test_boolean" in flag_names
        assert "test_percentage" in flag_names
        assert "test_disabled" in flag_names

    def test_list_flags_requires_admin(self, temp_config):
        """Test listing flags requires admin."""
        response = client.get(
            "/api/features/",
            headers={"X-API-Key": "regular_user"}
        )

        assert response.status_code == 403


class TestGetFlagEndpoint:
    """Test GET /api/features/{flag_name} endpoint."""

    def test_get_flag_success(self, temp_config):
        """Test getting a flag."""
        response = client.get(
            "/api/features/test_boolean",
            headers={"X-API-Key": "test_key_12345678"}
        )

        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "test_boolean"
        assert data["enabled"] is True
        assert data["flag_type"] == "boolean"
        assert data["description"] == "Test boolean flag"

    def test_get_flag_not_found(self, temp_config):
        """Test getting non-existent flag."""
        response = client.get(
            "/api/features/nonexistent",
            headers={"X-API-Key": "test_key_12345678"}
        )

        assert response.status_code == 404
        assert "Flag not found" in response.json()["detail"]

    def test_get_flag_requires_auth(self, temp_config):
        """Test getting flag requires authentication."""
        response = client.get("/api/features/test_boolean")

        assert response.status_code == 401


class TestEvaluateFlagEndpoint:
    """Test POST /api/features/{flag_name}/evaluate endpoint."""

    def test_evaluate_flag_success(self, temp_config):
        """Test evaluating a flag."""
        response = client.post(
            "/api/features/test_boolean/evaluate",
            headers={"X-API-Key": "test_key_12345678"},
            json={
                "user_id": "user-123",
                "email": "test@example.com",
                "environment": "prod"
            }
        )

        assert response.status_code == 200

        data = response.json()
        assert data["flag_name"] == "test_boolean"
        assert data["enabled"] is True
        assert data["flag_type"] == "boolean"

    def test_evaluate_flag_disabled(self, temp_config):
        """Test evaluating disabled flag."""
        response = client.post(
            "/api/features/test_disabled/evaluate",
            headers={"X-API-Key": "test_key_12345678"},
            json={}
        )

        assert response.status_code == 200

        data = response.json()
        assert data["enabled"] is False

    def test_evaluate_flag_percentage(self, temp_config):
        """Test evaluating percentage flag."""
        response = client.post(
            "/api/features/test_percentage/evaluate",
            headers={"X-API-Key": "test_key_12345678"},
            json={"user_id": "user-123"}
        )

        assert response.status_code == 200

        data = response.json()
        assert data["flag_name"] == "test_percentage"
        assert isinstance(data["enabled"], bool)

    def test_evaluate_flag_not_found(self, temp_config):
        """Test evaluating non-existent flag."""
        response = client.post(
            "/api/features/nonexistent/evaluate",
            headers={"X-API-Key": "test_key_12345678"},
            json={}
        )

        assert response.status_code == 404

    def test_evaluate_flag_requires_auth(self, temp_config):
        """Test evaluation requires authentication."""
        response = client.post(
            "/api/features/test_boolean/evaluate",
            json={}
        )

        assert response.status_code == 401


class TestUpdateFlagEndpoint:
    """Test PATCH /api/features/{flag_name} endpoint."""

    def test_update_flag_enabled(self, temp_config):
        """Test updating flag enabled state."""
        response = client.patch(
            "/api/features/test_boolean",
            headers={"X-API-Key": "admin_test_key"},
            json={"enabled": False}
        )

        assert response.status_code == 200

        data = response.json()
        assert data["enabled"] is False

    def test_update_flag_percentage(self, temp_config):
        """Test updating flag percentage."""
        response = client.patch(
            "/api/features/test_percentage",
            headers={"X-API-Key": "admin_test_key"},
            json={"percentage": 75}
        )

        assert response.status_code == 200

        data = response.json()
        # Note: This updates the in-memory object, not the YAML
        assert data["name"] == "test_percentage"

    def test_update_flag_invalid_percentage_type(self, temp_config):
        """Test updating percentage on non-percentage flag."""
        response = client.patch(
            "/api/features/test_boolean",
            headers={"X-API-Key": "admin_test_key"},
            json={"percentage": 50}
        )

        assert response.status_code == 400
        assert "Cannot set percentage" in response.json()["detail"]

    def test_update_flag_requires_admin(self, temp_config):
        """Test update requires admin."""
        response = client.patch(
            "/api/features/test_boolean",
            headers={"X-API-Key": "regular_user"},
            json={"enabled": False}
        )

        assert response.status_code == 403

    def test_update_flag_not_found(self, temp_config):
        """Test updating non-existent flag."""
        response = client.patch(
            "/api/features/nonexistent",
            headers={"X-API-Key": "admin_test_key"},
            json={"enabled": False}
        )

        assert response.status_code == 404


class TestReloadFlagEndpoint:
    """Test POST /api/features/{flag_name}/reload endpoint."""

    def test_reload_flag_success(self, temp_config):
        """Test reloading flag."""
        response = client.post(
            "/api/features/test_boolean/reload",
            headers={"X-API-Key": "admin_test_key"}
        )

        assert response.status_code == 200
        assert "reloaded successfully" in response.json()["message"]

    def test_reload_flag_requires_admin(self, temp_config):
        """Test reload requires admin."""
        response = client.post(
            "/api/features/test_boolean/reload",
            headers={"X-API-Key": "regular_user"}
        )

        assert response.status_code == 403

    def test_reload_flag_not_found(self, temp_config):
        """Test reloading non-existent flag."""
        response = client.post(
            "/api/features/nonexistent/reload",
            headers={"X-API-Key": "admin_test_key"}
        )

        assert response.status_code == 404


class TestRateLimiting:
    """Test rate limiting."""

    def test_rate_limit_enforcement(self, temp_config):
        """Test rate limiting is enforced."""
        # Make many requests rapidly
        api_key = "test_rate_limit"
        success_count = 0
        rate_limited_count = 0

        for i in range(110):  # More than limit of 100
            response = client.post(
                "/api/features/test_boolean/evaluate",
                headers={"X-API-Key": api_key},
                json={}
            )

            if response.status_code == 200:
                success_count += 1
            elif response.status_code == 429:
                rate_limited_count += 1

        # Should have rate limited some requests
        assert rate_limited_count > 0
        assert success_count <= 100
