"""Import-smoke for core.governance.identity.biometric.biometric_fusion_engine."""

def test_biometric_fusion_engine_imports():
    mod = __import__("core.governance.identity.biometric.biometric_fusion_engine", fromlist=["*"])
    assert mod is not None
