"""
Compatibility shim for memory.hippocampal
DEPRECATED: This module will be removed on 2025-11-01
Please update imports to: lukhas.accepted.memory.hippocampal
"""
import warnings

try:
    from lukhas.accepted.memory.hippocampal import *
except ImportError:
    # Fallback for gradual migration
    pass

warnings.warn(
    "Import 'memory.hippocampal' is deprecated and will be removed on 2025-11-01. "
    "Please update to 'lukhas.accepted.memory.hippocampal'",
    DeprecationWarning,
    stacklevel=2,
)