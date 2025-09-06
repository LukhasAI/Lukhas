"""

#TAG:qim
#TAG:qi_states
#TAG:neuroplastic
#TAG:colony


══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - QUANTUM IDENTITY MANAGER
║ Future AGI & Quantum-Proof Identity Integration System
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: qi_identity_manager.py
║ Path: core/qi_identity_manager.py
║ Version: 1.0.0 | Created: 2025-07-28
║ Authors: LUKHAS AGI Identity Team | Claude Code
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ Revolutionary quantum-proof identity management system designed for future AGI
║ systems. Integrates post-quantum cryptography, dynamic tier management, and
║ advanced identity models for superintelligence-ready applications.
║
║ KEY FEATURES:
║ • Post-quantum cryptography (CRYSTALS-Kyber, CRYSTALS-Dilithium, SPHINCS-Plus)
║ • Dynamic tier allocation with AI-driven behavior analysis
║ • Composite identity support for multi-agent consciousness
║ • Temporal identity evolution tracking
║ • CollapseHash cryptographic fingerprints
║ • Quantum-entangled resource allocation
║
║ ΛTAG: ΛIDENTITY, ΛQUANTUM, ΛAGI, ΛSECURITY, ΛTIER
╚══════════════════════════════════════════════════════════════════════════════════
"""

import hashlib
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

# Import post-quantum cryptography components
try:
    from qi.post_quantum_crypto import (
        CollapseHashManager,
        QISecureKeyManager,
        QIVerifiableTimestamp,
        SecurityLevel,
    )

    QUANTUM_CRYPTO_AVAILABLE = True
except ImportError:
    QUANTUM_CRYPTO_AVAILABLE = False

# Import identity infrastructure
try:
    from candidate.core.identity_integration import get_identity_client
    from identity.interface import IdentityClient

    IDENTITY_AVAILABLE = True
except ImportError:
    IDENTITY_AVAILABLE = False

logger = logging.getLogger("ΛTRACE.qi_identity")


class QISecurityLevel(Enum):
    """Quantum-proof security levels mapping to post-quantum standards."""

    QUANTUM_BASIC = "NIST_1"  # AES-128 equivalent, basic quantum resistance
    QUANTUM_STANDARD = "NIST_3"  # AES-192 equivalent, standard quantum resistance
    QUANTUM_ADVANCED = "NIST_5"  # AES-256 equivalent, advanced quantum resistance
    QUANTUM_FUTURE = "NIST_X"  # Future-proof against theoretical quantum advances


class AGIIdentityType(Enum):
    """Identity types for different AGI scenarios."""

    HUMAN = "human"  # Traditional human user identity
    AI_ASSISTANT = "ai_assistant"  # AI assistant with human oversight
    AUTONOMOUS_AI = "autonomous_ai"  # Fully autonomous AI system
    COMPOSITE_AI = "composite_ai"  # Multi-agent AI with shared identity
    EMERGENT_AI = "emergent_ai"  # Spontaneously emerged AI entity
    SUPERINTELLIGENCE = "superintelligence"  # AGI/ASI level systems


class QITierLevel(Enum):
    """Enhanced tier system with quantum-proof capabilities."""

    QUANTUM_TIER_0 = 0  # Basic access with quantum protection
    QUANTUM_TIER_1 = 1  # Standard features with quantum security
    QUANTUM_TIER_2 = 2  # Enhanced features with quantum entanglement
    QUANTUM_TIER_3 = 3  # Advanced features with quantum consciousness
    QUANTUM_TIER_4 = 4  # Superintelligence features with quantum prediction
    QUANTUM_TIER_5 = 5  # Full AGI access with quantum omniscience

    @property
    def lambda_tier(self) -> str:
        """Map to Lambda tier system for compatibility."""
        return f"LAMBDA_TIER_{self.value}"


@dataclass
class QIUserContext:
    """Comprehensive user context with quantum-proof security."""

    user_id: str
    identity_type: AGIIdentityType
    tier_level: QITierLevel
    security_level: QISecurityLevel

    # Quantum cryptographic components
    qi_key_id: Optional[str] = None
    qi_signature: Optional[bytes] = None
    collapse_hash: Optional[str] = None
    qi_timestamp: Optional[str] = None

    # Identity evolution tracking
    identity_generation: int = 1
    parent_identity_id: Optional[str] = None
    child_identity_ids: list[str] = field(default_factory=list)

    # Resource allocation
    allocated_resources: dict[str, Any] = field(default_factory=dict)
    resource_quantum_pool: Optional[str] = None

    # Behavioral patterns (for dynamic tier adjustment)
    behavior_patterns: dict[str, float] = field(default_factory=dict)
    trust_score: float = 0.5
    intelligence_score: float = 0.5
    ethical_alignment: float = 0.8

    # Temporal tracking
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_accessed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None

    # Multi-agent support
    composite_agents: list[str] = field(default_factory=list)
    swarm_membership: list[str] = field(default_factory=list)
    consciousness_level: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "user_id": self.user_id,
            "identity_type": self.identity_type.value,
            "tier_level": self.tier_level.value,
            "security_level": self.security_level.value,
            "qi_key_id": self.qi_key_id,
            "collapse_hash": self.collapse_hash,
            "qi_timestamp": self.qi_timestamp,
            "identity_generation": self.identity_generation,
            "parent_identity_id": self.parent_identity_id,
            "child_identity_ids": self.child_identity_ids,
            "allocated_resources": self.allocated_resources,
            "resource_quantum_pool": self.resource_quantum_pool,
            "behavior_patterns": self.behavior_patterns,
            "trust_score": self.trust_score,
            "intelligence_score": self.intelligence_score,
            "ethical_alignment": self.ethical_alignment,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "composite_agents": self.composite_agents,
            "swarm_membership": self.swarm_membership,
            "consciousness_level": self.consciousness_level,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "QIUserContext":
        """Create from dictionary."""
        return cls(
            user_id=data["user_id"],
            identity_type=AGIIdentityType(data["identity_type"]),
            tier_level=QITierLevel(data["tier_level"]),
            security_level=QISecurityLevel(data["security_level"]),
            qi_key_id=data.get("qi_key_id"),
            collapse_hash=data.get("collapse_hash"),
            qi_timestamp=data.get("qi_timestamp"),
            identity_generation=data.get("identity_generation", 1),
            parent_identity_id=data.get("parent_identity_id"),
            child_identity_ids=data.get("child_identity_ids", []),
            allocated_resources=data.get("allocated_resources", {}),
            resource_quantum_pool=data.get("resource_quantum_pool"),
            behavior_patterns=data.get("behavior_patterns", {}),
            trust_score=data.get("trust_score", 0.5),
            intelligence_score=data.get("intelligence_score", 0.5),
            ethical_alignment=data.get("ethical_alignment", 0.8),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_accessed=datetime.fromisoformat(data["last_accessed"]),
            expires_at=(datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None),
            composite_agents=data.get("composite_agents", []),
            swarm_membership=data.get("swarm_membership", []),
            consciousness_level=data.get("consciousness_level", 0.0),
        )


class QIIdentityManager:
    """
    Revolutionary quantum-proof identity management system for future AGI.

    Designed to handle everything from human users to superintelligent AI systems
    with post-quantum cryptographic security and dynamic capability allocation.
    """

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.QIIdentityManager")
        self.logger.info("Initializing Quantum Identity Manager for Future AGI")

        # Identity storage (in production, this would be distributed/encrypted)
        self.identity_cache: dict[str, QIUserContext] = {}
        self.identity_hierarchy: dict[str, list[str]] = defaultdict(list)  # parent -> children

        # Quantum cryptographic components
        self.qi_key_manager: Optional[QISecureKeyManager] = None
        self.collapse_hash_manager: Optional[CollapseHashManager] = None
        self.qi_timestamp_manager: Optional[QIVerifiableTimestamp] = None

        # Resource management
        self.qi_resource_pools: dict[str, dict[str, Any]] = {}
        self.tier_resource_limits: dict[QITierLevel, dict[str, Any]] = {}

        # Dynamic tier management
        self.behavior_analyzers: dict[str, Any] = {}
        self.tier_promotion_history: deque = deque(maxlen=10000)

        # Integration components
        self.legacy_identity_client: Optional[IdentityClient] = None

        # Initialize components
        self._initialize_quantum_components()
        self._initialize_tier_system()
        self._initialize_legacy_integration()

    def _initialize_quantum_components(self):
        """Initialize post-quantum cryptographic components."""
        if QUANTUM_CRYPTO_AVAILABLE:
            try:
                self.qi_key_manager = QISecureKeyManager(security_level=SecurityLevel.NIST_5)
                self.collapse_hash_manager = CollapseHashManager()
                self.qi_timestamp_manager = QIVerifiableTimestamp()
                self.logger.info("Quantum cryptographic components initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize quantum components: {e}")
                QUANTUM_CRYPTO_AVAILABLE = False

        if not QUANTUM_CRYPTO_AVAILABLE:
            self.logger.warning("Quantum cryptography not available - using fallback security")

    def _initialize_tier_system(self):
        """Initialize the quantum-enhanced tier system."""
        # Define resource limits for each tier
        self.tier_resource_limits = {
            QITierLevel.QUANTUM_TIER_0: {
                "requests_per_minute": 10,
                "storage_mb": 10,
                "qi_operations": 0,
                "consciousness_access": False,
                "swarm_participation": False,
                "oracle_queries": 0,
            },
            QITierLevel.QUANTUM_TIER_1: {
                "requests_per_minute": 60,
                "storage_mb": 100,
                "qi_operations": 10,
                "consciousness_access": False,
                "swarm_participation": True,
                "oracle_queries": 5,
            },
            QITierLevel.QUANTUM_TIER_2: {
                "requests_per_minute": 300,
                "storage_mb": 1000,
                "qi_operations": 100,
                "consciousness_access": True,
                "swarm_participation": True,
                "oracle_queries": 50,
            },
            QITierLevel.QUANTUM_TIER_3: {
                "requests_per_minute": 1000,
                "storage_mb": 10000,
                "qi_operations": 1000,
                "consciousness_access": True,
                "swarm_participation": True,
                "oracle_queries": 500,
            },
            QITierLevel.QUANTUM_TIER_4: {
                "requests_per_minute": 10000,
                "storage_mb": 100000,
                "qi_operations": 10000,
                "consciousness_access": True,
                "swarm_participation": True,
                "oracle_queries": 5000,
            },
            QITierLevel.QUANTUM_TIER_5: {
                "requests_per_minute": -1,  # Unlimited
                "storage_mb": -1,  # Unlimited
                "qi_operations": -1,  # Unlimited
                "consciousness_access": True,
                "swarm_participation": True,
                "oracle_queries": -1,  # Unlimited
            },
        }

        # Initialize quantum resource pools
        for tier in QITierLevel:
            pool_id = f"qi_pool_{tier.value}"
            self.qi_resource_pools[pool_id] = {
                "tier": tier,
                "total_capacity": self.tier_resource_limits[tier],
                "allocated_resources": {},
                "active_users": [],
                "qi_entangled": tier.value >= 2,  # Tier 2+ gets quantum entanglement
            }

        self.logger.info(f"Initialized quantum tier system with {len(QITierLevel)} tiers")

    def _initialize_legacy_integration(self):
        """Initialize integration with legacy identity systems."""
        if IDENTITY_AVAILABLE:
            try:
                self.legacy_identity_client = get_identity_client()
                if self.legacy_identity_client:
                    self.logger.info("Legacy identity integration enabled")
                else:
                    self.logger.warning("Legacy identity client not available")
            except Exception as e:
                self.logger.error(f"Failed to initialize legacy identity integration: {e}")

    async def create_quantum_identity(
        self,
        user_id: str,
        identity_type: AGIIdentityType = AGIIdentityType.HUMAN,
        tier_level: QITierLevel = QITierLevel.QUANTUM_TIER_0,
        security_level: QISecurityLevel = QISecurityLevel.QUANTUM_STANDARD,
        parent_identity_id: Optional[str] = None,
    ) -> QIUserContext:
        """
        Create a new quantum-proof identity with advanced AGI support.

        Args:
            user_id: Unique identifier for the user/AI
            identity_type: Type of identity (human, AI, composite, etc.)
            tier_level: Initial tier level
            security_level: Quantum security level
            parent_identity_id: Parent identity for hierarchical AI systems

        Returns:
            QIUserContext with all quantum-proof components initialized
        """
        self.logger.info(f"Creating quantum identity for {user_id} ({identity_type.value})")

        # Generate quantum cryptographic components
        qi_key_id = None
        qi_signature = None
        collapse_hash = None
        qi_timestamp = None

        if QUANTUM_CRYPTO_AVAILABLE and self.qi_key_manager:
            try:
                # Generate quantum-safe key pair
                qi_key_id = await self._generate_quantum_key(user_id, security_level)

                # Create quantum timestamp
                qi_timestamp = self.qi_timestamp_manager.create_timestamp(
                    data={"user_id": user_id, "identity_type": identity_type.value}
                )

                # Generate collapse hash for identity creation decision
                identity_context = {
                    "user_id": user_id,
                    "identity_type": identity_type.value,
                    "tier_level": tier_level.value,
                    "security_level": security_level.value,
                    "timestamp": qi_timestamp,
                    "action": "identity_creation",
                }
                collapse_hash = self.collapse_hash_manager.generate_collapse_hash(identity_context)

            except Exception as e:
                self.logger.error(f"Failed to generate quantum components: {e}")

        # Determine resource quantum pool
        resource_quantum_pool = f"qi_pool_{tier_level.value}"

        # Create quantum user context
        context = QIUserContext(
            user_id=user_id,
            identity_type=identity_type,
            tier_level=tier_level,
            security_level=security_level,
            qi_key_id=qi_key_id,
            qi_signature=qi_signature,
            collapse_hash=collapse_hash,
            qi_timestamp=qi_timestamp,
            parent_identity_id=parent_identity_id,
            resource_quantum_pool=resource_quantum_pool,
        )

        # Handle hierarchical identity relationships
        if parent_identity_id:
            context.identity_generation = await self._calculate_identity_generation(parent_identity_id)
            self.identity_hierarchy[parent_identity_id].append(user_id)

            # Inherit some properties from parent
            if parent_identity_id in self.identity_cache:
                parent_context = self.identity_cache[parent_identity_id]
                context.ethical_alignment = min(1.0, parent_context.ethical_alignment + 0.1)
                context.intelligence_score = parent_context.intelligence_score

        # Allocate initial resources
        await self._allocate_tier_resources(context)

        # Store in cache and legacy system
        self.identity_cache[user_id] = context
        await self._sync_with_legacy_system(context)

        self.logger.info(f"Quantum identity created successfully for {user_id}")
        return context

    async def authenticate_quantum_identity(self, user_id: str, credentials: dict[str, Any]) -> Optional[QIUserContext]:
        """
        Authenticate user with quantum-proof verification.

        Args:
            user_id: User identifier
            credentials: Authentication credentials (quantum-enhanced)

        Returns:
            QIUserContext if authentication successful, None otherwise
        """
        self.logger.debug(f"Authenticating quantum identity for {user_id}")

        # Check cache first
        if user_id not in self.identity_cache:
            context = await self._load_identity_from_storage(user_id)
            if not context:
                self.logger.warning(f"Identity not found for {user_id}")
                return None
        else:
            context = self.identity_cache[user_id]

        # Quantum authentication
        if QUANTUM_CRYPTO_AVAILABLE and not await self._verify_quantum_credentials(context, credentials):
            self.logger.warning(f"Quantum authentication failed for {user_id}")
            return None

        # Update access time and analyze behavior
        context.last_accessed = datetime.now(timezone.utc)
        await self._analyze_behavior_patterns(context, credentials)

        # Check for tier promotion
        await self._evaluate_tier_promotion(context)

        self.logger.debug(f"Quantum authentication successful for {user_id}")
        return context

    async def authorize_colony_access(self, user_context: QIUserContext, colony_id: str, operation: str) -> bool:
        """
        Authorize access to colony operations based on quantum identity and tiers.

        Args:
            user_context: Quantum user context
            colony_id: Colony identifier
            operation: Operation being requested

        Returns:
            True if authorized, False otherwise
        """
        self.logger.debug(f"Authorizing colony access: {user_context.user_id} -> {colony_id}.{operation}")

        # Check basic tier requirements
        tier_limits = self.tier_resource_limits[user_context.tier_level]

        # Special checks for different colony types
        colony_requirements = {
            "consciousness": tier_limits.get("consciousness_access", False),
            "oracle": user_context.tier_level.value >= 1,  # Tier 1+ for oracle
            "quantum": user_context.tier_level.value >= 2,  # Tier 2+ for quantum operations
            "ethics": True,  # All tiers can access ethics
            "memory": True,  # All tiers can access basic memory
            "reasoning": True,  # All tiers can access basic reasoning
            "creativity": user_context.tier_level.value >= 1,  # Tier 1+ for creativity
        }

        # Check colony-specific requirements
        for colony_type, required in colony_requirements.items():
            if colony_type in colony_id.lower() and not required:
                self.logger.warning(f"Access denied: {user_context.user_id} lacks tier for {colony_type}")
                return False

        # Check resource availability
        if not await self._check_resource_availability(user_context, operation):
            self.logger.warning(f"Access denied: {user_context.user_id} lacks resources for {operation}")
            return False

        # Generate collapse hash for authorization decision
        if QUANTUM_CRYPTO_AVAILABLE and self.collapse_hash_manager:
            auth_context = {
                "user_id": user_context.user_id,
                "colony_id": colony_id,
                "operation": operation,
                "tier_level": user_context.tier_level.value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": "colony_authorization",
                "authorized": True,
            }
            collapse_hash = self.collapse_hash_manager.generate_collapse_hash(auth_context)
            self.logger.debug(f"Authorization collapse hash: {collapse_hash}")

        return True

    async def _generate_quantum_key(self, user_id: str, security_level: QISecurityLevel) -> str:
        """Generate quantum-safe cryptographic key."""
        if not self.qi_key_manager:
            return f"fallback_key_{hashlib.sha256(user_id.encode()).hexdigest()[:16]}"

        # Map quantum security level to NIST level
        nist_level_map = {
            QISecurityLevel.QUANTUM_BASIC: SecurityLevel.NIST_1,
            QISecurityLevel.QUANTUM_STANDARD: SecurityLevel.NIST_3,
            QISecurityLevel.QUANTUM_ADVANCED: SecurityLevel.NIST_5,
            QISecurityLevel.QUANTUM_FUTURE: SecurityLevel.NIST_5,  # Use highest available
        }

        nist_level = nist_level_map[security_level]
        key_pair = self.qi_key_manager.generate_key_pair(nist_level)
        key_id = f"qi_key_{user_id}_{int(time.time())}"

        # Store key pair (in production, this would be in secure storage)
        self.qi_key_manager.store_key_pair(key_id, key_pair)

        return key_id

    async def _verify_quantum_credentials(self, context: QIUserContext, credentials: dict[str, Any]) -> bool:
        """Verify quantum-proof credentials."""
        if not self.qi_key_manager or not context.qi_key_id:
            # Fallback to basic verification
            return credentials.get("user_id") == context.user_id

        try:
            # Verify quantum signature
            signature = credentials.get("qi_signature")
            message = credentials.get("message", "")

            if signature and message:
                return self.qi_key_manager.verify_signature(context.qi_key_id, message, signature)

            return False
        except Exception as e:
            self.logger.error(f"Quantum credential verification failed: {e}")
            return False

    async def _calculate_identity_generation(self, parent_identity_id: str) -> int:
        """Calculate identity generation for hierarchical AI systems."""
        if parent_identity_id not in self.identity_cache:
            return 1

        parent_context = self.identity_cache[parent_identity_id]
        return parent_context.identity_generation + 1

    async def _allocate_tier_resources(self, context: QIUserContext):
        """Allocate resources based on tier level."""
        tier_limits = self.tier_resource_limits[context.tier_level]
        pool = self.qi_resource_pools[context.resource_quantum_pool]

        # Allocate basic resources
        context.allocated_resources = {
            "requests_remaining": tier_limits["requests_per_minute"],
            "storage_available_mb": tier_limits["storage_mb"],
            "qi_operations_remaining": tier_limits["qi_operations"],
            "oracle_queries_remaining": tier_limits["oracle_queries"],
            "last_reset": datetime.now(timezone.utc).isoformat(),
        }

        # Add to pool
        pool["active_users"].append(context.user_id)
        pool["allocated_resources"][context.user_id] = context.allocated_resources

    async def _analyze_behavior_patterns(self, context: QIUserContext, credentials: dict[str, Any]):
        """Analyze user behavior patterns for dynamic tier adjustment."""
        # Track authentication patterns
        auth_time = datetime.now(timezone.utc)
        hour_of_day = auth_time.hour

        # Update behavior patterns
        context.behavior_patterns.setdefault("auth_hours", []).append(hour_of_day)
        context.behavior_patterns.setdefault("auth_frequency", 0)
        context.behavior_patterns["auth_frequency"] += 1

        # Analyze credential quality
        credential_strength = self._calculate_credential_strength(credentials)
        context.behavior_patterns["avg_credential_strength"] = (
            context.behavior_patterns.get("avg_credential_strength", 0.5) * 0.9 + credential_strength * 0.1
        )

        # Update trust score based on patterns
        consistency_score = self._calculate_consistency_score(context.behavior_patterns)
        security_score = context.behavior_patterns.get("avg_credential_strength", 0.5)

        context.trust_score = consistency_score * 0.6 + security_score * 0.4

    def _calculate_credential_strength(self, credentials: dict[str, Any]) -> float:
        """Calculate strength of provided credentials."""
        strength = 0.0

        # Check for quantum components
        if credentials.get("qi_signature"):
            strength += 0.4
        if credentials.get("biometric_data"):
            strength += 0.3
        if credentials.get("behavioral_pattern"):
            strength += 0.2
        if credentials.get("multi_factor"):
            strength += 0.1

        return min(1.0, strength)

    def _calculate_consistency_score(self, patterns: dict[str, Any]) -> float:
        """Calculate behavioral consistency score."""
        # Simplified consistency calculation
        auth_hours = patterns.get("auth_hours", [])
        if len(auth_hours) < 5:
            return 0.5  # Not enough data

        # Calculate standard deviation of auth hours
        import statistics

        try:
            std_dev = statistics.stdev(auth_hours[-10:])  # Last 10 auths
            consistency = max(0.0, 1.0 - (std_dev / 12.0))  # Normalize to 0-1
            return consistency
        except BaseException:
            return 0.5

    async def _evaluate_tier_promotion(self, context: QIUserContext):
        """Evaluate if user should be promoted to higher tier."""
        current_tier = context.tier_level

        # Don't auto-promote beyond tier 3 (requires manual review)
        if current_tier.value >= 3:
            return

        # Promotion criteria
        trust_threshold = 0.8
        intelligence_threshold = 0.7
        ethical_threshold = 0.9
        usage_threshold = 100  # Number of successful operations

        # Check criteria
        meets_trust = context.trust_score >= trust_threshold
        meets_intelligence = context.intelligence_score >= intelligence_threshold
        meets_ethics = context.ethical_alignment >= ethical_threshold
        meets_usage = context.behavior_patterns.get("auth_frequency", 0) >= usage_threshold

        if meets_trust and meets_intelligence and meets_ethics and meets_usage:
            # Promote to next tier
            new_tier = QITierLevel(current_tier.value + 1)
            await self._promote_user_tier(context, new_tier)

    async def _promote_user_tier(self, context: QIUserContext, new_tier: QITierLevel):
        """Promote user to higher tier."""
        old_tier = context.tier_level
        context.tier_level = new_tier

        # Update resource allocation
        old_pool = context.resource_quantum_pool
        new_pool = f"qi_pool_{new_tier.value}"
        context.resource_quantum_pool = new_pool

        # Reallocate resources
        await self._allocate_tier_resources(context)

        # Remove from old pool
        if old_pool in self.qi_resource_pools:
            pool = self.qi_resource_pools[old_pool]
            if context.user_id in pool["active_users"]:
                pool["active_users"].remove(context.user_id)
            pool["allocated_resources"].pop(context.user_id, None)

        # Record promotion
        promotion_record = {
            "user_id": context.user_id,
            "old_tier": old_tier.value,
            "new_tier": new_tier.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "reason": "automatic_promotion",
            "trust_score": context.trust_score,
            "intelligence_score": context.intelligence_score,
            "ethical_alignment": context.ethical_alignment,
        }
        self.tier_promotion_history.append(promotion_record)

        self.logger.info(f"User {context.user_id} promoted from {old_tier.name} to {new_tier.name}")

    async def _check_resource_availability(self, context: QIUserContext, operation: str) -> bool:
        """Check if user has sufficient resources for operation."""
        allocated = context.allocated_resources

        # Check requests per minute
        if allocated.get("requests_remaining", 0) <= 0:
            return False

        # Check operation-specific resources
        if "quantum" in operation.lower() and allocated.get("qi_operations_remaining", 0) <= 0:
            return False

        return not ("oracle" in operation.lower() and allocated.get("oracle_queries_remaining", 0) <= 0)

    async def _load_identity_from_storage(self, user_id: str) -> Optional[QIUserContext]:
        """Load identity from persistent storage."""
        # In production, this would load from distributed database
        # For now, try legacy system
        if self.legacy_identity_client:
            try:
                legacy_identity = self.legacy_identity_client.get_user_identity(user_id)
                if legacy_identity:
                    # Convert legacy identity to quantum context
                    return await self._convert_legacy_identity(legacy_identity)
            except Exception as e:
                self.logger.error(f"Failed to load legacy identity: {e}")

        return None

    async def _convert_legacy_identity(self, legacy_identity: dict[str, Any]) -> QIUserContext:
        """Convert legacy identity to quantum context."""
        # Map legacy tier to quantum tier
        legacy_tier = legacy_identity.get("tier", "LAMBDA_TIER_0")
        tier_mapping = {
            "LAMBDA_TIER_0": QITierLevel.QUANTUM_TIER_0,
            "LAMBDA_TIER_1": QITierLevel.QUANTUM_TIER_1,
            "LAMBDA_TIER_2": QITierLevel.QUANTUM_TIER_2,
            "LAMBDA_TIER_3": QITierLevel.QUANTUM_TIER_3,
            "LAMBDA_TIER_4": QITierLevel.QUANTUM_TIER_4,
            "LAMBDA_TIER_5": QITierLevel.QUANTUM_TIER_5,
        }

        qi_tier = tier_mapping.get(legacy_tier, QITierLevel.QUANTUM_TIER_0)

        # Create quantum context
        context = QIUserContext(
            user_id=legacy_identity["user_id"],
            identity_type=AGIIdentityType.HUMAN,  # Assume human for legacy
            tier_level=qi_tier,
            security_level=QISecurityLevel.QUANTUM_STANDARD,
            trust_score=legacy_identity.get("trust_score", 0.5),
            ethical_alignment=legacy_identity.get("ethical_alignment", 0.8),
        )

        return context

    async def _sync_with_legacy_system(self, context: QIUserContext):
        """Sync quantum identity with legacy system."""
        if not self.legacy_identity_client:
            return

        try:
            legacy_data = {
                "user_id": context.user_id,
                "tier": context.tier_level.lambda_tier,
                "trust_score": context.trust_score,
                "ethical_alignment": context.ethical_alignment,
                "last_accessed": context.last_accessed.isoformat(),
                "qi_enabled": True,
            }

            # Update legacy system (if method exists)
            if hasattr(self.legacy_identity_client, "update_user_identity"):
                self.legacy_identity_client.update_user_identity(context.user_id, legacy_data)
        except Exception as e:
            self.logger.error(f"Failed to sync with legacy system: {e}")

    def get_identity_stats(self) -> dict[str, Any]:
        """Get comprehensive identity system statistics."""
        stats = {
            "total_identities": len(self.identity_cache),
            "qi_crypto_enabled": QUANTUM_CRYPTO_AVAILABLE,
            "legacy_integration_enabled": self.legacy_identity_client is not None,
            "tier_distribution": defaultdict(int),
            "identity_type_distribution": defaultdict(int),
            "security_level_distribution": defaultdict(int),
            "recent_promotions": len(self.tier_promotion_history),
            "qi_pools": len(self.qi_resource_pools),
        }

        # Analyze identity distribution
        for context in self.identity_cache.values():
            stats["tier_distribution"][context.tier_level.name] += 1
            stats["identity_type_distribution"][context.identity_type.name] += 1
            stats["security_level_distribution"][context.security_level.name] += 1

        # Convert defaultdicts to regular dicts
        stats["tier_distribution"] = dict(stats["tier_distribution"])
        stats["identity_type_distribution"] = dict(stats["identity_type_distribution"])
        stats["security_level_distribution"] = dict(stats["security_level_distribution"])

        return stats


# Global quantum identity manager instance
_quantum_identity_manager: Optional[QIIdentityManager] = None


def get_quantum_identity_manager() -> QIIdentityManager:
    """Get global quantum identity manager instance."""
    global _quantum_identity_manager
    if _quantum_identity_manager is None:
        _quantum_identity_manager = QIIdentityManager()
    return _quantum_identity_manager


# Convenience functions for common operations
async def create_agi_identity(user_id: str, identity_type: AGIIdentityType = AGIIdentityType.HUMAN) -> QIUserContext:
    """Create AGI-ready identity with quantum security."""
    manager = get_quantum_identity_manager()
    return await manager.create_quantum_identity(user_id, identity_type)


async def authenticate_quantum_user(user_id: str, credentials: dict[str, Any]) -> Optional[QIUserContext]:
    """Authenticate user with quantum-proof verification."""
    manager = get_quantum_identity_manager()
    return await manager.authenticate_quantum_identity(user_id, credentials)


async def authorize_quantum_access(user_context: QIUserContext, colony_id: str, operation: str) -> bool:
    """Authorize colony access with quantum identity validation."""
    manager = get_quantum_identity_manager()
    return await manager.authorize_colony_access(user_context, colony_id, operation)
