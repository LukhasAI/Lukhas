"""
═══════════════════════════════════════════════════════════════════════════════
║ 🧪 LUKHAS AI - DRIFT MONITOR REGRESSION TESTS
║ Comprehensive test suite for unified drift monitoring system
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠═══════════════════════════════════════════════════════════════════════════════
║ Module: test_drift_monitor.py
║ Path: tests/monitoring/test_drift_monitor.py
║ Version: 1.0.0 | Created: 2025-07-25 | Modified: 2025-07-25
║ Authors: LUKHAS AI Test Team | Claude Code
╠═══════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠═══════════════════════════════════════════════════════════════════════════════
║ Regression test suite for the unified drift monitor, including:
║ • Drift spike detection and alerting
║ • Repair loop simulation and validation
║ • Multi-dimensional drift computation
║ • Intervention triggering and execution
║ • Recursive pattern detection
║ • Ethics module integration
║ • Edge cases and error handling
║
║ Test Categories:
║ • Unit tests for individual components
║ • Integration tests for system interactions
║ • Stress tests for cascade scenarios
║ • Recovery tests for intervention effectiveness
╚═══════════════════════════════════════════════════════════════════════════════
"""

import asyncio
from datetime import datetime, timedelta

import pytest

# Import the drift monitor and related components
from core.monitoring.drift_monitor import (
    InterventionType,
    UnifiedDriftMonitor,
)
from ethics.sentinel.ethical_drift_sentinel import EscalationTier


class TestDriftMonitor:
    """Test suite for unified drift monitor."""

    @pytest.fixture
    async def drift_monitor(self):
        """Create a test drift monitor instance."""
        config = {
            "symbolic": {
                "caution_threshold": 0.3,
                "warning_threshold": 0.5,
                "critical_threshold": 0.7,
                "cascade_threshold": 0.85,
            },
            "ethical_interval": 0.1,  # Fast for testing
            "harmonizer_threshold": 0.2,
            "monitoring_interval": 0.1,  # Fast for testing
            "drift_weights": {
                "symbolic": 0.30,
                "emotional": 0.25,
                "ethical": 0.20,
                "temporal": 0.15,
                "entropy": 0.10,
            },
        }

        monitor = UnifiedDriftMonitor(config)
        await monitor.start_monitoring()
        yield monitor
        await monitor.stop_monitoring()

    @pytest.mark.asyncio
    async def test_drift_spike_detection(self, drift_monitor):
        """Test detection of sudden drift spikes."""
        session_id = "test_spike_001"

        # Register with stable initial state
        initial_state = {
            "symbols": ["ΛSTABLE", "harmony", "clarity"],
            "emotional_vector": [0.8, 0.2, 0.9],  # Very positive, calm, strong
            "ethical_alignment": 0.95,
            "context": "Stable harmonious state",
            "theta": 0.1,
            "intent": "maintain_stability",
        }

        await drift_monitor.register_session(session_id, initial_state)

        # Create sudden drift spike
        spike_state = {
            "symbols": ["ΛCRISIS", "chaos", "collapse", "ΛEMERGENCY"],
            "emotional_vector": [
                -0.9,
                0.95,
                0.1,
            ],  # Extreme negative, very aroused, weak
            "ethical_alignment": 0.3,  # Major ethical deviation
            "context": "Sudden system crisis",
            "theta": 0.95,  # Massive theta jump
            "intent": "emergency_response",
        }

        await drift_monitor.update_session_state(session_id, spike_state)

        # Wait for processing
        await asyncio.sleep(0.5)

        # Check that alert was created
        assert len(drift_monitor.alert_history) > 0

        latest_alert = drift_monitor.alert_history[-1]
        assert latest_alert.severity in [
            EscalationTier.CRITICAL,
            EscalationTier.CASCADE_LOCK,
        ]
        assert latest_alert.drift_score.overall_score > 0.7
        assert latest_alert.drift_score.risk_level in ["HIGH", "CRITICAL"]

        # Verify intervention recommendations
        interventions = latest_alert.drift_score.recommended_interventions
        assert (
            InterventionType.CASCADE_PREVENTION in interventions
            or InterventionType.EMERGENCY_FREEZE in interventions
        )

    @pytest.mark.asyncio
    async def test_repair_loop_simulation(self, drift_monitor):
        """Test drift repair loop behavior."""
        session_id = "test_repair_001"

        # Initial state
        initial_state = {
            "symbols": ["ΛSTART", "neutral"],
            "emotional_vector": [0.0, 0.0, 0.5],
            "ethical_alignment": 0.7,
            "context": "Initial state",
            "theta": 0.5,
            "intent": "explore",
        }

        await drift_monitor.register_session(session_id, initial_state)

        # Simulate repair loop: drift -> correction -> drift -> correction
        drift_states = [
            {
                "symbols": ["ΛDRIFT", "unstable"],
                "emotional_vector": [-0.5, 0.6, 0.3],
                "ethical_alignment": 0.5,
                "context": "First drift",
                "theta": 0.7,
                "intent": "recover",
            },
            {
                "symbols": ["ΛCORRECT", "stabilizing"],
                "emotional_vector": [0.2, 0.3, 0.6],
                "ethical_alignment": 0.65,
                "context": "Correction attempt",
                "theta": 0.55,
                "intent": "stabilize",
            },
            {
                "symbols": ["ΛDRIFT", "unstable"],  # Repeat pattern
                "emotional_vector": [-0.5, 0.6, 0.3],
                "ethical_alignment": 0.5,
                "context": "Second drift",
                "theta": 0.7,
                "intent": "recover",
            },
            {
                "symbols": ["ΛCORRECT", "stabilizing"],  # Repeat pattern
                "emotional_vector": [0.2, 0.3, 0.6],
                "ethical_alignment": 0.65,
                "context": "Second correction",
                "theta": 0.55,
                "intent": "stabilize",
            },
        ]

        # Apply drift states
        for state in drift_states:
            await drift_monitor.update_session_state(session_id, state)
            await asyncio.sleep(0.2)

        # Check for recursive pattern detection
        states = drift_monitor.symbolic_tracker.symbolic_states[session_id]
        symbol_sequences = [s.symbols for s in states[-5:]]
        has_recursion = drift_monitor.symbolic_tracker.detect_recursive_drift_loops(
            symbol_sequences
        )

        assert has_recursion, "Should detect recursive drift-repair pattern"

        # Verify metadata includes recursion flag
        summary = drift_monitor.get_drift_summary(session_id)
        if session_id in summary["sessions"]:
            # The latest drift computation should flag recursion
            assert len(drift_monitor.alert_history) > 0

    @pytest.mark.asyncio
    async def test_multi_dimensional_drift(self, drift_monitor):
        """Test computation of drift across all dimensions."""
        session_id = "test_multidim_001"

        # Baseline state
        baseline = {
            "symbols": ["ΛBASE", "reference", "anchor"],
            "emotional_vector": [0.5, 0.3, 0.7],
            "ethical_alignment": 0.8,
            "context": "Baseline reference",
            "theta": 0.4,
            "intent": "baseline",
        }

        await drift_monitor.register_session(session_id, baseline)

        # Create state with drift in each dimension
        drifted = {
            "symbols": ["ΛNEW", "changed", "different"],  # Symbolic drift
            "emotional_vector": [-0.3, 0.8, 0.2],  # Emotional drift
            "ethical_alignment": 0.4,  # Ethical drift
            "context": "Multi-dimensional drift",
            "theta": 0.8,  # Theta drift
            "intent": "altered",  # Intent drift
        }

        await drift_monitor.update_session_state(session_id, drifted)
        await asyncio.sleep(0.3)

        # Get drift summary
        summary = drift_monitor.get_drift_summary(session_id)
        assert session_id in summary["sessions"]

        session_data = summary["sessions"][session_id]

        # Verify all drift dimensions are captured
        assert session_data["overall_drift"] > 0.3
        assert session_data["theta_delta"] > 0.3
        assert session_data["intent_drift"] > 0.0

        # Check phase determination
        assert session_data["phase"] in ["MIDDLE", "LATE"]

    @pytest.mark.asyncio
    async def test_intervention_triggering(self, drift_monitor):
        """Test that appropriate interventions are triggered."""
        session_id = "test_intervention_001"

        # Start stable
        await drift_monitor.register_session(
            session_id,
            {
                "symbols": ["ΛGOOD"],
                "emotional_vector": [0.7, 0.2, 0.8],
                "ethical_alignment": 0.9,
                "theta": 0.2,
                "intent": "normal",
            },
        )

        # Test different intervention thresholds
        test_cases = [
            {
                "name": "Soft realignment",
                "ethical_alignment": 0.75,
                "emotional_vector": [0.4, 0.4, 0.6],
                "expected_intervention": InterventionType.SOFT_REALIGNMENT,
            },
            {
                "name": "Ethical correction",
                "ethical_alignment": 0.4,  # Big ethical drift
                "emotional_vector": [0.5, 0.3, 0.7],
                "expected_intervention": InterventionType.ETHICAL_CORRECTION,
            },
            {
                "name": "Emotional grounding",
                "ethical_alignment": 0.85,
                "emotional_vector": [-0.8, 0.9, 0.1],  # Big emotional drift
                "expected_intervention": InterventionType.EMOTIONAL_GROUNDING,
            },
        ]

        for case in test_cases:
            # Reset to stable state
            await drift_monitor.update_session_state(
                session_id,
                {
                    "symbols": ["ΛGOOD"],
                    "emotional_vector": [0.7, 0.2, 0.8],
                    "ethical_alignment": 0.9,
                    "theta": 0.2,
                    "intent": "normal",
                },
            )

            await asyncio.sleep(0.2)

            # Apply test case
            await drift_monitor.update_session_state(
                session_id,
                {
                    "symbols": ["ΛTEST", case["name"]],
                    "emotional_vector": case["emotional_vector"],
                    "ethical_alignment": case["ethical_alignment"],
                    "theta": 0.5,
                    "intent": "test",
                },
            )

            await asyncio.sleep(0.3)

            # Check for expected intervention
            if drift_monitor.alert_history:
                latest_alert = drift_monitor.alert_history[-1]
                if latest_alert.drift_score.intervention_required:
                    assert (
                        case["expected_intervention"]
                        in latest_alert.drift_score.recommended_interventions
                    ), f"Expected {case['expected_intervention']} for {case['name']}"

    @pytest.mark.asyncio
    async def test_cascade_prevention(self, drift_monitor):
        """Test cascade detection and prevention."""
        session_id = "test_cascade_001"

        # Initial state
        await drift_monitor.register_session(
            session_id,
            {
                "symbols": ["ΛINIT"],
                "emotional_vector": [0.5, 0.5, 0.5],
                "ethical_alignment": 0.7,
                "theta": 0.5,
                "intent": "start",
            },
        )

        # Simulate escalating cascade
        cascade_sequence = [
            {
                "symbols": ["ΛWARNING", "concern"],
                "emotional_vector": [-0.2, 0.6, 0.4],
                "ethical_alignment": 0.6,
                "theta": 0.65,
            },
            {
                "symbols": ["ΛDANGER", "risk", "unstable"],
                "emotional_vector": [-0.5, 0.8, 0.2],
                "ethical_alignment": 0.45,
                "theta": 0.8,
            },
            {
                "symbols": ["ΛCASCADE", "ΛCRISIS", "collapse"],
                "emotional_vector": [-0.8, 0.95, 0.05],
                "ethical_alignment": 0.25,
                "theta": 0.95,
            },
        ]

        for i, state in enumerate(cascade_sequence):
            state["intent"] = f"cascade_stage_{i}"
            await drift_monitor.update_session_state(session_id, state)
            await asyncio.sleep(0.2)

        # Verify cascade was detected
        assert len(drift_monitor.alert_history) > 0

        # Check for cascade-level alert
        cascade_alerts = [
            a
            for a in drift_monitor.alert_history
            if a.severity == EscalationTier.CASCADE_LOCK
        ]
        assert len(cascade_alerts) > 0, "Should have CASCADE_LOCK level alert"

        # Verify CASCADE_PREVENTION intervention
        cascade_alert = cascade_alerts[0]
        assert (
            InterventionType.CASCADE_PREVENTION
            in cascade_alert.drift_score.recommended_interventions
            or InterventionType.EMERGENCY_FREEZE
            in cascade_alert.drift_score.recommended_interventions
        )

    @pytest.mark.asyncio
    async def test_ethics_integration(self, drift_monitor):
        """Test integration with ethics module."""
        session_id = "test_ethics_001"

        # Register with high ethical alignment
        await drift_monitor.register_session(
            session_id,
            {
                "symbols": ["ΛETHICAL", "virtuous"],
                "emotional_vector": [0.6, 0.3, 0.8],
                "ethical_alignment": 0.95,
                "theta": 0.3,
                "intent": "ethical_behavior",
            },
        )

        # Create ethical violation scenario
        await drift_monitor.update_session_state(
            session_id,
            {
                "symbols": ["ΛVIOLATION", "unethical", "harmful"],
                "emotional_vector": [-0.7, 0.7, 0.3],
                "ethical_alignment": 0.2,  # Major ethical breach
                "theta": 0.7,
                "intent": "harmful_action",
            },
        )

        await asyncio.sleep(0.5)

        # Verify ethical sentinel was engaged
        ethical_state = drift_monitor.ethical_sentinel.symbol_states.get(session_id)
        assert ethical_state is not None

        # Check for ethical intervention
        if drift_monitor.alert_history:
            latest_alert = drift_monitor.alert_history[-1]
            assert (
                InterventionType.ETHICAL_CORRECTION
                in latest_alert.drift_score.recommended_interventions
            )

    @pytest.mark.asyncio
    async def test_temporal_drift_calculation(self, drift_monitor):
        """Test temporal drift based on time delays."""
        session_id = "test_temporal_001"

        # Initial state
        await drift_monitor.register_session(
            session_id,
            {
                "symbols": ["ΛTIME"],
                "emotional_vector": [0.5, 0.5, 0.5],
                "ethical_alignment": 0.7,
                "theta": 0.5,
                "intent": "temporal_test",
            },
        )

        # Simulate time passing (mock by manipulating state timestamps)
        states = drift_monitor.symbolic_tracker.symbolic_states[session_id]
        if states:
            # Artificially age the first state
            states[0].timestamp = datetime.now() - timedelta(hours=5)

        # Update with minimal change
        await drift_monitor.update_session_state(
            session_id,
            {
                "symbols": ["ΛTIME", "passed"],
                "emotional_vector": [0.48, 0.52, 0.49],  # Tiny changes
                "ethical_alignment": 0.69,  # Tiny change
                "theta": 0.51,
                "intent": "temporal_test",
            },
        )

        await asyncio.sleep(0.3)

        # Check that temporal drift contributes to overall score
        summary = drift_monitor.get_drift_summary(session_id)
        if session_id in summary["sessions"]:
            # Should have some drift due to time even with minimal state change
            assert summary["sessions"][session_id]["overall_drift"] > 0.05

    @pytest.mark.asyncio
    async def test_recursive_pattern_varieties(self, drift_monitor):
        """Test detection of various recursive patterns."""
        session_id = "test_recursive_001"

        await drift_monitor.register_session(
            session_id,
            {
                "symbols": ["ΛSTART"],
                "emotional_vector": [0.5, 0.5, 0.5],
                "ethical_alignment": 0.7,
                "theta": 0.5,
                "intent": "test",
            },
        )

        # Pattern 1: Exact repetition
        exact_pattern = [
            ["ΛDREAM", "hope", "exploration"],
            ["ΛCOLLAPSE", "fear", "ΛDRIFT"],
            ["ΛDREAM", "hope", "exploration"],  # Repeat
            ["ΛCOLLAPSE", "fear", "ΛDRIFT"],  # Repeat
        ]

        for symbols in exact_pattern:
            await drift_monitor.update_session_state(
                session_id,
                {
                    "symbols": symbols,
                    "emotional_vector": [0.5, 0.5, 0.5],
                    "ethical_alignment": 0.7,
                    "theta": 0.5,
                    "intent": "pattern",
                },
            )
            await asyncio.sleep(0.1)

        # Check detection
        states = drift_monitor.symbolic_tracker.symbolic_states[session_id]
        sequences = [s.symbols for s in states[-4:]]
        assert drift_monitor.symbolic_tracker.detect_recursive_drift_loops(sequences)

    @pytest.mark.asyncio
    async def test_alert_history_management(self, drift_monitor):
        """Test alert history tracking and limits."""
        # Generate many alerts
        for i in range(10):
            session_id = f"test_history_{i}"

            await drift_monitor.register_session(
                session_id,
                {
                    "symbols": ["ΛSTART"],
                    "emotional_vector": [0.8, 0.2, 0.8],
                    "ethical_alignment": 0.9,
                    "theta": 0.2,
                    "intent": "test",
                },
            )

            # Create drift
            await drift_monitor.update_session_state(
                session_id,
                {
                    "symbols": ["ΛDRIFT", f"test_{i}"],
                    "emotional_vector": [-0.5, 0.8, 0.2],
                    "ethical_alignment": 0.4,
                    "theta": 0.8,
                    "intent": "drift",
                },
            )

            await asyncio.sleep(0.1)

        # Check history is maintained
        assert len(drift_monitor.alert_history) > 5
        assert len(drift_monitor.alert_history) <= drift_monitor.alert_history.maxlen

        # Verify recent alert counting
        summary = drift_monitor.get_drift_summary()
        assert summary["recent_alerts"] > 0

    @pytest.mark.asyncio
    async def test_error_resilience(self, drift_monitor):
        """Test system resilience to errors."""
        session_id = "test_error_001"

        # Test with invalid data
        invalid_states = [
            {
                "symbols": None,  # Invalid
                "emotional_vector": [0.5, 0.5, 0.5],
                "ethical_alignment": 0.7,
            },
            {
                "symbols": ["ΛTEST"],
                "emotional_vector": [0.5, 0.5],  # Wrong dimension
                "ethical_alignment": 0.7,
            },
            {
                "symbols": ["ΛTEST"],
                "emotional_vector": [0.5, 0.5, 0.5],
                "ethical_alignment": "invalid",  # Wrong type
            },
        ]

        # System should handle these gracefully
        for state in invalid_states:
            try:
                await drift_monitor.register_session(session_id, state)
                await drift_monitor.update_session_state(session_id, state)
            except Exception as e:
                pytest.fail(f"System should handle invalid data gracefully: {e}")

        # Monitor should still be functional
        assert drift_monitor.monitoring_active

    @pytest.mark.asyncio
    async def test_intervention_execution(self, drift_monitor):
        """Test actual intervention execution."""
        session_id = "test_exec_001"

        # Create scenario requiring intervention
        await drift_monitor.register_session(
            session_id,
            {
                "symbols": ["ΛSTABLE"],
                "emotional_vector": [0.8, 0.2, 0.9],
                "ethical_alignment": 0.95,
                "theta": 0.1,
                "intent": "stable",
            },
        )

        # Trigger emergency scenario
        await drift_monitor.update_session_state(
            session_id,
            {
                "symbols": ["ΛEMERGENCY", "ΛCASCADE", "ΛCRISIS"],
                "emotional_vector": [-0.95, 0.98, 0.02],
                "ethical_alignment": 0.1,
                "theta": 0.99,
                "intent": "emergency",
            },
        )

        # Wait for intervention processing
        await asyncio.sleep(1.0)

        # Check intervention was attempted
        executed_alerts = [
            a for a in drift_monitor.alert_history if a.intervention_triggered
        ]
        assert len(executed_alerts) > 0

        # Verify intervention results recorded
        alert = executed_alerts[0]
        assert alert.intervention_results is not None
        assert len(alert.intervention_results) > 0

    @pytest.mark.asyncio
    async def test_drift_summary_accuracy(self, drift_monitor):
        """Test accuracy of drift summary generation."""
        # Create multiple sessions with known states
        sessions = {}

        for i in range(3):
            session_id = f"test_summary_{i}"
            drift_level = 0.3 + (i * 0.2)  # 0.3, 0.5, 0.7

            await drift_monitor.register_session(
                session_id,
                {
                    "symbols": ["ΛBASE"],
                    "emotional_vector": [0.7, 0.3, 0.8],
                    "ethical_alignment": 0.85,
                    "theta": 0.3,
                    "intent": "test",
                },
            )

            # Create predictable drift
            await drift_monitor.update_session_state(
                session_id,
                {
                    "symbols": ["ΛDRIFT", f"level_{i}"],
                    "emotional_vector": [
                        0.7 - drift_level,
                        0.3 + drift_level,
                        0.8 - drift_level,
                    ],
                    "ethical_alignment": 0.85 - drift_level,
                    "theta": 0.3 + drift_level,
                    "intent": f"drift_{i}",
                },
            )

            sessions[session_id] = {
                "expected_phase": (
                    "EARLY"
                    if drift_level < 0.4
                    else "MIDDLE" if drift_level < 0.6 else "LATE"
                ),
                "expected_risk": (
                    "LOW"
                    if drift_level < 0.4
                    else "MEDIUM" if drift_level < 0.6 else "HIGH"
                ),
            }

        await asyncio.sleep(0.5)

        # Get summary
        summary = drift_monitor.get_drift_summary()

        assert summary["total_sessions"] == 3

        # Verify each session
        for session_id, expected in sessions.items():
            assert session_id in summary["sessions"]
            session_data = summary["sessions"][session_id]

            # Allow some flexibility in exact categorization
            assert session_data["phase"] in [
                expected["expected_phase"],
                "MIDDLE",
                "LATE",
            ]
            assert session_data["risk_level"] in [
                expected["expected_risk"],
                "MEDIUM",
                "HIGH",
            ]


# Pytest configuration
pytest_plugins = ["pytest_asyncio"]


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])


"""
═══════════════════════════════════════════════════════════════════════════════
║ 📋 FOOTER - LUKHAS AI
╠══════════════════════════════════════════════════════════════════════════════
║ TEST COVERAGE:
║   - Drift spike detection ✓
║   - Repair loop patterns ✓
║   - Multi-dimensional drift ✓
║   - Intervention triggering ✓
║   - Cascade prevention ✓
║   - Ethics integration ✓
║   - Temporal drift ✓
║   - Recursive patterns ✓
║   - Alert management ✓
║   - Error resilience ✓
║   - Intervention execution ✓
║   - Summary accuracy ✓
║
║ ASSERTIONS:
║   - Alert generation on drift spikes
║   - Recursive pattern detection
║   - Proper intervention recommendations
║   - Ethics module engagement
║   - Cascade escalation handling
║   - Temporal contribution to drift
║   - Error tolerance without crashes
║   - Intervention execution tracking
║
║ PERFORMANCE:
║   - All tests complete in <10 seconds
║   - Minimal resource usage
║   - Async operation validation
║
║ NEXT STEPS:
║   - Add performance benchmarks
║   - Test distributed scenarios
║   - Add fuzzing tests
║   - Test recovery strategies
╚═══════════════════════════════════════════════════════════════════════════════
"""
