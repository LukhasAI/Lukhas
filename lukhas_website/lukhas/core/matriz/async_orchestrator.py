#!/usr/bin/env python3
"""
MATRIZ Async Orchestrator

High-performance async orchestration engine for T4/0.01% targets:
- <100ms stage latency
- <250ms total pipeline latency
- 99.9% success rate
- Fail-soft behavior for non-critical stages
"""

import asyncio
import time
from dataclasses import dataclass
from typing import Any, Optional

from observability.opentelemetry_tracing import LUKHASTracer
from observability.prometheus_metrics import LUKHASMetrics

# Python 3.9 compatibility for asyncio.timeout
from .asyncio_compat import wait_for_with_timeout
from .pipeline_stage import PipelineStage, StageResult


@dataclass
class PipelineResult:
    """Result of pipeline execution."""
    success: bool
    output: Optional[dict[str, Any]]
    stage_results: dict[str, StageResult]
    total_duration: float
    error: Optional[Exception] = None


class AsyncOrchestrator:
    """
    High-performance async orchestration engine.

    Implements T4/0.01% performance targets with fail-soft behavior.
    """

    def __init__(
        self,
        metrics: Optional[LUKHASMetrics] = None,
        tracer: Optional[LUKHASTracer] = None,
        stage_timeout: float = 0.1,  # 100ms
        total_timeout: float = 0.25,  # 250ms
    ):
        self.stages: list[PipelineStage] = []
        self.metrics = metrics or LUKHASMetrics()
        self.tracer = tracer or LUKHASTracer()
        self.stage_timeout = stage_timeout
        self.total_timeout = total_timeout

    def add_stage(self, stage: PipelineStage) -> None:
        """Add a pipeline stage."""
        self.stages.append(stage)

    def remove_stage(self, stage_name: str) -> bool:
        """Remove a pipeline stage by name."""
        for i, stage in enumerate(self.stages):
            if stage.name == stage_name:
                del self.stages[i]
                return True
        return False

    async def process(self, input_data: dict[str, Any]) -> PipelineResult:
        """
        Process data through the pipeline.

        Args:
            input_data: Input data to process

        Returns:
            PipelineResult with success status and outputs
        """
        start_time = time.time()
        stage_results = {}
        current_data = input_data.copy()
        pipeline_error = None

        try:
            # Define pipeline execution coroutine
            async def pipeline_execution():
                nonlocal stage_results, current_data, pipeline_error

                with self.tracer.trace_operation("pipeline_execution") as span:
                    span.set_attribute("stage_count", len(self.stages))

                    for stage in self.stages:
                        try:
                            # Execute stage with timeout
                            stage_result = await self._execute_stage(stage, current_data)
                            stage_results[stage.name] = stage_result

                            if stage_result.success:
                                # Update data for next stage
                                if stage_result.output:
                                    current_data.update(stage_result.output)
                            else:
                                # Handle stage failure
                                if stage.critical:
                                    # Critical stage failure - abort pipeline
                                    pipeline_error = stage_result.error
                                    break
                                # Non-critical failure - continue with warning
                                # Metrics already recorded in _execute_stage

                        except asyncio.TimeoutError:
                            # Stage timeout
                            timeout_error = Exception(f"Stage {stage.name} timed out after {self.stage_timeout}s")
                            stage_results[stage.name] = StageResult(
                                success=False,
                                output=None,
                                processing_time=self.stage_timeout,
                                error=timeout_error
                            )

                            if stage.critical:
                                pipeline_error = timeout_error
                                break

                        except Exception as e:
                            # Unexpected stage error
                            stage_results[stage.name] = StageResult(
                                success=False,
                                output=None,
                                processing_time=0.0,
                                error=e
                            )

                            if stage.critical:
                                pipeline_error = e
                                break

            # Execute with total timeout
            await wait_for_with_timeout(pipeline_execution(), self.total_timeout)

        except asyncio.TimeoutError:
            pipeline_error = Exception(f"Pipeline timed out after {self.total_timeout}s")

        # Calculate total duration
        total_duration = time.time() - start_time

        # Record metrics
        self.metrics.record_matriz_pipeline(
            duration=total_duration,
            success=pipeline_error is None,
            within_budget=total_duration < self.total_timeout,
            stages_completed=len([r for r in stage_results.values() if r.success])
        )

        # Determine overall success
        success = pipeline_error is None

        return PipelineResult(
            success=success,
            output=current_data if success else None,
            stage_results=stage_results,
            total_duration=total_duration,
            error=pipeline_error
        )

    async def _execute_stage(self, stage: PipelineStage, input_data: dict[str, Any]) -> StageResult:
        """Execute a single pipeline stage."""
        start_time = time.time()

        try:
            # Define stage execution coroutine
            async def stage_execution():
                with self.tracer.trace_operation(f"stage_{stage.name}") as span:
                    span.set_attribute("critical", stage.critical)

                    # Execute the stage plugin
                    return await stage.plugin.process(input_data)

            # Execute with stage timeout
            output = await wait_for_with_timeout(stage_execution(), self.stage_timeout)

            processing_time = time.time() - start_time

            # Record stage metrics
            self.metrics.record_matriz_stage(
                stage=stage.name,
                duration=processing_time,
                success=True,
                timeout=False
            )

            return StageResult(
                success=True,
                output=output,
                processing_time=processing_time,
                error=None
            )

        except Exception as e:
            processing_time = time.time() - start_time

            # Record failure metrics
            is_timeout = isinstance(e, asyncio.TimeoutError)
            self.metrics.record_matriz_stage(
                stage=stage.name,
                duration=processing_time,
                success=False,
                timeout=is_timeout
            )

            return StageResult(
                success=False,
                output=None,
                processing_time=processing_time,
                error=e
            )

    async def health_check(self) -> dict[str, Any]:
        """Perform orchestrator health check."""
        health_data = {
            "orchestrator_healthy": True,
            "stage_count": len(self.stages),
            "stages": [],
            "performance_targets": {
                "stage_timeout_ms": self.stage_timeout * 1000,
                "total_timeout_ms": self.total_timeout * 1000,
            }
        }

        # Check each stage
        for stage in self.stages:
            stage_health = {
                "name": stage.name,
                "critical": stage.critical,
                "healthy": True
            }

            # Basic stage health check (if plugin supports it)
            if hasattr(stage.plugin, 'health_check'):
                try:
                    plugin_health = await stage.plugin.health_check()
                    stage_health.update(plugin_health)
                except Exception as e:
                    stage_health["healthy"] = False
                    stage_health["error"] = str(e)

            health_data["stages"].append(stage_health)

        return health_data

    async def get_metrics(self) -> dict[str, Any]:
        """Get orchestrator performance metrics."""
        return {
            "stage_count": len(self.stages),
            "critical_stages": len([s for s in self.stages if s.critical]),
            "non_critical_stages": len([s for s in self.stages if not s.critical]),
            "configuration": {
                "stage_timeout_ms": self.stage_timeout * 1000,
                "total_timeout_ms": self.total_timeout * 1000,
            }
        }


class MockAsyncOrchestrator(AsyncOrchestrator):
    """Mock orchestrator for testing."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.process_calls = 0
        self.last_input = None

    async def process(self, input_data: dict[str, Any]) -> PipelineResult:
        """Mock process that tracks calls."""
        self.process_calls += 1
        self.last_input = input_data

        # Simulate very fast processing
        await asyncio.sleep(0.001)

        return PipelineResult(
            success=True,
            output={"mock": True, "input": input_data},
            stage_results={},
            total_duration=0.001
        )
