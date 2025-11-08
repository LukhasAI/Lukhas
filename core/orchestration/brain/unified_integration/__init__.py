"""Unified integration primitives for brain orchestration adapters."""
from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Basic message categories supported by the integration layer."""

    COMMAND = "command"
    EVENT = "event"
    STATE = "state"
    NOTIFICATION = "notification"

    @classmethod
    def from_value(cls, value: str | None) -> MessageType:
        """Return the enum member matching ``value`` (case-insensitive)."""

        if value is None:
            return cls.EVENT
        try:
            return cls(value.lower())
        except ValueError:
            logger.debug("Unknown message type '%s', defaulting to EVENT", value)
            return cls.EVENT


class ComponentType(Enum):
    """Logical component groupings used for adapter registration."""

    ADAPTER = "adapter"
    LEGACY = "legacy"
    MODERN = "modern"


@dataclass
class Message:
    """Normalized message exchanged across integration adapters."""

    id: str
    type: MessageType
    source: str
    target: str | None
    content: Any
    metadata: dict[str, Any]
    timestamp: float

    def to_dict(self) -> dict[str, Any]:
        """Serialize message to a dictionary for logging or tests."""

        return {
            "id": self.id,
            "type": self.type.value,
            "source": self.source,
            "target": self.target,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }


class UnifiedIntegration:
    """Minimal integration bus used by the adapter stubs.

    The implementation keeps a registry of component handlers so unit tests can
    exercise registration and message dispatch without requiring the full
    production orchestration fabric.
    """

    def __init__(self) -> None:
        self._handlers: dict[str, Callable[[Message], None]] = {}
        self._component_types: dict[str, ComponentType] = {}
        self._message_history: list[Message] = []

    def register_component(
        self,
        component_id: str,
        component_type_or_handler: ComponentType | Callable[[Message], None],
        handler: Callable[[Message], None] | None = None,
    ) -> None:
        """Register a component handler.

        Supports both ``(component_id, handler)`` and
        ``(component_id, component_type, handler)`` call styles.
        """

        if handler is None:
            component_type = ComponentType.MODERN
            resolved_handler = component_type_or_handler  # type: ignore[assignment]
        else:
            component_type = (
                component_type_or_handler
                if isinstance(component_type_or_handler, ComponentType)
                else ComponentType.MODERN
            )
            resolved_handler = handler

        if not callable(resolved_handler):
            raise TypeError("Handler must be callable")

        self._handlers[component_id] = resolved_handler
        self._component_types[component_id] = component_type
        logger.debug("Registered component '%s' (%s)", component_id, component_type.value)

    async def publish(
        self,
        *,
        message_type: MessageType,
        content: Any,
        source: str,
        target: str | None = None,
        metadata: dict[str, Any | None] = None,
        message_id: str | None = None,
    ) -> str:
        """Publish a message to the bus and invoke a target handler if present."""

        msg = Message(
            id=message_id or str(uuid.uuid4()),
            type=message_type,
            source=source,
            target=target,
            content=content,
            metadata=dict(metadata or {}),
            timestamp=time.time(),
        )
        self._message_history.append(msg)

        if target and target in self._handlers:
            handler = self._handlers[target]
            try:
                handler(msg)
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.exception("Handler for '%s' failed: %s", target, exc)

        return msg.id

    async def send_message(
        self,
        *,
        source: str,
        target: str | None,
        message_type: MessageType,
        content: Any,
        metadata: dict[str, Any | None] = None,
    ) -> dict[str, Any]:
        """Send a message and return a lightweight delivery receipt."""

        message_id = await self.publish(
            message_type=message_type,
            content=content,
            source=source,
            target=target,
            metadata=metadata,
        )
        delivered = target in self._handlers if target else False
        return {"message_id": message_id, "delivered": delivered}

    @property
    def message_history(self) -> list[Message]:
        """Expose recorded messages for debugging and tests."""

        return list(self._message_history)


class UniversalIntegrationLayer(UnifiedIntegration):
    """Concrete integration layer used by the legacy adapter stubs."""

    pass


__all__ = [
    "ComponentType",
    "Message",
    "MessageType",
    "UnifiedIntegration",
    "UniversalIntegrationLayer",
]
