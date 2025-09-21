"""Stub streamlit module for tests."""

from types import SimpleNamespace


def __getattr__(name: str):
    def _noop(*args, **kwargs):
        return None
    return _noop


st = SimpleNamespace(**{name: __getattr__(name) for name in ["write", "markdown", "title"]})
