"""
Compatibility shim for bio.bio_engine
DEPRECATED: This module will be removed on 2025-11-01
Please update imports to: lukhas.accepted.bio.engine
"""
import warnings

import streamlit as st

from bio.engine import *

warnings.warn(
    "Import 'bio.bio_engine' is deprecated and will be removed on 2025-11-01. "
    "Please update to 'lukhas.accepted.bio.engine'",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything for backward compatibility
__all__ = dir()
