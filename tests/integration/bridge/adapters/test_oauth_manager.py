# owner: Jules-06
# tier: tier3
# module_uid: candidate.bridge.external_adapters
# criticality: P1

import pytest

from bridge.external_adapters.oauth_manager import OAuthManager, OAuthProvider


@pytest.mark.tier3
@pytest.mark.oauth
@pytest.mark.integration
class TestOAuthManagerIntegration:
    """
    Integration tests for the OAuthManager.
    """

    @pytest.fixture
    def manager(self):
        """Returns an OAuthManager instance."""
        return OAuthManager()

    @pytest.mark.asyncio
    async def test_store_and_get_credentials(self, manager: OAuthManager):
        """Tests storing and retrieving credentials."""
        user_id = "user-oauth-test"
        provider = OAuthProvider.GOOGLE
        creds = {"access_token": "test-token", "refresh_token": "refresh-token"}

        store_success = await manager.store_credentials(user_id, provider, creds)
        retrieved_creds = await manager.get_credentials(user_id, provider)

        assert store_success is True
        assert retrieved_creds is not None
        assert retrieved_creds["access_token"] == "test-token"

    @pytest.mark.asyncio
    async def test_refresh_credentials(self, manager: OAuthManager):
        """Tests refreshing credentials."""
        user_id = "user-refresh-test"
        provider = OAuthProvider.GOOGLE
        creds = {"access_token": "old-token", "refresh_token": "old-refresh"}
        await manager.store_credentials(user_id, provider, creds)

        new_creds = await manager.refresh_credentials(user_id, provider, "old-refresh")
        assert new_creds is not None
        assert new_creds["access_token"].startswith("refreshed_token_")

    @pytest.mark.asyncio
    async def test_revoke_credentials(self, manager: OAuthManager):
        """Tests revoking credentials."""
        user_id = "user-revoke-test"
        provider = OAuthProvider.GOOGLE
        creds = {"access_token": "test-token"}
        await manager.store_credentials(user_id, provider, creds)

        assert await manager.get_credentials(user_id, provider) is not None
        await manager.revoke_credentials(user_id, provider)
        assert await manager.get_credentials(user_id, provider) is None

    @pytest.mark.asyncio
    async def test_get_user_providers(self, manager: OAuthManager):
        """Tests getting a user's providers."""
        user_id = "user-providers-test"
        await manager.store_credentials(user_id, OAuthProvider.GOOGLE, {})
        await manager.store_credentials(user_id, OAuthProvider.DROPBOX, {})

        providers = await manager.get_user_providers(user_id)
        assert set(providers) == {"google", "dropbox"}

    @pytest.mark.asyncio
    async def test_health_check(self, manager: OAuthManager):
        """Tests the health check method."""
        health = await manager.health_check()
        assert health["status"] == "healthy"
        assert health["active_tokens"] == 0

    @pytest.mark.asyncio
    async def test_get_user_providers_error(self, manager: OAuthManager, monkeypatch):
        """Tests an error when getting user providers."""

        async def mock_get_creds_error(*args, **kwargs):
            raise ValueError("Test error")

        monkeypatch.setattr(manager, "get_credentials", mock_get_creds_error)

        providers = await manager.get_user_providers("user1")
        assert providers == []

    @pytest.mark.asyncio
    async def test_health_check_error(self, manager: OAuthManager, monkeypatch):
        """Tests an error during health check."""
        await manager.store_credentials("user-health-check", OAuthProvider.GOOGLE, {})

        def mock_decrypt_error(*args, **kwargs):
            raise ValueError("Test error")

        monkeypatch.setattr(manager, "_decrypt_token_data", mock_decrypt_error)

        health = await manager.health_check()
        assert health["status"] == "healthy"
        assert health["expired_tokens"] == 1

    @pytest.mark.asyncio
    async def test_refresh_credentials_error(self, manager: OAuthManager, monkeypatch):
        """Tests an error when refreshing credentials."""

        async def mock_store_creds_error(*args, **kwargs):
            raise ValueError("Test error")

        monkeypatch.setattr(manager, "store_credentials", mock_store_creds_error)

        creds = await manager.refresh_credentials("user1", OAuthProvider.GOOGLE, "refresh-token")
        assert creds is None
