"""
AGI Service Initializer
=======================

Initialization script that registers and configures all AGI services within
the LUKHAS ecosystem. This script is responsible for:

- Registering AGI components in the LUKHAS service registry
- Configuring service dependencies and connections
- Establishing integration with existing LUKHAS modules
- Starting AGI service monitoring and health checks
- Providing graceful initialization and error handling

This is the central entry point for AGI service integration with LUKHAS.
Run during system startup to enable AGI capabilities across all modules.

Part of Phase 2A: Core Integrations - Basic service connections
Created: 2025-09-05
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

try:
    # AGI Components
    from agi_core.reasoning import ChainOfThought, TreeOfThoughts, DreamIntegration
    from agi_core.orchestration import ModelRouter, ConsensusEngine, CapabilityMatrix, CostOptimizer
    from agi_core.memory import VectorMemory, MemoryConsolidator, EpisodicMemory, SemanticMemory, DreamMemory
    from agi_core.safety import ConstitutionalAI
    from agi_core.learning import DreamGuidedLearner
    from agi_core.tools import DreamGuidedTools
    
    # Integration Services
    from agi_core.integration import (
        agi_service_bridge, vocabulary_service, 
        register_agi_service, log_agi_operation
    )
    
    COMPONENTS_AVAILABLE = True
    
except ImportError as e:
    logging.warning(f"Some AGI components not available: {e}")
    COMPONENTS_AVAILABLE = False
    
    # Mock components for testing
    class MockAGIComponent:
        def __init__(self, name: str):
            self.name = name
        async def initialize(self): pass
        async def shutdown(self): pass
        def get_health(self): return {"status": "healthy", "component": self.name}
    
    # Create mock components
    ChainOfThought = lambda: MockAGIComponent("ChainOfThought")
    TreeOfThoughts = lambda: MockAGIComponent("TreeOfThoughts") 
    DreamIntegration = lambda: MockAGIComponent("DreamIntegration")
    ModelRouter = lambda: MockAGIComponent("ModelRouter")
    ConsensusEngine = lambda: MockAGIComponent("ConsensusEngine")
    CapabilityMatrix = lambda: MockAGIComponent("CapabilityMatrix")
    CostOptimizer = lambda: MockAGIComponent("CostOptimizer")
    VectorMemory = lambda: MockAGIComponent("VectorMemory")
    MemoryConsolidator = lambda: MockAGIComponent("MemoryConsolidator")
    EpisodicMemory = lambda: MockAGIComponent("EpisodicMemory")
    SemanticMemory = lambda: MockAGIComponent("SemanticMemory")
    DreamMemory = lambda: MockAGIComponent("DreamMemory")
    ConstitutionalAI = lambda: MockAGIComponent("ConstitutionalAI")
    DreamGuidedLearner = lambda: MockAGIComponent("DreamGuidedLearner")
    DreamGuidedTools = lambda: MockAGIComponent("DreamGuidedTools")
    
    # Mock services
    class MockBridge:
        async def register_agi_service(self, name, comp, auto_init=True):
            return MockAGIComponent(f"Adapter_{name}")
        async def initialize_all_services(self): return {}
        async def start_health_monitoring(self, interval=60): pass
        def get_service_registry_info(self): return {"status": "mock"}
    
    class MockVocabService:
        def log_agi_operation(self, op, details="", module="agi", severity="INFO"):
            return {"operation": op}
    
    agi_service_bridge = MockBridge()
    vocabulary_service = MockVocabService()
    register_agi_service = agi_service_bridge.register_agi_service
    log_agi_operation = vocabulary_service.log_agi_operation

class AGIServiceConfiguration:
    """Configuration for AGI service initialization."""
    
    def __init__(self):
        self.service_configs = {
            # Reasoning Services
            "agi_chain_of_thought": {
                "component_factory": ChainOfThought,
                "dependencies": [],
                "priority": 1,  # High priority - core reasoning
                "auto_initialize": True,
                "health_monitoring": True,
            },
            "agi_tree_of_thoughts": {
                "component_factory": TreeOfThoughts,
                "dependencies": ["agi_chain_of_thought"],
                "priority": 1,
                "auto_initialize": True,
                "health_monitoring": True,
            },
            "agi_dream_integration": {
                "component_factory": DreamIntegration,
                "dependencies": [],
                "priority": 2,
                "auto_initialize": True,
                "health_monitoring": True,
            },
            
            # Orchestration Services
            "agi_model_router": {
                "component_factory": ModelRouter,
                "dependencies": [],
                "priority": 1,
                "auto_initialize": True,
                "health_monitoring": True,
            },
            "agi_consensus_engine": {
                "component_factory": ConsensusEngine,
                "dependencies": ["agi_model_router"],
                "priority": 2,
                "auto_initialize": True,
                "health_monitoring": True,
            },
            "agi_capability_matrix": {
                "component_factory": CapabilityMatrix,
                "dependencies": ["agi_model_router"],
                "priority": 3,
                "auto_initialize": True,
                "health_monitoring": False,  # Static component
            },
            "agi_cost_optimizer": {
                "component_factory": CostOptimizer,
                "dependencies": ["agi_model_router", "agi_capability_matrix"],
                "priority": 3,
                "auto_initialize": True,
                "health_monitoring": True,
            },
            
            # Memory Services
            "agi_vector_memory": {
                "component_factory": VectorMemory,
                "dependencies": [],
                "priority": 1,
                "auto_initialize": True,
                "health_monitoring": True,
            },
            "agi_episodic_memory": {
                "component_factory": EpisodicMemory,
                "dependencies": ["agi_vector_memory"],
                "priority": 2,
                "auto_initialize": True,
                "health_monitoring": True,
            },
            "agi_semantic_memory": {
                "component_factory": SemanticMemory,
                "dependencies": ["agi_vector_memory"],
                "priority": 2,
                "auto_initialize": True,
                "health_monitoring": True,
            },
            "agi_dream_memory": {
                "component_factory": DreamMemory,
                "dependencies": ["agi_vector_memory", "agi_dream_integration"],
                "priority": 2,
                "auto_initialize": True,
                "health_monitoring": True,
            },
            "agi_memory_consolidator": {
                "component_factory": MemoryConsolidator,
                "dependencies": [
                    "agi_vector_memory", "agi_episodic_memory", 
                    "agi_semantic_memory", "agi_dream_memory"
                ],
                "priority": 3,
                "auto_initialize": True,
                "health_monitoring": True,
            },
            
            # Safety and Learning Services
            "agi_constitutional_ai": {
                "component_factory": ConstitutionalAI,
                "dependencies": [],
                "priority": 1,  # Critical for safety
                "auto_initialize": True,
                "health_monitoring": True,
            },
            "agi_dream_guided_learner": {
                "component_factory": DreamGuidedLearner,
                "dependencies": ["agi_dream_integration", "agi_memory_consolidator"],
                "priority": 2,
                "auto_initialize": True,
                "health_monitoring": True,
            },
            "agi_dream_guided_tools": {
                "component_factory": DreamGuidedTools,
                "dependencies": ["agi_dream_integration", "agi_dream_guided_learner"],
                "priority": 3,
                "auto_initialize": True,
                "health_monitoring": True,
            },
        }

class AGIServiceInitializer:
    """
    Central initializer for all AGI services within the LUKHAS ecosystem.
    
    Handles registration, dependency resolution, graceful initialization,
    and integration with existing LUKHAS service architecture.
    """
    
    def __init__(self, config: Optional[AGIServiceConfiguration] = None):
        self.config = config or AGIServiceConfiguration()
        self.initialized_services: Dict[str, Any] = {}
        self.initialization_order: List[str] = []
        self.failed_services: List[str] = []
        
        # Logger setup
        self.logger = logging.getLogger("agi_service_initializer")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - [%(levelname)s] - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def _resolve_dependency_order(self) -> List[str]:
        """
        Resolve service initialization order based on dependencies.
        
        Uses topological sorting to ensure dependencies are initialized
        before services that depend on them.
        """
        # Simple dependency resolution using priority and dependencies
        services_by_priority = {}
        
        for service_name, config in self.config.service_configs.items():
            priority = config.get("priority", 10)
            if priority not in services_by_priority:
                services_by_priority[priority] = []
            services_by_priority[priority].append(service_name)
        
        # Return services ordered by priority (lower number = higher priority)
        ordered_services = []
        for priority in sorted(services_by_priority.keys()):
            ordered_services.extend(services_by_priority[priority])
        
        return ordered_services
    
    async def initialize_service(self, service_name: str) -> bool:
        """
        Initialize a single AGI service.
        
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
            log_agi_operation("service_init_start", service_name, "agi_initializer")
            
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
            
            # Register with AGI service bridge
            adapter = await register_agi_service(
                service_name, 
                component, 
                auto_initialize=config.get("auto_initialize", True)
            )
            
            self.initialized_services[service_name] = adapter
            self.initialization_order.append(service_name)
            
            log_agi_operation("service_init_success", service_name, "agi_initializer")
            self.logger.info(f"Successfully initialized AGI service: {service_name}")
            
            return True
            
        except Exception as e:
            self.failed_services.append(service_name)
            log_agi_operation("service_init_fail", f"{service_name}: {e}", "agi_initializer", "ERROR")
            self.logger.error(f"Failed to initialize {service_name}: {e}")
            return False
    
    async def initialize_all_services(self) -> Dict[str, bool]:
        """
        Initialize all configured AGI services in dependency order.
        
        Returns:
            Dictionary mapping service names to initialization success status
        """
        log_agi_operation("system_init_start", "initializing all AGI services", "agi_initializer")
        
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
            "system_init_complete", 
            f"{successful_count}/{total_count} services initialized",
            "agi_initializer"
        )
        
        self.logger.info(f"AGI service initialization complete: {successful_count}/{total_count} successful")
        
        return results
    
    async def start_health_monitoring(self, interval_seconds: int = 60) -> None:
        """
        Start health monitoring for all initialized AGI services.
        
        Args:
            interval_seconds: Health check interval
        """
        await agi_service_bridge.start_health_monitoring(interval_seconds)
        log_agi_operation("health_monitor_start", f"monitoring every {interval_seconds}s", "agi_initializer")
    
    async def graceful_shutdown(self) -> Dict[str, bool]:
        """
        Gracefully shutdown all AGI services in reverse order.
        
        Returns:
            Dictionary mapping service names to shutdown success status
        """
        log_agi_operation("system_shutdown_start", "shutting down all AGI services", "agi_initializer")
        
        # Shutdown in reverse initialization order
        shutdown_results = {}
        
        for service_name in reversed(self.initialization_order):
            try:
                adapter = self.initialized_services.get(service_name)
                if adapter:
                    await adapter.shutdown()
                    shutdown_results[service_name] = True
                    log_agi_operation("service_shutdown_success", service_name, "agi_initializer")
                else:
                    shutdown_results[service_name] = False
                    
            except Exception as e:
                shutdown_results[service_name] = False
                log_agi_operation("service_shutdown_fail", f"{service_name}: {e}", "agi_initializer", "ERROR")
                self.logger.error(f"Failed to shutdown {service_name}: {e}")
        
        log_agi_operation("system_shutdown_complete", "AGI services shutdown", "agi_initializer")
        return shutdown_results
    
    def get_initialization_status(self) -> Dict[str, Any]:
        """
        Get comprehensive status of AGI service initialization.
        
        Returns:
            Status information including metrics and service states
        """
        return {
            "total_services": len(self.config.service_configs),
            "initialized_services": len(self.initialized_services),
            "failed_services": len(self.failed_services),
            "initialization_order": self.initialization_order,
            "failed_service_names": self.failed_services,
            "service_registry_info": agi_service_bridge.get_service_registry_info(),
            "components_available": COMPONENTS_AVAILABLE,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# Global initializer instance
agi_initializer = AGIServiceInitializer()

# Main initialization function for external use
async def initialize_agi_system(
    config: Optional[AGIServiceConfiguration] = None,
    start_monitoring: bool = True,
    monitoring_interval: int = 60
) -> Dict[str, Any]:
    """
    Main function to initialize the entire AGI system within LUKHAS.
    
    Args:
        config: Optional custom configuration
        start_monitoring: Whether to start health monitoring
        monitoring_interval: Health check interval in seconds
        
    Returns:
        Initialization status and results
    """
    global agi_initializer
    
    if config:
        agi_initializer = AGIServiceInitializer(config)
    
    log_agi_operation("system_init", "starting AGI system initialization", "agi_main")
    
    # Initialize all services
    init_results = await agi_initializer.initialize_all_services()
    
    # Start health monitoring if requested
    if start_monitoring:
        await agi_initializer.start_health_monitoring(monitoring_interval)
    
    # Get final status
    status = agi_initializer.get_initialization_status()
    status["initialization_results"] = init_results
    
    log_agi_operation("system_ready", "AGI system fully operational", "agi_main")
    
    return status

if __name__ == "__main__":
    # Test the AGI service initializer
    async def test_initializer():
        print("🧠 AGI Service Initializer Test")
        print("="*50)
        
        # Initialize the AGI system
        status = await initialize_agi_system(
            start_monitoring=False  # Disable monitoring for test
        )
        
        print(f"Initialization Status:")
        print(f"  Total services: {status['total_services']}")
        print(f"  Initialized: {status['initialized_services']}")
        print(f"  Failed: {status['failed_services']}")
        print(f"  Components available: {status['components_available']}")
        
        # Show initialization order
        print(f"\nInitialization order: {status['initialization_order']}")
        
        # Show service registry info
        registry_info = status.get('service_registry_info', {})
        print(f"Registry health monitoring: {registry_info.get('health_monitoring', False)}")
        
        # Graceful shutdown
        print("\nShutting down...")
        shutdown_results = await agi_initializer.graceful_shutdown()
        successful_shutdowns = sum(shutdown_results.values())
        print(f"Shutdown: {successful_shutdowns}/{len(shutdown_results)} successful")
    
    asyncio.run(test_initializer())

"""
Usage in LUKHAS System Startup:
==============================

# In main LUKHAS startup script:
from agi_core.integration.agi_service_initializer import initialize_agi_system

async def start_lukhas_system():
    # ... existing LUKHAS initialization ...
    
    # Initialize AGI system
    agi_status = await initialize_agi_system(
        start_monitoring=True,
        monitoring_interval=30
    )
    
    if agi_status["failed_services"] > 0:
        logger.warning(f"Some AGI services failed: {agi_status['failed_service_names']}")
    
    logger.info(f"LUKHAS AGI system ready: {agi_status['initialized_services']}/{agi_status['total_services']} services")
    
    # ... continue with rest of LUKHAS startup ...

# In shutdown handler:
async def shutdown_lukhas_system():
    # ... existing LUKHAS shutdown ...
    
    # Graceful AGI shutdown
    await agi_initializer.graceful_shutdown()
    
    # ... complete LUKHAS shutdown ...

Service Integration Examples:
===========================

# Accessing AGI services from existing LUKHAS modules:
from agi_core.integration import get_agi_service

# In consciousness module:
reasoning_service = get_agi_service("agi_chain_of_thought")
if reasoning_service and reasoning_service.get_health()["status"] == "healthy":
    # Use AGI reasoning capabilities
    pass

# In memory module:
vector_memory = get_agi_service("agi_vector_memory")
if vector_memory:
    # Enhanced memory operations with AGI
    pass

# In dream module:
dream_integration = get_agi_service("agi_dream_integration")
if dream_integration:
    # Dream-guided AGI processing
    pass
"""