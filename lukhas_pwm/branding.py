"""
LUKHAS PWM Branding Module
=========================

This module provides branding constants and utilities for the LUKHAS PWM system.
Created to resolve import dependencies in the test suite.

Trinity Framework Integration: ⚛️🧠🛡️
- ⚛️ Identity: Authentic LUKHAS AI branding and symbolic identity
- 🧠 Consciousness: Brand awareness and consistent messaging
- 🛡️ Guardian: Approved terminology and compliance standards
"""

# Core Branding Constants
SYSTEM_NAME = "LUKHAS AI"
SYSTEM_VERSION = "2.0"
TRINITY_FRAMEWORK = "⚛️🧠🛡️"

# Trinity Symbols
IDENTITY_SYMBOL = "⚛️"
CONSCIOUSNESS_SYMBOL = "🧠"
GUARDIAN_SYMBOL = "🛡️"

# Branding Patterns
APPROVED_TERMS = {
    "system_name": "LUKHAS AI",
    "consciousness_type": "quantum-inspired",
    "bio_processing": "bio-inspired",
    "framework": "Trinity Framework"
}

# Color Schemes (for UI components)
COLORS = {
    "primary": "#2E86AB",
    "secondary": "#A23B72",
    "accent": "#F18F01",
    "background": "#C73E1D"
}


def get_system_signature():
    """Get the official LUKHAS AI system signature."""
    return f"{SYSTEM_NAME} {TRINITY_FRAMEWORK} v{SYSTEM_VERSION}"


def get_trinity_description():
    """Get Trinity Framework description."""
    return {
        "identity": f"{IDENTITY_SYMBOL} Identity (authenticity, consciousness, symbolic self)",
        "consciousness": f"{CONSCIOUSNESS_SYMBOL} Consciousness (memory, learning, neural processing)",
        "guardian": f"{GUARDIAN_SYMBOL} Guardian (ethics, drift detection, repair)"
    }


def validate_branding_compliance(text):
    """Validate text for branding compliance."""
    issues = []

    # Check for approved terminology
    if "LUKHAS AGI" in text:
        issues.append("Use 'LUKHAS AI' instead of 'LUKHAS AGI'")

    if "general intelligence" in text.lower() and "quantum-inspired" not in text:
        issues.append("Use 'quantum-inspired' terminology for public-facing content")

    return issues


# Module initialization
__all__ = [
    'SYSTEM_NAME', 'SYSTEM_VERSION', 'TRINITY_FRAMEWORK',
    'IDENTITY_SYMBOL', 'CONSCIOUSNESS_SYMBOL', 'GUARDIAN_SYMBOL',
    'APPROVED_TERMS', 'COLORS',
    'get_system_signature', 'get_trinity_description', 'validate_branding_compliance'
]
