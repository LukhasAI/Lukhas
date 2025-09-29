"""
Compatibility shim for bio.bio_hub
DEPRECATED: This module will be removed on 2025-11-01
Please update imports to: lukhas.accepted.bio.hub
"""
import warnings

import streamlit as st

from lukhas.bio.hub import *

warnings.warn(
    "Import 'bio.bio_hub' is deprecated and will be removed on 2025-11-01. Please update to 'lukhas.accepted.bio.hub'",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything for backward compatibility
__all__ = dir()
