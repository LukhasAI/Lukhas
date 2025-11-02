"""Import-smoke for matriz.consciousness.reflection.distributed_state_manager."""


def test_distributed_state_manager_imports():
    mod = __import__("matriz.consciousness.reflection.distributed_state_manager", fromlist=["*"])
    assert mod is not None
