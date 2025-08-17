"""
Compatibility shim for memory.memory_consolidation
DEPRECATED: This module will be removed on 2025-11-01
Please update imports to: lukhas.accepted.memory.consolidation
"""

import warnings

from lukhas.accepted.memory.consolidation import *

warnings.warn(
    "Import 'memory.memory_consolidation' is deprecated and will be removed on 2025-11-01. "
    "Please update to 'lukhas.accepted.memory.consolidation'",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything for backward compatibility
__all__ = dir()
