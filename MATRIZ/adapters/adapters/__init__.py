"""
MATRIZ Adapters - Node Contract Implementations

All adapters implement MatrizNode.handle(MatrizMessage) -> MatrizResult
"""
from .bio_adapter import BioAdapter  # noqa: TID252 (relative imports in __init__.py are idiomatic)
from .bridge_adapter import (
    BridgeAdapter,  # noqa: TID252 (relative imports in __init__.py are idiomatic)
)
from .compliance_adapter import (
    ComplianceAdapter,  # noqa: TID252 (relative imports in __init__.py are idiomatic)
)
from .consciousness_adapter import (
    ConsciousnessAdapter,  # noqa: TID252 (relative imports in __init__.py are idiomatic)
)
from .contradiction_adapter import (
    ContradictionAdapter,  # noqa: TID252 (relative imports in __init__.py are idiomatic)
)
from .creative_adapter import (
    CreativeAdapter,  # noqa: TID252 (relative imports in __init__.py are idiomatic)
)
from .emotion_adapter import (
    EmotionAdapter,  # noqa: TID252 (relative imports in __init__.py are idiomatic)
)
from .governance_adapter import (
    GovernanceAdapter,  # noqa: TID252 (relative imports in __init__.py are idiomatic)
)
from .identity_adapter import (
    IdentityAdapter,  # noqa: TID252 (relative imports in __init__.py are idiomatic)
)
from .memory_adapter import (
    MemoryAdapter,  # noqa: TID252 (relative imports in __init__.py are idiomatic)
)
from .orchestration_adapter import (
    OrchestrationAdapter,  # noqa: TID252 (relative imports in __init__.py are idiomatic)
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
