"""
Terminology normalization module
Compatibility shim for imports expecting branding.terminology
"""

import importlib as _importlib

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
    try:
        _mod = _importlib.import_module("labs.branding")
        APPROVED_TERMS = _mod.APPROVED_TERMS
        SYSTEM_NAME = _mod.SYSTEM_NAME
        normalize_chunk = _mod.normalize_chunk
        normalize_output = _mod.normalize_output
        validate_branding_compliance = _mod.validate_branding_compliance
    except Exception:
        raise

__all__ = [
    "APPROVED_TERMS",
    "SYSTEM_NAME",
    "normalize_chunk",
    "normalize_output",
    "validate_branding_compliance",
]
