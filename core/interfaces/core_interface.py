"""
🔌 Core Interface
==================

Interface module to break circular dependencies between:
core.efficient_communication <-> core.resource_optimization_integration
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum
from core.common import GLYPHToken


class MessagePriority(Enum):
    """Message priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class CommunicationMode(Enum):
    """Communication mode types"""
    SYNC = "sync"
    ASYNC = "async"
    BROADCAST = "broadcast"
    DIRECT = "direct"


class OptimizationStrategy(Enum):
    """Resource optimization strategies"""
    BALANCED = "balanced"
    PERFORMANCE = "performance"
    MEMORY = "memory"
    POWER = "power"


class CoreInterface(ABC):
    """Abstract interface for core modules"""
    
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


class CommunicationFabricInterface(ABC):
    """Interface for communication fabric"""
    
    @abstractmethod
    async def send_message(self, message: Dict[str, Any], priority: MessagePriority = MessagePriority.NORMAL) -> bool:
        """Send a message"""
        pass
    
    @abstractmethod 
    async def broadcast(self, message: Dict[str, Any]) -> int:
        """Broadcast message to all subscribers"""
        pass


class ResourceOptimizerInterface(ABC):
    """Interface for resource optimization"""
    
    @abstractmethod
    async def optimize(self, strategy: OptimizationStrategy = OptimizationStrategy.BALANCED) -> Dict[str, Any]:
        """Optimize resources with given strategy"""
        pass
    
    @abstractmethod
    async def get_optimization_metrics(self) -> Dict[str, Any]:
        """Get current optimization metrics"""
        pass


# Module registry for dependency injection
_module_registry: Dict[str, CoreInterface] = {}


def register_module(name: str, module: CoreInterface) -> None:
    """Register module implementation"""
    _module_registry[name] = module
    

def get_module(name: str) -> Optional[CoreInterface]:
    """Get registered module"""
    return _module_registry.get(name)
