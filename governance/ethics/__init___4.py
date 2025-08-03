"""

#TAG:governance
#TAG:ethics
#TAG:neuroplastic
#TAG:colony


Ethics Core Module

Shared ethical reasoning and decision-making for LUKHAS systems.
"""

from .shared_ethics_engine import (
    SharedEthicsEngine,
    EthicalPrinciple,
    EthicalSeverity,
    DecisionType,
    EthicalConstraint,
    EthicalDecision,
    get_shared_ethics_engine
)

__all__ = [
    "SharedEthicsEngine",
    "EthicalPrinciple",
    "EthicalSeverity",
    "DecisionType",
    "EthicalConstraint",
    "EthicalDecision",
    "get_shared_ethics_engine"
]

__version__ = "1.0.0"