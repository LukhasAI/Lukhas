"""
🧠 LUKHAS Brain Systems Integration Bridge
Unified access to all cognitive and reasoning systems
"""

from orchestration.brain.neuro_symbolic.neuro_symbolic_engine import NeuroSymbolicEngine
from orchestration.brain.lukhas_brain import LUKHASBrain
from orchestration.meta_cognitive_orchestrator import MetaCognitiveOrchestrator

class LUKHASBrainBridge:
    """
    Unified interface for all LUKHAS brain and cognitive systems.
    """

    def __init__(self):
        self.neuro_symbolic = NeuroSymbolicEngine()
        self.brain = LUKHASBrain()
        self.meta_cognitive = MetaCognitiveOrchestrator()

    async def comprehensive_reasoning(self, input_data, context=None):
        """
        Run comprehensive reasoning across all brain systems.
        """
        # Neuro-symbolic processing
        symbolic_result = await self.neuro_symbolic.process(input_data)

        # Brain processing
        brain_result = await self.brain.process(input_data, context)

        # Meta-cognitive orchestration
        orchestrated_result = await self.meta_cognitive.orchestrate(
            symbolic_result, brain_result, context
        )

        return orchestrated_result

# Global brain bridge instance
brain_bridge = LUKHASBrainBridge()
