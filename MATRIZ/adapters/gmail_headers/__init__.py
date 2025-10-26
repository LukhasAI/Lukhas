"""
Gmail Headers Adapter
====================
Metadata-first Gmail adapter that provides email headers only by default.
Requires content escalation for full email body access.

System-wide guardrails applied:
1. Headers-only by default (from, to, subject, date, labels)
2. Content access requires capability token escalation
3. All operations verify capability token scopes
4. Complete audit trail for email access

ACK GUARDRAILS
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Optional

from consent.service import ConsentService

from matriz.adapters import (
    OperationResult,
    ResourceContent,
    ResourceMetadata,
    SearchQuery,
    ServiceAdapter,
)


class EmailHeaderMetadata(ResourceMetadata):
    """Extended metadata for email headers"""

    from_address: str
    to_addresses: list[str]
    cc_addresses: Optional[list[str]] = None
    bcc_addresses: Optional[list[str]] = None
    subject: str
    date_sent: datetime
    labels: ClassVar[list[str]] = []
    thread_id: str
    message_id: str
    snippet: Optional[str] = None  # First ~150 chars preview
    has_attachments: bool = False
    is_unread: bool = False
    importance: Optional[str] = None


class GmailHeadersAdapter(ServiceAdapter):
    """
    Gmail adapter that provides headers-only access by default.

    Metadata operations (long TTL capabilities):
    - list_resources: Email headers in inbox/folders
    - get_resource_metadata: Detailed headers for specific email
    - search_resources: Search by sender/subject/date

    Content operations (short TTL capabilities):
    - get_resource_content: Full email body and attachments
    """

    def __init__(self, consent_service: ConsentService = None):
        super().__init__("gmail", consent_service)
        self.gmail_service = None
        self.mock_mode = True  # For development without real Gmail API

    async def initialize(self, config: dict[str, Any]) -> None:
        """Initialize Gmail API client"""
        self.config = config
        self.mock_mode = config.get("mock_mode", True)

        if not self.mock_mode:
            # In production: initialize real Gmail API client
            # from googleapiclient.discovery import build
            # self.gmail_service = build('gmail', 'v1', credentials=creds)
            pass

        await self._log_operation("initialize", success=True)

    async def verify_capability_token(
        self, token: str, required_scopes: list[str], resource_id: Optional[str] = None
    ) -> dict[str, Any]:
        """Verify capability token with consent service"""
        if self.consent_service:
            return await self.consent_service.verify_capability_token(token, required_scopes, resource_id)
        else:
            # Mock verification for development
            if token.startswith("mock_"):
                return {
                    "lid": "gonzo",
                    "service": "gmail",
                    "scopes": required_scopes,
                    "valid": True,
                }
            else:
                raise ValueError("Invalid capability token")

    async def list_resources(
        self,
        capability_token: str,
        parent_id: Optional[str] = None,  # Label/folder ID
        _resource_type: Optional[str] = None,
        limit: int = 100,
    ) -> list[EmailHeaderMetadata]:
        """
        List email headers (metadata only).

        Requires: email.read.headers scope
        Returns: Email headers without body content
        """
        # Verify capability token
        required_scopes = ["email.read.headers"]
        await self.verify_capability_token(capability_token, required_scopes)

        try:
            if self.mock_mode:
                # Return mock email headers
                emails = self._generate_mock_email_headers(limit, parent_id)
            else:
                # Real Gmail API call
                emails = await self._fetch_gmail_headers(parent_id, limit)

            await self._log_operation(
                "list_resources",
                success=True,
                metadata={"count": len(emails), "parent_id": parent_id},
            )

            return emails

        except Exception as e:
            await self._log_operation("list_resources", success=False, error=str(e))
            raise

    async def get_resource_metadata(self, capability_token: str, resource_id: str) -> EmailHeaderMetadata:
        """
        Get detailed email headers for specific message.

        Requires: email.read.headers scope
        Returns: Complete headers without body
        """
        required_scopes = ["email.read.headers"]
        await self.verify_capability_token(capability_token, required_scopes, resource_id)

        try:
            if self.mock_mode:
                email_metadata = self._generate_mock_email_metadata(resource_id)
            else:
                email_metadata = await self._fetch_gmail_message_headers(resource_id)

            await self._log_operation("get_resource_metadata", resource_id=resource_id, success=True)

            return email_metadata

        except Exception as e:
            await self._log_operation("get_resource_metadata", resource_id=resource_id, success=False, error=str(e))
            raise

    async def get_resource_content(self, capability_token: str, resource_id: str) -> ResourceContent:
        """
        Get full email content including body and attachments.

        Requires: email.read.content scope (escalated capability)
        Returns: Complete email with body and attachments
        """
        required_scopes = ["email.read.content"]
        await self.verify_capability_token(capability_token, required_scopes, resource_id)

        try:
            if self.mock_mode:
                content = self._generate_mock_email_content(resource_id)
            else:
                content = await self._fetch_gmail_message_content(resource_id)

            await self._log_operation(
                "get_resource_content",
                resource_id=resource_id,
                success=True,
                metadata={"content_size": len(content.content)},
            )

            return content

        except Exception as e:
            await self._log_operation("get_resource_content", resource_id=resource_id, success=False, error=str(e))
            raise

    async def search_resources(self, capability_token: str, query: SearchQuery) -> list[EmailHeaderMetadata]:
        """
        Search emails by headers (sender, subject, date).

        Requires: email.search.headers scope
        Returns: Matching email headers only
        """
        required_scopes = ["email.search.headers", "email.read.headers"]
        await self.verify_capability_token(capability_token, required_scopes)

        try:
            if self.mock_mode:
                results = self._mock_search_emails(query)
            else:
                results = await self._search_gmail_messages(query)

            await self._log_operation(
                "search_resources",
                success=True,
                metadata={"query": query.query, "results": len(results)},
            )

            return results

        except Exception as e:
            await self._log_operation("search_resources", success=False, error=str(e))
            raise

    # Operations not supported for Gmail (read-only service for now)

    async def put_resource(
        self,
        capability_token: str,
        parent_id: Optional[str],
        name: str,
        content: bytes,
        content_type: str,
    ) -> OperationResult:
        """Gmail is read-only through this adapter"""
        raise NotImplementedError("Gmail adapter is read-only")

    async def move_resource(
        self,
        capability_token: str,
        resource_id: str,
        _new_parent_id: str,
        _new_name: Optional[str] = None,
    ) -> OperationResult:
        """Gmail messages can be labeled but not moved like files"""
        required_scopes = ["email.modify.labels"]
        await self.verify_capability_token(capability_token, required_scopes, resource_id)

        # This would add/remove labels in real implementation
        return OperationResult(
            success=True,
            resource_id=resource_id,
            message=f"Labels updated for message {resource_id}",
        )

    async def watch_resources(self, capability_token: str, watch_request) -> str:
        """Set up Gmail push notifications"""
        required_scopes = ["email.watch"]
        await self.verify_capability_token(capability_token, required_scopes)

        # In production: set up Gmail push notifications
        watch_id = f"gmail_watch_{datetime.now(timezone.utc).timestamp()}"

        await self._log_operation(
            "watch_resources",
            success=True,
            metadata={"watch_id": watch_id, "webhook": watch_request.webhook_url},
        )

        return watch_id

    async def unwatch_resources(self, capability_token: str, watch_id: str) -> OperationResult:
        """Remove Gmail watch"""
        required_scopes = ["email.watch"]
        await self.verify_capability_token(capability_token, required_scopes)

        return OperationResult(success=True, message=f"Watch {watch_id} removed")

    # Private helper methods

    def _generate_mock_email_headers(self, limit: int, folder: Optional[str]) -> list[EmailHeaderMetadata]:
        """Generate mock email headers for development"""
        mock_emails = []

        senders = [
            ("alice@example.com", "Alice Smith"),
            ("bob@company.com", "Bob Johnson"),
            ("noreply@service.com", "Service Notifications"),
            ("team@startup.io", "Startup Team"),
            ("newsletter@blog.com", "Tech Blog"),
        ]

        subjects = [
            "Weekly team sync notes",
            "Budget approval needed",
            "Your order has shipped",
            "Security alert: new login detected",
            "Proposal review requested",
        ]

        for i in range(min(limit, 20)):
            sender_email, sender_name = senders[i % len(senders)]
            subject = subjects[i % len(subjects)]

            mock_emails.append(
                EmailHeaderMetadata(
                    id=f"msg_{i + 1:03d}",
                    name=subject,
                    type="email",
                    created_at=datetime.now(timezone.utc),
                    modified_at=datetime.now(timezone.utc),
                    from_address=f"{sender_name} <{sender_email}>",
                    to_addresses=["gonzo@com"],
                    subject=subject,
                    date_sent=datetime.now(timezone.utc),
                    labels=["INBOX"] if not folder else [folder, "INBOX"],
                    thread_id=f"thread_{i + 1:03d}",
                    message_id=f"<{i + 1}@example.com>",
                    snippet=f"{subject[:50]}...",
                    has_attachments=i % 3 == 0,
                    is_unread=i % 4 == 0,
                    size=1024 + i * 512,
                )
            )

        return mock_emails

    def _generate_mock_email_metadata(self, message_id: str) -> EmailHeaderMetadata:
        """Generate detailed mock email metadata"""
        return EmailHeaderMetadata(
            id=message_id,
            name="Re: Project proposal review",
            type="email",
            created_at=datetime.now(timezone.utc),
            modified_at=datetime.now(timezone.utc),
            from_address="Alice Smith <alice@example.com>",
            to_addresses=["gonzo@com"],
            cc_addresses=["team@com"],
            subject="Re: Project proposal review",
            date_sent=datetime.now(timezone.utc),
            labels=["INBOX", "IMPORTANT"],
            thread_id=f"thread_{message_id}",
            message_id=f"<{message_id}@example.com>",
            snippet="Thanks for the detailed proposal. I have a few questions about the timeline...",
            has_attachments=True,
            is_unread=False,
            importance="high",
            size=2048,
        )

    def _generate_mock_email_content(self, message_id: str) -> ResourceContent:
        """Generate mock email content with body"""
        metadata = self._generate_mock_email_metadata(message_id)

        email_body = f"""From: {metadata.from_address}
To: {", ".join(metadata.to_addresses)}
Subject: {metadata.subject}
Date: {metadata.date_sent.isoformat()}

Hi Gonzo,

Thanks for the detailed proposal. I have a few questions about the timeline and resource allocation.

Can we schedule a call this week to discuss?

Best regards,
Alice Smith

---
This is a mock email generated for development purposes.
"""

        return ResourceContent(
            metadata=metadata,
            content=email_body.encode("utf-8"),
            encoding="utf-8",
            content_type="text/plain",
        )

    def _mock_search_emails(self, query: SearchQuery) -> list[EmailHeaderMetadata]:
        """Mock email search results"""
        all_emails = self._generate_mock_email_headers(100, None)

        # Simple filtering based on query
        if query.query:
            filtered = []
            search_term = query.query.lower()
            for email in all_emails:
                if (
                    search_term in email.subject.lower()
                    or search_term in email.from_address.lower()
                    or search_term in (email.snippet or "").lower()
                ):
                    filtered.append(email)
            return filtered[: query.limit]

        return all_emails[: query.limit]


# Factory function for easy initialization
async def create_gmail_adapter(
    consent_service: ConsentService = None, config: Optional[dict[str, Any]] = None
) -> GmailHeadersAdapter:
    """Create and initialize Gmail headers adapter"""
    adapter = GmailHeadersAdapter(consent_service)
    await adapter.initialize(config or {"mock_mode": True})
    return adapter
