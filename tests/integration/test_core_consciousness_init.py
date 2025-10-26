"""Import-smoke for core.consciousness (VERIFY)."""

def test_core_consciousness_init_imports():
    mod = __import__("core.consciousness", fromlist=["*"])
    assert mod is not None
