"""Integration smoke for matriz_consciousness_governance import."""


def test_matriz_consciousness_governance_module_imports():
    mod = __import__("core.governance.matriz_consciousness_governance", fromlist=["*"])
    assert mod is not None
