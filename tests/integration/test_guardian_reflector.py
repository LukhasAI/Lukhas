"""Import-smoke for core.governance.ethics.guardian_reflector."""


def test_guardian_reflector_imports():
    mod = __import__("core.governance.ethics.guardian_reflector", fromlist=["*"])
    assert mod is not None
