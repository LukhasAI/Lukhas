"""Unit tests for the symbolic QI attention integration helpers."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest


def _load_symbolic_module(monkeypatch: pytest.MonkeyPatch, suffix: str):
    """Load symbolic_qi_attention with safe stubs for integration testing."""

    module_name = f"tests.symbolic_qi_attention_under_test_{suffix}"
    module_path = (
        Path(__file__).resolve().parents[3]
        / "candidate"
        / "consciousness"
        / "awareness"
        / "symbolic_qi_attention.py"
    )

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)

    # Provide lightweight stubs so example integration code does not raise errors.
    module.CONFIG = SimpleNamespace(embedding_size=4)

    class _DummyAGI:
        def __init__(self) -> None:
            self.attention_mechanism = lambda *args, **kwargs: np.ones(1)

    class _DummyBioOrchestrator:
        def __init__(self, *args, **kwargs) -> None:
            self.modules = {}

        def register_module(self, name, module_instance, priority=None, energy_cost=None) -> None:
            self.modules[name] = {
                "module": module_instance,
                "priority": priority,
                "energy_cost": energy_cost,
            }

        def invoke_module(self, name, method, *args):
            return False, args[0]

    module.lukhas_agi = _DummyAGI()
    module.BioOrchestrator = _DummyBioOrchestrator
    module.ResourcePriority = SimpleNamespace(HIGH="high")

    monkeypatch.setitem(sys.modules, module_name, module)
    spec.loader.exec_module(module)  # type: ignore[call-arg]
    return module


def test_resolve_prefers_core_backend(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_symbolic_module(monkeypatch, "core")
    if module.CoreQIInspiredAttention is None:  # pragma: no cover - environment without core module
        pytest.skip("Core QI attention module is unavailable in this environment.")

    backend = module.resolve_qi_attention_backend()
    assert backend is module.CoreQIInspiredAttention

    instance = module.create_qi_attention()
    assert isinstance(instance, module.CoreQIInspiredAttention)


def test_resolve_can_force_symbolic(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_symbolic_module(monkeypatch, "symbolic")

    backend = module.resolve_qi_attention_backend(prefer_core=False)
    assert backend is module.QIInspiredAttention


def test_create_qi_attention_falls_back_on_error(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_symbolic_module(monkeypatch, "fallback")
    if module.CoreQIInspiredAttention is None:  # pragma: no cover - environment without core module
        pytest.skip("Core QI attention module is unavailable in this environment.")

    class _FailingCore:
        def __init__(self, *args, **kwargs) -> None:
            raise RuntimeError("boom")

    monkeypatch.setattr(module, "CoreQIInspiredAttention", _FailingCore)

    instance = module.create_qi_attention()
    assert isinstance(instance, module.QIInspiredAttention)
