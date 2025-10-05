#!/usr/bin/env python3
"""
Guardian Kill-Switch Unit Tests

Tests the emergency kill-switch behavior in Guardian system.
"""

import os
import unittest
from pathlib import Path
from unittest.mock import patch

from governance.guardian_system import GuardianSystem


class TestGuardianKillSwitch(unittest.TestCase):
    """Test Guardian emergency kill-switch functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.guardian = GuardianSystem()
        self.test_operation = {"action": "test", "user": "test_user"}

    def tearDown(self):
        """Clean up test fixtures"""
        # Ensure emergency file is removed
        emergency_file = Path("/tmp/guardian_emergency_disable")
        if emergency_file.exists():
            emergency_file.unlink()

    def test_normal_operation_with_enforcement_enabled(self):
        """Test normal operation when Guardian is enabled"""
        with patch.dict(os.environ, {"ENFORCE_ETHICS_DSL": "1"}):
            result = self.guardian.validate_safety(self.test_operation)

            self.assertTrue(result["safe"])
            self.assertEqual(result["guardian_status"], "active")
            self.assertTrue(result["enforcement_enabled"])
            self.assertFalse(result["emergency_active"])
            self.assertLessEqual(result["drift_score"], 0.15)

    def test_normal_operation_with_enforcement_disabled(self):
        """Test normal operation when Guardian is disabled"""
        with patch.dict(os.environ, {"ENFORCE_ETHICS_DSL": "0"}):
            result = self.guardian.validate_safety(self.test_operation)

            self.assertTrue(result["safe"])
            self.assertEqual(result["guardian_status"], "disabled")
            self.assertFalse(result["enforcement_enabled"])
            self.assertEqual(result["drift_score"], 0.0)

    def test_emergency_kill_switch_activation(self):
        """Test that emergency kill-switch disables all operations"""
        # Create emergency file
        emergency_file = Path("/tmp/guardian_emergency_disable")
        emergency_file.touch()

        try:
            with patch.dict(os.environ, {"ENFORCE_ETHICS_DSL": "1"}):
                result = self.guardian.validate_safety(self.test_operation)

                # Kill-switch should override all other settings
                self.assertFalse(result["safe"])
                self.assertEqual(result["guardian_status"], "emergency_disabled")
                self.assertTrue(result["emergency_active"])
                self.assertEqual(result["drift_score"], 1.0)
                self.assertEqual(result["reason"], "Emergency kill-switch activated")

        finally:
            # Clean up
            if emergency_file.exists():
                emergency_file.unlink()

    def test_emergency_kill_switch_overrides_disabled_enforcement(self):
        """Test that kill-switch works even when enforcement is disabled"""
        # Create emergency file
        emergency_file = Path("/tmp/guardian_emergency_disable")
        emergency_file.touch()

        try:
            with patch.dict(os.environ, {"ENFORCE_ETHICS_DSL": "0"}):
                result = self.guardian.validate_safety(self.test_operation)

                # Kill-switch should activate regardless of ENFORCE_ETHICS_DSL
                self.assertFalse(result["safe"])
                self.assertEqual(result["guardian_status"], "emergency_disabled")
                self.assertTrue(result["emergency_active"])

        finally:
            # Clean up
            if emergency_file.exists():
                emergency_file.unlink()

    def test_kill_switch_file_removal_restores_normal_operation(self):
        """Test that removing kill-switch file restores normal operation"""
        # Create emergency file
        emergency_file = Path("/tmp/guardian_emergency_disable")
        emergency_file.touch()

        # First call should be disabled
        with patch.dict(os.environ, {"ENFORCE_ETHICS_DSL": "1"}):
            result1 = self.guardian.validate_safety(self.test_operation)
            self.assertFalse(result1["safe"])
            self.assertEqual(result1["guardian_status"], "emergency_disabled")

        # Remove emergency file
        emergency_file.unlink()

        # Second call should be normal
        with patch.dict(os.environ, {"ENFORCE_ETHICS_DSL": "1"}):
            result2 = self.guardian.validate_safety(self.test_operation)
            self.assertTrue(result2["safe"])
            self.assertEqual(result2["guardian_status"], "active")
            self.assertFalse(result2["emergency_active"])

    def test_kill_switch_within_one_request_cycle(self):
        """Test that kill-switch activates within 1 request cycle"""
        import time

        with patch.dict(os.environ, {"ENFORCE_ETHICS_DSL": "1"}):
            # Normal operation first
            result1 = self.guardian.validate_safety(self.test_operation)
            self.assertTrue(result1["safe"])

            # Create emergency file
            emergency_file = Path("/tmp/guardian_emergency_disable")
            emergency_file.touch()

            try:
                # Immediate next call should be disabled (within 1 request cycle)
                start_time = time.perf_counter()
                result2 = self.guardian.validate_safety(self.test_operation)
                end_time = time.perf_counter()

                # Should be disabled immediately
                self.assertFalse(result2["safe"])
                self.assertEqual(result2["guardian_status"], "emergency_disabled")

                # Should be very fast (< 10ms)
                response_time_ms = (end_time - start_time) * 1000
                self.assertLess(response_time_ms, 10)

            finally:
                emergency_file.unlink()


if __name__ == "__main__":
    unittest.main()
