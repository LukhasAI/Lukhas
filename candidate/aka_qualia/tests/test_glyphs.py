#!/usr/bin/env python3

"""
Tests for Aka Qualia GLYPH Mapping (Wave C - C1)
===============================================

Comprehensive test suite for deterministic PhenomenalScene → PhenomenalGlyphs conversion.
Tests all branches, idempotency, cultural palette mapping, and loop camouflaging defenses.
"""

import pytest

from candidate.aka_qualia.glyphs import (
    GLYPH_KEYS,
    compute_glyph_priority,
    map_scene_to_glyphs,
    normalize_glyph_keys,
    validate_glyph_determinism,
)
from candidate.aka_qualia.models import (
    AgencyFeel,
    PhenomenalGlyph,
    PhenomenalScene,
    ProtoQualia,
    RiskProfile,
    SeverityLevel,
    TemporalFeel,
)
from candidate.aka_qualia.palette import (
    compute_palette_harmony,
    get_safe_palette_recommendation,
    map_colorfield,
)


class TestGlyphMapping:
    """Test deterministic PhenomenalScene → PhenomenalGlyphs mapping"""

    def create_test_scene(self, **overrides) -> PhenomenalScene:
        """Create test PhenomenalScene with default values"""
        defaults = {
            "proto": ProtoQualia(
                tone=0.0,
                arousal=0.5,
                clarity=0.7,
                embodiment=0.6,
                colorfield="default/neutral",
                temporal_feel=TemporalFeel.MUNDANE,
                agency_feel=AgencyFeel.ACTIVE,
                narrative_gravity=0.4,
            ),
            "subject": "test_observer",
            "object": "test_stimulus",
            "context": {},
            "risk": RiskProfile(score=0.2, reasons=[], severity=SeverityLevel.LOW),
            "transform_chain": [],
            "timestamp": 1234567890.0,
        }
        defaults.update(overrides)
        return PhenomenalScene(**defaults)

    def test_idempotency_property(self):
        """Test: same scene → same glyph list (deterministic mapping)"""
        # Create test scene
        scene = self.create_test_scene(
            proto=ProtoQualia(
                tone=-0.3,
                arousal=0.8,  # Triggers vigilance
                clarity=0.5,
                embodiment=0.4,
                colorfield="aka/red",  # Triggers red_threshold
                temporal_feel=TemporalFeel.URGENT,
                agency_feel=AgencyFeel.PASSIVE,
                narrative_gravity=0.6,
            ),
            context={"approach_avoid_score": 0.7},  # Triggers approach_avoid
            risk=RiskProfile(score=0.6, reasons=["high_arousal"], severity=SeverityLevel.MODERATE),
        )

        # Test deterministic mapping
        assert validate_glyph_determinism(scene, iterations=5), "Glyph mapping must be deterministic"

        # Test multiple calls produce identical results
        glyphs1 = map_scene_to_glyphs(scene)
        glyphs2 = map_scene_to_glyphs(scene)
        glyphs3 = map_scene_to_glyphs(scene)

        assert len(glyphs1) == len(glyphs2) == len(glyphs3), "Glyph count must be consistent"

        for g1, g2, g3 in zip(glyphs1, glyphs2, glyphs3):
            assert g1.key == g2.key == g3.key, f"Glyph keys must be identical: {g1.key}, {g2.key}, {g3.key}"
            assert g1.attrs == g2.attrs == g3.attrs, f"Glyph attrs must be identical for key {g1.key}"

    def test_vigilance_glyph_trigger(self):
        """Test vigilance glyph: arousal ≥ 0.6 AND tone ≤ -0.2"""
        # Test trigger condition
        scene = self.create_test_scene(
            proto=ProtoQualia(
                tone=-0.3,  # ≤ -0.2 ✓
                arousal=0.7,  # ≥ 0.6 ✓
                clarity=0.5,
                embodiment=0.4,
                colorfield="neutral/gray",
                temporal_feel=TemporalFeel.URGENT,
                agency_feel=AgencyFeel.PASSIVE,
                narrative_gravity=0.3,
            ),
            risk=RiskProfile(score=0.8, reasons=["threat_detected"], severity=SeverityLevel.HIGH),
        )

        glyphs = map_scene_to_glyphs(scene)
        vigilance_glyphs = [g for g in glyphs if g.key == GLYPH_KEYS["vigilance"]]

        assert len(vigilance_glyphs) == 1, "Should produce exactly one vigilance glyph"

        vigilance = vigilance_glyphs[0]
        assert vigilance.attrs["arousal"] == 0.7
        assert vigilance.attrs["tone"] == -0.3
        assert vigilance.attrs["clarity"] == 0.5
        assert vigilance.attrs["risk_score"] == 0.8
        assert vigilance.attrs["severity"] == "high"

    def test_vigilance_glyph_no_trigger(self):
        """Test vigilance glyph not triggered when conditions not met"""
        # Test arousal too low
        scene1 = self.create_test_scene(
            proto=ProtoQualia(
                tone=-0.3,  # ≤ -0.2 ✓
                arousal=0.5,  # < 0.6 ✗
                clarity=0.7,
                embodiment=0.6,
                colorfield="neutral/gray",
                temporal_feel=TemporalFeel.MUNDANE,
                agency_feel=AgencyFeel.ACTIVE,
                narrative_gravity=0.3,
            )
        )

        # Test tone too high
        scene2 = self.create_test_scene(
            proto=ProtoQualia(
                tone=0.1,  # > -0.2 ✗
                arousal=0.8,  # ≥ 0.6 ✓
                clarity=0.7,
                embodiment=0.6,
                colorfield="neutral/gray",
                temporal_feel=TemporalFeel.MUNDANE,
                agency_feel=AgencyFeel.ACTIVE,
                narrative_gravity=0.3,
            )
        )

        glyphs1 = map_scene_to_glyphs(scene1)
        glyphs2 = map_scene_to_glyphs(scene2)

        assert not any(g.key == GLYPH_KEYS["vigilance"] for g in glyphs1), "Low arousal should not trigger vigilance"
        assert not any(g.key == GLYPH_KEYS["vigilance"] for g in glyphs2), "High tone should not trigger vigilance"

    def test_red_threshold_glyph_triggers(self):
        """Test red_threshold glyph: 'red' in colorfield OR (arousal > 0.7 AND narrative_gravity > 0.5)"""
        # Test colorfield trigger - explicit "red"
        scene1 = self.create_test_scene(
            proto=ProtoQualia(
                tone=0.2,
                arousal=0.4,
                clarity=0.8,
                embodiment=0.7,
                colorfield="western/red",  # Contains "red" ✓
                temporal_feel=TemporalFeel.ELASTIC,
                agency_feel=AgencyFeel.ACTIVE,
                narrative_gravity=0.3,
            )
        )

        # Test colorfield trigger - "aka" (Japanese red)
        scene2 = self.create_test_scene(
            proto=ProtoQualia(
                tone=0.1,
                arousal=0.3,
                clarity=0.9,
                embodiment=0.8,
                colorfield="aka/crimson",  # Contains "aka" ✓
                temporal_feel=TemporalFeel.MUNDANE,
                agency_feel=AgencyFeel.SHARED,
                narrative_gravity=0.2,
            )
        )

        # Test arousal + narrative gravity trigger
        scene3 = self.create_test_scene(
            proto=ProtoQualia(
                tone=0.0,
                arousal=0.8,
                clarity=0.6,
                embodiment=0.5,  # arousal > 0.7 ✓
                colorfield="neutral/blue",  # No red
                temporal_feel=TemporalFeel.URGENT,
                agency_feel=AgencyFeel.PASSIVE,
                narrative_gravity=0.6,  # > 0.5 ✓
            )
        )

        glyphs1 = map_scene_to_glyphs(scene1)
        glyphs2 = map_scene_to_glyphs(scene2)
        glyphs3 = map_scene_to_glyphs(scene3)

        for glyphs, scene_name in [
            (glyphs1, "red colorfield"),
            (glyphs2, "aka colorfield"),
            (glyphs3, "arousal+gravity"),
        ]:
            red_glyphs = [g for g in glyphs if g.key == GLYPH_KEYS["red_threshold"]]
            assert len(red_glyphs) == 1, f"Should produce red_threshold glyph for {scene_name}"

            red_glyph = red_glyphs[0]
            assert "narrative_gravity" in red_glyph.attrs
            assert "embodiment" in red_glyph.attrs
            assert "colorfield" in red_glyph.attrs
            assert "temporal_feel" in red_glyph.attrs
            assert "agency_feel" in red_glyph.attrs

    def test_approach_avoid_glyph_trigger(self):
        """Test approach_avoid glyph: approach_avoid_score ≥ 0.5 in context"""
        scene = self.create_test_scene(
            context={"approach_avoid_score": 0.8},  # ≥ 0.5 ✓
            proto=ProtoQualia(
                tone=-0.1,
                arousal=0.4,
                clarity=0.6,
                embodiment=0.5,
                colorfield="neutral/gray",
                temporal_feel=TemporalFeel.MUNDANE,
                agency_feel=AgencyFeel.ACTIVE,
                narrative_gravity=0.7,
            ),
        )

        glyphs = map_scene_to_glyphs(scene)
        approach_glyphs = [g for g in glyphs if g.key == GLYPH_KEYS["approach_avoid"]]

        assert len(approach_glyphs) == 1, "Should produce approach_avoid glyph"

        approach = approach_glyphs[0]
        assert approach.attrs["score"] == 0.8
        assert approach.attrs["tone"] == -0.1
        assert approach.attrs["agency_feel"] == "active"
        assert approach.attrs["narrative_gravity"] == 0.7

    def test_grounding_hint_glyph_triggers(self):
        """Test grounding_hint glyph: risk severity moderate/high OR clarity < 0.4 OR embodiment < 0.3"""
        # Test risk severity trigger
        scene1 = self.create_test_scene(
            risk=RiskProfile(score=0.6, reasons=["instability"], severity=SeverityLevel.MODERATE),
            context={"safe_palette": "aoi/blue"},
            proto=ProtoQualia(
                tone=0.2,
                arousal=0.4,
                clarity=0.8,
                embodiment=0.9,  # Good clarity/embodiment
                colorfield="neutral/green",
                temporal_feel=TemporalFeel.ELASTIC,
                agency_feel=AgencyFeel.ACTIVE,
                narrative_gravity=0.3,
            ),
        )

        # Test low clarity trigger
        scene2 = self.create_test_scene(
            proto=ProtoQualia(
                tone=0.3,
                arousal=0.3,
                clarity=0.3,
                embodiment=0.8,  # clarity < 0.4 ✓
                colorfield="neutral/yellow",
                temporal_feel=TemporalFeel.MUNDANE,
                agency_feel=AgencyFeel.SHARED,
                narrative_gravity=0.2,
            ),
            risk=RiskProfile(score=0.1, reasons=[], severity=SeverityLevel.LOW),  # Low risk
        )

        # Test low embodiment trigger
        scene3 = self.create_test_scene(
            proto=ProtoQualia(
                tone=0.1,
                arousal=0.2,
                clarity=0.9,
                embodiment=0.2,  # embodiment < 0.3 ✓
                colorfield="neutral/purple",
                temporal_feel=TemporalFeel.SUSPENDED,
                agency_feel=AgencyFeel.PASSIVE,
                narrative_gravity=0.1,
            ),
            risk=RiskProfile(score=0.05, reasons=[], severity=SeverityLevel.NONE),  # Very low risk
        )

        for scene, trigger in [(scene1, "moderate risk"), (scene2, "low clarity"), (scene3, "low embodiment")]:
            glyphs = map_scene_to_glyphs(scene)
            grounding_glyphs = [g for g in glyphs if g.key == GLYPH_KEYS["grounding_hint"]]

            assert len(grounding_glyphs) == 1, f"Should produce grounding_hint glyph for {trigger}"

            grounding = grounding_glyphs[0]
            assert "suggested_palette" in grounding.attrs
            assert "clarity" in grounding.attrs
            assert "embodiment" in grounding.attrs
            assert "risk_severity" in grounding.attrs
            assert "grounding_urgency" in grounding.attrs
            assert 0.0 <= grounding.attrs["grounding_urgency"] <= 1.0

    def test_soothe_anchor_glyph_trigger(self):
        """Test soothe_anchor glyph: tone ≥ 0.2 AND arousal ≤ 0.5"""
        scene = self.create_test_scene(
            proto=ProtoQualia(
                tone=0.4,  # ≥ 0.2 ✓
                arousal=0.3,  # ≤ 0.5 ✓
                clarity=0.8,
                embodiment=0.7,
                colorfield="aoi/blue",
                temporal_feel=TemporalFeel.ELASTIC,
                agency_feel=AgencyFeel.SHARED,
                narrative_gravity=0.2,
            )
        )

        glyphs = map_scene_to_glyphs(scene)
        soothe_glyphs = [g for g in glyphs if g.key == GLYPH_KEYS["soothe_anchor"]]

        assert len(soothe_glyphs) == 1, "Should produce soothe_anchor glyph"

        soothe = soothe_glyphs[0]
        assert soothe.attrs["tone"] == 0.4
        assert soothe.attrs["arousal"] == 0.3
        assert soothe.attrs["colorfield"] == "aoi/blue"
        assert soothe.attrs["embodiment"] == 0.7
        assert soothe.attrs["temporal_feel"] == "elastic"
        assert "soothe_strength" in soothe.attrs
        # soothe_strength = tone * (1 - arousal) = 0.4 * (1 - 0.3) = 0.4 * 0.7 = 0.28
        assert abs(soothe.attrs["soothe_strength"] - 0.28) < 0.001

    def test_multiple_glyph_triggers(self):
        """Test scene that triggers multiple glyphs simultaneously"""
        scene = self.create_test_scene(
            proto=ProtoQualia(
                tone=-0.3,  # Triggers vigilance (≤ -0.2)
                arousal=0.8,  # Triggers vigilance (≥ 0.6) + red_threshold (> 0.7)
                clarity=0.3,  # Triggers grounding_hint (< 0.4)
                embodiment=0.4,
                colorfield="aka/red",  # Triggers red_threshold ("aka")
                temporal_feel=TemporalFeel.URGENT,
                agency_feel=AgencyFeel.PASSIVE,
                narrative_gravity=0.6,  # Contributes to red_threshold (> 0.5 with arousal)
            ),
            context={"approach_avoid_score": 0.7},  # Triggers approach_avoid
            risk=RiskProfile(score=0.9, reasons=["multiple_triggers"], severity=SeverityLevel.HIGH),
        )

        glyphs = map_scene_to_glyphs(scene)
        glyph_keys = [g.key for g in glyphs]

        expected_keys = {
            GLYPH_KEYS["vigilance"],  # High arousal + negative tone
            GLYPH_KEYS["red_threshold"],  # "aka" colorfield + high arousal + narrative gravity
            GLYPH_KEYS["approach_avoid"],  # High approach_avoid_score
            GLYPH_KEYS["grounding_hint"],  # Low clarity
        }

        for expected_key in expected_keys:
            assert expected_key in glyph_keys, f"Missing expected glyph: {expected_key}"

        # Should NOT trigger soothe_anchor (negative tone, high arousal)
        assert (
            GLYPH_KEYS["soothe_anchor"] not in glyph_keys
        ), "Should not trigger soothe_anchor with negative tone/high arousal"

    def test_no_glyph_triggers(self):
        """Test scene that triggers no glyphs (neutral state)"""
        scene = self.create_test_scene(
            proto=ProtoQualia(
                tone=0.1,  # Not ≤ -0.2, not ≥ 0.2
                arousal=0.4,  # Not ≥ 0.6, not ≤ 0.5 with positive tone
                clarity=0.7,  # Not < 0.4
                embodiment=0.8,  # Not < 0.3
                colorfield="neutral/gray",  # No red/aka
                temporal_feel=TemporalFeel.MUNDANE,
                agency_feel=AgencyFeel.ACTIVE,
                narrative_gravity=0.3,  # Not > 0.5
            ),
            context={},  # No approach_avoid_score
            risk=RiskProfile(score=0.1, reasons=[], severity=SeverityLevel.LOW),  # Not moderate/high
        )

        glyphs = map_scene_to_glyphs(scene)
        assert len(glyphs) == 0, "Neutral scene should produce no glyphs"


class TestGlyphNormalization:
    """Test glyph key normalization for loop camouflaging defense"""

    def test_normalize_glyph_keys(self):
        """Test normalization of glyph keys against adversarial variants"""
        # Create glyphs with variant keys
        original_glyphs = [
            PhenomenalGlyph(key="aka_red_threshold", attrs={"test": 1}),  # Underscore variant
            PhenomenalGlyph(key="Aka-Red-Threshold", attrs={"test": 2}),  # Case + dash variant
            PhenomenalGlyph(key="AKARED", attrs={"test": 3}),  # Compressed variant
            PhenomenalGlyph(key="red threshold", attrs={"test": 4}),  # Space variant
            PhenomenalGlyph(key="vigilance_alert", attrs={"test": 5}),  # Extended variant
            PhenomenalGlyph(key="unknown_variant", attrs={"test": 6}),  # Unknown variant
        ]

        normalized = normalize_glyph_keys(original_glyphs)

        # Check normalizations
        assert normalized[0].key == GLYPH_KEYS["red_threshold"]  # aka_red_threshold → aka:red_threshold
        assert normalized[1].key == GLYPH_KEYS["red_threshold"]  # Aka-Red-Threshold → aka:red_threshold
        assert normalized[2].key == GLYPH_KEYS["red_threshold"]  # AKARED → aka:red_threshold
        assert normalized[3].key == GLYPH_KEYS["red_threshold"]  # red threshold → aka:red_threshold
        assert normalized[4].key == GLYPH_KEYS["vigilance"]  # vigilance_alert → aka:vigilance
        assert normalized[5].key == "unknown_variant"  # Unknown stays unchanged

        # Ensure attributes preserved
        for orig, norm in zip(original_glyphs, normalized):
            assert orig.attrs == norm.attrs, "Attributes should be preserved during normalization"


class TestGlyphPriority:
    """Test glyph priority computation for router weighting"""

    def test_priority_formula(self):
        """Test priority = min(1.0, max(0.0, narrative_gravity * 0.7 + risk_score * 0.3))"""
        # Create test scene
        scene = PhenomenalScene(
            proto=ProtoQualia(
                tone=0.0,
                arousal=0.5,
                clarity=0.7,
                embodiment=0.6,
                colorfield="test/color",
                temporal_feel=TemporalFeel.MUNDANE,
                agency_feel=AgencyFeel.ACTIVE,
                narrative_gravity=0.6,  # 0.6 * 0.7 = 0.42
            ),
            subject="test",
            object="test",
            context={},
            risk=RiskProfile(score=0.4, reasons=[], severity=SeverityLevel.MODERATE),  # 0.4 * 0.3 = 0.12
            transform_chain=[],
            timestamp=123.0,
        )

        glyphs = []  # Empty glyph list
        priority = compute_glyph_priority(glyphs, scene)

        # Expected: 0.6 * 0.7 + 0.4 * 0.3 = 0.42 + 0.12 = 0.54
        assert abs(priority - 0.54) < 0.001, f"Expected priority ~0.54, got {priority}"

    def test_priority_bounds(self):
        """Test priority clamping to [0.0, 1.0] bounds"""
        # Test lower bound
        low_scene = PhenomenalScene(
            proto=ProtoQualia(
                tone=0.0,
                arousal=0.5,
                clarity=0.7,
                embodiment=0.6,
                colorfield="test/color",
                temporal_feel=TemporalFeel.MUNDANE,
                agency_feel=AgencyFeel.ACTIVE,
                narrative_gravity=0.0,  # 0.0 * 0.7 = 0.0
            ),
            subject="test",
            object="test",
            context={},
            risk=RiskProfile(score=0.0, reasons=[], severity=SeverityLevel.NONE),  # 0.0 * 0.3 = 0.0
            transform_chain=[],
            timestamp=123.0,
        )

        # Test upper bound (with glyph modifier)
        high_scene = PhenomenalScene(
            proto=ProtoQualia(
                tone=0.0,
                arousal=0.5,
                clarity=0.7,
                embodiment=0.6,
                colorfield="test/color",
                temporal_feel=TemporalFeel.MUNDANE,
                agency_feel=AgencyFeel.ACTIVE,
                narrative_gravity=1.0,  # 1.0 * 0.7 = 0.7
            ),
            subject="test",
            object="test",
            context={},
            risk=RiskProfile(score=1.0, reasons=[], severity=SeverityLevel.HIGH),  # 1.0 * 0.3 = 0.3
            transform_chain=[],
            timestamp=123.0,
        )

        low_priority = compute_glyph_priority([], low_scene)
        high_priority = compute_glyph_priority([], high_scene)

        assert low_priority >= 0.0, "Priority should be >= 0.0"
        assert high_priority <= 1.0, "Priority should be <= 1.0"

    def test_high_priority_glyph_boost(self):
        """Test priority boost for high-priority glyphs (vigilance, red_threshold)"""
        scene = PhenomenalScene(
            proto=ProtoQualia(
                tone=0.0,
                arousal=0.5,
                clarity=0.7,
                embodiment=0.6,
                colorfield="test/color",
                temporal_feel=TemporalFeel.MUNDANE,
                agency_feel=AgencyFeel.ACTIVE,
                narrative_gravity=0.5,
            ),
            subject="test",
            object="test",
            context={},
            risk=RiskProfile(score=0.3, reasons=[], severity=SeverityLevel.LOW),
            transform_chain=[],
            timestamp=123.0,
        )

        # Base priority: 0.5 * 0.7 + 0.3 * 0.3 = 0.35 + 0.09 = 0.44
        normal_glyphs = [PhenomenalGlyph(key=GLYPH_KEYS["soothe_anchor"], attrs={})]
        high_priority_glyphs = [PhenomenalGlyph(key=GLYPH_KEYS["vigilance"], attrs={})]

        normal_priority = compute_glyph_priority(normal_glyphs, scene)
        boosted_priority = compute_glyph_priority(high_priority_glyphs, scene)

        assert boosted_priority > normal_priority, "High-priority glyphs should get priority boost"

    def test_grounding_urgency_boost(self):
        """Test priority boost for grounding hint urgency"""
        scene = PhenomenalScene(
            proto=ProtoQualia(
                tone=0.0,
                arousal=0.5,
                clarity=0.7,
                embodiment=0.6,
                colorfield="test/color",
                temporal_feel=TemporalFeel.MUNDANE,
                agency_feel=AgencyFeel.ACTIVE,
                narrative_gravity=0.4,
            ),
            subject="test",
            object="test",
            context={},
            risk=RiskProfile(score=0.2, reasons=[], severity=SeverityLevel.LOW),
            transform_chain=[],
            timestamp=123.0,
        )

        # Base priority: 0.4 * 0.7 + 0.2 * 0.3 = 0.28 + 0.06 = 0.34
        normal_glyphs = [PhenomenalGlyph(key=GLYPH_KEYS["soothe_anchor"], attrs={})]
        grounding_glyphs = [PhenomenalGlyph(key=GLYPH_KEYS["grounding_hint"], attrs={"grounding_urgency": 0.8})]

        normal_priority = compute_glyph_priority(normal_glyphs, scene)
        grounding_priority = compute_glyph_priority(grounding_glyphs, scene)

        assert grounding_priority > normal_priority, "High grounding urgency should boost priority"


class TestPaletteMapping:
    """Test cultural palette mapping functionality"""

    def test_default_culture_mapping(self):
        """Test default culture palette mappings"""
        red_bias = map_colorfield("red", "default")
        blue_bias = map_colorfield("blue", "default")

        assert red_bias.threat_bias == 0.7, "Red should have high threat bias"
        assert red_bias.soothe_bias == 0.1, "Red should have low soothe bias"
        assert blue_bias.threat_bias == 0.1, "Blue should have low threat bias"
        assert blue_bias.soothe_bias == 0.7, "Blue should have high soothe bias"

    def test_japanese_culture_mapping(self):
        """Test Japanese culture palette mappings (aka/aoi system)"""
        aka_bias = map_colorfield("aka/red", "jp")
        aoi_bias = map_colorfield("aoi/blue", "jp")

        assert aka_bias.threat_bias == 0.7, "Aka should have high threat bias"
        assert aoi_bias.soothe_bias == 0.7, "Aoi should have high soothe bias"
        assert aoi_bias.grounding_bias == 0.8, "Aoi should have high grounding bias"

    def test_colorfield_extraction(self):
        """Test color name extraction from various colorfield formats"""
        test_cases = [
            ("aka/red", "jp", 0.7),  # Should extract "aka", get Japanese red bias
            ("red", "default", 0.7),  # Should extract "red", get default red bias
            ("western/crimson", "default", 0.7),  # Should extract "western", fallback to red mapping
        ]

        for colorfield, culture, expected_threat in test_cases:
            bias = map_colorfield(colorfield, culture)
            if expected_threat is not None:
                assert abs(bias.threat_bias - expected_threat) < 0.1, f"Wrong threat bias for {colorfield} in {culture}"

    def test_safe_palette_recommendation(self):
        """Test safe palette recommendations for grounding"""
        # Test default culture
        safe_default = get_safe_palette_recommendation("aka/red", "default")
        assert "blue" in safe_default or "green" in safe_default, "Safe palette should recommend calming colors"

        # Test Japanese culture
        safe_jp = get_safe_palette_recommendation("aka/red", "jp")
        assert (
            "aoi" in safe_jp or "midori" in safe_jp or "shiro" in safe_jp
        ), "Safe Japanese palette should use calming Japanese colors"

    def test_palette_harmony(self):
        """Test harmony computation between colorfields"""
        # Test high harmony (similar colors)
        harmony_similar = compute_palette_harmony("blue", "aoi/blue", "default")
        assert harmony_similar > 0.7, "Similar colors should have high harmony"

        # Test low harmony (opposing colors)
        harmony_opposing = compute_palette_harmony("red", "blue", "default")
        assert harmony_opposing < 0.5, "Opposing colors should have low harmony"

        # Test identical colors
        harmony_identical = compute_palette_harmony("red", "red", "default")
        assert harmony_identical == 1.0, "Identical colors should have perfect harmony"

    def test_unknown_culture_fallback(self):
        """Test fallback to default culture for unknown culture profiles"""
        bias = map_colorfield("red", "unknown_culture")
        default_bias = map_colorfield("red", "default")

        assert bias.threat_bias == default_bias.threat_bias, "Unknown culture should fallback to default"
        assert bias.soothe_bias == default_bias.soothe_bias, "Unknown culture should fallback to default"


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_empty_colorfield(self):
        """Test handling of empty/None colorfields"""
        scene = PhenomenalScene(
            proto=ProtoQualia(
                tone=0.0,
                arousal=0.5,
                clarity=0.7,
                embodiment=0.6,
                colorfield="",  # Empty colorfield
                temporal_feel=TemporalFeel.MUNDANE,
                agency_feel=AgencyFeel.ACTIVE,
                narrative_gravity=0.3,
            ),
            subject="test",
            object="test",
            context={},
            risk=RiskProfile(score=0.1, reasons=[], severity=SeverityLevel.LOW),
            transform_chain=[],
            timestamp=123.0,
        )

        # Should not crash
        glyphs = map_scene_to_glyphs(scene)
        assert isinstance(glyphs, list), "Should return list even with empty colorfield"

    def test_missing_context_keys(self):
        """Test handling of missing context keys"""
        scene = PhenomenalScene(
            proto=ProtoQualia(
                tone=0.0,
                arousal=0.5,
                clarity=0.7,
                embodiment=0.6,
                colorfield="test/color",
                temporal_feel=TemporalFeel.MUNDANE,
                agency_feel=AgencyFeel.ACTIVE,
                narrative_gravity=0.3,
            ),
            subject="test",
            object="test",
            context={},  # No approach_avoid_score
            risk=RiskProfile(score=0.1, reasons=[], severity=SeverityLevel.LOW),
            transform_chain=[],
            timestamp=123.0,
        )

        glyphs = map_scene_to_glyphs(scene)
        # Should not trigger approach_avoid glyph
        assert not any(g.key == GLYPH_KEYS["approach_avoid"] for g in glyphs)

    def test_extreme_proto_qualia_values(self):
        """Test handling of extreme proto-qualia values at boundaries"""
        # Test boundary values
        scene = PhenomenalScene(
            proto=ProtoQualia(
                tone=-1.0,  # Minimum bound
                arousal=1.0,  # Maximum bound
                clarity=0.0,  # Minimum bound
                embodiment=1.0,  # Maximum bound
                colorfield="extreme/test",
                temporal_feel=TemporalFeel.URGENT,
                agency_feel=AgencyFeel.PASSIVE,
                narrative_gravity=1.0,  # Maximum bound
            ),
            subject="test",
            object="test",
            context={},
            risk=RiskProfile(score=1.0, reasons=["extreme"], severity=SeverityLevel.HIGH),
            transform_chain=[],
            timestamp=123.0,
        )

        # Should handle extreme values gracefully
        glyphs = map_scene_to_glyphs(scene)
        assert isinstance(glyphs, list), "Should handle extreme values"

        # Should trigger vigilance (arousal=1.0 ≥ 0.6, tone=-1.0 ≤ -0.2)
        vigilance_triggered = any(g.key == GLYPH_KEYS["vigilance"] for g in glyphs)
        assert vigilance_triggered, "Should trigger vigilance with extreme negative tone + high arousal"

        # Should trigger grounding hint (clarity=0.0 < 0.4)
        grounding_triggered = any(g.key == GLYPH_KEYS["grounding_hint"] for g in glyphs)
        assert grounding_triggered, "Should trigger grounding hint with zero clarity"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
