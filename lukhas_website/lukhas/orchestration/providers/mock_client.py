#!/usr/bin/env python3
"""
LUKHAS Mock AI Client
Production Schema v1.0.0

Mock AI client for testing and development with realistic response patterns.
"""

import asyncio
import hashlib
import time
from typing import Optional

from .base_client import AIProvider, AIResponse, BaseAIClient


class MockAIClient(BaseAIClient):
    """Mock AI client for testing and development"""

    def __init__(self, **kwargs):
        super().__init__(AIProvider.MOCK, **kwargs)
        self.models = [
            "mock-gpt-4",
            "mock-gpt-3.5-turbo",
            "mock-claude-3",
            "mock-gemini-pro"
        ]

    async def generate(
        self,
        prompt: str,
        model: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """Generate mock response with realistic timing"""

        start_time = time.time()

        # Simulate realistic API latency based on prompt length
        base_latency = 0.1  # 100ms base latency
        length_factor = len(prompt) / 1000  # Additional latency based on prompt length
        simulated_latency = base_latency + (length_factor * 0.05)

        await asyncio.sleep(min(simulated_latency, 2.0))  # Cap at 2 seconds

        # Generate deterministic response based on prompt hash for consistency
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
        response_seed = int(prompt_hash[:8], 16) % 1000

        # Mock response templates
        response_templates = [
            f"Mock response from {model}: I understand your request about '{prompt[:50]}...' and here's my analysis.",
            f"Based on the prompt '{prompt[:30]}...', I can provide the following insights from {model}.",
            f"Processing request via {model}: {prompt[:40]}... [Mock implementation]",
            f"Mock {model} response: This is a simulated response for testing purposes.",
        ]

        response_content = response_templates[response_seed % len(response_templates)]

        # Add some variation based on model
        if "gpt-4" in model:
            response_content += " [GPT-4 enhanced reasoning]"
        elif "claude" in model:
            response_content += " [Claude analytical approach]"
        elif "gemini" in model:
            response_content += " [Gemini multimodal capabilities]"

        latency_ms = (time.time() - start_time) * 1000

        return AIResponse(
            content=response_content,
            provider=self.provider,
            model=model,
            latency_ms=latency_ms,
            usage={
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(response_content.split()),
                "total_tokens": len(prompt.split()) + len(response_content.split())
            },
            metadata={
                "mock": True,
                "response_seed": response_seed,
                "simulated_latency": simulated_latency
            },
            finish_reason="stop"
        )

    async def health_check(self) -> bool:
        """Mock health check - always healthy"""
        await asyncio.sleep(0.01)  # Minimal latency
        return True

    def get_available_models(self) -> list[str]:
        """Return available mock models"""
        return self.models.copy()

    async def batch_generate(
        self,
        prompts: list[str],
        model: str,
        **kwargs
    ) -> list[AIResponse]:
        """Mock batch generation with parallel processing simulation"""
        tasks = [
            self.generate(prompt, model, **kwargs)
            for prompt in prompts
        ]
        return await asyncio.gather(*tasks)

    def estimate_cost(
        self,
        prompt: str,
        model: str,
        max_tokens: Optional[int] = None
    ) -> float:
        """Mock cost estimation - always free"""
        return 0.0
