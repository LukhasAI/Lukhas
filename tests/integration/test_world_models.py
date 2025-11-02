"""Import-smoke for core.consciousness.world_models."""


def test_world_models_imports():
    mod = __import__("core.consciousness.world_models", fromlist=["*"])
    assert mod is not None
