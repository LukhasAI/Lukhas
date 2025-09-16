import sys
from pathlib import Path

import numpy as np
import pytest

path_obj = Path(__file__).resolve()
tests_unit_path = str(path_obj.parents[2])
if tests_unit_path in sys.path:
    sys.path.remove(tests_unit_path)

sys.path.insert(0, str(path_obj.parents[4]))

from products.infrastructure.trace.quantum_implementations.QuantumMemoryArchitecture import (
    QIAssociativeMemoryBank,
    QuantumQuery,
    QuantumState,
)


@pytest.mark.asyncio
async def test_quantum_memory_recall_matches_associations():
    bank = QIAssociativeMemoryBank(capacity_qubits=3)
    state = QuantumState(amplitudes=np.array([1.0, 0.0]))

    await bank.store_quantum_state("memory-alpha", state, ["dream", "ethics"])

    query = QuantumQuery(associations=("dream", "ethics"))
    memories = await bank.quantum_associative_recall(query)

    assert memories, "Expected at least one memory to be recalled"
    memory = memories[0]
    assert memory.memory_id == "memory-alpha"
    assert pytest.approx(1.0) == memory.confidence
    assert set(memory.associations) == {"dream", "ethics"}
    assert len(memory.collapse_hash) == len(bank.memory_register)
    assert bank.decoherence_mitigator._stabilization_events  # noqa: SLF001


@pytest.mark.asyncio
async def test_quantum_memory_recall_respects_min_confidence_threshold():
    bank = QIAssociativeMemoryBank(capacity_qubits=2)
    state = QuantumState(amplitudes=np.array([0.6, 0.8]))
    await bank.store_quantum_state("memory-beta", state, ["guardian"])

    query = QuantumQuery(associations=("guardian", "ethics"), min_confidence=0.6)
    memories = await bank.quantum_associative_recall(query)

    assert memories == []
