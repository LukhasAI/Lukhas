"""Integration smoke for reality_synthesis_engine import."""


def test_reality_synthesis_engine_module_imports():
    mod = __import__("matriz.consciousness.dream.reality_synthesis_engine", fromlist=["*"])
    assert mod is not None

