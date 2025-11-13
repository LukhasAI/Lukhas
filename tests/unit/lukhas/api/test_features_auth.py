# Make sure the app can find the auth_helpers module
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

# Add the project root to the path
# This is a bit of a hack for the test environment, in a real project you'd have a proper package structure
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from lukhas.api.auth_helpers import (
    FEATURE_ACCESS,
    USERS_DATA,
    get_current_user,
    require_feature_access,
)
from lukhas.api.features import router as features_router

# --- Test App Setup ---
app = FastAPI()
app.include_router(features_router)

client = TestClient(app)


# --- Mocks ---
@pytest.fixture
def mock_flags_service():
    """Mock the feature flags service."""
    mock_service = MagicMock()
    boolean_flag_type = MagicMock()
    boolean_flag_type.value = "boolean"

    mock_service.get_all_flags.return_value = {
        "feature1": MagicMock(
            enabled=True,
            flag_type=boolean_flag_type,
            description="Test flag 1",
            owner="test",
            created_at="2023-01-01",
            jira_ticket="T-1",
            percentage=100,
        )
    }
    mock_service.get_flag.return_value = MagicMock(
        enabled=True,
        flag_type=boolean_flag_type,
        description="Test flag 1",
        owner="test",
        created_at="2023-01-01",
        jira_ticket="T-1",
        percentage=100,
    )
    mock_service.is_enabled.return_value = True
    return mock_service


@pytest.fixture(autouse=True)
def override_dependencies(mock_flags_service):
    """Override FastAPI dependencies for all tests."""
    from lukhas.api.features import get_feature_flags_service

    app.dependency_overrides[get_feature_flags_service] = lambda: mock_flags_service
    yield
    app.dependency_overrides = {}


# --- Test Data ---
ADMIN_API_KEY = USERS_DATA["admin_user_001"]["api_key"]
PRO_API_KEY = USERS_DATA["user_pro_456"]["api_key"]
FREE_API_KEY = USERS_DATA["user_free_123"]["api_key"]


# --- Endpoint Tests ---

# Test GET /api/features (list_flags)
def test_list_flags_as_admin_success():
    response = client.get("/api/features/", headers={"X-API-Key": ADMIN_API_KEY})
    assert response.status_code == 200
    assert "flags" in response.json()
    assert response.json()["total"] > 0


def test_list_flags_as_pro_user_forbidden():
    response = client.get("/api/features/", headers={"X-API-Key": PRO_API_KEY})
    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient permissions"


def test_list_flags_unauthenticated_fails():
    response = client.get("/api/features/")
    assert response.status_code == 401
    assert "Invalid or missing API key" in response.json()["detail"]


# Test GET /api/features/{flag_name} (get_flag)
def test_get_flag_authenticated_success():
    response = client.get("/api/features/feature1", headers={"X-API-Key": FREE_API_KEY})
    assert response.status_code == 200
    assert response.json()["name"] == "feature1"


def test_get_flag_unauthenticated_fails():
    response = client.get("/api/features/feature1")
    assert response.status_code == 401
    assert "Invalid or missing API key" in response.json()["detail"]


def test_get_flag_not_found():
    # Configure the mock to return None for a specific flag
    mock_service = app.dependency_overrides.get(
        next(iter(app.dependency_overrides))
    )()
    mock_service.get_flag.return_value = None
    response = client.get("/api/features/non_existent_flag", headers={"X-API-Key": FREE_API_KEY})
    assert response.status_code == 404
    assert "Flag not found" in response.json()["detail"]


# Test POST /api/features/{flag_name}/evaluate (evaluate_flag)
def test_evaluate_flag_authenticated_success():
    response = client.post(
        "/api/features/feature1/evaluate",
        headers={"X-API-Key": PRO_API_KEY},
        json={"user_id": "test_user"},
    )
    assert response.status_code == 200
    assert response.json()["enabled"] is True


def test_evaluate_flag_unauthenticated_fails():
    response = client.post("/api/features/feature1/evaluate", json={"user_id": "test_user"})
    assert response.status_code == 401
    assert "Invalid or missing API key" in response.json()["detail"]


# Test PATCH /api/features/{flag_name} (update_flag)
def test_update_flag_as_admin_success():
    response = client.patch(
        "/api/features/feature1",
        headers={"X-API-Key": ADMIN_API_KEY},
        json={"enabled": False},
    )
    assert response.status_code == 200
    # In a real test, you'd check the mock was called with the correct data
    # For now, we just check success


def test_update_flag_as_free_user_forbidden():
    response = client.patch(
        "/api/features/feature1",
        headers={"X-API-Key": FREE_API_KEY},
        json={"enabled": False},
    )
    assert response.status_code == 403
    assert "Insufficient permissions" in response.json()["detail"]


def test_update_flag_unauthenticated_fails():
    response = client.patch("/api/features/feature1", json={"enabled": False})
    assert response.status_code == 401
    assert "Invalid or missing API key" in response.json()["detail"]


# Test POST /api/features/{flag_name}/reload (reload_flag)
def test_reload_flag_as_admin_success():
    response = client.post("/api/features/feature1/reload", headers={"X-API-Key": ADMIN_API_KEY})
    assert response.status_code == 200
    assert "reloaded successfully" in response.json()["message"]


def test_reload_flag_as_pro_user_forbidden():
    response = client.post("/api/features/feature1/reload", headers={"X-API-Key": PRO_API_KEY})
    assert response.status_code == 403
    assert "Insufficient permissions" in response.json()["detail"]


def test_reload_flag_unauthenticated_fails():
    response = client.post("/api/features/feature1/reload")
    assert response.status_code == 401
    assert "Invalid or missing API key" in response.json()["detail"]
