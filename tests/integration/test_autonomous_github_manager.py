"""Import-smoke for core.orchestration.brain.autonomous_github_manager."""

def test_autonomous_github_manager_imports():
    mod = __import__("core.orchestration.brain.autonomous_github_manager", fromlist=["*"])
    assert mod is not None
