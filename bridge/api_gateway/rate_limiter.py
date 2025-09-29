"""
LUKHAS AI - Rate Limiter
========================

Rate limiting functionality for the unified API gateway.

Copyright (c) 2025 LUKHAS AI. All rights reserved.
"""
import logging
import time
from collections import defaultdict
from typing import Any, Optional

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter for API gateway requests."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize rate limiter with configuration."""
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
        self.requests_per_minute = self.config.get("requests_per_minute", 60)
        self.burst_limit = self.config.get("burst_limit", 10)

        # In-memory storage for rate limiting (replace with Redis in production)
        self._request_counts: dict[str, list] = defaultdict(list)

    def check_rate_limit(self, client_id: str) -> dict[str, Any]:
        """Check if client has exceeded rate limit."""
        if not self.enabled:
            return {"allowed": True}

        current_time = time.time()
        minute_ago = current_time - 60

        # Clean old requests
        self._request_counts[client_id] = [
            req_time for req_time in self._request_counts[client_id] if req_time > minute_ago
        ]

        # Check rate limit
        request_count = len(self._request_counts[client_id])

        if request_count >= self.requests_per_minute:
            return {
                "allowed": False,
                "error": "Rate limit exceeded",
                "retry_after": 60,
                "current_count": request_count,
                "limit": self.requests_per_minute,
            }

        # Record this request
        self._request_counts[client_id].append(current_time)

        return {
            "allowed": True,
            "current_count": request_count + 1,
            "limit": self.requests_per_minute,
            "remaining": self.requests_per_minute - request_count - 1,
        }

    def get_client_id(self, request: dict[str, Any]) -> str:
        """Extract client ID from request for rate limiting."""
        # Try to get authenticated user ID first
        user_id = request.get("user_id")
        if user_id:
            return f"user:{user_id}"

        # Fall back to IP address
        client_ip = request.get("client_ip", "unknown")
        return f"ip:{client_ip}"

    def reset_client_limits(self, client_id: str) -> None:
        """Reset rate limits for a specific client."""
        if client_id in self._request_counts:
            del self._request_counts[client_id]

    def get_stats(self) -> dict[str, Any]:
        """Get rate limiting statistics."""
        current_time = time.time()
        minute_ago = current_time - 60

        active_clients = 0
        total_requests = 0

        for client_id, requests in self._request_counts.items():
            recent_requests = [r for r in requests if r > minute_ago]
            if recent_requests:
                active_clients += 1
                total_requests += len(recent_requests)

        return {
            "active_clients": active_clients,
            "total_requests_last_minute": total_requests,
            "rate_limit_per_minute": self.requests_per_minute,
            "enabled": self.enabled,
        }
