"""
LUKHAS AI Orchestration Module
Trinity Framework: ⚛️🧠🛡️

Orchestration system with integrated branding compliance for
multi-agent coordination and Trinity Framework decision making.
"""

# Import LUKHAS AI branding system for orchestration compliance
try:
    from lukhas.branding_bridge import (
        get_brand_voice, get_trinity_context, validate_output,
        BrandContext, normalize_output_text
    )
    ORCHESTRATION_BRANDING_AVAILABLE = True
except ImportError:
    ORCHESTRATION_BRANDING_AVAILABLE = False

__all__ = [
    # Branding integration
    "get_brand_voice",
    "get_trinity_context", 
    "validate_output",
    "BrandContext",
    "normalize_output_text",
    "ORCHESTRATION_BRANDING_AVAILABLE",
]
