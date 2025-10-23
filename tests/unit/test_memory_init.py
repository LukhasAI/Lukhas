"""Tests for the memory package initialization bridge."""

from __future__ import annotations

import importlib
import sys
import types


def test_memory_manager_fallback(monkeypatch) -> None:
    """Ensure the memory package exposes a fallback MemoryManager when needed."""

    fake_labs_memory = types.ModuleType("labs.memory")
    monkeypatch.setitem(sys.modules, "labs.memory", fake_labs_memory)
    monkeypatch.delen(sys.modules, "memory", raising=False)

    memory_module = importlib.import_module("memory")

    assert hasattr(memory_module, "MemoryManager")
    # Fallback class is defined in the memory package itself.
    assert memory_module.MemoryManager.__module__ == "memory"

    manager = memory_module.MemoryManager()
    assert isinstance(manager, memory_module.MemoryManager)
