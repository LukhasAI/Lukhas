import time
from trace.drift_metrics import DriftTracker


def test_real_time_drift_monitoring():
    # Setup
    tracker = DriftTracker()
    initial_state = {"value": 10.0}
    tracker.track(initial_state)

    # Action
    time.sleep(0.1)
    new_state = {"value": 15.0}
    tracker.track(new_state)
    drift = tracker.get_drift()

    # Assert
    assert drift > 0

    # Action
    time.sleep(0.1)
    new_state = {"value": 15.0}
    tracker.track(new_state)
    drift = tracker.get_drift()

    # Assert
    assert drift == 0
