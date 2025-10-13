"""
NIAS Hub
Central coordination for NIAS (Non-Intrusive Ad System) components
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)


class NIASHub:
    """Central hub for NIAS system coordination"""

    def __init__(self):
        self.services: dict[str, Any] = {}
        self.event_handlers: dict[str, list[callable]] = {}
        self.is_initialized = False
        self._initialize_services()

        logger.info("NIAS hub initialized")

    def _initialize_services(self):
        """Initialize all NIAS services"""
        # Cross-System Bridges (first, so they're available to other services)
        self._register_bridge_services()

        # Core NIAS Services
        self._register_core_nias_services()

        # NIAS Processing Components
        self._register_processing_services()

        # Register services globally for cross-hub access
        self._register_with_service_discovery()

        self.is_initialized = True
        logger.info(f"NIAS hub initialized with {len(self.services)} services")

    def _register_core_nias_services(self):
        """Register core NIAS services"""
        services = [
            ("nias_core", "NIASCore"),
            ("symbolic_matcher", "SymbolicMatcher"),
            ("consent_filter", "ConsentFilter"),
            ("dream_recorder", "DreamRecorder"),
        ]

        for service_name, class_name in services:
            try:
                module = __import__("core.modules.nias", fromlist=[class_name])
                cls = getattr(module, class_name)

                # Pass dream bridge to NIASCore if available
                if service_name == "nias_core" and hasattr(self, "dream_bridge"):
                    instance = cls(dream_bridge=self.dream_bridge)
                else:
                    instance = cls()

                self.register_service(service_name, instance)
                logger.debug(f"Registered {class_name} as {service_name}")
            except (ImportError, AttributeError, TypeError) as e:
                logger.warning(f"Could not register {class_name}: {e}")

    def _register_processing_services(self):
        """Register NIAS processing services"""
        services = [
            ("message_processor", "NIASMessageProcessor"),
            ("delivery_tracker", "DeliveryTracker"),
            ("feedback_processor", "FeedbackProcessor"),
        ]

        for service_name, class_name in services:
            try:
                module = __import__(f"core.modules.nias.{service_name}", fromlist=[class_name])
                cls = getattr(module, class_name)
                instance = cls()
                self.register_service(service_name, instance)
                logger.debug(f"Registered {class_name} as {service_name}")
            except (ImportError, AttributeError, TypeError) as e:
                logger.warning(f"Could not register {class_name}: {e}")

    def _register_bridge_services(self):
        """Register cross-system bridge services"""
        try:
            from dream.core.nias_dream_bridge import get_nias_dream_bridge

            self.dream_bridge = get_nias_dream_bridge()
            self.register_service("dream_bridge", self.dream_bridge)
            logger.debug("Registered NIAS-Dream bridge")
        except ImportError as e:
            logger.warning(f"Could not import nias_dream Bridge: {e}")

    def _register_with_service_discovery(self):
        """Register services with global service discovery"""
        try:
            from lukhas.core.integration.service_discovery import (
                get_service_discovery,
            )

            discovery = get_service_discovery()

            # Register key services globally for cross-hub access
            key_services = [
                "nias_core",
                "symbolic_matcher",
                "dream_recorder",
                "consent_filter",
                "message_processor",
                "delivery_tracker",
                "feedback_processor",
                "dream_bridge",
            ]

            for service_name in key_services:
                if service_name in self.services:
                    discovery.register_service_globally(service_name, self.services[service_name], "nias")

            logger.debug(f"Registered {len(key_services)} NIAS services with global discovery")
        except Exception as e:
            logger.warning(f"Could not register with service discovery: {e}")

    def register_service(self, name: str, service: Any) -> None:
        """Register a service with the hub"""
        self.services[name] = service
        logger.debug(f"Registered service '{name}' with NIAS hub")

    def get_service(self, name: str) -> Optional[Any]:
        """Get a registered service"""
        return self.services.get(name)

    def register_event_handler(self, event_type: str, handler: callable) -> None:
        """Register an event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)

    async def process_symbolic_message(self, message: dict[str, Any], user_context: dict[str, Any]) -> dict[str, Any]:
        """Process a symbolic message through NIAS system"""

        nias_core = self.get_service("nias_core")
        if nias_core and hasattr(nias_core, "push_symbolic_message"):
            try:
                result = await nias_core.push_symbolic_message(message, user_context)
                return {
                    "message_processed": True,
                    "result": result,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "processed_by": "nias_core",
                }
            except Exception as e:
                logger.error(f"NIAS core processing error: {e}")
                return {"error": str(e), "processed_by": "nias_core"}

        return {"error": "NIAS core not available"}

    async def process_event(self, event_type: str, data: dict[str, Any]) -> dict[str, Any]:
        """Process an event through registered handlers"""
        handlers = self.event_handlers.get(event_type, [])
        results = []

        for handler in handlers:
            try:
                result = await handler(data) if asyncio.iscoroutinefunction(handler) else handler(data)
                results.append(result)
            except Exception as e:
                logger.error(f"NIAS handler error for {event_type}: {e}")
                results.append({"error": str(e)})

        return {"event_type": event_type, "results": results}

    async def health_check(self) -> dict[str, Any]:
        """Health check for all registered NIAS services"""
        health = {"status": "healthy", "services": {}}

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
_nias_hub_instance = None


def get_nias_hub() -> NIASHub:
    """Get or create the NIAS hub instance"""
    global _nias_hub_instance
    if _nias_hub_instance is None:
        _nias_hub_instance = NIASHub()
    return _nias_hub_instance
