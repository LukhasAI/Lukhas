"""Import-smoke for core.consciousness.shared_state."""


def test_shared_state_imports():
    mod = __import__("core.consciousness.shared_state", fromlist=["*"])
    assert mod is not None
