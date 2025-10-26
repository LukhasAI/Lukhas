"""Import-smoke for core.consciousness.natural_language_interface."""

def test_nli_imports():
    mod = __import__("core.consciousness.natural_language_interface", fromlist=["*"])
    assert mod is not None
