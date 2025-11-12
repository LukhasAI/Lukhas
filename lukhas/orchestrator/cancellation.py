"""
Cancellation Registry

Registry for pipeline cancellation tokens and metadata.
"""

import asyncio
from datetime import datetime
from typing import Dict


class CancellationRegistry:
    """Registry for pipeline cancellation tokens."""

    def __init__(self):
        self._tokens: Dict[str, asyncio.Event] = {}
        self._metadata: Dict[str, dict] = {}

    def register(self, pipeline_id: str) -> asyncio.Event:
        """Register a new pipeline and return its cancellation token."""
        token = asyncio.Event()
        self._tokens[pipeline_id] = token
        self._metadata[pipeline_id] = {
            "created_at": datetime.utcnow(),
            "cancelled": False,
        }
        return token

    def cancel(self, pipeline_id: str, reason: str = "User requested") -> bool:
        """Cancel a pipeline by ID."""
        if pipeline_id not in self._tokens:
            return False

        token = self._tokens[pipeline_id]
        token.set()

        self._metadata[pipeline_id]["cancelled"] = True
        self._metadata[pipeline_id]["cancelled_at"] = datetime.utcnow()
        self._metadata[pipeline_id]["reason"] = reason

        return True

    def unregister(self, pipeline_id: str) -> None:
        """Unregister a completed pipeline."""
        self._tokens.pop(pipeline_id, None)
        self._metadata.pop(pipeline_id, None)

    def is_cancelled(self, pipeline_id: str) -> bool:
        """Check if pipeline is cancelled."""
        if pipeline_id not in self._tokens:
            return False
        return self._tokens[pipeline_id].is_set()

    def get_metadata(self, pipeline_id: str) -> dict:
        """Get pipeline metadata."""
        return self._metadata.get(pipeline_id, {})
