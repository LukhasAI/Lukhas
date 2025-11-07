"""Unit tests for quantum-inspired superposition utilities."""
from __future__ import annotations

import math

import pytest

from candidate.quantum.superposition_engine import QuantumSuperpositionEngine


def test_quantum_superposition_engine_initialization():
    """Test that the QuantumSuperpositionEngine can be initialized."""
    engine = QuantumSuperpositionEngine()
    assert engine is not None


def test_create_state_with_simple_options():
    """Test the create_state method with simple options."""
    engine = QuantumSuperpositionEngine()
    options = [{"id": "a"}, {"id": "b"}]
    state = engine.create_state(options)
    assert state is not None
    assert len(state.options) == 2
    assert len(state.amplitudes) == 2
    assert math.isclose(sum(abs(amp) ** 2 for amp in state.amplitudes), 1.0)


def test_create_state_raises_error_with_no_options():
    """Test that create_state raises a ValueError if no options are provided."""
    engine = QuantumSuperpositionEngine()
    with pytest.raises(ValueError, match="Cannot create a superposition without options"):
        engine.create_state([])
