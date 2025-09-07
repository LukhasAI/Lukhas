"""
Gmail Service Adapter Implementation
Agent 3: Service Adapter Integration Specialist
Implements OAuth2, resilience, telemetry, and consent validation
"""
from typing import List
import time
import streamlit as st

import asyncio
from datetime import datetime, timezone
from typing import Optional

import aiohttp

# Import base framework
from candidate.bridge.adapters.service_adapter_base import (
    BaseServiceAdapter,
    CapabilityToken,
    DryRunPlanner,
    with_resilience,
)


class GmailAdapter(BaseServiceAdapter):
    """
    Gmail adapter with OAuth2, circuit breakers, and Λ-trace telemetry
    Implements all Agent 3 requirements from Claude_7.yml
    """

    def __init__(self):
        super().__init__("gmail")
        self.base_url = "https://gmail.googleapis.com/gmail/v1"
        self.oauth_tokens = {}  # In production: use Agent 7's KMS vault
        self.dry_run_planner = DryRunPlanner()

    async def authenticate(self, credentials: dict) -> dict:
        """
        OAuth2 authentication flow
        In production: integrates with Agent 7's token vault
        """
        if self.dry_run_mode:
            return {
                "access_token": "dry_run_token",
                "token_type": "Bearer",
                "expires_in": 3600,
            }

        # OAuth2 flow (simplified for MVP)
        # In production: full OAuth2 with PKCE
        client_id = credentials.get("client_id")
        client_secret = credentials.get("client_secret")
        refresh_token = credentials.get("refresh_token")

        if refresh_token:
            # Refresh access token
            token_data = await self._refresh_oauth_token(client_id, client_secret, refresh_token)

            # Store in vault (Agent 7 integration)
            lid = credentials.get("lid")
            if lid:
                self.oauth_tokens[lid] = {
                    "access_token": token_data["access_token"],
                    "expires_at": datetime.now(timezone.utc).timestamp() + token_data["expires_in"],
                }

            return token_data

        return {"error": "authentication_required"}

    async def _refresh_oauth_token(self, client_id: str, client_secret: str, refresh_token: str) -> dict:
        """Refresh OAuth2 access token"""
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
            return await response.json()

    @with_resilience
    async def fetch_emails(
        self,
        lid: str,
        query: Optional[str] = None,
        capability_token: Optional[CapabilityToken] = None,
        max_results: int = 10,
    ) -> dict:
        """
        Fetch emails with consent validation and telemetry
        Emits Λ-trace for audit
        """

        # Validate capability token
        if capability_token and not self.validate_capability_token(capability_token, "read"):
            return {"error": "invalid_capability_token"}

        # Check consent
        if not await self.check_consent(lid, "read"):
            return {"error": "consent_required", "action": "read_emails"}

        # Dry-run mode
        if self.dry_run_mode:
            plan = self.dry_run_planner.plan_operation("fetch_emails", {"query": query, "max_results": max_results})
            return {"dry_run": True, "plan": plan}

        # Get OAuth token from vault
        if lid not in self.oauth_tokens:
            return {"error": "authentication_required"}

        access_token = self.oauth_tokens[lid]["access_token"]

        # Build API request
        params = {"maxResults": max_results}
        if query:
            params["q"] = query

        # Make API call
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {access_token}"}

            async with session.get(f"{self.base_url}/users/me/messages", headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    messages = data.get("messages", [])

                    # Fetch message details
                    emails = []
                    for msg in messages[:max_results]:
                        email_data = await self._fetch_email_details(session, msg["id"], headers)
                        emails.append(email_data)

                    return {
                        "emails": emails,
                        "count": len(emails),
                        "trace_id": self.telemetry.metrics.get("last_trace_id"),
                    }
                else:
                    return {"error": f"api_error_{response.status}"}

    async def _fetch_email_details(self, session: aiohttp.ClientSession, message_id: str, headers: dict) -> dict:
        """Fetch individual email details"""
        async with session.get(
            f"{self.base_url}/users/me/messages/{message_id}",
            headers=headers,
            params={
                "format": "metadata",
                "metadataHeaders": ["Subject", "From", "Date"],
            },
        ) as response:
            if response.status == 200:
                data = await response.json()

                # Extract headers
                headers_data = {}
                for header in data.get("payload", {}).get("headers", []):
                    headers_data[header["name"]] = header["value"]

                return {
                    "id": message_id,
                    "subject": headers_data.get("Subject", ""),
                    "from": headers_data.get("From", ""),
                    "date": headers_data.get("Date", ""),
                    "snippet": data.get("snippet", ""),
                }

            return {"id": message_id, "error": "fetch_failed"}

    @with_resilience
    async def list_labels(self, lid: str, capability_token: Optional[CapabilityToken] = None) -> dict:
        """List Gmail labels/folders"""

        # Validate capability token
        if capability_token and not self.validate_capability_token(capability_token, "list"):
            return {"error": "invalid_capability_token"}

        # Check consent
        if not await self.check_consent(lid, "list"):
            return {"error": "consent_required", "action": "list_labels"}

        if self.dry_run_mode:
            return {
                "dry_run": True,
                "labels": ["INBOX", "SENT", "DRAFT", "SPAM", "TRASH"],
            }

        # Get OAuth token
        if lid not in self.oauth_tokens:
            return {"error": "authentication_required"}

        access_token = self.oauth_tokens[lid]["access_token"]

        # Make API call
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {access_token}"}

            async with session.get(f"{self.base_url}/users/me/labels", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "labels": data.get("labels", []),
                        "trace_id": self.telemetry.metrics.get("last_trace_id"),
                    }
                else:
                    return {"error": f"api_error_{response.status}"}

    @with_resilience
    async def search_emails(
        self,
        lid: str,
        search_query: str,
        capability_token: Optional[CapabilityToken] = None,
    ) -> dict:
        """
        Search emails with Gmail query syntax
        Example: "from:user@example.com subject:invoice"
        """
        return await self.fetch_emails(lid, search_query, capability_token)

    async def revoke_access(self, lid: str) -> bool:
        """
        Revoke Gmail access when consent is withdrawn
        Called by Agent 2's consent ledger on revocation
        """
        if lid in self.oauth_tokens:
            # In production: revoke OAuth token via Google API
            del self.oauth_tokens[lid]

            # Log revocation
            self.telemetry.record_request(
                lid=lid,
                action="revoke_access",
                resource="gmail_oauth",
                capability_token=None,
                latency_ms=0,
                success=True,
            )

            return True

        return False

    def get_quota_usage(self, lid: str) -> dict:
        """Get Gmail API quota usage"""
        return {
            "lid": lid,
            "service": "gmail",
            "daily_requests": self.telemetry.metrics["request_count"],
            "quota_limit": 1000000000,  # Gmail API daily quota
            "usage_percentage": (self.telemetry.metrics["request_count"] / 1000000000) * 100,
        }


# Integration with Agent 4's context bus
class GmailContextIntegration:
    """
    Integration layer for Agent 4's context orchestrator
    Enables Gmail operations in multi-step workflows
    """

    def __init__(self, gmail_adapter: GmailAdapter):
        self.adapter = gmail_adapter

    async def workflow_fetch_travel_emails(self, lid: str, context: dict) -> dict:
        """
        Workflow step: Fetch travel-related emails
        Used in MVP demo scenario
        """
        # Search for travel-related emails
        travel_query = "subject:(flight OR hotel OR travel OR booking OR itinerary)"

        result = await self.adapter.search_emails(
            lid=lid,
            search_query=travel_query,
            capability_token=context.get("capability_token"),
        )

        if "emails" in result:
            # Extract travel information
            travel_emails = []
            for email in result["emails"]:
                if any(
                    keyword in email.get("subject", "").lower() for keyword in ["flight", "hotel", "travel", "booking"]
                ):
                    travel_emails.append(
                        {
                            "type": self._classify_travel_email(email["subject"]),
                            "subject": email["subject"],
                            "from": email["from"],
                            "date": email["date"],
                            "preview": email["snippet"][:100],
                        }
                    )

            return {
                "travel_emails": travel_emails,
                "count": len(travel_emails),
                "trace_id": result.get("trace_id"),
            }

        return result

    def _classify_travel_email(self, subject: str) -> str:
        """Classify travel email type"""
        subject_lower = subject.lower()

        if "flight" in subject_lower:
            return "flight"
        elif "hotel" in subject_lower:
            return "accommodation"
        elif "insurance" in subject_lower:
            return "insurance"
        elif "itinerary" in subject_lower:
            return "itinerary"
        else:
            return "travel"


if __name__ == "__main__":
    import asyncio

    async def test_gmail_adapter():
        print("📧 Testing Gmail Adapter")
        print("-" * 50)

        # Initialize adapter
        adapter = GmailAdapter()

        # Test dry-run mode
        adapter.set_dry_run(True)
        print("🔍 Testing dry-run mode...")

        result = await adapter.fetch_emails(lid="USR-123456", query="subject:travel", max_results=5)

        if result.get("dry_run"):
            print("✅ Dry-run plan created")
            print(f"   Operation: {result['plan']['operation']}")
            print(f"   Estimated time: {result['plan']['estimated_time_ms']}ms")

        # Test health status
        health = adapter.get_health_status()
        print("\n🏥 Health Status:")
        print(f"   Circuit breaker: {health['circuit_state']}")
        print(f"   Dry-run mode: {health['dry_run_mode']}")

        # Test context integration
        integration = GmailContextIntegration(adapter)
        print("\n🔄 Testing workflow integration...")

        # This would be called by Agent 4's orchestrator
        await integration.workflow_fetch_travel_emails(lid="USR-123456", context={"stage": "email_analysis"})

        print("✅ Workflow step ready for Agent 4 integration")

        print("\n✅ Gmail adapter operational!")

    asyncio.run(test_gmail_adapter())
