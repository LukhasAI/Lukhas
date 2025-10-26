"""Import-smoke for core.consciousness.haiku_generator."""

def test_haiku_generator_imports():
    mod = __import__("core.consciousness.haiku_generator", fromlist=["*"])
    assert mod is not None
