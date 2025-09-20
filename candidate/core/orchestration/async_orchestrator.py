# candidate/core/orchestration/async_orchestrator.py
"""
Advanced async orchestrator with resilience patterns.

Features:
- Per-stage timeouts with exponential backoff
- Consensus arbitration with ethics gating
- Loop detection and escalation
- Comprehensive observability
"""

from __future__ import annotations
import asyncio
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional

from lukhas.core.interfaces import CognitiveNodeBase
from lukhas.core.registry import resolve
from .consensus_arbitrator import Proposal, choose
from .meta_controller import MetaController
from .otel import stage_span
from lukhas.metrics import (
    stage_latency, stage_timeouts, guardian_band,
    reasoning_chain_length, ethics_risk_distribution,
    node_confidence_scores, constellation_star_activations,
    arbitration_decisions_total, oscillation_detections_total,
    parallel_batch_duration, parallel_execution_mode_total
)


@dataclass
class StageConfig:
    name: str
    timeout_ms: int = 200
    max_retries: int = 2
    backoff_base_ms: int = 80


@dataclass
class PipelineResult:
    success: bool
    output: Dict[str, Any]
    stage_results: List[Dict[str, Any]]
    rationale: Optional[Dict[str, Any]] = None
    escalation_reason: Optional[str] = None


class AsyncOrchestrator:
    """Advanced async orchestrator with resilience patterns and parallel execution."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.meta_controller = MetaController()
        self.stages: List[StageConfig] = []
        self.enabled = self.config.get("MATRIZ_ASYNC", "1") == "1"
        self.parallel_enabled = self.config.get("MATRIZ_PARALLEL", "0") == "1"
        self.max_parallel_stages = int(self.config.get("MATRIZ_MAX_PARALLEL", "3"))

    def configure_stages(self, stages: List[Dict[str, Any]]) -> None:
        """Configure pipeline stages with timeouts and retry settings."""
        self.stages = [
            StageConfig(
                name=stage["name"],
                timeout_ms=stage.get("timeout_ms", 200),
                max_retries=stage.get("max_retries", 2),
                backoff_base_ms=stage.get("backoff_base_ms", 80)
            )
            for stage in stages
        ]

    async def _with_retry(
        self,
        fn: Any,
        stage_config: StageConfig
    ) -> Any:
        """Execute function with exponential backoff retry."""
        for attempt in range(stage_config.max_retries):
            try:
                return await fn()
            except Exception as e:
                if attempt == stage_config.max_retries - 1:
                    raise
                # Exponential backoff
                delay_ms = (2 ** attempt) * stage_config.backoff_base_ms
                await asyncio.sleep(delay_ms / 1000)

    async def _run_stage(
        self,
        stage_config: StageConfig,
        node: CognitiveNodeBase,
        context: Mapping[str, Any]
    ) -> Dict[str, Any]:
        """Run a single stage with timeout, retry, and observability."""

        # Check for oscillation
        if self.meta_controller.step(stage_config.name):
            guardian_band.labels("escalation", "oscillation").inc()
            oscillation_detections_total.labels("A-B-A-B", stage_config.name).inc()
            return {
                "action": "escalate",
                "reason": "oscillation_detected",
                "stage": stage_config.name
            }

        constellation_star = self._get_constellation_star(stage_config.name)
        constellation_star_activations.labels(constellation_star, "stage_start").inc()

        with stage_latency.labels(stage_config.name, constellation_star).time():
            try:
                # Enhanced distributed tracing with more attributes
                with stage_span(
                    stage_config.name,
                    node=node.name,
                    timeout=stage_config.timeout_ms,
                    max_retries=stage_config.max_retries,
                    context_keys=list(context.keys()),
                    context_size=len(str(context))
                ) as span:
                    async def execute():
                        return await node.process(context)

                    result = await asyncio.wait_for(
                        self._with_retry(execute, stage_config),
                        timeout=stage_config.timeout_ms / 1000
                    )

                    # Add constellation metadata and collect metrics
                    if isinstance(result, dict):
                        result["_constellation"] = {
                            "star": constellation_star,
                            "stage": stage_config.name,
                            "timestamp": time.time()
                        }

                        # Collect domain-specific metrics
                        if "confidence" in result:
                            node_confidence_scores.labels(node.name, stage_config.name).observe(result["confidence"])

                        if "ethics_risk" in result:
                            risk_band = "low" if result["ethics_risk"] < 0.3 else "medium" if result["ethics_risk"] < 0.8 else "high"
                            ethics_risk_distribution.labels(stage_config.name, risk_band).observe(result["ethics_risk"])

                        if "reasoning_chain" in result:
                            chain_length = len(result["reasoning_chain"])
                            complexity = "simple" if chain_length <= 2 else "moderate" if chain_length <= 5 else "complex"
                            reasoning_chain_length.labels(node.name, complexity).observe(chain_length)

                        constellation_star_activations.labels(constellation_star, "stage_complete").inc()

                    return result

            except asyncio.TimeoutError:
                stage_timeouts.labels(stage_config.name).inc()
                return {
                    "action": "timeout",
                    "stage": stage_config.name,
                    "timeout_ms": stage_config.timeout_ms
                }

    def _get_constellation_star(self, stage_name: str) -> str:
        """Map stage names to Constellation stars."""
        mapping = {
            "INTENT": "Awareness",
            "THOUGHT": "Memory",
            "VISION": "Perception",
            "DECISION": "Guardian"
        }
        return mapping.get(stage_name, "Unknown")

    async def _arbitrate_proposals(
        self,
        proposals: List[Dict[str, Any]]
    ) -> PipelineResult:
        """Use consensus arbitration to choose among competing proposals."""
        if not proposals:
            return PipelineResult(
                success=False,
                output={},
                stage_results=[],
                escalation_reason="no_proposals"
            )

        # Convert to Proposal objects
        proposal_objects = []
        for i, prop in enumerate(proposals):
            proposal_objects.append(Proposal(
                id=f"proposal_{i}",
                confidence=prop.get("confidence", 0.5),
                ts=prop.get("timestamp", time.time()),
                ethics_risk=prop.get("ethics_risk", 0.0),
                role_weight=prop.get("role_weight", 0.5),
                rationale=prop.get("rationale", "")
            ))

        winner, rationale = choose(proposal_objects)

        if winner is None:
            return PipelineResult(
                success=False,
                output={},
                stage_results=proposals,
                escalation_reason="no_viable_proposals"
            )

        # Find the corresponding original proposal
        winner_idx = int(winner.id.split("_")[1])
        winning_proposal = proposals[winner_idx]

        return PipelineResult(
            success=True,
            output=winning_proposal,
            stage_results=proposals,
            rationale=rationale
        )

    async def process_query(self, context: Mapping[str, Any]) -> PipelineResult:
        """Process a query through the async pipeline with comprehensive tracing."""

        # Start root span for entire pipeline
        with stage_span(
            "matriz_pipeline",
            pipeline_enabled=self.enabled,
            stage_count=len(self.stages),
            query_length=len(str(context.get("query", ""))),
            pipeline_id=id(self)
        ) as pipeline_span:

            if not self.enabled:
                if pipeline_span:
                    pipeline_span.set_attribute("matriz.disabled_reason", "async_disabled")
                return PipelineResult(
                    success=False,
                    output={},
                    stage_results=[],
                    escalation_reason="async_disabled"
                )

            results = []
            current_context = dict(context)
            pipeline_start_time = time.time()

            # Add pipeline metadata to span
            if pipeline_span:
                pipeline_span.set_attribute("matriz.start_time", pipeline_start_time)
                pipeline_span.set_attribute("matriz.context_keys", ",".join(context.keys()))

            for stage_index, stage_config in enumerate(self.stages):
                try:
                    # Add stage-level tracing context
                    with stage_span(
                        f"stage_{stage_config.name.lower()}",
                        stage_index=stage_index,
                        stage_name=stage_config.name,
                        constellation_star=self._get_constellation_star(stage_config.name)
                    ) as stage_span_ctx:

                        # Resolve node from registry
                        node = resolve(f"node:{stage_config.name.lower()}")

                        # Add node metadata to span
                        if stage_span_ctx:
                            stage_span_ctx.set_attribute("matriz.node_name", node.name)
                            stage_span_ctx.set_attribute("matriz.node_class", node.__class__.__name__)

                        # Run stage
                        stage_result = await self._run_stage(stage_config, node, current_context)
                        results.append(stage_result)

                        # Add result metadata to span
                        if stage_span_ctx and isinstance(stage_result, dict):
                            stage_span_ctx.set_attribute("matriz.stage_success", stage_result.get("action") != "escalate")
                            stage_span_ctx.set_attribute("matriz.confidence", stage_result.get("confidence", 0.0))
                            stage_span_ctx.set_attribute("matriz.ethics_risk", stage_result.get("ethics_risk", 0.0))

                        # Check for escalation
                        if stage_result.get("action") == "escalate":
                            if pipeline_span:
                                pipeline_span.set_attribute("matriz.escalation_reason", stage_result.get("reason"))
                                pipeline_span.set_attribute("matriz.escalation_stage", stage_config.name)
                            return PipelineResult(
                                success=False,
                                output=stage_result,
                                stage_results=results,
                                escalation_reason=stage_result.get("reason")
                            )

                        # Update context for next stage
                        if isinstance(stage_result, dict):
                            current_context.update(stage_result)

                except LookupError:
                    # Node not found in registry, skip
                    results.append({
                        "stage": stage_config.name,
                        "status": "skipped",
                        "reason": "node_not_registered"
                    })
                    if pipeline_span:
                        pipeline_span.set_attribute(f"matriz.stage_{stage_index}_skipped", True)
                    continue
                except Exception as e:
                    results.append({
                        "stage": stage_config.name,
                        "status": "error",
                        "error": str(e)
                    })
                    if pipeline_span:
                        pipeline_span.set_attribute("matriz.error_stage", stage_config.name)
                        pipeline_span.set_attribute("matriz.error_message", str(e))
                    return PipelineResult(
                        success=False,
                        output={"error": str(e)},
                        stage_results=results,
                        escalation_reason="stage_error"
                    )

            # Pipeline completion and final arbitration
            pipeline_end_time = time.time()
            pipeline_duration = pipeline_end_time - pipeline_start_time

            if pipeline_span:
                pipeline_span.set_attribute("matriz.end_time", pipeline_end_time)
                pipeline_span.set_attribute("matriz.duration_seconds", pipeline_duration)
                pipeline_span.set_attribute("matriz.stages_completed", len(results))
                pipeline_span.set_attribute("matriz.total_stages", len(self.stages))

            # If we have multiple viable results, arbitrate
            viable_results = [r for r in results if r.get("status") != "error" and r.get("action") != "escalate"]

            if pipeline_span:
                pipeline_span.set_attribute("matriz.viable_results_count", len(viable_results))

            if len(viable_results) > 1:
                # Add arbitration span and metrics
                with stage_span("consensus_arbitration", proposals_count=len(viable_results)) as arb_span:
                    result = await self._arbitrate_proposals(viable_results)

                    # Collect arbitration metrics
                    outcome = "success" if result.success else "failure"
                    arbitration_decisions_total.labels(outcome, str(len(viable_results))).inc()

                    if arb_span and result.rationale:
                        arb_span.set_attribute("matriz.arbitration_rationale", str(result.rationale))
                    return result
            elif viable_results:
                if pipeline_span:
                    pipeline_span.set_attribute("matriz.result_source", "single_viable")
                return PipelineResult(
                    success=True,
                    output=viable_results[0],
                    stage_results=results
                )
            else:
                if pipeline_span:
                    pipeline_span.set_attribute("matriz.failure_reason", "no_viable_results")
                return PipelineResult(
                    success=False,
                    output={},
                    stage_results=results,
                    escalation_reason="no_viable_results"
                )

    async def process_query_parallel(self, context: Mapping[str, Any]) -> PipelineResult:
        """Process query with parallel stage execution where possible."""

        # Start root span for entire parallel pipeline
        with stage_span(
            "matriz_parallel_pipeline",
            pipeline_enabled=self.enabled and self.parallel_enabled,
            stage_count=len(self.stages),
            max_parallel_stages=self.max_parallel_stages,
            query_length=len(str(context.get("query", ""))),
            pipeline_id=id(self)
        ) as pipeline_span:

            if not self.enabled or not self.parallel_enabled:
                reason = "async_disabled" if not self.enabled else "parallel_disabled"
                if pipeline_span:
                    pipeline_span.set_attribute("matriz.disabled_reason", reason)
                # Fall back to sequential processing
                return await self.process_query(context)

            pipeline_start_time = time.time()

            if pipeline_span:
                pipeline_span.set_attribute("matriz.start_time", pipeline_start_time)
                pipeline_span.set_attribute("matriz.context_keys", ",".join(context.keys()))
                pipeline_span.set_attribute("matriz.execution_mode", "parallel")

            # Group stages into batches for parallel execution
            stage_batches = self._create_stage_batches()
            all_results = []
            current_context = dict(context)

            for batch_index, batch in enumerate(stage_batches):
                batch_start_time = time.time()
                with stage_span(
                    f"parallel_batch_{batch_index}",
                    batch_size=len(batch),
                    batch_index=batch_index
                ) as batch_span:

                    # Execute stages in parallel within this batch
                    batch_tasks = []

                    for stage_config in batch:
                        try:
                            # Resolve node from registry
                            node = resolve(f"node:{stage_config.name.lower()}")

                            # Create async task for this stage
                            task = asyncio.create_task(
                                self._run_stage_with_context(
                                    stage_config, node, current_context, batch_index
                                )
                            )
                            batch_tasks.append((stage_config, task))

                        except LookupError:
                            # Node not found, create placeholder result
                            all_results.append({
                                "stage": stage_config.name,
                                "status": "skipped",
                                "reason": "node_not_registered",
                                "batch": batch_index
                            })

                    # Wait for all tasks in this batch to complete
                    if batch_tasks:
                        batch_results = await self._execute_batch_with_timeout(
                            batch_tasks, batch_span
                        )
                        all_results.extend(batch_results)

                        # Collect batch duration metrics
                        batch_duration = time.time() - batch_start_time
                        parallel_batch_duration.labels(
                            batch_index=str(batch_index),
                            batch_size=str(len(batch))
                        ).observe(batch_duration)

                        # Check for escalations before proceeding to next batch
                        escalation = self._check_batch_escalations(batch_results)
                        if escalation:
                            if pipeline_span:
                                pipeline_span.set_attribute("matriz.escalation_batch", batch_index)
                            return PipelineResult(
                                success=False,
                                output=escalation,
                                stage_results=all_results,
                                escalation_reason=escalation.get("reason")
                            )

                        # Update context with successful results for next batch
                        current_context = self._merge_batch_context(
                            current_context, batch_results
                        )

            # Final pipeline processing (same as sequential)
            pipeline_end_time = time.time()
            pipeline_duration = pipeline_end_time - pipeline_start_time

            if pipeline_span:
                pipeline_span.set_attribute("matriz.end_time", pipeline_end_time)
                pipeline_span.set_attribute("matriz.duration_seconds", pipeline_duration)
                pipeline_span.set_attribute("matriz.stages_completed", len(all_results))
                pipeline_span.set_attribute("matriz.total_stages", len(self.stages))
                pipeline_span.set_attribute("matriz.parallel_batches", len(stage_batches))

            return await self._finalize_parallel_results(all_results, pipeline_span)

    def _create_stage_batches(self) -> List[List[StageConfig]]:
        """Create batches of stages that can run in parallel.

        Current implementation creates simple batches based on max_parallel_stages.
        Future enhancement: Analyze dependencies between stages.
        """
        batches = []
        current_batch = []

        for stage in self.stages:
            current_batch.append(stage)

            # Create new batch when we reach max parallel stages
            if len(current_batch) >= self.max_parallel_stages:
                batches.append(current_batch)
                current_batch = []

        # Add remaining stages as final batch
        if current_batch:
            batches.append(current_batch)

        return batches

    async def _run_stage_with_context(
        self,
        stage_config: StageConfig,
        node: CognitiveNodeBase,
        context: Mapping[str, Any],
        batch_index: int
    ) -> Dict[str, Any]:
        """Run stage with additional parallel execution context."""
        result = await self._run_stage(stage_config, node, context)

        # Add parallel execution metadata
        if isinstance(result, dict):
            result["_parallel"] = {
                "batch_index": batch_index,
                "execution_mode": "parallel"
            }

        return result

    async def _execute_batch_with_timeout(
        self,
        batch_tasks: List[tuple],
        batch_span: Any
    ) -> List[Dict[str, Any]]:
        """Execute a batch of tasks with comprehensive error handling."""
        results = []

        try:
            # Use asyncio.gather with return_exceptions=True for resilience
            completed_results = await asyncio.gather(
                *[task for _, task in batch_tasks],
                return_exceptions=True
            )

            for i, (stage_config, task) in enumerate(batch_tasks):
                result = completed_results[i]

                if isinstance(result, Exception):
                    # Handle task exception
                    error_result = {
                        "stage": stage_config.name,
                        "status": "error",
                        "error": str(result),
                        "error_type": type(result).__name__
                    }
                    results.append(error_result)

                    if batch_span:
                        batch_span.set_attribute(f"matriz.stage_{stage_config.name}_error", str(result))
                else:
                    # Successful result
                    if isinstance(result, dict):
                        result["stage"] = stage_config.name
                        result["status"] = "completed"
                    results.append(result)

                    if batch_span:
                        batch_span.set_attribute(f"matriz.stage_{stage_config.name}_success", True)

            if batch_span:
                batch_span.set_attribute("matriz.batch_completion_rate",
                    len([r for r in results if r.get("status") == "completed"]) / len(results))

        except Exception as e:
            # Batch-level error
            for stage_config, _ in batch_tasks:
                results.append({
                    "stage": stage_config.name,
                    "status": "batch_error",
                    "error": str(e)
                })

            if batch_span:
                batch_span.set_attribute("matriz.batch_error", str(e))

        return results

    def _check_batch_escalations(self, batch_results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Check if any results in the batch require escalation."""
        for result in batch_results:
            if result.get("action") == "escalate":
                return result
        return None

    def _merge_batch_context(
        self,
        current_context: Dict[str, Any],
        batch_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Merge successful batch results into context for next batch."""
        merged_context = dict(current_context)

        for result in batch_results:
            if (isinstance(result, dict) and
                result.get("status") == "completed" and
                result.get("action") != "escalate"):
                # Merge non-metadata fields
                for key, value in result.items():
                    if not key.startswith("_") and key not in ["stage", "status", "action"]:
                        merged_context[key] = value

        return merged_context

    async def _finalize_parallel_results(
        self,
        all_results: List[Dict[str, Any]],
        pipeline_span: Any
    ) -> PipelineResult:
        """Finalize parallel execution results with arbitration if needed."""
        # Filter viable results (same logic as sequential)
        viable_results = [
            r for r in all_results
            if r.get("status") not in ["error", "batch_error", "skipped"]
            and r.get("action") != "escalate"
        ]

        if pipeline_span:
            pipeline_span.set_attribute("matriz.viable_results_count", len(viable_results))
            pipeline_span.set_attribute("matriz.total_results_count", len(all_results))

        if len(viable_results) > 1:
            # Arbitrate between multiple viable results
            with stage_span("parallel_consensus_arbitration", proposals_count=len(viable_results)) as arb_span:
                result = await self._arbitrate_proposals(viable_results)

                # Collect arbitration metrics
                outcome = "success" if result.success else "failure"
                arbitration_decisions_total.labels(outcome, str(len(viable_results))).inc()

                if arb_span and result.rationale:
                    arb_span.set_attribute("matriz.arbitration_rationale", str(result.rationale))
                    arb_span.set_attribute("matriz.execution_mode", "parallel")

                return result

        elif viable_results:
            if pipeline_span:
                pipeline_span.set_attribute("matriz.result_source", "single_viable_parallel")
            return PipelineResult(
                success=True,
                output=viable_results[0],
                stage_results=all_results
            )
        else:
            if pipeline_span:
                pipeline_span.set_attribute("matriz.failure_reason", "no_viable_results_parallel")
            return PipelineResult(
                success=False,
                output={},
                stage_results=all_results,
                escalation_reason="no_viable_results"
            )

    async def process_adaptive(self, context: Mapping[str, Any]) -> PipelineResult:
        """Adaptive processing that chooses between sequential and parallel based on context."""
        # Simple heuristic: use parallel for complex queries
        query_complexity = len(str(context.get("query", "")))
        stage_count = len(self.stages)

        # Use parallel if:
        # - Parallel is enabled
        # - Query is complex (>100 chars) OR many stages (>3)
        # - At least 2 stages to parallelize
        should_use_parallel = (
            self.parallel_enabled and
            (query_complexity > 100 or stage_count > 3) and
            stage_count >= 2
        )

        chosen_mode = "parallel" if should_use_parallel else "sequential"
        reason = "complex_query" if query_complexity > 100 else "many_stages" if stage_count > 3 else "simple_fallback"

        # Collect execution mode metrics
        parallel_execution_mode_total.labels(
            mode=chosen_mode,
            chosen_reason=reason
        ).inc()

        with stage_span(
            "adaptive_orchestration",
            chosen_mode=chosen_mode,
            query_complexity=query_complexity,
            stage_count=stage_count,
            decision_reason=reason
        ):
            if should_use_parallel:
                return await self.process_query_parallel(context)
            else:
                return await self.process_query(context)