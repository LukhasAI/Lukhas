"""
Compatibility shim for governance.guardian
DEPRECATED: This module will be removed on 2025-11-01
Please update imports to: lukhas.accepted.governance.guardian
"""

import warnings
from lukhas.accepted.governance.guardian import *

warnings.warn(
    "Import 'governance.guardian' is deprecated and will be removed on 2025-11-01. "
    "Please update to 'lukhas.accepted.governance.guardian'",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything for backward compatibility
__all__ = dir()
