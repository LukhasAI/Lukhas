"""
🔌 Memory Interface
====================

Interface module to break circular dependencies between:
memory.core.unified_memory_orchestrator <-> memory.systems.memory_comprehensive
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from enum import Enum
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
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data through the module"""
        pass
        
    @abstractmethod
    async def handle_glyph(self, token: GLYPHToken) -> GLYPHToken:
        """Handle GLYPH token"""
        pass
        
    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """Get module status"""
        pass


class MemoryTestInterface(ABC):
    """Interface for memory testing functions"""
    
    @abstractmethod
    async def test_error_conditions(self) -> Dict[str, Any]:
        """Test error handling conditions"""
        pass
        
    @abstractmethod
    async def test_memory_lifecycle(self) -> Dict[str, Any]:
        """Test memory lifecycle operations"""
        pass


# Module registry for dependency injection
_module_registry: Dict[str, MemoryInterface] = {}
_test_registry: Dict[str, MemoryTestInterface] = {}


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
