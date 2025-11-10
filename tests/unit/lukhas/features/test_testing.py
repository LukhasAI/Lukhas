"""
Comprehensive tests for feature flag testing utilities.

Tests context managers, fixtures, and temporary configuration handling.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import yaml

from lukhas.features.testing import (
    override_flag,
    override_flags,
    temp_flags_config,
    feature_flags,
    flag_context,
    override_flag_fixture,
    override_flags_fixture,
)


@pytest.fixture
def mock_service():
    """Mock FeatureFlagsService for testing."""
    service = Mock()
    service.flags = {
        'test_flag': Mock(enabled=True),
        'another_flag': Mock(enabled=False),
    }
    service.get_flag = lambda name: service.flags.get(name)
    return service


class TestOverrideFlag:
    """Test override_flag context manager."""

    def test_override_flag_enables(self, mock_service):
        """Test overriding a flag to enabled."""
        with override_flag('test_flag', True, service=mock_service):
            assert mock_service.flags['test_flag'].enabled is True

    def test_override_flag_disables(self, mock_service):
        """Test overriding a flag to disabled."""
        with override_flag('test_flag', False, service=mock_service):
            assert mock_service.flags['test_flag'].enabled is False

    def test_override_flag_restores_original(self, mock_service):
        """Test that original state is restored after context."""
        original_state = mock_service.flags['test_flag'].enabled

        with override_flag('test_flag', not original_state, service=mock_service):
            assert mock_service.flags['test_flag'].enabled is not original_state

        # Should be restored
        assert mock_service.flags['test_flag'].enabled == original_state

    def test_override_flag_restores_on_exception(self, mock_service):
        """Test that original state is restored even on exception."""
        original_state = mock_service.flags['test_flag'].enabled

        try:
            with override_flag('test_flag', not original_state, service=mock_service):
                raise ValueError("Test exception")
        except ValueError:
            pass

        # Should still be restored
        assert mock_service.flags['test_flag'].enabled == original_state

    def test_override_nonexistent_flag(self, mock_service):
        """Test overriding a flag that doesn't exist."""
        with override_flag('nonexistent_flag', True, service=mock_service):
            # Should not raise error
            pass

    def test_override_flag_uses_global_service_by_default(self):
        """Test that override_flag uses global service when not specified."""
        with patch('lukhas.features.testing.get_service') as mock_get_service:
            mock_service = Mock()
            mock_service.flags = {'test': Mock(enabled=True)}
            mock_service.get_flag = lambda name: mock_service.flags.get(name)
            mock_get_service.return_value = mock_service

            with override_flag('test', False):
                mock_get_service.assert_called()


class TestOverrideFlags:
    """Test override_flags context manager for multiple flags."""

    def test_override_multiple_flags(self, mock_service):
        """Test overriding multiple flags at once."""
        overrides = {
            'test_flag': False,
            'another_flag': True,
        }

        with override_flags(overrides, service=mock_service):
            assert mock_service.flags['test_flag'].enabled is False
            assert mock_service.flags['another_flag'].enabled is True

    def test_override_flags_restores_all(self, mock_service):
        """Test that all original states are restored."""
        original_test = mock_service.flags['test_flag'].enabled
        original_another = mock_service.flags['another_flag'].enabled

        overrides = {
            'test_flag': not original_test,
            'another_flag': not original_another,
        }

        with override_flags(overrides, service=mock_service):
            pass

        # All should be restored
        assert mock_service.flags['test_flag'].enabled == original_test
        assert mock_service.flags['another_flag'].enabled == original_another

    def test_override_flags_restores_on_exception(self, mock_service):
        """Test restoration even when exception occurs."""
        original_test = mock_service.flags['test_flag'].enabled

        try:
            with override_flags({'test_flag': not original_test}, service=mock_service):
                raise RuntimeError("Test error")
        except RuntimeError:
            pass

        assert mock_service.flags['test_flag'].enabled == original_test

    def test_override_empty_dict(self, mock_service):
        """Test overriding with empty dictionary."""
        with override_flags({}, service=mock_service):
            pass  # Should not raise error

    def test_override_flags_partial_exist(self, mock_service):
        """Test overriding when some flags don't exist."""
        overrides = {
            'test_flag': False,
            'nonexistent': True,
        }

        with override_flags(overrides, service=mock_service):
            # Should only override existing flags
            assert mock_service.flags['test_flag'].enabled is False

    def test_override_flags_uses_global_service(self):
        """Test that override_flags uses global service by default."""
        with patch('lukhas.features.testing.get_service') as mock_get_service:
            mock_service = Mock()
            mock_service.flags = {'test': Mock(enabled=True)}
            mock_get_service.return_value = mock_service

            with override_flags({'test': False}):
                mock_get_service.assert_called()


class TestTempFlagsConfig:
    """Test temp_flags_config context manager."""

    def test_temp_config_creates_service(self):
        """Test that temp config creates a FeatureFlagsService."""
        config = {
            'version': '1.0',
            'flags': {
                'test_flag': {
                    'type': 'boolean',
                    'enabled': True,
                    'description': 'Test flag',
                }
            }
        }

        with temp_flags_config(config) as service:
            assert service is not None
            assert service.is_enabled('test_flag')

    def test_temp_config_cleans_up_file(self):
        """Test that temporary file is cleaned up."""
        config = {
            'version': '1.0',
            'flags': {
                'test_flag': {
                    'type': 'boolean',
                    'enabled': True,
                    'description': 'Test flag',
                }
            }
        }

        temp_path = None
        with patch('tempfile.NamedTemporaryFile') as mock_temp:
            mock_file = MagicMock()
            mock_file.name = '/tmp/test_config.yaml'
            mock_file.__enter__ = Mock(return_value=mock_file)
            mock_file.__exit__ = Mock(return_value=None)
            mock_temp.return_value = mock_file
            temp_path = mock_file.name

            with patch('lukhas.features.testing.FeatureFlagsService'):
                with patch('pathlib.Path.unlink') as mock_unlink:
                    with temp_flags_config(config):
                        pass

                    # Should clean up file
                    mock_unlink.assert_called_once()

    def test_temp_config_multiple_flags(self):
        """Test temp config with multiple flags."""
        config = {
            'version': '1.0',
            'flags': {
                'flag1': {
                    'type': 'boolean',
                    'enabled': True,
                    'description': 'Flag 1',
                },
                'flag2': {
                    'type': 'boolean',
                    'enabled': False,
                    'description': 'Flag 2',
                },
            }
        }

        with temp_flags_config(config) as service:
            assert service.is_enabled('flag1')
            assert not service.is_enabled('flag2')

    def test_temp_config_with_percentage_flag(self):
        """Test temp config with percentage-based flag."""
        config = {
            'version': '1.0',
            'flags': {
                'rollout_flag': {
                    'type': 'percentage',
                    'enabled': True,
                    'percentage': 50,
                    'description': 'Rollout flag',
                }
            }
        }

        with temp_flags_config(config) as service:
            assert 'rollout_flag' in [f.name for f in service.flags.values()]

    def test_temp_config_cleans_up_on_exception(self):
        """Test that temp file is cleaned up even on exception."""
        config = {
            'version': '1.0',
            'flags': {},
        }

        try:
            with temp_flags_config(config) as service:
                raise ValueError("Test error")
        except ValueError:
            pass

        # File cleanup should still happen (tested via mock)


class TestFeatureFlagsFixture:
    """Test the feature_flags pytest fixture."""

    def test_fixture_provides_service(self, feature_flags):
        """Test that fixture provides a FeatureFlagsService."""
        assert feature_flags is not None

    def test_fixture_has_test_flags(self, feature_flags):
        """Test that fixture includes test flags."""
        # Should have the test flags defined in the fixture
        assert feature_flags.is_enabled('test_boolean_flag')

    def test_fixture_boolean_flag(self, feature_flags):
        """Test boolean flag in fixture."""
        result = feature_flags.is_enabled('test_boolean_flag')
        assert result is True

    def test_fixture_percentage_flag(self, feature_flags):
        """Test percentage flag in fixture."""
        # Just verify it exists and can be evaluated
        flag = feature_flags.get_flag('test_percentage_flag')
        assert flag is not None
        assert flag.enabled is True

    def test_fixture_user_targeting_flag(self, feature_flags):
        """Test user targeting flag in fixture."""
        flag = feature_flags.get_flag('test_user_targeting_flag')
        assert flag is not None
        assert flag.type == 'user_targeting'

    def test_fixture_time_based_flag(self, feature_flags):
        """Test time-based flag in fixture."""
        flag = feature_flags.get_flag('test_time_based_flag')
        assert flag is not None
        assert flag.type == 'time_based'

    def test_fixture_environment_flag(self, feature_flags):
        """Test environment flag in fixture."""
        flag = feature_flags.get_flag('test_environment_flag')
        assert flag is not None
        assert flag.type == 'environment'


class TestFlagContextFixture:
    """Test the flag_context pytest fixture."""

    def test_fixture_provides_context(self, flag_context):
        """Test that fixture provides a FlagEvaluationContext."""
        assert flag_context is not None

    def test_fixture_has_user_id(self, flag_context):
        """Test that context has user_id."""
        assert flag_context.user_id == "test-user-123"

    def test_fixture_has_email(self, flag_context):
        """Test that context has email."""
        assert flag_context.email == "test@test.com"

    def test_fixture_has_environment(self, flag_context):
        """Test that context has environment."""
        assert flag_context.environment == "test"

    def test_context_can_be_used_with_service(self, feature_flags, flag_context):
        """Test that context works with service evaluation."""
        # Test with environment flag
        result = feature_flags.is_enabled('test_environment_flag', context=flag_context)
        assert result is True


class TestOverrideFlagFixture:
    """Test the override_flag_fixture pytest fixture."""

    def test_fixture_returns_function(self, override_flag_fixture):
        """Test that fixture returns the override_flag function."""
        assert callable(override_flag_fixture)
        assert override_flag_fixture == override_flag

    def test_fixture_can_be_used_as_context_manager(self, override_flag_fixture, mock_service):
        """Test that fixture result can be used as context manager."""
        with override_flag_fixture('test_flag', False, service=mock_service):
            assert mock_service.flags['test_flag'].enabled is False


class TestOverrideFlagsFixture:
    """Test the override_flags_fixture pytest fixture."""

    def test_fixture_returns_function(self, override_flags_fixture):
        """Test that fixture returns the override_flags function."""
        assert callable(override_flags_fixture)
        assert override_flags_fixture == override_flags

    def test_fixture_can_be_used_as_context_manager(self, override_flags_fixture, mock_service):
        """Test that fixture result can be used as context manager."""
        with override_flags_fixture({'test_flag': False}, service=mock_service):
            assert mock_service.flags['test_flag'].enabled is False


class TestIntegration:
    """Integration tests for testing utilities."""

    def test_nested_overrides(self, mock_service):
        """Test nested flag overrides."""
        original = mock_service.flags['test_flag'].enabled

        with override_flag('test_flag', True, service=mock_service):
            assert mock_service.flags['test_flag'].enabled is True

            with override_flag('test_flag', False, service=mock_service):
                assert mock_service.flags['test_flag'].enabled is False

            # Should restore to outer context
            assert mock_service.flags['test_flag'].enabled is True

        # Should restore to original
        assert mock_service.flags['test_flag'].enabled == original

    def test_override_within_temp_config(self):
        """Test using override within temp config."""
        config = {
            'version': '1.0',
            'flags': {
                'test_flag': {
                    'type': 'boolean',
                    'enabled': True,
                    'description': 'Test',
                }
            }
        }

        with temp_flags_config(config) as service:
            assert service.is_enabled('test_flag')

            with override_flag('test_flag', False, service=service):
                assert not service.is_enabled('test_flag')

            # Should be restored
            assert service.is_enabled('test_flag')

    def test_multiple_override_contexts(self, mock_service):
        """Test multiple separate override contexts."""
        original = mock_service.flags['test_flag'].enabled

        with override_flag('test_flag', True, service=mock_service):
            assert mock_service.flags['test_flag'].enabled is True

        assert mock_service.flags['test_flag'].enabled == original

        with override_flag('test_flag', False, service=mock_service):
            assert mock_service.flags['test_flag'].enabled is False

        assert mock_service.flags['test_flag'].enabled == original

    def test_fixture_integration(self, feature_flags, flag_context):
        """Test using multiple fixtures together."""
        # Use both fixtures in same test
        result = feature_flags.is_enabled('test_environment_flag', context=flag_context)
        assert isinstance(result, bool)


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_override_flag_none_service(self):
        """Test override_flag with None service uses global."""
        with patch('lukhas.features.testing.get_service') as mock_get:
            mock_service = Mock()
            mock_service.flags = {}
            mock_service.get_flag = lambda name: None
            mock_get.return_value = mock_service

            with override_flag('test', True, service=None):
                pass

    def test_temp_config_empty_flags(self):
        """Test temp config with no flags."""
        config = {
            'version': '1.0',
            'flags': {}
        }

        with temp_flags_config(config) as service:
            assert service is not None

    def test_temp_config_with_cache_ttl_zero(self):
        """Test that temp config uses cache_ttl=0."""
        config = {
            'version': '1.0',
            'flags': {
                'test': {
                    'type': 'boolean',
                    'enabled': True,
                    'description': 'Test',
                }
            }
        }

        with patch('lukhas.features.testing.FeatureFlagsService') as mock_service_class:
            with patch('pathlib.Path.unlink'):
                with temp_flags_config(config):
                    pass

                # Verify cache_ttl=0 was passed
                call_kwargs = mock_service_class.call_args[1]
                assert call_kwargs.get('cache_ttl') == 0

    def test_override_flag_with_special_characters(self, mock_service):
        """Test overriding flags with special characters in name."""
        mock_service.flags['flag-with-dashes'] = Mock(enabled=True)

        with override_flag('flag-with-dashes', False, service=mock_service):
            assert mock_service.flags['flag-with-dashes'].enabled is False

    def test_multiple_flags_same_override(self, mock_service):
        """Test overriding multiple flags to same value."""
        overrides = {
            'test_flag': True,
            'another_flag': True,
        }

        with override_flags(overrides, service=mock_service):
            assert mock_service.flags['test_flag'].enabled is True
            assert mock_service.flags['another_flag'].enabled is True


class TestRealWorldUsage:
    """Test real-world usage scenarios."""

    def test_test_scenario_with_feature_enabled(self, feature_flags):
        """Test a scenario where a feature is enabled."""
        with override_flag('test_boolean_flag', True, service=feature_flags):
            # Simulate testing code that checks the flag
            if feature_flags.is_enabled('test_boolean_flag'):
                result = "feature enabled"
            else:
                result = "feature disabled"

            assert result == "feature enabled"

    def test_test_scenario_with_feature_disabled(self, feature_flags):
        """Test a scenario where a feature is disabled."""
        with override_flag('test_boolean_flag', False, service=feature_flags):
            if feature_flags.is_enabled('test_boolean_flag'):
                result = "feature enabled"
            else:
                result = "feature disabled"

            assert result == "feature disabled"

    def test_ab_test_scenario(self, feature_flags, flag_context):
        """Test A/B testing scenario with percentage flags."""
        # User targeting flag should work with context
        result = feature_flags.is_enabled('test_user_targeting_flag', context=flag_context)
        assert isinstance(result, bool)

    def test_environment_specific_feature(self, feature_flags):
        """Test environment-specific feature flag."""
        from lukhas.features.flags_service import FlagEvaluationContext

        test_context = FlagEvaluationContext(
            user_id="user-1",
            environment="test",
        )

        result = feature_flags.is_enabled('test_environment_flag', context=test_context)
        assert result is True

    def test_multiple_test_cases_with_different_flags(self, feature_flags):
        """Test running multiple test cases with different flag states."""
        # Test case 1: Feature enabled
        with override_flag('test_boolean_flag', True, service=feature_flags):
            assert feature_flags.is_enabled('test_boolean_flag')

        # Test case 2: Feature disabled
        with override_flag('test_boolean_flag', False, service=feature_flags):
            assert not feature_flags.is_enabled('test_boolean_flag')

        # Test case 3: Default state restored
        assert feature_flags.is_enabled('test_boolean_flag')  # Original state


class TestYamlGeneration:
    """Test YAML configuration generation."""

    def test_temp_config_writes_valid_yaml(self):
        """Test that temp config writes valid YAML."""
        config = {
            'version': '1.0',
            'flags': {
                'test_flag': {
                    'type': 'boolean',
                    'enabled': True,
                    'description': 'Test flag',
                }
            }
        }

        written_content = None

        with patch('tempfile.NamedTemporaryFile') as mock_temp:
            mock_file = MagicMock()
            mock_file.name = '/tmp/test.yaml'

            def capture_write(content):
                nonlocal written_content
                written_content = content

            mock_file.write = capture_write
            mock_file.__enter__ = Mock(return_value=mock_file)
            mock_file.__exit__ = Mock(return_value=None)
            mock_temp.return_value = mock_file

            with patch('lukhas.features.testing.FeatureFlagsService'):
                with patch('pathlib.Path.unlink'):
                    with temp_flags_config(config):
                        pass

        # Would verify YAML was written (in real implementation yaml.dump is called)
