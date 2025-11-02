"""Import-smoke for core.memory.distributed_memory_fold."""


def test_distributed_memory_fold_imports():
    mod = __import__("core.memory.distributed_memory_fold", fromlist=["*"])
    assert mod is not None
