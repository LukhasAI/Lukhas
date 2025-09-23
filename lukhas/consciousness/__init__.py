#!/usr/bin/env python3
"""
LUKHAS Consciousness Module - Production Schema v1.0.0

Complete consciousness system implementation with awareness monitoring,
reflection processing, dream cycles, and autonomous decision-making.

Constellation Framework: Flow Star (🌊), Spark Star (⚡), Oracle Star (🔮)
"""

from .types import (
    # Core types
    ConsciousnessState,
    AwarenessSnapshot,
    ReflectionReport,
    DreamTrace,
    DecisionContext,
    ConsciousnessMetrics,

    # Enums
    StatePhase,
    DreamPhase,
    AwarenessLevel,
    AnomalySeverity,

    # Type aliases
    ConsciousnessEvent,
    EngineState,
    SignalData,

    # Configuration constants
    DEFAULT_AWARENESS_CONFIG,
    DEFAULT_REFLECTION_CONFIG,
    DEFAULT_DREAM_CONFIG
)

from .awareness_engine import AwarenessEngine
from .dream_engine import DreamEngine, DreamState
from .auto_consciousness import AutoConsciousness, GuardianResponse
from .consciousness_stream import ConsciousnessStream

# Version information
__version__ = "1.0.0"
__schema_version__ = "1.0.0"
__framework__ = "Constellation Framework - Flow Star (🌊)"

# Export all public interfaces
__all__ = [
    # Main consciousness stream
    "ConsciousnessStream",

    # Core engines
    "AwarenessEngine",
    "DreamEngine",
    "AutoConsciousness",

    # Core data types
    "ConsciousnessState",
    "AwarenessSnapshot",
    "ReflectionReport",
    "DreamTrace",
    "DecisionContext",
    "ConsciousnessMetrics",

    # Supporting types
    "GuardianResponse",
    "DreamState",

    # Type definitions
    "StatePhase",
    "DreamPhase",
    "AwarenessLevel",
    "AnomalySeverity",
    "ConsciousnessEvent",
    "EngineState",
    "SignalData",

    # Configuration
    "DEFAULT_AWARENESS_CONFIG",
    "DEFAULT_REFLECTION_CONFIG",
    "DEFAULT_DREAM_CONFIG",

    # Metadata
    "__version__",
    "__schema_version__",
    "__framework__"
]