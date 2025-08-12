"""
Compatibility shim for vivox
DEPRECATED: This module will be removed on 2025-11-01
Please update imports to: lukhas.candidate.vivox

NOTE: This is a candidate module. Enable with feature flag:
  VIVOX_ENABLED=true
"""

import os
import warnings

warnings.warn(
    "Import 'vivox' is deprecated. "
    "Please update to 'lukhas.candidate.vivox' and enable feature flag",
    DeprecationWarning,
    stacklevel=2
)

# Check if feature flag is enabled
flag_name = "VIVOX_ENABLED"
if os.getenv(flag_name, "false").lower() == "true":
    try:
        from lukhas.candidate.vivox import *
    except ImportError:
        pass
