"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: legacy_adapter.py
Advanced: legacy_adapter.py
Integration Date: 2025-05-31T07:55:29.984497
"""
import uuid

from typing import Any, Callable, Optional
import logging
import time

"""
LegacyAdapter - Compatibility layer for existing LUKHAS components

Provides adapters and wrappers to help existing components communicate with
the new UniversalIntegrationLayer while maintaining all functionality.
"""


logger = logging.getLogger("LegacyAdapter")


class LegacyComponentAdapter:
    """Adapter to help legacy components work with new integration layer"""

    def __init__(
        self,
        integration_layer: UniversalIntegrationLayer,
        component_id: str,
        component_type: ComponentType,
    ):
        """Initialize the adapter

        Args:
            integration_layer: Reference to integration layer
            component_id: ID of the legacy component
            component_type: Type of the component
        """
        self.integration = integration_layer
        self.component_id = component_id
        self.component_type = component_type

        # Register with integration layer
        self.integration.register_component(
            component_id, component_type, self._handle_message
        )

        logger.info(f"Legacy adapter initialized for {component_id}")

    def adapt_legacy_message(
        self, message: dict[str, Any], target: Optional[str] = None
    ) -> Message:
        """Convert legacy message format to new standard

        Args:
            message: Legacy message dictionary
            target: Optional target component

        Returns:
            Message: Standardized message object
        """
        # Determine message type
        if "type" in message:
            msg_type = MessageType(message["type"])
        else:
            msg_type = MessageType.COMMAND

        # Extract or create metadata
        metadata = message.get("metadata", {})
        metadata["legacy"] = True

        # Create standardized message
        return Message(
            id=message.get("id", str(uuid.uuid4())),
            type=msg_type,
            source=self.component_id,
            target=target,
            content=message.get("content", message),
            metadata=metadata,
            timestamp=time.time(),
        )

    async def send_message(
        self, message: dict[str, Any], target: Optional[str] = None
    ) -> str:
        """Send a legacy message through the new integration layer

        Args:
            message: Legacy message dictionary
            target: Optional target component

        Returns:
            str: Message ID
        """
        # Convert to new format
        new_message = self.adapt_legacy_message(message, target)

        # Publish through integration layer
        return await self.integration.publish(
            message_type=new_message.type,
            content=new_message.content,
            source=self.component_id,
            target=target,
            metadata=new_message.metadata,
        )

    def register_legacy_handler(self, handler: Callable) -> None:
        """Register a legacy message handler

        Args:
            handler: Legacy message handling function
        """
        self.legacy_handler = handler

    def _handle_message(self, message: Message) -> None:
        """Handle messages from integration layer

        Args:
            message: Standardized message object
        """
        if hasattr(self, "legacy_handler"):
            # Convert to legacy format
            legacy_message = {
                "type": message.type.value,
                "content": message.content,
                "source": message.source,
                "metadata": message.metadata,
            }

            # Call legacy handler
            try:
                self.legacy_handler(legacy_message)
            except Exception as e:
                logger.error(f"Error in legacy handler: {e}")
        else:
            logger.warning("No legacy handler registered")


class LUKHASCoreAdapter(LegacyComponentAdapter):
    """Specialized adapter for Lukhas Core integration"""

    def __init__(self, integration_layer: UniversalIntegrationLayer):
        """Initialize Lukhas Core adapter"""
        super().__init__(integration_layer, "lukhas_core", ComponentType.CORE)

        # Subscribe to core message types
        self.integration.subscribe(
            self.component_id, MessageType.COMMAND, self._handle_message
        )
        self.integration.subscribe(
            self.component_id, MessageType.EVENT, self._handle_message
        )


class BrainIntegrationAdapter(LegacyComponentAdapter):
    """Specialized adapter for Brain Integration system"""

    def __init__(self, integration_layer: UniversalIntegrationLayer):
        """Initialize Brain Integration adapter"""
        super().__init__(integration_layer, "brain_integration", ComponentType.AGI)

        # Subscribe to relevant message types
        self.integration.subscribe(
            self.component_id, MessageType.COMMAND, self._handle_message
        )

    async def process_brain_message(
        self,
        message: dict[str, Any],
        metadata: Optional[dict[str, Any]] = None,
    ) -> str:
        """Process a brain-specific message

        Args:
            message: Brain message dictionary
            metadata: Optional metadata

        Returns:
            str: Message ID
        """
        return await self.send_message(
            message, metadata=metadata or {"subsystem": "brain"}
        )