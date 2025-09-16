"""Minimal workflow monitoring helpers for orchestrator tests."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict

logger = logging.getLogger(__name__)


@dataclass
class TaskLifecycle:
    """Simple lifecycle record for a workflow task."""

    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    success: bool | None = None


# ΛTAG:workflow_monitoring
class WorkflowMonitor:
    """Lightweight monitor that tracks task lifecycles for tests.

    The production monitor streams metrics to the observability layer. For test
    purposes we maintain in-memory state that allows the orchestrator to observe
    task execution without requiring the full monitoring stack.
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self._workflow_tasks: Dict[str, Dict[str, TaskLifecycle]] = {}

    async def record_task_start(self, workflow_id: str, task_id: str) -> None:
        """Register the start of a task."""

        workflow_tasks = self._workflow_tasks.setdefault(workflow_id, {})
        workflow_tasks[task_id] = TaskLifecycle()
        logger.debug("Task %s started in workflow %s", task_id, workflow_id)

    async def record_task_completion(self, workflow_id: str, task_id: str, success: bool) -> None:
        """Mark a task as complete."""

        workflow_tasks = self._workflow_tasks.setdefault(workflow_id, {})
        lifecycle = workflow_tasks.get(task_id)
        if lifecycle is None:
            lifecycle = TaskLifecycle()
            workflow_tasks[task_id] = lifecycle
        lifecycle.completed_at = datetime.now(timezone.utc)
        lifecycle.success = success
        logger.debug("Task %s completed in workflow %s (success=%s)", task_id, workflow_id, success)

    async def health_check(self) -> dict[str, Any]:
        """Return monitor state for orchestrator health reporting."""

        total_tasks = sum(len(tasks) for tasks in self._workflow_tasks.values())
        completed = sum(
            1
            for tasks in self._workflow_tasks.values()
            for lifecycle in tasks.values()
            if lifecycle.completed_at is not None
        )
        return {
            "status": "healthy",
            "tracked_workflows": len(self._workflow_tasks),
            "tracked_tasks": total_tasks,
            "completed_tasks": completed,
        }
