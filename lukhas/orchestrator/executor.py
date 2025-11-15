"""
Node Executor

Executes cognitive nodes with timeout enforcement and cancellation support.
"""

import asyncio
import logging
from typing import Any, Callable, Optional

from lukhas.orchestrator.config import TimeoutConfig
from lukhas.orchestrator.exceptions import CancellationException, NodeTimeoutException

logger = logging.getLogger(__name__)


class NodeExecutor:
    """Executes cognitive nodes with timeout enforcement."""

    def __init__(self, config: TimeoutConfig):
        self.config = config

    async def execute_node(
        self,
        node_id: str,
        node_func: Callable,
        input_data: Any,
        cancellation_token: Optional[asyncio.Event] = None,
        on_timeout: Optional[Callable] = None,
        on_cancel: Optional[Callable] = None,
    ) -> Any:
        """
        Execute a cognitive node with timeout enforcement.

        Args:
            node_id: Unique identifier for the node
            node_func: Async function to execute
            input_data: Input data for the node
            cancellation_token: Optional event to check for cancellation
            on_timeout: Optional async function to call on timeout
            on_cancel: Optional async function to call on cancellation

        Returns:
            Node execution result

        Raises:
            NodeTimeoutException: If node exceeds timeout
            CancellationException: If cancelled via token
        """
        start_time = asyncio.get_event_loop().time()

        try:
            # Create task for node execution
            task = asyncio.create_task(node_func(input_data))

            # Wait with timeout
            result = await asyncio.wait_for(
                self._execute_with_cancellation(task, cancellation_token),
                timeout=self.config.node_timeout_seconds,
            )

            # Record success metric
            elapsed_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            self._record_node_success(node_id, elapsed_ms)

            return result

        except asyncio.TimeoutError:
            # Cancel the task
            task.cancel()

            # Wait briefly for cleanup
            try:
                await asyncio.wait_for(task, timeout=self.config.cleanup_grace_seconds)
            except (asyncio.TimeoutError, asyncio.CancelledError):
                logger.warning(f"Node {node_id} did not cleanup gracefully")

            # Record timeout metric
            self._record_node_timeout(node_id)

            # Call timeout handler
            if on_timeout:
                try:
                    await on_timeout()
                except Exception:
                    logger.exception(f"Node {node_id} on_timeout handler failed")

            # Raise timeout exception
            raise NodeTimeoutException(node_id, self.config.node_timeout_ms)

        except CancellationException:
            # Call cancellation handler
            if on_cancel:
                try:
                    await on_cancel()
                except Exception:
                    logger.exception(f"Node {node_id} on_cancel handler failed")
            # Propagate cancellation
            task.cancel()
            raise

        except Exception as e:
            # Record error metric
            elapsed_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            self._record_node_error(node_id, elapsed_ms, type(e).__name__)
            raise

    async def _execute_with_cancellation(
        self, task: asyncio.Task, cancellation_token: Optional[asyncio.Event]
    ) -> Any:
        """Execute task while checking cancellation token."""
        if not cancellation_token:
            return await task

        # Wait for either task completion or cancellation
        cancel_task = asyncio.create_task(cancellation_token.wait())

        done, pending = await asyncio.wait(
            [task, cancel_task], return_when=asyncio.FIRST_COMPLETED
        )

        # Cancel pending tasks
        for p in pending:
            p.cancel()

        # Check if cancelled
        if cancel_task in done:
            raise CancellationException("unknown", "Cancellation token set")

        # Return task result
        return task.result()

    def _record_node_success(self, node_id: str, elapsed_ms: float) -> None:
        """Record successful node execution."""
        try:
            from lukhas.monitoring.metrics import get_metrics_client

            metrics = get_metrics_client()
            metrics.histogram(
                "orchestrator_node_duration_ms",
                elapsed_ms,
                tags={"node_id": node_id, "status": "success"},
            )
            metrics.increment(
                "orchestrator_node_executions_total",
                tags={"node_id": node_id, "status": "success"},
            )
        except Exception as e:
            logger.warning(f"Failed to record node success metric: {e}")

    def _record_node_timeout(self, node_id: str) -> None:
        """Record node timeout."""
        try:
            from lukhas.monitoring.metrics import get_metrics_client

            metrics = get_metrics_client()
            metrics.increment(
                "orchestrator_node_timeouts_total", tags={"node_id": node_id}
            )
            metrics.increment(
                "orchestrator_node_executions_total",
                tags={"node_id": node_id, "status": "timeout"},
            )
        except Exception as e:
            logger.warning(f"Failed to record node timeout metric: {e}")

    def _record_node_error(
        self, node_id: str, elapsed_ms: float, error_type: str
    ) -> None:
        """Record node error."""
        try:
            from lukhas.monitoring.metrics import get_metrics_client

            metrics = get_metrics_client()
            metrics.histogram(
                "orchestrator_node_duration_ms",
                elapsed_ms,
                tags={"node_id": node_id, "status": "error"},
            )
            metrics.increment(
                "orchestrator_node_executions_total",
                tags={"node_id": node_id, "status": "error", "error_type": error_type},
            )
        except Exception as e:
            logger.warning(f"Failed to record node error metric: {e}")
