"""Memory identity structures and factory utilities."""

from __future__ import annotations

import copy
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict

from memory.metrics import compute_affect_delta, compute_drift

logger = logging.getLogger(__name__)


# ΛTAG: memory_identity
@dataclass
class MemoryIdentity:
    """Representation of an entity capable of holding memories."""

    identifier: str
    attributes: Dict[str, Any]


# ΛTAG: memory_identity_registry
class MemoryIdentityRegistry:
    """Registry maintaining identity telemetry for memory-aware systems."""

    def __init__(self) -> None:
        self._identities: dict[str, MemoryIdentity] = {}
        self._metrics: dict[str, dict[str, Any]] = {}

    def register(self, identity: MemoryIdentity) -> dict[str, Any]:
        """Register an identity and compute affect metrics."""

        affect_delta = compute_affect_delta(identity.attributes)
        previous_metrics = self._metrics.get(identity.identifier)
        previous_affect = None
        if previous_metrics:
            previous_affect = previous_metrics.get("affect_delta")

        drift_score = compute_drift(previous_affect, affect_delta)
        metrics = {
            "affect_delta": affect_delta,
            "driftScore": drift_score,
            "registered_at": datetime.now(timezone.utc).isoformat(),
        }

        self._identities[identity.identifier] = identity
        self._metrics[identity.identifier] = metrics

        logger.info(
            "MemoryIdentity_registered",
            extra={
                "identity": identity.identifier,
                "affect_delta": affect_delta,
                "driftScore": drift_score,
                "ΛTAG": "memory_identity_registry",
            },
        )
        return metrics

    def get_identity(self, identifier: str) -> MemoryIdentity | None:
        """Retrieve a registered identity if available."""

        return self._identities.get(identifier)

    def get_metrics(self, identifier: str) -> dict[str, Any] | None:
        """Retrieve telemetry metrics for a registered identity."""

        return self._metrics.get(identifier)


class MemoryIdentityFactory:
    """Factory for creating :class:`MemoryIdentity` objects."""

    def __init__(self, registry: MemoryIdentityRegistry | None = None) -> None:
        self.registry = registry or MemoryIdentityRegistry()

    # ΛTAG: memory_identity_factory
    def create(self, identifier: str, attributes: Dict[str, Any]) -> MemoryIdentity:
        """Create a new :class:`MemoryIdentity` instance.

        Args:
            identifier: Unique identity key.
            attributes: Supplementary attribute mapping.

        Returns:
            A populated :class:`MemoryIdentity` enriched with telemetry metrics.
        """

        self._validate_inputs(identifier, attributes)
        safe_attributes: Dict[str, Any] = copy.deepcopy(attributes)

        identity = MemoryIdentity(identifier=identifier, attributes=safe_attributes)
        metrics = self.registry.register(identity)

        telemetry = identity.attributes.setdefault("telemetry", {})
        telemetry.update(metrics)

        logger.debug(
            "MemoryIdentity_created",
            extra={
                "identity": identifier,
                "affect_delta": metrics["affect_delta"],
                "driftScore": metrics["driftScore"],
                "ΛTAG": "memory_identity",
            },
        )
        return identity

    def _validate_inputs(self, identifier: str, attributes: Dict[str, Any]) -> None:
        """Validate identity creation inputs."""

        if not isinstance(identifier, str) or not identifier.strip():
            raise ValueError("identifier must be a non-empty string")
        if not isinstance(attributes, dict):
            raise TypeError("attributes must be a dictionary")


__all__ = ["MemoryIdentity", "MemoryIdentityFactory", "MemoryIdentityRegistry", "logger"]
