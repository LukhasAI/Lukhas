"""OpenAI Provider Protocol - Type-safe interface for OpenAI client abstraction.

This module defines the Protocol (structural typing interface) that any OpenAI
provider implementation must satisfy. Enables dependency injection, testing
with mocks, and clear contracts for OpenAI-dependent code.

Part of T4 lane isolation initiative to remove hard dependencies on labs.
"""
from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import Any, Protocol

from typing_extensions import NotRequired, TypedDict


class ChatMessage(TypedDict):
    """Structured chat message for OpenAI API."""
    role: str
    content: str
    name: NotRequired[str]
    function_call: NotRequired[dict[str, Any]]


class ChatCompletionResponse(TypedDict):
    """Response from chat completion endpoint."""
    id: str
    object: str
    created: int
    model: str
    choices: list[dict[str, Any]]
    usage: NotRequired[dict[str, int]]


class OpenAIProvider(Protocol):
    """Protocol defining the interface for OpenAI client providers.

    Any concrete implementation (real OpenAI client, mock, or alternative)
    must implement these methods to be compatible with OpenAI-dependent code.

    Examples:
        Using the protocol with dependency injection:

        >>> def process_with_ai(provider: OpenAIProvider, prompt: str) -> str:
        ...     response = provider.create_chat_completion(
        ...         model="gpt-4",
        ...         messages=[{"role": "user", "content": prompt}]
        ...     )
        ...     return response["choices"][0]["message"]["content"]

        Testing with a mock:

        >>> class MockProvider:
        ...     def create_chat_completion(self, **kwargs):
        ...         return {
        ...             "choices": [{"message": {"content": "Mock response"}}]
        ...         }
        ...
        >>> provider = MockProvider()
        >>> result = process_with_ai(provider, "test")
        >>> assert result == "Mock response"
    """

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
    ) -> ChatCompletionResponse | Iterator[dict[str, Any]]:
        """Create a chat completion (synchronous).

        Args:
            model: Model identifier (e.g., "gpt-4", "gpt-3.5-turbo")
            messages: List of chat messages with role and content
            temperature: Sampling temperature 0-2 (default: 0.7)
            max_tokens: Maximum tokens to generate (default: model limit)
            top_p: Nucleus sampling parameter (default: 1.0)
            frequency_penalty: Frequency penalty -2 to 2 (default: 0)
            presence_penalty: Presence penalty -2 to 2 (default: 0)
            stop: Stop sequences (string or list)
            stream: Whether to stream responses (default: False)
            **kwargs: Additional provider-specific parameters

        Returns:
            ChatCompletionResponse if not streaming, Iterator if streaming

        Raises:
            Exception: Provider-specific exceptions for API errors
        """
        ...

    async def create_chat_completion_async(
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
    ) -> ChatCompletionResponse | AsyncIterator[dict[str, Any]]:
        """Create a chat completion (asynchronous).

        Args:
            Same as create_chat_completion

        Returns:
            ChatCompletionResponse if not streaming, AsyncIterator if streaming

        Raises:
            Exception: Provider-specific exceptions for API errors
        """
        ...

    def create_embedding(
        self,
        *,
        model: str,
        input: str | list[str],
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create embeddings for input text.

        Args:
            model: Embedding model (e.g., "text-embedding-ada-002")
            input: Text or list of texts to embed
            **kwargs: Additional provider-specific parameters

        Returns:
            Embedding response with data and usage information

        Raises:
            Exception: Provider-specific exceptions for API errors
        """
        ...

    async def create_embedding_async(
        self,
        *,
        model: str,
        input: str | list[str],
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create embeddings for input text (asynchronous).

        Args:
            Same as create_embedding

        Returns:
            Embedding response with data and usage information

        Raises:
            Exception: Provider-specific exceptions for API errors
        """
        ...


__all__ = [
    "ChatCompletionResponse",
    "ChatMessage",
    "OpenAIProvider",
]
