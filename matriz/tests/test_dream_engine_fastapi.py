import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from matriz.consciousness.dream.oneiric.oneiric_core.engine.dream_engine_fastapi import (
    app,
    get_current_user,
    User,
)

client = TestClient(app)


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == "healthy"
    assert json_response["service"] == "LUKHAS Dream Engine API"


# Mock the user for testing
@pytest.fixture
def mock_get_current_user():
    def _mock_user(tier):
        return User(id="testuser", tier=tier)

    return _mock_user


def test_process_dream_success(mock_get_current_user):
    app.dependency_overrides[get_current_user] = lambda: mock_get_current_user(tier=3)
    response = client.post(
        "/dream/process",
        json={"dream_content": "test dream", "qi_enhanced": True, "reflection_enabled": True},
    )
    assert response.status_code == 200
    json_response = response.json()
    assert "dream_id" in json_response
    app.dependency_overrides = {}


def test_process_dream_insufficient_tier(mock_get_current_user):
    app.dependency_overrides[get_current_user] = lambda: mock_get_current_user(tier=1)
    response = client.post(
        "/dream/process",
        json={"dream_content": "test dream", "qi_enhanced": True, "reflection_enabled": True},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient tier level"
    app.dependency_overrides = {}


def test_create_snapshot_success(mock_get_current_user):
    app.dependency_overrides[get_current_user] = lambda: mock_get_current_user(tier=3)
    with patch(
        "matriz.consciousness.dream.oneiric.oneiric_core.engine.dream_engine_fastapi.EnhancedDreamEngine.reflection_loop"
    ) as mock_reflection_loop:
        # Create a mock that is awaitable
        async def mock_create_dream_snapshot(*args, **kwargs):
            return "snapshot_123"

        mock_reflection_loop.create_dream_snapshot = MagicMock(
            side_effect=mock_create_dream_snapshot
        )
        response = client.post(
            "/memory/snapshot",
            json={
                "fold_id": "fold1",
                "dream_state": {},
                "introspective_content": {},
            },
        )
        assert response.status_code == 200
        assert response.json()["snapshot_id"] == "snapshot_123"
        app.dependency_overrides = {}


def test_create_snapshot_insufficient_tier(mock_get_current_user):
    app.dependency_overrides[get_current_user] = lambda: mock_get_current_user(tier=2)
    response = client.post(
        "/memory/snapshot",
        json={
            "fold_id": "fold1",
            "dream_state": {},
            "introspective_content": {},
        },
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient tier level"
    app.dependency_overrides = {}


@patch(
    "matriz.consciousness.dream.oneiric.oneiric_core.engine.dream_engine_fastapi.get_dream_engine"
)
def test_dream_processing_exception(mock_get_dream_engine):
    mock_engine = MagicMock()
    mock_engine.process_dream.side_effect = Exception("Processing error")
    mock_get_dream_engine.return_value = mock_engine

    response = client.post(
        "/dream/process",
        json={"dream_content": "test dream"},
    )
    assert response.status_code == 500
    assert "Dream processing failed: Processing error" in response.json()["detail"]
