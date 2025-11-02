"""Import-smoke for core.memory.tier_system."""


def test_tier_system_imports():
    mod = __import__("core.memory.tier_system", fromlist=["*"])
    assert mod is not None
