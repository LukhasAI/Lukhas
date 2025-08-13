"""
Compatibility shim for bio_core
DEPRECATED: This module will be removed on 2025-11-01
Please update imports to: lukhas.accepted.bio
"""

import warnings
from lukhas.accepted.bio import *

warnings.warn(
    "Import 'bio_core' is deprecated and will be removed on 2025-11-01. "
    "Please update to 'lukhas.accepted.bio'",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything for backward compatibility
__all__ = dir()
