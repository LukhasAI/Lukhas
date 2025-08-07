import json
from diagnostics.drift_diagnostics import (
    calculate_drift_score,
    detect_collapse_points,
    generate_entropy_map_from_memory,
    get_diagnostics_summary,
)
from pytest import approx


def test_calculate_drift_score():
    assert calculate_drift_score([0.0, 1.0, 2.0]) == approx(1.0)
    assert calculate_drift_score([1.0]) == 0.0


def test_generate_entropy_map_from_memory():
    result = generate_entropy_map_from_memory({"a": 1, "b": 1})
    assert result["a"] == approx(0.5)
    assert result["b"] == approx(0.5)


def test_detect_collapse_points():
    cp = detect_collapse_points({"a": 0.05, "b": 0.3}, threshold=0.1)
    assert cp == ["a"]


def test_get_diagnostics_summary_keys():
    summary_json = get_diagnostics_summary([0, 1], {"a": 1, "b": 3})
    summary = json.loads(summary_json)
    assert set(summary) == {"driftScore", "entropyMap", "collapsePoints"}
