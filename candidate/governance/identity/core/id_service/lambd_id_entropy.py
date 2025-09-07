"""Compatibility shim for legacy `lambd_id_entropy` module.

Re-exports canonical entropy implementation from `lambda_id_entropy.py`.
"""
from datetime import timezone

from .lambda_id_entropy import EntropyCalculator

# Backwards-compatible alias
EntropyCalculatorLegacy = EntropyCalculator

__all__ = ["EntropyCalculator", "EntropyCalculatorLegacy"]
"""
LUKHAS ΛiD Entropy Engine
========================

Advanced entropy scoring and analysis system for LUKHAS ΛiDs.
Evaluates randomness, uniqueness, and security strength of generated identities.

Features:
- Shannon entropy calculation
- Pattern analysis
- Randomness testing
- Security scoring
- Predictability analysis
- Tier-based entropy requirements
- Temporal entropy tracking

Author: LUKHAS AI Systems
Created: 2025-07-05
"""

import math
import re
import statistics
from collections import Counter
from datetime import datetime
from enum import Enum
from typing import Optional


class EntropyLevel(Enum):
    """Entropy quality levels"""

    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    CRYPTOGRAPHIC = "cryptographic"


class EntropyAnalysis:
    """Comprehensive entropy analysis results"""

    def __init__(self):
        self.shannon_entropy: float = 0.0
        self.normalized_entropy: float = 0.0
        self.character_diversity: float = 0.0
        self.pattern_score: float = 0.0
        self.randomness_score: float = 0.0
        self.security_level: EntropyLevel = EntropyLevel.VERY_LOW
        self.recommendations: list[str] = []
        self.warnings: list[str] = []


class LambdaIDEntropy:
    """
    Advanced entropy analysis engine for ΛiD components.

    Provides comprehensive entropy scoring for security validation,
    pattern detection, and randomness assessment.
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize entropy engine with configuration"""
        self.config = self._load_config(config_path)
        self.entropy_history: list[dict] = []
        self.pattern_database: set[str] = set()
        self.weak_patterns = self._load_weak_patterns()
        self.tier_requirements = self._load_tier_requirements()

    def analyze_lambda_id_entropy(self, lambda_id: str) -> EntropyAnalysis:
        """
        Comprehensive entropy analysis of a complete ΛiD.

        Args:
            lambda_id: The ΛiD string to analyze

        Returns:
            EntropyAnalysis: Detailed entropy analysis results
        """
        analysis = EntropyAnalysis()

        # Parse ΛiD components
        components = self._parse_lambda_id(lambda_id)
        if not components:
            analysis.warnings.append("Invalid ΛiD format for entropy analysis")
            return analysis

        tier, timestamp_hash, symbolic_char, entropy_hash = components

        # Analyze individual components
        self._analyze_component_entropy(timestamp_hash)
        self._analyze_component_entropy(entropy_hash)
        self._analyze_symbolic_entropy(symbolic_char, tier)

        # Calculate overall entropy scores
        analysis.shannon_entropy = self._calculate_combined_shannon_entropy(components)
        analysis.normalized_entropy = self._normalize_entropy(analysis.shannon_entropy, len(lambda_id))
        analysis.character_diversity = self._calculate_character_diversity(lambda_id)
        analysis.pattern_score = self._analyze_patterns(lambda_id)
        analysis.randomness_score = self._analyze_randomness(entropy_hash)

        # Determine security level
        analysis.security_level = self._determine_security_level(analysis)

        # Generate recommendations and warnings
        analysis.recommendations = self._generate_recommendations(analysis, tier)
        analysis.warnings = self._detect_entropy_warnings(analysis, components)

        # Store in history for temporal analysis
        self._store_entropy_analysis(lambda_id, analysis)

        return analysis

    def _calculate_combined_shannon_entropy(self, components: tuple) -> float:
        """Calculate Shannon entropy for the complete ΛiD"""
        tier, timestamp_hash, symbolic_char, entropy_hash = components

        # Combine all meaningful components (exclude tier as it's not random)
        combined_string = timestamp_hash + symbolic_char + entropy_hash

        return self._calculate_shannon_entropy(combined_string)

    def _calculate_shannon_entropy(self, text: str) -> float:
        """
        Calculate Shannon entropy for a given string.

        Formula: H(X) = -Σ P(xi) * log2(P(xi))
        """
        if not text:
            return 0.0

        # Count character frequencies
        char_counts = Counter(text)
        text_length = len(text)

        # Calculate entropy
        entropy = 0.0
        for count in char_counts.values():
            probability = count / text_length
            if probability > 0:
                entropy -= probability * math.log2(probability)

        return entropy

    def _normalize_entropy(self, entropy: float, string_length: int) -> float:
        """Normalize entropy to 0-1 scale based on string length"""
        if string_length == 0:
            return 0.0

        # Maximum possible entropy for given length
        max_entropy = math.log2(min(256, string_length))  # Assuming ASCII/UTF-8

        return min(entropy / max_entropy, 1.0) if max_entropy > 0 else 0.0

    def _calculate_character_diversity(self, text: str) -> float:
        """Calculate character diversity score (unique chars / total chars)"""
        if not text:
            return 0.0

        unique_chars = len(set(text))
        total_chars = len(text)

        return unique_chars / total_chars

    def _analyze_component_entropy(self, component: str) -> float:
        """Analyze entropy of individual ΛiD component"""
        return self._calculate_shannon_entropy(component)

    def _analyze_symbolic_entropy(self, symbolic_char: str, tier: int) -> float:
        """Analyze entropy contribution of symbolic character"""
        tier_symbols = self.tier_requirements.get(f"tier_{tier}", {}).get("symbols", [])

        if not tier_symbols:
            return 0.0

        # Entropy is log2 of possible choices
        return math.log2(len(tier_symbols))

    def _analyze_patterns(self, lambda_id: str) -> float:
        """
        Analyze for predictable patterns in ΛiD.

        Returns pattern score where 1.0 = no patterns, 0.0 = highly predictable
        """
        pattern_score = 1.0

        # Check for weak patterns
        for pattern in self.weak_patterns:
            if pattern in lambda_id.lower():
                pattern_score -= 0.2

        # Check for repetitive sequences
        repetition_penalty = self._detect_repetitive_sequences(lambda_id)
        pattern_score -= repetition_penalty

        # Check for sequential patterns
        sequential_penalty = self._detect_sequential_patterns(lambda_id)
        pattern_score -= sequential_penalty

        return max(pattern_score, 0.0)

    def _detect_repetitive_sequences(self, text: str) -> float:
        """Detect repetitive character sequences"""
        penalty = 0.0

        for i in range(len(text) - 1):
            if text[i] == text[i + 1]:
                penalty += 0.1

        # Check for longer repetitive patterns
        for length in range(2, min(len(text) // 2 + 1, 4)):
            for i in range(len(text) - length * 2 + 1):
                if text[i : i + length] == text[i + length : i + length * 2]:
                    penalty += 0.2

        return min(penalty, 1.0)

    def _detect_sequential_patterns(self, text: str) -> float:
        """Detect sequential patterns (ABC, 123, etc.)"""
        penalty = 0.0

        # Convert to ASCII values for sequence detection
        ascii_values = [ord(c) for c in text if c.isalnum()]

        for i in range(len(ascii_values) - 2):
            # Check for ascending sequences
            if ascii_values[i + 1] == ascii_values[i] + 1 and ascii_values[i + 2] == ascii_values[i] + 2:
                penalty += 0.3

            # Check for descending sequences
            if ascii_values[i + 1] == ascii_values[i] - 1 and ascii_values[i + 2] == ascii_values[i] - 2:
                penalty += 0.3

        return min(penalty, 1.0)

    def _analyze_randomness(self, entropy_hash: str) -> float:
        """
        Analyze randomness quality of entropy hash.

        Uses multiple statistical tests to assess randomness.
        """
        if not entropy_hash:
            return 0.0

        scores = []

        # Test 1: Character distribution uniformity
        char_distribution_score = self._test_character_distribution(entropy_hash)
        scores.append(char_distribution_score)

        # Test 2: Runs test (alternating patterns)
        runs_score = self._test_runs(entropy_hash)
        scores.append(runs_score)

        # Test 3: Chi-square test for uniformity
        chi_square_score = self._test_chi_square(entropy_hash)
        scores.append(chi_square_score)

        # Return average of all tests
        return statistics.mean(scores) if scores else 0.0

    def _test_character_distribution(self, text: str) -> float:
        """Test uniformity of character distribution"""
        if not text:
            return 0.0

        char_counts = Counter(text)
        expected_frequency = len(text) / len(char_counts)

        # Calculate variance from expected uniform distribution
        variance = sum((count - expected_frequency) ** 2 for count in char_counts.values())
        variance /= len(char_counts)

        # Normalize score (lower variance = higher score)
        max_variance = expected_frequency**2
        uniformity_score = 1.0 - (variance / max_variance)

        return max(uniformity_score, 0.0)

    def _test_runs(self, text: str) -> float:
        """Test for runs (consecutive identical characters)"""
        if len(text) < 2:
            return 1.0

        runs = 1
        for i in range(1, len(text)):
            if text[i] != text[i - 1]:
                runs += 1

        # Expected runs for random sequence
        expected_runs = (2 * len(text) - 1) / 3

        # Score based on how close to expected
        runs_score = 1.0 - abs(runs - expected_runs) / expected_runs

        return max(runs_score, 0.0)

    def _test_chi_square(self, text: str) -> float:
        """Chi-square test for character frequency uniformity"""
        if not text:
            return 0.0

        char_counts = Counter(text)
        expected_frequency = len(text) / len(char_counts)

        # Calculate chi-square statistic
        chi_square = sum((count - expected_frequency) ** 2 / expected_frequency for count in char_counts.values())

        # Normalize to 0-1 scale (this is a simplified version)
        # In practice, you'd compare against chi-square distribution
        degrees_of_freedom = len(char_counts) - 1
        normalized_chi_square = chi_square / (degrees_of_freedom + 1)

        # Score inversely related to chi-square (lower chi-square = more uniform)
        return max(1.0 - normalized_chi_square / 10.0, 0.0)

    def _determine_security_level(self, analysis: EntropyAnalysis) -> EntropyLevel:
        """Determine overall security level based on entropy analysis"""
        # Weighted scoring
        total_score = (
            analysis.normalized_entropy * 0.3
            + analysis.character_diversity * 0.2
            + analysis.pattern_score * 0.3
            + analysis.randomness_score * 0.2
        )

        if total_score >= 0.9:
            return EntropyLevel.CRYPTOGRAPHIC
        elif total_score >= 0.8:
            return EntropyLevel.VERY_HIGH
        elif total_score >= 0.7:
            return EntropyLevel.HIGH
        elif total_score >= 0.5:
            return EntropyLevel.MEDIUM
        elif total_score >= 0.3:
            return EntropyLevel.LOW
        else:
            return EntropyLevel.VERY_LOW

    def _generate_recommendations(self, analysis: EntropyAnalysis, tier: int) -> list[str]:
        """Generate entropy improvement recommendations"""
        recommendations = []

        tier_min_entropy = self.tier_requirements.get(f"tier_{tier}", {}).get("min_entropy", 0.5)

        if analysis.normalized_entropy < tier_min_entropy:
            recommendations.append(
                f"Increase entropy for Tier {tier} (current: {analysis.normalized_entropy:.2f}, required: {tier_min_entropy:.2f})"
            )

        if analysis.character_diversity < 0.7:
            recommendations.append("Improve character diversity in entropy generation")

        if analysis.pattern_score < 0.8:
            recommendations.append("Avoid predictable patterns in ID generation")

        if analysis.randomness_score < 0.7:
            recommendations.append("Improve randomness quality in entropy source")

        return recommendations

    def _detect_entropy_warnings(self, analysis: EntropyAnalysis, components: tuple) -> list[str]:
        """Detect entropy-related warnings"""
        warnings = []

        if analysis.security_level in [EntropyLevel.VERY_LOW, EntropyLevel.LOW]:
            warnings.append("Low entropy detected - ΛiD may be predictable")

        if analysis.pattern_score < 0.5:
            warnings.append("High pattern predictability detected")

        if analysis.randomness_score < 0.5:
            warnings.append("Poor randomness quality in entropy generation")

        return warnings

    def _parse_lambda_id(self, lambda_id: str) -> Optional[tuple]:
        """Parse ΛiD into components"""
        pattern = re.compile(r"^LUKHAS([0-5])-([A-F0-9]{4})-(.)-([A-F0-9]{4})$")
        match = pattern.match(lambda_id)

        if not match:
            return None

        tier = int(match.group(1))
        timestamp_hash = match.group(2)
        symbolic_char = match.group(3)
        entropy_hash = match.group(4)

        return tier, timestamp_hash, symbolic_char, entropy_hash

    def _store_entropy_analysis(self, lambda_id: str, analysis: EntropyAnalysis) -> None:
        """Store entropy analysis for temporal tracking"""
        self.entropy_history.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "lambda_id": lambda_id,
                "shannon_entropy": analysis.shannon_entropy,
                "normalized_entropy": analysis.normalized_entropy,
                "security_level": analysis.security_level.value,
            }
        )

        # Keep only recent history (last 1000 entries)
        if len(self.entropy_history) > 1000:
            self.entropy_history = self.entropy_history[-1000:]

    def get_entropy_statistics(self) -> dict:
        """Get entropy statistics from historical data"""
        if not self.entropy_history:
            return {"message": "No entropy history available"}

        entropies = [entry["normalized_entropy"] for entry in self.entropy_history]

        return {
            "total_analyzed": len(self.entropy_history),
            "average_entropy": statistics.mean(entropies),
            "median_entropy": statistics.median(entropies),
            "min_entropy": min(entropies),
            "max_entropy": max(entropies),
            "entropy_std": statistics.stdev(entropies) if len(entropies) > 1 else 0.0,
        }

    def _load_config(self, config_path: Optional[str] = None) -> dict:
        """Load entropy engine configuration"""
        return {
            "history_limit": 1000,
            "statistical_tests": ["distribution", "runs", "chi_square"],
            "pattern_detection": True,
            "temporal_analysis": True,
        }

    def _load_weak_patterns(self) -> list[str]:
        """Load known weak patterns to detect"""
        return [
            "1234",
            "abcd",
            "0000",
            "ffff",
            "1111",
            "aaaa",
            "test",
            "null",
            "admin",
            "user",
            "pass",
            "demo",
        ]

    def _load_tier_requirements(self) -> dict:
        """Load entropy requirements for each tier"""
        return {
            "tier_0": {"min_entropy": 0.3, "symbols": ["◊", "○", "□"]},
            "tier_1": {"min_entropy": 0.4, "symbols": ["◊", "○", "□", "△", "▽"]},
            "tier_2": {"min_entropy": 0.5, "symbols": ["🌀", "✨", "🔮", "◊", "⟐"]},
            "tier_3": {
                "min_entropy": 0.6,
                "symbols": ["🌀", "✨", "🔮", "⟐", "◈", "⬟"],
            },
            "tier_4": {"min_entropy": 0.7, "symbols": ["⟐", "◈", "⬟", "⬢", "⟁", "◐"]},
            "tier_5": {
                "min_entropy": 0.8,
                "symbols": ["⟐", "◈", "⬟", "⬢", "⟁", "◐", "◑", "⬧"],
            },
        }


# Example usage and testing
if __name__ == "__main__":
    entropy_engine = LambdaIDEntropy()

    # Test ΛiDs with different entropy levels
    test_ids = [
        "Λ2-A9F3-🌀-X7K1",  # Good entropy
        "Λ0-1234-○-ABCD",  # Weak patterns
        "Λ5-B2E8-⟐-Z9M4",  # High entropy
        "Λ1-0000-△-1111",  # Very weak entropy
    ]

    for lambda_id in test_ids:
        analysis = entropy_engine.analyze_lambda_id_entropy(lambda_id)

        print(f"\nEntropy Analysis for: {lambda_id}")
        print(f"  Shannon Entropy: {analysis.shannon_entropy:.3f}")
        print(f"  Normalized Entropy: {analysis.normalized_entropy:.3f}")
        print(f"  Character Diversity: {analysis.character_diversity:.3f}")
        print(f"  Pattern Score: {analysis.pattern_score:.3f}")
        print(f"  Randomness Score: {analysis.randomness_score:.3f}")
        print(f"  Security Level: {analysis.security_level.value}")

        if analysis.recommendations:
            print(f"  Recommendations: {analysis.recommendations}")

        if analysis.warnings:
            print(f"  Warnings: {analysis.warnings}")

    print(f"\nEntropy Statistics: {entropy_engine.get_entropy_statistics()}")
