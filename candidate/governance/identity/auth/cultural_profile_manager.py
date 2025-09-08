"""
LUKHAS Cultural Profile Manager - Emoji Cultural Exclusion Logic

This module implements cultural profile management for emoji safety and cultural
sensitivity in the LUKHAS authentication system. It provides real-time cultural
adaptation and emoji filtering based on user cultural context and accessibility needs.

Author: LUKHAS Team
Date: June 2025
Constitutional AI Guidelines: Enforced
Integration: Cultural sensitivity with constitutional oversight
"""

import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional

# Import constitutional enforcement
from .constitutional_gatekeeper import ConstitutionalLevel, get_constitutional_gatekeeper

# Configure cultural logging
logging.basicConfig(level=logging.INFO)
cultural_logger = logging.getLogger("LUKHAS_CULTURAL")


class CulturalContext(Enum):
    """Cultural contexts for emoji filtering"""

    WESTERN = "western"
    EASTERN = "eastern"
    ISLAMIC = "islamic"
    HINDU = "hindu"
    BUDDHIST = "buddhist"
    JEWISH = "jewish"
    CHRISTIAN = "christian"
    SECULAR = "secular"
    MULTICULTURAL = "multicultural"


class AccessibilityProfile(Enum):
    """Accessibility profiles for specialized filtering"""

    NEUROTYPICAL = "neurotypical"
    ADHD = "adhd"
    AUTISM_SPECTRUM = "autism_spectrum"
    DYSLEXIA = "dyslexia"
    VISUAL_IMPAIRMENT = "visual_impairment"
    COGNITIVE_ACCESSIBILITY = "cognitive_accessibility"


@dataclass
class CulturalProfile:
    """User cultural profile for personalized filtering"""

    primary_culture: CulturalContext
    secondary_cultures: list[CulturalContext]
    accessibility_profile: AccessibilityProfile
    language_preference: str
    age_group: Optional[str]  # "child", "teen", "adult", "senior"
    sensitivity_level: float  # 0.0 (permissive) to 1.0 (strict)
    custom_exclusions: list[str]
    custom_inclusions: list[str]
    created_at: datetime
    last_updated: datetime


class CulturalProfileManager:
    """
    Cultural profile manager for emoji safety and cultural sensitivity.

    This class manages cultural profiles and provides real-time emoji filtering
    based on cultural context, accessibility needs, and constitutional requirements.
    """

    def __init__(self, enforcement_level: ConstitutionalLevel = ConstitutionalLevel.STANDARD):
        self.constitutional_gatekeeper = get_constitutional_gatekeeper(enforcement_level)
        self.cultural_profiles: dict[str, CulturalProfile] = {}
        self.emoji_cultural_map = self._load_emoji_cultural_mappings()
        self.accessibility_map = self._load_accessibility_mappings()

        cultural_logger.info("Cultural Profile Manager initialized")

    def _load_emoji_cultural_mappings(self) -> dict[str, dict[str, Any]]:
        """Load comprehensive emoji cultural mappings"""
        return {
            # Religious symbols
            "☪️": {
                "categories": ["religious"],
                "primary_cultures": [CulturalContext.ISLAMIC],
                "sensitivity_level": 0.9,
                "safe_contexts": [
                    CulturalContext.ISLAMIC,
                    CulturalContext.MULTICULTURAL,
                ],
                "interpretation_variations": {
                    "islamic": "Sacred Islamic symbol",
                    "western": "Religious symbol",
                    "secular": "Moon and star symbol",
                },
            },
            "✡️": {
                "categories": ["religious"],
                "primary_cultures": [CulturalContext.JEWISH],
                "sensitivity_level": 0.9,
                "safe_contexts": [
                    CulturalContext.JEWISH,
                    CulturalContext.MULTICULTURAL,
                ],
                "interpretation_variations": {
                    "jewish": "Star of David - sacred symbol",
                    "western": "Jewish religious symbol",
                    "eastern": "Six-pointed star",
                },
            },
            "🙏": {
                "categories": ["gesture", "religious"],
                "primary_cultures": [CulturalContext.WESTERN, CulturalContext.EASTERN],
                "sensitivity_level": 0.3,
                "platform_variations": {
                    "ios": "Prayer/gratitude gesture",
                    "android": "Namaste/greeting gesture",
                    "windows": "High-five gesture",
                },
                "cultural_interpretations": {
                    "western": "Prayer or please",
                    "hindu": "Namaste greeting",
                    "buddhist": "Prayer or respect",
                    "secular": "Thank you or please",
                },
            },
            # Food and dietary restrictions
            "🍖": {
                "categories": ["food", "dietary"],
                "sensitivity_level": 0.7,
                "restricted_cultures": [
                    CulturalContext.HINDU,
                    CulturalContext.BUDDHIST,
                ],
                "partially_restricted": [
                    CulturalContext.ISLAMIC,
                    CulturalContext.JEWISH,
                ],
                "safe_contexts": [CulturalContext.WESTERN, CulturalContext.SECULAR],
            },
            "🥓": {
                "categories": ["food", "dietary"],
                "sensitivity_level": 0.8,
                "restricted_cultures": [
                    CulturalContext.ISLAMIC,
                    CulturalContext.JEWISH,
                ],
                "safe_contexts": [
                    CulturalContext.WESTERN,
                    CulturalContext.CHRISTIAN,
                    CulturalContext.SECULAR,
                ],
            },
            "🍷": {
                "categories": ["alcohol", "beverage"],
                "sensitivity_level": 0.6,
                "restricted_cultures": [CulturalContext.ISLAMIC],
                "age_restricted": ["child", "teen"],
                "safe_contexts": [
                    CulturalContext.WESTERN,
                    CulturalContext.CHRISTIAN,
                    CulturalContext.SECULAR,
                ],
            },
            # Gestures with cultural variations
            "👍": {
                "categories": ["gesture"],
                "sensitivity_level": 0.2,
                "cultural_interpretations": {
                    "western": "Approval, good job",
                    "middle_eastern": "Potentially offensive gesture",
                    "eastern": "Generally positive",
                },
                "safe_contexts": [
                    CulturalContext.WESTERN,
                    CulturalContext.EASTERN,
                    CulturalContext.SECULAR,
                ],
            },
            # Animals with cultural significance
            "🐷": {
                "categories": ["animal", "dietary"],
                "sensitivity_level": 0.8,
                "restricted_cultures": [
                    CulturalContext.ISLAMIC,
                    CulturalContext.JEWISH,
                ],
                "safe_contexts": [
                    CulturalContext.WESTERN,
                    CulturalContext.EASTERN,
                    CulturalContext.SECULAR,
                ],
            },
            "🐶": {
                "categories": ["animal"],
                "sensitivity_level": 0.3,
                "cultural_considerations": {
                    "islamic": "Dogs considered impure in some interpretations",
                    "western": "Beloved pets and companions",
                    "eastern": "Varies by region",
                },
            },
            # Symbols with multiple meanings
            "⚡": {
                "categories": ["symbol", "energy"],
                "sensitivity_level": 0.4,
                "cultural_interpretations": {
                    "western": "Energy, power, speed",
                    "political": "Historical associations with certain movements",
                    "modern": "Lightning, electricity",
                },
                "context_dependent": True,
            },
        }

    def _load_accessibility_mappings(
        self,
    ) -> dict[AccessibilityProfile, dict[str, Any]]:
        """Load accessibility-specific emoji considerations"""
        return {
            AccessibilityProfile.ADHD: {
                "avoid_categories": ["time_pressure", "complex_visual"],
                "problematic_emojis": ["⏰", "⏳", "📊", "📈"],
                "reasoning": "Time pressure and complex visuals can increase anxiety",
            },
            AccessibilityProfile.AUTISM_SPECTRUM: {
                "avoid_categories": ["sensory_overwhelming", "ambiguous_meaning"],
                "problematic_emojis": ["🎆", "🎇", "💥", "🌪️"],
                "preferred_categories": ["clear_meaning", "simple_shapes"],
                "reasoning": "Prefer clear, unambiguous symbols without sensory overload",
            },
            AccessibilityProfile.DYSLEXIA: {
                "avoid_categories": ["text_heavy", "similar_looking"],
                "problematic_emojis": ["📃", "📄", "📝", "📋"],
                "preferred_categories": ["distinct_shapes", "high_contrast"],
                "reasoning": "Avoid text-heavy or similar-looking symbols",
            },
            AccessibilityProfile.VISUAL_IMPAIRMENT: {
                "require_alt_text": True,
                "prefer_high_contrast": True,
                "avoid_categories": ["subtle_differences", "color_dependent"],
                "reasoning": "Need clear descriptions and high contrast",
            },
            AccessibilityProfile.COGNITIVE_ACCESSIBILITY: {
                "prefer_simple": True,
                "avoid_categories": ["abstract", "metaphorical"],
                "preferred_categories": ["literal", "concrete"],
                "reasoning": "Prefer literal, concrete symbols over abstract concepts",
            },
        }

    def create_cultural_profile(
        self,
        user_id: str,
        primary_culture: CulturalContext,
        accessibility_profile: AccessibilityProfile = AccessibilityProfile.NEUROTYPICAL,
        **kwargs,
    ) -> CulturalProfile:
        """
        Create a new cultural profile for a user.

        Args:
            user_id: Unique user identifier
            primary_culture: Primary cultural context
            accessibility_profile: Accessibility profile
            **kwargs: Additional profile parameters

        Returns:
            Created CulturalProfile object
        """
        profile = CulturalProfile(
            primary_culture=primary_culture,
            secondary_cultures=kwargs.get("secondary_cultures", []),
            accessibility_profile=accessibility_profile,
            language_preference=kwargs.get("language_preference", "en"),
            age_group=kwargs.get("age_group"),
            sensitivity_level=kwargs.get("sensitivity_level", 0.7),
            custom_exclusions=kwargs.get("custom_exclusions", []),
            custom_inclusions=kwargs.get("custom_inclusions", []),
            created_at=datetime.now(timezone.utc),
            last_updated=datetime.now(timezone.utc),
        )

        self.cultural_profiles[user_id] = profile
        cultural_logger.info(f"Created cultural profile for user {user_id}: {primary_culture.value}")

        return profile

    def filter_emojis_for_user(
        self, user_id: str, emoji_list: list[str], context: Optional[str] = None
    ) -> tuple[list[str], dict[str, list[str]]]:
        """
        Filter emoji list based on user's cultural profile.

        Args:
            user_id: User identifier
            emoji_list: List of emojis to filter
            context: Optional context for filtering

        Returns:
            Tuple of (filtered_emojis, exclusion_report)
        """
        profile = self.cultural_profiles.get(user_id)
        if not profile:
            # Use constitutional filtering only
            return (
                self.constitutional_gatekeeper.enforce_cultural_safety(emoji_list),
                {},
            )

        filtered_emojis = []
        exclusion_report = {
            "cultural_exclusions": [],
            "accessibility_exclusions": [],
            "constitutional_exclusions": [],
            "custom_exclusions": [],
        }

        for emoji in emoji_list:
            should_exclude, reasons = self._should_exclude_emoji(emoji, profile, context)

            if should_exclude:
                for reason_type, reason_details in reasons.items():
                    if reason_details:
                        exclusion_report[reason_type].append(f"{emoji}: {reason_details}")
            else:
                filtered_emojis.append(emoji)

        # Apply constitutional filtering as final check
        constitutional_filtered = self.constitutional_gatekeeper.enforce_cultural_safety(
            filtered_emojis, profile.primary_culture.value
        )

        # Log any additional constitutional exclusions
        constitutional_exclusions = set(filtered_emojis) - set(constitutional_filtered)
        for emoji in constitutional_exclusions:
            exclusion_report["constitutional_exclusions"].append(f"{emoji}: Constitutional safety enforcement")

        cultural_logger.info(f"Filtered {len(emoji_list)} emojis to {len(constitutional_filtered)} for user {user_id}")

        return constitutional_filtered, exclusion_report

    def _should_exclude_emoji(
        self, emoji: str, profile: CulturalProfile, context: Optional[str]
    ) -> tuple[bool, dict[str, str]]:
        """
        Determine if an emoji should be excluded for a specific profile.

        Returns:
            Tuple of (should_exclude, reasons_dict)
        """
        reasons = {
            "cultural_exclusions": "",
            "accessibility_exclusions": "",
            "constitutional_exclusions": "",
            "custom_exclusions": "",
        }

        # Check custom exclusions first
        if emoji in profile.custom_exclusions:
            reasons["custom_exclusions"] = "User-specified exclusion"
            return True, reasons

        # Check custom inclusions (override other filters)
        if emoji in profile.custom_inclusions:
            return False, reasons

        # Check cultural mappings
        emoji_data = self.emoji_cultural_map.get(emoji, {})

        if emoji_data:
            # Check cultural restrictions
            restricted_cultures = emoji_data.get("restricted_cultures", [])
            if profile.primary_culture in restricted_cultures:
                reasons["cultural_exclusions"] = f"Restricted in {profile.primary_culture.value} culture"
                return True, reasons

            # Check sensitivity level against user's sensitivity threshold
            emoji_sensitivity = emoji_data.get("sensitivity_level", 0.0)
            if emoji_sensitivity > profile.sensitivity_level:
                reasons["cultural_exclusions"] = (
                    f"Sensitivity level {emoji_sensitivity} exceeds user threshold {profile.sensitivity_level}"
                )
                return True, reasons

            # Check age restrictions
            if profile.age_group and profile.age_group in emoji_data.get("age_restricted", []):
                reasons["cultural_exclusions"] = f"Age-restricted for {profile.age_group}"
                return True, reasons

        # Check accessibility considerations
        accessibility_data = self.accessibility_map.get(profile.accessibility_profile, {})
        problematic_emojis = accessibility_data.get("problematic_emojis", [])

        if emoji in problematic_emojis:
            reasoning = accessibility_data.get("reasoning", "Accessibility concern")
            reasons["accessibility_exclusions"] = f"{profile.accessibility_profile.value}: {reasoning}"
            return True, reasons

        return False, reasons

    def suggest_alternative_emojis(
        self, excluded_emoji: str, user_id: str, category_hint: Optional[str] = None
    ) -> list[str]:
        """
        Suggest alternative emojis for an excluded emoji.

        Args:
            excluded_emoji: The emoji that was excluded
            user_id: User identifier
            category_hint: Optional category hint for alternatives

        Returns:
            List of alternative emoji suggestions
        """
        profile = self.cultural_profiles.get(user_id)
        if not profile:
            return []

        emoji_data = self.emoji_cultural_map.get(excluded_emoji, {})
        if not emoji_data:
            return []

        # Get emoji categories to find similar alternatives
        categories = emoji_data.get("categories", [])

        # Find alternatives in the same categories
        alternatives = []
        for emoji, data in self.emoji_cultural_map.items():
            if emoji == excluded_emoji:
                continue

            # Check if emoji shares categories
            emoji_categories = data.get("categories", [])
            if any(cat in categories for cat in emoji_categories):
                # Check if this alternative would be allowed
                should_exclude, _ = self._should_exclude_emoji(emoji, profile, None)
                if not should_exclude:
                    alternatives.append(emoji)

        # Limit to top 5 alternatives
        return alternatives[:5]

    def get_cultural_insights(self, emoji: str) -> dict[str, Any]:
        """
        Get cultural insights for a specific emoji.

        Args:
            emoji: Emoji to analyze

        Returns:
            Dictionary containing cultural insights
        """
        emoji_data = self.emoji_cultural_map.get(emoji, {})

        return {
            "emoji": emoji,
            "categories": emoji_data.get("categories", []),
            "sensitivity_level": emoji_data.get("sensitivity_level", 0.0),
            "cultural_interpretations": emoji_data.get("cultural_interpretations", {}),
            "platform_variations": emoji_data.get("platform_variations", {}),
            "safe_contexts": emoji_data.get("safe_contexts", []),
            "restricted_cultures": emoji_data.get("restricted_cultures", []),
            "accessibility_considerations": self._get_accessibility_considerations(emoji),
        }

    def _get_accessibility_considerations(self, emoji: str) -> list[str]:
        """Get accessibility considerations for an emoji"""
        considerations = []

        for profile, data in self.accessibility_map.items():
            if emoji in data.get("problematic_emojis", []):
                considerations.append(f"{profile.value}: {data.get('reasoning', 'Accessibility concern')}")

        return considerations

    def update_profile(self, user_id: str, updates: dict[str, Any]) -> bool:
        """
        Update an existing cultural profile.

        Args:
            user_id: User identifier
            updates: Dictionary of updates to apply

        Returns:
            True if update successful
        """
        if user_id not in self.cultural_profiles:
            return False

        profile = self.cultural_profiles[user_id]

        # Apply updates
        for key, value in updates.items():
            if hasattr(profile, key):
                setattr(profile, key, value)

        profile.last_updated = datetime.now(timezone.utc)

        cultural_logger.info(f"Updated cultural profile for user {user_id}")
        return True

    def get_profile_summary(self, user_id: str) -> Optional[dict[str, Any]]:
        """
        Get summary of user's cultural profile.

        Args:
            user_id: User identifier

        Returns:
            Profile summary or None if not found
        """
        profile = self.cultural_profiles.get(user_id)
        if not profile:
            return None

        return asdict(profile)


# Export the main classes and enums
__all__ = [
    "AccessibilityProfile",
    "CulturalContext",
    "CulturalProfile",
    "CulturalProfileManager",
]
