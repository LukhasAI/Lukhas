#!/usr/bin/env python3
"""
LUKHAS Base AI Client
Production Schema v1.0.0

Abstract base class for all AI provider clients with standardized interface.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class AIProvider(Enum):
    """AI Provider enumeration"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    MOCK = "mock"


@dataclass
class AIResponse:
    """Standardized AI response format"""
    content: str
    provider: AIProvider
    model: str
    latency_ms: float
    usage: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    finish_reason: Optional[str] = None


@dataclass
class AIError:
    """AI provider error information"""
    provider: AIProvider
    model: str
    error_code: str
    error_message: str
    is_retryable: bool = False
    retry_after: Optional[float] = None


class BaseAIClient(ABC):
    """Abstract base class for AI provider clients"""

    def __init__(self, provider: AIProvider, api_key: Optional[str] = None, **kwargs):
        self.provider = provider
        self.api_key = api_key
        self.config = kwargs
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the client (async setup if needed)"""
        self._initialized = True

    @property
    def is_initialized(self) -> bool:
        """Check if client is initialized"""
        return self._initialized

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        model: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """Generate response from AI model"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is healthy and accessible"""
        pass

    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models for this provider"""
        pass

    async def batch_generate(
        self,
        prompts: List[str],
        model: str,
        **kwargs
    ) -> List[AIResponse]:
        """Generate responses for multiple prompts (default sequential implementation)"""
        responses = []
        for prompt in prompts:
            response = await self.generate(prompt, model, **kwargs)
            responses.append(response)
        return responses

    def estimate_cost(
        self,
        prompt: str,
        model: str,
        max_tokens: Optional[int] = None
    ) -> float:
        """Estimate cost for a request (provider-specific implementation)"""
        return 0.0  # Default implementation

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(provider={self.provider.value})"
