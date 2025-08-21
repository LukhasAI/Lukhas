"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: brain_adapter.py
Advanced: brain_adapter.py
Integration Date: 2025-05-31T07:55:29.988109
"""

import asyncio
import logging
from datetime import datetime

# Simple adapter for brain integration
from typing import Any, Optional

from ..unified_integration import MessageType, UnifiedIntegration

logger = logging.getLogger("brain_adapter")


class BrainAdapter:
    """Adapter for brain integration with the unified integration layer"""

    def __init__(self, integration: UnifiedIntegration):
        """Initialize brain adapter

        Args:
            integration: Reference to integration layer
        """
        self.integration = integration
        self.component_id = "brain"

        # Track active cognitive states
        self.cognitive_states = {
            "active": False,
            "processing": False,
            "last_activity": None,
            "current_task": None,
        }

        # Memory integration settings
        self.memory_settings = {
            "consolidation_enabled": True,
            "pattern_recognition": True,
            "emotional_integration": True,
        }

        # Register with integration layer
        self.integration.register_component(self.component_id, self.handle_message)

        logger.info("Brain adapter initialized")

    def handle_message(self, message: dict[str, Any]) -> None:
        """Handle incoming messages"""
        try:
            content = message["content"]
            action = content.get("action")

            if action == "process_input":
                self._handle_input_processing(content)
            elif action == "consolidate_memories":
                self._handle_memory_consolidation(content)
            elif action == "start_dream_cycle":
                self._handle_dream_cycle(content)

        except Exception as e:
            logger.error(f"Error handling message: {e}")

    async def process_input(
        self, input_data: str, context: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Process input through brain

        Args:
            input_data: Input to process
            context: Optional processing context

        Returns:
            Dict with processing results
        """
        self.cognitive_states["processing"] = True
        self.cognitive_states["current_task"] = "input_processing"

        try:
            result = await self.integration.send_message(
                source=self.component_id,
                target="cognitive_core",
                message_type=MessageType.COMMAND,
                content={
                    "action": "process_input",
                    "input": input_data,
                    "context": context or {},
                    "settings": self.memory_settings,
                },
            )
            return result

        finally:
            self.cognitive_states["processing"] = False
            self.cognitive_states["current_task"] = None
            self.cognitive_states["last_activity"] = datetime.now().isoformat()

    async def consolidate_memories(
        self, hours_limit: float = 24.0, max_memories: int = 100
    ) -> dict[str, Any]:
        """Consolidate recent memories

        Args:
            hours_limit: How many hours of memories to process
            max_memories: Maximum number of memories to process

        Returns:
            Dict with consolidation results
        """
        return await self.integration.send_message(
            source=self.component_id,
            target="memory_core",
            message_type=MessageType.COMMAND,
            content={
                "action": "consolidate_memories",
                "hours_limit": hours_limit,
                "max_memories": max_memories,
                "settings": self.memory_settings,
            },
        )

    async def start_dream_cycle(self, duration_minutes: float = 10.0) -> dict[str, Any]:
        """Start a dream processing cycle

        Args:
            duration_minutes: How long to run the cycle

        Returns:
            Dict with cycle results
        """
        return await self.integration.send_message(
            source=self.component_id,
            target="dream_engine",
            message_type=MessageType.COMMAND,
            content={
                "action": "start_dream_cycle",
                "duration_minutes": duration_minutes,
                "settings": self.memory_settings,
            },
        )

    def _handle_input_processing(self, content: dict[str, Any]) -> None:
        """Handle input processing request"""
        input_data = content.get("input", "")
        context = content.get("context")

        logger.info(f"Processing input: {input_data[:50]}...")
        asyncio.create_task(self.process_input(input_data, context))

    def _handle_memory_consolidation(self, content: dict[str, Any]) -> None:
        """Handle memory consolidation request"""
        hours = content.get("hours_limit", 24.0)
        max_count = content.get("max_memories", 100)

        logger.info(
            f"Starting memory consolidation: {hours}h limit, max {max_count}..."
        )
        asyncio.create_task(self.consolidate_memories(hours, max_count))

    def _handle_dream_cycle(self, content: dict[str, Any]) -> None:
        """Handle dream cycle request"""
        duration = content.get("duration_minutes", 10.0)

        logger.info(f"Starting dream cycle for {duration} minutes...")
        asyncio.create_task(self.start_dream_cycle(duration))
