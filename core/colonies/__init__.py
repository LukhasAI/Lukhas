"""Core colony modules for LUKHAS."""

from . import oracle_colony
from .base_colony import BaseColony, ConsensusResult, Tag, TagScope
from .ethics_swarm_colony import (
    EthicalDecisionRequest,
    EthicalDecisionResponse,
    EthicalDecisionType,
    EthicalSignal,
    EthicsSwarmColony,
)

__all__ = [
    "oracle_colony",
    "BaseColony",
    "Tag",
    "TagScope",
    "ConsensusResult",
    "EthicalDecisionRequest",
    "EthicalDecisionResponse",
    "EthicalDecisionType",
    "EthicalSignal",
    "EthicsSwarmColony",
]
