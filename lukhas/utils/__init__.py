"""Utilities façade."""
from .streamlit_compat import (
    st,  # re-export convenience  # (relative imports in __init__.py are idiomatic)
)

__all__ = ["st"]
