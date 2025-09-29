"""
LUKHAS Context Handoff API
=========================

Minimal, safe context bus handoff with rate limiting.
- In Phase 3, wire to bus providers via registry if FEATURE enabled
"""

import streamlit as st

from .api import handoff_context

__all__ = ["handoff_context"]
