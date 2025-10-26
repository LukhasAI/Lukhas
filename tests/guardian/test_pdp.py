import os
import sys
import unittest
from datetime import datetime
from typing import Optional

# Add the project root to the path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from adapters.openai.policy_models import Context
from adapters.openai.policy_pdp import PDP, PolicyLoader


class TestGuardianPDP(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Load the policy once for all tests."""
        policy_path = os.path.join(os.path.dirname(__file__), "test_guardian_policies.yaml")
        cls.policy = PolicyLoader.load_from_file(policy_path)
        cls.pdp = PDP(cls.policy)

    def _create_context(
        self,
        scopes: set,
        action: str,
        resource: str,
        model: Optional[str] = None,
        ip: str = "10.0.0.1",
        time_utc: Optional[datetime] = None,
        tenant_id: str = "acme"
    ) -> Context:
        """Helper to create a mock context for testing."""
        return Context(
            tenant_id=tenant_id,
            user_id="user-123",
            roles={"member"},
            scopes=scopes,
            action=action,
            resource=resource,
            model=model,
            ip=ip,
            time_utc=time_utc or datetime(2023, 1, 1, 12, 0, 0),
            data_classification="internal",
            policy_etag=self.policy.etag,
            trace_id="trace-abc"
        )

    def test_default_deny_when_no_rules_match(self):
        """1. PDP should deny access if no rules match the request."""
        ctx = self._create_context(
            scopes={"some:scope"},
            action="nonexistent.action",
            resource="/v1/nonexistent"
        )
        decision = self.pdp.decide(ctx)
        self.assertFalse(decision.allow)
        self.assertEqual(decision.reason, "default_deny")
        self.assertIsNone(decision.rule_id)

    def test_allow_with_correct_scope(self):
        """2. PDP should allow access with a matching scope and resource."""
        ctx = self._create_context(
            scopes={"dreams:write"},
            action="dreams.create",
            resource="/v1/dreams"
        )
        decision = self.pdp.decide(ctx)
        self.assertTrue(decision.allow)
        self.assertEqual(decision.rule_id, "R-001-AllowDreamCreate")
        self.assertEqual(decision.reason, "allow_rule_matched:R-001-AllowDreamCreate")

    def test_deny_overrides_allow(self):
        """3. PDP should deny if a Deny rule matches, even if an Allow rule also matches."""
        ctx = self._create_context(
            scopes={"dreams:write"},
            action="dreams.create",
            resource="/v1/dreams",
            model="model-restricted"  # This should trigger the Deny rule
        )
        decision = self.pdp.decide(ctx)
        self.assertFalse(decision.allow)
        self.assertEqual(decision.rule_id, "R-002-DenyRestrictedModel")
        self.assertEqual(decision.reason, "deny_rule_matched:R-002-DenyRestrictedModel")

    def test_resource_wildcard_match(self):
        """5. PDP should allow access based on a resource wildcard."""
        ctx = self._create_context(
            scopes={"indexes:read"},
            action="indexes.read",
            resource="indexes/some-random-index-123"
        )
        decision = self.pdp.decide(ctx)
        self.assertTrue(decision.allow)
        self.assertEqual(decision.rule_id, "R-004-AllowIndexReadWildcard")

    def test_time_window_condition_allow(self):
        """7. PDP should allow access within the specified time window."""
        ctx = self._create_context(
            scopes={"time:access"},
            action="time.check",
            resource="/v1/time",
            time_utc=datetime(2023, 1, 1, 14, 0, 0) # 14:00 is between 09:00 and 17:00
        )
        decision = self.pdp.decide(ctx)
        self.assertTrue(decision.allow)
        self.assertEqual(decision.rule_id, "R-005-AllowTimeWindow")

    def test_time_window_condition_deny(self):
        """7. PDP should deny access outside the specified time window."""
        ctx = self._create_context(
            scopes={"time:access"},
            action="time.check",
            resource="/v1/time",
            time_utc=datetime(2023, 1, 1, 20, 0, 0) # 20:00 is outside 09:00-17:00
        )
        decision = self.pdp.decide(ctx)
        self.assertFalse(decision.allow)
        self.assertEqual(decision.reason, "default_deny") # No allow rule matches

    def test_ip_cidr_condition_deny(self):
        """10. PDP should deny access from a blocked IP CIDR range."""
        ctx = self._create_context(
            scopes={"any:scope"},
            action="any.action",
            resource="/any/resource",
            ip="192.168.1.50" # This IP is in the denied range
        )
        decision = self.pdp.decide(ctx)
        self.assertFalse(decision.allow)
        self.assertEqual(decision.rule_id, "R-006-DenyIpRange")

    def test_ip_cidr_condition_not_denied(self):
        """10. PDP should not deny based on IP if the IP is not in the range."""
        ctx = self._create_context(
            scopes={"any:scope"},
            action="any.action",
            resource="/any/resource",
            ip="10.0.0.2" # This IP is not in the denied range
        )
        decision = self.pdp.decide(ctx)
        # It will be denied by default, but not by the IP rule
        self.assertFalse(decision.allow)
        self.assertEqual(decision.reason, "default_deny")
        self.assertNotEqual(decision.rule_id, "R-006-DenyIpRange")

if __name__ == "__main__":
    unittest.main()
