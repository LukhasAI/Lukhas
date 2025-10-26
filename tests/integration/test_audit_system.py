"""Import-smoke for core.governance.security.audit_system."""

def test_audit_system_imports():
    mod = __import__("core.governance.security.audit_system", fromlist=["*"])
    assert mod is not None
