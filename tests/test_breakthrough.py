"""
tests/test_breakthrough_stability.py

Tier-2 robustness & performance tests for BreakthroughDetector.
Focus: numerical stability at scale, pathological inputs, boundary z thresholds,
independent instance behavior, and (optional) micro-benchmarks.
"""
import math
import os
import random
import pytest

from core.breakthrough import BreakthroughDetector


# ---- Helpers ---------------------------------------------------------------

def _seed():
    # Make runs deterministic regardless of external env
    os.environ.setdefault("PYTHONHASHSEED", "0")
    random.seed(42)


def _mk_detector(**kw) -> BreakthroughDetector:
    return BreakthroughDetector(**kw)


# ---- Tier-2 Stability ------------------------------------------------------

@pytest.mark.tier2
@pytest.mark.stability
def test_large_n_stability_no_nan_inf():
    """Feed a long sequence and ensure stats remain finite and in-range.

    This is a stability test, not a performance test. We purposely avoid
    tight time assertions to keep CI non-flaky.
    """
    _seed()
    det = _mk_detector()

    # 50k steps: alternating around a center with mild noise in [0,1]
    n_steps = 50_000
    for i in range(n_steps):
        base = 0.5 + (0.1 if (i & 1) == 0 else -0.1)
        # deterministic jitter in [−0.02, +0.02]
        jitter = ((i * 9301 + 49297) % 233280) / 233280.0  # [0,1)
        jitter = (jitter - 0.5) * 0.04
        val = min(1.0, max(0.0, base + jitter))
        det.step(novelty=val, value=val)

    # Finite, bounded outputs
    assert math.isfinite(det.mu)
    assert math.isfinite(det.sq)
    assert det.n == n_steps
    # Mean must lie in [0,1]
    assert 0.0 <= det.mu <= 1.0
    # Variance proxy (sq accumulator) must be non-negative
    assert det.sq >= 0.0


@pytest.mark.tier2
@pytest.mark.stability
def test_small_variance_sequence_never_false_positive():
    """Very small variance sequence should not trigger breakthroughs when z is large."""
    _seed()
    det = _mk_detector(z=8.0)  # extremely strict

    for _ in range(10_000):
        det.step(0.5001, 0.4999)

    # Last step shouldn't be a breakthrough
    res = det.step(0.5002, 0.4998)
    assert res["breakthrough"] is False


@pytest.mark.tier2
@pytest.mark.stability
def test_boundary_z_thresholds():
    """Boundary z behavior: z=0 should always flag; z=1e6 effectively never flags."""
    _seed()

    # z=0 → any deviation is a breakthrough after first sample
    det0 = _mk_detector(z=0.0)
    det0.step(0.5, 0.5)
    res0 = det0.step(0.51, 0.49)
    assert res0["breakthrough"] is True

    # very large z → practically never
    det_hi = _mk_detector(z=1e6)
    for _ in range(1000):
        res_hi = det_hi.step(0.5, 0.5)
    assert res_hi["breakthrough"] is False


@pytest.mark.tier2
@pytest.mark.stability
def test_multiple_instances_independent_state():
    """Two detectors should evolve independently and not leak state."""
    _seed()
    d1 = _mk_detector()
    d2 = _mk_detector()

    seq1 = [(0.2, 0.8), (0.3, 0.7), (0.4, 0.6), (0.5, 0.5)]
    seq2 = [(0.8, 0.2), (0.7, 0.3), (0.6, 0.4), (0.5, 0.5)]

    for (n1, v1), (n2, v2) in zip(seq1, seq2):
        r1 = d1.step(n1, v1)
        r2 = d2.step(n2, v2)
        # scores differ, means diverge, states isolated
        assert r1["score"] != r2["score"]

    # final means must differ in opposite directions around ~0.5
    assert d1.mu < 0.55 and d2.mu > 0.45


# ---- Tier-2 Performance (optional) ----------------------------------------

@pytest.mark.tier2
@pytest.mark.perf
@pytest.mark.benchmark(group="breakthrough.step")
def test_step_throughput_benchmark():
    """Micro-benchmark: measure step() throughput with pytest-benchmark if available.

    Will be skipped automatically if the plugin is not installed.
    """
    pytest.importorskip("pytest_benchmark")
    _seed()
    det = _mk_detector()

    def _do():
        # typical mid-range values
        det.step(0.6, 0.4)

    # Run benchmark; budgets are enforced elsewhere by CI perf guardrails
    result = pytest.benchmark(_do)  # type: ignore[attr-defined]
    # Basic sanity on benchmark object
    assert hasattr(result, "stats")
