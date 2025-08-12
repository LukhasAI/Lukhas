"""
Compatibility shim for identity.core
DEPRECATED: This module will be removed on 2025-11-01
Please update imports to: lukhas.accepted.identity
"""

import warnings
from lukhas.accepted.identity import *

warnings.warn(
    "Import 'identity.core' is deprecated and will be removed on 2025-11-01. "
    "Please update to 'lukhas.accepted.identity'",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything for backward compatibility
__all__ = dir()
