#!/usr/bin/env python3
"""
NIAS Reward System - Mutual Benefit Model
Implements rewards and incentives for dream engagement

Original Vision from Audit:
- "In-game rewards for watching an ad"
- "Exclusive content offers"
- "Win-win scenario where users get something in return"
- "Turns advertising into something users actually appreciate"
"""
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional


class RewardType(Enum):
    """Types of rewards available in the system"""

    DREAM_CREDITS = "dream_credits"  # Virtual currency
    EXCLUSIVE_CONTENT = "exclusive_content"  # Special content access
    PREMIUM_FEATURE = "premium_feature"  # Temporary premium features
    DISCOUNT_CODE = "discount_code"  # Vendor discount codes
    EXPERIENCE_POINTS = "experience_points"  # XP for gamification
    ACHIEVEMENT = "achievement"  # Badges and achievements
    EARLY_ACCESS = "early_access"  # Early access to new features
    PERSONALIZATION = "personalization"  # Enhanced personalization options
    AD_FREE_TIME = "ad_free_time"  # Period without dreams
    DONATION_MATCH = "donation_match"  # Charity donation matching


class EngagementLevel(Enum):
    """Levels of user engagement with dreams"""

    VIEWED = "viewed"  # Dream was displayed
    INTERACTED = "interacted"  # User clicked or engaged
    COMPLETED = "completed"  # Full dream experience completed
    SHARED = "shared"  # Dream was shared
    PURCHASED = "purchased"  # Led to actual purchase
    DEEP_ENGAGEMENT = "deep_engagement"  # Extended interaction


@dataclass
class Reward:
    """A single reward instance"""

    reward_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: RewardType = RewardType.DREAM_CREDITS
    value: float = 0.0
    description: str = ""
    expires_at: Optional[datetime] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    redeemed: bool = False
    redeemed_at: Optional[datetime] = None


@dataclass
class UserRewardProfile:
    """User's reward history and status"""

    user_id: str
    total_credits: float = 0.0
    lifetime_earnings: float = 0.0
    current_level: int = 1
    experience_points: int = 0
    achievements: list[str] = field(default_factory=list)
    reward_history: list[Reward] = field(default_factory=list)
    pending_rewards: list[Reward] = field(default_factory=list)
    preferences: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)


class RewardEngine:
    """
    NIAS Reward System Engine

    Implements the mutual benefit model where users receive rewards
    for engaging with dreams, turning advertising into value exchange.
    """

    def __init__(self, config: Optional[dict] = None):
        self.config = config or self._default_config()
        self.user_profiles: dict[str, UserRewardProfile] = {}
        self.reward_catalog = self._initialize_reward_catalog()
        self.achievement_system = self._initialize_achievements()

    def _default_config(self) -> dict:
        """Default reward system configuration"""
        return {
            "base_rewards": {
                EngagementLevel.VIEWED: 1.0,
                EngagementLevel.INTERACTED: 5.0,
                EngagementLevel.COMPLETED: 10.0,
                EngagementLevel.SHARED: 15.0,
                EngagementLevel.PURCHASED: 50.0,
                EngagementLevel.DEEP_ENGAGEMENT: 25.0,
            },
            "multipliers": {
                "first_time_bonus": 2.0,
                "streak_bonus": 1.5,
                "quality_engagement": 1.3,
                "off_peak_bonus": 1.2,
            },
            "credit_exchange_rates": {
                "100_credits": "1_month_ad_free",
                "50_credits": "exclusive_content_unlock",
                "25_credits": "premium_feature_7_days",
                "10_credits": "vendor_discount_10_percent",
            },
            "level_thresholds": [
                0,  # Level 1
                100,  # Level 2
                300,  # Level 3
                600,  # Level 4
                1000,  # Level 5
                1500,  # Level 6
                2500,  # Level 7
                4000,  # Level 8
                6000,  # Level 9
                10000,  # Level 10+
            ],
        }

    def _initialize_reward_catalog(self) -> dict[str, dict]:
        """Initialize the catalog of available rewards"""
        return {
            "monthly_ad_free": {
                "type": RewardType.AD_FREE_TIME,
                "cost": 100,
                "description": "Enjoy 30 days without dream advertisements",
                "duration_days": 30,
            },
            "exclusive_story": {
                "type": RewardType.EXCLUSIVE_CONTENT,
                "cost": 50,
                "description": "Unlock exclusive dream narratives and experiences",
                "content_ids": ["story_001", "story_002", "story_003"],
            },
            "premium_week": {
                "type": RewardType.PREMIUM_FEATURE,
                "cost": 25,
                "description": "7 days of premium features and enhanced dreams",
                "duration_days": 7,
            },
            "vendor_discount": {
                "type": RewardType.DISCOUNT_CODE,
                "cost": 10,
                "description": "10% discount at participating dream vendors",
                "discount_percent": 10,
            },
            "charity_match": {
                "type": RewardType.DONATION_MATCH,
                "cost": 20,
                "description": "We'll match your donation to selected charities",
                "match_amount": 5.00,
            },
            "early_bird": {
                "type": RewardType.EARLY_ACCESS,
                "cost": 30,
                "description": "Get early access to new dream features",
                "access_days_early": 7,
            },
            "dream_designer": {
                "type": RewardType.PERSONALIZATION,
                "cost": 15,
                "description": "Customize your dream experience with special themes",
                "theme_options": ["cosmic", "nature", "abstract", "vintage"],
            },
        }

    def _initialize_achievements(self) -> dict[str, dict]:
        """Initialize achievement system"""
        return {
            "first_dream": {
                "name": "Dream Beginner",
                "description": "Experience your first dream",
                "reward_credits": 10,
                "icon": "🌙",
            },
            "dream_week": {
                "name": "Week Dreamer",
                "description": "Engage with dreams for 7 consecutive days",
                "reward_credits": 25,
                "icon": "📅",
            },
            "dream_month": {
                "name": "Lucid Master",
                "description": "30 days of dream engagement",
                "reward_credits": 100,
                "icon": "🏆",
            },
            "dream_sharer": {
                "name": "Dream Evangelist",
                "description": "Share 5 dreams with friends",
                "reward_credits": 50,
                "icon": "🌟",
            },
            "deep_dreamer": {
                "name": "Deep Dreamer",
                "description": "Spend over 5 minutes in a single dream",
                "reward_credits": 30,
                "icon": "🌊",
            },
            "dream_collector": {
                "name": "Dream Collector",
                "description": "Experience 100 unique dreams",
                "reward_credits": 200,
                "icon": "💎",
            },
            "ethical_dreamer": {
                "name": "Ethical Dreamer",
                "description": "Only engage with ethically positive dreams",
                "reward_credits": 75,
                "icon": "😇",
            },
        }

    async def process_engagement(
        self,
        user_id: str,
        dream_id: str,
        engagement_level: EngagementLevel,
        engagement_data: dict[str, Any],
    ) -> Reward:
        """
        Process user engagement with a dream and award appropriate rewards

        Args:
            user_id: User identifier
            dream_id: Dream that was engaged with
            engagement_level: Level of engagement
            engagement_data: Additional engagement metrics

        Returns:
            Reward awarded for this engagement
        """
        # Get or create user profile
        profile = self._get_or_create_profile(user_id)

        # Calculate base reward
        base_reward = self.config["base_rewards"][engagement_level]

        # Apply multipliers
        multiplier = 1.0

        # First time bonus
        if len(profile.reward_history) == 0:
            multiplier *= self.config["multipliers"]["first_time_bonus"]

        # Streak bonus
        if self._check_streak(profile):
            multiplier *= self.config["multipliers"]["streak_bonus"]

        # Quality engagement bonus
        if engagement_data.get("quality_score", 0) > 0.8:
            multiplier *= self.config["multipliers"]["quality_engagement"]

        # Off-peak bonus (encourage engagement during low-traffic times)
        if engagement_data.get("is_off_peak", False):
            multiplier *= self.config["multipliers"]["off_peak_bonus"]

        # Calculate final reward value
        reward_value = base_reward * multiplier

        # Create reward
        reward = Reward(
            type=RewardType.DREAM_CREDITS,
            value=reward_value,
            description=f"Reward for {engagement_level.value} engagement with dream",
            metadata={
                "dream_id": dream_id,
                "engagement_level": engagement_level.value,
                "multiplier": multiplier,
                "engagement_data": engagement_data,
            },
        )

        # Update profile
        profile.total_credits += reward_value
        profile.lifetime_earnings += reward_value
        profile.experience_points += int(reward_value * 10)
        profile.reward_history.append(reward)
        profile.last_activity = datetime.now(timezone.utc)

        # Check for level up
        self._check_level_up(profile)

        # Check for achievements
        await self._check_achievements(profile, engagement_level, engagement_data)

        return reward

    async def redeem_reward(self, user_id: str, catalog_item_id: str) -> Optional[Reward]:
        """
        Redeem credits for a reward from the catalog

        Args:
            user_id: User identifier
            catalog_item_id: Item to redeem from catalog

        Returns:
            Reward if successful, None if insufficient credits
        """
        profile = self._get_or_create_profile(user_id)

        if catalog_item_id not in self.reward_catalog:
            return None

        item = self.reward_catalog[catalog_item_id]
        cost = item["cost"]

        # Check if user has enough credits
        if profile.total_credits < cost:
            return None

        # Deduct credits
        profile.total_credits -= cost

        # Create reward
        reward = Reward(
            type=item["type"],
            value=cost,
            description=item["description"],
            metadata=item,
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),  # 30 day expiry
        )

        profile.pending_rewards.append(reward)

        return reward

    def _get_or_create_profile(self, user_id: str) -> UserRewardProfile:
        """Get existing profile or create new one"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserRewardProfile(user_id=user_id)
        return self.user_profiles[user_id]

    def _check_streak(self, profile: UserRewardProfile) -> bool:
        """Check if user has an active engagement streak"""
        if not profile.reward_history:
            return False

        # Check if last activity was within 24 hours
        last_activity = profile.last_activity
        return (datetime.now(timezone.utc) - last_activity).days <= 1

    def _check_level_up(self, profile: UserRewardProfile) -> bool:
        """Check if user has leveled up"""
        thresholds = self.config["level_thresholds"]
        xp = profile.experience_points

        new_level = 1
        for i, threshold in enumerate(thresholds):
            if xp >= threshold:
                new_level = i + 1
            else:
                break

        if new_level > profile.current_level:
            profile.current_level = new_level

            # Award level up bonus
            bonus = Reward(
                type=RewardType.DREAM_CREDITS,
                value=new_level * 10,
                description=f"Level up bonus! Reached level {new_level}",
            )
            profile.pending_rewards.append(bonus)
            profile.total_credits += bonus.value

            return True

        return False

    async def _check_achievements(
        self,
        profile: UserRewardProfile,
        engagement_level: EngagementLevel,
        engagement_data: dict[str, Any],
    ):
        """Check and award achievements"""

        # First dream achievement
        if len(profile.reward_history) == 1 and "first_dream" not in profile.achievements:
            self._award_achievement(profile, "first_dream")

        # Dream sharer achievement
        if engagement_level == EngagementLevel.SHARED:
            share_count = sum(1 for r in profile.reward_history if r.metadata.get("engagement_level") == "shared")
            if share_count >= 5 and "dream_sharer" not in profile.achievements:
                self._award_achievement(profile, "dream_sharer")

        # Deep dreamer achievement
        if engagement_level == EngagementLevel.DEEP_ENGAGEMENT and "deep_dreamer" not in profile.achievements:
            self._award_achievement(profile, "deep_dreamer")

        # Dream collector achievement
        unique_dreams = {r.metadata.get("dream_id") for r in profile.reward_history if r.metadata.get("dream_id")}
        if len(unique_dreams) >= 100 and "dream_collector" not in profile.achievements:
            self._award_achievement(profile, "dream_collector")

    def _award_achievement(self, profile: UserRewardProfile, achievement_id: str):
        """Award an achievement to a user"""
        if achievement_id in self.achievement_system:
            achievement = self.achievement_system[achievement_id]
            profile.achievements.append(achievement_id)

            # Award achievement credits
            reward = Reward(
                type=RewardType.ACHIEVEMENT,
                value=achievement["reward_credits"],
                description=f"Achievement unlocked: {achievement['name']}",
                metadata={"achievement": achievement},
            )

            profile.pending_rewards.append(reward)
            profile.total_credits += reward.value

    def get_user_rewards_summary(self, user_id: str) -> dict[str, Any]:
        """Get summary of user's rewards and status"""
        profile = self._get_or_create_profile(user_id)

        return {
            "user_id": user_id,
            "total_credits": profile.total_credits,
            "lifetime_earnings": profile.lifetime_earnings,
            "current_level": profile.current_level,
            "experience_points": profile.experience_points,
            "achievements": [
                {
                    "id": ach_id,
                    "name": self.achievement_system[ach_id]["name"],
                    "icon": self.achievement_system[ach_id]["icon"],
                }
                for ach_id in profile.achievements
            ],
            "pending_rewards": [
                {
                    "reward_id": r.reward_id,
                    "type": r.type.value,
                    "value": r.value,
                    "description": r.description,
                    "expires_at": r.expires_at.isoformat() if r.expires_at else None,
                }
                for r in profile.pending_rewards
                if not r.redeemed
            ],
            "available_catalog": [
                {
                    "id": item_id,
                    "cost": item["cost"],
                    "description": item["description"],
                    "affordable": profile.total_credits >= item["cost"],
                }
                for item_id, item in self.reward_catalog.items()
            ],
            "next_level_xp": (
                self.config["level_thresholds"][profile.current_level]
                if profile.current_level < len(self.config["level_thresholds"])
                else None
            ),
            "streak_active": self._check_streak(profile),
        }


if __name__ == "__main__":
    import asyncio

    async def test_reward_system():
        """Test the reward system"""
        engine = RewardEngine()

        print("=" * 80)
        print("🎁 NIAS REWARD SYSTEM TEST")
        print("=" * 80)

        # Simulate user engagement
        user_id = "test_user_001"

        # First engagement - should get first time bonus
        reward1 = await engine.process_engagement(
            user_id=user_id,
            dream_id="dream_001",
            engagement_level=EngagementLevel.VIEWED,
            engagement_data={"quality_score": 0.9},
        )
        print(f"\n🎆 First View Reward: {reward1.value:.1f} credits")
        print(f"   Description: {reward1.description}")

        # Interaction
        reward2 = await engine.process_engagement(
            user_id=user_id,
            dream_id="dream_001",
            engagement_level=EngagementLevel.INTERACTED,
            engagement_data={"quality_score": 0.85, "interaction_time": 30},
        )
        print(f"\n🔗 Interaction Reward: {reward2.value:.1f} credits")

        # Deep engagement
        reward3 = await engine.process_engagement(
            user_id=user_id,
            dream_id="dream_001",
            engagement_level=EngagementLevel.DEEP_ENGAGEMENT,
            engagement_data={"quality_score": 0.95, "engagement_time": 300},
        )
        print(f"\n🌊 Deep Engagement Reward: {reward3.value:.1f} credits")

        # Get summary
        summary = engine.get_user_rewards_summary(user_id)

        print("\n📊 User Rewards Summary:")
        print(f"   Total Credits: {summary['total_credits']:.1f}")
        print(f"   Level: {summary['current_level']}")
        print(f"   XP: {summary['experience_points']}")
        print(f"   Achievements: {len(summary['achievements'])}")

        if summary["achievements"]:
            print("\n🏆 Achievements Unlocked:")
            for ach in summary["achievements"]:
                print(f"   {ach['icon']} {ach['name']}")

        print("\n🛍️ Available Rewards:")
        for item in summary["available_catalog"][:3]:
            status = "✅" if item["affordable"] else "🔒"
            print(f"   {status} {item['description']} ({item['cost']} credits)")

        # Try to redeem a reward
        if summary["total_credits"] >= 10:
            redeemed = await engine.redeem_reward(user_id, "vendor_discount")
            if redeemed:
                print(f"\n🎉 Successfully redeemed: {redeemed.description}")

        print("\n" + "=" * 80)
        print("✅ Reward System Test Complete")
        print("=" * 80)

    # Run test
    asyncio.run(test_reward_system())
