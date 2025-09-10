"""
Common interfaces for LUKHAS
================================
Consolidated interface definitions to reduce duplication.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional


class BaseInterface(ABC):
    """Base interface for all LUKHAS components"""

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the component"""

    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the component"""

    @abstractmethod
    async def get_status(self) -> dict[str, Any]:
        """Get component status"""


class ProcessingInterface(BaseInterface):
    """Interface for components that process data"""

    @abstractmethod
    async def process(self, data: Any) -> Any:
        """Process input data"""

    @abstractmethod
    async def validate(self, data: Any) -> bool:
        """Validate input data"""


class StorageInterface(BaseInterface):
    """Interface for storage components"""

    @abstractmethod
    async def store(self, key: str, value: Any) -> bool:
        """Store a value"""

    @abstractmethod
    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a value"""

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a value"""

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists"""


class CommunicationInterface(BaseInterface):
    """Interface for inter-module communication"""

    @abstractmethod
    async def send_message(self, target: str, message: Any) -> bool:
        """Send a message to target"""

    @abstractmethod
    async def receive_message(self) -> Optional[Any]:
        """Receive next message"""

    @abstractmethod
    async def subscribe(self, topic: str) -> bool:
        """Subscribe to a topic"""

    @abstractmethod
    async def publish(self, topic: str, message: Any) -> bool:
        """Publish to a topic"""


@dataclass
class ModuleInfo:
    """Standard module information"""

    name: str
    version: str
    description: str
    dependencies: list[str]
    status: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "dependencies": self.dependencies,
            "status": self.status,
        }