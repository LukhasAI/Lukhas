"""Bridge module for core.quantized_thought_cycles → labs.core.quantized_thought_cycles"""
from __future__ import annotations

from labs.core.quantized_thought_cycles import (
    CycleManager,
    QuantizedThoughtCycles,
    create_thought_cycles,
)

__all__ = ["CycleManager", "QuantizedThoughtCycles", "create_thought_cycles"]
