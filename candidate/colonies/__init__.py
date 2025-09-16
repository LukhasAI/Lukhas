"""
LUKHAS AI Colony System
Distributed agent colonies for specialized processing
Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian

TODO[T4-AUDIT]:triage - Colony system implementation status unclear. Need integration assessment with actor system.
"""
import importlib
import logging
from dataclasses import dataclass
from typing import Any, Dict

import streamlit as st

__version__ = "1.0.0"
__triad__ = "⚛️🧠🛡️"

# Core colony interfaces
from . import (
    base,
    consciousness,
    creativity,
    governance,
    identity,
    memory,
    orchestrator,
    reasoning,
)

# Colony registry
from .base import ColonyRegistry, get_colony_registry

logger = logging.getLogger(__name__)

__all__ = [
    "ColonyRegistry",
    "base",
    "consciousness",
    "creativity",
    "get_colony_registry",
    "governance",
    "identity",
    "memory",
    "orchestrator",
    "reasoning",
]


def triad_sync():
    """Synchronize all colonies with Trinity Framework"""
    registry = get_colony_registry()

    sync_results = {}
    for colony_name, colony in registry.get_all_colonies().items():
        if hasattr(colony, "triad_sync"):
            sync_results[colony_name] = colony.triad_sync()
        else:
            sync_results[colony_name] = {"status": "no_triad_support"}

    return {
        "identity": "⚛️",
        "consciousness": "🧠",
        "guardian": "🛡️",
        "colony_sync": sync_results,
        "total_colonies": len(sync_results),
    }


@dataclass
class ColonyIntegrationReport:
    """Summary of the colony ↔ actor system integration state."""

    actor_system_available: bool
    colonies_registered: int
    missing_capabilities: list[str]
    details: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "actor_system_available": self.actor_system_available,
            "colonies_registered": self.colonies_registered,
            "missing_capabilities": self.missing_capabilities,
            "details": self.details,
        }


def assess_actor_system_integration() -> ColonyIntegrationReport:
    """Evaluate the current integration status with the actor system.

    The colony framework depends on the asynchronous actor runtime.  This
    helper inspects the registry, checks for the actor system bridge, and
    reports any missing capabilities.  The result is consumable by
    observability tooling while remaining import-safe in partial deployments.
    """

    # ΛTAG: colony_actor_integration
    details: dict[str, Any] = {}
    missing: list[str] = []

    try:
        actor_module = importlib.import_module("candidate.core.actor_system")
        actor_system = getattr(actor_module, "get_global_actor_system", None)
        actor_system_available = callable(actor_system)
        details["actor_module"] = actor_module.__name__
    except Exception as exc:  # pragma: no cover - diagnostic fallback
        logger.debug("Actor system import failed", exc_info=exc)
        actor_system_available = False
        missing.append("actor_system")
        details["error"] = str(exc)

    registry = get_colony_registry()
    colonies = registry.get_all_colonies()
    colony_details: dict[str, dict[str, Any]] = {}

    for colony_name, colony in colonies.items():
        capabilities = getattr(colony, "capabilities", [])
        has_actor_bridge = hasattr(colony, "actor_system")
        if not capabilities:
            missing.append(f"capabilities:{colony_name}")
        if not has_actor_bridge:
            missing.append(f"actor_bridge:{colony_name}")
        colony_details[colony_name] = {
            "capabilities": list(capabilities),
            "actor_bridge": has_actor_bridge,
        }

    details["colonies"] = colony_details

    return ColonyIntegrationReport(
        actor_system_available=actor_system_available,
        colonies_registered=len(colonies),
        missing_capabilities=sorted(set(missing)),
        details=details,
    )
