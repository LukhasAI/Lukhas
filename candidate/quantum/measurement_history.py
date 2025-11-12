
import time
from collections import defaultdict
from typing import Any, Dict, List, Mapping

import numpy as np

from .superposition_engine import SuperpositionState


class MeasurementHistory:
    def __init__(self, max_history: int = 1000):
        self.measurements: List[Dict[str, Any]] = []
        self.max_history = max_history

    def record_measurement(
        self,
        state: SuperpositionState,
        context: Mapping[str, Any],
        outcome_label: str,
        probability: float,
    ):
        # Unique identifier for the measurement scenario
        state_id = self._get_state_id(state)
        context_id = self._get_context_id(context)

        entry = {
            "timestamp": time.time(),
            "state_id": state_id,
            "context_id": context_id,
            "outcome_label": outcome_label,
            "probability": probability,
        }

        if len(self.measurements) >= self.max_history:
            self.measurements.pop(0)
        self.measurements.append(entry)

    def estimate_future_bias(
        self, state: SuperpositionState, context: Mapping[str, Any]
    ) -> Dict[str, float]:
        state_id = self._get_state_id(state)
        context_id = self._get_context_id(context)

        # Find measurements of the same state under the same context
        similar_measurements = [
            m
            for m in self.measurements
            if m["state_id"] == state_id and m["context_id"] == context_id
        ]

        if not similar_measurements:
            return {}

        # Calculate the historical probability of each outcome
        outcome_counts = defaultdict(int)
        for m in similar_measurements:
            outcome_counts[m["outcome_label"]] += 1

        num_similar = len(similar_measurements)
        historical_probs = {
            label: count / num_similar for label, count in outcome_counts.items()
        }

        # Simple bias: if an outcome occurred more than average, increase its bias
        avg_prob = 1.0 / len(state.options)
        bias = {
            label: prob - avg_prob for label, prob in historical_probs.items()
        }

        return bias

    def _get_state_id(self, state: SuperpositionState) -> str:
        # Create a stable identifier for the state based on its options
        option_ids = "-".join(sorted([str(opt.get("id", "")) for opt in state.options]))
        return f"state_{option_ids}"

    def _get_context_id(self, context: Mapping[str, Any]) -> str:
        # Create a stable identifier for the context, ignoring volatile keys
        stable_context = {
            k: v for k, v in context.items() if k not in ["bias", "preferred_option"]
        }
        return f"context_{hash(frozenset(stable_context.items()))}"
