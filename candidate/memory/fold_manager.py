"""
Compatibility shim for memory.fold_manager
DEPRECATED: This module will be removed on 2025-11-01
Please update imports to: lukhas.accepted.memory.fold
"""
import warnings

try:
    from lukhas.memory.fold import *
except ImportError:
    # Fallback for gradual migration
    pass

warnings.warn(
    "Import 'memory.fold_manager' is deprecated and will be removed on 2025-11-01. "
    "Please update to 'lukhas.accepted.memory.fold'",
    DeprecationWarning,
    stacklevel=2,
)
