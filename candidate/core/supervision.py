"""
Supervision Hierarchies and Fault Tolerance for Actor System
Addresses TODO 41: Inherent Fault Tolerance and Resilience

This module implements sophisticated supervision strategies for the actor model,
enabling self-healing systems through hierarchical error handling.
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

from bio.bio_utilities import simulate_colony_self_repair
from lukhas.core.actor_system import Actor, ActorMessage, ActorRef

logger = logging.getLogger(__name__)


class SupervisionDirective(Enum):
    """Directives that a supervisor can return"""

    RESUME = "resume"  # Resume the actor, keeping its state
    RESTART = "restart"  # Restart the actor, clearing its state
    STOP = "stop"  # Stop the actor permanently
    ESCALATE = "escalate"  # Escalate to the parent supervisor


class RestartPolicy(Enum):
    """When to restart child actors"""

    NEVER = "never"  # Never restart
    ALWAYS = "always"  # Always restart on failure
    ON_FAILURE = "on_failure"  # Restart only on failure
    ON_STOP = "on_stop"  # Restart even on normal stop


@dataclass
class FailureInfo:
    """Information about an actor failure"""

    actor_id: str
    error: Exception
    timestamp: float
    failure_count: int
    message: Optional[ActorMessage] = None
    stack_trace: Optional[str] = None


@dataclass
class SupervisionStrategy:
    """Configuration for supervision behavior"""

    max_failures: int = 3
    within_time_window: float = 60.0  # seconds
    restart_policy: RestartPolicy = RestartPolicy.ON_FAILURE
    restart_delay: float = 0.1  # seconds
    backoff_multiplier: float = 2.0  # exponential backoff
    max_restart_delay: float = 30.0  # max delay between restarts

    def calculate_restart_delay(self, failure_count: int) -> float:
        """Calculate delay before restart using exponential backoff"""
        delay = self.restart_delay * (self.backoff_multiplier ** (failure_count - 1))
        return min(delay, self.max_restart_delay)


class SupervisionDecider(ABC):
    """Abstract base for custom supervision decision logic"""

    @abstractmethod
    async def decide(self, failure: FailureInfo) -> SupervisionDirective:
        """Decide what to do with a failed actor"""


class DefaultSupervisionDecider(SupervisionDecider):
    """Default supervision decider with configurable thresholds"""

    def __init__(self, strategy: SupervisionStrategy):
        self.strategy = strategy
        self.failure_history: dict[str, list[float]] = {}

    async def decide(self, failure: FailureInfo) -> SupervisionDirective:
        """Decide based on failure history and strategy"""
        actor_id = failure.actor_id
        current_time = failure.timestamp

        # Update failure history
        if actor_id not in self.failure_history:
            self.failure_history[actor_id] = []

        # Remove old failures outside the time window
        self.failure_history[actor_id] = [
            t for t in self.failure_history[actor_id] if current_time - t <= self.strategy.within_time_window
        ]

        # Add current failure
        self.failure_history[actor_id].append(current_time)

        # Check if we've exceeded max failures
        failure_count = len(self.failure_history[actor_id])

        if failure_count > self.strategy.max_failures:
            logger.warning(f"Actor {actor_id} exceeded max failures " f"({failure_count}/{self.strategy.max_failures})")
            return SupervisionDirective.STOP

        # Check restart policy
        if self.strategy.restart_policy == RestartPolicy.NEVER:
            return SupervisionDirective.STOP
        elif self.strategy.restart_policy == RestartPolicy.ALWAYS:
            return SupervisionDirective.RESTART
        elif self.strategy.restart_policy == RestartPolicy.ON_FAILURE:
            # Restart on exceptions, stop on normal termination
            if isinstance(failure.error, Exception):
                return SupervisionDirective.RESTART
            else:
                return SupervisionDirective.STOP

        return SupervisionDirective.RESUME


class AllForOneStrategy(SupervisionDecider):
    """If one child fails, stop all children"""

    async def decide(self, failure: FailureInfo) -> SupervisionDirective:
        return SupervisionDirective.STOP


class OneForOneStrategy(SupervisionDecider):
    """Only the failed child is affected"""

    def __init__(self, strategy: SupervisionStrategy):
        self.default_decider = DefaultSupervisionDecider(strategy)

    async def decide(self, failure: FailureInfo) -> SupervisionDirective:
        return await self.default_decider.decide(failure)


class RestForOneStrategy(SupervisionDecider):
    """Stop the failed child and all children started after it"""

    def __init__(self, strategy: SupervisionStrategy):
        self.default_decider = DefaultSupervisionDecider(strategy)
        self.start_order: list[str] = []

    def register_child(self, actor_id: str):
        """Register a child in start order"""
        if actor_id not in self.start_order:
            self.start_order.append(actor_id)

    async def decide(self, failure: FailureInfo) -> SupervisionDirective:
        # This strategy requires special handling in the supervisor
        return await self.default_decider.decide(failure)

    def get_affected_children(self, failed_actor_id: str) -> list[str]:
        """Get all children that should be stopped"""
        try:
            index = self.start_order.index(failed_actor_id)
            return self.start_order[index:]
        except ValueError:
            return [failed_actor_id]


class CircuitBreaker:
    """Circuit breaker pattern for cascading failure prevention"""

    def __init__(
        self,
        failure_threshold: int = 5,
        reset_timeout: float = 60.0,
        half_open_requests: int = 3,
    ):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.half_open_requests = half_open_requests

        self.failure_count = 0
        self.last_failure_time = 0.0
        self.success_count = 0
        self.state = "closed"  # closed, open, half_open

    def record_success(self):
        """Record a successful operation"""
        if self.state == "half_open":
            self.success_count += 1
            if self.success_count >= self.half_open_requests:
                self.reset()
        elif self.state == "closed":
            self.failure_count = 0

    def record_failure(self):
        """Record a failed operation"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")

    def can_proceed(self) -> bool:
        """Check if operation can proceed"""
        if self.state == "open" and time.time() - self.last_failure_time > self.reset_timeout:
            self.state = "half_open"
            self.success_count = 0
            logger.info("Circuit breaker entering half-open state")

        if self.state == "half_open":
            return self.success_count < self.half_open_requests

        return self.state == "closed"

    def reset(self):
        """Reset the circuit breaker"""
        self.state = "closed"
        self.failure_count = 0
        self.success_count = 0
        logger.info("Circuit breaker reset to closed state")


class SupervisorActor(Actor):
    """
    Enhanced actor with supervision capabilities
    Manages child actors and handles their failures
    """

    def __init__(
        self,
        actor_id: str,
        supervision_strategy: Optional[SupervisionStrategy] = None,
        supervision_decider: Optional[SupervisionDecider] = None,
        enable_self_repair: bool = False,
    ):
        super().__init__(actor_id)

        self.supervision_strategy = supervision_strategy or SupervisionStrategy()
        self.supervision_decider = supervision_decider or DefaultSupervisionDecider(self.supervision_strategy)

        # Track child actor metadata
        self.child_metadata: dict[str, dict[str, Any]] = {}
        self.enable_self_repair = enable_self_repair
        self.health_metrics = {
            "attempts": 0,
            "health": 0.0,
        }

        # Circuit breaker for cascading failure prevention
        self.circuit_breaker = CircuitBreaker()

        # Register supervision message handlers
        self.register_handler("child_failed", self._handle_child_failure)
        self.register_handler("child_terminated", self._handle_child_terminated)
        self.register_handler("supervise_child", self._handle_supervise_child)

    async def create_child(
        self,
        child_class: type,
        child_id: str,
        restart_with_state: Optional[dict[str, Any]] = None,
        *args,
        **kwargs,
    ) -> ActorRef:
        """Create a supervised child actor"""
        if not self.circuit_breaker.can_proceed():
            raise RuntimeError(f"Circuit breaker open - cannot create child {child_id}")

        try:
            # Create the child actor
            child_ref = await super().create_child(child_class, child_id, *args, **kwargs)

            # Store metadata for supervision
            self.child_metadata[child_id] = {
                "class": child_class,
                "args": args,
                "kwargs": kwargs,
                "created_at": time.time(),
                "restart_count": 0,
                "last_restart": None,
                "state_snapshot": restart_with_state,
            }

            # Handle special strategies
            if isinstance(self.supervision_decider, RestForOneStrategy):
                self.supervision_decider.register_child(child_id)

            self.circuit_breaker.record_success()
            logger.info(f"Supervisor {self.actor_id} created child {child_id}")

            return child_ref

        except Exception:
            self.circuit_breaker.record_failure()
            raise

    async def _handle_child_failure(self, message: ActorMessage) -> dict[str, Any]:
        """Handle child actor failure notification"""
        child_id = message.payload.get("child_id")
        error = message.payload.get("error", "Unknown error")

        if child_id not in self.child_metadata:
            logger.error(f"Unknown child {child_id} reported failure")
            return {"status": "error", "reason": "unknown_child"}

        metadata = self.child_metadata[child_id]
        metadata["restart_count"] = metadata.get("restart_count", 0) + 1

        # Create failure info
        failure = FailureInfo(
            actor_id=child_id,
            error=Exception(error),
            timestamp=time.time(),
            failure_count=metadata["restart_count"],
            stack_trace=message.payload.get("stack_trace"),
        )

        # Get supervision directive
        directive = await self.supervision_decider.decide(failure)

        logger.info(f"Supervisor {self.actor_id} handling failure of {child_id}: {directive.value}")

        if self.enable_self_repair:
            try:
                repair_result = await simulate_colony_self_repair({"repair_protein": 1})
                self.health_metrics["attempts"] += 1
                self.health_metrics["health"] += repair_result.get("health_delta", 0.0)
                logger.info(
                    f"Self-repair initiated for {child_id}; "
                    f"health_delta={repair_result.get('health_delta', 0.0):.2f}"
                )
            except Exception as e:
                logger.error(f"Self-repair failed for {child_id}: {e}")

        # Execute directive
        if directive == SupervisionDirective.RESUME:
            # Just log and continue
            logger.info(f"Resuming actor {child_id} after failure")

        elif directive == SupervisionDirective.RESTART:
            await self._restart_child(child_id, metadata)

        elif directive == SupervisionDirective.STOP:
            await self._stop_child_tree(child_id)

        elif directive == SupervisionDirective.ESCALATE:
            # Escalate to our supervisor
            if self.supervisor:
                await self.supervisor.tell(
                    "child_failed",
                    {
                        "child_id": self.actor_id,
                        "error": f"Escalated from child {child_id}: {error}",
                        "original_failure": failure,
                    },
                )
            else:
                logger.error(f"Cannot escalate - no supervisor for {self.actor_id}")

        return {"status": "handled", "directive": directive.value}

    async def _restart_child(self, child_id: str, metadata: dict[str, Any]):
        """Restart a failed child actor"""
        try:
            # Calculate restart delay
            restart_count = metadata.get("restart_count", 1)
            delay = self.supervision_strategy.calculate_restart_delay(restart_count)

            logger.info(f"Restarting child {child_id} after {delay:.2f}s (attempt {restart_count})")

            # Stop the old instance
            if child_id in self.children:
                await self.actor_system.stop_actor(child_id)

            # Wait before restart
            await asyncio.sleep(delay)

            # Recreate the child
            child_class = metadata["class"]
            args = metadata.get("args", ())
            kwargs = metadata.get("kwargs", {})

            # Create new child with saved state if available
            child_ref = await self.create_child(
                child_class,
                child_id,
                restart_with_state=metadata.get("state_snapshot"),
                *args,
                **kwargs,
            )

            metadata["last_restart"] = time.time()

            # Notify child it was restarted
            await child_ref.tell(
                "restarted",
                {"restart_count": restart_count, "previous_failure": True},
            )

        except Exception as e:
            logger.error(f"Failed to restart child {child_id}: {e}")
            # Stop the child if restart fails
            await self._stop_child_tree(child_id)

    async def _stop_child_tree(self, child_id: str):
        """Stop a child and all its descendants"""
        if child_id in self.children:
            # Remove from our children
            del self.children[child_id]

            # Stop the actor
            await self.actor_system.stop_actor(child_id)

            # Clean up metadata
            if child_id in self.child_metadata:
                del self.child_metadata[child_id]

    async def _handle_child_terminated(self, message: ActorMessage) -> dict[str, Any]:
        """Handle normal child termination"""
        child_id = message.payload.get("child_id")

        if self.supervision_strategy.restart_policy == RestartPolicy.ON_STOP:
            # Treat as failure and potentially restart
            return await self._handle_child_failure(message)
        else:
            # Just clean up
            if child_id in self.children:
                del self.children[child_id]
            if child_id in self.child_metadata:
                del self.child_metadata[child_id]

            return {"status": "acknowledged"}

    async def _handle_supervise_child(self, message: ActorMessage) -> dict[str, Any]:
        """Handle request to supervise an existing actor"""
        child_id = message.payload.get("child_id")
        child_ref = self.actor_system.get_actor_ref(child_id)

        if not child_ref:
            return {"status": "error", "reason": "actor_not_found"}

        # Add to our children
        self.children[child_id] = child_ref

        # Set us as supervisor
        child_actor = self.actor_system.get_actor(child_id)
        if child_actor:
            child_actor.supervisor = ActorRef(self.actor_id, self.actor_system)

        return {"status": "supervising", "child_id": child_id}

    async def stop_all_children(self):
        """Stop all child actors"""
        stop_tasks = []
        for child_id in list(self.children.keys()):
            stop_tasks.append(self._stop_child_tree(child_id))

        if stop_tasks:
            await asyncio.gather(*stop_tasks, return_exceptions=True)

    async def pre_stop(self):
        """Called before supervisor stops"""
        await self.stop_all_children()

    def get_supervision_stats(self) -> dict[str, Any]:
        """Get supervision-specific statistics"""
        stats = {
            "supervisor_id": self.actor_id,
            "children_count": len(self.children),
            "circuit_breaker_state": self.circuit_breaker.state,
            "children": {},
            "health_metrics": self.health_metrics,
        }

        for child_id, metadata in self.child_metadata.items():
            stats["children"][child_id] = {
                "restart_count": metadata.get("restart_count", 0),
                "last_restart": metadata.get("last_restart"),
                "created_at": metadata.get("created_at"),
            }

        return stats


class RootSupervisor(SupervisorActor):
    """
    Special root supervisor for the entire actor system
    Cannot be stopped by normal means and handles system-wide failures
    """

    def __init__(self):
        super().__init__(
            "root-supervisor",
            supervision_strategy=SupervisionStrategy(
                max_failures=10,
                within_time_window=300.0,  # 5 minutes
                restart_policy=RestartPolicy.ALWAYS,
            ),
            enable_self_repair=True,
        )

        # System-wide policies
        self.register_handler("system_shutdown", self._handle_system_shutdown)
        self.register_handler("emergency_stop", self._handle_emergency_stop)

    async def _handle_system_shutdown(self, message: ActorMessage) -> dict[str, Any]:
        """Graceful system shutdown"""
        logger.info("Root supervisor initiating system shutdown")

        await self.stop_all_children()

        return {"status": "shutdown_complete"}

    async def _handle_emergency_stop(self, message: ActorMessage) -> dict[str, Any]:
        """Emergency stop all actors"""
        logger.warning("Root supervisor executing emergency stop")

        # Force stop all children without cleanup
        for child_id in list(self.children.keys()):
            try:
                await self.actor_system.stop_actor(child_id)
            except Exception as e:
                logger.error(f"Failed to emergency stop {child_id}: {e}")

        self.children.clear()
        self.child_metadata.clear()

        return {"status": "emergency_stop_complete"}


# Example usage


async def demo_supervision():
    """Demonstrate supervision hierarchies"""
    from .actor_system import get_global_actor_system

    system = await get_global_actor_system()

    # Create root supervisor
    root_ref = await system.create_actor(RootSupervisor, "root-supervisor")

    # Create a middle-tier supervisor with OneForOne strategy

    class DepartmentSupervisor(SupervisorActor):
        def __init__(self, actor_id: str, department: str):
            super().__init__(
                actor_id,
                supervision_strategy=SupervisionStrategy(
                    max_failures=3,
                    within_time_window=60.0,
                    restart_policy=RestartPolicy.ON_FAILURE,
                ),
                supervision_decider=OneForOneStrategy(SupervisionStrategy(max_failures=3)),
            )
            self.department = department

    # Create department supervisor under root
    await root_ref.ask(
        "create_child",
        {
            "child_class": DepartmentSupervisor,
            "child_id": "analytics-dept",
            "department": "analytics",
        },
    )

    logger.info("Supervision hierarchy created successfully")

    # Get supervision stats
    stats = await root_ref.ask("get_supervision_stats", {})
    print("Root supervision stats:", stats)


if __name__ == "__main__":
    asyncio.run(demo_supervision())
