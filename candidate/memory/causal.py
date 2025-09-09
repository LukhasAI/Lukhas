"""
Compatibility shim for memory.causal
DEPRECATED: This module will be removed on 2025-11-01
Please update imports to: lukhas.accepted.memory.causal
"""
import warnings

try:
    from lukhas.accepted.memory.causal import *
except ImportError:
    # Fallback for gradual migration
    pass

warnings.warn(
    "Import 'memory.causal' is deprecated and will be removed on 2025-11-01. "
    "Please update to 'lukhas.accepted.memory.causal'",
    DeprecationWarning,
    stacklevel=2,
)