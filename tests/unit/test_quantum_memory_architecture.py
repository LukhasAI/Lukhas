from products.infrastructure.trace.quantum_implementations.QuantumMemoryArchitecture import (
    QIAssociativeMemoryBank,
)


def test_quantum_memory_bank_register_size() -> None:
    bank = QIAssociativeMemoryBank(capacity_qubits=3)
    assert len(bank.memory_register) == 3
