"""
LUKHAS AI Bridge Module
Trinity Framework: ⚛️🧠🛡️

Bridge system with integrated branding compliance for external
communications and API responses with consistent brand voice.
"""

# Import LUKHAS AI branding system for bridge operations
try:
    from lukhas.branding_bridge import (
        get_brand_voice, validate_output, normalize_output_text,
        BrandContext
    )
    BRIDGE_BRANDING_AVAILABLE = True
except ImportError:
    BRIDGE_BRANDING_AVAILABLE = False

__all__ = [
    # Branding integration
    "get_brand_voice",
    "validate_output",
    "normalize_output_text",
    "BrandContext",
    "BRIDGE_BRANDING_AVAILABLE",
]
