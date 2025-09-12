"""
Unified Three-Way System Orchestration
Coordinates NIΛS, ΛBAS, and DΛST for complete intelligent message delivery
"""

from datetime import timezone

import logging
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Import integrations
try:
    from .abas_adapter import get_abas_adapter
    from .dast_adapter import get_dast_adapter

    ADAPTERS_AVAILABLE = True
except ImportError:
    ADAPTERS_AVAILABLE = False

# Import NIAS components
nias_path = Path(__file__).parent.parent
sys.path.insert(0, str(nias_path))

try:
    from lukhas.core.nias_engine import get_nias_engine

    NIAS_AVAILABLE = True
except ImportError:
    NIAS_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class UnifiedProcessingContext:
    """Complete processing context for three-way integration"""

    user_id: str
    message: dict[str, Any]
    user_context: dict[str, Any]
    session_id: str

    # Integration states
    abas_available: bool = False
    dast_available: bool = False
    nias_available: bool = False

    # Processing results
    symbolic_context: Optional[dict[str, Any]] = None
    attention_decision: Optional[dict[str, Any]] = None
    delivery_result: Optional[dict[str, Any]] = None

    # Performance metrics
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_processing_time_ms: float = 0.0

    # Lambda signatures
    lambda_trace: str = ""

    def __post_init__(self):
        if self.start_time is None:
            self.start_time = datetime.now(timezone.utc)
        if not self.lambda_trace:
            import hashlib

            trace_data = f"{self.session_id}{self.user_id}{self.start_time.isoformat()}"
            trace_hash = hashlib.sha256(trace_data.encode()).hexdigest()[:12]
            self.lambda_trace = f"Λ-UNIFIED-{trace_hash.upper()}"


class UnifiedMessageProcessor:
    """
    Unified processor coordinating NIΛS, ΛBAS, and DΛST for intelligent message delivery.

    This represents the complete three-way integration architecture where:
    - DΛST provides symbolic context and activity tracking
    - ΛBAS makes attention boundary decisions based on symbolic context
    - NIΛS handles final message processing and delivery
    - All systems work together with shared context and decision making
    """

    def __init__(self):
        self.session_counter = 0

        # Initialize adapters
        self.abas_adapter = None
        self.dast_adapter = None
        self.nias_engine = None

        # Integration status
        self.integrations_initialized = False
        self.system_health = {"abas": False, "dast": False, "nias": False}

        # Performance tracking
        self.processing_stats = {
            "total_requests": 0,
            "successful_deliveries": 0,
            "blocked_messages": 0,
            "deferred_messages": 0,
            "integration_errors": 0,
            "average_processing_time_ms": 0.0,
        }

        self._initialize_integrations()

        logger.info("Unified Message Processor initialized for NIΛS-ΛBAS-DΛST orchestration")

    def _initialize_integrations(self):
        """Initialize all three system integrations"""
        try:
            # Initialize ABAS adapter
            if ADAPTERS_AVAILABLE:
                try:
                    self.abas_adapter = get_abas_adapter()
                    self.system_health["abas"] = self.abas_adapter.is_abas_available()
                    logger.info(f"ΛBAS adapter initialized: {self.system_health['abas']}")
                except Exception as e:
                    logger.warning(f"ΛBAS adapter initialization failed: {e}")

                # Initialize DAST adapter
                try:
                    self.dast_adapter = get_dast_adapter()
                    self.system_health["dast"] = self.dast_adapter.is_dast_available()
                    logger.info(f"DΛST adapter initialized: {self.system_health['dast']}")
                except Exception as e:
                    logger.warning(f"DΛST adapter initialization failed: {e}")

            # Initialize NIAS engine
            if NIAS_AVAILABLE:
                try:
                    self.nias_engine = get_nias_engine()
                    self.system_health["nias"] = True
                    logger.info("NIΛS engine initialized")
                except Exception as e:
                    logger.warning(f"NIΛS engine initialization failed: {e}")

            self.integrations_initialized = any(self.system_health.values())

            if self.integrations_initialized:
                logger.info("Unified processor ready - three-way integration active")
            else:
                logger.warning("No integrations available - unified processor running in fallback mode")

        except Exception as e:
            logger.error(f"Failed to initialize integrations: {e}")
            self.integrations_initialized = False

    async def process_message(
        self, user_id: str, message: dict[str, Any], user_context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Process message through complete NIΛS-ΛBAS-DΛST pipeline.

        This is the main entry point for unified three-way processing:
        1. DΛST analyzes symbolic context
        2. ΛBAS makes attention boundary decisions using DΛST context
        3. NIΛS processes message with full context and ΛBAS approval

        Args:
            user_id: User identifier
            message: Message to process
            user_context: User context including preferences, tier, etc.

        Returns:
            Complete processing result with all integration data
        """

        self.session_counter += 1
        session_id = f"unified_{self.session_counter}_{uuid.uuid4().hex[:8]}"

        # Create unified processing context
        context = UnifiedProcessingContext(
            user_id=user_id,
            message=message,
            user_context=user_context,
            session_id=session_id,
            abas_available=self.system_health["abas"],
            dast_available=self.system_health["dast"],
            nias_available=self.system_health["nias"],
        )

        try:
            self.processing_stats["total_requests"] += 1

            logger.info(f"Starting unified processing: {session_id} for user {user_id}")

            # Phase 1: DΛST Symbolic Analysis
            if context.dast_available and self.dast_adapter:
                context.symbolic_context = await self._phase_dast_analysis(context)
            else:
                context.symbolic_context = self._fallback_symbolic_context(context)

            # Phase 2: ΛBAS Attention Decision with DΛST context
            if context.abas_available and self.abas_adapter:
                context.attention_decision = await self._phase_abas_decision(context)
            else:
                context.attention_decision = self._fallback_attention_decision(context)

            # Phase 3: Handle ΛBAS Decision
            if not context.attention_decision.get("approved", False):
                return self._handle_non_approved_message(context)

            # Phase 4: NIΛS Processing with Full Context
            if context.nias_available and self.nias_engine:
                context.delivery_result = await self._phase_nias_processing(context)
            else:
                context.delivery_result = self._fallback_nias_processing(context)

            # Phase 5: Update symbolic context based on delivery result
            if context.dast_available and self.dast_adapter and context.delivery_result.get("status") == "delivered":
                await self._phase_update_symbolic_context(context)

            # Finalize processing
            return self._finalize_processing(context)

        except Exception as e:
            logger.error(f"Unified processing failed for {session_id}: {e}")
            self.processing_stats["integration_errors"] += 1

            return self._handle_processing_error(context, e)

    async def _phase_dast_analysis(self, context: UnifiedProcessingContext) -> dict[str, Any]:
        """Phase 1: DΛST Symbolic Context Analysis"""
        logger.debug(f"DΛST analysis for {context.user_id}")

        try:
            # Register user if needed
            if context.user_id not in self.dast_adapter.registered_users:
                await self.dast_adapter.register_user(context.user_id)

            # Get comprehensive symbolic context
            symbolic_context = await self.dast_adapter.get_symbolic_context(
                context.user_id, context.message.get("type")
            )

            # Enhance with activity suggestions
            activity_suggestions = await self.dast_adapter.get_activity_suggestions(context.user_id, symbolic_context)

            symbolic_context["activity_suggestions"] = activity_suggestions
            symbolic_context["dast_phase_success"] = True

            logger.debug(
                f"DΛST provided {len(symbolic_context.get('symbolic_tags', []))} symbols for {context.user_id}"
            )
            return symbolic_context

        except Exception as e:
            logger.warning(f"DΛST analysis failed for {context.user_id}: {e}")
            return self._fallback_symbolic_context(context)

    async def _phase_abas_decision(self, context: UnifiedProcessingContext) -> dict[str, Any]:
        """Phase 2: ΛBAS Attention Decision Enhanced with DΛST Context"""
        logger.debug(f"ΛBAS decision for {context.user_id}")

        try:
            # Register user if needed
            if context.user_id not in self.abas_adapter.registered_users:
                await self.abas_adapter.register_user(context.user_id)

            # Enhance user context with DΛST symbolic information
            enhanced_context = context.user_context.copy()
            if context.symbolic_context:
                enhanced_context["symbolic_context"] = context.symbolic_context
                enhanced_context["primary_activity"] = context.symbolic_context.get("primary_activity")
                enhanced_context["coherence_score"] = context.symbolic_context.get("coherence_score")
                enhanced_context["focus_score"] = context.symbolic_context.get("context_scores", {}).get(
                    "focus_score", 0.5
                )

            # Get ΛBAS attention decision
            attention_result = await self.abas_adapter.check_attention_availability(
                context.user_id, context.message, enhanced_context
            )

            attention_result["abas_phase_success"] = True
            attention_result["symbolic_enhancement"] = context.symbolic_context is not None

            logger.debug(
                f"ΛBAS decision for {context.user_id}: {attention_result.get('approved')} ({attention_result.get('emotional_state')})"
            )
            return attention_result

        except Exception as e:
            logger.warning(f"ΛBAS decision failed for {context.user_id}: {e}")
            return self._fallback_attention_decision(context)

    async def _phase_nias_processing(self, context: UnifiedProcessingContext) -> dict[str, Any]:
        """Phase 3: NIΛS Message Processing with Full Integration Context"""
        logger.debug(f"NIΛS processing for {context.user_id}")

        try:
            # Enhance user context with all integration data
            full_context = context.user_context.copy()
            full_context["unified_processing"] = True
            full_context["session_id"] = context.session_id
            full_context["lambda_trace"] = context.lambda_trace

            if context.symbolic_context:
                full_context["symbolic_context"] = context.symbolic_context

            if context.attention_decision:
                full_context["attention_decision"] = context.attention_decision

            # Process through NIΛS engine
            nias_result = await self.nias_engine.process_message(context.message, full_context)

            nias_result["nias_phase_success"] = True
            nias_result["unified_processing"] = True

            # Update processing stats
            if nias_result.get("status") == "delivered":
                self.processing_stats["successful_deliveries"] += 1
            elif nias_result.get("status") == "blocked":
                self.processing_stats["blocked_messages"] += 1
            elif nias_result.get("status") == "deferred":
                self.processing_stats["deferred_messages"] += 1

            logger.debug(f"NIΛS processing completed for {context.user_id}: {nias_result.get('status')}")
            return nias_result

        except Exception as e:
            logger.warning(f"NIΛS processing failed for {context.user_id}: {e}")
            return self._fallback_nias_processing(context)

    async def _phase_update_symbolic_context(self, context: UnifiedProcessingContext):
        """Phase 4: Update DΛST Symbolic Context Based on Delivery Result"""
        logger.debug(f"Updating DΛST context for {context.user_id}")

        try:
            if context.delivery_result and context.delivery_result.get("status") == "delivered":
                interaction_result = {
                    "status": "delivered",
                    "successful": True,
                    "widget_generated": context.delivery_result.get("widget_config") is not None,
                    "processing_time_ms": context.total_processing_time_ms,
                    "unified_processing": True,
                }

                await self.dast_adapter.update_symbolic_context_from_message(
                    context.user_id, context.message, interaction_result
                )

                logger.debug(f"DΛST context updated for {context.user_id} after successful delivery")

        except Exception as e:
            logger.warning(f"Failed to update DΛST context for {context.user_id}: {e}")

    def _handle_non_approved_message(self, context: UnifiedProcessingContext) -> dict[str, Any]:
        """Handle messages that were not approved by ΛBAS"""
        decision = context.attention_decision

        if decision.get("defer_until"):
            self.processing_stats["deferred_messages"] += 1
            status = "deferred"
        else:
            self.processing_stats["blocked_messages"] += 1
            status = "blocked"

        return {
            "status": status,
            "reason": decision.get("reason", "attention_boundary"),
            "attention_decision": decision,
            "symbolic_context": context.symbolic_context,
            "defer_until": decision.get("defer_until"),
            "confidence": decision.get("confidence"),
            "lambda_trace": context.lambda_trace,
            "unified_processing": True,
            "processing_time_ms": (datetime.now(timezone.utc) - context.start_time).total_seconds() * 1000,
        }

    def _finalize_processing(self, context: UnifiedProcessingContext) -> dict[str, Any]:
        """Finalize unified processing with complete results"""
        context.end_time = datetime.now(timezone.utc)
        context.total_processing_time_ms = (context.end_time - context.start_time).total_seconds() * 1000

        # Update average processing time
        total_requests = self.processing_stats["total_requests"]
        current_avg = self.processing_stats["average_processing_time_ms"]
        self.processing_stats["average_processing_time_ms"] = (
            current_avg * (total_requests - 1) + context.total_processing_time_ms
        ) / total_requests

        # Build comprehensive result
        result = context.delivery_result.copy() if context.delivery_result else {"status": "error"}

        # Add unified processing metadata
        result.update(
            {
                "unified_processing": True,
                "session_id": context.session_id,
                "lambda_trace": context.lambda_trace,
                "processing_time_ms": context.total_processing_time_ms,
                "integration_status": {
                    "abas_available": context.abas_available,
                    "dast_available": context.dast_available,
                    "nias_available": context.nias_available,
                },
                "symbolic_context": context.symbolic_context,
                "attention_decision": context.attention_decision,
            }
        )

        logger.info(
            f"Unified processing completed: {context.session_id} - {result.get('status')} ({context.total_processing_time_ms:.1f}ms)"
        )
        return result

    def _handle_processing_error(self, context: UnifiedProcessingContext, error: Exception) -> dict[str, Any]:
        """Handle processing errors with graceful degradation"""
        processing_time = (datetime.now(timezone.utc) - context.start_time).total_seconds() * 1000

        return {
            "status": "error",
            "error": str(error),
            "unified_processing": True,
            "session_id": context.session_id,
            "lambda_trace": context.lambda_trace,
            "processing_time_ms": processing_time,
            "integration_status": {
                "abas_available": context.abas_available,
                "dast_available": context.dast_available,
                "nias_available": context.nias_available,
            },
            "partial_results": {
                "symbolic_context": context.symbolic_context,
                "attention_decision": context.attention_decision,
            },
        }

    def _fallback_symbolic_context(self, context: UnifiedProcessingContext) -> dict[str, Any]:
        """Fallback symbolic context when DΛST is unavailable"""
        current_hour = datetime.now(timezone.utc).hour

        return {
            "symbolic_tags": ["general", "available"],
            "primary_activity": "working" if 9 <= current_hour <= 17 else "relaxed",
            "context_scores": {
                "focus_score": 0.5,
                "coherence_score": 0.5,
                "stability_score": 0.5,
            },
            "recommended_colors": ["#4a90e2", "#2e7d32"],
            "recommended_elements": ["💡", "⚡"],
            "recommended_tone": "neutral",
            "coherence_score": 0.5,
            "dast_integration": False,
            "fallback_mode": True,
            "lambda_fingerprint": f"FALLBACK-DAST-{context.session_id}",
        }

    def _fallback_attention_decision(self, context: UnifiedProcessingContext) -> dict[str, Any]:
        """Fallback attention decision when ΛBAS is unavailable"""
        current_hour = datetime.now(timezone.utc).hour
        message_priority = context.message.get("priority", 1)

        # Simple time-based decision
        if 9 <= current_hour <= 17 and message_priority < 4:
            approved = False
            reason = "Work hours - only high priority messages"
        else:
            approved = True
            reason = "Standard availability"

        return {
            "approved": approved,
            "emotional_state": "neutral",
            "attention_state": "available" if approved else "busy",
            "reason": reason,
            "confidence": 0.6,
            "abas_integration": False,
            "fallback_mode": True,
            "lambda_trace": f"FALLBACK-ABAS-{context.session_id}",
        }

    def _fallback_nias_processing(self, context: UnifiedProcessingContext) -> dict[str, Any]:
        """Fallback NIAS processing when NIAS engine is unavailable"""
        return {
            "status": "delivered",
            "message": context.message,
            "widget_config": None,
            "delivery_method": "basic",
            "nias_integration": False,
            "fallback_mode": True,
            "lambda_trace": f"FALLBACK-NIAS-{context.session_id}",
        }

    async def health_check(self) -> dict[str, Any]:
        """Comprehensive health check for unified processor"""
        health_data = {
            "status": "healthy" if self.integrations_initialized else "degraded",
            "unified_processing": True,
            "integrations": self.system_health.copy(),
            "processing_stats": self.processing_stats.copy(),
        }

        # Get detailed integration status
        if self.abas_adapter:
            try:
                health_data["abas_details"] = self.abas_adapter.get_integration_status()
            except Exception as e:
                health_data["abas_error"] = str(e)

        if self.dast_adapter:
            try:
                health_data["dast_details"] = self.dast_adapter.get_integration_status()
            except Exception as e:
                health_data["dast_error"] = str(e)

        if self.nias_engine:
            try:
                nias_health = await self.nias_engine.health_check()
                health_data["nias_details"] = nias_health
            except Exception as e:
                health_data["nias_error"] = str(e)

        return health_data

    def get_system_metrics(self) -> dict[str, Any]:
        """Get comprehensive system metrics"""
        return {
            "system": "Unified NIΛS-ΛBAS-DΛST Processor",
            "version": "1.0.0-unified",
            "lambda_brand": "Λ",
            "integrations_active": sum(1 for status in self.system_health.values() if status),
            "total_integrations": len(self.system_health),
            "processing_stats": self.processing_stats,
            "system_health": self.system_health,
            "session_counter": self.session_counter,
        }


# Global unified processor instance
_global_unified_processor = None


def get_unified_processor() -> UnifiedMessageProcessor:
    """Get the global unified processor instance"""
    global _global_unified_processor
    if _global_unified_processor is None:
        _global_unified_processor = UnifiedMessageProcessor()
    return _global_unified_processor
