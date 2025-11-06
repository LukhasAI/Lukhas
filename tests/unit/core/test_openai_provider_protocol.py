"""Tests for OpenAIProvider Protocol.

Verifies that the Protocol can be implemented by mock classes and used
for type-safe dependency injection without requiring actual OpenAI clients.
"""
from __future__ import annotations

from typing import Any

import pytest
from core.ports import ChatCompletionResponse, ChatMessage, OpenAIProvider


class MockOpenAIProvider:
    """Mock implementation of OpenAIProvider for testing.

    Demonstrates that any class implementing the Protocol methods
    can be used interchangeably with real OpenAI clients.
    """

    def __init__(self, mock_response: str = "Mock response"):
        self.mock_response = mock_response
        self.last_call_args: dict[str, Any] = {}

    def create_chat_completion(
        self,
        *,
        model: str,
        messages: list[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        stop: str | list[str] | None = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> ChatCompletionResponse:
        """Mock chat completion."""
        self.last_call_args = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        return ChatCompletionResponse(
            id="mock-id-123",
            object="chat.completion",
            created=1234567890,
            model=model,
            choices=[
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": self.mock_response},
                    "finish_reason": "stop",
                }
            ],
        )

    async def create_chat_completion_async(
        self,
        *,
        model: str,
        messages: list[ChatMessage],
        **kwargs: Any,
    ) -> ChatCompletionResponse:
        """Mock async chat completion."""
        return self.create_chat_completion(model=model, messages=messages, **kwargs)

    def create_embedding(
        self,
        *,
        model: str,
        input: str | list[str],
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Mock embedding creation."""
        return {
            "object": "list",
            "data": [{"embedding": [0.1, 0.2, 0.3], "index": 0}],
            "model": model,
            "usage": {"prompt_tokens": 10, "total_tokens": 10},
        }

    async def create_embedding_async(
        self,
        *,
        model: str,
        input: str | list[str],
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Mock async embedding creation."""
        return self.create_embedding(model=model, input=input, **kwargs)


def test_protocol_implementation():
    """Test that mock class satisfies OpenAIProvider Protocol."""
    # This type checks correctly with mypy/pyright because MockOpenAIProvider
    # implements all required methods from OpenAIProvider Protocol
    provider: OpenAIProvider = MockOpenAIProvider()

    # Verify basic functionality
    response = provider.create_chat_completion(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello"}],
    )

    assert response["id"] == "mock-id-123"
    assert response["model"] == "gpt-4"
    assert len(response["choices"]) == 1
    assert response["choices"][0]["message"]["content"] == "Mock response"


def test_protocol_with_custom_response():
    """Test that mock can be configured with custom responses."""
    provider = MockOpenAIProvider(mock_response="Custom test response")

    response = provider.create_chat_completion(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Test"}],
        temperature=0.5,
    )

    assert response["choices"][0]["message"]["content"] == "Custom test response"
    assert provider.last_call_args["model"] == "gpt-3.5-turbo"
    assert provider.last_call_args["temperature"] == 0.5


def test_embedding_creation():
    """Test embedding endpoint implementation."""
    provider = MockOpenAIProvider()

    response = provider.create_embedding(
        model="text-embedding-ada-002",
        input="Test text",
    )

    assert response["object"] == "list"
    assert len(response["data"]) == 1
    assert "embedding" in response["data"][0]
    assert response["model"] == "text-embedding-ada-002"


@pytest.mark.asyncio
async def test_async_chat_completion():
    """Test async chat completion."""
    provider = MockOpenAIProvider(mock_response="Async response")

    response = await provider.create_chat_completion_async(
        model="gpt-4",
        messages=[{"role": "user", "content": "Async test"}],
    )

    assert response["choices"][0]["message"]["content"] == "Async response"


@pytest.mark.asyncio
async def test_async_embedding():
    """Test async embedding creation."""
    provider = MockOpenAIProvider()

    response = await provider.create_embedding_async(
        model="text-embedding-ada-002",
        input="Async embedding test",
    )

    assert response["object"] == "list"
    assert len(response["data"]) == 1


def test_dependency_injection_example():
    """Demonstrate dependency injection pattern with Protocol."""

    def process_with_ai(provider: OpenAIProvider, prompt: str) -> str:
        """Function that accepts any OpenAIProvider implementation."""
        response = provider.create_chat_completion(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
        )
        return response["choices"][0]["message"]["content"]

    # Can use mock in tests
    mock_provider = MockOpenAIProvider(mock_response="Test output")
    result = process_with_ai(mock_provider, "Test input")
    assert result == "Test output"

    # In production, would use real OpenAI client (not shown here)
    # real_provider = RealOpenAIClient(api_key="...")
    # result = process_with_ai(real_provider, "Real input")
