"""
Unit tests for the ConsentLedger module.
"""

import sys
import unittest
from datetime import datetime, timedelta, timezone

# Add the project root to the path to allow for `lukhas.*` imports
sys.path.insert(0, ".")

from lukhas.governance.consent_ledger import ConsentLedger, ConsentRecord


class TestConsentRecord(unittest.TestCase):
    """Test cases for the ConsentRecord class."""

    def test_record_creation(self):
        """Test that a ConsentRecord is created with the correct attributes."""
        record = ConsentRecord(
            principal_id="user1",
            service_id="service1",
            scopes=["read", "write"],
            audience="audience1",
        )
        self.assertIsNotNone(record.record_id)
        self.assertEqual(record.principal_id, "user1")
        self.assertEqual(record.service_id, "service1")
        self.assertEqual(record.scopes, ["read", "write"])
        self.assertEqual(record.audience, "audience1")
        self.assertEqual(record.status, "active")
        self.assertIsNotNone(record.issued_at)
        self.assertIsNone(record.expires_at)

    def test_is_expired(self):
        """Test that is_expired returns the correct value."""
        record = ConsentRecord(
            principal_id="user1",
            service_id="service1",
            scopes=["read"],
            audience="audience1",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=1),
        )
        self.assertFalse(record.is_expired())

        record.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
        self.assertTrue(record.is_expired())

    def test_revoke(self):
        """Test that revoke marks the record as revoked."""
        record = ConsentRecord(
            principal_id="user1",
            service_id="service1",
            scopes=["read"],
            audience="audience1",
        )
        self.assertEqual(record.status, "active")
        record.revoke()
        self.assertEqual(record.status, "revoked")


class TestConsentLedger(unittest.TestCase):
    """Test cases for the ConsentLedger class."""

    def setUp(self):
        """Set up a new ConsentLedger for each test."""
        self.ledger = ConsentLedger()

    def test_grant(self):
        """Test that grant creates a new consent record."""
        record = self.ledger.grant(
            principal_id="user1",
            service_id="service1",
            scopes=["read", "write"],
            audience="audience1",
        )
        self.assertIn(record.record_id, self.ledger._records)
        self.assertEqual(record.principal_id, "user1")

    def test_revoke(self):
        """Test that revoke marks a consent record as revoked."""
        record = self.ledger.grant(
            principal_id="user1",
            service_id="service1",
            scopes=["read"],
            audience="audience1",
        )
        self.assertTrue(self.ledger.revoke(record.record_id))
        self.assertEqual(self.ledger._records[record.record_id].status, "revoked")

    def test_revoke_nonexistent_record(self):
        """Test that revoke returns False for a nonexistent record."""
        self.assertFalse(self.ledger.revoke("nonexistent"))

    def test_verify(self):
        """Test that verify returns True for active, unexpired consent."""
        self.ledger.grant(
            principal_id="user1",
            service_id="service1",
            scopes=["read", "write"],
            audience="audience1",
        )
        self.assertTrue(
            self.ledger.verify(
                principal_id="user1",
                service_id="service1",
                scopes=["read"],
                audience="audience1",
            )
        )

    def test_verify_revoked_consent(self):
        """Test that verify returns False for revoked consent."""
        record = self.ledger.grant(
            principal_id="user1",
            service_id="service1",
            scopes=["read"],
            audience="audience1",
        )
        self.ledger.revoke(record.record_id)
        self.assertFalse(
            self.ledger.verify(
                principal_id="user1",
                service_id="service1",
                scopes=["read"],
                audience="audience1",
            )
        )

    def test_verify_expired_consent(self):
        """Test that verify returns False for expired consent."""
        self.ledger.grant(
            principal_id="user1",
            service_id="service1",
            scopes=["read"],
            audience="audience1",
            ttl_minutes=-1,
        )
        self.assertFalse(
            self.ledger.verify(
                principal_id="user1",
                service_id="service1",
                scopes=["read"],
                audience="audience1",
            )
        )

    def test_verify_insufficient_scopes(self):
        """Test that verify returns False for insufficient scopes."""
        self.ledger.grant(
            principal_id="user1",
            service_id="service1",
            scopes=["read"],
            audience="audience1",
        )
        self.assertFalse(
            self.ledger.verify(
                principal_id="user1",
                service_id="service1",
                scopes=["read", "write"],
                audience="audience1",
            )
        )

    def test_get_records_for_principal(self):
        """Test that get_records_for_principal returns the correct records."""
        self.ledger.grant(
            principal_id="user1",
            service_id="service1",
            scopes=["read"],
            audience="audience1",
        )
        self.ledger.grant(
            principal_id="user1",
            service_id="service2",
            scopes=["read"],
            audience="audience1",
        )
        self.ledger.grant(
            principal_id="user2",
            service_id="service1",
            scopes=["read"],
            audience="audience1",
        )

        records = self.ledger.get_records_for_principal("user1")
        self.assertEqual(len(records), 2)
        self.assertTrue(all(r.principal_id == "user1" for r in records))


if __name__ == "__main__":
    unittest.main()
