import json
import time
from typing import Dict, Optional, Tuple

import redis

from .idempotency import IdempotencyStore


class RedisIdempotencyStore(IdempotencyStore):
    def __init__(self, url: str, ttl_seconds: int = 300):
        self.r = redis.Redis.from_url(url, decode_responses=True)
        self.ttl = ttl_seconds

    def get(self, k: str) -> Optional[Tuple[int, Dict, bytes, str]]:
        raw = self.r.get(k)
        if not raw:
            return None

        try:
            obj = json.loads(raw)
            # Ensure all keys are present, providing defaults for backward compatibility
            status = obj.get("status")
            headers = obj.get("headers", {})
            body_hex = obj.get("body_hex", "")
            body_sha256 = obj.get("body_sha256", self._hash_body(bytes.fromhex(body_hex)))  # Recalculate if missing

            if status is None:
                return None  # Invalid data

            return status, headers, bytes.fromhex(body_hex), body_sha256
        except (json.JSONDecodeError, KeyError):
            # Handle cases where the data is malformed or missing keys
            return None

    def put(self, k: str, status: int, headers: Dict, body: bytes) -> None:
        body_sha256 = self._hash_body(body)
        payload = {
            "status": status,
            "headers": headers,
            "body_hex": (body or b"").hex(),
            "body_sha256": body_sha256,
            "ts": int(time.time()),
        }

        # Using a pipeline for atomicity
        with self.r.pipeline() as p:
            p.set(k, json.dumps(payload))
            p.expire(k, self.ttl)
            p.execute()
