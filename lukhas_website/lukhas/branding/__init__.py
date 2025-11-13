"""
LUKHAS AI Branding Module

⚛️🧠🛡️ Constellation Framework: Identity-Consciousness-Guardian
Official branding, terminology, and symbolic vocabulary for LUKHAS consciousness systems.
"""

from __future__ import annotations

# Constellation Framework Symbols
TRINITY_IDENTITY = "⚛️"
TRINITY_CONSCIOUSNESS = "🧠"
TRINITY_GUARDIAN = "🛡️"

# Core LUKHAS Branding
LUKHAS_NAME = "LUKHAS AI"
LUKHAS_FULL_NAME = "Lukhas Universal Knowledge Harmonization and Adaptive Symbolic AI"

# Symbolic Vocabulary
LAMBDA_SYMBOLS = {
    "TRACE": "ΛTRACE",
    "ID": "ΛID",
    "MOOD": "ΛMOOD",
    "CALM": "ΛCALM",
    "HARMONY": "ΛHARMONY",
    "DISSONANCE": "ΛDISSONANCE",
    "DREAM": "ΛDREAM",
    "MEMORY": "ΛMEMORY",
}

# Brand Colors (as names for terminal output)
COLORS = {
    "primary": "blue",
    "secondary": "cyan",
    "accent": "green",
    "warning": "yellow",
    "error": "red",
    "consciousness": "purple",
}


# Core Module Information
def get_version():
    """Get LUKHAS version information."""
    return "1.0.0"


def get_triad_framework():
    """Get Constellation Framework description."""
    return f"{TRINITY_IDENTITY} Identity - {TRINITY_CONSCIOUSNESS} Consciousness - {TRINITY_GUARDIAN} Guardian"


def get_branding_info():
    """Get complete branding information."""
    return {
        "name": LUKHAS_NAME,
        "full_name": LUKHAS_FULL_NAME,
        "version": get_version(),
        "constellation": get_triad_framework(),
        "symbols": LAMBDA_SYMBOLS,
        "colors": COLORS,
    }


# Export key components
__all__ = [
    "COLORS",
    "LAMBDA_SYMBOLS",
    "LUKHAS_FULL_NAME",
    "LUKHAS_NAME",
    "TRINITY_CONSCIOUSNESS",
    "TRINITY_GUARDIAN",
    "TRINITY_IDENTITY",
    "get_branding_info",
    "get_triad_framework",
    "get_version",
]
