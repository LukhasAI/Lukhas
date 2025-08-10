from typing import Any

from core.colonies.governance_colony import GovernanceColony
from core.colonies.reasoning_colony import ReasoningColony


class _StubColony:
    """Minimal colony used for perception and action."""

    def __init__(self, colony_id: str, capability: str):
        self.colony_id = colony_id
        self.capabilities = [capability]

    async def execute_task(self, task_id: str, task: dict[str, Any]) -> dict[str, Any]:
        return {
            "task_id": task_id,
            "capability": self.capabilities[0],
            "status": "done",
        }


class BrainColonyCoordinator:
    """Coordinates brain functions through colony architecture."""

    def __init__(self, brain_id: str = "lukhas-brain"):
        self.brain_id = brain_id
        self.governance = GovernanceColony(f"{brain_id}-governance")
        self.functional_colonies = {
            "perception": self._create_perception_colony(),
            "reasoning": ReasoningColony(f"{brain_id}-reasoning"),
            "action": self._create_action_colony(),
            "emotion": self._create_emotion_colony(),
        }

    def _create_perception_colony(self) -> _StubColony:
        return _StubColony(f"{self.brain_id}-perception", "perception")

    def _create_action_colony(self) -> _StubColony:
        return _StubColony(f"{self.brain_id}-action", "action")

    def _create_emotion_colony(self) -> _StubColony:
        return _StubColony(f"{self.brain_id}-emotion", "emotion")

    async def _execute_colony_task(
        self, colony_key: str, task: dict[str, Any]
    ) -> dict[str, Any]:
        colony = self.functional_colonies[colony_key]
        return await colony.execute_task(task.get("id", "task"), task)

    async def _create_execution_plan(self, stimulus: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": f"plan-{self.brain_id}",
            "steps": [
                {
                    "id": "perceive",
                    "colony": "perception",
                    "task": {"type": "perceive"},
                    "parallel": False,
                },
                {
                    "id": "reason",
                    "colony": "reasoning",
                    "task": {"type": "reason"},
                    "parallel": False,
                },
                {
                    "id": "emote",
                    "colony": "emotion",
                    "task": {"type": "emote"},
                    "parallel": False,
                },
                {
                    "id": "act",
                    "colony": "action",
                    "task": {"type": "act"},
                    "parallel": False,
                },
            ],
        }

    async def _integrate_results(
        self, plan_id: str, results: dict[str, Any], stimulus: dict[str, Any]
    ) -> dict[str, Any]:
        return {
            "plan_id": plan_id,
            "results": results,
            "original_stimulus": stimulus,
        }

    async def coordinate_thought(self, stimulus: dict[str, Any]) -> dict[str, Any]:
        plan = await self._create_execution_plan(stimulus)
        results = {}

        for step in plan["steps"]:
            result = await self._execute_colony_task(step["colony"], step["task"])
            results[step["id"]] = result

        integrated = await self._integrate_results(plan["id"], results, stimulus)
        return integrated
