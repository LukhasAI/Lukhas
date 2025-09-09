import os
import shutil
from unittest.mock import MagicMock

import pytest

from candidate.governance.compliance_drift_monitor import ComplianceMonitor


@pytest.fixture
def monitor():
    """Fixture to create a ComplianceMonitor instance for testing."""
    log_dir = "test_compliance_logs"
    if os.path.exists(log_dir):
        shutil.rmtree(log_dir)
    monitor = ComplianceMonitor(log_dir=log_dir, moving_average_window=5)
    monitor.recalibrate = MagicMock()
    monitor.escalate_to_human = MagicMock()
    yield monitor
    shutil.rmtree(log_dir)


def test_initial_drift_score_is_zero(monitor: ComplianceMonitor):
    """Test that the initial drift score is 0."""
    assert monitor.drift_score == 0.0


def test_no_drift_with_stable_high_compliance(monitor: ComplianceMonitor):
    """Test that the drift score remains low with stable high compliance."""
    for i in range(10):
        monitor.evaluate_decision(f"D{i}", 0.95)

    assert monitor.drift_score < 0.1
    monitor.recalibrate.assert_not_called()
    monitor.escalate_to_human.assert_not_called()


def test_drift_detection_with_sudden_drop(monitor: ComplianceMonitor):
    """Test that a sudden drop in compliance is detected."""
    for i in range(5):
        monitor.evaluate_decision(f"D{i}", 0.95)

    initial_drift_score = monitor.drift_score

    monitor.evaluate_decision("D6", 0.5)

    assert monitor.drift_score > initial_drift_score
    assert monitor.drift_score > 0.05


def test_recalibration_is_triggered(monitor: ComplianceMonitor):
    """Test that recalibration is triggered when drift exceeds threshold."""
    # Establish a high compliance baseline
    for i in range(5):
        monitor.evaluate_decision(f"D{i}", 0.95)

    # Introduce drift
    for i in range(5, 10):
        monitor.evaluate_decision(f"D{i}", 0.7)

    monitor.recalibrate.assert_called()
    monitor.escalate_to_human.assert_not_called()


def test_escalation_is_triggered(monitor: ComplianceMonitor):
    """Test that escalation is triggered when drift exceeds critical threshold."""
    # Establish a high compliance baseline
    for i in range(5):
        monitor.evaluate_decision(f"D{i}", 0.95)

    # Introduce severe drift
    for i in range(5, 15):
        monitor.evaluate_decision(f"D{i}", 0.5)

    monitor.escalate_to_human.assert_called()


def test_compliance_history_is_maintained(monitor: ComplianceMonitor):
    """Test that the compliance history window is maintained."""
    for i in range(10):
        monitor.evaluate_decision(f"D{i}", 0.9)

    assert len(monitor.compliance_history) == monitor.moving_average_window
    assert len(monitor.compliance_history) == 5