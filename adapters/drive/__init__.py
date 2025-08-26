"""
Google Drive Adapter
===================
Metadata-first Google Drive adapter with file content escalation.

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


class DriveFileMetadata(ResourceMetadata):
    """Extended metadata for Google Drive files"""
    shared_with_me: bool = False
    shared_publicly: bool = False
    folder_path: str = "/"
    version: Optional[int] = None
    download_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    is_folder: bool = False
    permissions: List[Dict[str, str]] = []
    last_viewed_at: Optional[datetime] = None


class DriveAdapter(ServiceAdapter):
    """
    Google Drive adapter with metadata-first design.

    Metadata operations (long TTL):
    - list_resources: File/folder listings with metadata
    - get_resource_metadata: Detailed file information
    - search_resources: Search by name, type, content

    Content operations (short TTL):
    - get_resource_content: Download actual file content
    - put_resource: Upload/update files
    - move_resource: Move files between folders
    """

    def __init__(self, consent_service: ConsentService = None):
        super().__init__("drive", consent_service)
        self.drive_service = None
        self.mock_mode = True

    async def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize Google Drive API client"""
        self.config = config
        self.mock_mode = config.get("mock_mode", True)

        if not self.mock_mode:
            # In production: initialize real Drive API client
            # from googleapiclient.discovery import build
            # self.drive_service = build('drive', 'v3', credentials=creds)
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
                    "service": "drive",
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
    ) -> List[DriveFileMetadata]:
        """
        List Drive files/folders with metadata only.

        Requires: files.list.metadata scope
        Returns: File metadata without content
        """
        required_scopes = ["files.list.metadata"]
        await self.verify_capability_token(capability_token, required_scopes)

        try:
            if self.mock_mode:
                files = self._generate_mock_drive_files(limit, parent_id, resource_type)
            else:
                files = await self._fetch_drive_files(parent_id, resource_type, limit)

            await self._log_operation(
                "list_resources",
                success=True,
                metadata={"count": len(files), "parent_id": parent_id}
            )

            return files

        except Exception as e:
            await self._log_operation("list_resources", success=False, error=str(e))
            raise

    async def get_resource_metadata(
        self,
        capability_token: str,
        resource_id: str
    ) -> DriveFileMetadata:
        """
        Get detailed file metadata.

        Requires: files.read.metadata scope
        Returns: Complete metadata including permissions
        """
        required_scopes = ["files.read.metadata"]
        await self.verify_capability_token(capability_token, required_scopes, resource_id)

        try:
            if self.mock_mode:
                file_metadata = self._generate_mock_file_metadata(resource_id)
            else:
                file_metadata = await self._fetch_drive_file_metadata(resource_id)

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
                content = await self._download_drive_file(resource_id)

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
        Returns: Upload result with new file ID
        """
        required_scopes = ["files.write"]
        await self.verify_capability_token(capability_token, required_scopes)

        try:
            if self.mock_mode:
                file_id = self._mock_upload_file(parent_id, name, content, content_type)
            else:
                file_id = await self._upload_drive_file(parent_id, name, content, content_type)

            await self._log_operation(
                "put_resource",
                resource_id=file_id,
                success=True,
                metadata={"name": name, "size": len(content)}
            )

            return OperationResult(
                success=True,
                resource_id=file_id,
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
                result = await self._move_drive_file(resource_id, new_parent_id, new_name)

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
    ) -> List[DriveFileMetadata]:
        """
        Search Drive files by name, content, or metadata.

        Requires: files.search scope
        Returns: Matching files with metadata only
        """
        required_scopes = ["files.search", "files.list.metadata"]
        await self.verify_capability_token(capability_token, required_scopes)

        try:
            if self.mock_mode:
                results = self._mock_search_files(query)
            else:
                results = await self._search_drive_files(query)

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
        Set up Drive change notifications.

        Requires: files.watch scope
        Returns: Watch channel ID
        """
        required_scopes = ["files.watch"]
        await self.verify_capability_token(capability_token, required_scopes)

        try:
            if self.mock_mode:
                watch_id = f"drive_watch_{datetime.now().timestamp()}"
            else:
                watch_id = await self._setup_drive_watch(watch_request)

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
        Remove Drive watch channel.

        Requires: files.watch scope
        Returns: Unwatch operation result
        """
        required_scopes = ["files.watch"]
        await self.verify_capability_token(capability_token, required_scopes)

        try:
            if self.mock_mode:
                success = True
            else:
                success = await self._stop_drive_watch(watch_id)

            await self._log_operation(
                "unwatch_resources",
                success=success,
                metadata={"watch_id": watch_id}
            )

            return OperationResult(
                success=success,
                message=f"Watch {watch_id} removed"
            )

        except Exception as e:
            await self._log_operation("unwatch_resources", success=False, error=str(e))
            raise

    # Private helper methods for mock data generation

    def _generate_mock_drive_files(
        self,
        limit: int,
        parent_id: Optional[str],
        resource_type: Optional[str]
    ) -> List[DriveFileMetadata]:
        """Generate mock Drive file listings"""
        mock_files = []

        file_types = [
            ("document.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", False),
            ("spreadsheet.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", False),
            ("presentation.pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation", False),
            ("image.jpg", "image/jpeg", False),
            ("Projects", "application/vnd.google-apps.folder", True),
            ("Archive", "application/vnd.google-apps.folder", True),
            ("notes.txt", "text/plain", False),
            ("budget.pdf", "application/pdf", False)
        ]

        for i in range(min(limit, len(file_types))):
            name, mime_type, is_folder = file_types[i]

            mock_files.append(DriveFileMetadata(
                id=f"drive_file_{i+1:03d}",
                name=f"{i+1:02d}_{name}",
                type="folder" if is_folder else "file",
                size=None if is_folder else 1024 + i * 2048,
                mime_type=mime_type,
                created_at=datetime.now(timezone.utc) - timedelta(days=i),
                modified_at=datetime.now(timezone.utc) - timedelta(hours=i),
                owner="gonzo@lukhas.com",
                parent_id=parent_id or "root",
                shared_with_me=i % 3 == 0,
                shared_publicly=i % 5 == 0,
                folder_path="/My Drive/" + (f"{parent_id}/" if parent_id else ""),
                is_folder=is_folder,
                permissions=[
                    {"type": "user", "role": "owner", "email": "gonzo@lukhas.com"},
                    {"type": "user", "role": "reader", "email": "alice@example.com"}
                ] if i % 3 == 0 else [],
                version=1 + i,
                last_viewed_at=datetime.now(timezone.utc) - timedelta(hours=i*2)
            ))

        # Filter by resource type if specified
        if resource_type:
            if resource_type == "folder":
                mock_files = [f for f in mock_files if f.is_folder]
            elif resource_type == "file":
                mock_files = [f for f in mock_files if not f.is_folder]

        return mock_files

    def _generate_mock_file_metadata(self, file_id: str) -> DriveFileMetadata:
        """Generate detailed mock file metadata"""
        return DriveFileMetadata(
            id=file_id,
            name="project_proposal.docx",
            type="file",
            size=45678,
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            created_at=datetime.now(timezone.utc) - timedelta(days=5),
            modified_at=datetime.now(timezone.utc) - timedelta(hours=2),
            owner="gonzo@lukhas.com",
            parent_id="folder_projects",
            shared_with_me=False,
            shared_publicly=False,
            folder_path="/My Drive/Projects/",
            is_folder=False,
            permissions=[
                {"type": "user", "role": "owner", "email": "gonzo@lukhas.com"},
                {"type": "user", "role": "writer", "email": "alice@example.com"},
                {"type": "user", "role": "commenter", "email": "bob@company.com"}
            ],
            version=3,
            download_url=f"https://drive.google.com/file/d/{file_id}/export?format=docx",
            thumbnail_url=f"https://drive.google.com/thumbnail?id={file_id}&sz=w200",
            last_viewed_at=datetime.now(timezone.utc) - timedelta(hours=1)
        )

    def _generate_mock_file_content(self, file_id: str) -> ResourceContent:
        """Generate mock file content"""
        metadata = self._generate_mock_file_metadata(file_id)

        # Generate fake document content
        document_content = f"""Project Proposal - LUKHAS Integration
=====================================

Date: {datetime.now().strftime('%Y-%m-%d')}
Author: Gonzo
File ID: {file_id}

Executive Summary
-----------------
This document outlines the proposal for integrating LUKHAS AI capabilities
with existing cloud services through a unified consent framework.

Key Features:
- Metadata-first access patterns
- Capability-based authorization
- Content escalation on demand
- Complete audit trails

Technical Architecture
----------------------
The system uses service adapters to provide a common interface across
Google Drive, Dropbox, and other cloud providers.

Implementation Timeline
-----------------------
Phase 1: Core adapters (4 weeks)
Phase 2: Studio integration (2 weeks)
Phase 3: Testing and deployment (2 weeks)

---
This is a mock document generated for development purposes.
File size: {metadata.size} bytes
"""

        return ResourceContent(
            metadata=metadata,
            content=document_content.encode('utf-8'),
            encoding='utf-8',
            content_type='text/plain'
        )

    def _mock_upload_file(
        self,
        parent_id: Optional[str],
        name: str,
        content: bytes,
        content_type: str
    ) -> str:
        """Mock file upload"""
        # Generate mock file ID based on content hash
        content_hash = hashlib.sha256(  # Changed from MD5 for securitycontent).hexdigest()[:16]
        file_id = f"upload_{content_hash}"
        return file_id

    def _mock_move_file(
        self,
        file_id: str,
        new_parent_id: str,
        new_name: Optional[str]
    ) -> OperationResult:
        """Mock file move operation"""
        return OperationResult(
            success=True,
            resource_id=file_id,
            message=f"File moved to folder {new_parent_id}"
        )

    def _mock_search_files(self, query: SearchQuery) -> List[DriveFileMetadata]:
        """Mock file search"""
        all_files = self._generate_mock_drive_files(100, None, None)

        if query.query:
            # Simple name-based filtering
            search_term = query.query.lower()
            filtered = [f for f in all_files if search_term in f.name.lower()]
            return filtered[:query.limit]

        return all_files[:query.limit]


# Factory function
async def create_drive_adapter(consent_service: ConsentService = None, config: Dict[str, Any] = None) -> DriveAdapter:
    """Create and initialize Google Drive adapter"""
    adapter = DriveAdapter(consent_service)
    await adapter.initialize(config or {"mock_mode": True})
    return adapter
