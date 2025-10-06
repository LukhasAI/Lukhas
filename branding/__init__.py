"""
LUKHAS Branding - Canonical Public API
Bridge to candidate.branding (single source of truth)

Constellation Framework Integration: ⚛️🧠🛡️
- ⚛️ Identity: Authentic LUKHAS AI branding and symbolic identity
- 🧠 Consciousness: Brand awareness and consistent messaging
- 🛡️ Guardian: Approved terminology and compliance standards
"""
from candidate.branding import (
    APPROVED_TERMS,
    COLORS,
    CONSCIOUSNESS_SYMBOL,
    CONSTELLATION_FRAMEWORK,
    GUARDIAN_SYMBOL,
    IDENTITY_SYMBOL,
    SYSTEM_NAME,
    SYSTEM_VERSION,
    get_constellation_description,
    get_system_signature,
    normalize_chunk,
    normalize_output,
    validate_branding_compliance,
)

__all__ = [
    "APPROVED_TERMS",
    "COLORS",
    "CONSCIOUSNESS_SYMBOL",
    "CONSTELLATION_FRAMEWORK",
    "GUARDIAN_SYMBOL",
    "IDENTITY_SYMBOL",
    "SYSTEM_NAME",
    "SYSTEM_VERSION",
    "get_constellation_description",
    "get_system_signature",
    "normalize_chunk",
    "normalize_output",
    "validate_branding_compliance",
]
