"""
LUKHAS Service Adapters
======================
Common interface for external service integrations with capability token validation.

System-wide guardrails applied:
1. All adapters verify capability tokens with required scopes
2. Metadata-only operations by default, content requires escalation
3. No direct vendor calls from orchestrator - use adapters only
4. Complete audit trail for all operations

ACK GUARDRAILS
"""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ResourceMetadata(BaseModel):
    """Standard resource metadata structure across all adapters"""
    id: str = Field(..., description="Unique resource identifier")
    name: str = Field(..., description="Human-readable name")
    type: str = Field(..., description="Resource type (email, file, folder, etc.)")
    size: Optional[int] = Field(None, description="Size in bytes")
    modified_at: Optional[datetime] = Field(None, description="Last modified timestamp")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    owner: Optional[str] = Field(None, description="Resource owner")
    sharing: Optional[Dict[str, Any]] = Field(None, description="Sharing permissions")
    tags: Optional[List[str]] = Field(None, description="Tags or labels")
    parent_id: Optional[str] = Field(None, description="Parent folder/container ID")
    mime_type: Optional[str] = Field(None, description="MIME type for files")
    url: Optional[str] = Field(None, description="Access URL if applicable")


class ResourceContent(BaseModel):
    """Resource content structure (requires content-level capabilities)"""
    metadata: ResourceMetadata
    content: bytes = Field(..., description="Raw content data")
    encoding: Optional[str] = Field(None, description="Content encoding")
    content_type: str = Field(..., description="Content MIME type")


class SearchQuery(BaseModel):
    """Common search query structure"""
    query: Optional[str] = Field(None, description="Text search query")
    type_filter: Optional[str] = Field(None, description="Resource type filter")
    size_min: Optional[int] = Field(None, description="Minimum size filter")
    size_max: Optional[int] = Field(None, description="Maximum size filter")
    modified_after: Optional[datetime] = Field(None, description="Modified after date")
    modified_before: Optional[datetime] = Field(None, description="Modified before date")
    owner_filter: Optional[str] = Field(None, description="Owner filter")
    tags_filter: Optional[List[str]] = Field(None, description="Tags filter")
    limit: int = Field(100, ge=1, le=1000, description="Result limit")
    offset: int = Field(0, ge=0, description="Result offset for pagination")


class WatchRequest(BaseModel):
    """Watch request for real-time updates"""
    resource_id: Optional[str] = Field(None, description="Specific resource to watch")
    resource_type: Optional[str] = Field(None, description="Type of resources to watch")
    webhook_url: str = Field(..., description="Webhook URL for notifications")
    events: List[str] = Field(default=["created", "updated", "deleted"], description="Events to watch")


class OperationResult(BaseModel):
    """Standard operation result structure"""
    success: bool
    resource_id: Optional[str] = None
    message: str
    metadata: Optional[Dict[str, Any]] = None


class ServiceAdapter(ABC):
    """
    Abstract base class for all service adapters.
    
    Defines common interface for external service integrations:
    - list, get, put, move, search, watch operations
    - Capability token verification for all operations
    - Metadata-first design with content escalation
    - Comprehensive error handling and audit logging
    """

    def __init__(self, service_name: str, consent_service=None):
        self.service_name = service_name
        self.consent_service = consent_service

    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the adapter with configuration"""
        pass

    @abstractmethod
    async def verify_capability_token(
        self,
        token: str,
        required_scopes: List[str],
        resource_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Verify capability token has required scopes for operation"""
        pass

    # Core operations (all require capability token verification)

    @abstractmethod
    async def list_resources(
        self,
        capability_token: str,
        parent_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        limit: int = 100
    ) -> List[ResourceMetadata]:
        """List resources with metadata only (requires metadata scope)"""
        pass

    @abstractmethod
    async def get_resource_metadata(
        self,
        capability_token: str,
        resource_id: str
    ) -> ResourceMetadata:
        """Get detailed metadata for specific resource (requires metadata scope)"""
        pass

    @abstractmethod
    async def get_resource_content(
        self,
        capability_token: str,
        resource_id: str
    ) -> ResourceContent:
        """Get full resource content (requires content scope)"""
        pass

    @abstractmethod
    async def put_resource(
        self,
        capability_token: str,
        parent_id: Optional[str],
        name: str,
        content: bytes,
        content_type: str
    ) -> OperationResult:
        """Create or update resource (requires write scope)"""
        pass

    @abstractmethod
    async def move_resource(
        self,
        capability_token: str,
        resource_id: str,
        new_parent_id: str,
        new_name: Optional[str] = None
    ) -> OperationResult:
        """Move resource to different location (requires move scope)"""
        pass

    @abstractmethod
    async def search_resources(
        self,
        capability_token: str,
        query: SearchQuery
    ) -> List[ResourceMetadata]:
        """Search resources (requires appropriate scope based on search depth)"""
        pass

    @abstractmethod
    async def watch_resources(
        self,
        capability_token: str,
        watch_request: WatchRequest
    ) -> str:
        """Set up real-time resource watching (requires watch scope)"""
        pass

    @abstractmethod
    async def unwatch_resources(
        self,
        capability_token: str,
        watch_id: str
    ) -> OperationResult:
        """Remove resource watch (requires watch scope)"""
        pass

    # Helper methods

    async def _log_operation(
        self,
        operation: str,
        resource_id: Optional[str] = None,
        success: bool = True,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log operation for audit trail"""
        # This would integrate with the consent service audit log
        log_entry = {
            "service": self.service_name,
            "operation": operation,
            "resource_id": resource_id,
            "success": success,
            "error": error,
            "metadata": metadata,
            "timestamp": datetime.utcnow()
        }
        print(f"AUDIT: {log_entry}")  # In production: send to audit service

    def _extract_required_scopes(self, operation: str, resource_type: str = None) -> List[str]:
        """Extract required scopes based on operation and resource type"""
        scope_map = {
            "list": [f"{resource_type or 'files'}.list.metadata"],
            "get_metadata": [f"{resource_type or 'files'}.read.metadata"],
            "get_content": [f"{resource_type or 'files'}.read.content"],
            "put": [f"{resource_type or 'files'}.write"],
            "move": [f"{resource_type or 'files'}.move"],
            "search": [f"{resource_type or 'files'}.search"],
            "watch": [f"{resource_type or 'files'}.watch"]
        }
        return scope_map.get(operation, [f"{resource_type or 'files'}.read.metadata"])


__all__ = [
    'ServiceAdapter',
    'ResourceMetadata',
    'ResourceContent',
    'SearchQuery',
    'WatchRequest',
    'OperationResult'
]
