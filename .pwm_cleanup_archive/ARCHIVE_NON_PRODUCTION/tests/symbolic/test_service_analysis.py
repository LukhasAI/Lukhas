from symbolic.service_analysis import (
    compute_digital_friction,
    compute_modularity_score,
)


def test_compute_digital_friction_zero_calls():
    assert compute_digital_friction(0, 5.0, 10.0) == 0.0


def test_compute_digital_friction_basic():
    score = compute_digital_friction(50, 1.0, 2.0)
    assert 0.0 < score <= 1.0


def test_compute_modularity_score_perfect():
    score = compute_modularity_score(3, [[0, 0, 0], [0, 0, 0], [0, 0, 0]])
    assert score == 1.0


def test_compute_modularity_score_basic():
    matrix = [[0, 0.2, 0.2], [0.2, 0, 0.1], [0.2, 0.1, 0]]
    score = compute_modularity_score(3, matrix)
    assert 0.0 <= score <= 1.0
