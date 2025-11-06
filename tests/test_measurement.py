"""Unit tests for quantum-inspired measurement collapse utilities."""
from __future__ import annotations

import pytest

from candidate.quantum.measurement import QuantumMeasurement
from candidate.quantum.superposition_engine import SuperpositionState


def test_quantum_measurement_initialization():
    """Test that the QuantumMeasurement can be initialized."""
    measurement = QuantumMeasurement()
    assert measurement is not None


def test_collapse_with_simple_state():
    """Test the collapse method with a simple superposition state."""
    measurement = QuantumMeasurement()
    options = [{"id": "a"}, {"id": "b"}]
    amplitudes = [complex(1.0, 0.0), complex(0.0, 0.0)]
    state = SuperpositionState(
        options=options,
        amplitudes=amplitudes,
        metadata={"probabilities": [1.0, 0.0]}
    )
    result = measurement.collapse(state, context={"mode": "argmax"})
    assert result.collapsed_option == {"id": "a"}


def test_collapse_raises_error_with_no_options():
    """Test that collapse raises a ValueError if the state has no options."""
    measurement = QuantumMeasurement()
    state = SuperpositionState(options=[], amplitudes=[], metadata={})
    with pytest.raises(ValueError, match="Superposition has no options to measure"):
        measurement.collapse(state)
