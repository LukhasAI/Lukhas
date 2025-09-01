from unittest.mock import AsyncMock, patch

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from candidate.bridge.llm_wrappers.base import LLMProvider
from enterprise.api.main import app


@pytest.fixture
def mock_orchestrator():
    orchestrator = AsyncMock()
    orchestrator.generate_response = AsyncMock(return_value=("mock response", "openai", "gpt-4"))
    orchestrator.get_available_providers = lambda: [LLMProvider.OPENAI, LLMProvider.ANTHROPIC]
    return orchestrator


@pytest.fixture
def test_app(mock_orchestrator):
    with patch("enterprise.api.main.ModelOrchestrator", return_value=mock_orchestrator):
        yield app


@pytest.mark.asyncio
async def test_health_check(test_app):
    async with LifespanManager(test_app):
        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.get("/health")
        assert response.status_code == 200
        assert response.json() == {
            "status": "ok",
            "available_providers": ["openai", "anthropic"],
        }


@pytest.mark.asyncio
async def test_chat_completions_specific_provider(test_app, mock_orchestrator):
    async with LifespanManager(test_app):
        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.post(
                "/v1/chat/completions",
                json={"prompt": "test prompt", "provider": "openai", "model": "gpt-4"},
            )
        assert response.status_code == 200
        assert response.json()["response"] == "mock response"
        assert response.json()["provider"] == "openai"
        assert response.json()["model"] == "gpt-4"
        mock_orchestrator.generate_response.assert_called_once_with(
            prompt="test prompt", provider=LLMProvider.OPENAI, model="gpt-4"
        )


@pytest.mark.asyncio
async def test_chat_completions_fallback(test_app, mock_orchestrator):
    mock_orchestrator.generate_response = AsyncMock(return_value=("mock response", "openai", "gpt-3.5-turbo"))
    async with LifespanManager(test_app):
        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.post("/v1/chat/completions", json={"prompt": "test prompt"})
        assert response.status_code == 200
        assert response.json()["response"] == "mock response"
        assert response.json()["provider"] == "openai"  # Default fallback
        assert response.json()["model"] == "gpt-3.5-turbo"
        mock_orchestrator.generate_response.assert_called_once_with(prompt="test prompt", provider=None, model=None)


@pytest.mark.asyncio
async def test_chat_completions_invalid_provider(test_app):
    async with LifespanManager(test_app):
        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.post(
                "/v1/chat/completions",
                json={"prompt": "test prompt", "provider": "invalid"},
            )
        assert response.status_code == 400
        assert "Invalid provider" in response.json()["detail"]


@pytest.mark.asyncio
async def test_chat_completions_missing_prompt(test_app):
    async with LifespanManager(test_app):
        async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as client:
            response = await client.post("/v1/chat/completions", json={"provider": "openai"})
        assert response.status_code == 422  # Unprocessable Entity
