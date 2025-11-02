"""Integration smoke for integrator import."""


def test_integrator_module_imports():
    mod = __import__("core.consciousness.integrator", fromlist=["*"])
    assert mod is not None
