"""Import-smoke for core.orchestration.brain.brain_integration (VERIFY)."""

def test_brain_integration_imports():
    mod = __import__("core.orchestration.brain.brain_integration", fromlist=["*"])
    assert mod is not None
