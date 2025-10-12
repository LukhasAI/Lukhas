"""
🔌 Core Interface
==================

Interface module to break circular dependencies between:
core.efficient_communication <-> core.resource_optimization_integration
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Optional

from lukhas.core.common import GLYPHToken


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
    MEMORY = "lukhas.memory"
    POWER = "power"


class CoreInterface(ABC):
    """Abstract interface for core modules"""

    @abstractmethod
    async def process(self, data: dict[str, Any]) -> dict[str, Any]:
        """Process data through the module"""

    @abstractmethod
    async def handle_glyph(self, token: GLYPHToken) -> GLYPHToken:
        """Handle GLYPH token"""

    @abstractmethod
    async def get_status(self) -> dict[str, Any]:
        """Get module status"""


class CommunicationFabricInterface(ABC):
    """Interface for communication fabric"""

    @abstractmethod
    async def send_message(
        self,
        message: dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
    ) -> bool:
        """Send a message"""

    @abstractmethod
    async def broadcast(self, message: dict[str, Any]) -> int:
        """Broadcast message to all subscribers"""


class ResourceOptimizerInterface(ABC):
    """Interface for resource optimization"""

    @abstractmethod
    async def optimize(self, strategy: OptimizationStrategy = OptimizationStrategy.BALANCED) -> dict[str, Any]:
        """Optimize resources with given strategy"""

    @abstractmethod
    async def get_optimization_metrics(self) -> dict[str, Any]:
        """Get current optimization metrics"""


# Module registry for dependency injection
_module_registry: dict[str, CoreInterface] = {}


def register_module(name: str, module: CoreInterface) -> None:
    """Register module implementation"""
    _module_registry[name] = module


def get_module(name: str) -> Optional[CoreInterface]:
    """Get registered module"""
    return _module_registry.get(name)
