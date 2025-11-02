"""Import-smoke for matriz.consciousness.dream.oneiric.oneiric_core.engine.dream_engine_fastapi."""


def test_dream_engine_fastapi_imports():
    mod = __import__("matriz.consciousness.dream.oneiric.oneiric_core.engine.dream_engine_fastapi", fromlist=["*"])
    assert mod is not None
