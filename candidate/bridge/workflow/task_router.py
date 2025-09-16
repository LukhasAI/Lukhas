"""Minimal task routing utilities for workflow orchestration tests."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


@dataclass
class RouteRecord:
    """Record of a routed task for lightweight diagnostics."""

    workflow_id: str
    task_id: str
    route: str
    metadata: Dict[str, Any] = field(default_factory=dict)


# ΛTAG:workflow_routing
class TaskRouter:
    """Simplified task router used to unblock workflow orchestrator tests.

    The production router includes adaptive routing based on workload metrics
    and provider capabilities. For test coverage we only need to capture that a
    routing decision happened, so this class stores the routing history and
    exposes a health check describing the internal state.
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self._route_history: List[RouteRecord] = []
        self._default_route = self.config.get("default_route", "default")

    async def route_task(self, workflow_id: str, task_id: str, **metadata: Any) -> str:
        """Record a routing event and return the configured destination."""

        route = metadata.get("route", self._default_route)
        record = RouteRecord(workflow_id=workflow_id, task_id=task_id, route=route, metadata=metadata)
        self._route_history.append(record)
        logger.debug("Routed task %s for workflow %s via %s", task_id, workflow_id, route)
        return route

    async def health_check(self) -> dict[str, Any]:
        """Return basic router state for observability."""

        return {
            "status": "healthy",
            "default_route": self._default_route,
            "routed_tasks": len(self._route_history),
        }
