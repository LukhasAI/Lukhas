#!/usr/bin/env python3
"""
LUKHAS Identity Token Storage - Production Schema v1.0.0

Implements secure token storage with rotation history, revocation support,
and key management for ΛiD token lifecycle management.

Constellation Framework: Identity ⚛️ pillar with cross-system coordination.
"""

from __future__ import annotations
import time
import json
import os
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, asdict
from enum import Enum
from opentelemetry import trace
from prometheus_client import Counter, Histogram, Gauge

tracer = trace.get_tracer(__name__)

# Prometheus metrics (test-safe)
class MockMetric:
    def labels(self, **kwargs):
        return self
    def inc(self, amount=1):
        pass
    def dec(self, amount=1):
        pass
    def observe(self, amount):
        pass

try:
    token_storage_operations_total = Counter(
        'lukhas_token_storage_operations_total',
        'Total token storage operations',
        ['component', 'operation', 'status']
    )
except ValueError:
    token_storage_operations_total = MockMetric()

try:
    token_storage_latency_seconds = Histogram(
        'lukhas_token_storage_latency_seconds',
        'Token storage operation latency',
        ['component', 'operation'],
        buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
    )
except ValueError:
    token_storage_latency_seconds = MockMetric()

try:
    active_tokens_gauge = Gauge(
        'lukhas_active_tokens_total',
        'Number of active tokens',
        ['component', 'realm']
    )
except ValueError:
    active_tokens_gauge = MockMetric()

try:
    revoked_tokens_gauge = Gauge(
        'lukhas_revoked_tokens_total',
        'Number of revoked tokens',
        ['component', 'realm']
    )
except ValueError:
    revoked_tokens_gauge = MockMetric()


class TokenStatus(Enum):
    """Token lifecycle status."""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING = "pending"


@dataclass
class StoredToken:
    """
    Token storage record with metadata.

    Comprehensive token information for lifecycle management.
    """
    jti: str  # JWT ID (primary key)
    alias: str  # ΛiD alias
    kid: str  # Key ID used for signing
    iat: int  # Issued at timestamp
    exp: int  # Expiration timestamp
    realm: str
    zone: str
    status: TokenStatus = TokenStatus.ACTIVE

    # Revocation metadata
    revoked_at: Optional[int] = None
    revoked_by: Optional[str] = None
    revoked_reason: Optional[str] = None

    # Audit metadata
    created_at: int = None
    last_validated: Optional[int] = None
    validation_count: int = 0

    def __post_init__(self):
        """Initialize creation timestamp."""
        if self.created_at is None:
            self.created_at = int(time.time())

    @property
    def is_active(self) -> bool:
        """Check if token is currently active."""
        now = int(time.time())
        return (
            self.status == TokenStatus.ACTIVE and
            self.exp > now
        )

    @property
    def is_expired(self) -> bool:
        """Check if token has expired."""
        return int(time.time()) >= self.exp

    @property
    def is_revoked(self) -> bool:
        """Check if token has been revoked."""
        return self.status == TokenStatus.REVOKED


@dataclass
class KeyRotationRecord:
    """
    Key rotation history record.

    Tracks key lifecycle for security audit and rotation management.
    """
    kid: str
    created_at: int
    activated_at: Optional[int] = None
    deactivated_at: Optional[int] = None
    rotation_reason: str = "scheduled"
    predecessor_kid: Optional[str] = None
    successor_kid: Optional[str] = None

    @property
    def is_active(self) -> bool:
        """Check if key is currently active."""
        return (
            self.activated_at is not None and
            self.deactivated_at is None
        )

    @property
    def age_hours(self) -> float:
        """Get key age in hours."""
        return (time.time() - self.created_at) / 3600


class TokenStorage:
    """
    Secure token storage with rotation history and revocation support.

    Provides comprehensive token lifecycle management with Guardian integration
    and performance optimization for enterprise-scale deployment.
    """

    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize token storage.

        Args:
            storage_path: Optional file system storage path (default: in-memory)
        """
        self.storage_path = storage_path
        self._component_id = "TokenStorage"

        # In-memory storage (production should use persistent storage)
        self._tokens: Dict[str, StoredToken] = {}
        self._key_rotation_history: List[KeyRotationRecord] = []
        self._revocation_blacklist: Set[str] = set()

        # Performance tracking
        self._cache_hits = 0
        self._cache_misses = 0

        # Load from persistent storage if configured
        if self.storage_path:
            self._load_from_storage()

    def store_token(
        self,
        jti: str,
        alias: str,
        kid: str,
        iat: int,
        exp: int,
        realm: str,
        zone: str
    ) -> StoredToken:
        """
        Store new token record.

        Args:
            jti: JWT ID (unique identifier)
            alias: ΛiD alias
            kid: Key ID used for signing
            iat: Issued at timestamp
            exp: Expiration timestamp
            realm: Security realm
            zone: Zone within realm

        Returns:
            Created token storage record
        """
        start_time = time.time()

        with tracer.start_as_current_span("token_storage_store") as span:
            span.set_attribute("component", self._component_id)
            span.set_attribute("jti", jti)
            span.set_attribute("realm", realm)
            span.set_attribute("zone", zone)

            try:
                # Create storage record
                stored_token = StoredToken(
                    jti=jti,
                    alias=alias,
                    kid=kid,
                    iat=iat,
                    exp=exp,
                    realm=realm,
                    zone=zone
                )

                # Store in memory
                self._tokens[jti] = stored_token

                # Persist if configured
                if self.storage_path:
                    self._persist_to_storage()

                # Update metrics
                token_storage_operations_total.labels(
                    component=self._component_id,
                    operation="store",
                    status="success"
                ).inc()

                active_tokens_gauge.labels(
                    component=self._component_id,
                    realm=realm
                ).inc()

                processing_time = time.time() - start_time
                token_storage_latency_seconds.labels(
                    component=self._component_id,
                    operation="store"
                ).observe(processing_time)

                span.set_attribute("processing_time_ms", processing_time * 1000)

                return stored_token

            except Exception as e:
                token_storage_operations_total.labels(
                    component=self._component_id,
                    operation="store",
                    status="error"
                ).inc()

                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise

    def get_token(self, jti: str) -> Optional[StoredToken]:
        """
        Retrieve token by JWT ID.

        Args:
            jti: JWT ID to lookup

        Returns:
            Token record if found, None otherwise
        """
        start_time = time.time()

        with tracer.start_as_current_span("token_storage_get") as span:
            span.set_attribute("component", self._component_id)
            span.set_attribute("jti", jti)

            try:
                token = self._tokens.get(jti)

                if token:
                    self._cache_hits += 1
                    # Update last validated timestamp
                    token.last_validated = int(time.time())
                    token.validation_count += 1

                    span.set_attribute("cache_hit", True)
                    span.set_attribute("token_status", token.status.value)
                else:
                    self._cache_misses += 1
                    span.set_attribute("cache_hit", False)

                # Update metrics
                token_storage_operations_total.labels(
                    component=self._component_id,
                    operation="get",
                    status="success" if token else "not_found"
                ).inc()

                processing_time = time.time() - start_time
                token_storage_latency_seconds.labels(
                    component=self._component_id,
                    operation="get"
                ).observe(processing_time)

                return token

            except Exception as e:
                token_storage_operations_total.labels(
                    component=self._component_id,
                    operation="get",
                    status="error"
                ).inc()

                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise

    def revoke_token(
        self,
        jti: str,
        revoked_by: str,
        reason: str = "user_request"
    ) -> bool:
        """
        Revoke token by JWT ID.

        Args:
            jti: JWT ID to revoke
            revoked_by: Entity that initiated revocation
            reason: Reason for revocation

        Returns:
            True if token was revoked, False if not found
        """
        start_time = time.time()

        with tracer.start_as_current_span("token_storage_revoke") as span:
            span.set_attribute("component", self._component_id)
            span.set_attribute("jti", jti)
            span.set_attribute("revoked_by", revoked_by)
            span.set_attribute("reason", reason)

            try:
                token = self._tokens.get(jti)
                if not token:
                    return False

                # Update token status
                token.status = TokenStatus.REVOKED
                token.revoked_at = int(time.time())
                token.revoked_by = revoked_by
                token.revoked_reason = reason

                # Add to revocation blacklist
                self._revocation_blacklist.add(jti)

                # Persist if configured
                if self.storage_path:
                    self._persist_to_storage()

                # Update metrics
                token_storage_operations_total.labels(
                    component=self._component_id,
                    operation="revoke",
                    status="success"
                ).inc()

                active_tokens_gauge.labels(
                    component=self._component_id,
                    realm=token.realm
                ).dec()

                revoked_tokens_gauge.labels(
                    component=self._component_id,
                    realm=token.realm
                ).inc()

                processing_time = time.time() - start_time
                token_storage_latency_seconds.labels(
                    component=self._component_id,
                    operation="revoke"
                ).observe(processing_time)

                span.set_attribute("processing_time_ms", processing_time * 1000)

                return True

            except Exception as e:
                token_storage_operations_total.labels(
                    component=self._component_id,
                    operation="revoke",
                    status="error"
                ).inc()

                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise

    def is_revoked(self, jti: str) -> bool:
        """
        Check if token is revoked (fast blacklist lookup).

        Args:
            jti: JWT ID to check

        Returns:
            True if token is revoked
        """
        return jti in self._revocation_blacklist

    def record_key_rotation(
        self,
        old_kid: str,
        new_kid: str,
        reason: str = "scheduled"
    ) -> KeyRotationRecord:
        """
        Record key rotation event.

        Args:
            old_kid: Previous key ID
            new_kid: New key ID
            reason: Reason for rotation

        Returns:
            Key rotation record
        """
        now = int(time.time())

        # Deactivate old key
        for record in self._key_rotation_history:
            if record.kid == old_kid and record.is_active:
                record.deactivated_at = now
                record.successor_kid = new_kid
                break

        # Create new key record
        new_record = KeyRotationRecord(
            kid=new_kid,
            created_at=now,
            activated_at=now,
            rotation_reason=reason,
            predecessor_kid=old_kid
        )

        self._key_rotation_history.append(new_record)

        # Persist if configured
        if self.storage_path:
            self._persist_to_storage()

        return new_record

    def cleanup_expired_tokens(self, batch_size: int = 1000) -> int:
        """
        Remove expired tokens from storage.

        Args:
            batch_size: Maximum tokens to process in single batch

        Returns:
            Number of tokens removed
        """
        start_time = time.time()

        with tracer.start_as_current_span("token_storage_cleanup") as span:
            span.set_attribute("component", self._component_id)
            span.set_attribute("batch_size", batch_size)

            now = int(time.time())
            expired_tokens = []
            processed = 0

            # Find expired tokens
            for jti, token in self._tokens.items():
                if processed >= batch_size:
                    break

                if token.exp <= now and token.status != TokenStatus.REVOKED:
                    expired_tokens.append(jti)
                    token.status = TokenStatus.EXPIRED

                processed += 1

            # Remove expired tokens
            for jti in expired_tokens:
                if jti in self._tokens:
                    del self._tokens[jti]

                if jti in self._revocation_blacklist:
                    self._revocation_blacklist.remove(jti)

            # Persist if configured
            if self.storage_path and expired_tokens:
                self._persist_to_storage()

            processing_time = time.time() - start_time
            span.set_attribute("tokens_removed", len(expired_tokens))
            span.set_attribute("processing_time_ms", processing_time * 1000)

            return len(expired_tokens)

    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics and health metrics.

        Returns:
            Storage statistics dictionary
        """
        now = int(time.time())

        active_count = sum(1 for t in self._tokens.values() if t.is_active)
        expired_count = sum(1 for t in self._tokens.values() if t.is_expired)
        revoked_count = sum(1 for t in self._tokens.values() if t.is_revoked)

        cache_total = self._cache_hits + self._cache_misses
        cache_hit_rate = self._cache_hits / cache_total if cache_total > 0 else 0.0

        return {
            "total_tokens": len(self._tokens),
            "active_tokens": active_count,
            "expired_tokens": expired_count,
            "revoked_tokens": revoked_count,
            "revocation_blacklist_size": len(self._revocation_blacklist),
            "key_rotation_history": len(self._key_rotation_history),
            "cache_hit_rate": cache_hit_rate,
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "storage_path": self.storage_path,
            "timestamp": now
        }

    def _load_from_storage(self) -> None:
        """Load data from persistent storage."""
        if not os.path.exists(self.storage_path):
            return

        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)

            # Load tokens
            for token_data in data.get("tokens", []):
                token = StoredToken(**token_data)
                self._tokens[token.jti] = token

                if token.is_revoked:
                    self._revocation_blacklist.add(token.jti)

            # Load key rotation history
            for rotation_data in data.get("key_rotations", []):
                rotation = KeyRotationRecord(**rotation_data)
                self._key_rotation_history.append(rotation)

        except Exception as e:
            # Log error but don't fail startup
            pass

    def _persist_to_storage(self) -> None:
        """Persist data to storage."""
        if not self.storage_path:
            return

        data = {
            "tokens": [asdict(token) for token in self._tokens.values()],
            "key_rotations": [asdict(rotation) for rotation in self._key_rotation_history],
            "timestamp": int(time.time())
        }

        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            # Log error but don't fail operation
            pass


# Export public interface
__all__ = [
    "TokenStorage",
    "StoredToken",
    "KeyRotationRecord",
    "TokenStatus"
]