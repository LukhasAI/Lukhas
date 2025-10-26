"""Import-smoke for core.memory.simple_store."""

def test_simple_store_imports():
    mod = __import__("core.memory.simple_store", fromlist=["*"])
    assert mod is not None
