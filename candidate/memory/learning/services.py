#!/usr/bin/env python3
"""
Learning Services
Dependency injection services for the learning module.
"""
from typing import Any, Optional

from hub.service_registry import get_service, inject_services, register_factory


class LearningService:
    """
    Service layer for learning operations.
    Uses dependency injection to avoid circular imports.
    """

    def __init__(self):
        # Services will be injected as needed
        self._memory = None
        self._identity = None
        self._consciousness = None
        self._initialized = False

    def _ensure_services(self):
        """Lazy load services to avoid circular imports"""
        if not self._initialized:
            try:
                self._memory = get_service("memory_service")
            except KeyError:
                self._memory = None

            try:
                self._identity = get_service("identity_service")
            except KeyError:
                self._identity = None

            try:
                self._consciousness = get_service("consciousness_service")
            except KeyError:
                self._consciousness = None

            self._initialized = True

    @inject_services(memory="memory_service", identity="identity_service")
    async def train(
        self,
        agent_id: str,
        training_data: dict[str, Any],
        config: Optional[dict[str, Any]] = None,
        memory=None,
        identity=None,
    ) -> dict[str, Any]:
        """
        Train a model with injected dependencies.
        """
        # Verify access through identity service
        if identity:
            if not await identity.verify_access(agent_id, "learning.train"):
                raise PermissionError(f"Agent {agent_id} lacks training access")

            # Log training event
            await identity.log_audit(agent_id, "learning.train", training_data)

        # Retrieve relevant memories for context
        if memory:
            context = await memory.retrieve_learning_context(agent_id, limit=100)
        else:
            context = []

        # Perform training
        result = await self._perform_training(agent_id=agent_id, data=training_data, context=context, config=config)

        # Store training results in memory
        if memory:
            await memory.store_learning_outcome(agent_id, result)

        return result

    async def _perform_training(
        self,
        agent_id: str,
        data: dict[str, Any],
        context: list[dict[str, Any]],
        config: Optional[dict[str, Any]],
    ) -> dict[str, Any]:
        """Perform actual training logic"""
        # Simplified training simulation
        return {
            "agent_id": agent_id,
            "training_complete": True,
            "metrics": {"loss": 0.234, "accuracy": 0.912, "iterations": 100},
            "context_used": len(context),
            "config": config or {},
        }

    @inject_services(consciousness="consciousness_service")
    async def conscious_learning(self, agent_id: str, experience: dict[str, Any], consciousness=None) -> dict[str, Any]:
        """
        Learning that integrates with consciousness for meta-cognitive awareness.
        """
        # Get consciousness state
        if consciousness:
            awareness = await consciousness.get_awareness_level(agent_id)

            # Adjust learning based on awareness
            if awareness > 0.7:
                # High awareness - more reflective learning
                learning_mode = "reflective"
            else:
                # Lower awareness - more reactive learning
                learning_mode = "reactive"
        else:
            learning_mode = "standard"

        # Perform learning with awareness integration
        result = await self.train(
            agent_id,
            experience,
            {"mode": learning_mode, "consciousness_integrated": True},
        )

        # Update consciousness with learning insights
        if consciousness:
            await consciousness.update_from_learning(agent_id, result)

        return result

    async def federated_learning(self, agent_ids: list[str], global_model: dict[str, Any]) -> dict[str, Any]:
        """
        Coordinate federated learning across multiple agents.
        """
        self._ensure_services()

        local_updates = []

        # Collect local updates from each agent
        for agent_id in agent_ids:
            local_update = await self.train(
                agent_id,
                {"model": global_model, "local_data": True},
                {"federated": True},
            )
            local_updates.append(local_update)

        # Aggregate updates
        aggregated = self._aggregate_updates(local_updates)

        # Distribute back to agents
        for agent_id in agent_ids:
            if self._memory:
                await self._memory.store_federated_update(agent_id, aggregated)

        return aggregated

    def _aggregate_updates(self, updates: list[dict[str, Any]]) -> dict[str, Any]:
        """Aggregate federated learning updates"""
        # Simplified aggregation
        avg_loss = sum(u["metrics"]["loss"] for u in updates) / len(updates)
        avg_acc = sum(u["metrics"]["accuracy"] for u in updates) / len(updates)

        return {
            "type": "federated_aggregate",
            "num_agents": len(updates),
            "aggregated_metrics": {"loss": avg_loss, "accuracy": avg_acc},
        }

    async def get_learning_status(self, agent_id: str) -> dict[str, Any]:
        """Get current learning status for an agent"""
        self._ensure_services()

        status = {
            "agent_id": agent_id,
            "active_learning": False,
            "total_training_sessions": 0,
            "last_training": None,
        }

        if self._memory:
            history = await self._memory.get_learning_history(agent_id)
            status.update(
                {
                    "total_training_sessions": len(history),
                    "last_training": history[-1]["timestamp"] if history else None,
                }
            )

        return status


# Create service factory
def create_learning_service():
    """Factory function for learning service"""
    from learning.learning_gateway import get_learning_gateway

    service = LearningService()
    service.gateway = get_learning_gateway()

    return service


# Register with hub on import

register_factory(
    "learning_service",
    create_learning_service,
    {"module": "learning", "provides": ["training", "inference", "federated_learning"]},
)