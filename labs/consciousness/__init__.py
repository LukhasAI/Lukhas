"""
LUKHAS AI Consolidated Consciousness Module

This module consolidates all consciousness-related components:
- Core consciousness logic
- API interfaces
- Bridge modules
- Processing engines
- Consciousness layers
- Stream processors
- Colony systems
"""

import contextlib

import streamlit as st

# Version info
__version__ = "2.0.0"
__author__ = "LUKHAS AI Team"

# Import core components
try:
    from .core import ConsciousnessCore
except ImportError:
    ConsciousnessCore = None

# Import API components
try:
    from .api.core import ConsciousnessAPI
except ImportError:
    ConsciousnessAPI = None

# Import bridges
try:
    from .bridges.core import CoreConsciousnessBridge
    from .bridges.memory import MemoryConsciousnessBridge
    from .bridges.quantum import QIConsciousnessBridge
except ImportError:
    pass

# Import engines
with contextlib.suppress(ImportError):
    from .engines.expansion import ExpansionEngine

# Import LUKHAS AI branding system for consciousness outputs
try:
    from branding_bridge import (
        BrandContext,
        get_brand_voice,
        get_constellation_context,
    )

    CONSCIOUSNESS_BRANDING_AVAILABLE = True
except ImportError:
    CONSCIOUSNESS_BRANDING_AVAILABLE = False

__all__ = [
    "CONSCIOUSNESS_BRANDING_AVAILABLE",
    "BrandContext",
    "ConsciousnessAPI",
    "ConsciousnessCore",
    "CoreConsciousnessBridge",
    "ExpansionEngine",
    "MemoryConsciousnessBridge",
    "QIConsciousnessBridge",
    # Branding integration
    "get_brand_voice",
    "get_constellation_context",
]
