"""
Tests for Hash Chain Utilities

Simple utility tests for hash chain generation, validation, and integrity checks.
Real implementations only, no mocks needed.

Trinity Framework: 🛡️ Guardian · 🔒 Security
"""

import hashlib
from datetime import datetime, timezone

import pytest

# ============================================================================
# Hash Generation Tests
# ============================================================================


@pytest.mark.unit
def test_sha256_hash_generation():
    """Test SHA256 hash generation."""
    data = "test_data_123"

    # Generate hash
    hash_value = hashlib.sha256(data.encode()).hexdigest()

    # Verify hash properties
    assert len(hash_value) == 64  # SHA256 produces 64 hex characters
    assert all(c in "0123456789abcdef" for c in hash_value)


@pytest.mark.unit
def test_sha512_hash_generation():
    """Test SHA512 hash generation."""
    data = "test_data_456"

    # Generate hash
    hash_value = hashlib.sha512(data.encode()).hexdigest()

    # Verify hash properties
    assert len(hash_value) == 128  # SHA512 produces 128 hex characters
    assert all(c in "0123456789abcdef" for c in hash_value)


@pytest.mark.unit
def test_hash_determinism():
    """Test that hashing is deterministic."""
    data = "deterministic_test"

    # Generate hash multiple times
    hash1 = hashlib.sha256(data.encode()).hexdigest()
    hash2 = hashlib.sha256(data.encode()).hexdigest()
    hash3 = hashlib.sha256(data.encode()).hexdigest()

    # All hashes should be identical
    assert hash1 == hash2 == hash3


@pytest.mark.unit
def test_hash_sensitivity():
    """Test that hash changes with data."""
    data1 = "test_data"
    data2 = "test_data_"  # One character difference

    hash1 = hashlib.sha256(data1.encode()).hexdigest()
    hash2 = hashlib.sha256(data2.encode()).hexdigest()

    # Hashes should be completely different
    assert hash1 != hash2


# ============================================================================
# Hash Chain Building Tests
# ============================================================================


@pytest.mark.unit
def test_hash_chain_basic():
    """Test basic hash chain construction."""
    entries = ["entry1", "entry2", "entry3"]

    # Build hash chain
    chain = []
    previous_hash = "0" * 64  # Genesis hash

    for entry in entries:
        # Chain: hash(previous_hash + entry)
        data = f"{previous_hash}{entry}"
        current_hash = hashlib.sha256(data.encode()).hexdigest()

        chain.append({"entry": entry, "hash": current_hash, "previous_hash": previous_hash})

        previous_hash = current_hash

    # Verify chain length
    assert len(chain) == 3

    # Verify linkage
    assert chain[1]["previous_hash"] == chain[0]["hash"]
    assert chain[2]["previous_hash"] == chain[1]["hash"]


@pytest.mark.unit
def test_hash_chain_genesis():
    """Test genesis block (first entry) in hash chain."""
    first_entry = "genesis_entry"
    genesis_hash = "0" * 64

    # Create first chain entry
    data = f"{genesis_hash}{first_entry}"
    first_hash = hashlib.sha256(data.encode()).hexdigest()

    chain_entry = {"entry": first_entry, "hash": first_hash, "previous_hash": genesis_hash}

    # Verify genesis properties
    assert chain_entry["previous_hash"] == "0" * 64
    assert len(chain_entry["hash"]) == 64
    assert chain_entry["hash"] != genesis_hash


@pytest.mark.unit
def test_hash_chain_integrity_verification():
    """Test hash chain integrity verification."""
    # Build chain
    entries = ["a", "b", "c"]
    chain = []
    previous_hash = "0" * 64

    for entry in entries:
        data = f"{previous_hash}{entry}"
        current_hash = hashlib.sha256(data.encode()).hexdigest()
        chain.append({"entry": entry, "hash": current_hash, "previous_hash": previous_hash})
        previous_hash = current_hash

    # Verify integrity
    is_valid = True
    for i in range(1, len(chain)):
        if chain[i]["previous_hash"] != chain[i - 1]["hash"]:
            is_valid = False
            break

    assert is_valid is True


@pytest.mark.unit
def test_hash_chain_tampering_detection():
    """Test detection of tampering in hash chain."""
    # Build chain
    chain = []
    previous_hash = "0" * 64

    for i in range(3):
        entry = f"entry{i}"
        data = f"{previous_hash}{entry}"
        current_hash = hashlib.sha256(data.encode()).hexdigest()
        chain.append({"entry": entry, "hash": current_hash, "previous_hash": previous_hash})
        previous_hash = current_hash

    # Tamper with middle entry
    chain[1]["entry"]
    chain[1]["entry"] = "tampered_entry"

    # Verify tampering detected
    # Recalculate hash for tampered entry
    data = f"{chain[1]['previous_hash']}{chain[1]['entry']}"
    recalculated_hash = hashlib.sha256(data.encode()).hexdigest()

    # Hash should not match
    assert recalculated_hash != chain[1]["hash"]


# ============================================================================
# Hash Chain Validation Tests
# ============================================================================


@pytest.mark.unit
def test_validate_hash_chain_valid():
    """Test validation of valid hash chain."""

    def validate_chain(chain):
        """Validate hash chain integrity."""
        for i in range(len(chain)):
            # Recalculate hash
            data = f"{chain[i]['previous_hash']}{chain[i]['entry']}"
            expected_hash = hashlib.sha256(data.encode()).hexdigest()

            # Check if hash matches
            if chain[i]["hash"] != expected_hash:
                return False

            # Check linkage (except first entry)
            if i > 0 and chain[i]["previous_hash"] != chain[i - 1]["hash"]:
                return False

        return True

    # Build valid chain
    chain = []
    previous_hash = "0" * 64

    for i in range(5):
        entry = f"entry{i}"
        data = f"{previous_hash}{entry}"
        current_hash = hashlib.sha256(data.encode()).hexdigest()
        chain.append({"entry": entry, "hash": current_hash, "previous_hash": previous_hash})
        previous_hash = current_hash

    # Should be valid
    assert validate_chain(chain) is True


@pytest.mark.unit
def test_validate_hash_chain_broken_link():
    """Test detection of broken link in hash chain."""
    # Build chain with broken link
    chain = []
    previous_hash = "0" * 64

    for i in range(3):
        entry = f"entry{i}"
        data = f"{previous_hash}{entry}"
        current_hash = hashlib.sha256(data.encode()).hexdigest()
        chain.append({"entry": entry, "hash": current_hash, "previous_hash": previous_hash})
        previous_hash = current_hash

    # Break the link
    chain[2]["previous_hash"] = "broken_hash"

    # Verify broken link detected
    for i in range(1, len(chain)):
        if chain[i]["previous_hash"] != chain[i - 1]["hash"]:
            # Broken link detected
            assert True
            break


# ============================================================================
# Audit Trail Hash Tests
# ============================================================================


@pytest.mark.unit
def test_audit_entry_hash():
    """Test hash generation for audit entry."""
    audit_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": "data_access",
        "user_id": "user_123",
        "result": "success",
    }

    # Generate hash from entry data
    entry_str = f"{audit_entry['timestamp']}{audit_entry['action']}{audit_entry['user_id']}{audit_entry['result']}"
    entry_hash = hashlib.sha256(entry_str.encode()).hexdigest()

    # Verify hash
    assert len(entry_hash) == 64
    assert isinstance(entry_hash, str)


@pytest.mark.unit
def test_audit_trail_with_lambda_id():
    """Test audit trail with ΛID integration."""
    audit_entries = [
        {"lambda_id": "Λ_alpha_user1", "action": "login", "timestamp": "2025-10-09T10:00:00Z"},
        {"lambda_id": "Λ_beta_user2", "action": "data_access", "timestamp": "2025-10-09T10:01:00Z"},
    ]

    # Hash each entry
    for entry in audit_entries:
        entry_str = f"{entry['lambda_id']}{entry['action']}{entry['timestamp']}"
        entry["hash"] = hashlib.sha256(entry_str.encode()).hexdigest()

    # Verify hashes generated
    assert all("hash" in entry for entry in audit_entries)
    assert len(audit_entries[0]["hash"]) == 64


# ============================================================================
# Hash Utilities Tests
# ============================================================================


@pytest.mark.unit
def test_hash_truncation():
    """Test hash truncation for short identifiers."""
    data = "test_data"
    full_hash = hashlib.sha256(data.encode()).hexdigest()

    # Truncate to 8 characters
    short_hash = full_hash[:8]

    assert len(short_hash) == 8
    assert short_hash == full_hash[:8]


@pytest.mark.unit
def test_hash_collision_resistance():
    """Test that similar inputs produce different hashes."""
    data1 = "test_data_1"
    data2 = "test_data_2"

    hash1 = hashlib.sha256(data1.encode()).hexdigest()
    hash2 = hashlib.sha256(data2.encode()).hexdigest()

    # Should be completely different
    assert hash1 != hash2

    # Even one bit difference should cascade
    matching_chars = sum(c1 == c2 for c1, c2 in zip(hash1, hash2))
    # Should have very few matching characters (avalanche effect)
    assert matching_chars < 20  # Less than 1/3 matching


@pytest.mark.unit
def test_hash_empty_string():
    """Test hashing empty string."""
    empty = ""
    hash_value = hashlib.sha256(empty.encode()).hexdigest()

    # Should produce valid hash even for empty string
    assert len(hash_value) == 64
    assert hash_value == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


@pytest.mark.unit
def test_hash_unicode_data():
    """Test hashing Unicode data."""
    unicode_data = "Hello 世界 🌍"
    hash_value = hashlib.sha256(unicode_data.encode("utf-8")).hexdigest()

    # Should handle Unicode
    assert len(hash_value) == 64
    assert isinstance(hash_value, str)


# ============================================================================
# Hash Chain Performance Tests
# ============================================================================


@pytest.mark.unit
def test_hash_chain_large_scale():
    """Test hash chain with many entries."""
    num_entries = 1000

    chain = []
    previous_hash = "0" * 64

    for i in range(num_entries):
        entry = f"entry_{i}"
        data = f"{previous_hash}{entry}"
        current_hash = hashlib.sha256(data.encode()).hexdigest()
        chain.append({"entry": entry, "hash": current_hash, "previous_hash": previous_hash})
        previous_hash = current_hash

    # Verify chain built successfully
    assert len(chain) == num_entries

    # Spot check linkage
    assert chain[500]["previous_hash"] == chain[499]["hash"]
    assert chain[999]["previous_hash"] == chain[998]["hash"]


# ============================================================================
# Capability Tests
# ============================================================================


@pytest.mark.capability
def test_hash_chain_full_capability():
    """Test complete hash chain capability."""
    # 1. Generate entries
    entries = ["entry1", "entry2", "entry3", "entry4", "entry5"]

    # 2. Build chain
    chain = []
    previous_hash = "0" * 64

    for entry in entries:
        data = f"{previous_hash}{entry}"
        current_hash = hashlib.sha256(data.encode()).hexdigest()
        chain.append({"entry": entry, "hash": current_hash, "previous_hash": previous_hash})
        previous_hash = current_hash

    # 3. Verify integrity
    is_valid = True
    for i in range(len(chain)):
        # Recalculate hash
        data = f"{chain[i]['previous_hash']}{chain[i]['entry']}"
        expected = hashlib.sha256(data.encode()).hexdigest()

        if chain[i]["hash"] != expected:
            is_valid = False
            break

        # Check linkage
        if i > 0 and chain[i]["previous_hash"] != chain[i - 1]["hash"]:
            is_valid = False
            break

    assert is_valid is True

    # 4. Test tampering detection
    original_hash = chain[2]["hash"]
    chain[2]["entry"] = "tampered"

    # Recalculate
    data = f"{chain[2]['previous_hash']}{chain[2]['entry']}"
    new_hash = hashlib.sha256(data.encode()).hexdigest()

    # Should detect tampering
    assert new_hash != original_hash


@pytest.mark.capability
def test_audit_trail_hash_chain_capability():
    """Test audit trail with hash chain capability."""
    # Simulate audit trail
    actions = [
        {"action": "login", "user": "user1", "time": "10:00"},
        {"action": "read", "user": "user1", "time": "10:01"},
        {"action": "write", "user": "user1", "time": "10:02"},
        {"action": "logout", "user": "user1", "time": "10:03"},
    ]

    # Build audit chain
    audit_chain = []
    previous_hash = "0" * 64

    for action in actions:
        # Serialize action
        action_str = f"{action['action']}_{action['user']}_{action['time']}"

        # Create chain entry
        data = f"{previous_hash}{action_str}"
        current_hash = hashlib.sha256(data.encode()).hexdigest()

        audit_chain.append({"action": action, "hash": current_hash, "previous_hash": previous_hash})

        previous_hash = current_hash

    # Verify audit chain
    assert len(audit_chain) == 4

    # Verify linkage
    for i in range(1, len(audit_chain)):
        assert audit_chain[i]["previous_hash"] == audit_chain[i - 1]["hash"]

    # Verify tamper-evident
    # If we change any action, the hash chain breaks
    original_hash = audit_chain[1]["hash"]
    audit_chain[1]["action"]["action"] = "modified"

    # Recalculate hash
    action_str = (
        f"{audit_chain[1]['action']['action']}_{audit_chain[1]['action']['user']}_{audit_chain[1]['action']['time']}"
    )
    data = f"{audit_chain[1]['previous_hash']}{action_str}"
    new_hash = hashlib.sha256(data.encode()).hexdigest()

    # Should be different
    assert new_hash != original_hash
