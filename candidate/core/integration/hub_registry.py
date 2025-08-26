"""

#TAG:core
#TAG:integration
#TAG:neuroplastic
#TAG:colony

Global Hub Registry
Central registry for all system hubs
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class HubRegistry:
    """Central registry for all system hubs"""

    def __init__(self):
        self.hubs = {}
        self._initialize_hubs()

    def _initialize_hubs(self):
        """Initialize all system hubs"""
        hub_configs = [
            ("core", "core.core_hub", "get_core_hub"),
            (
                "consciousness",
                "consciousness.consciousness_hub",
                "get_consciousness_hub",
            ),
            ("memory", "memory.memory_hub", "get_memory_hub"),
            ("quantum", "qi.qi_hub", "get_quantum_hub"),
            ("safety", "core.safety.safety_hub", "get_safety_hub"),
            ("bio", "bio.bio_hub", "get_bio_hub"),
            (
                "orchestration",
                "orchestration.orchestration_hub",
                "get_orchestration_hub",
            ),
            ("nias", "core.modules.nias.nias_hub", "get_nias_hub"),
            ("dream", "orchestration.dream.dream_hub", "get_dream_hub"),
            ("symbolic", "symbolic.symbolic_hub", "get_symbolic_hub"),
            ("learning", "learning.learning_hub", "get_learning_hub"),
            ("reasoning", "reasoning.reasoning_hub", "get_reasoning_hub"),
        ]

        for hub_name, module_path, factory_name in hub_configs:
            try:
                module = __import__(module_path, fromlist=[factory_name])
                factory = getattr(module, factory_name)
                self.hubs[hub_name] = factory
                logger.debug(f"Registered hub factory: {hub_name}")
            except (ImportError, AttributeError) as e:
                logger.warning(f"Could not register hub {hub_name}: {e}")

    def get_hub(self, hub_name: str):
        """Get a hub by name"""
        factory = self.hubs.get(hub_name)
        if factory:
            return factory()
        return None

    def get_all_hubs(self) -> dict[str, Any]:
        """Get all registered hubs"""
        return {name: factory() for name, factory in self.hubs.items()}

    async def health_check_all(self) -> dict[str, Any]:
        """Health check all hubs"""
        results = {}
        for name, factory in self.hubs.items():
            try:
                hub = factory()
                if hasattr(hub, "health_check"):
                    results[name] = await hub.health_check()
                else:
                    results[name] = {"status": "unknown"}
            except Exception as e:
                results[name] = {"status": "error", "error": str(e)}
        return results


# Singleton
_hub_registry = None


def get_hub_registry() -> HubRegistry:
    global _hub_registry
    if _hub_registry is None:
        _hub_registry = HubRegistry()
    return _hub_registry
