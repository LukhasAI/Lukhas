"""Integration smoke for MemorySystem import and basic instantiation."""

def test_memory_system_import_and_init():
    from matriz.core.memory_system import MemorySystem

    ms = MemorySystem()
    assert ms is not None

