"""
Widget Engine for NIΛS Interactive Experience Layer
Handles gesture-based UI widgets and user interactions
"""

import logging
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class WidgetType(Enum):
    """Types of widgets supported by NIΛS"""

    BASIC_CARD = "basic_card"
    INTERACTIVE_WIDGET = "interactive_widget"
    IMMERSIVE_EXPERIENCE = "immersive_experience"
    SEASONAL_THEMED = "seasonal_themed"
    BRAND_SHOWCASE = "brand_showcase"
    ASSISTANT_MODE = "assistant_mode"


class InteractionType(Enum):
    """Gesture-based interaction types"""

    TAP = "tap"  # Single tap for pitch
    DOUBLE_TAP = "double_tap"  # Double tap for details
    TRIPLE_TAP = "triple_tap"  # Triple tap for Assistant Mode (T2+)
    HOLD = "hold"  # Tap and hold to add to basket
    SWIPE_LEFT = "swipe_left"  # Swipe to move to bin
    SWIPE_RIGHT = "swipe_right"  # Swipe for more options
    SWIPE_UP = "swipe_up"  # Swipe up for full screen
    SWIPE_DOWN = "swipe_down"  # Swipe down to dismiss
    PINCH = "pinch"  # Pinch for sizing (T1 only)
    ROTATE = "rotate"  # Rotate for perspective (T1 only)


class WidgetEngine:
    """
    Advanced widget engine for NIΛS interactive experiences.

    Features:
    - Gesture-based interactions (tap, double-tap, hold, swipe)
    - Tier-appropriate widget complexity
    - Seasonal and branded theming
    - Real-time interaction tracking
    - Assistant Mode integration (T2+)
    """

    def __init__(self):
        self.active_widgets: dict[str, dict[str, Any]] = {}
        self.interaction_history: list[dict[str, Any]] = []
        self.widget_templates = self._initialize_widget_templates()
        self.seasonal_themes = self._initialize_seasonal_themes()
        self.brand_configurations = {}

        logger.info("Widget Engine initialized")

    def _initialize_widget_templates(self) -> dict[str, dict[str, Any]]:
        """Initialize widget templates for different tiers and types"""
        return {
            "T3": {  # Basic tier templates
                WidgetType.BASIC_CARD.value: {
                    "layout": "simple_card",
                    "animations": False,
                    "interactions": [
                        InteractionType.TAP,
                        InteractionType.DOUBLE_TAP,
                        InteractionType.HOLD,
                        InteractionType.SWIPE_LEFT,
                    ],
                    "styling": {
                        "colors": ["#f0f0f0", "#ffffff", "#e0e0e0"],
                        "fonts": ["system"],
                        "shadows": False,
                        "borders": True,
                    },
                    "mandatory_elements": ["feedback_button", "rating_prompt"],
                }
            },
            "T2": {  # Enhanced tier templates
                WidgetType.INTERACTIVE_WIDGET.value: {
                    "layout": "enhanced_card",
                    "animations": True,
                    "interactions": [
                        InteractionType.TAP,
                        InteractionType.DOUBLE_TAP,
                        InteractionType.TRIPLE_TAP,  # Assistant Mode
                        InteractionType.HOLD,
                        InteractionType.SWIPE_LEFT,
                        InteractionType.SWIPE_RIGHT,
                        InteractionType.SWIPE_UP,
                    ],
                    "styling": {
                        "colors": ["#4a90e2", "#ffffff", "#f8f9fa"],
                        "fonts": ["system", "custom"],
                        "shadows": True,
                        "borders": False,
                        "gradients": True,
                    },
                    "features": ["assistant_mode", "enhanced_preview"],
                },
                WidgetType.SEASONAL_THEMED.value: {
                    "layout": "themed_card",
                    "animations": True,
                    "seasonal_adaptation": True,
                    "brand_integration": True,
                },
            },
            "T1": {  # Premium tier templates
                WidgetType.IMMERSIVE_EXPERIENCE.value: {
                    "layout": "immersive_fullscreen",
                    "animations": True,
                    "interactions": list(InteractionType),  # All interactions
                    "styling": {
                        "colors": "brand_adaptive",
                        "fonts": "custom_premium",
                        "shadows": True,
                        "borders": False,
                        "gradients": True,
                        "transparency": True,
                        "3d_effects": True,
                    },
                    "features": [
                        "ai_assistant",
                        "voice_interaction",
                        "gesture_recognition",
                        "eye_tracking",
                        "haptic_feedback",
                    ],
                },
                WidgetType.BRAND_SHOWCASE.value: {
                    "layout": "premium_showcase",
                    "animations": True,
                    "brand_integration": "full",
                    "customization": "unlimited",
                },
            },
        }

    def _initialize_seasonal_themes(self) -> dict[str, dict[str, Any]]:
        """Initialize seasonal theming configurations"""
        return {
            "spring": {
                "colors": ["#90EE90", "#98FB98", "#00FF7F"],
                "animations": ["bloom", "growth", "flutter"],
                "symbols": ["🌸", "🌱", "🦋", "☀️"],
                "gradients": ["linear-gradient(45deg, #90EE90, #98FB98)"],
            },
            "summer": {
                "colors": ["#FFD700", "#FF6347", "#00BFFF"],
                "animations": ["wave", "shine", "pulse"],
                "symbols": ["☀️", "🌊", "🏖️", "🌺"],
                "gradients": ["radial-gradient(circle, #FFD700, #FF6347)"],
            },
            "autumn": {
                "colors": ["#FF8C00", "#DC143C", "#B8860B"],
                "animations": ["fall", "swirl", "fade"],
                "symbols": ["🍂", "🍁", "🎃", "🦃"],
                "gradients": ["linear-gradient(135deg, #FF8C00, #DC143C)"],
            },
            "winter": {
                "colors": ["#E0E6FF", "#B0C4DE", "#4682B4"],
                "animations": ["sparkle", "drift", "freeze"],
                "symbols": ["❄️", "⭐", "🎄", "☃️"],
                "gradients": ["linear-gradient(180deg, #E0E6FF, #B0C4DE)"],
            },
        }

    async def generate_widget(
        self,
        message: dict[str, Any],
        user_context: dict[str, Any],
        tier: str,
        widget_type: Optional[WidgetType] = None,
    ) -> dict[str, Any]:
        """
        Generate a tier-appropriate widget for message delivery.

        Args:
            message: The message/content to display
            user_context: User context and preferences
            tier: User tier (T1, T2, T3)
            widget_type: Optional specific widget type

        Returns:
            Complete widget configuration
        """
        try:
            # Determine appropriate widget type
            if not widget_type:
                widget_type = await self._determine_widget_type(
                    tier, message, user_context
                )

            # Get base template
            template = self._get_widget_template(tier, widget_type)

            # Generate unique widget ID
            widget_id = f"widget_{uuid.uuid4().hex[:8]}"

            # Build widget configuration
            widget_config = {
                "widget_id": widget_id,
                "type": widget_type.value,
                "tier": tier,
                "created_at": datetime.now().isoformat(),
                "expires_at": self._calculate_expiry(tier),
                "template": template,
                "content": await self._process_content(message, tier),
                "styling": await self._apply_styling(template, user_context, tier),
                "interactions": await self._configure_interactions(template, tier),
                "metadata": {
                    "user_id": user_context.get("user_id"),
                    "brand_id": message.get("brand_id"),
                    "campaign_id": message.get("campaign_id"),
                    "priority": message.get("priority", 1),
                },
            }

            # Apply seasonal theming (T2+)
            if tier in ["T1", "T2"]:
                widget_config = await self._apply_seasonal_theming(widget_config)

            # Apply brand customization
            if message.get("brand_id"):
                widget_config = await self._apply_brand_customization(
                    widget_config, message["brand_id"], tier
                )

            # Store active widget
            self.active_widgets[widget_id] = widget_config

            logger.info(
                f"Generated {widget_type.value} widget {widget_id} for tier {tier}"
            )

            return widget_config

        except Exception as e:
            logger.error(f"Failed to generate widget: {e}")
            return await self._generate_fallback_widget(message, tier)

    async def _determine_widget_type(
        self, tier: str, message: dict[str, Any], user_context: dict[str, Any]
    ) -> WidgetType:
        """Determine the most appropriate widget type"""

        # Tier-based defaults
        if tier == "T3":
            return WidgetType.BASIC_CARD
        elif tier == "T2":
            # Check for seasonal content
            if message.get("seasonal", False):
                return WidgetType.SEASONAL_THEMED
            return WidgetType.INTERACTIVE_WIDGET
        else:  # T1
            # Check for premium brand content
            if message.get("premium_brand", False):
                return WidgetType.BRAND_SHOWCASE
            if message.get("immersive", False):
                return WidgetType.IMMERSIVE_EXPERIENCE
            return WidgetType.INTERACTIVE_WIDGET

    def _get_widget_template(
        self, tier: str, widget_type: WidgetType
    ) -> dict[str, Any]:
        """Get widget template for tier and type"""
        tier_templates = self.widget_templates.get(tier, self.widget_templates["T3"])
        return tier_templates.get(
            widget_type.value, tier_templates[list(tier_templates.keys())[0]]
        )

    async def _process_content(
        self, message: dict[str, Any], tier: str
    ) -> dict[str, Any]:
        """Process and format content based on tier capabilities"""
        content = {
            "title": message.get("title", ""),
            "description": message.get("description", ""),
            "image_url": message.get("image_url"),
            "action_url": message.get("action_url"),
            "price": message.get("price"),
            "brand": message.get("brand_name", ""),
        }

        # Tier-specific content enhancements
        if tier == "T1":
            # Premium content with full details
            content.update(
                {
                    "detailed_description": message.get("detailed_description"),
                    "video_url": message.get("video_url"),
                    "3d_model_url": message.get("3d_model_url"),
                    "reviews": message.get("reviews", []),
                    "specifications": message.get("specifications", {}),
                    "related_products": message.get("related_products", []),
                }
            )
        elif tier == "T2":
            # Enhanced content
            content.update(
                {
                    "short_video": message.get("short_video"),
                    "quick_specs": message.get("quick_specs", {}),
                    "user_rating": message.get("user_rating"),
                }
            )

        return content

    async def _apply_styling(
        self, template: dict[str, Any], user_context: dict[str, Any], tier: str
    ) -> dict[str, Any]:
        """Apply styling based on template and user preferences"""
        styling = template.get("styling", {}).copy()

        # User preference overrides (T1 only)
        if tier == "T1":
            user_prefs = user_context.get("preferences", {})
            if "theme" in user_prefs:
                styling["theme"] = user_prefs["theme"]
            if "accent_color" in user_prefs:
                styling["accent_color"] = user_prefs["accent_color"]

        # Accessibility enhancements
        if user_context.get("accessibility", {}).get("high_contrast"):
            styling["high_contrast"] = True
            styling["colors"] = ["#000000", "#ffffff", "#ffff00"]

        if user_context.get("accessibility", {}).get("large_text"):
            styling["font_scale"] = 1.5

        return styling

    async def _configure_interactions(
        self, template: dict[str, Any], tier: str
    ) -> dict[str, list]:
        """Configure available interactions based on tier"""
        available_interactions = template.get("interactions", [])

        interaction_config = {
            "enabled_gestures": [],
            "action_mappings": {},
            "feedback_requirements": {},
        }

        for interaction in available_interactions:
            if isinstance(interaction, InteractionType):
                gesture = interaction.value
            else:
                gesture = interaction

            interaction_config["enabled_gestures"].append(gesture)

            # Configure action mappings
            if gesture == InteractionType.TAP.value:
                interaction_config["action_mappings"][gesture] = "show_pitch"
            elif gesture == InteractionType.DOUBLE_TAP.value:
                interaction_config["action_mappings"][gesture] = "show_details"
            elif gesture == InteractionType.TRIPLE_TAP.value and tier != "T3":
                interaction_config["action_mappings"][gesture] = "activate_assistant"
            elif gesture == InteractionType.HOLD.value:
                interaction_config["action_mappings"][gesture] = "add_to_basket"
            elif gesture == InteractionType.SWIPE_LEFT.value:
                action = "permanent_delete" if tier == "T1" else "move_to_bin"
                interaction_config["action_mappings"][gesture] = action

            # Feedback requirements (T3 mandatory)
            if tier == "T3" and gesture in [
                InteractionType.SWIPE_LEFT.value,
                InteractionType.HOLD.value,
            ]:
                interaction_config["feedback_requirements"][gesture] = {
                    "required": True,
                    "prompt": "Please tell us why you performed this action",
                }

        return interaction_config

    async def _apply_seasonal_theming(
        self, widget_config: dict[str, Any]
    ) -> dict[str, Any]:
        """Apply seasonal theming to widget"""
        current_season = self._get_current_season()
        theme = self.seasonal_themes.get(current_season, self.seasonal_themes["spring"])

        # Merge seasonal theme with existing styling
        styling = widget_config.get("styling", {})
        styling.update(
            {
                "seasonal_theme": current_season,
                "seasonal_colors": theme["colors"],
                "seasonal_animations": theme["animations"],
                "seasonal_symbols": theme["symbols"][:2],  # Limit to 2 symbols
                "seasonal_gradient": theme["gradients"][0],
            }
        )

        widget_config["styling"] = styling
        return widget_config

    def _get_current_season(self) -> str:
        """Determine current season based on date"""
        month = datetime.now().month

        if 3 <= month <= 5:
            return "spring"
        elif 6 <= month <= 8:
            return "summer"
        elif 9 <= month <= 11:
            return "autumn"
        else:
            return "winter"

    async def _apply_brand_customization(
        self, widget_config: dict[str, Any], brand_id: str, tier: str
    ) -> dict[str, Any]:
        """Apply brand-specific customization"""
        brand_config = await self._get_brand_configuration(brand_id)

        if not brand_config:
            return widget_config

        styling = widget_config.get("styling", {})

        # Apply brand colors
        if "brand_colors" in brand_config:
            styling["brand_colors"] = brand_config["brand_colors"]
            if tier != "T3":  # Enhanced tiers get brand color integration
                styling["accent_color"] = brand_config["brand_colors"][0]

        # Apply brand fonts (T1 only)
        if tier == "T1" and "brand_fonts" in brand_config:
            styling["fonts"] = brand_config["brand_fonts"]

        # Brand logo integration
        if "logo_url" in brand_config:
            widget_config["content"]["brand_logo"] = brand_config["logo_url"]

        widget_config["styling"] = styling
        return widget_config

    async def _get_brand_configuration(self, brand_id: str) -> Optional[dict[str, Any]]:
        """Get brand configuration (would typically come from brand management service)"""
        # Simulated brand configurations
        brand_configs = {
            "premium_brand_001": {
                "brand_colors": ["#1a1a1a", "#gold", "#white"],
                "brand_fonts": ["custom_premium", "serif"],
                "logo_url": "https://brands.example.com/premium_001/logo.svg",
                "animation_style": "elegant",
            },
            "eco_brand_002": {
                "brand_colors": ["#22c55e", "#16a34a", "#f0fdf4"],
                "brand_fonts": ["eco_friendly", "sans-serif"],
                "logo_url": "https://brands.example.com/eco_002/logo.svg",
                "animation_style": "organic",
            },
        }

        return brand_configs.get(brand_id)

    def _calculate_expiry(self, tier: str) -> str:
        """Calculate widget expiry based on tier"""
        if tier == "T1":
            # Unlimited duration for premium
            return (datetime.now() + timedelta(days=365)).isoformat()
        elif tier == "T2":
            # 14 days for enhanced
            return (datetime.now() + timedelta(days=14)).isoformat()
        else:  # T3
            # 7 days for basic
            return (datetime.now() + timedelta(days=7)).isoformat()

    async def _generate_fallback_widget(
        self, message: dict[str, Any], tier: str
    ) -> dict[str, Any]:
        """Generate a simple fallback widget if main generation fails"""
        return {
            "widget_id": f"fallback_{uuid.uuid4().hex[:8]}",
            "type": WidgetType.BASIC_CARD.value,
            "tier": tier,
            "created_at": datetime.now().isoformat(),
            "content": {
                "title": message.get("title", "Message"),
                "description": message.get("description", ""),
            },
            "styling": {"colors": ["#f0f0f0", "#ffffff"], "simple": True},
            "interactions": {
                "enabled_gestures": [
                    InteractionType.TAP.value,
                    InteractionType.SWIPE_LEFT.value,
                ],
                "action_mappings": {
                    InteractionType.TAP.value: "show_content",
                    InteractionType.SWIPE_LEFT.value: "dismiss",
                },
            },
            "fallback": True,
        }

    async def handle_interaction(
        self,
        widget_id: str,
        interaction_type: str,
        user_id: str,
        interaction_data: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Handle user interaction with a widget.

        Args:
            widget_id: Widget identifier
            interaction_type: Type of interaction performed
            user_id: User performing interaction
            interaction_data: Additional interaction context

        Returns:
            Interaction result and any follow-up actions
        """
        try:
            if widget_id not in self.active_widgets:
                return {"success": False, "error": "Widget not found or expired"}

            widget = self.active_widgets[widget_id]
            interaction_config = widget.get("interactions", {})

            # Check if interaction is enabled for this widget
            if interaction_type not in interaction_config.get("enabled_gestures", []):
                return {
                    "success": False,
                    "error": f"Interaction {interaction_type} not enabled",
                }

            # Record interaction
            interaction_record = {
                "interaction_id": f"int_{uuid.uuid4().hex[:8]}",
                "widget_id": widget_id,
                "user_id": user_id,
                "interaction_type": interaction_type,
                "timestamp": datetime.now().isoformat(),
                "data": interaction_data or {},
            }

            self.interaction_history.append(interaction_record)

            # Get mapped action
            action = interaction_config.get("action_mappings", {}).get(interaction_type)
            result = await self._execute_action(action, widget, interaction_data)

            # Check for feedback requirements
            feedback_req = interaction_config.get("feedback_requirements", {}).get(
                interaction_type
            )
            if feedback_req and feedback_req.get("required", False):
                result["feedback_required"] = True
                result["feedback_prompt"] = feedback_req.get(
                    "prompt", "Please provide feedback"
                )

            # Update widget state
            if "widget_updates" in result:
                widget.update(result["widget_updates"])

            logger.info(f"Processed {interaction_type} on widget {widget_id}")

            return {
                "success": True,
                "interaction_id": interaction_record["interaction_id"],
                "action_taken": action,
                "result": result,
            }

        except Exception as e:
            logger.error(f"Failed to handle interaction: {e}")
            return {"success": False, "error": str(e)}

    async def _execute_action(
        self,
        action: str,
        widget: dict[str, Any],
        interaction_data: Optional[dict[str, Any]],
    ) -> dict[str, Any]:
        """Execute the mapped action for an interaction"""

        if action == "show_pitch":
            return {
                "action_type": "display_content",
                "content_type": "pitch",
                "title": widget["content"].get("title", ""),
                "pitch_text": f"Check out this {widget['content'].get('brand', 'amazing')} product!",
                "duration_ms": 2000,
            }

        elif action == "show_details":
            return {
                "action_type": "display_content",
                "content_type": "details",
                "detailed_view": {
                    "description": widget["content"].get(
                        "detailed_description", widget["content"].get("description", "")
                    ),
                    "price": widget["content"].get("price"),
                    "specifications": widget["content"].get("specifications", {}),
                    "reviews": widget["content"].get("reviews", []),
                },
            }

        elif action == "activate_assistant":
            return {
                "action_type": "launch_assistant",
                "assistant_mode": True,
                "context": {
                    "product": widget["content"].get("title"),
                    "brand": widget["content"].get("brand"),
                    "user_intent": "product_inquiry",
                },
            }

        elif action == "add_to_basket":
            return {
                "action_type": "add_to_basket",
                "product_id": widget.get("metadata", {}).get("product_id"),
                "quantity": (
                    interaction_data.get("quantity", 1) if interaction_data else 1
                ),
                "basket_updated": True,
            }

        elif action in ["move_to_bin", "permanent_delete"]:
            # Remove widget from active widgets
            widget_id = widget["widget_id"]
            if widget_id in self.active_widgets:
                del self.active_widgets[widget_id]

            return {
                "action_type": action,
                "widget_removed": True,
                "permanent": action == "permanent_delete",
            }

        else:
            return {
                "action_type": "unknown",
                "message": f"Action '{action}' not implemented",
            }

    async def get_widget_analytics(self, days: int = 30) -> dict[str, Any]:
        """Get analytics for widget performance"""
        cutoff_date = datetime.now() - timedelta(days=days)

        recent_interactions = [
            i
            for i in self.interaction_history
            if datetime.fromisoformat(i["timestamp"]) >= cutoff_date
        ]

        # Interaction type breakdown
        interaction_breakdown = {}
        for interaction in recent_interactions:
            itype = interaction["interaction_type"]
            interaction_breakdown[itype] = interaction_breakdown.get(itype, 0) + 1

        # Widget type performance
        widget_performance = {}
        for widget in self.active_widgets.values():
            wtype = widget["type"]
            if wtype not in widget_performance:
                widget_performance[wtype] = {"created": 0, "interactions": 0}
            widget_performance[wtype]["created"] += 1

        # Count interactions per widget type
        for interaction in recent_interactions:
            widget_id = interaction["widget_id"]
            if widget_id in self.active_widgets:
                wtype = self.active_widgets[widget_id]["type"]
                if wtype in widget_performance:
                    widget_performance[wtype]["interactions"] += 1

        return {
            "period_days": days,
            "total_interactions": len(recent_interactions),
            "active_widgets": len(self.active_widgets),
            "interaction_breakdown": interaction_breakdown,
            "widget_performance": widget_performance,
            "top_interactions": sorted(
                interaction_breakdown.items(), key=lambda x: x[1], reverse=True
            )[:5],
        }

    async def cleanup_expired_widgets(self):
        """Remove expired widgets from active widgets"""
        current_time = datetime.now()
        expired_widgets = []

        for widget_id, widget in list(self.active_widgets.items()):
            expiry_time = datetime.fromisoformat(widget["expires_at"])
            if current_time >= expiry_time:
                expired_widgets.append(widget_id)
                del self.active_widgets[widget_id]

        if expired_widgets:
            logger.info(f"Cleaned up {len(expired_widgets)} expired widgets")

        return len(expired_widgets)

    async def health_check(self) -> dict[str, Any]:
        """Health check for widget engine"""
        return {
            "status": "healthy",
            "active_widgets": len(self.active_widgets),
            "total_interactions": len(self.interaction_history),
            "widget_types_configured": len(self.widget_templates),
            "seasonal_themes_available": len(self.seasonal_themes),
        }


# Global widget engine instance
_global_widget_engine = None


def get_widget_engine() -> WidgetEngine:
    """Get the global widget engine instance"""
    global _global_widget_engine
    if _global_widget_engine is None:
        _global_widget_engine = WidgetEngine()
    return _global_widget_engine
