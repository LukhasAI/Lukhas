"""
Compatibility shim for vivox
DEPRECATED: This module will be removed on 2025-11-01
Please update imports to: candidate.vivox

NOTE: This is a candidate module. Enable with feature flag:
  VIVOX_LITE=true
"""

import contextlib
import os
import warnings

import streamlit as st

warnings.warn(
    "Import 'vivox' is deprecated. Please update to 'candidate.vivox' and enable feature flag",
    DeprecationWarning,
    stacklevel=2,
)

# Check if feature flag is enabled
flag_name = "VIVOX_LITE"
if os.getenv(flag_name, "false").lower() == "true":
    with contextlib.suppress(ImportError):
        from candidate.vivox import *
