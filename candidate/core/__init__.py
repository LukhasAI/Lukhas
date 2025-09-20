"""
LUKHAS AI Core Module
Constellation Framework: ⚛️🧠🛡️

Core system with integrated GLYPH-based Constellation Framework support
and branding compliance for symbolic communication.
"""
import streamlit as st

# Import LUKHAS AI branding system for core operations
try:
    from lukhas.branding_bridge import (
        CONSCIOUSNESS_SYMBOL,
        GUARDIAN_SYMBOL,
        IDENTITY_SYMBOL,
        CONSTELLATION_FRAMEWORK,
        get_constellation_context,
    )

    CORE_BRANDING_AVAILABLE = True
except ImportError:
    CORE_BRANDING_AVAILABLE = False
    # Fallback Trinity symbols
    CONSTELLATION_FRAMEWORK = "⚛️🧠🛡️"
    IDENTITY_SYMBOL = "⚛️"
    CONSCIOUSNESS_SYMBOL = "🧠"
    GUARDIAN_SYMBOL = "🛡️"

# Core business platform
from . import business

__all__ = [
    "CONSCIOUSNESS_SYMBOL",
    "CORE_BRANDING_AVAILABLE",
    "GUARDIAN_SYMBOL",
    "IDENTITY_SYMBOL",
    "CONSTELLATION_FRAMEWORK",
    # Business modules
    "business",
    # Constellation Framework integration
    "get_constellation_context",
]
