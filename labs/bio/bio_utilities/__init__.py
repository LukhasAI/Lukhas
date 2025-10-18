"""
Compatibility shim for bio.bio_utilities
DEPRECATED: This module will be removed on 2025-11-01
Please update imports to: accepted.bio.utils
"""
import warnings

import streamlit as st

from bio.utils import *

warnings.warn(
    "Import 'bio.bio_utilities' is deprecated and will be removed on 2025-11-01. "
    "Please update to 'accepted.bio.utils'",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything for backward compatibility
__all__ = dir()
