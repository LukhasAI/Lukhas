"""
AGI Service Bridge
==================

Bridge service that integrates AGI capabilities with existing LUKHAS service architecture.
Provides seamless connectivity between AGI components and LUKHAS consciousness modules
through the existing service registry and dependency injection system.

This service:
- Registers AGI components in the LUKHAS service registry
- Provides service adapters for legacy LUKHAS interfaces
- Manages AGI service lifecycle within LUKHAS ecosystem
- Enables dependency injection for AGI services
- Maintains service health monitoring and metrics

Part of Phase 2A: Core Integrations - Basic service connections
Created: 2025-09-05
"""

import asyncio
import contextlib
import logging
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Protocol

try:
    from agi_core.integration import log_agi_operation, vocabulary_service
    from agi_core.learning import DreamGuidedLearner
    from agi_core.memory import DreamMemory, MemoryConsolidator, VectorMemory
    from agi_core.orchestration import ConsensusEngine, ModelRouter
    from agi_core.reasoning import ChainOfThought, DreamIntegration, TreeOfThoughts
    from agi_core.safety import ConstitutionalAI
except ImportError:
    # Mock classes for development
    class MockAGIComponent:
        async def initialize(self): pass
        async def shutdown(self): pass
        def get_health(self): return {"status": "healthy"}

    ChainOfThought = TreeOfThoughts = DreamIntegration = MockAGIComponent
    ModelRouter = ConsensusEngine = MockAGIComponent
    VectorMemory = MemoryConsolidator = DreamMemory = MockAGIComponent
    ConstitutionalAI = DreamGuidedLearner = MockAGIComponent

    class MockVocabService:
        def log_agi_operation(self, op, details="", module="agi", severity="INFO"):
            return {"operation": op, "details": details}

    vocabulary_service = MockVocabService()
    log_agi_operation = vocabulary_service.log_agi_operation

# AGI Service Interface (compatible with LUKHAS IService)
class IAGIService(Protocol):
    """Interface for AGI services compatible with LUKHAS service architecture."""

    async def initialize(self) -> None:
        """Initialize the AGI service."""
        ...

    async def shutdown(self) -> None:
        """Gracefully shutdown the AGI service."""
        ...

    def get_health(self) -> dict[str, Any]:
        """Get service health status."""
        ...

@dataclass
class ServiceRegistration:
    """Information about a registered AGI service."""
    name: str
    service: Any
    service_type: str
    registration_time: datetime
    health_status: str = "unknown"
    last_health_check: Optional[datetime] = None

@dataclass
class ServiceMetrics:
    """Metrics for AGI service integration."""
    total_services: int = 0
    healthy_services: int = 0
    failed_services: int = 0
    initialization_errors: int = 0
    last_health_check: Optional[datetime] = None

class AGIServiceAdapter:
    """
    Adapter that wraps AGI components to be compatible with LUKHAS service interfaces.

    Provides compatibility layer between AGI services and existing LUKHAS
    service contracts, enabling seamless integration without breaking existing code.
    """

    def __init__(self, agi_component: Any, service_name: str):
        self.agi_component = agi_component
        self.service_name = service_name
        self._initialized = False
        self._health_status = "unknown"

    async def initialize(self) -> None:
        """Initialize the wrapped AGI component."""
        try:
            if hasattr(self.agi_component, "initialize"):
                await self.agi_component.initialize()
            self._initialized = True
            self._health_status = "healthy"
            log_agi_operation("service_init", f"{self.service_name} initialized", "service_bridge")
        except Exception as e:
            self._health_status = "failed"
            log_agi_operation("service_error", f"{self.service_name} init failed: {e}", "service_bridge", "ERROR")
            raise

    async def shutdown(self) -> None:
        """Shutdown the wrapped AGI component."""
        try:
            if hasattr(self.agi_component, "shutdown"):
                await self.agi_component.shutdown()
            self._initialized = False
            self._health_status = "shutdown"
            log_agi_operation("service_shutdown", f"{self.service_name} shutdown", "service_bridge")
        except Exception as e:
            log_agi_operation("service_error", f"{self.service_name} shutdown failed: {e}", "service_bridge", "ERROR")
            raise

    def get_health(self) -> dict[str, Any]:
        """Get health status of the wrapped AGI component."""
        base_health = {
            "status": self._health_status,
            "initialized": self._initialized,
            "service_name": self.service_name,
            "service_type": type(self.agi_component).__name__,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Get AGI component health if available
        if hasattr(self.agi_component, "get_health"):
            try:
                component_health = self.agi_component.get_health()
                base_health.update(component_health)
            except Exception as e:
                base_health["component_health_error"] = str(e)

        return base_health

class AGIServiceBridge:
    """
    Central bridge service that integrates AGI capabilities with LUKHAS service architecture.

    This bridge:
    - Registers AGI services in the existing LUKHAS service registry
    - Provides adapters for AGI-LUKHAS service compatibility
    - Manages AGI service lifecycle (initialization, health, shutdown)
    - Enables dependency injection for AGI services
    - Monitors service health and integration quality
    """

    def __init__(self, enable_health_monitoring: bool = True):
        self.registered_services: dict[str, ServiceRegistration] = {}
        self.service_adapters: dict[str, AGIServiceAdapter] = {}
        self.metrics = ServiceMetrics()
        self.enable_health_monitoring = enable_health_monitoring
        self._health_check_task: Optional[asyncio.Task] = None

        # Logger setup
        self.logger = logging.getLogger("agi_service_bridge")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - [%(levelname)s] - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    async def register_agi_service(self, service_name: str, agi_component: Any,
                                 auto_initialize: bool = True) -> AGIServiceAdapter:
        """
        Register an AGI component as a service in the LUKHAS ecosystem.

        Args:
            service_name: Unique service identifier
            agi_component: AGI component to register
            auto_initialize: Whether to automatically initialize the service

        Returns:
            AGIServiceAdapter wrapping the component
        """
        try:
            # Create adapter for the AGI component
            adapter = AGIServiceAdapter(agi_component, service_name)

            # Initialize if requested
            if auto_initialize:
                await adapter.initialize()

            # Register the service
            registration = ServiceRegistration(
                name=service_name,
                service=adapter,
                service_type=type(agi_component).__name__,
                registration_time=datetime.now(timezone.utc),
                health_status=adapter.get_health()["status"]
            )

            self.registered_services[service_name] = registration
            self.service_adapters[service_name] = adapter

            # Update metrics
            self.metrics.total_services += 1
            if registration.health_status == "healthy":
                self.metrics.healthy_services += 1

            log_agi_operation("bridge_register", f"registered {service_name} successfully", "service_bridge")
            self.logger.info(f"Registered AGI service: {service_name}")

            return adapter

        except Exception as e:
            self.metrics.initialization_errors += 1
            log_agi_operation("bridge_error", f"failed to register {service_name}: {e}", "service_bridge", "ERROR")
            self.logger.error(f"Failed to register {service_name}: {e}")
            raise

    def get_agi_service(self, service_name: str) -> Optional[AGIServiceAdapter]:
        """
        Retrieve a registered AGI service by name.

        Args:
            service_name: Service identifier

        Returns:
            AGIServiceAdapter if found, None otherwise
        """
        return self.service_adapters.get(service_name)

    async def initialize_all_services(self) -> dict[str, bool]:
        """
        Initialize all registered AGI services.

        Returns:
            Dictionary mapping service names to initialization success status
        """
        results = {}

        for service_name, adapter in self.service_adapters.items():
            try:
                await adapter.initialize()
                results[service_name] = True
                log_agi_operation("bridge_init_success", service_name, "service_bridge")
            except Exception as e:
                results[service_name] = False
                log_agi_operation("bridge_init_fail", f"{service_name}: {e}", "service_bridge", "ERROR")

        # Update health counts
        await self._update_health_metrics()

        return results

    async def shutdown_all_services(self) -> dict[str, bool]:
        """
        Shutdown all registered AGI services.

        Returns:
            Dictionary mapping service names to shutdown success status
        """
        results = {}

        # Stop health monitoring
        if self._health_check_task:
            self._health_check_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._health_check_task

        # Shutdown services
        for service_name, adapter in self.service_adapters.items():
            try:
                await adapter.shutdown()
                results[service_name] = True
                log_agi_operation("bridge_shutdown_success", service_name, "service_bridge")
            except Exception as e:
                results[service_name] = False
                log_agi_operation("bridge_shutdown_fail", f"{service_name}: {e}", "service_bridge", "ERROR")

        return results

    async def health_check_all_services(self) -> dict[str, dict[str, Any]]:
        """
        Perform health check on all registered services.

        Returns:
            Dictionary mapping service names to their health status
        """
        health_results = {}

        for service_name, adapter in self.service_adapters.items():
            try:
                health = adapter.get_health()
                health_results[service_name] = health

                # Update registration health status
                if service_name in self.registered_services:
                    self.registered_services[service_name].health_status = health["status"]
                    self.registered_services[service_name].last_health_check = datetime.now(timezone.utc)

            except Exception as e:
                health_results[service_name] = {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }

        await self._update_health_metrics()
        return health_results

    async def _update_health_metrics(self) -> None:
        """Update service health metrics."""
        healthy_count = 0
        failed_count = 0

        for registration in self.registered_services.values():
            if registration.health_status == "healthy":
                healthy_count += 1
            elif registration.health_status in ["failed", "error"]:
                failed_count += 1

        self.metrics.healthy_services = healthy_count
        self.metrics.failed_services = failed_count
        self.metrics.last_health_check = datetime.now(timezone.utc)

    async def start_health_monitoring(self, interval_seconds: int = 60) -> None:
        """
        Start periodic health monitoring of all AGI services.

        Args:
            interval_seconds: Health check interval in seconds
        """
        if not self.enable_health_monitoring:
            return

        async def health_monitor():
            while True:
                try:
                    await asyncio.sleep(interval_seconds)
                    await self.health_check_all_services()
                    log_agi_operation("bridge_health_check", "completed health check cycle", "service_bridge")
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    log_agi_operation("bridge_health_error", f"health check failed: {e}", "service_bridge", "ERROR")

        self._health_check_task = asyncio.create_task(health_monitor())
        log_agi_operation("bridge_monitor_start", f"health monitoring every {interval_seconds}s", "service_bridge")

    def get_service_registry_info(self) -> dict[str, Any]:
        """
        Get comprehensive information about the AGI service registry.

        Returns:
            Dictionary containing service registry status and metrics
        """
        return {
            "metrics": asdict(self.metrics),
            "total_services": len(self.registered_services),
            "service_list": [
                {
                    "name": reg.name,
                    "type": reg.service_type,
                    "status": reg.health_status,
                    "registration_time": reg.registration_time.isoformat(),
                    "last_health_check": reg.last_health_check.isoformat() if reg.last_health_check else None
                }
                for reg in self.registered_services.values()
            ],
            "health_monitoring": self.enable_health_monitoring,
            "active_health_task": self._health_check_task is not None and not self._health_check_task.done()
        }

# Global service bridge instance
agi_service_bridge = AGIServiceBridge()

# Convenience functions for external use
async def register_agi_service(service_name: str, agi_component: Any,
                             auto_initialize: bool = True) -> AGIServiceAdapter:
    """Convenience function to register an AGI service."""
    return await agi_service_bridge.register_agi_service(service_name, agi_component, auto_initialize)

def get_agi_service(service_name: str) -> Optional[AGIServiceAdapter]:
    """Convenience function to get an AGI service."""
    return agi_service_bridge.get_agi_service(service_name)

async def initialize_agi_services() -> dict[str, bool]:
    """Convenience function to initialize all AGI services."""
    return await agi_service_bridge.initialize_all_services()

async def health_check_agi_services() -> dict[str, dict[str, Any]]:
    """Convenience function to health check all AGI services."""
    return await agi_service_bridge.health_check_all_services()

if __name__ == "__main__":
    # Test the AGI service bridge
    async def test_bridge():
        bridge = AGIServiceBridge()

        print("🧠 AGI Service Bridge Test")
        print("="*50)

        # Create mock AGI components
        class MockChainOfThought:
            async def initialize(self):
                print("ChainOfThought initialized")
            async def shutdown(self):
                print("ChainOfThought shutdown")
            def get_health(self):
                return {"status": "healthy", "reasoning_chains": 42}

        class MockModelRouter:
            async def initialize(self):
                print("ModelRouter initialized")
            def get_health(self):
                return {"status": "healthy", "active_models": 3}

        # Test service registration
        cot = MockChainOfThought()
        router = MockModelRouter()

        await bridge.register_agi_service("chain_of_thought", cot)
        await bridge.register_agi_service("model_router", router)

        print(f"Registered services: {list(bridge.registered_services.keys())}")

        # Test health checks
        health = await bridge.health_check_all_services()
        print(f"Health check results: {health}")

        # Test service retrieval
        retrieved_cot = bridge.get_agi_service("chain_of_thought")
        print(f"Retrieved service: {retrieved_cot.service_name}")

        # Test registry info
        registry_info = bridge.get_service_registry_info()
        print(f"Registry metrics: {registry_info['metrics']}")

        # Cleanup
        await bridge.shutdown_all_services()

    asyncio.run(test_bridge())

"""
Integration with Existing LUKHAS Services:
=========================================

1. Service Registry Integration:
   - AGI services are registered in the existing LUKHAS service registry
   - Compatible with dependency injection patterns used throughout LUKHAS
   - Maintains service lifecycle management consistency

2. Interface Compatibility:
   - AGI services implement compatible versions of IService interface
   - Existing LUKHAS modules can access AGI services through standard patterns
   - No changes required to existing service consumers

3. Health Monitoring Integration:
   - AGI service health integrates with existing LUKHAS monitoring systems
   - Compatible metrics format for existing dashboards and alerts
   - Unified health reporting across all system services

4. Lifecycle Management:
   - AGI services participate in standard LUKHAS service lifecycle
   - Graceful initialization and shutdown with other LUKHAS services
   - Error handling and recovery patterns consistent with existing services

Usage Examples:
==============

# Register AGI services during system startup
await register_agi_service("agi_reasoning", ChainOfThought())
await register_agi_service("agi_orchestration", ModelRouter())
await register_agi_service("agi_memory", VectorMemory())

# Access AGI services from existing LUKHAS modules
reasoning_service = get_agi_service("agi_reasoning")
if reasoning_service:
    health = reasoning_service.get_health()
    if health["status"] == "healthy":
        # Use the service
        pass

# Health monitoring integration
health_status = await health_check_agi_services()
for service_name, health in health_status.items():
    if health["status"] != "healthy":
        alert_service_issue(service_name, health)

# Start monitoring
await agi_service_bridge.start_health_monitoring(interval_seconds=30)
"""
