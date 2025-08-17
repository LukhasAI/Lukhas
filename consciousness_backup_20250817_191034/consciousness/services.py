#!/usr/bin/env python3
"""
Consciousness Services
Dependency injection services for the consciousness module.
"""

from typing import Any

from hub.service_registry import get_service, inject_services, register_factory


class ConsciousnessService:
    """
    Service layer for consciousness operations.
    Uses dependency injection to avoid circular imports.
    """

    def __init__(self):
        # Services will be injected as needed
        self._memory = None
        self._learning = None
        self._identity = None
        self._initialized = False

    def _ensure_services(self):
        """Lazy load services to avoid circular imports"""
        if not self._initialized:
            self._memory = get_service("memory_service")
            self._learning = get_service("learning_service")
            self._identity = get_service("identity_service")
            self._initialized = True

    @inject_services(
        memory="memory_service",
        learning="learning_service",
        identity="identity_service",
    )
    async def process_awareness(
        self,
        agent_id: str,
        stimulus: dict[str, Any],
        memory=None,
        learning=None,
        identity=None,
    ) -> dict[str, Any]:
        """
        Process awareness with injected dependencies.

        This method demonstrates how to use dependency injection
        to access other modules without direct imports.
        """
        # Verify identity access
        if not await identity.verify_access(agent_id, "consciousness"):
            raise PermissionError(f"Agent {agent_id} lacks consciousness access")

        # Store stimulus in memory
        memory_result = await memory.store_experience(
            agent_id, {"type": "awareness_stimulus", "data": stimulus}
        )

        # Process through learning if patterns detected
        if stimulus.get("pattern_detected", False):
            learning_result = await learning.process_pattern(agent_id, stimulus)
        else:
            learning_result = None

        return {
            "awareness_state": "processed",
            "memory_ref": memory_result.get("ref_id"),
            "learning_outcome": learning_result,
            "timestamp": memory_result.get("timestamp"),
        }

    async def integrate_experience(
        self, agent_id: str, experience: dict[str, Any]
    ) -> dict[str, Any]:
        """Integrate experience across consciousness systems"""
        self._ensure_services()

        # This method can access all services without circular imports
        result = {"integrated": True, "subsystems": []}

        # Memory integration
        if self._memory:
            memory_result = await self._memory.integrate(agent_id, experience)
            result["subsystems"].append({"memory": memory_result})

        # Learning integration
        if self._learning:
            learning_result = await self._learning.integrate(agent_id, experience)
            result["subsystems"].append({"learning": learning_result})

        return result


# Create service factory
def create_consciousness_service():
    """Factory function for consciousness service"""
    from consciousness.bridge import ConsciousnessBridge

    # Create bridge but wrap with service layer
    bridge = ConsciousnessBridge()
    service = ConsciousnessService()

    # Attach bridge methods to service
    service.bridge = bridge

    return service


# Register with hub on import

register_factory(
    "consciousness_service",
    create_consciousness_service,
    {"module": "consciousness", "provides": ["awareness", "integration", "binding"]},
)
