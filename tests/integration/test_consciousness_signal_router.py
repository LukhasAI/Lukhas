"""Import-smoke for core.consciousness_signal_router."""


def test_consciousness_signal_router_imports():
    mod = __import__("core.consciousness_signal_router", fromlist=["*"])
    assert mod is not None
