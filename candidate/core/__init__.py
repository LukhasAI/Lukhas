"""
LUKHAS AI Core Module
Trinity Framework: ⚛️🧠🛡️

Core system with integrated GLYPH-based Trinity Framework support
and branding compliance for symbolic communication.
"""

# Import LUKHAS AI branding system for core operations
try:
    from lukhas.branding_bridge import (
        CONSCIOUSNESS_SYMBOL,
        GUARDIAN_SYMBOL,
        IDENTITY_SYMBOL,
        TRINITY_FRAMEWORK,
        get_triad_context,
    )

    CORE_BRANDING_AVAILABLE = True
except ImportError:
    CORE_BRANDING_AVAILABLE = False
    # Fallback Trinity symbols
    TRINITY_FRAMEWORK = "⚛️🧠🛡️"
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
    "TRINITY_FRAMEWORK",
    # Business modules
    "business",
    # Trinity Framework integration
    "get_triad_context",
]
