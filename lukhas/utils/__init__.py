"""Utilities façade."""
from .streamlit_compat import st  # re-export convenience  # noqa: TID252 (relative imports in __init__.py are idiomatic)

__all__ = ["st"]
