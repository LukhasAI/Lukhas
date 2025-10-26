"""Import-smoke for core.governance.identity.core.unified_auth_manager."""

def test_unified_auth_manager_imports():
    mod = __import__("core.governance.identity.core.unified_auth_manager", fromlist=["*"])
    assert mod is not None
