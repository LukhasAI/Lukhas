"""Import-smoke for core.identity.manager."""


def test_identity_manager_imports():
    mod = __import__("core.identity.manager", fromlist=["*"])
    assert mod is not None
