"""Legacy adapter that bridges the unified integration layer with legacy components."""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any, Callable

from ..unified_integration import (
    ComponentType,
    Message,
    MessageType,
    UniversalIntegrationLayer,
)

logger = logging.getLogger("LegacyAdapter")


class LegacyComponentAdapter:
    """Adapter to help legacy components interact with the integration layer."""

    def __init__(
        self,
        integration_layer: UniversalIntegrationLayer,
        component_id: str,
        component_type: ComponentType = ComponentType.LEGACY,
    ) -> None:
        self.integration = integration_layer
        self.component_id = component_id
        self.component_type = component_type
        self.legacy_handler: Callable[[dict[str, Any]], None] | None = None

        # Register with integration layer using the legacy component type.
        self.integration.register_component(
            component_id,
            component_type,
            self._handle_message,
        )

        logger.info("Legacy adapter initialized for component '%s'", component_id)

    def adapt_legacy_message(
        self,
        message: dict[str, Any],
        target: str | None = None,
    ) -> Message:
        """Normalize a legacy-style message to the integration format."""

        metadata = dict(message.get("metadata", {}))
        metadata.setdefault("legacy", True)

        msg_type = MessageType.from_value(message.get("type"))
        resolved_target = target or message.get("target")
        content = message.get("content", message)

        return Message(
            id=message.get("id", str(uuid.uuid4())),
            type=msg_type,
            source=self.component_id,
            target=resolved_target,
            content=content,
            metadata=metadata,
            timestamp=time.time(),
        )

    async def send_message(
        self,
        message: dict[str, Any],
        target: str | None = None,
    ) -> str:
        """Send a legacy message through the integration layer."""

        new_message = self.adapt_legacy_message(message, target)

        return await self.integration.publish(
            message_type=new_message.type,
            content=new_message.content,
            source=new_message.source,
            target=new_message.target,
            metadata=new_message.metadata,
            message_id=new_message.id,
        )

    def register_legacy_handler(self, handler: Callable[[dict[str, Any]], None]) -> None:
        """Register a handler that should receive normalized messages."""

        self.legacy_handler = handler

    def _handle_message(self, message: Message) -> None:
        """Dispatch integration messages to the legacy handler if present."""

        if self.legacy_handler is None:
            logger.debug("No legacy handler registered for '%s'", self.component_id)
            return

        legacy_message = {
            "type": message.type.value,
            "content": message.content,
            "source": message.source,
            "metadata": message.metadata,
        }

        try:
            self.legacy_handler(legacy_message)
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.error("Error in legacy handler for '%s': %s", self.component_id, exc)
