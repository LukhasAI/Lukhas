"""
Shared Memory Base Classes

Common base classes for memory-related components.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional


class MemoryManager(ABC):
    """Base class for memory managers."""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.memory_store = {}
        self.access_logs = []

    @abstractmethod
    def store(self, key: str, data: Any) -> str:
        """Store data in memory."""

    @abstractmethod
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data from memory."""

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete data from memory."""

    def log_access(self, key: str, operation: str, user_id: str):
        """Log memory access."""
        self.access_logs.append(
            {
                "key": key,
                "operation": operation,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
            }
        )


class MemoryAccessPolicy:
    """Base class for memory access policies."""

    def __init__(
        self,
        owner_id: str,
        public: bool = False,
        allowed_users: Optional[list[str]] = None,
    ):
        self.owner_id = owner_id
        self.public = public
        self.allowed_users = allowed_users or []

    def can_access(self, user_id: str) -> bool:
        """Check if user can access memory."""
        if self.public:
            return True
        if user_id == self.owner_id:
            return True
        return user_id in self.allowed_users


class MemoryIdentityIntegration:
    """Base class for memory-identity integration."""

    def __init__(self, memory_manager, identity_manager):
        self.memory_manager = memory_manager
        self.identity_manager = identity_manager

    def link_memory_to_identity(self, memory_key: str, identity_id: str):
        """Link memory to identity."""

    def get_identity_memories(self, identity_id: str) -> list[str]:
        """Get memories linked to identity."""
        return []
