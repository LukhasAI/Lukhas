import time
import unittest

import fakeredis

from core.reliability.idempotency_redis import RedisIdempotencyStore


class TestRedisIdempotencyStore(unittest.TestCase):

    def setUp(self):
        # Use fakeredis for testing
        self.fake_redis_server = fakeredis.FakeServer()
        self.store = RedisIdempotencyStore(url="redis://localhost:6379/0", ttl_seconds=2)
        self.store.r = fakeredis.FakeRedis(server=self.fake_redis_server)

    def tearDown(self):
        self.store.r.flushall()

    def test_put_and_get_hit(self):
        """Test storing and retrieving a response."""
        key = self.store.key("route", "tenant", "idem_key")
        status = 200
        headers = {"X-Trace-Id": "123"}
        body = b'{"message": "success"}'

        self.store.put(key, status, headers, body)

        result = self.store.get(key)
        self.assertIsNotNone(result)
        retrieved_status, retrieved_headers, retrieved_body, retrieved_hash = result

        self.assertEqual(status, retrieved_status)
        self.assertEqual(headers, retrieved_headers)
        self.assertEqual(body, retrieved_body)
        self.assertEqual(self.store._hash_body(body), retrieved_hash)

    def test_get_miss(self):
        """Test getting a non-existent key."""
        key = self.store.key("route", "tenant", "non_existent_key")
        result = self.store.get(key)
        self.assertIsNone(result)

    def test_ttl_expiry(self):
        """Test that a key expires after the TTL."""
        self.store.ttl = 1 # override for faster test
        key = self.store.key("route", "tenant", "ttl_key")
        status = 201
        headers = {}
        body = b"data"

        self.store.put(key, status, headers, body)

        # Wait for TTL to expire
        time.sleep(1.1)

        result = self.store.get(key)
        self.assertIsNone(result)

    def test_body_hash_correctness(self):
        """Test that the body hash is correctly stored and retrieved."""
        key = self.store.key("route", "tenant", "hash_key")
        body = b"some complex body"

        self.store.put(key, 200, {}, body)

        result = self.store.get(key)
        self.assertIsNotNone(result)
        _, _, _, retrieved_hash = result

        expected_hash = self.store._hash_body(body)
        self.assertEqual(expected_hash, retrieved_hash)

    def test_empty_body(self):
        """Test handling of an empty body."""
        key = self.store.key("route", "tenant", "empty_body_key")
        status = 204
        headers = {}
        body = b""

        self.store.put(key, status, headers, body)

        result = self.store.get(key)
        self.assertIsNotNone(result)
        retrieved_status, _, retrieved_body, retrieved_hash = result

        self.assertEqual(status, retrieved_status)
        self.assertEqual(body, retrieved_body)
        self.assertEqual(self.store._hash_body(body), retrieved_hash)

    def test_headers_persisted(self):
        """Test that headers are correctly persisted."""
        key = self.store.key("route", "tenant", "headers_key")
        headers = {
            "Content-Type": "application/json",
            "X-RateLimit-Limit": "100",
        }

        self.store.put(key, 200, headers, b"body")

        result = self.store.get(key)
        self.assertIsNotNone(result)
        _, retrieved_headers, _, _ = result

        self.assertEqual(headers, retrieved_headers)

if __name__ == "__main__":
    unittest.main()
