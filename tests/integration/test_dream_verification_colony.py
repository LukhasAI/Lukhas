"""Import-smoke for core.governance.identity.core.colonies.dream_verification_colony."""

def test_dream_verification_colony_imports():
    mod = __import__(
        "core.governance.identity.core.colonies.dream_verification_colony",
        fromlist=["*"]
    )
    assert mod is not None
