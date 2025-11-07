#!/usr/bin/env python3
"""
LUKHAS I.5 Multi-Tenant Identity System - Production Schema v1.0.0

Implements secure multi-tenant identity management with namespace isolation,
tenant lifecycle management, and integrated ΛiD Token System support.

Features:
- Secure tenant isolation with namespace-scoped identities
- Hierarchical tenant management (enterprise/org/team levels)
- Integration with I.1 ΛiD Token System and I.2 Tiered Authentication
- Guardian-based tenant governance and compliance
- Cross-tenant access controls and audit trails

Constellation Framework: Identity ⚛️ + Guardian 🛡️ + Memory 🗃️ coordination.
"""

from __future__ import annotations

import hashlib
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List
from uuid import uuid4

from opentelemetry import trace

from .tier_system import TierLevel
from .token_generator import TokenGenerator
from .token_validator import TokenValidator, ValidationContext, ValidationResult

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)


class TenantStatus(Enum):
    """Tenant lifecycle status."""
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"
    DELETED = "deleted"


class TenantType(Enum):
    """Tenant organization type."""
    ENTERPRISE = "enterprise"      # Top-level organizational tenant
    ORGANIZATION = "organization"  # Department/division level
    TEAM = "team"                 # Project/team level
    INDIVIDUAL = "individual"      # Personal tenant


class TenantPlan(Enum):
    """Tenant service plan levels."""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


@dataclass
class TenantQuotas:
    """Tenant resource quotas and limits."""
    max_users: int = 50
    max_identities_per_user: int = 10
    max_tier_level: TierLevel = TierLevel.ELEVATED
    max_tokens_per_hour: int = 1000
    max_storage_mb: int = 1024
    max_api_calls_per_day: int = 10000
    custom_domains_enabled: bool = False
    advanced_auth_enabled: bool = True
    guardian_monitoring_enabled: bool = True


@dataclass
class TenantSecurityPolicy:
    """Tenant-specific security policies."""
    enforce_mfa: bool = True
    min_tier_level: TierLevel = TierLevel.PUBLIC
    max_session_duration_hours: int = 8
    require_fresh_auth_minutes: int = 60
    allowed_ip_ranges: list[str] = field(default_factory=list)
    blocked_ip_ranges: list[str] = field(default_factory=list)
    password_policy: dict[str, Any] = field(default_factory=dict)
    audit_all_actions: bool = True
    cross_tenant_access_enabled: bool = False


@dataclass
class TenantMetadata:
    """Tenant metadata and configuration."""
    # Basic tenant information
    tenant_id: str
    name: str
    display_name: str
    description: str = ""

    # Organizational structure
    tenant_type: TenantType = TenantType.ORGANIZATION
    parent_tenant_id: str | None = None
    root_tenant_id: str | None = None

    # Status and lifecycle
    status: TenantStatus = TenantStatus.PENDING
    plan: TenantPlan = TenantPlan.STARTER
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime | None = None

    # Configuration
    namespace: str = ""  # Auto-generated from tenant_id if empty
    domain: str | None = None
    custom_claims: dict[str, Any] = field(default_factory=dict)
    tags: dict[str, str] = field(default_factory=dict)

    # Resource management
    quotas: TenantQuotas = field(default_factory=TenantQuotas)
    security_policy: TenantSecurityPolicy = field(default_factory=TenantSecurityPolicy)

    # Audit and compliance
    created_by: str | None = None
    compliance_flags: dict[str, bool] = field(default_factory=dict)
    audit_retention_days: int = 90

    def __post_init__(self):
        """Initialize computed fields."""
        if not self.namespace:
            self.namespace = self._generate_namespace()
        if not self.root_tenant_id:
            self.root_tenant_id = self.tenant_id if not self.parent_tenant_id else None

    def _generate_namespace(self) -> str:
        """Generate secure namespace from tenant ID."""
        # Use first 8 characters of tenant ID + CRC32 for collision resistance
        tenant_hash = hashlib.sha256(self.tenant_id.encode()).hexdigest()[:8]
        return f"tenant_{tenant_hash}"


@dataclass
class TenantUser:
    """User within a specific tenant context."""
    user_id: str
    tenant_id: str
    username: str
    email: str
    roles: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    max_tier_level: TierLevel = TierLevel.ELEVATED
    status: str = "active"
    last_login: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)


class TenantManager:
    """
    Multi-tenant identity management system.

    Provides secure tenant isolation, lifecycle management, and integration
    with the LUKHAS Constellation Framework.
    """

    def __init__(
        self,
        token_generator: TokenGenerator | None = None,
        token_validator: TokenValidator | None = None,
        guardian: Any | None = None,
        storage_provider: Callable | None = None
    ):
        self.token_generator = token_generator
        self.token_validator = token_validator
        self.guardian = guardian
        self.storage_provider = storage_provider or self._default_storage

        # In-memory storage for demo (replace with persistent storage)
        self._tenants: dict[str, TenantMetadata] = {}
        self._tenant_users: dict[str, list[TenantUser]] = {}
        self._tenant_index: dict[str, str] = {}  # namespace -> tenant_id mapping

        self.logger = logging.getLogger(f"{__name__}.TenantManager")
        self.logger.info("TenantManager initialized with multi-tenant isolation")

    async def create_tenant(
        self,
        name: str,
        display_name: str,
        tenant_type: TenantType = TenantType.ORGANIZATION,
        parent_tenant_id: str | None = None,
        creator_user_id: str | None = None,
        **kwargs
    ) -> TenantMetadata:
        """
        Create a new tenant with secure namespace isolation.

        Args:
            name: Unique tenant name (lowercase, alphanumeric + hyphens)
            display_name: Human-readable tenant name
            tenant_type: Type of tenant (enterprise/org/team/individual)
            parent_tenant_id: Parent tenant for hierarchical organization
            creator_user_id: User creating the tenant
            **kwargs: Additional tenant configuration

        Returns:
            Created tenant metadata

        Raises:
            ValueError: If tenant name conflicts or parent doesn't exist
        """
        with tracer.start_as_current_span("create_tenant") as span:
            span.set_attribute("tenant_name", name)
            span.set_attribute("tenant_type", tenant_type.value)

            # Validate tenant name uniqueness
            if name in self._tenant_index:
                raise ValueError(f"Tenant name '{name}' already exists")

            # Validate parent tenant if specified
            if parent_tenant_id and parent_tenant_id not in self._tenants:
                raise ValueError(f"Parent tenant '{parent_tenant_id}' not found")

            # Generate secure tenant ID
            tenant_id = f"tenant_{uuid4().hex[:16]}"

            # Determine root tenant
            root_tenant_id = tenant_id
            if parent_tenant_id:
                parent = self._tenants[parent_tenant_id]
                root_tenant_id = parent.root_tenant_id or parent.tenant_id

            # Create tenant metadata
            tenant = TenantMetadata(
                tenant_id=tenant_id,
                name=name,
                display_name=display_name,
                tenant_type=tenant_type,
                parent_tenant_id=parent_tenant_id,
                root_tenant_id=root_tenant_id,
                created_by=creator_user_id,
                **kwargs
            )

            # Guardian pre-validation
            if self.guardian:
                await self._guardian_validate_tenant_creation(tenant)

            # Store tenant
            self._tenants[tenant_id] = tenant
            self._tenant_index[name] = tenant_id
            self._tenant_index[tenant.namespace] = tenant_id
            self._tenant_users[tenant_id] = []

            # Guardian post-monitoring
            if self.guardian:
                await self._guardian_monitor_tenant_event("tenant_created", tenant)

            span.set_attribute("tenant_id", tenant_id)
            span.set_attribute("namespace", tenant.namespace)

            self.logger.info(
                f"Tenant created successfully: {name} (id={tenant_id}, ns={tenant.namespace}, parent={parent_tenant_id})"
            )

            return tenant

    async def get_tenant(self, tenant_identifier: str) -> TenantMetadata | None:
        """
        Retrieve tenant by ID, name, or namespace.

        Args:
            tenant_identifier: Tenant ID, name, or namespace

        Returns:
            Tenant metadata if found, None otherwise
        """
        # Direct tenant ID lookup
        if tenant_identifier in self._tenants:
            return self._tenants[tenant_identifier]

        # Name/namespace lookup via index
        if tenant_identifier in self._tenant_index:
            tenant_id = self._tenant_index[tenant_identifier]
            return self._tenants.get(tenant_id)

        return None

    async def update_tenant(
        self,
        tenant_id: str,
        updates: dict[str, Any],
        updater_user_id: str | None = None
    ) -> TenantMetadata:
        """
        Update tenant configuration.

        Args:
            tenant_id: Tenant to update
            updates: Fields to update
            updater_user_id: User making the update

        Returns:
            Updated tenant metadata

        Raises:
            ValueError: If tenant not found or update invalid
        """
        tenant = await self.get_tenant(tenant_id)
        if not tenant:
            raise ValueError(f"Tenant '{tenant_id}' not found")

        # Guardian pre-validation
        if self.guardian:
            await self._guardian_validate_tenant_update(tenant, updates, updater_user_id)

        # Apply updates (with validation)
        for attr, value in updates.items():
            if hasattr(tenant, attr):
                setattr(tenant, attr, value)

        tenant.updated_at = datetime.now(timezone.utc)

        # Guardian post-monitoring
        if self.guardian:
            await self._guardian_monitor_tenant_event("tenant_updated", tenant)

        self.logger.info(
            f"Tenant updated successfully: {tenant_id} (updates={list(updates.keys())}, updater={updater_user_id})"
        )

        return tenant

    async def generate_tenant_token(
        self,
        tenant_id: str,
        user_id: str,
        tier_level: TierLevel = TierLevel.AUTHENTICATED,
        custom_claims: dict[str, Any] | None = None,
        expires_in_seconds: int = 3600
    ) -> str:
        """
        Generate ΛiD token scoped to specific tenant.

        Args:
            tenant_id: Target tenant
            user_id: User within tenant
            tier_level: Authentication tier level
            custom_claims: Additional token claims
            expires_in_seconds: Token expiration (default 1 hour)

        Returns:
            Signed JWT token with tenant namespace

        Raises:
            ValueError: If tenant not found or user not authorized
        """
        with tracer.start_as_current_span("generate_tenant_token") as span:
            tenant = await self.get_tenant(tenant_id)
            if not tenant:
                raise ValueError(f"Tenant '{tenant_id}' not found")

            # Validate user access to tenant
            user = await self.get_tenant_user(tenant_id, user_id)
            if not user:
                raise ValueError(f"User '{user_id}' not found in tenant '{tenant_id}'")

            # Enforce tenant quotas
            if tier_level.value > tenant.quotas.max_tier_level.value:
                tier_level = tenant.quotas.max_tier_level

            if not self.token_generator:
                raise ValueError("Token generator not available")

            # Build tenant-scoped claims using direct dictionary approach
            # (TokenClaims requires too many mandatory fields for this use case)

            # Build token claims
            token_claims = {
                "aud": "lukhas-multi-tenant",
                "lukhas_tier": tier_level.value,
                "lukhas_namespace": tenant.namespace,
                "permissions": user.permissions.copy(),
                "tenant_id": tenant_id,
                "tenant_name": tenant.name,
                "tenant_type": tenant.tenant_type.value,
                "user_id": user_id,
                "username": user.username,
                "roles": user.roles,
                "exp": int(time.time()) + expires_in_seconds
            }

            if custom_claims:
                token_claims.update(custom_claims)

            # Guardian pre-validation
            if self.guardian:
                await self._guardian_validate_token_generation(tenant, user, token_claims)

            # Generate token
            response = self.token_generator.create(
                realm=tenant.namespace,
                zone=f"tenant_{tenant.tenant_type.value}",
                claims=token_claims
            )

            # Guardian post-monitoring
            if self.guardian:
                await self._guardian_monitor_tenant_event("token_generated", tenant, {
                    "user_id": user_id,
                    "tier_level": tier_level.value,
                    "expires_in": expires_in_seconds
                })

            span.set_attribute("tenant_id", tenant_id)
            span.set_attribute("user_id", user_id)
            span.set_attribute("tier_level", tier_level.value)
            span.set_attribute("namespace", tenant.namespace)

            self.logger.info(
                f"Tenant token generated successfully: tenant={tenant_id}, user={user_id}, tier={tier_level.value}, ns={tenant.namespace}"
            )

            return response.jwt

    async def validate_tenant_token(
        self,
        token: str,
        required_tenant: str | None = None,
        required_permissions: list[str] | None = None
    ) -> ValidationResult:
        """
        Validate tenant-scoped token with namespace verification.

        Args:
            token: JWT token to validate
            required_tenant: Required tenant ID/name/namespace
            required_permissions: Required permissions

        Returns:
            Validation result with tenant context
        """
        if not self.token_validator:
            raise ValueError("Token validator not available")

        # Basic token validation
        context = ValidationContext(
            guardian_enabled=self.guardian is not None,
            ethical_validation_enabled=True
        )

        result = self.token_validator.verify(token, context)

        if not result.valid:
            return result

        # Extract tenant information from claims
        claims = result.claims or {}
        token_namespace = claims.get("lukhas_namespace")
        token_tenant_id = claims.get("tenant_id")
        token_permissions = claims.get("permissions", [])

        # Validate tenant scope if required
        if required_tenant:
            tenant = await self.get_tenant(required_tenant)
            if not tenant:
                result.valid = False
                result.error_code = "tenant_not_found"
                result.error_message = f"Required tenant '{required_tenant}' not found"
                return result

            # Check if token is scoped to the required tenant
            if (token_tenant_id != tenant.tenant_id and
                token_namespace != tenant.namespace):
                result.valid = False
                result.error_code = "tenant_mismatch"
                result.error_message = f"Token not scoped to tenant '{required_tenant}'"
                return result

        # Validate permissions if required
        if required_permissions:
            missing_permissions = set(required_permissions) - set(token_permissions)
            if missing_permissions:
                result.valid = False
                result.error_code = "insufficient_permissions"
                result.error_message = f"Missing permissions: {list(missing_permissions)}"
                return result

        # Guardian validation
        if self.guardian and token_tenant_id:
            tenant = await self.get_tenant(token_tenant_id)
            if tenant:
                await self._guardian_validate_token_access(tenant, claims)

        self.logger.debug(
            f"Tenant token validated successfully: tenant={token_tenant_id}, ns={token_namespace}, perms={len(token_permissions)}"
        )

        return result

    async def add_tenant_user(
        self,
        tenant_id: str,
        user_id: str,
        username: str,
        email: str,
        roles: list[str] | None = None,
        permissions: list[str] | None = None,
        max_tier_level: TierLevel = TierLevel.ELEVATED
    ) -> TenantUser:
        """
        Add user to tenant with specified roles and permissions.

        Args:
            tenant_id: Target tenant
            user_id: Unique user identifier
            username: Username within tenant
            email: User email address
            roles: User roles within tenant
            permissions: User permissions within tenant
            max_tier_level: Maximum authentication tier for user

        Returns:
            Created tenant user

        Raises:
            ValueError: If tenant not found or user already exists
        """
        tenant = await self.get_tenant(tenant_id)
        if not tenant:
            raise ValueError(f"Tenant '{tenant_id}' not found")

        # Check if user already exists in tenant
        existing_user = await self.get_tenant_user(tenant_id, user_id)
        if existing_user:
            raise ValueError(f"User '{user_id}' already exists in tenant '{tenant_id}'")

        # Enforce tenant quotas
        current_users = len(self._tenant_users.get(tenant_id, []))
        if current_users >= tenant.quotas.max_users:
            raise ValueError(f"Tenant user limit ({tenant.quotas.max_users}) exceeded")

        # Enforce tenant security policy
        if max_tier_level.value > tenant.quotas.max_tier_level.value:
            max_tier_level = tenant.quotas.max_tier_level

        user = TenantUser(
            user_id=user_id,
            tenant_id=tenant_id,
            username=username,
            email=email,
            roles=roles or [],
            permissions=permissions or [],
            max_tier_level=max_tier_level
        )

        # Guardian validation
        if self.guardian:
            await self._guardian_validate_user_addition(tenant, user)

        # Add user to tenant
        if tenant_id not in self._tenant_users:
            self._tenant_users[tenant_id] = []
        self._tenant_users[tenant_id].append(user)

        # Guardian monitoring
        if self.guardian:
            await self._guardian_monitor_tenant_event("user_added", tenant, {
                "user_id": user_id,
                "username": username,
                "roles": roles,
                "max_tier_level": max_tier_level.value
            })

        self.logger.info(
            f"User added to tenant successfully: {username} (user={user_id}, tenant={tenant_id}, tier={max_tier_level.value})"
        )

        return user

    async def get_tenant_user(
        self,
        tenant_id: str,
        user_id: str
    ) -> TenantUser | None:
        """
        Retrieve user within specific tenant context.

        Args:
            tenant_id: Tenant to search in
            user_id: User to find

        Returns:
            Tenant user if found, None otherwise
        """
        users = self._tenant_users.get(tenant_id, [])
        for user in users:
            if user.user_id == user_id:
                return user
        return None

    async def list_tenant_users(
        self,
        tenant_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> list[TenantUser]:
        """
        List users in tenant with pagination.

        Args:
            tenant_id: Tenant to list users from
            limit: Maximum users to return
            offset: Number of users to skip

        Returns:
            List of tenant users
        """
        users = self._tenant_users.get(tenant_id, [])
        return users[offset:offset + limit]

    async def get_user_tenants(self, user_id: str) -> list[TenantMetadata]:
        """
        Get all tenants a user belongs to.

        Args:
            user_id: User to search for

        Returns:
            List of tenant metadata for tenants user belongs to
        """
        user_tenants = []

        for tenant_id, users in self._tenant_users.items():
            for user in users:
                if user.user_id == user_id:
                    tenant = self._tenants.get(tenant_id)
                    if tenant:
                        user_tenants.append(tenant)
                    break

        return user_tenants

    # Guardian integration methods
    async def _guardian_validate_tenant_creation(self, tenant: TenantMetadata) -> None:
        """Guardian validation for tenant creation."""
        if self.guardian:
            await self.guardian.validate_action_async("create_tenant", {
                "tenant_id": tenant.tenant_id,
                "name": tenant.name,
                "tenant_type": tenant.tenant_type.value,
                "parent_tenant_id": tenant.parent_tenant_id
            })

    async def _guardian_validate_tenant_update(
        self,
        tenant: TenantMetadata,
        updates: dict[str, Any],
        updater_user_id: str | None
    ) -> None:
        """Guardian validation for tenant updates."""
        if self.guardian:
            await self.guardian.validate_action_async("update_tenant", {
                "tenant_id": tenant.tenant_id,
                "updates": list(updates.keys()),
                "updater": updater_user_id
            })

    async def _guardian_validate_token_generation(
        self,
        tenant: TenantMetadata,
        user: TenantUser,
        claims: dict[str, Any]
    ) -> None:
        """Guardian validation for token generation."""
        if self.guardian:
            await self.guardian.validate_action_async("generate_tenant_token", {
                "tenant_id": tenant.tenant_id,
                "user_id": user.user_id,
                "tier_level": claims.get("lukhas_tier"),
                "permissions": claims.get("permissions", [])
            })

    async def _guardian_validate_token_access(
        self,
        tenant: TenantMetadata,
        claims: dict[str, Any]
    ) -> None:
        """Guardian validation for token access."""
        if self.guardian:
            await self.guardian.validate_action_async("validate_tenant_token", {
                "tenant_id": tenant.tenant_id,
                "namespace": tenant.namespace,
                "user_id": claims.get("user_id"),
                "permissions": claims.get("permissions", [])
            })

    async def _guardian_validate_user_addition(
        self,
        tenant: TenantMetadata,
        user: TenantUser
    ) -> None:
        """Guardian validation for adding user to tenant."""
        if self.guardian:
            await self.guardian.validate_action_async("add_tenant_user", {
                "tenant_id": tenant.tenant_id,
                "user_id": user.user_id,
                "roles": user.roles,
                "max_tier_level": user.max_tier_level.value
            })

    async def _guardian_monitor_tenant_event(
        self,
        event: str,
        tenant: TenantMetadata,
        context: dict[str, Any] | None = None
    ) -> None:
        """Guardian monitoring for tenant events."""
        if self.guardian:
            monitor_data = {
                "event": event,
                "tenant_id": tenant.tenant_id,
                "namespace": tenant.namespace,
                "tenant_type": tenant.tenant_type.value,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            if context:
                monitor_data.update(context)

            await self.guardian.monitor_behavior_async(monitor_data)

    def _default_storage(self, operation: str, data: Any) -> Any:
        """Default in-memory storage provider."""
        # In production, replace with persistent storage (PostgreSQL, etc.)
        self.logger.warning("Using in-memory storage - not suitable for production")
        return data


# Export main classes
__all__ = [
    "TenantManager",
    "TenantMetadata",
    "TenantPlan",
    "TenantQuotas",
    "TenantSecurityPolicy",
    "TenantStatus",
    "TenantType",
    "TenantUser"
]
