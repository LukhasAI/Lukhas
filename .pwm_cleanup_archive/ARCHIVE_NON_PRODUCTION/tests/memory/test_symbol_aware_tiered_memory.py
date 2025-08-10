"""Tests for SymbolAwareTieredMemory."""

from memory.memory_optimization import MemoryTier
from memory.symbol_aware_tiered_memory import SymbolAwareTieredMemory


def test_store_and_retrieve():
    mem = SymbolAwareTieredMemory()
    mem.store("m1", {"data": 1}, symbols=["alpha"], is_dream=True, tier=MemoryTier.HOT)
    assert mem.retrieve("m1") == {"data": 1}
    dreams = mem.get_dream_flagged()
    assert len(dreams) == 1
    assert dreams[0]["id"] == "m1"
