"""
LUKHAS Brand Sentiment Intelligence Engine - Trinity Framework (⚛️🧠🛡️)
Advanced sentiment analysis and brand perception tracking for LUKHAS AI
"""

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional


class SentimentPolarity(Enum):
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


class BrandDimension(Enum):
    INNOVATION = "innovation"
    TRUSTWORTHINESS = "trustworthiness"
    CONSCIOUSNESS = "consciousness"
    HELPFULNESS = "helpfulness"
    ACCESSIBILITY = "accessibility"
    TECHNICAL_COMPETENCE = "technical_competence"
    ETHICAL_FOUNDATION = "ethical_foundation"


@dataclass
class SentimentResult:
    """Structured sentiment analysis result"""

    overall_sentiment: float  # -1.0 to 1.0
    polarity: SentimentPolarity
    confidence: float  # 0.0 to 1.0
    brand_dimensions: dict[BrandDimension, float]
    trinity_sentiment: dict[str, float]  # Identity, Consciousness, Guardian
    emotional_indicators: dict[str, float]
    context_appropriateness: float


class BrandSentimentEngine:
    """
    Advanced sentiment analysis engine specifically tuned for LUKHAS brand
    perception, Trinity Framework alignment, and consciousness technology sentiment
    """

    def __init__(self):
        self.sentiment_lexicon = self._build_brand_sentiment_lexicon()
        self.trinity_lexicon = self._build_trinity_sentiment_lexicon()
        self.emotion_patterns = self._compile_emotion_patterns()
        self.brand_dimension_indicators = self._build_brand_dimension_indicators()
        self.context_analyzers = self._build_context_analyzers()
        self.sentiment_history = []

    def _build_brand_sentiment_lexicon(self) -> dict[str, dict[str, float]]:
        """Build LUKHAS-specific sentiment lexicon"""
        return {
            # Positive brand indicators
            "consciousness": {
                "sentiment": 0.8,
                "brand_relevance": 0.95,
                "trinity_component": "consciousness",
            },
            "awakening": {
                "sentiment": 0.9,
                "brand_relevance": 0.9,
                "trinity_component": "consciousness",
            },
            "transcendent": {
                "sentiment": 0.85,
                "brand_relevance": 0.8,
                "trinity_component": "consciousness",
            },
            "authentic": {
                "sentiment": 0.8,
                "brand_relevance": 0.9,
                "trinity_component": "identity",
            },
            "genuine": {"sentiment": 0.7, "brand_relevance": 0.85, "trinity_component": "identity"},
            "trustworthy": {
                "sentiment": 0.85,
                "brand_relevance": 0.9,
                "trinity_component": "guardian",
            },
            "protective": {
                "sentiment": 0.8,
                "brand_relevance": 0.85,
                "trinity_component": "guardian",
            },
            "ethical": {"sentiment": 0.8, "brand_relevance": 0.9, "trinity_component": "guardian"},
            "innovative": {
                "sentiment": 0.85,
                "brand_relevance": 0.9,
                "trinity_component": "consciousness",
            },
            "intelligent": {
                "sentiment": 0.8,
                "brand_relevance": 0.85,
                "trinity_component": "consciousness",
            },
            "helpful": {"sentiment": 0.8, "brand_relevance": 0.8, "trinity_component": "identity"},
            "empathetic": {
                "sentiment": 0.85,
                "brand_relevance": 0.8,
                "trinity_component": "identity",
            },
            "wise": {
                "sentiment": 0.8,
                "brand_relevance": 0.85,
                "trinity_component": "consciousness",
            },
            "enlightened": {
                "sentiment": 0.9,
                "brand_relevance": 0.8,
                "trinity_component": "consciousness",
            },
            "secure": {"sentiment": 0.8, "brand_relevance": 0.85, "trinity_component": "guardian"},
            "reliable": {"sentiment": 0.8, "brand_relevance": 0.8, "trinity_component": "guardian"},
            # LUKHAS-specific positive terms
            "trinity_framework": {
                "sentiment": 0.9,
                "brand_relevance": 1.0,
                "trinity_component": "all",
            },
            "qi_inspired": {
                "sentiment": 0.8,
                "brand_relevance": 0.95,
                "trinity_component": "consciousness",
            },
            "bio_inspired": {
                "sentiment": 0.8,
                "brand_relevance": 0.9,
                "trinity_component": "consciousness",
            },
            "consciousness_platform": {
                "sentiment": 0.85,
                "brand_relevance": 0.95,
                "trinity_component": "consciousness",
            },
            # Neutral terms (important for context)
            "system": {"sentiment": 0.0, "brand_relevance": 0.3, "trinity_component": "neutral"},
            "technology": {
                "sentiment": 0.1,
                "brand_relevance": 0.5,
                "trinity_component": "neutral",
            },
            "platform": {"sentiment": 0.1, "brand_relevance": 0.6, "trinity_component": "neutral"},
            # Negative indicators (what we want to avoid)
            "confusing": {
                "sentiment": -0.7,
                "brand_relevance": 0.8,
                "trinity_component": "identity",
            },
            "artificial": {
                "sentiment": -0.5,
                "brand_relevance": 0.7,
                "trinity_component": "identity",
            },
            "robotic": {"sentiment": -0.6, "brand_relevance": 0.8, "trinity_component": "identity"},
            "cold": {"sentiment": -0.7, "brand_relevance": 0.8, "trinity_component": "identity"},
            "unreliable": {
                "sentiment": -0.8,
                "brand_relevance": 0.9,
                "trinity_component": "guardian",
            },
            "unsafe": {"sentiment": -0.9, "brand_relevance": 0.95, "trinity_component": "guardian"},
            "unethical": {
                "sentiment": -0.9,
                "brand_relevance": 0.95,
                "trinity_component": "guardian",
            },
            "complicated": {
                "sentiment": -0.6,
                "brand_relevance": 0.7,
                "trinity_component": "identity",
            },
            "overwhelming": {
                "sentiment": -0.7,
                "brand_relevance": 0.8,
                "trinity_component": "identity",
            },
            # Deprecated terminology (negative for brand)
            "pwm": {"sentiment": -0.8, "brand_relevance": 0.9, "trinity_component": "identity"},
            "lukhas_pwm": {
                "sentiment": -0.8,
                "brand_relevance": 0.95,
                "trinity_component": "identity",
            },
            "lukhas_agi": {
                "sentiment": -0.7,
                "brand_relevance": 0.9,
                "trinity_component": "identity",
            },
            "lambda_function": {
                "sentiment": -0.6,
                "brand_relevance": 0.8,
                "trinity_component": "consciousness",
            },
        }

    def _build_trinity_sentiment_lexicon(self) -> dict[str, dict[str, Any]]:
        """Build Trinity Framework-specific sentiment indicators"""
        return {
            "identity": {
                "positive_indicators": [
                    "authentic",
                    "genuine",
                    "real",
                    "true",
                    "self-aware",
                    "conscious",
                    "unique",
                    "individual",
                    "personal",
                    "meaningful",
                ],
                "negative_indicators": [
                    "fake",
                    "artificial",
                    "generic",
                    "impersonal",
                    "robotic",
                    "mechanical",
                    "cold",
                    "distant",
                ],
                "symbol": "⚛️",
                "weight": 0.35,
            },
            "consciousness": {
                "positive_indicators": [
                    "aware",
                    "intelligent",
                    "thinking",
                    "understanding",
                    "learning",
                    "conscious",
                    "mindful",
                    "perceptive",
                    "insightful",
                    "wise",
                ],
                "negative_indicators": [
                    "unconscious",
                    "unaware",
                    "mindless",
                    "dumb",
                    "ignorant",
                    "oblivious",
                    "senseless",
                    "thoughtless",
                ],
                "symbol": "🧠",
                "weight": 0.35,
            },
            "guardian": {
                "positive_indicators": [
                    "safe",
                    "secure",
                    "protected",
                    "ethical",
                    "trustworthy",
                    "reliable",
                    "responsible",
                    "careful",
                    "protective",
                    "honest",
                ],
                "negative_indicators": [
                    "unsafe",
                    "dangerous",
                    "unethical",
                    "untrustworthy",
                    "unreliable",
                    "irresponsible",
                    "reckless",
                    "dishonest",
                ],
                "symbol": "🛡️",
                "weight": 0.30,
            },
        }

    def _compile_emotion_patterns(self) -> dict[str, re.Pattern]:
        """Compile regex patterns for emotion detection"""
        return {
            "excitement": re.compile(r"excit|amazing|incredible|fantastic|wonderful|brilliant", re.IGNORECASE),
            "satisfaction": re.compile(r"satisf|pleased|happy|content|glad|great", re.IGNORECASE),
            "frustration": re.compile(r"frustrat|annoying|difficult|hard|struggle|problem", re.IGNORECASE),
            "confusion": re.compile(r"confus|unclear|don't understand|lost|puzzle", re.IGNORECASE),
            "trust": re.compile(r"trust|reliable|depend|confident|faith|believe", re.IGNORECASE),
            "concern": re.compile(r"concern|worry|anxious|nervous|uncertain|doubt", re.IGNORECASE),
            "appreciation": re.compile(r"appreciat|grateful|thank|helpful|useful|valuable", re.IGNORECASE),
            "disappointment": re.compile(r"disappoint|let down|expected more|not what|underwhelm", re.IGNORECASE),
        }

    def _build_brand_dimension_indicators(self) -> dict[BrandDimension, dict[str, list[str]]]:
        """Build indicators for different brand dimensions"""
        return {
            BrandDimension.INNOVATION: {
                "positive": ["innovative", "cutting-edge", "advanced", "breakthrough", "novel"],
                "negative": ["outdated", "old-fashioned", "behind", "primitive", "basic"],
            },
            BrandDimension.TRUSTWORTHINESS: {
                "positive": [
                    "trustworthy",
                    "reliable",
                    "dependable",
                    "honest",
                    "transparent",
                    "credible",
                ],
                "negative": ["untrustworthy", "unreliable", "dishonest", "shady", "suspicious"],
            },
            BrandDimension.CONSCIOUSNESS: {
                "positive": [
                    "conscious",
                    "aware",
                    "intelligent",
                    "understanding",
                    "perceptive",
                    "mindful",
                ],
                "negative": ["unconscious", "unaware", "mindless", "ignorant", "oblivious"],
            },
            BrandDimension.HELPFULNESS: {
                "positive": [
                    "helpful",
                    "useful",
                    "supportive",
                    "assistance",
                    "beneficial",
                    "valuable",
                ],
                "negative": ["unhelpful", "useless", "hindrance", "obstacle", "worthless"],
            },
            BrandDimension.ACCESSIBILITY: {
                "positive": ["easy", "simple", "clear", "accessible", "user-friendly", "intuitive"],
                "negative": ["difficult", "complex", "confusing", "inaccessible", "complicated"],
            },
            BrandDimension.TECHNICAL_COMPETENCE: {
                "positive": ["competent", "capable", "skilled", "expert", "proficient", "advanced"],
                "negative": ["incompetent", "incapable", "unskilled", "amateur", "poor"],
            },
            BrandDimension.ETHICAL_FOUNDATION: {
                "positive": [
                    "ethical",
                    "moral",
                    "responsible",
                    "principled",
                    "virtuous",
                    "righteous",
                ],
                "negative": ["unethical", "immoral", "irresponsible", "unprincipled", "corrupt"],
            },
        }

    def _build_context_analyzers(self) -> dict[str, dict[str, Any]]:
        """Build context-specific sentiment analyzers"""
        return {
            "user_feedback": {
                "weight_multiplier": 1.2,  # User feedback carries more weight
                "focus_dimensions": [BrandDimension.HELPFULNESS, BrandDimension.ACCESSIBILITY],
                "critical_emotions": ["frustration", "satisfaction", "appreciation"],
            },
            "technical_review": {
                "weight_multiplier": 1.1,
                "focus_dimensions": [
                    BrandDimension.TECHNICAL_COMPETENCE,
                    BrandDimension.INNOVATION,
                ],
                "critical_emotions": ["trust", "concern", "satisfaction"],
            },
            "marketing_content": {
                "weight_multiplier": 0.9,  # Marketing content may be biased
                "focus_dimensions": [BrandDimension.INNOVATION, BrandDimension.CONSCIOUSNESS],
                "critical_emotions": ["excitement", "trust", "appreciation"],
            },
            "social_media": {
                "weight_multiplier": 1.0,
                "focus_dimensions": [BrandDimension.TRUSTWORTHINESS, BrandDimension.HELPFULNESS],
                "critical_emotions": [
                    "excitement",
                    "frustration",
                    "appreciation",
                    "disappointment",
                ],
            },
        }

    def analyze_sentiment(
        self, text: str, context: str = "general", metadata: Optional[dict[str, Any]] = None
    ) -> SentimentResult:
        """
        Perform comprehensive sentiment analysis with LUKHAS brand focus
        """

        # Basic sentiment calculation
        overall_sentiment = self._calculate_overall_sentiment(text)

        # Brand dimension analysis
        brand_dimensions = self._analyze_brand_dimensions(text)

        # Trinity Framework sentiment analysis
        trinity_sentiment = self._analyze_trinity_sentiment(text)

        # Emotional indicators analysis
        emotional_indicators = self._analyze_emotional_indicators(text)

        # Context appropriateness assessment
        context_appropriateness = self._assess_context_appropriateness(text, context)

        # Determine polarity and confidence
        polarity = self._determine_sentiment_polarity(overall_sentiment)
        confidence = self._calculate_sentiment_confidence(text, overall_sentiment, brand_dimensions)

        # Apply context-specific adjustments
        if context in self.context_analyzers:
            overall_sentiment = self._apply_context_adjustments(
                overall_sentiment, context, brand_dimensions, emotional_indicators
            )

        result = SentimentResult(
            overall_sentiment=overall_sentiment,
            polarity=polarity,
            confidence=confidence,
            brand_dimensions=brand_dimensions,
            trinity_sentiment=trinity_sentiment,
            emotional_indicators=emotional_indicators,
            context_appropriateness=context_appropriateness,
        )

        # Store for trend analysis
        self._store_sentiment_result(result, text, context, metadata)

        return result

    def _calculate_overall_sentiment(self, text: str) -> float:
        """Calculate overall sentiment score from -1.0 to 1.0"""

        words = re.findall(r"\b\w+\b", text.lower())
        sentiment_scores = []
        brand_relevance_weights = []

        for word in words:
            if word in self.sentiment_lexicon:
                lexicon_entry = self.sentiment_lexicon[word]
                sentiment_scores.append(lexicon_entry["sentiment"])
                brand_relevance_weights.append(lexicon_entry["brand_relevance"])

        if not sentiment_scores:
            return 0.0

        # Calculate weighted average sentiment
        if brand_relevance_weights:
            weighted_sentiment = sum(
                score * weight for score, weight in zip(sentiment_scores, brand_relevance_weights)
            ) / sum(brand_relevance_weights)
        else:
            weighted_sentiment = sum(sentiment_scores) / len(sentiment_scores)

        # Normalize to -1.0 to 1.0 range
        return max(-1.0, min(1.0, weighted_sentiment))

    def _analyze_brand_dimensions(self, text: str) -> dict[BrandDimension, float]:
        """Analyze sentiment for each brand dimension"""

        dimension_scores = {}
        text_lower = text.lower()

        for dimension, indicators in self.brand_dimension_indicators.items():
            positive_count = sum(1 for term in indicators["positive"] if term in text_lower)
            negative_count = sum(1 for term in indicators["negative"] if term in text_lower)

            total_mentions = positive_count + negative_count

            if total_mentions == 0:
                dimension_scores[dimension] = 0.0  # Neutral when no mentions
            else:
                # Calculate score from -1.0 to 1.0
                dimension_scores[dimension] = (positive_count - negative_count) / total_mentions

        return dimension_scores

    def _analyze_trinity_sentiment(self, text: str) -> dict[str, float]:
        """Analyze sentiment for each Trinity Framework component"""

        trinity_scores = {}
        text_lower = text.lower()

        for component, lexicon in self.trinity_lexicon.items():
            positive_count = sum(1 for term in lexicon["positive_indicators"] if term in text_lower)
            negative_count = sum(1 for term in lexicon["negative_indicators"] if term in text_lower)

            # Check for symbol presence (adds positive weight)
            symbol_present = lexicon["symbol"] in text
            if symbol_present:
                positive_count += 1

            total_mentions = positive_count + negative_count

            if total_mentions == 0:
                trinity_scores[component] = 0.0
            else:
                trinity_scores[component] = (positive_count - negative_count) / total_mentions

        return trinity_scores

    def _analyze_emotional_indicators(self, text: str) -> dict[str, float]:
        """Analyze emotional indicators in the text"""

        emotional_scores = {}

        for emotion, pattern in self.emotion_patterns.items():
            matches = pattern.findall(text)

            # Calculate emotional intensity based on frequency and context
            if matches:
                # Basic frequency-based scoring
                frequency_score = min(1.0, len(matches) / 3)  # Cap at 3 mentions for max score

                # Adjust for text length
                text_length_factor = len(text.split()) / 100  # Normalize by approximate word count
                adjusted_score = frequency_score / max(1.0, text_length_factor)

                emotional_scores[emotion] = min(1.0, adjusted_score)
            else:
                emotional_scores[emotion] = 0.0

        return emotional_scores

    def _assess_context_appropriateness(self, text: str, context: str) -> float:
        """Assess how appropriate the sentiment is for the given context"""

        if context not in self.context_analyzers:
            return 0.5  # Neutral appropriateness for unknown contexts

        context_config = self.context_analyzers[context]
        focus_dimensions = context_config["focus_dimensions"]
        critical_emotions = context_config["critical_emotions"]

        # Analyze brand dimensions relevant to this context
        brand_dimensions = self._analyze_brand_dimensions(text)
        relevant_dimension_scores = [brand_dimensions.get(dim, 0.0) for dim in focus_dimensions]

        # Analyze critical emotions for this context
        emotional_indicators = self._analyze_emotional_indicators(text)
        critical_emotion_scores = [emotional_indicators.get(emotion, 0.0) for emotion in critical_emotions]

        # Calculate appropriateness based on positive indicators in relevant dimensions
        dimension_appropriateness = (
            sum(max(0, score) for score in relevant_dimension_scores) / len(relevant_dimension_scores)
            if relevant_dimension_scores
            else 0.5
        )

        # Factor in emotional appropriateness (presence of relevant emotions)
        emotion_appropriateness = (
            sum(critical_emotion_scores) / len(critical_emotion_scores) if critical_emotion_scores else 0.5
        )

        # Combined appropriateness score
        overall_appropriateness = dimension_appropriateness * 0.7 + emotion_appropriateness * 0.3

        return min(1.0, overall_appropriateness)

    def _determine_sentiment_polarity(self, sentiment_score: float) -> SentimentPolarity:
        """Determine sentiment polarity category"""

        if sentiment_score >= 0.6:
            return SentimentPolarity.VERY_POSITIVE
        elif sentiment_score >= 0.2:
            return SentimentPolarity.POSITIVE
        elif sentiment_score >= -0.2:
            return SentimentPolarity.NEUTRAL
        elif sentiment_score >= -0.6:
            return SentimentPolarity.NEGATIVE
        else:
            return SentimentPolarity.VERY_NEGATIVE

    def _calculate_sentiment_confidence(
        self, text: str, overall_sentiment: float, brand_dimensions: dict[BrandDimension, float]
    ) -> float:
        """Calculate confidence in sentiment analysis"""

        # Factors that increase confidence:
        # 1. Presence of brand-relevant terms
        # 2. Clear sentiment indicators
        # 3. Consistency across dimensions
        # 4. Sufficient text length

        words = text.lower().split()
        brand_relevant_terms = sum(1 for word in words if word in self.sentiment_lexicon)
        brand_relevance_factor = min(1.0, brand_relevant_terms / max(1, len(words) / 10))

        # Sentiment clarity (distance from neutral)
        sentiment_clarity = abs(overall_sentiment)

        # Dimensional consistency (low variance indicates consistent sentiment)
        dimension_values = [score for score in brand_dimensions.values() if score != 0.0]
        if dimension_values:
            dimension_variance = sum((score - overall_sentiment) ** 2 for score in dimension_values) / len(
                dimension_values
            )
            consistency_factor = max(0.0, 1.0 - dimension_variance)
        else:
            consistency_factor = 0.5

        # Text length factor (more text generally gives more confidence, up to a point)
        text_length_factor = min(1.0, len(words) / 50)  # Optimal around 50 words

        # Combine factors
        confidence = (
            brand_relevance_factor * 0.3 + sentiment_clarity * 0.3 + consistency_factor * 0.2 + text_length_factor * 0.2
        )

        return min(1.0, max(0.1, confidence))  # Ensure confidence is between 0.1 and 1.0

    def _apply_context_adjustments(
        self,
        base_sentiment: float,
        context: str,
        brand_dimensions: dict[BrandDimension, float],
        emotional_indicators: dict[str, float],
    ) -> float:
        """Apply context-specific adjustments to sentiment score"""

        context_config = self.context_analyzers[context]
        weight_multiplier = context_config["weight_multiplier"]

        # Adjust based on context relevance
        adjusted_sentiment = base_sentiment * weight_multiplier

        # Apply context-specific emotional adjustments
        critical_emotions = context_config["critical_emotions"]
        emotion_adjustment = 0.0

        for emotion in critical_emotions:
            if emotion in emotional_indicators:
                if emotion in ["frustration", "concern", "disappointment"]:
                    emotion_adjustment -= emotional_indicators[emotion] * 0.1
                else:  # Positive emotions
                    emotion_adjustment += emotional_indicators[emotion] * 0.1

        final_sentiment = adjusted_sentiment + emotion_adjustment

        return max(-1.0, min(1.0, final_sentiment))

    def _store_sentiment_result(
        self, result: SentimentResult, text: str, context: str, metadata: Optional[dict[str, Any]]
    ) -> None:
        """Store sentiment result for historical analysis"""

        self.sentiment_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "text_length": len(text),
                "context": context,
                "overall_sentiment": result.overall_sentiment,
                "polarity": result.polarity.value,
                "confidence": result.confidence,
                "brand_dimensions": {dim.value: score for dim, score in result.brand_dimensions.items()},
                "trinity_sentiment": result.trinity_sentiment,
                "context_appropriateness": result.context_appropriateness,
                "metadata": metadata or {},
            }
        )

        # Keep only recent history (last 1000 entries)
        if len(self.sentiment_history) > 1000:
            self.sentiment_history = self.sentiment_history[-1000:]

    def get_sentiment_trends(self, time_period: str = "24h") -> dict[str, Any]:
        """Get sentiment trends over specified time period"""

        # Parse time period
        if time_period == "24h":
            cutoff_time = datetime.now() - timedelta(hours=24)
        elif time_period == "7d":
            cutoff_time = datetime.now() - timedelta(days=7)
        elif time_period == "30d":
            cutoff_time = datetime.now() - timedelta(days=30)
        else:
            cutoff_time = datetime.now() - timedelta(hours=24)  # Default to 24h

        # Filter recent sentiment history
        recent_sentiments = [
            entry for entry in self.sentiment_history if datetime.fromisoformat(entry["timestamp"]) > cutoff_time
        ]

        if not recent_sentiments:
            return {"error": "No sentiment data available for specified time period"}

        # Calculate trends
        overall_sentiments = [entry["overall_sentiment"] for entry in recent_sentiments]
        confidences = [entry["confidence"] for entry in recent_sentiments]

        # Brand dimension trends
        dimension_trends = {}
        for dimension in BrandDimension:
            dimension_scores = [entry["brand_dimensions"].get(dimension.value, 0.0) for entry in recent_sentiments]
            dimension_trends[dimension.value] = {
                "average": sum(dimension_scores) / len(dimension_scores),
                "trend": "improving"
                if dimension_scores[-1] > dimension_scores[0]
                else "declining"
                if len(dimension_scores) > 1
                else "stable",
            }

        # Trinity sentiment trends
        trinity_trends = {}
        for component in ["identity", "consciousness", "guardian"]:
            component_scores = [entry["trinity_sentiment"].get(component, 0.0) for entry in recent_sentiments]
            trinity_trends[component] = {
                "average": sum(component_scores) / len(component_scores),
                "trend": "improving"
                if component_scores[-1] > component_scores[0]
                else "declining"
                if len(component_scores) > 1
                else "stable",
            }

        return {
            "time_period": time_period,
            "total_analyses": len(recent_sentiments),
            "overall_sentiment": {
                "average": sum(overall_sentiments) / len(overall_sentiments),
                "latest": overall_sentiments[-1],
                "trend": "improving"
                if overall_sentiments[-1] > overall_sentiments[0]
                else "declining"
                if len(overall_sentiments) > 1
                else "stable",
            },
            "average_confidence": sum(confidences) / len(confidences),
            "brand_dimension_trends": dimension_trends,
            "trinity_sentiment_trends": trinity_trends,
            "sentiment_distribution": self._calculate_sentiment_distribution(overall_sentiments),
        }

    def _calculate_sentiment_distribution(self, sentiments: list[float]) -> dict[str, float]:
        """Calculate distribution of sentiments across polarity categories"""

        distribution = {polarity.value: 0 for polarity in SentimentPolarity}

        for sentiment in sentiments:
            polarity = self._determine_sentiment_polarity(sentiment)
            distribution[polarity.value] += 1

        # Convert to percentages
        total = len(sentiments)
        for polarity in distribution:
            distribution[polarity] = (distribution[polarity] / total) * 100

        return distribution

    def analyze_brand_perception_evolution(self, time_periods: list[str] = None) -> dict[str, Any]:
        """Analyze how brand perception has evolved over time"""

        if time_periods is None:
            time_periods = ["24h", "7d", "30d"]

        evolution_analysis = {}

        for period in time_periods:
            trends = self.get_sentiment_trends(period)
            if "error" not in trends:
                evolution_analysis[period] = {
                    "overall_sentiment": trends["overall_sentiment"]["average"],
                    "confidence": trends["average_confidence"],
                    "strongest_dimension": max(trends["brand_dimension_trends"].items(), key=lambda x: x[1]["average"])[
                        0
                    ],
                    "trinity_strength": {
                        component: data["average"] for component, data in trends["trinity_sentiment_trends"].items()
                    },
                }

        # Calculate evolution insights
        if len(evolution_analysis) >= 2:
            periods = sorted(evolution_analysis.keys())
            latest_period = periods[-1]
            previous_period = periods[-2]

            sentiment_change = (
                evolution_analysis[latest_period]["overall_sentiment"]
                - evolution_analysis[previous_period]["overall_sentiment"]
            )

            evolution_insights = {
                "sentiment_change": sentiment_change,
                "evolution_direction": "improving"
                if sentiment_change > 0.05
                else "declining"
                if sentiment_change < -0.05
                else "stable",
                "confidence_evolution": evolution_analysis[latest_period]["confidence"]
                - evolution_analysis[previous_period]["confidence"],
                "key_changes": [],
            }

            # Identify key changes in Trinity components
            for component in ["identity", "consciousness", "guardian"]:
                latest_score = evolution_analysis[latest_period]["trinity_strength"][component]
                previous_score = evolution_analysis[previous_period]["trinity_strength"][component]
                change = latest_score - previous_score

                if abs(change) > 0.1:  # Significant change threshold
                    evolution_insights["key_changes"].append(
                        {
                            "component": component,
                            "change": change,
                            "direction": "improvement" if change > 0 else "decline",
                        }
                    )

            evolution_analysis["evolution_insights"] = evolution_insights

        return evolution_analysis

    def generate_sentiment_report(self, context: str = "general") -> dict[str, Any]:
        """Generate comprehensive sentiment analysis report"""

        # Get recent trends
        recent_trends = self.get_sentiment_trends("24h")
        weekly_trends = self.get_sentiment_trends("7d")

        # Get evolution analysis
        evolution = self.analyze_brand_perception_evolution()

        # Calculate context-specific insights
        context_insights = self._generate_context_specific_insights(context, recent_trends)

        return {
            "report_timestamp": datetime.now().isoformat(),
            "context": context,
            "executive_summary": {
                "overall_brand_sentiment": recent_trends.get("overall_sentiment", {}).get("average", 0.0),
                "sentiment_trend": recent_trends.get("overall_sentiment", {}).get("trend", "stable"),
                "confidence_level": recent_trends.get("average_confidence", 0.0),
                "key_strength": self._identify_key_strength(recent_trends),
                "primary_opportunity": self._identify_primary_opportunity(recent_trends),
            },
            "detailed_analysis": {
                "recent_trends": recent_trends,
                "weekly_trends": weekly_trends,
                "brand_evolution": evolution,
                "context_insights": context_insights,
            },
            "recommendations": self._generate_sentiment_recommendations(recent_trends, evolution, context),
        }

    def _generate_context_specific_insights(self, context: str, trends: dict[str, Any]) -> dict[str, Any]:
        """Generate insights specific to the given context"""

        if context not in self.context_analyzers:
            return {"insight": "No specific insights available for this context"}

        context_config = self.context_analyzers[context]
        focus_dimensions = context_config["focus_dimensions"]

        # Analyze performance in focus dimensions
        dimension_performance = {}
        for dimension in focus_dimensions:
            if dimension.value in trends.get("brand_dimension_trends", {}):
                dimension_data = trends["brand_dimension_trends"][dimension.value]
                dimension_performance[dimension.value] = {
                    "score": dimension_data["average"],
                    "trend": dimension_data["trend"],
                    "performance_level": "excellent"
                    if dimension_data["average"] > 0.7
                    else "good"
                    if dimension_data["average"] > 0.3
                    else "needs_improvement",
                }

        return {
            "context": context,
            "focus_dimensions_performance": dimension_performance,
            "context_appropriateness": "high"
            if all(perf["score"] > 0.5 for perf in dimension_performance.values())
            else "moderate",
        }

    def _identify_key_strength(self, trends: dict[str, Any]) -> str:
        """Identify the key brand strength from sentiment trends"""

        dimension_trends = trends.get("brand_dimension_trends", {})
        if not dimension_trends:
            return "Insufficient data"

        strongest_dimension = max(dimension_trends.items(), key=lambda x: x[1]["average"])
        return strongest_dimension[0].replace("_", " ").title()

    def _identify_primary_opportunity(self, trends: dict[str, Any]) -> str:
        """Identify the primary improvement opportunity"""

        dimension_trends = trends.get("brand_dimension_trends", {})
        if not dimension_trends:
            return "Insufficient data"

        weakest_dimension = min(dimension_trends.items(), key=lambda x: x[1]["average"])
        return f"Improve {weakest_dimension[0].replace('_', ' ').title()}"

    def _generate_sentiment_recommendations(
        self, recent_trends: dict[str, Any], evolution: dict[str, Any], context: str
    ) -> list[dict[str, str]]:
        """Generate actionable recommendations based on sentiment analysis"""

        recommendations = []

        # Overall sentiment recommendations
        overall_sentiment = recent_trends.get("overall_sentiment", {}).get("average", 0.0)
        if overall_sentiment < 0.5:
            recommendations.append(
                {
                    "category": "overall_sentiment",
                    "priority": "high",
                    "recommendation": "Focus on improving overall brand sentiment through enhanced user experience and clearer value communication",
                }
            )

        # Brand dimension recommendations
        dimension_trends = recent_trends.get("brand_dimension_trends", {})
        for dimension, data in dimension_trends.items():
            if data["average"] < 0.3:
                recommendations.append(
                    {
                        "category": dimension,
                        "priority": "medium",
                        "recommendation": f"Improve {dimension.replace('_', ' ')} through targeted messaging and feature enhancements",
                    }
                )

        # Trinity Framework recommendations
        trinity_trends = recent_trends.get("trinity_sentiment_trends", {})
        for component, data in trinity_trends.items():
            if data["average"] < 0.4:
                recommendations.append(
                    {
                        "category": f"trinity_{component}",
                        "priority": "high",
                        "recommendation": f"Strengthen {component} component of Trinity Framework to improve brand coherence",
                    }
                )

        # Context-specific recommendations
        if context in self.context_analyzers:
            context_config = self.context_analyzers[context]
            focus_dimensions = context_config["focus_dimensions"]

            for dimension in focus_dimensions:
                dimension_score = dimension_trends.get(dimension.value, {}).get("average", 0.0)
                if dimension_score < 0.6:  # Higher threshold for focus dimensions
                    recommendations.append(
                        {
                            "category": f"context_{context}",
                            "priority": "high",
                            "recommendation": f"Improve {dimension.value.replace('_', ' ')} specifically for {context} contexts",
                        }
                    )

        return recommendations


# Example usage and testing
if __name__ == "__main__":
    engine = BrandSentimentEngine()

    # Test sentiment analysis
    test_texts = [
        "LUKHAS AI consciousness platform is incredibly innovative and trustworthy. The Trinity Framework (⚛️🧠🛡️) makes it feel authentic and ethical.",
        "This system seems confusing and artificial. I don't understand how it works.",
        "The quantum-inspired technology is fascinating, but the interface could be more user-friendly.",
        "LUKHAS PWM is difficult to use and unreliable.",  # Contains deprecated terminology
    ]

    for i, text in enumerate(test_texts):
        print(f"\n--- Test {i + 1} ---")
        print(f"Text: {text}")

        result = engine.analyze_sentiment(text, context="user_feedback")

        print(f"Overall Sentiment: {result.overall_sentiment:.3f}")
        print(f"Polarity: {result.polarity.value}")
        print(f"Confidence: {result.confidence:.3f}")
        print(f"Context Appropriateness: {result.context_appropriateness:.3f}")

        # Show top brand dimensions
        top_dimensions = sorted(result.brand_dimensions.items(), key=lambda x: abs(x[1]), reverse=True)[:3]

        print("Top Brand Dimensions:")
        for dimension, score in top_dimensions:
            if score != 0.0:
                print(f"  {dimension.value}: {score:.3f}")

        # Show Trinity sentiment
        print("Trinity Sentiment:")
        for component, score in result.trinity_sentiment.items():
            if score != 0.0:
                print(f"  {component}: {score:.3f}")

    # Test sentiment trends
    print("\n--- Sentiment Trends ---")
    trends = engine.get_sentiment_trends("24h")
    if "error" not in trends:
        print(f"Overall Sentiment Average: {trends['overall_sentiment']['average']:.3f}")
        print(f"Trend: {trends['overall_sentiment']['trend']}")
        print(f"Average Confidence: {trends['average_confidence']:.3f}")

    # Generate sentiment report
    print("\n--- Sentiment Report ---")
    report = engine.generate_sentiment_report("user_feedback")
    print(f"Brand Sentiment: {report['executive_summary']['overall_brand_sentiment']:.3f}")
    print(f"Key Strength: {report['executive_summary']['key_strength']}")
    print(f"Primary Opportunity: {report['executive_summary']['primary_opportunity']}")
    print(f"Recommendations: {len(report['recommendations'])}")
