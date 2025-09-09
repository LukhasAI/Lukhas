"""Simple supervisor agent for restricted tasks."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class SupervisorAgent:
    """Handle escalated tasks."""

    async def review_task(self, colony_id: str, task_id: str, task_data: dict[str, Any]) -> dict[str, Any]:
        logger.info(f"Supervisor reviewing task {task_id} from colony {colony_id}")
        return {"status": "escalated", "task_id": task_id, "colony": colony_id}