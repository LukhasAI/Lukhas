"""Import-smoke for core.governance.identity.unified_login_interface."""


def test_unified_login_interface_imports():
    mod = __import__("core.governance.identity.unified_login_interface", fromlist=["*"])
    assert mod is not None
