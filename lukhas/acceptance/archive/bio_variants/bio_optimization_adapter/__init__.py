"""
Compatibility shim for bio_optimization_adapter
DEPRECATED: This module will be removed on 2025-11-01
Please update imports to: lukhas.accepted.bio.optimizer
"""

import warnings

from lukhas.accepted.bio.optimizer import *

warnings.warn(
    "Import 'bio_optimization_adapter' is deprecated and will be removed on 2025-11-01. "
    "Please update to 'lukhas.accepted.bio.optimizer'",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything for backward compatibility
__all__ = dir()
