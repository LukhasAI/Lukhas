"""Unit tests for memory lifecycle management."""

import pytest
from memory.lifecycle import Lifecycle, RetentionPolicy

def test_retention_policy_defaults():
    policy = RetentionPolicy()
    assert policy.days == 30

def test_retention_policy_custom():
    policy = RetentionPolicy(days=90)
    assert policy.days == 90

def test_lifecycle_initialization():
    policy = RetentionPolicy(days=7)
    lifecycle = Lifecycle(policy)
    assert lifecycle.retention == policy
    assert lifecycle.retention.days == 7

def test_enforce_retention_not_implemented():
    policy = RetentionPolicy()
    lifecycle = Lifecycle(policy)

    with pytest.raises(NotImplementedError):
        lifecycle.enforce_retention()