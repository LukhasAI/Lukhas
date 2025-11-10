import os

# Adjust the path to import from the parent directory
import sys
import unittest
from unittest.mock import MagicMock, Mock

import yaml

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from core.reliability.ratelimit import QuotaConfig, RateLimiter
from core.reliability.ratelimit_backends import LimiterBackend
from typing import Dict, Tuple


# A simple in-memory backend for predictable testing that handles multiple keys
class InMemoryLimiterForTesting(LimiterBackend):
    def __init__(self):
        self.buckets: Dict[str, Dict[str, float]] = {} # Store buckets per key

    def allow(self, key: str, rate: float, burst: int) -> Tuple[bool, int, float]:
        now = 1.0 # Use a fixed time for predictability
        if key not in self.buckets:
            self.buckets[key] = {"tokens": float(burst)}

        bucket = self.buckets[key]

        # Simple decrement for testing, not a full token bucket implementation
        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            return True, int(bucket["tokens"]), now + 10.0 # Dummy reset time
        return False, 0, now + 10.0

class TestQuotaHierarchy(unittest.TestCase):

    def setUp(self):
        # Create a mock quota config file
        self.config_data = {
            "defaults": {"rate_per_sec": 100, "burst": 200},
            "orgs": {
                "org_abc": {"rate_per_sec": 50, "burst": 100}
            },
            "tokens": {
                "sk-abc...": {"rate_per_sec": 5, "burst": 10}
            },
            "routes": {
                "/v1/dreams": {"rate_per_sec": 3, "burst": 5},
                "/v1/responses": {"rate_per_sec": 40, "burst": 80}
            }
        }
        self.config_path = "test_quotas.yaml"
        with open(self.config_path, "w") as f:
            yaml.dump(self.config_data, f)

        self.quota_config = QuotaConfig(config_path=self.config_path)
        self.backend = InMemoryLimiterForTesting()
        self.rate_limiter = RateLimiter(backend=self.backend, config=self.quota_config)

    def tearDown(self):
        if os.path.exists(self.config_path):
            os.remove(self.config_path)

    def _create_mock_request(self, org, token, route):
        request = Mock()
        request.state = Mock()
        request.state.org = org
        request.state.token = token
        request.url = Mock()
        request.url.path = route
        # Simulate the auth header for token extraction logic
        request.headers = MagicMock()
        request.headers.get.return_value = f"Bearer {token}"
        return request

    def test_default_quota_applied(self):
        """Test that default quotas are used when no specific rules match."""
        rate, burst = self.quota_config.resolve_limits("org_unknown", "tok_unknown", "/v1/unknown")
        self.assertEqual(rate, 100)
        self.assertEqual(burst, 200)

    def test_org_quota_overrides_default(self):
        """Test that org-level quota is more restrictive than default."""
        rate, burst = self.quota_config.resolve_limits("org_abc", "tok_unknown", "/v1/unknown")
        self.assertEqual(rate, 50)
        self.assertEqual(burst, 100)

    def test_token_quota_is_most_restrictive(self):
        """Test that token-level quota is the most restrictive."""
        rate, burst = self.quota_config.resolve_limits("org_abc", "sk-abc...", "/v1/unknown")
        self.assertEqual(rate, 5)
        self.assertEqual(burst, 10)

    def test_route_quota_is_most_restrictive(self):
        """Test that a route-specific quota can be the most restrictive."""
        rate, burst = self.quota_config.resolve_limits("org_abc", "tok_other", "/v1/dreams")
        self.assertEqual(rate, 3) # min(default_rate, org_rate, route_rate)
        self.assertEqual(burst, 5) # min(default_burst, org_burst, route_burst)

    def test_headers_correctness(self):
        """Test that the generated headers are correct."""
        request = self._create_mock_request("org_abc", "sk-abc...", "/v1/dreams")

        # Resolve limits to find the expected burst
        _, expected_burst = self.quota_config.resolve_limits("org_abc", "sk-abc...", "/v1/dreams")

        allowed, headers = self.rate_limiter.check_limit(request)

        self.assertTrue(allowed)
        self.assertEqual(headers["X-RateLimit-Limit"], str(expected_burst))
        self.assertEqual(headers["X-RateLimit-Remaining"], str(expected_burst - 1))
        self.assertTrue("X-RateLimit-Reset" in headers)

    def test_rate_limiter_denies_request_when_bucket_is_empty(self):
        """Test that the limiter denies a request if the bucket is empty."""
        org, token, route = "org_xyz", "tok_limited", "/v1/limited"
        request = self._create_mock_request(org, token, route)

        # Manually construct the key and empty the bucket for this test
        key = f"rl:{org}:{token}:{route}"
        self.backend.buckets[key] = {"tokens": 0.0}

        allowed, _ = self.rate_limiter.check_limit(request)

        self.assertFalse(allowed)

if __name__ == "__main__":
    unittest.main()
