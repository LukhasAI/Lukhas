import math

import pytest
from qi.qi_entanglement import (
    QuantumState,
    compute_entanglement,
    generate_entanglement_report,
    validate_states,
)


def test_compute_entanglement_returns_metrics():
    state_a = QuantumState("alpha", (1.0, 0.0), phase=0.1, coherence=0.9, affect_bias=0.3)
    state_b = QuantumState("beta", (1 / math.sqrt(2), 1 / math.sqrt(2)), phase=0.2, coherence=0.95, affect_bias=-0.1)

    result = compute_entanglement(state_a, state_b)

    assert 0.0 <= result.entanglement_score <= 1.0
    assert 0.0 <= result.driftScore <= 1.0
    assert isinstance(result.collapseHash, str) and result.collapseHash
    assert result.diagnostics["vector_delta"] >= 0

    report = generate_entanglement_report(result)
    assert report["state_a"] == "alpha"
    assert "entanglement_score" in report
    assert "collapseHash" in report


def test_validate_states_dimension_mismatch():
    state_a = QuantumState("alpha", (1.0, 0.0))
    state_b = QuantumState("beta", (0.5, 0.5, 0.5))

    with pytest.raises(ValueError):
        validate_states(state_a, state_b)
