"""
NIΛS Engine - Core processing engine for Non-Intrusive Advertising System
Coordinates emotional gating, symbolic processing, and message delivery
"""

import logging
import sys
import uuid
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__, timezone)


class EmotionalState(Enum):
    """Emotional states for gating decisions"""

    RECEPTIVE = "receptive"
    NEUTRAL = "neutral"
    STRESSED = "stressed"
    FOCUSED = "focused"
    OVERWHELMED = "overwhelmed"
    RELAXED = "relaxed"


class ProcessingPhase(Enum):
    """Processing phases in NIAS pipeline"""

    CONSENT_CHECK = "consent_check"
    EMOTIONAL_GATING = "emotional_gating"
    SYMBOLIC_PROCESSING = "symbolic_processing"
    TIER_FILTERING = "tier_filtering"
    WIDGET_GENERATION = "widget_generation"
    DELIVERY = "delivery"


class NIASEngine:
    """
    Core NIΛS processing engine that orchestrates the entire message delivery pipeline.

    Features:
    - Emotional state gating
    - Symbolic message processing
    - Lambda Products integration
    - Tier-aware processing
    - Event bus coordination
    """

    def __init__(self, event_bus=None):
        self.event_bus = event_bus
        self.processing_stats = {
            "messages_processed": 0,
            "messages_delivered": 0,
            "messages_blocked": 0,
            "messages_deferred": 0,
        }

        # Emotional gating configuration (legacy fallback)
        self.emotional_gating_config = self._initialize_emotional_gating()

        # Symbolic processing patterns
        self.symbolic_patterns = self._initialize_symbolic_patterns()

        # ΛBAS integration
        self.abas_adapter = None
        self._initialize_abas_integration()

        # DΛST integration
        self.dast_adapter = None
        self._initialize_dast_integration()

        # Message queue for deferred processing
        self.deferred_messages = {}

        logger.info("NIΛS Engine initialized with ΛBAS and DΛST integration")

    def _initialize_abas_integration(self):
        """Initialize ABAS adapter integration"""
        try:
            # Import ABAS adapter
            integration_path = Path(__file__).parent.parent / "integration"
            sys.path.insert(0, str(integration_path))

            from abas_adapter import get_abas_adapter

            self.abas_adapter = get_abas_adapter()

            if self.abas_adapter.is_abas_available():
                logger.info("ΛBAS integration active - real attention boundaries enabled")
            else:
                logger.info("ΛBAS integration available with fallback mode")

        except ImportError as e:
            logger.warning(f"ΛBAS integration not available: {e}")
            self.abas_adapter = None
        except Exception as e:
            logger.error(f"Error initializing ΛBAS integration: {e}")
            self.abas_adapter = None

    def _initialize_dast_integration(self):
        """Initialize DAST adapter integration"""
        try:
            # Import DAST adapter
            # Use proper relative import for better module resolution
            try:
                from ..integration.dast_adapter import get_dast_adapter
            except ImportError:
                # Fallback to path manipulation if needed
                integration_path = Path(__file__).parent.parent / "integration"
                sys.path.insert(0, str(integration_path))
                from dast_adapter import get_dast_adapter
            self.dast_adapter = get_dast_adapter()

            if self.dast_adapter.is_dast_available():
                logger.info("DΛST integration active - real symbolic context enabled")
            else:
                logger.info("DΛST integration available with fallback mode")

        except ImportError as e:
            logger.warning(f"DΛST integration not available: {e}")
            self.dast_adapter = None
        except Exception as e:
            logger.error(f"Error initializing DΛST integration: {e}")
            self.dast_adapter = None

    def _initialize_emotional_gating(self) -> dict[str, dict[str, Any]]:
        """Initialize emotional gating rules"""
        return {
            EmotionalState.RECEPTIVE.value: {
                "allow_delivery": True,
                "priority_boost": 1.2,
                "widget_enhancement": True,
                "optimal_timing": True,
            },
            EmotionalState.NEUTRAL.value: {
                "allow_delivery": True,
                "priority_boost": 1.0,
                "widget_enhancement": False,
                "optimal_timing": False,
            },
            EmotionalState.RELAXED.value: {
                "allow_delivery": True,
                "priority_boost": 1.1,
                "widget_enhancement": True,
                "optimal_timing": True,
                "preferred_types": ["dream_seeds", "gentle_recommendations"],
            },
            EmotionalState.FOCUSED.value: {
                "allow_delivery": False,
                "defer_duration_hours": 2,
                "exception_priority": 5,  # Only critical messages
                "reason": "User is focused - avoid interruption",
            },
            EmotionalState.STRESSED.value: {
                "allow_delivery": False,
                "defer_duration_hours": 4,
                "exception_priority": 5,
                "wellness_consideration": True,
                "reason": "User appears stressed - deferring for wellness",
            },
            EmotionalState.OVERWHELMED.value: {
                "allow_delivery": False,
                "defer_duration_hours": 8,
                "exception_priority": None,  # No exceptions
                "wellness_consideration": True,
                "reason": "User appears overwhelmed - extended deferral",
            },
        }

    def _initialize_symbolic_patterns(self) -> dict[str, dict[str, Any]]:
        """Initialize symbolic processing patterns for LUKHAS integration"""
        return {
            "color_symbolism": {
                "trust": ["#4a90e2", "#2e7d32", "#1976d2"],
                "energy": ["#ff5722", "#ff9800", "#f57c00"],
                "calm": ["#81c784", "#64b5f6", "#a5d6a7"],
                "luxury": ["#6a1b9a", "#bf9000", "#1a1a1a"],
                "nature": ["#4caf50", "#8bc34a", "#cddc39"],
            },
            "symbolic_elements": {
                "growth": ["🌱", "📈", "⬆️", "🚀"],
                "connection": ["🔗", "🌐", "🤝", "💫"],
                "discovery": ["🔍", "💡", "🧩", "🗝️"],
                "achievement": ["🏆", "⭐", "🎯", "✅"],
                "harmony": ["☯️", "🌸", "🕊️", "🌊"],
            },
            "emotional_mappings": {
                EmotionalState.RECEPTIVE.value: {
                    "colors": ["trust", "energy"],
                    "symbols": ["discovery", "growth"],
                    "tone": "enthusiastic",
                },
                EmotionalState.NEUTRAL.value: {
                    "colors": ["trust", "calm"],
                    "symbols": ["connection"],
                    "tone": "informative",
                },
                EmotionalState.RELAXED.value: {
                    "colors": ["calm", "nature"],
                    "symbols": ["harmony", "connection"],
                    "tone": "gentle",
                },
            },
        }

    async def process_message(self, message: dict[str, Any], user_context: dict[str, Any]) -> dict[str, Any]:
        """
        Process a message through the complete NIΛS pipeline.

        Args:
            message: Message to process
            user_context: User context including ID, tier, preferences

        Returns:
            Processing result with delivery status
        """
        user_id = user_context.get("user_id")
        tier = user_context.get("tier", "T3")

        processing_session = {
            "session_id": f"nias_proc_{uuid.uuid4().hex[:8]}",
            "message_id": message.get("message_id", f"msg_{uuid.uuid4().hex[:8]}"),
            "user_id": user_id,
            "tier": tier,
            "start_time": datetime.now(timezone.utc).isoformat(),
            "phases": {},
        }

        try:
            # Phase 1: Consent Check
            result = await self._phase_consent_check(message, user_context, processing_session)
            if not result["approved"]:
                return self._complete_processing(processing_session, result)

            # Phase 2: Emotional Gating
            result = await self._phase_emotional_gating(message, user_context, processing_session)
            if not result["approved"]:
                return self._complete_processing(processing_session, result)

            # Phase 3: Symbolic Processing
            result = await self._phase_symbolic_processing(message, user_context, processing_session)
            message = result["processed_message"]

            # Phase 4: Tier Filtering
            result = await self._phase_tier_filtering(message, user_context, processing_session)
            message = result["filtered_message"]

            # Phase 5: Widget Generation
            result = await self._phase_widget_generation(message, user_context, processing_session)

            # Phase 6: Delivery
            delivery_result = await self._phase_delivery(result, user_context, processing_session)

            return self._complete_processing(processing_session, delivery_result)

        except Exception as e:
            logger.error(f"Error processing message {processing_session['message_id']}: {e}")
            error_result = {"status": "error", "error": str(e), "phase": "unknown"}
            return self._complete_processing(processing_session, error_result)

    async def _phase_consent_check(
        self,
        message: dict[str, Any],
        user_context: dict[str, Any],
        session: dict[str, Any],
    ) -> dict[str, Any]:
        """Phase 1: Check user consent for message delivery"""
        phase_start = datetime.now(timezone.utc)

        try:
            # Import here to avoid circular imports
            from .consent_filter import get_consent_filter

            consent_filter = get_consent_filter()
            consent_result = await consent_filter.check_consent(user_context["user_id"], message)

            session["phases"][ProcessingPhase.CONSENT_CHECK.value] = {
                "start_time": phase_start.isoformat(),
                "duration_ms": (datetime.now(timezone.utc) - phase_start).total_seconds() * 1000,
                "result": consent_result,
            }

            if not consent_result.get("approved", False):
                return {
                    "approved": False,
                    "status": "blocked",
                    "reason": "consent_denied",
                    "phase": ProcessingPhase.CONSENT_CHECK.value,
                    "consent_result": consent_result,
                }

            return {"approved": True}

        except Exception as e:
            logger.error(f"Consent check failed: {e}")
            return {
                "approved": False,
                "status": "error",
                "reason": "consent_check_failed",
                "error": str(e),
            }

    async def _phase_emotional_gating(
        self,
        message: dict[str, Any],
        user_context: dict[str, Any],
        session: dict[str, Any],
    ) -> dict[str, Any]:
        """Phase 2: Check emotional state for appropriate timing using ΛBAS integration"""
        phase_start = datetime.now(timezone.utc)

        try:
            # Use ABAS adapter for attention-based gating if available
            if self.abas_adapter:
                user_id = user_context.get("user_id")
                if user_id:
                    try:
                        # Check attention availability through ABAS
                        abas_result = await self.abas_adapter.check_attention_availability(
                            user_id, message, user_context
                        )

                        session["phases"][ProcessingPhase.EMOTIONAL_GATING.value] = {
                            "start_time": phase_start.isoformat(),
                            "duration_ms": (datetime.now(timezone.utc) - phase_start).total_seconds() * 1000,
                            "emotional_state": abas_result.get("emotional_state"),
                            "attention_state": abas_result.get("attention_state"),
                            "abas_decision": abas_result.get("abas_decision"),
                            "lambda_trace": abas_result.get("lambda_trace"),
                        }

                        # Handle ABAS decision
                        if not abas_result["approved"]:
                            defer_until_str = abas_result.get("defer_until")
                            if defer_until_str:
                                defer_until = datetime.fromisoformat(defer_until_str)
                                await self._defer_message(message, user_context, defer_until)

                            return {
                                "approved": False,
                                "status": "deferred" if defer_until_str else "blocked",
                                "reason": abas_result.get("reason", "attention_boundary"),
                                "phase": ProcessingPhase.EMOTIONAL_GATING.value,
                                "defer_until": defer_until_str,
                                "emotional_state": abas_result.get("emotional_state"),
                                "attention_state": abas_result.get("attention_state"),
                                "confidence": abas_result.get("confidence"),
                                "lambda_trace": abas_result.get("lambda_trace"),
                            }

                        # Apply ABAS-informed enhancements
                        attention_state = abas_result.get("attention_state")
                        if attention_state in ["flow_state", "receptive"]:
                            message["attention_enhancement"] = {
                                "state": abas_result.get("emotional_state"),
                                "attention_state": attention_state,
                                "optimal_timing": True,
                                "confidence": abas_result.get("confidence"),
                                "lambda_trace": abas_result.get("lambda_trace"),
                            }

                        return {
                            "approved": True,
                            "emotional_state": abas_result.get("emotional_state"),
                            "attention_state": attention_state,
                            "abas_integration": True,
                        }

                    except Exception as e:
                        logger.warning(f"ΛBAS gating failed, using fallback: {e}")

            # Fallback to legacy emotional gating
            return await self._phase_emotional_gating_fallback(message, user_context, session, phase_start)

        except Exception as e:
            logger.error(f"Emotional gating failed: {e}")
            return {
                "approved": False,
                "status": "error",
                "reason": "emotional_gating_failed",
                "error": str(e),
            }

    async def _phase_emotional_gating_fallback(
        self,
        message: dict[str, Any],
        user_context: dict[str, Any],
        session: dict[str, Any],
        phase_start: datetime,
    ) -> dict[str, Any]:
        """Fallback emotional gating using legacy heuristics"""

        # Get user's current emotional state (fallback method)
        emotional_state = await self._assess_emotional_state(user_context)
        gating_config = self.emotional_gating_config.get(
            emotional_state, self.emotional_gating_config[EmotionalState.NEUTRAL.value]
        )

        session["phases"][ProcessingPhase.EMOTIONAL_GATING.value] = {
            "start_time": phase_start.isoformat(),
            "duration_ms": (datetime.now(timezone.utc) - phase_start).total_seconds() * 1000,
            "emotional_state": emotional_state,
            "gating_config": gating_config,
            "fallback_mode": True,
        }

        # Check if delivery is allowed
        if not gating_config.get("allow_delivery", True):
            # Check for priority exceptions
            message_priority = message.get("priority", 1)
            exception_priority = gating_config.get("exception_priority")

            if exception_priority is None or message_priority < exception_priority:
                # Defer the message
                defer_hours = gating_config.get("defer_duration_hours", 2)
                defer_until = datetime.now(timezone.utc) + timedelta(hours=defer_hours)

                await self._defer_message(message, user_context, defer_until)

                return {
                    "approved": False,
                    "status": "deferred",
                    "reason": gating_config.get("reason", "emotional_gating"),
                    "phase": ProcessingPhase.EMOTIONAL_GATING.value,
                    "defer_until": defer_until.isoformat(),
                    "emotional_state": emotional_state,
                }

        # Apply emotional enhancements if appropriate
        if gating_config.get("widget_enhancement", False):
            message["emotional_enhancement"] = {
                "state": emotional_state,
                "priority_boost": gating_config.get("priority_boost", 1.0),
                "optimal_timing": gating_config.get("optimal_timing", False),
            }

        return {"approved": True, "emotional_state": emotional_state}

    async def _phase_symbolic_processing(
        self,
        message: dict[str, Any],
        user_context: dict[str, Any],
        session: dict[str, Any],
    ) -> dict[str, Any]:
        """Phase 3: Apply symbolic processing using DΛST integration"""
        phase_start = datetime.now(timezone.utc)

        try:
            # Use DAST adapter for symbolic processing if available
            if self.dast_adapter:
                user_id = user_context.get("user_id")
                message_type = message.get("type")

                if user_id:
                    try:
                        # Get symbolic context from DAST
                        symbolic_context = await self.dast_adapter.get_symbolic_context(user_id, message_type)

                        # Enhanced symbolic processing with DAST
                        processed_message = message.copy()
                        processed_message["symbolic_processing"] = {
                            "symbolic_tags": symbolic_context.get("symbolic_tags", []),
                            "primary_activity": symbolic_context.get("primary_activity"),
                            "recommended_colors": symbolic_context.get("recommended_colors", []),
                            "recommended_symbols": symbolic_context.get("recommended_elements", []),
                            "recommended_tone": symbolic_context.get("recommended_tone", "neutral"),
                            "coherence_score": symbolic_context.get("coherence_score", 0.5),
                            "message_coherence": symbolic_context.get("message_coherence", 0.5),
                            "context_scores": symbolic_context.get("context_scores", {}),
                            "lambda_fingerprint": symbolic_context.get("lambda_fingerprint"),
                            "dast_integration": True,
                            "processed_at": datetime.now(timezone.utc).isoformat(),
                        }

                        # Apply LUKHAS symbolic authentication
                        if self._has_lukhas_integration():
                            processed_message["symbolic_auth"] = await self._apply_symbolic_auth(
                                processed_message, user_context
                            )

                        session["phases"][ProcessingPhase.SYMBOLIC_PROCESSING.value] = {
                            "start_time": phase_start.isoformat(),
                            "duration_ms": (datetime.now(timezone.utc) - phase_start).total_seconds() * 1000,
                            "dast_integration": True,
                            "symbolic_tags_count": len(symbolic_context.get("symbolic_tags", [])),
                            "primary_activity": symbolic_context.get("primary_activity"),
                            "coherence_score": symbolic_context.get("coherence_score"),
                            "message_coherence": symbolic_context.get("message_coherence"),
                            "lambda_fingerprint": symbolic_context.get("lambda_fingerprint"),
                        }

                        logger.debug(
                            f"DΛST symbolic processing for {user_id}: {len(symbolic_context.get('symbolic_tags', []))} symbols, coherence {symbolic_context.get('coherence_score', 0):.2f}"
                        )
                        return {"processed_message": processed_message}

                    except Exception as e:
                        logger.warning(f"DΛST symbolic processing failed, using fallback: {e}")

            # Fallback to legacy symbolic processing
            return await self._phase_symbolic_processing_fallback(message, user_context, session, phase_start)

        except Exception as e:
            logger.error(f"Symbolic processing failed: {e}")
            return {"processed_message": message}  # Return original on error

    async def _phase_symbolic_processing_fallback(
        self,
        message: dict[str, Any],
        user_context: dict[str, Any],
        session: dict[str, Any],
        phase_start: datetime,
    ) -> dict[str, Any]:
        """Fallback symbolic processing using legacy patterns"""

        emotional_state = session["phases"][ProcessingPhase.EMOTIONAL_GATING.value]["emotional_state"]

        # Apply symbolic mappings based on emotional state
        emotional_mapping = self.symbolic_patterns["emotional_mappings"].get(
            emotional_state,
            self.symbolic_patterns["emotional_mappings"][EmotionalState.NEUTRAL.value],
        )

        # Enhance message with symbolic elements
        processed_message = message.copy()
        processed_message["symbolic_processing"] = {
            "emotional_state": emotional_state,
            "recommended_colors": self._get_symbolic_colors(emotional_mapping["colors"]),
            "recommended_symbols": self._get_symbolic_elements(emotional_mapping["symbols"]),
            "recommended_tone": emotional_mapping["tone"],
            "dast_integration": False,
            "fallback_mode": True,
            "processed_at": datetime.now(timezone.utc).isoformat(),
        }

        # Apply LUKHAS symbolic authentication if available
        if self._has_lukhas_integration():
            processed_message["symbolic_auth"] = await self._apply_symbolic_auth(processed_message, user_context)

        session["phases"][ProcessingPhase.SYMBOLIC_PROCESSING.value] = {
            "start_time": phase_start.isoformat(),
            "duration_ms": (datetime.now(timezone.utc) - phase_start).total_seconds() * 1000,
            "emotional_mapping": emotional_mapping,
            "symbols_applied": len(processed_message["symbolic_processing"]["recommended_symbols"]),
            "dast_integration": False,
            "fallback_mode": True,
        }

        return {"processed_message": processed_message}

    async def _phase_tier_filtering(
        self,
        message: dict[str, Any],
        user_context: dict[str, Any],
        session: dict[str, Any],
    ) -> dict[str, Any]:
        """Phase 4: Apply tier-specific filtering"""
        phase_start = datetime.now(timezone.utc)

        try:
            from .tier_manager import get_tier_manager

            tier_manager = get_tier_manager()
            processing_config = await tier_manager.get_processing_config(user_context["tier"])
            filtered_message = await tier_manager.apply_tier_filters(message, processing_config)

            session["phases"][ProcessingPhase.TIER_FILTERING.value] = {
                "start_time": phase_start.isoformat(),
                "duration_ms": (datetime.now(timezone.utc) - phase_start).total_seconds() * 1000,
                "tier": user_context["tier"],
                "processing_config": processing_config["name"],
            }

            return {"filtered_message": filtered_message}

        except Exception as e:
            logger.error(f"Tier filtering failed: {e}")
            return {"filtered_message": message}  # Return original on error

    async def _phase_widget_generation(
        self,
        message: dict[str, Any],
        user_context: dict[str, Any],
        session: dict[str, Any],
    ) -> dict[str, Any]:
        """Phase 5: Generate appropriate widget for delivery"""
        phase_start = datetime.now(timezone.utc)

        try:
            from .widget_engine import get_widget_engine

            widget_engine = get_widget_engine()
            widget_config = await widget_engine.generate_widget(message, user_context, user_context["tier"])

            session["phases"][ProcessingPhase.WIDGET_GENERATION.value] = {
                "start_time": phase_start.isoformat(),
                "duration_ms": (datetime.now(timezone.utc) - phase_start).total_seconds() * 1000,
                "widget_type": widget_config.get("type", "unknown"),
                "widget_id": widget_config.get("widget_id"),
            }

            return {"widget_config": widget_config, "message": message}

        except Exception as e:
            logger.error(f"Widget generation failed: {e}")
            return {"widget_config": None, "message": message, "error": str(e)}

    async def _phase_delivery(
        self,
        delivery_data: dict[str, Any],
        user_context: dict[str, Any],
        session: dict[str, Any],
    ) -> dict[str, Any]:
        """Phase 6: Complete message delivery"""
        phase_start = datetime.now(timezone.utc)

        try:
            widget_config = delivery_data["widget_config"]
            message = delivery_data["message"]

            # Record dream seed if applicable
            if message.get("dream_seed"):
                await self._record_dream_seed(message, user_context)

            # Update DAST symbolic context based on successful delivery
            if self.dast_adapter:
                try:
                    user_id = user_context.get("user_id")
                    if user_id:
                        delivery_result = {"status": "delivered", "successful": True}
                        await self.dast_adapter.update_symbolic_context_from_message(user_id, message, delivery_result)
                        logger.debug(f"Updated DΛST context for {user_id} after successful delivery")
                except Exception as e:
                    logger.warning(f"Failed to update DΛST context after delivery: {e}")

            # Update processing stats
            self.processing_stats["messages_processed"] += 1
            self.processing_stats["messages_delivered"] += 1

            session["phases"][ProcessingPhase.DELIVERY.value] = {
                "start_time": phase_start.isoformat(),
                "duration_ms": (datetime.now(timezone.utc) - phase_start).total_seconds() * 1000,
                "delivery_method": "widget" if widget_config else "basic",
                "dast_context_updated": self.dast_adapter is not None,
            }

            return {
                "status": "delivered",
                "widget_config": widget_config,
                "message": message,
                "delivery_method": "widget" if widget_config else "basic",
            }

        except Exception as e:
            logger.error(f"Delivery failed: {e}")
            self.processing_stats["messages_processed"] += 1
            return {
                "status": "error",
                "error": str(e),
                "phase": ProcessingPhase.DELIVERY.value,
            }

    def _complete_processing(self, session: dict[str, Any], final_result: dict[str, Any]) -> dict[str, Any]:
        """Complete processing session with final result"""
        session["end_time"] = datetime.now(timezone.utc).isoformat()
        session["total_duration_ms"] = (
            datetime.fromisoformat(session["end_time"]) - datetime.fromisoformat(session["start_time"])
        ).total_seconds() * 1000
        session["final_result"] = final_result

        # Update stats based on result
        status = final_result.get("status", "unknown")
        if status == "blocked":
            self.processing_stats["messages_blocked"] += 1
        elif status == "deferred":
            self.processing_stats["messages_deferred"] += 1

        return {
            **final_result,
            "processing_session": session,
            "processed_at": session["end_time"],
        }

    async def _assess_emotional_state(self, user_context: dict[str, Any]) -> str:
        """Assess user's current emotional state using ΛBAS integration"""
        if self.abas_adapter:
            try:
                # Use ABAS adapter to get attention status
                user_id = user_context.get("user_id")
                if user_id:
                    # Register user if needed
                    if user_id not in self.abas_adapter.registered_users:
                        await self.abas_adapter.register_user(user_id)

                    # Get attention analytics from ABAS
                    abas_status = await self.abas_adapter.get_attention_analytics(user_id)

                    if "error" not in abas_status:
                        attention_state = abas_status.get("attention_state", "available")
                        # Map attention state to emotional state
                        emotional_state = self.abas_adapter.attention_to_emotional_mapping.get(
                            attention_state, "neutral"
                        )
                        logger.debug(f"ΛBAS mapped {attention_state} -> {emotional_state} for {user_id}")
                        return emotional_state

            except Exception as e:
                logger.warning(f"ΛBAS assessment failed, using fallback: {e}")

        # Fallback to legacy heuristic-based assessment
        return self._assess_emotional_state_fallback(user_context)

    def _assess_emotional_state_fallback(self, user_context: dict[str, Any]) -> str:
        """Fallback emotional state assessment (legacy heuristics)"""
        # Check for stress indicators
        recent_interactions = user_context.get("recent_interactions", [])
        if len(recent_interactions) > 10:  # High interaction volume
            return EmotionalState.OVERWHELMED.value

        # Check time of day
        current_hour = datetime.now(timezone.utc).hour
        if 9 <= current_hour <= 17:  # Work hours
            return EmotionalState.FOCUSED.value
        elif 20 <= current_hour <= 22:  # Evening relaxation
            return EmotionalState.RELAXED.value

        # Default to neutral
        return EmotionalState.NEUTRAL.value

    def _get_symbolic_colors(self, color_categories: list[str]) -> list[str]:
        """Get symbolic colors for given categories"""
        colors = []
        for category in color_categories:
            colors.extend(self.symbolic_patterns["color_symbolism"].get(category, []))
        return colors[:3]  # Limit to 3 colors

    def _get_symbolic_elements(self, element_categories: list[str]) -> list[str]:
        """Get symbolic elements for given categories"""
        elements = []
        for category in element_categories:
            elements.extend(self.symbolic_patterns["symbolic_elements"].get(category, []))
        return elements[:4]  # Limit to 4 elements

    def _has_lukhas_integration(self) -> bool:
        """Check if LUKHAS symbolic integration is available"""
        # Placeholder for actual LUKHAS integration check
        return False

    async def _apply_symbolic_auth(self, message: dict[str, Any], user_context: dict[str, Any]) -> dict[str, Any]:
        """Apply LUKHAS symbolic authentication"""
        # Placeholder for ΛSYMBOLIC integration
        return {
            "authenticated": True,
            "symbolic_signature": f"lukhas_sym_{uuid.uuid4().hex[:8]}",
            "auth_timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def _defer_message(
        self,
        message: dict[str, Any],
        user_context: dict[str, Any],
        defer_until: datetime,
    ):
        """Defer message for later processing"""
        defer_id = f"defer_{uuid.uuid4().hex[:8]}"

        self.deferred_messages[defer_id] = {
            "defer_id": defer_id,
            "message": message,
            "user_context": user_context,
            "deferred_at": datetime.now(timezone.utc).isoformat(),
            "defer_until": defer_until.isoformat(),
            "retry_count": 0,
        }

        logger.info(f"Message deferred until {defer_until.isoformat()}: {defer_id}")

    async def _record_dream_seed(self, message: dict[str, Any], user_context: dict[str, Any]):
        """Record dream seed for dream system integration"""
        try:
            from .dream_recorder import get_dream_recorder

            dream_recorder = get_dream_recorder()
            dream_seed_data = message.get("dream_seed", {})

            await dream_recorder.record_dream_seed(
                brand_id=message.get("brand_id", "unknown"),
                dream_seed=dream_seed_data,
                user_id=user_context["user_id"],
                consent_context={"consent_verified": True},
            )
        except Exception as e:
            logger.error(f"Failed to record dream seed: {e}")

    async def check_emotional_state(self, user_context: dict[str, Any]) -> dict[str, Any]:
        """Public method to check emotional state (used by NIAS Hub) with ΛBAS integration"""
        if self.abas_adapter:
            try:
                user_id = user_context.get("user_id")
                if user_id:
                    # Create a simple message for checking state
                    test_message = {
                        "message_id": f"state_check_{user_id}",
                        "type": "notification",
                        "priority": 3,
                        "description": "State check",
                    }

                    # Use ABAS adapter for comprehensive state check
                    abas_result = await self.abas_adapter.check_attention_availability(
                        user_id, test_message, user_context
                    )

                    return {
                        "approved": abas_result["approved"],
                        "emotional_state": abas_result.get("emotional_state"),
                        "attention_state": abas_result.get("attention_state"),
                        "defer_until": abas_result.get("defer_until"),
                        "confidence": abas_result.get("confidence"),
                        "abas_integration": True,
                        "lambda_trace": abas_result.get("lambda_trace"),
                    }
            except Exception as e:
                logger.warning(f"ΛBAS state check failed, using fallback: {e}")

        # Fallback to legacy emotional state assessment
        emotional_state = await self._assess_emotional_state(user_context)
        gating_config = self.emotional_gating_config.get(
            emotional_state, self.emotional_gating_config[EmotionalState.NEUTRAL.value]
        )

        return {
            "approved": gating_config.get("allow_delivery", True),
            "emotional_state": emotional_state,
            "defer_until": (
                (datetime.now(timezone.utc) + timedelta(hours=gating_config.get("defer_duration_hours", 0))).isoformat()
                if not gating_config.get("allow_delivery", True)
                else None
            ),
            "abas_integration": False,
        }

    async def process_deferred_messages(self):
        """Process messages that were deferred and are now ready"""
        current_time = datetime.now(timezone.utc)
        ready_messages = []

        for defer_id, deferred_data in list(self.deferred_messages.items()):
            defer_until = datetime.fromisoformat(deferred_data["defer_until"])
            if current_time >= defer_until:
                ready_messages.append((defer_id, deferred_data))
                del self.deferred_messages[defer_id]

        for defer_id, deferred_data in ready_messages:
            try:
                logger.info(f"Processing deferred message: {defer_id}")
                await self.process_message(deferred_data["message"], deferred_data["user_context"])
            except Exception as e:
                logger.error(f"Failed to process deferred message {defer_id}: {e}")

    async def get_processing_stats(self) -> dict[str, Any]:
        """Get NIAS engine processing statistics"""
        return {
            **self.processing_stats,
            "deferred_messages_count": len(self.deferred_messages),
            "emotional_states_configured": len(self.emotional_gating_config),
            "symbolic_patterns_available": len(self.symbolic_patterns),
        }

    async def health_check(self) -> dict[str, Any]:
        """Health check for NIAS engine"""
        health_data = {
            "status": "healthy",
            "processing_stats": self.processing_stats,
            "deferred_messages": len(self.deferred_messages),
            "event_bus_connected": self.event_bus is not None,
            "emotional_gating_enabled": len(self.emotional_gating_config) > 0,
            "abas_integration": {
                "available": self.abas_adapter is not None,
                "active": False,
                "mode": "disabled",
            },
            "dast_integration": {
                "available": self.dast_adapter is not None,
                "active": False,
                "mode": "disabled",
            },
        }

        # Add ABAS integration details
        if self.abas_adapter:
            try:
                integration_status = self.abas_adapter.get_integration_status()
                health_data["abas_integration"] = {
                    "available": True,
                    "active": integration_status.get("abas_available", False),
                    "mode": integration_status.get("integration_mode", "unknown"),
                    "registered_users": integration_status.get("registered_users", 0),
                }
            except Exception as e:
                health_data["abas_integration"]["error"] = str(e)

        # Add DAST integration details
        if self.dast_adapter:
            try:
                integration_status = self.dast_adapter.get_integration_status()
                health_data["dast_integration"] = {
                    "available": True,
                    "active": integration_status.get("dast_available", False),
                    "mode": integration_status.get("integration_mode", "unknown"),
                    "registered_users": integration_status.get("registered_users", 0),
                }
            except Exception as e:
                health_data["dast_integration"]["error"] = str(e)

        return health_data


# Global NIAS engine instance
_global_nias_engine = None


def get_nias_engine(event_bus=None) -> NIASEngine:
    """Get the global NIAS engine instance"""
    global _global_nias_engine
    if _global_nias_engine is None:
        _global_nias_engine = NIASEngine(event_bus=event_bus)
    return _global_nias_engine
