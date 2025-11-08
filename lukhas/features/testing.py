"""
Testing utilities for feature flags.

Provides context managers and fixtures for overriding feature flags in tests.
"""

import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Iterator, Optional

import pytest
import yaml

from lukhas.features.flags_service import (
    FlagEvaluationContext,
    FeatureFlagsService,
    get_service,
)


@contextmanager
def override_flag(
    flag_name: str,
    enabled: bool,
    service: Optional[FeatureFlagsService] = None,
) -> Iterator[None]:
    """
    Context manager to temporarily override a feature flag.

    Args:
        flag_name: Name of the flag to override
        enabled: Whether the flag should be enabled
        service: Optional service instance (defaults to global service)

    Example:
        ```python
        with override_flag('reasoning_lab_enabled', True):
            # Test code with flag enabled
            assert is_enabled('reasoning_lab_enabled')
        ```
    """
    svc = service or get_service()

    # Get original flag state
    original_flag = svc.get_flag(flag_name)
    original_enabled = original_flag.enabled if original_flag else False

    try:
        # Override flag
        if flag_name in svc.flags:
            svc.flags[flag_name].enabled = enabled
        yield

    finally:
        # Restore original state
        if flag_name in svc.flags:
            svc.flags[flag_name].enabled = original_enabled


@contextmanager
def override_flags(
    flags: Dict[str, bool],
    service: Optional[FeatureFlagsService] = None,
) -> Iterator[None]:
    """
    Context manager to temporarily override multiple feature flags.

    Args:
        flags: Dictionary of flag names to enabled states
        service: Optional service instance (defaults to global service)

    Example:
        ```python
        with override_flags({
            'reasoning_lab_enabled': True,
            'matriz_v2_rollout': False,
        }):
            # Test code with flags overridden
            assert is_enabled('reasoning_lab_enabled')
            assert not is_enabled('matriz_v2_rollout')
        ```
    """
    svc = service or get_service()

    # Store original states
    original_states = {}
    for flag_name in flags:
        if flag_name in svc.flags:
            original_states[flag_name] = svc.flags[flag_name].enabled

    try:
        # Override flags
        for flag_name, enabled in flags.items():
            if flag_name in svc.flags:
                svc.flags[flag_name].enabled = enabled
        yield

    finally:
        # Restore original states
        for flag_name, enabled in original_states.items():
            svc.flags[flag_name].enabled = enabled


@contextmanager
def temp_flags_config(flags_config: Dict[str, Any]) -> Iterator[FeatureFlagsService]:
    """
    Context manager to create a temporary flags configuration.

    Args:
        flags_config: Dictionary of flag configurations

    Yields:
        FeatureFlagsService instance with temporary config

    Example:
        ```python
        config = {
            'flags': {
                'test_flag': {
                    'type': 'boolean',
                    'enabled': True,
                    'description': 'Test flag',
                }
            }
        }
        with temp_flags_config(config) as service:
            assert service.is_enabled('test_flag')
        ```
    """
    # Create temporary config file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(flags_config, f)
        temp_path = f.name

    try:
        # Create service with temporary config
        service = FeatureFlagsService(config_path=temp_path, cache_ttl=0)
        yield service

    finally:
        # Clean up temporary file
        Path(temp_path).unlink(missing_ok=True)


# Pytest fixtures


@pytest.fixture
def feature_flags() -> FeatureFlagsService:
    """
    Pytest fixture for feature flags service.

    Returns:
        FeatureFlagsService instance for testing
    """
    # Create test config
    config = {
        "version": "1.0",
        "flags": {
            "test_boolean_flag": {
                "type": "boolean",
                "enabled": True,
                "description": "Test boolean flag",
            },
            "test_percentage_flag": {
                "type": "percentage",
                "enabled": True,
                "percentage": 50,
                "description": "Test percentage flag",
            },
            "test_user_targeting_flag": {
                "type": "user_targeting",
                "enabled": True,
                "allowed_domains": ["test.com"],
                "description": "Test user targeting flag",
            },
            "test_time_based_flag": {
                "type": "time_based",
                "enabled": True,
                "enable_after": "2000-01-01T00:00:00Z",
                "disable_after": "2099-12-31T23:59:59Z",
                "description": "Test time-based flag",
            },
            "test_environment_flag": {
                "type": "environment",
                "enabled": True,
                "allowed_environments": ["test"],
                "description": "Test environment flag",
            },
        },
    }

    with temp_flags_config(config) as service:
        yield service


@pytest.fixture
def flag_context() -> FlagEvaluationContext:
    """
    Pytest fixture for flag evaluation context.

    Returns:
        FlagEvaluationContext for testing
    """
    return FlagEvaluationContext(
        user_id="test-user-123",
        email="test@test.com",
        environment="test",
    )


@pytest.fixture
def override_flag_fixture():
    """
    Pytest fixture that returns the override_flag context manager.

    Returns:
        Function to create override_flag context manager
    """
    return override_flag


@pytest.fixture
def override_flags_fixture():
    """
    Pytest fixture that returns the override_flags context manager.

    Returns:
        Function to create override_flags context manager
    """
    return override_flags
