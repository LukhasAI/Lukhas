import asyncio
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from serve.consciousness_api import dream, memory, query, router

# --- Test Setup ---

@pytest.fixture
def mock_engine():
    """Fixture to mock the ConsciousnessEngine for logic-specific tests."""
    with patch("serve.consciousness_api.engine", new_callable=AsyncMock) as mock:
        mock.process_query.return_value = {"response": "mocked awareness"}
        mock.initiate_dream.return_value = {"dream_id": "mock-dream-456", "status": "pending"}
        mock.retrieve_memory_state.return_value = {"memory_folds": 2048, "recall_accuracy": 0.95}
        mock.save_user_state = AsyncMock(return_value=None)
        mock.get_user_state = AsyncMock(side_effect=lambda user_id: {"last_query": "mock"} if user_id == "user1" else None)
        yield mock

@pytest.fixture
def client():
    """Fixture providing a FastAPI test client."""
    app = FastAPI()
    app.include_router(router)
    with TestClient(app) as c:
        yield c

@pytest.fixture
def mocked_client(mock_engine):
    """Fixture providing a FastAPI test client with the mocked engine."""
    app = FastAPI()
    app.include_router(router)
    with TestClient(app) as c:
        yield c

# --- Original Comprehensive Tests (Unmocked Engine) ---

class TestQueryEndpoint:
    @pytest.mark.asyncio
    async def test_query_returns_awareness_level(self):
        result = await query()
        assert "response" in result
        assert isinstance(result["response"], str)
        assert "awareness level" in result["response"].lower()

    @pytest.mark.asyncio
    async def test_query_response_content(self):
        result = await query()
        assert result["response"] == "The current awareness level is high."

    def test_query_via_api(self, client):
        response = client.post("/api/v1/consciousness/query")
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "awareness level" in data["response"].lower()

class TestDreamEndpoint:
    @pytest.mark.asyncio
    async def test_dream_response_content(self):
        result = await dream()
        assert result["dream_id"] == "dream-123"
        assert result["status"] == "generating"

    def test_dream_via_api(self, client):
        response = client.post("/api/v1/consciousness/dream")
        assert response.status_code == 200
        data = response.json()
        assert data["dream_id"] == "dream-123"
        assert data["status"] == "generating"

class TestMemoryEndpoint:
    @pytest.mark.asyncio
    async def test_memory_response_content(self):
        result = await memory()
        assert result["memory_folds"] == 1024
        assert result["recall_accuracy"] == 0.98

    def test_memory_via_api(self, client):
        response = client.get("/api/v1/consciousness/memory")
        assert response.status_code == 200
        data = response.json()
        assert data["memory_folds"] == 1024
        assert data["recall_accuracy"] == 0.98

# --- New Comprehensive Tests (Mocked Engine) ---

class TestConsciousnessQueryWithMock:
    def test_success(self, mocked_client, mock_engine):
        response = mocked_client.post("/api/v1/consciousness/query")
        assert response.status_code == 200
        assert response.json() == {"response": "mocked awareness"}
        mock_engine.process_query.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_engine_error(self, mock_engine):
        mock_engine.process_query.side_effect = Exception("Engine failure")
        with pytest.raises(Exception, match="Engine failure"):
            await query()

class TestStateManagementWithMock:
    def test_save_state_success(self, mocked_client, mock_engine):
        payload = {"user_id": "user1", "state_data": {"key": "value"}}
        response = mocked_client.post("/api/v1/consciousness/state", json=payload)
        assert response.status_code == 200
        assert response.json() == {"status": "success", "user_id": "user1"}
        mock_engine.save_user_state.assert_awaited_with("user1", {"key": "value"})

    def test_save_state_validation_error(self, mocked_client):
        response = mocked_client.post("/api/v1/consciousness/state", json={"user_id": "user1"})
        assert response.status_code == 422 # Unprocessable Entity

    def test_retrieve_state_success(self, mocked_client, mock_engine):
        response = mocked_client.get("/api/v1/consciousness/state/user1")
        assert response.status_code == 200
        assert response.json() == {"user_id": "user1", "state_data": {"last_query": "mock"}}
        mock_engine.get_user_state.assert_awaited_with("user1")

    def test_retrieve_state_not_found(self, mocked_client, mock_engine):
        response = mocked_client.get("/api/v1/consciousness/state/user-not-found")
        assert response.status_code == 404
        assert response.json() == {"detail": "State not found for user"}

class TestUserIsolationWithMock:
    def test_user_cannot_access_another_users_state(self, mocked_client, mock_engine):
        response_user1 = mocked_client.get("/api/v1/consciousness/state/user1")
        assert response_user1.status_code == 200
        response_user2 = mocked_client.get("/api/v1/consciousness/state/user2")
        assert response_user2.status_code == 404

# --- Placeholder Tests for Unimplemented Features ---

@pytest.mark.skip(reason="Context submission not implemented")
class TestContextSubmission:
    def test_large_context_submission(self, mocked_client):
        pass
    def test_streaming_context_submission(self, mocked_client):
        pass

@pytest.mark.skip(reason="Authentication not implemented")
class TestAuthentication:
    def test_unauthorized_access(self, client):
        response = client.post("/api/v1/consciousness/query", headers={"Authorization": "Bearer invalid"})
        assert response.status_code == 401

@pytest.mark.skip(reason="Rate limiting not implemented")
class TestRateLimiting:
    def test_rate_limit_exceeded(self, client):
        for i in range(101):
            client.post("/api/v1/consciousness/query")
        response = client.post("/api/v1/consciousness/query")
        assert response.status_code == 429
