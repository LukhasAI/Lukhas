"""Test core bridge exports and contract."""
import pytest


def test_identity_bridge_exports():
    """Verify core.identity bridge exports IdentityManager."""
    from core.identity import IdentityManager

    # Verify class exists
    assert IdentityManager is not None


def test_identity_single_source_of_truth():
    """Verify IdentityManager comes from candidate.core.identity."""
    from labs.core.identity import IdentityManager as canonical_manager
    from core.identity import IdentityManager as bridge_manager

    # Should be same class
    assert bridge_manager is canonical_manager


def test_ethics_bridge_exports():
    """Verify core.ethics bridge exports ethics module."""
    from core.ethics import ethics

    # Should be a module
    assert hasattr(ethics, '__file__')


def test_policy_guard_bridge_exports():
    """Verify core.policy_guard bridge exports expected symbols."""
    from core.policy_guard import PolicyGuard, PolicyResult, ReplayDecision

    # Verify classes/enums exist
    assert PolicyGuard is not None
    assert PolicyResult is not None
    assert ReplayDecision is not None


def test_policy_guard_single_source_of_truth():
    """Verify PolicyGuard comes from lukhas_website.core.policy_guard."""
    from core.policy_guard import PolicyGuard as bridge_guard
    from lukhas_website.core.policy_guard import PolicyGuard as canonical_guard

    # Should be same class
    assert bridge_guard is canonical_guard
