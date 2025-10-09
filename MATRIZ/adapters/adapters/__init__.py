"""
MATRIZ Adapters - Node Contract Implementations

All adapters implement MatrizNode.handle(MatrizMessage) -> MatrizResult
"""
from .bio_adapter import BioAdapter
from .bridge_adapter import BridgeAdapter
from .compliance_adapter import ComplianceAdapter
from .consciousness_adapter import ConsciousnessAdapter
from .contradiction_adapter import ContradictionAdapter
from .creative_adapter import CreativeAdapter
from .emotion_adapter import EmotionAdapter
from .governance_adapter import GovernanceAdapter
from .identity_adapter import IdentityAdapter
from .memory_adapter import MemoryAdapter
from .orchestration_adapter import OrchestrationAdapter

__all__ = [
    "BioAdapter",
    "MemoryAdapter",
    "ConsciousnessAdapter",
    "BridgeAdapter",
    "GovernanceAdapter",
    "EmotionAdapter",
    "OrchestrationAdapter",
    "ComplianceAdapter",
    "IdentityAdapter",
    "ContradictionAdapter",
    "CreativeAdapter",
]
