"""
Event Adapters for LUKHAS Modules
=================================
Adapts existing module communication to use event bus.
"""

import logging
from typing import Any, Dict

from .event_bus import Event, EventTypes, event_bus

logger = logging.getLogger(__name__)


class ConsciousnessEventAdapter:
    """Adapter for consciousness module events"""

    def __init__(self, consciousness_module):
        self.module = consciousness_module
        self._register_handlers()

    def _register_handlers(self):
        """Register event handlers"""
        event_bus.subscribe(EventTypes.MODULE_INITIALIZED, self._on_module_initialized)

    def _on_module_initialized(self, event: Event):
        """Handle module initialization events"""
        if event.source_module != "consciousness":
            logger.info(f"Consciousness aware of {event.source_module} initialization")

    async def emit_awareness_changed(self, new_state: Dict[str, Any]):
        """Emit awareness changed event"""
        await event_bus.publish(
            Event(
                event_type=EventTypes.AWARENESS_CHANGED,
                source_module="consciousness",
                payload={"new_state": new_state},
            )
        )


class MemoryEventAdapter:
    """Adapter for memory module events"""

    def __init__(self, memory_module):
        self.module = memory_module
        self._register_handlers()

    def _register_handlers(self):
        """Register event handlers"""
        event_bus.subscribe(
            EventTypes.MEMORY_STORED, self._on_memory_stored, is_async=True
        )

    async def _on_memory_stored(self, event: Event):
        """Handle memory stored events"""
        # Could trigger related operations

    async def emit_fold_created(self, fold_id: str, fold_data: Dict[str, Any]):
        """Emit fold created event"""
        await event_bus.publish(
            Event(
                event_type=EventTypes.FOLD_CREATED,
                source_module="memory",
                payload={"fold_id": fold_id, "data": fold_data},
            )
        )


class OrchestrationEventAdapter:
    """Adapter for orchestration module events"""

    def __init__(self, orchestration_module):
        self.module = orchestration_module
        self._register_handlers()

    def _register_handlers(self):
        """Register event handlers"""
        event_bus.subscribe(EventTypes.TASK_COMPLETED, self._on_task_completed)

    def _on_task_completed(self, event: Event):
        """Handle task completion events"""
        task_id = event.payload.get("task_id")
        logger.info(f"Task {task_id} completed, updating orchestration state")

    async def emit_workflow_triggered(self, workflow_id: str):
        """Emit workflow triggered event"""
        await event_bus.publish(
            Event(
                event_type=EventTypes.WORKFLOW_TRIGGERED,
                source_module="orchestration",
                payload={"workflow_id": workflow_id},
            )
        )


# Factory functions for creating adapters
def create_consciousness_adapter(module):
    """Create consciousness event adapter"""
    return ConsciousnessEventAdapter(module)


def create_memory_adapter(module):
    """Create memory event adapter"""
    return MemoryEventAdapter(module)


def create_orchestration_adapter(module):
    """Create orchestration event adapter"""
    return OrchestrationEventAdapter(module)
