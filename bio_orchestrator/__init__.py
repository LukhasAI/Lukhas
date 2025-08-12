"""
Compatibility shim for bio_orchestrator
DEPRECATED: This module will be removed on 2025-11-01
Please update imports to: lukhas.accepted.bio.orchestrator
"""

import warnings
from lukhas.accepted.bio.orchestrator import *

warnings.warn(
    "Import 'bio_orchestrator' is deprecated and will be removed on 2025-11-01. "
    "Please update to 'lukhas.accepted.bio.orchestrator'",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything for backward compatibility
__all__ = dir()
