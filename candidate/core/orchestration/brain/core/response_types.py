"""
AI Response Data Structures

This module defines the response structures used throughout the AI system.
"""
from dataclasses import dataclass, field
from typing import Any

from .capability_levels import AGICapabilityLevel


@dataclass
class AGIResponse:
    """Response structure for AI processing results"""

    content: str
    confidence: float
    reasoning_path: list[dict] = field(default_factory=list)
    metacognitive_state: dict = field(default_factory=dict)
    ethical_compliance: dict = field(default_factory=dict)
    capability_level: AGICapabilityLevel = AGICapabilityLevel.BASIC
    processing_time: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


__all__ = ["AGIResponse"]