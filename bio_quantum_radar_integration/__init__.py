"""
Compatibility shim for bio_quantum_radar_integration
DEPRECATED: This module will be removed on 2025-11-01
Please update imports to: lukhas.candidate.bio.quantum
"""

import warnings
from lukhas.candidate.bio.quantum import *

warnings.warn(
    "Import 'bio_quantum_radar_integration' is deprecated and will be removed on 2025-11-01. "
    "Please update to 'lukhas.candidate.bio.quantum'",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything for backward compatibility
__all__ = dir()
