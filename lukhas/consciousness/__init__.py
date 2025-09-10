"""
LUKHAS AI Consciousness Module
=============================

Production-safe consciousness interface with comprehensive safety measures.
Implements the Trinity Framework principles: ⚛️ Identity, 🧠 Consciousness, 🛡️ Guardian

This module provides controlled access to consciousness capabilities with:
- Feature flags for safe activation (dry-run by default)
- MATRIZ instrumentation for observability
- Guardian integration for ethical oversight
- Performance boundaries (<100ms responses)
- Drift detection and safety thresholds

Author: LUKHAS AI Consciousness Systems Architect
Version: 1.0.0
"""
import streamlit as st

from .consciousness_wrapper import (
    AwarenessLevel,
    ConsciousnessConfig,
    ConsciousnessState,
    ConsciousnessWrapper,
    SafetyMode,
)

# Alias for backward compatibility
ConsciousnessKernel = ConsciousnessWrapper
ConsciousnessModule = ConsciousnessWrapper  # Alias for RL integration

__all__ = [
    "AwarenessLevel",
    "ConsciousnessConfig",
    "ConsciousnessKernel",  # Alias
    "ConsciousnessModule",  # Alias for RL
    "ConsciousnessState",
    "ConsciousnessWrapper",
    "SafetyMode",
]

__version__ = "1.0.0"