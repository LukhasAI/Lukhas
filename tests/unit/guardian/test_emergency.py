#!/usr/bin/env python3
"""Unit tests for Guardian Emergency Kill-Switch System"""

import unittest
from pathlib import Path
from guardian.emergency import trigger_kill_switch, is_kill_switch_active, clear_kill_switch


class TestGuardianEmergency(unittest.TestCase):
    """Test Guardian emergency kill-switch functionality"""

    def setUp(self):
        self.kill_switch_file = Path("/tmp/guardian_emergency_disable")
        self.reason_file = Path("/tmp/guardian_emergency_reason.txt")
        self._cleanup()

    def tearDown(self):
        self._cleanup()

    def _cleanup(self):
        if self.kill_switch_file.exists():
            self.kill_switch_file.unlink()
        if self.reason_file.exists():
            self.reason_file.unlink()

    def test_kill_switch_initially_inactive(self):
        self.assertFalse(is_kill_switch_active())

    def test_trigger_and_clear(self):
        result = trigger_kill_switch("Test", "tester")
        self.assertTrue(result["success"])
        self.assertTrue(is_kill_switch_active())

        clear_result = clear_kill_switch("ops")
        self.assertTrue(clear_result["success"])
        self.assertFalse(is_kill_switch_active())


if __name__ == "__main__":
    unittest.main()
