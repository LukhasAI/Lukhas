"""
Terminology normalization module
Compatibility shim for imports expecting lukhas_pwm.branding.terminology
"""

# Import from package __init__
from . import (
    normalize_output,
    normalize_chunk,
    validate_branding_compliance,
    APPROVED_TERMS,
    SYSTEM_NAME,
)

__all__ = [
    "normalize_output",
    "normalize_chunk",
    "validate_branding_compliance",
    "APPROVED_TERMS",
    "SYSTEM_NAME",
]