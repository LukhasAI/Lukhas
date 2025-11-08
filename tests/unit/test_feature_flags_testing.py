"""
Comprehensive tests for feature flags testing utilities.

Tests override_flag, override_flags, temp_flags_config, and pytest fixtures.
"""

import tempfile
from pathlib import Path

import pytest
import yaml

from lukhas.features.flags_service import FeatureFlagsService, is_enabled
from lukhas.features.testing import (
    override_flag,
    override_flags,
    temp_flags_config,
)


class TestOverrideFlag:
    """Test override_flag context manager."""

    def test_override_flag_enable(self):
        """Test overriding flag to enabled."""
        # Create service with disabled flag
        config = {
            "flags": {
                "test_flag": {
                    "type": "boolean",
                    "enabled": False,
                    "description": "Test flag",
                }
            }
        }

        with temp_flags_config(config) as service:
            # Initially disabled
            assert service.is_enabled("test_flag") is False

            # Override to enabled
            with override_flag("test_flag", True, service):
                assert service.is_enabled("test_flag") is True

            # Should restore after context
            assert service.is_enabled("test_flag") is False

    def test_override_flag_disable(self):
        """Test overriding flag to disabled."""
        config = {
            "flags": {
                "test_flag": {
                    "type": "boolean",
                    "enabled": True,
                    "description": "Test flag",
                }
            }
        }

        with temp_flags_config(config) as service:
            # Initially enabled
            assert service.is_enabled("test_flag") is True

            # Override to disabled
            with override_flag("test_flag", False, service):
                assert service.is_enabled("test_flag") is False

            # Should restore after context
            assert service.is_enabled("test_flag") is True

    def test_override_flag_nested(self):
        """Test nested flag overrides."""
        config = {
            "flags": {
                "test_flag": {
                    "type": "boolean",
                    "enabled": False,
                    "description": "Test flag",
                }
            }
        }

        with temp_flags_config(config) as service:
            assert service.is_enabled("test_flag") is False

            with override_flag("test_flag", True, service):
                assert service.is_enabled("test_flag") is True

                with override_flag("test_flag", False, service):
                    assert service.is_enabled("test_flag") is False

                # Should restore to True (outer override)
                assert service.is_enabled("test_flag") is True

            # Should restore to original False
            assert service.is_enabled("test_flag") is False

    def test_override_nonexistent_flag(self):
        """Test overriding non-existent flag does not crash."""
        config = {"flags": {}}

        with temp_flags_config(config) as service:
            # Should not crash
            with override_flag("nonexistent", True, service):
                pass


class TestOverrideFlags:
    """Test override_flags context manager."""

    def test_override_multiple_flags(self):
        """Test overriding multiple flags."""
        config = {
            "flags": {
                "flag1": {
                    "type": "boolean",
                    "enabled": False,
                    "description": "Flag 1",
                },
                "flag2": {
                    "type": "boolean",
                    "enabled": True,
                    "description": "Flag 2",
                },
                "flag3": {
                    "type": "boolean",
                    "enabled": False,
                    "description": "Flag 3",
                },
            }
        }

        with temp_flags_config(config) as service:
            # Initial state
            assert service.is_enabled("flag1") is False
            assert service.is_enabled("flag2") is True
            assert service.is_enabled("flag3") is False

            # Override multiple flags
            with override_flags({
                "flag1": True,
                "flag2": False,
                "flag3": True,
            }, service):
                assert service.is_enabled("flag1") is True
                assert service.is_enabled("flag2") is False
                assert service.is_enabled("flag3") is True

            # Should restore all
            assert service.is_enabled("flag1") is False
            assert service.is_enabled("flag2") is True
            assert service.is_enabled("flag3") is False

    def test_override_flags_partial(self):
        """Test overriding subset of flags."""
        config = {
            "flags": {
                "flag1": {
                    "type": "boolean",
                    "enabled": False,
                    "description": "Flag 1",
                },
                "flag2": {
                    "type": "boolean",
                    "enabled": True,
                    "description": "Flag 2",
                },
            }
        }

        with temp_flags_config(config) as service:
            # Override only flag1
            with override_flags({"flag1": True}, service):
                assert service.is_enabled("flag1") is True
                assert service.is_enabled("flag2") is True  # Unchanged

            # Should restore flag1
            assert service.is_enabled("flag1") is False
            assert service.is_enabled("flag2") is True


class TestTempFlagsConfig:
    """Test temp_flags_config context manager."""

    def test_temp_config_creation(self):
        """Test temporary config creation."""
        config = {
            "flags": {
                "test_flag": {
                    "type": "boolean",
                    "enabled": True,
                    "description": "Test flag",
                }
            }
        }

        with temp_flags_config(config) as service:
            assert isinstance(service, FeatureFlagsService)
            assert service.is_enabled("test_flag") is True

    def test_temp_config_cleanup(self):
        """Test temporary config file is cleaned up."""
        config = {
            "flags": {
                "test_flag": {
                    "type": "boolean",
                    "enabled": True,
                    "description": "Test flag",
                }
            }
        }

        config_path = None
        with temp_flags_config(config) as service:
            config_path = service.config_path
            assert Path(config_path).exists()

        # File should be deleted after context
        assert not Path(config_path).exists()

    def test_temp_config_multiple_flags(self):
        """Test temporary config with multiple flags."""
        config = {
            "flags": {
                "flag1": {
                    "type": "boolean",
                    "enabled": True,
                    "description": "Flag 1",
                },
                "flag2": {
                    "type": "percentage",
                    "enabled": True,
                    "percentage": 50,
                    "description": "Flag 2",
                },
                "flag3": {
                    "type": "environment",
                    "enabled": True,
                    "allowed_environments": ["test"],
                    "description": "Flag 3",
                },
            }
        }

        with temp_flags_config(config) as service:
            assert len(service.list_flags()) == 3
            assert service.is_enabled("flag1") is True
            assert "flag2" in service.list_flags()
            assert "flag3" in service.list_flags()


class TestPytestFixtures:
    """Test pytest fixtures."""

    def test_feature_flags_fixture(self, feature_flags):
        """Test feature_flags fixture."""
        assert isinstance(feature_flags, FeatureFlagsService)

        # Should have test flags
        flags = feature_flags.list_flags()
        assert "test_boolean_flag" in flags
        assert "test_percentage_flag" in flags
        assert "test_user_targeting_flag" in flags
        assert "test_time_based_flag" in flags
        assert "test_environment_flag" in flags

    def test_feature_flags_boolean(self, feature_flags):
        """Test boolean flag from fixture."""
        assert feature_flags.is_enabled("test_boolean_flag") is True

    def test_feature_flags_percentage(self, feature_flags, flag_context):
        """Test percentage flag from fixture."""
        result = feature_flags.is_enabled("test_percentage_flag", flag_context)
        assert isinstance(result, bool)

    def test_flag_context_fixture(self, flag_context):
        """Test flag_context fixture."""
        assert flag_context.user_id == "test-user-123"
        assert flag_context.email == "test@test.com"
        assert flag_context.environment == "test"

    def test_override_flag_fixture(self, feature_flags, override_flag_fixture):
        """Test override_flag fixture."""
        # Initially enabled
        assert feature_flags.is_enabled("test_boolean_flag") is True

        # Override to disabled
        with override_flag_fixture("test_boolean_flag", False, feature_flags):
            assert feature_flags.is_enabled("test_boolean_flag") is False

        # Restored
        assert feature_flags.is_enabled("test_boolean_flag") is True

    def test_override_flags_fixture(self, feature_flags, override_flags_fixture):
        """Test override_flags fixture."""
        with override_flags_fixture({
            "test_boolean_flag": False,
        }, feature_flags):
            assert feature_flags.is_enabled("test_boolean_flag") is False
