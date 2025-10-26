import importlib


def test_import_australian_awareness_engine():
    mod = importlib.import_module(
        "core.orchestration.brain.australian_awareness_engine"
    )
    assert hasattr(mod, "AustralianAwarenessEngine")


