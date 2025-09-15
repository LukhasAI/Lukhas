"""
LUKHAS AI Bridge Module
Trinity Framework: ⚛️🧠🛡️

Bridge system with integrated branding compliance for external
communications and API responses with consistent brand voice.
"""
# Import LUKHAS AI branding system for bridge operations
try:
    from lukhas.branding_bridge import (
        BrandContext,
        get_brand_voice,
        normalize_output_text,
        validate_output,
    )

    BRIDGE_BRANDING_AVAILABLE = True
except ImportError:
    BRIDGE_BRANDING_AVAILABLE = False

__all__ = [
    "BRIDGE_BRANDING_AVAILABLE",
    "BrandContext",
    # Branding integration
    "get_brand_voice",
    "normalize_output_text",
    "validate_output",
]
