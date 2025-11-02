#!/usr/bin/env python3
"""
Guardian System Default Behavior Tests
=====================================

Regression tests ensuring Guardian System fails closed by default.
Critical for T4/0.01% operational excellence.
"""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from governance.guardian_system import GuardianSystem


class TestGuardianDefaults:
    """Test Guardian System default behavior - must fail closed"""

    def test_guardian_defaults_to_enabled(self):
        """Guardian enforcement must be ON by default (fail closed)"""
        # Clear any existing environment variable
        with patch.dict(os.environ, {}, clear=True):
            guardian = GuardianSystem()
            result = guardian.validate_safety({"action": "test_default_behavior"})

            # Guardian should be active by default
            assert result["enforcement_enabled"] is True
            assert result["guardian_status"] == "active"
            assert result["safe"] is True
            assert "emergency_active" in result
            assert result["emergency_active"] is False

    def test_guardian_explicit_disable_requires_env_var(self):
        """Guardian can only be disabled with explicit ENFORCE_ETHICS_DSL=0"""
        with patch.dict(os.environ, {"ENFORCE_ETHICS_DSL": "0"}):
            guardian = GuardianSystem()
            result = guardian.validate_safety({"action": "test_explicit_disable"})

            # Should be disabled when explicitly set to 0
            assert result["enforcement_enabled"] is False
            assert result["guardian_status"] == "disabled"
            assert result["safe"] is True

    def test_guardian_explicit_enable(self):
        """Guardian works when explicitly enabled with ENFORCE_ETHICS_DSL=1"""
        with patch.dict(os.environ, {"ENFORCE_ETHICS_DSL": "1"}):
            guardian = GuardianSystem()
            result = guardian.validate_safety({"action": "test_explicit_enable"})

            # Should be active when explicitly set to 1
            assert result["enforcement_enabled"] is True
            assert result["guardian_status"] == "active"
            assert result["safe"] is True

    def test_emergency_kill_switch_overrides_everything(self):
        """Emergency kill-switch must override all other settings"""
        emergency_file = Path("/tmp/guardian_emergency_disable")

        try:
            # Create emergency file
            emergency_file.touch()

            # Test with default settings (enabled)
            with patch.dict(os.environ, {}, clear=True):
                guardian = GuardianSystem()
                result = guardian.validate_safety({"action": "test_emergency_override"})

                assert result["safe"] is False
                assert result["guardian_status"] == "emergency_disabled"
                assert result["emergency_active"] is True
                assert result["drift_score"] == 1.0

            # Test with explicitly enabled
            with patch.dict(os.environ, {"ENFORCE_ETHICS_DSL": "1"}):
                guardian = GuardianSystem()
                result = guardian.validate_safety({"action": "test_emergency_override"})

                assert result["safe"] is False
                assert result["guardian_status"] == "emergency_disabled"
                assert result["emergency_active"] is True

            # Test with explicitly disabled - emergency still overrides
            with patch.dict(os.environ, {"ENFORCE_ETHICS_DSL": "0"}):
                guardian = GuardianSystem()
                result = guardian.validate_safety({"action": "test_emergency_override"})

                assert result["safe"] is False
                assert result["guardian_status"] == "emergency_disabled"
                assert result["emergency_active"] is True

        finally:
            # Clean up emergency file
            if emergency_file.exists():
                emergency_file.unlink()

    def test_drift_threshold_default(self):
        """Drift threshold should default to 0.15 (production standard)"""
        guardian = GuardianSystem()
        assert guardian.drift_threshold == 0.15

    @pytest.mark.parametrize(
        "env_value,expected_enabled",
        [
            ("1", True),
            ("true", True),  # Fail closed - non-"0" values enable
            ("True", True),  # Fail closed - non-"0" values enable
            ("yes", True),  # Fail closed - non-"0" values enable
            ("0", False),  # Only "0" explicitly disables
            ("false", True),  # Fail closed - non-"0" values enable
            ("", True),  # Fail closed - non-"0" values enable
            ("invalid", True),  # Fail closed - non-"0" values enable
        ],
    )
    def test_env_var_parsing_strict(self, env_value, expected_enabled):
        """Environment variable parsing must be fail-closed - only '0' disables"""
        with patch.dict(os.environ, {"ENFORCE_ETHICS_DSL": env_value}):
            guardian = GuardianSystem()
            result = guardian.validate_safety({"action": "test_env_parsing"})

            assert result["enforcement_enabled"] == expected_enabled

    def test_guardian_initialization_logging(self, caplog):
        """Guardian initialization should log properly"""
        with caplog.at_level("INFO"):
            GuardianSystem()

        assert "GuardianSystem initialized" in caplog.text

    def test_guardian_disabled_warning_logging(self, caplog):
        """Disabling Guardian should log a warning"""
        with patch.dict(os.environ, {"ENFORCE_ETHICS_DSL": "0"}):
            guardian = GuardianSystem()

            with caplog.at_level("WARNING"):
                guardian.validate_safety({"action": "test_warning_log"})

            assert "Guardian enforcement explicitly disabled" in caplog.text

    def test_fail_closed_security_behavior(self):
        """Test that fail-closed behavior provides security by default"""
        # Simulate various potentially problematic environment states
        test_cases = [
            {},  # No env vars
            {"RANDOM_VAR": "1"},  # Unrelated env vars
            {"ENFORCE_ETHICS_DSL": ""},  # Empty string
            {"ENFORCE_ETHICS_DSL": "maybe"},  # Invalid value
        ]

        for env_state in test_cases:
            with patch.dict(os.environ, env_state, clear=True):
                guardian = GuardianSystem()
                result = guardian.validate_safety({"action": "security_test"})

                # All cases should default to ENABLED (fail closed)
                assert result["enforcement_enabled"] is True, f"Failed for env: {env_state}"
                assert result["guardian_status"] == "active", f"Failed for env: {env_state}"


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])
