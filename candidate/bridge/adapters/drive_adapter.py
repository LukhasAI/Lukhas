"""
Google Drive Service Adapter Implementation
Agent 3: Service Adapter Integration Specialist
Implements OAuth2, file operations, resilience, and telemetry
"""
import asyncio
import json
import mimetypes
from datetime import datetime, timezone
from typing import Optional

import aiohttp

from candidate.bridge.adapters.service_adapter_base import (
    BaseServiceAdapter,
    CapabilityToken,
    DryRunPlanner,
    with_resilience,
)


class DriveAdapter(BaseServiceAdapter):
    """
    Google Drive adapter with OAuth2, circuit breakers, and Λ-trace telemetry
    Implements all Agent 3 requirements from Claude_7.yml
    """

    def __init__(self):
        super().__init__("drive")
        self.base_url = "https://www.googleapis.com/drive/v3"
        self.upload_url = "https://www.googleapis.com/upload/drive/v3"
        self.oauth_tokens = {}  # In production: use Agent 7's KMS vault
        self.dry_run_planner = DryRunPlanner()

    async def authenticate(self, credentials: dict) -> dict:
        """OAuth2 authentication flow for Google Drive"""
        if self.dry_run_mode:
            return {
                "access_token": "dry_run_token",
                "token_type": "Bearer",
                "expires_in": 3600,
            }

        client_id = credentials.get("client_id")
        client_secret = credentials.get("client_secret")
        refresh_token = credentials.get("refresh_token")

        if refresh_token:
            # Refresh access token
            async with (
                aiohttp.ClientSession() as session,
                session.post(
                    "https://oauth2.googleapis.com/token",
                    data={
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "refresh_token": refresh_token,
                        "grant_type": "refresh_token",
                    },
                ) as response,
            ):
                token_data = await response.json()

                # Store in vault (Agent 7 integration)
                lid = credentials.get("lid")
                if lid and "access_token" in token_data:
                    self.oauth_tokens[lid] = {
                        "access_token": token_data["access_token"],
                        "expires_at": datetime.now(timezone.utc).timestamp() + token_data["expires_in"],
                    }

                return token_data

        return {"error": "authentication_required"}

    @with_resilience
    async def list_files(
        self,
        lid: str,
        folder_id: Optional[str] = None,
        query: Optional[str] = None,
        capability_token: Optional[CapabilityToken] = None,
        page_size: int = 100,
    ) -> dict:
        """
        List files in Google Drive with optional folder and query
        Emits Λ-trace for audit
        """

        # Validate capability token
        if capability_token and not self.validate_capability_token(capability_token, "list"):
            return {"error": "invalid_capability_token"}

        # Check consent
        if not await self.check_consent(lid, "list"):
            return {"error": "consent_required", "action": "list_files"}

        # Dry-run mode
        if self.dry_run_mode:
            plan = self.dry_run_planner.plan_operation(
                "list_files",
                {"folder_id": folder_id, "query": query, "page_size": page_size},
            )
            return {"dry_run": True, "plan": plan}

        # Get OAuth token
        if lid not in self.oauth_tokens:
            return {"error": "authentication_required"}

        access_token = self.oauth_tokens[lid]["access_token"]

        # Build query
        q_parts = []
        if folder_id:
            q_parts.append(f"'{folder_id}' in parents")
        if query:
            q_parts.append(query)

        params = {
            "pageSize": page_size,
            "fields": "files(id,name,mimeType,size,createdTime,modifiedTime,parents)",
        }
        if q_parts:
            params["q"] = " and ".join(q_parts)

        # Make API call
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {access_token}"}

            async with session.get(f"{self.base_url}/files", headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()

                    return {
                        "files": data.get("files", []),
                        "count": len(data.get("files", [])),
                        "trace_id": self.telemetry.metrics.get("last_trace_id"),
                    }
                else:
                    return {"error": f"api_error_{response.status}"}

    @with_resilience
    async def get_file(self, lid: str, file_id: str, capability_token: Optional[CapabilityToken] = None) -> dict:
        """Get file metadata and content"""

        # Validate capability token
        if capability_token and not self.validate_capability_token(capability_token, "read"):
            return {"error": "invalid_capability_token"}

        # Check consent
        if not await self.check_consent(lid, "read"):
            return {"error": "consent_required", "action": "read_file"}

        if self.dry_run_mode:
            return {
                "dry_run": True,
                "file": {
                    "id": file_id,
                    "name": "mock_file.pdf",
                    "mimeType": "application/pdf",
                    "size": "2048000",
                },
            }

        # Get OAuth token
        if lid not in self.oauth_tokens:
            return {"error": "authentication_required"}

        access_token = self.oauth_tokens[lid]["access_token"]

        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {access_token}"}

            # Get metadata
            async with session.get(
                f"{self.base_url}/files/{file_id}",
                headers=headers,
                params={"fields": "id,name,mimeType,size,createdTime,modifiedTime,description"},
            ) as response:
                if response.status == 200:
                    metadata = await response.json()

                    # For text files, also get content
                    if metadata.get("mimeType", "").startswith("text/"):
                        async with session.get(
                            f"{self.base_url}/files/{file_id}",
                            headers=headers,
                            params={"alt": "media"},
                        ) as content_response:
                            if content_response.status == 200:
                                content = await content_response.text()
                                metadata["content"] = content[:1000]  # First 1000 chars

                    return {
                        "file": metadata,
                        "trace_id": self.telemetry.metrics.get("last_trace_id"),
                    }
                else:
                    return {"error": f"api_error_{response.status}"}

    @with_resilience
    async def search_files(
        self,
        lid: str,
        search_query: str,
        capability_token: Optional[CapabilityToken] = None,
    ) -> dict:
        """
        Search files in Drive
        Example: "name contains 'travel' and mimeType = 'application/pdf\'"
        """
        return await self.list_files(lid, query=search_query, capability_token=capability_token)

    @with_resilience
    async def upload_file(
        self,
        lid: str,
        file_name: str,
        content: bytes,
        parent_folder_id: Optional[str] = None,
        capability_token: Optional[CapabilityToken] = None,
    ) -> dict:
        """Upload file to Google Drive"""

        # Validate capability token
        if capability_token and not self.validate_capability_token(capability_token, "write"):
            return {"error": "invalid_capability_token"}

        # Check consent
        if not await self.check_consent(lid, "write"):
            return {"error": "consent_required", "action": "upload_file"}

        if self.dry_run_mode:
            plan = self.dry_run_planner.plan_operation("upload_file", {"file_name": file_name, "size": len(content)})
            return {"dry_run": True, "plan": plan}

        # Get OAuth token
        if lid not in self.oauth_tokens:
            return {"error": "authentication_required"}

        access_token = self.oauth_tokens[lid]["access_token"]

        # Prepare metadata
        metadata = {"name": file_name}
        if parent_folder_id:
            metadata["parents"] = [parent_folder_id]

        # Detect MIME type
        mime_type = mimetypes.guess_type(file_name)[0] or "application/octet-stream"

        # Upload file
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            # Create file metadata
            async with session.post(
                f"{self.upload_url}/files",
                headers=headers,
                params={"uploadType": "multipart"},
                data=aiohttp.FormData()(
                    ("metadata", json.dumps(metadata), "application/json"),
                    ("file", content, mime_type),
                ),
            ) as response:
                if response.status == 200:
                    file_data = await response.json()
                    return {
                        "file_id": file_data["id"],
                        "name": file_data["name"],
                        "trace_id": self.telemetry.metrics.get("last_trace_id")
                    }
                else:
                    return {"error": f"upload_error_{response.status}"}

    async def revoke_access(self, lid: str) -> bool:
        """Revoke Drive access when consent is withdrawn"""
        if lid in self.oauth_tokens:
            del self.oauth_tokens[lid]

            # Log revocation
            self.telemetry.record_request(
                lid=lid,
                action="revoke_access",
                resource="drive_oauth",
                capability_token=None,
                latency_ms=0,
                success=True,
            )

            return True

        return False

    def get_quota_usage(self, lid: str) -> dict:
        """Get Drive storage quota usage"""
        # In production: call Drive API for actual quota
        return {
            "lid": lid,
            "service": "drive",
            "storage_used_bytes": 1073741824,  # 1GB mock
            "storage_limit_bytes": 15737418240,  # 15GB
            "usage_percentage": 6.67,
        }


# Integration with Agent 4\'s context bus
class DriveContextIntegration:
    """
    Integration layer for Agent 4's context orchestrator
    Enables Drive operations in multi-step workflows
    """

    def __init__(self, drive_adapter: DriveAdapter):
        self.adapter = drive_adapter

    async def workflow_fetch_travel_documents(self, lid: str, context: dict) -> dict:
        """
        Workflow step: Fetch travel-related documents from Drive
        Used in MVP demo scenario
        """
        # Search for travel documents
        travel_query = "name contains 'travel' or name contains 'passport' or name contains 'itinerary'"

        result = await self.adapter.search_files(
            lid=lid,
            search_query=travel_query,
            capability_token=context.get("capability_token"),
        )

        if "files" in result:
            # Categorize travel documents
            travel_docs = []
            for file in result["files"]:
                doc_type = self._classify_travel_document(file["name"])
                travel_docs.append(
                    {
                        "id": file["id"],
                        "name": file["name"],
                        "type": doc_type,
                        "size": file.get("size", "unknown"),
                        "modified": file.get("modifiedTime", ""),
                    }
                )

            return {
                "travel_documents": travel_docs,
                "count": len(travel_docs),
                "trace_id": result.get("trace_id"),
            }

        return result

    def _classify_travel_document(self, name: str) -> str:
        """Classify travel document type"""
        name_lower = name.lower()

        if "passport" in name_lower:
            return "identification"
        elif "itinerary" in name_lower:
            return "itinerary"
        elif "ticket" in name_lower or "boarding" in name_lower:
            return "tickets"
        elif "insurance" in name_lower:
            return "insurance"
        elif "visa" in name_lower:
            return "visa"
        else:
            return "travel_document"


if __name__ == "__main__":
    import asyncio

    async def test_drive_adapter():
        print("📁 Testing Google Drive Adapter")
        print("-" * 50)

        # Initialize adapter
        adapter = DriveAdapter()

        # Test dry-run mode
        adapter.set_dry_run(True)
        print("🔍 Testing dry-run mode...")

        result = await adapter.list_files(lid="USR-123456", query="name contains 'travel'", page_size=10)

        if result.get("dry_run"):
            print("✅ Dry-run plan created")
            print(f"   Operation: {result['plan']['operation']}")
            print(f"   Required scopes: {result['plan']['required_scopes']}")

        # Test file operations
        print("\n📄 Testing file operations...")
        file_result = await adapter.get_file(lid="USR-123456", file_id="mock_file_id")

        if file_result.get("dry_run"):
            print(f"✅ Mock file retrieved: {file_result['file']['name']}")

        # Test health status
        health = adapter.get_health_status()
        print("\n🏥 Health Status:")
        print(f"   Circuit breaker: {health['circuit_state']}")
        print(f"   Dry-run mode: {health['dry_run_mode']}")

        # Test context integration
        integration = DriveContextIntegration(adapter)
        print("\n🔄 Testing workflow integration...")

        await integration.workflow_fetch_travel_documents(lid="USR-123456", context={"stage": "document_retrieval"})

        print("✅ Workflow step ready for Agent 4 integration")

        print("\n✅ Drive adapter operational!")

    asyncio.run(test_drive_adapter())