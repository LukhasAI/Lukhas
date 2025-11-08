#!/usr/bin/env python3
"""
WebAuthn Credential Storage System

Thread-safe in-memory credential storage implementing CRUD operations
for WebAuthn credentials with proper metadata tracking.

Constellation Framework: Identity ⚛️ pillar
Task: #589 - WebAuthn credential storage implementation
"""
from __future__ import annotations

import threading
from typing import Any, Dict, List, Optional

from typing_extensions import NotRequired, TypedDict


class WebAuthnCredential(TypedDict):
    """WebAuthn credential with metadata for storage.

    Stores essential credential information for WebAuthn/FIDO2 authentication
    including public key, signature counter, and usage metadata.
    """
    user_id: str  # ΛID or user identifier
    credential_id: str  # Base64url-encoded credential ID (unique key)
    public_key: str  # Base64url-encoded public key
    counter: int  # Signature counter (prevent replay attacks)
    created_at: str  # ISO 8601 timestamp
    last_used: NotRequired[str]  # ISO 8601 timestamp (optional)
    device_name: NotRequired[str]  # User-friendly device name (optional)
    aaguid: NotRequired[str]  # Authenticator AAGUID (optional)
    transports: NotRequired[List[str]]  # Transport types (usb, nfc, ble, internal, hybrid)
    backup_eligible: NotRequired[bool]  # Credential can be backed up
    backup_state: NotRequired[bool]  # Credential is currently backed up
    metadata: NotRequired[Dict[str, Any]]  # Additional metadata


class WebAuthnCredentialStore:
    """Thread-safe in-memory WebAuthn credential storage.

    Provides CRUD operations for WebAuthn credentials with proper concurrency
    control using threading.Lock. Supports multiple credentials per user.

    This is an in-memory implementation suitable for development and testing.
    Production deployments should use a persistent backend (database, Redis, etc.).
    """

    def __init__(self) -> None:
        """Initialize empty credential store with thread safety."""
        self._lock = threading.Lock()
        # Map: credential_id -> WebAuthnCredential
        self._credentials: Dict[str, WebAuthnCredential] = {}
        # Map: user_id -> list of credential_ids (for fast user lookup)
        self._user_index: Dict[str, List[str]] = {}

    def store_credential(self, user_id: str, credential: Dict[str, Any]) -> None:
        """Store a new WebAuthn credential.

        Args:
            user_id: User identifier (ΛID)
            credential: Credential data dictionary (will be validated and typed)

        Raises:
            ValueError: If credential_id already exists or required fields missing
            TypeError: If credential data has invalid types
        """
        # Validate required fields
        required_fields = ["credential_id", "public_key", "counter", "created_at"]
        for field in required_fields:
            if field not in credential:
                raise ValueError(f"Missing required field: {field}")

        credential_id = credential["credential_id"]

        if not isinstance(credential_id, str) or not credential_id:
            raise TypeError("credential_id must be a non-empty string")
        if not isinstance(credential["public_key"], str):
            raise TypeError("public_key must be a string")
        if not isinstance(credential["counter"], int):
            raise TypeError("counter must be an integer")
        if not isinstance(credential["created_at"], str):
            raise TypeError("created_at must be an ISO 8601 string")

        with self._lock:
            # Check for duplicate credential_id
            if credential_id in self._credentials:
                raise ValueError(f"Credential {credential_id} already exists")

            # Build typed credential
            typed_credential: WebAuthnCredential = {
                "user_id": user_id,
                "credential_id": credential_id,
                "public_key": credential["public_key"],
                "counter": credential["counter"],
                "created_at": credential["created_at"],
            }

            # Add optional fields if present
            if "last_used" in credential:
                typed_credential["last_used"] = credential["last_used"]
            if "device_name" in credential:
                typed_credential["device_name"] = credential["device_name"]
            if "aaguid" in credential:
                typed_credential["aaguid"] = credential["aaguid"]
            if "transports" in credential:
                typed_credential["transports"] = credential["transports"]
            if "backup_eligible" in credential:
                typed_credential["backup_eligible"] = credential["backup_eligible"]
            if "backup_state" in credential:
                typed_credential["backup_state"] = credential["backup_state"]
            if "metadata" in credential:
                typed_credential["metadata"] = credential["metadata"]

            # Store credential
            self._credentials[credential_id] = typed_credential

            # Update user index
            if user_id not in self._user_index:
                self._user_index[user_id] = []
            self._user_index[user_id].append(credential_id)

    def get_credential(self, credential_id: str) -> Optional[WebAuthnCredential]:
        """Retrieve a credential by credential_id.

        Args:
            credential_id: Unique credential identifier

        Returns:
            WebAuthnCredential if found, None otherwise
        """
        with self._lock:
            return self._credentials.get(credential_id)

    def list_credentials(self, user_id: str) -> List[WebAuthnCredential]:
        """List all credentials for a user.

        Args:
            user_id: User identifier (ΛID)

        Returns:
            List of WebAuthnCredential objects (empty list if user has none)
        """
        with self._lock:
            credential_ids = self._user_index.get(user_id, [])
            return [
                self._credentials[cid]
                for cid in credential_ids
                if cid in self._credentials  # Defensive check
            ]

    def get_credentials_by_user(self, user_id: str) -> List[WebAuthnCredential]:
        """Get all credentials for a user with O(1) lookup performance.

        This method provides efficient user-to-credentials mapping using
        the secondary index. Useful for authentication flows where the user
        needs to select from their registered authenticators.

        Args:
            user_id: User identifier (ΛID)

        Returns:
            List of WebAuthnCredential objects (empty list if user has none)

        Performance:
            O(1) index lookup + O(n) where n = number of user's credentials
        """
        # Delegate to list_credentials which already uses the index
        return self.list_credentials(user_id)

    def get_credential_by_user_and_id(
        self,
        user_id: str,
        credential_id: str
    ) -> Optional[WebAuthnCredential]:
        """Get a specific credential for a user with validation.

        This method provides O(1) lookup with user ownership validation,
        ensuring the credential belongs to the specified user. Prevents
        credential enumeration attacks by validating user ownership.

        Args:
            user_id: User identifier (ΛID)
            credential_id: Unique credential identifier

        Returns:
            WebAuthnCredential if found and belongs to user, None otherwise

        Performance:
            O(1) for both credential lookup and user validation
        """
        with self._lock:
            # O(1) lookup by credential_id
            credential = self._credentials.get(credential_id)

            # Validate credential exists and belongs to user
            if credential is None or credential["user_id"] != user_id:
                return None

            return credential

    def delete_credential(self, credential_id: str) -> bool:
        """Delete a credential by credential_id.

        Args:
            credential_id: Unique credential identifier

        Returns:
            True if credential was deleted, False if not found
        """
        with self._lock:
            credential = self._credentials.get(credential_id)
            if credential is None:
                return False

            # Remove from main store
            del self._credentials[credential_id]

            # Remove from user index
            user_id = credential["user_id"]
            if user_id in self._user_index:
                try:
                    self._user_index[user_id].remove(credential_id)
                    # Clean up empty user index entries
                    if not self._user_index[user_id]:
                        del self._user_index[user_id]
                except ValueError:
                    # Credential wasn't in index (shouldn't happen, but defensive)
                    pass

            return True

    def update_credential(
        self,
        credential_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update specific fields of an existing credential.

        Args:
            credential_id: Unique credential identifier
            updates: Dictionary of fields to update (partial update)

        Returns:
            True if credential was updated, False if not found

        Raises:
            ValueError: If trying to update credential_id or user_id
            TypeError: If update values have invalid types
        """
        # Prevent updating immutable fields
        if "credential_id" in updates:
            raise ValueError("Cannot update credential_id")
        if "user_id" in updates:
            raise ValueError("Cannot update user_id")

        with self._lock:
            credential = self._credentials.get(credential_id)
            if credential is None:
                return False

            # Validate types for known fields
            if "counter" in updates and not isinstance(updates["counter"], int):
                raise TypeError("counter must be an integer")
            if "last_used" in updates and not isinstance(updates["last_used"], str):
                raise TypeError("last_used must be an ISO 8601 string")
            if "device_name" in updates and not isinstance(updates["device_name"], str):
                raise TypeError("device_name must be a string")

            # Apply updates
            for key, value in updates.items():
                if key in {"counter", "last_used", "device_name", "aaguid",
                          "transports", "backup_eligible", "backup_state", "metadata"}:
                    credential[key] = value  # type: ignore[literal-required]

            return True

    def count_credentials(self, user_id: Optional[str] = None) -> int:
        """Count total credentials or credentials for a specific user.

        Args:
            user_id: Optional user identifier (if None, counts all credentials)

        Returns:
            Number of credentials
        """
        with self._lock:
            if user_id is None:
                return len(self._credentials)
            return len(self._user_index.get(user_id, []))


__all__ = [
    "WebAuthnCredential",
    "WebAuthnCredentialStore",
]
