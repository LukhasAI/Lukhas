"""
Module Interfaces
================
Interface definitions to break circular dependencies.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class IConsciousnessModule(ABC):
    """Interface for consciousness modules"""

    @abstractmethod
    async def get_awareness_state(self) -> dict[str, Any]:
        """Get current awareness state"""

    @abstractmethod
    async def update_awareness(self, state: dict[str, Any]) -> bool:
        """Update awareness state"""

    @abstractmethod
    async def process_reflection(self, input_data: Any) -> Any:
        """Process reflection request"""


class IMemoryModule(ABC):
    """Interface for memory modules"""

    @abstractmethod
    async def store(self, key: str, value: Any, metadata: Optional[dict[str, Any]] = None) -> bool:
        """Store data in memory"""

    @abstractmethod
    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data from memory"""

    @abstractmethod
    async def create_fold(self, fold_data: dict[str, Any]) -> str:
        """Create memory fold"""


class IOrchestrationModule(ABC):
    """Interface for orchestration modules"""

    @abstractmethod
    async def execute_task(self, task_id: str, params: dict[str, Any]) -> Any:
        """Execute orchestration task"""

    @abstractmethod
    async def get_task_status(self, task_id: str) -> dict[str, Any]:
        """Get task execution status"""

    @abstractmethod
    async def schedule_workflow(self, workflow: dict[str, Any]) -> str:
        """Schedule workflow execution"""


class IGovernanceModule(ABC):
    """Interface for governance modules"""

    @abstractmethod
    async def validate_action(self, action: str, context: dict[str, Any]) -> bool:
        """Validate if action is allowed"""

    @abstractmethod
    async def audit_log(self, event: dict[str, Any]) -> None:
        """Log audit event"""

    @abstractmethod
    async def check_policy(self, policy_id: str, data: Any) -> bool:
        """Check if data complies with policy"""


class ICoreModule(ABC):
    """Interface for core modules"""

    @abstractmethod
    async def process_glyph(self, glyph: Any) -> Any:
        """Process GLYPH symbol"""

    @abstractmethod
    async def get_system_status(self) -> dict[str, Any]:
        """Get system status"""

    @abstractmethod
    async def execute_symbolic_operation(self, operation: str, params: dict[str, Any]) -> Any:
        """Execute symbolic operation"""
