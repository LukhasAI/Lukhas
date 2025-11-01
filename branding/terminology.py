"""
Terminology normalization module
Compatibility shim for imports expecting branding.terminology
"""

# Import from package __init__ when available, otherwise fall back to the labs
# branding module directly (avoids circular import issues when the shim is
# resolving its backend).
try:
    from . import (
        APPROVED_TERMS,
        SYSTEM_NAME,
        normalize_chunk,
        normalize_output,
        validate_branding_compliance,
    )
except ImportError:  # pragma: no cover - executed in degraded environments
    from labs.branding import (  # type: ignore
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
