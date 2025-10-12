"""
Dream Hub
Central coordination for dream processing subsystem components
"""
import streamlit as st
from datetime import timezone

import asyncio
import logging
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)


class DreamHub:
    """Central hub for dream system coordination"""

    def __init__(self):
        self.services: dict[str, Any] = {}
        self.event_handlers: dict[str, list[callable]] = {}
        self.is_initialized = False
        self._initialize_services()

        logger.info("Dream hub initialized")

    def _initialize_services(self):
        """Initialize all dream services"""
        # Dream Processing Services
        self._register_dream_processing_services()

        # Dream Integration Services
        self._register_integration_services()

        self.is_initialized = True
        logger.info(f"Dream hub initialized with {len(self.services)} services")

    def _register_dream_processing_services(self):
        """Register dream processing services"""
        services = [
            ("dream_processor", "DreamProcessor"),
            ("dream_recorder", "DreamRecorder"),
            ("dream_interpreter", "DreamInterpreter"),
            ("dream_synthesizer", "DreamSynthesizer"),
        ]

        for service_name, class_name in services:
            try:
                if service_name == "dream_recorder":
                    # Import from nias_module
                    module = __import__("core.modules.nias", fromlist=[class_name])
                else:
                    module = __import__(
                        f"orchestration.dream.{service_name}",
                        fromlist=[class_name],
                    )

                cls = getattr(module, class_name)
                instance = cls()
                self.register_service(service_name, instance)
                logger.debug(f"Registered {class_name} as {service_name}")
            except (ImportError, AttributeError, TypeError) as e:
                logger.warning(f"Could not register {class_name}: {e}")

    def _register_integration_services(self):
        """Register dream integration services"""
        services = [
            ("nias_dream_bridge", "NIASDreamBridge"),
            ("consciousness_dream_link", "ConsciousnessDreamLink"),
        ]

        for service_name, class_name in services:
            try:
                module = __import__(
                    f"orchestration.dream.{service_name}",
                    fromlist=[class_name],
                )
                cls = getattr(module, class_name)
                instance = cls()
                self.register_service(service_name, instance)
                logger.debug(f"Registered {class_name} as {service_name}")
            except (ImportError, AttributeError, TypeError) as e:
                logger.warning(f"Could not register {class_name}: {e}")

    def register_service(self, name: str, service: Any) -> None:
        """Register a service with the hub"""
        self.services[name] = service
        logger.debug(f"Registered service '{name}' with dream hub")

    def get_service(self, name: str) -> Optional[Any]:
        """Get a registered service"""
        return self.services.get(name)

    def register_event_handler(self, event_type: str, handler: callable) -> None:
        """Register an event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)

    async def process_dream_message(self, message: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Process a message for dream integration"""

        dream_recorder = self.get_service("dream_recorder")
        if dream_recorder and hasattr(dream_recorder, "record_dream_message"):
            try:
                result = await dream_recorder.record_dream_message(message, context)
                return {
                    "dream_recorded": True,
                    "result": result,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "processed_by": "dream_recorder",
                }
            except Exception as e:
                logger.error(f"Dream recording error: {e}")
                return {"error": str(e), "processed_by": "dream_recorder"}

        return {"error": "Dream recorder not available"}

    async def process_event(self, event_type: str, data: dict[str, Any]) -> dict[str, Any]:
        """Process an event through registered handlers"""
        handlers = self.event_handlers.get(event_type, [])
        results = []

        for handler in handlers:
            try:
                result = await handler(data) if asyncio.iscoroutinefunction(handler) else handler(data)
                results.append(result)
            except Exception as e:
                logger.error(f"Dream handler error for {event_type}: {e}")
                results.append({"error": str(e)})

        return {"event_type": event_type, "results": results}

    async def health_check(self) -> dict[str, Any]:
        """Health check for all registered dream services"""
        health = {"status": "healthy", "services": {}  # noqa: invalid-syntax  # TODO: Expected }, found newline

        for name, service in self.services.items():
            try:
                if hasattr(service, "health_check"):
                    health["services"][name] = await service.health_check()
                else:
                    health["services"][name] = {"status": "active"}
            except Exception as e:
                health["services"][name] = {"status": "error", "error": str(e)}
                health["status"] = "degraded"

        return health


# Singleton instance
_dream_hub_instance = None


def get_dream_hub() -> DreamHub:
    """Get or create the dream hub instance"""
    global _dream_hub_instance
    if _dream_hub_instance is None:
        _dream_hub_instance = DreamHub()
    return _dream_hub_instance
