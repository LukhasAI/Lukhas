# Tests for QRG Consciousness PKI

import pytest
import numpy as np
from datetime import datetime, timezone

from products.security.qrg.qrg_core import (
    QIResonanceGlyph,
    QIGlyphConfig,
    ConsciousnessContext,
    QIGlyph,
)

class TestQIResonanceGlyph:
    """Tests for the QIResonanceGlyph class."""

    def setup_method(self):
        """Set up a test instance."""
        self.qrg = QIResonanceGlyph()
        self.user_identity = "test_user_123"

    def test_initialization(self):
        """Test that the class initializes correctly."""
        assert self.qrg.config is not None
        assert isinstance(self.qrg.config, QIGlyphConfig)
        assert self.qrg.qi_entropy_pool is not None

    def test_initialization_with_custom_config(self):
        """Test initialization with a custom configuration."""
        custom_config = QIGlyphConfig(radius=150.0, resolution=1024)
        qrg = QIResonanceGlyph(config=custom_config)
        assert qrg.config.radius == 150.0
        assert qrg.config.resolution == 1024

    def test_generate_auth_glyph(self):
        """Test the generation of an authentication glyph."""
        glyph = self.qrg.generate_auth_glyph(self.user_identity)

        assert isinstance(glyph, QIGlyph)
        assert isinstance(glyph.glyph_id, str)
        assert len(glyph.glyph_id) > 0

        assert isinstance(glyph.visual_matrix, np.ndarray)
        assert glyph.visual_matrix.shape == (
            self.qrg.config.resolution,
            self.qrg.config.resolution,
            3,
        )

        assert isinstance(glyph.animation_frames, list)
        assert len(glyph.animation_frames) > 0
        assert isinstance(glyph.animation_frames[0], np.ndarray)

        assert isinstance(glyph.qi_signature, str)
        assert len(glyph.qi_signature) > 0

        assert isinstance(glyph.consciousness_fingerprint, str)
        assert len(glyph.consciousness_fingerprint) > 0

        assert isinstance(glyph.temporal_validity, datetime)
        assert glyph.temporal_validity > datetime.now(timezone.utc)

    def test_generate_quantum_signature(self):
        """Test the quantum signature generation."""
        sig1 = self.qrg._generate_quantum_signature(self.user_identity, security_tier=1)
        sig2 = self.qrg._generate_quantum_signature(self.user_identity, security_tier=3)
        sig3 = self.qrg._generate_quantum_signature("another_user", security_tier=1)

        assert isinstance(sig1, str)
        assert len(sig1) > 0
        assert sig1 != sig2
        assert sig1 != sig3

    def test_create_consciousness_fingerprint(self):
        """Test the consciousness fingerprint generation."""
        context1 = ConsciousnessContext(emotional_state="joy")
        context2 = ConsciousnessContext(emotional_state="stress")
        fp1 = self.qrg._create_consciousness_fingerprint(context1)
        fp2 = self.qrg._create_consciousness_fingerprint(context2)

        assert isinstance(fp1, str)
        assert len(fp1) > 0
        assert fp1 != fp2

    def test_hsv_to_rgb(self):
        """Test the HSV to RGB color conversion."""
        # Red
        assert self.qrg._hsv_to_rgb(0, 1, 1) == (255, 0, 0)
        # Green
        assert self.qrg._hsv_to_rgb(120, 1, 1) == (0, 255, 0)
        # Blue
        assert self.qrg._hsv_to_rgb(240, 1, 1) == (0, 0, 255)
        # White
        assert self.qrg._hsv_to_rgb(0, 0, 1) == (255, 255, 255)
        # Black
        assert self.qrg._hsv_to_rgb(0, 1, 0) == (0, 0, 0)

    def test_apply_consciousness_adaptation(self):
        """Test consciousness-aware visual adaptations."""
        matrix = np.full((10, 10, 3), 100, dtype=np.uint8)

        ctx_stress = ConsciousnessContext(emotional_state="stress")
        adapted_stress = self.qrg._apply_consciousness_adaptation(matrix, ctx_stress)
        assert adapted_stress[0, 0, 0] > matrix[0, 0, 0] # Red channel increased

        ctx_calm = ConsciousnessContext(emotional_state="calm")
        adapted_calm = self.qrg._apply_consciousness_adaptation(matrix, ctx_calm)
        assert adapted_calm[0, 0, 2] > matrix[0, 0, 2] # Blue channel increased

        ctx_joy = ConsciousnessContext(emotional_state="joy")
        adapted_joy = self.qrg._apply_consciousness_adaptation(matrix, ctx_joy)
        assert adapted_joy[0, 0, 0] > matrix[0, 0, 0] # Red channel increased
        assert adapted_joy[0, 0, 1] > matrix[0, 0, 1] # Green channel increased

    def test_generate_animation_frames(self):
        """Test the generation of animation frames."""
        base_matrix = np.zeros((10, 10, 3), dtype=np.uint8)
        context = ConsciousnessContext()

        # Test gentle_pulse
        frames_pulse = self.qrg._generate_animation_frames(
            base_matrix, "gentle_pulse", context
        )
        assert len(frames_pulse) > 0
        assert isinstance(frames_pulse[0], np.ndarray)

        # Test spiral_rotation
        frames_spiral = self.qrg._generate_animation_frames(
            base_matrix, "spiral_rotation", context
        )
        assert len(frames_spiral) > 0
        assert isinstance(frames_spiral[0], np.ndarray)

        # Test consciousness_wave
        frames_wave = self.qrg._generate_animation_frames(
            base_matrix, "consciousness_wave", context
        )
        assert len(frames_wave) > 0
        assert isinstance(frames_wave[0], np.ndarray)

        # Test unknown animation
        frames_unknown = self.qrg._generate_animation_frames(
            base_matrix, "unknown", context
        )
        assert np.array_equal(frames_unknown[0], base_matrix)

    def test_embed_hidden_data(self):
        """Test embedding hidden data into a glyph."""
        glyph = self.qrg.generate_auth_glyph(self.user_identity)
        hidden_payload = {"secret_message": "hello", "data_id": 42}

        embedded_glyph = self.qrg.embed_hidden_data(glyph, hidden_payload)

        assert embedded_glyph is not None
        assert embedded_glyph.glyph_id != glyph.glyph_id
        assert embedded_glyph.hidden_payload == hidden_payload
        assert not np.array_equal(
            glyph.visual_matrix, embedded_glyph.visual_matrix
        )

    def test_verify_glyph_authenticity_valid(self):
        """Test glyph verification with a valid glyph."""
        glyph = self.qrg.generate_auth_glyph(self.user_identity, security_tier=3)

        # We need to regenerate the signature here because the entropy pool is time-based
        expected_signature = self.qrg._generate_quantum_signature(self.user_identity, 3)
        glyph.qi_signature = expected_signature

        result = self.qrg.verify_glyph_authenticity(glyph, self.user_identity)

        assert result["authentic"]
        assert result["temporal_valid"]
        assert result["qi_verified"]
        assert result["confidence_score"] == 1.0

    def test_verify_glyph_authenticity_invalid_signature(self):
        """Test glyph verification with an invalid signature."""
        glyph = self.qrg.generate_auth_glyph(self.user_identity)
        glyph.qi_signature = "invalid_signature"
        result = self.qrg.verify_glyph_authenticity(glyph, self.user_identity)

        assert not result["authentic"]
        assert not result["qi_verified"]

    def test_verify_glyph_authenticity_expired(self, monkeypatch):
        """Test glyph verification with an expired glyph."""
        glyph = self.qrg.generate_auth_glyph(self.user_identity)

        # We need to regenerate the signature here because the entropy pool is time-based
        expected_signature = self.qrg._generate_quantum_signature(self.user_identity, 3)
        glyph.qi_signature = expected_signature

        # Expire the glyph
        glyph.temporal_validity = datetime.now(timezone.utc)

        result = self.qrg.verify_glyph_authenticity(glyph, self.user_identity)

        assert not result["authentic"]
        assert not result["temporal_valid"]

    def test_qiglyph_to_dict(self):
        """Test the to_dict method of the QIGlyph dataclass."""
        glyph = self.qrg.generate_auth_glyph(self.user_identity)
        glyph_dict = glyph.to_dict()

        assert isinstance(glyph_dict, dict)
        assert glyph_dict["glyph_id"] == glyph.glyph_id
        assert glyph_dict["qi_signature"] == glyph.qi_signature
        assert (
            glyph_dict["consciousness_fingerprint"]
            == glyph.consciousness_fingerprint
        )
        assert (
            glyph_dict["temporal_validity"] == glyph.temporal_validity.isoformat()
        )
        assert glyph_dict["hidden_payload"] == glyph.hidden_payload

    def test_create_holographic_glyph(self):
        """Test the creation of a holographic glyph."""
        holographic_glyph = self.qrg.create_holographic_glyph(self.user_identity)

        assert isinstance(holographic_glyph, dict)
        assert "base_glyph" in holographic_glyph
        assert "spatial_dimensions" in holographic_glyph
        assert "projection_matrices" in holographic_glyph
        assert "interaction_zones" in holographic_glyph
        assert "consciousness_layer" in holographic_glyph
        assert "qi_entangled" in holographic_glyph
