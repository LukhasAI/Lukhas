from __future__ import annotations

import pytest
from core.identity.vault.lukhas_id import (
    IdentityManager,
    IdentityProfile,
    IdentityRateLimitExceeded,
    LukhasIdentityVault,
)


@pytest.mark.asyncio
async def test_get_user_identity_returns_profile() -> None:
    vault = LukhasIdentityVault()
    profile = IdentityProfile(
        user_id="tester",
        tier_level=2,
        attributes={"display_name": "Tester"},
        scopes={"core:read"},
        api_keys={"sk_live_std_test1234"},
    )
    await vault.register_identity(profile)

    manager = IdentityManager(vault=vault)
    resolved = await manager.get_user_identity("tester")

    assert resolved.user_id == "tester"
    assert resolved.tier_level == 2
    assert resolved.attributes["display_name"] == "Tester"


@pytest.mark.asyncio
async def test_authenticate_api_key_enforces_rate_limit() -> None:
    vault = LukhasIdentityVault()
    profile = IdentityProfile(
        user_id="rate_user",
        tier_level=0,
        attributes={},
        scopes=set(),
        api_keys={"sk_live_std_rate0001"},
    )
    await vault.register_identity(profile)

    manager = IdentityManager(vault=vault)
    manager.RATE_LIMITS_PER_MINUTE[profile.tier_level] = 1

    await manager.authenticate_api_key("sk_live_std_rate0001")

    with pytest.raises(IdentityRateLimitExceeded):
        await manager.authenticate_api_key("sk_live_std_rate0001")


@pytest.mark.asyncio
async def test_describe_permissions_returns_active_sessions() -> None:
    vault = LukhasIdentityVault()
    profile = IdentityProfile(
        user_id="dash_user",
        tier_level=3,
        attributes={"display_name": "Dash"},
        scopes={"core:read", "identity:manage"},
        api_keys={"sk_live_admin_dash0002"},
    )
    await vault.register_identity(profile)

    manager = IdentityManager(vault=vault)
    await manager.start_session("dash_user", "session::dash::1")
    permissions = await manager.describe_permissions("dash_user")

    assert permissions["user_id"] == "dash_user"
    assert permissions["tier_level"] == 3
    assert "session::dash::1" in permissions["active_sessions"]
