"""Guardian serialization for LUKHAS governance system."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


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

    _reg: dict[str, GuardianSerializer] = {}

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
    "GuardianSerializer",
    "GuardianEnvelopeSerializer",
    "GuardianSerializerRegistry",
    "deserialize_guardian",
]
