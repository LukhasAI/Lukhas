"""Import-smoke for core.governance.identity.core.colonies.consciousness_verification_colony."""

def test_consciousness_verification_colony_imports():
    mod = __import__(
        "core.governance.identity.core.colonies.consciousness_verification_colony",
        fromlist=["*"]
    )
    assert mod is not None
