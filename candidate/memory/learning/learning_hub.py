"""
Learning Hub
Central coordination for learning subsystem components with meta-learning
"""

import asyncio
from datetime import datetime
from typing import Any, Optional

from candidate.core.common import get_logger

logger = get_logger(__name__)

# Import meta-learning enhancement system
try:
    from .metalearningenhancementsystem_wrapper import get_meta_learning_enhancement

    META_ENHANCEMENT_AVAILABLE = True
except ImportError as e:
    META_ENHANCEMENT_AVAILABLE = False
    logger.warning(f"Meta-learning enhancement system not available: {e}")

# Agent 1 Task 4: Add meta-learning enhancement system imports
try:
    from candidate.core.meta_learning.enhancement_system import (
        EnhancementMode as CoreEnhancementMode,
        MetaLearningEnhancementSystem as CoreMetaLearningEnhancementSystem,
        SystemIntegrationStatus as CoreSystemIntegrationStatus,
    )

    ENHANCEMENT_SYSTEM_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Enhancement system components not available: {e}")

    # Create fallback classes
    class CoreEnhancementMode:
        MONITORING_ONLY = "monitoring_only"
        OPTIMIZATION_ACTIVE = "optimization_active"

    class CoreSystemIntegrationStatus:
        def __init__(self):
            self.systems_enhanced = 0

    class CoreMetaLearningEnhancementSystem:
        def __init__(self, **kwargs):
            self.initialized = False

    ENHANCEMENT_SYSTEM_AVAILABLE = False


class LearningHub:
    """Central hub for learning system coordination"""

    def __init__(self):
        self.services: dict[str, Any] = {}
        self.event_handlers: dict[str, list] = {}
        self.learning_metrics: dict[str, Any] = {}
        self.is_initialized = False

        # Initialize meta-learning enhancement system if available
        self.meta_enhancement = None
        if META_ENHANCEMENT_AVAILABLE:
            try:
                self.meta_enhancement = get_meta_learning_enhancement()
                if self.meta_enhancement:
                    logger.info("Meta-learning enhancement system initialized")
            except Exception as e:
                logger.error(f"Failed to initialize meta-learning enhancement: {e}")

        # Agent 1 Task 4: Initialize core enhancement system
        self.enhancement_system = None
        if ENHANCEMENT_SYSTEM_AVAILABLE:
            try:
                self.enhancement_system = CoreMetaLearningEnhancementSystem(
                    node_id="learning_hub",
                    enhancement_mode=CoreEnhancementMode.OPTIMIZATION_ACTIVE,
                    enable_federation=False,
                )
                self.register_service("enhancement_system", self.enhancement_system)
                logger.info("Core meta-learning enhancement system initialized")
            except Exception as e:
                logger.error(f"Failed to initialize core enhancement system: {e}")

        self._initialize_services()

        logger.info("Learning hub initialized")

    def _initialize_services(self):
        """Initialize all learning services"""
        # Core Learning Services
        self._register_core_learning_services()

        # Meta-Learning Systems
        self._register_meta_learning_services()

        # Adaptive Learning Systems
        self._register_adaptive_services()

        # Federated Learning Components
        self._register_federated_services()

        # Learning Analysis & Enhancement
        self._register_analysis_services()

        # Initialize learning metrics
        self._initialize_learning_metrics()

        # Register services globally for cross-hub access
        self._register_with_service_discovery()

        self.is_initialized = True
        logger.info(f"Learning hub initialized with {len(self.services)} services")

    async def initialize(self):
        """Async initialization for learning hub"""
        if self.is_initialized:
            return

        # Initialize meta-learning enhancement if available
        if self.meta_enhancement:
            try:
                await self.meta_enhancement.initialize()
                logger.info("Meta-learning enhancement system fully initialized")
            except Exception as e:
                logger.error(f"Failed to initialize meta-learning enhancement: {e}")

    def _register_core_learning_services(self):
        """Register core learning services"""
        services = [
            ("learning_gateway", "LearningGateway"),
            ("meta_learning", "MetaLearning"),
            ("adaptive_meta_learning", "AdaptiveMetaLearning"),
            ("exponential_learning", "ExponentialLearning"),
            ("usage_learning", "UsageLearning"),
        ]

        for service_name, class_name in services:
            try:
                module = __import__(f"learning.{service_name}", fromlist=[class_name])
                cls = getattr(module, class_name)
                instance = cls()
                self.register_service(service_name, instance)
                logger.debug(f"Registered {class_name} as {service_name}")
            except (ImportError, AttributeError, TypeError) as e:
                logger.warning(f"Could not register {class_name}: {e}")

    def _register_meta_learning_services(self):
        """Register meta-learning services"""
        services = [
            ("meta_core", "MetaCore"),
            ("symbolic_feedback", "SymbolicFeedback"),
            ("federated_integration", "FederatedIntegration"),
            ("meta_learning_adapter", "MetaLearningAdapter"),
            ("meta_learning_recovery", "MetaLearningRecovery"),
        ]

        # Register meta-learning enhancement system if available
        if self.meta_enhancement:
            self.register_service("meta_learning_enhancement", self.meta_enhancement)
            logger.info("Meta-learning enhancement system registered")

        for service_name, class_name in services:
            try:
                if service_name in [
                    "meta_core",
                    "symbolic_feedback",
                    "federated_integration",
                ]:
                    module = __import__(
                        f"learning.meta_learning.{service_name}", fromlist=[class_name]
                    )
                else:
                    module = __import__(
                        f"learning.{service_name}", fromlist=[class_name]
                    )

                cls = getattr(module, class_name)
                instance = cls()
                self.register_service(service_name, instance)
                logger.debug(f"Registered {class_name} as {service_name}")
            except (ImportError, AttributeError, TypeError) as e:
                logger.warning(f"Could not register {class_name}: {e}")

    def _register_adaptive_services(self):
        """Register adaptive learning services"""
        services = [
            ("adaptive_interface_generator", "AdaptiveInterfaceGenerator"),
            ("adaptive_ux_core", "AdaptiveUXCore"),
            ("system", "System"),
        ]

        for service_name, class_name in services:
            try:
                module = __import__(
                    f"learning.meta_adaptive.{service_name}", fromlist=[class_name]
                )
                cls = getattr(module, class_name)
                instance = cls()
                self.register_service(service_name, instance)
                logger.debug(f"Registered {class_name} as {service_name}")
            except (ImportError, AttributeError, TypeError) as e:
                logger.warning(f"Could not register {class_name}: {e}")

    def _register_federated_services(self):
        """Register federated learning services"""
        services = [
            ("federated_learning", "FederatedLearning"),
            ("federated_learning_system", "FederatedLearningSystem"),
            ("federated_meta_learning", "FederatedMetaLearning"),
            ("federated_colony_learning", "FederatedColonyLearning"),
        ]

        for service_name, class_name in services:
            try:
                module = __import__(f"learning.{service_name}", fromlist=[class_name])
                cls = getattr(module, class_name)
                instance = cls()
                self.register_service(service_name, instance)
                logger.debug(f"Registered {class_name} as {service_name}")
            except (ImportError, AttributeError, TypeError) as e:
                logger.warning(f"Could not register {class_name}: {e}")

    def _register_analysis_services(self):
        """Register learning analysis services"""
        services = [
            ("neural_integrator", "NeuralIntegrator"),
            ("plugin_learning_engine", "PluginLearningEngine"),
            ("doc_generator_learning_engine", "DocGeneratorLearningEngine"),
            ("tutor_learning_engine", "TutorLearningEngine"),
            ("generative_reflex", "GenerativeReflex"),
        ]

        for service_name, class_name in services:
            try:
                if service_name == "generative_reflex":
                    module = __import__(
                        f"learning.embodied_thought.{service_name}",
                        fromlist=[class_name],
                    )
                else:
                    module = __import__(
                        f"learning.{service_name}", fromlist=[class_name]
                    )

                cls = getattr(module, class_name)
                instance = cls()
                self.register_service(service_name, instance)
                logger.debug(f"Registered {class_name} as {service_name}")
            except (ImportError, AttributeError, TypeError) as e:
                logger.warning(f"Could not register {class_name}: {e}")

    def _initialize_learning_metrics(self):
        """Initialize learning metrics tracking"""
        self.learning_metrics = {
            "learning_sessions": 0,
            "adaptation_events": 0,
            "meta_learning_cycles": 0,
            "federated_updates": 0,
            "performance_improvements": [],
            "last_updated": datetime.now().isoformat(),
        }
        logger.debug("Learning metrics initialized")

    def _register_with_service_discovery(self):
        """Register services with global service discovery"""
        try:
            from candidate.core.integration.service_discovery import (
                get_service_discovery,
            )

            discovery = get_service_discovery()

            # Register key services globally for cross-hub access
            key_services = [
                "learning_gateway",
                "meta_learning",
                "adaptive_meta_learning",
                "exponential_learning",
                "meta_core",
                "symbolic_feedback",
                "federated_integration",
                "adaptive_interface_generator",
                "learning_optimizer",
                "learning_validator",
            ]

            for service_name in key_services:
                if service_name in self.services:
                    discovery.register_service_globally(
                        service_name, self.services[service_name], "learning"
                    )

            logger.debug(
                f"Registered {len(key_services)} learning services with global discovery"
            )
        except Exception as e:
            logger.warning(f"Could not register with service discovery: {e}")

    def register_service(self, name: str, service: Any) -> None:
        """Register a service with the hub"""
        self.services[name] = service
        logger.debug(f"Registered service '{name}' with learning hub")

    def get_service(self, name: str) -> Optional[Any]:
        """Get a registered service"""
        return self.services.get(name)

    def register_event_handler(self, event_type: str, handler) -> None:
        """Register an event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)

    # Agent 1 Task 4: Add enhancement system methods to LearningHub
    async def start_enhancement_operations(self) -> bool:
        """Start meta-learning enhancement operations"""
        if not self.enhancement_system:
            logger.warning("Enhancement system not available")
            return False

        try:
            # Discover existing learning systems for enhancement
            await self.enhancement_system.discover_and_enhance_meta_learning_systems()

            # Start enhancement operations
            await self.enhancement_system.start_enhancement_operations()

            logger.info("Enhancement operations started successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to start enhancement operations: {e}")
            return False

    async def get_enhancement_status(self) -> dict[str, Any]:
        """Get current enhancement system status"""
        if not self.enhancement_system:
            return {
                "status": "unavailable",
                "error": "Enhancement system not initialized",
            }

        try:
            status = self.enhancement_system.integration_status
            return {
                "status": "active",
                "systems_found": status.meta_learning_systems_found,
                "systems_enhanced": status.systems_enhanced,
                "monitoring_active": status.monitoring_active,
                "rate_optimization_active": status.rate_optimization_active,
                "symbolic_feedback_active": status.symbolic_feedback_active,
                "federation_enabled": status.federation_enabled,
                "last_health_check": status.last_health_check.isoformat(),
                "integration_errors": status.integration_errors,
            }
        except Exception as e:
            logger.error(f"Failed to get enhancement status: {e}")
            return {"status": "error", "error": str(e)}

    async def run_enhancement_cycle(self) -> dict[str, Any]:
        """Run a single enhancement cycle"""
        if not self.enhancement_system:
            return {"success": False, "error": "Enhancement system not available"}

        try:
            result = await self.enhancement_system.run_enhancement_cycle()
            self.learning_metrics["enhancement_cycles"] = (
                self.learning_metrics.get("enhancement_cycles", 0) + 1
            )
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"Enhancement cycle failed: {e}")
            return {"success": False, "error": str(e)}

    async def process_learning_event(
        self, learning_data: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        """Process a learning event through the learning system"""

        # Route through meta-learning first
        meta_core = self.get_service("meta_core")
        meta_result = None
        if meta_core and hasattr(meta_core, "process_learning"):
            try:
                meta_result = await meta_core.process_learning(learning_data, context)
                self.learning_metrics["meta_learning_cycles"] += 1
            except Exception as e:
                logger.error(f"Meta-learning processing error: {e}")
                meta_result = {"error": str(e)}

        # Process through adaptive learning
        adaptive_core = self.get_service("adaptive_ux_core")
        adaptive_result = None
        if adaptive_core and hasattr(adaptive_core, "adapt_from_learning"):
            try:
                adaptive_result = await adaptive_core.adapt_from_learning(
                    meta_result or learning_data
                )
                self.learning_metrics["adaptation_events"] += 1
            except Exception as e:
                logger.error(f"Adaptive learning error: {e}")
                adaptive_result = {"error": str(e)}

        # Update learning metrics
        self.learning_metrics["learning_sessions"] += 1
        self.learning_metrics["last_updated"] = datetime.now().isoformat()

        return {
            "meta_learning": meta_result,
            "adaptive_learning": adaptive_result,
            "learning_metrics": self.learning_metrics,
            "timestamp": datetime.now().isoformat(),
            "processed_by": "learning_hub",
        }

    async def process_federated_update(
        self, update_data: dict[str, Any], source_context: dict[str, Any]
    ) -> dict[str, Any]:
        """Process federated learning updates"""

        federated_system = self.get_service("federated_learning_system")
        if federated_system and hasattr(federated_system, "process_update"):
            try:
                result = await federated_system.process_update(
                    update_data, source_context
                )
                self.learning_metrics["federated_updates"] += 1
                self.learning_metrics["last_updated"] = datetime.now().isoformat()

                return {
                    "federated_update": result,
                    "source": source_context.get("source", "unknown"),
                    "timestamp": datetime.now().isoformat(),
                    "processed_by": "federated_learning_system",
                }
            except Exception as e:
                logger.error(f"Federated learning error: {e}")
                return {"error": str(e), "processed_by": "federated_learning_system"}

        return {"error": "Federated learning system not available"}

    def register_learning_feedback(
        self, feedback_type: str, feedback_data: dict[str, Any]
    ):
        """Register learning feedback for continuous improvement"""
        # This method will be used by other hubs to provide learning feedback

        symbolic_feedback = self.get_service("symbolic_feedback")
        if symbolic_feedback and hasattr(symbolic_feedback, "register_feedback"):
            try:
                symbolic_feedback.register_feedback(feedback_type, feedback_data)
                logger.debug(f"Learning feedback registered: {feedback_type}")
            except Exception as e:
                logger.error(f"Learning feedback registration error: {e}")

    async def process_event(
        self, event_type: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Process an event through registered handlers"""
        handlers = self.event_handlers.get(event_type, [])
        results = []

        for handler in handlers:
            try:
                result = (
                    await handler(data)
                    if asyncio.iscoroutinefunction(handler)
                    else handler(data)
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Learning handler error for {event_type}: {e}")
                results.append({"error": str(e)})

        return {"event_type": event_type, "results": results}

    async def health_check(self) -> dict[str, Any]:
        """Health check for all registered learning services"""
        health = {
            "status": "healthy",
            "services": {},
            "learning_metrics": self.learning_metrics,
            "timestamp": datetime.now().isoformat(),
            "hub": "learning",
        }

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

    def get_learning_metrics(self) -> dict[str, Any]:
        """Get current learning metrics"""
        return self.learning_metrics.copy()

    def reset_learning_metrics(self):
        """Reset learning metrics"""
        self._initialize_learning_metrics()
        logger.info("Learning metrics reset")


# Singleton instance
_learning_hub_instance = None


def get_learning_hub() -> LearningHub:
    """Get or create the learning hub instance"""
    global _learning_hub_instance
    if _learning_hub_instance is None:
        _learning_hub_instance = LearningHub()
    return _learning_hub_instance
