"""
Cancellation Registry

Registry for pipeline cancellation tokens, cleanup handlers, and partial results.
"""

import asyncio
import logging
from collections.abc import Coroutine
from datetime import datetime
from typing import Any, Callable, Dict, List

logger = logging.getLogger(__name__)


class CancellationRegistry:
    """Registry for pipeline cancellation tokens, handlers, and results."""

    def __init__(self):
        self._tokens: Dict[str, asyncio.Event] = {}
        self._metadata: Dict[str, dict] = {}
        self._cleanup_handlers: Dict[str, List[Callable[[], Coroutine]]] = {}
        self._partial_results: Dict[str, Dict[str, Any]] = {}

    def register(self, pipeline_id: str) -> asyncio.Event:
        """Register a new pipeline and return its cancellation token."""
        token = asyncio.Event()
        self._tokens[pipeline_id] = token
        self._metadata[pipeline_id] = {
            "created_at": datetime.utcnow(),
            "cancelled": False,
        }
        self._cleanup_handlers[pipeline_id] = []
        self._partial_results[pipeline_id] = {}
        return token

    def register_cleanup_handler(
        self, pipeline_id: str, handler: Callable[[], Coroutine]
    ):
        """Register a cleanup handler for a given pipeline."""
        if pipeline_id in self._cleanup_handlers:
            self._cleanup_handlers[pipeline_id].append(handler)

    def store_partial_result(self, pipeline_id: str, node_id: str, result: Any):
        """Store the partial result of a completed node."""
        if pipeline_id in self._partial_results:
            self._partial_results[pipeline_id][node_id] = result

    def get_partial_results(self, pipeline_id: str) -> Dict[str, Any]:
        """Get the partial results for a given pipeline."""
        return self._partial_results.get(pipeline_id, {})

    async def cancel(self, pipeline_id: str, reason: str = "User requested") -> bool:
        """Cancel a pipeline by ID and execute cleanup handlers."""
        if pipeline_id not in self._tokens:
            return False

        token = self._tokens[pipeline_id]
        token.set()

        self._metadata[pipeline_id]["cancelled"] = True
        self._metadata[pipeline_id]["cancelled_at"] = datetime.utcnow()
        self._metadata[pipeline_id]["reason"] = reason

        await self._execute_cleanup_handlers(pipeline_id)

        return True

    async def _execute_cleanup_handlers(self, pipeline_id: str):
        """Execute all registered cleanup handlers for a pipeline."""
        handlers = self._cleanup_handlers.get(pipeline_id, [])
        if not handlers:
            return

        logger.info(
            f"Executing {len(handlers)} cleanup handlers for pipeline {pipeline_id}"
        )
        for handler in handlers:
            try:
                await handler()
            except Exception as e:
                logger.error(
                    f"Error executing cleanup handler for pipeline {pipeline_id}: {e}",
                    exc_info=True,
                )

    def unregister(self, pipeline_id: str) -> None:
        """Unregister a completed pipeline."""
        self._tokens.pop(pipeline_id, None)
        self._metadata.pop(pipeline_id, None)
        self._cleanup_handlers.pop(pipeline_id, None)
        self._partial_results.pop(pipeline_id, None)

    def is_cancelled(self, pipeline_id: str) -> bool:
        """Check if pipeline is cancelled."""
        if pipeline_id not in self._tokens:
            return False
        return self._tokens[pipeline_id].is_set()

    def get_metadata(self, pipeline_id: str) -> dict:
        """Get pipeline metadata."""
        return self._metadata.get(pipeline_id, {})
