"""
Comprehensive tests for Guardian Emergency Kill-Switch
=======================================================

Tests the ultimate safety backstop for LUKHAS consciousness platform.
Ensures emergency shutdown works correctly under all trigger conditions.
"""

import pytest
from pathlib import Path
import tempfile
import time
import json
from lukhas.governance.emergency_disable import GuardianEmergencyKillSwitch, EmergencySnapshot


class TestEmergencyKillSwitch:
    """Comprehensive tests for Guardian emergency system"""

    @pytest.fixture
    def temp_emergency_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir) / "emergency_disable"

    @pytest.fixture
    def temp_log_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir) / "emergency_logs"

    @pytest.fixture
    def kill_switch(self, temp_emergency_path, temp_log_dir):
        return GuardianEmergencyKillSwitch(
            emergency_path=str(temp_emergency_path),
            log_dir=str(temp_log_dir)
        )

    def test_initial_state_active(self, kill_switch):
        """Guardian should be active initially"""
        assert kill_switch.allow_decision() == True
        assert kill_switch.disabled == False

    def test_catastrophic_drift_triggers_shutdown(self, kill_switch):
        """Drift > threshold triggers emergency shutdown"""
        # Prod lane: threshold 0.25
        activated = kill_switch.check_emergency_triggers(
            drift_ema=0.30,  # Exceeds 0.25
            lane="prod"
        )

        assert activated == True
        assert kill_switch.allow_decision() == False
        assert kill_switch.snapshot is not None
        assert kill_switch.snapshot.reason == "catastrophic_drift"

    def test_systematic_violations_trigger_shutdown(self, kill_switch):
        """Multiple violations in window trigger shutdown"""
        activated = kill_switch.check_emergency_triggers(
            drift_ema=0.10,  # Low drift
            lane="prod",
            recent_violations=6  # Exceeds 5
        )

        assert activated == True
        assert kill_switch.snapshot.reason == "systematic_violations"

    def test_file_based_trigger(self, kill_switch, temp_emergency_path):
        """Creating emergency file triggers shutdown"""
        # Create emergency file
        temp_emergency_path.write_text("EMERGENCY: Manual override")

        activated = kill_switch.check_emergency_triggers(
            drift_ema=0.10,
            lane="prod"
        )

        assert activated == True
        assert kill_switch.snapshot.trigger_source == "filesystem"

    def test_forensic_snapshot_captured(self, kill_switch):
        """Emergency activation captures full forensic snapshot"""
        # Record some decisions
        kill_switch.record_decision({"id": 1, "action": "allow"})
        kill_switch.record_decision({"id": 2, "action": "veto"})

        kill_switch.check_emergency_triggers(
            drift_ema=0.30,
            lane="prod"
        )

        snapshot = kill_switch.snapshot
        assert snapshot.drift_ema == 0.30
        assert snapshot.lane == "prod"
        assert snapshot.last_decision["id"] == 2
        assert snapshot.system_state["decision_buffer_size"] == 2

    def test_no_false_positives(self, kill_switch):
        """Normal operation doesn't trigger shutdown"""
        # All safe values
        activated = kill_switch.check_emergency_triggers(
            drift_ema=0.10,  # Below threshold
            lane="prod",
            recent_violations=2  # Below 5
        )

        assert activated == False
        assert kill_switch.allow_decision() == True

    def test_per_lane_thresholds(self, temp_emergency_path, temp_log_dir):
        """Different lanes have different thresholds"""
        # Prod: 0.25
        kill_switch1 = GuardianEmergencyKillSwitch(
            emergency_path=str(temp_emergency_path / "ks1"),
            log_dir=str(temp_log_dir / "ks1")
        )
        assert kill_switch1.check_emergency_triggers(0.26, "prod") == True

        # Candidate: 0.35
        kill_switch2 = GuardianEmergencyKillSwitch(
            emergency_path=str(temp_emergency_path / "ks2"),
            log_dir=str(temp_log_dir / "ks2")
        )
        assert kill_switch2.check_emergency_triggers(0.36, "candidate") == True

        # Experimental: 0.50
        kill_switch3 = GuardianEmergencyKillSwitch(
            emergency_path=str(temp_emergency_path / "ks3"),
            log_dir=str(temp_log_dir / "ks3")
        )
        assert kill_switch3.check_emergency_triggers(0.51, "experimental") == True

    def test_decision_buffer_bounded(self, kill_switch):
        """Decision buffer maintains only last 100 decisions"""
        # Record 150 decisions
        for i in range(150):
            kill_switch.record_decision({"id": i})

        assert len(kill_switch._decision_buffer) == 100
        assert kill_switch._decision_buffer[0]["id"] == 50  # Oldest kept
        assert kill_switch._decision_buffer[-1]["id"] == 149  # Newest

    def test_violation_window_cleanup(self, kill_switch):
        """Violation window only keeps recent (<10s) violations"""
        # Record violation
        kill_switch.record_violation({"type": "constraint_breach"})
        assert len(kill_switch._violation_window) == 1

        # Mock old timestamp (>10s ago)
        kill_switch._violation_window[0]["timestamp"] = time.time() - 11

        # Record new violation (triggers cleanup)
        kill_switch.record_violation({"type": "new_breach"})

        # Old violation should be cleaned
        assert len(kill_switch._violation_window) == 1
        assert kill_switch._violation_window[0]["violation"]["type"] == "new_breach"

    def test_emergency_file_created_on_activation(self, kill_switch, temp_emergency_path):
        """Emergency file created with details on activation"""
        kill_switch.check_emergency_triggers(drift_ema=0.30, lane="prod")

        assert temp_emergency_path.exists()
        content = temp_emergency_path.read_text()
        assert "catastrophic_drift" in content
        assert "0.3" in content
        assert "prod" in content

    def test_snapshot_written_to_log_dir(self, kill_switch):
        """Forensic snapshot written to configured log directory"""
        kill_switch.record_decision({"id": 1, "action": "test"})
        kill_switch.check_emergency_triggers(drift_ema=0.30, lane="prod")

        # Check snapshot was created in configured log_dir
        snapshots = list(kill_switch.log_dir.glob("snapshot_*.json"))
        assert len(snapshots) > 0

        # Verify snapshot content
        snapshot_data = json.loads(snapshots[-1].read_text())
        assert snapshot_data["reason"] == "catastrophic_drift"
        assert snapshot_data["drift_ema"] == 0.30
        assert snapshot_data["lane"] == "prod"

    def test_already_activated_returns_true(self, kill_switch):
        """Subsequent checks return True if already activated"""
        # First activation
        kill_switch.check_emergency_triggers(drift_ema=0.30, lane="prod")
        assert kill_switch.disabled == True

        # Second check should immediately return True
        result = kill_switch.check_emergency_triggers(drift_ema=0.10, lane="prod")
        assert result == True

    def test_activation_from_existing_file(self, temp_emergency_path, temp_log_dir):
        """Kill-switch activates if emergency file already exists"""
        # Create emergency file before init
        temp_emergency_path.parent.mkdir(parents=True, exist_ok=True)
        temp_emergency_path.write_text("EMERGENCY: Pre-existing shutdown")

        # Create kill-switch (should activate from file)
        kill_switch = GuardianEmergencyKillSwitch(
            emergency_path=str(temp_emergency_path),
            log_dir=str(temp_log_dir)
        )

        assert kill_switch.disabled == True
        assert kill_switch.allow_decision() == False

    def test_record_decision_preserves_last_100(self, kill_switch):
        """Decision recording maintains circular buffer of 100"""
        for i in range(200):
            kill_switch.record_decision({"id": i, "timestamp": i})

        # Should have exactly 100
        assert len(kill_switch._decision_buffer) == 100
        # Should be decisions 100-199
        assert kill_switch._decision_buffer[0]["id"] == 100
        assert kill_switch._decision_buffer[-1]["id"] == 199

    def test_emergency_snapshot_dataclass(self):
        """EmergencySnapshot captures all required fields"""
        snapshot = EmergencySnapshot(
            timestamp=datetime.utcnow(),
            reason="test_reason",
            drift_ema=0.42,
            lane="test_lane",
            last_decision={"id": 123},
            system_state={"foo": "bar"},
            trigger_source="test"
        )

        assert snapshot.reason == "test_reason"
        assert snapshot.drift_ema == 0.42
        assert snapshot.lane == "test_lane"
        assert snapshot.last_decision["id"] == 123
        assert snapshot.system_state["foo"] == "bar"
        assert snapshot.trigger_source == "test"

    def test_lane_threshold_default_fallback(self, kill_switch):
        """Unknown lanes use default threshold (0.50)"""
        activated = kill_switch.check_emergency_triggers(
            drift_ema=0.51,
            lane="unknown_lane"
        )

        assert activated == True
        assert kill_switch.snapshot.reason == "catastrophic_drift"


# Import datetime for snapshot test
from datetime import datetime
