"""
AI Capability Level Definitions

This module defines the different levels of AI capability that the system can achieve.
"""
from enum import Enum


class AGICapabilityLevel(Enum):
    """Defines different levels of AI capability"""

    BASIC = "basic_reasoning"
    ADVANCED = "advanced_symbolic"
    METACOGNITIVE = "metacognitive_aware"
    SELF_MODIFYING = "self_modifying"
    TRUE_AGI = "true_agi"


__all__ = ["AGICapabilityLevel"]