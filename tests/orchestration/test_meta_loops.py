# tests/orchestration/test_meta_loops.py
from lukhas.core.orchestration.meta_controller import MetaController


def test_detects_two_cycle():
    m = MetaController()
    assert not m.step("A")
    assert not m.step("B")
    assert not m.step("A")
    assert m.step("B")  # A,B,A,B
