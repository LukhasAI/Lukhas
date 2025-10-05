"""
Tests for noise injection system.
Validates noise injection clamping and safety guarantees.
"""
import os
from unittest.mock import patch

from lukhas.consciousness.dream.expand.noise import get_noise_config, inject_noise, validate_noise_output


class TestNoiseInjection:
    """Test noise injection functionality."""

    def test_disabled_by_default(self):
        """Test that noise injection is disabled by default."""
        emotion = {"confidence": 0.5, "joy": 0.8, "fear": 0.2}
        result = inject_noise(emotion)

        assert result == emotion
        assert get_noise_config()["enabled"] is False

    @patch.dict(os.environ, {"LUKHAS_NOISE_LEVEL": "low"})
    def test_low_noise_enabled(self):
        """Test noise injection with low intensity."""
        emotion = {"confidence": 0.5, "joy": 0.8, "fear": 0.2}

        # Run multiple times to check variation
        results = []
        for _ in range(10):
            result = inject_noise(emotion)
            results.append(result)

        # Should have some variation
        assert not all(r == emotion for r in results)

        # All results should be valid
        for result in results:
            assert validate_noise_output(emotion, result)

    @patch.dict(os.environ, {"LUKHAS_NOISE_LEVEL": "high"})
    def test_high_noise_clamping(self):
        """Test that high noise still clamps values properly."""
        # Edge case: emotion at boundary
        emotion = {"confidence": 1.0, "joy": 0.0, "fear": 0.5}

        for _ in range(20):  # Multiple trials for statistical confidence
            result = inject_noise(emotion)

            # Values must stay in [0,1] range
            for key, value in result.items():
                assert 0.0 <= value <= 1.0, f"{key}={value} outside valid range"

            assert validate_noise_output(emotion, result)

    @patch.dict(os.environ, {"LUKHAS_NOISE_LEVEL": "med"})
    def test_noise_intensity_scaling(self):
        """Test that noise intensity scales appropriately."""
        emotion = {"confidence": 0.5, "joy": 0.5, "fear": 0.5}

        deviations = []
        for _ in range(50):
            result = inject_noise(emotion)
            deviation = abs(result["confidence"] - emotion["confidence"])
            deviations.append(deviation)

        max_deviation = max(deviations)
        avg_deviation = sum(deviations) / len(deviations)

        # Should have meaningful noise but within intensity bounds
        assert max_deviation <= 0.15 + 0.01  # Medium intensity + small epsilon
        assert avg_deviation > 0.01  # Should have some noticeable effect

    def test_noise_validation(self):
        """Test noise output validation logic."""
        original = {"confidence": 0.5, "joy": 0.8}

        # Valid noisy output
        valid_noisy = {"confidence": 0.55, "joy": 0.75}
        assert validate_noise_output(original, valid_noisy)

        # Invalid: out of range
        invalid_range = {"confidence": 1.5, "joy": 0.8}
        assert not validate_noise_output(original, invalid_range)

        # Invalid: different keys
        invalid_keys = {"confidence": 0.5, "anger": 0.3}
        assert not validate_noise_output(original, invalid_keys)

    @patch.dict(os.environ, {"LUKHAS_NOISE_LEVEL": "off"})
    def test_explicit_disable(self):
        """Test explicit disabling works."""
        emotion = {"confidence": 0.5, "joy": 0.8}
        result = inject_noise(emotion)

        assert result == emotion
        assert get_noise_config()["enabled"] is False

    def test_config_reporting(self):
        """Test configuration reporting."""
        with patch.dict(os.environ, {"LUKHAS_NOISE_LEVEL": "low"}):
            config = get_noise_config()
            assert config["level"] == "low"
            assert config["intensity"] == 0.05
            assert config["enabled"] is True

    def test_empty_emotion_handling(self):
        """Test handling of empty emotion dictionaries."""
        assert inject_noise({}) == {}

        # Should still validate properly
        assert validate_noise_output({}, {})

    @patch.dict(os.environ, {"LUKHAS_NOISE_LEVEL": "invalid"})
    def test_invalid_noise_level(self):
        """Test handling of invalid noise level settings."""
        emotion = {"confidence": 0.5}
        result = inject_noise(emotion)

        # Should default to disabled for invalid settings
        assert result == emotion
        assert get_noise_config()["intensity"] == 0.0
