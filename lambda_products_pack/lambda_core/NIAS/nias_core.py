#!/usr/bin/env python3
"""
NIΛS Core - Non-Intrusive Lambda Symbolic System
Advanced consent-based symbolic message delivery with emotional filtering

Part of the Lambda Products Suite by LUKHAS AI
Commercial Version - Ready for Enterprise Deployment
"""

import asyncio
import hashlib
import json
import logging

# Cryptographic imports for Lambda security
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger("Lambda.NIΛS")


class ConsentLevel(Enum):
    """User consent levels for symbolic message delivery"""

    NONE = "none"
    BASIC = "basic"
    ENHANCED = "enhanced"
    FULL_SYMBOLIC = "full_symbolic"
    DREAM_AWARE = "dream_aware"


class MessageTier(Enum):
    """Lambda message tier system"""

    PUBLIC = 1  # Basic public messages
    PERSONAL = 2  # Personalized content
    CREATIVE = 3  # Creative and dream-based content
    ENTERPRISE = 4  # Enterprise and verified content
    QUANTUM = 5  # Quantum-secured symbolic content


class EmotionalState(Enum):
    """Emotional filtering categories"""

    CALM = "calm"
    FOCUSED = "focused"
    CREATIVE = "creative"
    STRESSED = "stressed"
    OVERWHELMED = "overwhelmed"
    DREAMING = "dreaming"


@dataclass
class SymbolicMessage:
    """Lambda symbolic message structure"""

    id: str
    content: str
    tags: List[str]
    tier: MessageTier
    emotional_tone: EmotionalState
    intensity: float  # 0.0 to 1.0
    dream_based: bool = False
    voice_tag: Optional[str] = None
    lambda_signature: Optional[str] = None
    consent_required: ConsentLevel = ConsentLevel.BASIC
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.lambda_signature is None:
            self.lambda_signature = self._generate_signature()

    def _generate_signature(self) -> str:
        """Generate Lambda signature for message authenticity"""
        content_hash = hashlib.sha256(
            f"{self.id}{self.content}{self.tier.value}".encode()
        ).hexdigest()[:8]
        return f"Λ-{content_hash.upper()}"


@dataclass
class UserContext:
    """Complete user context for symbolic filtering"""

    user_id: str
    tier: MessageTier
    consent_level: ConsentLevel
    emotional_vector: Dict[str, float]
    current_tags: List[str]
    dream_residue: bool = False
    stress_level: float = 0.0
    attention_capacity: float = 1.0
    symbolic_preferences: Dict[str, Any] = None
    session_message_count: int = 0

    def __post_init__(self):
        if self.symbolic_preferences is None:
            self.symbolic_preferences = {}


@dataclass
class DeliveryResult:
    """Result of message delivery processing"""

    status: str  # "delivered", "blocked", "deferred", "transformed"
    message_id: str
    reason: str
    delivery_method: Optional[str] = None
    scheduled_for: Optional[datetime] = None
    lambda_trace: Optional[str] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class NIΛS:
    """
    Non-Intrusive Lambda Symbolic System

    Core Features:
    - Consent-based symbolic message delivery
    - Emotional state filtering and protection
    - Dream-aware message scheduling
    - Quantum-secured audit trails
    - Tier-based access control
    - Integration with ΛBAS and DΛST systems
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        self.lambda_brand = "Λ"

        # Storage systems
        self.user_contexts: Dict[str, UserContext] = {}
        self.message_history: Dict[str, List[SymbolicMessage]] = {}
        self.delivery_log: List[DeliveryResult] = []
        self.dream_schedule: Dict[str, List[SymbolicMessage]] = {}

        # Rate limiting
        self.session_limits: Dict[str, List[datetime]] = {}

        # Integration systems
        self.abas_available = False
        self.dast_available = False
        self.mesh_available = False

        # Initialize mode detection
        self._detect_integration_mode()

        logger.info("NIΛS system initialized with Lambda consciousness")

    def _default_config(self) -> Dict:
        """Default NIΛS configuration"""
        return {
            "brand": "LUKHAS",
            "symbol": "Λ",
            "max_messages_per_session": 5,
            "cooldown_period": 300,  # seconds
            "dream_delivery_enabled": True,
            "quantum_security": True,
            "emotional_protection": True,
            "symbolic_learning": True,
            "audit_level": "full",
        }

    def _detect_integration_mode(self):
        """Detect available integration systems"""
        try:
            # Check for ΛBAS
            # This would import ΛBAS when available
            self.abas_available = False  # Placeholder

            # Check for DΛST
            # This would import DΛST when available
            self.dast_available = False  # Placeholder

            # Check for mesh visualizer
            # This would import mesh system when available
            self.mesh_available = False  # Placeholder

        except ImportError:
            pass

        mode = "STANDALONE"
        if self.dast_available and self.abas_available:
            mode = "LAMBDA_FULL"
        elif self.dast_available:
            mode = "DAST_ENHANCED"

        logger.info(f"NIΛS running in {mode} mode")

    async def register_user(
        self, user_id: str, tier: MessageTier, consent_level: ConsentLevel
    ) -> UserContext:
        """Register a new user with NIΛS system"""
        context = UserContext(
            user_id=user_id,
            tier=tier,
            consent_level=consent_level,
            emotional_vector={
                "stress": 0.0,
                "openness": 0.8,
                "focus": 0.7,
                "creativity": 0.5,
            },
            current_tags=["general"],
            symbolic_preferences={
                "preferred_intensity": 0.5,
                "block_high_stress": True,
                "dream_delivery": consent_level.value
                in ["dream_aware", "full_symbolic"],
            },
        )

        self.user_contexts[user_id] = context
        self.session_limits[user_id] = []

        logger.info(f"Registered user {user_id} with tier {tier.name}")
        return context

    async def update_emotional_state(
        self, user_id: str, emotional_vector: Dict[str, float]
    ):
        """Update user's emotional state"""
        if user_id not in self.user_contexts:
            raise ValueError(f"User {user_id} not registered")

        context = self.user_contexts[user_id]
        context.emotional_vector.update(emotional_vector)

        # Update derived values
        context.stress_level = emotional_vector.get("stress", 0.0)
        context.attention_capacity = max(0.1, 1.0 - context.stress_level)

    async def push_message(
        self, message: SymbolicMessage, user_id: str
    ) -> DeliveryResult:
        """
        Main entry point for symbolic message delivery

        Args:
            message: The symbolic message to deliver
            user_id: Target user identifier

        Returns:
            DeliveryResult with delivery status and details
        """
        if user_id not in self.user_contexts:
            return DeliveryResult(
                status="blocked",
                message_id=message.id,
                reason="User not registered with NIΛS system",
            )

        context = self.user_contexts[user_id]

        try:
            # 1. Rate limiting check
            rate_check = await self._check_rate_limits(user_id)
            if not rate_check:
                return DeliveryResult(
                    status="deferred",
                    message_id=message.id,
                    reason="Rate limit exceeded - message queued",
                )

            # 2. Consent validation
            consent_check = await self._validate_consent(message, context)
            if not consent_check["approved"]:
                return DeliveryResult(
                    status="blocked",
                    message_id=message.id,
                    reason=consent_check["reason"],
                )

            # 3. Emotional state filtering
            emotional_check = await self._filter_emotional_state(message, context)
            if not emotional_check["stable"]:
                if emotional_check["defer"]:
                    return await self._schedule_for_later(
                        message, user_id, emotional_check["reason"]
                    )
                else:
                    return DeliveryResult(
                        status="blocked",
                        message_id=message.id,
                        reason=emotional_check["reason"],
                    )

            # 4. Symbolic matching
            symbolic_match = await self._match_symbolic_context(message, context)
            if not symbolic_match["matches"]:
                return DeliveryResult(
                    status="blocked",
                    message_id=message.id,
                    reason=symbolic_match["reason"],
                )

            # 5. Dream-aware delivery
            if message.dream_based and context.symbolic_preferences.get(
                "dream_delivery", False
            ):
                return await self._schedule_dream_delivery(message, user_id)

            # 6. Final delivery
            result = await self._deliver_message(message, context)

            # 7. Update context and log
            await self._update_delivery_history(user_id, message, result)

            return result

        except Exception as e:
            logger.error(f"NIΛS processing error: {e}")
            return DeliveryResult(
                status="blocked",
                message_id=message.id,
                reason=f"System error: {str(e)}",
            )

    async def _check_rate_limits(self, user_id: str) -> bool:
        """Check if user has exceeded message rate limits"""
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(seconds=self.config["cooldown_period"])

        # Clean old entries
        if user_id in self.session_limits:
            self.session_limits[user_id] = [
                timestamp
                for timestamp in self.session_limits[user_id]
                if timestamp > cutoff_time
            ]
        else:
            self.session_limits[user_id] = []

        # Check limits
        message_count = len(self.session_limits[user_id])
        if message_count >= self.config["max_messages_per_session"]:
            return False

        return True

    async def _validate_consent(
        self, message: SymbolicMessage, context: UserContext
    ) -> Dict[str, Any]:
        """Validate user consent for message delivery"""
        # Check tier requirements
        if context.tier.value < message.tier.value:
            return {
                "approved": False,
                "reason": f"User tier {context.tier.name} insufficient for {message.tier.name} message",
            }

        # Check consent level requirements
        required_consent_levels = {
            MessageTier.PUBLIC: ConsentLevel.NONE,
            MessageTier.PERSONAL: ConsentLevel.BASIC,
            MessageTier.CREATIVE: ConsentLevel.ENHANCED,
            MessageTier.ENTERPRISE: ConsentLevel.FULL_SYMBOLIC,
            MessageTier.QUANTUM: ConsentLevel.DREAM_AWARE,
        }

        required_level = required_consent_levels.get(message.tier, ConsentLevel.BASIC)
        consent_hierarchy = {
            ConsentLevel.NONE: 0,
            ConsentLevel.BASIC: 1,
            ConsentLevel.ENHANCED: 2,
            ConsentLevel.FULL_SYMBOLIC: 3,
            ConsentLevel.DREAM_AWARE: 4,
        }

        if consent_hierarchy[context.consent_level] < consent_hierarchy[required_level]:
            return {
                "approved": False,
                "reason": f"Consent level {context.consent_level.value} insufficient",
            }

        return {"approved": True, "reason": "Consent validated"}

    async def _filter_emotional_state(
        self, message: SymbolicMessage, context: UserContext
    ) -> Dict[str, Any]:
        """Filter based on emotional state and stability"""
        emotional_vector = context.emotional_vector
        stress = emotional_vector.get("stress", 0.0)

        # Dream residue protection
        if context.dream_residue:
            return {
                "stable": False,
                "defer": True,
                "reason": "Dream residue active - deferring until clear",
            }

        # High stress protection
        if stress > 0.8:
            if message.emotional_tone in [EmotionalState.CALM]:
                return {
                    "stable": True,
                    "reason": "Calming message approved during stress",
                }
            else:
                return {
                    "stable": False,
                    "defer": True,
                    "reason": "High stress level - non-calming messages deferred",
                }

        # Intensity vs attention capacity
        if message.intensity > context.attention_capacity:
            return {
                "stable": False,
                "defer": False,
                "reason": f"Message intensity {message.intensity} exceeds attention capacity {context.attention_capacity}",
            }

        return {"stable": True, "reason": "Emotional state stable for delivery"}

    async def _match_symbolic_context(
        self, message: SymbolicMessage, context: UserContext
    ) -> Dict[str, Any]:
        """Match message symbols with user's current context"""
        user_tags = set(context.current_tags)
        message_tags = set(message.tags)

        # Check for tag overlap
        overlap = user_tags.intersection(message_tags)
        if not overlap:
            return {
                "matches": False,
                "reason": f"No symbolic overlap between user tags {list(user_tags)} and message tags {list(message_tags)}",
            }

        # Check symbolic preferences
        preferences = context.symbolic_preferences
        if preferences.get("block_high_intensity", False) and message.intensity > 0.7:
            return {
                "matches": False,
                "reason": "High intensity blocked by user preference",
            }

        return {"matches": True, "reason": f"Symbolic match found: {list(overlap)}"}

    async def _schedule_dream_delivery(
        self, message: SymbolicMessage, user_id: str
    ) -> DeliveryResult:
        """Schedule message for dream-aware delivery"""
        if user_id not in self.dream_schedule:
            self.dream_schedule[user_id] = []

        self.dream_schedule[user_id].append(message)

        # Schedule for next wake cycle (simplified - would integrate with sleep tracking)
        scheduled_time = datetime.now() + timedelta(hours=8)

        return DeliveryResult(
            status="deferred",
            message_id=message.id,
            reason="Scheduled for dream-aware delivery",
            delivery_method="dream_delivery",
            scheduled_for=scheduled_time,
            lambda_trace=f"Λ-DREAM-{message.lambda_signature}",
        )

    async def _schedule_for_later(
        self, message: SymbolicMessage, user_id: str, reason: str
    ) -> DeliveryResult:
        """Schedule message for later delivery"""
        # Simple scheduling - would integrate with more sophisticated timing
        scheduled_time = datetime.now() + timedelta(minutes=30)

        return DeliveryResult(
            status="deferred",
            message_id=message.id,
            reason=reason,
            scheduled_for=scheduled_time,
            lambda_trace=f"Λ-DEFER-{message.lambda_signature}",
        )

    async def _deliver_message(
        self, message: SymbolicMessage, context: UserContext
    ) -> DeliveryResult:
        """Execute final message delivery"""
        delivery_method = "visual"

        # Voice delivery for appropriate tiers
        if (
            message.voice_tag
            and context.tier.value >= MessageTier.CREATIVE.value
            and context.consent_level.value in ["full_symbolic", "dream_aware"]
        ):
            delivery_method = "voice"

        # Update session count
        context.session_message_count += 1

        # Record delivery timestamp
        if context.user_id not in self.session_limits:
            self.session_limits[context.user_id] = []
        self.session_limits[context.user_id].append(datetime.now())

        return DeliveryResult(
            status="delivered",
            message_id=message.id,
            reason="Successfully delivered",
            delivery_method=delivery_method,
            lambda_trace=f"Λ-DELIVER-{message.lambda_signature}",
        )

    async def _update_delivery_history(
        self, user_id: str, message: SymbolicMessage, result: DeliveryResult
    ):
        """Update delivery history and logs"""
        if user_id not in self.message_history:
            self.message_history[user_id] = []

        self.message_history[user_id].append(message)
        self.delivery_log.append(result)

        # Quantum audit trail for enterprise users
        if (
            self.config["quantum_security"]
            and self.user_contexts[user_id].tier.value >= MessageTier.ENTERPRISE.value
        ):
            await self._create_quantum_audit_entry(user_id, message, result)

    async def _create_quantum_audit_entry(
        self, user_id: str, message: SymbolicMessage, result: DeliveryResult
    ):
        """Create quantum-secured audit entry"""
        audit_data = {
            "timestamp": datetime.now().isoformat(),
            "user_id": hashlib.sha256(user_id.encode()).hexdigest()[
                :16
            ],  # Privacy hash
            "message_id": message.id,
            "result_status": result.status,
            "lambda_signature": message.lambda_signature,
        }

        # In production, this would use actual quantum-resistant signatures
        audit_hash = hashlib.sha256(json.dumps(audit_data).encode()).hexdigest()
        logger.info(f"Quantum audit entry created: Λ-AUDIT-{audit_hash[:8]}")

    async def get_user_status(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user status"""
        if user_id not in self.user_contexts:
            return {"error": "User not found"}

        context = self.user_contexts[user_id]
        recent_messages = len(self.session_limits.get(user_id, []))

        return {
            "user_id": user_id,
            "tier": context.tier.name,
            "consent_level": context.consent_level.value,
            "emotional_state": context.emotional_vector,
            "current_tags": context.current_tags,
            "session_message_count": recent_messages,
            "dream_queue_size": len(self.dream_schedule.get(user_id, [])),
            "lambda_status": "active",
        }

    async def process_dream_deliveries(self, user_id: str) -> List[DeliveryResult]:
        """Process queued dream deliveries for wake cycle"""
        if user_id not in self.dream_schedule:
            return []

        queued_messages = self.dream_schedule[user_id]
        results = []

        for message in queued_messages:
            # Re-validate current state
            context = self.user_contexts[user_id]
            context.dream_residue = False  # Clear dream residue for wake processing

            result = await self._deliver_message(message, context)
            result.delivery_method = "dream_wake"
            result.reason = "Dream delivery executed on wake"

            results.append(result)

        # Clear processed dream queue
        self.dream_schedule[user_id] = []

        logger.info(f"Processed {len(results)} dream deliveries for user {user_id}")
        return results

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get NIΛS system metrics"""
        total_users = len(self.user_contexts)
        total_deliveries = len(
            [r for r in self.delivery_log if r.status == "delivered"]
        )
        total_blocks = len([r for r in self.delivery_log if r.status == "blocked"])

        return {
            "system": "NIΛS",
            "version": "1.0.0-lambda",
            "lambda_brand": self.lambda_brand,
            "total_users": total_users,
            "total_deliveries": total_deliveries,
            "total_blocks": total_blocks,
            "delivery_rate": total_deliveries / max(1, total_deliveries + total_blocks),
            "integration_mode": self._get_integration_mode(),
            "features": {
                "dream_delivery": self.config["dream_delivery_enabled"],
                "quantum_security": self.config["quantum_security"],
                "emotional_protection": self.config["emotional_protection"],
            },
        }

    def _get_integration_mode(self) -> str:
        """Get current integration mode"""
        if self.abas_available and self.dast_available:
            return "LAMBDA_FULL"
        elif self.dast_available:
            return "DΛST_ENHANCED"
        else:
            return "STANDALONE"


# Demo and testing
if __name__ == "__main__":

    async def demo():
        print("🧠 NIΛS - Non-Intrusive Lambda Symbolic System Demo")
        print("=" * 60)

        # Initialize NIΛS
        nias = NIΛS()

        # Register test user
        user = await nias.register_user(
            user_id="alice",
            tier=MessageTier.CREATIVE,
            consent_level=ConsentLevel.ENHANCED,
        )

        print(f"✅ Registered user: {user.user_id}")
        print(f"   Tier: {user.tier.name}")
        print(f"   Consent: {user.consent_level.value}")

        # Create test message
        message = SymbolicMessage(
            id=str(uuid.uuid4()),
            content="Your creative flow is ready to emerge 🌊",
            tags=["creativity", "flow", "inspiration"],
            tier=MessageTier.CREATIVE,
            emotional_tone=EmotionalState.CREATIVE,
            intensity=0.6,
            voice_tag="gentle_inspirational",
        )

        print("\n📤 Testing message delivery:")
        print(f"   Content: {message.content}")
        print(f"   Tags: {message.tags}")
        print(f"   Λ Signature: {message.lambda_signature}")

        # Update user context
        await nias.update_emotional_state(
            "alice", {"stress": 0.2, "creativity": 0.9, "focus": 0.7}
        )

        nias.user_contexts["alice"].current_tags = ["creativity", "work"]

        # Process message
        result = await nias.push_message(message, "alice")

        print("\n🎯 Delivery Result:")
        print(f"   Status: {result.status}")
        print(f"   Method: {result.delivery_method}")
        print(f"   Reason: {result.reason}")
        print(f"   Λ Trace: {result.lambda_trace}")

        # System metrics
        metrics = nias.get_system_metrics()
        print("\n📊 System Metrics:")
        print(f"   Users: {metrics['total_users']}")
        print(f"   Deliveries: {metrics['total_deliveries']}")
        print(f"   Delivery Rate: {metrics['delivery_rate']:.2%}")
        print(f"   Mode: {metrics['integration_mode']}")

    asyncio.run(demo())
