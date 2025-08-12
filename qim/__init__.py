"""
Compatibility shim for qim
DEPRECATED: This module will be removed on 2025-11-01
Please update imports to: lukhas.candidate.qim

NOTE: This is a candidate module. Enable with feature flag:
  QIM_ENABLED=true
"""

import os
import warnings

warnings.warn(
    "Import 'qim' is deprecated. "
    "Please update to 'lukhas.candidate.qim' and enable feature flag",
    DeprecationWarning,
    stacklevel=2
)

# Check if feature flag is enabled
flag_name = "QIM_ENABLED"
if os.getenv(flag_name, "false").lower() == "true":
    try:
        from lukhas.candidate.qim import *
    except ImportError:
        pass
