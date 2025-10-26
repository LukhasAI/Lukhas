"""Core governance modules for LUKHAS."""

from importlib import import_module
from typing import TYPE_CHECKING, Any

__all__ = [
    "examples",
    "guardian_system_integration",
]

if TYPE_CHECKING:  # pragma: no cover - static type support
    from core.governance import examples as examples
    from core.governance import guardian_system_integration as guardian_system_integration


def __getattr__(name: str) -> Any:
    """Lazily import governance submodules to avoid heavy dependencies."""

    if name == "guardian_system_integration":
        module = import_module("core.governance.guardian_system_integration")
        globals()[name] = module
        return module
    if name == "examples":
        module = import_module("core.governance.examples")
        globals()[name] = module
        return module
    raise AttributeError(f"module 'core.governance' has no attribute {name!r}")
