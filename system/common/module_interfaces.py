"""
Module Interfaces
================
Interface definitions to break circular dependencies.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class IConsciousnessModule(ABC):
    """Interface for consciousness modules"""

    @abstractmethod
    async def get_awareness_state(self) -> Dict[str, Any]:
        """Get current awareness state"""
        pass

    @abstractmethod
    async def update_awareness(self, state: Dict[str, Any]) -> bool:
        """Update awareness state"""
        pass

    @abstractmethod
    async def process_reflection(self, input_data: Any) -> Any:
        """Process reflection request"""
        pass


class IMemoryModule(ABC):
    """Interface for memory modules"""

    @abstractmethod
    async def store(self, key: str, value: Any, metadata: Dict[str, Any] = None) -> bool:
        """Store data in memory"""
        pass

    @abstractmethod
    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data from memory"""
        pass

    @abstractmethod
    async def create_fold(self, fold_data: Dict[str, Any]) -> str:
        """Create memory fold"""
        pass


class IOrchestrationModule(ABC):
    """Interface for orchestration modules"""

    @abstractmethod
    async def execute_task(self, task_id: str, params: Dict[str, Any]) -> Any:
        """Execute orchestration task"""
        pass

    @abstractmethod
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get task execution status"""
        pass

    @abstractmethod
    async def schedule_workflow(self, workflow: Dict[str, Any]) -> str:
        """Schedule workflow execution"""
        pass


class IGovernanceModule(ABC):
    """Interface for governance modules"""

    @abstractmethod
    async def validate_action(self, action: str, context: Dict[str, Any]) -> bool:
        """Validate if action is allowed"""
        pass

    @abstractmethod
    async def audit_log(self, event: Dict[str, Any]) -> None:
        """Log audit event"""
        pass

    @abstractmethod
    async def check_policy(self, policy_id: str, data: Any) -> bool:
        """Check if data complies with policy"""
        pass


class ICoreModule(ABC):
    """Interface for core modules"""

    @abstractmethod
    async def process_glyph(self, glyph: Any) -> Any:
        """Process GLYPH symbol"""
        pass

    @abstractmethod
    async def get_system_status(self) -> Dict[str, Any]:
        """Get system status"""
        pass

    @abstractmethod
    async def execute_symbolic_operation(self, operation: str, params: Dict[str, Any]) -> Any:
        """Execute symbolic operation"""
        pass
