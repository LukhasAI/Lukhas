"""Unified OpenAI integration for LUKHAS AI.

This file provides a consolidated OpenAI client wrapper used by the
candidate bridge. The implementation is intentionally conservative and
typed to reduce static-analysis noise during the migration work.
"""

import asyncio
import json
import logging
import os
import uuid
from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, ClassVar, Optional, Union

try:
    from openai import AsyncOpenAI, OpenAI  # type: ignore
except Exception:  # pragma: no cover - optional runtime dependency
    AsyncOpenAI = OpenAI = object  # type: ignore

from .base import LLMWrapper

logger = logging.getLogger("ΛTRACE.bridge.unified_openai")


@dataclass
class ConversationMessage:
    """Represents a single message in a conversation."""

    role: str
    content: str
    timestamp: str
    message_id: str
    metadata: Optional[dict[str, Any]] = None
    function_call: Optional[dict[str, Any]] = None


@dataclass
class ConversationState:
    """Represents the state of a conversation."""

    conversation_id: str
    session_id: str
    user_id: str
    messages: list[ConversationMessage]
    context: dict[str, Any]
    created_at: str
    updated_at: str
    total_tokens: int = 0
    max_context_length: int = 8000


class UnifiedOpenAIClient(LLMWrapper):
    """
    Unified OpenAI client for LUKHAS Cognitive system.
    Combines best features from all previous implementations.
    """

    # Task-specific model configurations
    TASK_MODELS: ClassVar[dict[str, str]] = {
        "reasoning": "gpt-4",
        "creativity": "gpt-4",
        "consciousness": "gpt-4",
        "memory": "gpt-3.5-turbo",
        "ethics": "gpt-4",
        "coding": "gpt-4",
        "voice_processing": "gpt-3.5-turbo",
        "symbolic_reasoning": "gpt-4",
        "general": "gpt-3.5-turbo",
    }

    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Initialize the unified OpenAI client.

        Args:
            api_key: Optional API key. If not provided, will use OPENAI_API_KEY env var.
        """
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.organization = os.getenv("ORGANIZATION_ID")
        self.project = os.getenv("PROJECT_ID")

        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")

        org: Optional[str] = self.organization
        # initialize client objects if real classes are available
        try:
            self.client = OpenAI(api_key=self.api_key, organization=org)  # type: ignore[arg-type]
            self.async_client = AsyncOpenAI(api_key=self.api_key, organization=org)  # type: ignore[arg-type]
        except Exception:
            # Keep fallback placeholders for environments without openai package
            self.client = None  # type: ignore[assignment]
            self.async_client = None  # type: ignore[assignment]

        self.project_id = self.project
        self.conversations: dict[str, ConversationState] = {}

        # Default parameters
        self.default_temperature: float = 0.7
        self.default_max_tokens: int = 2000
        self.retry_attempts: int = 3
        self.retry_delay: float = 1.0

        logger.info("UnifiedOpenAIClient initialized")

    # Conversation Management

    def create_conversation(self, user_id: str, session_id: str) -> str:
        """Create a new conversation"""
        conversation_id = str(uuid.uuid4())
        now = datetime.now(tz=timezone.utc).isoformat()

        self.conversations[conversation_id] = ConversationState(
            conversation_id=conversation_id,
            session_id=session_id,
            user_id=user_id,
            messages=[],
            context={},
            created_at=now,
            updated_at=now,
        )

        logger.info(f"Created conversation {conversation_id} for user {user_id}")
        return conversation_id

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        function_call: Optional[dict] = None,
    ) -> ConversationMessage:
        """Add a message to a conversation"""
        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation {conversation_id} not found")
        message = ConversationMessage(
            role=role,
            content=content,
            timestamp=datetime.now(tz=timezone.utc).isoformat(),
            message_id=str(uuid.uuid4()),
            function_call=function_call,
        )

        self.conversations[conversation_id].messages.append(message)
        self.conversations[conversation_id].updated_at = datetime.now(tz=timezone.utc).isoformat()

        return message

    def get_conversation_messages(self, conversation_id: str, max_tokens: int = 4000) -> list[dict[str, Any]]:
        """Get conversation messages formatted for OpenAI API"""
        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation {conversation_id} not found")
        messages: list[dict[str, Any]] = []
        token_count = 0

        # Add messages in reverse order until we hit token limit
        for msg in reversed(self.conversations[conversation_id].messages):
            msg_dict: dict[str, Any] = {"role": msg.role, "content": msg.content}
            if msg.function_call:
                msg_dict["function_call"] = msg.function_call

            # Rough token estimation (4 chars per token)
            msg_tokens = len(json.dumps(msg_dict)) // 4
            if token_count + msg_tokens > max_tokens:
                break

            messages.insert(0, msg_dict)
            token_count += msg_tokens

        return messages

    # Core API Methods

    async def chat_completion(
        self,
        messages: Union[list[dict[str, Any]], str],
        model: Optional[str] = None,
        task: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        functions: Optional[list[dict[str, Any]]] = None,
        function_call: Optional[Union[str, dict[str, str]]] = None,
        tools: Optional[list[dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, dict[str, str]]] = None,
        **kwargs,
    ) -> Union[dict[str, Any], AsyncIterator[dict[str, Any]]]:
        """
        Create a chat completion with the OpenAI API.

        Args:
            messages: List of message dicts or a single prompt string
            model: Model to use (defaults to task-specific or general)
            task: Task type for model selection
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            functions: Function definitions for function calling
            function_call: Function calling behavior
            **kwargs: Additional parameters for the API

        Returns:
            Response dict or async iterator for streaming
        """
        # Handle string prompt
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]

        # Select model based on task
        if model is None:
            key = task if task is not None else "general"
            model = self.TASK_MODELS.get(key, self.TASK_MODELS["general"])

        # Set defaults
        temperature = temperature if temperature is not None else self.default_temperature
        max_tokens = max_tokens if max_tokens is not None else self.default_max_tokens

        # Prepare request parameters
        params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs,
        }

        # Add function calling parameters if provided
        if functions:
            params["functions"] = functions
        if function_call is not None:
            params["function_call"] = function_call

        # Add tools (newer function calling API) if provided
        if tools:
            params["tools"] = tools
        if tool_choice is not None:
            params["tool_choice"] = tool_choice

        # Execute request with retries
        last_exc: Optional[BaseException] = None
        for attempt in range(self.retry_attempts):
            try:
                if self.async_client is None:  # pragma: no cover - runtime fallback
                    raise RuntimeError("OpenAI async client not available")

                if stream:
                    return await self.async_client.chat.completions.create(**params, stream=True)
                response = await self.async_client.chat.completions.create(**params)
                # model_dump may not exist on all client objects; fall back to dict()
                return getattr(response, "model_dump", lambda r=response: dict(r))()

            except Exception as exc:  # capture and retry
                last_exc = exc
                logger.debug("OpenAI API error (attempt %d): %s", attempt + 1, exc)
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))

        # If we exhausted retries, raise the last exception
        if last_exc:
            raise last_exc

    def chat_completion_sync(
        self,
        messages: Union[list[dict[str, Any]], str],
        model: Optional[str] = None,
        task: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Synchronous version of chat_completion"""
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]

        if model is None:
            model = self.TASK_MODELS.get(task, self.TASK_MODELS["general"])

        temperature = temperature if temperature is not None else self.default_temperature
        max_tokens = max_tokens if max_tokens is not None else self.default_max_tokens

        if self.client is None:  # pragma: no cover - runtime fallback
            raise RuntimeError("OpenAI sync client not available")

        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

        return getattr(response, "model_dump", lambda: dict(response))()

    # Task-Specific Methods

    async def reasoning_task(self, prompt: str, context: Optional[dict] = None) -> str:
        """Execute a reasoning task with appropriate model and parameters"""
        system_prompt = "You are an advanced reasoning system. Analyze the problem step by step."

        messages = [{"role": "system", "content": system_prompt}]

        if context:
            messages.append(
                {
                    "role": "system",
                    "content": f"Context: {json.dumps(context)}",
                }
            )

        messages.append({"role": "user", "content": prompt})

        response = await self.chat_completion(
            messages=messages,
            task="reasoning",
            temperature=0.2,  # Lower temperature for reasoning
        )

        return response["choices"][0]["message"]["content"]

    async def creative_task(self, prompt: str, style: Optional[str] = None) -> str:
        """Execute a creative task with appropriate parameters"""
        system_prompt = "You are a creative AI assistant capable of generating imaginative content."

        if style:
            system_prompt += f" Generate content in the style of: {style}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        response = await self.chat_completion(
            messages=messages,
            task="creativity",
            temperature=0.9,  # Higher temperature for creativity
        )

        return response["choices"][0]["message"]["content"]

    async def ethics_check(self, action: str, context: dict[str, Any]) -> dict[str, Any]:
        """Check ethical implications of an action"""
        messages = [
            {
                "role": "system",
                "content": "You are an ethical reasoning system. Analyze the ethical implications of actions.",
            },
            {
                "role": "user",
                "content": f"Analyze the ethical implications of: {action}\nContext: {json.dumps(context)}",
            },
        ]

        response = await self.chat_completion(messages=messages, task="ethics", temperature=0.3)

        content = response["choices"][0]["message"]["content"]

        # Parse response for ethical assessment
        return {
            "action": action,
            "assessment": content,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        }

    # Utility Methods

    async def count_tokens(self, text: str, model: str = "gpt-3.5-turbo") -> int:
        """Estimate token count for text"""
        # Rough estimation: 4 characters per token
        # In production, use tiktoken library for accurate counting
        _ = model
        return len(text) // 4

    def get_model_info(self, task: Optional[str] = None) -> dict[str, Any]:
        """Get information about available models and current configuration"""
        return {
            "task_models": self.TASK_MODELS,
            "selected_model": (self.TASK_MODELS.get(task, self.TASK_MODELS["general"]) if task else None),
            "organization": self.organization,
            "project_id": self.project_id,
            "default_temperature": self.default_temperature,
            "default_max_tokens": self.default_max_tokens,
        }

    async def close(self):
        """Clean up resources"""
        if self.async_client is not None:
            close = getattr(self.async_client, "close", None)
            if callable(close):
                await close()
        logger.info("UnifiedOpenAIClient closed")

    async def generate_response(self, prompt: str, model: Optional[str] = None, **kwargs) -> tuple[str, str]:
        """
        Generate a response from the LLM.
        This is an adapter method to comply with the LLMWrapper interface.
        """
        task = kwargs.get("task")
        temperature = kwargs.get("temperature")
        max_tokens = kwargs.get("max_tokens")

        if model is None:
            model = self.TASK_MODELS.get(task, self.TASK_MODELS["general"])

        response = await self.chat_completion(
            messages=prompt,
            model=model,
            task=task,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response["choices"][0]["message"]["content"], model

    def is_available(self) -> bool:
        """
        Check if the OpenAI client is available.
        """
        return self.api_key is not None


# Backward compatibility aliases
GPTClient = UnifiedOpenAIClient
LukhasOpenAIClient = UnifiedOpenAIClient
OpenAIWrapper = UnifiedOpenAIClient
