"""
Pipeline Executor

Executes multi-node pipelines with timeout enforcement and cancellation support.
"""

import asyncio
import logging
from typing import Any, Callable

from lukhas.orchestrator.cancellation import CancellationRegistry
from lukhas.orchestrator.config import OrchestratorConfig
from lukhas.orchestrator.exceptions import (
    CancellationException,
    NodeTimeoutException,
    PipelineTimeoutException,
)
from lukhas.orchestrator.executor import NodeExecutor

logger = logging.getLogger(__name__)


class PipelineExecutor:
    """Executes multi-node pipelines with timeout enforcement."""

    def __init__(self, config: OrchestratorConfig, registry: CancellationRegistry):
        self.config = config
        self.registry = registry
        self.node_executor = NodeExecutor(config.timeouts)

    async def execute_pipeline(
        self,
        pipeline_id: str,
        nodes: list[tuple[str, Callable]],
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
        start_time = asyncio.get_event_loop().time()
        cancellation_token = self.registry.register(pipeline_id)
        completed_nodes = []

        try:
            result = await asyncio.wait_for(
                self._execute_nodes(
                    pipeline_id, nodes, initial_input, cancellation_token, completed_nodes
                ),
                timeout=self.config.timeouts.pipeline_timeout_seconds,
            )

            elapsed_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            self._record_pipeline_success(pipeline_id, len(nodes), elapsed_ms)

            return result

        except asyncio.TimeoutError:
            await self.registry.cancel(pipeline_id, "Pipeline timeout")
            self._record_pipeline_timeout(pipeline_id, len(completed_nodes))

            raise PipelineTimeoutException(
                pipeline_id,
                self.config.timeouts.pipeline_timeout_ms,
                completed_nodes,
                self.registry.get_partial_results(pipeline_id),
            )

        except (NodeTimeoutException, CancellationException):
            await self.registry.cancel(pipeline_id, "Downstream exception")
            raise

        except Exception as e:
            elapsed_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            self._record_pipeline_error(
                pipeline_id, len(completed_nodes), elapsed_ms, type(e).__name__
            )
            await self.registry.cancel(pipeline_id, "Unhandled exception")
            raise

        finally:
            self.registry.unregister(pipeline_id)

    async def _execute_nodes(
        self,
        pipeline_id: str,
        nodes: list[tuple[str, Callable]],
        initial_input: Any,
        cancellation_token: asyncio.Event,
        completed_nodes: list[str],
    ) -> Any:
        """Execute pipeline nodes sequentially."""
        current_input = initial_input

        for node_id, node_func in nodes:
            logger.debug(f"Executing node {node_id} in pipeline {pipeline_id}")

            current_input = await self.node_executor.execute_node(
                node_id=node_id,
                node_func=node_func,
                input_data=current_input,
                cancellation_token=cancellation_token,
            )

            completed_nodes.append(node_id)
            self.registry.store_partial_result(pipeline_id, node_id, current_input)

            logger.debug(
                f"Node {node_id} completed ({len(completed_nodes)}/{len(nodes)})"
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
