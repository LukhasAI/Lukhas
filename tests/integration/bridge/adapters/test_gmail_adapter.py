# owner: Jules-06
# tier: tier3
# module_uid: candidate.bridge.adapters
# criticality: P1

from unittest.mock import AsyncMock, patch

import pytest

from candidate.bridge.adapters.gmail_adapter import GmailAdapter


@pytest.mark.tier3
@pytest.mark.adapters
@pytest.mark.integration
class TestGmailAdapterIntegration:
    """
    Integration tests for the Gmail Service Adapter.
    External API calls are mocked.
    """

    @pytest.fixture
    def adapter(self):
        """Returns a GmailAdapter instance."""
        adapter = GmailAdapter()
        adapter.check_consent = AsyncMock(return_value=True)
        adapter.oauth_tokens["user123"] = {"access_token": "fake_token"}
        return adapter

    @patch("aiohttp.ClientSession.post")
    @pytest.mark.asyncio
    async def test_authenticate_refresh_token(self, mock_post, adapter: GmailAdapter):
        """Tests the OAuth refresh token flow."""
        # Arrange
        mock_response = AsyncMock()
        mock_response.json.return_value = {"access_token": "new_access_token", "expires_in": 3600}
        mock_post.return_value.__aenter__.return_value = mock_response

        credentials = {
            "client_id": "test_client",
            "client_secret": "test_secret",
            "refresh_token": "test_refresh",
            "lid": "user123",
        }

        # Act
        token_data = await adapter.authenticate(credentials)

        # Assert
        assert token_data["access_token"] == "new_access_token"
        assert "user123" in adapter.oauth_tokens
        assert adapter.oauth_tokens["user123"]["access_token"] == "new_access_token"

    @patch("aiohttp.ClientSession.get")
    @pytest.mark.asyncio
    async def test_fetch_emails_success(self, mock_get, adapter: GmailAdapter):
        """Tests successfully fetching emails."""
        # Mock the response for listing messages
        mock_list_response = AsyncMock()
        mock_list_response.status = 200
        mock_list_response.json.return_value = {"messages": [{"id": "msg1"}, {"id": "msg2"}]}

        # Mock the response for fetching email details
        mock_detail_response = AsyncMock()
        mock_detail_response.status = 200
        mock_detail_response.json.side_effect = [
            {"id": "msg1", "snippet": "Snippet 1", "payload": {"headers": [{"name": "Subject", "value": "Subject 1"}]}},
            {"id": "msg2", "snippet": "Snippet 2", "payload": {"headers": [{"name": "Subject", "value": "Subject 2"}]}},
        ]

        mock_get.return_value.__aenter__.side_effect = [
            mock_list_response,
            mock_detail_response,
            mock_detail_response,
        ]

        # Act
        result = await adapter.fetch_emails(lid="user123")

        # Assert
        assert "emails" in result
        assert len(result["emails"]) == 2
        assert result["emails"][0]["id"] == "msg1"

    @patch("aiohttp.ClientSession.get")
    @pytest.mark.asyncio
    async def test_list_labels_success(self, mock_get, adapter: GmailAdapter):
        """Tests successfully listing labels."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {"labels": [{"id": "label1", "name": "INBOX"}]}
        mock_get.return_value.__aenter__.return_value = mock_response

        result = await adapter.list_labels(lid="user123")
        assert "labels" in result
        assert len(result["labels"]) == 1
        assert result["labels"][0]["name"] == "INBOX"

    @patch("aiohttp.ClientSession.get")
    @pytest.mark.asyncio
    async def test_list_labels_api_error(self, mock_get, adapter: GmailAdapter):
        """Tests API error when listing labels."""
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_get.return_value.__aenter__.return_value = mock_response

        result = await adapter.list_labels(lid="user123")
        assert result["error"] == "api_error_500"

    @patch("aiohttp.ClientSession.get")
    @pytest.mark.asyncio
    async def test_search_emails(self, mock_get, adapter: GmailAdapter):
        """Tests the search_emails method."""
        # search_emails is just a wrapper around fetch_emails, so this test is similar
        mock_list_response = AsyncMock()
        mock_list_response.status = 200
        mock_list_response.json.return_value = {"messages": [{"id": "msg1"}]}
        mock_detail_response = AsyncMock()
        mock_detail_response.status = 200
        mock_detail_response.json.return_value = {"id": "msg1", "snippet": "Test"}
        mock_get.return_value.__aenter__.side_effect = [mock_list_response, mock_detail_response]

        result = await adapter.search_emails(lid="user123", search_query="test")
        assert "emails" in result
        assert len(result["emails"]) == 1

    @patch("aiohttp.ClientSession.get")
    @pytest.mark.asyncio
    async def test_fetch_emails_api_error(self, mock_get, adapter: GmailAdapter):
        """Tests API error during fetch_emails."""
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_get.return_value.__aenter__.return_value = mock_response

        result = await adapter.fetch_emails(lid="user123")
        assert result["error"] == "api_error_401"

    @patch("aiohttp.ClientSession.get")
    @pytest.mark.asyncio
    async def test_list_labels_maps_fields(self, mock_get, adapter: GmailAdapter):
        """Tests that list_labels correctly maps fields."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {"labels": [{"id": "INBOX", "name": "INBOX", "type": "system"}]}
        mock_get.return_value.__aenter__.return_value = mock_response

        labels = await adapter.list_labels(lid="user123")
        assert "labels" in labels
        assert {"id", "name", "type"}.issubset(labels["labels"][0].keys())

    @patch("aiohttp.ClientSession.get")
    @pytest.mark.asyncio
    async def test_search_emails_handles_429_retry_after(self, mock_get, adapter: GmailAdapter):
        """Tests that search_emails handles a 429 error with a Retry-After header."""
        mock_response_429 = AsyncMock()
        mock_response_429.status = 429
        mock_response_429.headers = {"Retry-After": "1"}
        mock_response_429.json.return_value = {"error": "rate limit"}

        mock_response_200 = AsyncMock()
        mock_response_200.status = 200
        mock_response_200.json.return_value = {"messages": []}

        # The first call to _fetch_email_details will be for the 429, the second for the 200
        mock_detail_response = AsyncMock()
        mock_detail_response.status = 200
        mock_detail_response.json.return_value = {"id": "msg1", "snippet": "Test"}

        mock_get.return_value.__aenter__.side_effect = [mock_response_429, mock_response_200, mock_detail_response]

        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            result = await adapter.search_emails(lid="user123", search_query="test")
            assert "emails" in result

    @patch("aiohttp.ClientSession.get")
    @pytest.mark.asyncio
    async def test_fetch_email_details_error(self, mock_get, adapter: GmailAdapter):
        """Tests an error when fetching email details."""
        mock_list_response = AsyncMock()
        mock_list_response.status = 200
        mock_list_response.json.return_value = {"messages": [{"id": "msg1"}]}

        mock_detail_response = AsyncMock()
        mock_detail_response.status = 500  # Simulate error

        mock_get.return_value.__aenter__.side_effect = [mock_list_response, mock_detail_response]

        result = await adapter.fetch_emails(lid="user123")
        assert len(result["emails"]) == 1
        assert result["emails"][0]["error"] == "fetch_failed"

    @patch("aiohttp.ClientSession.post")
    @pytest.mark.asyncio
    async def test_authenticate_refresh_token_error(self, mock_post, adapter: GmailAdapter):
        """Tests an error during the OAuth refresh token flow."""
        mock_response = AsyncMock()
        mock_response.status = 400
        mock_response.json.return_value = {"error": "invalid_grant"}
        mock_post.return_value.__aenter__.return_value = mock_response

        credentials = {
            "client_id": "test_client",
            "client_secret": "test_secret",
            "refresh_token": "bad_refresh_token",
            "lid": "user123",
        }

        token_data = await adapter.authenticate(credentials)
        assert "error" in token_data
