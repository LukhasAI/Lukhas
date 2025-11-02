"""Import-smoke for matriz.consciousness.reflection.learning_system."""


def test_learning_system_imports():
    mod = __import__("matriz.consciousness.reflection.learning_system", fromlist=["*"])
    assert mod is not None
