#!/usr/bin/env python3
"""
LUKHAS OpenAI Client Adapter
Production Schema v1.0.0

OpenAI API client adapter with feature flag gating and production error handling.
"""

import asyncio
import logging
import os
import time
from typing import List, Optional

from .base_client import AIProvider, AIResponse, BaseAIClient

logger = logging.getLogger(__name__)

# Feature flag to enable actual OpenAI calls
ENABLE_OPENAI_CALLS = os.getenv("LUKHAS_ENABLE_PROVIDER_CALLS", "0") == "1"


class OpenAIClient(BaseAIClient):
    """OpenAI API client adapter"""

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(AIProvider.OPENAI, api_key, **kwargs)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = kwargs.get("base_url", "https://api.openai.com/v1")
        self.organization = kwargs.get("organization", os.getenv("OPENAI_ORGANIZATION"))

        # Available models
        self.models = ["gpt-4-turbo-preview", "gpt-4", "gpt-3.5-turbo", "gpt-3.5-turbo-16k"]

        if ENABLE_OPENAI_CALLS:
            try:
                import openai

                self.openai = openai
                if self.api_key:
                    self.openai.api_key = self.api_key
                if self.organization:
                    self.openai.organization = self.organization
                logger.info("OpenAI client initialized with real API")
            except ImportError:
                logger.warning("OpenAI package not installed - falling back to mock mode")
                self.openai = None
        else:
            logger.info("OpenAI calls disabled by feature flag - using mock mode")
            self.openai = None

    async def generate(
        self,
        prompt: str,
        model: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> AIResponse:
        """Generate response from OpenAI API or mock"""

        if not ENABLE_OPENAI_CALLS or not self.openai or not self.api_key:
            return await self._mock_generate(prompt, model, max_tokens, temperature, system_prompt, **kwargs)

        start_time = time.time()

        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            # Prepare OpenAI request
            request_params = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens or 1000,
                "temperature": temperature if temperature is not None else 0.7,
            }

            # Add any additional OpenAI-specific parameters
            if "top_p" in kwargs:
                request_params["top_p"] = kwargs["top_p"]
            if "frequency_penalty" in kwargs:
                request_params["frequency_penalty"] = kwargs["frequency_penalty"]
            if "presence_penalty" in kwargs:
                request_params["presence_penalty"] = kwargs["presence_penalty"]

            # Make async request to OpenAI
            response = await self.openai.ChatCompletion.acreate(**request_params)

            latency_ms = (time.time() - start_time) * 1000

            # Extract response content
            content = response.choices[0].message.content
            finish_reason = response.choices[0].finish_reason

            # Extract usage information
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }

            return AIResponse(
                content=content,
                provider=self.provider,
                model=model,
                latency_ms=latency_ms,
                usage=usage,
                metadata={
                    "openai_response_id": response.id,
                    "openai_model": response.model,
                    "created": response.created,
                },
                finish_reason=finish_reason,
            )

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"OpenAI API error: {e}")

            # For production, we could implement retry logic here
            # For now, fall back to mock response
            logger.warning("Falling back to mock response due to OpenAI error")
            return await self._mock_generate(prompt, model, max_tokens, temperature, system_prompt, **kwargs)

    async def _mock_generate(
        self,
        prompt: str,
        model: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> AIResponse:
        """Generate mock response when OpenAI is disabled or unavailable"""

        start_time = time.time()

        # Simulate realistic OpenAI API latency
        await asyncio.sleep(0.2 + (len(prompt) / 10000))  # 200ms base + length factor

        mock_content = f"[MOCK OpenAI {model}] Response to: {prompt[:100]}..."
        if system_prompt:
            mock_content = f"[System: {system_prompt[:50]}...] {mock_content}"

        latency_ms = (time.time() - start_time) * 1000

        return AIResponse(
            content=mock_content,
            provider=self.provider,
            model=model,
            latency_ms=latency_ms,
            usage={
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(mock_content.split()),
                "total_tokens": len(prompt.split()) + len(mock_content.split()),
            },
            metadata={"mock": True, "feature_flag_enabled": ENABLE_OPENAI_CALLS, "api_key_present": bool(self.api_key)},
            finish_reason="stop",
        )

    async def health_check(self) -> bool:
        """Check OpenAI API health"""
        if not ENABLE_OPENAI_CALLS or not self.openai or not self.api_key:
            logger.info("OpenAI health check: feature flag disabled or no API key")
            return True  # Mock is always healthy

        try:
            # Simple API call to check health
            response = await self.openai.Model.alist()
            return bool(response and response.get("data"))
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            return False

    def get_available_models(self) -> List[str]:
        """Get available OpenAI models"""
        return self.models.copy()

    def estimate_cost(self, prompt: str, model: str, max_tokens: Optional[int] = None) -> float:
        """Estimate cost for OpenAI request"""
        if not ENABLE_OPENAI_CALLS:
            return 0.0

        # Rough cost estimation for OpenAI models (prices as of 2024)
        cost_per_1k_tokens = {
            "gpt-4": 0.03,  # Input tokens
            "gpt-4-turbo-preview": 0.01,
            "gpt-3.5-turbo": 0.001,
            "gpt-3.5-turbo-16k": 0.003,
        }

        base_cost = cost_per_1k_tokens.get(model, 0.001)
        prompt_tokens = len(prompt.split()) * 1.3  # Rough token estimation
        completion_tokens = max_tokens or 500

        total_cost = (prompt_tokens + completion_tokens) / 1000 * base_cost
        return round(total_cost, 4)
