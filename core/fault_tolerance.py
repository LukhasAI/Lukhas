"""
Fault Tolerance and Supervision for Swarm Architecture

Provides supervision strategies and fault recovery for agent colonies
with support for restart, escalate, and resume patterns.
"""

import logging
from enum import Enum
from typing import Any, Callable, Optional, Type, Union

logger = logging.getLogger(__name__)


class SupervisionStrategy(str, Enum):
    """Supervision strategies for fault handling in agent colonies"""

    RESTART = "restart"  # Restart failed agent
    RESUME = "resume"  # Resume agent from last known state
    ESCALATE = "escalate"  # Escalate failure to higher level
    STOP = "stop"  # Stop the failed agent permanently


HandlerFunc = Callable[[str, Exception, Optional[dict[str, Any]]], dict[str, Any]]


def _get_handler_name(handler: HandlerFunc) -> str:
    """Resolve a readable handler name for logging."""
    # ΛTAG: handler_name_resolver
    return getattr(handler, "__name__", handler.__class__.__name__)


class Supervisor:
    """
    Supervisor for agent fault tolerance and recovery

    Implements supervision patterns for handling agent failures
    with configurable strategies (restart, resume, escalate, stop).

    Example:
        supervisor = Supervisor(strategy=SupervisionStrategy.RESTART)
        supervisor.handle_failure(agent, exception)
    """

    def __init__(
        self,
        strategy: SupervisionStrategy = SupervisionStrategy.RESTART,
        max_retries: int = 3,
        backoff_seconds: float = 1.0,
    ):
        """
        Initialize supervisor with strategy

        Args:
            strategy: Supervision strategy to use for failures
            max_retries: Maximum number of retry attempts
            backoff_seconds: Backoff time between retries
        """
        self.strategy = strategy
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds

        # Failure tracking
        self.failure_count: dict[str, int] = {}
        self.last_failures: dict[str, Exception] = {}

        # ΛTAG: handler_registry_state
        self._custom_handlers_by_exception: dict[Type[Exception], HandlerFunc] = {}
        self._custom_handlers_by_agent: dict[str, HandlerFunc] = {}

        logger.info(f"Supervisor initialized with strategy: {strategy.value}")

    def handle_failure(
        self, agent_id: str, exception: Exception, context: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """
        Handle agent failure according to supervision strategy

        Args:
            agent_id: ID of the failed agent
            exception: Exception that caused the failure
            context: Additional context about the failure

        Returns:
            Dictionary with recovery action and metadata
        """
        # Track failure
        self.failure_count[agent_id] = self.failure_count.get(agent_id, 0) + 1
        self.last_failures[agent_id] = exception

        failure_count = self.failure_count[agent_id]

        logger.warning(
            f"Agent {agent_id} failed (attempt {failure_count}/{self.max_retries})",
            extra={
                "agent_id": agent_id,
                "strategy": self.strategy.value,
                "exception": str(exception),
                "failure_count": failure_count,
            },
        )

        # Apply supervision strategy
        # ΛTAG: handler_precedence_agent
        if agent_id in self._custom_handlers_by_agent:
            logger.debug(
                "Invoking agent-specific custom handler",
                extra={
                    "agent_id": agent_id,
                    "handler": _get_handler_name(self._custom_handlers_by_agent[agent_id]),
                },
            )
            return self._custom_handlers_by_agent[agent_id](agent_id, exception, context)

        # ΛTAG: handler_precedence_exception
        for exc_type, handler in self._custom_handlers_by_exception.items():
            if isinstance(exception, exc_type):
                logger.debug(
                    "Invoking exception-specific custom handler",
                    extra={
                        "agent_id": agent_id,
                        "handler": _get_handler_name(handler),
                        "exception_type": exc_type.__name__,
                    },
                )
                return handler(agent_id, exception, context)

        if self.strategy == SupervisionStrategy.RESTART:
            return self._handle_restart(agent_id, failure_count)

        elif self.strategy == SupervisionStrategy.RESUME:
            return self._handle_resume(agent_id, context)

        elif self.strategy == SupervisionStrategy.ESCALATE:
            return self._handle_escalate(agent_id, exception)

        elif self.strategy == SupervisionStrategy.STOP:
            return self._handle_stop(agent_id)

        else:
            logger.error(f"Unknown supervision strategy: {self.strategy}")
            return {"action": "stop", "reason": "unknown_strategy"}

    def _handle_restart(self, agent_id: str, failure_count: int) -> dict[str, Any]:
        """Handle restart strategy"""
        if failure_count > self.max_retries:
            logger.error(f"Agent {agent_id} exceeded max retries, stopping")
            return {"action": "stop", "reason": "max_retries_exceeded", "failure_count": failure_count}

        return {"action": "restart", "backoff": self.backoff_seconds * failure_count, "attempt": failure_count}

    def _handle_resume(self, agent_id: str, context: Optional[dict[str, Any]]) -> dict[str, Any]:
        """Handle resume strategy"""
        return {
            "action": "resume",
            "state": context.get("last_state") if context else None,
            "checkpoint": context.get("checkpoint") if context else None,
        }

    def _handle_escalate(self, agent_id: str, exception: Exception) -> dict[str, Any]:
        """Handle escalate strategy"""
        return {
            "action": "escalate",
            "agent_id": agent_id,
            "exception": str(exception),
            "escalate_to": "colony_supervisor",
        }

    def _handle_stop(self, agent_id: str) -> dict[str, Any]:
        """Handle stop strategy"""
        return {"action": "stop", "agent_id": agent_id, "reason": "stopped_by_strategy"}

    def reset_failures(self, agent_id: str) -> None:
        """Reset failure count for an agent"""
        self.failure_count.pop(agent_id, None)
        self.last_failures.pop(agent_id, None)
        logger.debug(f"Reset failure tracking for agent {agent_id}")

    def get_failure_stats(self) -> dict[str, Any]:
        """Get failure statistics across all agents"""
        return {
            "total_failures": sum(self.failure_count.values()),
            "agents_with_failures": len(self.failure_count),
            "failure_counts": dict(self.failure_count),
            "strategy": self.strategy.value,
            "max_retries": self.max_retries,
        }

    def register_custom_handler(
        self,
        target: Union[Type[Exception], str],
        handler: HandlerFunc,
    ) -> None:
        """Register a custom handler for an exception type or agent.

        Args:
            target: Exception type or agent identifier to bind the handler to.
            handler: Callable used for handling failures.

        Raises:
            TypeError: If the target is not an exception type or agent identifier.
        """
        if isinstance(target, str):
            # ΛTAG: handler_registry_agent
            self._custom_handlers_by_agent[target] = handler
            logger.info(
                "Registered agent-specific custom handler",
                extra={"agent_id": target, "handler": _get_handler_name(handler)},
            )
            return

        if isinstance(target, type) and issubclass(target, Exception):
            # ΛTAG: handler_registry_exception
            self._custom_handlers_by_exception[target] = handler
            logger.info(
                "Registered exception-specific custom handler",
                extra={"exception_type": target.__name__, "handler": _get_handler_name(handler)},
            )
            return

        raise TypeError("Custom handler target must be an agent_id (str) or Exception subclass")


__all__ = [
    "SupervisionStrategy",
    "Supervisor",
]
