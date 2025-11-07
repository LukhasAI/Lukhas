"""Unit tests for quantum-inspired annealing optimizer."""
from __future__ import annotations

import pytest

from candidate.quantum.annealing import QuantumAnnealer


def test_quantum_annealer_initialization():
    """Test that the QuantumAnnealer can be initialized."""
    annealer = QuantumAnnealer()
    assert annealer is not None


def test_anneal_with_simple_objective():
    """Test the anneal method with a simple objective function."""
    annealer = QuantumAnnealer()
    search_space = [{"x": 1}, {"x": 2}, {"x": 3}]
    objective = lambda state: state["x"]
    result = annealer.anneal(objective, search_space=search_space)
    assert result.solution == {"x": 1}
    assert result.energy == 1


def test_anneal_raises_error_without_objective():
    """Test that anneal raises a ValueError if no objective is provided."""
    annealer = QuantumAnnealer()
    search_space = [{"x": 1}, {"x": 2}, {"x": 3}]
    with pytest.raises(ValueError, match="No objective or energy function provided"):
        annealer.anneal(None, search_space=search_space)
