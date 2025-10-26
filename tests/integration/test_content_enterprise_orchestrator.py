"""Import-smoke for matriz.consciousness.reflection.content_enterprise_orchestrator."""

def test_ceo_imports():
    mod = __import__(
        "matriz.consciousness.reflection.content_enterprise_orchestrator",
        fromlist=["*"]
    )
    assert mod is not None
