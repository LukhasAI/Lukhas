"""Bridge module for memory.symbol_aware_tiered_memory → labs.memory.symbol_aware_tiered_memory"""
from __future__ import annotations

from labs.memory.symbol_aware_tiered_memory import (
    MemoryManager,
    SymbolAwareTieredMemory,
    create_tiered_memory,
)

__all__ = ["MemoryManager", "SymbolAwareTieredMemory", "create_tiered_memory"]
