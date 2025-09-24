#!/usr/bin/env python3
"""
LUKHAS Google AI Client Adapter
Production Schema v1.0.0

Google Gemini API client adapter with feature flag gating and production error handling.
"""

import os
import time
import asyncio
from typing import List, Optional, Dict, Any
import logging

from .base_client import BaseAIClient, AIResponse, AIProvider

logger = logging.getLogger(__name__)

# Feature flag to enable actual Google calls
ENABLE_GOOGLE_CALLS = os.getenv("LUKHAS_ENABLE_PROVIDER_CALLS", "0") == "1"


class GoogleClient(BaseAIClient):
    """Google Gemini API client adapter"""

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(AIProvider.GOOGLE, api_key, **kwargs)
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.project_id = kwargs.get("project_id", os.getenv("GOOGLE_PROJECT_ID"))

        # Available models
        self.models = [
            "gemini-pro",
            "gemini-pro-vision",
            "gemini-1.0-pro",
            "gemini-1.0-pro-vision"
        ]

        if ENABLE_GOOGLE_CALLS:
            try:
                import google.generativeai as genai
                self.genai = genai
                if self.api_key:
                    genai.configure(api_key=self.api_key)
                logger.info("Google AI client initialized with real API")
            except ImportError:
                logger.warning("Google AI package not installed - falling back to mock mode")
                self.genai = None
        else:
            logger.info("Google AI calls disabled by feature flag - using mock mode")
            self.genai = None

    async def generate(
        self,
        prompt: str,
        model: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """Generate response from Google Gemini API or mock"""

        if not ENABLE_GOOGLE_CALLS or not self.genai or not self.api_key:
            return await self._mock_generate(prompt, model, max_tokens, temperature, system_prompt, **kwargs)

        start_time = time.time()

        try:
            # Initialize the model
            ai_model = self.genai.GenerativeModel(model)

            # Prepare generation config
            generation_config = {}
            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens
            if temperature is not None:
                generation_config["temperature"] = temperature
            if "top_p" in kwargs:
                generation_config["top_p"] = kwargs["top_p"]
            if "top_k" in kwargs:
                generation_config["top_k"] = kwargs["top_k"]

            # Combine system prompt and user prompt if system prompt exists
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"

            # Generate response
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: ai_model.generate_content(
                    full_prompt,
                    generation_config=generation_config if generation_config else None
                )
            )

            latency_ms = (time.time() - start_time) * 1000

            # Extract response content
            content = response.text if response.text else ""

            # Extract usage information (if available)
            usage = {
                "prompt_tokens": response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else len(prompt.split()),
                "completion_tokens": response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else len(content.split()),
                "total_tokens": response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else len(prompt.split()) + len(content.split())
            }

            return AIResponse(
                content=content,
                provider=self.provider,
                model=model,
                latency_ms=latency_ms,
                usage=usage,
                metadata={
                    "google_response_id": getattr(response, 'response_id', None),
                    "google_model": model,
                    "finish_reason": getattr(response.candidates[0], 'finish_reason', 'stop') if response.candidates else 'stop',
                    "safety_ratings": [rating.__dict__ for rating in response.candidates[0].safety_ratings] if response.candidates and hasattr(response.candidates[0], 'safety_ratings') else []
                },
                finish_reason=getattr(response.candidates[0], 'finish_reason', 'stop') if response.candidates else 'stop'
            )

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"Google AI API error: {e}")

            # Fall back to mock response
            logger.warning("Falling back to mock response due to Google AI error")
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
        """Generate mock response when Google AI is disabled or unavailable"""

        start_time = time.time()

        # Simulate realistic Gemini API latency
        await asyncio.sleep(0.25 + (len(prompt) / 12000))  # 250ms base + length factor

        mock_content = f"[MOCK Google {model}] Gemini's response to: {prompt[:100]}..."
        if system_prompt:
            mock_content = f"[System context: {system_prompt[:50]}...] {mock_content}"

        # Gemini tends to be comprehensive and multimodal-aware
        mock_content += " This is a simulated response showcasing Gemini's comprehensive analysis capabilities."

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
                "feature_flag_enabled": ENABLE_GOOGLE_CALLS,
                "api_key_present": bool(self.api_key),
                "gemini_style": "comprehensive_multimodal"
            },
            finish_reason="stop"
        )

    async def health_check(self) -> bool:
        """Check Google AI API health"""
        if not ENABLE_GOOGLE_CALLS or not self.genai or not self.api_key:
            logger.info("Google AI health check: feature flag disabled or no API key")
            return True  # Mock is always healthy

        try:
            # Simple health check - list available models
            models = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: list(self.genai.list_models())
            )
            return len(models) > 0
        except Exception as e:
            logger.error(f"Google AI health check failed: {e}")
            return False

    def get_available_models(self) -> List[str]:
        """Get available Google AI models"""
        return self.models.copy()

    def estimate_cost(
        self,
        prompt: str,
        model: str,
        max_tokens: Optional[int] = None
    ) -> float:
        """Estimate cost for Google AI request"""
        if not ENABLE_GOOGLE_CALLS:
            return 0.0

        # Rough cost estimation for Google AI models (prices as of 2024)
        cost_per_1k_tokens = {
            "gemini-pro": 0.0005,  # Input tokens
            "gemini-pro-vision": 0.0025,
            "gemini-1.0-pro": 0.0005,
            "gemini-1.0-pro-vision": 0.0025
        }

        base_cost = cost_per_1k_tokens.get(model, 0.0005)
        prompt_tokens = len(prompt.split()) * 1.3  # Rough token estimation
        completion_tokens = max_tokens or 500

        total_cost = (prompt_tokens + completion_tokens) / 1000 * base_cost
        return round(total_cost, 4)