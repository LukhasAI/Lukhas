"""
NIAS Reward Engine - Mutual Benefit Model Implementation
Transforms advertising from interruption to opportunity
"""
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional

import streamlit as st


class RewardType(Enum):
    """Types of rewards users can earn"""

    CREDITS = "credits"
    POINTS = "points"
    EXCLUSIVE_CONTENT = "exclusive_content"
    PREMIUM_FEATURE = "premium_feature"
    DISCOUNT_CODE = "discount_code"
    ACHIEVEMENT = "achievement"
    BADGE = "badge"
    EXPERIENCE = "experience"


class ContentAccessLevel(Enum):
    """Content access tiers"""

    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    EXCLUSIVE = "exclusive"
    VIP = "vip"


@dataclass
class UserRewardProfile:
    """User's reward and benefit tracking"""

    user_id: str
    total_credits: float = 0.0
    total_points: int = 0
    experience_level: int = 1
    unlocked_content: list[str] = field(default_factory=list)
    active_benefits: dict[str, Any] = field(default_factory=dict)
    achievements: list[str] = field(default_factory=list)
    badges: list[str] = field(default_factory=list)
    engagement_history: list[dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)


@dataclass
class Reward:
    """Individual reward configuration"""

    reward_id: str
    reward_type: RewardType
    value: Any
    name: str
    description: str
    requirements: dict[str, Any] = field(default_factory=dict)
    expiry: Optional[datetime] = None
    is_stackable: bool = True
    max_redemptions: Optional[int] = None
    redemption_count: int = 0


@dataclass
class ExclusiveContent:
    """Exclusive content that can be unlocked"""

    content_id: str
    name: str
    description: str
    access_level: ContentAccessLevel
    unlock_requirements: dict[str, Any]
    content_type: str  # video, article, feature, tool, etc.
    value_proposition: str
    preview_available: bool = True
    unlocked_by: list[str] = field(default_factory=list)


class NIASRewardEngine:
    """
    Core reward engine for NIAS - implements mutual benefit model
    where users receive tangible benefits for ad engagement
    """

    def __init__(self):
        self.user_profiles: dict[str, UserRewardProfile] = {}
        self.rewards_catalog: dict[str, Reward] = {}
        self.exclusive_content: dict[str, ExclusiveContent] = {}
        self.engagement_multipliers: dict[str, float] = {
            "watched_full_ad": 1.0,
            "clicked_ad": 2.0,
            "shared_content": 3.0,
            "converted": 5.0,
            "referred_friend": 10.0,
        }
        self._initialize_default_rewards()
        self._initialize_exclusive_content()

    def _initialize_default_rewards(self):
        """Set up default reward types"""
        default_rewards = [
            Reward(
                reward_id="daily_credits",
                reward_type=RewardType.CREDITS,
                value=10,
                name="Daily Engagement Credits",
                description="Credits for daily ad engagement",
                requirements={"daily_engagement": 1},
            ),
            Reward(
                reward_id="milestone_100",
                reward_type=RewardType.ACHIEVEMENT,
                value="Century Viewer",
                name="100 Ad Milestone",
                description="Watched 100 ads with full attention",
                requirements={"total_ads_watched": 100},
            ),
            Reward(
                reward_id="premium_week",
                reward_type=RewardType.PREMIUM_FEATURE,
                value={"duration": "7_days", "tier": "premium"},
                name="Premium Week Pass",
                description="One week of premium features",
                requirements={"points": 1000},
            ),
        ]

        for reward in default_rewards:
            self.rewards_catalog[reward.reward_id] = reward

    def _initialize_exclusive_content(self):
        """Set up exclusive content library"""
        exclusive_items = [
            ExclusiveContent(
                content_id="advanced_analytics",
                name="Advanced Analytics Dashboard",
                description="Professional analytics tools",
                access_level=ContentAccessLevel.PREMIUM,
                unlock_requirements={"credits": 500, "level": 5},
                content_type="feature",
                value_proposition="10x deeper insights into your data",
            ),
            ExclusiveContent(
                content_id="ai_assistant_pro",
                name="AI Assistant Pro Mode",
                description="Advanced AI capabilities",
                access_level=ContentAccessLevel.EXCLUSIVE,
                unlock_requirements={"credits": 1000, "achievements": ["power_user"]},
                content_type="feature",
                value_proposition="Unlimited AI requests with priority processing",
            ),
            ExclusiveContent(
                content_id="masterclass_series",
                name="Expert Masterclass Series",
                description="Exclusive educational content",
                access_level=ContentAccessLevel.VIP,
                unlock_requirements={"points": 5000},
                content_type="video",
                value_proposition="Learn from industry leaders",
            ),
        ]

        for content in exclusive_items:
            self.exclusive_content[content.content_id] = content

    def process_ad_engagement(
        self,
        user_id: str,
        ad_id: str,
        engagement_type: str,
        engagement_duration: float,
        full_engagement: bool = False,
    ) -> dict[str, Any]:
        """
        Process user's ad engagement and calculate rewards
        This is the core of the mutual benefit model
        """
        profile = self._get_or_create_profile(user_id)

        # Calculate base reward
        base_credits = 1.0
        base_points = 10

        # Apply engagement multipliers
        multiplier = self.engagement_multipliers.get(engagement_type, 1.0)

        # Bonus for full engagement
        if full_engagement:
            multiplier *= 1.5

        # Duration bonus (longer engagement = more rewards)
        duration_bonus = min(engagement_duration / 30.0, 2.0)  # Cap at 2x for 30+ seconds

        # Calculate final rewards
        credits_earned = base_credits * multiplier * duration_bonus
        points_earned = int(base_points * multiplier * duration_bonus)

        # Update profile
        profile.total_credits += credits_earned
        profile.total_points += points_earned

        # Check for level up
        new_level = self._calculate_level(profile.total_points)
        level_up = new_level > profile.experience_level
        if level_up:
            profile.experience_level = new_level

        # Record engagement
        engagement_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ad_id": ad_id,
            "type": engagement_type,
            "duration": engagement_duration,
            "credits_earned": credits_earned,
            "points_earned": points_earned,
        }
        profile.engagement_history.append(engagement_record)
        profile.last_activity = datetime.now(timezone.utc)

        # Check for unlockable content
        newly_unlocked = self._check_unlockables(profile)

        # Check for achievements
        new_achievements = self._check_achievements(profile)

        return {
            "success": True,
            "credits_earned": credits_earned,
            "points_earned": points_earned,
            "total_credits": profile.total_credits,
            "total_points": profile.total_points,
            "level": profile.experience_level,
            "level_up": level_up,
            "newly_unlocked": newly_unlocked,
            "new_achievements": new_achievements,
            "message": self._generate_reward_message(credits_earned, points_earned, newly_unlocked, new_achievements),
        }

    def redeem_reward(self, user_id: str, reward_id: str) -> dict[str, Any]:
        """Redeem a specific reward"""
        profile = self._get_or_create_profile(user_id)

        if reward_id not in self.rewards_catalog:
            return {"success": False, "error": "Reward not found"}

        reward = self.rewards_catalog[reward_id]

        # Check requirements
        if not self._check_requirements(profile, reward.requirements):
            return {
                "success": False,
                "error": "Requirements not met",
                "requirements": reward.requirements,
            }

        # Check redemption limits
        if reward.max_redemptions and reward.redemption_count >= reward.max_redemptions:
            return {"success": False, "error": "Reward no longer available"}

        # Process redemption
        if reward.reward_type == RewardType.CREDITS:
            profile.total_credits += reward.value
        elif reward.reward_type == RewardType.POINTS:
            profile.total_points += reward.value
        elif reward.reward_type == RewardType.ACHIEVEMENT:
            profile.achievements.append(reward.value)
        elif reward.reward_type == RewardType.BADGE:
            profile.badges.append(reward.value)
        elif reward.reward_type == RewardType.PREMIUM_FEATURE:
            self._activate_premium_feature(profile, reward.value)

        reward.redemption_count += 1

        return {
            "success": True,
            "reward_type": reward.reward_type.value,
            "reward_value": reward.value,
            "message": f"Successfully redeemed: {reward.name}",
        }

    def unlock_exclusive_content(self, user_id: str, content_id: str) -> dict[str, Any]:
        """Unlock exclusive content using credits/points"""
        profile = self._get_or_create_profile(user_id)

        if content_id not in self.exclusive_content:
            return {"success": False, "error": "Content not found"}

        content = self.exclusive_content[content_id]

        # Check if already unlocked
        if content_id in profile.unlocked_content:
            return {
                "success": True,
                "already_unlocked": True,
                "message": "Content already unlocked",
            }

        # Check requirements
        if not self._check_requirements(profile, content.unlock_requirements):
            return {
                "success": False,
                "error": "Unlock requirements not met",
                "requirements": content.unlock_requirements,
                "current_stats": {
                    "credits": profile.total_credits,
                    "points": profile.total_points,
                    "level": profile.experience_level,
                },
            }

        # Deduct costs
        if "credits" in content.unlock_requirements:
            profile.total_credits -= content.unlock_requirements["credits"]
        if "points" in content.unlock_requirements:
            profile.total_points -= content.unlock_requirements["points"]

        # Unlock content
        profile.unlocked_content.append(content_id)
        content.unlocked_by.append(user_id)

        return {
            "success": True,
            "content_id": content_id,
            "content_name": content.name,
            "access_level": content.access_level.value,
            "message": f"Unlocked: {content.name}! {content.value_proposition}",
        }

    def get_user_rewards_dashboard(self, user_id: str) -> dict[str, Any]:
        """Get comprehensive rewards dashboard for user"""
        profile = self._get_or_create_profile(user_id)

        # Calculate available rewards
        available_rewards = []
        for reward_id, reward in self.rewards_catalog.items():
            if self._check_requirements(profile, reward.requirements):
                available_rewards.append(
                    {
                        "reward_id": reward_id,
                        "name": reward.name,
                        "description": reward.description,
                        "type": reward.reward_type.value,
                        "value": reward.value,
                    }
                )

        # Calculate unlockable content
        unlockable_content = []
        for content_id, content in self.exclusive_content.items():
            if content_id not in profile.unlocked_content:
                can_unlock = self._check_requirements(profile, content.unlock_requirements)
                unlockable_content.append(
                    {
                        "content_id": content_id,
                        "name": content.name,
                        "description": content.description,
                        "can_unlock": can_unlock,
                        "requirements": content.unlock_requirements,
                        "value_proposition": content.value_proposition,
                    }
                )

        # Calculate next level progress
        current_level_threshold = (profile.experience_level - 1) * 100
        next_level_threshold = profile.experience_level * 100
        level_progress = (
            (profile.total_points - current_level_threshold) / (next_level_threshold - current_level_threshold) * 100
        )

        return {
            "user_id": user_id,
            "credits": profile.total_credits,
            "points": profile.total_points,
            "level": profile.experience_level,
            "level_progress": level_progress,
            "next_level_points": next_level_threshold,
            "achievements": profile.achievements,
            "badges": profile.badges,
            "unlocked_content": profile.unlocked_content,
            "available_rewards": available_rewards,
            "unlockable_content": unlockable_content,
            "active_benefits": profile.active_benefits,
            "engagement_streak": self._calculate_streak(profile),
            "total_engagements": len(profile.engagement_history),
        }

    def _get_or_create_profile(self, user_id: str) -> UserRewardProfile:
        """Get or create user reward profile"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserRewardProfile(user_id=user_id)
        return self.user_profiles[user_id]

    def _calculate_level(self, total_points: int) -> int:
        """Calculate user level based on points"""
        return max(1, total_points // 100 + 1)

    def _check_requirements(self, profile: UserRewardProfile, requirements: dict[str, Any]) -> bool:
        """Check if user meets requirements"""
        for req_type, req_value in requirements.items():
            if (
                (req_type == "credits" and profile.total_credits < req_value)
                or (req_type == "points" and profile.total_points < req_value)
                or (req_type == "level" and profile.experience_level < req_value)
            ) or (req_type == "achievements" and not all(ach in profile.achievements for ach in req_value)):
                return False
        return True

    def _check_unlockables(self, profile: UserRewardProfile) -> list[dict[str, Any]]:
        """Check for newly unlockable content"""
        newly_unlocked = []

        for content_id, content in self.exclusive_content.items():
            if content_id in profile.unlocked_content:
                continue

            # Auto-unlock if requirements met and it's a free upgrade
            if (
                self._check_requirements(profile, content.unlock_requirements)
                and content.access_level == ContentAccessLevel.BASIC
            ):
                profile.unlocked_content.append(content_id)
                newly_unlocked.append(
                    {
                        "content_id": content_id,
                        "name": content.name,
                        "type": content.content_type,
                    }
                )

        return newly_unlocked

    def _check_achievements(self, profile: UserRewardProfile) -> list[str]:
        """Check for new achievements"""
        new_achievements = []

        # Engagement milestones
        total_engagements = len(profile.engagement_history)
        milestones = [10, 50, 100, 500, 1000]

        for milestone in milestones:
            achievement_name = f"engagement_{milestone}"
            if total_engagements >= milestone and achievement_name not in profile.achievements:
                profile.achievements.append(achievement_name)
                new_achievements.append(f"Milestone: {milestone} engagements!")

        # Level achievements
        if profile.experience_level >= 10 and "level_10" not in profile.achievements:
            profile.achievements.append("level_10")
            new_achievements.append("Power User: Level 10!")

        return new_achievements

    def _activate_premium_feature(self, profile: UserRewardProfile, feature_config: dict[str, Any]):
        """Activate premium feature for user"""
        duration = feature_config.get("duration", "7_days")
        days = int(duration.split("_")[0])

        profile.active_benefits[feature_config["tier"]] = {
            "activated_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=days)).isoformat(),
            "tier": feature_config["tier"],
        }

    def _calculate_streak(self, profile: UserRewardProfile) -> int:
        """Calculate engagement streak in days"""
        if not profile.engagement_history:
            return 0

        dates = set()
        for engagement in profile.engagement_history:
            date = datetime.fromisoformat(engagement["timestamp"]).date()
            dates.add(date)

        if not dates:
            return 0

        sorted_dates = sorted(dates)
        streak = 1
        current_streak = 1

        for i in range(1, len(sorted_dates)):
            if (sorted_dates[i] - sorted_dates[i - 1]).days == 1:
                current_streak += 1
                streak = max(streak, current_streak)
            else:
                current_streak = 1

        return streak

    def _generate_reward_message(
        self, credits: float, points: int, unlocked: list[dict], achievements: list[str]
    ) -> str:
        """Generate engaging reward message"""
        parts = []

        if credits > 0:
            parts.append(f"🪙 +{credits:.1f} credits")
        if points > 0:
            parts.append(f"⭐ +{points} points")

        if unlocked:
            parts.append(f"🎁 Unlocked: {unlocked[0]['name']}")

        if achievements:
            parts.append(f"🏆 {achievements[0]}")

        if not parts:
            return "Thank you for engaging!"

        return " | ".join(parts)


# Example usage and testing
if __name__ == "__main__":
    # Initialize reward engine
    reward_engine = NIASRewardEngine()

    # Simulate user engagement with an ad
    result = reward_engine.process_ad_engagement(
        user_id="user_123",
        ad_id="ad_456",
        engagement_type="watched_full_ad",
        engagement_duration=15.0,
        full_engagement=True,
    )

    print("Engagement Result:", json.dumps(result, indent=2))

    # Get user dashboard
    dashboard = reward_engine.get_user_rewards_dashboard("user_123")
    print("\nUser Dashboard:", json.dumps(dashboard, indent=2, default=str))

    # Try to unlock content
    unlock_result = reward_engine.unlock_exclusive_content(user_id="user_123", content_id="advanced_analytics")
    print("\nUnlock Result:", json.dumps(unlock_result, indent=2))
