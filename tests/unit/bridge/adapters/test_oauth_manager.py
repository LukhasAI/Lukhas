# owner: Jules-06
# tier: tier3
# module_uid: candidate.bridge.external_adapters
# criticality: P1

import pytest

from candidate.bridge.external_adapters.oauth_manager import OAuthManager, OAuthProvider


@pytest.mark.tier3
@pytest.mark.oauth
@pytest.mark.unit
class TestOAuthManagerUnit:
    """
    Unit tests for the OAuthManager.
    """

    @pytest.fixture
    def manager(self):
        """Returns an OAuthManager instance."""
        return OAuthManager()

    def test_state_generation_and_validation(self, manager: OAuthManager):
        """Tests the CSRF state generation and validation logic."""
        user_id = "user-state-test"
        provider = OAuthProvider.DROPBOX

        state = manager.generate_auth_state(user_id, provider)
        is_valid = manager.validate_auth_state(state, user_id, provider)
        is_invalid_after_use = manager.validate_auth_state(state, user_id, provider)

        assert isinstance(state, str)
        assert len(state) > 30
        assert is_valid is True
        assert is_invalid_after_use is False

    def test_validate_auth_state_errors(self, manager: OAuthManager):
        """Tests error conditions for state validation."""
        assert manager.validate_auth_state("non-existent-state", "user", OAuthProvider.GOOGLE) is False

        state = manager.generate_auth_state("user", OAuthProvider.GOOGLE)
        assert manager.validate_auth_state(state, "wrong-user", OAuthProvider.GOOGLE) is False

    @pytest.mark.asyncio
    async def test_rate_limiting(self, manager: OAuthManager):
        """Tests the auth rate limiting."""
        manager.max_attempts_per_hour = 2
        assert manager._check_auth_rate_limit("rate-limit-user") is True
        assert manager._check_auth_rate_limit("rate-limit-user") is True
        assert manager._check_auth_rate_limit("rate-limit-user") is False

    def test_decrypt_token_data_error(self, manager: OAuthManager):
        """Tests an error when decrypting token data."""
        with pytest.raises(ValueError):
            manager._decrypt_token_data("invalid.data")

    def test_encrypt_token_data_error(self, manager: OAuthManager, monkeypatch):
        """Tests an error when encrypting token data."""

        def mock_json_dumps_error(*args, **kwargs):
            raise TypeError("Test error")

        monkeypatch.setattr("json.dumps", mock_json_dumps_error)

        with pytest.raises(TypeError):
            manager._encrypt_token_data({"test": "data"})

    def test_decrypt_token_data_invalid_signature(self, manager: OAuthManager):
        """Tests an error when decrypting token data with an invalid signature."""
        encrypted = manager._encrypt_token_data({"test": "data"})
        parts = encrypted.split(".")
        invalid_encrypted = f"{parts[0]}.invalidsignature"
        with pytest.raises(ValueError):
            manager._decrypt_token_data(invalid_encrypted)

    def test_generate_auth_state_error(self, manager: OAuthManager, monkeypatch):
        """Tests an error when generating auth state."""

        def mock_token_urlsafe_error(*args, **kwargs):
            raise ValueError("Test error")

        monkeypatch.setattr("secrets.token_urlsafe", mock_token_urlsafe_error)

        with pytest.raises(ValueError):
            manager.generate_auth_state("user", OAuthProvider.GOOGLE)

    def test_validate_auth_state_invalid_format(self, manager: OAuthManager):
        """Tests an error when validating auth state with an invalid format."""
        assert manager.validate_auth_state("invalid-state", "user", OAuthProvider.GOOGLE) is False

    @pytest.mark.asyncio
    async def test_get_credentials_invalid_signature(self, manager: OAuthManager):
        """Tests getting credentials with an invalid signature."""
        encrypted = manager._encrypt_token_data({"test": "data"})
        parts = encrypted.split(".")
        invalid_encrypted = f"{parts[0]}.invalidsignature"
        manager.token_store["user1:google"] = {"encrypted_data": invalid_encrypted}

        creds = await manager.get_credentials("user1", OAuthProvider.GOOGLE)
        assert creds is None

    @pytest.mark.asyncio
    async def test_store_credentials_rate_limit(self, manager: OAuthManager):
        """Tests rate limiting when storing credentials."""
        manager.max_attempts_per_hour = 0
        assert await manager.store_credentials("user-rate-limit", OAuthProvider.GOOGLE, {}) is False

    @pytest.mark.asyncio
    async def test_store_credentials_encryption_error(self, manager: OAuthManager, monkeypatch):
        """Tests an error when encrypting credentials."""

        def mock_encrypt_error(*args, **kwargs):
            raise ValueError("Test error")

        monkeypatch.setattr(manager, "_encrypt_token_data", mock_encrypt_error)

        assert await manager.store_credentials("user-encrypt-error", OAuthProvider.GOOGLE, {}) is False

    @pytest.mark.asyncio
    async def test_get_user_providers_empty(self, manager: OAuthManager):
        """Tests getting user providers with an empty token store."""
        providers = await manager.get_user_providers("user-empty")
        assert providers == []

    @pytest.mark.asyncio
    async def test_health_check_empty(self, manager: OAuthManager):
        """Tests the health check method with an empty token store."""
        health = await manager.health_check()
        assert health["status"] == "healthy"
        assert health["active_tokens"] == 0
        assert health["expired_tokens"] == 0

    @pytest.mark.asyncio
    async def test_cleanup_expired_tokens_empty(self, manager: OAuthManager):
        """Tests the cleanup of expired tokens with an empty token store."""
        await manager.cleanup_expired_tokens()
        assert manager.token_store == {}

    @pytest.mark.asyncio
    async def test_cleanup_expired_tokens_corrupted(self, manager: OAuthManager):
        """Tests the cleanup of expired tokens with a corrupted token."""
        manager.token_store["user-corrupt:google"] = {"encrypted_data": "corrupted"}
        await manager.cleanup_expired_tokens()
        assert "user-corrupt:google" not in manager.token_store

    @pytest.mark.asyncio
    async def test_get_credentials_invalid_format(self, manager: OAuthManager):
        """Tests getting credentials with an invalid format."""
        manager.token_store["user1:google"] = {"encrypted_data": "invalid_format"}

        creds = await manager.get_credentials("user1", OAuthProvider.GOOGLE)
        assert creds is None
