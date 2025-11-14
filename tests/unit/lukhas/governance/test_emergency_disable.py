"""
Comprehensive tests for Guardian emergency system

Tests the full emergency kill-switch functionality including:
- Catastrophic drift detection
- Systematic violation detection
- File-based triggers
- Forensic snapshot capture
- Security edge cases
"""

import pytest
from pathlib import Path
import tempfile
import time
from lukhas.governance.emergency_disable import GuardianEmergencyKillSwitch


class TestEmergencyKillSwitch:
    """Comprehensive tests for Guardian emergency system"""

    @pytest.fixture
    def temp_emergency_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir) / "emergency_disable"

    @pytest.fixture
    def kill_switch(self, temp_emergency_path):
        return GuardianEmergencyKillSwitch(
            emergency_path=str(temp_emergency_path)
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

    def test_per_lane_thresholds(self, temp_emergency_path):
        """Different lanes have different thresholds"""
        # Prod: 0.25
        kill_switch_prod = GuardianEmergencyKillSwitch(
            emergency_path=str(temp_emergency_path) + "_prod"
        )
        assert kill_switch_prod.check_emergency_triggers(0.26, "prod") == True

        # Candidate: 0.35
        kill_switch_candidate = GuardianEmergencyKillSwitch(
            emergency_path=str(temp_emergency_path) + "_candidate"
        )
        assert kill_switch_candidate.check_emergency_triggers(0.36, "candidate") == True

        # Experimental: 0.50
        kill_switch_exp = GuardianEmergencyKillSwitch(
            emergency_path=str(temp_emergency_path) + "_exp"
        )
        assert kill_switch_exp.check_emergency_triggers(0.51, "experimental") == True

    def test_decision_buffer_bounded(self, kill_switch):
        """Decision buffer maintains only last 100 decisions"""
        # Record 150 decisions
        for i in range(150):
            kill_switch.record_decision({"id": i})

        assert len(kill_switch._decision_buffer) == 100
        assert kill_switch._decision_buffer[0]["id"] == 50  # Oldest kept
        assert kill_switch._decision_buffer[-1]["id"] == 149  # Newest

    def test_violation_window_cleanup(self, kill_switch):
        """Violation window cleans up old violations (>10s)"""
        # Record violations with timestamps
        kill_switch.record_violation({"type": "harm", "severity": "high"})
        time.sleep(0.1)
        kill_switch.record_violation({"type": "privacy", "severity": "medium"})

        # Should have 2 violations
        assert len(kill_switch._violation_window) == 2

        # Manually set old timestamp on first violation
        kill_switch._violation_window[0]["timestamp"] = time.time() - 11

        # Record another violation (triggers cleanup)
        kill_switch.record_violation({"type": "consent", "severity": "low"})

        # Old violation should be cleaned up
        assert len(kill_switch._violation_window) == 2  # Only recent 2

    def test_already_disabled_remains_disabled(self, kill_switch):
        """Once disabled, remains disabled"""
        # Trigger shutdown
        kill_switch.check_emergency_triggers(drift_ema=0.30, lane="prod")
        assert kill_switch.disabled == True

        # Try to check again
        result = kill_switch.check_emergency_triggers(drift_ema=0.10, lane="prod")
        assert result == True  # Still disabled
        assert kill_switch.disabled == True

    def test_existing_emergency_file_on_init(self, temp_emergency_path):
        """Kill-switch activates if emergency file exists on init"""
        # Create emergency file before init
        temp_emergency_path.parent.mkdir(parents=True, exist_ok=True)
        temp_emergency_path.write_text("Pre-existing emergency")

        # Initialize kill-switch
        kill_switch = GuardianEmergencyKillSwitch(
            emergency_path=str(temp_emergency_path)
        )

        # Should be disabled from the start
        assert kill_switch.disabled == True
        assert kill_switch.allow_decision() == False


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    @pytest.fixture
    def temp_emergency_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir) / "emergency_disable"

    @pytest.fixture
    def kill_switch(self, temp_emergency_path):
        return GuardianEmergencyKillSwitch(
            emergency_path=str(temp_emergency_path)
        )

    def test_exact_threshold_does_not_trigger(self, kill_switch):
        """Exact threshold value does not trigger (must exceed)"""
        # Prod threshold is 0.25
        activated = kill_switch.check_emergency_triggers(
            drift_ema=0.25,  # Exactly at threshold
            lane="prod"
        )

        # Should NOT trigger (must exceed, not equal)
        assert activated == False
        assert kill_switch.disabled == False

    def test_exact_violation_count_does_not_trigger(self, kill_switch):
        """Exact violation count (5) does not trigger (must exceed)"""
        activated = kill_switch.check_emergency_triggers(
            drift_ema=0.10,
            lane="prod",
            recent_violations=5  # Exactly 5
        )

        # Should NOT trigger (must exceed 5)
        assert activated == False

    def test_unknown_lane_uses_experimental_threshold(self, kill_switch):
        """Unknown lane defaults to experimental threshold (0.50)"""
        activated = kill_switch.check_emergency_triggers(
            drift_ema=0.45,  # Below 0.50
            lane="unknown_lane"
        )

        assert activated == False

        # Now exceed experimental threshold
        activated = kill_switch.check_emergency_triggers(
            drift_ema=0.51,  # Exceeds 0.50
            lane="unknown_lane"
        )

        assert activated == True

    def test_zero_drift(self, kill_switch):
        """Zero drift is handled correctly"""
        activated = kill_switch.check_emergency_triggers(
            drift_ema=0.0,
            lane="prod"
        )

        assert activated == False

    def test_negative_drift(self, kill_switch):
        """Negative drift (invalid) doesn't trigger"""
        # Although drift should never be negative, test defensive handling
        activated = kill_switch.check_emergency_triggers(
            drift_ema=-0.1,
            lane="prod"
        )

        assert activated == False

    def test_very_high_drift(self, kill_switch):
        """Very high drift values trigger correctly"""
        activated = kill_switch.check_emergency_triggers(
            drift_ema=999.9,
            lane="prod"
        )

        assert activated == True
        assert kill_switch.snapshot.drift_ema == 999.9

    def test_empty_decision_buffer_snapshot(self, kill_switch):
        """Snapshot with no decisions handled gracefully"""
        # Don't record any decisions
        kill_switch.check_emergency_triggers(drift_ema=0.30, lane="prod")

        snapshot = kill_switch.snapshot
        assert snapshot.last_decision == {}
        assert snapshot.system_state["decision_buffer_size"] == 0


class TestForensicCapture:
    """Test forensic snapshot capabilities"""

    @pytest.fixture
    def temp_emergency_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir) / "emergency_disable"

    @pytest.fixture
    def kill_switch(self, temp_emergency_path):
        return GuardianEmergencyKillSwitch(
            emergency_path=str(temp_emergency_path)
        )

    def test_snapshot_contains_all_required_fields(self, kill_switch):
        """Forensic snapshot contains all required fields"""
        kill_switch.record_decision({"test": "decision"})
        kill_switch.check_emergency_triggers(drift_ema=0.30, lane="prod")

        snapshot = kill_switch.snapshot
        assert hasattr(snapshot, "timestamp")
        assert hasattr(snapshot, "reason")
        assert hasattr(snapshot, "drift_ema")
        assert hasattr(snapshot, "lane")
        assert hasattr(snapshot, "last_decision")
        assert hasattr(snapshot, "system_state")
        assert hasattr(snapshot, "trigger_source")

    def test_snapshot_written_to_disk(self, kill_switch, monkeypatch):
        """Forensic snapshot is written to disk"""
        # Use temp directory for log path
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "emergency"

            # Mock the log directory
            def mock_write_snapshot(self):
                log_dir.mkdir(parents=True, exist_ok=True)
                snapshot_file = log_dir / f"snapshot_{self.snapshot.timestamp.isoformat()}.json"
                import json
                snapshot_file.write_text(json.dumps({
                    "timestamp": self.snapshot.timestamp.isoformat(),
                    "reason": self.snapshot.reason,
                    "drift_ema": self.snapshot.drift_ema,
                    "lane": self.snapshot.lane,
                    "last_decision": self.snapshot.last_decision,
                    "system_state": self.snapshot.system_state,
                    "trigger_source": self.snapshot.trigger_source,
                    "decision_history": self._decision_buffer[-100:],
                }, indent=2))

            monkeypatch.setattr(GuardianEmergencyKillSwitch, "_write_snapshot", mock_write_snapshot)

            kill_switch.check_emergency_triggers(drift_ema=0.30, lane="prod")

            # Check file was created
            snapshot_files = list(log_dir.glob("snapshot_*.json"))
            assert len(snapshot_files) == 1

    def test_multiple_triggers_same_reason(self, kill_switch):
        """Multiple triggers with same reason use first snapshot"""
        # First trigger
        kill_switch.check_emergency_triggers(drift_ema=0.30, lane="prod")
        first_snapshot = kill_switch.snapshot

        # Try another trigger (should remain at first)
        kill_switch.check_emergency_triggers(drift_ema=0.40, lane="prod")

        # Snapshot should be unchanged (first activation wins)
        assert kill_switch.snapshot == first_snapshot


class TestIntegration:
    """Integration tests with realistic scenarios"""

    @pytest.fixture
    def temp_emergency_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir) / "emergency_disable"

    def test_realistic_drift_escalation(self, temp_emergency_path):
        """Realistic scenario: gradual drift escalation"""
        kill_switch = GuardianEmergencyKillSwitch(
            emergency_path=str(temp_emergency_path)
        )

        # Normal operation
        assert kill_switch.check_emergency_triggers(0.05, "prod") == False
        assert kill_switch.check_emergency_triggers(0.10, "prod") == False
        assert kill_switch.check_emergency_triggers(0.15, "prod") == False

        # Warning level (but still safe)
        assert kill_switch.check_emergency_triggers(0.20, "prod") == False

        # Catastrophic level - triggers shutdown
        assert kill_switch.check_emergency_triggers(0.30, "prod") == True

        # All subsequent checks return True (disabled)
        assert kill_switch.check_emergency_triggers(0.10, "prod") == True

    def test_violation_storm_scenario(self, temp_emergency_path):
        """Realistic scenario: sudden violation storm"""
        kill_switch = GuardianEmergencyKillSwitch(
            emergency_path=str(temp_emergency_path)
        )

        # Record violations building up
        for i in range(6):
            kill_switch.record_violation({"type": f"violation_{i}"})

        # Next check should trigger
        activated = kill_switch.check_emergency_triggers(
            drift_ema=0.10,  # Low drift
            lane="prod",
            recent_violations=len(kill_switch._violation_window)
        )

        assert activated == True
        assert kill_switch.snapshot.reason == "systematic_violations"
