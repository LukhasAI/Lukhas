"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: dream_adapter.py
Advanced: dream_adapter.py
Integration Date: 2025-05-31T07:55:29.982795
"""

import asyncio
import logging
from datetime import datetime

# Simple adapter for dream engine integration
from typing import Any

from ..unified_integration import MessageType, UnifiedIntegration

logger = logging.getLogger("dream_adapter")


class DreamEngineAdapter:
    """Adapter for dream engine integration"""

    def __init__(self, integration: UnifiedIntegration):
        """Initialize dream engine adapter

        Args:
            integration: Reference to integration layer
        """
        self.integration = integration
        self.component_id = "dream_engine"
        self.dream_state = "idle"  # idle, dreaming
        self.current_dream_cycle = {}

        # Register with integration layer
        self.integration.register_component(self.component_id, self.handle_message)

        logger.info("Dream Engine adapter initialized")

    def handle_message(self, message: dict[str, Any]) -> None:
        """Handle incoming messages"""
        try:
            content = message["content"]
            action = content.get("action")

            if action == "start_dream_cycle":
                self._handle_start_cycle(content)
            elif action == "stop_dream_cycle":
                self._handle_stop_cycle(content)
            elif action == "get_dream_state":
                self._handle_get_state(content)

        except Exception as e:
            logger.error(f"Error handling message: {e}")

    async def start_dream_cycle(self, duration_minutes: int = 10) -> None:
        """Start a dream cycle

        Args:
            duration_minutes: Duration in minutes
        """
        await self.integration.send_message(
            source=self.component_id,
            target="dream_reflection",
            message_type=MessageType.COMMAND,
            content={
                "action": "start_dream_cycle",
                "duration_minutes": duration_minutes,
            },
        )

    async def stop_dream_cycle(self) -> None:
        """Stop the current dream cycle"""
        await self.integration.send_message(
            source=self.component_id,
            target="dream_reflection",
            message_type=MessageType.COMMAND,
            content={"action": "stop_dream_cycle"},
        )

    def _handle_start_cycle(self, content: dict[str, Any]) -> None:
        """Handle start cycle request"""
        logger.info(f"Starting dream cycle: {content}")
        duration = content.get("duration_minutes", 10)
        self.dream_state = "dreaming"
        self.current_dream_cycle = {
            "start_time": datetime.now().isoformat(),
            "duration_minutes": duration,
        }
        asyncio.create_task(self.start_dream_cycle(duration))

    def _handle_stop_cycle(self, content: dict[str, Any]) -> None:
        """Handle stop cycle request"""
        logger.info("Stopping dream cycle")
        self.dream_state = "idle"
        self.current_dream_cycle = {}
        asyncio.create_task(self.stop_dream_cycle())

    def _handle_get_state(self, content: dict[str, Any]) -> None:
        """Handle get state request"""
        state_info = {
            "state": self.dream_state,
            "cycle_info": self.current_dream_cycle,
        }
        requester = content.get("source_component", "unknown")

        async def send_state():
            await self.integration.send_message(
                source=self.component_id,
                target=requester,
                message_type=MessageType.RESPONSE,
                content={"action": "dream_state_response", "data": state_info},
            )

        asyncio.create_task(send_state())
        logger.info(f"Sent dream state to {requester}")

    def get_state(self) -> dict[str, Any]:
        """Returns the current state of the dream engine."""
        return {
            "state": self.dream_state,
            "cycle_info": self.current_dream_cycle,
        }
