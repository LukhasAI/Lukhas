"""
Terminology normalization module
Compatibility shim for imports expecting lukhas.branding.terminology
"""

# Import from package __init__
from . import (
    APPROVED_TERMS,
    SYSTEM_NAME,
    normalize_chunk,
    normalize_output,
    validate_branding_compliance,
)

__all__ = [
    "APPROVED_TERMS",
    "SYSTEM_NAME",
    "normalize_chunk",
    "normalize_output",
    "validate_branding_compliance",
]