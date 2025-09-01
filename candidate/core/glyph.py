"""
Compatibility shim for core.glyph
DEPRECATED: This module will be removed on 2025-11-01
Please update imports to: lukhas.core.glyph
"""

import warnings

from .glyph.glyph import *

warnings.warn(
    "Import 'core.glyph' is deprecated and will be removed on 2025-11-01. Please update to 'lukhas.core.glyph'",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything for backward compatibility
__all__ = dir()
