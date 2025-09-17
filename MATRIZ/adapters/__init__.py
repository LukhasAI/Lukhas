"""
MATRIZ Adapters - Node Contract Implementations

All adapters implement MatrizNode.handle(MatrizMessage) -> MatrizResult
"""
from .bio_adapter import BioAdapter
from .memory_adapter import MemoryAdapter
from .consciousness_adapter import ConsciousnessAdapter
from .bridge_adapter import BridgeAdapter
from .governance_adapter import GovernanceAdapter
from .emotion_adapter import EmotionAdapter
from .orchestration_adapter import OrchestrationAdapter
from .compliance_adapter import ComplianceAdapter
from .identity_adapter import IdentityAdapter
from .contradiction_adapter import ContradictionAdapter
from .creative_adapter import CreativeAdapter

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