from unittest.mock import AsyncMock, patch

import pytest

from bridge.llm_wrappers.base import LLMProvider, LLMWrapper
from lukhas.bridge.orchestration.multi_ai_orchestrator import ModelOrchestrator


class MockLLMWrapper(LLMWrapper):
    def __init__(self, is_available=True, response="mock response", model="mock_model"):
        self._is_available = is_available
        self.response = response
        self.model = model
        self.generate_response = AsyncMock(return_value=(self.response, self.model))

    def is_available(self) -> bool:
        return self._is_available

    async def generate_response(self, prompt: str, model: str, **kwargs) -> tuple[str, str]:
        # This is a bit of a hack to make the mock work with the abstract method
        if "return_value" in self.generate_response.__dict__:
            return self.generate_response.return_value
        return (self.response, self.model)


@pytest.fixture
def mock_openai_wrapper():
    return MockLLMWrapper(response="openai response")


@pytest.fixture
def mock_anthropic_wrapper():
    return MockLLMWrapper(response="anthropic response")


@pytest.fixture
def mock_gemini_wrapper():
    return MockLLMWrapper(is_available=False)


@pytest.fixture
def orchestrator(mock_openai_wrapper, mock_anthropic_wrapper, mock_gemini_wrapper):
    with (
        patch(
            "labs.bridge.orchestration.multi_ai_orchestrator.UnifiedOpenAIClient",
            new=lambda: mock_openai_wrapper,
        ),
        patch(
            "labs.bridge.orchestration.multi_ai_orchestrator.AnthropicWrapper",
            new=lambda: mock_anthropic_wrapper,
        ),
        patch(
            "labs.bridge.orchestration.multi_ai_orchestrator.GeminiWrapper",
            new=lambda: mock_gemini_wrapper,
        ),
    ):
        return ModelOrchestrator()


@pytest.mark.asyncio
async def test_orchestrator_initialization(orchestrator):
    assert len(orchestrator.wrappers) == 2
    assert LLMProvider.OPENAI in orchestrator.wrappers
    assert LLMProvider.ANTHROPIC in orchestrator.wrappers
    assert LLMProvider.GOOGLE not in orchestrator.wrappers


@pytest.mark.asyncio
async def test_get_available_providers(orchestrator):
    providers = orchestrator.get_available_providers()
    assert len(providers) == 2
    assert LLMProvider.OPENAI in providers
    assert LLMProvider.ANTHROPIC in providers


@pytest.mark.asyncio
async def test_generate_response_specific_provider(orchestrator, mock_openai_wrapper):
    prompt = "test prompt"
    response, provider, model = await orchestrator.generate_response(prompt, provider=LLMProvider.OPENAI, model="gpt-4")
    assert response == "openai response"
    assert provider == "openai"
    assert model == "mock_model"
    mock_openai_wrapper.generate_response.assert_called_once_with(prompt, model="gpt-4")


@pytest.mark.asyncio
async def test_generate_response_fallback(orchestrator, mock_openai_wrapper):
    prompt = "test prompt"
    response, provider, model = await orchestrator.generate_response(prompt)
    # The default fallback is the first available wrapper, which is OpenAI in this case.
    assert response == "openai response"
    assert provider == "openai"
    assert model == "mock_model"
    mock_openai_wrapper.generate_response.assert_called_once_with(prompt, model=None)


@pytest.mark.asyncio
async def test_generate_response_invalid_provider(orchestrator):
    prompt = "test prompt"
    with pytest.raises(ValueError, match="Provider google is not available."):
        await orchestrator.generate_response(prompt, provider=LLMProvider.GOOGLE)


@pytest.mark.asyncio
async def test_generate_response_no_providers():
    with (
        patch(
            "labs.bridge.orchestration.multi_ai_orchestrator.UnifiedOpenAIClient",
            new=lambda: MockLLMWrapper(is_available=False),
        ),
        patch(
            "labs.bridge.orchestration.multi_ai_orchestrator.AnthropicWrapper",
            new=lambda: MockLLMWrapper(is_available=False),
        ),
        patch(
            "labs.bridge.orchestration.multi_ai_orchestrator.GeminiWrapper",
            new=lambda: MockLLMWrapper(is_available=False),
        ),
    ):
        orchestrator = ModelOrchestrator()
        prompt = "test prompt"
        with pytest.raises(ValueError, match="No LLM providers are available"):
            await orchestrator.generate_response(prompt)
