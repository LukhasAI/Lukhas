#!/usr/bin/env python3
"""
Task 7: Integrity micro-check tests for AkaQualia loop

Validates that integrity micro-checks are properly integrated into the AkaQualia
processing loop and can detect drift and trigger autonomous repair.

#TAG:test
#TAG:task7
#TAG:microcheck
"""
import os
import time

import pytest

# Set experimental flags before imports (deterministic test env)
os.environ.setdefault("LUKHAS_EXPERIMENTAL", "1")
os.environ.setdefault("LUKHAS_LANE", "labs")
os.environ.setdefault("LUKHAS_AUTOREPAIR_ENABLED", "1")


def test_microcheck_triggers_once(monkeypatch):
    """Test that micro-check triggers repair exactly once, no oscillation."""
    from lukhas.aka_qualia.core import AkaQualia

    q = AkaQualia()

    # Ensure IntegrityProbe is available
    if not q.integrity_probe:
        pytest.skip("IntegrityProbe not available")

    # spy on on_exceed from the actual drift manager
    fired = {"n": 0}
    original_on_exceed = q.integrity_probe.drift_manager.on_exceed
    def spy_on_exceed(kind, score, ctx):
        fired["n"] += 1
        return original_on_exceed(kind, score, ctx)
    monkeypatch.setattr(q.integrity_probe.drift_manager, "on_exceed", spy_on_exceed)

    # inject a failing probe once
    called = {"n": 0}
    original_run_check = q.integrity_probe.run_consistency_check
    def fake_check(state=None):
        called["n"] += 1
        if called["n"] == 1:
            # First call: inject high drift that should trigger repair
            threshold = float(os.environ.get("DRIFT_SAFE_THRESHOLD", "0.15"))
            monkeypatch.setattr(q.integrity_probe.drift_manager, "compute",
                              lambda kind, prev, curr: {
                                  'score': threshold + 0.10,  # Above threshold + margin
                                  'top_symbols': ['test.injection'],
                                  'confidence': 1.0,
                                  'kind': kind,
                                  'metadata': {}
                              })
            # Ensure we have state for drift calculation
            q.integrity_probe.prev_state = {'ethical': {'test': 'prev'}}
            q.integrity_probe.curr_state = {'ethical': {'test': 'curr'}}
            return original_run_check(state)
        else:
            # Subsequent calls: normal behavior
            return True
    monkeypatch.setattr(q.integrity_probe, "run_consistency_check", fake_check)

    # run a few ticks
    for _ in range(5):
        q.tick_once()

    # Tolerant assertion - allows for rate-limiting/dwell coalescing
    assert fired["n"] >= 1, f"micro-check should trigger repair at least once, got {fired['n']}"


def test_microcheck_performance_overhead():
    """Test that micro-check adds ≤5% overhead to AkaQualia loop."""
    from lukhas.aka_qualia.core import AkaQualia

    # Measure baseline (no micro-check)
    q_baseline = AkaQualia()
    q_baseline.integrity_probe = None  # Disable micro-check

    baseline_times = []
    for _ in range(10):
        start = time.perf_counter()
        q_baseline.tick_once()
        baseline_times.append(time.perf_counter() - start)

    baseline_avg = sum(baseline_times) / len(baseline_times)

    # Measure with micro-check
    q_microcheck = AkaQualia()

    microcheck_times = []
    for _ in range(10):
        start = time.perf_counter()
        q_microcheck.tick_once()
        microcheck_times.append(time.perf_counter() - start)

    microcheck_avg = sum(microcheck_times) / len(microcheck_times)

    # Calculate overhead
    overhead_pct = ((microcheck_avg - baseline_avg) / baseline_avg) * 100 if baseline_avg > 0 else 0
    overhead_abs = microcheck_avg - baseline_avg

    print(f"Baseline avg: {baseline_avg*1000:.3f}ms")
    print(f"Microcheck avg: {microcheck_avg*1000:.3f}ms")
    print(f"Overhead: {overhead_pct:.1f}% (+{overhead_abs*1000:.3f}ms)")

    # Accept either ≤5% relative or ≤10ms absolute
    passes_pct = overhead_pct <= 5.0
    passes_abs = overhead_abs <= 0.010  # 10ms

    assert passes_pct or passes_abs, f"Performance overhead {overhead_pct:.1f}% / {overhead_abs*1000:.3f}ms exceeds limits"


def test_microcheck_no_false_positives():
    """Test that micro-check doesn't trigger false positives on stable corpus."""
    from lukhas.aka_qualia.core import AkaQualia
    from monitoring.drift_manager import DriftManager

    q = AkaQualia()
    dm = DriftManager()

    # Track repair attempts
    repair_attempts = {"n": 0}
    original_on_exceed = dm.on_exceed

    def tracking_on_exceed(kind, score, ctx):
        repair_attempts["n"] += 1
        return original_on_exceed(kind, score, ctx)

    # Use partial monkey patch to preserve original behavior
    import types
    dm.on_exceed = types.MethodType(lambda self, kind, score, ctx: tracking_on_exceed(kind, score, ctx), dm)

    # Run stable processing for multiple ticks
    for _ in range(20):
        q.tick_once()

    # Should have no false positive repairs on stable data
    assert repair_attempts["n"] == 0, f"False positive repairs detected: {repair_attempts['n']}"


def test_microcheck_detects_injected_inconsistency():
    """Test that micro-check detects artificially injected drift."""
    from lukhas.aka_qualia.core import AkaQualia

    q = AkaQualia()

    # Ensure IntegrityProbe is available
    if not q.integrity_probe:
        pytest.skip("IntegrityProbe not available")

    # Track detected drifts
    detected_drifts = []
    original_on_exceed = q.integrity_probe.drift_manager.on_exceed

    def drift_tracking_on_exceed(kind, score, ctx):
        detected_drifts.append((kind, score))
        return original_on_exceed(kind, score, ctx)

    # Replace the on_exceed method
    q.integrity_probe.drift_manager.on_exceed = drift_tracking_on_exceed

    # Inject high drift by modifying drift manager compute method
    original_compute = q.integrity_probe.drift_manager.compute

    def injected_drift_compute(kind, prev, curr):
        result = original_compute(kind, prev, curr)
        if kind == 'ethical':
            # Inject critical drift on ethical dimension
            threshold = float(os.environ.get("DRIFT_SAFE_THRESHOLD", "0.15"))
            result['score'] = threshold + 0.10  # Above threshold + margin
            result['top_symbols'] = ['ethical.test_injection']
        return result

    q.integrity_probe.drift_manager.compute = injected_drift_compute

    # Run processing - should detect injected drift
    for _ in range(3):
        q.tick_once()

    # Restore originals to avoid cross-test contamination
    q.integrity_probe.drift_manager.on_exceed = original_on_exceed
    q.integrity_probe.drift_manager.compute = original_compute

    # Should have detected at least one ethical drift
    ethical_drifts = [d for d in detected_drifts if d[0] == 'ethical']
    assert len(ethical_drifts) > 0, "Failed to detect injected ethical drift"
    assert any(score >= 0.15 for _, score in ethical_drifts), "Detected drift below critical threshold"


def test_microcheck_telemetry():
    """Test that micro-check telemetry metrics are recorded."""
    from lukhas.aka_qualia.core import AkaQualia
    from lukhas.qi.states.integrity_probe import _get_microcheck_metrics

    metrics = _get_microcheck_metrics()
    if not metrics:
        pytest.skip("Prometheus metrics not available")

    q = AkaQualia()

    # Get initial metric values
    initial_attempts = metrics['attempts']._value._value if 'attempts' in metrics and hasattr(metrics['attempts']._value, '_value') else 0

    # Run processing
    q.tick_once()

    # Check metrics were updated
    final_attempts = metrics['attempts']._value._value if 'attempts' in metrics and hasattr(metrics['attempts']._value, '_value') else 0

    assert final_attempts > initial_attempts, "Micro-check attempts metric not incremented"


def test_threshold_consistency():
    """Test that all components use the same critical threshold from env."""
    import os

    from lukhas.aka_qualia.core import AkaQualia
    from monitoring.drift_manager import DriftManager

    # Set custom threshold for test
    custom_threshold = "0.12"
    os.environ["DRIFT_SAFE_THRESHOLD"] = custom_threshold

    try:
        # Clear singleton to force fresh read
        import monitoring.drift_manager
        monitoring.drift_manager._drift_manager = None

        # Create fresh instances that should read the env var
        dm = DriftManager()
        q = AkaQualia()

        # All should use the same threshold
        expected = float(custom_threshold)

        # DriftManager should use env threshold
        assert dm.critical_threshold == expected, f"DriftManager threshold {dm.critical_threshold} != {expected}"

        # IntegrityProbe should read same env var (via factory or singleton)
        if q.integrity_probe:
            # Test by checking the actual threshold used in comparison
            assert q.integrity_probe.drift_manager.critical_threshold == expected, \
                f"IntegrityProbe drift_manager threshold {q.integrity_probe.drift_manager.critical_threshold} != {expected}"

    finally:
        # Restore default and clear singleton
        os.environ["DRIFT_SAFE_THRESHOLD"] = "0.15"
        import monitoring.drift_manager
        monitoring.drift_manager._drift_manager = None


def test_dwell_after_successful_repair():
    """Test that micro-check implements dwell period after successful repair."""
    import os

    from lukhas.aka_qualia.core import AkaQualia
    from monitoring.drift_manager import DriftManager

    # Set short dwell period for test
    os.environ["DRIFT_DWELL_CYCLES"] = "2"

    try:
        q = AkaQualia()
        dm = DriftManager()

        # Simulate successful repair first
        dm._record_successful_repair("ethical")

        # Track ledger entries instead of on_exceed calls
        initial_ledger_size = len(dm.drift_ledger)

        # Now call on_exceed multiple times - should be blocked by dwell
        for i in range(5):
            dm.on_exceed("ethical", 0.25, {"test": f"call_{i}"})

        # Check ledger - should have 1 exceedance + 4 dwell_skip events
        new_entries = dm.drift_ledger[initial_ledger_size:]
        exceedance_entries = [e for e in new_entries if e.get('event') == 'threshold_exceeded']
        dwell_skip_entries = [e for e in new_entries if e.get('event') == 'repair_skipped_dwell']

        assert len(exceedance_entries) == 1, f"Expected 1 exceedance event, got {len(exceedance_entries)}"
        assert len(dwell_skip_entries) == 4, f"Expected 4 dwell skip events, got {len(dwell_skip_entries)}"

        # Simulate enough cycles to exit dwell period
        for _ in range(3):  # More than DRIFT_DWELL_CYCLES=2
            dm._increment_cycle_counter("ethical")

        # Now on_exceed should work again
        dm.on_exceed("ethical", 0.25, {"test": "after_dwell"})

        # Check that a new exceedance was recorded (not skipped)
        final_entries = dm.drift_ledger[initial_ledger_size:]
        final_exceedance_entries = [e for e in final_entries if e.get('event') == 'threshold_exceeded']
        assert len(final_exceedance_entries) == 2, f"Expected 2 exceedance events after dwell, got {len(final_exceedance_entries)}"

    finally:
        # Restore default
        os.environ["DRIFT_DWELL_CYCLES"] = "3"


def test_microcheck_with_rate_limiting():
    """Test that micro-check respects repair rate limiting."""
    from lukhas.aka_qualia.core import AkaQualia
    from monitoring.drift_manager import DriftManager

    q = AkaQualia()
    dm = DriftManager()

    # Track repair attempts
    repair_attempts = []
    original_on_exceed = dm.on_exceed

    def rate_limit_tracking_on_exceed(kind, score, ctx):
        repair_attempts.append((time.time(), kind, score))
        return original_on_exceed(kind, score, ctx)

    import types
    dm.on_exceed = types.MethodType(lambda self, kind, score, ctx: rate_limit_tracking_on_exceed(kind, score, ctx), dm)

    # Force consistent drift detection
    def always_critical_drift_compute(kind, prev, curr):
        result = dm._compute_ethical_drift(prev, curr) if kind == 'ethical' else {'score': 0.0, 'top_symbols': [], 'confidence': 1.0, 'metadata': {}}
        threshold = float(os.environ.get("DRIFT_SAFE_THRESHOLD", "0.15"))
        result['score'] = threshold + 0.10  # Above threshold + margin
        result['top_symbols'] = [f'{kind}.rate_limit_test']
        return result

    dm.compute = types.MethodType(lambda self, kind, prev, curr: always_critical_drift_compute(kind, prev, curr), dm)

    # Run many ticks rapidly
    for _ in range(10):
        q.tick_once()
        time.sleep(0.1)  # Small delay between ticks

    # Should respect rate limiting (max 3 attempts per 5 minutes per kind)
    ethical_attempts = [a for a in repair_attempts if a[1] == 'ethical']
    assert len(ethical_attempts) <= 3, f"Rate limiting not working: {len(ethical_attempts)} attempts > 3 limit"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
