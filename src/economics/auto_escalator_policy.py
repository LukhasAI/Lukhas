#!/usr/bin/env python3
"""
Auto-Escalator Split Policy
Dynamic profit sharing that evolves from 40/60 → 80/20 based on user value creation
Implements rule-based escalation with transparency and fairness
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class EscalatorTier(Enum):
    """User tiers with associated profit sharing splits"""

    GUEST = "guest"  # 30/70 - New users, limited data
    VISITOR = "visitor"  # 40/60 - Basic engagement, some data
    FRIEND = "friend"  # 50/50 - Regular usage, good data quality
    TRUSTED = "trusted"  # 60/40 - High engagement, valuable insights
    INNER_CIRCLE = "inner_circle"  # 70/30 - Power users, exceptional value
    ROOT_DEV = "root_dev"  # 80/20 - Maximum tier, developer/partner level


class ValueContribution(Enum):
    """Types of value contributions that drive escalation"""

    DATA_SHARING = "data_sharing"  # Providing high-quality data
    ENGAGEMENT = "engagement"  # Active platform usage
    FEEDBACK = "feedback"  # Providing valuable feedback
    REFERRALS = "referrals"  # Bringing new users
    CONTENT_CREATION = "content_creation"  # Creating valuable content
    MERCHANT_ADVOCACY = "merchant_advocacy"  # Promoting merchant success
    PLATFORM_ADVOCACY = "platform_advocacy"  # Promoting LUKHAS


@dataclass
class SplitConfiguration:
    """Split configuration for a specific tier"""

    tier: EscalatorTier
    user_bps: int  # Basis points to user (out of 10000)
    platform_bps: int  # Basis points to platform (out of 10000)
    min_monthly_volume: float  # Minimum monthly transaction volume
    min_engagement_score: float  # Minimum engagement score (0-1)
    min_data_quality_score: float  # Minimum data quality score (0-1)
    tier_benefits: list[str]  # Additional benefits for this tier
    escalation_requirements: dict[str, Any]  # Requirements to reach next tier


@dataclass
class UserValueMetrics:
    """Comprehensive user value assessment"""

    user_id: str
    current_tier: EscalatorTier

    # Volume metrics
    monthly_transaction_volume: float
    total_lifetime_volume: float
    avg_order_value: float

    # Engagement metrics
    engagement_score: float  # 0-1 based on platform usage
    session_frequency: float  # Sessions per week
    time_on_platform: float  # Hours per month

    # Data quality metrics
    data_quality_score: float  # 0-1 based on data completeness/accuracy
    consent_breadth: float  # Percentage of available data shared
    data_freshness: float  # How recent/updated user data is

    # Value creation metrics
    feedback_score: float  # Quality of feedback provided
    referral_count: int  # Number of successful referrals
    merchant_satisfaction: float  # Merchant satisfaction with user
    platform_advocacy: float  # Social sharing, reviews, etc.

    # Computed fields
    total_value_score: float = 0.0
    next_tier_progress: float = 0.0
    escalation_eligible: bool = False
    last_updated: float = 0.0


class AutoEscalatorPolicy:
    """
    Dynamic profit sharing policy that rewards user value creation

    Core Philosophy:
    - Users who create more value should receive higher profit shares
    - Escalation is earned through sustained value contribution
    - Transparency in how splits are calculated and changed
    - Fair and objective criteria prevent arbitrary decisions
    """

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.split_configurations = self._initialize_split_configurations()
        self.value_weights = self._initialize_value_weights()
        self.escalation_cooldown = config.get("escalation_cooldown_days", 30)

    def _initialize_split_configurations(self) -> dict[EscalatorTier, SplitConfiguration]:
        """Initialize profit split configurations for each tier"""

        return {
            EscalatorTier.GUEST: SplitConfiguration(
                tier=EscalatorTier.GUEST,
                user_bps=3000,  # 30%
                platform_bps=7000,  # 70%
                min_monthly_volume=0.0,
                min_engagement_score=0.0,
                min_data_quality_score=0.0,
                tier_benefits=[
                    "Basic product recommendations",
                    "Standard delivery timing",
                    "Email support",
                ],
                escalation_requirements={
                    "min_volume": 100.0,
                    "min_engagement": 0.2,
                    "min_data_quality": 0.3,
                    "min_transactions": 3,
                },
            ),
            EscalatorTier.VISITOR: SplitConfiguration(
                tier=EscalatorTier.VISITOR,
                user_bps=4000,  # 40%
                platform_bps=6000,  # 60%
                min_monthly_volume=100.0,
                min_engagement_score=0.2,
                min_data_quality_score=0.3,
                tier_benefits=[
                    "Personalized recommendations",
                    "Priority support",
                    "Early access to deals",
                ],
                escalation_requirements={
                    "min_volume": 500.0,
                    "min_engagement": 0.4,
                    "min_data_quality": 0.5,
                    "min_feedback_score": 0.3,
                },
            ),
            EscalatorTier.FRIEND: SplitConfiguration(
                tier=EscalatorTier.FRIEND,
                user_bps=5000,  # 50%
                platform_bps=5000,  # 50%
                min_monthly_volume=500.0,
                min_engagement_score=0.4,
                min_data_quality_score=0.5,
                tier_benefits=[
                    "Advanced personalization",
                    "Exclusive deals",
                    "Monthly bonus rewards",
                    "Beta feature access",
                ],
                escalation_requirements={
                    "min_volume": 1500.0,
                    "min_engagement": 0.6,
                    "min_data_quality": 0.7,
                    "min_feedback_score": 0.5,
                    "min_referrals": 2,
                },
            ),
            EscalatorTier.TRUSTED: SplitConfiguration(
                tier=EscalatorTier.TRUSTED,
                user_bps=6000,  # 60%
                platform_bps=4000,  # 40%
                min_monthly_volume=1500.0,
                min_engagement_score=0.6,
                min_data_quality_score=0.7,
                tier_benefits=[
                    "Premium recommendations",
                    "Concierge support",
                    "Quarterly bonus payments",
                    "Merchant partnership opportunities",
                    "Advanced analytics dashboard",
                ],
                escalation_requirements={
                    "min_volume": 5000.0,
                    "min_engagement": 0.8,
                    "min_data_quality": 0.8,
                    "min_feedback_score": 0.7,
                    "min_referrals": 5,
                    "min_platform_advocacy": 0.6,
                },
            ),
            EscalatorTier.INNER_CIRCLE: SplitConfiguration(
                tier=EscalatorTier.INNER_CIRCLE,
                user_bps=7000,  # 70%
                platform_bps=3000,  # 30%
                min_monthly_volume=5000.0,
                min_engagement_score=0.8,
                min_data_quality_score=0.8,
                tier_benefits=[
                    "Maximum profit sharing",
                    "White-glove service",
                    "Co-creation opportunities",
                    "Revenue sharing from referrals",
                    "Product advisory board access",
                    "Annual summit invitation",
                ],
                escalation_requirements={
                    "min_volume": 15000.0,
                    "min_engagement": 0.9,
                    "min_data_quality": 0.9,
                    "min_feedback_score": 0.8,
                    "min_referrals": 15,
                    "min_platform_advocacy": 0.8,
                    "special_qualification": "developer_or_enterprise_partner",
                },
            ),
            EscalatorTier.ROOT_DEV: SplitConfiguration(
                tier=EscalatorTier.ROOT_DEV,
                user_bps=8000,  # 80%
                platform_bps=2000,  # 20%
                min_monthly_volume=15000.0,
                min_engagement_score=0.9,
                min_data_quality_score=0.9,
                tier_benefits=[
                    "Maximum profit sharing (80/20)",
                    "Developer API access",
                    "Revenue sharing partnerships",
                    "Platform governance participation",
                    "Custom integration support",
                    "Direct founder access",
                ],
                escalation_requirements={},  # No higher tier
            ),
        }

    def _initialize_value_weights(self) -> dict[str, float]:
        """Initialize weights for different value contribution types"""

        return {
            "transaction_volume": 0.25,  # 25% weight on spending
            "engagement_score": 0.20,  # 20% weight on platform usage
            "data_quality_score": 0.20,  # 20% weight on data sharing
            "feedback_score": 0.15,  # 15% weight on feedback quality
            "referral_contribution": 0.10,  # 10% weight on referrals
            "platform_advocacy": 0.10,  # 10% weight on advocacy
        }

    async def calculate_user_value_metrics(self, user_id: str) -> UserValueMetrics:
        """
        Calculate comprehensive user value metrics
        This would integrate with various LUKHAS systems in production
        """

        # In production, this would query multiple systems:
        # - Transaction database for volume metrics
        # - Analytics system for engagement metrics
        # - Data quality service for data metrics
        # - Feedback system for satisfaction metrics
        # - Referral tracking for referral metrics

        # For now, return mock metrics for demonstration
        mock_metrics = UserValueMetrics(
            user_id=user_id,
            current_tier=EscalatorTier.VISITOR,  # Default starting tier
            # Volume metrics (would come from transaction database)
            monthly_transaction_volume=750.0,
            total_lifetime_volume=2500.0,
            avg_order_value=125.0,
            # Engagement metrics (would come from analytics)
            engagement_score=0.65,
            session_frequency=4.2,  # Sessions per week
            time_on_platform=8.5,  # Hours per month
            # Data quality metrics (would come from data quality service)
            data_quality_score=0.78,
            consent_breadth=0.85,  # 85% of available data shared
            data_freshness=0.92,  # Very recent data
            # Value creation metrics (would come from various services)
            feedback_score=0.72,
            referral_count=3,
            merchant_satisfaction=0.88,
            platform_advocacy=0.56,
            last_updated=time.time(),
        )

        # Calculate total value score
        mock_metrics.total_value_score = self._calculate_total_value_score(mock_metrics)

        return mock_metrics

    def _calculate_total_value_score(self, metrics: UserValueMetrics) -> float:
        """Calculate weighted total value score"""

        # Normalize transaction volume (log scale to prevent extreme outliers)
        import math

        volume_score = min(math.log10(max(metrics.monthly_transaction_volume, 1)) / 4, 1.0)

        # Normalize referral contribution
        referral_score = min(metrics.referral_count / 10, 1.0)  # Max score at 10 referrals

        # Weighted combination
        total_score = (
            self.value_weights["transaction_volume"] * volume_score
            + self.value_weights["engagement_score"] * metrics.engagement_score
            + self.value_weights["data_quality_score"] * metrics.data_quality_score
            + self.value_weights["feedback_score"] * metrics.feedback_score
            + self.value_weights["referral_contribution"] * referral_score
            + self.value_weights["platform_advocacy"] * metrics.platform_advocacy
        )

        return min(total_score, 1.0)

    async def evaluate_tier_escalation(self, user_id: str) -> dict[str, Any]:
        """
        Evaluate if user is eligible for tier escalation
        """

        # Get current user metrics
        metrics = await self.calculate_user_value_metrics(user_id)
        current_config = self.split_configurations[metrics.current_tier]

        # Check if user can escalate to next tier
        next_tier = self._get_next_tier(metrics.current_tier)

        if not next_tier:
            return {
                "escalation_eligible": False,
                "current_tier": metrics.current_tier.value,
                "reason": "Already at maximum tier",
                "current_split": f"{current_config.user_bps / 100:.0f}/{current_config.platform_bps / 100:.0f}",
            }

        next_config = self.split_configurations[next_tier]
        requirements = current_config.escalation_requirements

        # Check all escalation requirements
        requirement_results = {}

        # Volume requirement
        if "min_volume" in requirements:
            requirement_results["volume"] = {
                "required": requirements["min_volume"],
                "actual": metrics.monthly_transaction_volume,
                "met": metrics.monthly_transaction_volume >= requirements["min_volume"],
            }

        # Engagement requirement
        if "min_engagement" in requirements:
            requirement_results["engagement"] = {
                "required": requirements["min_engagement"],
                "actual": metrics.engagement_score,
                "met": metrics.engagement_score >= requirements["min_engagement"],
            }

        # Data quality requirement
        if "min_data_quality" in requirements:
            requirement_results["data_quality"] = {
                "required": requirements["min_data_quality"],
                "actual": metrics.data_quality_score,
                "met": metrics.data_quality_score >= requirements["min_data_quality"],
            }

        # Feedback requirement
        if "min_feedback_score" in requirements:
            requirement_results["feedback"] = {
                "required": requirements["min_feedback_score"],
                "actual": metrics.feedback_score,
                "met": metrics.feedback_score >= requirements["min_feedback_score"],
            }

        # Referral requirement
        if "min_referrals" in requirements:
            requirement_results["referrals"] = {
                "required": requirements["min_referrals"],
                "actual": metrics.referral_count,
                "met": metrics.referral_count >= requirements["min_referrals"],
            }

        # Platform advocacy requirement
        if "min_platform_advocacy" in requirements:
            requirement_results["platform_advocacy"] = {
                "required": requirements["min_platform_advocacy"],
                "actual": metrics.platform_advocacy,
                "met": metrics.platform_advocacy >= requirements["min_platform_advocacy"],
            }

        # Check if all requirements are met
        all_requirements_met = all(result["met"] for result in requirement_results.values())

        # Calculate progress toward next tier
        progress_scores = []
        for req_type, result in requirement_results.items():
            if result["required"] > 0:
                progress = min(result["actual"] / result["required"], 1.0)
                progress_scores.append(progress)

        next_tier_progress = sum(progress_scores) / len(progress_scores) if progress_scores else 0.0

        return {
            "escalation_eligible": all_requirements_met,
            "current_tier": metrics.current_tier.value,
            "next_tier": next_tier.value if next_tier else None,
            "current_split": f"{current_config.user_bps / 100:.0f}/{current_config.platform_bps / 100:.0f}",
            "next_split": f"{next_config.user_bps / 100:.0f}/{next_config.platform_bps / 100:.0f}"
            if next_tier
            else None,
            "requirements": requirement_results,
            "progress_to_next_tier": next_tier_progress,
            "total_value_score": metrics.total_value_score,
        }

    async def apply_tier_escalation(self, user_id: str, force: bool = False) -> dict[str, Any]:
        """
        Apply tier escalation if user is eligible
        """

        escalation_eval = await self.evaluate_tier_escalation(user_id)

        if not escalation_eval["escalation_eligible"] and not force:
            return {
                "escalated": False,
                "reason": "Requirements not met",
                "evaluation": escalation_eval,
            }

        # Check escalation cooldown (prevent frequent tier changes)
        last_escalation = await self._get_last_escalation_time(user_id)
        cooldown_expired = not last_escalation or (time.time() - last_escalation) > (
            self.escalation_cooldown * 24 * 3600
        )

        if not cooldown_expired and not force:
            return {
                "escalated": False,
                "reason": "Escalation cooldown active",
                "cooldown_expires": last_escalation + (self.escalation_cooldown * 24 * 3600),
            }

        # Apply escalation
        current_tier = EscalatorTier(escalation_eval["current_tier"])
        next_tier = EscalatorTier(escalation_eval["next_tier"])

        escalation_record = {
            "user_id": user_id,
            "from_tier": current_tier.value,
            "to_tier": next_tier.value,
            "escalated_at": time.time(),
            "reason": "automatic_qualification" if not force else "manual_override",
            "requirements_snapshot": escalation_eval["requirements"],
            "value_score_at_escalation": escalation_eval["total_value_score"],
        }

        # Store escalation record
        await self._store_escalation_record(escalation_record)

        # Update user tier
        await self._update_user_tier(user_id, next_tier)

        # Send notification to user
        await self._notify_user_escalation(user_id, escalation_record)

        new_config = self.split_configurations[next_tier]

        return {
            "escalated": True,
            "from_tier": current_tier.value,
            "to_tier": next_tier.value,
            "new_split": f"{new_config.user_bps / 100:.0f}/{new_config.platform_bps / 100:.0f}",
            "new_benefits": new_config.tier_benefits,
            "escalation_record_id": f"escalation_{int(time.time())}",
            "effective_date": datetime.utcnow().isoformat(),
        }

    async def calculate_transaction_split(
        self, user_id: str, transaction_amount: float, opportunity_id: str
    ) -> dict[str, Any]:
        """
        Calculate profit split for a specific transaction
        """

        # Get user's current tier
        user_metrics = await self.calculate_user_value_metrics(user_id)
        tier_config = self.split_configurations[user_metrics.current_tier]

        # Calculate base splits
        user_amount = (transaction_amount * tier_config.user_bps) / 10000
        platform_amount = (transaction_amount * tier_config.platform_bps) / 10000

        # Apply any special bonuses or adjustments
        bonuses = await self._calculate_transaction_bonuses(user_metrics, transaction_amount)

        user_amount += bonuses.get("user_bonus", 0.0)
        platform_amount += bonuses.get("platform_bonus", 0.0)

        # Ensure splits don't exceed transaction amount
        total_split = user_amount + platform_amount
        if total_split > transaction_amount:
            # Proportionally reduce to fit
            scale_factor = transaction_amount / total_split
            user_amount *= scale_factor
            platform_amount *= scale_factor

        return {
            "transaction_amount": transaction_amount,
            "user_tier": user_metrics.current_tier.value,
            "base_user_bps": tier_config.user_bps,
            "base_platform_bps": tier_config.platform_bps,
            "user_amount": round(user_amount, 2),
            "platform_amount": round(platform_amount, 2),
            "bonuses_applied": bonuses,
            "split_ratio": f"{tier_config.user_bps / 100:.0f}/{tier_config.platform_bps / 100:.0f}",
            "opportunity_id": opportunity_id,
            "calculated_at": datetime.utcnow().isoformat(),
        }

    async def generate_escalation_transparency_report(self, user_id: str) -> dict[str, Any]:
        """
        Generate transparent report showing how user's tier and splits are determined
        """

        metrics = await self.calculate_user_value_metrics(user_id)
        current_config = self.split_configurations[metrics.current_tier]
        escalation_eval = await self.evaluate_tier_escalation(user_id)

        # Get escalation history
        escalation_history = await self._get_escalation_history(user_id)

        report = {
            "user_id": user_id,
            "generated_at": datetime.utcnow().isoformat(),
            "current_status": {
                "tier": metrics.current_tier.value,
                "split_ratio": f"{current_config.user_bps / 100:.0f}/{current_config.platform_bps / 100:.0f}",
                "tier_benefits": current_config.tier_benefits,
                "total_value_score": metrics.total_value_score,
            },
            "value_breakdown": {
                "transaction_volume": {
                    "monthly": metrics.monthly_transaction_volume,
                    "lifetime": metrics.total_lifetime_volume,
                    "avg_order": metrics.avg_order_value,
                    "contribution_to_score": self.value_weights["transaction_volume"]
                    * min(metrics.monthly_transaction_volume / 1000, 1.0),
                },
                "engagement": {
                    "score": metrics.engagement_score,
                    "sessions_per_week": metrics.session_frequency,
                    "hours_per_month": metrics.time_on_platform,
                    "contribution_to_score": self.value_weights["engagement_score"]
                    * metrics.engagement_score,
                },
                "data_quality": {
                    "score": metrics.data_quality_score,
                    "consent_breadth": metrics.consent_breadth,
                    "data_freshness": metrics.data_freshness,
                    "contribution_to_score": self.value_weights["data_quality_score"]
                    * metrics.data_quality_score,
                },
                "community_contribution": {
                    "feedback_score": metrics.feedback_score,
                    "referrals": metrics.referral_count,
                    "platform_advocacy": metrics.platform_advocacy,
                    "total_contribution": (
                        self.value_weights["feedback_score"] * metrics.feedback_score
                        + self.value_weights["referral_contribution"]
                        * min(metrics.referral_count / 10, 1.0)
                        + self.value_weights["platform_advocacy"] * metrics.platform_advocacy
                    ),
                },
            },
            "escalation_status": escalation_eval,
            "tier_comparison": {
                tier.value: {
                    "split_ratio": f"{config.user_bps / 100:.0f}/{config.platform_bps / 100:.0f}",
                    "requirements": config.escalation_requirements,
                    "benefits": config.tier_benefits,
                }
                for tier, config in self.split_configurations.items()
            },
            "escalation_history": escalation_history,
            "methodology": {
                "value_weights": self.value_weights,
                "escalation_cooldown_days": self.escalation_cooldown,
                "philosophy": "Users who create more value receive higher profit shares",
                "fairness_principles": [
                    "Objective, measurable criteria",
                    "No arbitrary decisions",
                    "Transparent calculation methods",
                    "Sustainable reward progression",
                ],
            },
        }

        return report

    def _get_next_tier(self, current_tier: EscalatorTier) -> Optional[EscalatorTier]:
        """Get the next tier in progression"""
        tier_progression = [
            EscalatorTier.GUEST,
            EscalatorTier.VISITOR,
            EscalatorTier.FRIEND,
            EscalatorTier.TRUSTED,
            EscalatorTier.INNER_CIRCLE,
            EscalatorTier.ROOT_DEV,
        ]

        try:
            current_index = tier_progression.index(current_tier)
            if current_index < len(tier_progression) - 1:
                return tier_progression[current_index + 1]
        except ValueError:
            pass

        return None

    async def _calculate_transaction_bonuses(
        self, metrics: UserValueMetrics, amount: float
    ) -> dict[str, float]:
        """Calculate any special bonuses for transaction"""

        bonuses = {"user_bonus": 0.0, "platform_bonus": 0.0}

        # High-value transaction bonus (for large purchases)
        if amount > 1000:
            bonuses["user_bonus"] += amount * 0.001  # 0.1% bonus for high-value transactions

        # Data quality bonus
        if metrics.data_quality_score > 0.9:
            bonuses["user_bonus"] += amount * 0.005  # 0.5% bonus for excellent data quality

        # Engagement bonus
        if metrics.engagement_score > 0.8:
            bonuses["user_bonus"] += amount * 0.003  # 0.3% bonus for high engagement

        return bonuses

    async def _get_last_escalation_time(self, user_id: str) -> Optional[float]:
        """Get timestamp of user's last tier escalation"""
        # In production, this would query the escalation history database
        return None  # Mock: no previous escalations

    async def _store_escalation_record(self, record: dict[str, Any]) -> None:
        """Store escalation record for audit trail"""
        # In production, this would store in database
        logger.info(f"Escalation recorded: {record}")

    async def _update_user_tier(self, user_id: str, new_tier: EscalatorTier) -> None:
        """Update user's tier in user database"""
        # In production, this would update the user profile database
        logger.info(f"User {user_id} escalated to tier {new_tier.value}")

    async def _notify_user_escalation(
        self, user_id: str, escalation_record: dict[str, Any]
    ) -> None:
        """Send notification to user about tier escalation"""
        # In production, this would send email/push notification
        logger.info(f"Escalation notification sent to user {user_id}")

    async def _get_escalation_history(self, user_id: str) -> list[dict[str, Any]]:
        """Get user's escalation history"""
        # In production, this would query the escalation database
        return []  # Mock: no history


# Usage Example and Testing
async def main():
    """Example usage of auto-escalator policy"""

    config = {
        "escalation_cooldown_days": 30,
        "bonus_thresholds": {"high_value_transaction": 1000, "data_quality_bonus_threshold": 0.9},
    }

    policy = AutoEscalatorPolicy(config)
    user_id = "lukhas_user_12345"

    # Evaluate current tier eligibility
    print("=== Tier Escalation Evaluation ===")
    escalation_eval = await policy.evaluate_tier_escalation(user_id)
    print(json.dumps(escalation_eval, indent=2))

    # Calculate transaction split
    print("\n=== Transaction Split Calculation ===")
    transaction_split = await policy.calculate_transaction_split(
        user_id=user_id, transaction_amount=299.99, opportunity_id="opp_headphones_123"
    )
    print(json.dumps(transaction_split, indent=2))

    # Generate transparency report
    print("\n=== Transparency Report ===")
    transparency_report = await policy.generate_escalation_transparency_report(user_id)
    print(json.dumps(transparency_report, indent=2)[:1000] + "...")  # Truncated for brevity


if __name__ == "__main__":
    asyncio.run(main())
