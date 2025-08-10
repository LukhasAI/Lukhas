"""
Common interfaces for LUKHAS PWM
================================
Consolidated interface definitions to reduce duplication.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


class BaseInterface(ABC):
    """Base interface for all LUKHAS components"""

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the component"""
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the component"""
        pass

    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """Get component status"""
        pass


class ProcessingInterface(BaseInterface):
    """Interface for components that process data"""

    @abstractmethod
    async def process(self, data: Any) -> Any:
        """Process input data"""
        pass

    @abstractmethod
    async def validate(self, data: Any) -> bool:
        """Validate input data"""
        pass


class StorageInterface(BaseInterface):
    """Interface for storage components"""

    @abstractmethod
    async def store(self, key: str, value: Any) -> bool:
        """Store a value"""
        pass

    @abstractmethod
    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a value"""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a value"""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        pass


class CommunicationInterface(BaseInterface):
    """Interface for inter-module communication"""

    @abstractmethod
    async def send_message(self, target: str, message: Any) -> bool:
        """Send a message to target"""
        pass

    @abstractmethod
    async def receive_message(self) -> Optional[Any]:
        """Receive next message"""
        pass

    @abstractmethod
    async def subscribe(self, topic: str) -> bool:
        """Subscribe to a topic"""
        pass

    @abstractmethod
    async def publish(self, topic: str, message: Any) -> bool:
        """Publish to a topic"""
        pass


@dataclass
class ModuleInfo:
    """Standard module information"""
    name: str
    version: str
    description: str
    dependencies: List[str]
    status: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'dependencies': self.dependencies,
            'status': self.status
        }
