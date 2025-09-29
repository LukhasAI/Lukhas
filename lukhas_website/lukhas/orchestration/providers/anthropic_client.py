#!/usr/bin/env python3
"""
LUKHAS Anthropic Client Adapter
Production Schema v1.0.0

Anthropic Claude API client adapter with feature flag gating and production error handling.
"""

import os
import time
import asyncio
from typing import List, Optional
import logging

from .base_client import BaseAIClient, AIResponse, AIProvider

logger = logging.getLogger(__name__)

# Feature flag to enable actual Anthropic calls
ENABLE_ANTHROPIC_CALLS = os.getenv("LUKHAS_ENABLE_PROVIDER_CALLS", "0") == "1"


class AnthropicClient(BaseAIClient):
    """Anthropic Claude API client adapter"""

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(AIProvider.ANTHROPIC, api_key, **kwargs)
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.base_url = kwargs.get("base_url", "https://api.anthropic.com")

        # Available models
        self.models = [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-2.1",
            "claude-2.0"
        ]

        if ENABLE_ANTHROPIC_CALLS:
            try:
                import anthropic
                self.anthropic = anthropic.Anthropic(api_key=self.api_key) if self.api_key else None
                logger.info("Anthropic client initialized with real API")
            except ImportError:
                logger.warning("Anthropic package not installed - falling back to mock mode")
                self.anthropic = None
        else:
            logger.info("Anthropic calls disabled by feature flag - using mock mode")
            self.anthropic = None

    async def generate(
        self,
        prompt: str,
        model: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """Generate response from Anthropic Claude API or mock"""

        if not ENABLE_ANTHROPIC_CALLS or not self.anthropic or not self.api_key:
            return await self._mock_generate(prompt, model, max_tokens, temperature, system_prompt, **kwargs)

        start_time = time.time()

        try:
            # Prepare messages for Claude
            messages = [{"role": "user", "content": prompt}]

            # Prepare request parameters
            request_params = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens or 1000,
            }

            # Add system prompt if provided
            if system_prompt:
                request_params["system"] = system_prompt

            # Add temperature if provided
            if temperature is not None:
                request_params["temperature"] = temperature

            # Add any additional Anthropic-specific parameters
            if "top_p" in kwargs:
                request_params["top_p"] = kwargs["top_p"]
            if "top_k" in kwargs:
                request_params["top_k"] = kwargs["top_k"]

            # Make request to Anthropic
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.anthropic.messages.create(**request_params)
            )

            latency_ms = (time.time() - start_time) * 1000

            # Extract response content
            content = response.content[0].text if response.content else ""

            # Extract usage information
            usage = {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            }

            return AIResponse(
                content=content,
                provider=self.provider,
                model=model,
                latency_ms=latency_ms,
                usage=usage,
                metadata={
                    "anthropic_response_id": response.id,
                    "anthropic_model": response.model,
                    "stop_reason": response.stop_reason,
                    "stop_sequence": response.stop_sequence
                },
                finish_reason=response.stop_reason
            )

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"Anthropic API error: {e}")

            # Fall back to mock response
            logger.warning("Falling back to mock response due to Anthropic error")
            return await self._mock_generate(prompt, model, max_tokens, temperature, system_prompt, **kwargs)

    async def _mock_generate(
        self,
        prompt: str,
        model: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """Generate mock response when Anthropic is disabled or unavailable"""

        start_time = time.time()

        # Simulate realistic Claude API latency
        await asyncio.sleep(0.3 + (len(prompt) / 8000))  # 300ms base + length factor

        mock_content = f"[MOCK Anthropic {model}] Claude's response to: {prompt[:100]}..."
        if system_prompt:
            mock_content = f"[System guidance: {system_prompt[:50]}...] {mock_content}"

        # Claude tends to be more verbose
        mock_content += " This is a simulated response with Claude's characteristic thoughtfulness and detail."

        latency_ms = (time.time() - start_time) * 1000

        return AIResponse(
            content=mock_content,
            provider=self.provider,
            model=model,
            latency_ms=latency_ms,
            usage={
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(mock_content.split()),
                "total_tokens": len(prompt.split()) + len(mock_content.split())
            },
            metadata={
                "mock": True,
                "feature_flag_enabled": ENABLE_ANTHROPIC_CALLS,
                "api_key_present": bool(self.api_key),
                "claude_style": "thoughtful_detailed"
            },
            finish_reason="stop"
        )

    async def health_check(self) -> bool:
        """Check Anthropic API health"""
        if not ENABLE_ANTHROPIC_CALLS or not self.anthropic or not self.api_key:
            logger.info("Anthropic health check: feature flag disabled or no API key")
            return True  # Mock is always healthy

        try:
            # Simple health check - create a minimal request
            test_response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.anthropic.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=10,
                    messages=[{"role": "user", "content": "Hi"}]
                )
            )
            return bool(test_response)
        except Exception as e:
            logger.error(f"Anthropic health check failed: {e}")
            return False

    def get_available_models(self) -> List[str]:
        """Get available Anthropic models"""
        return self.models.copy()

    def estimate_cost(
        self,
        prompt: str,
        model: str,
        max_tokens: Optional[int] = None
    ) -> float:
        """Estimate cost for Anthropic request"""
        if not ENABLE_ANTHROPIC_CALLS:
            return 0.0

        # Rough cost estimation for Anthropic models (prices as of 2024)
        cost_per_1k_tokens = {
            "claude-3-opus-20240229": 0.015,  # Input tokens
            "claude-3-sonnet-20240229": 0.003,
            "claude-3-haiku-20240307": 0.00025,
            "claude-2.1": 0.008,
            "claude-2.0": 0.008
        }

        base_cost = cost_per_1k_tokens.get(model, 0.003)
        prompt_tokens = len(prompt.split()) * 1.3  # Rough token estimation
        completion_tokens = max_tokens or 500

        total_cost = (prompt_tokens + completion_tokens) / 1000 * base_cost
        return round(total_cost, 4)