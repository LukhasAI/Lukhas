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
    from .governance_colony_enhanced import GovernanceColonyEnhanced

    logger.debug("Imported GovernanceColonyEnhanced from .governance_colony_enhanced")
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

try:
    from .memory_colony_enhanced import MemoryColonyEnhanced

    logger.debug("Imported MemoryColonyEnhanced from .memory_colony_enhanced")
except ImportError as e:
    logger.warning(f"Could not import MemoryColonyEnhanced: {e}")
    MemoryColonyEnhanced = None

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

__all__ = [
    "MemoryColony",
    "GovernanceColonyEnhanced",
    "BaseColony",
    "OracleColony",
    "ReasoningColony",
    "CreativityColony",
    "GovernanceColony",
    "MemoryColonyEnhanced",
    "SupervisorAgent",
    "TemporalColony",
    "TensorColonyOps",
    "EthicsSwarmColony",
]

# Filter out None values from __all__ if imports failed
__all__ = [name for name in __all__ if globals().get(name) is not None]

logger.info(f"colonies module initialized. Available components: {__all__}")
