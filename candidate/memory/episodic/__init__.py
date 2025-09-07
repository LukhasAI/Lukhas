"""
Compatibility shim for memory.episodic
DEPRECATED: This module will be removed on 2025-11-01
Please update imports to: lukhas.accepted.memory.episodic
"""
import streamlit as st

import warnings

from lukhas.accepted.memory.episodic import *

warnings.warn(
    "Import 'memory.episodic' is deprecated and will be removed on 2025-11-01. "
    "Please update to 'lukhas.accepted.memory.episodic'",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything for backward compatibility
__all__ = dir()
