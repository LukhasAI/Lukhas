"""
LUKHAS Cultural Safety Checker - Emoji Cultural Exclusion Validator

This module implements cultural safety validation for emoji selection in
LUKHAS authentication to ensure cultural sensitivity and inclusivity.

Author: LUKHAS Team
Date: June 2025
Purpose: Validate emoji selections for cultural appropriateness and sensitivity
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from candidate.core.common import get_logger

logger = get_logger(__name__, timezone)


class CulturalContext(Enum):
    """Cultural contexts for emoji validation"""

    GLOBAL = "global"  # Universal/global context
    REGIONAL = "regional"  # Specific geographic region
    RELIGIOUS = "religious"  # Religious context
    CORPORATE = "corporate"  # Business/corporate environment
    EDUCATIONAL = "educational"  # Educational settings
    HEALTHCARE = "healthcare"  # Healthcare environments


class SensitivityLevel(Enum):
    """Levels of cultural sensitivity"""

    VERY_LOW = "very_low"  # Minimal filtering
    LOW = "low"  # Basic cultural awareness
    MODERATE = "moderate"  # Standard cultural sensitivity
    HIGH = "high"  # High cultural sensitivity
    MAXIMUM = "maximum"  # Maximum cultural protection


class ValidationResult(Enum):
    """Emoji validation results"""

    APPROVED = "approved"  # Safe to use
    WARNING = "warning"  # Use with caution
    REJECTED = "rejected"  # Should not be used
    CONTEXT_DEPENDENT = "context_dependent"  # Depends on context


@dataclass
class CulturalRule:
    """Cultural validation rule"""

    emoji: str
    result: ValidationResult
    contexts: list[CulturalContext]
    regions: list[str]
    reason: str
    severity: SensitivityLevel
    alternatives: list[str]


@dataclass
class ValidationReport:
    """Cultural validation report for emoji set"""

    approved_emojis: list[str]
    rejected_emojis: list[str]
    warnings: list[dict[str, Any]]
    alternatives_suggested: dict[str, list[str]]
    total_checked: int
    safety_score: float  # 0.0-1.0 cultural safety score
    recommendations: list[str]
    timestamp: datetime


class CulturalSafetyChecker:
    """
    Cultural safety validation system for LUKHAS emoji authentication.

    Features:
    - Comprehensive cultural sensitivity database
    - Regional customization support
    - Context-aware validation
    - Alternative emoji suggestions
    - Multi-level sensitivity filtering
    - Real-time validation
    - Learning from feedback
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or self._get_default_config()

        # Cultural sensitivity database
        self.cultural_rules = self._initialize_cultural_rules()
        self.regional_preferences = self._initialize_regional_preferences()
        self.context_rules = self._initialize_context_rules()

        # Active configuration
        self.active_contexts = [CulturalContext.GLOBAL]
        self.target_regions = ["global"]
        self.sensitivity_level = SensitivityLevel.MODERATE

        # Safe emoji sets by category
        self.safe_emoji_sets = self._initialize_safe_emoji_sets()

        # Validation statistics
        self.validation_stats = {
            "total_validations": 0,
            "rejections": 0,
            "warnings": 0,
            "approvals": 0,
        }

    def _get_default_config(self) -> dict[str, Any]:
        """Get default configuration for cultural safety checker."""
        return {
            "sensitivity_level": SensitivityLevel.MODERATE,
            "default_contexts": [CulturalContext.GLOBAL],
            "regional_adaptation": True,
            "learning_enabled": True,
            "alternative_suggestions": True,
            "context_awareness": True,
            "real_time_updates": False,
            "strict_mode": False,
        }

    def _initialize_cultural_rules(self) -> dict[str, CulturalRule]:
        """Initialize comprehensive cultural sensitivity rules."""
        rules = {}

        # Religious symbols and references
        religious_concerns = ["🕎", "☪️", "✝️", "☦️", "☯️", "🕉️", "☸️", "✡️", "🔯"]
        for emoji in religious_concerns:
            rules[emoji] = CulturalRule(
                emoji=emoji,
                result=ValidationResult.CONTEXT_DEPENDENT,
                contexts=[CulturalContext.RELIGIOUS],
                regions=["global"],
                reason="Religious symbol may be sensitive in secular contexts",
                severity=SensitivityLevel.HIGH,
                alternatives=["⭐", "✨", "🌟", "💫"],
            )

        # Potentially offensive gestures
        gesture_concerns = [
            "🖕",  # Middle finger
            "🤏",  # Pinching hand (can be offensive in some cultures)
        ]
        for emoji in gesture_concerns:
            rules[emoji] = CulturalRule(
                emoji=emoji,
                result=ValidationResult.REJECTED,
                contexts=[CulturalContext.GLOBAL],
                regions=["global"],
                reason="Potentially offensive gesture",
                severity=SensitivityLevel.MAXIMUM,
                alternatives=["👍", "👋", "🤝", "👏"],
            )

        # Cultural food items that might be sensitive
        food_sensitivities = {
            "🥓": ["muslim", "jewish"],  # Pork products
            "🍷": ["muslim"],  # Alcohol
            "🍺": ["muslim"],  # Alcohol
            "🥩": ["hindu", "buddhist"],  # Beef products
        }
        for emoji, sensitive_cultures in food_sensitivities.items():
            rules[emoji] = CulturalRule(
                emoji=emoji,
                result=ValidationResult.WARNING,
                contexts=[CulturalContext.RELIGIOUS, CulturalContext.GLOBAL],
                regions=sensitive_cultures,
                reason=f"May be culturally sensitive for {', '.join(sensitive_cultures)}",
                severity=SensitivityLevel.MODERATE,
                alternatives=["🍎", "🥕", "🥬", "🍇"],
            )

        # National symbols and flags (context-dependent)
        flag_emojis = [
            "🇺🇸",
            "🇨🇳",
            "🇷🇺",
            "🇬🇧",
            "🇫🇷",
            "🇩🇪",
            "🇯🇵",
            "🇮🇳",
            "🇧🇷",
            "🇨🇦",
            "🇦🇺",
            "🇲🇽",
            "🇰🇷",
            "🇮🇹",
        ]
        for emoji in flag_emojis:
            rules[emoji] = CulturalRule(
                emoji=emoji,
                result=ValidationResult.CONTEXT_DEPENDENT,
                contexts=[CulturalContext.GLOBAL, CulturalContext.CORPORATE],
                regions=["global"],
                reason="National flag may show bias or create political associations",
                severity=SensitivityLevel.MODERATE,
                alternatives=["🌍", "🌎", "🌏", "🌐"],
            )

        # Skin tone modifiers (handle with care)
        skin_tone_emojis = [
            "👋🏻",
            "👋🏼",
            "👋🏽",
            "👋🏾",
            "👋🏿",
            "👍🏻",
            "👍🏼",
            "👍🏽",
            "👍🏾",
            "👍🏿",
        ]
        for emoji in skin_tone_emojis:
            rules[emoji] = CulturalRule(
                emoji=emoji,
                result=ValidationResult.WARNING,
                contexts=[CulturalContext.GLOBAL],
                regions=["global"],
                reason="Skin tone modifiers require careful consideration for inclusivity",
                severity=SensitivityLevel.MODERATE,
                alternatives=["👋", "👍", "🤝", "✨"],
            )

        return rules

    def _initialize_regional_preferences(self) -> dict[str, dict[str, Any]]:
        """Initialize regional emoji preferences and restrictions."""
        return {
            "middle_east": {
                "avoid": ["🍷", "🍺", "🥓", "🐷"],
                "prefer": ["🌙", "⭐", "🕌", "🌹"],
                "sensitivity": SensitivityLevel.HIGH,
            },
            "east_asia": {
                "avoid": ["🎌"],  # Rising sun flag can be sensitive
                "prefer": ["🌸", "🐼", "🍜", "🏮"],
                "sensitivity": SensitivityLevel.MODERATE,
            },
            "south_asia": {
                "avoid": ["🥩", "🍖"],  # Beef products
                "prefer": ["🕉️", "🪔", "🐘", "🌺"],
                "sensitivity": SensitivityLevel.MODERATE,
            },
            "western": {
                "avoid": [],
                "prefer": ["😊", "❤️", "👍", "🎉"],
                "sensitivity": SensitivityLevel.LOW,
            },
            "africa": {
                "avoid": [],
                "prefer": ["🦁", "🐘", "🌍", "🌅"],
                "sensitivity": SensitivityLevel.MODERATE,
            },
        }

    def _initialize_context_rules(self) -> dict[CulturalContext, dict[str, Any]]:
        """Initialize context-specific validation rules."""
        return {
            CulturalContext.CORPORATE: {
                "avoid": ["🍷", "🍺", "💋", "🔞", "💊"],
                "prefer": ["💼", "📊", "✅", "🎯", "🚀"],
                "professional_only": True,
            },
            CulturalContext.EDUCATIONAL: {
                "avoid": ["🍷", "🍺", "💋", "🔞"],
                "prefer": ["📚", "🎓", "✏️", "🧮", "🔬"],
                "age_appropriate": True,
            },
            CulturalContext.HEALTHCARE: {
                "avoid": ["💊", "🏥", "⚰️", "☠️"],
                "prefer": ["❤️", "😊", "🌟", "✨", "🤝"],
                "sensitive_context": True,
            },
            CulturalContext.RELIGIOUS: {
                "avoid": ["🍷", "🍺", "💋", "🔞"],
                "prefer": ["🙏", "⭐", "❤️", "🕊️", "🌟"],
                "respectful_only": True,
            },
        }

    def _initialize_safe_emoji_sets(self) -> dict[str, list[str]]:
        """Initialize categorized safe emoji sets."""
        return {
            "universally_safe": [
                "😊",
                "😄",
                "😃",
                "🙂",
                "😌",
                "😍",
                "🥰",
                "😘",
                "👍",
                "👏",
                "🤝",
                "👋",
                "🙌",
                "✨",
                "⭐",
                "🌟",
                "❤️",
                "💙",
                "💚",
                "💛",
                "💜",
                "🧡",
                "💗",
                "💕",
                "🎉",
                "🎊",
                "🎈",
                "🎁",
                "🎀",
                "🎂",
                "🍰",
                "🎯",
                "🌈",
                "🌞",
                "⛅",
                "🌙",
                "💫",
                "🔆",
                "☀️",
                "🌺",
                "🌸",
                "🌼",
                "🌻",
                "🌷",
                "🌹",
                "🍀",
                "🌿",
                "🌱",
            ],
            "nature_safe": [
                "🌍",
                "🌎",
                "🌏",
                "🌳",
                "🌲",
                "🌴",
                "🌵",
                "🌾",
                "🍃",
                "🌿",
                "🌱",
                "🌿",
                "🦋",
                "🐝",
                "🐞",
                "🌺",
                "🌸",
                "🌼",
                "🌻",
                "🌷",
                "🌹",
                "🌙",
                "⭐",
                "✨",
            ],
            "technology_safe": [
                "💻",
                "📱",
                "⌚",
                "🖥️",
                "⌨️",
                "🖱️",
                "🔍",
                "📊",
                "📈",
                "📉",
                "💡",
                "🔧",
                "⚙️",
                "🔩",
                "🔗",
                "💾",
                "💿",
                "📀",
                "🎮",
                "🕹️",
                "📷",
                "📹",
                "🎬",
                "📺",
            ],
            "food_safe": [
                "🍎",
                "🍊",
                "🍋",
                "🍌",
                "🍇",
                "🍓",
                "🫐",
                "🍈",
                "🍒",
                "🍑",
                "🥭",
                "🍍",
                "🥝",
                "🍅",
                "🥕",
                "🌽",
                "🥒",
                "🥬",
                "🥦",
                "🥔",
                "🍠",
                "🥜",
                "🌰",
                "🍞",
            ],
            "symbols_safe": [
                "✅",
                "❌",
                "⭐",
                "✨",
                "💫",
                "🔆",
                "💎",
                "🔑",
                "🏆",
                "🎯",
                "🎪",
                "🎭",
                "🎨",
                "🎵",
                "🎶",
                "🎼",
                "🔔",
                "🔕",
                "📢",
                "📣",
                "💌",
                "💝",
                "🎀",
                "🎁",
            ],
        }

    def validate_emoji_set(
        self,
        emojis: list[str],
        contexts: Optional[list[CulturalContext]] = None,
        regions: Optional[list[str]] = None,
        sensitivity_level: Optional[SensitivityLevel] = None,
    ) -> ValidationReport:
        """
        Validate a set of emojis for cultural safety.

        Args:
            emojis: List of emojis to validate
            contexts: Cultural contexts to consider
            regions: Target regions/cultures
            sensitivity_level: Level of cultural sensitivity

        Returns:
            Comprehensive validation report
        """
        contexts = contexts or self.active_contexts
        regions = regions or self.target_regions
        sensitivity_level = sensitivity_level or self.sensitivity_level

        approved = []
        rejected = []
        warnings = []
        alternatives = {}
        recommendations = []

        for emoji in emojis:
            result = self._validate_single_emoji(emoji, contexts, regions, sensitivity_level)

            if result["validation_result"] == ValidationResult.APPROVED:
                approved.append(emoji)
            elif result["validation_result"] == ValidationResult.REJECTED:
                rejected.append(emoji)
                if result["alternatives"]:
                    alternatives[emoji] = result["alternatives"]
            elif result["validation_result"] == ValidationResult.WARNING:
                approved.append(emoji)  # Include but with warning
                warnings.append(
                    {
                        "emoji": emoji,
                        "reason": result["reason"],
                        "severity": result["severity"].value,
                        "alternatives": result["alternatives"],
                    }
                )
            elif result["validation_result"] == ValidationResult.CONTEXT_DEPENDENT:
                if self._should_approve_context_dependent(emoji, contexts, sensitivity_level):
                    approved.append(emoji)
                else:
                    rejected.append(emoji)
                    if result["alternatives"]:
                        alternatives[emoji] = result["alternatives"]

        # Calculate safety score
        safety_score = self._calculate_safety_score(approved, rejected, warnings)

        # Generate recommendations
        recommendations = self._generate_recommendations(approved, rejected, warnings, contexts)

        # Update statistics
        self.validation_stats["total_validations"] += len(emojis)
        self.validation_stats["approvals"] += len(approved)
        self.validation_stats["rejections"] += len(rejected)
        self.validation_stats["warnings"] += len(warnings)

        return ValidationReport(
            approved_emojis=approved,
            rejected_emojis=rejected,
            warnings=warnings,
            alternatives_suggested=alternatives,
            total_checked=len(emojis),
            safety_score=safety_score,
            recommendations=recommendations,
            timestamp=datetime.now(timezone.utc),
        )

    def _validate_single_emoji(
        self,
        emoji: str,
        contexts: list[CulturalContext],
        regions: list[str],
        sensitivity_level: SensitivityLevel,
    ) -> dict[str, Any]:
        """Validate a single emoji against cultural rules."""
        # Check if emoji has specific cultural rules
        if emoji in self.cultural_rules:
            rule = self.cultural_rules[emoji]

            # Check if any target context matches rule contexts
            context_match = any(ctx in rule.contexts for ctx in contexts)

            # Check if any target region matches rule regions
            region_match = any(region in rule.regions for region in regions) or "global" in rule.regions

            # Check sensitivity level
            severity_match = rule.severity.value <= sensitivity_level.value

            if context_match and region_match and severity_match:
                return {
                    "validation_result": rule.result,
                    "reason": rule.reason,
                    "severity": rule.severity,
                    "alternatives": rule.alternatives,
                }

        # Check context-specific rules
        for context in contexts:
            if context in self.context_rules:
                context_rule = self.context_rules[context]
                if emoji in context_rule.get("avoid", []):
                    return {
                        "validation_result": ValidationResult.REJECTED,
                        "reason": f"Not appropriate for {context.value} context",
                        "severity": SensitivityLevel.HIGH,
                        "alternatives": context_rule.get("prefer", [])[:3],
                    }

        # Check regional preferences
        for region in regions:
            if region in self.regional_preferences:
                pref = self.regional_preferences[region]
                if emoji in pref.get("avoid", []):
                    return {
                        "validation_result": ValidationResult.WARNING,
                        "reason": f"May be culturally sensitive in {region}",
                        "severity": pref.get("sensitivity", SensitivityLevel.MODERATE),
                        "alternatives": pref.get("prefer", [])[:3],
                    }

        # Check if emoji is in universally safe set
        if emoji in self.safe_emoji_sets["universally_safe"]:
            return {
                "validation_result": ValidationResult.APPROVED,
                "reason": "Universally safe emoji",
                "severity": SensitivityLevel.VERY_LOW,
                "alternatives": [],
            }

        # Default: approve with low confidence
        return {
            "validation_result": ValidationResult.APPROVED,
            "reason": "No specific cultural concerns identified",
            "severity": SensitivityLevel.LOW,
            "alternatives": [],
        }

    def _should_approve_context_dependent(
        self,
        emoji: str,
        contexts: list[CulturalContext],
        sensitivity_level: SensitivityLevel,
    ) -> bool:
        """Determine if context-dependent emoji should be approved."""
        # More permissive for lower sensitivity levels
        if sensitivity_level in [SensitivityLevel.VERY_LOW, SensitivityLevel.LOW]:
            return True

        # More restrictive for higher sensitivity levels
        if sensitivity_level in [SensitivityLevel.HIGH, SensitivityLevel.MAXIMUM]:
            return False

        # Moderate sensitivity: depends on context
        safe_contexts = [CulturalContext.GLOBAL]
        return any(ctx in safe_contexts for ctx in contexts)

    def _calculate_safety_score(
        self, approved: list[str], rejected: list[str], warnings: list[dict[str, Any]]
    ) -> float:
        """Calculate overall cultural safety score."""
        total = len(approved) + len(rejected)
        if total == 0:
            return 1.0

        # Base score from approval rate
        approval_rate = len(approved) / total

        # Penalty for warnings (less severe than rejections)
        warning_penalty = len(warnings) * 0.1

        # Penalty for rejections
        rejection_penalty = len(rejected) * 0.5

        # Calculate final score
        safety_score = approval_rate - (warning_penalty + rejection_penalty) / total

        return max(0.0, min(1.0, safety_score))

    def _generate_recommendations(
        self,
        approved: list[str],
        rejected: list[str],
        warnings: list[dict[str, Any]],
        contexts: list[CulturalContext],
    ) -> list[str]:
        """Generate recommendations for improving cultural safety."""
        recommendations = []

        if len(rejected) > len(approved) * 0.3:  # More than 30% rejected
            recommendations.append("Consider using more universally safe emojis")

        if len(warnings) > 0:
            recommendations.append("Review warned emojis for context appropriateness")

        if CulturalContext.CORPORATE in contexts and any("🍷" in emoji for emoji in approved):
            recommendations.append("Avoid alcohol-related emojis in corporate contexts")

        if CulturalContext.EDUCATIONAL in contexts:
            recommendations.append("Ensure all emojis are age-appropriate")

        if len(approved) < 10:
            recommendations.append("Consider expanding emoji set with universally safe options")

        return recommendations

    def get_safe_emoji_suggestions(
        self,
        category: str = "universally_safe",
        count: int = 10,
        contexts: Optional[list[CulturalContext]] = None,
    ) -> list[str]:
        """
        Get suggestions for culturally safe emojis.

        Args:
            category: Category of safe emojis
            count: Number of suggestions to return
            contexts: Contexts to optimize for

        Returns:
            List of safe emoji suggestions
        """
        if category in self.safe_emoji_sets:
            safe_set = self.safe_emoji_sets[category]
        else:
            safe_set = self.safe_emoji_sets["universally_safe"]

        # Filter based on contexts if provided
        if contexts:
            filtered_set = []
            for emoji in safe_set:
                validation = self._validate_single_emoji(emoji, contexts, ["global"], self.sensitivity_level)
                if validation["validation_result"] == ValidationResult.APPROVED:
                    filtered_set.append(emoji)
            safe_set = filtered_set

        # Return requested number of suggestions
        return safe_set[:count]

    def add_custom_rule(self, rule: CulturalRule):
        """Add custom cultural validation rule."""
        self.cultural_rules[rule.emoji] = rule
        logger.info(f"Added custom cultural rule for emoji {rule.emoji}")

    def update_regional_preferences(self, region: str, preferences: dict[str, Any]):
        """Update regional preferences for emoji usage."""
        self.regional_preferences[region] = preferences
        logger.info(f"Updated regional preferences for {region}")

    def set_active_configuration(
        self,
        contexts: list[CulturalContext],
        regions: list[str],
        sensitivity_level: SensitivityLevel,
    ):
        """Set active configuration for validation."""
        self.active_contexts = contexts
        self.target_regions = regions
        self.sensitivity_level = sensitivity_level
        logger.info(
            f"Updated configuration: contexts={contexts}, regions={regions}, sensitivity={sensitivity_level.value}"
        )

    def get_cultural_status(self) -> dict[str, Any]:
        """Get comprehensive cultural safety checker status."""
        return {
            "active_configuration": {
                "contexts": [ctx.value for ctx in self.active_contexts],
                "regions": self.target_regions,
                "sensitivity_level": self.sensitivity_level.value,
            },
            "cultural_rules_count": len(self.cultural_rules),
            "regional_preferences_count": len(self.regional_preferences),
            "safe_emoji_sets": {category: len(emojis) for category, emojis in self.safe_emoji_sets.items()},
            "validation_statistics": self.validation_stats.copy(),
            "config": self.config.copy(),
        }


# Export the main classes
__all__ = [
    "CulturalContext",
    "CulturalRule",
    "CulturalSafetyChecker",
    "SensitivityLevel",
    "ValidationReport",
    "ValidationResult",
]
