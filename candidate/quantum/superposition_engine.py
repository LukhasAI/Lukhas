"""Quantum-inspired superposition utilities for the QI-AGI system."""
from __future__ import annotations

import cmath
import hashlib
import logging
import math
import random
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class SuperpositionState:
    """Container for a quantum-inspired superposition state."""

    options: list[dict[str, Any]]
    amplitudes: list[complex]
    metadata: dict[str, Any]


class QuantumSuperpositionEngine:
    """Create and manage quantum-inspired superposition states."""

    def __init__(self, *, rng: Any | None = None) -> None:
        self._rng = rng or random.Random()

    def create_state(
        self,
        options: Sequence[Mapping[str, Any]],
        context: Mapping[str, Any] | None = None,
    ) -> SuperpositionState:
        """Create a normalized superposition state with interference patterns."""

        if not options:
            raise ValueError("Cannot create a superposition without options")

        context = context or {}
        amplitudes = [
            self._compute_amplitude(index, option, context)
            for index, option in enumerate(options)
        ]

        # ΛTAG: interference_modulation - apply contextual interference effects
        interference_events: list[dict[str, Any]] = []
        for event in context.get("interference", []):
            self._apply_interference(event, amplitudes, options, interference_events)

        norm = math.sqrt(sum(abs(a) ** 2 for a in amplitudes))
        if norm == 0:
            logger.debug("Amplitude norm was zero; reverting to uniform distribution")
            amplitudes = [complex(1.0, 0.0) for _ in amplitudes]
            norm = math.sqrt(len(amplitudes))

        amplitudes = [amp / norm for amp in amplitudes]
        probabilities = [abs(amp) ** 2 for amp in amplitudes]

        coherence = max(0.0, min(1.0, 1.0 - (len(interference_events) * 0.05)))
        metadata = {
            "probabilities": probabilities,
            "interference_events": interference_events,
            "coherence": coherence,
        }
        return SuperpositionState(options=[dict(o) for o in options], amplitudes=amplitudes, metadata=metadata)

    def _compute_amplitude(
        self,
        index: int,
        option: Mapping[str, Any],
        context: Mapping[str, Any],
    ) -> complex:
        base_weight = self._extract_weight(option)
        bias = self._contextual_bias(option, context)
        weighted = max(0.0, base_weight * (1.0 + bias))

        phase = self._resolve_phase(index, option, context)
        amplitude = cmath.rect(weighted, phase)
        return amplitude

    def _extract_weight(self, option: Mapping[str, Any]) -> float:
        for key in ("weight", "score", "confidence", "priority"):
            if key in option:
                try:
                    return float(option[key])
                except (TypeError, ValueError):
                    logger.debug("Non-numeric %s value %s; skipping", key, option[key])
        return 1.0

    def _contextual_bias(self, option: Mapping[str, Any], context: Mapping[str, Any]) -> float:
        label = self._option_label(option)
        bias_map = context.get("bias", {})
        if label in bias_map:
            return float(bias_map[label])
        return float(context.get("global_bias", 0.0))

    def _resolve_phase(
        self,
        index: int,
        option: Mapping[str, Any],
        context: Mapping[str, Any],
    ) -> float:
        if "phase" in option:
            base_phase = float(option["phase"])
        else:
            phase_bias = context.get("phase_bias", {})
            label = self._option_label(option)
            if label in phase_bias:
                base_phase = float(phase_bias[label])
            else:
                basis = f"{label}:{index}:{context.get('phase_seed', '')}"
                digest = hashlib.sha256(basis.encode("utf-8")).digest()
                base_phase = (int.from_bytes(digest[:8], "big") % 360) * math.pi / 180.0

        noise = float(context.get("phase_noise", 0.0))
        if noise:
            base_phase = (base_phase + (self._rng.random() - 0.5) * 2 * noise) % (2 * math.pi)
        return base_phase

    def _apply_interference(
        self,
        event: Mapping[str, Any],
        amplitudes: list[complex],
        options: Sequence[Mapping[str, Any]],
        trace: list[dict[str, Any]],
    ) -> None:
        source_label = event.get("source")
        target_label = event.get("target")
        strength = float(event.get("strength", 0.0))
        if strength == 0.0:
            return

        source_index = self._resolve_index(source_label, options)
        target_index = self._resolve_index(target_label, options)
        if source_index is None or target_index is None:
            return

        phase_diff = cmath.phase(amplitudes[source_index]) - cmath.phase(amplitudes[target_index])
        alignment = math.cos(phase_diff)
        delta = strength * alignment * amplitudes[target_index]
        amplitudes[source_index] += delta
        amplitudes[target_index] -= delta
        trace.append(
            {
                "source": source_label,
                "target": target_label,
                "strength": strength,
                "alignment": alignment,
            }
        )

    def _resolve_index(
        self,
        label: str | None,
        options: Sequence[Mapping[str, Any]],
    ) -> int | None:
        if label is None:
            return None
        for index, option in enumerate(options):
            if self._option_label(option) == label:
                return index
        return None

    def _option_label(self, option: Mapping[str, Any]) -> str:
        for key in ("id", "label", "name", "action"):
            if key in option:
                return str(option[key])
        try:
            return str(hash(frozenset(option.items())))
        except TypeError:
            return repr(sorted(option.items(), key=lambda item: item[0]))


# TODO: Extend with entanglement modelling across multiple superpositions.
