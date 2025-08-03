"""
VIVOX - Living Voice and Ethical Conscience System
Complete ethical AGI framework for LUKHAS

Components:
- VIVOX.ME: Memory Expansion with 3D helix storage
- VIVOX.MAE: Moral Alignment Engine with z(t) collapse
- VIVOX.CIL: Consciousness Interpretation Layer
- VIVOX.SRM: Self-Reflective Memory audit system
"""

from .memory_expansion.vivox_me_core import (
    VIVOXMemoryExpansion,
    MemoryHelixEntry,
    EmotionalDNA,
    VeilLevel,
    VeilingOperation,
    TruthAuditResult
)

from .memory_expansion.symbolic_proteome import (
    VIVOXSymbolicProteome,
    ProteinFold,
    MisfoldingReport,
    MisfoldingType,
    MisfoldingIssue
)

from .moral_alignment.vivox_mae_core import (
    VIVOXMoralAlignmentEngine,
    ActionProposal,
    MAEDecision,
    DissonanceResult,
    PotentialState,
    CollapsedState
)

from .consciousness.vivox_cil_core import (
    VIVOXConsciousnessInterpretationLayer,
    ConsciousExperience,
    ConsciousnessState,
    CollapsedAwareness,
    DriftMeasurement,
    SimulationBranch,
    CollapsedAction
)

from .self_reflection.vivox_srm_core import (
    VIVOXSelfReflectiveMemory,
    CollapseLogEntry,
    SuppressionRecord,
    AuditTrail,
    ConscienceReport,
    DecisionType
)

__version__ = "1.0.0"
__author__ = "LUKHAS AI"

__all__ = [
    # Core Classes
    "VIVOXMemoryExpansion",
    "VIVOXSymbolicProteome", 
    "VIVOXMoralAlignmentEngine",
    "VIVOXConsciousnessInterpretationLayer",
    "VIVOXSelfReflectiveMemory",
    
    # Memory Types
    "MemoryHelixEntry",
    "EmotionalDNA",
    "VeilLevel",
    "VeilingOperation",
    "TruthAuditResult",
    "ProteinFold",
    "MisfoldingReport",
    "MisfoldingType",
    "MisfoldingIssue",
    
    # Moral Alignment Types
    "ActionProposal",
    "MAEDecision",
    "DissonanceResult",
    "PotentialState",
    "CollapsedState",
    
    # Consciousness Types
    "ConsciousExperience",
    "ConsciousnessState",
    "CollapsedAwareness",
    "DriftMeasurement",
    "SimulationBranch",
    "CollapsedAction",
    
    # Self-Reflection Types
    "CollapseLogEntry",
    "SuppressionRecord",
    "AuditTrail",
    "ConscienceReport",
    "DecisionType"
]


async def create_vivox_system(memory_expansion: VIVOXMemoryExpansion = None) -> dict:
    """
    Create complete VIVOX system with all components initialized
    
    Returns:
        dict: Dictionary containing all VIVOX components
    """
    # Initialize memory expansion if not provided
    if memory_expansion is None:
        memory_expansion = VIVOXMemoryExpansion()
    
    # Initialize other components
    moral_alignment = VIVOXMoralAlignmentEngine(memory_expansion)
    consciousness = VIVOXConsciousnessInterpretationLayer(memory_expansion, moral_alignment)
    self_reflection = VIVOXSelfReflectiveMemory(memory_expansion)
    
    return {
        "memory_expansion": memory_expansion,
        "moral_alignment": moral_alignment,
        "consciousness": consciousness,
        "self_reflection": self_reflection
    }