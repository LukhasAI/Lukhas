"""Import-smoke for core.consciousness.simulation_controller."""


def test_simulation_controller_imports():
    mod = __import__("core.consciousness.simulation_controller", fromlist=["*"])
    assert mod is not None
