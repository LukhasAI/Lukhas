# lukhas/core/interfaces.py
"""
Interfaces and light ABCs for pluggable subsystems.

T4 defaults:
- Small, composable, explicit contracts
- No import side-effects
- Pure typing + ABCs (runtime_checkable where useful)

Usage (example):
    from lukhas.core.interfaces import CognitiveNodeBase

    class EchoNode(CognitiveNodeBase):
        name = "echo"
        AUTOINIT = True

        @classmethod
        def from_env(cls):
            return cls()

        async def process(self, ctx):
            return {"echo": ctx.get("input", "")}
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Mapping, Protocol, runtime_checkable


class CognitiveNodeBase(ABC):
    """Minimal ABC for dynamic discovery and execution."""
    name: str = "unnamed"
    AUTOINIT: bool = False  # loader respects this

    @classmethod
    def from_env(cls) -> "CognitiveNodeBase":
        """Construct from environment (override in impls)."""
        return cls()

    @abstractmethod
    async def process(self, ctx: Mapping[str, Any]) -> Mapping[str, Any]:
        """Do work and return output dict."""
        raise NotImplementedError


@runtime_checkable
class Memory(Protocol):
    def get(self, key: str) -> Any: ...
    def set(self, key: str, value: Any) -> None: ...


@runtime_checkable
class Guardian(Protocol):
    def band_for(self, ctx: Mapping[str, Any]) -> str: ...
    def warn(self, code: str, **fields: Any) -> None: ...