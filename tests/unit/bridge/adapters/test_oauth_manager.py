# owner: Jules-06
# tier: tier3
# module_uid: candidate.bridge.external_adapters
# criticality: P1

import pytest

from bridge.external_adapters.oauth_manager import OAuthManager, OAuthProvider


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
    async def test_retry_with_backoff(self, manager: OAuthManager, monkeypatch, mocker):
        """Tests the retry mechanism with exponential backoff."""
        import asyncio

        mock_sleep = mocker.AsyncMock()
        monkeypatch.setattr(asyncio, "sleep", mock_sleep)

        mock_func = mocker.AsyncMock(side_effect=Exception("Test failure"))

        manager.config["max_retries"] = 2
        manager.config["retry_base_delay"] = 0.1

        with pytest.raises(Exception, match="Test failure"):
            async with manager._with_retry_and_circuit_breaker(OAuthProvider.GOOGLE, "test_op") as cb:
                await cb.call(mock_func)

        assert mock_func.call_count == 3  # 1 initial + 2 retries
        assert mock_sleep.call_count == 2

        # Check backoff delays (with jitter)
        assert 0.1 <= mock_sleep.call_args_list[0].args[0] < 1.1 # 0.1 * 2**0 + jitter
        assert 0.2 <= mock_sleep.call_args_list[1].args[0] < 1.2 # 0.1 * 2**1 + jitter

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
