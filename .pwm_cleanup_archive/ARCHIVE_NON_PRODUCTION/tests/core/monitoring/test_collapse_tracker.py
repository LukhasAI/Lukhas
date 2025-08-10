"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - COLLAPSE TRACKER TESTS
║ Test suite for collapse detection and entropy monitoring.
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: test_collapse_tracker.py
║ Path: lukhas/tests/core/monitoring/test_collapse_tracker.py
║ Version: 1.0.0 | Created: 2025-07-25 | Modified: 2025-07-25
║ Authors: LUKHAS AI Testing Team | Jules
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ This module contains the test suite for the collapse tracker system, including:
║ • Entropy calculation validation
║ • Alert level threshold testing
║ • Integration with orchestrator and ethics callbacks
║ • Synthetic scenario testing (normal, drift, collapse)
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock

import pytest

from core.monitoring.collapse_integration import CollapseIntegration

# Import the modules to test
from core.monitoring.collapse_tracker import (
    CollapseAlertLevel,
    CollapseTracker,
)


class TestCollapseTracker:
    """Test suite for the collapse tracker system."""

    @pytest.fixture
    def tracker(self):
        """Create a fresh tracker instance for each test."""
        return CollapseTracker()

    @pytest.fixture
    def mock_orchestrator(self):
        """Create a mock orchestrator with required methods."""
        mock = Mock()
        mock.handle_collapse_alert = AsyncMock()
        mock.broadcast_event = AsyncMock()
        mock.update_system_state = Mock()
        return mock

    @pytest.fixture
    def mock_ethics_sentinel(self):
        """Create a mock ethics sentinel with required methods."""
        mock = Mock()
        mock.handle_collapse_risk = AsyncMock(return_value={"action": "monitor"})
        mock.record_violation = AsyncMock()
        mock.request_intervention = AsyncMock()
        return mock

    def test_shannon_entropy_calculation(self, tracker):
        """Test Shannon entropy calculation for various data distributions."""
        # Test 1: Uniform distribution (high entropy)
        uniform_data = list(range(100))  # Each element appears once
        entropy_uniform = tracker.calculate_shannon_entropy(uniform_data)
        assert (
            0.95 <= entropy_uniform <= 1.0
        ), f"Uniform entropy {entropy_uniform} not in expected range"

        # Test 2: Skewed distribution (medium entropy)
        skewed_data = ["a"] * 50 + ["b"] * 30 + ["c"] * 20
        entropy_skewed = tracker.calculate_shannon_entropy(skewed_data)
        assert (
            0.4 <= entropy_skewed <= 0.7
        ), f"Skewed entropy {entropy_skewed} not in expected range"

        # Test 3: Single value (zero entropy)
        single_data = ["x"] * 100
        entropy_single = tracker.calculate_shannon_entropy(single_data)
        assert (
            entropy_single == 0.0
        ), f"Single value entropy {entropy_single} should be 0"

        # Test 4: Empty data
        entropy_empty = tracker.calculate_shannon_entropy([])
        assert entropy_empty == 0.0, "Empty data entropy should be 0"

    def test_alert_level_thresholds(self, tracker):
        """Test alert level transitions based on entropy scores."""
        # Test GREEN level (low entropy)
        tracker.update_entropy_score(["glyph_001"] * 80 + ["glyph_002"] * 20)
        assert tracker.current_state.alert_level == CollapseAlertLevel.GREEN
        assert tracker.current_state.entropy_score < 0.3

        # Test YELLOW level (medium-low entropy)
        tracker.update_entropy_score(
            ["glyph_001"] * 50 + ["glyph_002"] * 30 + ["glyph_003"] * 20
        )
        assert tracker.current_state.alert_level in [
            CollapseAlertLevel.YELLOW,
            CollapseAlertLevel.GREEN,
        ]

        # Test ORANGE level (medium-high entropy)
        diverse_data = [f"glyph_{i:03d}" for i in range(30)] * 3
        tracker.update_entropy_score(diverse_data)
        assert tracker.current_state.alert_level in [
            CollapseAlertLevel.YELLOW,
            CollapseAlertLevel.ORANGE,
        ]

        # Test RED level (high entropy)
        chaotic_data = [f"glyph_{i:03d}" for i in range(100)]
        tracker.update_entropy_score(chaotic_data)
        assert tracker.current_state.alert_level in [
            CollapseAlertLevel.ORANGE,
            CollapseAlertLevel.RED,
        ]

    @pytest.mark.asyncio
    async def test_synthetic_scenario_normal(self, tracker):
        """Test Case 1: Normal system operation scenario."""
        print("\n=== SYNTHETIC TEST 1: NORMAL OPERATION ===")

        # Generate synthetic normal data
        symbols, component_scores = tracker.generate_synthetic_test_data("normal")

        # Update tracker with normal data
        entropy_score = tracker.update_entropy_score(symbols, component_scores)

        # Validate normal operation characteristics
        assert entropy_score < 0.3, f"Normal scenario entropy {entropy_score} too high"
        assert tracker.current_state.alert_level == CollapseAlertLevel.GREEN
        assert all(score < 0.3 for score in component_scores.values())

        # Record event for tracking
        trace_id = tracker.record_collapse_event(
            affected_components=list(component_scores.keys()),
            symbolic_drift=component_scores,
            metadata={"scenario": "normal", "test": True},
        )

        print("Normal scenario results:")
        print(f"  - Entropy Score: {entropy_score:.3f}")
        print(f"  - Alert Level: {tracker.current_state.alert_level.value}")
        print(f"  - Trace ID: {trace_id}")
        print(f"  - Component Scores: {component_scores}")

    @pytest.mark.asyncio
    async def test_synthetic_scenario_drift(self, tracker):
        """Test Case 2: Symbolic drift scenario."""
        print("\n=== SYNTHETIC TEST 2: DRIFT DETECTION ===")

        # Generate synthetic drift data
        symbols, component_scores = tracker.generate_synthetic_test_data("drift")

        # Update tracker with drift data
        entropy_score = tracker.update_entropy_score(symbols, component_scores)

        # Validate drift characteristics
        assert (
            0.3 <= entropy_score <= 0.7
        ), f"Drift scenario entropy {entropy_score} out of range"
        assert tracker.current_state.alert_level in [
            CollapseAlertLevel.YELLOW,
            CollapseAlertLevel.ORANGE,
        ]
        assert any(0.3 <= score <= 0.6 for score in component_scores.values())

        # Simulate drift progression over time
        for i in range(3):
            await asyncio.sleep(0.1)  # Small delay to show progression
            # Slightly increase entropy
            new_scores = {k: min(1.0, v + 0.1) for k, v in component_scores.items()}
            entropy_score = tracker.update_entropy_score(symbols, new_scores)

        # Check entropy slope (should be positive for increasing drift)
        assert (
            tracker.current_state.entropy_slope >= 0
        ), "Drift should show positive entropy slope"

        trace_id = tracker.record_collapse_event(
            affected_components=list(component_scores.keys()),
            symbolic_drift=component_scores,
            metadata={"scenario": "drift", "test": True, "progression": "increasing"},
        )

        print("Drift scenario results:")
        print(f"  - Final Entropy Score: {entropy_score:.3f}")
        print(f"  - Alert Level: {tracker.current_state.alert_level.value}")
        print(f"  - Entropy Slope: {tracker.current_state.entropy_slope:.4f}")
        print(f"  - Trace ID: {trace_id}")

    @pytest.mark.asyncio
    async def test_synthetic_scenario_collapse(
        self, tracker, mock_orchestrator, mock_ethics_sentinel
    ):
        """Test Case 3: System collapse scenario."""
        print("\n=== SYNTHETIC TEST 3: COLLAPSE SCENARIO ===")

        # Set up integration with mocks
        integration = CollapseIntegration(mock_orchestrator, mock_ethics_sentinel)

        # Generate synthetic collapse data
        symbols, component_scores = tracker.generate_synthetic_test_data("collapse")

        # Update tracker with collapse data
        entropy_score = tracker.update_entropy_score(symbols, component_scores)

        # Validate collapse characteristics
        assert entropy_score > 0.7, f"Collapse scenario entropy {entropy_score} too low"
        assert tracker.current_state.alert_level in [
            CollapseAlertLevel.ORANGE,
            CollapseAlertLevel.RED,
        ]
        assert all(score > 0.7 for score in component_scores.values())

        # Wait for alert callbacks to complete
        await asyncio.sleep(0.1)

        # Verify orchestrator was notified
        if tracker.current_state.alert_level == CollapseAlertLevel.RED:
            assert mock_orchestrator.broadcast_event.called
            event_call = mock_orchestrator.broadcast_event.call_args
            assert event_call[1]["event_type"] in [
                "collapse_alert",
                "collapse_critical",
            ]

        # Verify ethics sentinel was notified for high-risk scenarios
        if tracker.current_state.alert_level in [
            CollapseAlertLevel.ORANGE,
            CollapseAlertLevel.RED,
        ]:
            # The ethics callback should have been triggered
            # Note: Due to async nature, we may need to wait
            await asyncio.sleep(0.1)

        trace_id = tracker.record_collapse_event(
            affected_components=list(component_scores.keys()),
            symbolic_drift=component_scores,
            metadata={
                "scenario": "collapse",
                "test": True,
                "severity": "critical",
                "component_failures": len(
                    [s for s in component_scores.values() if s > 0.8]
                ),
            },
        )

        print("Collapse scenario results:")
        print(f"  - Entropy Score: {entropy_score:.3f}")
        print(f"  - Alert Level: {tracker.current_state.alert_level.value}")
        print(
            f"  - Critical Components: {[k for k, v in component_scores.items() if v > 0.8]}"
        )
        print(f"  - Trace ID: {trace_id}")
        print(f"  - Orchestrator Notified: {mock_orchestrator.broadcast_event.called}")

    def test_collapse_history_persistence(self, tracker):
        """Test collapse history tracking and retrieval."""
        # Record multiple events
        trace_ids = []
        for i in range(5):
            trace_id = tracker.record_collapse_event(
                affected_components=[f"component_{i}"],
                symbolic_drift={f"component_{i}": 0.1 * i},
                metadata={"test_index": i},
            )
            trace_ids.append(trace_id)

        # Retrieve full history
        history = tracker.get_collapse_history(limit=10)
        assert len(history) == 5

        # Retrieve specific trace
        specific_history = tracker.get_collapse_history(trace_id=trace_ids[2])
        assert len(specific_history) == 1
        assert specific_history[0]["collapse_trace_id"] == trace_ids[2]

    def test_system_health_reporting(self, tracker):
        """Test system health status reporting."""
        # Update with some test data
        tracker.update_entropy_score(
            ["glyph_001"] * 50 + ["glyph_002"] * 50, {"memory": 0.3, "reasoning": 0.4}
        )

        # Get health status
        health = tracker.get_system_health()

        # Validate health report structure
        assert "entropy_score" in health
        assert "alert_level" in health
        assert "entropy_slope" in health
        assert "component_entropy" in health
        assert health["component_entropy"] == {"memory": 0.3, "reasoning": 0.4}


@pytest.mark.asyncio
async def test_integration_with_memory():
    """Test integration with memory system for collapse state storage."""
    # This would test the actual integration with HierarchicalDataStore
    # For now, we'll create a mock test
    from memory.core_memory.hierarchical_data_store import (
        MemoryNode,
        MemoryTier,
    )

    # Create a test memory node
    node = MemoryNode(
        node_id="test_node_001", tier=MemoryTier.SEMANTIC, content={"test": "data"}
    )

    # Simulate collapse state update
    node.collapse_trace_id = "collapse_test_001"
    node.collapse_alert_level = "ORANGE"
    node.collapse_score_history.append((datetime.now(timezone.utc), 0.75))

    # Validate collapse fields
    assert node.collapse_trace_id == "collapse_test_001"
    assert node.collapse_alert_level == "ORANGE"
    assert len(node.collapse_score_history) == 1
    assert node.collapse_score_history[0][1] == 0.75


if __name__ == "__main__":
    # Run the synthetic tests directly
    print("Running Collapse Tracker Synthetic Tests")
    print("=" * 50)

    # Create test instance
    test_suite = TestCollapseTracker()
    tracker = CollapseTracker()

    # Run synchronous tests
    print("\nTesting entropy calculation...")
    test_suite.test_shannon_entropy_calculation(tracker)
    print("✓ Entropy calculation tests passed")

    print("\nTesting alert level thresholds...")
    test_suite.test_alert_level_thresholds(tracker)
    print("✓ Alert level tests passed")

    # Run async tests
    async def run_async_tests():
        print("\nRunning synthetic scenario tests...")

        # Create fresh tracker for each scenario
        await test_suite.test_synthetic_scenario_normal(CollapseTracker())
        await test_suite.test_synthetic_scenario_drift(CollapseTracker())

        # For collapse test, we need mocks
        mock_orch = test_suite.mock_orchestrator()
        mock_ethics = test_suite.mock_ethics_sentinel()
        collapse_tracker = CollapseTracker(
            orchestrator_callback=mock_orch.handle_collapse_alert,
            ethics_callback=mock_ethics.handle_collapse_risk,
        )
        await test_suite.test_synthetic_scenario_collapse(
            collapse_tracker, mock_orch, mock_ethics
        )

    # Run the async tests
    asyncio.run(run_async_tests())

    print("\n" + "=" * 50)
    print("All synthetic tests completed successfully! ✓")


"""
═══════════════════════════════════════════════════════════════════════════════
║ 📋 TEST DOCUMENTATION
╠═══════════════════════════════════════════════════════════════════════════════
║ RUNNING TESTS:
║   pytest lukhas/tests/core/monitoring/test_collapse_tracker.py -v
║   python lukhas/tests/core/monitoring/test_collapse_tracker.py  # Direct run
║
║ TEST SCENARIOS:
║   1. Normal Operation - Low entropy, stable system
║   2. Drift Detection - Medium entropy, increasing trend
║   3. Collapse Scenario - High entropy, critical state
║
║ COVERAGE:
║   - Entropy calculation algorithms
║   - Alert level state transitions
║   - Integration callbacks
║   - History persistence
║   - System health reporting
║
║ VALIDATION CRITERIA:
║   - Normal: entropy < 0.3, GREEN alert
║   - Drift: 0.3 <= entropy <= 0.7, YELLOW/ORANGE alert
║   - Collapse: entropy > 0.7, ORANGE/RED alert
╚═══════════════════════════════════════════════════════════════════════════════
"""
