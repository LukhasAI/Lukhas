import re
from unittest.mock import AsyncMock, MagicMock, patch
from urllib.parse import urlencode

import pytest
from aioresponses import aioresponses
from bridge.adapters.drive_adapter import DriveAdapter, DriveContextIntegration
from bridge.adapters.service_adapter_base import CapabilityToken

# Mark all tests in this file as async
pytestmark = pytest.mark.asyncio


# Create a concrete implementation of the abstract DriveAdapter for testing
class ConcreteDriveAdapter(DriveAdapter):
    async def fetch_resource(
        self, lid: str, resource_id: str, capability_token: CapabilityToken
    ) -> dict:
        """Dummy implementation for the abstract method."""
        return {"mock": "resource"}


@pytest.fixture
def adapter():
    """Provides a concrete DriveAdapter instance for testing."""
    adapter_instance = ConcreteDriveAdapter()
    adapter_instance.check_consent = AsyncMock(return_value=True)
    adapter_instance.validate_capability_token = MagicMock(return_value=True)
    yield adapter_instance


async def test_authenticate_success(adapter):
    """Test successful authentication with a refresh token."""
    with aioresponses() as m:
        m.post(
            "https://oauth2.googleapis.com/token",
            status=200,
            payload={"access_token": "new_access_token", "expires_in": 3600},
        )

        credentials = {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "refresh_token": "test_refresh_token",
            "lid": "USR-123",
        }
        result = await adapter.authenticate(credentials)

        assert "access_token" in result
        assert result["access_token"] == "new_access_token"
        assert "USR-123" in adapter.oauth_tokens


async def test_authenticate_dry_run(adapter):
    """Test authenticate in dry-run mode."""
    adapter.set_dry_run(True)
    result = await adapter.authenticate({})
    assert result["access_token"] == "dry_run_token"


async def test_authenticate_no_refresh_token(adapter):
    """Test authentication failure when no refresh token is provided."""
    result = await adapter.authenticate({})
    assert result == {"error": "authentication_required"}


async def test_list_files_success(adapter):
    """Test successfully listing files."""
    adapter.oauth_tokens["USR-123"] = {"access_token": "test_token"}
    with aioresponses() as m:
        m.get(
            re.compile(f"^{adapter.base_url}/files.*"),
            status=200,
            payload={"files": [{"id": "1", "name": "test.txt"}]},
        )
        result = await adapter.list_files(lid="USR-123")

    assert "files" in result
    assert len(result["files"]) == 1
    assert result["files"][0]["name"] == "test.txt"


async def test_list_files_api_error(adapter):
    """Test API error when listing files."""
    adapter.oauth_tokens["USR-123"] = {"access_token": "test_token"}
    with aioresponses() as m:
        m.get(re.compile(f"^{adapter.base_url}/files.*"), status=500)
        result = await adapter.list_files(lid="USR-123")

    assert result == {"error": "api_error_500"}


async def test_list_files_dry_run(adapter):
    """Test dry-run mode for listing files."""
    adapter.set_dry_run(True)
    result = await adapter.list_files(lid="USR-123")
    assert result["dry_run"] is True
    assert "plan" in result


async def test_list_files_no_auth(adapter):
    """Test listing files without being authenticated."""
    result = await adapter.list_files(lid="USR-123")
    assert result == {"error": "authentication_required"}


async def test_list_files_consent_denied(adapter):
    """Test listing files when consent is denied."""
    adapter.check_consent.return_value = False
    result = await adapter.list_files(lid="USR-123")
    assert result == {"error": "consent_required", "action": "list_files"}


async def test_list_files_invalid_token(adapter):
    """Test listing files with an invalid capability token."""
    adapter.validate_capability_token.return_value = False
    mock_token = MagicMock()
    result = await adapter.list_files(lid="USR-123", capability_token=mock_token)
    assert result == {"error": "invalid_capability_token"}


async def test_get_file_success(adapter):
    """Test successfully getting a file."""
    adapter.oauth_tokens["USR-123"] = {"access_token": "test_token"}
    file_id = "1"
    with aioresponses() as m:
        m.get(
            re.compile(f"^{adapter.base_url}/files/{file_id}.*alt=media"),
            status=200,
            body="file content",
        )
        m.get(
            re.compile(f"^{adapter.base_url}/files/{file_id}.*"),
            status=200,
            payload={"id": "1", "name": "test.txt", "mimeType": "text/plain"},
        )
        result = await adapter.get_file(lid="USR-123", file_id=file_id)

    assert "file" in result
    assert result["file"]["name"] == "test.txt"
    assert result["file"]["content"] == "file content"


@patch("aiohttp.FormData")
async def test_upload_file_success(MockFormData, adapter):
    """Test successfully uploading a file."""
    adapter.oauth_tokens["USR-123"] = {"access_token": "test_token"}
    with aioresponses() as m:
        m.post(
            re.compile(f"^{adapter.upload_url}/files.*"),
            status=200,
            payload={"id": "new_id", "name": "new_file.txt"},
        )
        result = await adapter.upload_file(
            lid="USR-123", file_name="new_file.txt", content=b"hello world"
        )
    assert "file_id" in result
    assert result["file_id"] == "new_id"


async def test_search_files_success(adapter):
    """Test successfully searching for files."""
    adapter.oauth_tokens["USR-123"] = {"access_token": "test_token"}
    with aioresponses() as m:
        m.get(
            re.compile(f"^{adapter.base_url}/files.*"),
            status=200,
            payload={"files": [{"id": "1", "name": "found.txt"}]},
        )
        result = await adapter.search_files(lid="USR-123", search_query="found")

    assert "files" in result
    assert len(result["files"]) == 1
    assert result["files"][0]["name"] == "found.txt"


async def test_revoke_access(adapter):
    """Test revoking access."""
    adapter.oauth_tokens["USR-123"] = {"access_token": "test_token"}
    assert await adapter.revoke_access(lid="USR-123") is True
    assert "USR-123" not in adapter.oauth_tokens
    assert await adapter.revoke_access(lid="USR-456") is False


# Tests for DriveContextIntegration
async def test_workflow_fetch_travel_documents():
    """Test the travel documents workflow."""
    mock_adapter = AsyncMock(spec=ConcreteDriveAdapter)
    mock_adapter.search_files.return_value = {
        "files": [
            {"id": "1", "name": "My Passport.pdf", "size": "123"},
            {"id": "2", "name": "Travel Itinerary.docx", "size": "456"},
        ]
    }

    integration = DriveContextIntegration(mock_adapter)
    result = await integration.workflow_fetch_travel_documents(
        lid="USR-123", context={}
    )

    assert "travel_documents" in result
    assert len(result["travel_documents"]) == 2
    assert result["travel_documents"][0]["type"] == "identification"
    assert result["travel_documents"][1]["type"] == "itinerary"
    mock_adapter.search_files.assert_called_once()
