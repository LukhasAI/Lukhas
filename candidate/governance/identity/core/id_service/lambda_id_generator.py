"""
DEPRECATED: lambda_id_generator.py - Legacy Compatibility Shim
=============================================================

🚨 **WARNING**: This naming was based on a misunderstanding!
    - Λ = LUKHAS, not Lambda!
    - "lambda_id" was wrong interpretation of the Λ symbol

✅ **USE INSTEAD**: lukhas_id_generator.py (correct implementation)

This file provides backward compatibility for existing code that imports
the incorrectly named "lambda_id" modules. All real implementation has 
moved to lukhas_id_generator.py.

MIGRATION PATH:
- OLD: from .lambda_id_generator import LambdaIDGenerator
- NEW: from .lukhas_id_generator import LukhasIDGenerator

This file will be removed in a future version once migration is complete.
"""

# Import from the CORRECT implementation
from .lukhas_id_generator import LukhasIDGenerator

# Legacy alias for backward compatibility
LambdaIDGenerator = LukhasIDGenerator  # Legacy misunderstood name

__all__ = ["LambdaIDGenerator", "LukhasIDGenerator"]

# Deprecation warning when this module is imported
import warnings
warnings.warn(
    "lambda_id_generator.py is deprecated. Λ=LUKHAS, not Lambda! "
    "Use lukhas_id_generator.py instead.",
    DeprecationWarning,
    stacklevel=2
)
