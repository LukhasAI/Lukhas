import sys
from pathlib import Path as _Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bridge.adapters.service_adapter_base import CapabilityToken
from bridge.external_adapters.dropbox_adapter import DropboxAdapter, DropboxContextIntegration

# owner: Jules-06
# tier: tier3
# module_uid: candidate.bridge.adapters
# criticality: P1



_PROJECT_ROOT = _Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))



@pytest.mark.tier3
@pytest.mark.adapters
@pytest.mark.unit
class TestDropboxAdapterUnit:
    """
    Unit tests for the Dropbox Service Adapter.
    """

    @pytest.fixture
    def adapter(self):
        """Returns a DropboxAdapter instance."""
        adapter = DropboxAdapter()
        adapter.check_consent = AsyncMock(return_value=True)
        adapter.oauth_tokens["user123"] = {"access_token": "fake_token"}
        return adapter

    @pytest.mark.asyncio
    async def test_authenticate_dry_run(self, adapter: DropboxAdapter):
        """Tests authentication in dry-run mode."""
        adapter.set_dry_run(True)
        creds = await adapter.authenticate({})
        assert creds["access_token"] == "dry_run_token"

    @pytest.mark.asyncio
    async def test_list_folder_auth_error(self, adapter: DropboxAdapter):
        """Tests authentication error when listing a folder."""
        del adapter.oauth_tokens["user123"]
        result = await adapter.list_folder(lid="user123", path="/")
        assert result["error"] == "authentication_required"

    def test_get_storage_info(self, adapter: DropboxAdapter):
        """Tests getting storage info."""
        info = adapter.get_storage_info(lid="user123")
        assert info["lid"] == "user123"
        assert info["service"] == "dropbox"

    @patch.object(DropboxAdapter, "search_files", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_context_integration_workflow(self, mock_search_files, adapter: DropboxAdapter):
        """Tests the DropboxContextIntegration workflow."""
        mock_search_files.return_value = {
            "matches": [{"name": "travel_guide.pdf", "type": "file", "id": "id:456", "path": "/travel_guide.pdf"}]
        }
        integration = DropboxContextIntegration(adapter)
        result = await integration.workflow_fetch_travel_files(lid="user123", context={})

        assert "travel_files" in result
        assert len(result["travel_files"]) == 1
        assert result["travel_files"][0]["type"] == "travel_guide"

    @pytest.mark.parametrize(
        "filename, expected_type",
        [
            ("travel_guide.pdf", "travel_guide"),
            ("emergency_contacts.txt", "emergency_info"),
            ("city_map.png", "map"),
            ("hotel_reservation.pdf", "reservation"),
            ("packing_checklist.docx", "checklist"),
            ("random_file.txt", "travel_file"),
        ],
    )
    def test_classify_travel_file(self, filename, expected_type, adapter: DropboxAdapter):
        """Tests the _classify_travel_file method."""
        integration = DropboxContextIntegration(adapter)
        assert integration._classify_travel_file(filename) == expected_type

    @patch.object(DropboxAdapter, "search_files", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_context_integration_workflow_error(self, mock_search_files, adapter: DropboxAdapter):
        """Tests an error in the DropboxContextIntegration workflow."""
        mock_search_files.return_value = {"error": "search_failed"}
        integration = DropboxContextIntegration(adapter)
        result = await integration.workflow_fetch_travel_files(lid="user123", context={})
        assert result["error"] == "search_failed"

    @pytest.mark.asyncio
    async def test_list_folder_dry_run(self, adapter: DropboxAdapter):
        """Tests list_folder in dry-run mode."""
        adapter.set_dry_run(True)
        result = await adapter.list_folder(lid="user123", path="/")
        assert result["dry_run"] is True
        assert "plan" in result

    @pytest.mark.asyncio
    async def test_search_files_dry_run(self, adapter: DropboxAdapter):
        """Tests search_files in dry-run mode."""
        adapter.set_dry_run(True)
        result = await adapter.search_files(lid="user123", query="test")
        assert result["dry_run"] is True
        assert "plan" in result

    @pytest.mark.asyncio
    async def test_invalid_capability_token(self, adapter: DropboxAdapter):
        """Tests that an invalid capability token is rejected."""
        adapter.validate_capability_token = MagicMock(return_value=False)
        invalid_token = CapabilityToken(
            token_id="invalid-token",
            lid="user123",
            scope=["read"],
            resource_ids=[],
            ttl=3600,
            audience="dropbox",
            issued_at="2025-01-01T00:00:00Z",
            signature="invalid-sig",
        )
        result = await adapter.list_folder(lid="user123", capability_token=invalid_token)
        assert result["error"] == "invalid_capability_token"

    @pytest.mark.asyncio
    async def test_consent_required(self, adapter: DropboxAdapter):
        """Tests that consent is required."""
        adapter.check_consent = AsyncMock(return_value=False)
        result = await adapter.list_folder(lid="user123")
        assert result["error"] == "consent_required"

    @pytest.mark.asyncio
    async def test_download_file_invalid_token(self, adapter: DropboxAdapter):
        """Tests downloading a file with an invalid capability token."""
        adapter.validate_capability_token = MagicMock(return_value=False)
        invalid_token = CapabilityToken(
            token_id="invalid-token",
            lid="user123",
            scope=["read"],
            resource_ids=[],
            ttl=3600,
            audience="dropbox",
            issued_at="2025-01-01T00:00:00Z",
            signature="invalid-sig",
        )
        result = await adapter.download_file(lid="user123", path="/test.txt", capability_token=invalid_token)
        assert result["error"] == "invalid_capability_token"

    @pytest.mark.asyncio
    async def test_upload_file_invalid_token(self, adapter: DropboxAdapter):
        """Tests uploading a file with an invalid capability token."""
        adapter.validate_capability_token = MagicMock(return_value=False)
        invalid_token = CapabilityToken(
            token_id="invalid-token",
            lid="user123",
            scope=["write"],
            resource_ids=[],
            ttl=3600,
            audience="dropbox",
            issued_at="2025-01-01T00:00:00Z",
            signature="invalid-sig",
        )
        result = await adapter.upload_file(
            lid="user123", path="/test.txt", content=b"test", capability_token=invalid_token
        )
        assert result["error"] == "invalid_capability_token"

    @pytest.mark.asyncio
    async def test_search_files_invalid_token(self, adapter: DropboxAdapter):
        """Tests searching files with an invalid capability token."""
        adapter.validate_capability_token = MagicMock(return_value=False)
        invalid_token = CapabilityToken(
            token_id="invalid-token",
            lid="user123",
            scope=["read"],
            resource_ids=[],
            ttl=3600,
            audience="dropbox",
            issued_at="2025-01-01T00:00:00Z",
            signature="invalid-sig",
        )
        result = await adapter.search_files(lid="user123", query="test", capability_token=invalid_token)
        assert result["error"] == "invalid_capability_token"

    @pytest.mark.asyncio
    async def test_download_file_consent_required(self, adapter: DropboxAdapter):
        """Tests that consent is required for downloading a file."""
        adapter.check_consent = AsyncMock(return_value=False)
        result = await adapter.download_file(lid="user123", path="/test.txt")
        assert result["error"] == "consent_required"

    @pytest.mark.asyncio
    async def test_upload_file_consent_required(self, adapter: DropboxAdapter):
        """Tests that consent is required for uploading a file."""
        adapter.check_consent = AsyncMock(return_value=False)
        result = await adapter.upload_file(lid="user123", path="/test.txt", content=b"test")
        assert result["error"] == "consent_required"

    @pytest.mark.asyncio
    async def test_search_files_consent_required(self, adapter: DropboxAdapter):
        """Tests that consent is required for searching files."""
        adapter.check_consent = AsyncMock(return_value=False)
        result = await adapter.search_files(lid="user123", query="test")
        assert result["error"] == "consent_required"

    @pytest.mark.asyncio
    async def test_revoke_access(self, adapter: DropboxAdapter):
        """Tests revoking access."""
        assert "user123" in adapter.oauth_tokens
        revoked = await adapter.revoke_access(lid="user123")
        assert revoked is True
        assert "user123" not in adapter.oauth_tokens
