"""
Entropy Calculation Helpers
===========================

Advanced entropy calculation utilities for ΛiD generation,
security validation, and randomness assessment.

Features:
- Shannon entropy calculation
- Pattern analysis
- Randomness validation
- Security strength assessment
"""

import math
import secrets
from collections import Counter
from typing import List, Dict

class EntropyCalculator:
    """Calculate various entropy metrics"""

    def __init__(self):
        self.min_entropy_threshold = 3.0

    def shannon_entropy(self, data: str) -> float:
        """Calculate Shannon entropy of data"""
        if not data:
            return 0.0

        # Count character frequencies
        char_counts = Counter(data)
        data_len = len(data)

        # Calculate Shannon entropy
        entropy = 0.0
        for count in char_counts.values():
            probability = count / data_len
            if probability > 0:
                entropy -= probability * math.log2(probability)

        return entropy

    def pattern_entropy(self, data: str, pattern_length: int = 2) -> float:
        """Calculate entropy based on pattern analysis"""
        # ΛTAG: entropy_pattern_analysis
        if not data or pattern_length <= 0:
            return 0.0

        patterns = [data[i:i + pattern_length]
                    for i in range(len(data) - pattern_length + 1)]
        if not patterns:
            return 0.0

        counts = Counter(patterns)
        total = len(patterns)
        entropy = 0.0
        for count in counts.values():
            p = count / total
            entropy -= p * math.log2(p)
        return entropy

    def validate_randomness(self, data: str) -> Dict[str, float]:
        """Validate randomness of data using multiple metrics"""
        # ΛTAG: entropy_randomness_validation
        shannon = self.shannon_entropy(data)
        pattern = self.pattern_entropy(data)
        randomness_score = (shannon + pattern) / 2
        return {
            "shannon_entropy": shannon,
            "pattern_entropy": pattern,
            "randomness_score": randomness_score,
            "is_random": randomness_score >= self.min_entropy_threshold
        }

class SecureRandomGenerator:
    """Generate cryptographically secure random data"""

    def __init__(self, entropy_source=None):
        self.entropy_source = entropy_source or secrets

    def generate_secure_bytes(self, length: int) -> bytes:
        """Generate secure random bytes"""
        return self.entropy_source.token_bytes(length)

    def generate_secure_string(self, length: int, charset: str = None) -> str:
        """Generate secure random string"""
        if charset is None:
            charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

        return ''.join(self.entropy_source.choice(charset) for _ in range(length))

    def assess_entropy_strength(self, data: str) -> str:
        """Assess the entropy strength of generated data"""
        entropy = EntropyCalculator().shannon_entropy(data)

        if entropy >= 4.0:
            return "excellent"
        elif entropy >= 3.5:
            return "good"
        elif entropy >= 3.0:
            return "adequate"
        else:
            return "insufficient"
