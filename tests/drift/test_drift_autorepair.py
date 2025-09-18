"""
Tests for Autonomous Drift Correction (Closed Loop)

Verifies that the drift management system can autonomously detect
and repair drift exceedances with the TraceRepairEngine integration.

Acceptance criteria:
- Injected drift reduces by ≥ 20-40% within 2-3 cycles
- No added p95 > 5% on hot paths
- Ledger includes repair rationale

#TAG:test
#TAG:drift
#TAG:autorepair
#TAG:autonomous
"""
import os
import time
import pytest
from unittest.mock import Mock, patch

# Set feature flags for auto-repair testing
os.environ['LUKHAS_EXPERIMENTAL'] = '1'
os.environ['LUKHAS_LANE'] = 'candidate'
os.environ['ENABLE_LLM_GUARDRAIL'] = '1'

from monitoring.drift_manager import DriftManager
from lukhas.trace.TraceRepairEngine import TraceRepairEngine, RepairResult, RepairMethod


class TestAutonomousDriftCorrection:
    """Test suite for autonomous drift correction functionality."""

    def test_repair_engine_initialization(self):
        """Test that TraceRepairEngine initializes correctly."""
        manager = DriftManager()

        # Trigger repair engine initialization
        manager._initialize_repair_engine()

        assert hasattr(manager, '_repair_engine')
        assert manager._repair_engine is not None
        assert isinstance(manager._repair_engine, TraceRepairEngine)

    def test_should_attempt_repair_logic(self):
        """Test repair attempt decision logic."""
        manager = DriftManager()

        # Should not attempt repair for low drift
        assert not manager._should_attempt_repair('ethical', 0.10)

        # Should attempt repair for high drift
        assert manager._should_attempt_repair('ethical', 0.20)

        # Should not attempt if feature flag disabled
        with patch.dict(os.environ, {'LUKHAS_EXPERIMENTAL': '0'}):
            assert not manager._should_attempt_repair('ethical', 0.20)

    def test_threshold_exceedance_triggers_repair(self):
        """Test that drift threshold exceedance triggers autonomous repair."""
        manager = DriftManager()
        manager._initialize_repair_engine()

        initial_ledger_size = len(manager.drift_ledger)

        # Create high drift scenario
        high_drift_ctx = {
            'top_symbols': ['ethical.compliance', 'ethical.drift_score'],
            'probe': 'test'
        }

        # Trigger threshold exceedance (0.25 > 0.15 critical threshold)
        manager.on_exceed('ethical', 0.25, high_drift_ctx)

        # Verify repair was attempted
        assert len(manager.drift_ledger) > initial_ledger_size

        # Check for repair events in ledger
        repair_events = [
            entry for entry in manager.drift_ledger
            if entry.get('event', '').startswith('auto_repair')
        ]
        assert len(repair_events) > 0

        # Verify policy ledger line was emitted
        policy_events = [
            entry for entry in manager.drift_ledger
            if 'rationale' in entry
        ]
        assert len(policy_events) > 0

    def test_successful_repair_reduces_drift(self):
        """Test that successful repair actually reduces drift scores."""
        repair_engine = TraceRepairEngine()

        # Test ethical drift repair
        ethical_result = repair_engine.reconsolidate(
            kind='ethical',
            score=0.30,  # High drift
            context={'test': 'context'},
            top_symbols=['ethical.compliance', 'ethical.constitutional']
        )

        assert ethical_result.success
        assert ethical_result.post_score < ethical_result.pre_score
        assert ethical_result.improvement_pct >= 20.0  # At least 20% improvement

        # Test memory drift repair
        memory_result = repair_engine.reconsolidate(
            kind='memory',
            score=0.25,
            context={'test': 'context'},
            top_symbols=['memory.fold_stability', 'memory.entropy']
        )

        assert memory_result.success
        assert memory_result.post_score < memory_result.pre_score
        assert memory_result.improvement_pct >= 20.0

    def test_repair_method_selection(self):
        """Test that appropriate repair methods are selected based on drift type."""
        repair_engine = TraceRepairEngine()

        # Memory drift should prefer reconsolidation
        memory_result = repair_engine.reconsolidate(
            'memory', 0.20, {},
            ['memory.fold_stability', 'memory.fold_count']
        )
        assert memory_result.method == RepairMethod.RECONSOLIDATE

        # Ethical drift should prefer realignment
        ethical_result = repair_engine.reconsolidate(
            'ethical', 0.20, {},
            ['ethical.compliance', 'ethical.constitutional']
        )
        assert ethical_result.method == RepairMethod.REALIGN

        # Identity drift should prefer stabilization
        identity_result = repair_engine.reconsolidate(
            'identity', 0.20, {},
            ['identity.coherence', 'identity.namespace_integrity']
        )
        assert identity_result.method == RepairMethod.STABILIZE

    def test_repair_effectiveness_by_severity(self):
        """Test that repair effectiveness varies by drift severity."""
        repair_engine = TraceRepairEngine()

        # Minor drift should have better repair effectiveness
        minor_result = repair_engine.reconsolidate(
            'ethical', 0.18, {},  # Just above critical (0.15)
            ['ethical.compliance']
        )

        # Severe drift should have lower repair effectiveness
        severe_result = repair_engine.reconsolidate(
            'ethical', 0.35, {},  # Well above severe (0.25)
            ['ethical.compliance']
        )

        # Minor drift should have better improvement percentage
        assert minor_result.improvement_pct > severe_result.improvement_pct

    def test_repair_rate_limiting(self):
        """Test that excessive repair attempts are rate-limited."""
        manager = DriftManager()
        manager._initialize_repair_engine()

        # Simulate rapid fire repair attempts
        for i in range(5):
            # Check if repair should be attempted
            should_attempt = manager._should_attempt_repair('ethical', 0.20)
            print(f"Attempt {i}: Should attempt = {should_attempt}")

            manager.on_exceed('ethical', 0.20, {'attempt': i})

        # Count actual repair attempts in ledger (successful + failed, not errors)
        repair_attempts = [
            entry for entry in manager.drift_ledger
            if entry.get('event') in ['auto_repair_success', 'auto_repair_failure', 'auto_repair_error']
            and entry.get('kind') == 'ethical'
        ]

        # Should be rate-limited to 3 attempts per 5 minutes
        print(f"Repair attempts: {len(repair_attempts)}")
        assert len(repair_attempts) <= 3

    def test_drift_reduction_cycle(self):
        """Test complete drift detection -> repair -> verification cycle."""
        manager = DriftManager()
        manager._initialize_repair_engine()

        # Simulate drift cycle
        # 1. Initial state
        prev_state = {'compliance': 0.95, 'drift_score': 0.05}

        # 2. High drift detected
        curr_state = {'compliance': 0.50, 'drift_score': 0.40}

        # 3. Compute drift (should exceed threshold)
        drift_result = manager.compute('ethical', prev_state, curr_state)
        assert drift_result['score'] > manager.critical_threshold

        # 4. Trigger auto-repair
        initial_score = drift_result['score']
        manager.on_exceed('ethical', initial_score, {
            'top_symbols': drift_result['top_symbols'],
            'state': curr_state
        })

        # 5. Verify repair was attempted and succeeded
        successful_repairs = [
            entry for entry in manager.drift_ledger
            if entry.get('event') == 'auto_repair_success'
        ]
        assert len(successful_repairs) > 0

        # 6. Verify improvement
        last_repair = successful_repairs[-1]
        improvement_pct = last_repair['improvement_pct']
        assert improvement_pct >= 20.0  # Minimum 20% improvement

        # 7. Simulate post-repair state (reduced drift)
        post_repair_score = last_repair['post_score']
        assert post_repair_score < initial_score

    def test_hybrid_repair_for_unified_drift(self):
        """Test hybrid repair approach for complex unified drift."""
        repair_engine = TraceRepairEngine()

        # Unified drift with mixed contributing symbols
        unified_result = repair_engine.reconsolidate(
            'unified', 0.30, {},
            ['ethical.compliance', 'memory.fold_stability', 'identity.coherence']
        )

        assert unified_result.success
        assert unified_result.method == RepairMethod.HYBRID
        assert 'repair_components' in unified_result.details

        # Should have addressed all three dimensions
        components = unified_result.details['repair_components']
        assert components.get('memory', 0) > 0
        assert components.get('ethical', 0) > 0
        assert components.get('identity', 0) > 0

    def test_repair_history_tracking(self):
        """Test that repair history is properly tracked."""
        repair_engine = TraceRepairEngine()

        # Perform multiple repairs
        for i in range(3):
            repair_engine.reconsolidate(
                'ethical', 0.20 + i * 0.05, {},
                [f'ethical.test_symbol_{i}']
            )

        # Check history
        assert len(repair_engine.repair_history) == 3

        # Check success rate calculation
        success_rate = repair_engine.get_repair_success_rate(24)
        assert success_rate == 100.0  # All should be successful

        # Check average improvement
        avg_improvement = repair_engine.get_average_improvement()
        assert avg_improvement > 0.0

    def test_emergency_rollback_for_severe_drift(self):
        """Test emergency rollback for extremely severe drift."""
        repair_engine = TraceRepairEngine()

        # Extremely severe drift (above 0.4) should trigger rollback
        severe_result = repair_engine.reconsolidate(
            'memory', 0.45, {},  # Very high drift
            ['memory.fold_collapse', 'memory.critical_failure']
        )

        assert severe_result.success
        assert severe_result.method == RepairMethod.ROLLBACK
        assert severe_result.post_score < 0.15  # Should bring back to safe levels

    def test_namespace_change_repair_effectiveness(self):
        """Test special handling for namespace changes in identity drift."""
        repair_engine = TraceRepairEngine()

        # Identity drift with namespace issues
        result = repair_engine.reconsolidate(
            'identity', 0.20, {},
            ['identity.namespace_change', 'identity.coherence']
        )

        assert result.success
        assert result.method == RepairMethod.STABILIZE

        # Namespace repairs should be very effective
        assert result.improvement_pct > 70.0  # Should be > 70% improvement
        assert 'namespace_repairs' in result.details

    def test_repair_ledger_rationale(self):
        """Test that repair rationale is included in ledger entries."""
        manager = DriftManager()
        manager._initialize_repair_engine()

        # Trigger repair
        manager.on_exceed('ethical', 0.25, {
            'top_symbols': ['ethical.compliance'],
            'test': 'rationale'
        })

        # Check that ledger entries contain rationale
        repair_events = [
            entry for entry in manager.drift_ledger
            if entry.get('event') == 'auto_repair_success'
        ]

        assert len(repair_events) > 0
        for event in repair_events:
            assert 'rationale' in event
            assert len(event['rationale']) > 0

    def test_repair_without_engine_available(self):
        """Test behavior when TraceRepairEngine is not available."""
        manager = DriftManager()

        # Mock failed import
        with patch.object(manager, '_initialize_repair_engine') as mock_init:
            mock_init.side_effect = ImportError("Engine not available")

            # Should not crash, just log and continue
            manager.on_exceed('ethical', 0.25, {'test': 'no_engine'})

        # Should still record exceedance but no repair
        exceedance_events = [
            entry for entry in manager.drift_ledger
            if entry.get('event') == 'threshold_exceeded'
        ]
        assert len(exceedance_events) > 0

    def test_symbol_extraction_from_context(self):
        """Test symbol extraction when top_symbols not provided directly."""
        manager = DriftManager()

        # Test context with state
        symbols = manager._extract_symbols_from_context('ethical', {
            'state': {'compliance': 0.8, 'constitutional': 0.7}
        })

        assert 'ethical.compliance' in symbols
        assert 'ethical.constitutional' in symbols

        # Test fallback symbols
        symbols = manager._extract_symbols_from_context('memory', {})
        assert 'memory.fold_stability' in symbols
        assert 'memory.entropy' in symbols


class TestAutorepairAcceptanceGates:
    """Acceptance gate tests for autonomous drift correction."""

    def test_drift_reduction_percentage(self):
        """Test that repairs achieve ≥ 20-40% drift reduction."""
        repair_engine = TraceRepairEngine()

        # Test various drift scenarios
        test_cases = [
            ('ethical', 0.20, ['ethical.compliance']),
            ('memory', 0.25, ['memory.fold_stability']),
            ('identity', 0.18, ['identity.coherence']),
        ]

        for kind, score, symbols in test_cases:
            result = repair_engine.reconsolidate(kind, score, {}, symbols)

            assert result.success, f"Repair failed for {kind}"
            assert result.improvement_pct >= 20.0, \
                f"Improvement {result.improvement_pct:.1f}% < 20% for {kind}"

            # Most should achieve > 30% improvement
            print(f"{kind}: {result.improvement_pct:.1f}% improvement")

    def test_repair_within_cycle_limit(self):
        """Test that effective repair happens within 2-3 cycles."""
        manager = DriftManager()
        manager._initialize_repair_engine()

        # Simulate multi-cycle drift reduction
        initial_score = 0.30
        current_score = initial_score
        cycles = 0
        max_cycles = 3

        while current_score > manager.critical_threshold and cycles < max_cycles:
            cycles += 1

            # Trigger repair
            manager.on_exceed('ethical', current_score, {
                'top_symbols': ['ethical.compliance'],
                'cycle': cycles
            })

            # Get latest repair result
            repair_events = [
                entry for entry in manager.drift_ledger
                if entry.get('event') == 'auto_repair_success'
            ]

            if repair_events:
                latest_repair = repair_events[-1]
                current_score = latest_repair['post_score']
                print(f"Cycle {cycles}: {current_score:.4f}")

        # Should reach safe levels within max_cycles
        assert current_score <= manager.critical_threshold, \
            f"Failed to reduce drift below {manager.critical_threshold} in {max_cycles} cycles"
        assert cycles <= max_cycles

    def test_no_performance_degradation(self):
        """Test that auto-repair adds minimal performance overhead."""
        manager = DriftManager()
        manager._initialize_repair_engine()

        # Measure baseline (just threshold check)
        baseline_times = []
        for _ in range(50):
            start = time.perf_counter()
            # Simulate threshold check without repair
            _ = 0.10 > manager.critical_threshold
            baseline_times.append(time.perf_counter() - start)

        # Measure with auto-repair
        repair_times = []
        for _ in range(50):
            start = time.perf_counter()
            manager.on_exceed('ethical', 0.25, {'top_symbols': ['ethical.test']})
            repair_times.append(time.perf_counter() - start)

        # Calculate overhead
        baseline_avg = sum(baseline_times) / len(baseline_times)
        repair_avg = sum(repair_times) / len(repair_times)

        overhead_ms = (repair_avg - baseline_avg) * 1000

        print(f"Baseline: {baseline_avg*1000:.3f}ms, Repair: {repair_avg*1000:.3f}ms")
        print(f"Overhead: {overhead_ms:.3f}ms")

        # Should add < 10ms overhead for auto-repair
        assert overhead_ms < 10.0, f"Auto-repair overhead {overhead_ms:.3f}ms exceeds 10ms limit"

    def test_ledger_includes_repair_rationale(self):
        """Test that ledger entries include repair rationale."""
        manager = DriftManager()
        manager._initialize_repair_engine()

        # Trigger repair
        manager.on_exceed('memory', 0.22, {
            'top_symbols': ['memory.fold_instability'],
            'test': 'rationale_check'
        })

        # Verify repair event has rationale
        repair_events = [
            entry for entry in manager.drift_ledger
            if entry.get('event') == 'auto_repair_success'
        ]

        assert len(repair_events) > 0
        for event in repair_events:
            assert 'rationale' in event
            rationale = event['rationale']
            assert 'reduced drift' in rationale.lower()
            assert event['method'] in rationale.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])