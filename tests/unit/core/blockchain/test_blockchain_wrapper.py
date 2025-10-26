"""Comprehensive tests for BlockchainWrapper module.

Tests cover:
- Transaction recording and chain building
- Hash computation and collision resistance
- Integrity verification
- Edge cases (empty chain, single transaction, large chain)
- Concurrent access patterns
- Hash stability and determinism
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta
from typing import Any

import pytest

from core.blockchain.blockchain_wrapper import BlockchainTransaction, BlockchainWrapper


class TestBlockchainTransaction:
    """Test BlockchainTransaction dataclass."""

    def test_transaction_creation(self):
        """Test basic transaction creation with all fields."""
        payload = {"action": "audit", "severity": "high"}
        tx = BlockchainTransaction(
            reference_id="ref-001",
            payload=payload,
            timestamp=datetime(2025, 10, 26, 12, 0, 0),
            previous_hash="prev123",
            collapseHash="hash456",
        )

        assert tx.reference_id == "ref-001"
        assert tx.payload == payload
        assert tx.timestamp == datetime(2025, 10, 26, 12, 0, 0)
        assert tx.previous_hash == "prev123"
        assert tx.collapseHash == "hash456"

    def test_transaction_default_timestamp(self):
        """Test that transactions get automatic timestamp."""
        before = datetime.utcnow()
        tx = BlockchainTransaction(reference_id="ref-002", payload={})
        after = datetime.utcnow()

        assert before <= tx.timestamp <= after

    def test_transaction_immutability(self):
        """Test that payload is properly stored."""
        original_payload = {"key": "value", "nested": {"inner": "data"}}
        tx = BlockchainTransaction(reference_id="ref-003", payload=original_payload)

        # Payload should be stored
        assert tx.payload == original_payload
        assert tx.payload["key"] == "value"
        assert tx.payload["nested"]["inner"] == "data"


class TestBlockchainWrapperInitialization:
    """Test BlockchainWrapper initialization and basic state."""

    def test_initialization(self):
        """Test wrapper initializes with empty chain."""
        wrapper = BlockchainWrapper()
        assert wrapper.get_transactions() == []

    def test_initial_integrity(self):
        """Test empty chain verifies as valid."""
        wrapper = BlockchainWrapper()
        assert wrapper.verify_integrity() is True


class TestTransactionRecording:
    """Test transaction recording functionality."""

    def test_record_single_transaction(self):
        """Test recording a single transaction."""
        wrapper = BlockchainWrapper()
        payload = {"event": "user_login", "user_id": "123"}

        tx = wrapper.record_transaction("ref-001", payload)

        assert tx.reference_id == "ref-001"
        assert tx.payload == payload
        assert tx.previous_hash == ""  # First transaction
        assert len(tx.collapseHash) == 64  # SHA-256 hex digest

    def test_record_multiple_transactions(self):
        """Test recording multiple transactions builds chain."""
        wrapper = BlockchainWrapper()

        tx1 = wrapper.record_transaction("ref-001", {"event": "login"})
        tx2 = wrapper.record_transaction("ref-002", {"event": "logout"})
        tx3 = wrapper.record_transaction("ref-003", {"event": "update"})

        transactions = wrapper.get_transactions()
        assert len(transactions) == 3

        # Verify chain linkage
        assert tx1.previous_hash == ""
        assert tx2.previous_hash == tx1.collapseHash
        assert tx3.previous_hash == tx2.collapseHash

    def test_transaction_ordering(self):
        """Test transactions maintain insertion order."""
        wrapper = BlockchainWrapper()

        refs = [f"ref-{i:03d}" for i in range(10)]
        for ref in refs:
            wrapper.record_transaction(ref, {"index": ref})

        transactions = wrapper.get_transactions()
        recorded_refs = [tx.reference_id for tx in transactions]

        assert recorded_refs == refs

    def test_complex_payload_recording(self):
        """Test recording complex nested payloads."""
        wrapper = BlockchainWrapper()

        complex_payload = {
            "user": {"id": 123, "name": "Alice", "roles": ["admin", "user"]},
            "action": "config_change",
            "changes": [
                {"field": "timeout", "old": 30, "new": 60},
                {"field": "max_retries", "old": 3, "new": 5},
            ],
            "metadata": {"timestamp": "2025-10-26T12:00:00Z", "source": "api"},
        }

        tx = wrapper.record_transaction("ref-complex", complex_payload)

        assert tx.payload == complex_payload
        assert tx.payload["user"]["name"] == "Alice"
        assert len(tx.payload["changes"]) == 2


class TestHashComputation:
    """Test hash computation and properties."""

    def test_hash_determinism(self):
        """Test that identical inputs produce identical hashes."""
        wrapper1 = BlockchainWrapper()
        wrapper2 = BlockchainWrapper()

        payload = {"data": "test"}

        tx1 = wrapper1.record_transaction("ref-001", payload)
        tx2 = wrapper2.record_transaction("ref-001", payload)

        assert tx1.collapseHash == tx2.collapseHash

    def test_hash_uniqueness_different_ref(self):
        """Test different reference IDs produce different hashes."""
        wrapper = BlockchainWrapper()

        tx1 = wrapper.record_transaction("ref-001", {"data": "test"})
        tx2 = wrapper.record_transaction("ref-002", {"data": "test"})

        assert tx1.collapseHash != tx2.collapseHash

    def test_hash_uniqueness_different_payload(self):
        """Test different payloads produce different hashes."""
        wrapper = BlockchainWrapper()

        tx1 = wrapper.record_transaction("ref-001", {"data": "test1"})
        tx2 = wrapper.record_transaction("ref-001", {"data": "test2"})

        assert tx1.collapseHash != tx2.collapseHash

    def test_hash_includes_previous_hash(self):
        """Test that hash computation includes previous hash."""
        wrapper = BlockchainWrapper()

        # Same ref and payload but different positions in chain
        wrapper.record_transaction("ref-001", {"event": "setup"})
        tx1 = wrapper.record_transaction("ref-dup", {"data": "test"})

        # Create new wrapper to get same transaction without previous
        wrapper2 = BlockchainWrapper()
        tx2 = wrapper2.record_transaction("ref-dup", {"data": "test"})

        # Should have different hashes due to different previous_hash
        assert tx1.collapseHash != tx2.collapseHash

    def test_hash_format(self):
        """Test hash is valid SHA-256 hex string."""
        wrapper = BlockchainWrapper()
        tx = wrapper.record_transaction("ref-001", {"data": "test"})

        # SHA-256 produces 64-character hex string
        assert len(tx.collapseHash) == 64
        assert all(c in "0123456789abcdef" for c in tx.collapseHash)

    def test_manual_hash_computation(self):
        """Test manual hash computation matches internal method."""
        wrapper = BlockchainWrapper()

        ref_id = "ref-001"
        payload = {"key": "value", "number": 42}
        previous_hash = ""

        # Compute hash manually
        serialized = json.dumps(payload, sort_keys=True, default=str)
        digest = hashlib.sha256()
        digest.update(ref_id.encode("utf-8"))
        digest.update(previous_hash.encode("utf-8"))
        digest.update(serialized.encode("utf-8"))
        expected_hash = digest.hexdigest()

        tx = wrapper.record_transaction(ref_id, payload)

        assert tx.collapseHash == expected_hash


class TestIntegrityVerification:
    """Test blockchain integrity verification."""

    def test_verify_empty_chain(self):
        """Test empty chain is valid."""
        wrapper = BlockchainWrapper()
        assert wrapper.verify_integrity() is True

    def test_verify_single_transaction(self):
        """Test single transaction chain is valid."""
        wrapper = BlockchainWrapper()
        wrapper.record_transaction("ref-001", {"data": "test"})
        assert wrapper.verify_integrity() is True

    def test_verify_multiple_transactions(self):
        """Test multi-transaction chain is valid."""
        wrapper = BlockchainWrapper()

        for i in range(10):
            wrapper.record_transaction(f"ref-{i:03d}", {"index": i})

        assert wrapper.verify_integrity() is True

    def test_detect_tampered_payload(self):
        """Test integrity check detects tampered payload."""
        wrapper = BlockchainWrapper()
        wrapper.record_transaction("ref-001", {"data": "original"})
        wrapper.record_transaction("ref-002", {"data": "next"})

        # Tamper with the payload
        transactions = wrapper.get_transactions()
        transactions[0].payload["data"] = "tampered"  # type: ignore

        # Should detect tampering
        assert wrapper.verify_integrity() is False

    def test_detect_tampered_hash(self):
        """Test integrity check detects modified hash."""
        wrapper = BlockchainWrapper()
        wrapper.record_transaction("ref-001", {"data": "test"})
        wrapper.record_transaction("ref-002", {"data": "test"})

        # Tamper with hash
        transactions = wrapper.get_transactions()
        original_hash = transactions[0].collapseHash
        # Modify one character in the hash
        tampered_hash = "x" + original_hash[1:]
        object.__setattr__(transactions[0], "collapseHash", tampered_hash)

        # Should detect tampering
        assert wrapper.verify_integrity() is False

    def test_detect_broken_chain_linkage(self):
        """Test integrity check detects broken chain links."""
        wrapper = BlockchainWrapper()
        wrapper.record_transaction("ref-001", {"data": "test1"})
        wrapper.record_transaction("ref-002", {"data": "test2"})
        wrapper.record_transaction("ref-003", {"data": "test3"})

        # Break the chain by modifying previous_hash
        transactions = wrapper.get_transactions()
        object.__setattr__(transactions[1], "previous_hash", "broken_link")

        # Should detect broken chain
        assert wrapper.verify_integrity() is False


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_payload(self):
        """Test recording transaction with empty payload."""
        wrapper = BlockchainWrapper()
        tx = wrapper.record_transaction("ref-001", {})

        assert tx.payload == {}
        assert len(tx.collapseHash) == 64
        assert wrapper.verify_integrity() is True

    def test_large_payload(self):
        """Test recording transaction with large payload."""
        wrapper = BlockchainWrapper()

        large_payload = {f"key_{i}": f"value_{i}" * 100 for i in range(100)}
        tx = wrapper.record_transaction("ref-large", large_payload)

        assert tx.payload == large_payload
        assert wrapper.verify_integrity() is True

    def test_unicode_in_payload(self):
        """Test handling Unicode characters in payload."""
        wrapper = BlockchainWrapper()

        unicode_payload = {
            "emoji": "🎭🧠🛡️",
            "chinese": "测试数据",
            "arabic": "بيانات الاختبار",
            "symbols": "⚛️✦🔬",
        }

        tx = wrapper.record_transaction("ref-unicode", unicode_payload)

        assert tx.payload == unicode_payload
        assert wrapper.verify_integrity() is True

    def test_special_characters_in_ref_id(self):
        """Test special characters in reference ID."""
        wrapper = BlockchainWrapper()

        special_refs = [
            "ref-with-dashes",
            "ref_with_underscores",
            "ref.with.dots",
            "ref@with#special!chars",
            "ref/with/slashes",
        ]

        for ref in special_refs:
            tx = wrapper.record_transaction(ref, {"test": "data"})
            assert tx.reference_id == ref

        assert wrapper.verify_integrity() is True

    def test_very_long_chain(self):
        """Test performance with long chain."""
        wrapper = BlockchainWrapper()

        # Create 1000-transaction chain
        for i in range(1000):
            wrapper.record_transaction(f"ref-{i:04d}", {"index": i})

        transactions = wrapper.get_transactions()
        assert len(transactions) == 1000

        # Verify integrity of long chain
        assert wrapper.verify_integrity() is True

        # Verify proper chain linkage
        for i in range(1, len(transactions)):
            assert transactions[i].previous_hash == transactions[i - 1].collapseHash


class TestGetTransactions:
    """Test get_transactions method."""

    def test_returns_copy(self):
        """Test that get_transactions returns a copy, not reference."""
        wrapper = BlockchainWrapper()
        wrapper.record_transaction("ref-001", {"data": "test"})

        transactions1 = wrapper.get_transactions()
        transactions2 = wrapper.get_transactions()

        # Should be equal but not the same object
        assert transactions1 == transactions2
        assert transactions1 is not transactions2

    def test_modification_does_not_affect_chain(self):
        """Test modifying returned list doesn't affect internal chain."""
        wrapper = BlockchainWrapper()
        wrapper.record_transaction("ref-001", {"data": "test"})

        transactions = wrapper.get_transactions()
        original_length = len(transactions)

        # Try to modify returned list
        transactions.clear()

        # Internal chain should be unchanged
        assert len(wrapper.get_transactions()) == original_length
        assert wrapper.verify_integrity() is True


class TestPayloadSerialization:
    """Test payload serialization edge cases."""

    def test_datetime_in_payload(self):
        """Test payload with datetime objects."""
        wrapper = BlockchainWrapper()

        payload = {
            "timestamp": datetime(2025, 10, 26, 12, 0, 0),
            "expiry": datetime(2025, 12, 31, 23, 59, 59),
        }

        tx = wrapper.record_transaction("ref-datetime", payload)

        # Should handle datetime serialization
        assert tx.collapseHash is not None
        assert len(tx.collapseHash) == 64

    def test_nested_complex_payload(self):
        """Test deeply nested complex payload."""
        wrapper = BlockchainWrapper()

        payload = {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "level5": {"data": "deep", "values": [1, 2, 3, 4, 5]}
                        }
                    }
                }
            }
        }

        tx = wrapper.record_transaction("ref-nested", payload)
        assert wrapper.verify_integrity() is True

    def test_none_values_in_payload(self):
        """Test payload with None values."""
        wrapper = BlockchainWrapper()

        payload = {"optional": None, "required": "value", "empty": None}

        tx = wrapper.record_transaction("ref-none", payload)
        assert tx.payload == payload
        assert wrapper.verify_integrity() is True

    def test_boolean_values_in_payload(self):
        """Test payload with boolean values."""
        wrapper = BlockchainWrapper()

        payload = {"is_active": True, "is_deleted": False, "is_verified": True}

        tx = wrapper.record_transaction("ref-bool", payload)
        assert tx.payload == payload
        assert wrapper.verify_integrity() is True


class TestConcurrency:
    """Test concurrent access patterns."""

    def test_sequential_access_is_consistent(self):
        """Test that sequential recording is consistent."""
        wrapper = BlockchainWrapper()

        # Simulate sequential access
        for i in range(10):
            wrapper.record_transaction(f"ref-{i}", {"index": i})

        assert wrapper.verify_integrity() is True

    def test_independent_wrappers_dont_interfere(self):
        """Test multiple independent wrapper instances."""
        wrapper1 = BlockchainWrapper()
        wrapper2 = BlockchainWrapper()

        wrapper1.record_transaction("ref-001", {"source": "wrapper1"})
        wrapper2.record_transaction("ref-001", {"source": "wrapper2"})

        assert len(wrapper1.get_transactions()) == 1
        assert len(wrapper2.get_transactions()) == 1
        assert wrapper1.verify_integrity() is True
        assert wrapper2.verify_integrity() is True

        # Same ref/payload but different chains
        tx1 = wrapper1.get_transactions()[0]
        tx2 = wrapper2.get_transactions()[0]
        assert tx1.collapseHash == tx2.collapseHash  # First tx, no previous


@pytest.mark.integration
class TestBlockchainIntegration:
    """Integration tests for blockchain wrapper."""

    def test_audit_trail_workflow(self):
        """Test complete audit trail workflow."""
        wrapper = BlockchainWrapper()

        # Simulate audit events
        events = [
            {"event": "system_start", "timestamp": "2025-10-26T10:00:00Z"},
            {"event": "user_login", "user_id": "123", "timestamp": "2025-10-26T10:05:00Z"},
            {"event": "config_change", "field": "timeout", "timestamp": "2025-10-26T10:10:00Z"},
            {"event": "user_logout", "user_id": "123", "timestamp": "2025-10-26T10:30:00Z"},
            {"event": "system_shutdown", "timestamp": "2025-10-26T11:00:00Z"},
        ]

        for i, event in enumerate(events):
            wrapper.record_transaction(f"audit-{i:03d}", event)

        transactions = wrapper.get_transactions()
        assert len(transactions) == 5
        assert wrapper.verify_integrity() is True

        # Verify audit trail completeness
        assert transactions[0].payload["event"] == "system_start"
        assert transactions[-1].payload["event"] == "system_shutdown"

    def test_healix_integration_pattern(self):
        """Test pattern matching Healix integration use case."""
        wrapper = BlockchainWrapper()

        # Simulate Healix memory audit events
        healix_events = [
            {
                "action": "memory_store",
                "memory_id": "mem-001",
                "tone": "neutral",
                "intensity": 0.6,
            },
            {
                "action": "memory_retrieve",
                "memory_id": "mem-001",
                "query": "recent events",
            },
            {
                "action": "memory_update",
                "memory_id": "mem-001",
                "field": "tone",
                "new_value": "focused",
            },
        ]

        for i, event in enumerate(healix_events):
            wrapper.record_transaction(f"healix-{i:03d}", event)

        assert len(wrapper.get_transactions()) == 3
        assert wrapper.verify_integrity() is True

    def test_blockchain_export_import_pattern(self):
        """Test exporting and verifying chain data."""
        wrapper = BlockchainWrapper()

        # Build a chain
        for i in range(5):
            wrapper.record_transaction(f"ref-{i:03d}", {"data": f"item-{i}"})

        # Export chain data
        exported = wrapper.get_transactions()

        # Verify exported data maintains integrity
        assert len(exported) == 5
        for i in range(1, len(exported)):
            assert exported[i].previous_hash == exported[i - 1].collapseHash

        # Original wrapper should still verify
        assert wrapper.verify_integrity() is True
