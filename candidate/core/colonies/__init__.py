"""
Colonies Module
Auto-generated module initialization file
"""

import logging

logger = logging.getLogger(__name__)

try:
    from .memory_colony import MemoryColony

    logger.debug("Imported MemoryColony from .memory_colony")
except ImportError as e:
    logger.warning(f"Could not import MemoryColony: {e}")
    MemoryColony = None

try:
    from .governance_colony import GovernanceColonyEnhanced

    logger.debug("Imported GovernanceColonyEnhanced from .governance_colony")
except ImportError as e:
    logger.warning(f"Could not import GovernanceColonyEnhanced: {e}")
    GovernanceColonyEnhanced = None

try:
    from .base_colony import BaseColony

    logger.debug("Imported BaseColony from .base_colony")
except ImportError as e:
    logger.warning(f"Could not import BaseColony: {e}")
    BaseColony = None

try:
    from .oracle_colony import OracleColony

    logger.debug("Imported OracleColony from .oracle_colony")
except ImportError as e:
    logger.warning(f"Could not import OracleColony: {e}")
    OracleColony = None

try:
    from .reasoning_colony import ReasoningColony

    logger.debug("Imported ReasoningColony from .reasoning_colony")
except ImportError as e:
    logger.warning(f"Could not import ReasoningColony: {e}")
    ReasoningColony = None

try:
    from .creativity_colony import CreativityColony

    logger.debug("Imported CreativityColony from .creativity_colony")
except ImportError as e:
    logger.warning(f"Could not import CreativityColony: {e}")
    CreativityColony = None

try:
    from .governance_colony import GovernanceColony

    logger.debug("Imported GovernanceColony from .governance_colony")
except ImportError as e:
    logger.warning(f"Could not import GovernanceColony: {e}")
    GovernanceColony = None

# MemoryColonyEnhanced is now part of the main MemoryColony
MemoryColonyEnhanced = MemoryColony

try:
    from .supervisor_agent import SupervisorAgent

    logger.debug("Imported SupervisorAgent from .supervisor_agent")
except ImportError as e:
    logger.warning(f"Could not import SupervisorAgent: {e}")
    SupervisorAgent = None

try:
    from .temporal_colony import TemporalColony

    logger.debug("Imported TemporalColony from .temporal_colony")
except ImportError as e:
    logger.warning(f"Could not import TemporalColony: {e}")
    TemporalColony = None

try:
    from .tensor_colony_ops import TensorColonyOps

    logger.debug("Imported TensorColonyOps from .tensor_colony_ops")
except ImportError as e:
    logger.warning(f"Could not import TensorColonyOps: {e}")
    TensorColonyOps = None

try:
    from .ethics_swarm_colony import EthicsSwarmColony

    logger.debug("Imported EthicsSwarmColony from .ethics_swarm_colony")
except ImportError as e:
    logger.warning(f"Could not import EthicsSwarmColony: {e}")
    EthicsSwarmColony = None

try:
    from .colony import EnhancedReasoningColony, SwarmSignalNetwork

    logger.debug("Imported EnhancedReasoningColony and SwarmSignalNetwork from .colony")
except ImportError as e:
    logger.warning(f"Could not import from colony: {e}")
    EnhancedReasoningColony = None
    SwarmSignalNetwork = None

try:
    from .consensus_mechanisms import (
        ColonyConsensus,
        ConsensusMethod,
        ConsensusProposal,
        VoteType,
    )

    logger.debug("Imported consensus mechanisms from .consensus_mechanisms")
except ImportError as e:
    logger.warning(f"Could not import from consensus_mechanisms: {e}")
    ColonyConsensus = None
    ConsensusMethod = None
    VoteType = None
    ConsensusProposal = None

try:
    from .swarm_simulation import SimAgent, SwarmNetwork

    logger.debug("Imported SwarmNetwork and SimAgent from .swarm_simulation")
except ImportError as e:
    logger.warning(f"Could not import from swarm_simulation: {e}")
    SwarmNetwork = None
    SimAgent = None

try:
    from .tag_propagation import SymbolicReasoningColony

    logger.debug("Imported SymbolicReasoningColony from .tag_propagation")
except ImportError as e:
    logger.warning(f"Could not import SymbolicReasoningColony: {e}")
    SymbolicReasoningColony = None

__all__ = [
    "BaseColony",
    "ColonyConsensus",
    "ConsensusMethod",
    "ConsensusProposal",
    "CreativityColony",
    "EnhancedReasoningColony",
    "EthicsSwarmColony",
    "GovernanceColony",
    "GovernanceColonyEnhanced",
    "MemoryColony",
    "MemoryColonyEnhanced",
    "OracleColony",
    "ReasoningColony",
    "SimAgent",
    "SupervisorAgent",
    "SwarmNetwork",
    "SwarmSignalNetwork",
    "SymbolicReasoningColony",
    "TemporalColony",
    "TensorColonyOps",
    "VoteType",
]

# Filter out None values from __all__ if imports failed
__all__ = [name for name in __all__ if globals().get(name) is not None]

logger.info(f"colonies module initialized. Available components: {__all__}")
