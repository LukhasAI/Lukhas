"""
Compatibility shim - DEPRECATED
This module has been moved to production.
Will be removed after 2025-11-01 (SHIM_CULL_DATE)
"""

import warnings

warnings.warn(
    "Import path deprecated. Use 'from lukhas.monitoring.drift_tracker import ...'",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export from new location
from lukhas.monitoring.drift_tracker import MemoryDriftTracker

__all__ = ["MemoryDriftTracker"]
