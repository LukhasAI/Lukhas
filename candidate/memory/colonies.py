"""
Compatibility shim for memory.colonies
DEPRECATED: This module will be removed on 2025-11-01
Please update imports to: lukhas.accepted.memory.colonies
"""
import warnings

try:
    from lukhas.accepted.memory.colonies import *
except ImportError:
    # Fallback for gradual migration
    pass

warnings.warn(
    "Import 'memory.colonies' is deprecated and will be removed on 2025-11-01. "
    "Please update to 'lukhas.accepted.memory.colonies'",
    DeprecationWarning,
    stacklevel=2,
)