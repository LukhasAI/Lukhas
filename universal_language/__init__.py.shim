"""
Compatibility shim for universal_language
DEPRECATED: This module will be removed on 2025-11-01
Please update imports to: lukhas.candidate.ul

NOTE: This is a candidate module. Enable with feature flag:
  UL_ENABLED=true
"""

import os
import warnings

warnings.warn(
    "Import 'universal_language' is deprecated. "
    "Please update to 'lukhas.candidate.ul' and enable feature flag",
    DeprecationWarning,
    stacklevel=2
)

# Check if feature flag is enabled
flag_name = "UL_ENABLED"
if os.getenv(flag_name, "false").lower() == "true":
    try:
        from lukhas.candidate.ul import *
    except ImportError:
        pass
