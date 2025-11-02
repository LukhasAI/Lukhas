"""Integration smoke for openai_core_service import."""


def test_openai_core_service_module_imports():
    mod = __import__("matriz.consciousness.reflection.openai_core_service", fromlist=["*"])
    assert mod is not None
