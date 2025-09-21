"""
LUKHAS  Branding Module
=========================

This module provides branding constants and utilities for the LUKHAS  system.
Created to resolve import dependencies in the test suite.

Constellation Framework Integration: ⚛️🧠🛡️
- ⚛️ Identity: Authentic LUKHAS AI branding and symbolic identity
- 🧠 Consciousness: Brand awareness and consistent messaging
- 🛡️ Guardian: Approved terminology and compliance standards
"""
import re
from typing import Optional

import streamlit as st

# Core Branding Constants
SYSTEM_NAME = "LUKHAS AI"
SYSTEM_VERSION = "2.0"
CONSTELLATION_FRAMEWORK = "⚛️🧠🛡️"

# Constellation Symbols
IDENTITY_SYMBOL = "⚛️"
CONSCIOUSNESS_SYMBOL = "🧠"
GUARDIAN_SYMBOL = "🛡️"

# Branding Patterns
APPROVED_TERMS = {
    "system_name": "LUKHAS AI",
    "consciousness_type": "quantum-inspired",
    "bio_processing": "bio-inspired",
    "framework": "Constellation Framework",
}

# Color Schemes (for UI components)
COLORS = {
    "primary": "#2E86AB",
    "secondary": "#A23B72",
    "accent": "#F18F01",
    "background": "#C73E1D",
}

# Terminology normalization patterns
_REPLACEMENTS: tuple[tuple[re.Pattern[str], str], ...] = (
    # Lukhas Cognitive AI -> Lukhas AI (various caseings)
    (re.compile(r"\bLUKHAS\s+Cognitive AI\b", re.IGNORECASE), "LUKHAS AI"),
    # quantum process family -> quantum-inspired
    (
        re.compile(
            r"\bquantum[\s-]?(?:process|processes|processing|proccess|proccesses)\b",
            re.IGNORECASE,
        ),
        "quantum-inspired",
    ),
    # Standalone 'quantum' should default to 'quantum-inspired' unless explicitly
    # followed by accepted qualifiers (inspired, metaphor/metaphors)
    (
        re.compile(
            r"\bquantum\b(?![\s-]?(?:inspired|metaphor|metaphors))",
            re.IGNORECASE,
        ),
        "quantum-inspired",
    ),
    # bio process family -> bio-inspired
    (
        re.compile(
            r"\bbio[\s-]?(?:process|processes|processing)\b",
            re.IGNORECASE,
        ),
        "bio-inspired",
    ),
)


def get_system_signature():
    """Get the official LUKHAS AI system signature."""
    return f"{SYSTEM_NAME} {CONSTELLATION_FRAMEWORK} v{SYSTEM_VERSION}"


def get_constellation_description():
    """Get Constellation Framework description."""
    return {
        "identity": f"{IDENTITY_SYMBOL} Identity (authenticity, consciousness, symbolic self)",
        "consciousness": f"{CONSCIOUSNESS_SYMBOL} Consciousness (memory, learning, neural processing)",
        "guardian": f"{GUARDIAN_SYMBOL} Guardian (ethics, drift detection, repair)",
    }


def validate_branding_compliance(text):
    """Validate text for branding compliance."""
    issues = []

    # Check for approved terminology
    if "LUKHAS Cognitive AI" in text:
        issues.append("Use 'LUKHAS AI' instead of 'LUKHAS Cognitive AI'")

    if "general intelligence" in text.lower() and "quantum-inspired" not in text:
        issues.append("Use 'quantum-inspired' terminology for public-facing content")

    return issues


def normalize_output(text: Optional[str]) -> Optional[str]:
    """Apply terminology normalization to plain text.

    Returns the original text if None or not a str.
    """
    if not isinstance(text, str):
        return text
    out = text
    for pat, repl in _REPLACEMENTS:
        out = pat.sub(repl, out)
    # Preserve casing for 'LUKHAS' if it was originally uppercase in the segment.
    # Simple heuristic: if 'LUKHAS' present with AI/Cognitive AI, re-upcase.
    out = re.sub(r"\bLukhas AI\b", "LUKHAS AI", out) if "LUKHAS" in text else out
    return out


def normalize_chunk(chunk: str) -> str:
    """Chunk-safe normalization for streaming; best-effort per chunk.

    Note: boundary-spanning phrases might escape normalization.
    """
    return normalize_output(chunk) or ""


# Module initialization
__all__ = [
    "APPROVED_TERMS",
    "COLORS",
    "CONSCIOUSNESS_SYMBOL",
    "GUARDIAN_SYMBOL",
    "IDENTITY_SYMBOL",
    "SYSTEM_NAME",
    "SYSTEM_VERSION",
    "CONSTELLATION_FRAMEWORK",
    "get_system_signature",
    "get_constellation_description",
    "normalize_chunk",
    "normalize_output",
    "validate_branding_compliance",
]
