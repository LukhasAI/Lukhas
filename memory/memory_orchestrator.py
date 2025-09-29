"""
LUKHAS Memory Orchestrator
========================

Central orchestrator for memory systems coordination.
"""

from __future__ import annotations
import logging
from typing import Any, Dict
from .indexer import Indexer
from .observability import MemoryTracer

logger = logging.getLogger(__name__)


class MemoryOrchestrator:
    """Public facade API kept stable for callers."""

    def __init__(self, indexer: Indexer, guardian=None):
        self.indexer = indexer
        self.guardian = guardian
        self.tracer = MemoryTracer()
        self.logger = logger
        self.logger.info("MemoryOrchestrator initialized")

    async def add_event(self, text: str, meta: Dict[str, Any]) -> str:
        """Add memory event with Guardian validation."""
        with self.tracer.trace_operation("add_event") as span:
            span.add_attributes(text_length=len(text), meta_keys=list(meta.keys()))

            # Guardian pre-validation
            if self.guardian:
                await self.guardian.validate_action_async("memory_add", {"text": text, "meta": meta})

            result = self.indexer.upsert(text, meta)

            # Guardian post-validation
            if self.guardian:
                await self.guardian.monitor_behavior_async("memory_added", {"id": result, "text_len": len(text)})

            span.add_attributes(result_id=result)
            return result

    def query(self, text: str, k: int = 8, filters: Dict[str, Any] | None = None):
        """Query memories with filters."""
        with self.tracer.trace_operation("query") as span:
            span.add_attributes(query_length=len(text), k=k, has_filters=filters is not None)
            results = self.indexer.search_text(text, k=k, filters=filters)
            span.add_attributes(results_count=len(results) if results else 0)
            return results

    def orchestrate_memory(self, operation: str, data: dict[str, Any]) -> dict[str, Any]:
        """Legacy orchestrate method for compatibility."""
        return {"status": "success", "operation": operation, "result": f"Memory operation {operation} completed"}
