"""Import-smoke for core.memory.adaptive_meta_learning_system."""


def test_adaptive_meta_learning_system_imports():
    mod = __import__("core.memory.adaptive_meta_learning_system", fromlist=["*"])
    assert mod is not None
