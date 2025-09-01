"""
OpenAI Modulated Service
========================
Simplified LUKHAS OpenAI service for production use.

This is a production-ready version that provides core functionality
without complex signal modulation dependencies.
"""

import logging
import time
import uuid
from typing import Any, Optional

# Pre-declare the UnifiedOpenAIClient type to allow a runtime import fallback
# without causing 'Cannot assign to a type' mypy errors when the import fails.
UnifiedOpenAIClient: Optional[Any] = None

# Use fallback imports
try:
    from lukhas.core.common import get_logger

    logger = get_logger(__name__, "BRIDGE")
except ImportError:
    logger = logging.getLogger(__name__)

try:
    from .unified_openai_client import UnifiedOpenAIClient
except ImportError:
    UnifiedOpenAIClient = None


class OpenAIModulatedService:
    """
    Production OpenAI service with basic modulation capabilities.

    This simplified version provides:
    - OpenAI API integration via UnifiedOpenAIClient
    - Basic response normalization
    - Error handling and logging
    - Simple conversation management
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = "gpt-4o-mini",
        max_retries: int = 3,
        timeout: float = 60.0,
    ) -> None:
        """
        Initialize the modulated service.

        Args:
            api_key: OpenAI API key
            default_model: Default model to use
            max_retries: Maximum retry attempts
            timeout: Request timeout
        """
        if UnifiedOpenAIClient is None:
            raise ImportError("UnifiedOpenAIClient not available")

        self.client = UnifiedOpenAIClient(
            api_key=api_key,
            default_model=default_model,
            max_retries=max_retries,
            timeout=timeout,
        )

        self.default_model = default_model
        self._metrics = {"requests": 0, "errors": 0, "total_time": 0.0}

        logger.info("OpenAIModulatedService initialized")

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
        conversation_id: Optional[str] = None,
        stream: bool = False,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Generate a response using OpenAI.

        Args:
            prompt: User prompt
            model: Model to use
            context: Additional context
            conversation_id: Conversation ID for state management
            stream: Whether to stream response
            **kwargs: Additional parameters

        Returns:
            Normalized response dictionary
        """
        start_time = time.time()
        self._metrics["requests"] += 1

        try:
            # Build messages
            messages = self._build_messages(prompt, context)

            # Call client
            response = await self.client.chat_completion(
                messages=messages,
                model=model or self.default_model,
                conversation_id=conversation_id,
                stream=stream,
                **kwargs,
            )

            # Normalize response
            if stream:
                return {
                    "type": "stream",
                    "stream": response,
                    "request_id": str(uuid.uuid4()),
                }
            else:
                normalized = self._normalize_response(response)

                # Update metrics
                duration = time.time() - start_time
                self._metrics["total_time"] += duration

                logger.debug(f"Generated response in {duration:.3f}s")

                return normalized

        except Exception as e:
            self._metrics["errors"] += 1
            logger.error(f"Generation failed: {e!s}")

            return {
                "content": f"Error: {e!s}",
                "error": True,
                "error_type": type(e).__name__,
                "request_id": str(uuid.uuid4()),
                "metadata": {
                    "model": model or self.default_model,
                    "error_time": time.time(),
                },
            }

    def _build_messages(
        self,
        prompt: str,
        context: Optional[dict[str, Any]] = None,
    ) -> list[dict[str, Any]]:
        """Build messages array for OpenAI API"""
        messages = []

        # Add system message if context provides one
        if context and context.get("system_prompt"):
            messages.append({"role": "system", "content": context["system_prompt"]})

        # Add user prompt
        messages.append({"role": "user", "content": prompt})

        return messages

    def _normalize_response(self, response: dict[str, Any]) -> dict[str, Any]:
        """Normalize OpenAI response to standard format"""
        if not response.get("choices"):
            return {
                "content": "",
                "error": True,
                "error_type": "EmptyResponse",
                "request_id": str(uuid.uuid4()),
            }

        choice = response["choices"][0]
        content = choice.get("message", {}).get("content", "")

        return {
            "content": content,
            "model": response.get("model", self.default_model),
            "finish_reason": choice.get("finish_reason"),
            "usage": response.get("usage"),
            "request_id": response.get("id", str(uuid.uuid4())),
            "metadata": {
                "created": response.get("created"),
                "object": response.get("object"),
                "choice_index": choice.get("index", 0),
            },
        }

    async def embed(
        self,
        text: str,
        model: str = "text-embedding-ada-002",
    ) -> dict[str, Any]:
        """
        Generate embeddings for text.

        Args:
            text: Text to embed
            model: Embedding model

        Returns:
            Normalized embedding response
        """
        try:
            response = await self.client.embeddings(text, model=model)

            if not response.get("data"):
                raise ValueError("Empty embeddings response")

            return {
                "embedding": response["data"][0]["embedding"],
                "model": response.get("model", model),
                "usage": response.get("usage"),
                "request_id": str(uuid.uuid4()),
            }

        except Exception as e:
            logger.error(f"Embedding failed: {e!s}")
            raise

    def create_conversation(
        self,
        system_prompt: Optional[str] = None,
        max_history: int = 50,
    ) -> str:
        """Create a new conversation"""
        return self.client.create_conversation(
            system_prompt=system_prompt,
            max_history=max_history,
        )

    def clear_conversation(self, conversation_id: str) -> bool:
        """Clear a conversation"""
        return self.client.clear_conversation(conversation_id)

    def get_metrics(self) -> dict[str, Any]:
        """Get service metrics"""
        avg_time = self._metrics["total_time"] / self._metrics["requests"] if self._metrics["requests"] > 0 else 0

        return {
            "total_requests": self._metrics["requests"],
            "total_errors": self._metrics["errors"],
            "error_rate": (self._metrics["errors"] / self._metrics["requests"] if self._metrics["requests"] > 0 else 0),
            "average_response_time": avg_time,
            "total_time": self._metrics["total_time"],
        }

    def health_check(self) -> dict[str, Any]:
        """Perform health check"""
        try:
            # Simple check - verify client is initialized
            if self.client is None:
                raise ValueError("Client not initialized")

            return {
                "status": "healthy",
                "timestamp": time.time(),
                "metrics": self.get_metrics(),
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time(),
            }
