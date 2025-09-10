"""
Dream Service Initialization
============================
Registers dream services and related consciousness services for dependency injection.
"""

import logging

from candidate.core.interfaces.dependency_injection import register_service
from consciousness.dream.core.dream_engine import DreamEngine
from datetime import timezone

logger = logging.getLogger(__name__)


def initialize_dream_services():
    """Initialize and register dream services"""
    try:
        # Create dream engine instance
        dream_engine = DreamEngine()

        # Register dream service
        register_service("dream_engine", dream_engine, singleton=True)

        logger.info("Dream services initialized and registered")
        return True

    except Exception as e:
        logger.error(f"Failed to initialize dream services: {e}")
        return False


def initialize_consciousness_services():
    """Initialize consciousness services needed by the interface"""
    try:
        # Import and register consciousness service
        from consciousness.unified.auto_consciousness import AutoConsciousness

        consciousness = AutoConsciousness()
        register_service("consciousness_service", consciousness, singleton=True)

        # Mock other required services with minimal implementations
        class MockMemoryService:
            async def search(self, query=None, limit=5):
                return [
                    {
                        "id": "mem1",
                        "summary": "Mock memory entry",
                        "timestamp": "2025-08-10",
                    },
                    {
                        "id": "mem2",
                        "summary": "Another memory",
                        "timestamp": "2025-08-10",
                    },
                ]

        class MockEmotionService:
            async def analyze_text(self, text):
                return {
                    "emotions": {
                        "joy": 0.5,
                        "sadness": 0.1,
                        "anger": 0.0,
                        "fear": 0.1,
                        "surprise": 0.3,
                    }
                }

            async def get_current_state(self):
                return {
                    "dominant_emotion": "contentment",
                    "valence": 0.6,
                    "arousal": 0.4,
                    "dominance": 0.5,
                }

        class MockParallelRealitySimulator:
            async def create_simulation(self, origin_scenario, branch_count=3):
                from datetime import datetime

                from consciousness.dream.parallel_reality_simulator import RealityBranch, RealityType

                return type(
                    "Simulation",
                    (),
                    {
                        "branches": [
                            RealityBranch(
                                branch_id=f"branch_{i}",
                                probability=0.8 - i * 0.1,
                                reality_type=RealityType.OPTIMISTIC,
                                timestamp=datetime.now(timezone.utc),
                                ethical_score=0.9,
                                causal_chain=[],
                                divergence_point={"summary": f"path {i + 1}"},
                            )
                            for i in range(branch_count)
                        ]
                    },
                )()

        register_service("memory_service", MockMemoryService(), singleton=True)
        register_service("emotion_service", MockEmotionService(), singleton=True)
        register_service("parallel_reality_simulator", MockParallelRealitySimulator(), singleton=True)

        logger.info("Consciousness services initialized and registered")
        return True

    except Exception as e:
        logger.error(f"Failed to initialize consciousness services: {e}")
        return False


def initialize_all_services():
    """Initialize all required services for dream integration"""
    dream_success = initialize_dream_services()
    consciousness_success = initialize_consciousness_services()
    return dream_success and consciousness_success


# Auto-initialize when module is imported
if __name__ != "__main__":
    initialize_all_services()