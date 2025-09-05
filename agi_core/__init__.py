"""
AGI Core Infrastructure for LUKHAS AI

Advanced Artificial General Intelligence capabilities built on top of LUKHAS
consciousness framework, integrating with the dream system for enhanced
cognitive abilities.

Core Components:
- reasoning: Advanced reasoning with dream integration
- orchestration: Multi-model coordination and consensus  
- memory: Enhanced memory architecture with vector storage
- dream_learning: Dream-guided learning and insight generation
- tools: Tool use framework with dream-guided selection
- constitutional: Constitutional AI safety and alignment
- confidence: Uncertainty quantification and fact checking
- learning: Real-time learning and adaptation
- multimodal: Cross-modal processing and understanding

This system respects the LUKHAS lane system:
- Development at root level (agi_core/)
- Validation in candidate/ 
- Production promotion to lukhas/
"""

from .reasoning import ChainOfThought, TreeOfThoughts
from .orchestration import ModelRouter, ConsensusEngine
from .memory import VectorMemory, EpisodicMemory
from .dream_learning import PatternEmergence, CreativeSynthesis
from .tools import CodeExecutor, ToolSelector
from .constitutional import PrinciplesEngine, HarmPrevention
from .confidence import UncertaintyQuantifier, FactVerifier

__version__ = "0.1.0"
__author__ = "LUKHAS AI AGI Development Team"

# AGI capability exports
__all__ = [
    "ChainOfThought",
    "TreeOfThoughts", 
    "ModelRouter",
    "ConsensusEngine",
    "VectorMemory",
    "EpisodicMemory",
    "PatternEmergence",
    "CreativeSynthesis",
    "CodeExecutor",
    "ToolSelector",
    "PrinciplesEngine",
    "HarmPrevention",
    "UncertaintyQuantifier",
    "FactVerifier",
]