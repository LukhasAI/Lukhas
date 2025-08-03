"""
AI Response Data Structures

This module defines the response structures used throughout the AI system.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from .capability_levels import AGICapabilityLevel


@dataclass
class AGIResponse:
    """Response structure for AI processing results"""

    content: str
    confidence: float
    reasoning_path: List[Dict] = field(default_factory=list)
    metacognitive_state: Dict = field(default_factory=dict)
    ethical_compliance: Dict = field(default_factory=dict)
    capability_level: AGICapabilityLevel = AGICapabilityLevel.BASIC
    processing_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


__all__ = ["AGIResponse"]
