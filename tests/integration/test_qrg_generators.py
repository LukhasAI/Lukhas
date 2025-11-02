"""Import-smoke for core.governance.identity.auth.qrg_generators."""


def test_qrg_generators_imports():
    mod = __import__("core.governance.identity.auth.qrg_generators", fromlist=["*"])
    assert mod is not None
