"""
#AIM{core}
The Observatory
===============

Provides a sandboxed environment for structured external scrutiny by accredited third parties.
This module allows for read-only introspection of the AI's reasoning and memory,
without risking the integrity of the live system.
"""
from typing import Any, Optional

from lukhas.consciousness.reflection.unified_memory_manager import (
    EnhancedMemoryManager as MemoryManager,
)

from .symbolic.tracer import DecisionTrail, SymbolicTracer


class Observatory:
    """
    A sandboxed environment for external scrutiny.
    """

    def __init__(
        self,
        tracer: SymbolicTracer,
        memory_manager: MemoryManager,
        read_only: bool = True,
    ):
        self.tracer = tracer
        self.memory_manager = memory_manager
        self.read_only = read_only

    def get_decision_trail(self, trail_id: str) -> Optional[DecisionTrail]:
        """
        Retrieves a decision trail by its ID.
        """
        return self.tracer.get_trail(trail_id)

    async def query_memory(self, query: str) -> dict[str, Any]:
        """
        Queries the memory manager.
        """
        if self.read_only:
            # In a real implementation, we would have a read-only view of the memory
            # For now, we'll just simulate a read-only query
            return await self.memory_manager.retrieve_memory(query)
        else:
            # This part should not be accessible in a real observatory
            raise PermissionError("Write operations are not allowed in the Observatory.")

    def get_system_status(self) -> dict[str, Any]:
        """
        Returns the current status of the system.
        """
        return {
            "active_decision_trails": len(self.tracer.active_trails),
            "total_traces": len(self.tracer.trace_log),
            "active_memory_folds": len(self.memory_manager.get_active_folds()),
            "read_only_mode": self.read_only,
        }