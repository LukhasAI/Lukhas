"""
Reasoning Colony - A specialized colony for reasoning tasks.
"""

import asyncio
import logging
import time
import uuid
from typing import Any, Dict, List, Optional

from core.colonies.base_colony import BaseColony
from core.efficient_communication import MessagePriority
from core.symbolic.collapse.vector_ops import vector_collapse
from core.symbolism.tags import TagPermission, TagScope

try:
    from memory.systems.agent_memory import SymbolAwareTieredMemory
except ImportError:
    # Create a placeholder if import fails
    class SymbolAwareTieredMemory:
        pass


logger = logging.getLogger(__name__)


class ReasoningColony(BaseColony):
    """
    A specialized colony for reasoning tasks.
    """

    def __init__(
        self, colony_id: str, memory_system: Optional[SymbolAwareTieredMemory] = None
    ):
        super().__init__(
            colony_id, capabilities=["reasoning", "analysis", "problem_solving"]
        )
        # Symbol-aware memory system for contextual decisions
        self.memory_system = memory_system or SymbolAwareTieredMemory()

    async def start(self):
        await super().start()
        # Subscribe to relevant events
        self.comm_fabric.subscribe_to_events(
            "collaboration_request", self._handle_collaboration_request
        )
        self.comm_fabric.subscribe_to_events(
            "task_assignment", self._handle_task_assignment
        )
        logger.info(
            f"ReasoningColony {self.colony_id} started and subscribed to events."
        )

    async def execute_task(
        self, task_id: str, task_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a reasoning task.
        """
        correlation_id = str(uuid.uuid4())

        self.prune_expired_tags()

        if any(
            perm == TagPermission.RESTRICTED
            for _, _, perm, _ in task_data.get("tags", {}).values()
        ):
            self.fast_execution_blocked = True
            return await self.supervisor_agent.review_task(
                self.colony_id, task_id, task_data
            )

        self.propagate_tags(task_data, self.colony_id)

        with self.tracer.trace_agent_operation(
            self.colony_id, "task_execution", task_data
        ) as ctx:
            dream_context: List[Dict[str, Any]] = []
            if task_data.get("high_stakes"):
                dream_context = self.memory_system.get_dream_flagged()
                self.tracer.add_log(
                    ctx, "dream_context_loaded", {"count": len(dream_context)}
                )

            # Record task assignment in event store
            task_data_for_event = task_data.copy()
            if "tags" in task_data_for_event:
                task_data_for_event["tags"] = {
                    k: (v[0], v[1].value)
                    for k, v in task_data_for_event["tags"].items()
                }
            self.aggregate.assign_task(task_id, task_data_for_event, correlation_id)
            self.aggregate.commit_events()

            self.tracer.add_log(
                ctx,
                "task_assigned",
                {"task_id": task_id, "task_type": task_data.get("type", "unknown")},
            )

            # Execute task via actor system
            if self.actor_ref:
                try:
                    # Send task to actor
                    response = await self.actor_ref.ask(
                        "assign_task",
                        {"task_id": task_id, **task_data},
                        timeout=10.0,
                        correlation_id=correlation_id,
                    )

                    self.tracer.add_tag(ctx, "actor_response", response["status"])

                    if response["status"] == "accepted":
                        # Simulate task processing
                        with self.tracer.trace_operation("task_processing") as proc_ctx:
                            await asyncio.sleep(0.1)  # Simulate work

                            # Check if collaboration is needed
                            if task_data.get("requires_collaboration"):
                                collab_result = await self._collaborate_on_task(
                                    task_id, task_data, correlation_id
                                )
                                self.tracer.add_tag(proc_ctx, "collaboration", True)
                                self.tracer.add_tag(
                                    proc_ctx,
                                    "collaboration_success",
                                    collab_result["success"],
                                )

                        # Complete task
                        result = {
                            "status": "completed",
                            "task_id": task_id,
                            "output": f"Processed {task_data.get('type', 'unknown')} task",
                            "processing_time": 0.1,
                            "energy_efficiency": 0.95,
                            "context": {"dream_memories_used": len(dream_context)},
                        }

                        # Notify actor of completion
                        await self.actor_ref.tell(
                            "complete_task",
                            {"task_id": task_id, "result": result},
                            correlation_id=correlation_id,
                        )

                        # Record completion in event store
                        self.aggregate.complete_task(task_id, result, correlation_id)
                        self.aggregate.commit_events()

                        self.tracer.add_log(ctx, "task_completed", result)

                        return result

                    else:
                        error_result = {
                            "status": "failed",
                            "task_id": task_id,
                            "error": "Task rejected by actor",
                            "reason": response.get("reason", "unknown"),
                        }
                        self.tracer.add_tag(ctx, "error", True)
                        return error_result

                except Exception as e:
                    error_result = {
                        "status": "failed",
                        "task_id": task_id,
                        "error": str(e),
                    }
                    self.tracer.add_tag(ctx, "error", True)
                    self.tracer.add_log(ctx, "execution_error", {"error": str(e)})
                    return error_result

            else:
                return {
                    "status": "failed",
                    "task_id": task_id,
                    "error": "Actor system not available",
                }

    async def _collaborate_on_task(
        self, task_id: str, task_data: Dict[str, Any], correlation_id: str
    ) -> Dict[str, Any]:
        """
        Collaborate with other agents on a task
        """
        required_capability = task_data.get("required_capability", "memory")

        with self.tracer.trace_agent_collaboration(
            self.colony_id, "unknown", "capability_request"
        ) as ctx:

            # Send collaboration request via efficient communication
            success = await self.comm_fabric.send_message(
                "broadcast",  # Would be specific agents in real system
                "collaboration_request",
                {
                    "task_id": task_id,
                    "required_capability": required_capability,
                    "requesting_agent": self.colony_id,
                    "correlation_id": correlation_id,
                },
                MessagePriority.HIGH,
            )

            self.tracer.add_tag(ctx, "broadcast_success", success)

            if success:
                # Simulate receiving collaboration response
                await asyncio.sleep(0.05)

                return {
                    "success": True,
                    "collaborator": "simulated-partner",
                    "result": "collaborative_analysis_complete",
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to send collaboration request",
                }

    async def _handle_collaboration_request(self, message):
        """Handle incoming collaboration requests"""
        payload = message.payload
        required_capability = payload.get("required_capability")

        correlation_id = payload.get("correlation_id", str(uuid.uuid4()))

        with self.tracer.trace_agent_collaboration(
            payload.get("requesting_agent", "unknown"),
            self.colony_id,
            "collaboration_response",
        ) as ctx:

            if required_capability in self.capabilities:
                # We can help!
                response = {
                    "status": "available",
                    "agent_id": self.colony_id,
                    "capability": required_capability,
                }

                # Send response
                await self.comm_fabric.send_message(
                    payload.get("requesting_agent"),
                    "collaboration_response",
                    response,
                    MessagePriority.HIGH,
                )

                self.tracer.add_tag(ctx, "can_collaborate", True)
                self.tracer.add_log(ctx, "collaboration_accepted", response)

            else:
                self.tracer.add_tag(ctx, "can_collaborate", False)

    def propagate_tags(self, task_data: Dict[str, Any], source: str):
        """Propagate symbolic tags through the colony."""

        collapse_vector = task_data.get("collapse_vector")
        computed_scope = None
        if collapse_vector:
            try:
                computed_scope = vector_collapse(collapse_vector)
            except Exception as exc:  # pragma: no cover - log then ignore
                logger.warning("vector_collapse failed", exc_info=exc)

        if "tags" in task_data:
            for tag_key, (tag_value, tag_scope, tag_permission, lifespan) in list(
                task_data["tags"].items()
            ):
                if computed_scope and tag_scope is None:
                    tag_scope = computed_scope

                creation_time = time.time()
                self.symbolic_carryover[tag_key] = (
                    tag_value,
                    tag_scope,
                    tag_permission,
                    creation_time,
                    lifespan,
                )
                # Update original task_data to reflect resolved scope
                task_data["tags"][tag_key] = (
                    tag_value,
                    tag_scope,
                    tag_permission,
                    lifespan,
                )
                self.tag_propagation_log.append(
                    {
                        "tag": tag_key,
                        "value": tag_value,
                        "scope": (
                            tag_scope.value
                            if isinstance(tag_scope, TagScope)
                            else str(tag_scope)
                        ),
                        "permission": tag_permission.value,
                        "source": source,
                        "timestamp": creation_time,
                        "lifespan": lifespan,
                    }
                )

            logger.info(
                f"Propagated tags to colony {self.colony_id}: {self.symbolic_carryover}"
            )

    async def _handle_task_assignment(self, message):
        """Handle incoming task assignments"""
        payload = message.payload
        task_id = payload.get("task_id")

        if task_id:
            logger.info(f"Colony {self.colony_id} received external task {task_id}")
            # Would execute the task here in a real system
