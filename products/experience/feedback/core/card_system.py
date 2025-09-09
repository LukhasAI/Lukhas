"""
Feedback Card System for LUKHAS
================================
Human-in-the-loop learning system with symbolic feedback and bounded adaptation.
"""
import hashlib
import json
import logging
import time
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class FeedbackRating(int, Enum):
    """User feedback ratings"""

    VERY_POOR = 1
    POOR = 2
    NEUTRAL = 3
    GOOD = 4
    EXCELLENT = 5


@dataclass
class FeedbackCard:
    """
    Individual feedback card capturing user response to system action.
    """

    card_id: str
    action_id: str  # ID of the action being rated
    rating: FeedbackRating
    timestamp: float = field(default_factory=time.time)

    # User-provided feedback
    note: Optional[str] = None
    symbols: list[str] = field(default_factory=list)  # User-selected symbols
    tags: list[str] = field(default_factory=list)  # System-generated tags

    # Context for learning
    prompt: Optional[str] = None
    response: Optional[str] = None
    signal_state: dict[str, float] = field(default_factory=dict)
    modulation_params: dict[str, Any] = field(default_factory=dict)

    # Privacy
    user_id_hash: Optional[str] = None  # Hashed user ID for privacy
    session_id: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FeedbackCard":
        """Create from dictionary"""
        # Convert rating to enum
        if "rating" in data and not isinstance(data["rating"], FeedbackRating):
            data["rating"] = FeedbackRating(data["rating"])
        return cls(**data)


@dataclass
class PatternSet:
    """Collection of patterns extracted from feedback"""

    pattern_id: str
    pattern_type: str  # "preference", "correction", "reinforcement"
    frequency: int
    confidence: float  # 0.0 to 1.0

    # Pattern details
    conditions: dict[str, Any] = field(default_factory=dict)
    preferred_params: dict[str, Any] = field(default_factory=dict)
    avoided_params: dict[str, Any] = field(default_factory=dict)

    # Symbol associations
    positive_symbols: list[str] = field(default_factory=list)
    negative_symbols: list[str] = field(default_factory=list)

    def matches(self, context: dict[str, Any]) -> bool:
        """Check if pattern matches current context"""
        return all(not (key not in context or context[key] != value) for key, value in self.conditions.items())


@dataclass
class PolicyUpdate:
    """Proposed update to system policy based on feedback"""

    update_id: str
    timestamp: float
    pattern_ids: list[str]  # Patterns that triggered this update

    # Proposed changes
    parameter_adjustments: dict[str, float] = field(default_factory=dict)
    weight_adjustments: dict[str, float] = field(default_factory=dict)
    threshold_adjustments: dict[str, float] = field(default_factory=dict)

    # Safety bounds
    max_change: float = 0.2  # Maximum parameter change per update
    requires_validation: bool = True
    validated: bool = False

    def apply_bounds(self):
        """Apply safety bounds to all adjustments"""
        for param_dict in [
            self.parameter_adjustments,
            self.weight_adjustments,
            self.threshold_adjustments,
        ]:
            for key, value in param_dict.items():
                # Clamp changes to max_change
                param_dict[key] = max(-self.max_change, min(self.max_change, value))


@dataclass
class LearningReport:
    """Report on what the system has learned from a user"""

    user_id_hash: str
    report_date: float
    total_feedback_cards: int

    # Learning summary
    overall_satisfaction: float  # Average rating
    improvement_trend: float  # Positive if improving over time

    # Discovered preferences
    preferred_styles: list[str] = field(default_factory=list)
    preferred_temperature_range: tuple[float, float] = (0.5, 0.8)
    preferred_response_length: str = "medium"

    # Symbol dictionary
    personal_symbols: dict[str, str] = field(default_factory=dict)

    # Patterns
    identified_patterns: list[PatternSet] = field(default_factory=list)

    # Recommendations
    recommended_adjustments: dict[str, Any] = field(default_factory=dict)


class FeedbackCardSystem:
    """
    Main feedback card system for human-in-the-loop learning.
    """

    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize feedback system.

        Args:
            storage_path: Directory to store feedback data
        """
        self.storage_path = Path(storage_path or "feedback_data")
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # In-memory caches
        self.feedback_cards: list[FeedbackCard] = []
        self.patterns: dict[str, PatternSet] = {}
        self.policy_updates: list[PolicyUpdate] = []

        # User-specific data (privacy-preserving)
        self.user_preferences: dict[str, dict[str, Any]] = defaultdict(dict)
        self.user_symbols: dict[str, dict[str, str]] = defaultdict(dict)

        # Load existing data
        self._load_feedback_data()

        # Metrics
        self.metrics = {
            "cards_captured": 0,
            "patterns_identified": 0,
            "policies_updated": 0,
            "validations_passed": 0,
            "validations_failed": 0,
        }

    def _load_feedback_data(self):
        """Load existing feedback data from storage"""
        cards_file = self.storage_path / "feedback_cards.jsonl"
        if cards_file.exists():
            with open(cards_file) as f:
                for line in f:
                    try:
                        card_data = json.loads(line)
                        card = FeedbackCard.from_dict(card_data)
                        self.feedback_cards.append(card)
                    except Exception as e:
                        logger.error(f"Error loading feedback card: {e}")

        patterns_file = self.storage_path / "patterns.json"
        if patterns_file.exists():
            with open(patterns_file) as f:
                patterns_data = json.load(f)
                for pattern_id, pattern_dict in patterns_data.items():
                    self.patterns[pattern_id] = PatternSet(**pattern_dict)

    def _save_feedback_card(self, card: FeedbackCard):
        """Save feedback card to storage"""
        cards_file = self.storage_path / "feedback_cards.jsonl"
        with open(cards_file, "a") as f:
            f.write(json.dumps(card.to_dict()) + "\n")

    def _save_patterns(self):
        """Save patterns to storage"""
        patterns_file = self.storage_path / "patterns.json"
        patterns_data = {pid: asdict(pattern) for pid, pattern in self.patterns.items()}
        with open(patterns_file, "w") as f:
            json.dump(patterns_data, f, indent=2)

    def capture_feedback(
        self,
        action_id: str,
        rating: int,
        note: Optional[str] = None,
        symbols: Optional[list[str]] = None,
        context: Optional[dict[str, Any]] = None,
        user_id: Optional[str] = None,
    ) -> FeedbackCard:
        """
        Capture user feedback for an action.

        Args:
            action_id: ID of the action being rated
            rating: Rating from 1-5
            note: Optional text note
            symbols: Optional list of symbols
            context: Optional context (prompt, response, etc.)
            user_id: Optional user ID (will be hashed)

        Returns:
            Created feedback card
        """
        # Hash user ID for privacy
        user_id_hash = None
        if user_id:
            user_id_hash = hashlib.sha256(user_id.encode()).hexdigest()[:16]

        # Create feedback card
        card = FeedbackCard(
            card_id=f"card_{int(time.time()) * 1000}",
            action_id=action_id,
            rating=FeedbackRating(rating),
            note=note,
            symbols=symbols or [],
            user_id_hash=user_id_hash,
        )

        # Add context if provided
        if context:
            card.prompt = context.get("prompt")
            card.response = context.get("response")
            card.signal_state = context.get("signal_state", {})
            card.modulation_params = context.get("modulation_params", {})

        # Store card
        self.feedback_cards.append(card)
        self._save_feedback_card(card)
        self.metrics["cards_captured"] += 1

        # Update user preferences
        if user_id_hash:
            self._update_user_preferences(user_id_hash, card)

        # Check for patterns periodically
        if len(self.feedback_cards) % 10 == 0:
            self.extract_patterns(self.feedback_cards[-50:])

        logger.info(f"Captured feedback card: {card.card_id} (rating={rating})")
        return card

    def _update_user_preferences(self, user_id_hash: str, card: FeedbackCard):
        """Update user-specific preferences based on feedback"""
        prefs = self.user_preferences[user_id_hash]

        # Track rating history
        if "ratings" not in prefs:
            prefs["ratings"] = []
        prefs["ratings"].append(card.rating.value)

        # Track symbol usage
        for symbol in card.symbols:
            if symbol not in self.user_symbols[user_id_hash]:
                self.user_symbols[user_id_hash][symbol] = card.note or ""

        # Track preferred parameters for high ratings
        if card.rating >= FeedbackRating.GOOD:
            if "preferred_params" not in prefs:
                prefs["preferred_params"] = defaultdict(list)

            for param, value in card.modulation_params.items():
                prefs["preferred_params"][param].append(value)

    def extract_patterns(self, cards: list[FeedbackCard]) -> list[PatternSet]:
        """
        Extract patterns from feedback cards.

        Args:
            cards: Feedback cards to analyze

        Returns:
            List of identified patterns
        """
        patterns = []

        # Group cards by rating
        by_rating = defaultdict(list)
        for card in cards:
            by_rating[card.rating].append(card)

        # Look for preference patterns (high ratings)
        if FeedbackRating.EXCELLENT in by_rating:
            excellent_cards = by_rating[FeedbackRating.EXCELLENT]

            # Find common parameters in excellent feedback
            param_counts = Counter()
            for card in excellent_cards:
                for param, value in card.modulation_params.items():
                    # Discretize continuous values
                    if isinstance(value, float):
                        value = round(value, 1)
                    param_counts[(param, value)] += 1

            # Create patterns for frequent parameter combinations
            for (param, value), count in param_counts.most_common(3):
                if count >= 3:  # Minimum frequency
                    pattern = PatternSet(
                        pattern_id=f"pref_{param}_{value}_{int(time.time())}",
                        pattern_type="preference",
                        frequency=count,
                        confidence=count / len(excellent_cards),
                        preferred_params={param: value},
                    )
                    patterns.append(pattern)
                    self.patterns[pattern.pattern_id] = pattern

        # Look for correction patterns (poor ratings with notes)
        if FeedbackRating.POOR in by_rating:
            poor_cards = by_rating[FeedbackRating.POOR]

            # Analyze notes for common complaints
            note_themes = defaultdict(list)
            for card in poor_cards:
                if card.note:
                    # Simple keyword extraction
                    keywords = ["short", "long", "unclear", "wrong", "slow", "fast"]
                    for keyword in keywords:
                        if keyword in card.note.lower():
                            note_themes[keyword].append(card)

            # Create correction patterns
            for theme, theme_cards in note_themes.items():
                if len(theme_cards) >= 2:
                    pattern = PatternSet(
                        pattern_id=f"correct_{theme}_{int(time.time())}",
                        pattern_type="correction",
                        frequency=len(theme_cards),
                        confidence=len(theme_cards) / len(poor_cards),
                        conditions={"theme": theme},
                    )
                    patterns.append(pattern)
                    self.patterns[pattern.pattern_id] = pattern

        # Look for symbol patterns
        symbol_ratings = defaultdict(list)
        for card in cards:
            for symbol in card.symbols:
                symbol_ratings[symbol].append(card.rating.value)

        # Identify positive/negative symbol associations
        for symbol, ratings in symbol_ratings.items():
            if len(ratings) >= 3:
                avg_rating = sum(ratings) / len(ratings)
                if avg_rating >= 4.0:
                    # Positive symbol association
                    for pattern in patterns:
                        if pattern.pattern_type == "preference":
                            pattern.positive_symbols.append(symbol)
                elif avg_rating <= 2.0:
                    # Negative symbol association
                    for pattern in patterns:
                        if pattern.pattern_type == "correction":
                            pattern.negative_symbols.append(symbol)

        self.metrics["patterns_identified"] += len(patterns)

        if patterns:
            self._save_patterns()
            logger.info(f"Extracted {len(patterns)} patterns from {len(cards)} cards")

        return patterns

    def update_policy(self, patterns: list[PatternSet]) -> Optional[PolicyUpdate]:
        """
        Generate bounded policy modifications from patterns.

        Args:
            patterns: Patterns to base updates on

        Returns:
            Policy update or None if no update needed
        """
        if not patterns:
            return None

        update = PolicyUpdate(
            update_id=f"update_{int(time.time())}",
            timestamp=time.time(),
            pattern_ids=[p.pattern_id for p in patterns],
        )

        # Aggregate preferred parameters
        param_votes = defaultdict(list)
        for pattern in patterns:
            if pattern.pattern_type == "preference":
                for param, value in pattern.preferred_params.items():
                    weight = pattern.confidence * pattern.frequency
                    param_votes[param].append((value, weight))

        # Calculate weighted average adjustments
        for param, votes in param_votes.items():
            if votes:
                weighted_sum = sum(value * weight for value, weight in votes)
                total_weight = sum(weight for _, weight in votes)
                target_value = weighted_sum / total_weight

                # Calculate adjustment (capped by max_change)
                current_value = self._get_current_param_value(param)
                adjustment = target_value - current_value
                update.parameter_adjustments[param] = adjustment

        # Handle correction patterns
        for pattern in patterns:
            if pattern.pattern_type == "correction":
                theme = pattern.conditions.get("theme")
                if theme == "short":
                    update.parameter_adjustments["max_output_tokens"] = 0.2
                elif theme == "long":
                    update.parameter_adjustments["max_output_tokens"] = -0.2
                elif theme == "unclear":
                    update.parameter_adjustments["reasoning_effort"] = 0.1

        # Apply safety bounds
        update.apply_bounds()

        # Store update
        self.policy_updates.append(update)
        self.metrics["policies_updated"] += 1

        logger.info(f"Generated policy update: {update.update_id}")
        return update

    def _get_current_param_value(self, param: str) -> float:
        """Get current value of a parameter (placeholder)"""
        # This would connect to the actual system configuration
        defaults = {
            "temperature": 0.7,
            "max_output_tokens": 1024,
            "reasoning_effort": 0.5,
            "top_p": 0.9,
        }
        return defaults.get(param, 0.5)

    def validate_update(self, update: PolicyUpdate) -> bool:
        """
        Validate that a policy update maintains safety constraints.

        Args:
            update: Policy update to validate

        Returns:
            True if update is safe to apply
        """
        # Check that all adjustments are within bounds
        for adjustment in update.parameter_adjustments.values():
            if abs(adjustment) > update.max_change:
                logger.warning(f"Update {update.update_id} exceeds max change")
                self.metrics["validations_failed"] += 1
                return False

        # Check specific parameter constraints
        for param, adjustment in update.parameter_adjustments.items():
            current = self._get_current_param_value(param)
            new_value = current + adjustment

            # Temperature must stay in [0.1, 1.0]
            if param == "temperature" and not (0.1 <= new_value <= 1.0):
                logger.warning(f"Temperature {new_value} out of bounds")
                self.metrics["validations_failed"] += 1
                return False

            # Max tokens must stay positive
            if param == "max_output_tokens" and new_value < 100:
                logger.warning(f"Max tokens {new_value} too low")
                self.metrics["validations_failed"] += 1
                return False

        update.validated = True
        self.metrics["validations_passed"] += 1
        logger.info(f"Validated update {update.update_id}")
        return True

    def explain_learning(self, user_id: str) -> LearningReport:
        """
        Generate a report explaining what the system learned from a user.

        Args:
            user_id: User ID (will be hashed)

        Returns:
            Learning report
        """
        user_id_hash = hashlib.sha256(user_id.encode()).hexdigest()[:16]

        # Get user's feedback cards
        user_cards = [card for card in self.feedback_cards if card.user_id_hash == user_id_hash]

        if not user_cards:
            return LearningReport(
                user_id_hash=user_id_hash,
                report_date=time.time(),
                total_feedback_cards=0,
                overall_satisfaction=0.0,
                improvement_trend=0.0,
            )

        # Calculate satisfaction metrics
        ratings = [card.rating.value for card in user_cards]
        overall_satisfaction = sum(ratings) / len(ratings)

        # Calculate improvement trend
        if len(ratings) > 1:
            first_half = ratings[: len(ratings) // 2]
            second_half = ratings[len(ratings) // 2 :]
            improvement_trend = (sum(second_half) / len(second_half)) - (sum(first_half) / len(first_half))
        else:
            improvement_trend = 0.0

        # Get user preferences
        prefs = self.user_preferences.get(user_id_hash, {})

        # Determine preferred style
        preferred_styles = []
        if "preferred_params" in prefs:
            avg_temp = sum(prefs["preferred_params"].get("temperature", [0.7])) / len(
                prefs["preferred_params"].get("temperature", [0.7])
            )
            if avg_temp < 0.4:
                preferred_styles.append("conservative")
            elif avg_temp > 0.7:
                preferred_styles.append("creative")
            else:
                preferred_styles.append("balanced")

        # Get user's patterns
        user_patterns = []
        for pattern in self.patterns.values():
            # Check if pattern is relevant to user
            pattern_cards = [
                card for card in user_cards if any(pid == pattern.pattern_id for pid in self.policy_updates)
            ]
            if pattern_cards:
                user_patterns.append(pattern)

        report = LearningReport(
            user_id_hash=user_id_hash,
            report_date=time.time(),
            total_feedback_cards=len(user_cards),
            overall_satisfaction=overall_satisfaction,
            improvement_trend=improvement_trend,
            preferred_styles=preferred_styles,
            personal_symbols=self.user_symbols.get(user_id_hash, {}),
            identified_patterns=user_patterns[:10],  # Top 10 patterns
        )

        # Add recommendations
        if overall_satisfaction < 3.0:
            report.recommended_adjustments["increase_reasoning"] = True
            report.recommended_adjustments["reduce_temperature"] = True

        if improvement_trend < 0:
            report.recommended_adjustments["revert_recent_changes"] = True

        logger.info(f"Generated learning report for user {user_id_hash}")
        return report

    def get_metrics(self) -> dict[str, Any]:
        """Get system metrics"""
        return {
            **self.metrics,
            "total_cards": len(self.feedback_cards),
            "total_patterns": len(self.patterns),
            "total_updates": len(self.policy_updates),
        }