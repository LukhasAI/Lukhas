"""
Compatibility shim for qim
DEPRECATED: This module will be removed on 2025-11-01
Please update imports to: lukhas.candidate.qim

NOTE: This is a candidate module. Enable with feature flag:
  QIM_SANDBOX=true
"""
import contextlib
import os
import warnings

import streamlit as st

# Import the qi stub we created
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from consciousness.qi import qi

warnings.warn(
    "Import 'qim' is deprecated. Please update to 'lukhas.candidate.qim' and enable feature flag",
    DeprecationWarning,
    stacklevel=2,
)

# Check if feature flag is enabled
flag_name = "QIM_SANDBOX"
if os.getenv(flag_name, "false").lower() == "true":
    with contextlib.suppress(ImportError):
        from lukhas.candidate.qim import *
