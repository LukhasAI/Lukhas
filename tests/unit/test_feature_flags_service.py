"""
Comprehensive tests for feature flags service.

Tests all flag types, evaluation logic, caching, and error handling.
"""

import hashlib
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
import yaml

from lukhas.features.flags_service import (
    FlagEvaluationContext,
    FlagType,
    FeatureFlag,
    FeatureFlagsService,
    get_service,
    is_enabled,
)


class TestFlagEvaluationContext:
    """Test FlagEvaluationContext."""

    def test_default_values(self):
        """Test context with default values."""
        context = FlagEvaluationContext()

        assert context.user_id is None
        assert context.email is None
        assert context.environment in ["dev", "staging", "prod"]
        assert isinstance(context.timestamp, datetime)

    def test_custom_values(self):
        """Test context with custom values."""
        now = datetime.now(timezone.utc)
        context = FlagEvaluationContext(
            user_id="user-123",
            email="test@lukhas.ai",
            environment="prod",
            timestamp=now,
        )

        assert context.user_id == "user-123"
        assert context.email == "test@lukhas.ai"
        assert context.environment == "prod"
        assert context.timestamp == now

    def test_get_user_hash(self):
        """Test privacy-preserving user hash."""
        context = FlagEvaluationContext(user_id="user-123")

        user_hash = context.get_user_hash()

        # Should be SHA-256 hex string (64 chars)
        assert len(user_hash) == 64
        assert all(c in "0123456789abcdef" for c in user_hash)

        # Should be consistent
        assert user_hash == context.get_user_hash()

        # Should match expected hash
        expected = hashlib.sha256("user-123".encode()).hexdigest()
        assert user_hash == expected

    def test_get_user_hash_no_user_id(self):
        """Test user hash with no user ID."""
        context = FlagEvaluationContext()

        user_hash = context.get_user_hash()

        assert user_hash == ""

    def test_get_email_domain(self):
        """Test email domain extraction."""
        context = FlagEvaluationContext(email="test@lukhas.ai")

        domain = context.get_email_domain()

        assert domain == "lukhas.ai"

    def test_get_email_domain_case_insensitive(self):
        """Test email domain is lowercase."""
        context = FlagEvaluationContext(email="Test@LUKHAS.AI")

        domain = context.get_email_domain()

        assert domain == "lukhas.ai"

    def test_get_email_domain_no_email(self):
        """Test email domain with no email."""
        context = FlagEvaluationContext()

        domain = context.get_email_domain()

        assert domain == ""

    def test_get_email_domain_invalid_email(self):
        """Test email domain with invalid email."""
        context = FlagEvaluationContext(email="invalid-email")

        domain = context.get_email_domain()

        assert domain == ""


class TestFeatureFlag:
    """Test FeatureFlag class."""

    def test_boolean_flag_enabled(self):
        """Test boolean flag that is enabled."""
        flag = FeatureFlag(
            "test_flag",
            {
                "type": "boolean",
                "enabled": True,
                "description": "Test flag",
            },
        )

        context = FlagEvaluationContext()
        assert flag.evaluate(context) is True

    def test_boolean_flag_disabled(self):
        """Test boolean flag that is disabled."""
        flag = FeatureFlag(
            "test_flag",
            {
                "type": "boolean",
                "enabled": False,
                "description": "Test flag",
            },
        )

        context = FlagEvaluationContext()
        assert flag.evaluate(context) is False

    def test_percentage_flag_0_percent(self):
        """Test percentage flag at 0%."""
        flag = FeatureFlag(
            "test_flag",
            {
                "type": "percentage",
                "enabled": True,
                "percentage": 0,
                "description": "Test flag",
            },
        )

        context = FlagEvaluationContext(user_id="user-123")
        assert flag.evaluate(context) is False

    def test_percentage_flag_100_percent(self):
        """Test percentage flag at 100%."""
        flag = FeatureFlag(
            "test_flag",
            {
                "type": "percentage",
                "enabled": True,
                "percentage": 100,
                "description": "Test flag",
            },
        )

        context = FlagEvaluationContext(user_id="user-123")
        assert flag.evaluate(context) is True

    def test_percentage_flag_consistency(self):
        """Test percentage flag is consistent for same user."""
        flag = FeatureFlag(
            "test_flag",
            {
                "type": "percentage",
                "enabled": True,
                "percentage": 50,
                "description": "Test flag",
            },
        )

        context = FlagEvaluationContext(user_id="user-123")

        # Should get same result multiple times
        result1 = flag.evaluate(context)
        result2 = flag.evaluate(context)
        result3 = flag.evaluate(context)

        assert result1 == result2 == result3

    def test_percentage_flag_distribution(self):
        """Test percentage flag distribution across users."""
        flag = FeatureFlag(
            "test_flag",
            {
                "type": "percentage",
                "enabled": True,
                "percentage": 50,
                "description": "Test flag",
            },
        )

        # Test 100 users
        enabled_count = 0
        for i in range(100):
            context = FlagEvaluationContext(user_id=f"user-{i}")
            if flag.evaluate(context):
                enabled_count += 1

        # Should be roughly 50% (allow 30-70% due to randomness)
        assert 30 <= enabled_count <= 70

    def test_percentage_flag_no_user_id(self):
        """Test percentage flag with no user ID."""
        flag = FeatureFlag(
            "test_flag",
            {
                "type": "percentage",
                "enabled": True,
                "percentage": 50,
                "description": "Test flag",
            },
        )

        context = FlagEvaluationContext()
        # Should return False without user ID
        assert flag.evaluate(context) is False

    def test_user_targeting_by_domain(self):
        """Test user targeting by email domain."""
        flag = FeatureFlag(
            "test_flag",
            {
                "type": "user_targeting",
                "enabled": True,
                "allowed_domains": ["lukhas.ai", "lukhas.com"],
                "description": "Test flag",
            },
        )

        # Allowed domain
        context1 = FlagEvaluationContext(email="test@lukhas.ai")
        assert flag.evaluate(context1) is True

        # Allowed domain (case insensitive)
        context2 = FlagEvaluationContext(email="Test@LUKHAS.AI")
        assert flag.evaluate(context2) is True

        # Different allowed domain
        context3 = FlagEvaluationContext(email="user@lukhas.com")
        assert flag.evaluate(context3) is True

        # Not allowed domain
        context4 = FlagEvaluationContext(email="user@example.com")
        assert flag.evaluate(context4) is False

        # No email
        context5 = FlagEvaluationContext()
        assert flag.evaluate(context5) is False

    def test_user_targeting_by_hash(self):
        """Test user targeting by user hash."""
        user_id = "user-123"
        user_hash = hashlib.sha256(user_id.encode()).hexdigest()

        flag = FeatureFlag(
            "test_flag",
            {
                "type": "user_targeting",
                "enabled": True,
                "allowed_user_hashes": [user_hash],
                "description": "Test flag",
            },
        )

        # Matching user
        context1 = FlagEvaluationContext(user_id=user_id)
        assert flag.evaluate(context1) is True

        # Different user
        context2 = FlagEvaluationContext(user_id="user-456")
        assert flag.evaluate(context2) is False

        # No user
        context3 = FlagEvaluationContext()
        assert flag.evaluate(context3) is False

    def test_time_based_enable_after(self):
        """Test time-based flag with enable_after."""
        now = datetime.now(timezone.utc)
        past = (now - timedelta(days=1)).isoformat()
        future = (now + timedelta(days=1)).isoformat()

        # Flag enabled in the past - should be enabled
        flag1 = FeatureFlag(
            "test_flag",
            {
                "type": "time_based",
                "enabled": True,
                "enable_after": past,
                "description": "Test flag",
            },
        )
        context = FlagEvaluationContext(timestamp=now)
        assert flag1.evaluate(context) is True

        # Flag enabled in the future - should be disabled
        flag2 = FeatureFlag(
            "test_flag",
            {
                "type": "time_based",
                "enabled": True,
                "enable_after": future,
                "description": "Test flag",
            },
        )
        assert flag2.evaluate(context) is False

    def test_time_based_disable_after(self):
        """Test time-based flag with disable_after."""
        now = datetime.now(timezone.utc)
        past = (now - timedelta(days=1)).isoformat()
        future = (now + timedelta(days=1)).isoformat()

        # Flag disabled in the past - should be disabled
        flag1 = FeatureFlag(
            "test_flag",
            {
                "type": "time_based",
                "enabled": True,
                "disable_after": past,
                "description": "Test flag",
            },
        )
        context = FlagEvaluationContext(timestamp=now)
        assert flag1.evaluate(context) is False

        # Flag disabled in the future - should be enabled
        flag2 = FeatureFlag(
            "test_flag",
            {
                "type": "time_based",
                "enabled": True,
                "disable_after": future,
                "description": "Test flag",
            },
        )
        assert flag2.evaluate(context) is True

    def test_environment_flag(self):
        """Test environment-based flag."""
        flag = FeatureFlag(
            "test_flag",
            {
                "type": "environment",
                "enabled": True,
                "allowed_environments": ["dev", "staging"],
                "description": "Test flag",
            },
        )

        # Allowed environment
        context1 = FlagEvaluationContext(environment="dev")
        assert flag.evaluate(context1) is True

        context2 = FlagEvaluationContext(environment="staging")
        assert flag.evaluate(context2) is True

        # Not allowed environment
        context3 = FlagEvaluationContext(environment="prod")
        assert flag.evaluate(context3) is False

    def test_fallback_value(self):
        """Test fallback value on errors."""
        # Invalid flag type should return fallback
        flag = FeatureFlag(
            "test_flag",
            {
                "type": "invalid_type",
                "enabled": True,
                "fallback": True,
                "description": "Test flag",
            },
        )

        context = FlagEvaluationContext()
        assert flag.evaluate(context) is True

    def test_globally_disabled_flag(self):
        """Test globally disabled flag."""
        # Even with 100% rollout, disabled flag should be False
        flag = FeatureFlag(
            "test_flag",
            {
                "type": "percentage",
                "enabled": False,
                "percentage": 100,
                "description": "Test flag",
            },
        )

        context = FlagEvaluationContext(user_id="user-123")
        assert flag.evaluate(context) is False


class TestFeatureFlagsService:
    """Test FeatureFlagsService."""

    @pytest.fixture
    def temp_config(self):
        """Create temporary config file."""
        config = {
            "version": "1.0",
            "flags": {
                "boolean_flag": {
                    "type": "boolean",
                    "enabled": True,
                    "description": "Boolean flag",
                },
                "percentage_flag": {
                    "type": "percentage",
                    "enabled": True,
                    "percentage": 50,
                    "description": "Percentage flag",
                },
                "disabled_flag": {
                    "type": "boolean",
                    "enabled": False,
                    "description": "Disabled flag",
                },
            },
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump(config, f)
            temp_path = f.name

        yield temp_path

        # Cleanup
        Path(temp_path).unlink(missing_ok=True)

    def test_service_initialization(self, temp_config):
        """Test service initialization."""
        service = FeatureFlagsService(config_path=temp_config, cache_ttl=60)

        assert service.config_path == temp_config
        assert service.cache_ttl == 60
        assert len(service.flags) == 3

    def test_is_enabled(self, temp_config):
        """Test is_enabled method."""
        service = FeatureFlagsService(config_path=temp_config)

        # Enabled flag
        assert service.is_enabled("boolean_flag") is True

        # Disabled flag
        assert service.is_enabled("disabled_flag") is False

        # Non-existent flag
        assert service.is_enabled("nonexistent_flag") is False

    def test_get_flag(self, temp_config):
        """Test get_flag method."""
        service = FeatureFlagsService(config_path=temp_config)

        flag = service.get_flag("boolean_flag")
        assert flag is not None
        assert flag.name == "boolean_flag"
        assert flag.enabled is True

        # Non-existent flag
        flag = service.get_flag("nonexistent_flag")
        assert flag is None

    def test_list_flags(self, temp_config):
        """Test list_flags method."""
        service = FeatureFlagsService(config_path=temp_config)

        flags = service.list_flags()

        assert len(flags) == 3
        assert "boolean_flag" in flags
        assert "percentage_flag" in flags
        assert "disabled_flag" in flags

    def test_get_all_flags(self, temp_config):
        """Test get_all_flags method."""
        service = FeatureFlagsService(config_path=temp_config)

        flags = service.get_all_flags()

        assert len(flags) == 3
        assert all(isinstance(flag, FeatureFlag) for flag in flags.values())

    def test_reload(self, temp_config):
        """Test reload method."""
        service = FeatureFlagsService(config_path=temp_config)

        # Initial state
        assert service.is_enabled("boolean_flag") is True

        # Modify config file
        config = {
            "version": "1.0",
            "flags": {
                "boolean_flag": {
                    "type": "boolean",
                    "enabled": False,  # Changed to False
                    "description": "Boolean flag",
                },
            },
        }
        with open(temp_config, "w") as f:
            yaml.dump(config, f)

        # Reload
        service.reload()

        # Should reflect new state
        assert service.is_enabled("boolean_flag") is False

    def test_cache_ttl(self, temp_config):
        """Test cache TTL."""
        service = FeatureFlagsService(config_path=temp_config, cache_ttl=0)

        # Initial state
        assert service.is_enabled("boolean_flag") is True

        # Modify config file
        config = {
            "version": "1.0",
            "flags": {
                "boolean_flag": {
                    "type": "boolean",
                    "enabled": False,
                    "description": "Boolean flag",
                },
            },
        }
        with open(temp_config, "w") as f:
            yaml.dump(config, f)

        # Should auto-reload due to cache_ttl=0
        assert service.is_enabled("boolean_flag") is False

    def test_missing_config_file(self):
        """Test handling of missing config file."""
        service = FeatureFlagsService(config_path="/nonexistent/path.yaml")

        # Should not crash, just return empty flags
        assert len(service.flags) == 0
        assert service.is_enabled("any_flag") is False

    def test_invalid_yaml(self):
        """Test handling of invalid YAML."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            f.write("invalid: yaml: content:")
            temp_path = f.name

        try:
            service = FeatureFlagsService(config_path=temp_path)

            # Should not crash, just return empty flags
            assert len(service.flags) == 0
            assert service.is_enabled("any_flag") is False

        finally:
            Path(temp_path).unlink(missing_ok=True)


class TestGlobalService:
    """Test global service functions."""

    def test_get_service_singleton(self):
        """Test get_service returns singleton."""
        service1 = get_service()
        service2 = get_service()

        assert service1 is service2

    def test_is_enabled_convenience_function(self):
        """Test is_enabled convenience function."""
        # This should work even with default config
        result = is_enabled("any_flag")

        assert isinstance(result, bool)
