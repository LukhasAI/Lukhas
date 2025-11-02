"""Import-smoke for core.orchestration.golden_trio.trio_orchestrator."""


def test_trio_orchestrator_imports():
    mod = __import__("core.orchestration.golden_trio.trio_orchestrator", fromlist=["*"])
    assert mod is not None
