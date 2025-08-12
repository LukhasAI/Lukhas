"""
Dropbox Adapter
==============
Metadata-first Dropbox adapter with file content escalation.

System-wide guardrails applied:
1. File metadata by default (name, size, modified, sharing)
2. Content access requires capability token escalation
3. All operations verify capability token scopes  
4. Complete audit trail for file operations

ACK GUARDRAILS
"""

import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from consent.service import ConsentService

from .. import (
    OperationResult,
    ResourceContent,
    ResourceMetadata,
    SearchQuery,
    ServiceAdapter,
    WatchRequest,
)


class DropboxFileMetadata(ResourceMetadata):
    """Extended metadata for Dropbox files"""
    path_display: str = "/"
    path_lower: str = "/"
    content_hash: Optional[str] = None
    is_shared: bool = False
    shared_link_url: Optional[str] = None
    client_modified: Optional[datetime] = None
    server_modified: Optional[datetime] = None
    revision: Optional[str] = None
    is_downloadable: bool = True


class DropboxAdapter(ServiceAdapter):
    """
    Dropbox adapter with metadata-first design.
    
    Metadata operations (long TTL):
    - list_resources: File/folder listings with metadata
    - get_resource_metadata: Detailed file information  
    - search_resources: Search by name and content
    
    Content operations (short TTL):
    - get_resource_content: Download actual file content
    - put_resource: Upload/update files
    - move_resource: Move files between folders
    """

    def __init__(self, consent_service: ConsentService = None):
        super().__init__("dropbox", consent_service)
        self.dropbox_client = None
        self.mock_mode = True

    async def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize Dropbox API client"""
        self.config = config
        self.mock_mode = config.get("mock_mode", True)

        if not self.mock_mode:
            # In production: initialize real Dropbox API client
            # import dropbox
            # self.dropbox_client = dropbox.Dropbox(access_token)
            pass

        await self._log_operation("initialize", success=True)

    async def verify_capability_token(
        self,
        token: str,
        required_scopes: List[str],
        resource_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Verify capability token with consent service"""
        if self.consent_service:
            return await self.consent_service.verify_capability_token(
                token, required_scopes, resource_id
            )
        else:
            # Mock verification for development
            if token.startswith("mock_"):
                return {
                    "lid": "gonzo",
                    "service": "dropbox",
                    "scopes": required_scopes,
                    "valid": True
                }
            else:
                raise ValueError("Invalid capability token")

    async def list_resources(
        self,
        capability_token: str,
        parent_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        limit: int = 100
    ) -> List[DropboxFileMetadata]:
        """
        List Dropbox files/folders with metadata only.
        
        Requires: files.list.metadata scope
        Returns: File metadata without content
        """
        required_scopes = ["files.list.metadata"]
        await self.verify_capability_token(capability_token, required_scopes)

        try:
            if self.mock_mode:
                files = self._generate_mock_dropbox_files(limit, parent_id, resource_type)
            else:
                files = await self._fetch_dropbox_files(parent_id, resource_type, limit)

            await self._log_operation(
                "list_resources",
                success=True,
                metadata={"count": len(files), "parent_path": parent_id}
            )

            return files

        except Exception as e:
            await self._log_operation("list_resources", success=False, error=str(e))
            raise

    async def get_resource_metadata(
        self,
        capability_token: str,
        resource_id: str
    ) -> DropboxFileMetadata:
        """
        Get detailed file metadata.
        
        Requires: files.read.metadata scope
        Returns: Complete metadata including sharing info
        """
        required_scopes = ["files.read.metadata"]
        await self.verify_capability_token(capability_token, required_scopes, resource_id)

        try:
            if self.mock_mode:
                file_metadata = self._generate_mock_file_metadata(resource_id)
            else:
                file_metadata = await self._fetch_dropbox_metadata(resource_id)

            await self._log_operation(
                "get_resource_metadata",
                resource_id=resource_id,
                success=True
            )

            return file_metadata

        except Exception as e:
            await self._log_operation(
                "get_resource_metadata",
                resource_id=resource_id,
                success=False,
                error=str(e)
            )
            raise

    async def get_resource_content(
        self,
        capability_token: str,
        resource_id: str
    ) -> ResourceContent:
        """
        Download actual file content.
        
        Requires: files.read.content scope (escalated capability)
        Returns: File content with metadata
        """
        required_scopes = ["files.read.content"]
        await self.verify_capability_token(capability_token, required_scopes, resource_id)

        try:
            if self.mock_mode:
                content = self._generate_mock_file_content(resource_id)
            else:
                content = await self._download_dropbox_file(resource_id)

            await self._log_operation(
                "get_resource_content",
                resource_id=resource_id,
                success=True,
                metadata={"content_size": len(content.content)}
            )

            return content

        except Exception as e:
            await self._log_operation(
                "get_resource_content",
                resource_id=resource_id,
                success=False,
                error=str(e)
            )
            raise

    async def put_resource(
        self,
        capability_token: str,
        parent_id: Optional[str],
        name: str,
        content: bytes,
        content_type: str
    ) -> OperationResult:
        """
        Upload or update file.
        
        Requires: files.write scope
        Returns: Upload result with file path
        """
        required_scopes = ["files.write"]
        await self.verify_capability_token(capability_token, required_scopes)

        try:
            if self.mock_mode:
                file_path = self._mock_upload_file(parent_id, name, content, content_type)
            else:
                file_path = await self._upload_dropbox_file(parent_id, name, content, content_type)

            await self._log_operation(
                "put_resource",
                resource_id=file_path,
                success=True,
                metadata={"name": name, "size": len(content)}
            )

            return OperationResult(
                success=True,
                resource_id=file_path,
                message=f"File '{name}' uploaded successfully"
            )

        except Exception as e:
            await self._log_operation(
                "put_resource",
                success=False,
                error=str(e),
                metadata={"name": name}
            )
            raise

    async def move_resource(
        self,
        capability_token: str,
        resource_id: str,
        new_parent_id: str,
        new_name: Optional[str] = None
    ) -> OperationResult:
        """
        Move file to different folder.
        
        Requires: files.move scope
        Returns: Move operation result
        """
        required_scopes = ["files.move"]
        await self.verify_capability_token(capability_token, required_scopes, resource_id)

        try:
            if self.mock_mode:
                result = self._mock_move_file(resource_id, new_parent_id, new_name)
            else:
                result = await self._move_dropbox_file(resource_id, new_parent_id, new_name)

            await self._log_operation(
                "move_resource",
                resource_id=resource_id,
                success=True,
                metadata={"new_parent": new_parent_id, "new_name": new_name}
            )

            return result

        except Exception as e:
            await self._log_operation(
                "move_resource",
                resource_id=resource_id,
                success=False,
                error=str(e)
            )
            raise

    async def search_resources(
        self,
        capability_token: str,
        query: SearchQuery
    ) -> List[DropboxFileMetadata]:
        """
        Search Dropbox files by name or content.
        
        Requires: files.search scope
        Returns: Matching files with metadata only
        """
        required_scopes = ["files.search", "files.list.metadata"]
        await self.verify_capability_token(capability_token, required_scopes)

        try:
            if self.mock_mode:
                results = self._mock_search_files(query)
            else:
                results = await self._search_dropbox_files(query)

            await self._log_operation(
                "search_resources",
                success=True,
                metadata={"query": query.query, "results": len(results)}
            )

            return results

        except Exception as e:
            await self._log_operation("search_resources", success=False, error=str(e))
            raise

    async def watch_resources(
        self,
        capability_token: str,
        watch_request: WatchRequest
    ) -> str:
        """
        Set up Dropbox webhooks for file changes.
        
        Requires: files.watch scope
        Returns: Webhook ID
        """
        required_scopes = ["files.watch"]
        await self.verify_capability_token(capability_token, required_scopes)

        try:
            if self.mock_mode:
                watch_id = f"dropbox_webhook_{datetime.now().timestamp()}"
            else:
                watch_id = await self._setup_dropbox_webhook(watch_request)

            await self._log_operation(
                "watch_resources",
                success=True,
                metadata={"watch_id": watch_id, "webhook": watch_request.webhook_url}
            )

            return watch_id

        except Exception as e:
            await self._log_operation("watch_resources", success=False, error=str(e))
            raise

    async def unwatch_resources(
        self,
        capability_token: str,
        watch_id: str
    ) -> OperationResult:
        """
        Remove Dropbox webhook.
        
        Requires: files.watch scope
        Returns: Unwatch operation result
        """
        required_scopes = ["files.watch"]
        await self.verify_capability_token(capability_token, required_scopes)

        try:
            if self.mock_mode:
                success = True
            else:
                success = await self._remove_dropbox_webhook(watch_id)

            await self._log_operation(
                "unwatch_resources",
                success=success,
                metadata={"watch_id": watch_id}
            )

            return OperationResult(
                success=success,
                message=f"Webhook {watch_id} removed"
            )

        except Exception as e:
            await self._log_operation("unwatch_resources", success=False, error=str(e))
            raise

    # Private helper methods for mock data generation

    def _generate_mock_dropbox_files(
        self,
        limit: int,
        parent_path: Optional[str],
        resource_type: Optional[str]
    ) -> List[DropboxFileMetadata]:
        """Generate mock Dropbox file listings"""
        mock_files = []
        base_path = parent_path or "/"

        file_entries = [
            ("Meeting Notes.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", False),
            ("Budget 2024.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", False),
            ("Product Photos", "folder", True),
            ("Contracts", "folder", True),
            ("presentation.pdf", "application/pdf", False),
            ("logo.png", "image/png", False),
            ("backup.zip", "application/zip", False),
            ("readme.txt", "text/plain", False)
        ]

        for i, (name, mime_type, is_folder) in enumerate(file_entries[:limit]):
            file_path = f"{base_path.rstrip('/')}/{name}"
            content_hash = hashlib.sha256(f"{file_path}{i}".encode()).hexdigest()[:32]

            mock_files.append(DropboxFileMetadata(
                id=file_path,  # Dropbox uses path as ID
                name=name,
                type="folder" if is_folder else "file",
                size=None if is_folder else 2048 + i * 1024,
                mime_type=mime_type,
                created_at=datetime.now(timezone.utc) - timedelta(days=10-i),
                modified_at=datetime.now(timezone.utc) - timedelta(hours=24-i),
                path_display=file_path,
                path_lower=file_path.lower(),
                content_hash=None if is_folder else content_hash,
                is_shared=i % 4 == 0,
                shared_link_url=f"https://dropbox.com/s/{content_hash[:16]}/{name}" if i % 4 == 0 else None,
                client_modified=datetime.now(timezone.utc) - timedelta(hours=25-i),
                server_modified=datetime.now(timezone.utc) - timedelta(hours=24-i),
                revision=f"rev_{i+1:03d}",
                is_downloadable=not is_folder
            ))

        # Filter by resource type if specified
        if resource_type:
            if resource_type == "folder":
                mock_files = [f for f in mock_files if f.type == "folder"]
            elif resource_type == "file":
                mock_files = [f for f in mock_files if f.type == "file"]

        return mock_files

    def _generate_mock_file_metadata(self, file_path: str) -> DropboxFileMetadata:
        """Generate detailed mock file metadata"""
        name = file_path.split("/")[-1] or "document.pdf"
        content_hash = hashlib.sha256(file_path.encode()).hexdigest()[:32]

        return DropboxFileMetadata(
            id=file_path,
            name=name,
            type="file",
            size=87654,
            mime_type="application/pdf",
            created_at=datetime.now(timezone.utc) - timedelta(days=3),
            modified_at=datetime.now(timezone.utc) - timedelta(hours=6),
            path_display=file_path,
            path_lower=file_path.lower(),
            content_hash=content_hash,
            is_shared=True,
            shared_link_url=f"https://dropbox.com/s/{content_hash[:16]}/{name}",
            client_modified=datetime.now(timezone.utc) - timedelta(hours=7),
            server_modified=datetime.now(timezone.utc) - timedelta(hours=6),
            revision="rev_045abc123",
            is_downloadable=True
        )

    def _generate_mock_file_content(self, file_path: str) -> ResourceContent:
        """Generate mock file content"""
        metadata = self._generate_mock_file_metadata(file_path)

        # Generate fake document content
        document_content = f"""LUKHAS Dropbox Integration Document
===================================

File Path: {file_path}
Content Hash: {metadata.content_hash}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Overview
--------
This document demonstrates the Dropbox adapter integration
with the LUKHAS consent framework.

Key Features:
- Metadata-first file listings
- Content access with capability tokens
- Move and upload operations
- Real-time change notifications via webhooks

Technical Details
-----------------
The Dropbox adapter implements the ServiceAdapter interface
and provides complete audit trails for all file operations.

File Operations:
1. list_resources() - List files with metadata only
2. get_resource_content() - Download file content (escalated)
3. put_resource() - Upload new files
4. move_resource() - Reorganize file structure
5. search_resources() - Find files by name/content

Security Model
--------------
All operations require valid capability tokens with appropriate
scopes verified through the consent service.

---
This is a mock document for development and testing.
Actual file size: {metadata.size} bytes
"""

        return ResourceContent(
            metadata=metadata,
            content=document_content.encode('utf-8'),
            encoding='utf-8',
            content_type='text/plain'
        )

    def _mock_upload_file(
        self,
        parent_path: Optional[str],
        name: str,
        content: bytes,
        content_type: str
    ) -> str:
        """Mock file upload"""
        base_path = parent_path or "/"
        file_path = f"{base_path.rstrip('/')}/{name}"
        return file_path

    def _mock_move_file(
        self,
        file_path: str,
        new_parent_path: str,
        new_name: Optional[str]
    ) -> OperationResult:
        """Mock file move operation"""
        old_name = file_path.split("/")[-1]
        final_name = new_name or old_name
        new_path = f"{new_parent_path.rstrip('/')}/{final_name}"

        return OperationResult(
            success=True,
            resource_id=new_path,
            message=f"File moved from {file_path} to {new_path}"
        )

    def _mock_search_files(self, query: SearchQuery) -> List[DropboxFileMetadata]:
        """Mock file search"""
        all_files = self._generate_mock_dropbox_files(100, "/", None)

        if query.query:
            # Simple name-based filtering
            search_term = query.query.lower()
            filtered = [f for f in all_files if search_term in f.name.lower()]
            return filtered[:query.limit]

        # Apply other filters
        filtered = all_files

        if query.size_min:
            filtered = [f for f in filtered if f.size and f.size >= query.size_min]

        if query.size_max:
            filtered = [f for f in filtered if f.size and f.size <= query.size_max]

        if query.modified_after:
            filtered = [f for f in filtered if f.modified_at and f.modified_at >= query.modified_after]

        if query.modified_before:
            filtered = [f for f in filtered if f.modified_at and f.modified_at <= query.modified_before]

        return filtered[:query.limit]


# Factory function
async def create_dropbox_adapter(consent_service: ConsentService = None, config: Dict[str, Any] = None) -> DropboxAdapter:
    """Create and initialize Dropbox adapter"""
    adapter = DropboxAdapter(consent_service)
    await adapter.initialize(config or {"mock_mode": True})
    return adapter
