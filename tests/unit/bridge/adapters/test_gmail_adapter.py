# owner: Jules-06
# tier: tier3
# module_uid: candidate.bridge.adapters
# criticality: P1

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bridge.adapters.gmail_adapter import GmailAdapter, GmailContextIntegration
from bridge.adapters.service_adapter_base import CapabilityToken


@pytest.mark.tier3
@pytest.mark.adapters
@pytest.mark.unit
class TestGmailAdapterUnit:
    """
    Unit tests for the Gmail Service Adapter.
    """

    @pytest.fixture
    def adapter(self):
        """Returns a GmailAdapter instance."""
        adapter = GmailAdapter()
        adapter.check_consent = AsyncMock(return_value=True)
        adapter.oauth_tokens["user123"] = {"access_token": "fake_token"}
        return adapter

    @pytest.mark.asyncio
    async def test_authenticate_dry_run(self, adapter: GmailAdapter):
        """Tests authentication in dry-run mode."""
        adapter.set_dry_run(True)
        creds = await adapter.authenticate({})
        assert creds["access_token"] == "dry_run_token"

    @pytest.mark.asyncio
    async def test_fetch_emails_consent_required(self, adapter: GmailAdapter):
        """Tests that fetching emails requires consent."""
        adapter.check_consent = AsyncMock(return_value=False)
        result = await adapter.fetch_emails(lid="user123")
        assert result["error"] == "consent_required"

    @pytest.mark.asyncio
    async def test_revoke_access(self, adapter: GmailAdapter):
        """Tests revoking access."""
        assert "user123" in adapter.oauth_tokens
        revoked = await adapter.revoke_access(lid="user123")
        assert revoked is True
        assert "user123" not in adapter.oauth_tokens

    def test_get_quota_usage(self, adapter: GmailAdapter):
        """Tests getting quota usage."""
        adapter.telemetry.metrics["request_count"] = 100
        quota = adapter.get_quota_usage(lid="user123")
        assert quota["lid"] == "user123"
        assert quota["daily_requests"] == 100

    @patch.object(GmailAdapter, "search_emails", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_context_integration_workflow(self, mock_search_emails, adapter: GmailAdapter):
        """Tests the GmailContextIntegration workflow."""
        mock_search_emails.return_value = {
            "emails": [
                {
                    "subject": "Your flight details",
                    "from": "airline@example.com",
                    "date": "2025-01-01",
                    "snippet": "Your flight itinerary is attached.",
                }
            ]
        }
        integration = GmailContextIntegration(adapter)
        result = await integration.workflow_fetch_travel_emails(lid="user123", context={})

        assert "travel_emails" in result
        assert len(result["travel_emails"]) == 1
        assert result["travel_emails"][0]["type"] == "flight"

    @pytest.mark.asyncio
    async def test_fetch_emails_auth_error(self, adapter: GmailAdapter):
        """Tests authentication error when fetching emails."""
        # Remove the user from the token store
        del adapter.oauth_tokens["user123"]
        result = await adapter.fetch_emails(lid="user123")
        assert result["error"] == "authentication_required"

    @pytest.mark.parametrize(
        "subject, expected_type",
        [
            ("Your flight to Japan", "flight"),
            ("Hotel confirmation", "accommodation"),
            ("Travel insurance details", "insurance"),
            ("Your trip itinerary", "itinerary"),
            ("A random email", "travel"),
        ],
    )
    def test_classify_travel_email(self, subject, expected_type, adapter: GmailAdapter):
        """Tests the _classify_travel_email method."""
        integration = GmailContextIntegration(adapter)
        assert integration._classify_travel_email(subject) == expected_type

    @pytest.mark.asyncio
    async def test_search_emails_invalid_token(self, adapter: GmailAdapter):
        """Tests searching emails with an invalid capability token."""
        adapter.validate_capability_token = MagicMock(return_value=False)
        invalid_token = CapabilityToken(
            token_id="invalid-token",
            lid="user123",
            scope=["read"],
            resource_ids=[],
            ttl=3600,
            audience="gmail",
            issued_at="2025-01-01T00:00:00Z",
            signature="invalid-sig",
        )
        result = await adapter.search_emails(lid="user123", search_query="test", capability_token=invalid_token)
        assert result["error"] == "invalid_capability_token"

    @pytest.mark.asyncio
    async def test_list_labels_invalid_token(self, adapter: GmailAdapter):
        """Tests listing labels with an invalid capability token."""
        adapter.validate_capability_token = MagicMock(return_value=False)
        invalid_token = CapabilityToken(
            token_id="invalid-token",
            lid="user123",
            scope=["list"],
            resource_ids=[],
            ttl=3600,
            audience="gmail",
            issued_at="2025-01-01T00:00:00Z",
            signature="invalid-sig",
        )
        result = await adapter.list_labels(lid="user123", capability_token=invalid_token)
        assert result["error"] == "invalid_capability_token"

    @pytest.mark.asyncio
    async def test_invalid_capability_token(self, adapter: GmailAdapter):
        """Tests that an invalid capability token is rejected."""
        adapter.validate_capability_token = MagicMock(return_value=False)
        invalid_token = CapabilityToken(
            token_id="invalid-token",
            lid="user123",
            scope=["read"],
            resource_ids=[],
            ttl=3600,
            audience="gmail",
            issued_at="2025-01-01T00:00:00Z",
            signature="invalid-sig",
        )
        result = await adapter.fetch_emails(lid="user123", capability_token=invalid_token)
        assert result["error"] == "invalid_capability_token"

    @pytest.mark.asyncio
    async def test_authenticate_no_refresh_token(self, adapter: GmailAdapter):
        """Tests the authentication flow when no refresh token is provided."""
        credentials = {"client_id": "test_client", "client_secret": "test_secret", "lid": "user123"}
        token_data = await adapter.authenticate(credentials)
        assert token_data["error"] == "authentication_required"
