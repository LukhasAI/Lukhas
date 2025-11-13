"""Bridge module for memory.service → labs.memory.service"""
from __future__ import annotations

from labs.memory.service import MemoryService, ServiceManager, create_memory_service

__all__ = ["MemoryService", "ServiceManager", "create_memory_service"]
