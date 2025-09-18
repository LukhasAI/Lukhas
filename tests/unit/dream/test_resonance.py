"""
Tests for dream resonance field.
Validates decay behavior and safety constraints.
"""
import os
from unittest.mock import patch

from candidate.consciousness.dream.expand.resonance import (
    ResonanceField, create_resonance_field, get_resonance_config, simulate_resonance_decay
)

class TestResonanceField:
    """Test resonance field functionality."""

    def test_disabled_by_default(self):
        """Test that resonance is disabled by default."""
        field = ResonanceField()
        emotion = {"confidence": 0.5, "joy": 0.8}

        result = field.apply(emotion)
        assert result == emotion  # Should be unchanged

        config = get_resonance_config()
        assert config["enabled"] is False

    @patch.dict(os.environ, {"LUKHAS_DREAM_RESONANCE": "1", "LUKHAS_RESONANCE_DECAY": "0.8"})
    def test_resonance_enabled(self):
        """Test resonance field when enabled."""
        field = ResonanceField()

        # First application - should be unchanged
        emotion1 = {"confidence": 0.5, "joy": 0.8, "fear": 0.2}
        result1 = field.apply(emotion1)
        assert result1 == emotion1

        # Second application - should blend with previous
        emotion2 = {"confidence": 0.9, "joy": 0.2, "fear": 0.6}
        result2 = field.apply(emotion2)

        # Result should be blend of emotion1 and emotion2
        assert result2 != emotion2
        assert field.validate_resonance(emotion2, result2)

        # Values should be between previous and current
        assert emotion1["confidence"] <= result2["confidence"] <= emotion2["confidence"]

    @patch.dict(os.environ, {"LUKHAS_DREAM_RESONANCE": "1", "LUKHAS_RESONANCE_DECAY": "0.9"})
    def test_decay_factor_behavior(self):
        """Test that decay factor affects blending properly."""
        field = ResonanceField()

        emotion1 = {"confidence": 1.0, "joy": 0.0}
        field.apply(emotion1)

        emotion2 = {"confidence": 0.0, "joy": 1.0}
        result = field.apply(emotion2)

        # With decay=0.9, result should be 0.9*previous + 0.1*current
        expected_confidence = 0.9 * 1.0 + 0.1 * 0.0  # = 0.9
        expected_joy = 0.9 * 0.0 + 0.1 * 1.0  # = 0.1

        assert abs(result["confidence"] - expected_confidence) < 0.001
        assert abs(result["joy"] - expected_joy) < 0.001

    @patch.dict(os.environ, {"LUKHAS_DREAM_RESONANCE": "1"})
    def test_value_clamping(self):
        """Test that resonance maintains [0,1] value range."""
        field = ResonanceField()

        # Start with extreme values
        emotion1 = {"confidence": 1.0, "joy": 0.0}
        field.apply(emotion1)

        # Apply many iterations to test clamping
        current_emotion = {"confidence": 0.0, "joy": 1.0}
        for _ in range(100):
            result = field.apply(current_emotion)

            # Values must always be in valid range
            for key, value in result.items():
                assert 0.0 <= value <= 1.0

            current_emotion = result

    def test_reset_functionality(self):
        """Test resonance field reset."""
        field = ResonanceField()

        emotion = {"confidence": 0.5}
        field.apply(emotion)

        assert field.get_state()["has_previous"] is True

        field.reset()
        state = field.get_state()
        assert state["has_previous"] is False
        assert state["history_length"] == 0

    @patch.dict(os.environ, {"LUKHAS_DREAM_RESONANCE": "1"})
    def test_history_tracking(self):
        """Test that resonance field tracks history properly."""
        field = ResonanceField()

        emotions = [
            {"confidence": 0.5, "joy": 0.5},
            {"confidence": 0.8, "joy": 0.2},
            {"confidence": 0.3, "joy": 0.9}
        ]

        for emotion in emotions:
            field.apply(emotion)

        state = field.get_state()
        assert state["history_length"] == len(emotions)

    def test_state_reporting(self):
        """Test state reporting functionality."""
        field = ResonanceField()

        initial_state = field.get_state()
        assert "enabled" in initial_state
        assert "decay_factor" in initial_state
        assert "has_previous" in initial_state

        emotion = {"confidence": 0.5}
        field.apply(emotion)

        updated_state = field.get_state()
        assert updated_state["last_vector"] == emotion

    @patch.dict(os.environ, {"LUKHAS_DREAM_RESONANCE": "1"})
    def test_validation_logic(self):
        """Test resonance validation logic."""
        field = ResonanceField()

        original = {"confidence": 0.5, "joy": 0.8}
        field.apply(original)  # Set up previous vector

        # Valid resonance should pass validation
        next_emotion = {"confidence": 0.7, "joy": 0.6}
        result = field.apply(next_emotion)
        assert field.validate_resonance(next_emotion, result)

        # Test with manually constructed invalid result
        invalid_result = {"confidence": 1.5, "joy": 0.5}  # Out of range
        assert not field.validate_resonance(next_emotion, invalid_result)

    def test_factory_function(self):
        """Test resonance field factory function."""
        field = create_resonance_field()
        assert isinstance(field, ResonanceField)

    @patch.dict(os.environ, {"LUKHAS_DREAM_RESONANCE": "1", "LUKHAS_RESONANCE_DECAY": "0.5"})
    def test_decay_simulation(self):
        """Test decay simulation functionality."""
        # Test with resonance enabled
        decay_values = simulate_resonance_decay(1.0, 5)

        assert len(decay_values) == 5
        assert decay_values[0] == 1.0  # Initial value

        # Each step should decay by factor of 0.5
        for i in range(1, len(decay_values)):
            expected = decay_values[i-1] * 0.5
            assert abs(decay_values[i] - expected) < 0.001

    def test_decay_simulation_disabled(self):
        """Test decay simulation when disabled."""
        # Default disabled state
        decay_values = simulate_resonance_decay(1.0, 5)

        # Should return constant values when disabled
        assert all(v == 1.0 for v in decay_values)

    @patch.dict(os.environ, {"LUKHAS_RESONANCE_DECAY": "0.95"})
    def test_config_validation(self):
        """Test configuration validation."""
        config = get_resonance_config()

        assert config["decay_factor"] == 0.95
        assert config["safe_range"] is True  # 0.95 is in safe range [0.1, 0.99]

    @patch.dict(os.environ, {"LUKHAS_RESONANCE_DECAY": "1.5"})
    def test_unsafe_decay_detection(self):
        """Test detection of unsafe decay factor."""
        config = get_resonance_config()

        # Decay factor outside safe range should be detected
        assert config["safe_range"] is False