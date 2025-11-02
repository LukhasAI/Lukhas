#!/usr/bin/env python3
"""
LUKHAS Consciousness Module - Production Schema v1.0.0

Complete consciousness system implementation with awareness monitoring,
reflection processing, dream cycles, and autonomous decision-making.

Constellation Framework: Flow Star (🌊), Spark Star (⚡), Oracle Star (🔮)
"""

from .auto_consciousness import AutoConsciousness, GuardianResponse
from .awareness_engine import AwarenessEngine
from .consciousness_stream import ConsciousnessStream
from .creativity_engine import CreativityEngine
from .dream_engine import DreamEngine, DreamState
from .types import (
    # Configuration constants
    DEFAULT_AWARENESS_CONFIG,
    DEFAULT_CREATIVITY_CONFIG,
    DEFAULT_DREAM_CONFIG,
    DEFAULT_REFLECTION_CONFIG,
    AnomalySeverity,
    AwarenessLevel,
    AwarenessSnapshot,
    # Type aliases
    ConsciousnessEvent,
    ConsciousnessMetrics,
    # Core types
    ConsciousnessState,
    CreativeFlowState,
    CreativeProcessType,
    CreativeTask,
    CreativitySnapshot,
    DecisionContext,
    DreamPhase,
    DreamTrace,
    EngineState,
    ImaginationMode,
    ReflectionReport,
    SignalData,
    # Enums
    StatePhase,
)

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
    "__framework__",
]
