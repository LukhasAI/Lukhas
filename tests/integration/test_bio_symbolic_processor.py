"""Import-smoke for core.bio_symbolic_processor."""

def test_bio_symbolic_processor_imports():
    mod = __import__("core.bio_symbolic_processor", fromlist=["*"])
    assert mod is not None
