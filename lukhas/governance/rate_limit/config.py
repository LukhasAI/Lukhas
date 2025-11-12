"""
Rate limiting configuration for LUKHAS AI.

Defines rate limit rules for different endpoints and user tiers.
"""

from dataclasses import dataclass

# T4: code=UP035 | ticket=ruff-cleanup | owner=lukhas-cleanup-team | status=resolved
# reason: Modernizing deprecated typing imports to native Python 3.9+ types for rate limiting
# estimate: 10min | priority: high | dependencies: none
from typing import Optional


@dataclass
class RateLimitRule:
    """
    Rate limit rule for a specific endpoint or pattern.

    Attributes:
        requests: Maximum number of requests allowed
        window_seconds: Time window in seconds
        path_pattern: Path pattern to match (e.g., "/api/v1/consciousness/*")
        tier: User tier this rule applies to (None = all tiers)
        description: Human-readable description of the rule
    """
    requests: int
    window_seconds: int
    path_pattern: str = "*"
    tier: Optional[int] = None
    description: str = ""

    @property
    def identifier(self) -> str:
        """Unique identifier for this rule."""
        tier_str = f"tier{self.tier}" if self.tier is not None else "all"
        return f"{self.path_pattern}:{tier_str}:{self.requests}/{self.window_seconds}s"


@dataclass
class RateLimitConfig:
    """
    Configuration for rate limiting system.

    Attributes:
        enabled: Whether rate limiting is enabled
        per_user_rules: Rate limit rules per authenticated user
        per_ip_rules: Rate limit rules per IP address
        burst_multiplier: Multiplier for burst traffic (e.g., 2.0 = allow 2x requests in short bursts)
        blocked_ips: List of IP addresses to block completely
        whitelisted_ips: List of IP addresses exempt from rate limiting
    """
    enabled: bool = True
    per_user_rules: List[RateLimitRule] = None
    per_ip_rules: List[RateLimitRule] = None
    burst_multiplier: float = 1.5
    blocked_ips: list[str] = None
    whitelisted_ips: list[str] = None

    def __post_init__(self):
        """Initialize default rules if not provided."""
        if self.per_user_rules is None:
            self.per_user_rules = self._default_per_user_rules()

        if self.per_ip_rules is None:
            self.per_ip_rules = self._default_per_ip_rules()

        if self.blocked_ips is None:
            self.blocked_ips = []

        if self.whitelisted_ips is None:
            self.whitelisted_ips = []

    def _default_per_user_rules(self) -> List[RateLimitRule]:
        """
        Default per-user rate limit rules.

        Strategy:
        - Tier 0 (Free): 100 requests/hour (reasonable for testing)
        - Tier 1 (Basic): 1000 requests/hour (sufficient for development)
        - Tier 2+ (Pro/Enterprise): 10000 requests/hour (production usage)

        Special endpoints have stricter limits to prevent abuse:
        - Feedback submission: 60 requests/hour (1 per minute)
        - Trace creation: 1000 requests/hour
        - Query endpoints: Higher limits
        """
        return [
            # Default limits by tier
            RateLimitRule(
                requests=100,
                window_seconds=3600,
                path_pattern="*",
                tier=0,
                description="Free tier: 100 requests/hour"
            ),
            RateLimitRule(
                requests=1000,
                window_seconds=3600,
                path_pattern="*",
                tier=1,
                description="Basic tier: 1000 requests/hour"
            ),
            RateLimitRule(
                requests=10000,
                window_seconds=3600,
                path_pattern="*",
                tier=2,
                description="Pro tier: 10000 requests/hour"
            ),

            # Feedback endpoints (stricter limits to prevent spam)
            RateLimitRule(
                requests=60,
                window_seconds=3600,
                path_pattern="/feedback/*",
                tier=0,
                description="Free tier feedback: 60 requests/hour (1/min)"
            ),
            RateLimitRule(
                requests=300,
                window_seconds=3600,
                path_pattern="/feedback/*",
                tier=1,
                description="Basic tier feedback: 300 requests/hour (5/min)"
            ),

            # Consciousness query endpoints
            RateLimitRule(
                requests=50,
                window_seconds=3600,
                path_pattern="/api/v1/consciousness/query",
                tier=0,
                description="Free tier consciousness queries: 50/hour"
            ),
            RateLimitRule(
                requests=500,
                window_seconds=3600,
                path_pattern="/api/v1/consciousness/query",
                tier=1,
                description="Basic tier consciousness queries: 500/hour"
            ),
        ]

    def _default_per_ip_rules(self) -> List[RateLimitRule]:
        """
        Default per-IP rate limit rules (applied to all requests from an IP).

        Strategy:
        - More generous than per-user to allow multiple users behind same NAT
        - Prevents single IP from overwhelming the system
        - Protects against DDoS from compromised machines
        """
        return [
            # Global IP limits (prevents DDoS)
            RateLimitRule(
                requests=10000,
                window_seconds=3600,
                path_pattern="*",
                tier=None,
                description="Per-IP: 10000 requests/hour (prevents DDoS)"
            ),
            RateLimitRule(
                requests=500,
                window_seconds=60,
                path_pattern="*",
                tier=None,
                description="Per-IP: 500 requests/minute (burst protection)"
            ),

            # Authentication endpoints (prevent brute force)
            RateLimitRule(
                requests=20,
                window_seconds=3600,
                path_pattern="/api/v1/auth/*",
                tier=None,
                description="Per-IP auth: 20 attempts/hour (brute force protection)"
            ),
            RateLimitRule(
                requests=5,
                window_seconds=60,
                path_pattern="/api/v1/auth/login",
                tier=None,
                description="Per-IP login: 5 attempts/minute"
            ),
        ]

    def get_rules_for_user(self, path: str, tier: int) -> List[RateLimitRule]:
        """
        Get applicable rate limit rules for a user request.

        Args:
            path: Request path
            tier: User tier level

        Returns:
            List of applicable rate limit rules (most specific first)
        """
        applicable_rules = []

        for rule in self.per_user_rules:
            # Check if rule applies to this tier
            if rule.tier is not None and rule.tier != tier:
                continue

            # Check if path matches pattern
            if self._path_matches_pattern(path, rule.path_pattern):
                applicable_rules.append(rule)

        # Sort by specificity (most specific first)
        applicable_rules.sort(key=lambda r: (
            0 if r.path_pattern == "*" else 1,  # Specific paths first
            -len(r.path_pattern),  # Longer patterns first
            r.tier is not None,  # Tier-specific rules first
        ), reverse=True)

        return applicable_rules

    def get_rules_for_ip(self, path: str) -> List[RateLimitRule]:
        """
        Get applicable rate limit rules for an IP address.

        Args:
            path: Request path

        Returns:
            List of applicable rate limit rules (most specific first)
        """
        applicable_rules = []

        for rule in self.per_ip_rules:
            if self._path_matches_pattern(path, rule.path_pattern):
                applicable_rules.append(rule)

        # Sort by specificity (most specific first)
        applicable_rules.sort(key=lambda r: (
            0 if r.path_pattern == "*" else 1,
            -len(r.path_pattern),
        ), reverse=True)

        return applicable_rules

    def _path_matches_pattern(self, path: str, pattern: str) -> bool:
        """
        Check if a path matches a pattern.

        Supports:
        - Exact match: "/api/v1/auth/login"
        - Wildcard: "/api/v1/auth/*" matches "/api/v1/auth/login"
        - Global: "*" matches everything

        Args:
            path: Request path to check
            pattern: Pattern to match against

        Returns:
            True if path matches pattern
        """
        if pattern == "*":
            return True

        if pattern.endswith("/*"):
            prefix = pattern[:-2]
            return path.startswith(prefix)

        return path == pattern

    def is_ip_blocked(self, ip: str) -> bool:
        """Check if an IP address is blocked."""
        return ip in self.blocked_ips

    def is_ip_whitelisted(self, ip: str) -> bool:
        """Check if an IP address is whitelisted (exempt from rate limiting)."""
        return ip in self.whitelisted_ips
