"""
Compatibility shim for memory.episodic
DEPRECATED: This module will be removed on 2025-11-01
Please update imports to: lukhas.accepted.memory.episodic
"""
import warnings

try:
    from lukhas.accepted.memory.episodic import *
except ImportError:
    # Fallback for gradual migration
    pass

warnings.warn(
    "Import 'memory.episodic' is deprecated and will be removed on 2025-11-01. "
    "Please update to 'lukhas.accepted.memory.episodic'",
    DeprecationWarning,
    stacklevel=2,
)
