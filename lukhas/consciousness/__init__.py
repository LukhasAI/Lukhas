"""
LUKHAS AI Consciousness Module
=============================

Production-safe consciousness interface with comprehensive safety measures.
Implements the Constellation Framework principles: ⚛️ Anchor, ✦ Trail, 🔬 Horizon, 🛡️ Watch

This module provides controlled access to consciousness capabilities with:
- Feature flags for safe activation (dry-run by default)
- MATRIZ instrumentation for observability
- Guardian integration for ethical oversight
- Performance boundaries (<100ms responses)
- Drift detection and safety thresholds

The consciousness module coordinates across the 4-star Constellation Framework:
- ⚛️ Anchor Star: Identity-consciousness coupling and authentication
- ✦ Trail Star: Memory-consciousness integration and experience patterns
- 🔬 Horizon Star: Natural language consciousness interface
- 🛡️ Watch Star: Ethical oversight and consciousness validation

Author: LUKHAS AI Consciousness Systems Architect
Version: 2.0.0 (Constellation Framework)
"""

from .bio_integration import (
    BIO_CONSCIOUSNESS_MAP,
    BioAwareConsciousnessState,
    bio_feedback_loop,
)
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
    "BIO_CONSCIOUSNESS_MAP",
    "BioAwareConsciousnessState",
    "ConsciousnessConfig",
    "ConsciousnessKernel",  # Alias
    "ConsciousnessModule",  # Alias for RL
    "ConsciousnessState",
    "ConsciousnessWrapper",
    "SafetyMode",
    "bio_feedback_loop",
]

__version__ = "1.0.0"
