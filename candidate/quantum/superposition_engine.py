"""Quantum-inspired superposition utilities for the QI-AGI system."""
from __future__ import annotations

import cmath
import hashlib
import logging
import math
import random
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class SuperpositionState:
    """Container for a quantum-inspired superposition state."""

    options: list[dict[str, Any]]
    amplitudes: list[complex]
    metadata: dict[str, Any]


class EntanglementType(Enum):
    """Types of quantum entanglement between superpositions."""

    CORRELATED = "correlated"  # Measurement correlation
    ANTI_CORRELATED = "anti_correlated"  # Opposite outcomes
    CONDITIONAL = "conditional"  # One depends on other
    FEEDBACK = "feedback"  # Bidirectional influence


@dataclass
class EntanglementLink:
    """Link representing entanglement between two superposition states."""

    state_a_id: str
    state_b_id: str
    entanglement_type: EntanglementType
    strength: float  # 0.0 to 1.0
    phase_offset: float = 0.0
    created_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EntangledSuperpositionState:
    """Container for a superposition state with entanglement tracking."""

    state_id: str
    superposition: SuperpositionState
    entanglement_links: list[EntanglementLink] = field(default_factory=list)
    measurement_history: list[dict[str, Any]] = field(default_factory=list)


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


class QuantumEntanglementManager:
    """
    Manage entanglement relationships between multiple superposition states.

    Tracks and enforces quantum-inspired correlations between superpositions,
    supporting measurement collapse propagation and correlated state evolution.
    """

    def __init__(self):
        """Initialize entanglement manager."""
        self._states: dict[str, EntangledSuperpositionState] = {}
        self._entanglement_graph: dict[str, list[str]] = {}  # state_id -> list of connected state_ids

    def register_state(
        self, state_id: str, superposition: SuperpositionState
    ) -> EntangledSuperpositionState:
        """
        Register a superposition state for entanglement tracking.

        Args:
            state_id: Unique identifier for this state
            superposition: The superposition state to track

        Returns:
            EntangledSuperpositionState with tracking metadata
        """
        if state_id in self._states:
            raise ValueError(f"State {state_id} already registered")

        entangled_state = EntangledSuperpositionState(
            state_id=state_id, superposition=superposition
        )

        self._states[state_id] = entangled_state
        self._entanglement_graph[state_id] = []

        logger.info("Registered entangled state", state_id=state_id)
        return entangled_state

    def create_entanglement(
        self,
        state_a_id: str,
        state_b_id: str,
        entanglement_type: EntanglementType,
        strength: float = 1.0,
        phase_offset: float = 0.0,
    ) -> EntanglementLink:
        """
        Create an entanglement link between two superposition states.

        Args:
            state_a_id: First state identifier
            state_b_id: Second state identifier
            entanglement_type: Type of entanglement
            strength: Entanglement strength (0.0 to 1.0)
            phase_offset: Phase offset between states

        Returns:
            EntanglementLink describing the connection
        """
        if state_a_id not in self._states:
            raise ValueError(f"State {state_a_id} not registered")
        if state_b_id not in self._states:
            raise ValueError(f"State {state_b_id} not registered")

        if not 0.0 <= strength <= 1.0:
            raise ValueError("Entanglement strength must be between 0.0 and 1.0")

        link = EntanglementLink(
            state_a_id=state_a_id,
            state_b_id=state_b_id,
            entanglement_type=entanglement_type,
            strength=strength,
            phase_offset=phase_offset,
        )

        # Add link to both states
        self._states[state_a_id].entanglement_links.append(link)
        self._states[state_b_id].entanglement_links.append(link)

        # Update entanglement graph
        if state_b_id not in self._entanglement_graph[state_a_id]:
            self._entanglement_graph[state_a_id].append(state_b_id)
        if state_a_id not in self._entanglement_graph[state_b_id]:
            self._entanglement_graph[state_b_id].append(state_a_id)

        logger.info(
            "Created entanglement",
            state_a=state_a_id,
            state_b=state_b_id,
            type=entanglement_type.value,
            strength=strength,
        )

        return link

    def measure_with_entanglement(
        self, state_id: str, option_index: int | None = None
    ) -> dict[str, Any]:
        """
        Measure a superposition state and propagate measurement effects through entanglement.

        Args:
            state_id: State to measure
            option_index: Specific option index to collapse to (None for probabilistic)

        Returns:
            Dict with measurement result and entanglement effects
        """
        if state_id not in self._states:
            raise ValueError(f"State {state_id} not registered")

        entangled_state = self._states[state_id]
        superposition = entangled_state.superposition

        # Perform measurement (collapse)
        if option_index is None:
            # Probabilistic measurement based on amplitudes
            probabilities = superposition.metadata["probabilities"]
            option_index = np.random.choice(len(probabilities), p=probabilities)

        measured_option = superposition.options[option_index]
        measured_amplitude = superposition.amplitudes[option_index]

        # Record measurement
        measurement = {
            "state_id": state_id,
            "option_index": option_index,
            "option": measured_option,
            "amplitude": measured_amplitude,
            "probability": abs(measured_amplitude) ** 2,
            "timestamp": time.time(),
        }

        entangled_state.measurement_history.append(measurement)

        # Propagate entanglement effects
        entanglement_effects = self._propagate_measurement(
            state_id, option_index, measured_amplitude
        )

        return {
            "measurement": measurement,
            "entanglement_effects": entanglement_effects,
            "entangled_states_affected": len(entanglement_effects),
        }

    def _propagate_measurement(
        self, measured_state_id: str, measured_index: int, measured_amplitude: complex
    ) -> list[dict[str, Any]]:
        """
        Propagate measurement effects to entangled states.

        Args:
            measured_state_id: ID of measured state
            measured_index: Index of measured option
            measured_amplitude: Amplitude of measured option

        Returns:
            List of effects on entangled states
        """
        effects = []
        measured_state = self._states[measured_state_id]

        for link in measured_state.entanglement_links:
            # Determine the other state in the entanglement
            other_state_id = (
                link.state_b_id if link.state_a_id == measured_state_id else link.state_a_id
            )

            if other_state_id not in self._states:
                continue

            other_state = self._states[other_state_id]
            other_superposition = other_state.superposition

            # Apply entanglement effect based on type
            effect = self._apply_entanglement_effect(
                link, measured_index, measured_amplitude, other_superposition
            )

            if effect:
                effects.append(
                    {
                        "target_state_id": other_state_id,
                        "entanglement_type": link.entanglement_type.value,
                        "strength": link.strength,
                        "amplitude_changes": effect,
                    }
                )

        return effects

    def _apply_entanglement_effect(
        self,
        link: EntanglementLink,
        measured_index: int,
        measured_amplitude: complex,
        target_superposition: SuperpositionState,
    ) -> dict[str, Any] | None:
        """
        Apply entanglement effect to target superposition based on link type.

        Args:
            link: Entanglement link
            measured_index: Index of measured option in source
            measured_amplitude: Amplitude of measured option
            target_superposition: Target superposition to modify

        Returns:
            Dict describing amplitude changes or None
        """
        if link.entanglement_type == EntanglementType.CORRELATED:
            # Correlated: Boost corresponding option in target
            return self._apply_correlated_entanglement(
                link, measured_index, measured_amplitude, target_superposition
            )

        elif link.entanglement_type == EntanglementType.ANTI_CORRELATED:
            # Anti-correlated: Suppress corresponding option in target
            return self._apply_anti_correlated_entanglement(
                link, measured_index, measured_amplitude, target_superposition
            )

        elif link.entanglement_type == EntanglementType.CONDITIONAL:
            # Conditional: Modify target based on measurement value
            return self._apply_conditional_entanglement(
                link, measured_index, measured_amplitude, target_superposition
            )

        elif link.entanglement_type == EntanglementType.FEEDBACK:
            # Feedback: Bidirectional influence (symmetric)
            return self._apply_feedback_entanglement(
                link, measured_index, measured_amplitude, target_superposition
            )

        return None

    def _apply_correlated_entanglement(
        self,
        link: EntanglementLink,
        measured_index: int,
        measured_amplitude: complex,
        target_superposition: SuperpositionState,
    ) -> dict[str, Any]:
        """Apply correlated entanglement (boost corresponding option)."""
        if measured_index >= len(target_superposition.amplitudes):
            return {}

        old_amplitude = target_superposition.amplitudes[measured_index]

        # Apply phase offset and strength
        phase_factor = cmath.exp(1j * link.phase_offset)
        boost = link.strength * measured_amplitude * phase_factor

        target_superposition.amplitudes[measured_index] = old_amplitude + boost

        # Renormalize
        self._renormalize_amplitudes(target_superposition)

        return {
            "option_index": measured_index,
            "old_amplitude": old_amplitude,
            "new_amplitude": target_superposition.amplitudes[measured_index],
            "effect": "boost",
        }

    def _apply_anti_correlated_entanglement(
        self,
        link: EntanglementLink,
        measured_index: int,
        measured_amplitude: complex,
        target_superposition: SuperpositionState,
    ) -> dict[str, Any]:
        """Apply anti-correlated entanglement (suppress corresponding option)."""
        if measured_index >= len(target_superposition.amplitudes):
            return {}

        old_amplitude = target_superposition.amplitudes[measured_index]

        # Suppress corresponding option
        suppression = link.strength * abs(measured_amplitude)
        target_superposition.amplitudes[measured_index] = old_amplitude * (1 - suppression)

        # Renormalize
        self._renormalize_amplitudes(target_superposition)

        return {
            "option_index": measured_index,
            "old_amplitude": old_amplitude,
            "new_amplitude": target_superposition.amplitudes[measured_index],
            "effect": "suppression",
        }

    def _apply_conditional_entanglement(
        self,
        link: EntanglementLink,
        measured_index: int,
        measured_amplitude: complex,
        target_superposition: SuperpositionState,
    ) -> dict[str, Any]:
        """Apply conditional entanglement (modify all options based on measurement)."""
        changes = []

        measurement_magnitude = abs(measured_amplitude)

        for i, amplitude in enumerate(target_superposition.amplitudes):
            old_amplitude = amplitude

            # Conditional modification based on measurement strength
            if i == measured_index:
                # Enhance matching option
                factor = 1.0 + link.strength * measurement_magnitude
            else:
                # Reduce non-matching options
                factor = 1.0 - link.strength * measurement_magnitude * 0.5

            target_superposition.amplitudes[i] = amplitude * factor

            changes.append(
                {
                    "option_index": i,
                    "old_amplitude": old_amplitude,
                    "new_amplitude": target_superposition.amplitudes[i],
                }
            )

        # Renormalize
        self._renormalize_amplitudes(target_superposition)

        return {"effect": "conditional", "changes": changes}

    def _apply_feedback_entanglement(
        self,
        link: EntanglementLink,
        measured_index: int,
        measured_amplitude: complex,
        target_superposition: SuperpositionState,
    ) -> dict[str, Any]:
        """Apply feedback entanglement (bidirectional influence)."""
        # Similar to correlated but with phase consideration
        if measured_index >= len(target_superposition.amplitudes):
            return {}

        old_amplitude = target_superposition.amplitudes[measured_index]

        # Bidirectional feedback with phase
        phase_factor = cmath.exp(1j * link.phase_offset)
        feedback = link.strength * measured_amplitude * phase_factor * 0.5

        target_superposition.amplitudes[measured_index] = old_amplitude + feedback

        # Also apply weak feedback to all other options
        for i in range(len(target_superposition.amplitudes)):
            if i != measured_index:
                weak_feedback = feedback * 0.1
                target_superposition.amplitudes[i] += weak_feedback

        # Renormalize
        self._renormalize_amplitudes(target_superposition)

        return {
            "option_index": measured_index,
            "old_amplitude": old_amplitude,
            "new_amplitude": target_superposition.amplitudes[measured_index],
            "effect": "feedback",
        }

    def _renormalize_amplitudes(self, superposition: SuperpositionState) -> None:
        """Renormalize amplitudes after modification."""
        norm = math.sqrt(sum(abs(a) ** 2 for a in superposition.amplitudes))
        if norm > 0:
            superposition.amplitudes = [a / norm for a in superposition.amplitudes]

            # Update probabilities in metadata
            superposition.metadata["probabilities"] = [
                abs(a) ** 2 for a in superposition.amplitudes
            ]

    def get_entanglement_network(self) -> dict[str, list[str]]:
        """Get the entanglement graph showing which states are connected."""
        return dict(self._entanglement_graph)

    def get_state(self, state_id: str) -> EntangledSuperpositionState | None:
        """Get an entangled state by ID."""
        return self._states.get(state_id)

    def get_entanglement_links(self, state_id: str) -> list[EntanglementLink]:
        """Get all entanglement links for a state."""
        if state_id not in self._states:
            return []
        return self._states[state_id].entanglement_links

    def get_measurement_history(self, state_id: str) -> list[dict[str, Any]]:
        """Get measurement history for a state."""
        if state_id not in self._states:
            return []
        return self._states[state_id].measurement_history

    def calculate_entanglement_entropy(self, state_a_id: str, state_b_id: str) -> float:
        """
        Calculate entanglement entropy between two states (simplified von Neumann entropy).

        Args:
            state_a_id: First state identifier
            state_b_id: Second state identifier

        Returns:
            Entanglement entropy value
        """
        if state_a_id not in self._states or state_b_id not in self._states:
            return 0.0

        # Find entanglement link
        state_a = self._states[state_a_id]
        link = next(
            (
                l
                for l in state_a.entanglement_links
                if (l.state_a_id == state_b_id or l.state_b_id == state_b_id)
            ),
            None,
        )

        if not link:
            return 0.0

        # Simple entropy based on link strength and type
        base_entropy = link.strength

        # Type-specific entropy modulation
        if link.entanglement_type == EntanglementType.CORRELATED:
            entropy_factor = 1.0
        elif link.entanglement_type == EntanglementType.ANTI_CORRELATED:
            entropy_factor = 0.8
        elif link.entanglement_type == EntanglementType.CONDITIONAL:
            entropy_factor = 1.2
        elif link.entanglement_type == EntanglementType.FEEDBACK:
            entropy_factor = 1.5
        else:
            entropy_factor = 1.0

        return base_entropy * entropy_factor
