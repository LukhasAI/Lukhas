#!/usr/bin/env python3
"""
NIΛS Dream Commerce Orchestrator - Complete integration of dream-based advertising system
Orchestrates all NIAS components for commercial dream delivery
Part of the Lambda Products Suite by LUKHAS AI
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

from .consent_manager import ConsentManager
from .dream_generator import BioRhythm, DreamContext, DreamGenerator, DreamMood, GeneratedDream
from .emotional_filter import EmotionalFilter
from .nias_core import (
    ConsentLevel,
    DeliveryResult,
    EmotionalState,
    MessageTier,
    SymbolicMessage,
    UserContext,
)
from .user_data_integrator import UserDataIntegrator, UserDataProfile
from .vendor_portal import DreamSeed, DreamSeedType, VendorPortal

# Set up logger first
logger = logging.getLogger("Lambda.NIΛS.DreamCommerce")

# Import all NIAS components

# Import ABAS and DAST integration
try:
    from ..ABAS.core import ABASCore
    from ..DAST.core import DASTCore

    INTEGRATION_AVAILABLE = True
except ImportError:
    INTEGRATION_AVAILABLE = False
    logger.warning("ABAS/DAST integration not available")


class DeliveryChannel(Enum):
    """Dream delivery channels"""

    VISUAL = "visual"  # Screen-based delivery
    AUDIO = "audio"  # Voice/audio delivery
    HAPTIC = "haptic"  # Tactile feedback
    AMBIENT = "ambient"  # Environmental/IoT
    NEURAL = "neural"  # Direct neural (future)


class DreamDeliveryTiming(Enum):
    """Optimal timing for dream delivery"""

    IMMEDIATE = "immediate"
    QUEUED = "queued"
    SCHEDULED = "scheduled"
    BIO_OPTIMAL = "bio_optimal"
    DREAM_STATE = "dream_state"


@dataclass
class DreamCommerceSession:
    """Active dream commerce session"""

    session_id: str
    user_id: str
    started_at: datetime
    dreams_delivered: list[str] = field(default_factory=list)
    vendor_interactions: dict[str, list] = field(default_factory=dict)
    conversion_events: list[dict] = field(default_factory=list)
    emotional_trajectory: list[dict] = field(default_factory=list)
    active: bool = True


@dataclass
class DreamDeliveryRequest:
    """Request for dream delivery"""

    user_id: str
    vendor_seed: Optional[DreamSeed] = None
    timing: DreamDeliveryTiming = DreamDeliveryTiming.BIO_OPTIMAL
    channel: DeliveryChannel = DeliveryChannel.VISUAL
    context_data: dict[str, Any] = field(default_factory=dict)
    priority: int = 5  # 1-10, higher is more priority


class DreamCommerceOrchestrator:
    """
    Master orchestrator for NIΛS Dream Commerce System

    Integrates:
    - User data and consent management
    - Vendor portal and dream seeds
    - AI-powered dream generation
    - Bio-rhythm aware delivery
    - Emotional state filtering
    - One-click commerce
    - Performance tracking
    """

    def __init__(self, config: Optional[dict] = None):
        self.config = config or self._default_config()

        # Initialize all components
        self.consent_manager = ConsentManager()
        self.user_data_integrator = UserDataIntegrator(self.consent_manager)
        self.vendor_portal = VendorPortal(consent_manager=self.consent_manager)
        self.dream_generator = DreamGenerator()
        self.emotional_filter = EmotionalFilter()

        # Integration components (if available)
        if INTEGRATION_AVAILABLE:
            self.abas = ABASCore()
            self.dast = DASTCore()
        else:
            self.abas = None
            self.dast = None

        # Session management
        self.active_sessions: dict[str, DreamCommerceSession] = {}
        self.delivery_queue: list[DreamDeliveryRequest] = []
        self.dream_cache: dict[str, GeneratedDream] = {}

        # Metrics tracking
        self.metrics = {
            "dreams_generated": 0,
            "dreams_delivered": 0,
            "conversions": 0,
            "ethical_blocks": 0,
            "consent_denials": 0,
        }

        # Start background processors
        self._start_background_tasks()

        logger.info("NIΛS Dream Commerce Orchestrator initialized")

    def _default_config(self) -> dict:
        """Default orchestrator configuration"""
        return {
            "max_dreams_per_session": 3,
            "session_timeout_minutes": 30,
            "bio_rhythm_checking": True,
            "emotional_filtering": True,
            "ethical_validation": True,
            "one_click_enabled": True,
            "delivery_retry_attempts": 3,
            "cache_duration_minutes": 60,
            "performance_tracking": True,
        }

    def _start_background_tasks(self):
        """Start background processing tasks"""
        asyncio.create_task(self._process_delivery_queue())
        asyncio.create_task(self._monitor_sessions())
        asyncio.create_task(self._update_bio_rhythms())

    async def initiate_dream_commerce(self, user_id: str) -> dict[str, Any]:
        """
        Initiate a dream commerce session for a user

        Args:
            user_id: User identifier

        Returns:
            Session initialization result
        """
        try:
            # Check if user has active session
            if user_id in self.active_sessions:
                session = self.active_sessions[user_id]
                if session.active:
                    return {
                        "status": "existing_session",
                        "session_id": session.session_id,
                    }

            # Verify consent
            consent_status = await self.consent_manager.get_consent_status(user_id)
            if not consent_status["has_consent"]:
                self.metrics["consent_denials"] += 1
                return {
                    "status": "consent_required",
                    "consent_url": f"https://consent.nias.ai/user/{user_id}",
                }

            # Get user profile
            user_profile = await self.user_data_integrator.get_user_profile(user_id)

            # Check emotional state
            emotional_check = await self._check_emotional_readiness(user_id, user_profile)
            if not emotional_check["ready"]:
                self.metrics["ethical_blocks"] += 1
                return {
                    "status": "deferred",
                    "reason": emotional_check["reason"],
                    "retry_after": emotional_check.get("retry_after"),
                }

            # Create new session
            session_id = f"dcs_{user_id}_{datetime.now(timezone.utc).timestamp()}"
            session = DreamCommerceSession(session_id=session_id, user_id=user_id, started_at=datetime.now(timezone.utc))

            self.active_sessions[user_id] = session

            # Queue initial dream generation
            await self._queue_dream_generation(user_id, user_profile)

            logger.info(f"Dream commerce session initiated: {session_id}")

            return {
                "status": "initiated",
                "session_id": session_id,
                "bio_rhythm": self._get_current_bio_rhythm().value,
                "emotional_state": emotional_check.get("state", "unknown"),
            }

        except Exception as e:
            logger.error(f"Error initiating dream commerce: {e}")
            return {"status": "error", "message": str(e)}

    async def deliver_vendor_dream(self, user_id: str, vendor_id: str, seed_id: str) -> dict[str, Any]:
        """
        Deliver a specific vendor dream to user

        Args:
            user_id: User identifier
            vendor_id: Vendor identifier
            seed_id: Dream seed identifier

        Returns:
            Delivery result
        """
        try:
            # Verify vendor and seed
            vendor_seeds = self.vendor_portal.dream_seeds.get(vendor_id, [])
            seed = next((s for s in vendor_seeds if s.seed_id == seed_id), None)

            if not seed:
                return {"status": "error", "message": "Dream seed not found"}

            if not seed.is_valid():
                return {"status": "error", "message": "Dream seed expired or invalid"}

            # Check vendor consent
            has_vendor_consent = await self.consent_manager.check_vendor_permission(user_id, vendor_id)

            if not has_vendor_consent:
                return {
                    "status": "consent_required",
                    "vendor": vendor_id,
                    "consent_url": f"https://consent.nias.ai/vendor/{vendor_id}",
                }

            # Get user profile
            user_profile = await self.user_data_integrator.get_user_profile(user_id)

            # Create dream context
            context = await self._create_dream_context(user_id, user_profile, seed)

            # Generate dream
            dream = await self.dream_generator.generate_dream(context)

            # Validate ethics
            if dream.ethical_score < self.config.get("min_ethical_score", 0.8):
                self.metrics["ethical_blocks"] += 1
                logger.warning(f"Dream blocked due to low ethical score: {dream.ethical_score}")
                return {"status": "blocked", "reason": "ethical_validation_failed"}

            # Deliver dream
            delivery_result = await self._deliver_dream(user_id, dream, seed)

            # Track performance
            if delivery_result["delivered"]:
                self.metrics["dreams_delivered"] += 1
                await self.vendor_portal.update_seed_performance(
                    seed_id, "impression", {"user_segment": user_profile.tier}
                )

                # Update session
                if user_id in self.active_sessions:
                    session = self.active_sessions[user_id]
                    session.dreams_delivered.append(dream.dream_id)

                    if vendor_id not in session.vendor_interactions:
                        session.vendor_interactions[vendor_id] = []
                    session.vendor_interactions[vendor_id].append(
                        {
                            "seed_id": seed_id,
                            "dream_id": dream.dream_id,
                            "delivered_at": datetime.now(timezone.utc).isoformat(),
                        }
                    )

            return {
                "status": "delivered" if delivery_result["delivered"] else "failed",
                "dream_id": dream.dream_id,
                "delivery_result": delivery_result,
            }

        except Exception as e:
            logger.error(f"Error delivering vendor dream: {e}")
            return {"status": "error", "message": str(e)}

    async def process_user_action(self, user_id: str, action: str, action_data: dict[str, Any]) -> dict[str, Any]:
        """
        Process user action on delivered dream

        Args:
            user_id: User identifier
            action: Action type (click, dismiss, save, purchase)
            action_data: Action details

        Returns:
            Processing result
        """
        try:
            dream_id = action_data.get("dream_id")

            if action == "click":
                # Track click
                seed_id = action_data.get("seed_id")
                if seed_id:
                    await self.vendor_portal.update_seed_performance(seed_id, "click", {"user_id": user_id})

                # Generate affiliate link
                vendor_id = action_data.get("vendor_id")
                product_id = action_data.get("product_id")

                if vendor_id and product_id:
                    user_profile = await self.user_data_integrator.get_user_profile(user_id)
                    affiliate_link = await self.vendor_portal.generate_affiliate_link(
                        vendor_id, product_id, user_profile.__dict__
                    )

                    return {
                        "status": "success",
                        "action": "click",
                        "affiliate_link": affiliate_link,
                        "one_click_ready": True,
                    }

            elif action == "purchase":
                # Track conversion
                seed_id = action_data.get("seed_id")
                amount = action_data.get("amount", 0)

                if seed_id:
                    await self.vendor_portal.update_seed_performance(seed_id, "conversion", {"amount": amount})

                self.metrics["conversions"] += 1

                # Update session
                if user_id in self.active_sessions:
                    session = self.active_sessions[user_id]
                    session.conversion_events.append(
                        {
                            "dream_id": dream_id,
                            "seed_id": seed_id,
                            "amount": amount,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        }
                    )

                return {"status": "success", "action": "purchase", "tracked": True}

            elif action == "dismiss":
                # Track dismissal for learning
                reason = action_data.get("reason", "user_choice")

                # Update user preferences
                await self._update_user_preferences(user_id, {"dismissed_dream": dream_id, "reason": reason})

                return {
                    "status": "success",
                    "action": "dismiss",
                    "learning_updated": True,
                }

            elif action == "save":
                # Save dream for later
                await self._save_dream_for_user(user_id, dream_id)

                return {"status": "success", "action": "save", "saved": True}

            return {"status": "unknown_action", "action": action}

        except Exception as e:
            logger.error(f"Error processing user action: {e}")
            return {"status": "error", "message": str(e)}

    async def _check_emotional_readiness(self, user_id: str, user_profile: UserDataProfile) -> dict[str, Any]:
        """Check if user is emotionally ready for dream delivery"""
        # Get current emotional state
        emotional_state = user_profile.current_context.get("emotional_state", {})

        # Check stress level
        stress_level = emotional_state.get("stress", 0)
        if stress_level > 0.7:
            return {
                "ready": False,
                "reason": "high_stress",
                "state": "stressed",
                "retry_after": datetime.now(timezone.utc) + timedelta(hours=2),
            }

        # Check with ABAS if available
        if self.abas:
            abas_check = await self.abas.check_emotional_capacity(user_id)
            if not abas_check.get("has_capacity", True):
                return {
                    "ready": False,
                    "reason": "insufficient_emotional_capacity",
                    "state": abas_check.get("state", "unknown"),
                }

        # Check attention capacity
        attention = emotional_state.get("attention_capacity", 1.0)
        if attention < 0.3:
            return {
                "ready": False,
                "reason": "low_attention",
                "state": "distracted",
                "retry_after": datetime.now(timezone.utc) + timedelta(minutes=30),
            }

        return {
            "ready": True,
            "state": "ready",
            "stress": stress_level,
            "attention": attention,
        }

    async def _create_dream_context(
        self,
        user_id: str,
        user_profile: UserDataProfile,
        seed: Optional[DreamSeed] = None,
    ) -> DreamContext:
        """Create dream generation context"""
        # Determine mood based on emotional state
        emotional_state = user_profile.current_context.get("emotional_state", {})
        mood = self._determine_mood(emotional_state)

        # Get bio rhythm
        bio_rhythm = self._get_current_bio_rhythm()

        # Extract personal data (privacy-filtered)
        personal_data = {
            "interests": user_profile.interests[:5],
            "recent_searches": user_profile.activity_patterns.get("recent_searches", [])[:3],
            "upcoming_events": user_profile.contextual_triggers.get("upcoming_events", [])[:2],
        }

        # Get recent events
        recent_events = user_profile.activity_patterns.get("recent_activity", [])[:5]

        # Create context
        context = DreamContext(
            user_id=user_id,
            user_profile=user_profile.__dict__,
            vendor_seed=seed,
            mood=mood,
            bio_rhythm=bio_rhythm,
            personal_data=personal_data,
            recent_events=recent_events,
            preferences=user_profile.preferences,
            ethical_constraints={
                "max_stress": 0.2,
                "require_positive": True,
                "respect_boundaries": True,
            },
        )

        return context

    def _determine_mood(self, emotional_state: dict[str, float]) -> DreamMood:
        """Determine dream mood from emotional state"""
        joy = emotional_state.get("joy", 0.5)
        calm = emotional_state.get("calm", 0.5)
        stress = emotional_state.get("stress", 0)
        longing = emotional_state.get("longing", 0.3)

        # Prioritize based on emotional levels
        if stress > 0.5:
            return DreamMood.COMFORTING
        elif joy > 0.7:
            return DreamMood.CELEBRATORY
        elif calm > 0.7:
            return DreamMood.SERENE
        elif longing > 0.6:
            return DreamMood.NOSTALGIC
        elif joy > 0.5 and calm < 0.5:
            return DreamMood.ADVENTUROUS
        else:
            return DreamMood.SERENE

    def _get_current_bio_rhythm(self) -> BioRhythm:
        """Get current biological rhythm based on time"""
        current_hour = datetime.now(timezone.utc).hour

        if 6 <= current_hour < 10:
            return BioRhythm.MORNING_PEAK
        elif 10 <= current_hour < 14:
            return BioRhythm.MIDDAY_FLOW
        elif 14 <= current_hour < 17:
            return BioRhythm.AFTERNOON_DIP
        elif 17 <= current_hour < 21:
            return BioRhythm.EVENING_WIND
        elif 21 <= current_hour < 24:
            return BioRhythm.NIGHT_QUIET
        else:
            return BioRhythm.DEEP_NIGHT

    async def _deliver_dream(
        self, user_id: str, dream: GeneratedDream, seed: Optional[DreamSeed] = None
    ) -> dict[str, Any]:
        """Deliver dream to user through appropriate channel"""
        try:
            # Create symbolic message
            message = SymbolicMessage(
                id=dream.dream_id,
                content=dream.narrative,
                tags=dream.symbolism,
                tier=MessageTier.CREATIVE,
                emotional_tone=EmotionalState.DREAMING,
                intensity=0.5,
                dream_based=True,
                consent_required=ConsentLevel.DREAM_AWARE,
                metadata={
                    "image_url": dream.image_url,
                    "call_to_action": dream.call_to_action,
                    "vendor_seed": seed.seed_id if seed else None,
                },
            )

            # Get user context
            UserContext(
                user_id=user_id,
                tier=MessageTier.CREATIVE,
                consent_level=ConsentLevel.DREAM_AWARE,
                emotional_vector=dream.emotional_profile,
                current_tags=dream.symbolism,
                dream_residue=True,
            )

            # Deliver through appropriate channel
            # This would integrate with actual delivery systems
            delivery_result = DeliveryResult(
                status="delivered",
                message_id=message.id,
                reason="Success",
                delivery_method="visual",
                timestamp=datetime.now(timezone.utc),
            )

            return {
                "delivered": delivery_result.status == "delivered",
                "channel": delivery_result.delivery_method,
                "message_id": delivery_result.message_id,
                "dream_content": {
                    "narrative": dream.narrative[:200] + "...",
                    "image": dream.image_url,
                    "action": dream.call_to_action,
                },
            }

        except Exception as e:
            logger.error(f"Error delivering dream: {e}")
            return {"delivered": False, "error": str(e)}

    async def _queue_dream_generation(self, user_id: str, user_profile: UserDataProfile):
        """Queue dream generation for user"""
        # Find relevant vendor seeds
        relevant_seeds = await self._find_relevant_seeds(user_profile)

        # Create delivery requests
        for seed in relevant_seeds[:3]:  # Limit to 3 seeds
            request = DreamDeliveryRequest(
                user_id=user_id,
                vendor_seed=seed,
                timing=DreamDeliveryTiming.BIO_OPTIMAL,
                channel=DeliveryChannel.VISUAL,
                priority=self._calculate_priority(seed, user_profile),
            )
            self.delivery_queue.append(request)

    async def _find_relevant_seeds(self, user_profile: UserDataProfile) -> list[DreamSeed]:
        """Find relevant vendor seeds for user"""
        relevant_seeds = []

        for seeds in self.vendor_portal.dream_seeds.values():
            for seed in seeds:
                if not seed.is_valid():
                    continue

                # Check targeting criteria
                relevance_score = self._calculate_relevance(seed, user_profile)
                if relevance_score > 0.5:
                    relevant_seeds.append((seed, relevance_score))

        # Sort by relevance
        relevant_seeds.sort(key=lambda x: x[1], reverse=True)

        return [seed for seed, _ in relevant_seeds[:10]]

    def _calculate_relevance(self, seed: DreamSeed, user_profile: UserDataProfile) -> float:
        """Calculate relevance score for seed and user"""
        score = 0.5  # Base score

        # Check interests overlap
        seed_categories = seed.targeting_criteria.get("interests", [])
        user_interests = user_profile.interests

        if seed_categories and user_interests:
            overlap = len(set(seed_categories) & set(user_interests))
            score += (overlap / len(seed_categories)) * 0.3

        # Check for contextual triggers
        if seed.seed_type == DreamSeedType.SEASONAL:
            # Check if seasonal timing matches
            current_season = self._get_current_season()
            if seed.targeting_criteria.get("season") == current_season:
                score += 0.2

        elif seed.seed_type == DreamSeedType.REPLENISHMENT:
            # Check purchase patterns
            if "replenishment" in user_profile.activity_patterns:
                score += 0.3

        # Emotional alignment
        user_emotional = user_profile.current_context.get("emotional_state", {})
        seed_emotional = seed.emotional_triggers

        emotional_alignment = 1.0 - abs(user_emotional.get("stress", 0) - seed_emotional.get("stress", 0))
        score += emotional_alignment * 0.2

        return min(1.0, score)

    def _calculate_priority(self, seed: DreamSeed, user_profile: UserDataProfile) -> int:
        """Calculate delivery priority"""
        priority = 5  # Default

        # Increase priority for time-sensitive offers
        if seed.expiry:
            days_until_expiry = (seed.expiry - datetime.now(timezone.utc)).days
            if days_until_expiry < 2:
                priority += 3
            elif days_until_expiry < 7:
                priority += 1

        # Adjust based on user tier
        if user_profile.tier == "premium":
            priority += 1

        return min(10, priority)

    def _get_current_season(self) -> str:
        """Get current season"""
        month = datetime.now(timezone.utc).month
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "fall"

    async def _update_user_preferences(self, user_id: str, update_data: dict[str, Any]):
        """Update user preferences based on actions"""
        # This would update the user's preference learning model

    async def _save_dream_for_user(self, user_id: str, dream_id: str):
        """Save dream to user's collection"""
        # This would save the dream for later viewing

    async def _process_delivery_queue(self):
        """Background task to process delivery queue"""
        while True:
            try:
                if self.delivery_queue:
                    # Sort by priority
                    self.delivery_queue.sort(key=lambda x: x.priority, reverse=True)

                    # Process top request
                    request = self.delivery_queue.pop(0)

                    # Check timing
                    if request.timing == DreamDeliveryTiming.BIO_OPTIMAL:
                        bio_rhythm = self._get_current_bio_rhythm()
                        if bio_rhythm not in [
                            BioRhythm.MORNING_PEAK,
                            BioRhythm.EVENING_WIND,
                        ]:
                            # Re-queue for better time
                            self.delivery_queue.append(request)
                            await asyncio.sleep(60)  # Check again in a minute
                            continue

                    # Process delivery
                    await self.deliver_vendor_dream(
                        request.user_id,
                        request.vendor_seed.vendor_id if request.vendor_seed else None,
                        request.vendor_seed.seed_id if request.vendor_seed else None,
                    )

                await asyncio.sleep(10)  # Process queue every 10 seconds

            except Exception as e:
                logger.error(f"Error processing delivery queue: {e}")
                await asyncio.sleep(30)

    async def _monitor_sessions(self):
        """Monitor and clean up inactive sessions"""
        while True:
            try:
                current_time = datetime.now(timezone.utc)
                timeout_duration = timedelta(minutes=self.config["session_timeout_minutes"])

                for user_id, session in list(self.active_sessions.items()):
                    if current_time - session.started_at > timeout_duration:
                        session.active = False
                        logger.info(f"Session timeout for user {user_id}")

                        # Archive session data
                        # This would save session data for analytics

                        del self.active_sessions[user_id]

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"Error monitoring sessions: {e}")
                await asyncio.sleep(60)

    async def _update_bio_rhythms(self):
        """Update bio rhythm calculations periodically"""
        while True:
            try:
                # This would update bio rhythm calculations for all active users
                await asyncio.sleep(3600)  # Update every hour

            except Exception as e:
                logger.error(f"Error updating bio rhythms: {e}")
                await asyncio.sleep(3600)

    def get_system_metrics(self) -> dict[str, Any]:
        """Get system metrics and performance data"""
        return {
            "active_sessions": len(self.active_sessions),
            "queue_size": len(self.delivery_queue),
            "cached_dreams": len(self.dream_cache),
            "metrics": self.metrics,
            "vendor_count": len(self.vendor_portal.vendors),
            "total_seeds": sum(len(seeds) for seeds in self.vendor_portal.dream_seeds.values()),
            "bio_rhythm": self._get_current_bio_rhythm().value,
            "system_status": "operational",
        }
