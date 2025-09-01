"""
Base classes for LLM wrappers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any


class LLMProvider(Enum):
    """
    Enum for the supported LLM providers.
    """

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"


class LLMWrapper(ABC):
    """
    Abstract base class for LLM wrappers.
    """

    @abstractmethod
    async def generate_response(
        self: LLMWrapper, prompt: str, model: str, **kwargs: Any
    ) -> tuple[str, str]:
        """
        Generate a response from the LLM.

        Args:
            prompt: The prompt to send to the LLM.
            model: The model to use for the generation.
            **kwargs: Additional arguments for the LLM provider.

        Returns:
            A tuple containing the generated response as a string and the model used.
        """
        pass

    @abstractmethod
    def is_available(self: LLMWrapper) -> bool:
        """
        Check if the LLM provider is available.

        Returns:
            True if the provider is available, False otherwise.
        """
        pass
