"""
DEPRECATED: Legacy Module Location
===================================

This module will be relocated in a future release.

**Deprecation Notice**: This import path is deprecated as of 2025-11-12.

The implementation will be moved to the canonical location:
    from lukhas_website.lukhas.governance.guardian.serializers import GuardianSerializer

Or use the new bridge pattern:
    from governance.guardian.serializers import GuardianSerializer

Migration Path:
    OLD: from governance.guardian_serializers import GuardianSerializer
    NEW: from lukhas_website.lukhas.governance.guardian.serializers import GuardianSerializer

This module will be relocated in Phase 4 (2025-Q1).

Legacy Implementation
=====================
Guardian serialization for LUKHAS governance system (temporary location).
"""
from __future__ import annotations

import warnings

warnings.warn(
    "governance.guardian_serializers is deprecated. "
    "Use lukhas_website.lukhas.governance.guardian.serializers or governance.guardian.serializers instead.",
    DeprecationWarning,
    stacklevel=2,
)

from dataclasses import dataclass
from typing import Any, ClassVar, Protocol


class GuardianSerializer(Protocol):
    """Protocol for guardian object serializers."""

    def serialize(self, obj: Any) -> dict:
        """Serialize guardian object to dictionary."""
        ...

    def deserialize(self, data: dict) -> Any:
        """Deserialize dictionary to guardian object."""
        ...


@dataclass
class GuardianEnvelopeSerializer:
    """Serializer for guardian envelope format with versioning."""

    version: str = "1"

    def wrap(self, payload: dict) -> dict:
        """Wrap payload in versioned envelope."""
        return {"v": self.version, "payload": payload}

    def unwrap(self, envelope: dict) -> dict:
        """Unwrap versioned envelope to get payload."""
        return envelope.get("payload", {})


class GuardianSerializerRegistry:
    """Registry for guardian serializers by name."""

    _reg: ClassVar[dict[str, GuardianSerializer]] = {}  # TODO[T4-ISSUE]: {"code":"RUF012","ticket":"GH-1031","owner":"consciousness-team","status":"planned","reason":"Mutable class attribute needs ClassVar annotation for type safety","estimate":"15m","priority":"medium","dependencies":"typing imports","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_governance_guardian_serializers_py_L38"}

    @classmethod
    def register(cls, name: str, ser: GuardianSerializer) -> None:
        """Register a serializer under a name."""
        cls._reg[name] = ser

    @classmethod
    def get(cls, name: str) -> GuardianSerializer:
        """Get a registered serializer by name."""
        return cls._reg[name]


def deserialize_guardian(envelope: dict) -> Any:
    """Deserialize guardian object from envelope format.

    Minimal default implementation - tests can inject custom registry entries.
    """
    return envelope.get("payload")


__all__ = [
    "GuardianEnvelopeSerializer",
    "GuardianSerializer",
    "GuardianSerializerRegistry",
    "deserialize_guardian",
]
