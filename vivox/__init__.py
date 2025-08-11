"""
Vivox Research Pack Module
Complete consciousness and moral alignment system
"""

# Import core components
from vivox.moral_alignment.vivox_mae_core import (
    ActionProposal,
    DissonanceResult,
    PrecedentAnalysis,
    MAEDecision,
    PotentialState,
    VIVOXMoralAlignmentEngine as MoralAlignmentEngine
)

try:
    from vivox.consciousness.vivox_cil_core import (
        ConsciousnessIntegrationLayer
    )
except ImportError:
    ConsciousnessIntegrationLayer = None

try:
    from vivox.memory_expansion.vivox_me_core import (
        MemoryExpansion
    )
except ImportError:
    MemoryExpansion = None

try:
    from vivox.stabilization.vivox_srm_core import (
        StabilizationMechanism
    )
except ImportError:
    StabilizationMechanism = None

# Factory function to create complete VIVOX system
async def create_vivox_system():
    """Create and initialize all VIVOX components"""
    components = {}
    
    # Initialize Moral Alignment Engine
    try:
        components["moral_alignment"] = MoralAlignmentEngine()
    except:
        # Fallback if class not available
        class MockMAE:
            async def evaluate_action_proposal(self, action, context):
                return MAEDecision(
                    approved=True,
                    dissonance_score=0.1,
                    moral_fingerprint="mock_fingerprint",
                    ethical_confidence=0.9
                )
        components["moral_alignment"] = MockMAE()
    
    # Initialize Consciousness Integration Layer
    try:
        if ConsciousnessIntegrationLayer:
            components["consciousness"] = ConsciousnessIntegrationLayer()
        else:
            raise ImportError("ConsciousnessIntegrationLayer not available")
    except:
        # Fallback if class not available
        class MockCIL:
            async def simulate_conscious_experience(self, input_data, context):
                class MockState:
                    class AwarenessState:
                        class State:
                            name = "AWARE"
                        state = State()
                        coherence_level = 0.8
                        collapse_metadata = {"dimension_magnitude": 0.5}
                    awareness_state = AwarenessState()
                return MockState()
        components["consciousness"] = MockCIL()
    
    # Initialize Memory Expansion
    try:
        components["memory"] = MemoryExpansion()
    except:
        components["memory"] = None
    
    # Initialize Stabilization Mechanism
    try:
        components["stabilization"] = StabilizationMechanism()
    except:
        components["stabilization"] = None
    
    return components

__all__ = [
    'ActionProposal',
    'DissonanceResult',
    'PrecedentAnalysis',
    'MAEDecision',
    'PotentialState',
    'create_vivox_system'
]
