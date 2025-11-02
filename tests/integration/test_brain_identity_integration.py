"""Import-smoke for core.governance.identity.core.brain_identity_integration."""


def test_brain_identity_integration_imports():
    mod = __import__("core.governance.identity.core.brain_identity_integration", fromlist=["*"])
    assert mod is not None
