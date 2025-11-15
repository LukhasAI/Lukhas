"""Bridge module for memory.contracts → labs.memory.contracts"""
from __future__ import annotations

from _bridgeutils import bridge_from_candidates, safe_guard

_CANDIDATES = (
    "lukhas_website.memory.contracts",
    "candidate.memory.contracts",
    "labs.memory.contracts",
)
__all__, _exports = bridge_from_candidates(*_CANDIDATES)
globals().update(_exports)

# Ensure AGIMemoryProtocol is always available
if "AGIMemoryProtocol" not in globals():
    from typing import Any, Optional, Protocol, runtime_checkable

    @runtime_checkable
    class AGIMemoryProtocol(Protocol):
        """Protocol for AGI memory implementations."""
        def put(self, key: str, value: Any) -> None: ...
        def get(self, key: str) -> Any: ...
        def fold_open(self, *, parent_id: Optional[str] = None) -> str: ...
        def fold_append(self, fold_id: str, item: Any) -> None: ...
        def fold_close(self, fold_id: str) -> dict: ...

    globals()["AGIMemoryProtocol"] = AGIMemoryProtocol
    if "AGIMemoryProtocol" not in __all__:
        __all__.append("AGIMemoryProtocol")

# Add stubs for commonly expected symbols if not found
if "ContractManager" not in globals():
    class ContractManager:
        """Stub ContractManager class."""
        pass
    globals()["ContractManager"] = ContractManager
    if "ContractManager" not in __all__:
        __all__.append("ContractManager")

if "MemoryContract" not in globals():
    class MemoryContract:
        """Stub MemoryContract class."""
        pass
    globals()["MemoryContract"] = MemoryContract
    if "MemoryContract" not in __all__:
        __all__.append("MemoryContract")

if "create_memory_contract" not in globals():
    def create_memory_contract(*args, **kwargs):
        """Stub create_memory_contract function."""
        return MemoryContract()
    globals()["create_memory_contract"] = create_memory_contract
    if "create_memory_contract" not in __all__:
        __all__.append("create_memory_contract")

safe_guard(__name__, __all__)
