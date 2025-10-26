"""Import-smoke for core.api.api_system."""

def test_api_system_imports():
    mod = __import__("core.api.api_system", fromlist=["*"])
    assert mod is not None
