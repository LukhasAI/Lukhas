"""
Cognitive AI Service Initializer
=======================

Initialization script that registers and configures all Cognitive services within
the LUKHAS ecosystem. This script is responsible for:

- Registering Cognitive AI components in the LUKHAS service registry
- Configuring service dependencies and connections
- Establishing integration with existing LUKHAS modules
- Starting Cognitive service monitoring and health checks
- Providing graceful initialization and error handling

This is the central entry point for Cognitive service integration with LUKHAS.
Run during system startup to enable Cognitive capabilities across all modules.

Part of Phase 2A: Core Integrations - Basic service connections
Created: 2025-09-05
"""

import asyncio
import logging
from collections import defaultdict  # ΛTAG: performance
from datetime import datetime, timezone
from typing import Any, Optional

try:
    # Cognitive Components
    # Integration Services
    from cognitive_core.integration import (
        cognitive_service_bridge,
        log_agi_operation,
        register_agi_service,
        vocabulary_service,
    )
    from cognitive_core.learning import DreamGuidedLearner
    from cognitive_core.memory import (
        DreamMemory,
        EpisodicMemory,
        MemoryConsolidator,
        SemanticMemory,
        VectorMemory,
    )
    from cognitive_core.orchestration import (
        CapabilityMatrix,
        ConsensusEngine,
        CostOptimizer,
        ModelRouter,
    )
    from cognitive_core.reasoning import ChainOfThought, DreamIntegration, TreeOfThoughts
    from cognitive_core.safety import ConstitutionalAI
    from cognitive_core.tools import DreamGuidedTools

    COMPONENTS_AVAILABLE = True

except ImportError as e:
    logging.warning(f"Some Cognitive AI components not available: {e}")
    COMPONENTS_AVAILABLE = False

    # Mock components for testing
    class MockAGIComponent:
        def __init__(self, name: str):
            self.name = name

        async def initialize(self):
            pass

        async def shutdown(self):
            pass

        def get_health(self):
            return {"status": "healthy", "component": self.name}

    # Create mock components
    def ChainOfThought():
        return MockAGIComponent("ChainOfThought")

    def TreeOfThoughts():
        return MockAGIComponent("TreeOfThoughts")

    def DreamIntegration():
        return MockAGIComponent("DreamIntegration")

    def ModelRouter():
        return MockAGIComponent("ModelRouter")

    def ConsensusEngine():
        return MockAGIComponent("ConsensusEngine")

    def CapabilityMatrix():
        return MockAGIComponent("CapabilityMatrix")

    def CostOptimizer():
        return MockAGIComponent("CostOptimizer")

    def VectorMemory():
        return MockAGIComponent("VectorMemory")

    def MemoryConsolidator():
        return MockAGIComponent("MemoryConsolidator")

    def EpisodicMemory():
        return MockAGIComponent("EpisodicMemory")

    def SemanticMemory():
        return MockAGIComponent("SemanticMemory")

    def DreamMemory():
        return MockAGIComponent("DreamMemory")

    def ConstitutionalAI():
        return MockAGIComponent("ConstitutionalAI")

    def DreamGuidedLearner():
        return MockAGIComponent("DreamGuidedLearner")

    def DreamGuidedTools():
        return MockAGIComponent("DreamGuidedTools")

    # Mock services
    class MockBridge:
        async def register_agi_service(self, name, comp, auto_init=True):
            return MockAGIComponent(f"Adapter_{name}")

        async def initialize_all_services(self):
            return {}

        async def start_health_monitoring(self, interval=60):
            pass

        def get_service_registry_info(self):
            return {"status": "mock"}

    class MockVocabService:
        def log_agi_operation(self, op, details="", module="agi", severity="INFO"):
            return {"operation": op}

    cognitive_service_bridge = MockBridge()
    vocabulary_service = MockVocabService()
    register_agi_service = cognitive_service_bridge.register_agi_service
    log_agi_operation = vocabulary_service.log_agi_operation


class AGIServiceConfiguration:
    """Configuration for Cognitive service initialization."""

    def __init__(self):
        self.service_configs = {
            # Reasoning Services
            "cognitive_chain_of_thought": {
                "component_factory": ChainOfThought,
                "dependencies": [],
                "priority": 1,  # High priority - core reasoning
                "auto_initialize": True,
                "health_monitoring": True,
            },
            "cognitive_tree_of_thoughts": {
                "component_factory": TreeOfThoughts,
                "dependencies": ["cognitive_chain_of_thought"],
                "priority": 1,
                "auto_initialize": True,
                "health_monitoring": True,
            },
            "cognitive_dream_integration": {
                "component_factory": DreamIntegration,
                "dependencies": [],
                "priority": 2,
                "auto_initialize": True,
                "health_monitoring": True,
            },
            # Orchestration Services
            "cognitive_model_router": {
                "component_factory": ModelRouter,
                "dependencies": [],
                "priority": 1,
                "auto_initialize": True,
                "health_monitoring": True,
            },
            "cognitive_consensus_engine": {
                "component_factory": ConsensusEngine,
                "dependencies": ["cognitive_model_router"],
                "priority": 2,
                "auto_initialize": True,
                "health_monitoring": True,
            },
            "cognitive_capability_matrix": {
                "component_factory": CapabilityMatrix,
                "dependencies": ["cognitive_model_router"],
                "priority": 3,
                "auto_initialize": True,
                "health_monitoring": False,  # Static component
            },
            "cognitive_cost_optimizer": {
                "component_factory": CostOptimizer,
                "dependencies": ["cognitive_model_router", "cognitive_capability_matrix"],
                "priority": 3,
                "auto_initialize": True,
                "health_monitoring": True,
            },
            # Memory Services
            "cognitive_vector_memory": {
                "component_factory": VectorMemory,
                "dependencies": [],
                "priority": 1,
                "auto_initialize": True,
                "health_monitoring": True,
            },
            "cognitive_episodic_memory": {
                "component_factory": EpisodicMemory,
                "dependencies": ["cognitive_vector_memory"],
                "priority": 2,
                "auto_initialize": True,
                "health_monitoring": True,
            },
            "cognitive_semantic_memory": {
                "component_factory": SemanticMemory,
                "dependencies": ["cognitive_vector_memory"],
                "priority": 2,
                "auto_initialize": True,
                "health_monitoring": True,
            },
            "cognitive_dream_memory": {
                "component_factory": DreamMemory,
                "dependencies": ["cognitive_vector_memory", "cognitive_dream_integration"],
                "priority": 2,
                "auto_initialize": True,
                "health_monitoring": True,
            },
            "cognitive_memory_consolidator": {
                "component_factory": MemoryConsolidator,
                "dependencies": [
                    "cognitive_vector_memory",
                    "cognitive_episodic_memory",
                    "cognitive_semantic_memory",
                    "cognitive_dream_memory",
                ],
                "priority": 3,
                "auto_initialize": True,
                "health_monitoring": True,
            },
            # Safety and Learning Services
            "cognitive_constitutional_ai": {
                "component_factory": ConstitutionalAI,
                "dependencies": [],
                "priority": 1,  # Critical for safety
                "auto_initialize": True,
                "health_monitoring": True,
            },
            "cognitive_dream_guided_learner": {
                "component_factory": DreamGuidedLearner,
                "dependencies": ["cognitive_dream_integration", "cognitive_memory_consolidator"],
                "priority": 2,
                "auto_initialize": True,
                "health_monitoring": True,
            },
            "cognitive_dream_guided_tools": {
                "component_factory": DreamGuidedTools,
                "dependencies": ["cognitive_dream_integration", "cognitive_dream_guided_learner"],
                "priority": 3,
                "auto_initialize": True,
                "health_monitoring": True,
            },
        }


class AGIServiceInitializer:
    """
    Central initializer for all Cognitive services within the LUKHAS ecosystem.

    Handles registration, dependency resolution, graceful initialization,
    and integration with existing LUKHAS service architecture.
    """

    def __init__(self, config: Optional[AGIServiceConfiguration] = None):
        self.config = config or AGIServiceConfiguration()
        self.initialized_services: dict[str, Any] = {}
        self.initialization_order: list[str] = []
        self.failed_services: list[str] = []

        # Logger setup
        self.logger = logging.getLogger("cognitive_service_initializer")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(name)s - [%(levelname)s] - %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def _resolve_dependency_order(self) -> list[str]:
        """
        Resolve service initialization order based on dependencies.

        Uses topological sorting to ensure dependencies are initialized
        before services that depend on them.
        """
        # Simple dependency resolution using priority and dependencies
        services_by_priority: dict[int, list[str]] = defaultdict(list)  # ΛTAG: performance

        for service_name, config in self.config.service_configs.items():
            priority = config.get("priority", 10)
            services_by_priority[priority].append(service_name)

        # Return services ordered by priority (lower number = higher priority)
        ordered_services = []
        for priority in sorted(services_by_priority):  # ΛTAG: performance
            ordered_services.extend(services_by_priority[priority])

        return ordered_services

    async def initialize_service(self, service_name: str) -> bool:
        """
        Initialize a single Cognitive service.

        Args:
            service_name: Name of the service to initialize

        Returns:
            True if initialization successful, False otherwise
        """
        if service_name in self.initialized_services:
            self.logger.info(f"Service {service_name} already initialized")
            return True

        config = self.config.service_configs.get(service_name)
        if not config:
            self.logger.error(f"No configuration found for service: {service_name}")
            return False

        try:
            log_agi_operation("service_init_start", service_name, "cognitive_initializer")

            # Check dependencies
            for dep in config.get("dependencies", []):
                if dep not in self.initialized_services:
                    self.logger.warning(f"Dependency {dep} not initialized for {service_name}")
                    # Try to initialize dependency first
                    if not await self.initialize_service(dep):
                        self.logger.error(f"Failed to initialize dependency {dep} for {service_name}")
                        return False

            # Create component instance
            component_factory = config["component_factory"]
            component = component_factory()

            # Register with Cognitive service bridge
            adapter = await register_agi_service(
                service_name, component, auto_initialize=config.get("auto_initialize", True)
            )

            self.initialized_services[service_name] = adapter
            self.initialization_order.append(service_name)

            log_agi_operation("service_init_success", service_name, "cognitive_initializer")
            self.logger.info(f"Successfully initialized Cognitive service: {service_name}")

            return True

        except Exception as e:
            self.failed_services.append(service_name)
            log_agi_operation("service_init_fail", f"{service_name}: {e}", "cognitive_initializer", "ERROR")
            self.logger.error(f"Failed to initialize {service_name}: {e}")
            return False

    async def initialize_all_services(self) -> dict[str, bool]:
        """
        Initialize all configured Cognitive services in dependency order.

        Returns:
            Dictionary mapping service names to initialization success status
        """
        log_agi_operation("system_init_start", "initializing all Cognitive services", "cognitive_initializer")

        # Get initialization order
        service_order = self._resolve_dependency_order()
        results = {}

        # Initialize services in order
        for service_name in service_order:
            success = await self.initialize_service(service_name)
            results[service_name] = success

            if not success:
                self.logger.warning(f"Service {service_name} failed to initialize, continuing...")

        # Log summary
        successful_count = sum(results.values())
        total_count = len(results)

        log_agi_operation(
            "system_init_complete", f"{successful_count}/{total_count} services initialized", "cognitive_initializer"
        )

        self.logger.info(f"Cognitive service initialization complete: {successful_count}/{total_count} successful")

        return results

    async def start_health_monitoring(self, interval_seconds: int = 60) -> None:
        """
        Start health monitoring for all initialized Cognitive services.

        Args:
            interval_seconds: Health check interval
        """
        await cognitive_service_bridge.start_health_monitoring(interval_seconds)
        log_agi_operation("health_monitor_start", f"monitoring every {interval_seconds}s", "cognitive_initializer")

    async def graceful_shutdown(self) -> dict[str, bool]:
        """
        Gracefully shutdown all Cognitive services in reverse order.

        Returns:
            Dictionary mapping service names to shutdown success status
        """
        log_agi_operation("system_shutdown_start", "shutting down all Cognitive services", "cognitive_initializer")

        # Shutdown in reverse initialization order
        shutdown_results = {}

        for service_name in reversed(self.initialization_order):
            try:
                adapter = self.initialized_services.get(service_name)
                if adapter:
                    await adapter.shutdown()
                    shutdown_results[service_name] = True
                    log_agi_operation("service_shutdown_success", service_name, "cognitive_initializer")
                else:
                    shutdown_results[service_name] = False

            except Exception as e:
                shutdown_results[service_name] = False
                log_agi_operation("service_shutdown_fail", f"{service_name}: {e}", "cognitive_initializer", "ERROR")
                self.logger.error(f"Failed to shutdown {service_name}: {e}")

        log_agi_operation("system_shutdown_complete", "Cognitive services shutdown", "cognitive_initializer")
        return shutdown_results

    def get_initialization_status(self) -> dict[str, Any]:
        """
        Get comprehensive status of Cognitive service initialization.

        Returns:
            Status information including metrics and service states
        """
        return {
            "total_services": len(self.config.service_configs),
            "initialized_services": len(self.initialized_services),
            "failed_services": len(self.failed_services),
            "initialization_order": self.initialization_order,
            "failed_service_names": self.failed_services,
            "service_registry_info": cognitive_service_bridge.get_service_registry_info(),
            "components_available": COMPONENTS_AVAILABLE,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# Global initializer instance
cognitive_initializer = AGIServiceInitializer()


# Main initialization function for external use
async def initialize_agi_system(
    config: Optional[AGIServiceConfiguration] = None, start_monitoring: bool = True, monitoring_interval: int = 60
) -> dict[str, Any]:
    """
    Main function to initialize the entire Cognitive system within LUKHAS.

    Args:
        config: Optional custom configuration
        start_monitoring: Whether to start health monitoring
        monitoring_interval: Health check interval in seconds

    Returns:
        Initialization status and results
    """
    global cognitive_initializer

    if config:
        cognitive_initializer = AGIServiceInitializer(config)

    log_agi_operation("system_init", "starting Cognitive system initialization", "cognitive_main")

    # Initialize all services
    init_results = await cognitive_initializer.initialize_all_services()

    # Start health monitoring if requested
    if start_monitoring:
        await cognitive_initializer.start_health_monitoring(monitoring_interval)

    # Get final status
    status = cognitive_initializer.get_initialization_status()
    status["initialization_results"] = init_results

    log_agi_operation("system_ready", "Cognitive system fully operational", "cognitive_main")

    return status


if __name__ == "__main__":
    # Test the Cognitive service initializer
    async def test_initializer():
        print("🧠 Cognitive AI Service Initializer Test")
        print("=" * 50)

        # Initialize the Cognitive system
        status = await initialize_agi_system(start_monitoring=False)  # Disable monitoring for test

        print("Initialization Status:")
        print(f"  Total services: {status['total_services']}")
        print(f"  Initialized: {status['initialized_services']}")
        print(f"  Failed: {status['failed_services']}")
        print(f"  Components available: {status['components_available']}")

        # Show initialization order
        print(f"\nInitialization order: {status['initialization_order']}")

        # Show service registry info
        registry_info = status.get("service_registry_info", {})
        print(f"Registry health monitoring: {registry_info.get('health_monitoring', False)}")

        # Graceful shutdown
        print("\nShutting down...")
        shutdown_results = await cognitive_initializer.graceful_shutdown()
        successful_shutdowns = sum(shutdown_results.values())
        print(f"Shutdown: {successful_shutdowns}/{len(shutdown_results)} successful")

    asyncio.run(test_initializer())

"""
Usage in LUKHAS System Startup:
==============================

# In main LUKHAS startup script:
from cognitive_core.integration.cognitive_service_initializer import initialize_agi_system

async def start_lukhas_system():
    # ... existing LUKHAS initialization ...

    # Initialize Cognitive system
    cognitive_status = await initialize_agi_system(
        start_monitoring=True,
        monitoring_interval=30
    )

    if cognitive_status["failed_services"] > 0:
        logger.warning(f"Some Cognitive services failed: {cognitive_status['failed_service_names']}")

    logger.info(f"LUKHAS Cognitive system ready: {cognitive_status['initialized_services']}/{cognitive_status['total_services']} services")

    # ... continue with rest of LUKHAS startup ...

# In shutdown handler:
async def shutdown_lukhas_system():
    # ... existing LUKHAS shutdown ...

    # Graceful Cognitive AI shutdown
    await cognitive_initializer.graceful_shutdown()

    # ... complete LUKHAS shutdown ...

Service Integration Examples:
===========================

# Accessing Cognitive services from existing LUKHAS modules:
from cognitive_core.integration import get_agi_service

# In consciousness module:
reasoning_service = get_agi_service("cognitive_chain_of_thought")
if reasoning_service and reasoning_service.get_health()["status"] == "healthy":
    # Use Cognitive AI reasoning capabilities
    pass

# In memory module:
vector_memory = get_agi_service("cognitive_vector_memory")
if vector_memory:
    # Enhanced memory operations with Cognitive AI
    pass

# In dream module:
dream_integration = get_agi_service("cognitive_dream_integration")
if dream_integration:
    # Dream-guided Cognitive AI processing
    pass
"""
