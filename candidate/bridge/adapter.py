"""
Compatibility shim for bridge.adapter
DEPRECATED: This module will be removed on 2025-11-01
Please update imports to: lukhas.accepted.adapters.base
"""

import warnings

from lukhas.accepted.adapters.base import *

warnings.warn(
    "Import 'bridge.adapter' is deprecated and will be removed on 2025-11-01. "
    "Please update to 'lukhas.accepted.adapters.base'",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything for backward compatibility
__all__ = dir()
