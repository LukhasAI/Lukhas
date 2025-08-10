"""
DAST Integration Adapter for NIΛS
Integrates Dynamic Lambda Symbol Tracker with NIAS symbolic message processing
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add DAST to the path
dast_path = Path(__file__).parent.parent.parent / "DΛST"
sys.path.insert(0, str(dast_path))

try:
    from dast_core import (
        DΛST,
        ContextSnapshot,
        SymbolCategory,
        SymbolicTag,
        SymbolSource,
    )

    DAST_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("DΛST integration available")
except ImportError as e:
    DAST_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"DΛST not available: {e}")

    # Mock classes for fallback
    class SymbolCategory:
        ACTIVITY = "activity"
        CONTEXT = "context"
        MOOD = "mood"
        FOCUS = "focus"
        CREATIVE = "creative"
        TEMPORAL = "temporal"

    class SymbolSource:
        USER_EXPLICIT = "user_explicit"
        AI_INFERENCE = "ai_inference"
        ACTIVITY_TRACKER = "activity_tracker"

    class SymbolicTag:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    class ContextSnapshot:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)


class NIASDastAdapter:
    """
    Adapter that integrates DΛST symbolic context system with NIΛS message processing.

    This adapter:
    - Provides symbolic context enhancement for message processing
    - Translates DΛST symbolic tags to NIΛS symbolic processing format
    - Enables context-aware widget personalization
    - Updates symbolic context based on message interactions
    - Provides fallback behavior when DΛST is unavailable
    """

    def __init__(self):
        self.dast_available = DAST_AVAILABLE
        self.dast_instance = None

        if self.dast_available:
            try:
                self.dast_instance = DΛST()
                logger.info("DΛST instance initialized for NIΛS integration")
            except Exception as e:
                logger.error(f"Failed to initialize DΛST: {e}")
                self.dast_available = False
                self.dast_instance = None

        # DAST to NIAS symbolic mappings
        self.symbol_to_color_mapping = self._initialize_symbol_color_mapping()
        self.symbol_to_element_mapping = self._initialize_symbol_element_mapping()
        self.activity_to_tone_mapping = self._initialize_activity_tone_mapping()

        # Message type to symbolic category mappings
        self.message_to_symbol_mapping = self._initialize_message_symbol_mapping()

        # Registered users for DAST
        self.registered_users = set()

        logger.info(
            f"NIΛS-DΛST adapter initialized (DAST available: {self.dast_available})"
        )

    def _initialize_symbol_color_mapping(self) -> Dict[str, List[str]]:
        """Map DAST symbolic tags to NIAS color themes"""
        return {
            # Activity-based colors
            "working": ["#1976d2", "#4a90e2"],  # Professional blues
            "coding": ["#2e7d32", "#4caf50"],  # Focused greens
            "creative": ["#6a1b9a", "#9c27b0"],  # Creative purples
            "meeting": ["#ff5722", "#ff9800"],  # Energetic oranges
            "learning": ["#0288d1", "#03a9f4"],  # Knowledge blues
            "relaxed": ["#81c784", "#a5d6a7"],  # Calm greens
            "focused": ["#1565c0", "#1976d2"],  # Deep focus blues
            # Context-based colors
            "home": ["#8bc34a", "#cddc39"],  # Natural greens
            "office": ["#424242", "#616161"],  # Professional grays
            "outdoor": ["#4caf50", "#66bb6a"],  # Nature greens
            "social": ["#ff9800", "#ffb74d"],  # Social oranges
            # Mood-based colors
            "energetic": ["#f57c00", "#ff9800"],  # Energy oranges
            "calm": ["#64b5f6", "#90caf9"],  # Peaceful blues
            "inspired": ["#ab47bc", "#ba68c8"],  # Inspiration purples
            "productive": ["#43a047", "#66bb6a"],  # Achievement greens
        }

    def _initialize_symbol_element_mapping(self) -> Dict[str, List[str]]:
        """Map DAST symbolic tags to NIAS symbolic elements"""
        return {
            # Activity elements
            "working": ["💼", "📊", "⚡"],
            "coding": ["💻", "🔧", "⚡"],
            "creative": ["🎨", "✨", "💡"],
            "meeting": ["👥", "🤝", "💬"],
            "learning": ["📚", "🧠", "🔍"],
            "focused": ["🎯", "⚡", "🔥"],
            # Context elements
            "home": ["🏠", "☕", "🌿"],
            "office": ["🏢", "📋", "⚙️"],
            "outdoor": ["🌲", "🌊", "☀️"],
            "travel": ["✈️", "🗺️", "🚀"],
            # Mood elements
            "energetic": ["⚡", "🚀", "🔥"],
            "calm": ["🌊", "🍃", "☯️"],
            "inspired": ["💡", "✨", "🌟"],
            "productive": ["✅", "🏆", "📈"],
        }

    def _initialize_activity_tone_mapping(self) -> Dict[str, str]:
        """Map DAST activities to NIAS communication tones"""
        return {
            "working": "professional",
            "coding": "technical",
            "creative": "inspiring",
            "meeting": "collaborative",
            "learning": "educational",
            "relaxed": "gentle",
            "focused": "direct",
            "social": "friendly",
            "productive": "motivational",
            "calm": "soothing",
        }

    def _initialize_message_symbol_mapping(self) -> Dict[str, List[str]]:
        """Map NIAS message types to relevant symbolic categories for DAST tracking"""
        return {
            "promotional": ["commercial", "product", "brand"],
            "educational": ["learning", "knowledge", "growth"],
            "notification": ["update", "information", "alert"],
            "dream_seed": ["creative", "inspiration", "visualization"],
            "interactive": ["engagement", "participation", "feedback"],
            "urgent": ["important", "priority", "action-required"],
            "widget": ["interface", "tool", "productivity"],
        }

    async def register_user(
        self, user_id: str, initial_symbols: Optional[List[str]] = None
    ) -> bool:
        """Register user with DAST for symbolic context tracking"""
        if not self.dast_available or not self.dast_instance:
            logger.debug(f"DAST not available, skipping user registration: {user_id}")
            return True  # Fallback: pretend success

        try:
            # Register with DAST using provided or default symbols
            default_symbols = initial_symbols or ["general", "available", "neutral"]
            success = await self.dast_instance.register_user(user_id, default_symbols)

            if success:
                self.registered_users.add(user_id)
                logger.info(f"User {user_id} registered with DΛST symbolic tracking")

            return success

        except Exception as e:
            logger.error(f"Failed to register user {user_id} with DΛST: {e}")
            return False

    async def get_symbolic_context(
        self, user_id: str, message_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get symbolic context for message processing.
        This is the primary integration point for NIAS symbolic processing phase.

        Returns:
            {
                "symbolic_tags": List[str],
                "primary_activity": str,
                "context_scores": Dict[str, float],
                "recommended_colors": List[str],
                "recommended_elements": List[str],
                "recommended_tone": str,
                "coherence_score": float,
                "lambda_fingerprint": str
            }
        """

        # Fallback behavior if DAST not available
        if not self.dast_available or not self.dast_instance:
            return self._fallback_symbolic_context(user_id, message_type)

        try:
            # Ensure user is registered
            if user_id not in self.registered_users:
                await self.register_user(user_id)

            # Get current symbolic context from DAST
            context_snapshot = await self.dast_instance.get_context_snapshot(user_id)
            current_tags = await self.dast_instance.get_current_tags(user_id)

            if not context_snapshot:
                return self._fallback_symbolic_context(user_id, message_type)

            # Translate DAST context to NIAS format
            symbolic_context = {
                "symbolic_tags": current_tags,
                "primary_activity": context_snapshot.primary_activity,
                "context_scores": {
                    "focus_score": context_snapshot.focus_score,
                    "coherence_score": context_snapshot.coherence_score,
                    "stability_score": context_snapshot.stability_score,
                },
                "recommended_colors": self._get_recommended_colors(current_tags),
                "recommended_elements": self._get_recommended_elements(current_tags),
                "recommended_tone": self._get_recommended_tone(
                    context_snapshot.primary_activity
                ),
                "coherence_score": context_snapshot.coherence_score,
                "lambda_fingerprint": context_snapshot.lambda_fingerprint,
                "dast_integration": True,
                "timestamp": (
                    context_snapshot.timestamp.isoformat()
                    if context_snapshot.timestamp
                    else None
                ),
            }

            # Add message-specific symbolic enhancements
            if message_type:
                message_symbols = self.message_to_symbol_mapping.get(message_type, [])
                symbolic_context["message_aligned_symbols"] = message_symbols
                symbolic_context["message_coherence"] = (
                    self._calculate_message_coherence(current_tags, message_symbols)
                )

            logger.debug(
                f"DΛST provided symbolic context for {user_id}: {len(current_tags)} active symbols"
            )
            return symbolic_context

        except Exception as e:
            logger.error(f"DΛST symbolic context failed for {user_id}: {e}")
            return self._fallback_symbolic_context(user_id, message_type, error=str(e))

    def _get_recommended_colors(self, symbolic_tags: List[str]) -> List[str]:
        """Get recommended colors based on symbolic tags"""
        colors = []
        for tag in symbolic_tags:
            tag_colors = self.symbol_to_color_mapping.get(tag.lower(), [])
            colors.extend(tag_colors)

        # Remove duplicates and limit to top 3
        unique_colors = list(dict.fromkeys(colors))
        return unique_colors[:3] if unique_colors else ["#4a90e2", "#2e7d32", "#1976d2"]

    def _get_recommended_elements(self, symbolic_tags: List[str]) -> List[str]:
        """Get recommended symbolic elements based on tags"""
        elements = []
        for tag in symbolic_tags:
            tag_elements = self.symbol_to_element_mapping.get(tag.lower(), [])
            elements.extend(tag_elements)

        # Remove duplicates and limit to top 4
        unique_elements = list(dict.fromkeys(elements))
        return unique_elements[:4] if unique_elements else ["💡", "⚡", "🎯", "✨"]

    def _get_recommended_tone(self, primary_activity: Optional[str]) -> str:
        """Get recommended communication tone based on primary activity"""
        if not primary_activity:
            return "neutral"

        return self.activity_to_tone_mapping.get(primary_activity.lower(), "neutral")

    def _calculate_message_coherence(
        self, current_tags: List[str], message_symbols: List[str]
    ) -> float:
        """Calculate coherence between current context and message symbols"""
        if not current_tags or not message_symbols:
            return 0.5  # Neutral coherence

        # Simple overlap-based coherence calculation
        current_set = set(tag.lower() for tag in current_tags)
        message_set = set(symbol.lower() for symbol in message_symbols)

        if not current_set or not message_set:
            return 0.5

        intersection = current_set.intersection(message_set)
        union = current_set.union(message_set)

        return len(intersection) / len(union) if union else 0.5

    def _fallback_symbolic_context(
        self,
        user_id: str,
        message_type: Optional[str] = None,
        error: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Fallback symbolic context when DAST is unavailable"""

        # Simple time-based context
        current_hour = datetime.now().hour

        # Determine basic symbolic context based on time
        if 9 <= current_hour <= 17:
            primary_activity = "working"
            symbolic_tags = ["working", "focused", "office"]
        elif 18 <= current_hour <= 22:
            primary_activity = "relaxed"
            symbolic_tags = ["relaxed", "home", "evening"]
        else:
            primary_activity = "resting"
            symbolic_tags = ["calm", "home", "night"]

        fallback_context = {
            "symbolic_tags": symbolic_tags,
            "primary_activity": primary_activity,
            "context_scores": {
                "focus_score": 0.6,
                "coherence_score": 0.7,
                "stability_score": 0.8,
            },
            "recommended_colors": self._get_recommended_colors(symbolic_tags),
            "recommended_elements": self._get_recommended_elements(symbolic_tags),
            "recommended_tone": self._get_recommended_tone(primary_activity),
            "coherence_score": 0.7,
            "lambda_fingerprint": f"FALLBACK_{user_id}_{datetime.now().strftime('%H%M%S')}",
            "dast_integration": False,
            "fallback_mode": True,
            "timestamp": datetime.now().isoformat(),
        }

        if error:
            fallback_context["dast_error"] = error

        if message_type:
            message_symbols = self.message_to_symbol_mapping.get(message_type, [])
            fallback_context["message_aligned_symbols"] = message_symbols
            fallback_context["message_coherence"] = self._calculate_message_coherence(
                symbolic_tags, message_symbols
            )

        return fallback_context

    async def update_symbolic_context_from_message(
        self, user_id: str, message: Dict[str, Any], interaction_result: Dict[str, Any]
    ) -> bool:
        """Update user's symbolic context based on message interaction"""
        if not self.dast_available or not self.dast_instance:
            return True  # Fallback: pretend success

        try:
            # Extract symbolic information from message and interaction
            message_type = message.get("type", "unknown")
            brand_id = message.get("brand_id")
            was_successful = interaction_result.get("status") == "delivered"

            # Determine symbols to add based on message interaction
            symbols_to_add = []

            # Add message type symbols
            message_symbols = self.message_to_symbol_mapping.get(message_type, [])
            for symbol in message_symbols:
                symbols_to_add.append((symbol, SymbolCategory.ACTIVITY, 0.6))

            # Add interaction outcome symbols
            if was_successful:
                symbols_to_add.append(("engaged", SymbolCategory.ACTIVITY, 0.7))
                if message.get("interactive_elements"):
                    symbols_to_add.append(("interactive", SymbolCategory.ACTIVITY, 0.5))

            # Add brand interaction symbols
            if brand_id:
                symbols_to_add.append(
                    (f"brand-{brand_id}", SymbolCategory.CONTEXT, 0.4)
                )

            # Add dream seed symbols
            if message.get("dream_seed"):
                dream_theme = message["dream_seed"].get("theme", "inspiration")
                symbols_to_add.append((dream_theme, SymbolCategory.CREATIVE, 0.8))
                symbols_to_add.append(
                    ("dream-interaction", SymbolCategory.CREATIVE, 0.6)
                )

            # Add symbols to DAST
            for symbol, category, confidence in symbols_to_add:
                await self.dast_instance.add_symbol(
                    user_id=user_id,
                    symbol=symbol,
                    category=category,
                    source=SymbolSource.AI_INFERENCE,
                    confidence=confidence,
                    metadata={
                        "source": "nias_message_interaction",
                        "message_type": message_type,
                        "message_id": message.get("message_id"),
                        "interaction_successful": was_successful,
                    },
                    expires_in_hours=2,  # Message-based symbols expire quickly
                )

            logger.debug(
                f"Updated DΛST context for {user_id} with {len(symbols_to_add)} symbols from message interaction"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to update symbolic context for {user_id}: {e}")
            return False

    async def get_activity_suggestions(
        self, user_id: str, current_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get activity suggestions based on current symbolic context"""
        if not self.dast_available or not self.dast_instance:
            return []

        try:
            context_snapshot = await self.dast_instance.get_context_snapshot(user_id)
            if not context_snapshot:
                return []

            suggestions = []

            # Suggest activities based on focus and coherence scores
            if context_snapshot.focus_score >= 0.8:
                suggestions.append(
                    {
                        "activity": "deep-work-session",
                        "reason": "High focus detected - perfect for concentrated work",
                        "priority": 0.9,
                        "duration_estimate": 45,
                    }
                )

            if context_snapshot.coherence_score < 0.4:
                suggestions.append(
                    {
                        "activity": "context-switch-break",
                        "reason": "Low coherence - consider a brief break to refocus",
                        "priority": 0.7,
                        "duration_estimate": 5,
                    }
                )

            if context_snapshot.primary_activity == "creative":
                suggestions.append(
                    {
                        "activity": "creative-expression",
                        "reason": "Creative context detected - optimal for artistic work",
                        "priority": 0.8,
                        "duration_estimate": 30,
                    }
                )

            return suggestions

        except Exception as e:
            logger.error(f"Failed to get activity suggestions for {user_id}: {e}")
            return []

    async def get_symbolic_analytics(
        self, user_id: str, hours: int = 24
    ) -> Dict[str, Any]:
        """Get symbolic analytics from DAST"""
        if not self.dast_available or not self.dast_instance:
            return {"error": "DAST not available"}

        try:
            return self.dast_instance.get_symbol_analytics(user_id, hours)
        except Exception as e:
            logger.error(f"Failed to get symbolic analytics for {user_id}: {e}")
            return {"error": str(e)}

    def is_dast_available(self) -> bool:
        """Check if DAST integration is available"""
        return self.dast_available and self.dast_instance is not None

    def get_integration_status(self) -> Dict[str, Any]:
        """Get status of DAST integration"""
        status = {
            "dast_available": self.dast_available,
            "registered_users": len(self.registered_users),
            "integration_mode": "full" if self.dast_available else "fallback",
        }

        if self.dast_available and self.dast_instance:
            try:
                system_metrics = self.dast_instance.get_system_metrics()
                status["dast_metrics"] = system_metrics
            except Exception as e:
                status["dast_error"] = str(e)

        return status


# Global adapter instance
_global_dast_adapter = None


def get_dast_adapter() -> NIASDastAdapter:
    """Get the global DAST adapter instance"""
    global _global_dast_adapter
    if _global_dast_adapter is None:
        _global_dast_adapter = NIASDastAdapter()
    return _global_dast_adapter
