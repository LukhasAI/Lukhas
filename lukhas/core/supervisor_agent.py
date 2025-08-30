"""
LUKHAS AI Supervisor Agent
Task escalation and colony supervision
Trinity Framework: ⚛️🧠🛡️
"""

import logging
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)


class SupervisorAgent:
    """
    Advanced supervisor agent for colony task escalation and oversight.

    Handles escalated tasks from colonies and provides supervision capabilities
    for critical operations that require elevated privileges or special handling.
    """

    def __init__(self, supervisor_id: str = "supervisor-1") -> None:
        self.supervisor_id = supervisor_id
        self.escalation_history: list[dict] = []
        self.max_history = 1000
        self.active_escalations: dict[str, dict] = {}

        logger.info(f"SupervisorAgent {supervisor_id} initialized")

    async def review_task(self, colony_id: str, task_id: str, task_data: dict[str, Any]) -> dict[str, Any]:
        """
        Review an escalated task from a colony.

        Args:
            colony_id: ID of the escalating colony
            task_id: Unique task identifier
            task_data: Task data and context

        Returns:
            Review result with status and recommendations
        """
        logger.info(f"Supervisor reviewing task {task_id} from colony {colony_id}")

        # Create escalation record
        escalation = {
            "task_id": task_id,
            "colony_id": colony_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "task_data": task_data,
            "supervisor_id": self.supervisor_id,
            "status": "under_review",
        }

        # Store active escalation
        self.active_escalations[task_id] = escalation

        # Perform review analysis
        review_result = await self._analyze_task(task_data)

        # Update escalation with result
        escalation.update(
            {
                "review_result": review_result,
                "status": "reviewed",
                "reviewed_at": datetime.now(timezone.utc).isoformat(),
            }
        )

        # Move to history
        self._record_escalation(escalation)
        if task_id in self.active_escalations:
            del self.active_escalations[task_id]

        return {
            "status": "escalated",
            "task_id": task_id,
            "colony": colony_id,
            "supervisor_id": self.supervisor_id,
            "review_result": review_result,
            "timestamp": escalation["timestamp"],
        }

    async def _analyze_task(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze the escalated task for complexity and risk.

        Args:
            task_data: Task data to analyze

        Returns:
            Analysis results
        """
        analysis = {
            "complexity": "medium",
            "risk_level": "low",
            "approval": "approved",
            "recommendations": [],
        }

        # Check task type
        task_type = task_data.get("type", "unknown")

        if task_type in ["system_override", "emergency", "critical"]:
            analysis["risk_level"] = "high"
            analysis["complexity"] = "high"
            analysis["recommendations"].append("Requires manual oversight")

        # Check for sensitive operations
        if any(keyword in str(task_data).lower() for keyword in ["delete", "remove", "override", "bypass", "escalate"]):
            analysis["risk_level"] = "medium"
            analysis["recommendations"].append("Monitor for side effects")

        # Check resource requirements
        if task_data.get("resource_intensive", False):
            analysis["complexity"] = "high"
            analysis["recommendations"].append("Schedule during low-load periods")

        # Determine approval
        if analysis["risk_level"] == "high":
            analysis["approval"] = "requires_confirmation"
        elif analysis["complexity"] == "high" and analysis["risk_level"] == "medium":
            analysis["approval"] = "conditional"

        return analysis

    def _record_escalation(self, escalation: dict[str, Any]) -> None:
        """Record escalation in history."""
        self.escalation_history.append(escalation)

        # Maintain history size limit
        if len(self.escalation_history) > self.max_history:
            self.escalation_history.pop(0)

    def get_escalation_stats(self) -> dict[str, Any]:
        """Get statistics about escalations."""
        total_escalations = len(self.escalation_history)

        if total_escalations == 0:
            return {
                "total_escalations": 0,
                "active_escalations": len(self.active_escalations),
                "approval_rate": 0.0,
                "average_risk_level": "unknown",
            }

        # Calculate approval rate
        approved = sum(1 for e in self.escalation_history if e.get("review_result", {}).get("approval") == "approved")
        approval_rate = approved / total_escalations

        # Calculate risk distribution
        risk_levels = [e.get("review_result", {}).get("risk_level", "unknown") for e in self.escalation_history]
        risk_counts = {level: risk_levels.count(level) for level in set(risk_levels)}

        return {
            "total_escalations": total_escalations,
            "active_escalations": len(self.active_escalations),
            "approval_rate": approval_rate,
            "risk_distribution": risk_counts,
            "supervisor_id": self.supervisor_id,
        }

    def get_active_escalations(self) -> list[dict[str, Any]]:
        """Get list of currently active escalations."""
        return list(self.active_escalations.values())

    def get_escalation_history(self, limit: Optional[int] = None) -> list[dict[str, Any]]:
        """
        Get escalation history.

        Args:
            limit: Maximum number of records to return

        Returns:
            List of escalation records
        """
        history = self.escalation_history.copy()
        history.reverse()  # Most recent first

        if limit:
            history = history[:limit]

        return history


# Global supervisor instance
_supervisor_agent = None


def get_supervisor_agent() -> SupervisorAgent:
    """Get or create the global supervisor agent."""
    global _supervisor_agent
    if _supervisor_agent is None:
        _supervisor_agent = SupervisorAgent()
    return _supervisor_agent


# Export public interface
__all__ = ["SupervisorAgent", "get_supervisor_agent"]
