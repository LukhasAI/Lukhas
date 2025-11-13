"""
Comprehensive test suite for Feature Flags Service.

Tests flag evaluation logic, caching, YAML config loading, percentage rollout,
user targeting, time-based flags, and environment-based flags.

Coverage target: 85%+
"""

import hashlib
import os
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
import yaml

from lukhas.features.flags_service import (
    FeatureFlag,
    FeatureFlagsService,
    FlagEvaluationContext,
    FlagType,
    get_service,
    is_enabled,
)


# Test FlagEvaluationContext


class TestFlagEvaluationContext:
    """Tests for FlagEvaluationContext class."""

    def test_init_defaults(self):
        """Test context initializes with defaults."""
        ctx = FlagEvaluationContext()

        assert ctx.user_id is None
        assert ctx.email is None
        assert ctx.environment in ["dev", os.getenv("LUKHAS_ENV", "dev")]
        assert isinstance(ctx.timestamp, datetime)

    def test_init_with_values(self):
        """Test context initializes with provided values."""
        ts = datetime.now(timezone.utc)
        ctx = FlagEvaluationContext(
            user_id="user123",
            email="test@example.com",
            environment="prod",
            timestamp=ts,
        )

        assert ctx.user_id == "user123"
        assert ctx.email == "test@example.com"
        assert ctx.environment == "prod"
        assert ctx.timestamp == ts

    def test_get_user_hash(self):
        """Test getting privacy-preserving user hash."""
        ctx = FlagEvaluationContext(user_id="user123")

        user_hash = ctx.get_user_hash()

        # Should be SHA-256 hex string
        assert len(user_hash) == 64
        assert user_hash == hashlib.sha256("user123".encode()).hexdigest()

    def test_get_user_hash_empty(self):
        """Test getting user hash with no user_id."""
        ctx = FlagEvaluationContext()

        assert ctx.get_user_hash() == ""

    def test_get_user_hash_consistent(self):
        """Test user hash is consistent for same user."""
        ctx1 = FlagEvaluationContext(user_id="user123")
        ctx2 = FlagEvaluationContext(user_id="user123")

        assert ctx1.get_user_hash() == ctx2.get_user_hash()

    def test_get_user_hash_different_users(self):
        """Test user hash differs for different users."""
        ctx1 = FlagEvaluationContext(user_id="user1")
        ctx2 = FlagEvaluationContext(user_id="user2")

        assert ctx1.get_user_hash() != ctx2.get_user_hash()

    def test_get_email_domain(self):
        """Test extracting email domain."""
        ctx = FlagEvaluationContext(email="user@lukhas.ai")

        assert ctx.get_email_domain() == "lukhas.ai"

    def test_get_email_domain_uppercase(self):
        """Test email domain is lowercased."""
        ctx = FlagEvaluationContext(email="USER@LUKHAS.AI")

        assert ctx.get_email_domain() == "lukhas.ai"

    def test_get_email_domain_no_email(self):
        """Test getting domain with no email."""
        ctx = FlagEvaluationContext()

        assert ctx.get_email_domain() == ""

    def test_get_email_domain_invalid(self):
        """Test getting domain from invalid email."""
        ctx = FlagEvaluationContext(email="not_an_email")

        assert ctx.get_email_domain() == ""

    def test_environment_from_env_var(self):
        """Test environment defaults to LUKHAS_ENV."""
        with patch.dict(os.environ, {"LUKHAS_ENV": "staging"}):
            ctx = FlagEvaluationContext()
            assert ctx.environment == "staging"


# Test FeatureFlag


class TestFeatureFlag:
    """Tests for FeatureFlag class."""

    def test_init_minimal(self):
        """Test initializing flag with minimal config."""
        flag = FeatureFlag("test_flag", {"enabled": True})

        assert flag.name == "test_flag"
        assert flag.enabled is True
        assert flag.flag_type == FlagType.BOOLEAN

    def test_init_full_config(self):
        """Test initializing flag with full config."""
        config = {
            "enabled": True,
            "type": "percentage",
            "description": "Test flag",
            "owner": "test-team",
            "created_at": "2024-01-01T00:00:00Z",
            "jira_ticket": "TEST-123",
            "percentage": 50,
            "fallback": True,
        }

        flag = FeatureFlag("test_flag", config)

        assert flag.enabled is True
        assert flag.flag_type == FlagType.PERCENTAGE
        assert flag.description == "Test flag"
        assert flag.owner == "test-team"
        assert flag.percentage == 50
        assert flag.fallback is True

    def test_init_user_targeting_config(self):
        """Test initializing user targeting flag."""
        config = {
            "enabled": True,
            "type": "user_targeting",
            "allowed_domains": ["lukhas.ai", "example.com"],
            "allowed_user_hashes": ["abc123", "def456"],
        }

        flag = FeatureFlag("test_flag", config)

        assert flag.flag_type == FlagType.USER_TARGETING
        assert "lukhas.ai" in flag.allowed_domains
        assert "abc123" in flag.allowed_user_hashes

    def test_init_time_based_config(self):
        """Test initializing time-based flag."""
        config = {
            "enabled": True,
            "type": "time_based",
            "enable_after": "2024-01-01T00:00:00Z",
            "disable_after": "2024-12-31T23:59:59Z",
        }

        flag = FeatureFlag("test_flag", config)

        assert flag.flag_type == FlagType.TIME_BASED
        assert flag.enable_after == "2024-01-01T00:00:00Z"
        assert flag.disable_after == "2024-12-31T23:59:59Z"

    def test_init_environment_config(self):
        """Test initializing environment-based flag."""
        config = {
            "enabled": True,
            "type": "environment",
            "allowed_environments": ["dev", "staging"],
        }

        flag = FeatureFlag("test_flag", config)

        assert flag.flag_type == FlagType.ENVIRONMENT
        assert flag.allowed_environments == ["dev", "staging"]

    def test_evaluate_boolean_enabled(self):
        """Test evaluating enabled boolean flag."""
        flag = FeatureFlag("test", {"enabled": True, "type": "boolean"})
        ctx = FlagEvaluationContext()

        assert flag.evaluate(ctx) is True

    def test_evaluate_boolean_disabled(self):
        """Test evaluating disabled boolean flag."""
        flag = FeatureFlag("test", {"enabled": False})
        ctx = FlagEvaluationContext()

        assert flag.evaluate(ctx) is False

    def test_evaluate_percentage_under_threshold(self):
        """Test percentage rollout for user under threshold."""
        flag = FeatureFlag("test", {
            "enabled": True,
            "type": "percentage",
            "percentage": 100,  # 100% rollout
        })

        ctx = FlagEvaluationContext(user_id="user123")

        # With 100%, should always be enabled
        assert flag.evaluate(ctx) is True

    def test_evaluate_percentage_over_threshold(self):
        """Test percentage rollout for user over threshold."""
        flag = FeatureFlag("test", {
            "enabled": True,
            "type": "percentage",
            "percentage": 0,  # 0% rollout
        })

        ctx = FlagEvaluationContext(user_id="user123")

        # With 0%, should never be enabled
        assert flag.evaluate(ctx) is False

    def test_evaluate_percentage_no_user_id(self):
        """Test percentage rollout without user ID."""
        flag = FeatureFlag("test", {
            "enabled": True,
            "type": "percentage",
            "percentage": 50,
        })

        ctx = FlagEvaluationContext()  # No user_id

        # Without user_id, should return False
        assert flag.evaluate(ctx) is False

    def test_evaluate_percentage_consistent(self):
        """Test percentage rollout is consistent for same user."""
        flag = FeatureFlag("test", {
            "enabled": True,
            "type": "percentage",
            "percentage": 50,
        })

        ctx = FlagEvaluationContext(user_id="user123")

        # Should get same result multiple times
        result1 = flag.evaluate(ctx)
        result2 = flag.evaluate(ctx)

        assert result1 == result2

    def test_evaluate_user_targeting_by_domain(self):
        """Test user targeting by email domain."""
        flag = FeatureFlag("test", {
            "enabled": True,
            "type": "user_targeting",
            "allowed_domains": ["lukhas.ai"],
        })

        ctx = FlagEvaluationContext(email="user@lukhas.ai")

        assert flag.evaluate(ctx) is True

    def test_evaluate_user_targeting_wrong_domain(self):
        """Test user targeting with wrong domain."""
        flag = FeatureFlag("test", {
            "enabled": True,
            "type": "user_targeting",
            "allowed_domains": ["lukhas.ai"],
        })

        ctx = FlagEvaluationContext(email="user@other.com")

        assert flag.evaluate(ctx) is False

    def test_evaluate_user_targeting_by_hash(self):
        """Test user targeting by user hash."""
        user_id = "user123"
        user_hash = hashlib.sha256(user_id.encode()).hexdigest()

        flag = FeatureFlag("test", {
            "enabled": True,
            "type": "user_targeting",
            "allowed_user_hashes": [user_hash],
        })

        ctx = FlagEvaluationContext(user_id=user_id)

        assert flag.evaluate(ctx) is True

    def test_evaluate_user_targeting_wrong_hash(self):
        """Test user targeting with wrong hash."""
        flag = FeatureFlag("test", {
            "enabled": True,
            "type": "user_targeting",
            "allowed_user_hashes": ["wrong_hash"],
        })

        ctx = FlagEvaluationContext(user_id="user123")

        assert flag.evaluate(ctx) is False

    def test_evaluate_time_based_before_enable(self):
        """Test time-based flag before enable time."""
        future_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()

        flag = FeatureFlag("test", {
            "enabled": True,
            "type": "time_based",
            "enable_after": future_time,
        })

        ctx = FlagEvaluationContext()

        assert flag.evaluate(ctx) is False

    def test_evaluate_time_based_after_enable(self):
        """Test time-based flag after enable time."""
        past_time = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()

        flag = FeatureFlag("test", {
            "enabled": True,
            "type": "time_based",
            "enable_after": past_time,
        })

        ctx = FlagEvaluationContext()

        assert flag.evaluate(ctx) is True

    def test_evaluate_time_based_after_disable(self):
        """Test time-based flag after disable time."""
        past_time = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()

        flag = FeatureFlag("test", {
            "enabled": True,
            "type": "time_based",
            "disable_after": past_time,
        })

        ctx = FlagEvaluationContext()

        assert flag.evaluate(ctx) is False

    def test_evaluate_time_based_before_disable(self):
        """Test time-based flag before disable time."""
        future_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()

        flag = FeatureFlag("test", {
            "enabled": True,
            "type": "time_based",
            "disable_after": future_time,
        })

        ctx = FlagEvaluationContext()

        assert flag.evaluate(ctx) is True

    def test_evaluate_time_based_window(self):
        """Test time-based flag within time window."""
        past_time = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        future_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()

        flag = FeatureFlag("test", {
            "enabled": True,
            "type": "time_based",
            "enable_after": past_time,
            "disable_after": future_time,
        })

        ctx = FlagEvaluationContext()

        assert flag.evaluate(ctx) is True

    def test_evaluate_environment_allowed(self):
        """Test environment-based flag with allowed environment."""
        flag = FeatureFlag("test", {
            "enabled": True,
            "type": "environment",
            "allowed_environments": ["dev", "staging"],
        })

        ctx = FlagEvaluationContext(environment="dev")

        assert flag.evaluate(ctx) is True

    def test_evaluate_environment_not_allowed(self):
        """Test environment-based flag with disallowed environment."""
        flag = FeatureFlag("test", {
            "enabled": True,
            "type": "environment",
            "allowed_environments": ["dev", "staging"],
        })

        ctx = FlagEvaluationContext(environment="prod")

        assert flag.evaluate(ctx) is False

    def test_evaluate_environment_empty_list(self):
        """Test environment-based flag with empty allowed list."""
        flag = FeatureFlag("test", {
            "enabled": True,
            "type": "environment",
            "allowed_environments": [],
        })

        ctx = FlagEvaluationContext(environment="prod")

        # Empty list means all environments allowed
        assert flag.evaluate(ctx) is True

    def test_evaluate_unknown_type_uses_fallback(self):
        """Test invalid flag type during evaluation uses fallback."""
        # Create flag with valid type first
        flag = FeatureFlag("test", {
            "enabled": True,
            "type": "boolean",
            "fallback": True,
        })

        # Mock flag_type to be unknown during evaluation
        flag.flag_type = Mock()
        flag.flag_type.__eq__ = lambda self, other: False

        ctx = FlagEvaluationContext()

        with patch("lukhas.features.flags_service.logger") as mock_logger:
            result = flag.evaluate(ctx)
            assert result is True  # fallback value
            assert mock_logger.warning.called

    def test_evaluate_error_uses_fallback(self):
        """Test evaluation error uses fallback value."""
        flag = FeatureFlag("test", {
            "enabled": True,
            "type": "percentage",
            "fallback": False,
        })

        # Mock evaluation to raise error
        with patch.object(flag, "_evaluate_percentage", side_effect=Exception("Error")):
            ctx = FlagEvaluationContext(user_id="user123")
            result = flag.evaluate(ctx)

            assert result is False  # fallback value


# Test FeatureFlagsService


class TestFeatureFlagsService:
    """Tests for FeatureFlagsService class."""

    @pytest.fixture
    def temp_config(self):
        """Create temporary config file."""
        config = {
            "flags": {
                "test_flag": {
                    "enabled": True,
                    "type": "boolean",
                    "description": "Test flag",
                    "owner": "test-team",
                    "created_at": "2024-01-01T00:00:00Z",
                    "jira_ticket": "TEST-123",
                },
                "percentage_flag": {
                    "enabled": True,
                    "type": "percentage",
                    "percentage": 50,
                    "description": "Percentage rollout",
                    "owner": "test-team",
                    "created_at": "2024-01-01T00:00:00Z",
                    "jira_ticket": "TEST-124",
                },
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config, f)
            temp_path = f.name

        yield temp_path

        # Cleanup
        os.unlink(temp_path)

    def test_init_with_config_path(self, temp_config):
        """Test initializing service with config path."""
        service = FeatureFlagsService(config_path=temp_config)

        assert len(service.flags) == 2
        assert "test_flag" in service.flags
        assert "percentage_flag" in service.flags

    def test_init_missing_config(self):
        """Test initializing with missing config file."""
        with patch("lukhas.features.flags_service.logger") as mock_logger:
            service = FeatureFlagsService(config_path="/nonexistent/path.yaml")

            assert len(service.flags) == 0
            assert mock_logger.warning.called

    def test_init_cache_ttl(self, temp_config):
        """Test initializing with custom cache TTL."""
        service = FeatureFlagsService(config_path=temp_config, cache_ttl=120)

        assert service.cache_ttl == 120

    def test_is_enabled_existing_flag(self, temp_config):
        """Test checking if existing flag is enabled."""
        service = FeatureFlagsService(config_path=temp_config)

        assert service.is_enabled("test_flag") is True

    def test_is_enabled_disabled_flag(self, temp_config):
        """Test checking disabled flag."""
        # Create config with disabled flag
        config = {
            "flags": {
                "disabled_flag": {
                    "enabled": False,
                    "type": "boolean",
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config, f)
            temp_path = f.name

        try:
            service = FeatureFlagsService(config_path=temp_path)
            assert service.is_enabled("disabled_flag") is False
        finally:
            os.unlink(temp_path)

    def test_is_enabled_nonexistent_flag(self, temp_config):
        """Test checking non-existent flag returns False."""
        service = FeatureFlagsService(config_path=temp_config)

        with patch("lukhas.features.flags_service.logger") as mock_logger:
            assert service.is_enabled("nonexistent") is False
            assert mock_logger.warning.called

    def test_is_enabled_with_context(self, temp_config):
        """Test checking flag with evaluation context."""
        service = FeatureFlagsService(config_path=temp_config)
        ctx = FlagEvaluationContext(user_id="user123", environment="dev")

        result = service.is_enabled("test_flag", ctx)

        assert result is True

    def test_is_enabled_reloads_on_cache_expiry(self, temp_config):
        """Test service reloads config when cache expires."""
        service = FeatureFlagsService(config_path=temp_config, cache_ttl=1)

        # First call
        service.is_enabled("test_flag")

        # Wait for cache to expire
        time.sleep(1.1)

        # Mock reload to verify it's called
        with patch.object(service, "_load_flags") as mock_load:
            service.is_enabled("test_flag")
            assert mock_load.called

    def test_get_flag_existing(self, temp_config):
        """Test getting existing flag."""
        service = FeatureFlagsService(config_path=temp_config)

        flag = service.get_flag("test_flag")

        assert flag is not None
        assert flag.name == "test_flag"
        assert flag.enabled is True

    def test_get_flag_nonexistent(self, temp_config):
        """Test getting non-existent flag returns None."""
        service = FeatureFlagsService(config_path=temp_config)

        assert service.get_flag("nonexistent") is None

    def test_list_flags(self, temp_config):
        """Test listing all flag names."""
        service = FeatureFlagsService(config_path=temp_config)

        flags = service.list_flags()

        assert len(flags) == 2
        assert "test_flag" in flags
        assert "percentage_flag" in flags

    def test_get_all_flags(self, temp_config):
        """Test getting all flag objects."""
        service = FeatureFlagsService(config_path=temp_config)

        all_flags = service.get_all_flags()

        assert len(all_flags) == 2
        assert isinstance(all_flags["test_flag"], FeatureFlag)
        assert isinstance(all_flags["percentage_flag"], FeatureFlag)

    def test_get_all_flags_returns_copy(self, temp_config):
        """Test get_all_flags returns copy, not original."""
        service = FeatureFlagsService(config_path=temp_config)

        flags1 = service.get_all_flags()
        flags2 = service.get_all_flags()

        # Should be different objects
        assert flags1 is not flags2
        # But with same content
        assert flags1.keys() == flags2.keys()

    def test_reload(self, temp_config):
        """Test manually reloading flags."""
        service = FeatureFlagsService(config_path=temp_config)

        initial_flags = len(service.flags)

        # Modify config file
        config = {
            "flags": {
                "new_flag": {
                    "enabled": True,
                    "type": "boolean",
                }
            }
        }

        with open(temp_config, "w") as f:
            yaml.dump(config, f)

        # Reload
        service.reload()

        # Should have new flags
        assert len(service.flags) == 1
        assert "new_flag" in service.flags

    def test_load_flags_invalid_yaml(self):
        """Test loading invalid YAML handles error gracefully."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content: {{{")
            temp_path = f.name

        try:
            with patch("lukhas.features.flags_service.logger") as mock_logger:
                service = FeatureFlagsService(config_path=temp_path)

                assert len(service.flags) == 0
                assert mock_logger.error.called
        finally:
            os.unlink(temp_path)

    def test_load_flags_empty_config(self):
        """Test loading empty config."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump({}, f)
            temp_path = f.name

        try:
            service = FeatureFlagsService(config_path=temp_path)
            assert len(service.flags) == 0
        finally:
            os.unlink(temp_path)

    def test_default_config_path(self):
        """Test getting default config path."""
        service = FeatureFlagsService()

        # Should look for branding/features/flags.yaml
        assert "flags.yaml" in service.config_path


# Test Global Functions


class TestGlobalFunctions:
    """Tests for global convenience functions."""

    def test_get_service_singleton(self):
        """Test get_service returns singleton instance."""
        service1 = get_service()
        service2 = get_service()

        assert service1 is service2

    def test_is_enabled_convenience(self):
        """Test global is_enabled function."""
        with patch("lukhas.features.flags_service.get_service") as mock_get:
            mock_service = Mock()
            mock_service.is_enabled.return_value = True
            mock_get.return_value = mock_service

            result = is_enabled("test_flag")

            assert result is True
            mock_service.is_enabled.assert_called_once_with("test_flag", None)

    def test_is_enabled_with_context(self):
        """Test global is_enabled with context."""
        with patch("lukhas.features.flags_service.get_service") as mock_get:
            mock_service = Mock()
            mock_service.is_enabled.return_value = False
            mock_get.return_value = mock_service

            ctx = FlagEvaluationContext(user_id="user123")
            result = is_enabled("test_flag", ctx)

            assert result is False
            mock_service.is_enabled.assert_called_once_with("test_flag", ctx)


# Test FlagType Enum


class TestFlagType:
    """Tests for FlagType enum."""

    def test_flag_type_values(self):
        """Test FlagType enum values."""
        assert FlagType.BOOLEAN.value == "boolean"
        assert FlagType.PERCENTAGE.value == "percentage"
        assert FlagType.USER_TARGETING.value == "user_targeting"
        assert FlagType.TIME_BASED.value == "time_based"
        assert FlagType.ENVIRONMENT.value == "environment"

    def test_flag_type_from_string(self):
        """Test creating FlagType from string."""
        assert FlagType("boolean") == FlagType.BOOLEAN
        assert FlagType("percentage") == FlagType.PERCENTAGE


# Integration Tests


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_percentage_rollout_distribution(self):
        """Test percentage rollout distributes users correctly."""
        config = {
            "flags": {
                "rollout_50": {
                    "enabled": True,
                    "type": "percentage",
                    "percentage": 50,
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config, f)
            temp_path = f.name

        try:
            service = FeatureFlagsService(config_path=temp_path)

            # Test with 100 users
            enabled_count = 0
            for i in range(100):
                ctx = FlagEvaluationContext(user_id=f"user{i}")
                if service.is_enabled("rollout_50", ctx):
                    enabled_count += 1

            # Should be roughly 50% (allow 20% variance)
            assert 30 <= enabled_count <= 70
        finally:
            os.unlink(temp_path)

    def test_multi_criteria_flag(self):
        """Test flag with multiple evaluation criteria."""
        # Create a complex flag that uses environment AND time-based
        past_time = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        future_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()

        # Note: Each flag only has one type, but we can test multiple flags
        config = {
            "flags": {
                "env_flag": {
                    "enabled": True,
                    "type": "environment",
                    "allowed_environments": ["dev"],
                },
                "time_flag": {
                    "enabled": True,
                    "type": "time_based",
                    "enable_after": past_time,
                    "disable_after": future_time,
                },
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config, f)
            temp_path = f.name

        try:
            service = FeatureFlagsService(config_path=temp_path)

            # Test environment flag
            ctx_dev = FlagEvaluationContext(environment="dev")
            ctx_prod = FlagEvaluationContext(environment="prod")

            assert service.is_enabled("env_flag", ctx_dev) is True
            assert service.is_enabled("env_flag", ctx_prod) is False

            # Test time flag
            assert service.is_enabled("time_flag") is True
        finally:
            os.unlink(temp_path)
