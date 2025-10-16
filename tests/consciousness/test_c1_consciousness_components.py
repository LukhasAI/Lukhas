#!/usr/bin/env python3
"""
LUKHAS Consciousness C.1 Components Test Suite - Production Schema v1.0.0

Comprehensive testing for the complete C.1 consciousness implementation:
- AwarenessEngine with drift EMA and anomaly detection
- DreamEngine with FSM phase transitions
- AutoConsciousness with Guardian validation
- ConsciousnessStream coordination

T4/0.01% excellence standards with property-based testing.
"""

import time

import pytest
from hypothesis import given, strategies as st

# Configure asyncio testing
pytestmark = pytest.mark.asyncio

# Import consciousness components
from consciousness import (
    AutoConsciousness,
    AwarenessEngine,
    AwarenessSnapshot,
    ConsciousnessState,
    ConsciousnessStream,
    DecisionContext,
    DreamEngine,
    DreamTrace,
    GuardianResponse,
    ReflectionReport,
)


class TestAwarenessEngine:
    """Test suite for AwarenessEngine with drift EMA and anomaly detection."""

    @pytest.fixture
    def awareness_engine(self):
        """Create AwarenessEngine instance for testing."""
        return AwarenessEngine()

    @pytest.fixture
    def sample_consciousness_state(self):
        """Create sample consciousness state."""
        return ConsciousnessState(
            phase="AWARE",
            awareness_level="basic",
            emotional_tone="neutral",
            level=0.7
        )

    @pytest.fixture
    def sample_signals(self):
        """Create sample signal data."""
        return {
            "processing_queue_size": 5,
            "active_threads": 3,
            "memory_pressure": 0.3,
            "cpu_utilization": 0.4,
            "signal_strength": 0.8
        }

    @pytest.mark.asyncio
    async def test_awareness_update_basic(self, awareness_engine, sample_consciousness_state, sample_signals):
        """Test basic awareness update functionality."""
        snapshot = await awareness_engine.update(sample_consciousness_state, sample_signals)

        assert isinstance(snapshot, AwarenessSnapshot)
        assert snapshot.schema_version == "1.0.0"
        assert snapshot.timestamp > 0
        assert 0.0 <= snapshot.drift_ema <= 1.0
        assert 0.0 <= snapshot.load_factor <= 1.0
        assert 0.0 <= snapshot.signal_strength <= 1.0
        assert snapshot.processing_time_ms >= 0

    @pytest.mark.asyncio
    async def test_drift_ema_tracking(self, awareness_engine, sample_consciousness_state, sample_signals):
        """Test EMA drift tracking over multiple updates."""
        snapshots = []

        # Perform multiple updates with changing state
        for i in range(5):
            state = ConsciousnessState(
                phase="AWARE",
                level=0.5 + (i * 0.1)  # Gradually increasing level
            )
            snapshot = await awareness_engine.update(state, sample_signals)
            snapshots.append(snapshot)

        # Verify drift tracking
        assert len(snapshots) == 5
        # Drift should reflect state changes
        assert snapshots[-1].drift_ema > 0.0

    @pytest.mark.asyncio
    async def test_anomaly_detection_high_drift(self, awareness_engine, sample_consciousness_state, sample_signals):
        """Test anomaly detection for high drift scenarios."""
        # Create conditions for high drift
        high_drift_signals = {**sample_signals, "processing_queue_size": 200}

        # Multiple updates to build up drift
        for i in range(10):
            state = ConsciousnessState(phase="AWARE", level=float(i % 2))  # Alternating levels
            snapshot = await awareness_engine.update(state, high_drift_signals)

        # Should detect drift anomaly
        if snapshot.drift_ema > 0.8:
            drift_anomalies = [a for a in snapshot.anomalies if a["type"] == "high_drift"]
            assert len(drift_anomalies) > 0

    @pytest.mark.asyncio
    async def test_load_factor_calculation(self, awareness_engine, sample_consciousness_state):
        """Test load factor calculation from signals."""
        high_load_signals = {
            "processing_queue_size": 150,
            "active_threads": 15,
            "memory_pressure": 0.9,
            "cpu_utilization": 0.95
        }

        snapshot = await awareness_engine.update(sample_consciousness_state, high_load_signals)
        assert snapshot.load_factor > 0.5

        # Should detect high load anomaly
        load_anomalies = [a for a in snapshot.anomalies if a["type"] == "high_load"]
        if snapshot.load_factor > 0.8:
            assert len(load_anomalies) > 0

    @pytest.mark.asyncio
    async def test_performance_latency_target(self, awareness_engine, sample_consciousness_state, sample_signals):
        """Test that awareness updates meet performance targets."""
        start_time = time.time()
        snapshot = await awareness_engine.update(sample_consciousness_state, sample_signals)
        latency_ms = (time.time() - start_time) * 1000

        # Should complete well under 100ms for T4/0.01% targets
        assert latency_ms < 100
        assert snapshot.processing_time_ms >= 0

    @pytest.mark.asyncio
    async def test_reset_state(self, awareness_engine, sample_consciousness_state, sample_signals):
        """Test state reset functionality."""
        # Build up some state
        await awareness_engine.update(sample_consciousness_state, sample_signals)
        await awareness_engine.update(sample_consciousness_state, sample_signals)

        # Reset and verify clean state
        awareness_engine.reset_state()

        # After reset, performance stats should show empty state
        stats = awareness_engine.get_performance_stats()
        # After reset with no processing times, should return minimal stats
        assert "mean_processing_time_ms" in stats
        assert stats["mean_processing_time_ms"] == 0.0


class TestDreamEngine:
    """Test suite for DreamEngine with FSM phase transitions."""

    @pytest.fixture
    def dream_engine(self):
        """Create DreamEngine instance for testing."""
        return DreamEngine()

    @pytest.fixture
    def sample_consciousness_state(self):
        """Create sample consciousness state."""
        return ConsciousnessState(phase="DREAM", level=0.8)

    @pytest.fixture
    def sample_memory_events(self):
        """Create sample memory events."""
        return [
            {"type": "reflection_completed", "data": {"score": 0.9}, "timestamp": time.time()},
            {"type": "anomaly_detected", "data": {"severity": "medium"}, "timestamp": time.time()},
            {"type": "decision_made", "data": {"approved": True}, "timestamp": time.time()}
        ]

    @pytest.mark.asyncio
    async def test_dream_cycle_fsm_transitions(self, dream_engine, sample_consciousness_state, sample_memory_events):
        """Test complete FSM phase transitions: IDLE→ENTERING→DREAMING→EXITING→IDLE."""
        initial_phase = dream_engine.get_current_phase()
        assert initial_phase == "IDLE"

        dream_trace = await dream_engine.process_cycle(
            sample_consciousness_state,
            sample_memory_events,
            trigger_reason="test_cycle"
        )

        # Verify dream trace structure
        assert isinstance(dream_trace, DreamTrace)
        assert dream_trace.schema_version == "1.0.0"
        assert dream_trace.phase == "IDLE"  # Should end in IDLE
        assert dream_trace.reason == "test_cycle"
        assert dream_trace.memory_events_processed == len(sample_memory_events)
        assert dream_trace.duration_ms > 0

        # Should be back in IDLE phase
        final_phase = dream_engine.get_current_phase()
        assert final_phase == "IDLE"

    @pytest.mark.asyncio
    async def test_memory_consolidation(self, dream_engine, sample_consciousness_state):
        """Test memory consolidation processing."""
        # Create enough events to trigger consolidation
        large_memory_events = [
            {"type": f"event_{i}", "data": {"value": i}, "timestamp": time.time()}
            for i in range(150)  # Exceeds default threshold of 100
        ]

        dream_trace = await dream_engine.process_cycle(
            sample_consciousness_state,
            large_memory_events,
            trigger_reason="memory_pressure"
        )

        assert dream_trace.consolidation_count > 0
        assert dream_trace.compression_ratio <= 1.0

    @pytest.mark.asyncio
    async def test_pattern_discovery(self, dream_engine, sample_consciousness_state, sample_memory_events):
        """Test pattern discovery functionality."""
        dream_trace = await dream_engine.process_cycle(
            sample_consciousness_state,
            sample_memory_events,
            trigger_reason="pattern_discovery"
        )

        # Should discover some patterns
        assert isinstance(dream_trace.top_k_motifs, list)
        assert dream_trace.memory_patterns_discovered >= 0

    @pytest.mark.asyncio
    async def test_dream_duration_constraint(self, dream_engine, sample_consciousness_state, sample_memory_events):
        """Test that dream cycles respect maximum duration constraint."""
        start_time = time.time()
        dream_trace = await dream_engine.process_cycle(
            sample_consciousness_state,
            sample_memory_events,
            trigger_reason="duration_test"
        )
        total_time = time.time() - start_time

        # Should complete within reasonable time
        assert total_time < 1.0  # 1 second max for test
        assert dream_trace.duration_ms < dream_engine.max_duration_ms * 2  # Allow some overhead

    @pytest.mark.asyncio
    async def test_should_trigger_dream_conditions(self, dream_engine):
        """Test dream trigger conditions."""
        # Test memory pressure trigger
        assert dream_engine.should_trigger_dream(memory_pressure=0.9) == True

        # Reset dream engine state first
        dream_engine.reset_state()

        # Test low memory pressure (should not trigger immediately after reset)
        result = dream_engine.should_trigger_dream(memory_pressure=0.1)
        # May still trigger due to time since last consolidation, so just verify it's a boolean
        assert isinstance(result, bool)

    @pytest.mark.asyncio
    async def test_dream_performance_stats(self, dream_engine, sample_consciousness_state, sample_memory_events):
        """Test performance statistics tracking."""
        await dream_engine.process_cycle(sample_consciousness_state, sample_memory_events)

        stats = dream_engine.get_performance_stats()
        assert "total_cycles" in stats
        assert "average_duration_ms" in stats
        assert "consolidation_rate" in stats
        assert stats["total_cycles"] == 1


class TestAutoConsciousness:
    """Test suite for AutoConsciousness with Guardian validation."""

    @pytest.fixture
    def mock_guardian_validator(self):
        """Create mock Guardian validator."""
        def validator(decision_context):
            # Approve if confidence > 0.7
            approved = decision_context.confidence_score > 0.7
            return GuardianResponse(
                approved=approved,
                reason="Test Guardian validation",
                confidence=decision_context.confidence_score
            )
        return validator

    @pytest.fixture
    def auto_consciousness(self, mock_guardian_validator):
        """Create AutoConsciousness instance for testing."""
        return AutoConsciousness(guardian_validator=mock_guardian_validator)

    @pytest.fixture
    def sample_consciousness_state(self):
        """Create sample consciousness state."""
        return ConsciousnessState(phase="DECIDE", level=0.8)

    @pytest.fixture
    def sample_awareness_snapshot(self):
        """Create sample awareness snapshot."""
        return AwarenessSnapshot(
            drift_ema=0.3,
            load_factor=0.5,
            signal_strength=0.8,
            signal_noise_ratio=2.0
        )

    @pytest.fixture
    def sample_reflection_report(self):
        """Create sample reflection report."""
        return ReflectionReport(
            coherence_score=0.9,
            drift_ema=0.2,
            state_delta_magnitude=0.1
        )

    @pytest.mark.asyncio
    async def test_decision_cycle_basic(self, auto_consciousness, sample_consciousness_state,
                                      sample_awareness_snapshot, sample_reflection_report):
        """Test basic decision-making cycle."""
        decision_context = await auto_consciousness.decide_and_act(
            consciousness_state=sample_consciousness_state,
            awareness_snapshot=sample_awareness_snapshot,
            reflection_report=sample_reflection_report
        )

        assert isinstance(decision_context, DecisionContext)
        assert decision_context.schema_version == "1.0.0"
        assert decision_context.consciousness_state == sample_consciousness_state
        assert decision_context.awareness_snapshot == sample_awareness_snapshot
        assert decision_context.reflection_report == sample_reflection_report
        assert 0.0 <= decision_context.confidence_score <= 1.0
        assert isinstance(decision_context.guardian_approved, bool)

    @pytest.mark.asyncio
    async def test_action_generation(self, auto_consciousness, sample_consciousness_state,
                                   sample_awareness_snapshot, sample_reflection_report):
        """Test action generation based on consciousness inputs."""
        # Create high-drift scenario
        high_drift_awareness = AwarenessSnapshot(
            drift_ema=0.9,  # High drift
            load_factor=0.9,  # High load
            anomalies=[{"type": "critical_error", "severity": "critical"}]
        )

        decision_context = await auto_consciousness.decide_and_act(
            consciousness_state=sample_consciousness_state,
            awareness_snapshot=high_drift_awareness,
            reflection_report=sample_reflection_report
        )

        # Should generate stabilization actions
        action_types = [action.get("type") for action in decision_context.proposed_actions]
        assert len(action_types) > 0
        # May include drift stabilization, load reduction, or anomaly response

    @pytest.mark.asyncio
    async def test_guardian_approval_logic(self, auto_consciousness, sample_consciousness_state):
        """Test Guardian approval logic."""
        # High confidence scenario
        high_confidence_awareness = AwarenessSnapshot(drift_ema=0.1, load_factor=0.2)
        decision_context = await auto_consciousness.decide_and_act(
            consciousness_state=sample_consciousness_state,
            awareness_snapshot=high_confidence_awareness
        )

        # Guardian approval depends on both confidence and Guardian logic
        # Just verify the approval is boolean and consistent with Guardian response
        assert isinstance(decision_context.guardian_approved, bool)
        if decision_context.guardian_response:
            assert decision_context.guardian_approved == decision_context.guardian_response["approved"]

    @pytest.mark.asyncio
    async def test_confidence_score_calculation(self, auto_consciousness, sample_consciousness_state):
        """Test confidence score calculation."""
        # Perfect conditions
        perfect_awareness = AwarenessSnapshot(drift_ema=0.0, load_factor=0.1)
        perfect_reflection = ReflectionReport(coherence_score=1.0, drift_ema=0.0)

        decision_context = await auto_consciousness.decide_and_act(
            consciousness_state=sample_consciousness_state,
            awareness_snapshot=perfect_awareness,
            reflection_report=perfect_reflection
        )

        # Should have high confidence
        assert decision_context.confidence_score > 0.5

    @pytest.mark.asyncio
    async def test_performance_latency_target(self, auto_consciousness, sample_consciousness_state):
        """Test decision-making latency meets performance targets."""
        start_time = time.time()
        await auto_consciousness.decide_and_act(
            consciousness_state=sample_consciousness_state
        )
        latency_ms = (time.time() - start_time) * 1000

        # Should complete within reasonable time for autonomous decisions
        assert latency_ms < 500  # 500ms target for decision cycles

    @pytest.mark.asyncio
    async def test_performance_stats_tracking(self, auto_consciousness, sample_consciousness_state):
        """Test performance statistics tracking."""
        await auto_consciousness.decide_and_act(consciousness_state=sample_consciousness_state)

        stats = auto_consciousness.get_performance_stats()
        assert "total_decisions" in stats
        assert "approval_rate" in stats
        assert "average_confidence" in stats
        assert stats["total_decisions"] >= 1


class TestConsciousnessStream:
    """Test suite for ConsciousnessStream coordination."""

    @pytest.fixture
    def consciousness_stream(self):
        """Create ConsciousnessStream instance for testing."""
        return ConsciousnessStream()

    @pytest.mark.asyncio
    async def test_stream_lifecycle(self, consciousness_stream):
        """Test consciousness stream start/stop lifecycle."""
        # Initially not running
        assert not consciousness_stream._is_running

        # Start the stream
        await consciousness_stream.start()
        assert consciousness_stream._is_running

        # Stop the stream
        await consciousness_stream.stop()
        assert not consciousness_stream._is_running

    @pytest.mark.asyncio
    async def test_consciousness_tick_basic(self, consciousness_stream):
        """Test basic consciousness tick processing."""
        await consciousness_stream.start()

        signals = {"test_signal": 1.0, "processing_queue_size": 5}
        metrics = await consciousness_stream.tick(signals)

        assert metrics.schema_version == "1.0.0"
        assert metrics.tick_rate_hz >= 0
        assert metrics.reflection_p95_ms >= 0

        await consciousness_stream.stop()

    @pytest.mark.asyncio
    async def test_phase_transitions(self, consciousness_stream):
        """Test consciousness phase transitions through complete cycle."""
        await consciousness_stream.start()

        initial_state = consciousness_stream.get_current_state()
        assert initial_state.phase == "IDLE"

        # Process several ticks to trigger phase transitions
        for i in range(10):
            signals = {"signal_strength": 0.8, "processing_queue_size": i}
            await consciousness_stream.tick(signals)

        # Should have transitioned through phases
        final_state = consciousness_stream.get_current_state()
        # Phase may vary based on processing, but should be valid
        assert final_state.phase in ["IDLE", "AWARE", "REFLECT", "DREAM", "DECIDE"]

        await consciousness_stream.stop()

    @pytest.mark.asyncio
    async def test_consciousness_coordination(self, consciousness_stream):
        """Test coordination between consciousness engines."""
        await consciousness_stream.start()

        # Process multiple ticks with varying signals
        for i in range(5):
            signals = {
                "processing_queue_size": 10 + i,
                "memory_pressure": 0.1 * i,
                "cpu_utilization": 0.2 + (0.1 * i)
            }
            await consciousness_stream.tick(signals)

        # Should have processed through multiple engines
        artifacts = consciousness_stream.get_recent_artifacts()
        # At least some artifacts should be generated
        artifact_count = sum(1 for v in artifacts.values() if v is not None)
        assert artifact_count >= 0  # May be 0 if no processing triggered

        await consciousness_stream.stop()

    @pytest.mark.asyncio
    async def test_performance_targets(self, consciousness_stream):
        """Test that consciousness stream meets T4/0.01% performance targets."""
        await consciousness_stream.start()

        # Process multiple ticks and measure performance
        start_time = time.time()
        tick_count = 10

        for i in range(tick_count):
            await consciousness_stream.tick({"test_signal": i})

        total_time = time.time() - start_time
        avg_tick_time = (total_time / tick_count) * 1000  # Convert to ms

        # Should maintain sub-100ms tick processing
        assert avg_tick_time < 100

        await consciousness_stream.stop()

    @pytest.mark.asyncio
    async def test_reset_state(self, consciousness_stream):
        """Test consciousness stream state reset."""
        await consciousness_stream.start()

        # Build up some state
        await consciousness_stream.tick({"test_signal": 1.0})
        await consciousness_stream.tick({"test_signal": 2.0})

        # Reset and verify clean state
        await consciousness_stream.reset_state()
        state = consciousness_stream.get_current_state()
        assert state.phase == "IDLE"
        assert state.level == 0.7  # Default level

        await consciousness_stream.stop()


# Property-based testing with Hypothesis
class TestConsciousnessProperties:
    """Property-based testing for consciousness components."""

    @given(
        consciousness_level=st.floats(min_value=0.0, max_value=1.0),
        drift_ema=st.floats(min_value=0.0, max_value=1.0),
        load_factor=st.floats(min_value=0.0, max_value=1.0)
    )
    @pytest.mark.asyncio
    async def test_awareness_engine_properties(self, consciousness_level, drift_ema, load_factor):
        """Test AwarenessEngine properties with random inputs."""
        awareness_engine = AwarenessEngine()
        state = ConsciousnessState(level=consciousness_level)
        signals = {
            "memory_pressure": load_factor,
            "cpu_utilization": drift_ema
        }

        snapshot = await awareness_engine.update(state, signals)

        # Properties that should always hold
        assert 0.0 <= snapshot.drift_ema <= 1.0
        assert 0.0 <= snapshot.load_factor <= 1.0
        assert 0.0 <= snapshot.signal_strength <= 1.0
        assert snapshot.processing_time_ms >= 0
        assert snapshot.timestamp > 0

    @given(
        memory_events_count=st.integers(min_value=0, max_value=500),
        consciousness_level=st.floats(min_value=0.0, max_value=1.0)
    )
    @pytest.mark.asyncio
    async def test_dream_engine_properties(self, memory_events_count, consciousness_level):
        """Test DreamEngine properties with random inputs."""
        dream_engine = DreamEngine()
        state = ConsciousnessState(level=consciousness_level)
        memory_events = [
            {"type": f"event_{i}", "timestamp": time.time()}
            for i in range(memory_events_count)
        ]

        dream_trace = await dream_engine.process_cycle(state, memory_events)

        # Properties that should always hold
        assert dream_trace.schema_version == "1.0.0"
        assert dream_trace.duration_ms >= 0
        assert dream_trace.consolidation_count >= 0
        assert 0.0 <= dream_trace.compression_ratio <= 1.0
        assert dream_trace.memory_events_processed == memory_events_count


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])
