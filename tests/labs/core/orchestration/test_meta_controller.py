import pytest
from labs.core.orchestration.meta_controller import MetaController


class TestMetaController:
    def test_no_oscillation(self):
        mc = MetaController()
        assert mc.step("A") is False
        assert mc.step("B") is False
        assert mc.step("C") is False
        assert mc.step("D") is False

    def test_oscillation_detected(self):
        mc = MetaController()
        mc.step("A")
        mc.step("B")
        mc.step("A")
        assert mc.step("B") is True

    def test_no_oscillation_with_repeats(self):
        mc = MetaController()
        mc.step("A")
        mc.step("A")
        mc.step("B")
        mc.step("B")
        assert mc.step("A") is False
