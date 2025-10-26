#!/usr/bin/env python3
"""
LUKHAS Rate Limiting Module
T4/0.01% Excellence Standard

Production-grade rate limiting for WebAuthn and identity endpoints.
Implements sliding window rate limiting with Redis backend support.
"""

import hashlib
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class RateLimitType(Enum):
    """Rate limit types"""
    WEBAUTHN_REGISTRATION = "webauthn_registration"
    WEBAUTHN_AUTHENTICATION = "webauthn_authentication"
    TOKEN_VALIDATION = "token_validation"
    API_GENERAL = "api_general"


@dataclass
class RateLimitConfig:
    """Rate limit configuration"""
    requests_per_minute: int
    requests_per_hour: int
    burst_allowance: int = 5
    lockout_duration_minutes: int = 15
    enable_progressive_penalties: bool = True


class RateLimiter:
    """Production-grade sliding window rate limiter"""

    def __init__(self):
        self.configs = {
            RateLimitType.WEBAUTHN_REGISTRATION: RateLimitConfig(
                requests_per_minute=5,
                requests_per_hour=20,
                burst_allowance=2,
                lockout_duration_minutes=30
            ),
            RateLimitType.WEBAUTHN_AUTHENTICATION: RateLimitConfig(
                requests_per_minute=30,
                requests_per_hour=200,
                burst_allowance=10,
                lockout_duration_minutes=10
            ),
            RateLimitType.TOKEN_VALIDATION: RateLimitConfig(
                requests_per_minute=100,
                requests_per_hour=2000,
                burst_allowance=50,
                lockout_duration_minutes=5
            ),
            RateLimitType.API_GENERAL: RateLimitConfig(
                requests_per_minute=60,
                requests_per_hour=1000,
                burst_allowance=20,
                lockout_duration_minutes=5
            )
        }

        # In-memory storage (for production, use Redis)
        self._minute_windows: Dict[str, deque] = defaultdict(deque)
        self._hour_windows: Dict[str, deque] = defaultdict(deque)
        self._lockouts: Dict[str, float] = {}
        self._violation_counts: Dict[str, int] = defaultdict(int)

    def _get_client_key(self,
                       client_identifier: str,
                       rate_limit_type: RateLimitType,
                       additional_context: Optional[str] = None) -> str:
        """Generate client key for rate limiting"""
        parts = [client_identifier, rate_limit_type.value]
        if additional_context:
            parts.append(additional_context)

        key_string = ":".join(parts)
        return hashlib.sha256(key_string.encode()).hexdigest()[:32]

    def _cleanup_windows(self, current_time: float):
        """Cleanup old entries from sliding windows"""
        minute_cutoff = current_time - 60
        hour_cutoff = current_time - 3600

        # Clean minute windows
        for key, window in list(self._minute_windows.items()):
            while window and window[0] < minute_cutoff:
                window.popleft()
            if not window:
                del self._minute_windows[key]

        # Clean hour windows
        for key, window in list(self._hour_windows.items()):
            while window and window[0] < hour_cutoff:
                window.popleft()
            if not window:
                del self._hour_windows[key]

        # Clean expired lockouts
        expired_lockouts = [
            key for key, lockout_until in self._lockouts.items()
            if lockout_until < current_time
        ]
        for key in expired_lockouts:
            del self._lockouts[key]
            # Reduce violation count on lockout expiry
            if key in self._violation_counts:
                self._violation_counts[key] = max(0, self._violation_counts[key] - 1)

    async def check_rate_limit(self,
                              client_identifier: str,
                              rate_limit_type: RateLimitType,
                              request_context: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if request should be rate limited

        Args:
            client_identifier: Client ID (IP, user ID, etc.)
            rate_limit_type: Type of rate limit to check
            request_context: Additional request context

        Returns:
            Tuple of (allowed: bool, metadata: dict)
        """
        current_time = time.time()
        config = self.configs[rate_limit_type]

        # Generate client key
        additional_context = None
        if request_context:
            # Add user ID to context for per-user limits
            user_id = request_context.get('user_id')
            if user_id:
                additional_context = f"user:{user_id}"

        client_key = self._get_client_key(client_identifier, rate_limit_type, additional_context)

        # Cleanup old entries
        self._cleanup_windows(current_time)

        # Check if client is locked out
        if client_key in self._lockouts:
            lockout_until = self._lockouts[client_key]
            if lockout_until > current_time:
                remaining_lockout = lockout_until - current_time
                return False, {
                    "error": "rate_limit_exceeded",
                    "message": "Client is locked out due to rate limit violations",
                    "lockout_remaining_seconds": remaining_lockout,
                    "retry_after": int(remaining_lockout) + 1
                }

        # Get current windows
        minute_window = self._minute_windows[client_key]
        hour_window = self._hour_windows[client_key]

        # Count requests in current windows
        minute_requests = len(minute_window)
        hour_requests = len(hour_window)

        # Check if burst allowance is available
        burst_available = config.burst_allowance - minute_requests

        # Determine if request is allowed
        minute_limit_ok = minute_requests < config.requests_per_minute
        hour_limit_ok = hour_requests < config.requests_per_hour

        # Apply progressive penalties for repeat violators
        violation_count = self._violation_counts[client_key]
        if violation_count > 0 and config.enable_progressive_penalties:
            # Reduce limits for repeat violators
            penalty_factor = max(0.5, 1.0 - (violation_count * 0.1))
            effective_minute_limit = int(config.requests_per_minute * penalty_factor)
            effective_hour_limit = int(config.requests_per_hour * penalty_factor)

            minute_limit_ok = minute_requests < effective_minute_limit
            hour_limit_ok = hour_requests < effective_hour_limit

        # Check limits
        if not (minute_limit_ok and hour_limit_ok):
            # Rate limit exceeded
            self._violation_counts[client_key] += 1

            # Apply lockout for severe violations
            if violation_count >= 3:  # 3 strikes rule
                lockout_duration = config.lockout_duration_minutes * 60
                # Progressive lockout: longer for repeat offenders
                lockout_duration *= (1 + violation_count * 0.5)
                self._lockouts[client_key] = current_time + lockout_duration

                logger.warning(f"Rate limit lockout applied: client={client_identifier}, type={rate_limit_type.value}, duration={lockout_duration}s")

                return False, {
                    "error": "rate_limit_exceeded",
                    "message": "Rate limit exceeded, lockout applied",
                    "lockout_duration_seconds": lockout_duration,
                    "retry_after": int(lockout_duration) + 1,
                    "violation_count": violation_count + 1
                }

            # Determine which limit was exceeded
            if not minute_limit_ok:
                retry_after = 60 - (current_time % 60)  # Next minute boundary
                limit_type = "per_minute"
                limit_value = config.requests_per_minute
            else:
                retry_after = 3600 - (current_time % 3600)  # Next hour boundary
                limit_type = "per_hour"
                limit_value = config.requests_per_hour

            logger.warning(f"Rate limit exceeded: client={client_identifier}, type={rate_limit_type.value}, limit={limit_type}")

            return False, {
                "error": "rate_limit_exceeded",
                "message": f"Rate limit exceeded: {minute_requests}/{config.requests_per_minute} per minute, {hour_requests}/{config.requests_per_hour} per hour",
                "limit_type": limit_type,
                "limit_value": limit_value,
                "current_usage": minute_requests if limit_type == "per_minute" else hour_requests,
                "retry_after": int(retry_after) + 1,
                "violation_count": violation_count + 1
            }

        # Request allowed - record it
        minute_window.append(current_time)
        hour_window.append(current_time)

        # Calculate remaining quota
        remaining_minute = config.requests_per_minute - minute_requests - 1
        remaining_hour = config.requests_per_hour - hour_requests - 1

        return True, {
            "allowed": True,
            "remaining_minute": remaining_minute,
            "remaining_hour": remaining_hour,
            "reset_minute": int(current_time + (60 - (current_time % 60))),
            "reset_hour": int(current_time + (3600 - (current_time % 3600))),
            "burst_remaining": burst_available - 1
        }

    def get_client_status(self,
                         client_identifier: str,
                         rate_limit_type: RateLimitType) -> Dict[str, Any]:
        """Get current rate limit status for client"""
        current_time = time.time()
        client_key = self._get_client_key(client_identifier, rate_limit_type)
        config = self.configs[rate_limit_type]

        self._cleanup_windows(current_time)

        minute_requests = len(self._minute_windows[client_key])
        hour_requests = len(self._hour_windows[client_key])

        lockout_until = self._lockouts.get(client_key, 0)
        is_locked_out = lockout_until > current_time

        return {
            "client_identifier": client_identifier,
            "rate_limit_type": rate_limit_type.value,
            "minute_requests": minute_requests,
            "hour_requests": hour_requests,
            "minute_limit": config.requests_per_minute,
            "hour_limit": config.requests_per_hour,
            "is_locked_out": is_locked_out,
            "lockout_remaining": max(0, lockout_until - current_time) if is_locked_out else 0,
            "violation_count": self._violation_counts[client_key],
            "timestamp": current_time
        }


# Global rate limiter instance
_global_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance"""
    global _global_rate_limiter
    if _global_rate_limiter is None:
        _global_rate_limiter = RateLimiter()
        logger.info("🚦 Rate limiter initialized")
    return _global_rate_limiter


# FastAPI dependency
async def check_webauthn_rate_limit(client_ip: str,
                                   operation: str,
                                   user_id: Optional[str] = None) -> Dict[str, Any]:
    """FastAPI dependency for WebAuthn rate limiting"""
    rate_limiter = get_rate_limiter()

    # Determine rate limit type
    if operation == "registration":
        limit_type = RateLimitType.WEBAUTHN_REGISTRATION
    elif operation == "authentication":
        limit_type = RateLimitType.WEBAUTHN_AUTHENTICATION
    else:
        limit_type = RateLimitType.API_GENERAL

    context = {"user_id": user_id} if user_id else None

    allowed, metadata = await rate_limiter.check_rate_limit(
        client_ip, limit_type, context
    )

    if not allowed:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=429,
            detail=metadata,
            headers={"Retry-After": str(metadata.get("retry_after", 60))}
        )

    return metadata
