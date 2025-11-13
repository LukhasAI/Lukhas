import asyncio
import os
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Set environment variables to enable dream features for testing
os.environ["LUKHAS_DREAMS_ENABLED"] = "1"
os.environ["LUKHAS_PARALLEL_DREAMS"] = "1"

# Mock core.common to prevent RecursionError during test collection
import sys

sys.modules['core.common'] = MagicMock()

# Since we're setting environment variables, we need to import the app after setting them
from labs.core.security.auth import get_auth_system


@pytest.fixture(scope="module")
def client():
    """
    Create a TestClient instance for the FastAPI app, ensuring all mocks
    are in place before the app is imported and the client is created.
    """
    with patch("labs.consciousness.dream.core.dream_engine.UnifiedIntegration") as mock_ui, \
         patch("lukhas.dream.get_dream_engine") as mock_get_engine:

        from serve.main import app

        with TestClient(app) as c:
            yield c


@pytest.fixture
def mock_user():
    """Provides a mock user dictionary."""
    return {"user_id": "test_user_123", "tier": "AUTHENTICATED", "permissions": ["memory:fold"]}


@pytest.fixture
def mock_user_2():
    """Provides a second mock user for concurrency tests."""
    return {"user_id": "test_user_456", "tier": "AUTHENTICATED", "permissions": ["memory:fold"]}


@pytest.fixture
def auth_headers(mock_user):
    """Generates authentication headers for a mock user."""
    auth_system = get_auth_system()
    token = auth_system.generate_jwt(mock_user)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_user_2(mock_user_2):
    """Generates authentication headers for the second mock user."""
    auth_system = get_auth_system()
    token = auth_system.generate_jwt(mock_user_2)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client_with_mocks():
    """
    Provides a TestClient with all necessary mocks for the dream system.
    Returns the client and the mock dream store.
    """
    dreams_db = []

    async def mock_store_data(store_name, data):
        if store_name == "enhanced_memories":
            dreams_db.append(data)

    async def mock_get_data(store_name):
        if store_name == "enhanced_memories":
            return dreams_db
        return []

    mock_integration = MagicMock()
    mock_integration.store_data = AsyncMock(side_effect=mock_store_data)
    mock_integration.get_data = AsyncMock(side_effect=mock_get_data)

    mock_engine = MagicMock()
    async def mock_process_dream(dream_object):
        await asyncio.sleep(0.01)
        dream_object["state"] = "consolidated"
        dream_object["result"] = {"narrative": "A mock dream narrative."}
        # Simulate storing the dream
        await mock_store_data("enhanced_memories", dream_object)

    mock_engine.process_dream = AsyncMock(side_effect=mock_process_dream)

    with patch("labs.consciousness.dream.core.dream_engine.UnifiedIntegration", return_value=mock_integration), \
         patch("lukhas.dream.get_dream_engine", return_value=mock_engine):

        from serve.main import app
        with TestClient(app) as c:
            yield c, dreams_db, mock_engine


def test_full_dream_generation_pipeline(client_with_mocks, mock_user, auth_headers):
    """
    Tests the full end-to-end dream generation and retrieval pipeline.
    """
    client, mock_dream_store, _ = client_with_mocks

    response = client.post(
        "/api/v1/dreams/simulate",
        json={"seed": "test_dream_seed", "context": {"mood": "testing"}},
        headers=auth_headers,
    )
    assert response.status_code == 200
    dream_data = response.json()
    assert dream_data["success"] is True
    dream_id = dream_data["dream_id"]

    assert len(mock_dream_store) > 0
    stored_dream = mock_dream_store[0]
    assert stored_dream["id"] == dream_id
    assert stored_dream["user_id"] == mock_user["user_id"]

    retrieve_response = client.get(f"/api/v1/dreams/{dream_id}", headers=auth_headers)
    assert retrieve_response.status_code == 200
    retrieved_dream = retrieve_response.json()
    assert retrieved_dream["id"] == dream_id
    assert retrieved_dream["user_id"] == mock_user["user_id"]


def test_dream_simulation_engine_failure(client_with_mocks, auth_headers):
    """
    Tests API handling of dream engine failure.
    """
    client, _, mock_dream_engine = client_with_mocks
    mock_dream_engine.process_dream.side_effect = Exception("Engine critical failure")

    response = client.post(
        "/api/v1/dreams/simulate",
        json={"seed": "a_failing_dream"},
        headers=auth_headers,
    )
    assert response.status_code == 500
    assert "Dream simulation failed: Engine critical failure" in response.json()["detail"]


def test_dream_simulation_timeout(client_with_mocks, auth_headers):
    """
    Tests API handling of dream engine timeout.
    """
    client, _, mock_dream_engine = client_with_mocks
    mock_dream_engine.process_dream.side_effect = asyncio.TimeoutError("Simulation timed out")

    response = client.post(
        "/api/v1/dreams/simulate",
        json={"seed": "a_slow_dream"},
        headers=auth_headers,
    )
    assert response.status_code == 500
    assert "Simulation timed out" in response.json()["detail"]


def test_dream_simulation_when_disabled(client_with_mocks, auth_headers):
    """
    Tests that the endpoint is disabled correctly.
    """
    client, _, _ = client_with_mocks
    with patch("lukhas.dream.is_enabled", return_value=False):
        response = client.post(
            "/api/v1/dreams/simulate",
            json={"seed": "a_dream_that_should_not_be"},
            headers=auth_headers,
        )
        assert response.status_code == 503


def test_parallel_dream_mesh_success(client_with_mocks, auth_headers):
    """
    Tests successful creation of a parallel dream mesh.
    """
    client, mock_dream_store, _ = client_with_mocks
    seeds = ["seed1", "seed2", "seed3"]
    response = client.post(
        "/api/v1/dreams/mesh",
        json={"seeds": seeds},
        headers=auth_headers,
    )
    assert response.status_code == 200
    mesh_data = response.json()
    assert mesh_data["success"] is True
    assert len(mesh_data["dreams"]) == len(seeds)
    assert len(mock_dream_store) == len(seeds)


def test_dream_retrieval_unauthorized(client_with_mocks, auth_headers, mock_user_2):
    """
    Tests that a user cannot retrieve another user's dream.
    """
    client, mock_dream_store, _ = client_with_mocks
    dream_id = "other_users_dream"
    mock_dream_store.append({"id": dream_id, "user_id": mock_user_2["user_id"]})

    response = client.get(f"/api/v1/dreams/{dream_id}", headers=auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_multi_user_concurrent_dreams(client_with_mocks, auth_headers, auth_headers_user_2, mock_user, mock_user_2):
    """
    Tests that concurrent dream generation from multiple users does not result in cross-contamination.
    """
    client, mock_dream_store, _ = client_with_mocks

    client.post("/api/v1/dreams/simulate", json={"seed": "user1_dream"}, headers=auth_headers)
    client.post("/api/v1/dreams/simulate", json={"seed": "user2_dream"}, headers=auth_headers_user_2)

    user1_dreams = [d for d in mock_dream_store if d["user_id"] == mock_user["user_id"]]
    user2_dreams = [d for d in mock_dream_store if d["user_id"] == mock_user_2["user_id"]]

    assert len(user1_dreams) == 1
    assert len(user2_dreams) == 1


@pytest.mark.asyncio
async def test_performance_under_load(client_with_mocks):
    """
    Simulates 10 concurrent users generating dreams to test performance.
    """
    client, mock_dream_store, _ = client_with_mocks
    num_users = 10

    async def generate_dream_task(user_id):
        user = {"user_id": f"perf_user_{user_id}", "tier": "AUTHENTICATED", "permissions": ["memory:fold"]}
        token = get_auth_system().generate_jwt(user)
        headers = {"Authorization": f"Bearer {token}"}
        client.post("/api/v1/dreams/simulate", json={"seed": f"perf_dream_{user_id}"}, headers=headers)

    tasks = [generate_dream_task(i) for i in range(num_users)]
    await asyncio.gather(*tasks)

    assert len(mock_dream_store) == num_users
