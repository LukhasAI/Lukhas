"""
Compatibility shim for memory.compression
DEPRECATED: This module will be removed on 2025-11-01
Please update imports to: lukhas.accepted.memory.compression
"""

import warnings
try:
    from lukhas.accepted.memory.compression import *
except ImportError:
    # Fallback for gradual migration
    pass

warnings.warn(
    "Import 'memory.compression' is deprecated and will be removed on 2025-11-01. "
    "Please update to 'lukhas.accepted.memory.compression'",
    DeprecationWarning,
    stacklevel=2
)
