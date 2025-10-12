"""
Example integration of audit trail into Cognitive AI systems
Shows best practices for comprehensive audit logging
"""

import asyncio
from datetime import datetime
from typing import Any

from lukhas.core.audit import (  # noqa: F401 # TODO[T4-UNUSED-IMPORT]: kept for core infrastructure (review and implement)  # noqa: invalid-syntax
from datetime import timezone
    AuditEventType,  # noqa: invalid-syntax
    AuditSeverity,
    audit_decision,
    audit_learning,
    audit_operation,
    audit_security,
    get_audit_trail,
)  # noqa: invalid-syntax


class AuditedMemorySystem:
    """Example of memory system with integrated audit trail"""

    def __init__(self):
        self.audit = get_audit_trail()
        self.memories = {}

    @audit_operation("memory.store")
    async def store_memory(self, memory_id: str, content: dict[str, Any]) -> bool:
        """Store a memory with full audit trail"""
        # Manual audit log for more detail
        await self.audit.log_event(
            AuditEventType.MEMORY_STORED,
            "memory_system",
            {
                "memory_id": memory_id,
                "content_type": content.get("type", "unknown"),
                "size_bytes": len(str(content)),
                "emotional_valence": content.get("emotion", {}).get("valence", 0),
            },
            tags={"memory", "storage"},
        )

        # Store memory
        self.memories[memory_id] = content
        return True

    async def recall_memory(self, query: str) -> list[dict[str, Any]]:
        """Recall memories with audit trail"""
        start_time = datetime.now(timezone.utc)

        # Log recall attempt
        event_id = await self.audit.log_event(
            AuditEventType.MEMORY_RECALLED,
            "memory_system",
            {
                "query": query,
                "query_length": len(query),
                "memory_count": len(self.memories),
            },
        )

        # Perform recall (simplified)
        results = [m for m in self.memories.values() if query.lower() in str(m).lower()]

        # Log recall results
        await self.audit.log_event(
            AuditEventType.MEMORY_RECALLED,
            "memory_system",
            {
                "query": query,
                "results_count": len(results),
                "recall_time_ms": (datetime.now(timezone.utc) - start_time).total_seconds() * 1000,
            },
            parent_id=event_id,
        )

        return results


class AuditedDecisionEngine:
    """Example of decision engine with audit trail"""

    def __init__(self):
        self.audit = get_audit_trail()

    @audit_decision("action_selection")
    async def select_action(
        self, state: dict[str, Any], options: list[str]
    ) -> tuple[str, float, list[dict[str, float]]]:
        """Select action with full decision audit trail"""
        # Evaluate each option
        evaluations = []
        for option in options:
            score = self._evaluate_option(state, option)
            evaluations.append({"option": option, "score": score})

        # Sort by score
        evaluations.sort(key=lambda x: x["score"], reverse=True)

        # Select best option
        best_option = evaluations[0]["option"]
        confidence = evaluations[0]["score"]

        # Return decision with alternatives for audit
        return best_option, confidence, evaluations


class AuditedLearningSystem:
    """Example of learning system with audit trail"""

    def __init__(self):
        self.audit = get_audit_trail()
        self.knowledge_base = {}

    @audit_learning("concept_acquisition")
    async def learn_concept(self, concept: str, data: dict[str, Any]) -> dict[str, Any]:
        """Learn new concept with audit trail"""
        # Process learning
        existing_knowledge = self.knowledge_base.get(concept, {})

        # Integrate new data
        updated_knowledge = self._integrate_knowledge(existing_knowledge, data)

        # Calculate learning metrics
        complexity = len(str(updated_knowledge))
        improvement = complexity - len(str(existing_knowledge))

        # Store updated knowledge
        self.knowledge_base[concept] = updated_knowledge

        # Return learning result for audit
        return {
            "topic": concept,
            "progress": min(1.0, improvement / 100),
            "knowledge": {
                "type": "conceptual",
                "complexity": complexity,
                "integrated": True,
            },
            "metrics": {
                "knowledge_gain": improvement,
                "total_concepts": len(self.knowledge_base),
            },
        }

    def _integrate_knowledge(self, existing: dict, new: dict) -> dict:
        """Integrate new knowledge with existing"""
        # Simplified integration
        result = existing.copy()
        result.update(new)
        return result


class AuditedSecurityGateway:
    """Example of security gateway with audit trail"""

    def __init__(self):
        self.audit = get_audit_trail()
        self.access_rules = {}

    @audit_security("resource_access")
    async def validate_access(self, user: str, resource: str, operation: str) -> dict[str, Any]:
        """Validate access with security audit trail"""
        # Check access rules
        user_rules = self.access_rules.get(user, {})
        resource_rules = user_rules.get(resource, [])

        allowed = operation in resource_rules

        # Additional security checks
        if not allowed:
            # Log potential security issue
            await self.audit.log_security_event(
                threat_type="unauthorized_access_attempt",
                threat_level="MEDIUM",
                source=f"user:{user}",
                action_taken="access_denied",
                blocked=True,
            )

        return {
            "allowed": allowed,
            "reason": ("permission_granted" if allowed else "insufficient_permissions"),
            "user": user,
            "resource": resource,
            "operation": operation,
        }


async def example_audit_workflow():
    """Example workflow showing comprehensive audit integration"""

    # Initialize systems
    memory = AuditedMemorySystem()
    decision = AuditedDecisionEngine()
    learning = AuditedLearningSystem()
    security = AuditedSecurityGateway()
    audit = get_audit_trail()

    # Log workflow start
    workflow_id = await audit.log_event(
        AuditEventType.SYSTEM_START,
        "example_workflow",
        {"workflow": "audit_integration_demo"},
        tags={"demo", "workflow"},
    )

    try:
        # Security check
        access = await security.validate_access("demo_user", "memories", "write")

        if access["allowed"]:
            # Store memory
            await memory.store_memory(
                "demo_1",
                {
                    "content": "Important learning",
                    "type": "conceptual",
                    "emotion": {"valence": 0.8},
                },
            )

            # Learn from memory
            result = await learning.learn_concept(
                "audit_systems",
                {"importance": "critical", "complexity": "high"},
            )

            # Make decision based on learning
            decision_result = await decision.select_action(
                {"knowledge_level": result["metrics"]["total_concepts"]},
                ["continue_learning", "apply_knowledge", "rest"],
            )

            # Log workflow completion
            await audit.log_event(
                AuditEventType.SYSTEM_STOP,
                "example_workflow",
                {
                    "workflow": "audit_integration_demo",
                    "outcome": "success",
                    "decision": decision_result[0],
                },
                parent_id=workflow_id,
            )

    except Exception as e:
        # Log workflow error
        await audit.log_event(
            AuditEventType.SYSTEM_ERROR,
            "example_workflow",
            {"workflow": "audit_integration_demo", "error": str(e)},
            severity=AuditSeverity.ERROR,
            parent_id=workflow_id,
        )
        raise

    # Generate analytics
    analytics = await audit.get_analytics_summary()
    print(f"Workflow complete. Total events: {analytics['total_events']}")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_audit_workflow())
