#!/usr/bin/env python3
"""Basic governance routing example for the bridge package."""

from __future__ import annotations

import asyncio
import sys
from dataclasses import dataclass
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any, Iterable

_REPO_ROOT = Path(__file__).resolve().parents[3]


def _load_workflow_helper(module_name: str, relative_path: str):
    module_path = _REPO_ROOT / relative_path
    spec = spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module {module_name} from {module_path}")
    module = module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


_TaskRouterModule = _load_workflow_helper("bridge_examples_basic_task_router", "bridge/workflow/task_router.py")
_WorkflowMonitorModule = _load_workflow_helper(
    "bridge_examples_basic_workflow_monitor", "bridge/workflow/workflow_monitor.py"
)
TaskRouter = _TaskRouterModule.TaskRouter
WorkflowMonitor = _WorkflowMonitorModule.WorkflowMonitor


@dataclass
class GovernanceDecision:
    """Result of a governance evaluation."""

    action: str
    route: str
    approved: bool
    reasons: list[str]
    monitor_summary: dict[str, Any]


async def simulate_governance_flow(
    action: str,
    *,
    risk_score: float,
    tags: Iterable[str] | None = None,
    router: TaskRouter | None = None,
    monitor: WorkflowMonitor | None = None,
) -> GovernanceDecision:
    """Simulate routing a governance action through bridge workflow helpers."""

    router = router or TaskRouter({"default_route": "governance-check"})
    monitor = monitor or WorkflowMonitor({})

    workflow_id = f"governance-{action}"
    task_id = f"decision-{action}"
    tag_set = set(tags or ())

    await monitor.record_task_start(workflow_id, task_id)
    route = await router.route_task(workflow_id, task_id, risk=risk_score, tags=sorted(tag_set))

    reasons: list[str] = []
    approved = True
    if risk_score >= 0.6:
        approved = False
        reasons.append(f"risk score {risk_score:.2f} exceeds policy threshold 0.60")
    if "restricted" in tag_set:
        approved = False
        reasons.append("contains restricted classification tag")

    await monitor.record_task_completion(workflow_id, task_id, success=approved)
    monitor_summary = await monitor.health_check()

    if not reasons:
        reasons.append("risk and classification checks passed")

    return GovernanceDecision(
        action=action,
        route=route,
        approved=approved,
        reasons=reasons,
        monitor_summary=monitor_summary,
    )


def main() -> None:
    """Run the governance routing example and print a concise report."""

    decision = asyncio.run(
        simulate_governance_flow(
            "publish-report",
            risk_score=0.35,
            tags={"internal", "governed"},
        )
    )

    status = "APPROVED" if decision.approved else "REJECTED"
    print(f"Governance decision for {decision.action}: {status} via route '{decision.route}'")
    for reason in decision.reasons:
        print(f" - {reason}")
    print(
        "Monitor summary: tracked_workflows={tracked_workflows}, "
        "tracked_tasks={tracked_tasks}, completed_tasks={completed_tasks}".format(**decision.monitor_summary)
    )


if __name__ == "__main__":
    main()
