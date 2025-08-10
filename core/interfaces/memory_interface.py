"""
🔌 Memory Interface
====================

Interface module to break circular dependencies between:
memory.core.unified_memory_orchestrator <-> memory.systems.memory_comprehensive
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Optional

from core.common import GLYPHToken


class MemoryType(Enum):
    """Memory type enumeration shared between modules"""

    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    WORKING = "working"
    LONG_TERM = "long_term"
    SHORT_TERM = "short_term"


class MemoryInterface(ABC):
    """Abstract interface for memory modules"""

    @abstractmethod
    async def process(self, data: dict[str, Any]) -> dict[str, Any]:
        """Process data through the module"""

    @abstractmethod
    async def handle_glyph(self, token: GLYPHToken) -> GLYPHToken:
        """Handle GLYPH token"""

    @abstractmethod
    async def get_status(self) -> dict[str, Any]:
        """Get module status"""


class MemoryTestInterface(ABC):
    """Interface for memory testing functions"""

    @abstractmethod
    async def test_error_conditions(self) -> dict[str, Any]:
        """Test error handling conditions"""

    @abstractmethod
    async def test_memory_lifecycle(self) -> dict[str, Any]:
        """Test memory lifecycle operations"""


# Module registry for dependency injection
_module_registry: dict[str, MemoryInterface] = {}
_test_registry: dict[str, MemoryTestInterface] = {}


def register_module(name: str, module: MemoryInterface) -> None:
    """Register module implementation"""
    _module_registry[name] = module


def get_module(name: str) -> Optional[MemoryInterface]:
    """Get registered module"""
    return _module_registry.get(name)


def register_test_module(name: str, module: MemoryTestInterface) -> None:
    """Register test module implementation"""
    _test_registry[name] = module


def get_test_module(name: str) -> Optional[MemoryTestInterface]:
    """Get registered test module"""
    return _test_registry.get(name)
