# owner: Jules-06
# tier: tier3
# module_uid: candidate.bridge.adapters
# criticality: P1

import pytest
from unittest.mock import AsyncMock, patch

from candidate.bridge.adapters.dropbox_adapter import DropboxAdapter

@pytest.mark.tier3
@pytest.mark.adapters
@pytest.mark.integration
class TestDropboxAdapterIntegration:
    """
    Integration tests for the Dropbox Service Adapter.
    """

    @pytest.fixture
    def adapter(self):
        """Returns a DropboxAdapter instance."""
        adapter = DropboxAdapter()
        adapter.check_consent = AsyncMock(return_value=True)
        adapter.oauth_tokens["user123"] = {"access_token": "fake_token"}
        return adapter

    @patch('aiohttp.ClientSession.post')
    @pytest.mark.asyncio
    async def test_list_folder_success(self, mock_post, adapter: DropboxAdapter):
        """Tests successfully listing a folder."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "entries": [{
                "id": "id:123",
                "name": "test.txt",
                "path_display": "/test.txt",
                ".tag": "file",
                "size": 123
            }]
        }
        mock_post.return_value.__aenter__.return_value = mock_response

        result = await adapter.list_folder(lid="user123", path="/")
        assert "entries" in result
        assert len(result["entries"]) == 1
        assert result["entries"][0]["name"] == "test.txt"

    @patch('aiohttp.ClientSession.post')
    @pytest.mark.asyncio
    async def test_download_file_success(self, mock_post, adapter: DropboxAdapter):
        """Tests successfully downloading a file."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {
            "Dropbox-API-Result": '{"name": "test.txt", "size": 4}'
        }
        mock_response.read.return_value = b"test"
        mock_post.return_value.__aenter__.return_value = mock_response

        result = await adapter.download_file(lid="user123", path="/test.txt")
        assert "file" in result
        assert result["file"]["name"] == "test.txt"
        assert result["file"]["size"] == 4

    @patch('aiohttp.ClientSession.post')
    @pytest.mark.asyncio
    async def test_search_files_success(self, mock_post, adapter: DropboxAdapter):
        """Tests successfully searching for files."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "matches": [{
                "metadata": {"metadata": {"name": "test.txt"}}
            }]
        }
        mock_post.return_value.__aenter__.return_value = mock_response

        result = await adapter.search_files(lid="user123", query="test")
        assert "matches" in result
        assert len(result["matches"]) == 1
        assert result["matches"][0]["name"] == "test.txt"

    @patch('aiohttp.ClientSession.post')
    @pytest.mark.asyncio
    async def test_upload_file_success(self, mock_post, adapter: DropboxAdapter):
        """Tests successfully uploading a file."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {"name": "test.txt"}
        mock_post.return_value.__aenter__.return_value = mock_response

        result = await adapter.upload_file(lid="user123", path="/test.txt", content=b"test")
        assert "file" in result
        assert result["file"]["name"] == "test.txt"

    @patch('aiohttp.ClientSession.post')
    @pytest.mark.asyncio
    async def test_authenticate_refresh_token(self, mock_post, adapter: DropboxAdapter):
        """Tests the OAuth refresh token flow for Dropbox."""
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "access_token": "new_dropbox_token",
            "expires_in": 14400
        }
        mock_post.return_value.__aenter__.return_value = mock_response

        credentials = {
            "app_key": "test_key",
            "app_secret": "test_secret",
            "refresh_token": "test_refresh",
            "lid": "user123"
        }

        token_data = await adapter.authenticate(credentials)
        assert token_data["access_token"] == "new_dropbox_token"
        assert "user123" in adapter.oauth_tokens

    @patch('aiohttp.ClientSession.post')
    @pytest.mark.asyncio
    async def test_authenticate_refresh_token_error(self, mock_post, adapter: DropboxAdapter):
        """Tests an error during the OAuth refresh token flow for Dropbox."""
        mock_response = AsyncMock()
        mock_response.status = 400
        mock_response.json.return_value = {"error": "invalid_grant"}
        mock_post.return_value.__aenter__.return_value = mock_response

        credentials = {
            "app_key": "test_key",
            "app_secret": "test_secret",
            "refresh_token": "bad_refresh_token",
            "lid": "user123"
        }

        token_data = await adapter.authenticate(credentials)
        assert "error" in token_data

    @patch('aiohttp.ClientSession.post')
    @pytest.mark.asyncio
    async def test_authenticate_no_access_token(self, mock_post, adapter: DropboxAdapter):
        """Tests the case where no access token is returned."""
        mock_response = AsyncMock()
        mock_response.json.return_value = {"error": "no_token"}
        mock_post.return_value.__aenter__.return_value = mock_response

        credentials = {
            "app_key": "test_key",
            "app_secret": "test_secret",
            "refresh_token": "test_refresh",
            "lid": "user123"
        }

        token_data = await adapter.authenticate(credentials)
        assert "error" in token_data

    @patch('aiohttp.ClientSession.post')
    @pytest.mark.asyncio
    async def test_list_folder_api_error(self, mock_post, adapter: DropboxAdapter):
        """Tests API error when listing a folder."""
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_post.return_value.__aenter__.return_value = mock_response

        result = await adapter.list_folder(lid="user123", path="/")
        assert result["error"] == "api_error_500"

    @patch('aiohttp.ClientSession.post')
    @pytest.mark.asyncio
    async def test_download_file_error(self, mock_post, adapter: DropboxAdapter):
        """Tests an error when downloading a file."""
        mock_response = AsyncMock()
        mock_response.status = 404
        mock_post.return_value.__aenter__.return_value = mock_response

        result = await adapter.download_file(lid="user123", path="/not-found.txt")
        assert result["error"] == "download_error_404"

    @patch('aiohttp.ClientSession.post')
    @pytest.mark.asyncio
    async def test_search_files_error(self, mock_post, adapter: DropboxAdapter):
        """Tests an error when searching for files."""
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_post.return_value.__aenter__.return_value = mock_response

        result = await adapter.search_files(lid="user123", query="test")
        assert result["error"] == "search_error_401"

    @patch('aiohttp.ClientSession.post')
    @pytest.mark.asyncio
    async def test_upload_file_error(self, mock_post, adapter: DropboxAdapter):
        """Tests an error when uploading a file."""
        mock_response = AsyncMock()
        mock_response.status = 409
        mock_post.return_value.__aenter__.return_value = mock_response

        result = await adapter.upload_file(lid="user123", path="/test.txt", content=b"test")
        assert result["error"] == "upload_error_409"
