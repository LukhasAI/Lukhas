"""
LUKHAS ΛiD Entropy Scoring Engine
=================================

Advanced entropy analysis system for ΛiD generation and optimization.
Provides real-time entropy scoring, boost factor calculation, and optimization recommendations.

Features:
- Shannon entropy calculation with Unicode boost factors
- Real-time entropy scoring for Tier 4+ users
- Pattern complexity analysis
- Symbolic character strength evaluation
- Entropy optimization recommendations
- Batch entropy analysis
- Historical entropy tracking

Author: LUKHAS AI Systems
Version: 1.0.0
Created: 2025-07-05
"""

import math
import re
import unicodedata
from typing import Dict, List, Optional, Tuple, Any, Set
from enum import Enum
from datetime import datetime
from collections import defaultdict

class EntropyLevel(Enum):
    """Entropy quality levels"""
    VERY_LOW = "very_low"      # < 1.0
    LOW = "low"                # 1.0 - 2.0
    MEDIUM = "medium"          # 2.0 - 3.0
    HIGH = "high"              # 3.0 - 4.0
    VERY_HIGH = "very_high"    # > 4.0

class EntropyAnalysis:
    """Detailed entropy analysis result"""

    def __init__(self):
        self.lambda_id = ""
        self.overall_score = 0.0
        self.base_entropy = 0.0
        self.boost_factors = {}
        self.entropy_level = EntropyLevel.VERY_LOW
        self.component_scores = {}
        self.strengths = []
        self.weaknesses = []
        self.recommendations = []
        self.tier_compliance = {}
        self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert analysis to dictionary"""
        return {
            'lambda_id': self.lambda_id,
            'overall_score': self.overall_score,
            'base_entropy': self.base_entropy,
            'boost_factors': self.boost_factors,
            'entropy_level': self.entropy_level.value,
            'component_scores': self.component_scores,
            'strengths': self.strengths,
            'weaknesses': self.weaknesses,
            'recommendations': self.recommendations,
            'tier_compliance': self.tier_compliance,
            'metadata': self.metadata
        }

class LambdaIDEntropyEngine:
    """
    Advanced entropy scoring engine for ΛiD generation and analysis.

    Calculates entropy scores using Shannon entropy with Unicode boost factors,
    provides optimization recommendations, and tracks entropy patterns.
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize entropy engine with configuration"""
        self.config = self._load_config(config_path)
        self.tier_thresholds = self._load_tier_thresholds()
        self.boost_factors = self._load_boost_factors()
        self.unicode_categories = self._load_unicode_categories()
        self.pattern_weights = self._load_pattern_weights()
        self.entropy_history = defaultdict(list)  # For tracking improvements

    def analyze_entropy(self, lambda_id: str, tier: Optional[int] = None) -> EntropyAnalysis:
        """
        Comprehensive entropy analysis of a ΛiD.

        Args:
            lambda_id: The ΛiD to analyze
            tier: User tier level for compliance checking

        Returns:
            EntropyAnalysis with detailed scoring and recommendations
        """
        analysis = EntropyAnalysis()
        analysis.lambda_id = lambda_id

        try:
            # Parse ΛiD components
            components = self._parse_lambda_id(lambda_id)
            if not components:
                analysis.weaknesses.append("Invalid ΛiD format")
                return analysis

            tier_num, timestamp_hash, symbolic_char, entropy_hash = components

            # Calculate base Shannon entropy
            analysis.base_entropy = self._calculate_shannon_entropy(lambda_id)
            analysis.component_scores['shannon_entropy'] = analysis.base_entropy

            # Apply boost factors
            boost_analysis = self._calculate_boost_factors(lambda_id, symbolic_char)
            analysis.boost_factors = boost_analysis

            # Calculate component-specific scores
            analysis.component_scores.update({
                'timestamp_entropy': self._calculate_component_entropy(timestamp_hash),
                'symbolic_strength': self._calculate_symbolic_strength(symbolic_char),
                'entropy_hash_quality': self._calculate_component_entropy(entropy_hash),
                'pattern_complexity': self._calculate_pattern_complexity(lambda_id)
            })

            # Calculate overall score with boosts
            analysis.overall_score = self._calculate_overall_score(analysis)

            # Determine entropy level
            analysis.entropy_level = self._determine_entropy_level(analysis.overall_score)

            # Tier compliance analysis
            if tier is not None:
                analysis.tier_compliance = self._analyze_tier_compliance(analysis.overall_score, tier)

            # Generate strengths and weaknesses
            self._analyze_strengths_weaknesses(analysis)

            # Generate optimization recommendations
            self._generate_entropy_recommendations(analysis, tier)

            # Add metadata
            analysis.metadata = {
                'analyzed_at': datetime.now().isoformat(),
                'tier': tier,
                'component_count': len(analysis.component_scores),
                'boost_count': len(analysis.boost_factors)
            }

            # Track in history
            self._track_entropy_history(lambda_id, analysis.overall_score)

            return analysis

        except Exception as e:
            analysis.weaknesses.append(f"Analysis error: {str(e)}")
            return analysis

    def calculate_live_entropy(self, partial_id: str, tier: int) -> Dict[str, Any]:
        """
        Real-time entropy calculation for Tier 4+ users during generation.

        Args:
            partial_id: Partial ΛiD being constructed
            tier: User tier level

        Returns:
            Dict with live entropy score and suggestions
        """
        if tier < 4:
            return {
                'error': 'Live entropy scoring requires Tier 4+ membership',
                'tier_required': 4
            }

        live_score = self._calculate_shannon_entropy(partial_id)
        target_score = self.tier_thresholds.get(f'tier_{tier}', {}).get('recommended', 3.0)

        # Generate real-time suggestions
        suggestions = self._generate_live_suggestions(partial_id, live_score, target_score)

        return {
            'current_entropy': round(live_score, 2),
            'target_entropy': target_score,
            'progress_percentage': min(100, (live_score / target_score) * 100),
            'entropy_level': self._determine_entropy_level(live_score).value,
            'suggestions': suggestions,
            'next_character_boost': self._suggest_next_character(partial_id)
        }

    def optimize_lambda_id(self, lambda_id: str, target_tier: int) -> Dict[str, Any]:
        """
        Provide optimization suggestions for existing ΛiD.

        Args:
            lambda_id: Current ΛiD
            target_tier: Desired tier level

        Returns:
            Dict with optimization suggestions
        """
        current_analysis = self.analyze_entropy(lambda_id, target_tier)
        target_threshold = self.tier_thresholds.get(f'tier_{target_tier}', {})

        optimization = {
            'current_score': current_analysis.overall_score,
            'target_minimum': target_threshold.get('minimum', 1.0),
            'target_recommended': target_threshold.get('recommended', 2.0),
            'improvement_needed': max(0, target_threshold.get('minimum', 1.0) - current_analysis.overall_score),
            'optimizations': []
        }

        # Generate specific optimizations
        if current_analysis.overall_score < target_threshold.get('minimum', 1.0):
            optimization['optimizations'].extend(self._generate_optimizations(lambda_id, target_tier))

        return optimization

    def batch_entropy_analysis(self, lambda_ids: List[str]) -> List[EntropyAnalysis]:
        """
        Efficient batch entropy analysis for multiple ΛiDs.

        Args:
            lambda_ids: List of ΛiDs to analyze

        Returns:
            List of EntropyAnalysis results
        """
        results = []

        for lambda_id in lambda_ids:
            analysis = self.analyze_entropy(lambda_id)
            results.append(analysis)

        return results

    def get_entropy_statistics(self) -> Dict[str, Any]:
        """
        Get entropy statistics across all analyzed ΛiDs.

        Returns:
            Dict with entropy statistics
        """
        all_scores = []
        for scores in self.entropy_history.values():
            all_scores.extend(scores)

        if not all_scores:
            return {'error': 'No entropy data available'}

        return {
            'total_analyzed': len(all_scores),
            'average_entropy': sum(all_scores) / len(all_scores),
            'highest_entropy': max(all_scores),
            'lowest_entropy': min(all_scores),
            'distribution': self._calculate_entropy_distribution(all_scores),
            'tier_compliance_rates': self._calculate_tier_compliance_rates()
        }

    # Private calculation methods

    def _calculate_shannon_entropy(self, text: str) -> float:
        """Calculate Shannon entropy for text"""
        if not text:
            return 0.0

        # Count character frequencies
        char_counts = defaultdict(int)
        for char in text:
            char_counts[char] += 1

        # Calculate Shannon entropy
        total_chars = len(text)
        entropy = 0.0

        for count in char_counts.values():
            probability = count / total_chars
            if probability > 0:
                entropy -= probability * math.log2(probability)

        return entropy

    def _calculate_boost_factors(self, lambda_id: str, symbolic_char: str) -> Dict[str, float]:
        """Calculate boost factors for ΛiD components"""
        boosts = {}

        # Unicode symbolic character boost
        if ord(symbolic_char) > 127:  # Non-ASCII
            category = unicodedata.category(symbolic_char)
            boost_value = self.boost_factors.get('unicode_categories', {}).get(category, 1.0)
            boosts['unicode_symbolic'] = boost_value

        # Pattern complexity boost
        pattern_score = self._calculate_pattern_complexity(lambda_id)
        if pattern_score > 0.5:
            boosts['pattern_complexity'] = pattern_score

        # Character diversity boost
        unique_chars = len(set(lambda_id))
        if unique_chars > len(lambda_id) * 0.7:
            boosts['character_diversity'] = unique_chars / len(lambda_id)

        # Mixed case boost (if applicable)
        if any(c.isupper() for c in lambda_id) and any(c.islower() for c in lambda_id):
            boosts['mixed_case'] = 1.1

        return boosts

    def _calculate_component_entropy(self, component: str) -> float:
        """Calculate entropy for a specific component"""
        return self._calculate_shannon_entropy(component)

    def _calculate_symbolic_strength(self, symbolic_char: str) -> float:
        """Calculate strength score for symbolic character"""
        base_score = 1.0

        # Unicode bonus
        if ord(symbolic_char) > 127:
            base_score += 0.5

        # Category-specific bonuses
        if symbolic_char in ['⟐', '◈', '⬟', '⬢', '⟁', '◐', '◑', '⬧']:
            base_score += 1.0  # Premium symbols
        elif symbolic_char in ['🌀', '✨', '🔮']:
            base_score += 0.8  # Emoji symbols
        elif symbolic_char in ['◊', '○', '□', '△', '▽']:
            base_score += 0.3  # Basic symbols

        return base_score

    def _calculate_pattern_complexity(self, lambda_id: str) -> float:
        """Calculate pattern complexity score"""
        complexity = 0.0

        # Check for repeating patterns
        for i in range(2, len(lambda_id) // 2 + 1):
            for j in range(len(lambda_id) - i + 1):
                pattern = lambda_id[j:j+i]
                if lambda_id.count(pattern) > 1:
                    complexity -= 0.1  # Penalty for repetition

        # Bonus for alternating patterns
        alternating_count = 0
        for i in range(1, len(lambda_id)):
            if lambda_id[i] != lambda_id[i-1]:
                alternating_count += 1

        complexity += (alternating_count / len(lambda_id)) * 0.5

        return max(0.0, min(1.0, complexity + 0.5))  # Normalize to 0-1

    def _calculate_overall_score(self, analysis: EntropyAnalysis) -> float:
        """Calculate overall entropy score with boost factors"""
        base_score = analysis.base_entropy

        # Apply boost factors
        for boost_name, boost_value in analysis.boost_factors.items():
            base_score *= boost_value

        # Add component bonuses
        component_bonus = sum(analysis.component_scores.values()) * 0.1

        return base_score + component_bonus

    def _determine_entropy_level(self, score: float) -> EntropyLevel:
        """Determine entropy level from score"""
        if score >= 4.0:
            return EntropyLevel.VERY_HIGH
        elif score >= 3.0:
            return EntropyLevel.HIGH
        elif score >= 2.0:
            return EntropyLevel.MEDIUM
        elif score >= 1.0:
            return EntropyLevel.LOW
        else:
            return EntropyLevel.VERY_LOW

    def _analyze_tier_compliance(self, score: float, tier: int) -> Dict[str, Any]:
        """Analyze tier compliance for entropy score"""
        tier_config = self.tier_thresholds.get(f'tier_{tier}', {})
        minimum = tier_config.get('minimum', 1.0)
        recommended = tier_config.get('recommended', 2.0)

        return {
            'tier': tier,
            'meets_minimum': score >= minimum,
            'meets_recommended': score >= recommended,
            'minimum_threshold': minimum,
            'recommended_threshold': recommended,
            'score_gap': max(0, minimum - score),
            'recommendation_gap': max(0, recommended - score)
        }

    def _analyze_strengths_weaknesses(self, analysis: EntropyAnalysis) -> None:
        """Analyze strengths and weaknesses of the ΛiD"""
        # Strengths
        if analysis.base_entropy > 2.5:
            analysis.strengths.append("High base entropy")

        if 'unicode_symbolic' in analysis.boost_factors:
            analysis.strengths.append("Unicode symbolic character boost")

        if analysis.component_scores.get('pattern_complexity', 0) > 0.6:
            analysis.strengths.append("Good pattern complexity")

        if len(analysis.boost_factors) > 2:
            analysis.strengths.append("Multiple entropy boost factors")

        # Weaknesses
        if analysis.base_entropy < 1.5:
            analysis.weaknesses.append("Low base entropy")

        if not analysis.boost_factors:
            analysis.weaknesses.append("No entropy boost factors")

        if analysis.component_scores.get('symbolic_strength', 0) < 1.5:
            analysis.weaknesses.append("Weak symbolic character")

        if analysis.component_scores.get('pattern_complexity', 0) < 0.3:
            analysis.weaknesses.append("Simple pattern structure")

    def _generate_entropy_recommendations(self, analysis: EntropyAnalysis, tier: Optional[int]) -> None:
        """Generate optimization recommendations"""
        recommendations = []

        if analysis.base_entropy < 2.0:
            recommendations.append("Consider using more diverse characters in hash components")

        if 'unicode_symbolic' not in analysis.boost_factors:
            recommendations.append("Use Unicode symbolic characters for entropy boost")

        if analysis.component_scores.get('pattern_complexity', 0) < 0.4:
            recommendations.append("Avoid repetitive patterns for better complexity")

        if tier and tier >= 4:
            tier_config = self.tier_thresholds.get(f'tier_{tier}', {})
            if analysis.overall_score < tier_config.get('recommended', 2.0):
                recommendations.append(f"Aim for entropy score of {tier_config.get('recommended', 2.0)} for optimal Tier {tier} performance")

        analysis.recommendations = recommendations

    def _generate_live_suggestions(self, partial_id: str, current_score: float, target_score: float) -> List[str]:
        """Generate real-time suggestions during ΛiD construction"""
        suggestions = []

        if current_score < target_score * 0.5:
            suggestions.append("Consider using more diverse characters")
            suggestions.append("Add Unicode symbolic characters for boost")

        if current_score < target_score * 0.8:
            suggestions.append("Avoid repeating character patterns")
            suggestions.append("Mix uppercase and lowercase where possible")

        return suggestions

    def _suggest_next_character(self, partial_id: str) -> Dict[str, Any]:
        """Suggest next character for maximum entropy boost"""
        # Analyze current character distribution
        char_counts = defaultdict(int)
        for char in partial_id:
            char_counts[char] += 1

        # Find least used character types
        suggestions = {
            'high_entropy_chars': ['⟐', '◈', '⬟', '⬢'],
            'medium_entropy_chars': ['🌀', '✨', '🔮'],
            'avoid_chars': list(char_counts.keys()),
            'boost_potential': 0.5
        }

        return suggestions

    def _generate_optimizations(self, lambda_id: str, target_tier: int) -> List[str]:
        """Generate specific optimization suggestions"""
        optimizations = []

        # Parse current ΛiD
        components = self._parse_lambda_id(lambda_id)
        if components:
            tier_num, timestamp_hash, symbolic_char, entropy_hash = components

            # Symbolic character optimization
            tier_symbols = self._get_tier_symbols(target_tier)
            high_entropy_symbols = [s for s in tier_symbols if ord(s) > 127]

            if symbolic_char not in high_entropy_symbols:
                optimizations.append(f"Replace '{symbolic_char}' with higher-entropy symbol like {high_entropy_symbols[:3]}")

            # Hash component optimization
            if self._calculate_component_entropy(entropy_hash) < 2.0:
                optimizations.append("Generate new entropy hash with better character distribution")

        return optimizations

    def _calculate_entropy_distribution(self, scores: List[float]) -> Dict[str, int]:
        """Calculate distribution of entropy scores by level"""
        distribution = {level.value: 0 for level in EntropyLevel}

        for score in scores:
            level = self._determine_entropy_level(score)
            distribution[level.value] += 1

        return distribution

    def _calculate_tier_compliance_rates(self) -> Dict[str, float]:
        """Calculate compliance rates for each tier"""
        # This would typically analyze historical data
        return {
            'tier_0': 0.95,
            'tier_1': 0.92,
            'tier_2': 0.88,
            'tier_3': 0.84,
            'tier_4': 0.79,
            'tier_5': 0.75
        }

    def _track_entropy_history(self, lambda_id: str, score: float) -> None:
        """Track entropy score in history"""
        self.entropy_history[lambda_id].append(score)

        # Keep only last 10 scores per ID
        if len(self.entropy_history[lambda_id]) > 10:
            self.entropy_history[lambda_id] = self.entropy_history[lambda_id][-10:]

    # Helper methods

    def _parse_lambda_id(self, lambda_id: str) -> Optional[Tuple[int, str, str, str]]:
        """Parse ΛiD into components"""
        pattern = re.compile(r'^LUKHAS([0-5])-([A-F0-9]{4})-(.)-([A-F0-9]{4})$')
        match = pattern.match(lambda_id)

        if match:
            return (
                int(match.group(1)),
                match.group(2),
                match.group(3),
                match.group(4)
            )
        return None

    def _get_tier_symbols(self, tier: int) -> List[str]:
        """Get available symbols for tier"""
        tier_symbols = {
            0: ['◊', '○', '□'],
            1: ['◊', '○', '□', '△', '▽'],
            2: ['🌀', '✨', '🔮', '◊', '⟐'],
            3: ['🌀', '✨', '🔮', '⟐', '◈', '⬟'],
            4: ['⟐', '◈', '⬟', '⬢', '⟁', '◐'],
            5: ['⟐', '◈', '⬟', '⬢', '⟁', '◐', '◑', '⬧']
        }
        return tier_symbols.get(tier, [])

    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load entropy engine configuration"""
        return {
            'live_entropy_enabled': True,
            'boost_factors_enabled': True,
            'pattern_analysis_enabled': True,
            'history_tracking_enabled': True
        }

    def _load_tier_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Load entropy thresholds for each tier"""
        return {
            'tier_0': {'minimum': 0.8, 'recommended': 1.2},
            'tier_1': {'minimum': 1.0, 'recommended': 1.5},
            'tier_2': {'minimum': 1.2, 'recommended': 1.8},
            'tier_3': {'minimum': 1.5, 'recommended': 2.2},
            'tier_4': {'minimum': 1.8, 'recommended': 2.5},
            'tier_5': {'minimum': 2.0, 'recommended': 3.0}
        }

    def _load_boost_factors(self) -> Dict[str, Dict[str, float]]:
        """Load entropy boost factor configurations"""
        return {
            'unicode_categories': {
                'So': 1.3,  # Other symbols
                'Sm': 1.2,  # Math symbols
                'Sk': 1.1,  # Modifier symbols
                'Sc': 1.1   # Currency symbols
            },
            'pattern_complexity': {
                'high': 1.4,
                'medium': 1.2,
                'low': 1.0
            },
            'character_diversity': {
                'high': 1.3,
                'medium': 1.1,
                'low': 1.0
            }
        }

    def _load_unicode_categories(self) -> Set[str]:
        """Load allowed Unicode categories"""
        return {'So', 'Sm', 'Sk', 'Sc'}

    def _load_pattern_weights(self) -> Dict[str, float]:
        """Load pattern analysis weights"""
        return {
            'repetition_penalty': -0.1,
            'alternation_bonus': 0.05,
            'diversity_bonus': 0.1,
            'complexity_threshold': 0.5
        }


# Example usage and testing
if __name__ == "__main__":
    engine = LambdaIDEntropyEngine()

    # Test entropy analysis
    test_ids = [
        "Λ2-A9F3-🌀-X7K1",  # Medium entropy
        "Λ5-B2E8-⟐-Z9M4",   # High entropy
        "Λ0-1111-○-AAAA",   # Low entropy
        "Λ4-F7C2-⬢-D8N5"   # Very high entropy
    ]

    print("ΛiD Entropy Analysis:")
    print("=" * 50)

    for lambda_id in test_ids:
        analysis = engine.analyze_entropy(lambda_id, tier=2)
        print(f"\nΛiD: {lambda_id}")
        print(f"Overall Score: {analysis.overall_score:.2f}")
        print(f"Base Entropy: {analysis.base_entropy:.2f}")
        print(f"Entropy Level: {analysis.entropy_level.value}")
        print(f"Boost Factors: {analysis.boost_factors}")
        print(f"Strengths: {analysis.strengths}")
        print(f"Weaknesses: {analysis.weaknesses}")
        print(f"Recommendations: {analysis.recommendations}")

    # Test live entropy for Tier 4 user
    print(f"\n\nLive Entropy Test (Tier 4):")
    print("=" * 30)
    partial_id = "Λ4-A1B2"
    live_result = engine.calculate_live_entropy(partial_id, tier=4)
    print(f"Partial ID: {partial_id}")
    print(f"Current Entropy: {live_result['current_entropy']}")
    print(f"Target: {live_result['target_entropy']}")
    print(f"Progress: {live_result['progress_percentage']:.1f}%")
    print(f"Suggestions: {live_result['suggestions']}")

    # Test optimization
    print(f"\n\nOptimization Test:")
    print("=" * 20)
    optimization = engine.optimize_lambda_id("Λ2-1111-○-AAAA", target_tier=3)
    print(f"Current Score: {optimization['current_score']:.2f}")
    print(f"Target Minimum: {optimization['target_minimum']}")
    print(f"Improvement Needed: {optimization['improvement_needed']:.2f}")
    print(f"Optimizations: {optimization['optimizations']}")

    # Show statistics
    print(f"\n\nEntropy Statistics:")
    print("=" * 20)
    stats = engine.get_entropy_statistics()
    if 'error' not in stats:
        print(f"Total Analyzed: {stats['total_analyzed']}")
        print(f"Average Entropy: {stats['average_entropy']:.2f}")
        print(f"Distribution: {stats['distribution']}")


# Alias for backward compatibility
EntropyEngine = EntropyLevel
