#!/usr/bin/env python3
"""
WebAuthn Credential Storage Tests

Comprehensive unit tests for WebAuthnCredentialStore with 100% coverage.
Tests include CRUD operations, thread safety, error handling, and edge cases.

Task: #589 - WebAuthn credential storage tests
"""
from __future__ import annotations

import threading
import time
from datetime import datetime, timezone
from typing import Any

import pytest

from lukhas.identity.webauthn_credential import (
    WebAuthnCredential,
    WebAuthnCredentialStore,
)


# Test fixtures

@pytest.fixture
def store() -> WebAuthnCredentialStore:
    """Create a fresh credential store for each test."""
    return WebAuthnCredentialStore()


@pytest.fixture
def sample_credential() -> dict[str, Any]:
    """Create a sample credential with required fields."""
    return {
        "credential_id": "test_cred_123",
        "public_key": "base64_encoded_public_key",
        "counter": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


@pytest.fixture
def full_credential() -> dict[str, Any]:
    """Create a credential with all optional fields."""
    return {
        "credential_id": "full_cred_456",
        "public_key": "base64_encoded_public_key",
        "counter": 5,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_used": datetime.now(timezone.utc).isoformat(),
        "device_name": "My Laptop TouchID",
        "aaguid": "00000000-0000-0000-0000-000000000000",
        "transports": ["internal", "hybrid"],
        "backup_eligible": True,
        "backup_state": False,
        "metadata": {"browser": "Chrome", "os": "macOS"},
    }


# Test: store_credential

def test_store_credential_success(
    store: WebAuthnCredentialStore,
    sample_credential: dict[str, Any]
) -> None:
    """Test successful credential storage."""
    store.store_credential("user_123", sample_credential)

    # Verify credential was stored
    retrieved = store.get_credential("test_cred_123")
    assert retrieved is not None
    assert retrieved["user_id"] == "user_123"
    assert retrieved["credential_id"] == "test_cred_123"
    assert retrieved["public_key"] == "base64_encoded_public_key"
    assert retrieved["counter"] == 0


def test_store_credential_with_optional_fields(
    store: WebAuthnCredentialStore,
    full_credential: dict[str, Any]
) -> None:
    """Test storing credential with all optional fields."""
    store.store_credential("user_456", full_credential)

    retrieved = store.get_credential("full_cred_456")
    assert retrieved is not None
    assert retrieved["device_name"] == "My Laptop TouchID"
    assert retrieved["aaguid"] == "00000000-0000-0000-0000-000000000000"
    assert retrieved["transports"] == ["internal", "hybrid"]
    assert retrieved["backup_eligible"] is True
    assert retrieved["backup_state"] is False
    assert retrieved["metadata"]["browser"] == "Chrome"


def test_store_credential_missing_required_field(
    store: WebAuthnCredentialStore
) -> None:
    """Test error when missing required field."""
    incomplete = {
        "credential_id": "test_cred",
        "public_key": "key",
        # Missing counter and created_at
    }

    with pytest.raises(ValueError, match="Missing required field"):
        store.store_credential("user_123", incomplete)


def test_store_credential_invalid_types(
    store: WebAuthnCredentialStore
) -> None:
    """Test error with invalid field types."""
    # Invalid credential_id type
    with pytest.raises(TypeError, match="credential_id must be a non-empty string"):
        store.store_credential("user_123", {
            "credential_id": 123,  # type: ignore[dict-item]
            "public_key": "key",
            "counter": 0,
            "created_at": "2024-01-01T00:00:00Z",
        })

    # Invalid public_key type
    with pytest.raises(TypeError, match="public_key must be a string"):
        store.store_credential("user_123", {
            "credential_id": "test_cred",
            "public_key": 12345,  # type: ignore[dict-item]
            "counter": 0,
            "created_at": "2024-01-01T00:00:00Z",
        })

    # Invalid counter type
    with pytest.raises(TypeError, match="counter must be an integer"):
        store.store_credential("user_123", {
            "credential_id": "test_cred",
            "public_key": "key",
            "counter": "0",  # type: ignore[dict-item]
            "created_at": "2024-01-01T00:00:00Z",
        })

    # Invalid created_at type
    with pytest.raises(TypeError, match="created_at must be an ISO 8601 string"):
        store.store_credential("user_123", {
            "credential_id": "test_cred",
            "public_key": "key",
            "counter": 0,
            "created_at": 1234567890,  # type: ignore[dict-item]
        })


def test_store_credential_empty_credential_id(
    store: WebAuthnCredentialStore
) -> None:
    """Test error with empty credential_id."""
    with pytest.raises(TypeError, match="credential_id must be a non-empty string"):
        store.store_credential("user_123", {
            "credential_id": "",
            "public_key": "key",
            "counter": 0,
            "created_at": "2024-01-01T00:00:00Z",
        })


def test_store_credential_duplicate(
    store: WebAuthnCredentialStore,
    sample_credential: dict[str, Any]
) -> None:
    """Test error when storing duplicate credential_id."""
    store.store_credential("user_123", sample_credential)

    # Try to store same credential_id again
    with pytest.raises(ValueError, match="already exists"):
        store.store_credential("user_456", sample_credential)


# Test: get_credential

def test_get_credential_success(
    store: WebAuthnCredentialStore,
    sample_credential: dict[str, Any]
) -> None:
    """Test successful credential retrieval."""
    store.store_credential("user_123", sample_credential)
    retrieved = store.get_credential("test_cred_123")

    assert retrieved is not None
    assert retrieved["credential_id"] == "test_cred_123"


def test_get_credential_not_found(store: WebAuthnCredentialStore) -> None:
    """Test retrieving non-existent credential returns None."""
    retrieved = store.get_credential("nonexistent_cred")
    assert retrieved is None


# Test: list_credentials

def test_list_credentials_single_user(
    store: WebAuthnCredentialStore,
    sample_credential: dict[str, Any]
) -> None:
    """Test listing credentials for a user with one credential."""
    store.store_credential("user_123", sample_credential)
    credentials = store.list_credentials("user_123")

    assert len(credentials) == 1
    assert credentials[0]["credential_id"] == "test_cred_123"


def test_list_credentials_multiple_per_user(
    store: WebAuthnCredentialStore
) -> None:
    """Test listing multiple credentials for the same user."""
    cred1 = {
        "credential_id": "cred_1",
        "public_key": "key1",
        "counter": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    cred2 = {
        "credential_id": "cred_2",
        "public_key": "key2",
        "counter": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    cred3 = {
        "credential_id": "cred_3",
        "public_key": "key3",
        "counter": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    store.store_credential("user_123", cred1)
    store.store_credential("user_123", cred2)
    store.store_credential("user_123", cred3)

    credentials = store.list_credentials("user_123")
    assert len(credentials) == 3

    cred_ids = {c["credential_id"] for c in credentials}
    assert cred_ids == {"cred_1", "cred_2", "cred_3"}


def test_list_credentials_empty(store: WebAuthnCredentialStore) -> None:
    """Test listing credentials for user with none."""
    credentials = store.list_credentials("user_no_creds")
    assert credentials == []


def test_list_credentials_isolation(store: WebAuthnCredentialStore) -> None:
    """Test that different users' credentials are isolated."""
    cred_user1 = {
        "credential_id": "user1_cred",
        "public_key": "key1",
        "counter": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    cred_user2 = {
        "credential_id": "user2_cred",
        "public_key": "key2",
        "counter": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    store.store_credential("user_1", cred_user1)
    store.store_credential("user_2", cred_user2)

    user1_creds = store.list_credentials("user_1")
    user2_creds = store.list_credentials("user_2")

    assert len(user1_creds) == 1
    assert len(user2_creds) == 1
    assert user1_creds[0]["credential_id"] == "user1_cred"
    assert user2_creds[0]["credential_id"] == "user2_cred"


# Test: delete_credential

def test_delete_credential_success(
    store: WebAuthnCredentialStore,
    sample_credential: dict[str, Any]
) -> None:
    """Test successful credential deletion."""
    store.store_credential("user_123", sample_credential)

    # Verify it exists
    assert store.get_credential("test_cred_123") is not None

    # Delete it
    result = store.delete_credential("test_cred_123")
    assert result is True

    # Verify it's gone
    assert store.get_credential("test_cred_123") is None


def test_delete_credential_not_found(store: WebAuthnCredentialStore) -> None:
    """Test deleting non-existent credential returns False."""
    result = store.delete_credential("nonexistent_cred")
    assert result is False


def test_delete_credential_removes_from_user_index(
    store: WebAuthnCredentialStore
) -> None:
    """Test that deletion also removes from user index."""
    cred1 = {
        "credential_id": "cred_1",
        "public_key": "key1",
        "counter": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    cred2 = {
        "credential_id": "cred_2",
        "public_key": "key2",
        "counter": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    store.store_credential("user_123", cred1)
    store.store_credential("user_123", cred2)

    # User should have 2 credentials
    assert len(store.list_credentials("user_123")) == 2

    # Delete one
    store.delete_credential("cred_1")

    # User should now have 1
    credentials = store.list_credentials("user_123")
    assert len(credentials) == 1
    assert credentials[0]["credential_id"] == "cred_2"


def test_delete_last_credential_cleans_user_index(
    store: WebAuthnCredentialStore,
    sample_credential: dict[str, Any]
) -> None:
    """Test that deleting last credential removes user from index."""
    store.store_credential("user_123", sample_credential)
    store.delete_credential("test_cred_123")

    # User should have no credentials
    assert store.list_credentials("user_123") == []
    assert store.count_credentials("user_123") == 0


# Test: update_credential

def test_update_credential_counter(
    store: WebAuthnCredentialStore,
    sample_credential: dict[str, Any]
) -> None:
    """Test updating credential counter."""
    store.store_credential("user_123", sample_credential)

    result = store.update_credential("test_cred_123", {"counter": 5})
    assert result is True

    updated = store.get_credential("test_cred_123")
    assert updated is not None
    assert updated["counter"] == 5


def test_update_credential_last_used(
    store: WebAuthnCredentialStore,
    sample_credential: dict[str, Any]
) -> None:
    """Test updating last_used timestamp."""
    store.store_credential("user_123", sample_credential)

    new_time = datetime.now(timezone.utc).isoformat()
    result = store.update_credential("test_cred_123", {"last_used": new_time})
    assert result is True

    updated = store.get_credential("test_cred_123")
    assert updated is not None
    assert updated["last_used"] == new_time


def test_update_credential_device_name(
    store: WebAuthnCredentialStore,
    sample_credential: dict[str, Any]
) -> None:
    """Test updating device name."""
    store.store_credential("user_123", sample_credential)

    result = store.update_credential("test_cred_123", {"device_name": "New Device"})
    assert result is True

    updated = store.get_credential("test_cred_123")
    assert updated is not None
    assert updated["device_name"] == "New Device"


def test_update_credential_not_found(store: WebAuthnCredentialStore) -> None:
    """Test updating non-existent credential returns False."""
    result = store.update_credential("nonexistent", {"counter": 10})
    assert result is False


def test_update_credential_immutable_fields(
    store: WebAuthnCredentialStore,
    sample_credential: dict[str, Any]
) -> None:
    """Test error when trying to update immutable fields."""
    store.store_credential("user_123", sample_credential)

    # Try to update credential_id
    with pytest.raises(ValueError, match="Cannot update credential_id"):
        store.update_credential("test_cred_123", {"credential_id": "new_id"})

    # Try to update user_id
    with pytest.raises(ValueError, match="Cannot update user_id"):
        store.update_credential("test_cred_123", {"user_id": "new_user"})


def test_update_credential_invalid_types(
    store: WebAuthnCredentialStore,
    sample_credential: dict[str, Any]
) -> None:
    """Test error when updating with invalid types."""
    store.store_credential("user_123", sample_credential)

    # Invalid counter type
    with pytest.raises(TypeError, match="counter must be an integer"):
        store.update_credential("test_cred_123", {"counter": "5"})

    # Invalid last_used type
    with pytest.raises(TypeError, match="last_used must be an ISO 8601 string"):
        store.update_credential("test_cred_123", {"last_used": 12345})

    # Invalid device_name type
    with pytest.raises(TypeError, match="device_name must be a string"):
        store.update_credential("test_cred_123", {"device_name": 123})


# Test: count_credentials

def test_count_credentials_empty(store: WebAuthnCredentialStore) -> None:
    """Test counting credentials in empty store."""
    assert store.count_credentials() == 0
    assert store.count_credentials("user_123") == 0


def test_count_credentials_total(store: WebAuthnCredentialStore) -> None:
    """Test counting total credentials across all users."""
    cred1 = {
        "credential_id": "cred_1",
        "public_key": "key1",
        "counter": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    cred2 = {
        "credential_id": "cred_2",
        "public_key": "key2",
        "counter": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    store.store_credential("user_1", cred1)
    store.store_credential("user_2", cred2)

    assert store.count_credentials() == 2


def test_count_credentials_per_user(store: WebAuthnCredentialStore) -> None:
    """Test counting credentials for specific user."""
    cred1 = {
        "credential_id": "cred_1",
        "public_key": "key1",
        "counter": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    cred2 = {
        "credential_id": "cred_2",
        "public_key": "key2",
        "counter": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    cred3 = {
        "credential_id": "cred_3",
        "public_key": "key3",
        "counter": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    store.store_credential("user_123", cred1)
    store.store_credential("user_123", cred2)
    store.store_credential("user_456", cred3)

    assert store.count_credentials("user_123") == 2
    assert store.count_credentials("user_456") == 1
    assert store.count_credentials("user_789") == 0
    assert store.count_credentials() == 3


# Test: Thread Safety

def test_concurrent_store_operations(store: WebAuthnCredentialStore) -> None:
    """Test thread safety with concurrent store operations."""
    def store_credential(user_id: str, index: int) -> None:
        cred = {
            "credential_id": f"cred_{user_id}_{index}",
            "public_key": f"key_{index}",
            "counter": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        store.store_credential(user_id, cred)

    # Create 10 threads storing credentials concurrently
    threads = []
    for i in range(10):
        thread = threading.Thread(target=store_credential, args=("user_123", i))
        threads.append(thread)
        thread.start()

    # Wait for all threads
    for thread in threads:
        thread.join()

    # Verify all credentials were stored
    assert store.count_credentials("user_123") == 10


def test_concurrent_read_operations(
    store: WebAuthnCredentialStore,
    sample_credential: dict[str, Any]
) -> None:
    """Test thread safety with concurrent read operations."""
    store.store_credential("user_123", sample_credential)

    results = []

    def read_credential() -> None:
        cred = store.get_credential("test_cred_123")
        results.append(cred)

    # Create 20 threads reading concurrently
    threads = []
    for _ in range(20):
        thread = threading.Thread(target=read_credential)
        threads.append(thread)
        thread.start()

    # Wait for all threads
    for thread in threads:
        thread.join()

    # All reads should succeed
    assert len(results) == 20
    assert all(r is not None for r in results)
    assert all(r["credential_id"] == "test_cred_123" for r in results)  # type: ignore[index]


def test_concurrent_mixed_operations(store: WebAuthnCredentialStore) -> None:
    """Test thread safety with mixed read/write/update/delete operations."""
    # Pre-populate with some credentials
    for i in range(5):
        cred = {
            "credential_id": f"init_cred_{i}",
            "public_key": f"key_{i}",
            "counter": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        store.store_credential("user_init", cred)

    def mixed_operations(index: int) -> None:
        # Store
        cred = {
            "credential_id": f"thread_cred_{index}",
            "public_key": f"key_{index}",
            "counter": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        store.store_credential(f"user_{index}", cred)

        # Read
        store.get_credential(f"thread_cred_{index}")

        # Update
        store.update_credential(f"thread_cred_{index}", {"counter": index})

        # List
        store.list_credentials(f"user_{index}")

        # Count
        store.count_credentials(f"user_{index}")

    # Run 10 threads doing mixed operations
    threads = []
    for i in range(10):
        thread = threading.Thread(target=mixed_operations, args=(i,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # Verify final state
    total_count = store.count_credentials()
    assert total_count >= 10  # At least the new credentials


def test_concurrent_delete_operations(store: WebAuthnCredentialStore) -> None:
    """Test thread safety when multiple threads try to delete the same credential."""
    sample = {
        "credential_id": "to_delete",
        "public_key": "key",
        "counter": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    store.store_credential("user_123", sample)

    delete_results = []

    def delete_credential() -> None:
        result = store.delete_credential("to_delete")
        delete_results.append(result)
        time.sleep(0.001)  # Small delay to increase contention

    # Create 10 threads trying to delete the same credential
    threads = []
    for _ in range(10):
        thread = threading.Thread(target=delete_credential)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # Only one thread should have successfully deleted (returned True)
    assert sum(delete_results) == 1
    # Credential should be gone
    assert store.get_credential("to_delete") is None


# Integration-style tests

def test_full_lifecycle(store: WebAuthnCredentialStore) -> None:
    """Test complete credential lifecycle: create, read, update, delete."""
    # Create
    cred = {
        "credential_id": "lifecycle_cred",
        "public_key": "initial_key",
        "counter": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    store.store_credential("user_lifecycle", cred)

    # Read
    retrieved = store.get_credential("lifecycle_cred")
    assert retrieved is not None
    assert retrieved["counter"] == 0

    # Update counter (simulating authentication)
    store.update_credential("lifecycle_cred", {
        "counter": 1,
        "last_used": datetime.now(timezone.utc).isoformat(),
    })

    # Read again
    updated = store.get_credential("lifecycle_cred")
    assert updated is not None
    assert updated["counter"] == 1
    assert "last_used" in updated

    # List user credentials
    user_creds = store.list_credentials("user_lifecycle")
    assert len(user_creds) == 1

    # Delete
    deleted = store.delete_credential("lifecycle_cred")
    assert deleted is True

    # Verify deletion
    assert store.get_credential("lifecycle_cred") is None
    assert store.list_credentials("user_lifecycle") == []


def test_realistic_webauthn_usage_pattern(store: WebAuthnCredentialStore) -> None:
    """Test realistic WebAuthn usage: register device, authenticate multiple times."""
    user_id = "alice@example.com"

    # Registration: Store new credential
    registration_cred = {
        "credential_id": "alice_yubikey_5c",
        "public_key": "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE...",  # Truncated
        "counter": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "device_name": "YubiKey 5C",
        "aaguid": "cb69481e-8ff7-4039-93ec-0a2729a154a8",
        "transports": ["usb", "nfc"],
        "backup_eligible": False,
        "backup_state": False,
    }
    store.store_credential(user_id, registration_cred)

    # Authenticate 1: Update counter
    store.update_credential("alice_yubikey_5c", {
        "counter": 1,
        "last_used": datetime.now(timezone.utc).isoformat(),
    })

    # Authenticate 2: Update counter again
    store.update_credential("alice_yubikey_5c", {
        "counter": 2,
        "last_used": datetime.now(timezone.utc).isoformat(),
    })

    # Authenticate 3
    store.update_credential("alice_yubikey_5c", {
        "counter": 3,
        "last_used": datetime.now(timezone.utc).isoformat(),
    })

    # Verify final state
    final_cred = store.get_credential("alice_yubikey_5c")
    assert final_cred is not None
    assert final_cred["counter"] == 3
    assert "last_used" in final_cred

    # Register second device
    second_device = {
        "credential_id": "alice_touchid_macbook",
        "public_key": "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE...",
        "counter": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "device_name": "MacBook Pro Touch ID",
        "transports": ["internal"],
        "backup_eligible": True,
        "backup_state": True,
    }
    store.store_credential(user_id, second_device)

    # User should now have 2 credentials
    user_creds = store.list_credentials(user_id)
    assert len(user_creds) == 2

    device_names = {c["device_name"] for c in user_creds}
    assert "YubiKey 5C" in device_names
    assert "MacBook Pro Touch ID" in device_names


def test_update_credential_with_all_optional_fields(
    store: WebAuthnCredentialStore,
    sample_credential: dict[str, Any]
) -> None:
    """Test updating all supported optional fields."""
    store.store_credential("user_123", sample_credential)

    # Update all supported fields at once
    updates = {
        "counter": 10,
        "last_used": datetime.now(timezone.utc).isoformat(),
        "device_name": "Updated Device",
        "aaguid": "updated-aaguid",
        "transports": ["usb", "nfc"],
        "backup_eligible": True,
        "backup_state": True,
        "metadata": {"updated": True},
    }
    result = store.update_credential("test_cred_123", updates)
    assert result is True

    updated = store.get_credential("test_cred_123")
    assert updated is not None
    assert updated["counter"] == 10
    assert updated["device_name"] == "Updated Device"
    assert updated["aaguid"] == "updated-aaguid"
    assert updated["transports"] == ["usb", "nfc"]
    assert updated["backup_eligible"] is True
    assert updated["backup_state"] is True
    assert updated["metadata"]["updated"] is True


def test_list_credentials_after_corrupted_index(
    store: WebAuthnCredentialStore,
    sample_credential: dict[str, Any]
) -> None:
    """Test that list_credentials handles corrupted index gracefully."""
    store.store_credential("user_123", sample_credential)

    # Simulate index corruption by manually adding invalid credential_id to user index
    store._user_index["user_123"].append("nonexistent_credential_id")

    # list_credentials should handle this gracefully (defensive check)
    credentials = store.list_credentials("user_123")

    # Should only return the valid credential
    assert len(credentials) == 1
    assert credentials[0]["credential_id"] == "test_cred_123"


# Test: get_credentials_by_user (issue #597)

def test_get_credentials_by_user_single_credential(
    store: WebAuthnCredentialStore,
    sample_credential: dict[str, Any]
) -> None:
    """Test get_credentials_by_user with single credential."""
    store.store_credential("user_123", sample_credential)
    credentials = store.get_credentials_by_user("user_123")

    assert len(credentials) == 1
    assert credentials[0]["credential_id"] == "test_cred_123"
    assert credentials[0]["user_id"] == "user_123"


def test_get_credentials_by_user_multiple_credentials(
    store: WebAuthnCredentialStore
) -> None:
    """Test get_credentials_by_user with multiple credentials."""
    cred1 = {
        "credential_id": "yubikey_5c",
        "public_key": "key1",
        "counter": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "device_name": "YubiKey 5C",
    }
    cred2 = {
        "credential_id": "touchid_macbook",
        "public_key": "key2",
        "counter": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "device_name": "MacBook Touch ID",
    }
    cred3 = {
        "credential_id": "windows_hello",
        "public_key": "key3",
        "counter": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "device_name": "Windows Hello",
    }

    store.store_credential("alice@example.com", cred1)
    store.store_credential("alice@example.com", cred2)
    store.store_credential("alice@example.com", cred3)

    credentials = store.get_credentials_by_user("alice@example.com")
    assert len(credentials) == 3

    device_names = {c["device_name"] for c in credentials}
    assert device_names == {"YubiKey 5C", "MacBook Touch ID", "Windows Hello"}


def test_get_credentials_by_user_nonexistent_user(
    store: WebAuthnCredentialStore
) -> None:
    """Test get_credentials_by_user for non-existent user returns empty list."""
    credentials = store.get_credentials_by_user("nonexistent_user")
    assert credentials == []


def test_get_credentials_by_user_user_isolation(
    store: WebAuthnCredentialStore
) -> None:
    """Test that get_credentials_by_user properly isolates users."""
    cred_alice = {
        "credential_id": "alice_key",
        "public_key": "alice_pubkey",
        "counter": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    cred_bob = {
        "credential_id": "bob_key",
        "public_key": "bob_pubkey",
        "counter": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    store.store_credential("alice@example.com", cred_alice)
    store.store_credential("bob@example.com", cred_bob)

    alice_creds = store.get_credentials_by_user("alice@example.com")
    bob_creds = store.get_credentials_by_user("bob@example.com")

    assert len(alice_creds) == 1
    assert len(bob_creds) == 1
    assert alice_creds[0]["credential_id"] == "alice_key"
    assert bob_creds[0]["credential_id"] == "bob_key"


def test_get_credentials_by_user_performance_o1(
    store: WebAuthnCredentialStore
) -> None:
    """Test that get_credentials_by_user has O(1) index lookup."""
    # Create 100 users with credentials
    for i in range(100):
        cred = {
            "credential_id": f"cred_user_{i}",
            "public_key": f"key_{i}",
            "counter": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        store.store_credential(f"user_{i}", cred)

    # Lookup should be O(1) regardless of total credentials
    import time
    start = time.perf_counter()
    credentials = store.get_credentials_by_user("user_50")
    elapsed = time.perf_counter() - start

    assert len(credentials) == 1
    # Should be extremely fast (< 1ms even on slow systems)
    assert elapsed < 0.001


# Test: get_credential_by_user_and_id (issue #597)

def test_get_credential_by_user_and_id_success(
    store: WebAuthnCredentialStore,
    sample_credential: dict[str, Any]
) -> None:
    """Test get_credential_by_user_and_id happy path."""
    store.store_credential("user_123", sample_credential)

    credential = store.get_credential_by_user_and_id("user_123", "test_cred_123")
    assert credential is not None
    assert credential["user_id"] == "user_123"
    assert credential["credential_id"] == "test_cred_123"
    assert credential["public_key"] == "base64_encoded_public_key"


def test_get_credential_by_user_and_id_wrong_user(
    store: WebAuthnCredentialStore,
    sample_credential: dict[str, Any]
) -> None:
    """Test get_credential_by_user_and_id with wrong user_id returns None."""
    store.store_credential("alice@example.com", sample_credential)

    # Try to access with different user_id (prevents credential enumeration)
    credential = store.get_credential_by_user_and_id("bob@example.com", "test_cred_123")
    assert credential is None


def test_get_credential_by_user_and_id_wrong_credential(
    store: WebAuthnCredentialStore,
    sample_credential: dict[str, Any]
) -> None:
    """Test get_credential_by_user_and_id with wrong credential_id returns None."""
    store.store_credential("user_123", sample_credential)

    credential = store.get_credential_by_user_and_id("user_123", "nonexistent_cred")
    assert credential is None


def test_get_credential_by_user_and_id_nonexistent_user(
    store: WebAuthnCredentialStore
) -> None:
    """Test get_credential_by_user_and_id with non-existent user."""
    credential = store.get_credential_by_user_and_id("nonexistent_user", "some_cred")
    assert credential is None


def test_get_credential_by_user_and_id_user_validation(
    store: WebAuthnCredentialStore
) -> None:
    """Test that get_credential_by_user_and_id validates user ownership."""
    # Alice's credential
    cred_alice = {
        "credential_id": "shared_cred_id",
        "public_key": "alice_key",
        "counter": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    store.store_credential("alice@example.com", cred_alice)

    # Bob tries to access Alice's credential (should fail)
    credential = store.get_credential_by_user_and_id("bob@example.com", "shared_cred_id")
    assert credential is None

    # Alice can access her own credential
    credential = store.get_credential_by_user_and_id("alice@example.com", "shared_cred_id")
    assert credential is not None
    assert credential["user_id"] == "alice@example.com"


def test_get_credential_by_user_and_id_performance_o1(
    store: WebAuthnCredentialStore
) -> None:
    """Test that get_credential_by_user_and_id has O(1) performance."""
    # Create 1000 credentials
    for i in range(1000):
        cred = {
            "credential_id": f"cred_{i}",
            "public_key": f"key_{i}",
            "counter": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        store.store_credential(f"user_{i}", cred)

    # Lookup should be O(1) regardless of total credentials
    import time
    start = time.perf_counter()
    credential = store.get_credential_by_user_and_id("user_500", "cred_500")
    elapsed = time.perf_counter() - start

    assert credential is not None
    # Should be extremely fast (< 1ms even on slow systems)
    assert elapsed < 0.001


# Test: Index consistency (issue #597)

def test_index_consistency_after_store(
    store: WebAuthnCredentialStore
) -> None:
    """Test that user index is consistent after store operations."""
    cred1 = {
        "credential_id": "cred_1",
        "public_key": "key1",
        "counter": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    cred2 = {
        "credential_id": "cred_2",
        "public_key": "key2",
        "counter": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    store.store_credential("user_123", cred1)
    store.store_credential("user_123", cred2)

    # Verify index consistency
    assert "user_123" in store._user_index
    assert set(store._user_index["user_123"]) == {"cred_1", "cred_2"}

    # Verify via get_credentials_by_user
    credentials = store.get_credentials_by_user("user_123")
    assert len(credentials) == 2


def test_index_consistency_after_delete(
    store: WebAuthnCredentialStore
) -> None:
    """Test that user index is consistent after delete operations."""
    cred1 = {
        "credential_id": "cred_1",
        "public_key": "key1",
        "counter": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    cred2 = {
        "credential_id": "cred_2",
        "public_key": "key2",
        "counter": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    store.store_credential("user_123", cred1)
    store.store_credential("user_123", cred2)

    # Delete one credential
    store.delete_credential("cred_1")

    # Verify index updated
    assert store._user_index["user_123"] == ["cred_2"]

    # Verify via get_credentials_by_user
    credentials = store.get_credentials_by_user("user_123")
    assert len(credentials) == 1
    assert credentials[0]["credential_id"] == "cred_2"


def test_index_consistency_delete_last_credential(
    store: WebAuthnCredentialStore
) -> None:
    """Test that user index is cleaned up when last credential is deleted."""
    cred = {
        "credential_id": "only_cred",
        "public_key": "key",
        "counter": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    store.store_credential("user_123", cred)
    assert "user_123" in store._user_index

    # Delete last credential
    store.delete_credential("only_cred")

    # User should be removed from index
    assert "user_123" not in store._user_index

    # Verify via get_credentials_by_user
    credentials = store.get_credentials_by_user("user_123")
    assert credentials == []


def test_concurrent_user_lookups(store: WebAuthnCredentialStore) -> None:
    """Test thread safety with concurrent get_credentials_by_user calls."""
    # Create credentials for a user
    for i in range(5):
        cred = {
            "credential_id": f"cred_{i}",
            "public_key": f"key_{i}",
            "counter": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        store.store_credential("user_123", cred)

    results = []

    def lookup_user_credentials() -> None:
        creds = store.get_credentials_by_user("user_123")
        results.append(len(creds))

    # Create 20 threads looking up concurrently
    threads = []
    for _ in range(20):
        thread = threading.Thread(target=lookup_user_credentials)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # All lookups should return 5 credentials
    assert len(results) == 20
    assert all(count == 5 for count in results)


def test_concurrent_user_and_id_lookups(store: WebAuthnCredentialStore) -> None:
    """Test thread safety with concurrent get_credential_by_user_and_id calls."""
    cred = {
        "credential_id": "test_cred",
        "public_key": "key",
        "counter": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    store.store_credential("user_123", cred)

    results = []

    def lookup_credential() -> None:
        result = store.get_credential_by_user_and_id("user_123", "test_cred")
        results.append(result is not None)

    # Create 20 threads looking up concurrently
    threads = []
    for _ in range(20):
        thread = threading.Thread(target=lookup_credential)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # All lookups should succeed
    assert len(results) == 20
    assert all(results)


# Integration test: Authentication selection flow

def test_authentication_selection_flow(store: WebAuthnCredentialStore) -> None:
    """Test realistic authentication flow: list user's devices for selection."""
    user_id = "alice@example.com"

    # User has registered multiple authenticators
    devices = [
        {
            "credential_id": "yubikey_5c",
            "public_key": "yubikey_pubkey",
            "counter": 15,
            "created_at": "2024-01-15T10:00:00Z",
            "last_used": "2024-02-01T14:30:00Z",
            "device_name": "YubiKey 5C",
            "transports": ["usb", "nfc"],
        },
        {
            "credential_id": "touchid_macbook",
            "public_key": "touchid_pubkey",
            "counter": 42,
            "created_at": "2024-01-20T09:00:00Z",
            "last_used": "2024-02-01T16:45:00Z",
            "device_name": "MacBook Pro Touch ID",
            "transports": ["internal"],
        },
        {
            "credential_id": "iphone_faceid",
            "public_key": "faceid_pubkey",
            "counter": 8,
            "created_at": "2024-01-25T11:00:00Z",
            "last_used": "2024-02-01T12:00:00Z",
            "device_name": "iPhone 15 Pro",
            "transports": ["hybrid", "internal"],
        },
    ]

    for device in devices:
        store.store_credential(user_id, device)

    # Step 1: Get all user's credentials for selection UI
    available_devices = store.get_credentials_by_user(user_id)
    assert len(available_devices) == 3

    # Step 2: User selects a device (e.g., YubiKey)
    selected_credential_id = "yubikey_5c"

    # Step 3: Retrieve and validate the specific credential
    credential = store.get_credential_by_user_and_id(user_id, selected_credential_id)
    assert credential is not None
    assert credential["device_name"] == "YubiKey 5C"
    assert credential["counter"] == 15

    # Step 4: After successful authentication, update counter and last_used
    store.update_credential(selected_credential_id, {
        "counter": 16,
        "last_used": datetime.now(timezone.utc).isoformat(),
    })

    # Verify update
    updated = store.get_credential_by_user_and_id(user_id, selected_credential_id)
    assert updated is not None
    assert updated["counter"] == 16
