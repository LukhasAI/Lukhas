"""
Base class for all agent colonies.
"""

import logging
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional

from lukhas.core.actor_system import ActorRef, AIAgentActor, get_global_actor_system
from lukhas.core.colonies.supervisor_agent import SupervisorAgent
from lukhas.core.distributed_tracing import create_ai_tracer
from lukhas.core.efficient_communication import EfficientCommunicationFabric
from lukhas.core.event_sourcing import AIAgentAggregate, get_global_event_store
from lukhas.core.symbolism.methylation_model import MethylationModel
from lukhas.core.symbolism.tags import TagPermission, TagScope

logger = logging.getLogger(__name__)


@dataclass
class ConsensusResult:
    """Result of a consensus operation in a colony."""

    consensus_reached: bool
    decision: Any
    confidence: float
    votes: dict[str, Any]
    participation_rate: float
    dissent_reasons: list[str] = field(default_factory=list)


class BaseColony(ABC):
    """
    Base class for all agent colonies.

    A colony is a self-contained, independently deployable application
    that is responsible for a specific, high-level business or functional domain.
    """

    def __init__(self, colony_id: str, capabilities: list[str]):
        self.colony_id = colony_id
        self.capabilities = capabilities

        # Core components
        self.event_store = get_global_event_store()
        self.aggregate = AIAgentAggregate(self.colony_id, self.event_store)
        self.tracer = create_ai_tracer(self.colony_id)
        self.comm_fabric = EfficientCommunicationFabric(self.colony_id)
        self.methylation_model = MethylationModel()

        # Actor system integration
        self.actor_ref: Optional[ActorRef] = None
        self.actor_system = None

        # State
        self.is_running = False
        self.symbolic_carryover: dict[
            str, tuple[str, TagScope, TagPermission, float, Optional[float]]
        ] = {}
        self.tag_propagation_log: list[dict[str, Any]] = []
        self.fast_execution_blocked: bool = False
        self.supervisor_agent = SupervisorAgent()

        # Optional governance integration
        self.governance_colony: Optional[Any] = None

        logger.info(
            f"Colony {self.colony_id} initialized with capabilities: {self.capabilities}"
        )

    def set_governance_colony(self, colony: Any) -> None:
        """Attach a governance colony for ethical review."""
        self.governance_colony = colony

    async def start(self):
        """Start the colony."""
        if self.is_running:
            return

        # Start communication fabric
        await self.comm_fabric.start()

        # Get actor system and create actor
        self.actor_system = await get_global_actor_system()
        self.actor_ref = await self.actor_system.create_actor(
            AIAgentActor, self.colony_id, self.capabilities
        )

        # Create agent in event store
        correlation_id = str(uuid.uuid4())
        with self.tracer.trace_agent_operation(
            self.colony_id, "colony_creation"
        ) as ctx:
            self.aggregate.create_agent(self.capabilities, correlation_id)
            self.aggregate.commit_events()

            self.tracer.add_tag(ctx, "capabilities", self.capabilities)
            self.tracer.add_log(
                ctx,
                "colony_started",
                {
                    "event_store_connected": True,
                    "actor_system_connected": True,
                    "communication_fabric_ready": True,
                },
            )

        self.is_running = True
        logger.info(f"Colony {self.colony_id} started successfully")

    async def stop(self):
        """Stop the colony."""
        if not self.is_running:
            return

        self.is_running = False

        # Stop communication fabric
        await self.comm_fabric.stop()

        # Stop actor
        if self.actor_system and self.actor_ref:
            await self.actor_system.stop_actor(self.colony_id)

        logger.info(f"Colony {self.colony_id} stopped")

    @abstractmethod
    async def execute_task(
        self, task_id: str, task_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute a task."""

    def get_status(self) -> dict[str, Any]:
        """Get the status of the colony."""
        return {
            "colony_id": self.colony_id,
            "capabilities": self.capabilities,
            "is_running": self.is_running,
        }

    def link_symbolic_contexts(self, other_colony: "BaseColony"):
        """
        Simulate tag inheritance from another colony.
        """
        for tag_key, (
            tag_value,
            tag_scope,
            tag_permission,
            creation_time,
            lifespan,
        ) in other_colony.symbolic_carryover.items():
            if tag_scope == TagScope.GLOBAL and tag_permission == TagPermission.PUBLIC:
                self.symbolic_carryover[tag_key] = (
                    tag_value,
                    tag_scope,
                    tag_permission,
                    creation_time,
                    lifespan,
                )
                self.tag_propagation_log.append(
                    {
                        "tag": tag_key,
                        "value": tag_value,
                        "scope": tag_scope.value,
                        "permission": tag_permission.value,
                        "source": other_colony.colony_id,
                        "timestamp": time.time(),
                    }
                )

    def prune_expired_tags(self):
        """
        Remove expired tags from the symbolic carryover.
        """
        current_time = time.time()
        expired_tags = []
        for tag_key, (
            _,
            _,
            _,
            creation_time,
            lifespan,
        ) in self.symbolic_carryover.items():
            if lifespan is not None and current_time - creation_time > lifespan:
                expired_tags.append(tag_key)

        for tag_key in expired_tags:
            del self.symbolic_carryover[tag_key]
            logger.info(f"Pruned expired tag: {tag_key}")

    async def _pre_approve_if_ethical(
        self, task_id: str, task_data: dict[str, Any]
    ) -> bool:
        """Pass ethical tasks to governance for pre-approval."""
        if not self.governance_colony:
            return True

        tags = task_data.get("tags") or {}
        for _val, scope, _perm, _life in tags.values():
            if scope == TagScope.ETHICAL:
                return await self.governance_colony.pre_approve(task_id, task_data)
        return True

    def request_permission_escalation(
        self, tag_key: str, requested_permission: TagPermission
    ):
        """
        Request to escalate the permission of a tag.
        """
        logger.info(
            f"Colony {self.colony_id} is requesting to escalate permission for tag '{tag_key}' to '{requested_permission.value}'"
        )
        # In a real system, this would trigger a governance workflow.
        # For now, we'll just log the request.
        return True

    def override_tag(
        self,
        tag_key: str,
        new_value: Any,
        new_scope: TagScope,
        new_permission: TagPermission,
        new_lifespan: Optional[float] = None,
    ):
        """
        Override a tag's value, scope, and permission, if allowed.
        """
        if tag_key in self.symbolic_carryover:
            _, _, current_permission, _, _ = self.symbolic_carryover[tag_key]
            if current_permission == TagPermission.PRIVATE:
                logger.warning(f"Cannot override private tag '{tag_key}'")
                return False

        creation_time = time.time()
        new_lifespan = self.methylation_model.adjust_lifespan(new_scope, new_lifespan)
        self.symbolic_carryover[tag_key] = (
            new_value,
            new_scope,
            new_permission,
            creation_time,
            new_lifespan,
        )
        self.tag_propagation_log.append(
            {
                "tag": tag_key,
                "value": new_value,
                "scope": new_scope.value,
                "permission": new_permission.value,
                "source": self.colony_id,
                "timestamp": creation_time,
                "lifespan": new_lifespan,
                "action": "override",
            }
        )
        logger.info(f"Overrode tag '{tag_key}' in colony {self.colony_id}")
        return True

    def entangle_tags(
        self,
        tags: dict[str, tuple[str, TagScope, TagPermission, Optional[float]]],
    ):
        """Entangle provided tags with the colony's symbolic carryover and tracing baggage."""
        current_ctx = self.tracer.get_current_context()
        for tag_key, (
            tag_value,
            tag_scope,
            tag_permission,
            lifespan,
        ) in tags.items():
            creation_time = time.time()
            self.symbolic_carryover[tag_key] = (
                tag_value,
                tag_scope,
                tag_permission,
                creation_time,
                lifespan,
            )
            self.tag_propagation_log.append(
                {
                    "tag": tag_key,
                    "value": tag_value,
                    "scope": tag_scope.value,
                    "permission": tag_permission.value,
                    "source": "entangle",
                    "timestamp": creation_time,
                    "lifespan": lifespan,
                }
            )
            if current_ctx:
                current_ctx.set_baggage_item(tag_key, str(tag_value))
