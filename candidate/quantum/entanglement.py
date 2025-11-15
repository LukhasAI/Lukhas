
"""Quantum-inspired entanglement modelling."""
from __future__ import annotations

import logging
import random
from dataclasses import dataclass, field
from typing import Any, Optional
from uuid import uuid4

from .measurement import QuantumMeasurement
from .superposition_engine import SuperpositionState

logger = logging.getLogger(__name__)


@dataclass
class EntangledSystem:
    """Represents a group of entangled superposition states."""

    states: list[SuperpositionState]
    correlation_matrix: list[list[float]]
    system_id: str = field(default_factory=lambda: str(uuid4()))


class EntanglementEngine:
    """Models entanglement between multiple superposition states."""

    def __init__(
        self,
        *,
        measurement_harness: Optional[QuantumMeasurement] = None,
        rng: random.Random | None = None,
    ) -> None:
        self.entangled_systems: dict[str, EntangledSystem] = {}
        self._measurement = measurement_harness or QuantumMeasurement()
        self._rng = rng or random.Random()

    def create_entanglement(
        self, states: list[SuperpositionState]
    ) -> EntangledSystem:
        """
        Create an entangled system from a list of superposition states.

        For simplicity, this currently creates a GHZ-like state where all
        outcomes are correlated.
        """
        if len(states) < 2:
            raise ValueError("Entanglement requires at least two states.")

        # Simplified correlation: all states are perfectly correlated or anti-correlated
        # 1 for correlation, -1 for anti-correlation
        correlation_matrix = self._generate_correlation_matrix(len(states))
        system = EntangledSystem(states=states, correlation_matrix=correlation_matrix)
        self.entangled_systems[system.system_id] = system
        return system

    def measure_system(
        self,
        system: EntangledSystem,
        measured_state_index: int,
        context: Optional[dict[str, Any]] = None,
    ) -> list[dict[str, Any]]:
        """
        Measure one state in an entangled system and collapse all others based on correlations.
        """
        if not (0 <= measured_state_index < len(system.states)):
            raise IndexError("Measured state index is out of bounds.")

        context = context or {}
        measured_state = system.states[measured_state_index]
        measurement_result = self._measurement.collapse(measured_state, context)

        outcomes = [None] * len(system.states)
        outcomes[measured_state_index] = measurement_result.collapsed_option

        # Collapse other states based on the measurement outcome and correlation matrix
        for i, state in enumerate(system.states):
            if i == measured_state_index:
                continue

            correlation = system.correlation_matrix[measured_state_index][i]
            correlated_index = self._get_correlated_index(
                measurement_result.selected_index,
                correlation,
                len(state.options)
            )
            outcomes[i] = state.options[correlated_index]

        return outcomes


    def _get_correlated_index(self, measured_index: int, correlation: float, num_options: int) -> int:
        """
        Determines the collapsed index of a correlated state.
        A positive correlation means the same index, negative means the opposite.
        This is a simplified model.
        """
        if correlation > 0:
            return measured_index % num_options
        else:
            # Simplified "opposite" for n-dimensional state
            return (num_options - 1 - measured_index) % num_options

    def _generate_correlation_matrix(self, size: int) -> list[list[float]]:
        """Generates a simple correlation matrix for a new entangled system."""
        matrix = [[0.0] * size for _ in range(size)]
        for i in range(size):
            for j in range(i, size):
                if i == j:
                    matrix[i][j] = 1.0
                else:
                    # For simplicity, we entangle everything with everything else
                    # with a mix of correlation and anti-correlation.
                    correlation = self._rng.choice([1.0, -1.0])
                    matrix[i][j] = correlation
                    matrix[j][i] = correlation
        return matrix

    def apply_decoherence(self, system: EntangledSystem, strength: float) -> None:
        """
        Applies decoherence to an entangled system, weakening the correlations.
        """
        if not (0.0 <= strength <= 1.0):
            raise ValueError("Decoherence strength must be between 0.0 and 1.0.")

        for i in range(len(system.states)):
            for j in range(i + 1, len(system.states)):
                system.correlation_matrix[i][j] *= (1.0 - strength)
                system.correlation_matrix[j][i] *= (1.0 - strength)
