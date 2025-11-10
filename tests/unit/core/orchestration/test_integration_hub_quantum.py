"""Tests for the quantum-inspired features of :mod:`core.orchestration.integration_hub`."""
from __future__ import annotations

import asyncio
import math

import pytest
from core.orchestration.integration_hub import QIAGISystem
from typing import Dict


def test_create_superposition_generates_normalized_state() -> None:
    system = QIAGISystem(config={"seed": 7})
    options = [
        {"id": "alpha", "weight": 0.6},
        {"id": "beta", "weight": 0.3},
        {"id": "gamma", "weight": 0.1},
    ]
    context = {
        "bias": {"alpha": 0.2},
        "interference": [{"source": "alpha", "target": "beta", "strength": 0.4}],
        "phase_noise": 0.0,
    }

    result = asyncio.run(system.create_superposition(options, context))

    assert result["superposition_id"].startswith("sp_")
    assert len(result["probabilities"]) == len(options)
    assert pytest.approx(sum(result["probabilities"]), rel=1e-6) == 1.0
    assert result["stub"] is False
    assert result["coherence"] <= 1.0
    assert result["interference_events"], "interference events should be recorded"


def test_measure_collapse_respects_preference_bias() -> None:
    system = QIAGISystem(config={"seed": 21})
    options = [
        {"id": "keep", "weight": 0.2},
        {"id": "explore", "weight": 0.8},
    ]
    context = {"phase_noise": 0.0}
    state = asyncio.run(system.create_superposition(options, context))

    measurement = asyncio.run(
        system.measure_collapse(
            state["superposition_id"],
            {
                "mode": "argmax",
                "preferred_option": "explore",
                "preferred_weight": 4.0,
                "decoherence": 0.25,
            },
        )
    )

    assert measurement["collapsed"] is True
    assert measurement["decision"]["id"] == "explore"
    assert measurement["probability"] == max(measurement["measurement_metadata"]["probabilities"])
    assert measurement["coherence"] < 1.0
    assert measurement["stub"] is False


def test_quantum_anneal_finds_low_energy_state() -> None:
    system = QIAGISystem(config={"seed": 5})
    search_space = [
        {"id": "local", "energy": 5.0},
        {"id": "ridge", "energy": 3.5},
        {"id": "global", "energy": 1.0},
    ]

    def energy_function(state: Dict[str, float]) -> float:
        return float(state["energy"])

    result = asyncio.run(
        system.quantum_anneal(
            "minimize_energy",
            {
                "search_space": search_space,
                "energy_function": energy_function,
                "initial_state": search_space[0],
                "max_iterations": 64,
                "tunneling_rate": 0.2,
                "cooling_rate": 0.9,
                "initial_temperature": 2.0,
            },
        )
    )

    assert result["optimized"] is True
    assert result["solution"]["id"] == "global"
    assert math.isclose(result["energy"], 1.0, rel_tol=1e-6)
    assert result["stub"] is False
    assert result["metadata"]["final_temperature"] >= 0.01
    assert result["history"], "annealing should record energy history"
