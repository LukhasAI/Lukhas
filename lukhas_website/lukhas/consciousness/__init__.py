#!/usr/bin/env python3
"""
LUKHAS Consciousness Module - Production Schema v1.0.0

Complete consciousness system implementation with awareness monitoring,
reflection processing, dream cycles, and autonomous decision-making.

This module serves as the production wrapper for consciousness functionality.
Feature flag control is handled by lukhas.core.initialization - this module
should only be imported after initialization with CONSCIOUSNESS_ENABLED=true.

Constellation Framework: Flow Star (🌊), Spark Star (⚡), Oracle Star (🔮)
"""

import os
from typing import Any, Optional

# Feature flag (for reference - actual control in initialization.py)
CONSCIOUSNESS_ENABLED = os.environ.get("CONSCIOUSNESS_ENABLED", "false").lower() in ("true", "1", "yes", "on")

# Core imports - always available for type hints and initialization
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

# Lazy-loaded engine instances
_consciousness_stream: Optional[ConsciousnessStream] = None
_awareness_engine: Optional[AwarenessEngine] = None
_creativity_engine: Optional[CreativityEngine] = None
_dream_engine: Optional[DreamEngine] = None


def get_consciousness_stream(config: Optional[dict[str, Any]] = None) -> ConsciousnessStream:
    """
    Get or create consciousness stream instance (singleton pattern).

    Args:
        config: Optional configuration dict

    Returns:
        ConsciousnessStream instance

    Raises:
        RuntimeError: If consciousness not enabled
    """
    global _consciousness_stream

    if not CONSCIOUSNESS_ENABLED:
        raise RuntimeError("Consciousness not enabled (set CONSCIOUSNESS_ENABLED=true)")

    if _consciousness_stream is None:
        _consciousness_stream = ConsciousnessStream(config=config)

    return _consciousness_stream


def get_awareness_engine(config: Optional[dict[str, Any]] = None) -> AwarenessEngine:
    """
    Get or create awareness engine instance (singleton pattern).

    Args:
        config: Optional configuration dict

    Returns:
        AwarenessEngine instance

    Raises:
        RuntimeError: If consciousness not enabled
    """
    global _awareness_engine

    if not CONSCIOUSNESS_ENABLED:
        raise RuntimeError("Consciousness not enabled (set CONSCIOUSNESS_ENABLED=true)")

    if _awareness_engine is None:
        _awareness_engine = AwarenessEngine(config=config)

    return _awareness_engine


def get_creativity_engine(config: Optional[dict[str, Any]] = None) -> CreativityEngine:
    """
    Get or create creativity engine instance (singleton pattern).

    Args:
        config: Optional configuration dict

    Returns:
        CreativityEngine instance

    Raises:
        RuntimeError: If consciousness not enabled
    """
    global _creativity_engine

    if not CONSCIOUSNESS_ENABLED:
        raise RuntimeError("Consciousness not enabled (set CONSCIOUSNESS_ENABLED=true)")

    if _creativity_engine is None:
        _creativity_engine = CreativityEngine(config=config)

    return _creativity_engine


def get_dream_engine(config: Optional[dict[str, Any]] = None) -> DreamEngine:
    """
    Get or create dream engine instance (singleton pattern).

    Args:
        config: Optional configuration dict

    Returns:
        DreamEngine instance

    Raises:
        RuntimeError: If consciousness not enabled
    """
    global _dream_engine

    if not CONSCIOUSNESS_ENABLED:
        raise RuntimeError("Consciousness not enabled (set CONSCIOUSNESS_ENABLED=true)")

    if _dream_engine is None:
        _dream_engine = DreamEngine(config=config)

    return _dream_engine


# Version information
__version__ = "1.0.0"
__schema_version__ = "1.0.0"
__framework__ = "Constellation Framework - Flow Star (🌊)"

# Export all public interfaces
__all__ = [
    # Configuration
    "DEFAULT_AWARENESS_CONFIG",
    "DEFAULT_CREATIVITY_CONFIG",
    "DEFAULT_DREAM_CONFIG",
    "DEFAULT_REFLECTION_CONFIG",
    # Feature flag
    "CONSCIOUSNESS_ENABLED",
    "AnomalySeverity",
    "AutoConsciousness",
    # Core engines (classes for direct instantiation)
    "AwarenessEngine",
    "AwarenessLevel",
    "AwarenessSnapshot",
    "ConsciousnessEvent",
    "ConsciousnessMetrics",
    # Core data types
    "ConsciousnessState",
    # Main consciousness stream
    "ConsciousnessStream",
    "CreativeFlowState",
    "CreativeProcessType",
    "CreativeTask",
    "CreativityEngine",
    "CreativitySnapshot",
    "DecisionContext",
    "DreamEngine",
    "DreamPhase",
    "DreamState",
    "DreamTrace",
    "EngineState",
    # Wrapper functions (recommended for production use)
    "get_awareness_engine",
    "get_consciousness_stream",
    "get_creativity_engine",
    "get_dream_engine",
    # Supporting types
    "GuardianResponse",
    "ImaginationMode",
    "ReflectionReport",
    "SignalData",
    # Type definitions
    "StatePhase",
    "__framework__",
    "__schema_version__",
    # Metadata
    "__version__"
]
