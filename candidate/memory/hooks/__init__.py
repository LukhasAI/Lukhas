"""Memory Hook Interface

This module provides extensibility points for memory management,
allowing plugins to process memory items before storage and after recall.

ΛTAG: memory_hooks_interface
"""

from .base import HookExecutionError, MemoryHook, MemoryItem
from .registry import HookPriority, HookRegistrationError, HookRegistry

__all__ = [
    "HookExecutionError",
    "HookPriority",
    "HookRegistrationError",
    "HookRegistry",
    "MemoryHook",
    "MemoryItem",
]

# Module metadata
__version__ = "1.0.0"
__author__ = "LUKHAS AGI Team"
