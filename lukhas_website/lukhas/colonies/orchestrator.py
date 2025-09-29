"""
LUKHAS AI Colony System - Orchestrator Colony
Coordinates multiple colonies and manages workflows
Constellation Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""
from datetime import datetime, timezone
from typing import Any

from .base import BaseColony, ColonyTask, get_colony_registry


class OrchestratorColony(BaseColony):
    """Meta-colony that coordinates other colonies"""

    def __init__(self, max_agents: int = 6):
        self.workflow_templates = {}
        self.active_workflows = {}
        self.colony_status_cache = {}
        super().__init__("orchestrator", max_agents)

    def get_default_capabilities(self) -> list[str]:
        return [
            "workflow_management",
            "colony_coordination",
            "task_routing",
            "load_balancing",
            "system_orchestration",
        ]

    def process_task(self, task: ColonyTask) -> Any:
        task_type = task.task_type
        payload = task.payload

        if task_type == "execute_workflow":
            return self._execute_workflow(payload)
        elif task_type == "route_task":
            return self._route_task(payload)
        elif task_type == "balance_load":
            return self._balance_load()
        elif task_type == "system_status":
            return self._get_system_status()
        else:
            return {"status": "unknown_task_type", "task_type": task_type}

    def _execute_workflow(self, workflow_spec: dict[str, Any]) -> dict[str, Any]:
        """Execute a multi-colony workflow"""
        workflow_id = f"wf_{datetime.now(timezone.utc).timestamp()}"
        steps = workflow_spec.get("steps", [])

        workflow_result = {
            "workflow_id": workflow_id,
            "steps_completed": 0,
            "results": [],
            "status": "running",
            "started_at": datetime.now(timezone.utc),
        }

        registry = get_colony_registry()

        for i, step in enumerate(steps):
            colony_name = step.get("colony")
            task_type = step.get("task_type")
            task_payload = step.get("payload", {})

            if colony_name and colony_name in registry.colonies:
                colony = registry.colonies[colony_name]
                task = colony.submit_task(task_type, task_payload)

                # Process the task immediately for this demo
                colony.process_queue()

                if task.id in colony.completed_tasks:
                    step_result = colony.completed_tasks[task.id].result
                    workflow_result["results"].append({"step": i, "colony": colony_name, "result": step_result})
                    workflow_result["steps_completed"] += 1
                else:
                    workflow_result["status"] = "failed"
                    workflow_result["error"] = f"Step {i} failed in colony {colony_name}"
                    break
            else:
                workflow_result["status"] = "failed"
                workflow_result["error"] = f"Colony {colony_name} not found"
                break

        if workflow_result["status"] == "running":
            workflow_result["status"] = "completed"

        self.active_workflows[workflow_id] = workflow_result
        return workflow_result

    def _route_task(self, routing_request: dict[str, Any]) -> dict[str, Any]:
        """Route a task to the best colony"""
        task_type = routing_request.get("task_type")
        required_capabilities = routing_request.get("capabilities", [])

        registry = get_colony_registry()

        # Check if there's a specific route
        if task_type in registry.task_routes:
            colony_name = registry.task_routes[task_type]
            return {"routed_to": colony_name, "reason": "specific_route"}

        # Find best colony based on capabilities and load
        best_colony = None
        best_score = -1

        for colony in registry.colonies.values():
            if colony.status.value != "active":
                continue

            # Check if colony has required capabilities
            colony_capabilities = set()
            for agent in colony.agents.values():
                colony_capabilities.update(agent.capabilities)

            if not all(cap in colony_capabilities for cap in required_capabilities):
                continue

            # Calculate score based on load and agent availability
            avg_load = sum(agent.load for agent in colony.agents.values()) / len(colony.agents)
            queue_load = len(colony.task_queue) / 10.0  # Normalize queue size

            score = 1.0 - (avg_load * 0.6 + queue_load * 0.4)

            if score > best_score:
                best_score = score
                best_colony = colony

        if best_colony:
            return {
                "routed_to": best_colony.name,
                "reason": "best_match",
                "score": best_score,
            }
        else:
            return {"routed_to": None, "reason": "no_suitable_colony"}

    def _balance_load(self) -> dict[str, Any]:
        """Balance load across colonies"""
        registry = get_colony_registry()

        load_info = {}
        total_load = 0
        colony_count = 0

        for name, colony in registry.colonies.items():
            if colony.status.value == "active":
                avg_load = sum(agent.load for agent in colony.agents.values()) / len(colony.agents)
                queue_size = len(colony.task_queue)

                load_info[name] = {
                    "avg_agent_load": avg_load,
                    "queue_size": queue_size,
                    "total_agents": len(colony.agents),
                }

                total_load += avg_load
                colony_count += 1

        avg_system_load = total_load / colony_count if colony_count > 0 else 0

        # Identify overloaded and underloaded colonies
        overloaded = []
        underloaded = []

        for name, info in load_info.items():
            if info["avg_agent_load"] > avg_system_load * 1.5:
                overloaded.append(name)
            elif info["avg_agent_load"] < avg_system_load * 0.5:
                underloaded.append(name)

        return {
            "avg_system_load": avg_system_load,
            "load_info": load_info,
            "overloaded_colonies": overloaded,
            "underloaded_colonies": underloaded,
            "recommendation": "redistribute_tasks" if overloaded else "balanced",
        }

    def _get_system_status(self) -> dict[str, Any]:
        """Get comprehensive system status"""
        registry = get_colony_registry()

        status = {
            "total_colonies": len(registry.colonies),
            "active_colonies": 0,
            "total_agents": 0,
            "total_pending_tasks": 0,
            "colonies": {},
        }

        for name, colony in registry.colonies.items():
            colony_status = colony.get_status()
            status["colonies"][name] = colony_status

            if colony_status["status"] == "active":
                status["active_colonies"] += 1

            status["total_agents"] += colony_status["agents"]
            status["total_pending_tasks"] += colony_status["queue_size"]

        return status


_orchestrator_colony = None


def get_orchestrator_colony() -> OrchestratorColony:
    global _orchestrator_colony
    if _orchestrator_colony is None:
        _orchestrator_colony = OrchestratorColony()
        from .base import get_colony_registry

        registry = get_colony_registry()
        registry.register_colony(_orchestrator_colony)
        registry.add_task_route("execute_workflow", "orchestrator")
        registry.add_task_route("route_task", "orchestrator")
        registry.add_task_route("balance_load", "orchestrator")
        registry.add_task_route("system_status", "orchestrator")
    return _orchestrator_colony
