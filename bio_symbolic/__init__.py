"""
Compatibility shim for bio_symbolic
DEPRECATED: This module will be removed on 2025-11-01
Please update imports to: lukhas.accepted.bio.symbolic
"""

import warnings
from lukhas.accepted.bio.symbolic import *

warnings.warn(
    "Import 'bio_symbolic' is deprecated and will be removed on 2025-11-01. "
    "Please update to 'lukhas.accepted.bio.symbolic'",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything for backward compatibility
__all__ = dir()
