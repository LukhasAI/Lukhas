"""Tiny Streamlit compatibility shim.

Usage:
    from utils.streamlit_compat import st
or:
    from utils import st
"""
from __future__ import annotations

__all__ = ["st"]

try:
    import streamlit as st  # type: ignore
except Exception:  # pragma: no cover
    class _Sidebar:
        def __getattr__(self, _): return _noop
    def _noop(*_, **__): return None
    class _ST:
        sidebar = _Sidebar()
        def __getattr__(self, _): return _noop
    st = _ST()  # type: ignore
