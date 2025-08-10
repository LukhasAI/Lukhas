"""Governance Colony for ethical scenario review."""

import asyncio
import logging
from typing import Any, Dict

from core.colonies.base_colony import BaseColony
from ethics.meg_bridge import MEGPolicyBridge, create_meg_bridge
from ethics.policy_engines.base import Decision, RiskLevel

logger = logging.getLogger(__name__)


class GovernanceColony(BaseColony):
    """Colony responsible for ethical oversight."""

    def __init__(self, colony_id: str):
        super().__init__(colony_id, capabilities=["governance", "ethics"])
        self.bridge: MEGPolicyBridge = create_meg_bridge()

    def review_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a scenario using the MEG policy bridge."""
        decision = Decision(
            action=scenario.get("action", "dream_recursion"),
            context=scenario.get("context", {}),
            requester_id=scenario.get("user_id"),
            urgency=RiskLevel.MEDIUM,
        )
        evaluation = asyncio.run(self.bridge.evaluate_with_meg(decision))
        return {
            "allowed": evaluation.allowed,
            "confidence": evaluation.confidence,
            "risk_flags": evaluation.risk_flags,
        }

    async def execute_task(
        self, task_id: str, task_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        logger.info(f"GovernanceColony {self.colony_id} reviewing scenario {task_id}")
        evaluation = self.review_scenario(task_data)
        return {"status": "completed", "task_id": task_id, "evaluation": evaluation}
