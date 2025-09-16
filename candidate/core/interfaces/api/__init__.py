from __future__ import annotations

try:
    import streamlit as st
except ImportError:  # pragma: no cover
    from types import SimpleNamespace

    def _streamlit_placeholder(*_args, **_kwargs):
        return None

    st = SimpleNamespace(
        sidebar=SimpleNamespace(
            button=_streamlit_placeholder,
            checkbox=lambda *_a, **_k: False,
            selectbox=_streamlit_placeholder,
        ),
        button=_streamlit_placeholder,
        checkbox=lambda *_a, **_k: False,
        container=lambda *_a, **_k: SimpleNamespace(markdown=_streamlit_placeholder),
        markdown=_streamlit_placeholder,
        write=_streamlit_placeholder,
    )


"""API package with versioned interfaces."""

API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"
