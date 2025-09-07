"""
Tier Manager for NIΛS Subscription System
Manages T1 (Premium), T2 (Enhanced), T3 (Basic/Freemium) tiers
"""
import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class TierManager:
    """
    Manages NIΛS subscription tiers and user permissions.

    Tier Structure:
    - T1 (Premium): Unlimited capacity, ad-free, optional feedback
    - T2 (Enhanced): 10 items for 14 days, Assistant Mode
    - T3 (Basic): 5 items for 7 days, mandatory feedback
    """

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = Path(storage_path) if storage_path else Path("data/tiers")
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.user_tiers: dict[str, dict[str, Any]] = {}
        self.tier_configs = self._initialize_tier_configs()
        self.subscription_analytics = {}

        logger.info("Tier Manager initialized")

    def _initialize_tier_configs(self) -> dict[str, dict[str, Any]]:
        """Initialize tier configuration"""
        return {
            "T1": {
                "name": "Premium",
                "display_name": "Premium Experience",
                "price_monthly": 29.99,
                "price_yearly": 299.99,
                "bin_capacity": "unlimited",
                "duration_days": "unlimited",
                "features": {
                    "ad_free": True,
                    "optional_feedback": True,
                    "permanent_deletion": True,
                    "advanced_widgets": True,
                    "priority_support": True,
                    "dream_customization": True,
                    "export_data": True,
                    "api_access": True,
                },
                "widget_interactions": {
                    "tap": "instant_pitch",
                    "double_tap": "detailed_view",
                    "hold": "add_to_basket",
                    "swipe": "permanent_delete",
                    "triple_tap": "ai_assistant",
                },
                "limits": {
                    "daily_messages": "unlimited",
                    "monthly_messages": "unlimited",
                    "storage_mb": "unlimited",
                    "api_calls_daily": 10000,
                },
            },
            "T2": {
                "name": "Enhanced",
                "display_name": "Enhanced Experience",
                "price_monthly": 9.99,
                "price_yearly": 99.99,
                "bin_capacity": 10,
                "duration_days": 14,
                "features": {
                    "ad_free": False,
                    "optional_feedback": False,
                    "permanent_deletion": False,
                    "advanced_widgets": True,
                    "priority_support": False,
                    "dream_customization": False,
                    "export_data": True,
                    "api_access": False,
                },
                "widget_interactions": {
                    "tap": "pitch",
                    "double_tap": "detailed_view",
                    "hold": "add_to_basket",
                    "swipe": "move_to_bin",
                    "triple_tap": "assistant_mode",
                },
                "limits": {
                    "daily_messages": 50,
                    "monthly_messages": 1000,
                    "storage_mb": 500,
                    "api_calls_daily": 100,
                },
            },
            "T3": {
                "name": "Basic",
                "display_name": "Basic Experience",
                "price_monthly": 0,
                "price_yearly": 0,
                "bin_capacity": 5,
                "duration_days": 7,
                "features": {
                    "ad_free": False,
                    "optional_feedback": False,
                    "permanent_deletion": False,
                    "advanced_widgets": False,
                    "priority_support": False,
                    "dream_customization": False,
                    "export_data": False,
                    "api_access": False,
                },
                "widget_interactions": {
                    "tap": "basic_pitch",
                    "double_tap": "basic_details",
                    "hold": "add_to_basket",
                    "swipe": "move_to_bin",
                },
                "limits": {
                    "daily_messages": 10,
                    "monthly_messages": 200,
                    "storage_mb": 50,
                    "api_calls_daily": 0,
                },
                "requirements": {
                    "mandatory_feedback": True,
                    "view_ads": True,
                    "data_sharing_consent": True,
                },
            },
        }

    async def register_user(
        self, user_id: str, tier: str = "T3", subscription_data: Optional[dict] = None
    ) -> dict[str, Any]:
        """Register a new user with specified tier"""
        try:
            if tier not in self.tier_configs:
                tier = "T3"  # Default to basic tier

            user_tier_data = {
                "user_id": user_id,
                "tier": tier,
                "registered_at": datetime.now(timezone.utc).isoformat(),
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "subscription_data": subscription_data or {},
                "usage_stats": {
                    "messages_received": 0,
                    "widgets_interacted": 0,
                    "feedback_provided": 0,
                    "bin_items": 0,
                    "last_activity": None,
                },
                "tier_history": [
                    {
                        "tier": tier,
                        "started_at": datetime.now(timezone.utc).isoformat(),
                        "reason": "initial_registration",
                    }
                ],
                "preferences": {
                    "widget_style": "default",
                    "notification_frequency": "normal",
                    "content_categories": [],
                    "blocked_brands": [],
                },
            }

            self.user_tiers[user_id] = user_tier_data
            await self._save_user_tier_data(user_id)

            logger.info(f"User {user_id} registered with tier {tier}")

            return {
                "success": True,
                "user_id": user_id,
                "tier": tier,
                "tier_config": self.tier_configs[tier],
            }

        except Exception as e:
            logger.error(f"Failed to register user {user_id}: {e}")
            return {"success": False, "error": str(e)}

    async def get_user_tier(self, user_id: str) -> Optional[dict[str, Any]]:
        """Get user's current tier information"""
        if user_id not in self.user_tiers:
            # Try to load from storage
            await self._load_user_tier_data(user_id)

        return self.user_tiers.get(user_id)

    async def update_user_tier(self, user_id: str, new_tier: str, reason: str = "manual_update") -> dict[str, Any]:
        """Update user's tier"""
        try:
            if new_tier not in self.tier_configs:
                return {"success": False, "error": f"Invalid tier: {new_tier}"}

            user_data = await self.get_user_tier(user_id)
            if not user_data:
                return {"success": False, "error": "User not found"}

            old_tier = user_data["tier"]

            # Update tier
            user_data["tier"] = new_tier
            user_data["last_updated"] = datetime.now(timezone.utc).isoformat()

            # Add to tier history
            user_data["tier_history"].append(
                {
                    "tier": new_tier,
                    "started_at": datetime.now(timezone.utc).isoformat(),
                    "previous_tier": old_tier,
                    "reason": reason,
                }
            )

            # Update subscription analytics
            await self._update_subscription_analytics(old_tier, new_tier, reason)

            # Save changes
            await self._save_user_tier_data(user_id)

            logger.info(f"User {user_id} tier updated from {old_tier} to {new_tier}")

            return {
                "success": True,
                "user_id": user_id,
                "old_tier": old_tier,
                "new_tier": new_tier,
                "tier_config": self.tier_configs[new_tier],
            }

        except Exception as e:
            logger.error(f"Failed to update tier for {user_id}: {e}")
            return {"success": False, "error": str(e)}

    async def get_processing_config(self, tier: str) -> dict[str, Any]:
        """Get processing configuration for a specific tier"""
        if tier not in self.tier_configs:
            tier = "T3"  # Default fallback

        config = self.tier_configs[tier].copy()
        config["processing_rules"] = {
            "require_feedback": tier == "T3",
            "show_ads": not config["features"].get("ad_free", False),
            "enable_advanced_features": config["features"].get("advanced_widgets", False),
            "api_enabled": config["features"].get("api_access", False),
        }

        return config

    async def apply_tier_filters(self, message: dict[str, Any], processing_config: dict[str, Any]) -> dict[str, Any]:
        """Apply tier-specific filters to a message"""
        filtered_message = message.copy()

        # Add tier-specific metadata
        filtered_message["tier_info"] = {
            "tier": processing_config["name"],
            "features_available": processing_config["features"],
            "widget_interactions": processing_config["widget_interactions"],
        }

        # Apply content filtering based on tier
        if not processing_config["features"].get("advanced_widgets", False):
            # Remove advanced widget configurations
            if "advanced_widget_config" in filtered_message:
                del filtered_message["advanced_widget_config"]

        if processing_config["processing_rules"]["show_ads"]:
            # Add ad placement opportunities
            filtered_message["ad_placement_enabled"] = True
            filtered_message["ad_frequency"] = "standard" if processing_config["name"] == "Enhanced" else "high"

        if processing_config["processing_rules"]["require_feedback"]:
            filtered_message["feedback_required"] = True
            filtered_message["feedback_prompt"] = "Please rate this recommendation to help us improve"

        return filtered_message

    async def check_tier_limits(self, user_id: str, action: str) -> dict[str, Any]:
        """Check if user has exceeded tier limits"""
        user_data = await self.get_user_tier(user_id)
        if not user_data:
            return {"allowed": False, "reason": "user_not_found"}

        tier = user_data["tier"]
        config = self.tier_configs[tier]
        usage = user_data["usage_stats"]

        # Check daily/monthly limits
        datetime.now(timezone.utc).date()
        datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        if action == "message_delivery":
            daily_limit = config["limits"].get("daily_messages")
            monthly_limit = config["limits"].get("monthly_messages")

            if daily_limit != "unlimited":
                # Would need to track daily usage - simplified for now
                if usage.get("daily_messages_today", 0) >= daily_limit:
                    return {
                        "allowed": False,
                        "reason": "daily_limit_exceeded",
                        "limit": daily_limit,
                    }

            if monthly_limit != "unlimited" and usage.get("monthly_messages", 0) >= monthly_limit:
                return {
                    "allowed": False,
                    "reason": "monthly_limit_exceeded",
                    "limit": monthly_limit,
                }

        elif action == "api_call":
            api_limit = config["limits"].get("api_calls_daily", 0)
            if api_limit == 0:
                return {"allowed": False, "reason": "api_not_available_in_tier"}

            if usage.get("api_calls_today", 0) >= api_limit:
                return {
                    "allowed": False,
                    "reason": "api_daily_limit_exceeded",
                    "limit": api_limit,
                }

        return {"allowed": True}

    async def update_usage_stats(self, user_id: str, action: str, metadata: Optional[dict] = None):
        """Update user's usage statistics"""
        user_data = await self.get_user_tier(user_id)
        if not user_data:
            return

        usage = user_data["usage_stats"]
        usage["last_activity"] = datetime.now(timezone.utc).isoformat()

        if action == "message_received":
            usage["messages_received"] = usage.get("messages_received", 0) + 1
        elif action == "widget_interaction":
            usage["widgets_interacted"] = usage.get("widgets_interacted", 0) + 1
        elif action == "feedback_provided":
            usage["feedback_provided"] = usage.get("feedback_provided", 0) + 1
        elif action == "bin_item":
            usage["bin_items"] = usage.get("bin_items", 0) + 1

        await self._save_user_tier_data(user_id)

    async def suggest_tier_upgrade(self, user_id: str) -> Optional[dict[str, Any]]:
        """Suggest tier upgrade based on usage patterns"""
        user_data = await self.get_user_tier(user_id)
        if not user_data:
            return None

        current_tier = user_data["tier"]
        usage = user_data["usage_stats"]

        suggestions = []

        # T3 to T2 upgrade suggestions
        if current_tier == "T3":
            if usage.get("messages_received", 0) > 150:  # High usage
                suggestions.append(
                    {
                        "suggested_tier": "T2",
                        "reason": "High message volume - get 10x more capacity",
                        "benefits": ["10 items vs 5", "14 days vs 7", "Assistant Mode"],
                        "savings_yearly": 20,  # $9.99*12 - 20% discount
                    }
                )

            if usage.get("widgets_interacted", 0) > 50:
                suggestions.append(
                    {
                        "suggested_tier": "T2",
                        "reason": "Active engagement - unlock enhanced features",
                        "benefits": ["Advanced widgets", "Enhanced customization"],
                        "trial_offer": "7-day free trial",
                    }
                )

        # T2 to T1 upgrade suggestions
        elif current_tier == "T2":
            if usage.get("bin_items", 0) > 8:  # Near capacity regularly
                suggestions.append(
                    {
                        "suggested_tier": "T1",
                        "reason": "You're using most of your capacity - go unlimited",
                        "benefits": ["Unlimited capacity", "No ads", "API access"],
                        "upgrade_discount": 25,
                    }
                )

        return suggestions[0] if suggestions else None

    async def get_tier_analytics(self, days: int = 30) -> dict[str, Any]:
        """Get analytics across all tiers"""
        datetime.now(timezone.utc) - timedelta(days=days)

        tier_stats = {"T1": 0, "T2": 0, "T3": 0}
        total_revenue = 0
        usage_by_tier = {"T1": [], "T2": [], "T3": []}

        for user_data in self.user_tiers.values():
            tier = user_data["tier"]
            tier_stats[tier] += 1

            # Calculate revenue
            tier_price = self.tier_configs[tier]["price_monthly"]
            total_revenue += tier_price

            # Collect usage stats
            usage_by_tier[tier].append(user_data["usage_stats"])

        # Calculate average usage per tier
        avg_usage = {}
        for tier, usage_list in usage_by_tier.items():
            if usage_list:
                avg_usage[tier] = {
                    "avg_messages": sum(u.get("messages_received", 0) for u in usage_list) / len(usage_list),
                    "avg_interactions": sum(u.get("widgets_interacted", 0) for u in usage_list) / len(usage_list),
                    "avg_feedback": sum(u.get("feedback_provided", 0) for u in usage_list) / len(usage_list),
                }
            else:
                avg_usage[tier] = {
                    "avg_messages": 0,
                    "avg_interactions": 0,
                    "avg_feedback": 0,
                }

        return {
            "period_days": days,
            "total_users": len(self.user_tiers),
            "tier_distribution": tier_stats,
            "monthly_revenue": total_revenue,
            "average_usage_by_tier": avg_usage,
            "conversion_opportunities": await self._calculate_conversion_opportunities(),
        }

    async def _calculate_conversion_opportunities(self) -> dict[str, Any]:
        """Calculate potential tier upgrade opportunities"""
        upgrade_candidates = {"T3_to_T2": 0, "T2_to_T1": 0}

        for user_id in self.user_tiers:
            suggestion = await self.suggest_tier_upgrade(user_id)
            if suggestion:
                if suggestion["suggested_tier"] == "T2":
                    upgrade_candidates["T3_to_T2"] += 1
                elif suggestion["suggested_tier"] == "T1":
                    upgrade_candidates["T2_to_T1"] += 1

        return {
            "upgrade_candidates": upgrade_candidates,
            "potential_monthly_revenue": (
                upgrade_candidates["T3_to_T2"] * 9.99 + upgrade_candidates["T2_to_T1"] * 20.00
            ),
        }

    async def _update_subscription_analytics(self, old_tier: str, new_tier: str, reason: str):
        """Update subscription change analytics"""
        if "tier_changes" not in self.subscription_analytics:
            self.subscription_analytics["tier_changes"] = []

        self.subscription_analytics["tier_changes"].append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "old_tier": old_tier,
                "new_tier": new_tier,
                "reason": reason,
                "direction": ("upgrade" if new_tier < old_tier else "downgrade"),  # T1 < T2 < T3
            }
        )

    async def _save_user_tier_data(self, user_id: str):
        """Save user tier data to storage"""
        try:
            user_file = self.storage_path / f"{user_id}.json"
            with open(user_file, "w", encoding="utf-8") as f:
                json.dump(self.user_tiers[user_id], f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save user tier data for {user_id}: {e}")

    async def _load_user_tier_data(self, user_id: str):
        """Load user tier data from storage"""
        try:
            user_file = self.storage_path / f"{user_id}.json"
            if user_file.exists():
                with open(user_file, encoding="utf-8") as f:
                    self.user_tiers[user_id] = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load user tier data for {user_id}: {e}")

    async def health_check(self) -> dict[str, Any]:
        """Health check for tier manager"""
        return {
            "status": "healthy",
            "total_users": len(self.user_tiers),
            "tiers_configured": len(self.tier_configs),
            "storage_path": str(self.storage_path),
            "storage_accessible": self.storage_path.exists() and self.storage_path.is_dir(),
        }


# Global tier manager instance
_global_tier_manager = None


def get_tier_manager() -> TierManager:
    """Get the global tier manager instance"""
    global _global_tier_manager
    if _global_tier_manager is None:
        _global_tier_manager = TierManager()
    return _global_tier_manager
