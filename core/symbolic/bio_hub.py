"""

#TAG:core
#TAG:symbolic
#TAG:neuroplastic
#TAG:colony


Bio Hub
Central coordination for bio-symbolic subsystem components
"""

from typing import Dict, Any, Optional, List
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class BioHub:
    """Central hub for bio-symbolic system coordination"""

    def __init__(self):
        self.services: Dict[str, Any] = {}
        self.event_handlers: Dict[str, List[callable]] = {}
        self.is_initialized = False
        self._initialize_services()

        logger.info("Bio hub initialized")

    def _initialize_services(self):
        """Initialize all bio-symbolic services"""
        # Bio Processing Services
        self._register_bio_processing_services()

        # Bio-Symbolic Integration
        self._register_bio_symbolic_services()

        # Bio Analysis & Monitoring
        self._register_analysis_services()

        # Register services globally for cross-hub access
        self._register_with_service_discovery()

        # Mark as initialized
        self.is_initialized = True
        logger.info(f"Bio hub initialized with {len(self.services)} services")

    def _register_bio_processing_services(self):
        """Register bio processing services"""
        processing_services = [
            ("bio_processor", "BioProcessor"),
            ("bio_analyzer", "BioAnalyzer"),
            ("bio_transformer", "BioTransformer"),
            ("bio_validator", "BioValidator")
        ]

        for service_name, class_name in processing_services:
            try:
                module = __import__(f"bio.processing.{service_name}", fromlist=[class_name])
                cls = getattr(module, class_name)
                instance = cls()
                self.register_service(service_name, instance)
                logger.debug(f"Registered {class_name} as {service_name}")
            except (ImportError, AttributeError, TypeError) as e:
                logger.warning(f"Could not register {class_name}: {e}")

    def _register_bio_symbolic_services(self):
        """Register bio-symbolic integration services"""
        symbolic_services = [
            ("bio_symbolic_processor", "BioSymbolicProcessor"),
            ("bio_symbolic_fallback_manager", "BioSymbolicFallbackManager"),
            ("bio_symbolic_integrator", "BioSymbolicIntegrator"),
            ("bio_mapper", "BioMapper")
        ]

        for service_name, class_name in symbolic_services:
            try:
                if service_name == "bio_symbolic_processor":
                    module = __import__("bio.symbolic.processor", fromlist=[class_name])
                elif service_name == "bio_symbolic_fallback_manager":
                    module = __import__("bio.symbolic.fallback_systems", fromlist=[class_name])
                else:
                    module = __import__(f"bio.symbolic.{service_name}", fromlist=[class_name])

                cls = getattr(module, class_name)
                instance = cls()
                self.register_service(service_name, instance)
                logger.debug(f"Registered {class_name} as {service_name}")
            except (ImportError, AttributeError, TypeError) as e:
                logger.warning(f"Could not register {class_name}: {e}")

    def _register_analysis_services(self):
        """Register bio analysis services"""
        analysis_services = [
            ("coherence_optimizer", "CoherenceOptimizer"),
            ("bio_monitor", "BioMonitor"),
            ("pattern_detector", "BioPatternDetector")
        ]

        for service_name, class_name in analysis_services:
            try:
                module = __import__(f"bio.analysis.{service_name}", fromlist=[class_name])
                cls = getattr(module, class_name)
                instance = cls()
                self.register_service(service_name, instance)
                logger.debug(f"Registered {class_name} as {service_name}")
            except (ImportError, AttributeError, TypeError) as e:
                logger.warning(f"Could not register {class_name}: {e}")

    def _register_with_service_discovery(self):
        """Register services with global service discovery"""
        try:
            from core.service_discovery import get_service_discovery
            discovery = get_service_discovery()

            # Register key services globally for cross-hub access
            key_services = [
                "bio_symbolic_processor", "bio_symbolic_fallback_manager", "bio_processor",
                "bio_analyzer", "bio_symbolic_integrator", "bio_mapper", "coherence_optimizer",
                "bio_monitor", "pattern_detector"
            ]

            for service_name in key_services:
                if service_name in self.services:
                    discovery.register_service_globally(service_name, self.services[service_name], "bio")

            logger.debug(f"Registered {len(key_services)} bio services with global discovery")
        except Exception as e:
            logger.warning(f"Could not register with service discovery: {e}")

    def register_service(self, name: str, service: Any) -> None:
        """Register a service with the hub"""
        self.services[name] = service
        logger.debug(f"Registered service '{name}' with bio hub")

    def get_service(self, name: str) -> Optional[Any]:
        """Get a registered service"""
        return self.services.get(name)

    def register_event_handler(self, event_type: str, handler: callable) -> None:
        """Register an event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)

    async def process_bio_symbolic_event(self, bio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process bio data through symbolic reasoning"""

        # Bio processing first
        bio_processor = self.get_service("bio_processor")
        bio_result = None
        if bio_processor and hasattr(bio_processor, 'process'):
            try:
                bio_result = await bio_processor.process(bio_data)
            except Exception as e:
                logger.error(f"Bio processing error: {e}")
                bio_result = {"error": str(e)}

        # Then symbolic interpretation
        symbolic_processor = self.get_service("bio_symbolic_processor")
        symbolic_result = None
        if symbolic_processor and hasattr(symbolic_processor, 'interpret_bio_data'):
            try:
                symbolic_result = await symbolic_processor.interpret_bio_data(bio_result or bio_data)
            except Exception as e:
                logger.error(f"Symbolic processing error: {e}")
                symbolic_result = {"error": str(e)}

        return {
            "bio": bio_result,
            "symbolic": symbolic_result,
            "timestamp": datetime.now().isoformat(),
            "processed_by": "bio_hub"
        }

    async def process_event(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process an event through registered handlers"""
        handlers = self.event_handlers.get(event_type, [])
        results = []

        for handler in handlers:
            try:
                result = await handler(data) if asyncio.iscoroutinefunction(handler) else handler(data)
                results.append(result)
            except Exception as e:
                logger.error(f"Bio handler error for {event_type}: {e}")
                results.append({"error": str(e)})

        return {"event_type": event_type, "results": results}

    async def health_check(self) -> Dict[str, Any]:
        """Health check for all registered bio services"""
        health = {"status": "healthy", "services": {}}

        for name, service in self.services.items():
            try:
                if hasattr(service, 'health_check'):
                    health["services"][name] = await service.health_check()
                else:
                    health["services"][name] = {"status": "active"}
            except Exception as e:
                health["services"][name] = {"status": "error", "error": str(e)}
                health["status"] = "degraded"

        return health

# Singleton instance
_bio_hub_instance = None

def get_bio_hub() -> BioHub:
    """Get or create the bio hub instance"""
    global _bio_hub_instance
    if _bio_hub_instance is None:
        _bio_hub_instance = BioHub()
    return _bio_hub_instance