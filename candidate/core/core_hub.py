"""
Core System Hub
Core system coordination

This hub coordinates all core subsystem components and provides
a unified interface for external systems to interact with core.

"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Optional

try:
    from candidate.core.bio_symbolic_swarm_hub import BioSymbolicSwarmHub
    from candidate.core.cluster_sharding import ShardManager
    from candidate.core.core_system import LukhasCore
    from candidate.core.enhanced_swarm import EnhancedSwarmHub

    # Agent 1 Task 2: Add event replay and snapshot system imports
    from candidate.core.event_replay_snapshot import (
        ActorStateSnapshot,
        Event,
        EventStore,
        EventType,
        SnapshotStore,
    )
    from candidate.core.id import LukhosIDManager
    from candidate.core.integrator import (
        BioOrchestrator,
        CoreMessageType,
        EnhancedCoreConfig,
        EnhancedCoreIntegrator,
    )

    # Agent 1 Task 5: Add resource efficiency analyzer imports
    from candidate.core.resource_efficiency_analyzer import (
        EfficiencyReport,
        ResourceEfficiencyAnalyzer,
        ResourceSnapshot,
        ResourceTrend,
        ResourceType,
    )
    from candidate.core.swarm import SwarmHub
except Exception as e:
    logging.error(f"Failed to import LUKHΛS CORE components: {e}")
    SwarmHub = object
    (
        EnhancedCoreConfig,
        CoreMessageType,
        EnhancedCoreIntegrator,
        BioOrchestrator,
    ) = (
        object,
        object,
        object,
        object,
    )
    CoreConsciousnessBridge = object
    LukhosIDManager = object
    ShardManager = object
    EnhancedSwarmHub = object
    LukhasCore = object
    BioSymbolicSwarmHub = object
    # Agent 1 Task 2: Add fallback objects for event replay components
    EventType = object
    Event = object
    ActorStateSnapshot = object
    EventStore = object
    SnapshotStore = object
    # Agent 1 Task 5: Add fallback objects for resource efficiency analyzer
    ResourceType = object
    ResourceSnapshot = object
    ResourceTrend = object
    EfficiencyReport = object
    ResourceEfficiencyAnalyzer = object
from lukhas.core.bridges.core_consciousness_bridge import CoreConsciousnessBridge
from lukhas.core.bridges.core_safety_bridge import CoreSafetyBridge

# Task 3A: Add connectivity imports
try:
    from candidate.orchestration.golden_trio.trio_orchestrator import TrioOrchestrator
except ImportError:
    TrioOrchestrator = None
    logging.warning("TrioOrchestrator not available")

try:
    from candidate.bridge.integration_bridge import IntegrationBridge
except ImportError:
    IntegrationBridge = None
    logging.warning("IntegrationBridge not available")

try:
    from ethics.service import EthicsService
except ImportError:
    EthicsService = None
    logging.warning("EthicsService not available")

logger = logging.getLogger(__name__)


class CoreHub:
    """
    Central coordination hub for the core system.

    Manages all core components and provides service discovery,
    coordination, and communication with other systems.
    """

    def __init__(self):
        self.name = "core_hub"
        self.services: dict[str, Any] = {}
        self.event_handlers: dict[str, list[callable]] = {}
        self.is_initialized = False
        self.connected_hubs: list[dict[str, Any]] = []

        # Initialize components
        self.swarm = SwarmHub()
        self.register_service("swarm", self.swarm)
        self.enhancedconfig = EnhancedCoreConfig()
        self.register_service("enhancedconfig", self.enhancedconfig)
        # CoreMessageType is an enum, not instantiable
        self.register_service("messagetype", CoreMessageType)
        self.enhancedintegrator = EnhancedCoreIntegrator()
        self.register_service("enhancedintegrator", self.enhancedintegrator)
        # Initialize BioOrchestrator with proper error handling
        try:
            self.bioorchestrator = BioOrchestrator()
        except Exception as e:
            # Create minimal fallback if BioOrchestrator fails
            logger.warning(f"BioOrchestrator init failed: {e}, using fallback")

            class MinimalBioOrchestrator:
                def __init__(self):
                    self.config = {}

                def get_health(self):
                    return 0.98

            self.bioorchestrator = MinimalBioOrchestrator()
        self.register_service("bioorchestrator", self.bioorchestrator)
        self.lukhosidmanager = LukhosIDManager()
        self.register_service("lukhosidmanager", self.lukhosidmanager)
        self.shardmanager = ShardManager()
        self.register_service("shardmanager", self.shardmanager)
        self.enhancedswarm = EnhancedSwarmHub()
        self.register_service("enhancedswarm", self.enhancedswarm)
        self.lukhas = LukhasCore()
        self.register_service("lukhas", self.lukhas)
        self.biosymbolicswarm = BioSymbolicSwarmHub()
        self.register_service("biosymbolicswarm", self.biosymbolicswarm)

        self.consciousness_bridge = CoreConsciousnessBridge()
        self.register_service("consciousness_bridge", self.consciousness_bridge)
        self.safety_bridge = CoreSafetyBridge()
        self.register_service("safety_bridge", self.safety_bridge)

        # Agent 1 Task 2: Initialize event replay and snapshot services
        self.event_store = EventStore()
        self.register_service("event_store", self.event_store)
        self.snapshot_store = SnapshotStore()
        self.register_service("snapshot_store", self.snapshot_store)

        # Agent 1 Task 5: Initialize resource efficiency analyzer
        try:
            self.resource_analyzer = ResourceEfficiencyAnalyzer(
                sample_interval=1.0,
                history_size=3600,
                enable_memory_profiling=True,
            )
            self.register_service("resource_analyzer", self.resource_analyzer)
            logger.info("Resource efficiency analyzer initialized")
        except Exception as e:
            logger.warning(f"Resource analyzer init failed: {e}")

        logger.info(f"CoreHub initialized with {len(self.services)} services")

    async def initialize(self) -> None:
        """Initialize all core services"""
        if self.is_initialized:
            return

        # Initialize all registered services
        for name, service in self.services.items():
            if hasattr(service, "initialize"):
                try:
                    if asyncio.iscoroutinefunction(service.initialize):
                        await service.initialize()
                    else:
                        service.initialize()
                    logger.debug(f"Initialized {name} service")
                except Exception as e:
                    logger.error(f"Failed to initialize {name}: {e}")

        # Integration & Communication
        self._register_integration_services()

        # Event & State Management
        self._register_event_services()

        # Fault Tolerance & Monitoring
        self._register_monitoring_services()

        # Register services globally for cross-hub access
        self._register_with_service_discovery()

        # Task 3A: Initialize connectivity to other systems
        await self.initialize_connectivity()

        # Mark as initialized
        self.is_initialized = True
        logger.info(f"Core hub initialized with {len(self.services)} services")

    def _register_infrastructure_services(self):
        """Register core infrastructure services"""
        infrastructure_services = [
            ("actor_system", "ActorSystem"),
            ("actor_model", "Actor"),
            ("minimal_actor", "MinimalActor"),
            ("supervision", "SupervisionStrategy"),
            ("cluster_sharding", "ShardManager"),
        ]

        for service_name, class_name in infrastructure_services:
            try:
                module = __import__(f"core.{service_name}", fromlist=[class_name])
                cls = getattr(module, class_name)
                instance = cls()
                self.register_service(service_name, instance)
                logger.debug(f"Registered {class_name} as {service_name}")
            except (ImportError, AttributeError, TypeError) as e:
                logger.warning(f"Could not register {class_name}: {e}")

        # Register additional core system components
        additional_services = [
            ("swarm_coordinator", "SwarmCoordinator", "core.swarm"),
            ("task_manager", "TaskManager", "core.task_manager"),
            (
                "resource_scheduler",
                "ResourceScheduler",
                "core.resource_scheduler",
            ),
            (
                "symbolic_bridge",
                "SymbolicBridge",
                "core.bridges.symbolic_bridge",
            ),
            (
                "bio_symbolic_swarm_hub",
                "BioSymbolicSwarmHub",
                "core.bio_symbolic_swarm_hub",
            ),
            (
                "enhanced_swarm_hub",
                "EnhancedSwarmHub",
                "core.enhanced_swarm_hub",
            ),
        ]

        for service_name, class_name, module_path in additional_services:
            try:
                module = __import__(module_path, fromlist=[class_name])
                cls = getattr(module, class_name)
                instance = cls()
                self.register_service(service_name, instance)
                logger.debug(f"Registered {class_name} as {service_name}")
            except (ImportError, AttributeError, TypeError) as e:
                logger.warning(f"Could not register {class_name}: {e}")

    def _register_integration_services(self):
        """Register integration and coordination services"""
        integration_services = [
            ("ai_interface", "AIInterface"),
            ("integration_hub", "IntegrationHub"),
            ("integrator", "SystemIntegrator"),
            ("coordination", "CoordinationManager"),
            ("collaboration", "CollaborationManager"),
        ]

        for service_name, class_name in integration_services:
            try:
                if service_name == "ai_interface":
                    module = __import__("core.ai_interface", fromlist=[class_name])
                elif service_name == "integration_hub":
                    module = __import__("core.integration_hub", fromlist=[class_name])
                else:
                    module = __import__(f"core.{service_name}", fromlist=[class_name])

                cls = getattr(module, class_name)
                instance = cls()
                self.register_service(service_name, instance)
                logger.debug(f"Registered {class_name} as {service_name}")
            except (ImportError, AttributeError, TypeError) as e:
                logger.warning(f"Could not register {class_name}: {e}")

    def _register_event_services(self):
        """Register event and communication services"""
        event_services = [
            ("event_bus", "EventBus"),
            ("event_sourcing", "EventStore"),
            ("p2p_communication", "P2PManager"),
            ("state_management", "StateManager"),
            ("tiered_state_management", "TieredStateManager"),
        ]

        for service_name, class_name in event_services:
            try:
                module = __import__(f"core.{service_name}", fromlist=[class_name])
                cls = getattr(module, class_name)
                instance = cls()
                self.register_service(service_name, instance)
                logger.debug(f"Registered {class_name} as {service_name}")
            except (ImportError, AttributeError, TypeError) as e:
                logger.warning(f"Could not register {class_name}: {e}")

    def _register_monitoring_services(self):
        """Register monitoring and fault tolerance services"""
        monitoring_services = [
            ("fault_tolerance", "FaultToleranceManager"),
            ("circuit_breaker", "CircuitBreaker"),
            ("distributed_tracing", "TracingManager"),
            ("config_manager", "ConfigurationManager"),
            ("validation", "ValidationManager"),
        ]

        for service_name, class_name in monitoring_services:
            try:
                module = __import__(f"core.{service_name}", fromlist=[class_name])
                cls = getattr(module, class_name)
                instance = cls()
                self.register_service(service_name, instance)
                logger.debug(f"Registered {class_name} as {service_name}")
            except (ImportError, AttributeError, TypeError) as e:
                logger.warning(f"Could not register {class_name}: {e}")

    def _register_with_service_discovery(self):
        """Register services with global service discovery"""
        try:
            from candidate.core.integration.service_discovery import (
                get_service_discovery,
            )

            discovery = get_service_discovery()

            # Register key services globally for cross-hub access
            key_services = [
                "ai_interface",
                "event_bus",
                "integration_hub",
                "swarm_coordinator",
                "task_manager",
                "state_management",
                "circuit_breaker",
                "fault_tolerance",
                "resource_scheduler",
                "distributed_tracing",
                "symbolic_bridge",
            ]

            for service_name in key_services:
                if service_name in self.services:
                    discovery.register_service_globally(
                        service_name, self.services[service_name], "core"
                    )

            logger.debug(
                f"Registered {len(key_services)} core services with global discovery"
            )
        except Exception as e:
            logger.warning(f"Could not register with service discovery: {e}")

    def register_service(self, name: str, service: Any) -> None:
        """Register a service with the hub"""
        self.services[name] = service
        logger.debug(f"Registered {name} service in coreHub")

    def get_service(self, name: str) -> Optional[Any]:
        """Get a registered service by name"""
        return self.services.get(name)

    def list_services(self) -> list[str]:
        """List all registered service names"""
        return list(self.services.keys())

    async def process_event(
        self, event_type: str, event_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Process events from other systems"""
        handlers = self.event_handlers.get(event_type, [])
        results = []

        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    result = await handler(event_data)
                else:
                    result = handler(event_data)
                results.append(result)
            except Exception as e:
                logger.error(f"Event handler error in core: {e}")

        return {"results": results, "handled": len(handlers) > 0}

    def register_event_handler(self, event_type: str, handler) -> None:
        """Register an event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)

    async def initialize_connectivity(self) -> None:
        """Initialize connections to TrioOrchestrator, IntegrationBridge,
        and EthicsService"""
        logger.info("Initializing core module connectivity...")

        # Connect to TrioOrchestrator
        if TrioOrchestrator is not None:
            try:
                self.trio_orchestrator = TrioOrchestrator()
                await self.trio_orchestrator.register_hub("core", self)
                self.register_service("trio_orchestrator", self.trio_orchestrator)
                logger.info("Successfully connected to TrioOrchestrator")
            except Exception as e:
                logger.error(f"Failed to connect to TrioOrchestrator: {e}")
        else:
            logger.warning("TrioOrchestrator not available - skipping connection")

        # Connect to Integration Bridge
        if IntegrationBridge is not None:
            try:
                self.integration_bridge = IntegrationBridge()
                await self.integration_bridge.register_module(
                    "core",
                    {
                        "capabilities": [
                            "coordination",
                            "supervision",
                            "fault_tolerance",
                            "service_discovery",
                        ],
                        "endpoints": self.get_endpoints(),
                    },
                )
                self.register_service("integration_bridge", self.integration_bridge)
                logger.info("Successfully connected to IntegrationBridge")
            except Exception as e:
                logger.error(f"Failed to connect to IntegrationBridge: {e}")
        else:
            logger.warning("IntegrationBridge not available - skipping connection")

        # Connect to Ethics Service
        if EthicsService is not None:
            try:
                self.ethics_service = EthicsService()
                await self.ethics_service.register_observer(
                    "core", self.handle_ethics_event
                )
                self.register_service("ethics_service", self.ethics_service)
                logger.info("Successfully connected to EthicsService")
            except Exception as e:
                logger.error(f"Failed to connect to EthicsService: {e}")
        else:
            logger.warning("EthicsService not available - skipping connection")

        logger.info("Core module connectivity initialization complete")

    def get_endpoints(self) -> dict[str, str]:
        """Get available service endpoints for the core module"""
        endpoints = {
            "event_processing": "/core/events",
            "service_discovery": "/core/services",
            "task_management": "/core/tasks",
            "system_status": "/core/status",
            "coordination": "/core/coordinate",
            "supervision": "/core/supervise",
        }

        # Add endpoints for registered services
        for service_name in self.services:
            endpoints[f"service_{service_name}"] = f"/core/services/{service_name}"

        return endpoints

    async def handle_ethics_event(
        self, event_type: str, event_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle ethics-related events from the EthicsService"""
        logger.info(f"Received ethics event: {event_type}")

        if event_type == "ethics_violation":
            # Handle ethics violation - potentially halt operations
            logger.warning(f"Ethics violation detected: {event_data}")
            # Notify relevant services
            await self.process_event("ethics_violation", event_data)
            return {"action": "handled", "response": "violation_acknowledged"}

        elif event_type == "ethics_review_required":
            # Queue for ethics review
            logger.info(f"Ethics review required: {event_data}")
            await self.process_event("ethics_review", event_data)
            return {"action": "queued", "response": "review_scheduled"}

        else:
            # General ethics event
            await self.process_event(f"ethics_{event_type}", event_data)
            return {"action": "processed", "response": "event_handled"}

    def broadcast_to_all_hubs(self, message: dict[str, Any]) -> dict[str, list[Any]]:
        responses = {}
        for hub_info in self.connected_hubs:
            hub_name = hub_info["name"]
            hub = hub_info["instance"]
            try:
                if hasattr(hub, "receive_message"):
                    response = hub.receive_message(message)
                    responses[hub_name] = response
            except Exception as e:
                logger.error(f"Failed to broadcast to {hub_name}: {e}")
                responses[hub_name] = {"error": str(e)}
        return responses

    def receive_message(self, message: dict[str, Any]) -> dict[str, Any]:
        return {
            "hub": self.name,
            "received": True,
            "timestamp": datetime.now().isoformat(),
            "message_id": message.get("id", "unknown"),
        }

    # Agent 1 Task 2: Add event replay and snapshot functionality to CoreHub
    async def record_event(
        self,
        event_type: str,
        actor_id: str,
        data: dict[str, Any],
        correlation_id: Optional[str] = None,
        causation_id: Optional[str] = None,
    ) -> str:
        """Record an event in the event store"""
        if "event_store" not in self.services:
            logger.warning("Event store not available for recording")
            return ""

        import time
        import uuid

        from candidate.core.event_replay_snapshot import Event, EventType

        # Convert string event_type to EventType enum if needed
        if isinstance(event_type, str):
            try:
                event_type_enum = EventType(event_type)
            except ValueError:
                # If not a standard event type, use a default
                event_type_enum = EventType.STATE_CHANGED
        else:
            event_type_enum = event_type

        event = Event(
            event_id=str(uuid.uuid4()),
            event_type=event_type_enum,
            actor_id=actor_id,
            timestamp=time.time(),
            data=data,
            correlation_id=correlation_id,
            causation_id=causation_id,
        )

        await self.services["event_store"].append_event(event)
        return event.event_id

    async def replay_events_for_actor(
        self,
        actor_id: str,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        speed: float = 1.0,
    ) -> int:
        """Replay events for a specific actor"""
        if "event_store" not in self.services:
            logger.error("Event store not available for replay")
            return 0

        events = await self.services["event_store"].get_events_for_actor(
            actor_id, start_time, end_time
        )

        return await self.services["event_store"].replay_events(events, speed)

    async def take_actor_snapshot(self, actor, event_id: str) -> bool:
        """Take a snapshot of an actor's state"""
        if "snapshot_store" not in self.services:
            logger.warning("Snapshot store not available")
            return False

        from candidate.core.event_replay_snapshot import ActorStateSnapshot

        try:
            snapshot = ActorStateSnapshot.create_from_actor(actor, event_id)
            await self.services["snapshot_store"].save_snapshot(snapshot)
            logger.info(f"Snapshot saved for actor {actor.actor_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to take snapshot for {actor.actor_id}: {e}")
            return False

    async def restore_actor_from_snapshot(self, actor, timestamp: float) -> bool:
        """Restore an actor from the most recent snapshot before timestamp"""
        if "snapshot_store" not in self.services:
            logger.warning("Snapshot store not available")
            return False

        try:
            snapshot = await self.services["snapshot_store"].get_latest_snapshot(
                actor.actor_id, timestamp
            )
            if snapshot:
                snapshot.restore_to_actor(actor)
                logger.info(f"Restored actor {actor.actor_id} from snapshot")
                return True
            else:
                logger.warning(f"No snapshot found for {actor.actor_id}")
                return False
        except Exception as e:
            logger.error(f"Failed to restore {actor.actor_id}: {e}")
            return False

    # Agent 1 Task 5: Add resource efficiency methods to CoreHub
    async def start_resource_monitoring(self) -> bool:
        """Start resource monitoring"""
        if "resource_analyzer" not in self.services:
            logger.warning("Resource analyzer not available")
            return False

        try:
            self.services["resource_analyzer"].start_monitoring()
            logger.info("Resource monitoring started")
            return True
        except Exception as e:
            logger.error(f"Failed to start resource monitoring: {e}")
            return False

    async def get_resource_efficiency_report(
        self, duration_hours: float = 1.0
    ) -> dict[str, Any]:
        """Get resource efficiency report"""
        if "resource_analyzer" not in self.services:
            return {
                "status": "unavailable",
                "error": "Resource analyzer not initialized",
            }

        try:
            report = self.services["resource_analyzer"].analyze_efficiency(
                duration_hours
            )
            return {
                "status": "success",
                "efficiency_score": report.efficiency_score,
                "resource_utilization": report.resource_utilization,
                "bottlenecks": report.bottlenecks,
                "recommendations": report.recommendations,
                "timestamp": report.timestamp,
            }
        except Exception as e:
            logger.error(f"Failed to generate efficiency report: {e}")
            return {"status": "error", "error": str(e)}

    async def get_current_resource_snapshot(self) -> dict[str, Any]:
        """Get current resource usage snapshot"""
        if "resource_analyzer" not in self.services:
            return {"status": "unavailable"}

        try:
            stats = self.services["resource_analyzer"].get_quick_stats()
            return {"status": "success", "snapshot": stats}
        except Exception as e:
            logger.error(f"Failed to get resource snapshot: {e}")
            return {"status": "error", "error": str(e)}

    async def shutdown(self) -> None:
        """Gracefully shutdown all services"""
        # Agent 1 Task 2: Shutdown event store and snapshot store
        if "event_store" in self.services:
            try:
                await self.services["event_store"].stop()
            except Exception as e:
                logger.error(f"Error shutting down event store: {e}")

        for name, service in self.services.items():
            if hasattr(service, "shutdown"):
                try:
                    if asyncio.iscoroutinefunction(service.shutdown):
                        await service.shutdown()
                    else:
                        service.shutdown()
                except Exception as e:
                    logger.error(f"Error shutting down {name}: {e}")

        logger.info("CoreHub shutdown complete")


# Singleton instance
_core_hub_instance = None


def get_core_hub() -> CoreHub:
    """Get or create the core hub singleton instance"""
    global _core_hub_instance
    if _core_hub_instance is None:
        _core_hub_instance = CoreHub()
    return _core_hub_instance


async def initialize_core_system() -> CoreHub:
    """Initialize the complete core system"""
    hub = get_core_hub()
    await hub.initialize()
    return hub


# Export main components
__all__ = ["CoreHub", "get_core_hub", "initialize_core_system"]
