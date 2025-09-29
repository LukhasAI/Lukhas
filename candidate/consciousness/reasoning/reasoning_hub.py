import logging

logger = logging.getLogger(__name__)
"""
Reasoning Hub
Central coordination for reasoning subsystem components
"""

from typing import Any, Optional

from .ethical_reasoning_integration import create_ethical_reasoning_integration
from .LBot_reasoning_processed import ΛBotAdvancedReasoningOrchestrator


class ReasoningHub:
    """Central hub for reasoning system coordination"""

    def __init__(self) -> None:
        self.services: dict[str, Any] = {}
        self.event_handlers: dict[str, list[callable]] = {}
        self.is_initialized = False
        self.advanced_orchestrator = ΛBotAdvancedReasoningOrchestrator()
        self.register_service("advanced_orchestrator", self.advanced_orchestrator)

        # Initialize ethical reasoning integration
        self.ethical_reasoning = create_ethical_reasoning_integration()
        self.register_service("ethical_reasoning", self.ethical_reasoning)

        logger.info("reasoning_hub_initialized", service_count=len(self.services))

    def register_service(self, name: str, service: Any) -> None:
        """Register a service with the hub"""
        self.services[name] = service
        logger.debug("service_registered", service=name)

    def get_service(self, name: str) -> Optional[Any]:
        """Retrieve a registered service"""
        return self.services.get(name)

    async def initialize(self) -> None:
        """Initialize reasoning services and register with discovery"""
        if self.is_initialized:
            return

        # Initialize ethical reasoning system
        if hasattr(self.ethical_reasoning, "initialize"):
            await self.ethical_reasoning.initialize()
            logger.info("ethical_reasoning_initialized")

        await self._register_with_service_discovery()
        self.is_initialized = True
        logger.info("reasoning_hub_ready", service_count=len(self.services))

    async def _register_with_service_discovery(self) -> None:
        """Register services globally for cross-hub access"""
        try:
            from lukhas.core.integration.service_discovery import (
                get_service_discovery,
            )

            discovery = get_service_discovery()
            discovery.register_service_globally("advanced_orchestrator", self.advanced_orchestrator, "reasoning")
            discovery.register_service_globally("ethical_reasoning", self.ethical_reasoning, "reasoning")
            logger.debug("services_registered_globally")
        except Exception as exc:
            logger.warning("service_discovery_registration_failed", error=str(exc))


_reasoning_hub_instance: Optional[ReasoningHub] = None


def get_reasoning_hub() -> ReasoningHub:
    """Get or create the reasoning hub singleton instance"""
    global _reasoning_hub_instance
    if _reasoning_hub_instance is None:
        _reasoning_hub_instance = ReasoningHub()
    return _reasoning_hub_instance


async def initialize_reasoning_system() -> ReasoningHub:
    """Initialize the complete reasoning system"""
    hub = get_reasoning_hub()
    await hub.initialize()
    return hub


__all__ = [
    "ReasoningHub",
    "ΛBotAdvancedReasoningOrchestrator",
    "create_ethical_reasoning_integration",
    "get_reasoning_hub",
    "initialize_reasoning_system",
]
