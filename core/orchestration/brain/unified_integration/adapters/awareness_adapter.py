"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: awareness_adapter.py
Advanced: awareness_adapter.py
Integration Date: 2025-05-31T07:55:29.981335
"""
import asyncio
import logging
from datetime import datetime, timezone

# Simple adapter for awareness system integration
from typing import Any, Optional

from ..unified_integration import MessageType, UnifiedIntegration

logger = logging.getLogger("awareness_adapter")


class AwarenessAdapter:
    """Adapter for awareness system integration with unified integration layer"""

    def __init__(self, integration: UnifiedIntegration):
        """Initialize awareness adapter

        Args:
            integration: Reference to integration layer
        """
        self.integration = integration
        self.component_id = "awareness"

        # Track system awareness state
        self.awareness_state = {
            "active": True,
            "focus_area": None,
            "attention_targets": [],
            "last_update": None,
        }

        # Awareness settings
        self.awareness_settings = {
            "continuous_monitoring": True,
            "emotional_awareness": True,
            "system_reflection": True,
            "adaptive_focus": True,
        }

        # Register with integration layer
        self.integration.register_component(self.component_id, self.handle_message)

        logger.info("Awareness adapter initialized")

    def handle_message(self, message: dict[str, Any]) -> None:
        """Handle incoming messages"""
        try:
            content = message["content"]
            action = content.get("action")

            if action == "update_awareness":
                self._handle_awareness_update(content)
            elif action == "focus_attention":
                self._handle_focus_request(content)
            elif action == "system_reflection":
                self._handle_reflection_request(content)

        except Exception as e:
            logger.error(f"Error handling message: {e}")

    async def update_awareness(
        self,
        state_data: dict[str, Any],
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Update system awareness state

        Args:
            state_data: New awareness state data
            context: Optional update context

        Returns:
            Dict with update results
        """
        self.awareness_state["last_update"] = datetime.now(timezone.utc).isoformat()

        return await self.integration.send_message(
            source=self.component_id,
            target="awareness_core",
            message_type=MessageType.STATE,
            content={
                "action": "update_awareness",
                "state_data": state_data,
                "context": context or {},
                "settings": self.awareness_settings,
            },
        )

    async def focus_attention(
        self,
        target: str,
        duration_seconds: float = 60.0,
        priority: str = "normal",
    ) -> dict[str, Any]:
        """Focus system attention on specific target

        Args:
            target: What to focus on
            duration_seconds: How long to maintain focus
            priority: Focus priority level

        Returns:
            Dict with focus results
        """
        self.awareness_state["focus_area"] = target
        self.awareness_state["attention_targets"].append(
            {
                "target": target,
                "priority": priority,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        return await self.integration.send_message(
            source=self.component_id,
            target="awareness_core",
            message_type=MessageType.COMMAND,
            content={
                "action": "focus_attention",
                "target": target,
                "duration_seconds": duration_seconds,
                "priority": priority,
                "settings": self.awareness_settings,
            },
        )

    async def reflect_on_system(
        self,
        reflection_targets: Optional[list[str]] = None,
        depth: str = "normal",
    ) -> dict[str, Any]:
        """Perform system self-reflection

        Args:
            reflection_targets: Optional specific targets
            depth: Reflection depth level

        Returns:
            Dict with reflection results
        """
        return await self.integration.send_message(
            source=self.component_id,
            target="awareness_core",
            message_type=MessageType.COMMAND,
            content={
                "action": "system_reflection",
                "targets": reflection_targets,
                "depth": depth,
                "settings": self.awareness_settings,
            },
        )

    def _handle_awareness_update(self, content: dict[str, Any]) -> None:
        """Handle awareness state update request"""
        state_data = content.get("state_data", {})
        context = content.get("context")

        logger.info("Processing awareness update...")
        asyncio.create_task(self.update_awareness(state_data, context))

    def _handle_focus_request(self, content: dict[str, Any]) -> None:
        """Handle attention focus request"""
        target = content.get("target")
        duration = content.get("duration_seconds", 60.0)
        priority = content.get("priority", "normal")

        if not target:
            logger.error("No focus target provided")
            return

        logger.info(f"Focusing attention on: {target}")
        asyncio.create_task(self.focus_attention(target, duration, priority))

    def _handle_reflection_request(self, content: dict[str, Any]) -> None:
        """Handle system reflection request"""
        targets = content.get("targets")
        depth = content.get("depth", "normal")

        logger.info("Starting system reflection...")
        asyncio.create_task(self.reflect_on_system(targets, depth))
