"""Import-smoke for core.memory.replay_system."""


def test_replay_system_imports():
    mod = __import__("core.memory.replay_system", fromlist=["*"])
    assert mod is not None
