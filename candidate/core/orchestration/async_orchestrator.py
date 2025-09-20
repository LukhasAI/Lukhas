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
import math
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional

from lukhas.core.interfaces import CognitiveNodeBase
from lukhas.core.registry import resolve
from .consensus_arbitrator import Proposal, choose
from .meta_controller import MetaController
from .otel import stage_span
from lukhas.metrics import stage_latency, stage_timeouts, guardian_band


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
    """Advanced async orchestrator with resilience patterns."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.meta_controller = MetaController()
        self.stages: List[StageConfig] = []
        self.enabled = self.config.get("MATRIZ_ASYNC", "1") == "1"

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
            guardian_band.labels("escalation").inc()
            return {
                "action": "escalate",
                "reason": "oscillation_detected",
                "stage": stage_config.name
            }

        with stage_latency.labels(stage_config.name).time():
            try:
                with stage_span(stage_config.name, node=node.name, timeout=stage_config.timeout_ms):
                    async def execute():
                        return await node.process(context)

                    result = await asyncio.wait_for(
                        self._with_retry(execute, stage_config),
                        timeout=stage_config.timeout_ms / 1000
                    )

                    # Add constellation metadata
                    if isinstance(result, dict):
                        result["_constellation"] = {
                            "star": self._get_constellation_star(stage_config.name),
                            "stage": stage_config.name,
                            "timestamp": time.time()
                        }

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
        """Process a query through the async pipeline."""
        if not self.enabled:
            return PipelineResult(
                success=False,
                output={},
                stage_results=[],
                escalation_reason="async_disabled"
            )

        results = []
        current_context = dict(context)

        for stage_config in self.stages:
            try:
                # Resolve node from registry
                node = resolve(f"node:{stage_config.name.lower()}")

                # Run stage
                stage_result = await self._run_stage(stage_config, node, current_context)
                results.append(stage_result)

                # Check for escalation
                if stage_result.get("action") == "escalate":
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
                continue
            except Exception as e:
                results.append({
                    "stage": stage_config.name,
                    "status": "error",
                    "error": str(e)
                })
                return PipelineResult(
                    success=False,
                    output={"error": str(e)},
                    stage_results=results,
                    escalation_reason="stage_error"
                )

        # If we have multiple viable results, arbitrate
        viable_results = [r for r in results if r.get("status") != "error" and r.get("action") != "escalate"]

        if len(viable_results) > 1:
            return await self._arbitrate_proposals(viable_results)
        elif viable_results:
            return PipelineResult(
                success=True,
                output=viable_results[0],
                stage_results=results
            )
        else:
            return PipelineResult(
                success=False,
                output={},
                stage_results=results,
                escalation_reason="no_viable_results"
            )