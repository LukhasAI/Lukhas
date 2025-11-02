"""Import-smoke for core.orchestration.brain.australian_awareness_engine."""


def test_aus_awareness_imports():
    mod = __import__("core.orchestration.brain.australian_awareness_engine", fromlist=["*"])
    assert mod is not None
