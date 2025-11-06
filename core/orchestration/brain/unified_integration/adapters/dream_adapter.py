"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: dream_adapter.py
Advanced: dream_adapter.py
Integration Date: 2025-05-31T07:55:29.982795
"""
import asyncio
import logging
import time

# Simple adapter for dream engine integration
from typing import Any

from ..unified_integration import UnifiedIntegration

logger = logging.getLogger("dream_adapter")


class DreamEngineAdapter:
    """Adapter for dream engine integration with state tracking"""

    def __init__(self, integration: UnifiedIntegration):
        """Initialize dream engine adapter

        Args:
            integration: Reference to integration layer
        """
        self.integration = integration
        self.component_id = "dream_engine"

        # State tracking
        self.dream_state = {
            "status": "idle",
            "start_time": None,
            "duration": 0,
            "last_updated": time.time(),
        }

        # Register with integration layer
        self.integration.register_component(self.component_id, self.handle_message)

        logger.info("Dream Engine adapter initialized")

    def _send_response(self, content: dict[str, Any]) -> None:
        """Send response to the integration layer"""
        self.integration.send_message(self.component_id, content)

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
            logger.error(f"Error handling message: {e}",
        )

    def _update_state(self, status: str, duration: int = 0) -> None:
        """Update and log the dream state"""
        self.dream_state["status"] = status
        self.dream_state["duration"] = duration
        self.dream_state["start_time"] = (
            time.time() if status == "dreaming" else None
        )
        self.dream_state["last_updated"] = time.time()
        logger.info(f"Dream state updated: {self.dream_state}")

    async def start_dream_cycle(self, duration_minutes: int) -> None:
        """Simulate a dream cycle"""
        if self.dream_state["status"] == "dreaming":
            logger.warning("Dream cycle already in progress")
            return

        self._update_state("dreaming", duration_minutes)
        await asyncio.sleep(duration_minutes * 60)

        # End of dream cycle if not stopped manually
        if self.dream_state["status"] == "dreaming":
            self._update_state("idle")
            logger.info("Dream cycle finished")

    async def stop_dream_cycle(self) -> None:
        """Stop the current dream cycle"""
        if self.dream_state["status"] == "dreaming":
            self._update_state("idle")
            logger.info("Dream cycle stopped manually")
        else:
            logger.info("No dream cycle in progress to stop")

    def _handle_start_cycle(self, content: dict[str, Any]) -> None:
        """Handle start cycle request"""
        duration = content.get("duration_minutes", 10)
        logger.info(f"Received request to start dream cycle for {duration} minutes")
# T4: code=RUF006 | ticket=GH-1031 | owner=consciousness-team | status=accepted
# reason: Fire-and-forget async task - intentional background processing pattern
# estimate: 0h | priority: low | dependencies: none
        asyncio.create_task(self.start_dream_cycle(duration))

    def _handle_stop_cycle(self, content: dict[str, Any]) -> None:
        """Handle stop cycle request"""
        logger.info("Received request to stop dream cycle")
# T4: code=RUF006 | ticket=GH-1031 | owner=consciousness-team | status=accepted
# reason: Fire-and-forget async task - intentional background processing pattern
# estimate: 0h | priority: low | dependencies: none
        asyncio.create_task(self.stop_dream_cycle())

    def _handle_get_state(self, content: dict[str, Any]) -> None:
        """Handle get state request and send response"""
        logger.info("Received request for dream state")
        self._send_response(
            {
                "status": "state_report",
                "dream_state": self.dream_state,
            }
        )
