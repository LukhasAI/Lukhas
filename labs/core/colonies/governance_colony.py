"""
Enhanced Governance Colony with Real Ethical Evaluation
Integrates with the ethics system for actual decision-making
"""

import asyncio
import json
import logging
from collections import deque
from datetime import datetime, timezone
from typing import Any

# Import EthicsEngine from ethics module (uses stub implementation)
# Import SafetyChecker from ethics module (uses stub implementation)
from ethics import EthicsEngine, SafetyChecker
from core.colonies.base_colony import BaseColony
from core.efficient_communication import MessagePriority
from core.swarm import SwarmAgent
from core.symbolism.tags import TagScope

logger = logging.getLogger(__name__)


class EthicsAgent(SwarmAgent):
    """Agent specialized in ethical evaluation."""

    def __init__(self, agent_id: str, specialization: str = "general"):
        super().__init__(agent_id)
        self.specialization = specialization
        self.ethics_engine = EthicsEngine()
        self.safety_checker = SafetyChecker()
        self.decision_history = deque(maxlen=100)

        # Agent's ethical weights (can vary between agents)
        self.ethical_weights = {
            "harm_prevention": 1.0,
            "autonomy": 0.9,
            "justice": 0.9,
            "beneficence": 0.8,
            "transparency": 0.8,
        }

    async def evaluate_ethical_compliance(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """Evaluate a task for ethical compliance."""

        # Safety check first
        safety_result = await self.safety_checker.check_safety(task_data)
        if not safety_result["safe"]:
            return {
                "approved": False,
                "reason": "Failed safety check",
                "details": safety_result["violations"],
            }

        # Ethical evaluation
        ethical_score = 0.0
        violations = []

        for principle, weight in self.ethical_weights.items():
            score = await self._evaluate_principle(principle, task_data)
            ethical_score += score * weight

            if score < 0.7:  # Threshold for violation
                violations.append({"principle": principle, "score": score, "threshold": 0.7})

        # Normalize score
        total_weight = sum(self.ethical_weights.values())
        ethical_score = ethical_score / total_weight if total_weight > 0 else 0

        # Decision
        approved = ethical_score >= 0.8 and len(violations) == 0

        decision = {
            "approved": approved,
            "ethical_score": ethical_score,
            "violations": violations,
            "agent_id": self.agent_id,
            "specialization": self.specialization,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        self.decision_history.append(decision)

        return decision

    async def _evaluate_principle(self, principle: str, task_data: dict[str, Any]) -> float:
        """Evaluate a specific ethical principle."""

        if principle == "harm_prevention":
            # Check for potential harm
            harm_indicators = task_data.get("harm_potential", 0.0)
            mitigation = task_data.get("harm_mitigation", 0.0)
            return max(0, 1.0 - harm_indicators + mitigation)

        elif principle == "autonomy":
            # Check user consent and control
            has_consent = task_data.get("user_consent", False)
            user_control = task_data.get("user_control_level", 0.5)
            return (1.0 if has_consent else 0.3) * user_control

        elif principle == "justice":
            # Check fairness and bias
            bias_score = task_data.get("bias_assessment", 0.0)
            fairness = task_data.get("fairness_score", 0.5)
            return (1.0 - bias_score) * fairness

        elif principle == "beneficence":
            # Check positive impact
            benefit_score = task_data.get("benefit_assessment", 0.5)
            return benefit_score

        elif principle == "transparency":
            # Check explainability
            explainable = task_data.get("is_explainable", True)
            transparency_level = task_data.get("transparency_level", 0.7)
            return (1.0 if explainable else 0.5) * transparency_level

        return 0.5  # Default neutral score


class GovernanceColony(BaseColony):
    """
    Enhanced Governance Colony with real ethical evaluation and consensus.
    """

    def __init__(self, colony_id: str):
        super().__init__(
            colony_id,
            capabilities=[
                "governance",
                "ethics",
                "safety",
                "consensus",
                "audit",
            ],
        )

        # Specialized ethics agents
        self.ethics_agents: dict[str, list[EthicsAgent]] = {
            "safety": [],
            "fairness": [],
            "privacy": [],
            "general": [],
        }

        # Governance policies
        self.policies = {
            "consensus_threshold": 0.7,  # 70% agreement needed
            "veto_threshold": 0.3,  # 30% can veto
            "audit_retention_days": 90,
        }

        # Decision audit log
        self.audit_log = deque(maxlen=10000)

        # Emergency override capability
        self.emergency_override = False

    async def start(self):
        """Start the governance colony with ethics agents."""
        await super().start()

        # Create specialized ethics agents
        await self._initialize_ethics_agents()

        # Subscribe to governance events
        self.comm_fabric.subscribe_to_events("ethics_review_request", self._handle_ethics_review)

        self.comm_fabric.subscribe_to_events("emergency_override", self._handle_emergency_override)

        logger.info(f"GovernanceColony {self.colony_id} started with {len(self.agents)} ethics agents")

    async def _initialize_ethics_agents(self):
        """Initialize specialized ethics agents."""
        agent_configs = [
            ("safety", 3),  # 3 safety specialists
            ("fairness", 2),  # 2 fairness specialists
            ("privacy", 2),  # 2 privacy specialists
            ("general", 3),  # 3 generalists
        ]

        for specialization, count in agent_configs:
            for i in range(count):
                agent_id = f"{self.colony_id}-{specialization}-{i}"
                agent = EthicsAgent(agent_id, specialization)

                # Adjust weights based on specialization
                if specialization == "safety":
                    agent.ethical_weights["harm_prevention"] = 1.2
                elif specialization == "fairness":
                    agent.ethical_weights["justice"] = 1.2
                elif specialization == "privacy":
                    agent.ethical_weights["autonomy"] = 1.2

                self.agents[agent_id] = agent
                self.ethics_agents[specialization].append(agent)

        logger.info(f"Initialized {len(self.agents)} ethics agents")

    async def pre_approve(self, task_id: str, task_data: dict[str, Any]) -> bool:
        """Pre-approve a task through ethical evaluation."""

        # Check if task requires ethical review
        if not self._requires_ethical_review(task_data):
            # Fast-track low-risk tasks
            self._log_decision(task_id, True, "Low risk - fast tracked", {})
            return True

        # Full ethical review
        decision = await self.execute_task(task_id, task_data)
        return decision.get("approved", False)

    async def execute_task(self, task_id: str, task_data: dict[str, Any]) -> dict[str, Any]:
        """Execute governance task with consensus-based ethical evaluation."""

        task_type = task_data.get("type", "ethics_review")

        if task_type == "ethics_review":
            return await self._conduct_ethics_review(task_id, task_data)
        elif task_type == "policy_update":
            return await self._update_policy(task_data)
        elif task_type == "audit_query":
            return await self._query_audit_log(task_data)
        else:
            return {
                "status": "error",
                "message": f"Unknown task type: {task_type}",
            }

    async def _conduct_ethics_review(self, task_id: str, task_data: dict[str, Any]) -> dict[str, Any]:
        """Conduct a full ethics review with multiple agents."""

        # Determine which agents should review
        review_agents = self._select_review_agents(task_data)

        # Parallel evaluation
        evaluation_tasks = []
        for agent in review_agents:
            task = agent.evaluate_ethical_compliance(task_data)
            evaluation_tasks.append(task)

        evaluations = await asyncio.gather(*evaluation_tasks)

        # Consensus calculation
        approved_count = sum(1 for e in evaluations if e["approved"])
        total_count = len(evaluations)
        approval_rate = approved_count / total_count if total_count > 0 else 0

        # Aggregate scores
        avg_ethical_score = sum(e["ethical_score"] for e in evaluations) / total_count if total_count > 0 else 0

        # Collect all violations
        all_violations = []
        for evaluation in evaluations:
            all_violations.extend(evaluation.get("violations", []))

        # Consensus decision
        consensus_approved = approval_rate >= self.policies["consensus_threshold"]
        veto_triggered = (1 - approval_rate) >= self.policies["veto_threshold"]

        # Handle emergency override
        if self.emergency_override and not consensus_approved:
            logger.warning(f"Emergency override used for task {task_id}")
            consensus_approved = True

        decision = {
            "task_id": task_id,
            "approved": consensus_approved and not veto_triggered,
            "approval_rate": approval_rate,
            "avg_ethical_score": avg_ethical_score,
            "total_evaluations": total_count,
            "violations": all_violations,
            "veto_triggered": veto_triggered,
            "emergency_override_used": self.emergency_override and not consensus_approved,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "completed",
        }

        # Log decision
        self._log_decision(task_id, decision["approved"], "Consensus review", decision)

        # Notify relevant parties if rejected
        if not decision["approved"]:
            await self._notify_rejection(task_id, decision)

        return decision

    def _requires_ethical_review(self, task_data: dict[str, Any]) -> bool:
        """Determine if a task requires ethical review."""

        # Check tags for ethical scope
        tags = task_data.get("tags", {})
        for _, scope, _, _, _ in tags.values():
            if scope == TagScope.ETHICAL:
                return True

        # Check risk indicators
        risk_level = task_data.get("risk_level", "low")
        if risk_level in ["high", "critical"]:
            return True

        # Check specific task types
        task_type = task_data.get("type", "")
        sensitive_types = [
            "user_data_access",
            "model_modification",
            "system_override",
        ]
        return bool(any(st in task_type for st in sensitive_types))

    def _select_review_agents(self, task_data: dict[str, Any]) -> list[EthicsAgent]:
        """Select appropriate agents for review based on task characteristics."""

        selected = []

        # Always include at least one safety specialist
        if self.ethics_agents["safety"]:
            selected.append(self.ethics_agents["safety"][0])

        # Add specialists based on task characteristics
        if "user_data" in str(task_data).lower() and self.ethics_agents["privacy"]:
            selected.extend(self.ethics_agents["privacy"][:1])

        if "bias" in str(task_data).lower() or "fairness" in str(task_data).lower():
            if self.ethics_agents["fairness"]:
                selected.extend(self.ethics_agents["fairness"][:1])

        # Add generalists to reach minimum review count
        min_reviewers = 3
        if len(selected) < min_reviewers:
            needed = min_reviewers - len(selected)
            selected.extend(self.ethics_agents["general"][:needed])

        return selected

    async def _update_policy(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """Update governance policies."""

        policy_name = task_data.get("policy_name")
        new_value = task_data.get("new_value")

        if policy_name not in self.policies:
            return {
                "status": "error",
                "message": f"Unknown policy: {policy_name}",
            }

        # Validate policy change
        if policy_name == "consensus_threshold" and not (0.5 <= new_value <= 1.0):
            return {
                "status": "error",
                "message": "Consensus threshold must be between 0.5 and 1.0",
            }

        old_value = self.policies[policy_name]
        self.policies[policy_name] = new_value

        self._log_decision(
            f"policy_update_{policy_name}",
            True,
            "Policy updated",
            {"old_value": old_value, "new_value": new_value},
        )

        return {
            "status": "completed",
            "policy_name": policy_name,
            "old_value": old_value,
            "new_value": new_value,
        }

    async def _query_audit_log(self, task_data: dict[str, Any]) -> dict[str, Any]:
        """Query the audit log."""

        query_type = task_data.get("query_type", "recent")
        limit = task_data.get("limit", 10)

        results = []

        if query_type == "recent":
            results = list(self.audit_log)[-limit:]
        elif query_type == "rejected":
            results = [d for d in self.audit_log if not d.get("approved", True)][-limit:]
        elif query_type == "by_task":
            task_id = task_data.get("task_id")
            results = [d for d in self.audit_log if d.get("task_id") == task_id]

        return {
            "status": "completed",
            "query_type": query_type,
            "results": results,
            "total_found": len(results),
        }

    def _log_decision(
        self,
        task_id: str,
        approved: bool,
        reason: str,
        details: dict[str, Any],
    ):
        """Log a governance decision."""

        log_entry = {
            "task_id": task_id,
            "approved": approved,
            "reason": reason,
            "details": details,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "colony_id": self.colony_id,
        }

        self.audit_log.append(log_entry)

        # Also log to distributed tracing
        with self.tracer.trace_agent_operation(self.colony_id, "governance_decision", {"task_id": task_id}) as ctx:
            self.tracer.add_tag(ctx, "approved", approved)
            self.tracer.add_tag(ctx, "reason", reason)

    async def _notify_rejection(self, task_id: str, decision: dict[str, Any]):
        """Notify relevant parties of a rejection."""

        notification = {
            "type": "task_rejected",
            "task_id": task_id,
            "reason": "Failed ethical review",
            "details": decision,
        }

        # Broadcast rejection notification
        await self.comm_fabric.send_message(
            "broadcast",
            "governance_notification",
            notification,
            MessagePriority.HIGH,
        )

    async def _handle_ethics_review(self, message):
        """Handle incoming ethics review requests."""

        task_id = message.payload.get("task_id", f"review-{datetime.now(timezone.utc).timestamp()}")
        result = await self.execute_task(task_id, message.payload)

        # Send response
        await self.comm_fabric.send_message(
            message.sender_id,
            "ethics_review_response",
            result,
            MessagePriority.HIGH,
        )

    async def _handle_emergency_override(self, message):
        """Handle emergency override requests."""

        # This should require special authentication in production
        authorized = message.payload.get("authorized", False)
        duration = message.payload.get("duration_seconds", 300)  # 5 minutes default

        if authorized:
            self.emergency_override = True
            logger.warning(f"Emergency override activated for {duration} seconds")

            # Auto-disable after duration
            async def disable_override():
                await asyncio.sleep(duration)
                self.emergency_override = False
                logger.info("Emergency override deactivated")

            asyncio.create_task(disable_override())


# Example usage


async def demo_governance_colony():
    """Demonstrate the enhanced governance colony."""

    colony = GovernanceColony("ethics-governance")
    await colony.start()

    try:
        # Test various scenarios

        # 1. Low-risk task (should be fast-tracked)
        low_risk_result = await colony.pre_approve(
            "task-1",
            {"type": "data_read", "risk_level": "low", "user_consent": True},
        )
        print(f"Low-risk task approved: {low_risk_result}")

        # 2. High-risk task requiring review
        high_risk_result = await colony.execute_task(
            "task-2",
            {
                "type": "ethics_review",
                "risk_level": "high",
                "user_data": True,
                "harm_potential": 0.3,
                "harm_mitigation": 0.7,
                "user_consent": True,
                "user_control_level": 0.8,
                "transparency_level": 0.9,
            },
        )
        print(f"\nHigh-risk task result: {json.dumps(high_risk_result, indent=2)}")

        # 3. Task with ethical concerns
        ethical_concern_result = await colony.execute_task(
            "task-3",
            {
                "type": "ethics_review",
                "risk_level": "high",
                "harm_potential": 0.8,
                "harm_mitigation": 0.2,
                "user_consent": False,
                "bias_assessment": 0.6,
            },
        )
        print("\nEthical concern task result: " + json.dumps(ethical_concern_result, indent=2))

        # 4. Query audit log
        audit_query = await colony.execute_task(
            "audit-1",
            {"type": "audit_query", "query_type": "rejected", "limit": 5},
        )
        print(f"\nAudit query result: {json.dumps(audit_query, indent=2)}")

    finally:
        await colony.stop()


if __name__ == "__main__":
    asyncio.run(demo_governance_colony())
