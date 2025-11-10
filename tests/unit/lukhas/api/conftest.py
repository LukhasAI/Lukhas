"""Pytest fixtures for API tests."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from lukhas.api.features import router as features_router
from lukhas.features.flags_service import FeatureFlagsService, FeatureFlag, FlagType

@pytest.fixture(scope="module")
def mock_flags():
    """Provides a dictionary of mock feature flags for testing."""
    return {
        "test_boolean_flag_on": FeatureFlag("test_boolean_flag_on", {
            "type": "boolean",
            "enabled": True,
            "description": "A test boolean flag that is on.",
            "owner": "test-owner",
            "created_at": "2025-01-01",
            "jira_ticket": "TEST-1",
        }),
        "test_boolean_flag_off": FeatureFlag("test_boolean_flag_off", {
            "type": "boolean",
            "enabled": False,
            "description": "A test boolean flag that is off.",
            "owner": "test-owner",
            "created_at": "2025-01-01",
            "jira_ticket": "TEST-2",
        }),
        "test_percentage_flag": FeatureFlag("test_percentage_flag", {
            "type": "percentage",
            "enabled": True,
            "percentage": 50,
            "description": "A 50% rollout flag.",
            "owner": "test-owner",
            "created_at": "2025-01-01",
            "jira_ticket": "TEST-3",
        }),
         "test_user_targeting_flag": FeatureFlag("test_user_targeting_flag", {
            "type": "user_targeting",
            "enabled": True,
            "allowed_domains": ["lukhas.ai"],
            "description": "A user targeting flag.",
            "owner": "test-owner",
            "created_at": "2025-01-01",
            "jira_ticket": "TEST-4",
        }),
    }

@pytest.fixture
def mock_feature_flags_service(mock_flags):
    """Provides a mock FeatureFlagsService."""
    mock_service = MagicMock(spec=FeatureFlagsService)
    mock_service.get_all_flags.return_value = mock_flags

    def get_flag_side_effect(flag_name):
        return mock_flags.get(flag_name)

    mock_service.get_flag.side_effect = get_flag_side_effect

    # Default behavior for is_enabled can be simple
    mock_service.is_enabled.side_effect = lambda name, ctx: mock_flags.get(name).enabled if mock_flags.get(name) else False

    return mock_service

@pytest.fixture
def app(mock_feature_flags_service):
    """Creates a FastAPI app instance for testing."""
    app = FastAPI()
    app.include_router(features_router)
    # Use dependency overrides to inject the mock service
    from lukhas.api.features import get_feature_flags_service
    app.dependency_overrides[get_feature_flags_service] = lambda: mock_feature_flags_service
    return app

@pytest.fixture
def client(app):
    """Provides a TestClient for making requests to the app."""
    return TestClient(app)
