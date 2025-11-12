"""
Pipeline Executor

Executes multi-node pipelines with timeout enforcement and cancellation support.
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Callable, List, Optional

from lukhas.orchestrator.config import OrchestratorConfig
from lukhas.orchestrator.exceptions import (
    CancellationException,
    NodeTimeoutException,
    PipelineTimeoutException,
)
from lukhas.orchestrator.executor import NodeExecutor

logger = logging.getLogger(__name__)


@dataclass
class PipelineContext:
    """Context for pipeline execution."""

    pipeline_id: str
    nodes: List[str]
    cancellation_token: asyncio.Event
    start_time: float
    completed_nodes: List[str]


class PipelineExecutor:
    """Executes multi-node pipelines with timeout enforcement."""

    def __init__(self, config: OrchestratorConfig):
        self.config = config
        self.node_executor = NodeExecutor(config.timeouts)

    async def execute_pipeline(
        self,
        pipeline_id: str,
        nodes: List[tuple[str, Callable]],
        initial_input: Any,
    ) -> Any:
        """
        Execute a pipeline of cognitive nodes with timeout enforcement.

        Args:
            pipeline_id: Unique identifier for pipeline
            nodes: List of (node_id, node_func) tuples
            initial_input: Initial input data

        Returns:
            Final pipeline output

        Raises:
            PipelineTimeoutException: If pipeline exceeds timeout
            NodeTimeoutException: If a node exceeds its timeout
            CancellationException: If pipeline is cancelled
        """
        # Create pipeline context
        context = PipelineContext(
            pipeline_id=pipeline_id,
            nodes=[node_id for node_id, _ in nodes],
            cancellation_token=asyncio.Event(),
            start_time=asyncio.get_event_loop().time(),
            completed_nodes=[],
        )

        try:
            # Execute pipeline with timeout
            result = await asyncio.wait_for(
                self._execute_nodes(context, nodes, initial_input),
                timeout=self.config.timeouts.pipeline_timeout_seconds,
            )

            # Record success metric
            elapsed_ms = (asyncio.get_event_loop().time() - context.start_time) * 1000
            self._record_pipeline_success(pipeline_id, len(nodes), elapsed_ms)

            return result

        except asyncio.TimeoutError:
            # Set cancellation token
            context.cancellation_token.set()

            # Record timeout metric
            self._record_pipeline_timeout(pipeline_id, len(context.completed_nodes))

            raise PipelineTimeoutException(
                pipeline_id,
                self.config.timeouts.pipeline_timeout_ms,
                context.completed_nodes,
            )

        except (NodeTimeoutException, CancellationException):
            # Propagate node timeout or cancellation
            context.cancellation_token.set()
            raise

        except Exception as e:
            # Record error metric
            elapsed_ms = (asyncio.get_event_loop().time() - context.start_time) * 1000
            self._record_pipeline_error(
                pipeline_id,
                len(context.completed_nodes),
                elapsed_ms,
                type(e).__name__,
            )
            raise

    async def _execute_nodes(
        self,
        context: PipelineContext,
        nodes: List[tuple[str, Callable]],
        initial_input: Any,
    ) -> Any:
        """Execute pipeline nodes sequentially."""
        current_input = initial_input

        for node_id, node_func in nodes:
            logger.debug(f"Executing node {node_id} in pipeline {context.pipeline_id}")

            # Execute node with timeout
            current_input = await self.node_executor.execute_node(
                node_id=node_id,
                node_func=node_func,
                input_data=current_input,
                cancellation_token=context.cancellation_token,
            )

            # Mark node completed
            context.completed_nodes.append(node_id)

            logger.debug(
                f"Node {node_id} completed "
                f"({len(context.completed_nodes)}/{len(context.nodes)})"
            )

        return current_input

    def _record_pipeline_success(
        self, pipeline_id: str, node_count: int, elapsed_ms: float
    ) -> None:
        """Record successful pipeline execution."""
        try:
            from lukhas.monitoring.metrics import get_metrics_client

            metrics = get_metrics_client()
            metrics.histogram(
                "orchestrator_pipeline_duration_ms",
                elapsed_ms,
                tags={"pipeline_id": pipeline_id, "status": "success"},
            )
            metrics.increment(
                "orchestrator_pipeline_executions_total",
                tags={"pipeline_id": pipeline_id, "status": "success"},
            )
            metrics.histogram(
                "orchestrator_pipeline_node_count",
                node_count,
                tags={"pipeline_id": pipeline_id},
            )
        except Exception as e:
            logger.warning(f"Failed to record pipeline success metric: {e}")

    def _record_pipeline_timeout(
        self, pipeline_id: str, completed_nodes: int
    ) -> None:
        """Record pipeline timeout."""
        try:
            from lukhas.monitoring.metrics import get_metrics_client

            metrics = get_metrics_client()
            metrics.increment(
                "orchestrator_pipeline_timeouts_total",
                tags={"pipeline_id": pipeline_id},
            )
            metrics.increment(
                "orchestrator_pipeline_executions_total",
                tags={"pipeline_id": pipeline_id, "status": "timeout"},
            )
            metrics.gauge(
                "orchestrator_pipeline_completed_nodes_at_timeout",
                completed_nodes,
                tags={"pipeline_id": pipeline_id},
            )
        except Exception as e:
            logger.warning(f"Failed to record pipeline timeout metric: {e}")

    def _record_pipeline_error(
        self,
        pipeline_id: str,
        completed_nodes: int,
        elapsed_ms: float,
        error_type: str,
    ) -> None:
        """Record pipeline error."""
        try:
            from lukhas.monitoring.metrics import get_metrics_client

            metrics = get_metrics_client()
            metrics.histogram(
                "orchestrator_pipeline_duration_ms",
                elapsed_ms,
                tags={"pipeline_id": pipeline_id, "status": "error"},
            )
            metrics.increment(
                "orchestrator_pipeline_executions_total",
                tags={
                    "pipeline_id": pipeline_id,
                    "status": "error",
                    "error_type": error_type,
                },
            )
        except Exception as e:
            logger.warning(f"Failed to record pipeline error metric: {e}")
