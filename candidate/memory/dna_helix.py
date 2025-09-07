"""
Compatibility shim for memory.dna_helix
DEPRECATED: This module will be removed on 2025-11-01
Please update imports to: lukhas.accepted.memory.helix
"""
import streamlit as st

import warnings

try:
    from lukhas.accepted.memory.helix import *
except ImportError:
    # Fallback for gradual migration
    pass

warnings.warn(
    "Import 'memory.dna_helix' is deprecated and will be removed on 2025-11-01. "
    "Please update to 'lukhas.accepted.memory.helix'",
    DeprecationWarning,
    stacklevel=2,
)
