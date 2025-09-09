import logging

logger = logging.getLogger(__name__)
"""
Coherence Patch Validator
Validates reasoning coherence and applies patches to maintain logical consistency
"""

import asyncio
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from candidate.core.common import get_logger

logger = get_logger(__name__)


class CoherenceMetrics:
    """Container for coherence validation metrics"""

    def __init__(self):
        self.coherence_score = 0.0
        self.stability_score = 0.0
        self.drift_score = 0.0
        self.symbol_consistency = 0.0
        self.logical_validity = 0.0
        self.temporal_alignment = 0.0
        self.patch_effectiveness = 0.0

    def to_dict(self) -> dict[str, float]:
        return {
            "coherence_score": self.coherence_score,
            "stability_score": self.stability_score,
            "drift_score": self.drift_score,
            "symbol_consistency": self.symbol_consistency,
            "logical_validity": self.logical_validity,
            "temporal_alignment": self.temporal_alignment,
            "patch_effectiveness": self.patch_effectiveness,
        }

    def overall_score(self) -> float:
        """Calculate weighted overall coherence score"""
        weights = {
            "coherence_score": 0.25,
            "stability_score": 0.20,
            "drift_score": 0.15,  # Lower is better for drift
            "symbol_consistency": 0.15,
            "logical_validity": 0.15,
            "temporal_alignment": 0.10,
        }

        score = 0.0
        for metric, weight in weights.items():
            value = getattr(self, metric)
            if metric == "drift_score":
                # Invert drift score (lower drift = higher score)
                value = 1.0 - min(value, 1.0)
            score += value * weight

        return score


class CoherencePatch:
    """Represents a patch to fix coherence issues"""

    def __init__(self, patch_type: str, target: str, operation: str, value: Any):
        self.patch_type = patch_type
        self.target = target
        self.operation = operation
        self.value = value
        self.created_at = datetime.now(timezone.utc)
        self.applied = False
        self.effectiveness = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "patch_type": self.patch_type,
            "target": self.target,
            "operation": self.operation,
            "value": self.value,
            "created_at": self.created_at.isoformat(),
            "applied": self.applied,
            "effectiveness": self.effectiveness,
        }


class CoherencePatchValidator:
    """
    Validates reasoning coherence and generates/applies patches
    to maintain logical consistency across reasoning traces
    """

    def __init__(self):
        self.validation_history = []
        self.patch_history = []
        self.coherence_thresholds = {
            "minimum_coherence": 0.6,
            "acceptable_drift": 0.3,
            "symbol_consistency": 0.7,
            "logical_validity": 0.8,
        }
        self.log_dir = Path("lukhas/logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)

    async def validate_coherence(self, reasoning_trace: dict[str, Any]) -> CoherenceMetrics:
        """
        Validate the coherence of a reasoning trace

        Args:
            reasoning_trace: The trace to validate

        Returns:
            Coherence metrics
        """
        logger.info("Validating reasoning trace coherence")

        metrics = CoherenceMetrics()

        # Calculate individual metrics
        metrics.coherence_score = self._calculate_coherence_score(reasoning_trace)
        metrics.stability_score = self._calculate_stability_score(reasoning_trace)
        metrics.drift_score = self._calculate_drift_score(reasoning_trace)
        metrics.symbol_consistency = self._calculate_symbol_consistency(reasoning_trace)
        metrics.logical_validity = self._calculate_logical_validity(reasoning_trace)
        metrics.temporal_alignment = self._calculate_temporal_alignment(reasoning_trace)

        # Store validation result
        self.validation_history.append(
            {
                "timestamp": datetime.now(timezone.utc),
                "trace_id": reasoning_trace.get("id", "unknown"),
                "metrics": metrics.to_dict(),
                "overall_score": metrics.overall_score(),
            }
        )

        return metrics

    async def validate_and_patch(self, reasoning_trace: dict[str, Any], apply_patches: bool = True) -> dict[str, Any]:
        """
        Validate coherence and apply patches if needed

        Args:
            reasoning_trace: The trace to validate and potentially patch
            apply_patches: Whether to apply generated patches

        Returns:
            Validation and patching results
        """
        # Validate current state
        metrics_before = await self.validate_coherence(reasoning_trace)

        # Check if patching is needed
        issues = self._identify_coherence_issues(metrics_before)

        if not issues:
            return {
                "status": "valid",
                "metrics": metrics_before.to_dict(),
                "patches_applied": 0,
            }

        # Generate patches
        patches = await self._generate_patches(reasoning_trace, issues)

        if not patches:
            return {
                "status": "issues_found_no_patches",
                "metrics": metrics_before.to_dict(),
                "issues": issues,
                "patches_applied": 0,
            }

        # Apply patches if requested
        patched_trace = reasoning_trace.copy()
        patches_applied = []

        if apply_patches:
            for patch in patches:
                try:
                    patched_trace = await self._apply_patch(patched_trace, patch)
                    patch.applied = True
                    patches_applied.append(patch)
                except Exception as e:
                    logger.error(f"Failed to apply patch: {e}")

        # Validate after patching
        metrics_after = await self.validate_coherence(patched_trace)

        # Calculate patch effectiveness
        effectiveness = self._calculate_patch_effectiveness(metrics_before, metrics_after)

        for patch in patches_applied:
            patch.effectiveness = effectiveness

        # Store patch history
        self.patch_history.extend(patches_applied)

        # Log results
        await self._log_validation_results(
            reasoning_trace,
            patched_trace,
            metrics_before,
            metrics_after,
            patches_applied,
        )

        return {
            "status": "patched" if patches_applied else "patches_available",
            "metrics_before": metrics_before.to_dict(),
            "metrics_after": metrics_after.to_dict(),
            "issues": issues,
            "patches_generated": len(patches),
            "patches_applied": len(patches_applied),
            "effectiveness": effectiveness,
            "patched_trace": patched_trace if apply_patches else None,
        }

    def _calculate_coherence_score(self, trace: dict[str, Any]) -> float:
        """Calculate overall coherence score"""
        factors = []

        # Check reasoning path coherence
        path = trace.get("reasoning_path", [])
        if path:
            # Sequential logic flow
            for i in range(1, len(path)):
                prev_step = path[i - 1]
                curr_step = path[i]

                # Check if conclusions build on each other
                if "conclusion" in prev_step and "input" in curr_step:
                    # Simple check - in reality would use NLP
                    if any(word in str(curr_step["input"]) for word in str(prev_step["conclusion"]).split()):
                        factors.append(1.0)
                    else:
                        factors.append(0.5)

        # Check conclusion alignment
        if "conclusion" in trace and path:
            final_step_conclusion = path[-1].get("conclusion")
            if final_step_conclusion == trace["conclusion"]:
                factors.append(1.0)
            else:
                factors.append(0.0)

        return sum(factors) / len(factors) if factors else 0.5

    def _calculate_stability_score(self, trace: dict[str, Any]) -> float:
        """Calculate reasoning stability"""
        path = trace.get("reasoning_path", [])
        if not path:
            return 0.0

        # Check confidence stability
        confidences = [step.get("confidence", 0.5) for step in path]
        if len(confidences) > 1:
            variance = np.var(confidences)
            stability = 1.0 - min(variance * 2, 1.0)
        else:
            stability = 0.5

        # Check strategy consistency
        strategies = [step.get("strategy", "") for step in path]
        if len(set(strategies)) == 1 and len(strategies) > 3:
            # Too consistent might indicate lack of adaptability
            stability *= 0.8

        return stability

    def _calculate_drift_score(self, trace: dict[str, Any]) -> float:
        """Calculate logical drift in reasoning"""
        # Get from trace or calculate
        if "drift_score" in trace:
            return trace["drift_score"]

        path = trace.get("reasoning_path", [])
        if len(path) < 2:
            return 0.0

        # Measure drift between consecutive steps
        drift_values = []
        for i in range(1, len(path)):
            prev = path[i - 1]
            curr = path[i]

            # Strategy changes
            if prev.get("strategy") != curr.get("strategy"):
                drift_values.append(0.3)

            # Confidence changes
            conf_diff = abs(prev.get("confidence", 0.5) - curr.get("confidence", 0.5))
            drift_values.append(conf_diff)

        return sum(drift_values) / len(drift_values) if drift_values else 0.0

    def _calculate_symbol_consistency(self, trace: dict[str, Any]) -> float:
        """Calculate consistency of symbol usage"""
        symbols = trace.get("symbols", [])
        if not symbols:
            return 1.0  # No symbols = consistent

        # Check symbol definitions and usage
        defined_symbols = set()
        used_symbols = set()

        for item in trace.get("reasoning_path", []):
            # Look for symbol definitions
            if "defines" in item:
                defined_symbols.update(item["defines"])
            # Look for symbol usage
            if "uses" in item:
                used_symbols.update(item["uses"])

        # All used symbols should be defined
        undefined_symbols = used_symbols - defined_symbols
        consistency = 1.0 - len(undefined_symbols) / len(used_symbols) if undefined_symbols else 1.0

        return consistency

    def _calculate_logical_validity(self, trace: dict[str, Any]) -> float:
        """Calculate logical validity of reasoning"""
        # Simple heuristic-based validation
        validity_score = 1.0

        path = trace.get("reasoning_path", [])
        for step in path:
            # Check for contradictions
            if "contradiction" in str(step).lower():
                validity_score *= 0.7

            # Check for invalid operations
            if step.get("error"):
                validity_score *= 0.5

            # Check for circular reasoning
            if step.get("conclusion") == step.get("input"):
                validity_score *= 0.8

        return max(validity_score, 0.0)

    def _calculate_temporal_alignment(self, trace: dict[str, Any]) -> float:
        """Calculate temporal consistency"""
        path = trace.get("reasoning_path", [])
        if not path:
            return 1.0

        # Check if timestamps are sequential
        timestamps = []
        for step in path:
            if "timestamp" in step:
                try:
                    ts = datetime.fromisoformat(step["timestamp"].replace("Z", "+00:00"))
                    timestamps.append(ts)
                except BaseException:
                    pass

        if len(timestamps) > 1:
            # Check for proper ordering
            is_ordered = all(timestamps[i] <= timestamps[i + 1] for i in range(len(timestamps) - 1))
            return 1.0 if is_ordered else 0.5

        return 0.8  # Default if no timestamps

    def _identify_coherence_issues(self, metrics: CoherenceMetrics) -> list[dict[str, Any]]:
        """Identify specific coherence issues based on metrics"""
        issues = []

        if metrics.coherence_score < self.coherence_thresholds["minimum_coherence"]:
            issues.append(
                {
                    "type": "low_coherence",
                    "severity": "high",
                    "value": metrics.coherence_score,
                    "threshold": self.coherence_thresholds["minimum_coherence"],
                }
            )

        if metrics.drift_score > self.coherence_thresholds["acceptable_drift"]:
            issues.append(
                {
                    "type": "high_drift",
                    "severity": "medium",
                    "value": metrics.drift_score,
                    "threshold": self.coherence_thresholds["acceptable_drift"],
                }
            )

        if metrics.symbol_consistency < self.coherence_thresholds["symbol_consistency"]:
            issues.append(
                {
                    "type": "symbol_inconsistency",
                    "severity": "medium",
                    "value": metrics.symbol_consistency,
                    "threshold": self.coherence_thresholds["symbol_consistency"],
                }
            )

        if metrics.logical_validity < self.coherence_thresholds["logical_validity"]:
            issues.append(
                {
                    "type": "logical_invalidity",
                    "severity": "high",
                    "value": metrics.logical_validity,
                    "threshold": self.coherence_thresholds["logical_validity"],
                }
            )

        return issues

    async def _generate_patches(self, trace: dict[str, Any], issues: list[dict[str, Any]]) -> list[CoherencePatch]:
        """Generate patches to fix identified issues"""
        patches = []

        for issue in issues:
            if issue["type"] == "low_coherence":
                # Add bridging steps
                patch = CoherencePatch(
                    patch_type="add_bridging_step",
                    target="reasoning_path",
                    operation="insert",
                    value={
                        "strategy": "bridge",
                        "content": "Connecting previous conclusions",
                        "confidence": 0.7,
                    },
                )
                patches.append(patch)

            elif issue["type"] == "high_drift":
                # Stabilize reasoning strategy
                patch = CoherencePatch(
                    patch_type="stabilize_strategy",
                    target="metadata",
                    operation="update",
                    value={"force_strategy": "hybrid", "adaptation_rate": 0.1},
                )
                patches.append(patch)

            elif issue["type"] == "symbol_inconsistency":
                # Define missing symbols
                patch = CoherencePatch(
                    patch_type="define_symbols",
                    target="symbols",
                    operation="extend",
                    value={"auto_defined": True},
                )
                patches.append(patch)

            elif issue["type"] == "logical_invalidity":
                # Add validation step
                patch = CoherencePatch(
                    patch_type="add_validation",
                    target="reasoning_path",
                    operation="append",
                    value={
                        "strategy": "validation",
                        "content": "Validating logical consistency",
                        "confidence": 0.8,
                    },
                )
                patches.append(patch)

        return patches

    async def _apply_patch(self, trace: dict[str, Any], patch: CoherencePatch) -> dict[str, Any]:
        """Apply a coherence patch to a trace"""
        patched_trace = trace.copy()

        if patch.operation == "insert":
            if patch.target == "reasoning_path" and "reasoning_path" in patched_trace:
                # Insert in middle of path
                path = patched_trace["reasoning_path"]
                insert_pos = len(path) // 2
                path.insert(insert_pos, patch.value)

        elif patch.operation == "append":
            if patch.target == "reasoning_path" and "reasoning_path" in patched_trace:
                patched_trace["reasoning_path"].append(patch.value)

        elif patch.operation == "update":
            if patch.target == "metadata":
                if "metadata" not in patched_trace:
                    patched_trace["metadata"] = {}
                patched_trace["metadata"].update(patch.value)

        elif patch.operation == "extend" and patch.target == "symbols":
            if "symbols" not in patched_trace:
                patched_trace["symbols"] = []
            # Auto-define symbols based on usage
            patched_trace["symbols"].append("auto_defined_symbols")

        return patched_trace

    def _calculate_patch_effectiveness(
        self, metrics_before: CoherenceMetrics, metrics_after: CoherenceMetrics
    ) -> float:
        """Calculate how effective patches were"""
        before_score = metrics_before.overall_score()
        after_score = metrics_after.overall_score()

        improvement = (after_score - before_score) / before_score if before_score > 0 else after_score

        return max(0.0, min(1.0, improvement))

    async def _log_validation_results(
        self,
        trace_before: dict[str, Any],
        trace_after: dict[str, Any],
        metrics_before: CoherenceMetrics,
        metrics_after: CoherenceMetrics,
        patches_applied: list[CoherencePatch],
    ):
        """Log validation and patching results"""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trace_id": trace_before.get("id", "unknown"),
            "metrics_before": metrics_before.to_dict(),
            "metrics_after": metrics_after.to_dict(),
            "coherence_delta": metrics_after.coherence_score - metrics_before.coherence_score,
            "stability_delta": metrics_after.stability_score - metrics_before.stability_score,
            "drift_delta": metrics_after.drift_score - metrics_before.drift_score,
            "patches_applied": [p.to_dict() for p in patches_applied],
            "overall_improvement": self._calculate_patch_effectiveness(metrics_before, metrics_after),
        }

        # Write to log file
        log_file = self.log_dir / "coherence_validation.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    def get_validation_summary(self, last_n: int = 10) -> dict[str, Any]:
        """Get summary of recent validations"""
        recent = self.validation_history[-last_n:]

        if not recent:
            return {"status": "no_history"}

        avg_scores = defaultdict(list)
        for validation in recent:
            metrics = validation["metrics"]
            for key, value in metrics.items():
                avg_scores[key].append(value)

        summary = {
            "validations_analyzed": len(recent),
            "average_metrics": {key: sum(values) / len(values) for key, values in avg_scores.items()},
            "patches_applied_total": len([p for p in self.patch_history if p.applied]),
            "average_patch_effectiveness": (
                sum(p.effectiveness for p in self.patch_history if p.applied)
                / len([p for p in self.patch_history if p.applied])
                if any(p.applied for p in self.patch_history)
                else 0.0
            ),
        }

        return summary


# Backward compatibility function
def validate_harmonization(trace_before: dict[str, Any], trace_after: dict[str, Any]) -> dict[str, Any]:
    """
    Compare pre/post traces to determine effectiveness of harmonization.

    Returns:
        dict with 'coherence_delta', 'symbols_resolved', 'residual_drift'
    """
    # Use the new validator
    validator = CoherencePatchValidator()

    # Calculate metrics
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        metrics_before = loop.run_until_complete(validator.validate_coherence(trace_before))
        metrics_after = loop.run_until_complete(validator.validate_coherence(trace_after))

        # Calculate deltas
        coherence_delta = metrics_after.coherence_score - metrics_before.coherence_score
        stability_delta = metrics_after.stability_score - metrics_before.stability_score

        # Symbol resolution
        symbols_before = set(trace_before.get("symbols", []))
        symbols_after = set(trace_after.get("symbols", []))
        symbols_resolved = list(symbols_before - symbols_after)

        # Residual drift
        residual_drift = metrics_after.drift_score

        result = {
            "coherence_delta": coherence_delta,
            "stability_delta": stability_delta,
            "symbols_resolved": symbols_resolved,
            "residual_drift": residual_drift,
            "status": "success" if coherence_delta > 0 else "failure",
        }

        # Log results
        log_dir = Path("lukhas/logs")
        log_dir.mkdir(parents=True, exist_ok=True)

        with open(log_dir / "harmonization_results.jsonl", "a") as f:
            log_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                **result,
            }
            f.write(json.dumps(log_entry) + "\n")

        return result

    finally:
        loop.close()