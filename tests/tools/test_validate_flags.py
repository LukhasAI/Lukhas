"""
Tests for feature flags validation tool.
"""

import sys
import tempfile
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))

from validate_flags import FlagValidator


class TestFlagValidator:
    """Test FlagValidator class."""

    @pytest.fixture
    def temp_config_file(self):
        """Create temporary config file."""
        def _create(config):
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", delete=False
            ) as f:
                yaml.dump(config, f)
                return f.name

        return _create

    def test_valid_config(self, temp_config_file):
        """Test validation of valid config."""
        config = {
            "flags": {
                "test_flag": {
                    "type": "boolean",
                    "enabled": True,
                    "description": "Test flag description",
                    "owner": "team@lukhas.ai",
                    "created_at": "2025-11-08",
                }
            }
        }

        config_path = temp_config_file(config)
        try:
            validator = FlagValidator(config_path)
            assert validator.validate() is True
            assert len(validator.errors) == 0
        finally:
            Path(config_path).unlink()

    def test_missing_file(self):
        """Test validation of missing file."""
        validator = FlagValidator("/nonexistent/path.yaml")
        assert validator.validate() is False
        assert len(validator.errors) > 0

    def test_invalid_yaml(self, temp_config_file):
        """Test validation of invalid YAML."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            f.write("invalid: yaml: content:")
            config_path = f.name

        try:
            validator = FlagValidator(config_path)
            assert validator.validate() is False
            assert len(validator.errors) > 0
        finally:
            Path(config_path).unlink()

    def test_missing_required_fields(self, temp_config_file):
        """Test validation with missing required fields."""
        config = {
            "flags": {
                "test_flag": {
                    "type": "boolean",
                    # Missing: enabled, description, owner, created_at
                }
            }
        }

        config_path = temp_config_file(config)
        try:
            validator = FlagValidator(config_path)
            assert validator.validate() is False
            assert len(validator.errors) >= 4  # 4 missing fields
        finally:
            Path(config_path).unlink()

    def test_invalid_flag_type(self, temp_config_file):
        """Test validation with invalid flag type."""
        config = {
            "flags": {
                "test_flag": {
                    "type": "invalid_type",
                    "enabled": True,
                    "description": "Test flag",
                    "owner": "team@lukhas.ai",
                    "created_at": "2025-11-08",
                }
            }
        }

        config_path = temp_config_file(config)
        try:
            validator = FlagValidator(config_path)
            assert validator.validate() is False
            assert any("Invalid flag type" in err for err in validator.errors)
        finally:
            Path(config_path).unlink()

    def test_percentage_flag_validation(self, temp_config_file):
        """Test percentage flag validation."""
        # Valid percentage
        config = {
            "flags": {
                "test_flag": {
                    "type": "percentage",
                    "enabled": True,
                    "percentage": 50,
                    "description": "Test flag",
                    "owner": "team@lukhas.ai",
                    "created_at": "2025-11-08",
                }
            }
        }

        config_path = temp_config_file(config)
        try:
            validator = FlagValidator(config_path)
            assert validator.validate() is True
        finally:
            Path(config_path).unlink()

        # Invalid percentage (out of range)
        config = {
            "flags": {
                "test_flag": {
                    "type": "percentage",
                    "enabled": True,
                    "percentage": 150,  # > 100
                    "description": "Test flag",
                    "owner": "team@lukhas.ai",
                    "created_at": "2025-11-08",
                }
            }
        }

        config_path = temp_config_file(config)
        try:
            validator = FlagValidator(config_path)
            assert validator.validate() is False
            assert any("between 0 and 100" in err for err in validator.errors)
        finally:
            Path(config_path).unlink()

    def test_user_targeting_validation(self, temp_config_file):
        """Test user targeting flag validation."""
        # Valid with allowed_domains
        config = {
            "flags": {
                "test_flag": {
                    "type": "user_targeting",
                    "enabled": True,
                    "allowed_domains": ["lukhas.ai"],
                    "description": "Test flag",
                    "owner": "team@lukhas.ai",
                    "created_at": "2025-11-08",
                }
            }
        }

        config_path = temp_config_file(config)
        try:
            validator = FlagValidator(config_path)
            assert validator.validate() is True
        finally:
            Path(config_path).unlink()

        # Missing targeting fields
        config = {
            "flags": {
                "test_flag": {
                    "type": "user_targeting",
                    "enabled": True,
                    # Missing allowed_domains and allowed_user_hashes
                    "description": "Test flag",
                    "owner": "team@lukhas.ai",
                    "created_at": "2025-11-08",
                }
            }
        }

        config_path = temp_config_file(config)
        try:
            validator = FlagValidator(config_path)
            assert validator.validate() is False
        finally:
            Path(config_path).unlink()

    def test_time_based_validation(self, temp_config_file):
        """Test time-based flag validation."""
        # Valid with enable_after
        config = {
            "flags": {
                "test_flag": {
                    "type": "time_based",
                    "enabled": True,
                    "enable_after": "2025-12-01T00:00:00Z",
                    "description": "Test flag",
                    "owner": "team@lukhas.ai",
                    "created_at": "2025-11-08",
                }
            }
        }

        config_path = temp_config_file(config)
        try:
            validator = FlagValidator(config_path)
            assert validator.validate() is True
        finally:
            Path(config_path).unlink()

    def test_environment_validation(self, temp_config_file):
        """Test environment flag validation."""
        # Valid with allowed_environments
        config = {
            "flags": {
                "test_flag": {
                    "type": "environment",
                    "enabled": True,
                    "allowed_environments": ["dev", "staging"],
                    "description": "Test flag",
                    "owner": "team@lukhas.ai",
                    "created_at": "2025-11-08",
                }
            }
        }

        config_path = temp_config_file(config)
        try:
            validator = FlagValidator(config_path)
            assert validator.validate() is True
        finally:
            Path(config_path).unlink()
