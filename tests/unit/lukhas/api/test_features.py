"""
Comprehensive test suite for Feature Flags API endpoints.

Tests FastAPI routes for feature flag management, evaluation, authentication,
authorization, rate limiting, and error handling.

Coverage target: 85%+
"""

import time
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from lukhas.api.features import (
    FlagEvaluationRequest,
    FlagEvaluationResponse,
    FlagInfo,
    FlagListResponse,
    FlagUpdateRequest,
    _rate_limit_store,
    check_rate_limit,
    get_current_user,
    get_feature_flags_service,
    require_admin,
    router,
)
from lukhas.features.flags_service import FeatureFlag, FeatureFlagsService, FlagType


# Create test app
from fastapi import FastAPI

app = FastAPI()
app.include_router(router)
client = TestClient(app)


# Test Fixtures


@pytest.fixture
def mock_service():
    """Create a mock FeatureFlagsService."""
    service = Mock(spec=FeatureFlagsService)

    # Create test flags
    test_flag = Mock(spec=FeatureFlag)
    test_flag.enabled = True
    test_flag.flag_type = FlagType.BOOLEAN
    test_flag.description = "Test flag"
    test_flag.owner = "test-team"
    test_flag.created_at = "2024-01-01T00:00:00Z"
    test_flag.jira_ticket = "TEST-123"
    test_flag.percentage = 50

    service.get_flag.return_value = test_flag
    service.get_all_flags.return_value = {
        "test_flag": test_flag,
    }
    service.is_enabled.return_value = True

    return service


@pytest.fixture
def mock_service_dependency(mock_service):
    """Override service dependency."""
    app.dependency_overrides[get_feature_flags_service] = lambda: mock_service
    yield mock_service
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user():
    """Override to return admin user."""
    def _get_admin():
        return "admin_test_user"

    app.dependency_overrides[get_current_user] = _get_admin
    app.dependency_overrides[require_admin] = _get_admin
    yield
    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides.pop(require_admin, None)


@pytest.fixture
def regular_user():
    """Override to return regular user."""
    def _get_user():
        return "user_test_user"

    app.dependency_overrides[get_current_user] = _get_user
    yield
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def admin_headers():
    """Create headers for admin user."""
    return {"X-API-Key": "admin_test_key"}


@pytest.fixture
def user_headers():
    """Create headers for regular user."""
    return {"X-API-Key": "user_test_key"}


@pytest.fixture(autouse=True)
def clear_rate_limit_store():
    """Clear rate limit store before each test."""
    _rate_limit_store.clear()
    yield
    _rate_limit_store.clear()


# Test Helper Functions


class TestCheckRateLimit:
    """Tests for check_rate_limit function."""

    def test_first_request_allowed(self):
        """Test first request is allowed."""
        assert check_rate_limit("user1") is True

    def test_requests_under_limit(self):
        """Test requests under limit are allowed."""
        for i in range(50):
            assert check_rate_limit("user1") is True

    def test_requests_at_limit(self):
        """Test requests at limit threshold."""
        # Make 100 requests (the limit)
        for i in range(100):
            check_rate_limit("user1")

        # 101st request should be blocked
        assert check_rate_limit("user1") is False

    def test_requests_over_limit(self):
        """Test requests over limit are blocked."""
        # Exceed limit
        for i in range(101):
            check_rate_limit("user1")

        assert check_rate_limit("user1") is False

    def test_different_users_separate_limits(self):
        """Test different users have separate rate limits."""
        # User1 exceeds limit
        for i in range(101):
            check_rate_limit("user1")

        # User2 should still be allowed
        assert check_rate_limit("user2") is True

    def test_old_requests_expire(self):
        """Test old requests are removed from window."""
        user_id = "test_user"

        # Add old request (outside window)
        old_time = time.time() - 65  # 65 seconds ago
        _rate_limit_store[user_id] = [old_time]

        # New request should be allowed
        assert check_rate_limit(user_id) is True

        # Old request should be removed
        assert old_time not in _rate_limit_store[user_id]


class TestGetCurrentUser:
    """Tests for get_current_user dependency."""

    def test_with_api_key(self):
        """Test authentication with API key."""
        from fastapi import Request

        request = Mock(spec=Request)
        request.headers.get.return_value = "test_key_123"

        user_id = get_current_user(request)

        assert user_id == "user_test_key"

    def test_without_api_key(self):
        """Test authentication without API key raises error."""
        from fastapi import Request, HTTPException

        request = Mock(spec=Request)
        request.headers.get.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(request)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Authentication required" in exc_info.value.detail


class TestRequireAdmin:
    """Tests for require_admin dependency."""

    def test_admin_user_allowed(self):
        """Test admin user is allowed."""
        user_id = require_admin("admin_test_user")
        assert user_id == "admin_test_user"

    def test_non_admin_user_blocked(self):
        """Test non-admin user is blocked."""
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            require_admin("user_test_user")

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Admin access required" in exc_info.value.detail


# Test API Endpoints


class TestListFlags:
    """Tests for GET /api/features/ endpoint."""

    def test_list_flags_success(self, mock_service_dependency, admin_user, admin_headers):
        """Test listing all flags succeeds for admin."""
        response = client.get("/api/features/", headers=admin_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "flags" in data
        assert "total" in data
        assert data["total"] == 1
        assert len(data["flags"]) == 1
        assert data["flags"][0]["name"] == "test_flag"

    def test_list_flags_without_auth(self):
        """Test listing flags without auth fails."""
        response = client.get("/api/features/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_flags_non_admin(self, mock_service_dependency, regular_user, user_headers):
        """Test listing flags as non-admin fails."""
        response = client.get("/api/features/", headers=user_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_flags_empty(self, mock_service_dependency, admin_user, admin_headers):
        """Test listing flags when none exist."""
        mock_service_dependency.get_all_flags.return_value = {}

        response = client.get("/api/features/", headers=admin_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 0
        assert data["flags"] == []

    def test_list_flags_service_error(self, mock_service_dependency, admin_user, admin_headers):
        """Test listing flags handles service errors."""
        mock_service_dependency.get_all_flags.side_effect = Exception("Database error")

        response = client.get("/api/features/", headers=admin_headers)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


class TestGetFlag:
    """Tests for GET /api/features/{flag_name} endpoint."""

    def test_get_flag_success(self, mock_service_dependency, user_headers):
        """Test getting flag details succeeds."""
        response = client.get("/api/features/test_flag", headers=user_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["name"] == "test_flag"
        assert data["enabled"] is True
        assert data["flag_type"] == "boolean"
        assert data["description"] == "Test flag"

    def test_get_flag_not_found(self, mock_service_dependency, user_headers):
        """Test getting non-existent flag returns 404."""
        mock_service_dependency.get_flag.return_value = None

        response = client.get("/api/features/nonexistent", headers=user_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_get_flag_without_auth(self, mock_service_dependency):
        """Test getting flag without auth fails."""
        response = client.get("/api/features/test_flag")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_flag_service_error(self, mock_service_dependency, user_headers):
        """Test getting flag handles service errors."""
        mock_service_dependency.get_flag.side_effect = Exception("Error")

        response = client.get("/api/features/test_flag", headers=user_headers)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


class TestEvaluateFlag:
    """Tests for POST /api/features/{flag_name}/evaluate endpoint."""

    def test_evaluate_flag_success(self, mock_service_dependency, user_headers):
        """Test evaluating flag succeeds."""
        payload = {
            "user_id": "user123",
            "email": "test@example.com",
            "environment": "prod",
        }

        response = client.post(
            "/api/features/test_flag/evaluate",
            json=payload,
            headers=user_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["flag_name"] == "test_flag"
        assert data["enabled"] is True
        assert data["flag_type"] == "boolean"

    def test_evaluate_flag_disabled(self, mock_service_dependency, user_headers):
        """Test evaluating disabled flag."""
        mock_service_dependency.is_enabled.return_value = False

        payload = {"user_id": "user123"}

        response = client.post(
            "/api/features/test_flag/evaluate",
            json=payload,
            headers=user_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["enabled"] is False

    def test_evaluate_flag_empty_context(self, mock_service_dependency, user_headers):
        """Test evaluating flag with empty context."""
        payload = {}

        response = client.post(
            "/api/features/test_flag/evaluate",
            json=payload,
            headers=user_headers,
        )

        assert response.status_code == status.HTTP_200_OK

    def test_evaluate_flag_not_found(self, mock_service_dependency, user_headers):
        """Test evaluating non-existent flag returns 404."""
        mock_service_dependency.get_flag.return_value = None

        payload = {"user_id": "user123"}

        response = client.post(
            "/api/features/nonexistent/evaluate",
            json=payload,
            headers=user_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_evaluate_flag_without_auth(self, mock_service_dependency):
        """Test evaluating flag without auth fails."""
        response = client.post("/api/features/test_flag/evaluate", json={})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_evaluate_flag_rate_limit(self, mock_service_dependency, user_headers):
        """Test rate limiting on flag evaluation."""
        payload = {"user_id": "user123"}

        # Make requests up to limit
        for i in range(100):
            response = client.post(
                "/api/features/test_flag/evaluate",
                json=payload,
                headers=user_headers,
            )
            if i < 99:
                assert response.status_code == status.HTTP_200_OK

        # Next request should be rate limited
        response = client.post(
            "/api/features/test_flag/evaluate",
            json=payload,
            headers=user_headers,
        )

        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "Rate limit exceeded" in response.json()["detail"]

    def test_evaluate_flag_service_error(self, mock_service_dependency, user_headers):
        """Test evaluation handles service errors."""
        mock_service_dependency.is_enabled.side_effect = Exception("Error")

        payload = {"user_id": "user123"}

        response = client.post(
            "/api/features/test_flag/evaluate",
            json=payload,
            headers=user_headers,
        )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_evaluate_flag_calls_service_correctly(self, mock_service_dependency, user_headers):
        """Test evaluation passes context to service correctly."""
        payload = {
            "user_id": "user123",
            "email": "test@example.com",
            "environment": "staging",
        }

        response = client.post(
            "/api/features/test_flag/evaluate",
            json=payload,
            headers=user_headers,
        )

        assert response.status_code == status.HTTP_200_OK

        # Verify service was called with context
        mock_service_dependency.is_enabled.assert_called_once()
        call_args = mock_service_dependency.is_enabled.call_args
        assert call_args[0][0] == "test_flag"  # flag_name
        context = call_args[0][1]  # context
        assert context.user_id == "user123"
        assert context.email == "test@example.com"
        assert context.environment == "staging"


class TestUpdateFlag:
    """Tests for PATCH /api/features/{flag_name} endpoint."""

    def test_update_flag_enable(self, mock_service_dependency, admin_user, admin_headers):
        """Test enabling a flag."""
        payload = {"enabled": True}

        response = client.patch(
            "/api/features/test_flag",
            json=payload,
            headers=admin_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["enabled"] is True

    def test_update_flag_disable(self, mock_service_dependency, admin_user, admin_headers):
        """Test disabling a flag."""
        payload = {"enabled": False}

        response = client.patch(
            "/api/features/test_flag",
            json=payload,
            headers=admin_headers,
        )

        assert response.status_code == status.HTTP_200_OK

        # Verify flag was updated
        flag = mock_service_dependency.get_flag.return_value
        assert flag.enabled is False

    def test_update_flag_percentage(self, mock_service_dependency, admin_user, admin_headers):
        """Test updating percentage rollout."""
        # Set flag type to PERCENTAGE
        flag = mock_service_dependency.get_flag.return_value
        flag.flag_type = FlagType.PERCENTAGE

        payload = {"percentage": 75}

        response = client.patch(
            "/api/features/test_flag",
            json=payload,
            headers=admin_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        assert flag.percentage == 75

    def test_update_flag_percentage_validation(self, mock_service_dependency, admin_user, admin_headers):
        """Test percentage validation (0-100)."""
        flag = mock_service_dependency.get_flag.return_value
        flag.flag_type = FlagType.PERCENTAGE

        # Test invalid values
        for invalid_value in [-1, 101, 200]:
            payload = {"percentage": invalid_value}
            response = client.patch(
                "/api/features/test_flag",
                json=payload,
                headers=admin_headers,
            )
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_flag_percentage_on_boolean_flag(self, mock_service_dependency, admin_user, admin_headers):
        """Test setting percentage on non-percentage flag fails."""
        # Flag is BOOLEAN type
        payload = {"percentage": 50}

        response = client.patch(
            "/api/features/test_flag",
            json=payload,
            headers=admin_headers,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Cannot set percentage" in response.json()["detail"]

    def test_update_flag_not_found(self, mock_service_dependency, admin_user, admin_headers):
        """Test updating non-existent flag returns 404."""
        mock_service_dependency.get_flag.return_value = None

        payload = {"enabled": True}

        response = client.patch(
            "/api/features/nonexistent",
            json=payload,
            headers=admin_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_flag_without_auth(self, mock_service_dependency):
        """Test updating flag without auth fails."""
        payload = {"enabled": True}

        response = client.patch("/api/features/test_flag", json=payload)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_flag_non_admin(self, mock_service_dependency, user_headers):
        """Test updating flag as non-admin fails."""
        payload = {"enabled": True}

        response = client.patch(
            "/api/features/test_flag",
            json=payload,
            headers=user_headers,
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_flag_empty_payload(self, mock_service_dependency, admin_user, admin_headers):
        """Test updating with empty payload."""
        payload = {}

        response = client.patch(
            "/api/features/test_flag",
            json=payload,
            headers=admin_headers,
        )

        # Should succeed but not change anything
        assert response.status_code == status.HTTP_200_OK

    def test_update_flag_service_error(self, mock_service_dependency, admin_user, admin_headers):
        """Test update handles service errors."""
        mock_service_dependency.get_flag.side_effect = Exception("Error")

        payload = {"enabled": True}

        response = client.patch(
            "/api/features/test_flag",
            json=payload,
            headers=admin_headers,
        )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


class TestReloadFlag:
    """Tests for POST /api/features/{flag_name}/reload endpoint."""

    def test_reload_flag_success(self, mock_service_dependency, admin_user, admin_headers):
        """Test reloading flag succeeds."""
        response = client.post("/api/features/test_flag/reload", headers=admin_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "reloaded successfully" in data["message"]

        # Verify service reload was called
        mock_service_dependency.reload.assert_called_once()

    def test_reload_flag_not_found_after_reload(self, mock_service_dependency, admin_user, admin_headers):
        """Test reload fails if flag doesn't exist after reload."""
        mock_service_dependency.get_flag.return_value = None

        response = client.post("/api/features/test_flag/reload", headers=admin_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found after reload" in response.json()["detail"]

    def test_reload_flag_without_auth(self, mock_service_dependency):
        """Test reloading flag without auth fails."""
        response = client.post("/api/features/test_flag/reload")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_reload_flag_non_admin(self, mock_service_dependency, user_headers):
        """Test reloading flag as non-admin fails."""
        response = client.post("/api/features/test_flag/reload", headers=user_headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_reload_flag_service_error(self, mock_service_dependency, admin_user, admin_headers):
        """Test reload handles service errors."""
        mock_service_dependency.reload.side_effect = Exception("Error")

        response = client.post("/api/features/test_flag/reload", headers=admin_headers)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


# Test Request/Response Models


class TestModels:
    """Tests for Pydantic models."""

    def test_flag_evaluation_request_minimal(self):
        """Test FlagEvaluationRequest with minimal data."""
        request = FlagEvaluationRequest()
        assert request.user_id is None
        assert request.email is None
        assert request.environment is None

    def test_flag_evaluation_request_full(self):
        """Test FlagEvaluationRequest with all fields."""
        request = FlagEvaluationRequest(
            user_id="user123",
            email="test@example.com",
            environment="prod",
        )
        assert request.user_id == "user123"
        assert request.email == "test@example.com"
        assert request.environment == "prod"

    def test_flag_evaluation_response(self):
        """Test FlagEvaluationResponse."""
        response = FlagEvaluationResponse(
            flag_name="test_flag",
            enabled=True,
            flag_type="boolean",
        )
        assert response.flag_name == "test_flag"
        assert response.enabled is True
        assert response.flag_type == "boolean"

    def test_flag_info(self):
        """Test FlagInfo model."""
        info = FlagInfo(
            name="test_flag",
            enabled=True,
            flag_type="boolean",
            description="Test",
            owner="team",
            created_at="2024-01-01",
            jira_ticket="TEST-123",
        )
        assert info.name == "test_flag"

    def test_flag_update_request_enable_only(self):
        """Test FlagUpdateRequest with only enabled field."""
        request = FlagUpdateRequest(enabled=True)
        assert request.enabled is True
        assert request.percentage is None

    def test_flag_update_request_percentage_only(self):
        """Test FlagUpdateRequest with only percentage field."""
        request = FlagUpdateRequest(percentage=50)
        assert request.percentage == 50
        assert request.enabled is None

    def test_flag_list_response(self):
        """Test FlagListResponse model."""
        flag_info = FlagInfo(
            name="test",
            enabled=True,
            flag_type="boolean",
            description="Test",
            owner="team",
            created_at="2024-01-01",
            jira_ticket="TEST-123",
        )
        response = FlagListResponse(flags=[flag_info], total=1)
        assert response.total == 1
        assert len(response.flags) == 1


class TestLogging:
    """Tests for audit logging."""

    def test_evaluate_logs_aggregate_only(self, mock_service_dependency, user_headers):
        """Test flag evaluation logs aggregate data only (no PII)."""
        payload = {
            "user_id": "user123",
            "email": "sensitive@example.com",
        }

        with patch("lukhas.api.features.logger") as mock_logger:
            response = client.post(
                "/api/features/test_flag/evaluate",
                json=payload,
                headers=user_headers,
            )

            assert response.status_code == status.HTTP_200_OK

            # Verify logging was called
            assert mock_logger.info.called

            # Check that PII is not in log message
            log_call = mock_logger.info.call_args[0][0]
            assert "user123" not in log_call  # User ID not logged
            assert "sensitive@example.com" not in log_call  # Email not logged

    def test_update_logs_admin_action(self, mock_service_dependency, admin_user, admin_headers):
        """Test flag updates are logged with admin user."""
        payload = {"enabled": True}

        with patch("lukhas.api.features.logger") as mock_logger:
            response = client.patch(
                "/api/features/test_flag",
                json=payload,
                headers=admin_headers,
            )

            assert response.status_code == status.HTTP_200_OK

            # Verify audit log
            assert mock_logger.info.called
            log_call = mock_logger.info.call_args[0][0]
            assert "Flag updated" in log_call
            assert "test_flag" in log_call
