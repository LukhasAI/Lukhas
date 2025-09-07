"""
VIVOX.QREADY - Quantum Readiness Interface
Prepares VIVOX for future quantum computing substrates
"""
from consciousness.qi import qi
import streamlit as st

from typing import Optional

from .coherence.qsync_events import (
    EntanglementBridge,
    QISynchronizer,
    QSyncEvent,
    SyncType,
)
from .collapse.moral_superposition import (
    EthicalDimension,
    EthicalQIState,
    MoralSuperposition,
    SuperpositionPath,
    SuperpositionResolver,
)
from .core.qi_substrate import (
    QIEnvironment,
    QINoiseType,
    QIState,
    QIStateType,
    QISubstrate,
)
from .core.qubit_collapse import (
    CollapseField,
    CollapseType,
    ProbabilisticConvergence,
    QubitCollapseEngine,
)
from .integration.vivox_bridge import QIBridgeEvent, VIVOXQIBridge


# Main factory function
def create_quantum_readiness_system(
    vivox_interfaces: Optional[dict] = None, qi_config: Optional[dict] = None
) -> QISubstrate:
    """
    Create a complete VIVOX.QREADY system

    Args:
        vivox_interfaces: Connections to other VIVOX modules
        qi_config: Quantum-specific configuration

    Returns:
        Configured QISubstrate instance
    """
    return QISubstrate(interfaces=vivox_interfaces or {}, config=qi_config or {})


__all__ = [
    # Core
    "QISubstrate",
    "QIState",
    "QIEnvironment",
    "QIStateType",
    "QINoiseType",
    # Collapse
    "QubitCollapseEngine",
    "CollapseField",
    "ProbabilisticConvergence",
    "CollapseType",
    # Coherence
    "QSyncEvent",
    "QISynchronizer",
    "EntanglementBridge",
    "SyncType",
    # Superposition
    "MoralSuperposition",
    "EthicalQIState",
    "EthicalDimension",
    "SuperpositionPath",
    "SuperpositionResolver",
    # Integration
    "VIVOXQIBridge",
    "QIBridgeEvent",
    # Factory
    "create_quantum_readiness_system",
]
