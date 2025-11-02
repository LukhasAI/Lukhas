import unittest

from qi.engines.identity.consolidate_identity_qi_secure import consolidate_identities


class TestConsolidateIdentities(unittest.TestCase):

    def setUp(self):
        self.primary_identity = {
            "id": "primary-123",
            "name": "John Doe",
            "email": "john.doe@example.com",
            "timestamp": "2023-01-01T12:00:00Z",
        }
        self.secondary_identities = [
            {
                "id": "secondary-456",
                "email": "johndoe@work.com",
                "phone": "123-456-7890",
                "timestamp": "2023-01-02T12:00:00Z",
            },
            {"id": "secondary-789", "address": "123 Main St", "timestamp": "2023-01-01T18:00:00Z"},
        ]

    def test_standard_merge(self):
        merged, report = consolidate_identities(self.primary_identity, self.secondary_identities)
        self.assertEqual(merged["name"], "John Doe")
        self.assertEqual(merged["email"], "john.doe@example.com")
        self.assertEqual(merged["phone"], "123-456-7890")
        self.assertEqual(merged["address"], "123 Main St")

    def test_idempotency(self):
        merged1, report1 = consolidate_identities(self.primary_identity, self.secondary_identities)
        merged2, report2 = consolidate_identities(self.primary_identity, self.secondary_identities)
        # Reports will have different timestamps, so we only compare the merged identity
        self.assertEqual(merged1, merged2)

    def test_report_accuracy(self):
        merged, report = consolidate_identities(self.primary_identity, self.secondary_identities)
        self.assertEqual(len(report["conflicts"]), 1)
        self.assertEqual(report["conflicts"][0]["field"], "email")
        self.assertEqual(len(report["decisions"]), 2)
        self.assertEqual(report["primary_source"], "primary-123")
        self.assertIn("secondary-456", report["secondary_sources"])
        self.assertIn("secondary-789", report["secondary_sources"])

    def test_edge_case_no_timestamp(self):
        secondary_identities = self.secondary_identities + [
            {
                "id": "secondary-abc",
                "department": "Engineering",
                # No timestamp
            }
        ]
        # This should still run without error, but the order is not guaranteed for the new entry
        merged, report = consolidate_identities(self.primary_identity, secondary_identities)
        self.assertIn("department", merged)
        self.assertEqual(merged["department"], "Engineering")


if __name__ == "__main__":
    unittest.main()
