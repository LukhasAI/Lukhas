"""
LUKHAS AI - AI Provider Enumeration
==================================

AI provider types for orchestration system.

Copyright (c) 2025 LUKHAS AI. All rights reserved.
"""

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel


class AIProvider(Enum):
    """Enumeration of supported AI providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    PERPLEXITY = "perplexity"
    LOCAL = "local"

    @classmethod
    def from_string(cls, provider: str) -> "AIProvider":
        """Convert string to AIProvider enum."""
        provider_map = {
            "openai": cls.OPENAI,
            "anthropic": cls.ANTHROPIC,
            "claude": cls.ANTHROPIC,  # Alias
            "google": cls.GOOGLE,
            "gemini": cls.GOOGLE,  # Alias
            "perplexity": cls.PERPLEXITY,
            "local": cls.LOCAL,
        }
        return provider_map.get(provider.lower(), cls.OPENAI)


class TaskType(Enum):
    """Enumeration of supported task types."""

    CHAT_COMPLETION = "chat_completion"
    TEXT_GENERATION = "text_generation"
    CODE_GENERATION = "code_generation"
    ANALYSIS = "analysis"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    QUESTION_ANSWERING = "question_answering"
    CONSCIOUSNESS_QUERY = "consciousness_query"

    @classmethod
    def from_string(cls, task_type: str) -> "TaskType":
        """Convert string to TaskType enum."""
        task_map = {
            "chat": cls.CHAT_COMPLETION,
            "chat_completion": cls.CHAT_COMPLETION,
            "text": cls.TEXT_GENERATION,
            "text_generation": cls.TEXT_GENERATION,
            "code": cls.CODE_GENERATION,
            "code_generation": cls.CODE_GENERATION,
            "analysis": cls.ANALYSIS,
            "summarization": cls.SUMMARIZATION,
            "summary": cls.SUMMARIZATION,  # Alias
            "translation": cls.TRANSLATION,
            "translate": cls.TRANSLATION,  # Alias
            "qa": cls.QUESTION_ANSWERING,
            "question_answering": cls.QUESTION_ANSWERING,
            "consciousness": cls.CONSCIOUSNESS_QUERY,
            "consciousness_query": cls.CONSCIOUSNESS_QUERY,
        }
        return task_map.get(task_type.lower(), cls.CHAT_COMPLETION)


class OrchestrationRequest(BaseModel):
    """Request model for AI orchestration."""

    task_type: TaskType = TaskType.CHAT_COMPLETION
    provider: Optional[AIProvider] = None
    content: str
    context: Optional[dict[str, Any]] = None
    parameters: Optional[dict[str, Any]] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None

    class Config:
        use_enum_values = True

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OrchestrationRequest":
        """Create request from dictionary."""
        # Convert string enums to enum objects
        if "task_type" in data and isinstance(data["task_type"], str):
            data["task_type"] = TaskType.from_string(data["task_type"])

        if "provider" in data and isinstance(data["provider"], str):
            data["provider"] = AIProvider.from_string(data["provider"])

        return cls(**data)


class OrchestrationResponse(BaseModel):
    """Response model for AI orchestration."""

    content: str
    provider: AIProvider
    task_type: TaskType
    latency_ms: float
    token_count: Optional[int] = None
    cost_estimate: Optional[float] = None
    metadata: Optional[dict[str, Any]] = None
    error: Optional[str] = None

    class Config:
        use_enum_values = True
