"""
MATRIZ Adapters - Node Contract Implementations

All adapters implement MatrizNode.handle(MatrizMessage) -> MatrizResult
"""
from .bio_adapter import BioAdapter  # (relative imports in __init__.py are idiomatic)
from .bridge_adapter import (
    BridgeAdapter,  # (relative imports in __init__.py are idiomatic)
)
from .compliance_adapter import (
    ComplianceAdapter,  # (relative imports in __init__.py are idiomatic)
)
from .consciousness_adapter import (
    ConsciousnessAdapter,  # (relative imports in __init__.py are idiomatic)
)
from .contradiction_adapter import (
    ContradictionAdapter,  # (relative imports in __init__.py are idiomatic)
)
from .creative_adapter import (
    CreativeAdapter,  # (relative imports in __init__.py are idiomatic)
)
from .emotion_adapter import (
    EmotionAdapter,  # (relative imports in __init__.py are idiomatic)
)
from .governance_adapter import (
    GovernanceAdapter,  # (relative imports in __init__.py are idiomatic)
)
from .identity_adapter import (
    IdentityAdapter,  # (relative imports in __init__.py are idiomatic)
)
from .memory_adapter import (
    MemoryAdapter,  # (relative imports in __init__.py are idiomatic)
)
from .orchestration_adapter import (
    OrchestrationAdapter,  # (relative imports in __init__.py are idiomatic)
)

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
