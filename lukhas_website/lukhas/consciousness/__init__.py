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
    CreativitySnapshot,
    CreativeTask,

    # Enums
    StatePhase,
    DreamPhase,
    AwarenessLevel,
    AnomalySeverity,
    CreativeProcessType,
    CreativeFlowState,
    ImaginationMode,

    # Type aliases
    ConsciousnessEvent,
    EngineState,
    SignalData,

    # Configuration constants
    DEFAULT_AWARENESS_CONFIG,
    DEFAULT_REFLECTION_CONFIG,
    DEFAULT_DREAM_CONFIG,
    DEFAULT_CREATIVITY_CONFIG
)

from .awareness_engine import AwarenessEngine
from .creativity_engine import CreativityEngine
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
    "CreativityEngine",
    "DreamEngine",
    "AutoConsciousness",

    # Core data types
    "ConsciousnessState",
    "AwarenessSnapshot",
    "ReflectionReport",
    "CreativitySnapshot",
    "CreativeTask",
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
    "CreativeProcessType",
    "CreativeFlowState",
    "ImaginationMode",
    "ConsciousnessEvent",
    "EngineState",
    "SignalData",

    # Configuration
    "DEFAULT_AWARENESS_CONFIG",
    "DEFAULT_REFLECTION_CONFIG",
    "DEFAULT_DREAM_CONFIG",
    "DEFAULT_CREATIVITY_CONFIG",

    # Metadata
    "__version__",
    "__schema_version__",
    "__framework__"
]