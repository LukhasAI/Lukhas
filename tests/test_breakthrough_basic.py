"""
tests/test_breakthrough_basic.py

Basic unit tests for BreakthroughDetector - novelty x value scoring with z-score detection.
Covers core functionality and edge cases.
"""
import pytest

from core.breakthrough import BreakthroughDetector


def test_detector_initialization():
    """Test that BreakthroughDetector initializes correctly"""
    detector = BreakthroughDetector()

    assert detector.mu == 0.0
    assert detector.sq == 0.0
    assert detector.n == 0
    assert detector.z == 3.0
    assert detector.w == (0.5, 0.5)  # Default weights


def test_custom_initialization():
    """Test detector with custom parameters"""
    detector = BreakthroughDetector(novelty_w=0.7, value_w=0.3, z=2.5)

    assert detector.w == (0.7, 0.3)
    assert detector.z == 2.5


def test_single_step():
    """Test first step behavior"""
    detector = BreakthroughDetector()
    result = detector.step(novelty=0.6, value=0.8)

    expected_score = 0.5 * 0.6 + 0.5 * 0.8  # 0.7
    assert result["score"] == expected_score
    assert result["mean"] == expected_score
    assert result["std"] == 0.0  # No std with single sample
    assert result["breakthrough"] is False
    assert result["n"] == 1


def test_multiple_steps_no_breakthrough():
    """Test multiple steps with normal variance"""
    detector = BreakthroughDetector()

    # Add several normal scores
    scores = [(0.5, 0.5), (0.6, 0.4), (0.4, 0.6), (0.5, 0.5)]
    for i, (novelty, value) in enumerate(scores):
        result = detector.step(novelty, value)
        assert result["breakthrough"] is False
        assert result["n"] == i + 1


def test_weighted_scoring():
    """Test that novelty and value weights are applied correctly"""
    detector = BreakthroughDetector(novelty_w=0.8, value_w=0.2)

    result = detector.step(novelty=1.0, value=0.0)
    assert result["score"] == 0.8  # 0.8 * 1.0 + 0.2 * 0.0

    result = detector.step(novelty=0.0, value=1.0)
    assert result["score"] == 0.2  # 0.8 * 0.0 + 0.2 * 1.0


def test_edge_case_zero_values():
    """Test behavior with zero novelty/value"""
    detector = BreakthroughDetector()

    result = detector.step(novelty=0.0, value=0.0)
    assert result["score"] == 0.0
    assert result["breakthrough"] is False


def test_edge_case_maximum_values():
    """Test behavior with maximum novelty/value"""
    detector = BreakthroughDetector()

    result = detector.step(novelty=1.0, value=1.0)
    assert result["score"] == 1.0
    assert result["breakthrough"] is False  # No baseline for comparison


def test_reset_functionality():
    """Test detector reset clears state"""
    detector = BreakthroughDetector()

    # Add some data
    for _i in range(5):
        detector.step(novelty=0.5, value=0.5)

    assert detector.n == 5
    assert detector.mu != 0.0

    # Reset
    detector.reset()

    assert detector.n == 0
    assert detector.mu == 0.0
    assert detector.sq == 0.0


def test_result_structure():
    """Test that step returns proper result structure"""
    detector = BreakthroughDetector()
    result = detector.step(novelty=0.6, value=0.4)

    assert isinstance(result, dict)
    required_keys = ["score", "mean", "std", "breakthrough", "n", "lane"]
    for key in required_keys:
        assert key in result

    assert isinstance(result["score"], float)
    assert isinstance(result["mean"], float)
    assert isinstance(result["std"], float)
    assert isinstance(result["breakthrough"], bool)
    assert isinstance(result["n"], int)
    assert isinstance(result["lane"], str)


def test_input_validation():
    """Test input validation"""
    detector = BreakthroughDetector()

    # Test None values
    with pytest.raises(ValueError):
        detector.step(None, 0.5)

    # Test non-numeric values
    with pytest.raises(TypeError):
        detector.step("invalid", 0.5)


def test_deterministic_behavior():
    """Test that detector produces deterministic results"""
    detector1 = BreakthroughDetector()
    detector2 = BreakthroughDetector()

    test_pairs = [(0.3, 0.7), (0.6, 0.4), (0.8, 0.9), (0.2, 0.3)]

    results1 = []
    results2 = []

    for novelty, value in test_pairs:
        results1.append(detector1.step(novelty, value))
        results2.append(detector2.step(novelty, value))

    # Should produce identical results
    for r1, r2 in zip(results1, results2):
        assert abs(r1["score"] - r2["score"]) < 1e-10
        assert abs(r1["mean"] - r2["mean"]) < 1e-10
        assert abs(r1["std"] - r2["std"]) < 1e-10
        assert r1["breakthrough"] == r2["breakthrough"]
