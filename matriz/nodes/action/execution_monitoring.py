#!/usr/bin/env python3
"""
MATRIZ Execution Monitoring Node

Monitors ongoing action execution and detects deviations from plan.
Provides real-time feedback on progress and potential issues.

Example: "Action 'file download' is 75% complete, on track, no errors"
"""

import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List

from matriz.core.node_interface import CognitiveNode, NodeState, NodeTrigger


@dataclass
class ExecutionStatus:
    """Status of an executing action."""
    action_id: str
    action_name: str
    progress: float  # 0.0 - 1.0
    status: str  # running, completed, failed, blocked
    deviations: List[str]  # Detected deviations from plan
    issues: List[str]  # Current issues


class ExecutionMonitoringNode(CognitiveNode):
    """
    Monitors action execution in real-time.

    Capabilities:
    - Progress tracking
    - Deviation detection
    - Issue identification
    - Status reporting
    """

    def __init__(self, tenant: str = "default"):
        super().__init__(
            node_name="matriz_execution_monitoring",
            capabilities=[
                "execution_monitoring",
                "progress_tracking",
                "deviation_detection",
                "governed_trace"
            ],
            tenant=tenant
        )

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Monitor execution status.

        Args:
            input_data: Dict containing:
                - executing_actions: List of currently executing actions
                - expected_states: Expected states for each action
                - actual_states: Actual observed states
                - plan: Original plan for comparison

        Returns:
            Dict with execution status, deviations, and MATRIZ node
        """
        start_time = time.time()

        executing_actions = input_data.get("executing_actions", [])
        expected_states = input_data.get("expected_states", {})
        actual_states = input_data.get("actual_states", {})
        plan = input_data.get("plan", {})

        # Monitor each action
        statuses = self._monitor_actions(
            executing_actions,
            expected_states,
            actual_states,
            plan
        )

        # Detect overall deviations
        overall_deviations = self._detect_overall_deviations(statuses, plan)

        # Compute metrics
        overall_progress = self._compute_overall_progress(statuses)
        health_score = self._compute_health_score(statuses)

        # Compute confidence
        confidence = health_score

        # Create NodeState
        state = NodeState(
            confidence=confidence,
            salience=min(1.0, 0.8 + len(overall_deviations) * 0.05),
            novelty=max(0.1, len(overall_deviations) * 0.15),
            utility=min(1.0, 0.7 + overall_progress * 0.3),
            risk=min(1.0, len(overall_deviations) * 0.2)
        )

        # Create trigger
        trigger = NodeTrigger(
            event_type="execution_monitoring_update",
            timestamp=int(time.time() * 1000)
        )

        # Build MATRIZ node
        matriz_node = {
            "id": str(uuid.uuid4()),
            "type": "AWARENESS",
            "state": {
                "confidence": state.confidence,
                "salience": state.salience,
                "novelty": state.novelty,
                "utility": state.utility,
                "risk": state.risk
            },
            "triggers": [{
                "event_type": trigger.event_type,
                "timestamp": trigger.timestamp
            }],
            "metadata": {
                "node_name": self.node_name,
                "tenant": self.tenant,
                "capabilities": self.capabilities,
                "processing_time": time.time() - start_time,
                "action_count": len(executing_actions)
            },
            "execution_statuses": [
                {
                    "action_id": s.action_id,
                    "action_name": s.action_name,
                    "progress": s.progress,
                    "status": s.status,
                    "deviations": s.deviations,
                    "issues": s.issues
                }
                for s in statuses
            ],
            "overall_deviations": overall_deviations,
            "metrics": {
                "overall_progress": overall_progress,
                "health_score": health_score
            }
        }

        return {
            "answer": {
                "execution_statuses": matriz_node["execution_statuses"],
                "overall_deviations": overall_deviations,
                "metrics": matriz_node["metrics"]
            },
            "confidence": confidence,
            "matriz_node": matriz_node,
            "processing_time": time.time() - start_time
        }

    def validate_output(self, output: Dict[str, Any]) -> bool:
        """Validate output structure."""
        required = ["answer", "confidence", "matriz_node", "processing_time"]
        if not all(k in output for k in required):
            return False

        if not 0.0 <= output["confidence"] <= 1.0:
            return False

        if "execution_statuses" not in output["answer"]:
            return False

        return True

    def _monitor_actions(
        self,
        executing_actions: List[dict],
        expected_states: Dict[str, dict],
        actual_states: Dict[str, dict],
        plan: dict
    ) -> List[ExecutionStatus]:
        """Monitor each executing action."""
        statuses = []

        for action in executing_actions:
            action_id = action.get("id", f"action_{len(statuses)}")
            action_name = action.get("name", f"Action {len(statuses)}")

            # Get expected and actual states
            expected = expected_states.get(action_id, {})
            actual = actual_states.get(action_id, {})

            # Compute progress
            progress = self._compute_progress(action, actual)

            # Determine status
            status = self._determine_status(action, actual, expected)

            # Detect deviations
            deviations = self._detect_deviations(expected, actual)

            # Identify issues
            issues = self._identify_issues(action, actual)

            statuses.append(
                ExecutionStatus(
                    action_id=action_id,
                    action_name=action_name,
                    progress=progress,
                    status=status,
                    deviations=deviations,
                    issues=issues
                )
            )

        return statuses

    def _compute_progress(self, action: dict, actual: dict) -> float:
        """Compute progress of action execution."""
        # Check for explicit progress
        if "progress" in actual:
            return min(1.0, max(0.0, actual["progress"]))

        # Estimate from completed steps
        total_steps = action.get("total_steps", 1)
        completed_steps = actual.get("completed_steps", 0)

        return min(1.0, completed_steps / max(1, total_steps))

    def _determine_status(
        self,
        action: dict,
        actual: dict,
        expected: dict
    ) -> str:
        """Determine current status of action."""
        # Check explicit status
        if "status" in actual:
            return actual["status"]

        # Infer from state
        if actual.get("completed", False):
            return "completed"
        elif actual.get("failed", False):
            return "failed"
        elif actual.get("blocked", False):
            return "blocked"
        else:
            return "running"

    def _detect_deviations(self, expected: dict, actual: dict) -> List[str]:
        """Detect deviations from expected state."""
        deviations = []

        # Compare expected vs actual metrics
        for metric in ["progress", "duration", "resource_usage"]:
            if metric in expected and metric in actual:
                expected_val = expected[metric]
                actual_val = actual[metric]

                # Check for significant deviation (>20%)
                if abs(expected_val - actual_val) / max(1, expected_val) > 0.2:
                    deviations.append(
                        f"{metric}: expected {expected_val}, actual {actual_val}"
                    )

        return deviations

    def _identify_issues(self, action: dict, actual: dict) -> List[str]:
        """Identify current issues with execution."""
        issues = []

        # Check for errors
        if actual.get("errors"):
            issues.append(f"Errors: {len(actual['errors'])} errors encountered")

        # Check for resource problems
        if actual.get("resource_shortage"):
            issues.append("Resource shortage detected")

        # Check for timeouts
        if actual.get("timeout"):
            issues.append("Action timeout")

        # Check for dependencies
        if actual.get("blocked_dependencies"):
            issues.append("Blocked by dependencies")

        return issues

    def _detect_overall_deviations(
        self,
        statuses: List[ExecutionStatus],
        plan: dict
    ) -> List[str]:
        """Detect overall deviations from plan."""
        deviations = []

        # Count failed actions
        failed = sum(1 for s in statuses if s.status == "failed")
        if failed > 0:
            deviations.append(f"{failed} actions failed")

        # Count blocked actions
        blocked = sum(1 for s in statuses if s.status == "blocked")
        if blocked > 0:
            deviations.append(f"{blocked} actions blocked")

        # Check overall progress vs expected
        overall_progress = self._compute_overall_progress(statuses)
        expected_progress = plan.get("expected_progress", 0.5)

        if overall_progress < expected_progress - 0.2:
            deviations.append(
                f"Behind schedule: {int(overall_progress * 100)}% vs expected {int(expected_progress * 100)}%"
            )

        return deviations

    def _compute_overall_progress(self, statuses: List[ExecutionStatus]) -> float:
        """Compute overall progress across all actions."""
        if not statuses:
            return 0.0

        return sum(s.progress for s in statuses) / len(statuses)

    def _compute_health_score(self, statuses: List[ExecutionStatus]) -> float:
        """Compute overall health score of execution."""
        if not statuses:
            return 0.5

        # Factors:
        # 1. Proportion of successful/running actions
        # 2. Average progress
        # 3. Issue count

        healthy = sum(1 for s in statuses if s.status in ["running", "completed"])
        health_ratio = healthy / len(statuses)

        avg_progress = self._compute_overall_progress(statuses)

        total_issues = sum(len(s.issues) for s in statuses)
        issue_penalty = min(0.3, total_issues * 0.05)

        return max(0.0, (health_ratio + avg_progress) / 2 - issue_penalty)
