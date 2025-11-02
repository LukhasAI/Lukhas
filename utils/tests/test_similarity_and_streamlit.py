"""Targeted tests for utils similarity and streamlit compatibility helpers."""

# ΛTAG: coverage_expansion

from __future__ import annotations

import builtins
import importlib
import sys
import types
from contextlib import contextmanager

import pytest

from utils.similarity import _cosine
from utils.time import utc_now


@contextmanager
def _temporarily_remove_module(name: str):
    """Ensure a module is absent for the duration of the context."""
    # ΛTAG: test_safety_guard
    removed = sys.modules.pop(name, None)
    try:
        yield
    finally:
        if removed is not None:
            sys.modules[name] = removed
        else:
            sys.modules.pop(name, None)


class TestCosineSimilarity:
    """Tests covering the private cosine similarity helper."""

    # ΛTAG: similarity_nominal
    def test_cosine_similarity_matches_expected_value(self) -> None:
        vector_a = [1.0, 2.0, 3.0]
        vector_b = [4.0, 5.0, 6.0]
        # Computed manually: dot=32, norms=√14 and √77 → cosine ≈ 0.9746
        expected = 32 / ((14**0.5) * (77**0.5))
        assert pytest.approx(expected) == _cosine(vector_a, vector_b)

    # ΛTAG: similarity_guards
    def test_cosine_similarity_handles_invalid_inputs(self) -> None:
        assert _cosine([], [1.0]) == 0.0
        assert _cosine([1.0, 2.0], []) == 0.0
        assert _cosine([1.0], [2.0, 3.0]) == 0.0

    # ΛTAG: similarity_zero_norm
    def test_cosine_similarity_zero_norm_vector(self) -> None:
        assert _cosine([0.0, 0.0], [10.0, -2.5]) == 0.0


class TestStreamlitCompat:
    """Validation for the Streamlit compatibility shim."""

    # ΛTAG: streamlit_fallback
    def test_streamlit_fallback_noop_behaviour(self, monkeypatch: pytest.MonkeyPatch) -> None:
        module_name = "utils.streamlit_compat"
        with _temporarily_remove_module(module_name):
            original_import = builtins.__import__

            def fake_import(name, *args, **kwargs):
                if name == "streamlit":
                    raise ModuleNotFoundError("streamlit not installed for test")
                return original_import(name, *args, **kwargs)

            monkeypatch.setattr(builtins, "__import__", fake_import)
            compat = importlib.import_module(module_name)
            assert compat.st.sidebar.missing_widget() is None
            assert compat.st.write("anything") is None

    # ΛTAG: streamlit_passthrough
    def test_streamlit_passthrough_uses_real_module(self, monkeypatch: pytest.MonkeyPatch) -> None:
        fake_streamlit = types.SimpleNamespace()
        fake_streamlit.calls = []

        def record_call(*args, **kwargs):
            fake_streamlit.calls.append((args, kwargs))
            return "ok"

        fake_streamlit.write = record_call
        fake_streamlit.sidebar = types.SimpleNamespace(button=record_call)

        module_name = "utils.streamlit_compat"
        with _temporarily_remove_module(module_name):
            with _temporarily_remove_module("streamlit"):
                monkeypatch.setitem(sys.modules, "streamlit", fake_streamlit)
                compat = importlib.import_module(module_name)

        assert compat.st.write("hello") == "ok"
        assert compat.st.sidebar.button("click") == "ok"
        assert fake_streamlit.calls == [(("hello",), {}), (("click",), {})]


class TestUtcNow:
    """Regression coverage for the UTC timestamp helper."""

    # ΛTAG: time_utc_now
    def test_utc_now_returns_timezone_aware_utc_value(self) -> None:
        timestamp = utc_now()
        assert timestamp.tzinfo is not None
        assert timestamp.utcoffset() is not None
        assert timestamp.utcoffset().total_seconds() == 0
