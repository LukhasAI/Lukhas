import pytest
from unittest.mock import patch, mock_open, MagicMock
import sys
from datetime import datetime, timezone, timedelta

# Mock the non-existent dependency before importing the module under test
mock_core = MagicMock()
sys.modules['identity.core'] = mock_core
sys.modules['identity.core.user_tier_mapping'] = mock_core.user_tier_mapping


from identity.tier_system import (
    DynamicTierSystem,
    TierLevel,
    AccessType,
    PermissionScope,
    AccessContext,
    lukhas_tier_required,
)

@pytest.fixture
def tier_system():
    """Provides a clean instance of DynamicTierSystem for each test."""
    # Patch the file I/O operations to prevent writing logs to disk
    with patch('os.makedirs'), \
         patch('builtins.open', mock_open()):
        system = DynamicTierSystem()
        # Clear active sessions to ensure test isolation
        system.active_sessions = {}
        yield system

@pytest.fixture
def mock_approval(monkeypatch):
    """Fixture to mock the _has_approval method."""
    mock = MagicMock(return_value=True)
    monkeypatch.setattr(DynamicTierSystem, '_has_approval', mock)
    return mock

@pytest.fixture
def mock_user_tier():
    """Fixture to easily mock the user's tier level."""
    def _mock_tier(tier_level):
        # The function inside DynamicTierSystem expects a string like "LAMBDA_TIER_X"
        tier_map = {
            TierLevel.PUBLIC: "LAMBDA_TIER_0",
            TierLevel.AUTHENTICATED: "LAMBDA_TIER_1",
            TierLevel.ELEVATED: "LAMBDA_TIER_2",
            TierLevel.PRIVILEGED: "LAMBDA_TIER_3",
            TierLevel.ADMIN: "LAMBDA_TIER_4",
            TierLevel.SYSTEM: "LAMBDA_TIER_5",
        }
        mock_get_user_tier = MagicMock(return_value=tier_map.get(tier_level, "LAMBDA_TIER_0"))
        mock_core.user_tier_mapping.get_user_tier = mock_get_user_tier
        return mock_get_user_tier

    return _mock_tier

def create_access_context(
    user_id,
    operation_type,
    resource_scope,
    session_id=None,
    resource_id="test_resource",
    metadata=None,
):
    """Helper function to create an AccessContext object."""
    return AccessContext(
        user_id=user_id,
        session_id=session_id,
        operation_type=operation_type,
        resource_scope=resource_scope,
        resource_id=resource_id,
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        metadata=metadata or {},
    )

# --- Tier 0: PUBLIC ---
def test_tier_0_public_can_read_semantic_memory(tier_system, mock_user_tier):
    mock_user_tier(TierLevel.PUBLIC)
    context = create_access_context(
        user_id=None,
        operation_type=AccessType.READ,
        resource_scope=PermissionScope.MEMORY_FOLD,
        metadata={"memory_type": "semantic"},
    )
    decision = tier_system.check_access(context, TierLevel.PUBLIC)
    assert decision.granted
    assert decision.reasoning == "Access granted for tier PUBLIC"

def test_tier_0_public_cannot_write_memory(tier_system, mock_user_tier):
    mock_user_tier(TierLevel.PUBLIC)
    context = create_access_context(
        user_id=None,
        operation_type=AccessType.WRITE,
        resource_scope=PermissionScope.MEMORY_FOLD,
    )
    decision = tier_system.check_access(context, TierLevel.PUBLIC)
    assert not decision.granted
    assert decision.reasoning == f"Operation {AccessType.WRITE.value} not allowed for tier PUBLIC"

# --- Tier 1: AUTHENTICATED ---
def test_tier_1_authenticated_can_write_to_memory(tier_system, mock_user_tier):
    mock_user_tier(TierLevel.AUTHENTICATED)
    context = create_access_context(
        user_id="user123",
        operation_type=AccessType.WRITE,
        resource_scope=PermissionScope.MEMORY_FOLD,
    )
    decision = tier_system.check_access(context, TierLevel.AUTHENTICATED)
    assert decision.granted

def test_tier_1_authenticated_cannot_access_system_memory(tier_system, mock_user_tier):
    mock_user_tier(TierLevel.AUTHENTICATED)
    context = create_access_context(
        user_id="user123",
        operation_type=AccessType.READ,
        resource_scope=PermissionScope.MEMORY_FOLD,
        metadata={"memory_type": "system"},
    )
    decision = tier_system.check_access(context, TierLevel.AUTHENTICATED)
    assert not decision.granted
    assert "memory_type_system_restricted" in decision.restrictions

# --- Tier 2: ELEVATED ---
def test_tier_2_elevated_can_modify_memory(tier_system, mock_user_tier):
    mock_user_tier(TierLevel.ELEVATED)
    context = create_access_context(
        user_id="elevated_user",
        operation_type=AccessType.MODIFY,
        resource_scope=PermissionScope.MEMORY_FOLD,
    )
    decision = tier_system.check_access(context, TierLevel.ELEVATED)
    assert decision.granted

def test_tier_2_elevated_can_read_lineage_data(tier_system, mock_user_tier):
    mock_user_tier(TierLevel.ELEVATED)
    context = create_access_context(
        user_id="elevated_user",
        operation_type=AccessType.READ,
        resource_scope=PermissionScope.LINEAGE_DATA,
    )
    decision = tier_system.check_access(context, TierLevel.ELEVATED)
    assert decision.granted

# --- Tier 3: PRIVILEGED ---
def test_tier_3_privileged_delete_requires_approval(tier_system, mock_user_tier):
    mock_user_tier(TierLevel.PRIVILEGED)
    context = create_access_context(
        user_id="priv_user",
        operation_type=AccessType.DELETE,
        resource_scope=PermissionScope.MEMORY_FOLD,
    )
    # Un-mock the approval for this specific test
    with patch.object(tier_system, '_has_approval', return_value=False):
        decision = tier_system.check_access(context, TierLevel.PRIVILEGED)
        assert not decision.granted
        assert "approval_required" in decision.restrictions


def test_tier_3_privileged_can_modify_governance_rules(tier_system, mock_user_tier, mock_approval):
    mock_user_tier(TierLevel.PRIVILEGED)
    context = create_access_context(
        user_id="priv_user",
        operation_type=AccessType.MODIFY,
        resource_scope=PermissionScope.GOVERNANCE_RULES,
    )
    decision = tier_system.check_access(context, TierLevel.PRIVILEGED)
    assert decision.granted


# --- Tier 4: ADMIN ---
def test_tier_4_admin_requires_approval(tier_system, mock_user_tier):
    mock_user_tier(TierLevel.ADMIN)
    context = create_access_context(
        user_id="admin_user",
        operation_type=AccessType.WRITE,
        resource_scope=PermissionScope.SYSTEM_CONFIG,
    )
    with patch.object(tier_system, '_has_approval', return_value=False):
        decision = tier_system.check_access(context, TierLevel.ADMIN)
        assert not decision.granted
        assert "approval_required" in decision.restrictions


# --- Tier 5: SYSTEM ---
def test_tier_5_system_has_unrestricted_access(tier_system, mock_user_tier):
    mock_user_tier(TierLevel.SYSTEM)
    context = create_access_context(
        user_id="system_agent",
        operation_type=AccessType.ADMIN,
        resource_scope=PermissionScope.SYSTEM_CONFIG,
    )
    # The _has_approval mock returns True for system users, so this should pass
    decision = tier_system.check_access(context, TierLevel.SYSTEM)
    assert decision.granted

# --- Capability Enforcement ---
def test_check_access_denies_insufficient_tier(tier_system, mock_user_tier):
    mock_user_tier(TierLevel.AUTHENTICATED)
    context = create_access_context("user123", AccessType.READ, PermissionScope.MEMORY_FOLD)
    decision = tier_system.check_access(context, TierLevel.ADMIN)
    assert not decision.granted
    assert decision.requires_elevation
    assert "Insufficient tier level" in decision.reasoning

def test_decorator_grants_access_for_sufficient_tier(mock_user_tier, mock_approval):
    mock_user_tier(TierLevel.PRIVILEGED)

    @lukhas_tier_required(TierLevel.PRIVILEGED)
    def protected_function(user_id=None):
        return "success"

    assert protected_function(user_id="priv_user") == "success"

def test_decorator_denies_access_for_insufficient_tier(mock_user_tier):
    mock_user_tier(TierLevel.AUTHENTICATED)

    @lukhas_tier_required(TierLevel.ADMIN)
    def protected_function(user_id="user123"):
        return "success"

    with pytest.raises(PermissionError, match="Access denied: Insufficient tier level"):
        protected_function()

# --- Tier Promotion/Demotion ---
def test_elevate_session_successfully(tier_system, mock_user_tier, mock_approval):
    mock_user_tier(TierLevel.AUTHENTICATED)
    session_id = "session123"
    user_id = "user123"

    # First, confirm the user is at the base tier
    context = create_access_context(user_id, AccessType.READ, PermissionScope.MEMORY_FOLD, session_id=session_id)
    base_decision = tier_system.check_access(context, TierLevel.AUTHENTICATED)
    assert base_decision.granted and base_decision.tier_level == TierLevel.AUTHENTICATED

    # Elevate the session
    result = tier_system.elevate_session(session_id, TierLevel.PRIVILEGED, "test justification")
    assert result["success"]
    assert result["tier_level"] == "PRIVILEGED"

    # Verify the new tier is active
    context.operation_type = AccessType.MODIFY # MODIFY is allowed at ELEVATED without extra approval
    elevated_decision = tier_system.check_access(context, TierLevel.ELEVATED)
    assert elevated_decision.granted and elevated_decision.tier_level == TierLevel.PRIVILEGED

def test_elevate_session_fails_if_target_is_not_higher(tier_system, mock_user_tier):
    mock_user_tier(TierLevel.ELEVATED)
    # The session does not exist, so the base tier will be PUBLIC
    result = tier_system.elevate_session("s1", TierLevel.ELEVATED, "j")
    assert result["success"]

    # Now that the session is elevated, trying to elevate again to the same or lower tier should fail
    result2 = tier_system.elevate_session("s1", TierLevel.ELEVATED, "j2")
    assert not result2["success"]
    assert "not higher than current" in result2["reason"]

def test_elevated_session_expires(tier_system, mock_user_tier):
    mock_user_tier(TierLevel.AUTHENTICATED)
    session_id = "expiring_session"
    user_id = "user123"

    # Elevate for a very short duration
    with patch('identity.tier_system.datetime') as mock_dt:
        start_time = datetime.now(timezone.utc)
        mock_dt.now.return_value = start_time
        tier_system.elevate_session(session_id, TierLevel.ADMIN, "expiring test", duration_minutes=-1)

    # Verify the session is expired
    context = create_access_context(user_id, AccessType.READ, PermissionScope.MEMORY_FOLD, session_id=session_id)
    decision = tier_system.check_access(context, TierLevel.ADMIN)
    assert not decision.granted
    assert decision.tier_level == TierLevel.AUTHENTICATED # Should revert to base tier

# --- Performance ---
def test_check_access_performance(tier_system, mock_user_tier, benchmark):
    mock_user_tier(TierLevel.AUTHENTICATED)
    context = create_access_context("user123", AccessType.READ, PermissionScope.MEMORY_FOLD)

    def run_check():
        tier_system.check_access(context, TierLevel.AUTHENTICATED)

    benchmark(run_check)

    # Calculate p95 from the raw data
    import numpy as np
    p95 = np.percentile(benchmark.stats.stats.data, 95)

    assert p95 < 0.1  # Assert p95 is less than 100ms

# --- Miscellaneous ---
def test_get_current_tier_fallback_logic(tier_system, monkeypatch):
    # Test the fallback logic when the user_tier_mapping module is not available
    monkeypatch.setitem(sys.modules, 'identity.core.user_tier_mapping', None)

    assert tier_system._get_current_tier("system_user", None) == TierLevel.SYSTEM
    assert tier_system._get_current_tier("admin_user", None) == TierLevel.ADMIN
    assert tier_system._get_current_tier("normal_user", None) == TierLevel.AUTHENTICATED
    assert tier_system._get_current_tier(None, None) == TierLevel.PUBLIC

def test_symbolic_access_test_runs_without_error(tier_system):
    # Test the standalone symbolic_access_test function
    from identity.tier_system import symbolic_access_test
    # This test is primarily to ensure it doesn't crash and to get coverage.
    symbolic_access_test()

def test_check_access_level_stub(tier_system):
    # Test the minimal stub function for Tier 5 operations
    from identity.tier_system import check_access_level
    assert not check_access_level({"tier": 4}, "Tier5Operation")
    assert check_access_level({"tier": 5}, "Tier5Operation")
    assert check_access_level({}, "SomeOtherOperation")

def test_no_permissions_defined_for_scope(tier_system, mock_user_tier):
    mock_user_tier(TierLevel.PUBLIC)
    context = create_access_context(
        user_id=None,
        operation_type=AccessType.READ,
        resource_scope=PermissionScope.AUDIT_LOGS, # No permissions for PUBLIC tier
    )
    decision = tier_system.check_access(context, TierLevel.PUBLIC)
    assert not decision.granted
    assert "No permissions defined for scope" in decision.reasoning

def test_log_elevation_exception(tier_system, mock_user_tier):
    mock_user_tier(TierLevel.AUTHENTICATED)
    with patch('builtins.open', mock_open()) as mock_file:
        mock_file.side_effect = IOError("Failed to write")
        result = tier_system.elevate_session("s1", TierLevel.ELEVATED, "j")
        assert result["success"]

def test_decorator_with_system_tier(mock_user_tier, mock_approval):
    mock_user_tier(TierLevel.SYSTEM)

    @lukhas_tier_required(TierLevel.SYSTEM)
    def protected_function(user_id=None):
        return "success"

    assert protected_function(user_id="system_user") == "success"

def test_expired_session_reverts_to_base_tier(tier_system, mock_user_tier):
    mock_user_tier(TierLevel.AUTHENTICATED)
    session_id = "s1"
    tier_system.active_sessions[session_id] = {
        "tier_level": TierLevel.ADMIN.value,
        "expires_at": datetime.now(timezone.utc) - timedelta(minutes=1)
    }
    assert tier_system._get_current_tier("user123", session_id) == TierLevel.AUTHENTICATED

def test_memory_type_restriction(tier_system, mock_user_tier):
    mock_user_tier(TierLevel.PUBLIC)
    context = create_access_context(
        user_id=None,
        operation_type=AccessType.READ,
        resource_scope=PermissionScope.MEMORY_FOLD,
        metadata={"memory_type": "system"}, # Not allowed for PUBLIC
    )
    decision = tier_system.check_access(context, TierLevel.PUBLIC)
    assert not decision.granted
    assert "memory_type_system_not_allowed" in decision.restrictions

def test_create_tier_system_factory():
    from identity.tier_system import create_tier_system
    system = create_tier_system()
    assert isinstance(system, DynamicTierSystem)

def test_get_tier_system_instance():
    from identity.tier_system import _get_tier_system_instance
    instance1 = _get_tier_system_instance()
    instance2 = _get_tier_system_instance()
    assert instance1 is instance2
    assert isinstance(instance1, DynamicTierSystem)
