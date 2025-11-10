"""Bridge module for memory.memory_core → labs.memory.memory_core"""
from __future__ import annotations

from labs.memory.memory_core import CoreMemoryComponent, CoreMemoryConfig

# Also import consciousness interfaces if available
try:
    from labs.memory.memory_core import ConsciousnessPhase, QIMindInterface
    __all__ = ["CoreMemoryComponent", "CoreMemoryConfig", "ConsciousnessPhase", "QIMindInterface"]
except ImportError:
    # Fallback for basic memory functionality
    __all__ = ["CoreMemoryComponent", "CoreMemoryConfig"]
