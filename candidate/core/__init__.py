"""
LUKHAS AI Core Module  
Trinity Framework: ⚛️🧠🛡️

Core system with integrated GLYPH-based Trinity Framework support
and branding compliance for symbolic communication.
"""

# Import LUKHAS AI branding system for core operations
try:
    from lukhas.branding_bridge import (
        get_trinity_context, TRINITY_FRAMEWORK,
        IDENTITY_SYMBOL, CONSCIOUSNESS_SYMBOL, GUARDIAN_SYMBOL
    )
    CORE_BRANDING_AVAILABLE = True
except ImportError:
    CORE_BRANDING_AVAILABLE = False
    # Fallback Trinity symbols
    TRINITY_FRAMEWORK = "⚛️🧠🛡️"
    IDENTITY_SYMBOL = "⚛️"
    CONSCIOUSNESS_SYMBOL = "🧠"
    GUARDIAN_SYMBOL = "🛡️"

__all__ = [
    # Trinity Framework integration
    "get_trinity_context",
    "TRINITY_FRAMEWORK",
    "IDENTITY_SYMBOL",
    "CONSCIOUSNESS_SYMBOL", 
    "GUARDIAN_SYMBOL",
    "CORE_BRANDING_AVAILABLE",
]
