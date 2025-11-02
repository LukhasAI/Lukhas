"""Import-smoke for core.governance.identity.core.colonies.biometric_verification_colony."""


def test_biometric_verification_colony_imports():
    mod = __import__("core.governance.identity.core.colonies.biometric_verification_colony", fromlist=["*"])
    assert mod is not None
