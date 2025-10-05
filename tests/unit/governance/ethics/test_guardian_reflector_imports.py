# criticality: P1

from candidate.governance.ethics.guardian_reflector import (
    EthicsEngine,
    MemoryManager,
)


def _is_real(cls: type) -> bool:
    return cls.__module__ != "unittest.mock"


def test_core_components_are_real():
    assert _is_real(EthicsEngine)
    assert _is_real(MemoryManager)
