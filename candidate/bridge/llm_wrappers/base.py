"""
Base classes for LLM wrappers.
"""
import streamlit as st

from abc import ABC, abstractmethod
from enum import Enum


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
    async def generate_response(self, prompt: str, model: str, **kwargs) -> tuple[str, str]:
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
    def is_available(self) -> bool:
        """
        Check if the LLM provider is available.

        Returns:
            True if the provider is available, False otherwise.
        """
        pass
