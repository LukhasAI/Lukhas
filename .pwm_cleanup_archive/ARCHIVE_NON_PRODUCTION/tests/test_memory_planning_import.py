import importlib

import pytest


def test_memory_planning_imports():
    pytest.importorskip("torch")
    module = importlib.import_module("memory.systems.memory_planning")
    assert hasattr(module, "LiveRange")
    assert hasattr(module, "LiveRanges")


def test_memory_planning_basic_live_range():
    pytest.importorskip("torch")
    mp = importlib.import_module("memory.systems.memory_planning")
    lr1 = mp.LiveRange(begin=0, end=1)
    lr2 = mp.LiveRange(begin=1, end=2)
    joined = lr1.join(lr2)
    assert joined.begin == 0
    assert joined.end == 2
