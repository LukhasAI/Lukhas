"""
VIVOX.QREADY - Quantum Readiness Interface
Prepares VIVOX for future quantum computing substrates
"""

from .coherence.qsync_events import (
    EntanglementBridge,
    QSyncEvent,
    QuantumSynchronizer,
    SyncType,
)
from .collapse.moral_superposition import (
    EthicalDimension,
    EthicalQuantumState,
    MoralSuperposition,
    SuperpositionPath,
    SuperpositionResolver,
)
from .core.quantum_substrate import (
    QuantumEnvironment,
    QuantumNoiseType,
    QuantumState,
    QuantumStateType,
    QuantumSubstrate,
)
from .core.qubit_collapse import (
    CollapseField,
    CollapseType,
    ProbabilisticConvergence,
    QubitCollapseEngine,
)
from .integration.vivox_bridge import QuantumBridgeEvent, VIVOXQuantumBridge


# Main factory function
def create_quantum_readiness_system(
    vivox_interfaces: dict = None, quantum_config: dict = None
) -> QuantumSubstrate:
    """
    Create a complete VIVOX.QREADY system

    Args:
        vivox_interfaces: Connections to other VIVOX modules
        quantum_config: Quantum-specific configuration

    Returns:
        Configured QuantumSubstrate instance
    """
    return QuantumSubstrate(
        interfaces=vivox_interfaces or {}, config=quantum_config or {}
    )


__all__ = [
    # Core
    "QuantumSubstrate",
    "QuantumState",
    "QuantumEnvironment",
    "QuantumStateType",
    "QuantumNoiseType",
    # Collapse
    "QubitCollapseEngine",
    "CollapseField",
    "ProbabilisticConvergence",
    "CollapseType",
    # Coherence
    "QSyncEvent",
    "QuantumSynchronizer",
    "EntanglementBridge",
    "SyncType",
    # Superposition
    "MoralSuperposition",
    "EthicalQuantumState",
    "EthicalDimension",
    "SuperpositionPath",
    "SuperpositionResolver",
    # Integration
    "VIVOXQuantumBridge",
    "QuantumBridgeEvent",
    # Factory
    "create_quantum_readiness_system",
]
