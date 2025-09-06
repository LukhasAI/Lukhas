"""
Standalone SymbolicContext Enum for LUKHAS Consciousness System
==============================================================

This module provides the SymbolicContext enum without dependencies for easier importing.
"""

from enum import Enum


class SymbolicContext(Enum):
    """Context types for symbolic operations"""

    ANALYSIS = "analysis"
    INTENT_RESOLUTION = "intent_resolution"
    MEMORIA_RETRIEVAL = "memoria_retrieval"
    DREAM_REPLAY = "dream_replay"
    LEARNING_STRATEGY = "learning_strategy"
    ETHICAL_DECISION = "ethical_decision"
    SYMBOLIC_REASONING = "symbolic_reasoning"


class FeedbackType(Enum):
    """Types of symbolic feedback"""

    POSITIVE = "positive"
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    UNKNOWN = "unknown"
    REHEARSAL = "rehearsal"


# Export the main classes
__all__ = ["SymbolicContext", "FeedbackType"]
