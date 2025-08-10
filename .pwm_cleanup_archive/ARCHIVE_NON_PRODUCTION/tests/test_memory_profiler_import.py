import importlib

import pytest


def test_memory_profiler_import():
    pytest.importorskip("torch")
    module = importlib.import_module("memory.systems.memory_profiler")
    assert hasattr(module, "Category")
    assert hasattr(module, "Action")
