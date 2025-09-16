# owner: Jules-06
# tier: tier3
# module_uid: candidate.bridge.external_adapters.gmail_adapter
# criticality: P2

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from candidate.bridge.external_adapters.gmail_adapter import GmailAdapter, GmailMessage
from candidate.bridge.external_adapters.oauth_manager import OAuthManager


@pytest.mark.tier3
@pytest.mark.adapters
@pytest.mark.unit
class TestExternalGmailAdapterUnit:
    """
    Unit tests for the external Gmail Adapter.
    """

    @pytest.fixture
    def oauth_manager(self):
        """Returns a mock OAuthManager."""
        manager = OAuthManager()
        manager.get_credentials = AsyncMock(return_value={
            "token": "fake_token",
            "refresh_token": "fake_refresh_token",
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": "fake_client_id",
            "client_secret": "fake_client_secret",
            "scopes": ["https://www.googleapis.com/auth/gmail.readonly"],
        })
        return manager

    @pytest.fixture
    def adapter(self, oauth_manager):
        """Returns a GmailAdapter instance with a mock OAuthManager."""
        adapter = GmailAdapter()
        adapter.oauth_manager = oauth_manager
        return adapter

    @pytest.mark.asyncio
    async def test_get_auth_url(self, adapter: GmailAdapter):
        """Tests that get_auth_url returns a valid URL."""
        auth_url = await adapter.get_auth_url("user123")
        assert "accounts.google.com/o/oauth2/auth" in auth_url
        assert "response_type=code" in auth_url
        assert "client_id" in auth_url
        assert "redirect_uri" in auth_url
        assert "scope" in auth_url

    @pytest.mark.asyncio
    async def test_health_check_success(self, adapter: GmailAdapter, mocker):
        """Tests the health check method on success."""
        mock_service = mocker.MagicMock()
        mock_profile = mocker.MagicMock()
        mock_profile.get.side_effect = lambda key: {
            "emailAddress": "test@example.com",
            "messagesTotal": 100,
            "threadsTotal": 50,
        }.get(key)
        mock_service.users.return_value.getProfile.return_value.execute.return_value = mock_profile

        adapter._get_gmail_service = AsyncMock(return_value=mock_service)

        health = await adapter.health_check("user123")

        assert health["status"] == "healthy"
        assert health["email_address"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_health_check_failure(self, adapter: GmailAdapter, mocker):
        """Tests the health check method on failure."""
        adapter._get_gmail_service = AsyncMock(side_effect=Exception("API error"))

        health = await adapter.health_check("user123")

        assert health["status"] == "error"
        assert "API error" in health["error"]

    @pytest.mark.asyncio
    @patch("candidate.bridge.external_adapters.gmail_adapter.Flow")
    async def test_handle_callback_success(self, MockFlow, adapter: GmailAdapter):
        """Tests successful handling of OAuth callback."""
        mock_flow_instance = MockFlow.from_client_config.return_value
        mock_flow_instance.fetch_token.return_value = None  # Not used
        mock_flow_instance.credentials = MagicMock(
            token="new_token",
            refresh_token="new_refresh",
            token_uri="uri",
            client_id="id",
            client_secret="secret",
            scopes=["scope1"],
        )

        adapter.oauth_manager.store_credentials = AsyncMock(return_value=True)

        result = await adapter.handle_callback("auth_code", "user123")

        assert result is True
        adapter.oauth_manager.store_credentials.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_messages_success(self, adapter: GmailAdapter, mocker):
        """Tests successfully getting messages."""
        mock_service = mocker.MagicMock()
        mock_service.users.return_value.messages.return_value.list.return_value.execute.return_value = {
            "messages": [{"id": "msg1"}, {"id": "msg2"}]
        }

        # Mock the response for get message
        mock_msg1 = {"id": "msg1", "snippet": "Test snippet 1", "payload": {"headers": []}}
        mock_msg2 = {"id": "msg2", "snippet": "Test snippet 2", "payload": {"headers": []}}
        mock_service.users.return_value.messages.return_value.get.side_effect = [
            MagicMock(execute=MagicMock(return_value=mock_msg1)),
            MagicMock(execute=MagicMock(return_value=mock_msg2)),
        ]

        adapter._get_gmail_service = AsyncMock(return_value=mock_service)

        messages = await adapter.get_messages("user123")

        assert len(messages) == 2
        assert isinstance(messages[0], GmailMessage)
        assert messages[0].id == "msg1"
        assert messages[1].snippet == "Test snippet 2"
