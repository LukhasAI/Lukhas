#!/usr/bin/env python3
"""
Tests for the Guardian System Example
"""

import unittest
from datetime import datetime, timedelta

from examples.governance.consent_example import (
    GuardianPolicy,
    collect_user_consent,
    verify_consent,
    access_health_records,
    get_audit_trail,
    ConsentDeniedException,
    _consent_db,
    _audit_log,
)


class TestGuardianExample(unittest.TestCase):

    def setUp(self):
        _consent_db.clear()
        _audit_log.clear()

    def test_policy_creation(self):
        policy = GuardianPolicy(
            purpose="research",
            data_types=["health_records"],
            retention_days=365,
            jurisdictions=["US", "EU"],
        )
        self.assertEqual(policy.purpose, "research")
        self.assertEqual(policy.data_types, ["health_records"])

    def test_consent_collection(self):
        policy = GuardianPolicy("research", ["health_records"], 365, ["US", "EU"])
        user_id = "test-user"
        collect_user_consent(user_id, policy)

        self.assertIn(user_id, _consent_db)
        self.assertTrue(_consent_db[user_id]["granted"])
        self.assertEqual(len(_audit_log), 1)
        self.assertEqual(_audit_log[0]["event"], "consent_collected")

    def test_consent_verification(self):
        policy = GuardianPolicy("research", ["health_records"], 365, ["US", "EU"])
        user_id = "test-user"
        collect_user_consent(user_id, policy)

        self.assertTrue(verify_consent(user_id, "health_records"))
        self.assertFalse(verify_consent(user_id, "other_data"))
        self.assertEqual(len(_audit_log), 2)  # consent_collected, consent_verified

    def test_consent_expiration(self):
        policy = GuardianPolicy("research", ["health_records"], 1, ["US", "EU"])
        user_id = "test-user"
        consent = collect_user_consent(user_id, policy)
        consent["timestamp"] = datetime.utcnow() - timedelta(days=2)

        self.assertFalse(verify_consent(user_id, "health_records"))

    def test_access_with_consent(self):
        policy = GuardianPolicy("research", ["health_records"], 365, ["US", "EU"])
        user_id = "test-user"
        collect_user_consent(user_id, policy)

        data = access_health_records(user_id)
        self.assertIn("data", data)
        self.assertEqual(len(_audit_log), 3)  # collected, verified, accessed

    def test_access_without_consent(self):
        user_id = "test-user"
        with self.assertRaises(ConsentDeniedException):
            access_health_records(user_id)

    def test_audit_trail(self):
        policy = GuardianPolicy("research", ["health_records"], 365, ["US", "EU"])
        user_id = "test-user"
        collect_user_consent(user_id, policy)
        access_health_records(user_id)

        audit_trail = get_audit_trail(user_id)
        self.assertEqual(len(audit_trail), 3)
        self.assertEqual(audit_trail[0]["event"], "consent_collected")
        self.assertEqual(audit_trail[1]["event"], "consent_verified")
        self.assertEqual(audit_trail[2]["event"], "data_accessed")


if __name__ == "__main__":
    unittest.main()
