#!/usr/bin/env python3
"""
Auto-Escalator Split Policy - Production Implementation
Rule-based profit sharing that evolves from 40/60 to 80/20 based on performance
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class EscalatorTier(Enum):
    BRONZE = "bronze"  # 40/60 split (user/platform)
    SILVER = "silver"  # 50/50 split
    GOLD = "gold"  # 60/40 split
    PLATINUM = "platinum"  # 70/30 split
    DIAMOND = "diamond"  # 80/20 split


@dataclass
class SplitPolicy:
    tier: EscalatorTier
    user_share_bps: int  # User's share in basis points
    platform_share_bps: int  # Platform's share in basis points
    min_volume_usd: float  # Minimum volume to maintain tier
    min_quality_score: float  # Minimum quality score to maintain tier
    required_metrics: dict  # Required performance metrics


@dataclass
class UserMetrics:
    total_volume_usd: float
    conversions_count: int
    average_order_value: float
    quality_score: float  # 0.0 to 1.0
    retention_rate: float  # % of repeat customers
    merchant_satisfaction: float  # Merchant rating
    days_active: int
    last_activity: datetime


class AutoEscalatorEngine:
    """
    Production-ready auto-escalator system for dynamic profit sharing
    Promotes high-performing users to higher revenue shares automatically
    """

    def __init__(self):
        # Define tier requirements and rewards
        self.tier_policies = {
            EscalatorTier.BRONZE: SplitPolicy(
                tier=EscalatorTier.BRONZE,
                user_share_bps=4000,  # 40%
                platform_share_bps=6000,  # 60%
                min_volume_usd=0.0,
                min_quality_score=0.0,
                required_metrics={
                    "min_conversions": 0,
                    "min_retention": 0.0,
                    "min_merchant_rating": 0.0,
                },
            ),
            EscalatorTier.SILVER: SplitPolicy(
                tier=EscalatorTier.SILVER,
                user_share_bps=5000,  # 50%
                platform_share_bps=5000,  # 50%
                min_volume_usd=1000.0,
                min_quality_score=0.6,
                required_metrics={
                    "min_conversions": 10,
                    "min_retention": 0.3,
                    "min_merchant_rating": 4.0,
                    "min_days_active": 30,
                },
            ),
            EscalatorTier.GOLD: SplitPolicy(
                tier=EscalatorTier.GOLD,
                user_share_bps=6000,  # 60%
                platform_share_bps=4000,  # 40%
                min_volume_usd=5000.0,
                min_quality_score=0.7,
                required_metrics={
                    "min_conversions": 50,
                    "min_retention": 0.4,
                    "min_merchant_rating": 4.2,
                    "min_days_active": 90,
                },
            ),
            EscalatorTier.PLATINUM: SplitPolicy(
                tier=EscalatorTier.PLATINUM,
                user_share_bps=7000,  # 70%
                platform_share_bps=3000,  # 30%
                min_volume_usd=25000.0,
                min_quality_score=0.8,
                required_metrics={
                    "min_conversions": 200,
                    "min_retention": 0.5,
                    "min_merchant_rating": 4.5,
                    "min_days_active": 180,
                },
            ),
            EscalatorTier.DIAMOND: SplitPolicy(
                tier=EscalatorTier.DIAMOND,
                user_share_bps=8000,  # 80%
                platform_share_bps=2000,  # 20%
                min_volume_usd=100000.0,
                min_quality_score=0.85,
                required_metrics={
                    "min_conversions": 1000,
                    "min_retention": 0.6,
                    "min_merchant_rating": 4.7,
                    "min_days_active": 365,
                },
            ),
        }

        # Performance bonuses that can boost splits temporarily
        self.performance_bonuses = {
            "streak_bonus": {
                "description": "Consistent performance bonus",
                "condition": "7+ consecutive days with conversions",
                "bonus_bps": 200,  # +2% to user share
                "duration_days": 30,
            },
            "volume_spike": {
                "description": "High volume period bonus",
                "condition": "3x average volume in 7 days",
                "bonus_bps": 300,  # +3% to user share
                "duration_days": 14,
            },
            "quality_excellence": {
                "description": "Exceptional quality rating",
                "condition": "Quality score >0.9 for 30 days",
                "bonus_bps": 150,  # +1.5% to user share
                "duration_days": 60,
            },
        }

    def calculate_user_tier(self, user_metrics: UserMetrics) -> EscalatorTier:
        """
        Calculate user's current tier based on performance metrics

        Args:
            user_metrics: User's current performance data

        Returns:
            Appropriate escalator tier
        """

        # Start from highest tier and work down
        tiers_descending = [
            EscalatorTier.DIAMOND,
            EscalatorTier.PLATINUM,
            EscalatorTier.GOLD,
            EscalatorTier.SILVER,
            EscalatorTier.BRONZE,
        ]

        for tier in tiers_descending:
            policy = self.tier_policies[tier]

            if self._meets_tier_requirements(user_metrics, policy):
                return tier

        # Default to Bronze if no tier requirements met
        return EscalatorTier.BRONZE

    def calculate_split(
        self,
        user_metrics: UserMetrics,
        conversion_value_usd: float,
        active_bonuses: Optional[list[str]] = None,
    ) -> dict:
        """
        Calculate profit split for a specific conversion

        Args:
            user_metrics: User's performance data
            conversion_value_usd: Value of this conversion
            active_bonuses: List of active bonus types

        Returns:
            Detailed split calculation
        """

        # Determine base tier
        base_tier = self.calculate_user_tier(user_metrics)
        base_policy = self.tier_policies[base_tier]

        # Start with base split
        user_share_bps = base_policy.user_share_bps
        platform_share_bps = base_policy.platform_share_bps

        # Apply performance bonuses
        bonus_details = []
        if active_bonuses:
            for bonus_type in active_bonuses:
                if bonus_type in self.performance_bonuses:
                    bonus = self.performance_bonuses[bonus_type]
                    bonus_bps = bonus["bonus_bps"]

                    user_share_bps += bonus_bps
                    platform_share_bps -= bonus_bps

                    bonus_details.append(
                        {
                            "type": bonus_type,
                            "description": bonus["description"],
                            "bonus_bps": bonus_bps,
                        }
                    )

        # Ensure splits don't exceed bounds (user max 90%, platform min 10%)
        user_share_bps = min(user_share_bps, 9000)
        platform_share_bps = max(platform_share_bps, 1000)

        # Normalize to ensure they add up to 10000 bps
        total_bps = user_share_bps + platform_share_bps
        if total_bps != 10000:
            adjustment = 10000 - total_bps
            platform_share_bps += adjustment

        # Calculate dollar amounts
        user_amount_usd = conversion_value_usd * (user_share_bps / 10000.0)
        platform_amount_usd = conversion_value_usd * (platform_share_bps / 10000.0)

        return {
            "base_tier": base_tier.value,
            "user_share_bps": user_share_bps,
            "platform_share_bps": platform_share_bps,
            "user_share_percentage": user_share_bps / 100.0,
            "platform_share_percentage": platform_share_bps / 100.0,
            "user_amount_usd": round(user_amount_usd, 2),
            "platform_amount_usd": round(platform_amount_usd, 2),
            "conversion_value_usd": conversion_value_usd,
            "active_bonuses": bonus_details,
            "calculation_timestamp": datetime.now(timezone.utc).isoformat(),
            "next_tier": self._get_next_tier(base_tier),
            "tier_progress": self._calculate_tier_progress(user_metrics, base_tier),
        }

    def check_tier_promotion(self, user_id: str, current_tier: EscalatorTier, updated_metrics: UserMetrics) -> dict:
        """
        Check if user qualifies for tier promotion

        Args:
            user_id: User identifier
            current_tier: User's current tier
            updated_metrics: Latest user metrics

        Returns:
            Promotion status and details
        """

        new_tier = self.calculate_user_tier(updated_metrics)

        if new_tier != current_tier:
            # Tier change detected
            tier_order = [
                EscalatorTier.BRONZE,
                EscalatorTier.SILVER,
                EscalatorTier.GOLD,
                EscalatorTier.PLATINUM,
                EscalatorTier.DIAMOND,
            ]

            current_index = tier_order.index(current_tier)
            new_index = tier_order.index(new_tier)

            is_promotion = new_index > current_index

            return {
                "tier_changed": True,
                "is_promotion": is_promotion,
                "previous_tier": current_tier.value,
                "new_tier": new_tier.value,
                "previous_split": f"{self.tier_policies[current_tier].user_share_bps / 100}%",
                "new_split": f"{self.tier_policies[new_tier].user_share_bps / 100}%",
                "effective_date": datetime.now(timezone.utc).isoformat(),
                "promotion_benefits": self._get_tier_benefits(new_tier),
                "celebration_message": self._get_promotion_message(current_tier, new_tier) if is_promotion else None,
            }

        return {
            "tier_changed": False,
            "current_tier": current_tier.value,
            "tier_progress": self._calculate_tier_progress(updated_metrics, current_tier),
        }

    def check_performance_bonuses(self, user_metrics: UserMetrics, recent_activity: list[dict]) -> list[str]:
        """
        Check which performance bonuses user qualifies for

        Args:
            user_metrics: User's performance data
            recent_activity: Recent conversion/activity data

        Returns:
            List of qualifying bonus types
        """

        active_bonuses = []

        # Check streak bonus (7+ consecutive days with conversions)
        if self._check_conversion_streak(recent_activity, days=7):
            active_bonuses.append("streak_bonus")

        # Check volume spike (3x average volume in 7 days)
        if self._check_volume_spike(recent_activity, multiplier=3.0, days=7):
            active_bonuses.append("volume_spike")

        # Check quality excellence (>0.9 quality score for 30 days)
        if user_metrics.quality_score > 0.9 and self._sustained_quality(user_metrics, days=30):
            active_bonuses.append("quality_excellence")

        return active_bonuses

    def generate_tier_requirements_guide(self) -> dict:
        """Generate user-friendly guide to tier requirements"""

        guide = {
            "tier_system_overview": {
                "description": "LUKHAS Auto-Escalator rewards high performers with increased profit sharing",
                "progression": "Bronze (40%) → Silver (50%) → Gold (60%) → Platinum (70%) → Diamond (80%)",
                "evaluation_period": "Metrics evaluated continuously, tier adjustments monthly",
            },
            "tier_requirements": {},
        }

        for tier, policy in self.tier_policies.items():
            guide["tier_requirements"][tier.value] = {
                "user_share": f"{policy.user_share_bps / 100}%",
                "platform_share": f"{policy.platform_share_bps / 100}%",
                "minimum_volume": f"${policy.min_volume_usd:,.2f}",
                "quality_score": f"{policy.min_quality_score:.1f}",
                "requirements": {
                    "conversions": policy.required_metrics.get("min_conversions", 0),
                    "retention_rate": f"{policy.required_metrics.get('min_retention', 0.0) * 100:.1f}%",
                    "merchant_rating": policy.required_metrics.get("min_merchant_rating", 0.0),
                    "active_days": policy.required_metrics.get("min_days_active", 0),
                },
                "benefits": self._get_tier_benefits(tier),
            }

        guide["performance_bonuses"] = {
            bonus_type: {
                "description": bonus["description"],
                "condition": bonus["condition"],
                "bonus": f"+{bonus['bonus_bps'] / 100}%",
                "duration": f"{bonus['duration_days']} days",
            }
            for bonus_type, bonus in self.performance_bonuses.items()
        }

        return guide

    # Private helper methods

    def _meets_tier_requirements(self, metrics: UserMetrics, policy: SplitPolicy) -> bool:
        """Check if user meets all requirements for a tier"""

        # Check basic requirements
        if metrics.total_volume_usd < policy.min_volume_usd:
            return False

        if metrics.quality_score < policy.min_quality_score:
            return False

        # Check specific metrics
        required = policy.required_metrics

        if metrics.conversions_count < required.get("min_conversions", 0):
            return False

        if metrics.retention_rate < required.get("min_retention", 0.0):
            return False

        if metrics.merchant_satisfaction < required.get("min_merchant_rating", 0.0):
            return False

        return not metrics.days_active < required.get("min_days_active", 0)

    def _get_next_tier(self, current_tier: EscalatorTier) -> Optional[str]:
        """Get the next tier above current tier"""
        tier_progression = [
            EscalatorTier.BRONZE,
            EscalatorTier.SILVER,
            EscalatorTier.GOLD,
            EscalatorTier.PLATINUM,
            EscalatorTier.DIAMOND,
        ]

        try:
            current_index = tier_progression.index(current_tier)
            if current_index < len(tier_progression) - 1:
                return tier_progression[current_index + 1].value
        except (ValueError, IndexError):
            pass

        return None

    def _calculate_tier_progress(self, metrics: UserMetrics, current_tier: EscalatorTier) -> dict:
        """Calculate progress toward next tier"""

        next_tier_name = self._get_next_tier(current_tier)
        if not next_tier_name:
            return {"status": "max_tier_reached", "progress": 1.0}

        next_tier = EscalatorTier(next_tier_name)
        next_policy = self.tier_policies[next_tier]

        # Calculate progress as percentage of requirements met
        progress_factors = []

        # Volume progress
        volume_progress = min(metrics.total_volume_usd / next_policy.min_volume_usd, 1.0)
        progress_factors.append(volume_progress)

        # Quality progress
        quality_progress = min(metrics.quality_score / next_policy.min_quality_score, 1.0)
        progress_factors.append(quality_progress)

        # Conversions progress
        min_conversions = next_policy.required_metrics.get("min_conversions", 0)
        if min_conversions > 0:
            conversions_progress = min(metrics.conversions_count / min_conversions, 1.0)
            progress_factors.append(conversions_progress)

        # Days active progress
        min_days = next_policy.required_metrics.get("min_days_active", 0)
        if min_days > 0:
            days_progress = min(metrics.days_active / min_days, 1.0)
            progress_factors.append(days_progress)

        # Overall progress is minimum of all factors (all requirements must be met)
        overall_progress = min(progress_factors)

        return {
            "next_tier": next_tier_name,
            "overall_progress": round(overall_progress, 3),
            "requirements_met": overall_progress >= 1.0,
            "details": {
                "volume": {
                    "current": metrics.total_volume_usd,
                    "required": next_policy.min_volume_usd,
                    "progress": round(volume_progress, 3),
                },
                "quality": {
                    "current": metrics.quality_score,
                    "required": next_policy.min_quality_score,
                    "progress": round(quality_progress, 3),
                },
                "conversions": {
                    "current": metrics.conversions_count,
                    "required": min_conversions,
                    "progress": round(min(metrics.conversions_count / max(min_conversions, 1), 1.0), 3),
                },
                "days_active": {
                    "current": metrics.days_active,
                    "required": min_days,
                    "progress": round(min(metrics.days_active / max(min_days, 1), 1.0), 3),
                },
            },
        }

    def _get_tier_benefits(self, tier: EscalatorTier) -> list[str]:
        """Get list of benefits for a tier"""
        benefits_map = {
            EscalatorTier.BRONZE: [
                "40% revenue share",
                "Basic analytics dashboard",
                "Email support",
            ],
            EscalatorTier.SILVER: [
                "50% revenue share",
                "Advanced analytics",
                "Priority email support",
                "Monthly performance review",
            ],
            EscalatorTier.GOLD: [
                "60% revenue share",
                "Custom campaign tools",
                "Dedicated account manager",
                "Weekly performance calls",
                "Early access to new features",
            ],
            EscalatorTier.PLATINUM: [
                "70% revenue share",
                "Premium campaign optimization",
                "Direct merchant introductions",
                "Quarterly business reviews",
                "Co-marketing opportunities",
            ],
            EscalatorTier.DIAMOND: [
                "80% revenue share",
                "White-label partnership options",
                "Exclusive merchant access",
                "Strategic partnership discussions",
                "Revenue forecasting tools",
                "Custom integration support",
            ],
        }

        return benefits_map.get(tier, [])

    def _get_promotion_message(self, old_tier: EscalatorTier, new_tier: EscalatorTier) -> str:
        """Generate celebration message for promotions"""
        old_share = self.tier_policies[old_tier].user_share_bps / 100
        new_share = self.tier_policies[new_tier].user_share_bps / 100

        return f"""
        🎉 Congratulations! You've been promoted to {new_tier.value.title()} tier!

        Your revenue share has increased from {old_share}% to {new_share}%

        New benefits include:
        {chr(10).join("• " + benefit for benefit in self._get_tier_benefits(new_tier))}

        Keep up the excellent work!
        """

    def _check_conversion_streak(self, recent_activity: list[dict], days: int) -> bool:
        """Check if user has conversion streak"""
        # Mock implementation - in production would analyze actual activity
        return len(recent_activity) >= days

    def _check_volume_spike(self, recent_activity: list[dict], multiplier: float, days: int) -> bool:
        """Check if user has volume spike"""
        # Mock implementation - in production would calculate volume ratios
        recent_volume = sum(activity.get("value_usd", 0) for activity in recent_activity[-days:])
        avg_volume = sum(activity.get("value_usd", 0) for activity in recent_activity) / len(recent_activity)
        return recent_volume >= avg_volume * multiplier

    def _sustained_quality(self, metrics: UserMetrics, days: int) -> bool:
        """Check if user has sustained quality over period"""
        # Mock implementation - in production would check historical quality data
        return metrics.days_active >= days and metrics.quality_score > 0.9


# Usage example and testing
def demo_auto_escalator():
    """Demonstrate auto-escalator functionality"""

    escalator = AutoEscalatorEngine()

    # Test user metrics for different scenarios
    test_users = [
        {
            "name": "New User",
            "metrics": UserMetrics(
                total_volume_usd=50.0,
                conversions_count=2,
                average_order_value=25.0,
                quality_score=0.5,
                retention_rate=0.2,
                merchant_satisfaction=3.8,
                days_active=5,
                last_activity=datetime.now(timezone.utc),
            ),
        },
        {
            "name": "Growing User",
            "metrics": UserMetrics(
                total_volume_usd=2500.0,
                conversions_count=25,
                average_order_value=100.0,
                quality_score=0.7,
                retention_rate=0.4,
                merchant_satisfaction=4.3,
                days_active=60,
                last_activity=datetime.now(timezone.utc),
            ),
        },
        {
            "name": "Power User",
            "metrics": UserMetrics(
                total_volume_usd=50000.0,
                conversions_count=500,
                average_order_value=100.0,
                quality_score=0.85,
                retention_rate=0.6,
                merchant_satisfaction=4.8,
                days_active=200,
                last_activity=datetime.now(timezone.utc),
            ),
        },
    ]

    print("🚀 LUKHAS Auto-Escalator Demo\n")

    for user in test_users:
        print(f"📊 {user['name']} Analysis:")

        # Calculate tier
        tier = escalator.calculate_user_tier(user["metrics"])
        print(f"   Current Tier: {tier.value.title()}")

        # Calculate split for $100 conversion
        split = escalator.calculate_split(user["metrics"], 100.0)
        print(
            f"   Split: User ${split['user_amount_usd']:.2f} ({split['user_share_percentage']:.1f}%) | Platform ${split['platform_amount_usd']:.2f}"
        )

        # Show tier progress
        if split["next_tier"]:
            progress = split["tier_progress"]
            print(f"   Next Tier: {split['next_tier'].title()} ({progress['overall_progress']  * 100:.1f}% complete)")
        else:
            print("   Status: Maximum tier achieved! 🏆")

        print()

    # Show tier requirements guide
    print("📋 Tier Requirements Guide:")
    guide = escalator.generate_tier_requirements_guide()

    for tier_name, requirements in guide["tier_requirements"].items():
        print(f"\n   {tier_name.title()}: {requirements['user_share']} revenue share")
        print(f"   • Volume: {requirements['minimum_volume']}")
        print(f"   • Conversions: {requirements['requirements']['conversions']}")
        print(f"   • Retention: {requirements['requirements']['retention_rate']}")


if __name__ == "__main__":
    demo_auto_escalator()
