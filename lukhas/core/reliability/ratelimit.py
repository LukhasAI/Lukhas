import os
import time
from typing import Dict, Tuple, Optional, Any
import yaml
from .ratelimit_backends import LimiterBackend, RedisTokenBucket

class QuotaConfig:
    """Loads and resolves hierarchical quotas from a YAML file."""

    def __init__(self, config_path: str = "configs/quotas.yaml"):
        self.config_path = config_path
        self.quotas = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if not os.path.exists(self.config_path):
            # Return a default config if the file doesn't exist to prevent crashes
            return {"defaults": {"rate_per_sec": 10, "burst": 20}}
        with open(self.config_path, "r") as f:
            return yaml.safe_load(f)

    def resolve_limits(self, org: Optional[str], token: Optional[str], route: str) -> Tuple[float, int]:
        """
        Resolves the effective rate and burst limit by taking the minimum of the applicable quotas.
        """
        defaults = self.quotas.get("defaults", {"rate_per_sec": 10, "burst": 20})

        # Start with the default limits
        applicable_limits = [defaults]

        if org and "orgs" in self.quotas and org in self.quotas["orgs"]:
            applicable_limits.append(self.quotas["orgs"][org])

        if token and "tokens" in self.quotas and token in self.quotas["tokens"]:
            applicable_limits.append(self.quotas["tokens"][token])

        if route in self.quotas.get("routes", {}):
            applicable_limits.append(self.quotas["routes"][route])

        # The effective limit is the minimum of all applicable quotas for both rate and burst
        effective_rate = min(limit.get("rate_per_sec", defaults["rate_per_sec"]) for limit in applicable_limits)
        effective_burst = min(limit.get("burst", defaults["burst"]) for limit in applicable_limits)

        return effective_rate, effective_burst


class RateLimiter:
    """
    Hierarchical rate limiter that uses a configurable backend.
    """

    def __init__(self, backend: LimiterBackend, config: QuotaConfig):
        self.backend = backend
        self.config = config

    def _extract_context(self, request: Any) -> Tuple[Optional[str], Optional[str], str]:
        """
        Extracts (org, token, route) from the request.
        This is a placeholder and needs to be adapted to the actual request object.
        For now, it simulates extraction for testing purposes.
        """
        # In a real FastAPI app, this would come from auth middleware
        org = getattr(request.state, "org", "org_abc")
        # To simulate different tokens, we could inspect headers
        auth_header = getattr(request.headers, "get", lambda k: "")("Authorization")
        if "sk-abc" in auth_header:
            token = "sk-abc..."
        else:
            token = getattr(request.state, "token", "default_token")

        route = request.url.path
        return org, token, route

    def check_limit(self, request: Any) -> Tuple[bool, Dict[str, str]]:
        """
        Checks the rate limit for a request and returns the result and headers.
        """
        org, token, route = self._extract_context(request)
        
        rate, burst = self.config.resolve_limits(org, token, route)
        
        # The key should uniquely identify the user/token within the hierarchy
        key = f"rl:{org}:{token}:{route}"

        allowed, remaining, reset_ts = self.backend.allow(key, rate, burst)
        
        headers = {
            "X-RateLimit-Limit": str(burst),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(int(reset_ts)),
        }

        return allowed, headers

# Helper to create a default rate limiter based on environment variables
def create_rate_limiter() -> RateLimiter:
    backend_type = os.environ.get("LUKHAS_RL_BACKEND", "redis")

    if backend_type == "redis":
        redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
        backend = RedisTokenBucket(url=redis_url)
    else: # Fallback to an in-memory backend for testing
        class InMemoryLimiter(LimiterBackend):
            def __init__(self):
                self.buckets: Dict[str, Dict[str, float]] = {}

            def allow(self, key: str, rate: float, burst: int) -> Tuple[bool, int, float]:
                if key not in self.buckets:
                    self.buckets[key] = {"tokens": float(burst), "ts": time.time()}

                bucket = self.buckets[key]
                now = time.time()
                elapsed = now - bucket["ts"]
                bucket["tokens"] = min(burst, bucket["tokens"] + elapsed * rate)
                bucket["ts"] = now

                if bucket["tokens"] >= 1:
                    bucket["tokens"] -= 1
                    reset = (burst - bucket["tokens"]) / rate if rate > 0 else float('inf')
                    return True, int(bucket["tokens"]), now + reset
                else:
                    reset = (1 - bucket["tokens"]) / rate if rate > 0 else float('inf')
                    return False, int(bucket["tokens"]), now + reset

        backend = InMemoryLimiter()

    config = QuotaConfig()
    return RateLimiter(backend=backend, config=config)
