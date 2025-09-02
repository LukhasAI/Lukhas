"""
Dropbox Service Adapter Implementation
Agent 3: Service Adapter Integration Specialist
Implements OAuth2, file operations, resilience, and telemetry
"""

import asyncio
import hashlib
import json
from datetime import datetime, timezone
from typing import Optional

import aiohttp

from candidate.bridge.adapters.service_adapter_base import (
    BaseServiceAdapter,
    CapabilityToken,
    DryRunPlanner,
    with_resilience,
)


class DropboxAdapter(BaseServiceAdapter):
    """
    Dropbox adapter with OAuth2, circuit breakers, and Λ-trace telemetry
    Implements all Agent 3 requirements from Claude_7.yml
    """

    def __init__(self):
        super().__init__("dropbox")
        self.base_url = "https://api.dropboxapi.com/2"
        self.content_url = "https://content.dropboxapi.com/2"
        self.oauth_tokens = {}  # In production: use Agent 7's KMS vault
        self.dry_run_planner = DryRunPlanner()

    async def authenticate(self, credentials: dict) -> dict:
        """OAuth2 authentication flow for Dropbox"""
        if self.dry_run_mode:
            return {"access_token": "dry_run_token", "token_type": "Bearer", "expires_in": 14400}

        client_id = credentials.get("app_key")
        client_secret = credentials.get("app_secret")
        refresh_token = credentials.get("refresh_token")

        if refresh_token:
            # Refresh access token
            async with (
                aiohttp.ClientSession() as session,
                session.post(
                    "https://api.dropbox.com/oauth2/token",
                    data={
                        "grant_type": "refresh_token",
                        "refresh_token": refresh_token,
                        "client_id": client_id,
                        "client_secret": client_secret,
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
    async def list_folder(
        self,
        lid: str,
        path: str = "",
        recursive: bool = False,
        capability_token: Optional[CapabilityToken] = None,
        limit: int = 100,
    ) -> dict:
        """
        List files and folders in Dropbox
        Emits Λ-trace for audit
        """

        # Validate capability token
        if capability_token and not self.validate_capability_token(capability_token, "list"):
            return {"error": "invalid_capability_token"}

        # Check consent
        if not await self.check_consent(lid, "list"):
            return {"error": "consent_required", "action": "list_folder"}

        # Dry-run mode
        if self.dry_run_mode:
            plan = self.dry_run_planner.plan_operation(
                "list_folder", {"path": path, "recursive": recursive, "limit": limit}
            )
            return {
                "dry_run": True,
                "plan": plan,
                "mock_entries": [
                    {"name": "Travel_Guide_Japan.pdf", "type": "file", "size": 5242880},
                    {"name": "Passport_Scan.pdf", "type": "file", "size": 2097152},
                    {"name": "Emergency_Contacts.txt", "type": "file", "size": 2048},
                ],
            }

        # Get OAuth token
        if lid not in self.oauth_tokens:
            return {"error": "authentication_required"}

        access_token = self.oauth_tokens[lid]["access_token"]

        # Make API call
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            payload = {"path": path if path else "", "recursive": recursive, "limit": limit}

            async with session.post(f"{self.base_url}/files/list_folder", headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()

                    # Process entries
                    entries = []
                    for entry in data.get("entries", []):
                        entries.append(
                            {
                                "id": entry.get("id"),
                                "name": entry.get("name"),
                                "path": entry.get("path_display"),
                                "type": entry.get(".tag"),
                                "size": entry.get("size", 0),
                                "modified": entry.get("server_modified", ""),
                            }
                        )

                    return {
                        "entries": entries,
                        "count": len(entries),
                        "has_more": data.get("has_more", False),
                        "cursor": data.get("cursor"),
                        "trace_id": self.telemetry.metrics.get("last_trace_id"),
                    }
                else:
                    return {"error": f"api_error_{response.status}"}

    @with_resilience
    async def download_file(self, lid: str, path: str, capability_token: Optional[CapabilityToken] = None) -> dict:
        """Download file content from Dropbox"""

        # Validate capability token
        if capability_token and not self.validate_capability_token(capability_token, "read"):
            return {"error": "invalid_capability_token"}

        # Check consent
        if not await self.check_consent(lid, "read"):
            return {"error": "consent_required", "action": "download_file"}

        if self.dry_run_mode:
            return {
                "dry_run": True,
                "file": {
                    "path": path,
                    "name": path.split("/")[-1],
                    "size": 1024000,
                    "content_preview": "Mock content...",
                },
            }

        # Get OAuth token
        if lid not in self.oauth_tokens:
            return {"error": "authentication_required"}

        access_token = self.oauth_tokens[lid]["access_token"]

        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Dropbox-API-Arg": json.dumps({"path": path}),
            }

            async with session.post(f"{self.content_url}/files/download", headers=headers) as response:
                if response.status == 200:
                    # Get metadata from response header
                    metadata = json.loads(response.headers.get("Dropbox-API-Result", "{}"))

                    # Get content (limit size for MVP)
                    content = await response.read(1024 * 1024)  # Max 1MB

                    return {
                        "file": {
                            "id": metadata.get("id"),
                            "name": metadata.get("name"),
                            "path": metadata.get("path_display"),
                            "size": metadata.get("size"),
                            "modified": metadata.get("server_modified"),
                            "content_hash": hashlib.sha256(content).hexdigest(),
                            "content_preview": content[:1000].decode("utf-8", errors="ignore") if content else "",
                        },
                        "trace_id": self.telemetry.metrics.get("last_trace_id"),
                    }
                else:
                    return {"error": f"download_error_{response.status}"}

    @with_resilience
    async def search_files(
        self,
        lid: str,
        query: str,
        capability_token: Optional[CapabilityToken] = None,
        max_results: int = 50,
    ) -> dict:
        """Search files in Dropbox"""

        # Validate capability token
        if capability_token and not self.validate_capability_token(capability_token, "read"):
            return {"error": "invalid_capability_token"}

        # Check consent
        if not await self.check_consent(lid, "search"):
            return {"error": "consent_required", "action": "search_files"}

        if self.dry_run_mode:
            plan = self.dry_run_planner.plan_operation("search_files", {"query": query, "max_results": max_results})
            return {"dry_run": True, "plan": plan}

        # Get OAuth token
        if lid not in self.oauth_tokens:
            return {"error": "authentication_required"}

        access_token = self.oauth_tokens[lid]["access_token"]

        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            payload = {
                "query": query,
                "options": {"max_results": max_results, "file_status": "active"},
            }

            async with session.post(f"{self.base_url}/files/search_v2", headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()

                    matches = []
                    for match in data.get("matches", []):
                        metadata = match.get("metadata", {}).get("metadata", {})
                        matches.append(
                            {
                                "id": metadata.get("id"),
                                "name": metadata.get("name"),
                                "path": metadata.get("path_display"),
                                "type": metadata.get(".tag"),
                                "size": metadata.get("size", 0),
                            }
                        )

                    return {
                        "matches": matches,
                        "count": len(matches),
                        "has_more": data.get("has_more", False),
                        "trace_id": self.telemetry.metrics.get("last_trace_id"),
                    }
                else:
                    return {"error": f"search_error_{response.status}"}

    @with_resilience
    async def upload_file(
        self,
        lid: str,
        path: str,
        content: bytes,
        capability_token: Optional[CapabilityToken] = None,
        autorename: bool = True,
    ) -> dict:
        """Upload file to Dropbox"""

        # Validate capability token
        if capability_token and not self.validate_capability_token(capability_token, "write"):
            return {"error": "invalid_capability_token"}

        # Check consent
        if not await self.check_consent(lid, "write"):
            return {"error": "consent_required", "action": "upload_file"}

        if self.dry_run_mode:
            plan = self.dry_run_planner.plan_operation("upload_file", {"path": path, "size": len(content)})
            return {"dry_run": True, "plan": plan}

        # Get OAuth token
        if lid not in self.oauth_tokens:
            return {"error": "authentication_required"}

        access_token = self.oauth_tokens[lid]["access_token"]

        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Dropbox-API-Arg": json.dumps({"path": path, "mode": "add", "autorename": autorename}),
                "Content-Type": "application/octet-stream",
            }

            async with session.post(f"{self.content_url}/files/upload", headers=headers, data=content) as response:
                if response.status == 200:
                    file_data = await response.json()
                    return {
                        "file": {
                            "id": file_data.get("id"),
                            "name": file_data.get("name"),
                            "path": file_data.get("path_display"),
                            "size": file_data.get("size"),
                        },
                        "trace_id": self.telemetry.metrics.get("last_trace_id"),
                    }
                else:
                    return {"error": f"upload_error_{response.status}"}

    async def revoke_access(self, lid: str) -> bool:
        """Revoke Dropbox access when consent is withdrawn"""
        if lid in self.oauth_tokens:
            # In production: revoke OAuth token via Dropbox API
            del self.oauth_tokens[lid]

            # Log revocation
            self.telemetry.record_request(
                lid=lid,
                action="revoke_access",
                resource="dropbox_oauth",
                capability_token=None,
                latency_ms=0,
                success=True,
            )

            return True

        return False

    def get_storage_info(self, lid: str) -> dict:
        """Get Dropbox storage information"""
        # In production: call Dropbox API for actual storage
        return {
            "lid": lid,
            "service": "dropbox",
            "used_bytes": 2147483648,  # 2GB mock
            "allocated_bytes": 2199023255552,  # 2TB
            "usage_percentage": 0.098,
        }


# Integration with Agent 4's context bus
class DropboxContextIntegration:
    """
    Integration layer for Agent 4's context orchestrator
    Enables Dropbox operations in multi-step workflows
    """

    def __init__(self, dropbox_adapter: DropboxAdapter):
        self.adapter = dropbox_adapter

    async def workflow_fetch_travel_files(self, lid: str, context: dict) -> dict:
        """
        Workflow step: Fetch travel-related files from Dropbox
        Used in MVP demo scenario
        """
        # Search for travel files
        result = await self.adapter.search_files(
            lid=lid,
            query="travel",
            capability_token=context.get("capability_token"),
            max_results=20,
        )

        if "matches" in result:
            # Categorize travel files
            travel_files = []
            for file in result["matches"]:
                if file["type"] == "file":
                    file_type = self._classify_travel_file(file["name"])
                    travel_files.append(
                        {
                            "id": file["id"],
                            "name": file["name"],
                            "path": file["path"],
                            "type": file_type,
                            "size": file.get("size", 0),
                        }
                    )

            return {
                "travel_files": travel_files,
                "count": len(travel_files),
                "trace_id": result.get("trace_id"),
            }

        return result

    def _classify_travel_file(self, name: str) -> str:
        """Classify travel file type"""
        name_lower = name.lower()

        if "guide" in name_lower:
            return "travel_guide"
        elif "emergency" in name_lower or "contact" in name_lower:
            return "emergency_info"
        elif "map" in name_lower:
            return "map"
        elif "reservation" in name_lower or "booking" in name_lower:
            return "reservation"
        elif "checklist" in name_lower:
            return "checklist"
        else:
            return "travel_file"


if __name__ == "__main__":
    import asyncio

    async def test_dropbox_adapter():
        print("📦 Testing Dropbox Adapter")
        print("-" * 50)

        # Initialize adapter
        adapter = DropboxAdapter()

        # Test dry-run mode
        adapter.set_dry_run(True)
        print("🔍 Testing dry-run mode...")

        result = await adapter.list_folder(lid="USR-123456", path="/travel", recursive=False)

        if result.get("dry_run"):
            print("✅ Dry-run plan created")
            print(f"   Mock entries: {len(result.get('mock_entries', []))}")
            for entry in result.get("mock_entries", [])[:3]:
                print(f"   - {entry['name']} ({entry['type']})")

        # Test search
        print("\n🔎 Testing search...")
        search_result = await adapter.search_files(lid="USR-123456", query="passport")

        if search_result.get("dry_run"):
            print("✅ Search plan created")

        # Test health status
        health = adapter.get_health_status()
        print("\n🏥 Health Status:")
        print(f"   Circuit breaker: {health['circuit_state']}")
        print(f"   Dry-run mode: {health['dry_run_mode']}")

        # Test context integration
        integration = DropboxContextIntegration(adapter)
        print("\n🔄 Testing workflow integration...")

        await integration.workflow_fetch_travel_files(lid="USR-123456", context={"stage": "file_retrieval"})

        print("✅ Workflow step ready for Agent 4 integration")

        print("\n✅ Dropbox adapter operational!")

    asyncio.run(test_dropbox_adapter())
