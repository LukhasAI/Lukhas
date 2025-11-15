"""Production-grade Redis token store for Lukhas Identity System.

Provides high-performance, thread-safe token storage with:
- Automatic TTL expiry
- Sub-10ms revocation
- RFC 7662 introspection support
- Connection pooling and retry logic
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from uuid import uuid4

import redis
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class TokenMetadata(BaseModel):
    """Token metadata for introspection (RFC 7662)."""

    jti: str = Field(..., description="JWT ID (unique token identifier)")
    sub: str = Field(..., description="Subject (ΛID)")
    scope: str = Field(default="openid profile", description="OAuth2 scopes")
    exp: int = Field(..., description="Expiration timestamp (Unix)")
    iat: int = Field(..., description="Issued at timestamp (Unix)")
    iss: str = Field(default="https://ai", description="Issuer")
    client_id: Optional[str] = Field(None, description="Client identifier")
    token_type: str = Field(default="Bearer", description="Token type")
    active: bool = Field(default=True, description="Token active status")
    lid_type: Optional[str] = Field(None, description="ΛID type (USR/AGT/SVC/SYS)")
    revoked_at: Optional[int] = Field(None, description="Revocation timestamp")
    revocation_reason: Optional[str] = Field(None, description="Why token was revoked")


class RedisTokenStore:
    """Production Redis token store with TTL, revocation, and introspection.

    Thread-safe token operations with automatic expiry and sub-10ms revocation.

    Performance Targets:
        - SET/GET: <5ms p95
        - DEL (revocation): <10ms p95
        - Connection pool: 10-50 connections

    Example:
        ```python
        store = RedisTokenStore(redis_url="redis://localhost:6379/0")

        # Store token with 1-hour TTL
        await store.store_token(
            jti="tok_abc123",
            metadata={"sub": "usr_alice", "scope": "openid profile"},
            ttl_seconds=3600
        )

        # Introspect token
        data = await store.introspect_token("tok_abc123")
        assert data["active"] is True

        # Revoke token (immediate)
        await store.revoke_token("tok_abc123", reason="user_logout")
        ```
    """

    TOKEN_PREFIX = "lukhas:token:"
    REVOCATION_PREFIX = "lukhas:revoked:"

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        max_connections: int = 50,
        socket_timeout: float = 5.0,
        socket_connect_timeout: float = 5.0,
        retry_on_timeout: bool = True,
    ):
        """Initialize Redis connection pool.

        Args:
            redis_url: Redis connection URL
            max_connections: Maximum pool size
            socket_timeout: Socket timeout in seconds
            socket_connect_timeout: Connection timeout in seconds
            retry_on_timeout: Retry operations on timeout
        """
        self.pool = redis.ConnectionPool.from_url(
            redis_url,
            max_connections=max_connections,
            socket_timeout=socket_timeout,
            socket_connect_timeout=socket_connect_timeout,
            retry_on_timeout=retry_on_timeout,
            decode_responses=True,  # Auto-decode bytes to strings
        )
        self.client = redis.Redis(connection_pool=self.pool)
        logger.info(
            f"RedisTokenStore initialized: {redis_url} (pool_size={max_connections})"
        )

    def _make_token_key(self, jti: str) -> str:
        """Generate Redis key for token storage."""
        return f"{self.TOKEN_PREFIX}{jti}"

    def _make_revocation_key(self, jti: str) -> str:
        """Generate Redis key for revocation tracking."""
        return f"{self.REVOCATION_PREFIX}{jti}"

    async def store_token(
        self,
        jti: str,
        metadata: Dict[str, Any],
        ttl_seconds: int = 3600,
    ) -> bool:
        """Store token with automatic TTL expiry.

        Args:
            jti: JWT ID (unique token identifier)
            metadata: Token metadata (sub, scope, exp, etc.)
            ttl_seconds: Time-to-live in seconds (default: 1 hour)

        Returns:
            True if stored successfully

        Raises:
            redis.exceptions.ConnectionError: If Redis is unavailable
        """
        try:
            # Add server-side timestamps
            now = int(datetime.utcnow().timestamp())
            metadata.setdefault("iat", now)
            metadata.setdefault("exp", now + ttl_seconds)
            metadata["jti"] = jti

            # Validate with Pydantic
            token_data = TokenMetadata(**metadata)

            # Store with TTL
            key = self._make_token_key(jti)
            value = token_data.model_dump_json()

            result = self.client.setex(key, ttl_seconds, value)

            logger.debug(
                f"Token stored: jti={jti}, sub={token_data.sub}, ttl={ttl_seconds}s"
            )
            return bool(result)

        except redis.exceptions.RedisError as e:
            logger.error(f"Redis error storing token {jti}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error storing token {jti}: {e}")
            raise

    async def get_token(self, jti: str) -> Optional[TokenMetadata]:
        """Retrieve token metadata.

        Args:
            jti: JWT ID

        Returns:
            TokenMetadata if found and not revoked, None otherwise
        """
        try:
            # Check if revoked first (fast path)
            if await self.is_revoked(jti):
                logger.debug(f"Token {jti} is revoked")
                return None

            # Retrieve token data
            key = self._make_token_key(jti)
            value = self.client.get(key)

            if value is None:
                logger.debug(f"Token {jti} not found (expired or never existed)")
                return None

            # Parse and validate
            token_data = TokenMetadata.model_validate_json(value)

            # Check expiry (redundant with TTL, but defensive)
            now = int(datetime.utcnow().timestamp())
            if token_data.exp < now:
                logger.warning(f"Token {jti} expired but not yet evicted by Redis TTL")
                return None

            return token_data

        except redis.exceptions.RedisError as e:
            logger.error(f"Redis error retrieving token {jti}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error parsing token {jti}: {e}")
            return None

    async def introspect_token(self, jti: str) -> Dict[str, Any]:
        """Introspect token (RFC 7662 compliant).

        Args:
            jti: JWT ID

        Returns:
            Introspection response with 'active' field and metadata
        """
        token_data = await self.get_token(jti)

        if token_data is None:
            # Token not found or revoked
            return {"active": False}

        # Return RFC 7662 compliant response
        return {
            "active": True,
            "sub": token_data.sub,
            "scope": token_data.scope,
            "exp": token_data.exp,
            "iat": token_data.iat,
            "iss": token_data.iss,
            "token_type": token_data.token_type,
            "jti": token_data.jti,
            "client_id": token_data.client_id,
            "lid_type": token_data.lid_type,
        }

    async def revoke_token(
        self,
        jti: str,
        reason: str = "unspecified",
        ttl_seconds: int = 86400,
    ) -> bool:
        """Revoke token immediately (target: <10ms).

        Args:
            jti: JWT ID to revoke
            reason: Revocation reason (audit trail)
            ttl_seconds: How long to track revocation (default: 24 hours)

        Returns:
            True if revoked successfully
        """
        try:
            now = int(datetime.utcnow().timestamp())

            # Store revocation record
            revocation_key = self._make_revocation_key(jti)
            revocation_data = json.dumps(
                {"revoked_at": now, "reason": reason, "jti": jti}
            )

            # Set revocation flag with TTL
            self.client.setex(revocation_key, ttl_seconds, revocation_data)

            # Delete token (optional - TTL will expire it anyway)
            token_key = self._make_token_key(jti)
            self.client.delete(token_key)

            logger.info(f"Token revoked: jti={jti}, reason={reason}")
            return True

        except redis.exceptions.RedisError as e:
            logger.error(f"Redis error revoking token {jti}: {e}")
            raise

    async def is_revoked(self, jti: str) -> bool:
        """Check if token is revoked (fast path).

        Args:
            jti: JWT ID

        Returns:
            True if revoked
        """
        try:
            key = self._make_revocation_key(jti)
            return self.client.exists(key) > 0
        except redis.exceptions.RedisError as e:
            logger.error(f"Redis error checking revocation for {jti}: {e}")
            # Fail open: assume not revoked to avoid blocking users
            return False

    async def get_revocation_info(self, jti: str) -> Optional[Dict[str, Any]]:
        """Get revocation details for audit.

        Args:
            jti: JWT ID

        Returns:
            Revocation metadata if token is revoked
        """
        try:
            key = self._make_revocation_key(jti)
            value = self.client.get(key)

            if value is None:
                return None

            return json.loads(value)

        except Exception as e:
            logger.error(f"Error retrieving revocation info for {jti}: {e}")
            return None

    async def cleanup_expired(self) -> int:
        """Manual cleanup of expired tokens (optional - Redis TTL handles this).

        Returns:
            Number of tokens cleaned up
        """
        # Redis TTL handles expiry automatically
        # This method exists for compatibility but is a no-op
        logger.debug("Redis TTL handles expiry automatically, no manual cleanup needed")
        return 0

    def health_check(self) -> Dict[str, Any]:
        """Check Redis connection health.

        Returns:
            Health status dictionary
        """
        try:
            # Ping Redis
            self.client.ping()

            # Get connection pool stats
            pool_info = {
                "max_connections": self.pool.max_connections,
                "connection_kwargs": {
                    k: v
                    for k, v in self.pool.connection_kwargs.items()
                    if k not in ["password"]
                },
            }

            return {"status": "healthy", "pool": pool_info}

        except redis.exceptions.RedisError as e:
            logger.error(f"Redis health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}

    def close(self):
        """Close Redis connection pool."""
        try:
            self.pool.disconnect()
            logger.info("Redis connection pool closed")
        except Exception as e:
            logger.error(f"Error closing Redis pool: {e}")
