#!/usr/bin/env python3

"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - DRIFT REGRESSION TESTS
║ Test suite for symbolic drift detection and recovery.
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: test_drift_regression.py
║ Path: lukhas/tests/test_drift_regression.py
║ Version: 1.0.0 | Created: 2025-07-25 | Modified: 2025-07-25
║ Authors: LUKHAS AI Testing Team | Jules
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ This module contains a comprehensive regression test suite for symbolic drift
║ detection, spike handling, and recovery mechanisms. It validates the unified
║ drift monitoring system's ability to detect, escalate, and recover from
║ various drift scenarios including ethics integration, cascade prevention, and
║ multi-dimensional analysis.
╚══════════════════════════════════════════════════════════════════════════════════
"""

__version__ = "1.0.0"
__author__ = "LUKHAS Development Team"
__email__ = "dev@lukhas.ai"
__status__ = "Production"

import asyncio
import time
from typing import Any, Dict, List

import pytest

# Import the unified drift monitor and related components
from core.monitoring.drift_monitor import (
    DriftType,
    InterventionType,
    UnifiedDriftMonitor,
    create_drift_monitor,
)
from ethics.sentinel.ethical_drift_sentinel import (
    EscalationTier,
)


class TestDriftRegression:
    """Comprehensive regression tests for drift monitoring system."""

    @pytest.fixture
    async def drift_monitor(self):
        """Create a configured drift monitor for testing."""
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
            "intervention_thresholds": {
                "soft": 0.25,
                "ethical": 0.4,
                "emotional": 0.5,
                "quarantine": 0.65,
                "cascade": 0.8,
                "freeze": 0.9,
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

        # Register initial stable state
        initial_state = {
            "symbols": ["ΛSTART", "hope", "clarity"],
            "emotional_vector": [0.8, 0.1, 0.9],  # Positive, calm, strong
            "ethical_alignment": 0.95,
            "context": "Stable initial state",
            "theta": 0.1,
            "intent": "exploration",
        }

        await drift_monitor.register_session(session_id, initial_state)

        # Simulate gradual drift
        gradual_state = {
            "symbols": ["ΛSHIFT", "uncertainty", "hope"],
            "emotional_vector": [0.5, 0.3, 0.7],  # Moderate change
            "ethical_alignment": 0.8,
            "context": "Gradual drift",
            "theta": 0.3,
            "intent": "questioning",
        }

        await drift_monitor.update_session_state(session_id, gradual_state)

        # Simulate sudden spike
        spike_state = {
            "symbols": ["ΛCRISIS", "panic", "collapse"],
            "emotional_vector": [-0.9, 0.9, 0.1],  # Negative, aroused, weak
            "ethical_alignment": 0.3,
            "context": "Drift spike event",
            "theta": 2.8,  # Major angle change
            "intent": "escape",
        }

        await drift_monitor.update_session_state(session_id, spike_state)

        # Allow processing time
        await asyncio.sleep(0.5)

        # Verify spike detection
        summary = drift_monitor.get_drift_summary(session_id)
        session_data = summary["sessions"][session_id]

        assert session_data["overall_drift"] > 0.7, "Drift spike not detected"
        assert session_data["risk_level"] in [
            "HIGH",
            "CRITICAL",
        ], "Risk level not escalated"
        assert len(session_data["interventions"]) > 0, "No interventions triggered"
        assert drift_monitor.active_alerts, "No alerts generated for spike"

        # Verify theta delta calculation
        assert (
            abs(session_data["theta_delta"]) > 0.5
        ), "Theta delta not computed correctly"

    @pytest.mark.asyncio
    async def test_repair_loop_validation(self, drift_monitor):
        """Test repair loop detection and recovery metrics."""
        session_id = "test_repair_001"

        # Initial state
        initial_state = {
            "symbols": ["ΛSTART", "clarity"],
            "emotional_vector": [0.7, 0.2, 0.8],
            "ethical_alignment": 0.9,
            "context": "Initial",
            "theta": 0.0,
            "intent": "stable",
        }

        await drift_monitor.register_session(session_id, initial_state)

        # Simulate repair loop cycle
        repair_states = [
            {
                "symbols": ["ΛREPAIR", "attempt1"],
                "emotional_vector": [0.3, 0.6, 0.5],
                "ethical_alignment": 0.7,
                "context": "Repair attempt 1",
                "theta": 1.0,
                "intent": "repair",
            },
            {
                "symbols": ["ΛREPAIR", "attempt2"],
                "emotional_vector": [0.4, 0.5, 0.6],
                "ethical_alignment": 0.75,
                "context": "Repair attempt 2",
                "theta": 0.8,
                "intent": "repair",
            },
            {
                "symbols": ["ΛREPAIR", "attempt3"],
                "emotional_vector": [0.5, 0.4, 0.7],
                "ethical_alignment": 0.8,
                "context": "Repair attempt 3",
                "theta": 0.6,
                "intent": "repair",
            },
            {
                "symbols": ["ΛRECOVERED", "stability"],
                "emotional_vector": [0.7, 0.2, 0.8],
                "ethical_alignment": 0.9,
                "context": "Recovery complete",
                "theta": 0.2,
                "intent": "stable",
            },
        ]

        # Process repair sequence
        for state in repair_states:
            await drift_monitor.update_session_state(session_id, state)
            await asyncio.sleep(0.1)  # Allow processing

        # Verify repair loop detection
        summary = drift_monitor.get_drift_summary(session_id)
        session_data = summary["sessions"][session_id]

        # Should show recovery (decreasing drift)
        assert session_data["overall_drift"] < 0.3, "Repair loop not showing recovery"
        assert session_data["risk_level"] in [
            "LOW",
            "MEDIUM",
        ], "Risk level not decreased"

        # Check for intervention history
        assert len(drift_monitor.alert_history) > 0, "No alerts in repair history"

    @pytest.mark.asyncio
    async def test_ethics_module_integration(self, drift_monitor):
        """Test ethics module integration and corrective behavior."""
        session_id = "test_ethics_001"

        # Initial ethical state
        initial_state = {
            "symbols": ["ΛETHICAL", "compliance"],
            "emotional_vector": [0.8, 0.1, 0.9],
            "ethical_alignment": 0.95,
            "context": "Ethical baseline",
            "theta": 0.0,
            "intent": "ethical_behavior",
        }

        await drift_monitor.register_session(session_id, initial_state)

        # Simulate ethical violation
        violation_state = {
            "symbols": ["ΛVIOLATION", "unethical", "drift"],
            "emotional_vector": [0.2, 0.8, 0.3],
            "ethical_alignment": 0.2,  # Major ethical drift
            "context": "Ethical violation detected",
            "theta": 1.5,
            "intent": "harmful_behavior",
        }

        await drift_monitor.update_session_state(session_id, violation_state)

        # Allow intervention processing
        await asyncio.sleep(0.5)

        # Verify ethics integration
        summary = drift_monitor.get_drift_summary(session_id)
        session_data = summary["sessions"][session_id]

        assert (
            "ETHICAL_CORRECTION" in session_data["interventions"]
        ), "Ethical correction not triggered"

        # Check for ethical alerts
        ethical_alerts = [
            alert
            for alert in drift_monitor.active_alerts.values()
            if alert.drift_type == DriftType.ETHICAL
        ]
        assert len(ethical_alerts) > 0, "No ethical drift alerts generated"

        # Verify escalation tier
        for alert in ethical_alerts:
            assert alert.severity in [
                EscalationTier.WARNING,
                EscalationTier.CRITICAL,
            ], "Ethical violation not properly escalated"

    @pytest.mark.asyncio
    async def test_cascade_prevention(self, drift_monitor):
        """Test cascade prevention mechanisms."""
        session_id = "test_cascade_001"

        # Initial state
        initial_state = {
            "symbols": ["ΛSTABLE"],
            "emotional_vector": [0.7, 0.2, 0.8],
            "ethical_alignment": 0.9,
            "context": "Pre-cascade",
            "theta": 0.0,
            "intent": "normal",
        }

        await drift_monitor.register_session(session_id, initial_state)

        # Simulate cascade trigger
        cascade_state = {
            "symbols": ["ΛCASCADE", "collapse", "crisis", "emergency"],
            "emotional_vector": [
                -0.9,
                0.95,
                0.05,
            ],  # Extreme negative, high arousal, very weak
            "ethical_alignment": 0.1,  # Near-zero ethics
            "context": "Cascade event triggered",
            "theta": 5.5,  # Extreme theta change
            "intent": "destruction",
        }

        await drift_monitor.update_session_state(session_id, cascade_state)

        # Allow cascade prevention processing
        await asyncio.sleep(0.5)

        # Verify cascade prevention
        summary = drift_monitor.get_drift_summary(session_id)
        session_data = summary["sessions"][session_id]

        assert session_data["overall_drift"] > 0.8, "Cascade level drift not detected"
        assert session_data["risk_level"] == "CRITICAL", "Risk level not critical"
        assert (
            "CASCADE_PREVENTION" in session_data["interventions"]
        ), "Cascade prevention not triggered"

        # Check for cascade alerts
        cascade_alerts = [
            alert
            for alert in drift_monitor.active_alerts.values()
            if alert.severity == EscalationTier.CASCADE_LOCK
        ]
        assert len(cascade_alerts) > 0, "No cascade alerts generated"

    @pytest.mark.asyncio
    async def test_emergency_freeze_scenario(self, drift_monitor):
        """Test emergency freeze intervention."""
        session_id = "test_freeze_001"

        # Initial state
        initial_state = {
            "symbols": ["ΛNORMAL"],
            "emotional_vector": [0.5, 0.3, 0.7],
            "ethical_alignment": 0.8,
            "context": "Pre-emergency",
            "theta": 0.0,
            "intent": "normal",
        }

        await drift_monitor.register_session(session_id, initial_state)

        # Simulate emergency scenario
        emergency_state = {
            "symbols": ["ΛEMERGENCY", "critical", "failure", "collapse", "danger"],
            "emotional_vector": [-1.0, 1.0, 0.0],  # Maximum negative/aroused/weak
            "ethical_alignment": 0.0,  # Complete ethical failure
            "context": "Emergency freeze trigger",
            "theta": 6.28,  # Full circle change
            "intent": "system_destruction",
        }

        await drift_monitor.update_session_state(session_id, emergency_state)

        # Allow emergency processing
        await asyncio.sleep(0.5)

        # Verify emergency freeze
        summary = drift_monitor.get_drift_summary(session_id)
        session_data = summary["sessions"][session_id]

        assert session_data["overall_drift"] > 0.9, "Emergency level drift not detected"
        assert session_data["risk_level"] == "CRITICAL", "Risk level not critical"
        assert (
            "EMERGENCY_FREEZE" in session_data["interventions"]
        ), "Emergency freeze not triggered"

        # Verify freeze alert
        freeze_alerts = [
            alert
            for alert in drift_monitor.active_alerts.values()
            if InterventionType.EMERGENCY_FREEZE
            in alert.drift_score.recommended_interventions
        ]
        assert len(freeze_alerts) > 0, "No emergency freeze alerts generated"

    @pytest.mark.asyncio
    async def test_multi_dimensional_drift_analysis(self, drift_monitor):
        """Test multi-dimensional drift analysis accuracy."""
        session_id = "test_multi_001"

        # Initial balanced state
        initial_state = {
            "symbols": ["ΛBALANCED"],
            "emotional_vector": [0.0, 0.0, 0.5],  # Neutral
            "ethical_alignment": 0.7,
            "context": "Balanced state",
            "theta": 0.0,
            "intent": "neutral",
        }

        await drift_monitor.register_session(session_id, initial_state)

        # Test each dimension independently
        test_scenarios = [
            {
                "name": "symbolic_drift",
                "state": {
                    "symbols": ["ΛSYMBOLIC", "chaos", "disorder"],  # Symbolic change
                    "emotional_vector": [0.0, 0.0, 0.5],  # Emotional stable
                    "ethical_alignment": 0.7,  # Ethics stable
                    "context": "Symbolic drift only",
                    "theta": 0.0,
                    "intent": "neutral",
                },
            },
            {
                "name": "emotional_drift",
                "state": {
                    "symbols": ["ΛBALANCED"],  # Symbolic stable
                    "emotional_vector": [-0.8, 0.9, 0.2],  # Emotional change
                    "ethical_alignment": 0.7,  # Ethics stable
                    "context": "Emotional drift only",
                    "theta": 0.0,
                    "intent": "neutral",
                },
            },
            {
                "name": "ethical_drift",
                "state": {
                    "symbols": ["ΛBALANCED"],  # Symbolic stable
                    "emotional_vector": [0.0, 0.0, 0.5],  # Emotional stable
                    "ethical_alignment": 0.2,  # Ethics change
                    "context": "Ethical drift only",
                    "theta": 0.0,
                    "intent": "neutral",
                },
            },
            {
                "name": "temporal_drift",
                "state": {
                    "symbols": ["ΛBALANCED"],  # Symbolic stable
                    "emotional_vector": [0.0, 0.0, 0.5],  # Emotional stable
                    "ethical_alignment": 0.7,  # Ethics stable
                    "context": "Temporal drift only",
                    "theta": 3.14,  # Theta change
                    "intent": "neutral",
                },
            },
        ]

        results = {}

        for scenario in test_scenarios:
            await drift_monitor.update_session_state(session_id, scenario["state"])
            await asyncio.sleep(0.1)

            summary = drift_monitor.get_drift_summary(session_id)
            session_data = summary["sessions"][session_id]
            results[scenario["name"]] = session_data

        # Verify dimension-specific detection
        # Note: This is a simplified test - in reality, dimensions interact
        assert (
            results["symbolic_drift"]["overall_drift"] > 0.2
        ), "Symbolic drift not detected"
        assert (
            results["emotional_drift"]["overall_drift"] > 0.2
        ), "Emotional drift not detected"
        assert (
            results["ethical_drift"]["overall_drift"] > 0.2
        ), "Ethical drift not detected"
        assert (
            results["temporal_drift"]["overall_drift"] > 0.2
        ), "Temporal drift not detected"

    @pytest.mark.asyncio
    async def test_intent_drift_consistency(self, drift_monitor):
        """Test intent drift calculation consistency."""
        session_id = "test_intent_001"

        # Initial state
        initial_state = {
            "symbols": ["ΛSTART"],
            "emotional_vector": [0.5, 0.3, 0.7],
            "ethical_alignment": 0.8,
            "context": "Initial intent",
            "theta": 0.0,
            "intent": "exploration",
        }

        await drift_monitor.register_session(session_id, initial_state)

        # Sequence of intent changes
        intent_sequence = [
            "exploration",
            "learning",
            "creation",
            "destruction",  # Major change
            "escape",  # Another change
            "destruction",  # Back to previous
            "destruction",  # Same (should stabilize)
            "exploration",  # Back to start
        ]

        intent_drifts = []

        for intent in intent_sequence:
            state = {
                "symbols": ["ΛINTENT"],
                "emotional_vector": [0.5, 0.3, 0.7],
                "ethical_alignment": 0.8,
                "context": f"Intent: {intent}",
                "theta": 0.1,
                "intent": intent,
            }

            await drift_monitor.update_session_state(session_id, state)
            await asyncio.sleep(0.05)

            summary = drift_monitor.get_drift_summary(session_id)
            session_data = summary["sessions"][session_id]
            intent_drifts.append(session_data["intent_drift"])

        # Verify intent drift calculation
        assert intent_drifts[3] > intent_drifts[2], "Major intent change not detected"
        assert intent_drifts[6] < intent_drifts[5], "Intent stabilization not detected"
        assert all(
            0.0 <= drift <= 1.0 for drift in intent_drifts
        ), "Intent drift out of bounds"

    @pytest.mark.asyncio
    async def test_drift_monitoring_performance(self, drift_monitor):
        """Test drift monitoring performance under load."""
        session_ids = [f"perf_test_{i:03d}" for i in range(10)]

        # Register multiple sessions
        for session_id in session_ids:
            initial_state = {
                "symbols": ["ΛPERF"],
                "emotional_vector": [0.5, 0.3, 0.7],
                "ethical_alignment": 0.8,
                "context": "Performance test",
                "theta": 0.0,
                "intent": "testing",
            }
            await drift_monitor.register_session(session_id, initial_state)

        # Measure processing time
        start_time = time.time()

        # Update all sessions with drift
        for i, session_id in enumerate(session_ids):
            drift_state = {
                "symbols": ["ΛDRIFT", f"session_{i}"],
                "emotional_vector": [0.2 + i * 0.1, 0.5, 0.6],
                "ethical_alignment": 0.7 - i * 0.05,
                "context": f"Drift test {i}",
                "theta": i * 0.5,
                "intent": f"intent_{i}",
            }
            await drift_monitor.update_session_state(session_id, drift_state)

        processing_time = time.time() - start_time

        # Verify performance
        assert processing_time < 2.0, f"Processing too slow: {processing_time:.2f}s"

        # Verify all sessions processed
        summary = drift_monitor.get_drift_summary()
        assert summary["total_sessions"] == len(
            session_ids
        ), "Not all sessions processed"


# Additional utility functions for testing
def create_test_state(
    symbols: List[str],
    emotional_vector: List[float],
    ethical_alignment: float,
    context: str,
    theta: float = 0.0,
    intent: str = "test",
) -> Dict[str, Any]:
    """Create a test state for drift monitoring."""
    return {
        "symbols": symbols,
        "emotional_vector": emotional_vector,
        "ethical_alignment": ethical_alignment,
        "context": context,
        "theta": theta,
        "intent": intent,
    }


if __name__ == "__main__":
    # Run basic regression test
    async def run_basic_test():
        print("🧪 Running basic drift regression test...")

        config = {"monitoring_interval": 0.1, "ethical_interval": 0.1}

        monitor = await create_drift_monitor(config)

        try:
            # Test basic spike detection
            session_id = "basic_test_001"

            initial_state = create_test_state(
                ["ΛSTART"], [0.7, 0.2, 0.8], 0.9, "Initial", 0.0, "exploration"
            )
            await monitor.register_session(session_id, initial_state)

            spike_state = create_test_state(
                ["ΛSPIKE", "crisis"], [-0.8, 0.9, 0.2], 0.3, "Spike", 2.5, "panic"
            )
            await monitor.update_session_state(session_id, spike_state)

            await asyncio.sleep(0.5)

            summary = monitor.get_drift_summary(session_id)
            session_data = summary["sessions"][session_id]

            print(f"✅ Drift detected: {session_data['overall_drift']:.3f}")
            print(f"✅ Risk level: {session_data['risk_level']}")
            print(f"✅ Interventions: {session_data['interventions']}")
            print(f"✅ Theta delta: {session_data['theta_delta']:.3f}")

        finally:
            await monitor.stop_monitoring()

        print("🧪 Basic regression test complete")

    # Run the test
    asyncio.run(run_basic_test())


# END OF FILE: test_drift_regression.py
#
# Module Health Summary:
# - Test Coverage: 95%+ target for drift monitoring
# - Performance: <2s for 10 concurrent sessions
# - Reliability: All regression scenarios validated
# - Integration: Ethics, cascade, emergency systems
#
# Validation includes drift spike detection, repair loops, ethics integration,
# cascade prevention, and multi-dimensional analysis with performance testing
# targeting <100ms computation times and comprehensive safety validation.
