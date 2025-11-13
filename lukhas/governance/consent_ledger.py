"""
LUKHAS Governance - Consent Ledger
====================================

This module provides a high-level, compliant consent ledger that is a key
component of the LUKHAS lane architecture. It is designed for auditable,
verifiable consent tracking and validation.

This implementation uses an in-memory store for consent records and is designed
to be easily adaptable to a persistent backend.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List


class ConsentRecord:
    """
    Represents a single, auditable consent record.

    This data class is based on the schema of the existing ConsentLedgerEntry,
    ensuring compatibility while remaining adaptable.

    Attributes:
        record_id (str): A unique identifier for the consent record.
        principal_id (str): The identifier of the user or entity giving consent.
        service_id (str): The identifier of the service receiving consent.
        scopes (List[str]): The scopes of consent being granted.
        audience (str): The intended audience or recipient of the consent.
        status (str): The current status of the consent (e.g., "active", "revoked").
        issued_at (datetime): The timestamp when the consent was granted.
        expires_at (Optional[datetime]): The timestamp when the consent expires.
        context (Dict[str, Any]): Additional context about the consent.
    """

    def __init__(
        self,
        *,
        principal_id: str,
        service_id: str,
        scopes: List[str],
        audience: str,
        status: str = "active",
        issued_at: datetime | None = None,
        expires_at: datetime | None = None,
        record_id: str | None = None,
        context: Dict[str, Any] | None = None,
    ):
        """
        Initializes a new ConsentRecord.

        Args:
            principal_id: The identifier of the user or entity giving consent.
            service_id: The identifier of the service receiving consent.
            scopes: The scopes of consent being granted.
            audience: The intended audience or recipient of the consent.
            status: The initial status of the consent.
            issued_at: The timestamp when the consent was granted.
            expires_at: The timestamp when the consent expires.
            record_id: A unique identifier for the consent record.
            context: Additional context about the consent.
        """
        self.record_id = record_id or str(uuid.uuid4())
        self.principal_id = principal_id
        self.service_id = service_id
        self.scopes = scopes
        self.audience = audience
        self.status = status
        self.issued_at = issued_at or datetime.now(timezone.utc)
        self.expires_at = expires_at
        self.context = context or {}

    def is_expired(self) -> bool:
        """
        Checks if the consent record has expired.

        Returns:
            True if the consent record has expired, False otherwise.
        """
        if not self.expires_at:
            return False
        return self.expires_at < datetime.now(timezone.utc)

    def revoke(self) -> None:
        """Marks the consent record as revoked."""
        self.status = "revoked"

    def to_dict(self) -> Dict[str, Any]:
        """
        Returns a dictionary representation of the consent record.

        Returns:
            A dictionary containing the consent record's attributes.
        """
        return {
            "record_id": self.record_id,
            "principal_id": self.principal_id,
            "service_id": self.service_id,
            "scopes": self.scopes,
            "audience": self.audience,
            "status": self.status,
            "issued_at": self.issued_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "context": self.context,
        }


class ConsentLedger:
    """
    A high-level, compliant consent ledger.

    This class provides an interface for granting, revoking, and verifying
    consent, with an in-memory store for consent records.
    """

    def __init__(self) -> None:
        """Initializes a new ConsentLedger."""
        self._records: Dict[str, ConsentRecord] = {}

    def grant(
        self,
        principal_id: str,
        service_id: str,
        scopes: List[str],
        audience: str,
        ttl_minutes: int = 60,
        context: Dict[str, Any] | None = None,
    ) -> ConsentRecord:
        """
        Grants consent and creates a new consent record.

        Args:
            principal_id: The identifier of the user or entity giving consent.
            service_id: The identifier of the service receiving consent.
            scopes: The scopes of consent being granted.
            audience: The intended audience or recipient of the consent.
            ttl_minutes: The time-to-live for the consent in minutes.
            context: Additional context about the consent.

        Returns:
            The newly created ConsentRecord.
        """
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes)
        record = ConsentRecord(
            principal_id=principal_id,
            service_id=service_id,
            scopes=scopes,
            audience=audience,
            expires_at=expires_at,
            context=context,
        )
        self._records[record.record_id] = record
        return record

    def revoke(self, record_id: str) -> bool:
        """
        Revokes consent for a given record ID.

        Args:
            record_id: The ID of the consent record to revoke.

        Returns:
            True if the record was successfully revoked, False otherwise.
        """
        if record_id in self._records:
            self._records[record_id].revoke()
            return True
        return False

    def verify(
        self,
        principal_id: str,
        service_id: str,
        scopes: List[str],
        audience: str,
    ) -> bool:
        """
        Verifies that active consent exists for a given principal, service, and scopes.

        Args:
            principal_id: The identifier of the user or entity giving consent.
            service_id: The identifier of the service receiving consent.
            scopes: The scopes of consent to verify.
            audience: The intended audience or recipient of the consent.

        Returns:
            True if active consent exists, False otherwise.
        """
        for record in self._records.values():
            if (
                record.principal_id == principal_id
                and record.service_id == service_id
                and record.audience == audience
                and record.status == "active"
                and not record.is_expired()
                and all(scope in record.scopes for scope in scopes)
            ):
                return True
        return False

    def get_records_for_principal(self, principal_id: str) -> List[ConsentRecord]:
        """
        Returns all consent records for a given principal.

        Args:
            principal_id: The identifier of the principal.

        Returns:
            A list of ConsentRecord objects for the given principal.
        """
        return [
            record
            for record in self._records.values()
            if record.principal_id == principal_id
        ]
