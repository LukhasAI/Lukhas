"""
DEPRECATED: lambd_id_generator.py - Legacy Compatibility Shim
============================================================

🚨 **WARNING**: This naming was based on a misunderstanding!
    - Λ = LUKHAS, not Lambda!
    - "lambd_id" was a typo of the wrong interpretation

✅ **USE INSTEAD**: lukhas_id_generator.py (correct implementation)

This file provides backward compatibility for existing code that imports
the incorrectly named "lambd_id" modules. All real implementation has 
moved to lukhas_id_generator.py.

MIGRATION PATH:
- OLD: from .lambd_id_generator import LambdIDGenerator
- NEW: from .lukhas_id_generator import LukhasIDGenerator

This file will be removed in a future version once migration is complete.
"""

# Import from the CORRECT implementation
from .lukhas_id_generator import (
    LukhasIDGenerator,
    TierLevel,
    UserContext
)

# Legacy aliases for backward compatibility
LambdIDGenerator = LukhasIDGenerator      # Legacy typo name
LambdaIDGenerator = LukhasIDGenerator     # Legacy misunderstood name

# Also support the old validator import that some code expects
try:
    from .lukhas_id_validator import LukhasIDValidator
    LambdIDValidator = LukhasIDValidator  # Legacy alias
except ImportError:
    # Fallback if validator doesn't exist yet
    LambdIDValidator = None

# Backward-compatible exports
__all__ = [
    # Legacy names (deprecated)
    "LambdIDGenerator",
    "LambdIDValidator", 
    "LambdaIDGenerator",
    # Correct names (preferred)
    "LukhasIDGenerator",
    "TierLevel",
    "UserContext",
]

# Deprecation warning when this module is imported
import warnings
warnings.warn(
    "lambd_id_generator.py is deprecated. Λ=LUKHAS, not Lambda! "
    "Use lukhas_id_generator.py instead.",
    DeprecationWarning,
    stacklevel=2
)