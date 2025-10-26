"""Import-smoke for core.consciousness.bridge."""

def test_consciousness_bridge_imports():
    mod = __import__("core.consciousness.bridge", fromlist=["*"])
    assert mod is not None
