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
from typing import Any, Mapping, Optional, Protocol, runtime_checkable


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


@runtime_checkable
class ICognitiveNode(Protocol):
    """Protocol describing pluggable pipeline nodes."""

    name: str

    async def process(self, ctx: Mapping[str, Any]) -> Mapping[str, Any]: ...

    async def cancel(self, reason: Optional[str] = None) -> None: ...  # # ΛTAG: pipeline_interface

    async def health_check(self) -> Mapping[str, Any]: ...


@runtime_checkable
class CoreInterface(Protocol):
    """Base protocol for core system components - T4 architecture compliance"""

    def get_health_status(self) -> Mapping[str, Any]: ...


class ServiceInterface(ABC):
    """Abstract base class for service implementations"""

    @abstractmethod
    def get_health_status(self) -> dict[str, Any]:
        """Return health status of the service"""
        raise NotImplementedError
