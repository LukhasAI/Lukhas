"""Import-smoke for matriz.consciousness.reflection.event_replay_snapshot."""


def test_event_replay_snapshot_imports():
    mod = __import__("matriz.consciousness.reflection.event_replay_snapshot", fromlist=["*"])
    assert mod is not None
