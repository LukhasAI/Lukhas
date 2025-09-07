from typing import Optional

from candidate.bridge.llm_wrappers.anthropic_wrapper import AnthropicWrapper
from candidate.bridge.llm_wrappers.base import LLMProvider, LLMWrapper
from candidate.bridge.llm_wrappers.gemini_wrapper import GeminiWrapper
from candidate.bridge.llm_wrappers.unified_openai_client import UnifiedOpenAIClient
import streamlit as st


class ModelOrchestrator:
    """
    Orchestrates multiple LLM providers.
    """

    def __init__(self):
        self.wrappers: dict[LLMProvider, LLMWrapper] = {}
        self._initialize_wrappers()

    def _initialize_wrappers(self):
        """
        Initializes all available LLM wrappers.
        """
        # A simple way to initialize wrappers.
        # In a real system, this would be more dynamic, perhaps using the integration_bridge.
        potential_wrappers = {
            LLMProvider.OPENAI: UnifiedOpenAIClient,
            LLMProvider.ANTHROPIC: AnthropicWrapper,
            LLMProvider.GOOGLE: GeminiWrapper,
        }

        for provider, wrapper_class in potential_wrappers.items():
            try:
                wrapper_instance = wrapper_class()
                if wrapper_instance.is_available():
                    self.wrappers[provider] = wrapper_instance
            except Exception as e:
                print(f"Failed to initialize wrapper for {provider.value}: {e}")

    async def generate_response(
        self,
        prompt: str,
        provider: Optional[LLMProvider] = None,
        model: Optional[str] = None,
        **kwargs,
    ) -> tuple[str, str, str]:
        """
        Generates a response from the best available LLM provider, or a specific one if requested.

        Args:
            prompt: The prompt to send to the LLM.
            provider: The specific provider to use. If None, the orchestrator will choose.
            model: The specific model to use.
            **kwargs: Additional arguments for the LLM provider.

        Returns:
            A tuple of (generated response, provider name, model used).
        """
        selected_wrapper = None
        selected_provider = None
        if provider:
            if provider in self.wrappers:
                selected_wrapper = self.wrappers[provider]
                selected_provider = provider
            else:
                raise ValueError(f"Provider {provider.value} is not available.")
        elif self.wrappers:
            # Simple fallback strategy: use the first available wrapper.
            selected_provider = next(iter(self.wrappers.keys()))
            selected_wrapper = self.wrappers[selected_provider]
        else:
            raise ValueError("No LLM providers are available.")

        response_text, model_used = await selected_wrapper.generate_response(prompt, model=model, **kwargs)
        return response_text, selected_provider.value, model_used

    def get_available_providers(self) -> list[LLMProvider]:
        """
        Returns a list of available LLM providers.
        """
        return list(self.wrappers.keys())
