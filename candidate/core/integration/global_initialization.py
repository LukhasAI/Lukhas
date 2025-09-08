"""

#TAG:core
#TAG:integration
#TAG:neuroplastic
#TAG:colony

Global System Initialization
Coordinated initialization of all system hubs and cross-system connections
"""
import asyncio
import logging
from typing import Any

import streamlit as st

from consciousness.qi import qi

logger = logging.getLogger(__name__)


class GlobalSystemInitializer:
    """
    Manages the initialization of all system hubs and their interconnections
    """

    def __init__(self):
        self.hubs_initialized = []
        self.bridges_initialized = []
        self.services_registered = 0

    async def initialize_all_systems(self) -> dict[str, Any]:
        """Initialize all system hubs in the correct order"""
        logger.info("Starting global system initialization...")

        # Initialize core systems first
        await self._initialize_core_systems()

        # Initialize supporting systems
        await self._initialize_supporting_systems()

        # Initialize bridges between systems
        await self._initialize_bridges()

        # Perform cross-system registration
        await self._cross_register_services()

        # Verify system connectivity
        health_status = await self._verify_system_health()

        return {
            "status": "initialized",
            "hubs_initialized": self.hubs_initialized,
            "bridges_initialized": self.bridges_initialized,
            "services_registered": self.services_registered,
            "health_check": health_status,
        }

    async def _initialize_core_systems(self):
        """Initialize core system hubs"""
        core_systems = [
            ("core", "core.core_hub", "initialize_core_system"),
            (
                "consciousness",
                "consciousness.consciousness_hub",
                "initialize_consciousness_system",
            ),
            ("memory", "memory.memory_hub", "initialize_memory_system"),
            ("quantum", "qi.qi_hub", "initialize_quantum_system"),
        ]

        for system_name, module_path, init_func in core_systems:
            try:
                module = __import__(module_path, fromlist=[init_func])
                initializer = getattr(module, init_func)
                await initializer()
                self.hubs_initialized.append(system_name)
                logger.info(f"Initialized {system_name} hub")
            except Exception as e:
                logger.error(f"Failed to initialize {system_name}: {e}")

    async def _initialize_supporting_systems(self):
        """Initialize supporting system hubs"""
        supporting_systems = [
            ("safety", "core.safety.safety_hub", "get_safety_hub"),
            ("nias", "nias.nias_hub", "initialize_nias_system"),
            ("bio", "bio.bio_hub", "initialize_bio_system"),
            (
                "symbolic",
                "symbolic.symbolic_hub",
                "initialize_symbolic_system",
            ),
            (
                "learning",
                "learning.learning_hub",
                "initialize_learning_system",
            ),
            ("dream", "dream.dream_hub", "initialize_dream_system"),
        ]

        for system_name, module_path, init_func in supporting_systems:
            try:
                module = __import__(module_path, fromlist=[init_func])
                initializer = getattr(module, init_func)

                # Some hubs need async initialization
                if system_name in [
                    "nias",
                    "bio",
                    "symbolic",
                    "learning",
                    "dream",
                ]:
                    hub = await initializer()
                else:
                    hub = initializer()
                    if hasattr(hub, "initialize"):
                        await hub.initialize()

                self.hubs_initialized.append(system_name)
                logger.info(f"Initialized {system_name} hub")
            except Exception as e:
                logger.error(f"Failed to initialize {system_name}: {e}")

    async def _initialize_bridges(self):
        """Initialize all cross-system bridges"""
        bridges = [
            # Core bridges
            (
                "core_consciousness_bridge",
                "core.bridges.core_consciousness_bridge",
                "get_core_consciousness_bridge",
            ),
            (
                "core_safety_bridge",
                "core.bridges.core_safety_bridge",
                "get_core_safety_bridge",
            ),
            # Integration bridges
            (
                "nias_dream_bridge",
                "core.bridges.nias_dream_bridge",
                "get_nias_dream_bridge",
            ),
            (
                "consciousness_quantum_bridge",
                "core.bridges.consciousness_quantum_bridge",
                "get_consciousness_quantum_bridge",
            ),
            (
                "memory_learning_bridge",
                "core.bridges.memory_learning_bridge",
                "get_memory_learning_bridge",
            ),
            (
                "bio_symbolic_bridge",
                "core.bridges.bio_symbolic_bridge",
                "get_bio_symbolic_bridge",
            ),
            # Safety bridges
            (
                "safety_quantum_bridge",
                "safety.bridges.safety_quantum_bridge",
                "get_safety_quantum_bridge",
            ),
            (
                "safety_memory_bridge",
                "safety.bridges.safety_memory_bridge",
                "get_safety_memory_bridge",
            ),
            (
                "safety_core_bridge",
                "safety.bridges.safety_core_bridge",
                "get_safety_core_bridge",
            ),
        ]

        for bridge_name, module_path, getter_func in bridges:
            try:
                module = __import__(module_path, fromlist=[getter_func])
                getter = getattr(module, getter_func)
                bridge = getter()

                # Connect the bridge
                if hasattr(bridge, "connect"):
                    await bridge.connect()

                self.bridges_initialized.append(bridge_name)
                logger.info(f"Initialized {bridge_name}")
            except Exception as e:
                logger.error(f"Failed to initialize {bridge_name}: {e}")

    async def _cross_register_services(self):
        """Perform cross-hub service registration"""
        try:
            from candidate.core.integration.service_discovery import (
                get_service_discovery,
            )

            discovery = get_service_discovery()

            # Get all registered services
            all_services = discovery.get_all_services()
            self.services_registered = len(all_services)

            logger.info(f"Cross-registered {self.services_registered} services across all hubs")
        except Exception as e:
            logger.error(f"Failed to cross-register services: {e}")

    async def _verify_system_health(self) -> dict[str, Any]:
        """Verify health of all initialized systems"""
        health_status = {"overall": "healthy", "hubs": {}, "bridges": {}}

        # Check hub health
        hub_modules = {
            "core": ("core.hub_registry", "get_hub_registry"),
            "service_discovery": (
                "core.service_discovery",
                "get_service_discovery",
            ),
        }

        for hub_name, (module_path, getter_func) in hub_modules.items():
            try:
                module = __import__(module_path, fromlist=[getter_func])
                getter = getattr(module, getter_func)
                hub = getter()

                if hasattr(hub, "health_check"):
                    health = (
                        await hub.health_check()
                        if asyncio.iscoroutinefunction(hub.health_check)
                        else hub.health_check()
                    )
                    health_status["hubs"][hub_name] = health
                else:
                    health_status["hubs"][hub_name] = {"status": "active"}
            except Exception as e:
                health_status["hubs"][hub_name] = {
                    "status": "error",
                    "error": str(e),
                }
                health_status["overall"] = "degraded"

        # Check bridge health
        for bridge_name in self.bridges_initialized:
            health_status["bridges"][bridge_name] = {"status": "connected"}

        return health_status


async def initialize_global_system() -> dict[str, Any]:
    """
    Main entry point for global system initialization
    """
    initializer = GlobalSystemInitializer()
    return await initializer.initialize_all_systems()


# Convenience functions for specific initialization patterns


async def initialize_minimal_system() -> dict[str, Any]:
    """Initialize only core systems for minimal functionality"""
    initializer = GlobalSystemInitializer()
    await initializer._initialize_core_systems()
    return {
        "status": "minimal",
        "hubs_initialized": initializer.hubs_initialized,
    }


async def initialize_with_safety() -> dict[str, Any]:
    """Initialize systems with safety as priority"""
    initializer = GlobalSystemInitializer()

    # Initialize safety first
    try:
        from candidate.core.safety.safety_hub import get_safety_hub

        safety_hub = get_safety_hub()
        (await safety_hub.initialize() if hasattr(safety_hub, "initialize") else None)
        initializer.hubs_initialized.append("safety")
    except Exception as e:
        logger.error(f"Failed to initialize safety hub: {e}")
        return {"status": "error", "error": "Safety initialization failed"}

    # Then initialize other systems
    await initializer._initialize_core_systems()
    await initializer._initialize_supporting_systems()
    await initializer._initialize_bridges()

    return {
        "status": "initialized_with_safety",
        "hubs_initialized": initializer.hubs_initialized,
        "bridges_initialized": initializer.bridges_initialized,
    }


__all__ = [
    "GlobalSystemInitializer",
    "initialize_global_system",
    "initialize_minimal_system",
    "initialize_with_safety",
]
