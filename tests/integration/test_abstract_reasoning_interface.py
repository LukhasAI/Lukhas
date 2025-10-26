"""Import-smoke for core.orchestration.brain.abstract_reasoning.interface."""

def test_abstract_reasoning_interface_imports():
    mod = __import__("core.orchestration.brain.abstract_reasoning.interface", fromlist=["*"])
    assert mod is not None
