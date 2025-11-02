"""Quantum-inspired measurement collapse utilities."""

from __future__ import annotations

import logging
import math
import random
from dataclasses import dataclass
from typing import Any, Mapping

from .superposition_engine import SuperpositionState

logger = logging.getLogger(__name__)


@dataclass
class MeasurementResult:
    """Result of a quantum-inspired measurement."""

    selected_index: int
    collapsed_option: dict[str, Any]
    probability: float
    post_state: SuperpositionState
    metadata: dict[str, Any]


class QuantumMeasurement:
    """Collapse quantum-inspired superpositions with contextual bias."""

    def __init__(self, *, rng: random.Random | None = None) -> None:
        self._rng = rng or random.Random()

    def collapse(
        self,
        state: SuperpositionState,
        context: Mapping[str, Any] | None = None,
    ) -> MeasurementResult:
        """Collapse a superposition into a single option."""

        if not state.options:
            raise ValueError("Superposition has no options to measure")

        context = dict(context or {})
        # ΛTAG: measurement_bias - incorporate contextual weighting into measurement
        adjusted_probabilities = self._apply_bias(state, context)

        mode = context.get("mode", "stochastic")
        if mode == "argmax":
            selected_index = max(range(len(adjusted_probabilities)), key=adjusted_probabilities.__getitem__)
        else:
            selected_index = self._sample_index(adjusted_probabilities)

        decoherence = float(context.get("decoherence", 0.18))
        decoherence = max(0.0, min(1.0, decoherence))
        post_amplitudes = [amp * math.sqrt(1.0 - decoherence) for amp in state.amplitudes]
        post_amplitudes[selected_index] = complex(math.sqrt(1.0 - decoherence), 0.0)

        norm = math.sqrt(sum(abs(amp) ** 2 for amp in post_amplitudes))
        if norm > 0:
            post_amplitudes = [amp / norm for amp in post_amplitudes]
        post_probabilities = [abs(amp) ** 2 for amp in post_amplitudes]
        post_metadata = dict(state.metadata)
        post_metadata["probabilities"] = post_probabilities
        post_state = SuperpositionState(options=state.options, amplitudes=post_amplitudes, metadata=post_metadata)

        metadata = {
            "basis": context,
            "probabilities": adjusted_probabilities,
            "selected_label": self._option_label(state.options[selected_index]),
            "coherence_loss": decoherence,
        }

        return MeasurementResult(
            selected_index=selected_index,
            collapsed_option=state.options[selected_index],
            probability=adjusted_probabilities[selected_index],
            post_state=post_state,
            metadata=metadata,
        )

    def _apply_bias(
        self,
        state: SuperpositionState,
        context: Mapping[str, Any],
    ) -> list[float]:
        base_probabilities = state.metadata.get("probabilities")
        if not base_probabilities:
            base_probabilities = [1.0 / len(state.options)] * len(state.options)

        bias_map = dict(context.get("bias", {}))
        preferred = context.get("preferred_option")
        if preferred is not None:
            label = str(preferred)
            bias_strength = float(context.get("preferred_weight", 2.0))
            bias_map = {**bias_map, label: bias_map.get(label, 0.0) + bias_strength}
        weighted = []
        for index, probability in enumerate(base_probabilities):
            label = self._option_label(state.options[index])
            modifier = 1.0 + float(bias_map.get(label, 0.0))
            weighted.append(max(0.0, probability * modifier))

        total = sum(weighted)
        if total == 0:
            logger.debug("All biased probabilities zero; reverting to uniform distribution")
            return [1.0 / len(weighted)] * len(weighted)
        return [value / total for value in weighted]

    def _sample_index(self, probabilities: list[float]) -> int:
        threshold = self._rng.random()
        cumulative = 0.0
        for index, probability in enumerate(probabilities):
            cumulative += probability
            if threshold <= cumulative:
                return index
        return len(probabilities) - 1

    def _option_label(self, option: Mapping[str, Any]) -> str:
        for key in ("id", "label", "name", "action"):
            if key in option:
                return str(option[key])
        try:
            return str(hash(frozenset(option.items())))
        except TypeError:
            return repr(sorted(option.items(), key=lambda item: item[0]))


# TODO: Integrate measurement history feedback into future bias estimation.
