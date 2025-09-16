"""Transparency helpers for the workflow orchestrator tests."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict

logger = logging.getLogger(__name__)


# ΛTAG:workflow_transparency
class WorkflowTransparency:
    """Store lightweight transparency data for active workflows.

    The production system streams detailed telemetry to dashboards. For the
    integration tests we only need a deterministic, in-memory representation
    that reports workflow and task status changes.
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self._workflows: Dict[str, Dict[str, Any]] = {}

    async def initialize_workflow_tracking(self, workflow_id: str, definition: Any) -> None:
        """Create a transparency entry for a workflow definition."""

        tasks = getattr(definition, "tasks", {})
        self._workflows[workflow_id] = {
            "definition": {
                "name": getattr(definition, "name", "unknown"),
                "description": getattr(definition, "description", ""),
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
            "tasks": {task_id: {"status": "pending"} for task_id in tasks},
            "status": "pending",
        }
        logger.debug("Initialized transparency tracking for workflow %s", workflow_id)

    async def start_workflow_tracking(self, workflow_id: str) -> None:
        """Mark a workflow as running."""

        workflow = self._workflows.get(workflow_id)
        if workflow:
            workflow["status"] = "running"
            workflow["started_at"] = datetime.now(timezone.utc).isoformat()
            logger.debug("Workflow %s marked as running", workflow_id)

    async def update_task_status(self, workflow_id: str, task_id: str, status: Any) -> None:
        """Update a task status for transparency reporting."""

        workflow = self._workflows.get(workflow_id)
        if not workflow:
            return
        status_value = getattr(status, "value", str(status))
        workflow.setdefault("tasks", {}).setdefault(task_id, {})["status"] = status_value
        workflow["tasks"][task_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
        logger.debug("Task %s in workflow %s -> %s", task_id, workflow_id, status_value)

    async def complete_workflow_tracking(self, workflow_id: str, status: Any) -> None:
        """Finalize workflow transparency state."""

        workflow = self._workflows.get(workflow_id)
        if workflow:
            workflow["status"] = getattr(status, "value", str(status))
            workflow["completed_at"] = datetime.now(timezone.utc).isoformat()
            logger.debug("Workflow %s completed with status %s", workflow_id, workflow["status"])

    async def get_workflow_transparency(self, workflow_id: str) -> dict[str, Any]:
        """Return transparency snapshot for a workflow."""

        return self._workflows.get(workflow_id, {})

    async def health_check(self) -> dict[str, Any]:
        """Expose transparency service health data."""

        return {
            "status": "healthy",
            "tracked_workflows": len(self._workflows),
        }
