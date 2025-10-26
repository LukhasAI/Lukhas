"""Integration smoke for actor_system import."""


def test_actor_system_module_imports():
    mod = __import__(
        "matriz.consciousness.reflection.actor_system", fromlist=["*"]
    )
    assert mod is not None

