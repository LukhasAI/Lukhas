"""
Tests for LUKHAS Service Adapters
=================================
Smoke tests for adapter endpoints with fake vendors.
Tests capability token verification and denial of missing/expired tokens.
"""

import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, patch

from adapters import ServiceAdapter, ResourceMetadata, SearchQuery, WatchRequest
from adapters.gmail_headers import GmailHeadersAdapter, EmailHeaderMetadata
from adapters.drive import DriveAdapter, DriveFileMetadata
from adapters.dropbox import DropboxAdapter, DropboxFileMetadata
from adapters.cloud_consolidation import CloudConsolidationService, ConsolidationRequest
from consent.service import ConsentService


class TestServiceAdapterBase:
    """Test base ServiceAdapter functionality"""
    
    def test_extract_required_scopes(self):
        """Test scope extraction for different operations"""
        adapter = ServiceAdapter("test", None)
        
        # Test basic operations
        assert adapter._extract_required_scopes("list", "files") == ["files.list.metadata"]
        assert adapter._extract_required_scopes("get_content", "files") == ["files.read.content"]
        assert adapter._extract_required_scopes("put", "files") == ["files.write"]
        assert adapter._extract_required_scopes("move", "files") == ["files.move"]
        
        # Test email-specific operations
        assert adapter._extract_required_scopes("list", "email") == ["email.list.metadata"]


class TestGmailHeadersAdapter:
    """Test Gmail headers adapter"""
    
    @pytest.fixture
    async def adapter(self):
        """Create Gmail adapter with mock consent service"""
        mock_consent_service = AsyncMock(spec=ConsentService)
        adapter = GmailHeadersAdapter(mock_consent_service)
        await adapter.initialize({"mock_mode": True})
        return adapter, mock_consent_service
    
    @pytest.mark.asyncio
    async def test_list_resources_valid_token(self, adapter):
        """Test listing email headers with valid capability token"""
        gmail_adapter, mock_consent = adapter
        
        # Mock token verification success
        mock_consent.verify_capability_token.return_value = {
            "lid": "gonzo",
            "service": "gmail", 
            "scopes": ["email.read.headers"],
            "valid": True
        }
        
        # List emails
        emails = await gmail_adapter.list_resources("mock_valid_token", limit=5)
        
        # Verify results
        assert len(emails) <= 5
        assert all(isinstance(email, EmailHeaderMetadata) for email in emails)
        assert all(email.from_address for email in emails)
        assert all(email.subject for email in emails)
        
        # Verify token was checked
        mock_consent.verify_capability_token.assert_called_once_with(
            "mock_valid_token", ["email.read.headers"], None
        )
    
    @pytest.mark.asyncio
    async def test_list_resources_invalid_token(self, adapter):
        """Test email listing with invalid token is denied"""
        gmail_adapter, mock_consent = adapter
        
        # Mock token verification failure
        mock_consent.verify_capability_token.side_effect = ValueError("Invalid token")
        
        # Attempt to list emails
        with pytest.raises(ValueError, match="Invalid token"):
            await gmail_adapter.list_resources("invalid_token")
    
    @pytest.mark.asyncio
    async def test_get_resource_content_requires_content_scope(self, adapter):
        """Test that content access requires proper scope"""
        gmail_adapter, mock_consent = adapter
        
        # Mock token verification with content scope
        mock_consent.verify_capability_token.return_value = {
            "lid": "gonzo",
            "service": "gmail",
            "scopes": ["email.read.content"],
            "valid": True
        }
        
        # Get email content
        content = await gmail_adapter.get_resource_content("mock_content_token", "msg_001")
        
        assert content.metadata.id == "msg_001"
        assert len(content.content) > 0
        assert content.content_type == "text/plain"
        
        # Verify content scope was required
        mock_consent.verify_capability_token.assert_called_once_with(
            "mock_content_token", ["email.read.content"], "msg_001"
        )
    
    @pytest.mark.asyncio
    async def test_search_emails(self, adapter):
        """Test email search functionality"""
        gmail_adapter, mock_consent = adapter
        
        mock_consent.verify_capability_token.return_value = {
            "lid": "gonzo",
            "service": "gmail",
            "scopes": ["email.search.headers", "email.read.headers"],
            "valid": True
        }
        
        query = SearchQuery(
            query="proposal",
            limit=10
        )
        
        results = await gmail_adapter.search_resources("mock_search_token", query)
        
        assert len(results) <= 10
        assert all(isinstance(email, EmailHeaderMetadata) for email in results)
    
    @pytest.mark.asyncio
    async def test_gmail_read_only_operations(self, adapter):
        """Test that Gmail adapter properly handles read-only nature"""
        gmail_adapter, _ = adapter
        
        # Put operation should be rejected
        with pytest.raises(NotImplementedError, match="read-only"):
            await gmail_adapter.put_resource(
                "mock_token", None, "test.txt", b"content", "text/plain"
            )


class TestDriveAdapter:
    """Test Google Drive adapter"""
    
    @pytest.fixture
    async def adapter(self):
        """Create Drive adapter with mock consent service"""
        mock_consent_service = AsyncMock(spec=ConsentService)
        adapter = DriveAdapter(mock_consent_service)
        await adapter.initialize({"mock_mode": True})
        return adapter, mock_consent_service
    
    @pytest.mark.asyncio
    async def test_list_files_metadata_only(self, adapter):
        """Test listing files with metadata-only scope"""
        drive_adapter, mock_consent = adapter
        
        mock_consent.verify_capability_token.return_value = {
            "lid": "gonzo",
            "service": "drive",
            "scopes": ["files.list.metadata"],
            "valid": True
        }
        
        files = await drive_adapter.list_resources("mock_metadata_token", limit=10)
        
        assert len(files) <= 10
        assert all(isinstance(file, DriveFileMetadata) for file in files)
        assert all(file.name for file in files)
        assert all(file.size is not None or file.is_folder for file in files)
        
        # Verify metadata scope was required
        mock_consent.verify_capability_token.assert_called_once_with(
            "mock_metadata_token", ["files.list.metadata"]
        )
    
    @pytest.mark.asyncio
    async def test_get_file_content_escalation(self, adapter):
        """Test content access requires escalated capability"""
        drive_adapter, mock_consent = adapter
        
        mock_consent.verify_capability_token.return_value = {
            "lid": "gonzo",
            "service": "drive",
            "scopes": ["files.read.content"],
            "valid": True
        }
        
        content = await drive_adapter.get_resource_content("mock_content_token", "file_001")
        
        assert content.metadata.id == "file_001"
        assert len(content.content) > 0
        
        # Verify content scope was required with resource ID
        mock_consent.verify_capability_token.assert_called_once_with(
            "mock_content_token", ["files.read.content"], "file_001"
        )
    
    @pytest.mark.asyncio
    async def test_put_resource_requires_write_scope(self, adapter):
        """Test file upload requires write scope"""
        drive_adapter, mock_consent = adapter
        
        mock_consent.verify_capability_token.return_value = {
            "lid": "gonzo",
            "service": "drive", 
            "scopes": ["files.write"],
            "valid": True
        }
        
        result = await drive_adapter.put_resource(
            "mock_write_token",
            "parent_folder_123",
            "test_document.txt",
            b"Hello, LUKHAS!",
            "text/plain"
        )
        
        assert result.success
        assert result.resource_id.startswith("upload_")
        assert "uploaded successfully" in result.message
        
        # Verify write scope was required
        mock_consent.verify_capability_token.assert_called_once_with(
            "mock_write_token", ["files.write"]
        )
    
    @pytest.mark.asyncio
    async def test_move_resource_requires_move_scope(self, adapter):
        """Test file move requires move scope"""
        drive_adapter, mock_consent = adapter
        
        mock_consent.verify_capability_token.return_value = {
            "lid": "gonzo",
            "service": "drive",
            "scopes": ["files.move"],
            "valid": True
        }
        
        result = await drive_adapter.move_resource(
            "mock_move_token",
            "file_001",
            "new_parent_folder",
            "renamed_file.txt"
        )
        
        assert result.success
        assert "moved" in result.message.lower()
        
        # Verify move scope was required with resource ID
        mock_consent.verify_capability_token.assert_called_once_with(
            "mock_move_token", ["files.move"], "file_001"
        )
    
    @pytest.mark.asyncio
    async def test_expired_token_denied(self, adapter):
        """Test that expired tokens are properly denied"""
        drive_adapter, mock_consent = adapter
        
        # Mock expired token
        mock_consent.verify_capability_token.side_effect = ValueError("Token expired")
        
        with pytest.raises(ValueError, match="Token expired"):
            await drive_adapter.list_resources("expired_token")


class TestDropboxAdapter:
    """Test Dropbox adapter"""
    
    @pytest.fixture
    async def adapter(self):
        """Create Dropbox adapter with mock consent service"""
        mock_consent_service = AsyncMock(spec=ConsentService)
        adapter = DropboxAdapter(mock_consent_service)
        await adapter.initialize({"mock_mode": True})
        return adapter, mock_consent_service
    
    @pytest.mark.asyncio
    async def test_list_resources_with_path_ids(self, adapter):
        """Test Dropbox file listing using path-based IDs"""
        dropbox_adapter, mock_consent = adapter
        
        mock_consent.verify_capability_token.return_value = {
            "lid": "gonzo",
            "service": "dropbox",
            "scopes": ["files.list.metadata"],
            "valid": True
        }
        
        files = await dropbox_adapter.list_resources(
            "mock_token", 
            parent_id="/Documents",
            limit=5
        )
        
        assert len(files) <= 5
        assert all(isinstance(file, DropboxFileMetadata) for file in files)
        assert all(file.path_display for file in files)
        assert all(file.path_display.startswith("/Documents/") for file in files)
    
    @pytest.mark.asyncio  
    async def test_search_with_filters(self, adapter):
        """Test Dropbox search with various filters"""
        dropbox_adapter, mock_consent = adapter
        
        mock_consent.verify_capability_token.return_value = {
            "lid": "gonzo",
            "service": "dropbox",
            "scopes": ["files.search", "files.list.metadata"],
            "valid": True
        }
        
        query = SearchQuery(
            query="proposal",
            size_min=1024,
            size_max=10 * 1024 * 1024,  # 10MB max
            limit=20
        )
        
        results = await dropbox_adapter.search_resources("mock_search_token", query)
        
        assert len(results) <= 20
        # All results should match size filters
        for file in results:
            if file.size:
                assert file.size >= 1024
                assert file.size <= 10 * 1024 * 1024
    
    @pytest.mark.asyncio
    async def test_missing_capability_token_denied(self, adapter):
        """Test that missing tokens are denied"""
        dropbox_adapter, mock_consent = adapter
        
        # Mock missing/invalid token
        mock_consent.verify_capability_token.side_effect = ValueError("Invalid capability token")
        
        with pytest.raises(ValueError, match="Invalid capability token"):
            await dropbox_adapter.get_resource_metadata("", "some_file.txt")


class TestCloudConsolidation:
    """Test cloud consolidation service"""
    
    @pytest.fixture
    async def service(self):
        """Create consolidation service with mock adapters"""
        mock_consent_service = AsyncMock(spec=ConsentService)
        service = CloudConsolidationService(mock_consent_service)
        
        # Mock adapters
        service.adapters = {
            "gmail": AsyncMock(),
            "drive": AsyncMock(), 
            "dropbox": AsyncMock()
        }
        
        return service
    
    @pytest.mark.asyncio
    async def test_analyze_consolidation_cross_service(self, service):
        """Test consolidation analysis across multiple services"""
        
        # Mock files from different services
        drive_files = [
            DriveFileMetadata(
                id="drive_doc_1", name="project_proposal.docx", type="file",
                size=50000, created_at=datetime.now(timezone.utc),
                modified_at=datetime.now(timezone.utc), tags=["service:drive"]
            ),
            DriveFileMetadata(
                id="drive_doc_2", name="project_proposal.docx", type="file", 
                size=50000, created_at=datetime.now(timezone.utc),
                modified_at=datetime.now(timezone.utc), tags=["service:drive"]
            )
        ]
        
        dropbox_files = [
            DropboxFileMetadata(
                id="/Documents/project_proposal.docx", name="project_proposal.docx",
                type="file", size=50000, created_at=datetime.now(timezone.utc),
                modified_at=datetime.now(timezone.utc), tags=["service:dropbox"],
                path_display="/Documents/project_proposal.docx"
            )
        ]
        
        # Configure mock adapters
        service.adapters["drive"].list_resources.return_value = drive_files
        service.adapters["dropbox"].list_resources.return_value = dropbox_files
        service.adapters["gmail"].list_resources.return_value = []
        
        request = ConsolidationRequest(
            lid="gonzo",
            services=["drive", "dropbox"],
            duplicate_detection=True
        )
        
        capability_tokens = {
            "drive": "mock_drive_token",
            "dropbox": "mock_dropbox_token"
        }
        
        plan = await service.analyze_consolidation(request, capability_tokens)
        
        # Should detect cross-service duplicates
        assert plan.total_files_analyzed == 3
        assert len(plan.duplicate_groups) > 0
        assert plan.projected_savings_bytes > 0
        assert len(plan.recommended_actions) > 0
        
        # Check for cross-service duplicate detection
        duplicate_group = plan.duplicate_groups[0]
        services_found = set()
        for file in duplicate_group.files:
            if file.tags:
                service_tag = next(tag for tag in file.tags if tag.startswith("service:"))
                services_found.add(service_tag)
        
        assert len(services_found) > 1  # Cross-service duplicates detected
    
    @pytest.mark.asyncio
    async def test_old_files_detection(self, service):
        """Test detection of old files for archival"""
        
        # Mock old files
        old_date = datetime.now(timezone.utc) - timedelta(days=400)
        old_files = [
            DriveFileMetadata(
                id="old_file_1", name="old_document.txt", type="file",
                size=10000, created_at=old_date, modified_at=old_date,
                tags=["service:drive"]
            )
        ]
        
        service.adapters["drive"].list_resources.return_value = old_files
        service.adapters["dropbox"].list_resources.return_value = []
        service.adapters["gmail"].list_resources.return_value = []
        
        request = ConsolidationRequest(
            lid="gonzo",
            services=["drive"],
            include_old_threshold_days=365,  # Files older than 1 year
            duplicate_detection=False
        )
        
        plan = await service.analyze_consolidation(request, {"drive": "mock_token"})
        
        assert len(plan.old_files) == 1
        assert plan.old_files[0].name == "old_document.txt"
        
        # Should have archival recommendation
        archive_actions = [a for a in plan.recommended_actions if a["type"] == "archive_old_files"]
        assert len(archive_actions) > 0
    
    @pytest.mark.asyncio
    async def test_large_files_detection(self, service):
        """Test detection of large files for optimization"""
        
        # Mock large file (200MB)
        large_files = [
            DropboxFileMetadata(
                id="/Videos/presentation.mp4", name="presentation.mp4", type="file",
                size=200 * 1024 * 1024, created_at=datetime.now(timezone.utc),
                modified_at=datetime.now(timezone.utc), tags=["service:dropbox"],
                path_display="/Videos/presentation.mp4"
            )
        ]
        
        service.adapters["dropbox"].list_resources.return_value = large_files
        service.adapters["drive"].list_resources.return_value = []
        service.adapters["gmail"].list_resources.return_value = []
        
        request = ConsolidationRequest(
            lid="gonzo",
            services=["dropbox"],
            large_file_threshold_mb=100,  # Files > 100MB
            duplicate_detection=False
        )
        
        plan = await service.analyze_consolidation(request, {"dropbox": "mock_token"})
        
        assert len(plan.large_files) == 1
        assert plan.large_files[0].size > 100 * 1024 * 1024
        
        # Should have optimization recommendation
        optimize_actions = [a for a in plan.recommended_actions if a["type"] == "optimize_large_files"]
        assert len(optimize_actions) > 0
    
    def test_format_bytes(self, service):
        """Test byte formatting helper"""
        assert service._format_bytes(1024) == "1.0 KB"
        assert service._format_bytes(1024 * 1024) == "1.0 MB"
        assert service._format_bytes(1024 * 1024 * 1024) == "1.0 GB"
        assert service._format_bytes(500) == "500.0 B"


class TestAdapterIntegration:
    """Integration tests for adapter ecosystem"""
    
    @pytest.mark.asyncio
    async def test_adapter_factory_functions(self):
        """Test adapter factory functions work correctly"""
        from adapters.gmail_headers import create_gmail_adapter
        from adapters.drive import create_drive_adapter
        from adapters.dropbox import create_dropbox_adapter
        
        # Test all factories create working adapters
        gmail = await create_gmail_adapter(config={"mock_mode": True})
        drive = await create_drive_adapter(config={"mock_mode": True})
        dropbox = await create_dropbox_adapter(config={"mock_mode": True})
        
        assert isinstance(gmail, GmailHeadersAdapter)
        assert isinstance(drive, DriveAdapter)
        assert isinstance(dropbox, DropboxAdapter)
        
        # Test they all implement the common interface
        assert all(hasattr(adapter, method) for adapter in [gmail, drive, dropbox]
                  for method in ["list_resources", "get_resource_metadata", "get_resource_content"])
    
    @pytest.mark.asyncio
    async def test_cross_adapter_consistency(self):
        """Test that all adapters behave consistently"""
        from adapters.drive import create_drive_adapter
        from adapters.dropbox import create_dropbox_adapter
        
        drive = await create_drive_adapter(config={"mock_mode": True})
        dropbox = await create_dropbox_adapter(config={"mock_mode": True})
        
        # Both should handle invalid tokens the same way
        for adapter in [drive, dropbox]:
            with pytest.raises(ValueError, match="Invalid capability token"):
                await adapter.list_resources("invalid_token")
    
    @pytest.mark.asyncio
    async def test_audit_logging(self):
        """Test that all adapters perform audit logging"""
        from adapters.drive import create_drive_adapter
        
        adapter = await create_drive_adapter(config={"mock_mode": True})
        
        # Mock the logging method to capture calls
        log_calls = []
        original_log = adapter._log_operation
        
        async def mock_log(*args, **kwargs):
            log_calls.append((args, kwargs))
            await original_log(*args, **kwargs)
        
        adapter._log_operation = mock_log
        
        # Perform operation that should trigger logging
        try:
            await adapter.list_resources("mock_valid_token")
        except:
            pass  # We expect this to fail, we just want to test logging
        
        # Verify logging occurred
        assert len(log_calls) > 0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])