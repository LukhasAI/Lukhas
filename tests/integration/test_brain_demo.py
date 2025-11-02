"""Import-smoke for core.orchestration.brain.demo (VERIFY)."""


def test_brain_demo_imports():
    mod = __import__("core.orchestration.brain.demo", fromlist=["*"])
    assert mod is not None
