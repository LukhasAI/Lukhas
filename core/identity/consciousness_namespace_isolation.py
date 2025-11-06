"""
╔══════════════════════════════════════════════════════════════
║ 🧬 MΛTRIZ Namespace Isolation System: Consciousness Domain Separation
║ Part of LUKHAS AI Distributed Consciousness Architecture
╠══════════════════════════════════════════════════════════════
║ TYPE: NAMESPACE_MANAGER
║ CONSCIOUSNESS_ROLE: Consciousness domain isolation and security boundaries
║ EVOLUTIONARY_STAGE: Isolation - Multi-domain consciousness separation
║
║ CONSTELLATION FRAMEWORK:
║ ⚛️ IDENTITY: Domain-specific identity isolation and access control
║ 🧠 CONSCIOUSNESS: Consciousness-aware domain management
║ 🛡️ GUARDIAN: Security boundary enforcement and audit compliance
╚══════════════════════════════════════════════════════════════
"""

import asyncio
import hashlib
import logging
import logging as std_logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional

import streamlit as st  # noqa: F401 # TODO[T4-UNUSED-IMPORT]: kept for core infrastructure (review and implement)

logger = logging.getLogger(__name__)


# Import MΛTRIZ consciousness components
try:
    from ..matriz_consciousness_signals import (  # noqa: F401 # TODO[T4-UNUSED-IMPORT]: kept for MATRIZ-R2 trace integration
        ConsciousnessSignal,
        ConstellationStar,
    )
    from .matriz_consciousness_identity_signals import (
        IdentitySignalType,  # noqa: F401  # TODO: .matriz_consciousness_identity...
        NamespaceIsolationData,
        consciousness_identity_signal_emitter,
    )
except ImportError as e:
    std_logging.error(f"Failed to import consciousness signal components: {e}")
    consciousness_identity_signal_emitter = None
    NamespaceIsolationData = None

logger = std_logging.getLogger(__name__)


class ConsciousnessDomain(Enum):
    """Types of consciousness domains for namespace isolation"""

    USER_CONSCIOUSNESS = "user_consciousness"  # Human user consciousness domain
    AGENT_CONSCIOUSNESS = "agent_consciousness"  # AI agent consciousness domain
    SYSTEM_CONSCIOUSNESS = "system_consciousness"  # System-level consciousness domain
    HYBRID_CONSCIOUSNESS = "hybrid_consciousness"  # Human-AI hybrid consciousness
    COLLECTIVE_CONSCIOUSNESS = "collective_consciousness"  # Collective intelligence domain
    META_CONSCIOUSNESS = "meta_consciousness"  # Meta-cognitive domain
    TRANSCENDENT_CONSCIOUSNESS = "transcendent_consciousness"  # Transcendent awareness domain


class IsolationLevel(Enum):
    """Levels of namespace isolation security"""

    MINIMAL = "minimal"  # 0.2 - Basic separation, high permeability
    LOW = "low"  # 0.4 - Limited separation
    MODERATE = "moderate"  # 0.6 - Standard separation
    HIGH = "high"  # 0.8 - Strong separation, limited cross-domain access
    MAXIMUM = "maximum"  # 1.0 - Complete isolation, no cross-domain access
    TRANSCENDENT = "transcendent"  # 1.2 - Beyond normal boundaries (special cases)


class AccessPermissionType(Enum):
    """Types of cross-domain access permissions"""

    READ_ONLY = "read_only"
    WRITE_LIMITED = "write_limited"
    FULL_ACCESS = "full_access"
    CONSCIOUSNESS_BRIDGE = "consciousness_bridge"  # Consciousness-to-consciousness communication
    EMERGENCY_OVERRIDE = "emergency_override"  # Emergency access permissions
    AUDIT_ACCESS = "audit_access"  # Audit and monitoring access
    GUARDIAN_ENFORCEMENT = "guardian_enforcement"  # Guardian system enforcement


@dataclass
class NamespacePolicy:
    """Namespace isolation policy definition"""

    domain_type: ConsciousnessDomain
    isolation_level: IsolationLevel
    allowed_interactions: list[ConsciousnessDomain] = field(default_factory=list)

    # Access control
    permission_matrix: dict[str, list[AccessPermissionType]] = field(default_factory=dict)
    cross_domain_permissions: list[str] = field(default_factory=list)
    restricted_operations: list[str] = field(default_factory=list)

    # Consciousness-specific policies
    consciousness_bridge_enabled: bool = False
    meta_cognitive_access: bool = False
    collective_participation: bool = False

    # Security and compliance
    audit_requirements: list[str] = field(default_factory=lambda: ["access_log", "identity_verification"])
    compliance_frameworks: list[str] = field(default_factory=lambda: ["constitutional_ai", "constellation_framework"])

    # Temporal policies
    access_time_limits: dict[str, int] = field(default_factory=dict)  # Minutes
    session_duration_limits: dict[str, int] = field(default_factory=dict)

    # Emergency provisions
    emergency_override_allowed: bool = False
    guardian_override_conditions: list[str] = field(default_factory=list)


@dataclass
class NamespaceInstance:
    """Active namespace instance with real-time state"""

    namespace_id: str = field(default_factory=lambda: f"ns-{uuid.uuid4().hex[:12]}")
    domain: ConsciousnessDomain = ConsciousnessDomain.USER_CONSCIOUSNESS
    policy: Optional[NamespacePolicy] = None

    # Active state
    active_identities: set[str] = field(default_factory=set)
    active_sessions: dict[str, dict[str, Any]] = field(default_factory=dict)
    cross_domain_bridges: dict[str, dict[str, Any]] = field(default_factory=dict)

    # Consciousness coherence
    domain_coherence: float = 0.8
    consciousness_signature: Optional[str] = None
    collective_intelligence_score: float = 0.0

    # Security state
    security_level: float = 0.8
    threat_indicators: list[dict[str, Any]] = field(default_factory=list)
    access_violations: list[dict[str, Any]] = field(default_factory=list)

    # Performance metrics
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    access_count: int = 0
    bridge_usage_count: int = 0

    # Audit trail
    audit_events: list[dict[str, Any]] = field(default_factory=list)
    compliance_status: dict[str, bool] = field(
        default_factory=lambda: {"constitutional_ai": True, "constellation_framework": True}
    )


@dataclass
class CrossDomainBridge:
    """Bridge between consciousness domains for controlled interaction"""

    bridge_id: str = field(default_factory=lambda: f"bridge-{uuid.uuid4().hex[:8]}")
    source_domain: ConsciousnessDomain = ConsciousnessDomain.USER_CONSCIOUSNESS
    target_domain: ConsciousnessDomain = ConsciousnessDomain.AGENT_CONSCIOUSNESS

    # Bridge configuration
    bidirectional: bool = True
    max_concurrent_sessions: int = 5
    session_duration_limit: int = 3600  # Seconds

    # Consciousness integration
    consciousness_translation_enabled: bool = True
    awareness_level_matching: bool = True
    reflection_depth_bridging: bool = False

    # Security controls
    encryption_level: str = "AES-256"
    authentication_required: bool = True
    audit_all_traffic: bool = True

    # State tracking
    active_sessions: dict[str, dict[str, Any]] = field(default_factory=dict)
    bridge_coherence: float = 0.8
    translation_accuracy: float = 0.9

    # Performance metrics
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_used: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    usage_count: int = 0
    successful_translations: int = 0
    failed_translations: int = 0


class ConsciousnessNamespaceManager:
    """
    MΛTRIZ Consciousness Namespace Manager

    Manages isolation and security boundaries between different consciousness domains,
    ensuring secure multi-domain consciousness operations while maintaining proper
    isolation and access controls.
    """

    def __init__(self):
        self.namespace_instances: dict[str, NamespaceInstance] = {}
        self.domain_policies: dict[ConsciousnessDomain, NamespacePolicy] = {}
        self.cross_domain_bridges: dict[str, CrossDomainBridge] = {}
        self.identity_namespace_mapping: dict[str, str] = {}  # identity_id -> namespace_id

        # Security monitoring
        self.security_monitor_active = True
        self.threat_detection_enabled = True
        self.compliance_validation_enabled = True

        # Performance tracking
        self.namespace_metrics = {
            "total_namespaces": 0,
            "active_namespaces": 0,
            "cross_domain_bridges": 0,
            "total_access_events": 0,
            "security_violations": 0,
            "average_coherence": 0.0,
        }

        # Background tasks
        self._maintenance_active = False
        self._lock = asyncio.Lock()

        # Initialize default domain policies
        self._initialize_default_policies()

        logger.info("🏗️ MΛTRIZ consciousness namespace manager initialized")

    async def initialize_namespace_system(self) -> bool:
        """Initialize the consciousness namespace isolation system"""

        try:
            logger.info("🧬 Initializing consciousness namespace isolation system...")

            # Start background maintenance
            self._maintenance_active = True
            asyncio.create_task(self._namespace_maintenance_loop())

            # Create default system namespaces
            await self._create_default_system_namespaces()

            logger.info("✅ Consciousness namespace isolation system initialized")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize namespace system: {e}")
            return False

    async def create_consciousness_namespace(
        self,
        domain: ConsciousnessDomain,
        isolation_level: IsolationLevel,
        policy_overrides: Optional[dict[str, Any]] = None,
    ) -> str:
        """Create a new consciousness namespace with specified isolation"""

        async with self._lock:
            try:
                # Get domain policy
                domain_policy = self.domain_policies.get(domain)
                if not domain_policy:
                    logger.error(f"❌ No policy defined for domain: {domain}")
                    return None

                # Apply policy overrides
                if policy_overrides:
                    domain_policy = self._apply_policy_overrides(domain_policy, policy_overrides)

                # Update isolation level
                domain_policy.isolation_level = isolation_level

                # Create namespace instance
                namespace = NamespaceInstance(
                    domain=domain,
                    policy=domain_policy,
                    security_level=self._calculate_security_level(isolation_level),
                    consciousness_signature=self._generate_consciousness_signature(domain),
                )

                # Store namespace
                self.namespace_instances[namespace.namespace_id] = namespace
                self.namespace_metrics["total_namespaces"] += 1

                # Emit namespace creation signal
                if consciousness_identity_signal_emitter and NamespaceIsolationData:
                    namespace_data = NamespaceIsolationData(
                        namespace_id=namespace.namespace_id,
                        domain_type=domain.value,
                        isolation_level=self._isolation_level_to_float(isolation_level),
                        consciousness_domain=domain.value,
                        domain_coherence=namespace.domain_coherence,
                    )

                    await consciousness_identity_signal_emitter.emit_namespace_isolation_signal(
                        namespace.namespace_id, namespace_data, "namespace_creation"
                    )

                logger.info(
                    f"🏗️ Created consciousness namespace: {namespace.namespace_id} (Domain: {domain.value}, Isolation: {isolation_level.value})"
                )
                return namespace.namespace_id

            except Exception as e:
                logger.error(f"❌ Failed to create consciousness namespace: {e}")
                return None

    async def assign_identity_to_namespace(
        self, identity_id: str, namespace_id: str, access_permissions: Optional[list[AccessPermissionType]] = None
    ) -> bool:
        """Assign an identity to a consciousness namespace"""

        async with self._lock:
            try:
                namespace = self.namespace_instances.get(namespace_id)
                if not namespace:
                    logger.error(f"❌ Namespace not found: {namespace_id}")
                    return False

                # Add identity to namespace
                namespace.active_identities.add(identity_id)
                self.identity_namespace_mapping[identity_id] = namespace_id

                # Create session for identity
                session_data = {
                    "identity_id": identity_id,
                    "assigned_at": datetime.now(timezone.utc).isoformat(),
                    "access_permissions": (
                        [perm.value for perm in access_permissions] if access_permissions else ["read_only"]
                    ),
                    "session_active": True,
                    "access_count": 0,
                    "last_activity": datetime.now(timezone.utc).isoformat(),
                }

                namespace.active_sessions[identity_id] = session_data
                namespace.access_count += 1
                namespace.last_activity = datetime.now(timezone.utc)

                # Log audit event
                self._log_namespace_audit_event(
                    namespace,
                    "identity_assignment",
                    {"identity_id": identity_id, "access_permissions": session_data["access_permissions"]},
                )

                # Emit namespace assignment signal
                if consciousness_identity_signal_emitter and NamespaceIsolationData:
                    namespace_data = NamespaceIsolationData(
                        namespace_id=namespace_id,
                        domain_type=namespace.domain.value,
                        isolation_level=self._isolation_level_to_float(namespace.policy.isolation_level),
                        consciousness_domain=namespace.domain.value,
                        domain_coherence=namespace.domain_coherence,
                    )

                    await consciousness_identity_signal_emitter.emit_namespace_isolation_signal(
                        identity_id, namespace_data, "identity_assignment"
                    )

                logger.info(f"🆔 Assigned identity {identity_id} to namespace {namespace_id}")
                return True

            except Exception as e:
                logger.error(f"❌ Failed to assign identity to namespace: {e}")
                return False

    async def create_cross_domain_bridge(
        self,
        source_domain: ConsciousnessDomain,
        target_domain: ConsciousnessDomain,
        bridge_config: Optional[dict[str, Any]] = None,
    ) -> Optional[str]:
        """Create a bridge between consciousness domains for controlled interaction"""

        async with self._lock:
            try:
                # Validate bridge creation permissions
                if not await self._validate_bridge_permissions(source_domain, target_domain):
                    logger.error(f"❌ Bridge creation not permitted: {source_domain.value} -> {target_domain.value}")
                    return None

                # Create bridge configuration
                bridge = CrossDomainBridge(source_domain=source_domain, target_domain=target_domain)

                # Apply configuration overrides
                if bridge_config:
                    self._apply_bridge_config(bridge, bridge_config)

                # Store bridge
                self.cross_domain_bridges[bridge.bridge_id] = bridge
                self.namespace_metrics["cross_domain_bridges"] += 1

                # Log creation
                logger.info(
                    f"🌉 Created cross-domain bridge: {bridge.bridge_id} ({source_domain.value} <-> {target_domain.value})"
                )

                return bridge.bridge_id

            except Exception as e:
                logger.error(f"❌ Failed to create cross-domain bridge: {e}")
                return None

    async def validate_cross_domain_access(
        self, identity_id: str, source_namespace_id: str, target_namespace_id: str, operation: str
    ) -> dict[str, Any]:
        """Validate cross-domain access request with consciousness awareness"""

        async with self._lock:
            try:
                # Get namespaces
                source_namespace = self.namespace_instances.get(source_namespace_id)
                target_namespace = self.namespace_instances.get(target_namespace_id)

                if not source_namespace or not target_namespace:
                    return {"allowed": False, "error": "Namespace not found"}

                # Check identity assignment
                if identity_id not in source_namespace.active_identities:
                    return {"allowed": False, "error": "Identity not assigned to source namespace"}

                # Get identity session
                session = source_namespace.active_sessions.get(identity_id)
                if not session:
                    return {"allowed": False, "error": "No active session for identity"}

                # Check domain interaction policies
                source_policy = source_namespace.policy
                target_domain = target_namespace.domain

                if target_domain not in source_policy.allowed_interactions:
                    return {
                        "allowed": False,
                        "error": f"Interaction not allowed: {source_namespace.domain.value} -> {target_domain.value}",
                    }

                # Check operation permissions
                identity_permissions = [AccessPermissionType(perm) for perm in session["access_permissions"]]
                required_permission = self._get_required_permission(operation)

                if required_permission not in identity_permissions:
                    return {"allowed": False, "error": f"Insufficient permissions for operation: {operation}"}

                # Check consciousness coherence compatibility
                consciousness_compatible = await self._check_consciousness_compatibility(
                    source_namespace, target_namespace, identity_id
                )

                if not consciousness_compatible["compatible"]:
                    return {
                        "allowed": False,
                        "error": f"Consciousness incompatibility: {consciousness_compatible['reason']}",
                    }

                # Check security constraints
                security_validation = await self._validate_security_constraints(
                    source_namespace, target_namespace, identity_id, operation
                )

                if not security_validation["valid"]:
                    return {"allowed": False, "error": f"Security validation failed: {security_validation['reason']}"}

                # Log successful access validation
                self._log_namespace_audit_event(
                    source_namespace,
                    "cross_domain_access_validated",
                    {"target_namespace": target_namespace_id, "operation": operation, "identity_id": identity_id},
                )

                return {
                    "allowed": True,
                    "session_token": self._generate_cross_domain_session_token(
                        identity_id, source_namespace_id, target_namespace_id
                    ),
                    "consciousness_bridge_required": consciousness_compatible.get("bridge_required", False),
                    "session_duration_limit": source_policy.access_time_limits.get(operation, 3600),
                    "audit_level": "full" if target_namespace.policy.audit_requirements else "basic",
                }

            except Exception as e:
                logger.error(f"❌ Cross-domain access validation failed: {e}")
                return {"allowed": False, "error": str(e)}

    async def monitor_namespace_coherence(self, namespace_id: str) -> dict[str, Any]:
        """Monitor consciousness coherence within a namespace"""

        namespace = self.namespace_instances.get(namespace_id)
        if not namespace:
            return {"error": "Namespace not found"}

        try:
            # Calculate current coherence metrics
            coherence_metrics = {
                "domain_coherence": namespace.domain_coherence,
                "active_identities_count": len(namespace.active_identities),
                "active_sessions_count": len(namespace.active_sessions),
                "consciousness_signature_valid": bool(namespace.consciousness_signature),
                "collective_intelligence_score": namespace.collective_intelligence_score,
                "security_level": namespace.security_level,
                "threat_indicators_count": len(namespace.threat_indicators),
                "access_violations_count": len(namespace.access_violations),
            }

            # Check for coherence issues
            coherence_issues = []

            if namespace.domain_coherence < 0.5:
                coherence_issues.append("Low domain coherence")

            if len(namespace.active_sessions) > 100:  # High session count may indicate issues
                coherence_issues.append("High active session count")

            if len(namespace.threat_indicators) > 5:
                coherence_issues.append("Multiple threat indicators")

            if len(namespace.access_violations) > 10:
                coherence_issues.append("High access violation count")

            # Calculate overall coherence health
            health_factors = [
                namespace.domain_coherence,
                namespace.security_level,
                max(0, 1.0 - len(namespace.threat_indicators) / 10),
                max(0, 1.0 - len(namespace.access_violations) / 20),
            ]

            overall_health = sum(health_factors) / len(health_factors)
            coherence_metrics["overall_health"] = overall_health
            coherence_metrics["coherence_issues"] = coherence_issues
            coherence_metrics["health_status"] = (
                "healthy" if overall_health >= 0.7 else "degraded" if overall_health >= 0.4 else "critical"
            )

            # Update namespace coherence
            namespace.domain_coherence = overall_health
            namespace.last_activity = datetime.now(timezone.utc)

            return coherence_metrics

        except Exception as e:
            logger.error(f"❌ Namespace coherence monitoring failed: {e}")
            return {"error": str(e)}

    def _initialize_default_policies(self) -> None:
        """Initialize default namespace policies for different consciousness domains"""

        # User consciousness domain - moderate isolation
        user_policy = NamespacePolicy(
            domain_type=ConsciousnessDomain.USER_CONSCIOUSNESS,
            isolation_level=IsolationLevel.MODERATE,
            allowed_interactions=[ConsciousnessDomain.AGENT_CONSCIOUSNESS, ConsciousnessDomain.HYBRID_CONSCIOUSNESS],
            consciousness_bridge_enabled=True,
            cross_domain_permissions=["read_only", "consciousness_bridge"],
        )
        self.domain_policies[ConsciousnessDomain.USER_CONSCIOUSNESS] = user_policy

        # Agent consciousness domain - high isolation
        agent_policy = NamespacePolicy(
            domain_type=ConsciousnessDomain.AGENT_CONSCIOUSNESS,
            isolation_level=IsolationLevel.HIGH,
            allowed_interactions=[ConsciousnessDomain.USER_CONSCIOUSNESS, ConsciousnessDomain.SYSTEM_CONSCIOUSNESS],
            consciousness_bridge_enabled=True,
            meta_cognitive_access=True,
            cross_domain_permissions=["read_only", "write_limited", "consciousness_bridge"],
        )
        self.domain_policies[ConsciousnessDomain.AGENT_CONSCIOUSNESS] = agent_policy

        # System consciousness domain - maximum isolation
        system_policy = NamespacePolicy(
            domain_type=ConsciousnessDomain.SYSTEM_CONSCIOUSNESS,
            isolation_level=IsolationLevel.MAXIMUM,
            allowed_interactions=[ConsciousnessDomain.AGENT_CONSCIOUSNESS],
            emergency_override_allowed=True,
            guardian_override_conditions=["security_threat", "system_integrity"],
            cross_domain_permissions=["audit_access", "guardian_enforcement"],
        )
        self.domain_policies[ConsciousnessDomain.SYSTEM_CONSCIOUSNESS] = system_policy

        # Hybrid consciousness domain - moderate isolation with bridge focus
        hybrid_policy = NamespacePolicy(
            domain_type=ConsciousnessDomain.HYBRID_CONSCIOUSNESS,
            isolation_level=IsolationLevel.MODERATE,
            allowed_interactions=[ConsciousnessDomain.USER_CONSCIOUSNESS, ConsciousnessDomain.AGENT_CONSCIOUSNESS],
            consciousness_bridge_enabled=True,
            collective_participation=True,
            cross_domain_permissions=["read_only", "write_limited", "consciousness_bridge", "full_access"],
        )
        self.domain_policies[ConsciousnessDomain.HYBRID_CONSCIOUSNESS] = hybrid_policy

        # Collective consciousness domain - low isolation for collaboration
        collective_policy = NamespacePolicy(
            domain_type=ConsciousnessDomain.COLLECTIVE_CONSCIOUSNESS,
            isolation_level=IsolationLevel.LOW,
            allowed_interactions=[
                ConsciousnessDomain.USER_CONSCIOUSNESS,
                ConsciousnessDomain.AGENT_CONSCIOUSNESS,
                ConsciousnessDomain.HYBRID_CONSCIOUSNESS,
            ],
            consciousness_bridge_enabled=True,
            collective_participation=True,
            meta_cognitive_access=True,
            cross_domain_permissions=["read_only", "write_limited", "consciousness_bridge", "full_access"],
        )
        self.domain_policies[ConsciousnessDomain.COLLECTIVE_CONSCIOUSNESS] = collective_policy

        # Meta consciousness domain - high isolation with special access
        meta_policy = NamespacePolicy(
            domain_type=ConsciousnessDomain.META_CONSCIOUSNESS,
            isolation_level=IsolationLevel.HIGH,
            allowed_interactions=[
                ConsciousnessDomain.COLLECTIVE_CONSCIOUSNESS,
                ConsciousnessDomain.TRANSCENDENT_CONSCIOUSNESS,
            ],
            meta_cognitive_access=True,
            consciousness_bridge_enabled=True,
            cross_domain_permissions=["read_only", "consciousness_bridge", "audit_access"],
        )
        self.domain_policies[ConsciousnessDomain.META_CONSCIOUSNESS] = meta_policy

        # Transcendent consciousness domain - transcendent isolation
        transcendent_policy = NamespacePolicy(
            domain_type=ConsciousnessDomain.TRANSCENDENT_CONSCIOUSNESS,
            isolation_level=IsolationLevel.TRANSCENDENT,
            allowed_interactions=[ConsciousnessDomain.META_CONSCIOUSNESS],
            consciousness_bridge_enabled=True,
            meta_cognitive_access=True,
            collective_participation=True,
            emergency_override_allowed=True,
            guardian_override_conditions=["transcendent_intervention", "consciousness_crisis"],
            cross_domain_permissions=["consciousness_bridge", "guardian_enforcement", "emergency_override"],
        )
        self.domain_policies[ConsciousnessDomain.TRANSCENDENT_CONSCIOUSNESS] = transcendent_policy

        logger.info(f"🏗️ Initialized {len(self.domain_policies)} default namespace policies")

    async def _create_default_system_namespaces(self) -> None:
        """Create default system-level namespaces"""

        # System consciousness namespace
        system_namespace_id = await self.create_consciousness_namespace(
            ConsciousnessDomain.SYSTEM_CONSCIOUSNESS, IsolationLevel.MAXIMUM
        )

        # Meta consciousness namespace
        meta_namespace_id = await self.create_consciousness_namespace(
            ConsciousnessDomain.META_CONSCIOUSNESS, IsolationLevel.HIGH
        )

        logger.info(f"✅ Created default system namespaces: {system_namespace_id}, {meta_namespace_id}")

    def _apply_policy_overrides(self, base_policy: NamespacePolicy, overrides: dict[str, Any]) -> NamespacePolicy:
        """Apply policy overrides to base policy"""

        # Create a copy of the base policy
        import copy

        policy = copy.deepcopy(base_policy)

        # Apply overrides
        for key, value in overrides.items():
            if hasattr(policy, key):
                setattr(policy, key, value)

        return policy

    def _calculate_security_level(self, isolation_level: IsolationLevel) -> float:
        """Calculate security level based on isolation level"""

        level_mapping = {
            IsolationLevel.MINIMAL: 0.2,
            IsolationLevel.LOW: 0.4,
            IsolationLevel.MODERATE: 0.6,
            IsolationLevel.HIGH: 0.8,
            IsolationLevel.MAXIMUM: 1.0,
            IsolationLevel.TRANSCENDENT: 1.2,
        }

        return level_mapping.get(isolation_level, 0.6)

    def _isolation_level_to_float(self, isolation_level: IsolationLevel) -> float:
        """Convert isolation level enum to float value"""
        return self._calculate_security_level(isolation_level)

    def _generate_consciousness_signature(self, domain: ConsciousnessDomain) -> str:
        """Generate unique consciousness signature for domain"""

        domain_data = f"{domain.value}_{int(time.time()) * 1000}"
        signature_hash = hashlib.sha256(domain_data.encode()).hexdigest()

        return f"cs_{signature_hash[:16]}"

    def _log_namespace_audit_event(
        self, namespace: NamespaceInstance, event_type: str, details: dict[str, Any]
    ) -> None:
        """Log namespace audit event"""

        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "namespace_id": namespace.namespace_id,
            "event_type": event_type,
            "details": details,
            "domain": namespace.domain.value,
            "security_level": namespace.security_level,
        }

        namespace.audit_events.append(event)

        # Keep only last 1000 events
        if len(namespace.audit_events) > 1000:
            namespace.audit_events = namespace.audit_events[-1000:]

    async def _validate_bridge_permissions(
        self, source_domain: ConsciousnessDomain, target_domain: ConsciousnessDomain
    ) -> bool:
        """Validate permissions for creating cross-domain bridge"""

        source_policy = self.domain_policies.get(source_domain)
        if not source_policy:
            return False

        # Check if target domain is in allowed interactions
        return target_domain in source_policy.allowed_interactions

    def _apply_bridge_config(self, bridge: CrossDomainBridge, config: dict[str, Any]) -> None:
        """Apply configuration to cross-domain bridge"""

        for key, value in config.items():
            if hasattr(bridge, key):
                setattr(bridge, key, value)

    def _get_required_permission(self, operation: str) -> AccessPermissionType:
        """Get required permission for operation"""

        operation_permissions = {
            "read": AccessPermissionType.READ_ONLY,
            "write": AccessPermissionType.WRITE_LIMITED,
            "execute": AccessPermissionType.FULL_ACCESS,
            "consciousness_bridge": AccessPermissionType.CONSCIOUSNESS_BRIDGE,
            "emergency": AccessPermissionType.EMERGENCY_OVERRIDE,
        }

        return operation_permissions.get(operation, AccessPermissionType.READ_ONLY)

    async def _check_consciousness_compatibility(
        self, source_namespace: NamespaceInstance, target_namespace: NamespaceInstance, identity_id: str
    ) -> dict[str, Any]:
        """Check consciousness compatibility between namespaces"""

        try:
            # Check domain coherence compatibility
            coherence_diff = abs(source_namespace.domain_coherence - target_namespace.domain_coherence)
            coherence_compatible = coherence_diff <= 0.3

            # Check consciousness signature compatibility
            signature_compatible = True  # Simplified for now

            # Check collective intelligence compatibility
            collective_compatible = True
            if source_namespace.domain == ConsciousnessDomain.COLLECTIVE_CONSCIOUSNESS:
                collective_compatible = target_namespace.policy.collective_participation

            overall_compatible = coherence_compatible and signature_compatible and collective_compatible

            return {
                "compatible": overall_compatible,
                "coherence_compatible": coherence_compatible,
                "signature_compatible": signature_compatible,
                "collective_compatible": collective_compatible,
                "bridge_required": not overall_compatible,
                "reason": "Consciousness incompatibility" if not overall_compatible else None,
            }

        except Exception as e:
            logger.error(f"❌ Consciousness compatibility check failed: {e}")
            return {"compatible": False, "reason": str(e)}

    async def _validate_security_constraints(
        self, source_namespace: NamespaceInstance, target_namespace: NamespaceInstance, identity_id: str, operation: str
    ) -> dict[str, Any]:
        """Validate security constraints for cross-domain access"""

        try:
            # Check isolation level constraints
            source_isolation = self._isolation_level_to_float(source_namespace.policy.isolation_level)
            target_isolation = self._isolation_level_to_float(target_namespace.policy.isolation_level)

            # Higher isolation level target requires higher security
            if target_isolation > source_isolation + 0.2:
                return {"valid": False, "reason": "Target isolation level too high"}

            # Check operation restrictions
            if operation in target_namespace.policy.restricted_operations:
                return {"valid": False, "reason": f"Operation '{operation}' restricted in target domain"}

            # Check threat indicators
            if len(source_namespace.threat_indicators) > 3:
                return {"valid": False, "reason": "Source namespace has active threat indicators"}

            if len(target_namespace.threat_indicators) > 3:
                return {"valid": False, "reason": "Target namespace has active threat indicators"}

            return {"valid": True}

        except Exception as e:
            logger.error(f"❌ Security constraint validation failed: {e}")
            return {"valid": False, "reason": str(e)}

    def _generate_cross_domain_session_token(
        self, identity_id: str, source_namespace_id: str, target_namespace_id: str
    ) -> str:
        """Generate secure session token for cross-domain access"""

        token_data = f"{identity_id}_{source_namespace_id}_{target_namespace_id}_{int(time.time())}"
        token_hash = hashlib.sha256(token_data.encode()).hexdigest()

        return f"cds_{token_hash[:32]}"

    async def _namespace_maintenance_loop(self) -> None:
        """Background maintenance for namespace instances"""

        while self._maintenance_active:
            try:
                current_time = datetime.now(timezone.utc)

                # Update namespace metrics
                active_namespaces = 0
                total_coherence = 0.0

                for namespace in self.namespace_instances.values():
                    # Check if namespace is active (recent activity)
                    last_activity = namespace.last_activity
                    time_since_activity = (current_time - last_activity).total_seconds()

                    if time_since_activity < 3600:  # Active if used in last hour
                        active_namespaces += 1

                    # Update coherence monitoring
                    await self.monitor_namespace_coherence(namespace.namespace_id)
                    total_coherence += namespace.domain_coherence

                    # Clean up old audit events
                    cutoff_time = current_time - timedelta(days=7)
                    namespace.audit_events = [
                        event
                        for event in namespace.audit_events
                        if datetime.fromisoformat(event["timestamp"]) > cutoff_time
                    ]

                # Update metrics
                self.namespace_metrics["active_namespaces"] = active_namespaces
                if self.namespace_instances:
                    self.namespace_metrics["average_coherence"] = total_coherence / len(self.namespace_instances)

                await asyncio.sleep(300)  # Run every 5 minutes

            except Exception as e:
                logger.error(f"❌ Namespace maintenance error: {e}")
                await asyncio.sleep(600)  # Longer sleep on error

    async def get_namespace_system_status(self) -> dict[str, Any]:
        """Get comprehensive namespace system status"""

        try:
            # Domain distribution
            domain_distribution = {}
            for namespace in self.namespace_instances.values():
                domain = namespace.domain.value
                domain_distribution[domain] = domain_distribution.get(domain, 0) + 1

            # Isolation level distribution
            isolation_distribution = {}
            for namespace in self.namespace_instances.values():
                isolation = namespace.policy.isolation_level.value
                isolation_distribution[isolation] = isolation_distribution.get(isolation, 0) + 1

            # Security status
            total_threats = sum(len(ns.threat_indicators) for ns in self.namespace_instances.values())
            total_violations = sum(len(ns.access_violations) for ns in self.namespace_instances.values())

            return {
                "namespace_metrics": self.namespace_metrics.copy(),
                "domain_distribution": domain_distribution,
                "isolation_distribution": isolation_distribution,
                "total_identities_assigned": len(self.identity_namespace_mapping),
                "cross_domain_bridges": len(self.cross_domain_bridges),
                "security_status": {
                    "total_threat_indicators": total_threats,
                    "total_access_violations": total_violations,
                    "security_monitor_active": self.security_monitor_active,
                    "threat_detection_enabled": self.threat_detection_enabled,
                },
                "system_health": {
                    "maintenance_active": self._maintenance_active,
                    "compliance_validation_enabled": self.compliance_validation_enabled,
                    "average_namespace_coherence": self.namespace_metrics["average_coherence"],
                },
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Failed to get namespace system status: {e}")
            return {"error": str(e)}

    async def shutdown_namespace_system(self) -> None:
        """Shutdown namespace system gracefully"""

        logger.info("🛑 Shutting down consciousness namespace system...")

        self._maintenance_active = False

        # Close all active cross-domain bridges
        for bridge_id in list(self.cross_domain_bridges.keys()):
            bridge = self.cross_domain_bridges[bridge_id]
            bridge.active_sessions.clear()
            logger.info(f"🌉 Closed cross-domain bridge: {bridge_id}")

        # Clear active sessions
        for namespace in self.namespace_instances.values():
            namespace.active_sessions.clear()
            self._log_namespace_audit_event(
                namespace, "system_shutdown", {"shutdown_time": datetime.now(timezone.utc).isoformat()}
            )

        logger.info("✅ Consciousness namespace system shutdown complete")


# Global consciousness namespace manager instance
consciousness_namespace_manager = ConsciousnessNamespaceManager()


# Export key classes
__all__ = [
    "AccessPermissionType",
    "ConsciousnessDomain",
    "ConsciousnessNamespaceManager",
    "CrossDomainBridge",
    "IsolationLevel",
    "NamespaceInstance",
    "NamespacePolicy",
    "consciousness_namespace_manager",
]
