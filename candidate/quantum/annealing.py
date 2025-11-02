"""Quantum-inspired annealing optimizer for QI-AGI."""

from __future__ import annotations

import logging
import math
import random
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Mapping

logger = logging.getLogger(__name__)


@dataclass
class AnnealingResult:
    """Result of a quantum-inspired annealing process."""

    solution: dict[str, Any]
    energy: float
    explored: int
    history: list[float]
    metadata: dict[str, Any]


class QuantumAnnealer:
    """Quantum-inspired annealing with simulated tunneling."""

    def __init__(self, *, rng: random.Random | None = None) -> None:
        self._rng = rng or random.Random()

    def anneal(
        self,
        objective: Callable[[Mapping[str, Any]], float] | None,
        *,
        search_space: Iterable[Mapping[str, Any]],
        constraints: Mapping[str, Any] | None = None,
    ) -> AnnealingResult:
        """Run simulated annealing enhanced with quantum tunneling."""

        constraints = constraints or {}
        candidates = [dict(option) for option in search_space]
        if not candidates:
            raise ValueError("Quantum annealing requires a non-empty search space")

        energy_function = self._resolve_energy_function(objective, constraints)
        temperature = float(constraints.get("initial_temperature", 1.0))
        cooling_rate = float(constraints.get("cooling_rate", 0.85))
        min_temperature = float(constraints.get("min_temperature", 0.01))
        max_iterations = int(constraints.get("max_iterations", 128))
        tunneling_rate = float(constraints.get("tunneling_rate", 0.12))

        current = constraints.get("initial_state") or candidates[0]
        current_energy = energy_function(current)
        best = dict(current)
        best_energy = current_energy

        energy_history: list[float] = [current_energy]
        explored = 0

        for _ in range(max_iterations):
            neighbour = self._select_neighbour(current, candidates)
            neighbour_energy = energy_function(neighbour)
            explored += 1

            delta = neighbour_energy - current_energy
            acceptance_probability = math.exp(-delta / max(temperature, 1e-9)) if delta > 0 else 1.0

            # ΛTAG: quantum_tunneling - allow occasional state jumps to escape minima
            if delta < 0 or self._rng.random() < acceptance_probability or self._rng.random() < tunneling_rate:
                current = neighbour
                current_energy = neighbour_energy
                energy_history.append(current_energy)

                if current_energy < best_energy:
                    best = dict(current)
                    best_energy = current_energy

            temperature = max(min_temperature, temperature * cooling_rate)

        metadata = {
            "final_temperature": temperature,
            "tunneling_rate": tunneling_rate,
            "cooling_rate": cooling_rate,
        }
        return AnnealingResult(
            solution=best, energy=best_energy, explored=explored, history=energy_history, metadata=metadata
        )

    def _resolve_energy_function(
        self,
        objective: Callable[[Mapping[str, Any]], float] | None,
        constraints: Mapping[str, Any],
    ) -> Callable[[Mapping[str, Any]], float]:
        if objective is not None:
            return lambda state: float(objective(state))

        candidate_function = constraints.get("energy_function")
        if callable(candidate_function):
            return lambda state: float(candidate_function(state))

        raise ValueError("No objective or energy function provided for annealing")

    def _select_neighbour(
        self,
        current: Mapping[str, Any],
        candidates: list[Mapping[str, Any]],
    ) -> dict[str, Any]:
        if len(candidates) == 1:
            return dict(candidates[0])
        choice = self._rng.choice(candidates)
        if choice == current:
            index = candidates.index(choice)
            offset = 1 if index + 1 < len(candidates) else -1
            choice = candidates[index + offset]
        return dict(choice)


# TODO: Support adaptive schedules informed by drift metrics.
