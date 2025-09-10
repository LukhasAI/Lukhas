import logging
from datetime import timezone

logger = logging.getLogger(__name__)
"""
Reasoning Metrics
Comprehensive metrics for measuring reasoning performance and quality
"""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

import numpy as np

from candidate.core.common import get_logger

logger = get_logger(__name__)


@dataclass
class ReasoningMetrics:
    """Container for various reasoning metrics"""

    logic_drift: float = 0.0
    recall_efficiency: float = 0.0
    coherence_score: float = 0.0
    strategy_effectiveness: dict[str, float] = field(default_factory=dict)
    temporal_consistency: float = 0.0
    conclusion_stability: float = 0.0
    path_optimality: float = 0.0
    confidence_calibration: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class ReasoningMetricsCalculator:
    """
    Calculates comprehensive metrics for reasoning system performance
    """

    def __init__(self):
        self.metric_history = []
        self.baseline_metrics = None
        self.metric_weights = {
            "logic_drift": 0.15,
            "recall_efficiency": 0.20,
            "coherence_score": 0.15,
            "temporal_consistency": 0.10,
            "conclusion_stability": 0.15,
            "path_optimality": 0.15,
            "confidence_calibration": 0.10,
        }

    async def calculate_all_metrics(
        self,
        reasoning_trace: dict[str, Any],
        memory_context: Optional[dict[str, Any]] = None,
        previous_traces: Optional[list[dict[str, Any]]] = None,
    ) -> ReasoningMetrics:
        """
        Calculate all reasoning metrics

        Args:
            reasoning_trace: Current reasoning trace
            memory_context: Memory access patterns and efficiency
            previous_traces: Historical reasoning traces for comparison

        Returns:
            Comprehensive metrics object
        """
        metrics = ReasoningMetrics()

        # Calculate individual metrics
        if previous_traces:
            metrics.logic_drift = self._calculate_logic_drift(previous_traces[-1], reasoning_trace)
            metrics.temporal_consistency = self._calculate_temporal_consistency(previous_traces, reasoning_trace)
            metrics.conclusion_stability = self._calculate_conclusion_stability(previous_traces)

        if memory_context:
            metrics.recall_efficiency = self._calculate_recall_efficiency(
                memory_context.get("invoked_memories", []),
                memory_context.get("optimal_memories", []),
            )

        metrics.coherence_score = self._calculate_coherence_score(reasoning_trace)
        metrics.strategy_effectiveness = self._calculate_strategy_effectiveness(reasoning_trace)
        metrics.path_optimality = self._calculate_path_optimality(reasoning_trace)
        metrics.confidence_calibration = self._calculate_confidence_calibration(reasoning_trace)

        # Add metadata
        metrics.metadata = {
            "calculated_at": datetime.now(timezone.utc).isoformat(),
            "trace_id": reasoning_trace.get("id", "unknown"),
            "overall_score": self._calculate_overall_score(metrics),
        }

        # Store in history
        self.metric_history.append(metrics)

        return metrics

    def _calculate_logic_drift(self, previous_trace: dict[str, Any], current_trace: dict[str, Any]) -> float:
        """
        Calculate drift between consecutive reasoning traces

        Measures how much the reasoning approach has changed
        """
        if not previous_trace or not current_trace:
            return 0.0

        drift_factors = []

        # Strategy drift
        prev_strategies = set(previous_trace.get("strategies_used", []))
        curr_strategies = set(current_trace.get("strategies_used", []))
        if prev_strategies or curr_strategies:
            strategy_overlap = len(prev_strategies & curr_strategies)
            strategy_union = len(prev_strategies | curr_strategies)
            strategy_drift = 1.0 - (strategy_overlap / strategy_union if strategy_union > 0 else 0)
            drift_factors.append(strategy_drift)

        # Confidence drift
        prev_conf = previous_trace.get("overall_confidence", 0.5)
        curr_conf = current_trace.get("overall_confidence", 0.5)
        conf_drift = abs(curr_conf - prev_conf)
        drift_factors.append(conf_drift)

        # Path length drift
        prev_path_len = len(previous_trace.get("reasoning_path", []))
        curr_path_len = len(current_trace.get("reasoning_path", []))
        if prev_path_len > 0:
            path_drift = abs(curr_path_len - prev_path_len) / prev_path_len
            drift_factors.append(min(path_drift, 1.0))

        # Conclusion similarity
        prev_conclusion = str(previous_trace.get("conclusion", ""))
        curr_conclusion = str(current_trace.get("conclusion", ""))
        conclusion_drift = 0.0 if prev_conclusion == curr_conclusion else 1.0
        drift_factors.append(conclusion_drift * 0.5)  # Weight conclusion drift less

        return sum(drift_factors) / len(drift_factors) if drift_factors else 0.0

    def _calculate_recall_efficiency(
        self,
        invoked_memories: list[dict[str, Any]],
        optimal_memories: list[dict[str, Any]],
    ) -> float:
        """
        Calculate memory recall efficiency

        Measures how well the system recalled relevant memories
        """
        if not optimal_memories:
            return 1.0 if not invoked_memories else 0.0

        invoked_keys = {mem.get("key") for mem in invoked_memories if mem.get("key")}
        optimal_keys = {mem.get("key") for mem in optimal_memories if mem.get("key")}

        if not optimal_keys:
            return 0.5  # No optimal memories defined

        # Precision: What fraction of invoked memories were relevant?
        precision = len(invoked_keys & optimal_keys) / len(invoked_keys) if invoked_keys else 0.0

        # Recall: What fraction of relevant memories were invoked?
        recall = len(invoked_keys & optimal_keys) / len(optimal_keys)

        # F1 score combines precision and recall
        f1_score = 2 * (precision * recall) / (precision + recall) if precision + recall > 0 else 0.0

        # Also consider efficiency - penalize for invoking too many memories
        efficiency_penalty = min(len(invoked_memories) / (2 * len(optimal_memories)), 1.0) if optimal_memories else 0.5

        return f1_score * (2.0 - efficiency_penalty)

    def _calculate_coherence_score(self, reasoning_trace: dict[str, Any]) -> float:
        """
        Calculate reasoning coherence

        Measures internal consistency of the reasoning process
        """
        coherence_factors = []

        # Check if reasoning path is present
        reasoning_path = reasoning_trace.get("reasoning_path", [])
        if not reasoning_path:
            return 0.0

        # Sequential confidence consistency
        confidences = [step.get("confidence", 0.0) for step in reasoning_path]
        if len(confidences) > 1:
            # Check for wild confidence swings
            conf_diffs = [abs(confidences[i] - confidences[i - 1]) for i in range(1, len(confidences))]
            avg_conf_diff = sum(conf_diffs) / len(conf_diffs)
            conf_consistency = 1.0 - min(avg_conf_diff, 1.0)
            coherence_factors.append(conf_consistency)

        # Strategy consistency
        strategies_used = [step.get("strategy", "") for step in reasoning_path]
        if len(set(strategies_used)) == 1 and len(strategies_used) > 3:
            # Using only one strategy for many steps might indicate lack of adaptability
            coherence_factors.append(0.7)
        else:
            # Diverse strategies indicate good adaptability
            strategy_diversity = len(set(strategies_used)) / len(strategies_used) if strategies_used else 0
            coherence_factors.append(min(strategy_diversity * 2, 1.0))

        # Conclusion alignment
        final_conclusion = reasoning_trace.get("conclusion")
        if final_conclusion and reasoning_path:
            # Check if conclusion aligns with the reasoning path
            last_step = reasoning_path[-1]
            if last_step.get("conclusion") == final_conclusion:
                coherence_factors.append(1.0)
            else:
                coherence_factors.append(0.5)

        return sum(coherence_factors) / len(coherence_factors) if coherence_factors else 0.0

    def _calculate_strategy_effectiveness(self, reasoning_trace: dict[str, Any]) -> dict[str, float]:
        """
        Calculate effectiveness of each reasoning strategy used
        """
        strategy_performance = defaultdict(list)

        reasoning_path = reasoning_trace.get("reasoning_path", [])
        for step in reasoning_path:
            strategy = step.get("strategy")
            confidence = step.get("confidence", 0.0)
            if strategy:
                strategy_performance[strategy].append(confidence)

        # Calculate average effectiveness for each strategy
        effectiveness = {}
        for strategy, confidences in strategy_performance.items():
            effectiveness[strategy] = sum(confidences) / len(confidences)

        return effectiveness

    def _calculate_temporal_consistency(
        self, previous_traces: list[dict[str, Any]], current_trace: dict[str, Any]
    ) -> float:
        """
        Calculate consistency over time

        Measures how stable reasoning is across multiple iterations
        """
        if len(previous_traces) < 2:
            return 1.0  # Not enough history

        # Look at conclusions over time
        conclusions = [trace.get("conclusion") for trace in previous_traces[-5:]]
        conclusions.append(current_trace.get("conclusion"))

        # Count unique conclusions
        unique_conclusions = len({str(c) for c in conclusions if c is not None})
        total_conclusions = len([c for c in conclusions if c is not None])

        if total_conclusions == 0:
            return 0.0

        # More unique conclusions = less consistency
        consistency = 1.0 - (unique_conclusions - 1) / total_conclusions

        # Also check confidence stability
        confidences = [trace.get("overall_confidence", 0.5) for trace in previous_traces[-5:]]
        confidences.append(current_trace.get("overall_confidence", 0.5))

        if len(confidences) > 1:
            conf_variance = np.var(confidences)
            conf_stability = 1.0 - min(conf_variance * 2, 1.0)
            consistency = (consistency + conf_stability) / 2

        return consistency

    def _calculate_conclusion_stability(self, traces: list[dict[str, Any]]) -> float:
        """
        Calculate how stable conclusions are across reasoning attempts
        """
        if len(traces) < 2:
            return 1.0

        conclusions = [str(trace.get("conclusion", "")) for trace in traces[-10:]]

        # Count conclusion changes
        changes = sum(1 for i in range(1, len(conclusions)) if conclusions[i] != conclusions[i - 1])

        # Normalize by number of traces
        stability = 1.0 - (changes / (len(conclusions) - 1))

        return stability

    def _calculate_path_optimality(self, reasoning_trace: dict[str, Any]) -> float:
        """
        Calculate how optimal the reasoning path was

        Shorter paths with high confidence are considered more optimal
        """
        path = reasoning_trace.get("reasoning_path", [])
        if not path:
            return 0.0

        path_length = len(path)
        final_confidence = reasoning_trace.get("overall_confidence", 0.0)

        # Ideal path length depends on problem complexity
        # Assume 3-7 steps is optimal for most problems
        if path_length < 3:
            length_score = path_length / 3
        elif path_length <= 7:
            length_score = 1.0
        else:
            # Penalize very long paths
            length_score = 7 / path_length

        # Combine with confidence
        optimality = (length_score + final_confidence) / 2

        # Bonus for monotonically increasing confidence
        confidences = [step.get("confidence", 0.0) for step in path]
        if all(confidences[i] >= confidences[i - 1] for i in range(1, len(confidences))):
            optimality = min(optimality * 1.1, 1.0)

        return optimality

    def _calculate_confidence_calibration(self, reasoning_trace: dict[str, Any]) -> float:
        """
        Calculate how well calibrated the confidence scores are

        Well-calibrated systems have confidence scores that match actual accuracy
        """
        # In a real system, this would compare predicted confidence with actual outcomes
        # For now, we'll use heuristics

        path = reasoning_trace.get("reasoning_path", [])
        if not path:
            return 0.0

        confidences = [step.get("confidence", 0.0) for step in path]

        # Check for overconfidence (too many high scores)
        high_conf_ratio = len([c for c in confidences if c > 0.9]) / len(confidences)
        if high_conf_ratio > 0.5:
            calibration = 0.7  # Likely overconfident
        elif high_conf_ratio < 0.1:
            calibration = 0.8  # Might be underconfident
        else:
            calibration = 0.9  # Good distribution

        # Check for appropriate uncertainty
        avg_confidence = sum(confidences) / len(confidences)
        if 0.6 <= avg_confidence <= 0.8:
            calibration = min(calibration * 1.1, 1.0)

        return calibration

    def _calculate_overall_score(self, metrics: ReasoningMetrics) -> float:
        """
        Calculate weighted overall score
        """
        scores = {
            "logic_drift": 1.0 - metrics.logic_drift,  # Lower drift is better
            "recall_efficiency": metrics.recall_efficiency,
            "coherence_score": metrics.coherence_score,
            "temporal_consistency": metrics.temporal_consistency,
            "conclusion_stability": metrics.conclusion_stability,
            "path_optimality": metrics.path_optimality,
            "confidence_calibration": metrics.confidence_calibration,
        }

        weighted_sum = sum(scores[metric] * weight for metric, weight in self.metric_weights.items())

        return weighted_sum

    def get_metric_trends(self, window_size: int = 10) -> dict[str, list[float]]:
        """
        Get trends for each metric over recent history
        """
        if not self.metric_history:
            return {}

        recent_metrics = self.metric_history[-window_size:]

        trends = {
            "logic_drift": [m.logic_drift for m in recent_metrics],
            "recall_efficiency": [m.recall_efficiency for m in recent_metrics],
            "coherence_score": [m.coherence_score for m in recent_metrics],
            "temporal_consistency": [m.temporal_consistency for m in recent_metrics],
            "conclusion_stability": [m.conclusion_stability for m in recent_metrics],
            "path_optimality": [m.path_optimality for m in recent_metrics],
            "confidence_calibration": [m.confidence_calibration for m in recent_metrics],
            "overall_score": [m.metadata.get("overall_score", 0) for m in recent_metrics],
        }

        return trends

    def set_baseline(self, metrics: ReasoningMetrics):
        """
        Set baseline metrics for comparison
        """
        self.baseline_metrics = metrics
        logger.info("Baseline metrics set")

    def compare_to_baseline(self, current_metrics: ReasoningMetrics) -> dict[str, float]:
        """
        Compare current metrics to baseline
        """
        if not self.baseline_metrics:
            return {}

        comparison = {}
        for metric in [
            "logic_drift",
            "recall_efficiency",
            "coherence_score",
            "temporal_consistency",
            "conclusion_stability",
            "path_optimality",
            "confidence_calibration",
        ]:
            baseline_val = getattr(self.baseline_metrics, metric)
            current_val = getattr(current_metrics, metric)

            if baseline_val > 0:
                comparison[metric] = (current_val - baseline_val) / baseline_val
            else:
                comparison[metric] = current_val

        return comparison


# Global calculator instance
_metrics_calculator = None


def get_metrics_calculator() -> ReasoningMetricsCalculator:
    """Get or create the global metrics calculator"""
    global _metrics_calculator
    if _metrics_calculator is None:
        _metrics_calculator = ReasoningMetricsCalculator()
    return _metrics_calculator


# Backward compatibility functions
# LUKHAS_TAG: reasoning_metric
def logic_drift_index(previous_trace: dict[str, Any], current_trace: dict[str, Any]) -> float:
    """
    Calculates a drift index between two reasoning traces.
    """
    calculator = get_metrics_calculator()
    return calculator._calculate_logic_drift(previous_trace, current_trace)


# LUKHAS_TAG: reasoning_metric
def recall_efficiency_score(invoked_memories: list[dict[str, Any]], optimal_memories: list[dict[str, Any]]) -> float:
    """
    Calculates a recall efficiency score.
    """
    calculator = get_metrics_calculator()
    return calculator._calculate_recall_efficiency(invoked_memories, optimal_memories)
