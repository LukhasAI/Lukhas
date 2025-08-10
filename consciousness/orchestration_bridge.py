"""
Orchestration Bridge - Connects brain components to consciousness module
"""

from typing import Any, Dict, Optional

from core.common import get_logger

logger = get_logger(__name__)


class OrchestrationBridge:
    """Bridges orchestration components to main consciousness system"""

    def __init__(self):
        self.brain_components = {}
        self.active_thoughts = []

    def register_brain_component(self, name: str, component: Any):
        """Register a brain component"""
        self.brain_components[name] = component
        logger.info(f"Registered brain component: {name}")

    def think(self, thought: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a thought through brain components"""
        # Route through relevant brain components
        results = {}
        for name, component in self.brain_components.items():
            if hasattr(component, "process"):
                try:
                    results[name] = component.process(thought)
                except Exception as e:
                    logger.error(f"Brain component {name} failed: {e}")

        return results


# Auto-import orchestration components
orchestration_bridge = OrchestrationBridge()

# Import cognitive components
try:
    from orchestration.brain.cognitive.cognitive_updater import (
        CognitiveUpdater,
    )

    orchestration_bridge.register_brain_component(
        "cognitive_updater", CognitiveUpdater()
    )
except ImportError:
    pass

# Import monitoring components
try:
    from orchestration.brain.monitoring.rate_modulator import RateModulator

    orchestration_bridge.register_brain_component("rate_modulator", RateModulator())
except ImportError:
    pass

# Import personality components
try:
    from orchestration.brain.personality.personality import PersonalityEngine

    orchestration_bridge.register_brain_component("personality", PersonalityEngine())
except ImportError:
    pass
