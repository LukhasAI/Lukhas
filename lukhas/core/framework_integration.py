"""Framework integration manager for orchestrating constellation adapters."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, Mapping, MutableMapping, Optional

try:  # pragma: no cover - optional dependency
    from lukhas.consciousness.constellation_integration import (  # type: ignore
        ConstellationFrameworkIntegrator,
        ConstellationIntegrationConfig,
    )
except Exception:  # pragma: no cover - graceful degradation when dependency missing
    ConstellationFrameworkIntegrator = None  # type: ignore[assignment]
    ConstellationIntegrationConfig = None  # type: ignore[assignment]

try:  # pragma: no cover - optional dependency
    from lukhas.core.common.exceptions import LukhasException
except Exception:  # pragma: no cover - fallback when core exceptions are unavailable
    LukhasException = Exception  # type: ignore

logger = logging.getLogger(__name__)

Payload = Mapping[str, Any]
PreparedPayload = Mapping[str, Any]
PayloadPreparer = Callable[[Payload], Awaitable[PreparedPayload] | PreparedPayload]


async def _ensure_awaitable(callable_: PayloadPreparer, payload: Payload) -> PreparedPayload:
    """Execute a payload preparer that may be sync or async and return its payload."""

    result = callable_(payload)
    if asyncio.iscoroutine(result) or isinstance(result, asyncio.Future):
        return await result  # type: ignore[return-value]
    return result  # type: ignore[return-value]


@dataclass(frozen=True)
class ModuleAdapter:
    """Adapter definition for a module participating in the framework integration."""

    module_type: str
    triad_aspect: str
    prepare_payload: PayloadPreparer


def _default_module_adapters() -> Dict[str, ModuleAdapter]:
    async def _identity_payload(payload: Payload) -> PreparedPayload:
        return {
            **payload,
            "identity_integration": True,
            "required_scopes": payload.get("required_scopes", ["profile", "guardian"]),
        }

    async def _consciousness_payload(payload: Payload) -> PreparedPayload:
        return {
            **payload,
            "consciousness_integration": True,
            "dream_bridge_ready": payload.get("dream_bridge_ready", False),
        }

    async def _guardian_payload(payload: Payload) -> PreparedPayload:
        return {
            **payload,
            "guardian_integration": True,
            "risk_threshold": payload.get("risk_threshold", 0.15),
        }

    async def _memory_payload(payload: Payload) -> PreparedPayload:
        return {
            **payload,
            "memory_integration": True,
            "retention_policy": payload.get("retention_policy", "adaptive"),
        }

    return {
        "identity": ModuleAdapter("identity", "Λ", _identity_payload),
        "consciousness": ModuleAdapter("consciousness", "Ψ", _consciousness_payload),
        "guardian": ModuleAdapter("guardian", "Ω", _guardian_payload),
        "memory": ModuleAdapter("memory", "Μ", _memory_payload),
    }


@dataclass
class FrameworkIntegrationManager:
    """Coordinate constellation framework integrations across Lukhas subsystems."""

    config: Optional[ConstellationIntegrationConfig] = None
    module_adapters: MutableMapping[str, ModuleAdapter] = field(default_factory=_default_module_adapters)

    def __post_init__(self) -> None:
        self.registered_modules: Dict[str, ModuleAdapter] = {}
        self.trinity_integrator: Optional[ConstellationFrameworkIntegrator] = None
        self.is_active = False

        if ConstellationFrameworkIntegrator is None:
            logger.warning(
                "ConstellationFrameworkIntegrator unavailable; FrameworkIntegrationManager will run in inactive mode."
            )
            return

        try:
            self.trinity_integrator = ConstellationFrameworkIntegrator(self.config)  # type: ignore[call-arg]
            self.is_active = True
        except Exception as exc:  # pragma: no cover - initialization failure should be rare
            logger.exception("Failed to initialize ConstellationFrameworkIntegrator: %s", exc)
            raise LukhasException("Unable to initialize framework integrations") from exc

    def get_module_adapter(self, module_name: str) -> ModuleAdapter:
        if module_name in self.module_adapters:
            return self.module_adapters[module_name]
        if module_name in self.registered_modules:
            return self.registered_modules[module_name]
        raise KeyError(f"Unknown module adapter requested: {module_name}")

    async def register_module(
        self, module_name: str, context: Optional[Payload], adapter: ModuleAdapter
    ) -> bool:
        if not self.is_active:
            logger.warning("Cannot register module: FrameworkIntegrationManager is inactive.")
            return False

        if module_name in self.module_adapters or module_name in self.registered_modules:
            logger.debug("Overwriting existing module adapter for module '%s'", module_name)

        if context:
            await _ensure_awaitable(adapter.prepare_payload, context)

        self.registered_modules[module_name] = adapter
        return True

    async def initialize_integrations(self) -> bool:
        if not self.is_active or self.trinity_integrator is None:
            logger.error("Cannot initialize integrations: FrameworkIntegrationManager is inactive.")
            return False

        initialize_fn = getattr(self.trinity_integrator, "initialize_constellation_frameworks", None)
        if initialize_fn is None:
            logger.error("Constellation integrator does not expose initialize_constellation_frameworks().")
            return False

        result = initialize_fn()
        if asyncio.iscoroutine(result) or isinstance(result, asyncio.Future):
            result = await result

        return bool(result)


__all__ = [
    "FrameworkIntegrationManager",
    "ModuleAdapter",
]
