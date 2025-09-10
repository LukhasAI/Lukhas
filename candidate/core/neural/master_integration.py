"""

#TAG:core
#TAG:neural
#TAG:neuroplastic
#TAG:colony

LUKHAS Master Integration - Connects all neural pathways
"""
import logging
from typing import Any

logger = logging.getLogger(__name__)


class LUKHASNeuralNetwork:
    """Master neural network connecting all modules"""

    def __init__(self):
        self.modules = {}
        self.neural_pathways = {}
        self.active = False

        # Initialize core modules
        self._initialize_modules()

    def _initialize_modules(self):
        """Initialize and connect all modules"""
        try:
            # Import module connectors
            from candidate.bridge.neuroplastic_connector import BridgeConnector

            # Import bridges
            from candidate.core.neural_bridge import neural_bridge
            from candidate.core.neuroplastic_connector import CoreConnector
            from emotion.neuroplastic_connector import EmotionConnector
            from lukhas.consciousness.neuroplastic_connector import (
                ConsciousnessConnector,
            )
            from lukhas.governance.neuroplastic_connector import GovernanceConnector
            from lukhas.memory.neuroplastic_connector import MemoryConnector
            from qi.neuroplastic_connector import QimConnector

            # Register all modules with neural bridge
            self.modules = {
                "core": CoreConnector(),
                "consciousness": ConsciousnessConnector(),
                "memory": MemoryConnector(),
                "qim": QimConnector(),
                "emotion": EmotionConnector(),
                "governance": GovernanceConnector(),
                "bridge": BridgeConnector(),
            }

            # Register with neural bridge
            for name, connector in self.modules.items():
                neural_bridge.register_module(name, connector)

            # Create neural pathways
            self._create_neural_pathways()

            self.active = True
            logger.info("✅ LUKHAS Neural Network initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize neural network: {e}")
            self.active = False

    def _create_neural_pathways(self):
        """Create connections between modules"""
        from candidate.core.neural_bridge import neural_bridge

        # Core pathways
        neural_bridge.create_synapse("consciousness", "memory")
        neural_bridge.create_synapse("consciousness", "emotion")
        neural_bridge.create_synapse("memory", "emotion")
        neural_bridge.create_synapse("governance", "core")
        neural_bridge.create_synapse("bridge", "consciousness")
        neural_bridge.create_synapse("qim", "consciousness")

        logger.info("🧠 Neural pathways established")

    def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Process input through the neural network"""
        if not self.active:
            raise RuntimeError("Neural network not active")

        # Route through appropriate modules based on input
        results = {}

        # Always go through governance first
        if "governance" in self.modules:
            gov_result = self.modules["governance"].process(input_data)
            if not gov_result.get("allowed", True):
                return {
                    "error": "Governance check failed",
                    "reason": gov_result,
                }

        # Process through relevant modules
        for module_name, module in self.modules.items():
            if hasattr(module, "process"):
                try:
                    results[module_name] = module.process(input_data)
                except Exception as e:
                    logger.error(f"Module {module_name} processing failed: {e}")
                    results[module_name] = {"error": str(e)}

        return results


# Global neural network instance
lukhas_neural_network = LUKHASNeuralNetwork()

# Export for main.py


def get_neural_network():
    """Get the global neural network instance"""
    return lukhas_neural_network
