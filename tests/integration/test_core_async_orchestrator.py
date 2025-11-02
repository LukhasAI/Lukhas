"""Import-smoke for core.orchestration.async_orchestrator."""


def test_core_async_orchestrator_imports():
    mod = __import__("core.orchestration.async_orchestrator", fromlist=["*"])
    assert mod is not None
