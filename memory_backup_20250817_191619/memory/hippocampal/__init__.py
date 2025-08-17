"""
Hippocampal Memory System
Fast episodic memory encoding with pattern separation and completion
"""

from .hippocampal_buffer import (
    EpisodicMemory,
    HippocampalBuffer,
    HippocampalState,
)
from .pattern_separator import PatternSeparator
from .theta_oscillator import OscillationPhase, ThetaOscillator

__all__ = [
    "HippocampalBuffer",
    "EpisodicMemory",
    "HippocampalState",
    "PatternSeparator",
    "ThetaOscillator",
    "OscillationPhase",
]
