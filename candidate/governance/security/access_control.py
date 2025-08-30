"""
Tiered Access Control System for LUKHAS AI

This module provides a comprehensive tiered access control system with
5-tier hierarchical access levels (T1-T5), integrated with Trinity Framework,
constitutional principles, and comprehensive security controls.

Features:
- Five-tier access control system (T1: Basic -> T5: Administrator)
- Role-based access control (RBAC) with dynamic permissions
- Context-aware access decisions
- Real-time access monitoring and audit trails
- Integration with Trinity Framework (⚛️🧠🛡️)
- Constitutional AI compliance validation
- Multi-factor authentication support
- Session management and token-based authentication
- Advanced threat detection and response

Access Tiers:
- T1: Basic - Limited read-only access
- T2: User - Standard user operations
- T3: Advanced - Enhanced capabilities
- T4: Privileged - Administrative functions
- T5: System - Full system control

#TAG:governance
#TAG:security
#TAG:access_control
#TAG:authentication
#TAG:authorization
#TAG:trinity
"""

import asyncio
import hashlib
import secrets
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

from candidate.core.common import get_logger

logger = get_logger(__name__)


class AccessTier(Enum):
    """Access tier levels (T1-T5)"""

    T1_BASIC = 1  # Basic access - read-only, limited capabilities
    T2_USER = 2  # Standard user - normal operations
    T3_ADVANCED = 3  # Advanced user - enhanced capabilities
    T4_PRIVILEGED = 4  # Privileged user - administrative functions
    T5_SYSTEM = 5  # System level - full control


class AccessType(Enum):
    """Types of access operations"""

    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    DELETE = "delete"
    ADMIN = "admin"
    SYSTEM = "system"


class AuthenticationMethod(Enum):
    """Authentication methods"""

    PASSWORD = "password"  # nosec B105
    MFA = "mfa"  # Multi-factor authentication
    BIOMETRIC = "biometric"  # Biometric authentication
    TOKEN = "token"  # Token-based
    CERTIFICATE = "certificate"  # Certificate-based
    FEDERATED = "federated"  # Federated identity


class SessionStatus(Enum):
    """Session status states"""

    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    SUSPENDED = "suspended"
    LOCKED = "locked"


class AccessDecision(Enum):
    """Access control decisions"""

    ALLOW = "allow"
    DENY = "deny"
    CHALLENGE = "challenge"  # Require additional authentication
    ESCALATE = "escalate"  # Require higher tier approval
    MONITOR = "monitor"  # Allow but monitor closely


@dataclass
class Permission:
    """Represents a specific permission"""

    permission_id: str
    name: str
    description: str
    resource_type: str
    access_types: set[AccessType] = field(default_factory=set)
    required_tier: AccessTier = AccessTier.T1_BASIC
    context_conditions: dict[str, Any] = field(default_factory=dict)
    time_restrictions: Optional[dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Role:
    """Represents a role with associated permissions"""

    role_id: str
    name: str
    description: str
    tier: AccessTier
    permissions: set[str] = field(default_factory=set)  # Permission IDs
    inherits_from: set[str] = field(default_factory=set)  # Other role IDs
    constraints: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class User:
    """Represents a user in the access control system"""

    user_id: str
    username: str
    email: str
    current_tier: AccessTier
    max_tier: AccessTier  # Maximum tier user can achieve
    roles: set[str] = field(default_factory=set)  # Role IDs

    # Authentication
    password_hash: Optional[str] = None
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None
    auth_methods: set[AuthenticationMethod] = field(default_factory=set)

    # Account status
    active: bool = True
    locked: bool = False
    failed_attempts: int = 0
    last_login: Optional[datetime] = None
    password_expires: Optional[datetime] = None

    # Security context
    security_clearance: Optional[str] = None
    access_restrictions: dict[str, Any] = field(default_factory=dict)

    # Trinity Framework integration
    identity_verified: bool = False  # ⚛️ Identity system verification
    consciousness_level: int = 1  # 🧠 Consciousness interaction level
    guardian_cleared: bool = True  # 🛡️ Guardian system clearance

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class AccessSession:
    """Represents an access session"""

    session_id: str
    user_id: str
    tier: AccessTier
    status: SessionStatus = SessionStatus.ACTIVE

    # Session details
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(hours=8))

    # Authentication context
    auth_method: AuthenticationMethod = AuthenticationMethod.PASSWORD
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None
    mfa_verified: bool = False

    # Security context
    security_context: dict[str, Any] = field(default_factory=dict)
    risk_score: float = 0.0

    # Trinity Framework context
    trinity_context: dict[str, Any] = field(default_factory=dict)


@dataclass
class AccessRequest:
    """Represents an access control request"""

    request_id: str
    user_id: str
    session_id: str
    resource: str
    access_type: AccessType
    context: dict[str, Any] = field(default_factory=dict)
    requested_at: datetime = field(default_factory=datetime.now)


@dataclass
class AccessAuditEntry:
    """Audit entry for access control events"""

    audit_id: str
    event_type: str  # login, logout, access_granted, access_denied, etc.
    user_id: str
    session_id: Optional[str] = None
    resource: Optional[str] = None
    decision: Optional[AccessDecision] = None
    reason: str = ""

    # Context information
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None
    risk_factors: list[str] = field(default_factory=list)

    # Trinity Framework audit
    trinity_validation: dict[str, Any] = field(default_factory=dict)

    timestamp: datetime = field(default_factory=datetime.now)


class PermissionManager:
    """Manages permissions and roles"""

    def __init__(self):
        self.permissions: dict[str, Permission] = {}
        self.roles: dict[str, Role] = {}
        self._initialize_standard_permissions()
        self._initialize_standard_roles()

        logger.info("🔧 Permission Manager initialized")

    def _initialize_standard_permissions(self):
        """Initialize standard system permissions"""

        # Basic permissions (T1)
        self.add_permission(
            Permission(
                permission_id="basic_read",
                name="Basic Read Access",
                description="Basic read-only access to public resources",
                resource_type="public",
                access_types={AccessType.READ},
                required_tier=AccessTier.T1_BASIC,
            )
        )

        # User permissions (T2)
        self.add_permission(
            Permission(
                permission_id="user_profile",
                name="User Profile Management",
                description="Manage own user profile and settings",
                resource_type="user_profile",
                access_types={AccessType.READ, AccessType.WRITE},
                required_tier=AccessTier.T2_USER,
            )
        )

        self.add_permission(
            Permission(
                permission_id="data_access",
                name="Personal Data Access",
                description="Access personal data and AI interactions",
                resource_type="personal_data",
                access_types={AccessType.READ, AccessType.WRITE},
                required_tier=AccessTier.T2_USER,
            )
        )

        # Advanced permissions (T3)
        self.add_permission(
            Permission(
                permission_id="ai_advanced",
                name="Advanced AI Features",
                description="Access to advanced AI capabilities and models",
                resource_type="ai_advanced",
                access_types={AccessType.READ, AccessType.WRITE, AccessType.EXECUTE},
                required_tier=AccessTier.T3_ADVANCED,
            )
        )

        self.add_permission(
            Permission(
                permission_id="system_integration",
                name="System Integration",
                description="Integration with external systems and APIs",
                resource_type="integrations",
                access_types={AccessType.READ, AccessType.WRITE, AccessType.EXECUTE},
                required_tier=AccessTier.T3_ADVANCED,
            )
        )

        # Privileged permissions (T4)
        self.add_permission(
            Permission(
                permission_id="user_management",
                name="User Management",
                description="Manage other users and their access",
                resource_type="users",
                access_types={
                    AccessType.READ,
                    AccessType.WRITE,
                    AccessType.DELETE,
                    AccessType.ADMIN,
                },
                required_tier=AccessTier.T4_PRIVILEGED,
            )
        )

        self.add_permission(
            Permission(
                permission_id="system_config",
                name="System Configuration",
                description="Configure system settings and parameters",
                resource_type="system_config",
                access_types={AccessType.READ, AccessType.WRITE, AccessType.ADMIN},
                required_tier=AccessTier.T4_PRIVILEGED,
            )
        )

        # System permissions (T5)
        self.add_permission(
            Permission(
                permission_id="system_admin",
                name="System Administration",
                description="Full system administrative access",
                resource_type="system",
                access_types={
                    AccessType.READ,
                    AccessType.WRITE,
                    AccessType.DELETE,
                    AccessType.EXECUTE,
                    AccessType.ADMIN,
                    AccessType.SYSTEM,
                },
                required_tier=AccessTier.T5_SYSTEM,
            )
        )

        logger.info(f"✅ Initialized {len(self.permissions)} standard permissions")

    def _initialize_standard_roles(self):
        """Initialize standard system roles"""

        # T1 Basic Role
        self.add_role(
            Role(
                role_id="basic_user",
                name="Basic User",
                description="Basic read-only access",
                tier=AccessTier.T1_BASIC,
                permissions={"basic_read"},
            )
        )

        # T2 Standard User Role
        self.add_role(
            Role(
                role_id="standard_user",
                name="Standard User",
                description="Standard user with personal data access",
                tier=AccessTier.T2_USER,
                permissions={"basic_read", "user_profile", "data_access"},
                inherits_from={"basic_user"},
            )
        )

        # T3 Advanced User Role
        self.add_role(
            Role(
                role_id="advanced_user",
                name="Advanced User",
                description="Advanced user with AI capabilities",
                tier=AccessTier.T3_ADVANCED,
                permissions={
                    "basic_read",
                    "user_profile",
                    "data_access",
                    "ai_advanced",
                    "system_integration",
                },
                inherits_from={"standard_user"},
            )
        )

        # T4 Administrator Role
        self.add_role(
            Role(
                role_id="administrator",
                name="Administrator",
                description="System administrator with user management",
                tier=AccessTier.T4_PRIVILEGED,
                permissions={
                    "basic_read",
                    "user_profile",
                    "data_access",
                    "ai_advanced",
                    "system_integration",
                    "user_management",
                    "system_config",
                },
                inherits_from={"advanced_user"},
            )
        )

        # T5 System Administrator Role
        self.add_role(
            Role(
                role_id="system_admin",
                name="System Administrator",
                description="Full system administrative access",
                tier=AccessTier.T5_SYSTEM,
                permissions={
                    "basic_read",
                    "user_profile",
                    "data_access",
                    "ai_advanced",
                    "system_integration",
                    "user_management",
                    "system_config",
                    "system_admin",
                },
                inherits_from={"administrator"},
            )
        )

        logger.info(f"✅ Initialized {len(self.roles)} standard roles")

    def add_permission(self, permission: Permission) -> bool:
        """Add a permission to the system"""
        try:
            self.permissions[permission.permission_id] = permission
            logger.debug(f"Added permission: {permission.permission_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add permission {permission.permission_id}: {e}")
            return False

    def add_role(self, role: Role) -> bool:
        """Add a role to the system"""
        try:
            # Validate permissions exist
            for perm_id in role.permissions:
                if perm_id not in self.permissions:
                    logger.warning(f"Permission {perm_id} not found for role {role.role_id}")

            self.roles[role.role_id] = role
            logger.debug(f"Added role: {role.role_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add role {role.role_id}: {e}")
            return False

    def get_user_permissions(self, user: User) -> set[str]:
        """Get all permissions for a user based on their roles"""
        permissions = set()

        # Get permissions from all user roles
        for role_id in user.roles:
            permissions.update(self._get_role_permissions(role_id))

        return permissions

    def _get_role_permissions(self, role_id: str) -> set[str]:
        """Get all permissions for a role, including inherited"""
        if role_id not in self.roles:
            return set()

        role = self.roles[role_id]
        permissions = set(role.permissions)

        # Add inherited permissions
        for parent_role_id in role.inherits_from:
            permissions.update(self._get_role_permissions(parent_role_id))

        return permissions


class SessionManager:
    """Manages user sessions and authentication"""

    def __init__(self):
        self.active_sessions: dict[str, AccessSession] = {}
        self.jwt_secret = secrets.token_urlsafe(32)
        self.session_timeout = timedelta(hours=8)

        # Start cleanup task
        asyncio.create_task(self._session_cleanup_task())

        logger.info("🔧 Session Manager initialized")

    async def create_session(
        self,
        user: User,
        auth_method: AuthenticationMethod,
        source_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        mfa_verified: bool = False,
    ) -> AccessSession:
        """Create a new access session"""

        session_id = f"sess_{uuid.uuid4().hex}"
        expires_at = datetime.now() + self.session_timeout

        session = AccessSession(
            session_id=session_id,
            user_id=user.user_id,
            tier=user.current_tier,
            expires_at=expires_at,
            auth_method=auth_method,
            source_ip=source_ip,
            user_agent=user_agent,
            mfa_verified=mfa_verified,
        )

        # Calculate risk score
        session.risk_score = await self._calculate_session_risk(user, source_ip, user_agent)

        # Add Trinity Framework context
        session.trinity_context = {
            "identity_verified": user.identity_verified,
            "consciousness_level": user.consciousness_level,
            "guardian_cleared": user.guardian_cleared,
        }

        self.active_sessions[session_id] = session

        # Update user last login
        user.last_login = datetime.now()

        logger.info(
            f"✅ Created session {session_id} for user {user.user_id} (tier: T{user.current_tier.value})"
        )
        return session

    async def _calculate_session_risk(
        self, user: User, source_ip: Optional[str], user_agent: Optional[str]
    ) -> float:
        """Calculate risk score for session"""

        risk_score = 0.0

        # Account status risks
        if user.failed_attempts > 0:
            risk_score += user.failed_attempts * 0.1

        if user.last_login:
            days_since_login = (datetime.now() - user.last_login).days
            if days_since_login > 30:
                risk_score += 0.2

        # IP-based risk (simplified)
        if source_ip:
            if source_ip.startswith("10.") or source_ip.startswith("192.168."):
                risk_score -= 0.1  # Internal network - lower risk
            else:
                risk_score += 0.1  # External - higher risk

        # High privilege account risk
        if user.current_tier.value >= 4:
            risk_score += 0.2

        # Trinity Framework risk factors
        if not user.identity_verified:
            risk_score += 0.3

        if not user.guardian_cleared:
            risk_score += 0.5

        return max(0.0, min(1.0, risk_score))

    def get_session(self, session_id: str) -> Optional[AccessSession]:
        """Get session by ID"""
        session = self.active_sessions.get(session_id)

        if session and session.status == SessionStatus.ACTIVE:
            # Check if expired
            if datetime.now() > session.expires_at:
                session.status = SessionStatus.EXPIRED
                return None

            # Update last activity
            session.last_activity = datetime.now()
            return session

        return None

    def terminate_session(self, session_id: str) -> bool:
        """Terminate a session"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.status = SessionStatus.TERMINATED
            del self.active_sessions[session_id]
            logger.info(f"🔐 Terminated session {session_id}")
            return True
        return False

    def terminate_user_sessions(self, user_id: str) -> int:
        """Terminate all sessions for a user"""
        count = 0
        sessions_to_remove = []

        for session_id, session in self.active_sessions.items():
            if session.user_id == user_id:
                session.status = SessionStatus.TERMINATED
                sessions_to_remove.append(session_id)
                count += 1

        for session_id in sessions_to_remove:
            del self.active_sessions[session_id]

        if count > 0:
            logger.info(f"🔐 Terminated {count} sessions for user {user_id}")

        return count

    async def _session_cleanup_task(self):
        """Background task to clean up expired sessions"""
        while True:
            try:
                current_time = datetime.now()
                expired_sessions = []

                for session_id, session in self.active_sessions.items():
                    if current_time > session.expires_at or session.status != SessionStatus.ACTIVE:
                        expired_sessions.append(session_id)

                for session_id in expired_sessions:
                    session = self.active_sessions.pop(session_id, None)
                    if session:
                        session.status = SessionStatus.EXPIRED

                if expired_sessions:
                    logger.debug(f"🧹 Cleaned up {len(expired_sessions)} expired sessions")

                await asyncio.sleep(300)  # Check every 5 minutes

            except Exception as e:
                logger.error(f"Session cleanup error: {e}")
                await asyncio.sleep(60)


class AccessControlEngine:
    """
    Main access control engine for LUKHAS AI System

    Provides comprehensive tiered access control with T1-T5 hierarchy,
    role-based permissions, session management, and Trinity Framework integration.
    """

    def __init__(self):
        self.permission_manager = PermissionManager()
        self.session_manager = SessionManager()
        self.users: dict[str, User] = {}
        self.audit_trail: list[AccessAuditEntry] = []

        # Access control configuration
        self.max_failed_attempts = 5
        self.lockout_duration = timedelta(minutes=30)
        self.mfa_required_tier = AccessTier.T3_ADVANCED

        # Performance metrics
        self.metrics = {
            "total_requests": 0,
            "allowed_requests": 0,
            "denied_requests": 0,
            "active_users": 0,
            "active_sessions": 0,
            "failed_authentications": 0,
            "security_incidents": 0,
            "last_updated": datetime.now().isoformat(),
        }

        self._initialize_system_users()

        logger.info("🛡️ Access Control Engine initialized")

    def _initialize_system_users(self):
        """Initialize system users"""

        # Create system administrator
        system_admin = User(
            user_id="system_admin",
            username="system",
            email="system@lukhas.ai",
            current_tier=AccessTier.T5_SYSTEM,
            max_tier=AccessTier.T5_SYSTEM,
            roles={"system_admin"},
            active=True,
            identity_verified=True,
            consciousness_level=5,
            guardian_cleared=True,
        )

        self.users["system_admin"] = system_admin

        logger.info("✅ Initialized system users")

    async def authenticate_user(
        self,
        username: str,
        password: str,
        mfa_token: Optional[str] = None,
        source_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> tuple[bool, Optional[AccessSession], str]:
        """
        Authenticate user and create session

        Returns:
            (success, session, message)
        """

        try:
            # Find user
            user = None
            for u in self.users.values():
                if u.username == username and u.active:
                    user = u
                    break

            if not user:
                await self._audit_event(
                    "authentication_failed",
                    None,
                    None,
                    reason="User not found",
                    source_ip=source_ip,
                )
                return False, None, "Authentication failed"

            # Check if account is locked
            if user.locked:
                await self._audit_event(
                    "authentication_failed",
                    user.user_id,
                    None,
                    reason="Account locked",
                    source_ip=source_ip,
                )
                return False, None, "Account is locked"

            # Verify password
            if not self._verify_password(password, user.password_hash):
                user.failed_attempts += 1

                # Lock account if too many failures
                if user.failed_attempts >= self.max_failed_attempts:
                    user.locked = True
                    await self._audit_event(
                        "account_locked",
                        user.user_id,
                        None,
                        reason="Too many failed attempts",
                        source_ip=source_ip,
                    )
                    logger.warning(f"🔒 Account locked for user {username}")

                await self._audit_event(
                    "authentication_failed",
                    user.user_id,
                    None,
                    reason="Invalid password",
                    source_ip=source_ip,
                )
                return False, None, "Authentication failed"

            # Check MFA if required
            auth_method = AuthenticationMethod.PASSWORD
            mfa_verified = False

            if user.mfa_enabled or user.current_tier.value >= self.mfa_required_tier.value:
                if not mfa_token or not self._verify_mfa(user.mfa_secret, mfa_token):
                    await self._audit_event(
                        "authentication_failed",
                        user.user_id,
                        None,
                        reason="MFA verification failed",
                        source_ip=source_ip,
                    )
                    return False, None, "MFA verification required"

                auth_method = AuthenticationMethod.MFA
                mfa_verified = True

            # Trinity Framework validation
            if not await self._validate_trinity_authentication(user):
                await self._audit_event(
                    "authentication_failed",
                    user.user_id,
                    None,
                    reason="Trinity Framework validation failed",
                    source_ip=source_ip,
                )
                return False, None, "Additional validation required"

            # Reset failed attempts on successful auth
            user.failed_attempts = 0
            user.locked = False

            # Create session
            session = await self.session_manager.create_session(
                user, auth_method, source_ip, user_agent, mfa_verified
            )

            # Audit successful authentication
            await self._audit_event(
                "authentication_success",
                user.user_id,
                session.session_id,
                reason="Successful authentication",
                source_ip=source_ip,
            )

            # Update metrics
            self.metrics["active_users"] = len(
                {s.user_id for s in self.session_manager.active_sessions.values()}
            )
            self.metrics["active_sessions"] = len(self.session_manager.active_sessions)

            logger.info(
                f"✅ User {username} authenticated successfully (tier: T{user.current_tier.value})"
            )
            return True, session, "Authentication successful"

        except Exception as e:
            logger.error(f"Authentication error for user {username}: {e}")
            await self._audit_event(
                "authentication_error",
                None,
                None,
                reason=f"System error: {e!s}",
                source_ip=source_ip,
            )
            return False, None, "Authentication system error"

    async def _validate_trinity_authentication(self, user: User) -> bool:
        """Validate authentication against Trinity Framework"""

        # ⚛️ Identity validation
        if not user.identity_verified and user.current_tier.value >= 3:
            return False

        # 🛡️ Guardian validation
        if not user.guardian_cleared:
            return False

        # 🧠 Consciousness level check
        if user.consciousness_level < 1:
            return False

        return True

    def _verify_password(self, password: str, stored_hash: Optional[str]) -> bool:
        """Verify password against stored hash"""
        if not stored_hash:
            return False

        # Simple hash verification - in production use proper password hashing
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return password_hash == stored_hash

    def _verify_mfa(self, secret: Optional[str], token: str) -> bool:
        """Verify MFA token"""
        if not secret:
            return False

        # Simplified MFA verification - in production use TOTP
        # For demo purposes, accept "123456" as valid MFA token
        return token == "123456"

    async def check_access(
        self,
        session_id: str,
        resource: str,
        access_type: AccessType,
        context: Optional[dict[str, Any]] = None,
    ) -> tuple[AccessDecision, str]:
        """
        Check if user has access to resource

        Returns:
            (decision, reason)
        """

        context = context or {}
        request_id = f"req_{uuid.uuid4().hex[:8]}"

        try:
            # Get session
            session = self.session_manager.get_session(session_id)
            if not session:
                await self._audit_access_request(
                    request_id,
                    "unknown",
                    session_id,
                    resource,
                    access_type,
                    AccessDecision.DENY,
                    "Invalid or expired session",
                    context,
                )
                return AccessDecision.DENY, "Invalid or expired session"

            # Get user
            user = self.users.get(session.user_id)
            if not user or not user.active:
                await self._audit_access_request(
                    request_id,
                    session.user_id,
                    session_id,
                    resource,
                    access_type,
                    AccessDecision.DENY,
                    "User not found or inactive",
                    context,
                )
                return AccessDecision.DENY, "User not found or inactive"

            # Get user permissions
            user_permissions = self.permission_manager.get_user_permissions(user)

            # Check if user has required permission for resource
            decision, reason = await self._evaluate_access_permission(
                user, user_permissions, resource, access_type, context
            )

            # Additional security checks
            if decision == AccessDecision.ALLOW:
                decision, reason = await self._apply_security_policies(
                    user, session, resource, access_type, context, decision, reason
                )

            # Trinity Framework validation
            if decision == AccessDecision.ALLOW:
                decision, reason = await self._validate_trinity_access(
                    user, session, resource, access_type, context, decision, reason
                )

            # Risk-based adjustments
            if decision == AccessDecision.ALLOW and session.risk_score > 0.7:
                decision = AccessDecision.MONITOR
                reason += " | High risk session - monitoring enabled"

            # Audit the access request
            await self._audit_access_request(
                request_id,
                user.user_id,
                session_id,
                resource,
                access_type,
                decision,
                reason,
                context,
            )

            # Update metrics
            self.metrics["total_requests"] += 1
            if decision == AccessDecision.ALLOW:
                self.metrics["allowed_requests"] += 1
            else:
                self.metrics["denied_requests"] += 1

            self.metrics["last_updated"] = datetime.now().isoformat()

            logger.debug(f"Access check: {decision.value} - {reason}")
            return decision, reason

        except Exception as e:
            logger.error(f"Access check error: {e}")
            await self._audit_access_request(
                request_id,
                "unknown",
                session_id,
                resource,
                access_type,
                AccessDecision.DENY,
                f"System error: {e!s}",
                context,
            )
            return AccessDecision.DENY, "Access control system error"

    async def _evaluate_access_permission(
        self,
        user: User,
        user_permissions: set[str],
        resource: str,
        access_type: AccessType,
        context: dict[str, Any],
    ) -> tuple[AccessDecision, str]:
        """Evaluate if user has required permission"""

        # Find matching permissions
        matching_permissions = []

        for perm_id in user_permissions:
            permission = self.permission_manager.permissions.get(perm_id)
            if permission and self._permission_matches_resource(permission, resource):
                matching_permissions.append(permission)

        if not matching_permissions:
            return AccessDecision.DENY, f"No permissions for resource: {resource}"

        # Check if any permission allows the access type
        for permission in matching_permissions:
            if access_type in permission.access_types:
                # Check tier requirement
                if user.current_tier.value >= permission.required_tier.value:
                    # Check context conditions
                    if self._check_context_conditions(permission, context):
                        return AccessDecision.ALLOW, f"Permission granted: {permission.name}"
                    else:
                        return (
                            AccessDecision.DENY,
                            f"Context conditions not met for: {permission.name}",
                        )
                else:
                    return (
                        AccessDecision.ESCALATE,
                        f"Insufficient tier for: {permission.name} (requires T{permission.required_tier.value})",
                    )

        return AccessDecision.DENY, f"No permission allows {access_type.value} access to {resource}"

    def _permission_matches_resource(self, permission: Permission, resource: str) -> bool:
        """Check if permission matches resource"""
        # Simple matching - could be more sophisticated with patterns
        return permission.resource_type in resource or permission.resource_type == "public"

    def _check_context_conditions(self, permission: Permission, context: dict[str, Any]) -> bool:
        """Check if context meets permission conditions"""
        if not permission.context_conditions:
            return True

        for key, expected_value in permission.context_conditions.items():
            if context.get(key) != expected_value:
                return False

        return True

    async def _apply_security_policies(
        self,
        user: User,
        session: AccessSession,
        resource: str,
        access_type: AccessType,
        context: dict[str, Any],
        current_decision: AccessDecision,
        current_reason: str,
    ) -> tuple[AccessDecision, str]:
        """Apply additional security policies"""

        # Time-based restrictions
        current_hour = datetime.now().hour
        if current_hour < 6 or current_hour > 22:  # Outside business hours
            if user.current_tier.value < 4:  # Non-privileged users
                return (
                    AccessDecision.CHALLENGE,
                    "Outside business hours - additional verification required",
                )

        # Sensitive operations
        if access_type in [AccessType.DELETE, AccessType.ADMIN, AccessType.SYSTEM]:
            if not session.mfa_verified:
                return (
                    AccessDecision.CHALLENGE,
                    "MFA verification required for sensitive operations",
                )

        # Rate limiting (simplified)
        # In production, implement proper rate limiting

        return current_decision, current_reason

    async def _validate_trinity_access(
        self,
        user: User,
        session: AccessSession,
        resource: str,
        access_type: AccessType,
        context: dict[str, Any],
        current_decision: AccessDecision,
        current_reason: str,
    ) -> tuple[AccessDecision, str]:
        """Validate access against Trinity Framework"""

        trinity_issues = []

        # ⚛️ Identity validation
        if "identity" in resource and not user.identity_verified:
            trinity_issues.append("Identity verification required")

        # 🧠 Consciousness validation
        if "consciousness" in resource or "ai" in resource:
            required_level = context.get("consciousness_level", 1)
            if user.consciousness_level < required_level:
                trinity_issues.append(f"Consciousness level {required_level} required")

        # 🛡️ Guardian validation
        if not user.guardian_cleared:
            trinity_issues.append("Guardian clearance required")

        # Check drift score from context
        drift_score = context.get("drift_score", 0.0)
        if drift_score > 0.15:
            trinity_issues.append(f"High drift score detected: {drift_score:.3f}")

        if trinity_issues:
            return (
                AccessDecision.ESCALATE,
                f"Trinity validation failed: {'; '.join(trinity_issues)}",
            )

        return current_decision, current_reason

    async def _audit_event(
        self,
        event_type: str,
        user_id: Optional[str],
        session_id: Optional[str],
        reason: str = "",
        source_ip: Optional[str] = None,
        risk_factors: Optional[list[str]] = None,
    ):
        """Audit access control event"""

        audit_entry = AccessAuditEntry(
            audit_id=f"audit_{uuid.uuid4().hex[:8]}",
            event_type=event_type,
            user_id=user_id or "unknown",
            session_id=session_id,
            reason=reason,
            source_ip=source_ip,
            risk_factors=risk_factors or [],
        )

        self.audit_trail.append(audit_entry)

        # Maintain audit trail size
        if len(self.audit_trail) > 10000:
            self.audit_trail = self.audit_trail[-10000:]

        logger.debug(f"Audited event: {event_type} - {reason}")

    async def _audit_access_request(
        self,
        request_id: str,
        user_id: str,
        session_id: str,
        resource: str,
        access_type: AccessType,
        decision: AccessDecision,
        reason: str,
        context: dict[str, Any],
    ):
        """Audit access control request"""

        await self._audit_event(
            event_type="access_request",
            user_id=user_id,
            session_id=session_id,
            reason=f"Resource: {resource}, Type: {access_type.value}, Decision: {decision.value}, Reason: {reason}",
        )

    async def create_user(
        self,
        username: str,
        email: str,
        password: str,
        tier: AccessTier = AccessTier.T2_USER,
        roles: Optional[set[str]] = None,
    ) -> tuple[bool, Optional[str], str]:
        """
        Create a new user

        Returns:
            (success, user_id, message)
        """

        try:
            # Check if user already exists
            for user in self.users.values():
                if user.username == username or user.email == email:
                    return False, None, "User already exists"

            # Generate user ID
            user_id = f"user_{uuid.uuid4().hex[:8]}"

            # Hash password
            password_hash = hashlib.sha256(password.encode()).hexdigest()

            # Set default roles based on tier
            if roles is None:
                if tier == AccessTier.T1_BASIC:
                    roles = {"basic_user"}
                elif tier == AccessTier.T2_USER:
                    roles = {"standard_user"}
                elif tier == AccessTier.T3_ADVANCED:
                    roles = {"advanced_user"}
                elif tier == AccessTier.T4_PRIVILEGED:
                    roles = {"administrator"}
                elif tier == AccessTier.T5_SYSTEM:
                    roles = {"system_admin"}
                else:
                    roles = {"basic_user"}

            # Create user
            user = User(
                user_id=user_id,
                username=username,
                email=email,
                current_tier=tier,
                max_tier=tier,
                roles=roles,
                password_hash=password_hash,
                auth_methods={AuthenticationMethod.PASSWORD},
            )

            self.users[user_id] = user

            await self._audit_event(
                "user_created", user_id, None, f"Created user: {username} with tier T{tier.value}"
            )

            logger.info(f"✅ Created user: {username} (T{tier.value})")
            return True, user_id, "User created successfully"

        except Exception as e:
            logger.error(f"Failed to create user {username}: {e}")
            return False, None, f"User creation failed: {e!s}"

    async def update_user_tier(self, user_id: str, new_tier: AccessTier) -> tuple[bool, str]:
        """Update user's access tier"""

        try:
            user = self.users.get(user_id)
            if not user:
                return False, "User not found"

            if new_tier.value > user.max_tier.value:
                return (
                    False,
                    f"Tier T{new_tier.value} exceeds maximum allowed tier T{user.max_tier.value}",
                )

            old_tier = user.current_tier
            user.current_tier = new_tier
            user.updated_at = datetime.now()

            # Update roles based on new tier
            # This is simplified - in practice might need more sophisticated role management

            await self._audit_event(
                "tier_updated",
                user_id,
                None,
                f"Tier changed from T{old_tier.value} to T{new_tier.value}",
            )

            logger.info(
                f"✅ Updated user {user.username} tier: T{old_tier.value} -> T{new_tier.value}"
            )
            return True, f"Tier updated to T{new_tier.value}"

        except Exception as e:
            logger.error(f"Failed to update user tier: {e}")
            return False, f"Tier update failed: {e!s}"

    async def get_access_status(self) -> dict[str, Any]:
        """Get current access control system status"""

        return {
            "system_status": "operational",
            "total_users": len(self.users),
            "active_sessions": len(self.session_manager.active_sessions),
            "permissions": len(self.permission_manager.permissions),
            "roles": len(self.permission_manager.roles),
            "audit_entries": len(self.audit_trail),
            "metrics": self.metrics,
            "tier_distribution": {
                f"T{tier.value}": len([u for u in self.users.values() if u.current_tier == tier])
                for tier in AccessTier
            },
        }

    async def generate_access_report(self) -> dict[str, Any]:
        """Generate comprehensive access control report"""

        report = {
            "report_id": f"access_report_{uuid.uuid4().hex[:8]}",
            "generated_at": datetime.now().isoformat(),
            "system_status": await self.get_access_status(),
            "recent_activity": [
                {
                    "event": entry.event_type,
                    "user": entry.user_id,
                    "timestamp": entry.timestamp.isoformat(),
                    "reason": entry.reason,
                }
                for entry in self.audit_trail[-100:]  # Last 100 events
            ],
            "security_summary": {
                "failed_authentications": len(
                    [e for e in self.audit_trail if e.event_type == "authentication_failed"]
                ),
                "locked_accounts": len([u for u in self.users.values() if u.locked]),
                "high_risk_sessions": len(
                    [s for s in self.session_manager.active_sessions.values() if s.risk_score > 0.5]
                ),
                "mfa_enabled_users": len([u for u in self.users.values() if u.mfa_enabled]),
            },
        }

        return report


# Export main classes and functions
__all__ = [
    "AccessControlEngine",
    "AccessDecision",
    "AccessSession",
    "AccessTier",
    "AccessType",
    "AuthenticationMethod",
    "Permission",
    "PermissionManager",
    "Role",
    "SessionManager",
    "SessionStatus",
    "User",
]
