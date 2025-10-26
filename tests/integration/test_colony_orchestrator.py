"""Integration smoke for colony_orchestrator import."""


def test_colony_orchestrator_module_imports():
    mod = __import__(
        "matriz.consciousness.reflection.colony_orchestrator", fromlist=["*"]
    )
    assert mod is not None

