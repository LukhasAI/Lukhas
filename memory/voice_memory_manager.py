"""Bridge module for memory.voice_memory_manager → labs.memory.voice_memory_manager"""
from __future__ import annotations

from labs.memory.voice_memory_manager import (
    ManagerInterface,
    VoiceMemoryManager,
    create_voice_manager,
)

__all__ = ["ManagerInterface", "VoiceMemoryManager", "create_voice_manager"]
