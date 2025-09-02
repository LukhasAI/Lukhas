"""
API Budget Manager for NIAS Economic Platform.

This module manages daily spending budgets for users to ensure sustainable
unit economics while providing consciousness-aware advertising.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class BudgetTier:
    """Budget tier configuration."""

    name: str
    daily_limit: float
    features: list[str] = field(default_factory=list)


@dataclass
class UserBudgetUsage:
    """Tracks user's daily budget usage."""

    user_id: str
    tier: str
    daily_limit: float
    current_usage: float = 0.0
    last_reset: datetime = field(default_factory=datetime.now)
    usage_history: list[dict] = field(default_factory=list)


class APIBudgetManager:
    """
    Manages user API budgets to ensure sustainable unit economics.

    Features:
    - Tiered budget system (free: $0.50/day, premium: $2.00/day)
    - Real-time usage tracking
    - Automatic daily resets
    - Usage analytics and reporting
    """

    def __init__(self):
        self.tier_configs = {
            "free": BudgetTier(
                name="free",
                daily_limit=0.50,
                features=["basic_consciousness_profiling", "5_ads_per_day"],
            ),
            "premium": BudgetTier(
                name="premium",
                daily_limit=2.00,
                features=[
                    "advanced_profiling",
                    "biometric_integration",
                    "10_ads_per_day",
                ],
            ),
            "enterprise": BudgetTier(
                name="enterprise",
                daily_limit=10.00,
                features=["full_profiling", "real_time_biometrics", "unlimited_ads"],
            ),
        }
        self.user_budgets: dict[str, UserBudgetUsage] = {}

    async def check_budget(self, user_id: str, tier: str = "free") -> dict[str, any]:
        """
        Check if user is within their daily budget limit.

        Returns dict with within_budget (bool) and remaining_budget (float).
        """
        usage = await self._get_or_create_user_budget(user_id, tier)

        # Reset budget if new day
        if self._should_reset_budget(usage):
            await self._reset_daily_budget(usage)

        within_budget = usage.current_usage < usage.daily_limit
        remaining_budget = max(0, usage.daily_limit - usage.current_usage)

        return {
            "within_budget": within_budget,
            "remaining_budget": remaining_budget,
            "current_usage": usage.current_usage,
            "daily_limit": usage.daily_limit,
            "tier": usage.tier,
        }

    async def record_usage(
        self, user_id: str, cost: float, operation: str, metadata: Optional[dict] = None
    ) -> dict[str, any]:
        """
        Record API usage cost against user's daily budget.

        Returns updated budget status.
        """
        usage = self.user_budgets.get(user_id)
        if not usage:
            raise ValueError(f"No budget found for user {user_id}. Call check_budget first.")

        # Record the usage
        usage.current_usage += cost

        # Add to usage history
        usage_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "cost": cost,
            "metadata": metadata or {},
        }
        usage.usage_history.append(usage_entry)

        # Keep history manageable (last 100 entries)
        if len(usage.usage_history) > 100:
            usage.usage_history = usage.usage_history[-100:]

        return {
            "success": True,
            "new_usage": usage.current_usage,
            "remaining_budget": max(0, usage.daily_limit - usage.current_usage),
            "operation_recorded": operation,
        }

    async def get_user_analytics(self, user_id: str) -> dict[str, any]:
        """Get detailed analytics for a user's budget usage."""
        usage = self.user_budgets.get(user_id)
        if not usage:
            return {"error": "User not found"}

        # Calculate daily averages over last 7 days
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_usage = [
            entry for entry in usage.usage_history if datetime.fromisoformat(entry["timestamp"]) > seven_days_ago
        ]

        total_recent_cost = sum(entry["cost"] for entry in recent_usage)
        avg_daily_cost = total_recent_cost / 7 if recent_usage else 0

        # Most expensive operations
        operation_costs = {}
        for entry in recent_usage:
            op = entry["operation"]
            operation_costs[op] = operation_costs.get(op, 0) + entry["cost"]

        return {
            "user_id": user_id,
            "tier": usage.tier,
            "daily_limit": usage.daily_limit,
            "current_usage": usage.current_usage,
            "avg_daily_cost_7d": round(avg_daily_cost, 4),
            "total_operations_7d": len(recent_usage),
            "top_operations": sorted(operation_costs.items(), key=lambda x: x[1], reverse=True)[:5],
            "budget_utilization_rate": (round(avg_daily_cost / usage.daily_limit, 2) if usage.daily_limit > 0 else 0),
        }

    async def get_aggregate_metrics(self) -> dict[str, any]:
        """Get platform-wide budget metrics."""
        if not self.user_budgets:
            return {"total_users": 0, "total_allocated": 0, "total_used": 0}

        total_allocated = sum(usage.daily_limit for usage in self.user_budgets.values())
        total_used = sum(usage.current_usage for usage in self.user_budgets.values())

        tier_distribution = {}
        for usage in self.user_budgets.values():
            tier_distribution[usage.tier] = tier_distribution.get(usage.tier, 0) + 1

        return {
            "total_users": len(self.user_budgets),
            "total_allocated": round(total_allocated, 2),
            "total_used": round(total_used, 2),
            "utilization_rate": round(total_used / total_allocated if total_allocated > 0 else 0, 2),
            "tier_distribution": tier_distribution,
            "avg_user_budget": round(total_allocated / len(self.user_budgets), 2),
        }

    async def upgrade_user_tier(self, user_id: str, new_tier: str) -> dict[str, any]:
        """Upgrade user to a higher tier."""
        if new_tier not in self.tier_configs:
            return {"success": False, "error": f"Invalid tier: {new_tier}"}

        usage = self.user_budgets.get(user_id)
        if not usage:
            return {"success": False, "error": "User not found"}

        old_tier = usage.tier
        tier_config = self.tier_configs[new_tier]

        usage.tier = new_tier
        usage.daily_limit = tier_config.daily_limit

        return {
            "success": True,
            "old_tier": old_tier,
            "new_tier": new_tier,
            "new_daily_limit": tier_config.daily_limit,
            "features": tier_config.features,
        }

    async def _get_or_create_user_budget(self, user_id: str, tier: str) -> UserBudgetUsage:
        """Get existing user budget or create new one."""
        if user_id not in self.user_budgets:
            tier_config = self.tier_configs.get(tier, self.tier_configs["free"])
            self.user_budgets[user_id] = UserBudgetUsage(
                user_id=user_id, tier=tier, daily_limit=tier_config.daily_limit
            )
        return self.user_budgets[user_id]

    def _should_reset_budget(self, usage: UserBudgetUsage) -> bool:
        """Check if budget should be reset (new day)."""
        now = datetime.now()
        return now.date() > usage.last_reset.date()

    async def _reset_daily_budget(self, usage: UserBudgetUsage) -> None:
        """Reset user's daily budget for new day."""
        usage.current_usage = 0.0
        usage.last_reset = datetime.now()
        # Keep usage history but mark the reset point
