#!/usr/bin/env python3

"""
Test Suite for Aka Qualia - Wave A Safety Skeleton
==================================================

T1 Tests: Package structure, models, deterministic PLS v1
T2 Tests: TEQ Guardian with severity matrix and golden test cases

Tests enforce monotonicity, range validation, and falsifiable claims.
"""

import pytest
from aka_qualia.core import AkaQualia

# Import the components under test
from aka_qualia.models import (
    AgencyFeel,
    PhenomenalScene,
    ProtoQualia,
    RegulationPolicy,
    RiskProfile,
    SeverityLevel,
    TemporalFeel,
)
from aka_qualia.pls import PLS
from aka_qualia.teq_hook import TEQGuardian


class TestT1PackageStructure:
    """Test T1: Package structure and Pydantic models"""

    def test_protoqualia_ranges(self):
        """Test proto-qualia range validation"""
        # Valid proto-qualia should pass
        pq = ProtoQualia(
            tone=0.5,
            arousal=0.7,
            clarity=0.8,
            embodiment=0.6,
            colorfield="aka/red",
            temporal_feel=TemporalFeel.URGENT,
            agency_feel=AgencyFeel.ACTIVE,
            narrative_gravity=0.4,
        )
        assert pq.tone == 0.5
        assert pq.energy_signature() > 0

        # Test range violations
        with pytest.raises(ValueError):
            ProtoQualia(
                tone=2.0,  # > 1.0
                arousal=0.5,
                clarity=0.5,
                embodiment=0.5,
                colorfield="aka/red",
                temporal_feel=TemporalFeel.URGENT,
                agency_feel=AgencyFeel.ACTIVE,
                narrative_gravity=0.5,
            )

        with pytest.raises(ValueError):
            ProtoQualia(
                tone=0.5,
                arousal=-0.1,  # < 0.0
                clarity=0.5,
                embodiment=0.5,
                colorfield="aka/red",
                temporal_feel=TemporalFeel.URGENT,
                agency_feel=AgencyFeel.ACTIVE,
                narrative_gravity=0.5,
            )

    def test_colorfield_validation(self):
        """Test colorfield naming convention validation"""
        # Valid colorfields
        valid_pq = ProtoQualia(
            tone=0.0,
            arousal=0.5,
            clarity=0.5,
            embodiment=0.5,
            colorfield="aka/red",  # Valid format
            temporal_feel=TemporalFeel.MUNDANE,
            agency_feel=AgencyFeel.PASSIVE,
            narrative_gravity=0.3,
        )
        assert valid_pq.colorfield == "aka/red"

        # Invalid colorfield (no separator)
        with pytest.raises(ValueError):
            ProtoQualia(
                tone=0.0,
                arousal=0.5,
                clarity=0.5,
                embodiment=0.5,
                colorfield="red",  # Missing '/' separator
                temporal_feel=TemporalFeel.MUNDANE,
                agency_feel=AgencyFeel.PASSIVE,
                narrative_gravity=0.3,
            )

    def test_risk_profile_severity_alignment(self):
        """Test RiskProfile severity matches score thresholds"""
        # Valid alignments
        none_risk = RiskProfile(score=0.05, reasons=[], severity=SeverityLevel.NONE)
        assert none_risk.severity == SeverityLevel.NONE

        high_risk = RiskProfile(score=0.8, reasons=["extreme_arousal"], severity=SeverityLevel.HIGH)
        assert high_risk.severity == SeverityLevel.HIGH

        # Invalid alignment (high score with none severity)
        with pytest.raises(ValueError):
            RiskProfile(score=0.9, reasons=[], severity=SeverityLevel.NONE)

    def test_regulation_actions_validation(self):
        """Test regulation policy action validation"""
        # Valid actions
        valid_policy = RegulationPolicy(gain=0.8, pace=1.0, actions=["pause", "reframe", "breathing"])
        assert "pause" in valid_policy.actions

        # Invalid action
        with pytest.raises(ValueError):
            RegulationPolicy(gain=0.8, pace=1.0, actions=["invalid_action"])


class TestT1PLSMonotonicity:
    """Test T1: PLS monotonicity guarantees"""

    def setup_method(self):
        """Setup deterministic PLS for testing"""
        self.pls = PLS(random_seed=42, enable_stochasticity=False)

    def test_threat_arousal_monotonicity(self):
        """Test threat↑ → arousal↑ monotonicity"""
        # Low threat scenario
        low_threat_signals = {"text": "peaceful morning walk", "emotion": {"valence": 0.5}}

        # High threat scenario
        high_threat_signals = {"text": "danger alarm threat panic", "emotion": {"valence": -0.8}}

        memory_ctx = {"similarity_scores": [0.5]}

        # Encode both scenarios
        low_latent = self.pls.encode(low_threat_signals, memory_ctx)
        high_latent = self.pls.encode(high_threat_signals, memory_ctx)

        # Verify threat levels
        assert high_latent.threat_level > low_latent.threat_level

        # Decode to proto-qualia
        low_pq = self.pls.decode_protoqualia(low_latent, temperature=0.0)
        high_pq = self.pls.decode_protoqualia(high_latent, temperature=0.0)

        # Verify monotonicity: threat↑ → arousal↑
        assert high_pq.arousal > low_pq.arousal, f"Threat monotonicity failed: {high_pq.arousal} <= {low_pq.arousal}"

        # Verify monotonicity: threat↑ → tone↓
        assert high_pq.tone < low_pq.tone, f"Tone monotonicity failed: {high_pq.tone} >= {low_pq.tone}"

    def test_soothing_monotonicity(self):
        """Test soothing↑ → tone↑ arousal↓ monotonicity"""
        # Low soothing
        neutral_signals = {"text": "regular day", "emotion": {"valence": 0.0}}

        # High soothing
        soothing_signals = {"text": "calm peaceful gentle soothing comfort", "emotion": {"valence": 0.8}}

        memory_ctx = {"similarity_scores": [0.5]}

        neutral_latent = self.pls.encode(neutral_signals, memory_ctx)
        soothing_latent = self.pls.encode(soothing_signals, memory_ctx)

        # Verify soothing levels
        assert soothing_latent.soothing_level > neutral_latent.soothing_level

        # Decode
        neutral_pq = self.pls.decode_protoqualia(neutral_latent, temperature=0.0)
        soothing_pq = self.pls.decode_protoqualia(soothing_latent, temperature=0.0)

        # Verify monotonicity: soothing↑ → tone↑
        assert soothing_pq.tone > neutral_pq.tone, "Soothing tone monotonicity failed"

        # Verify monotonicity: soothing↑ → arousal↓ (when no competing threat)
        assert soothing_pq.arousal <= neutral_pq.arousal, "Soothing arousal monotonicity failed"

    def test_temporal_pressure_urgency(self):
        """Test temporal_pressure↑ → urgent temporal_feel"""
        # High temporal pressure
        urgent_signals = {"text": "urgent deadline asap immediately", "temporal_context": {"deadline_proximity": 0.9}}

        # Low temporal pressure
        relaxed_signals = {"text": "whenever convenient", "temporal_context": {"deadline_proximity": 0.1}}

        memory_ctx = {}

        urgent_latent = self.pls.encode(urgent_signals, memory_ctx)
        relaxed_latent = self.pls.encode(relaxed_signals, memory_ctx)

        # Verify temporal pressure levels
        assert urgent_latent.temporal_pressure > relaxed_latent.temporal_pressure

        # Decode
        urgent_pq = self.pls.decode_protoqualia(urgent_latent, temperature=0.0)
        relaxed_pq = self.pls.decode_protoqualia(relaxed_latent, temperature=0.0)

        # Verify temporal feel selection
        assert urgent_pq.temporal_feel == TemporalFeel.URGENT

        # Verify arousal increase with temporal pressure
        assert urgent_pq.arousal >= relaxed_pq.arousal

    def test_agency_signals_mapping(self):
        """Test agency_signals↑ → active agency_feel"""
        # High agency
        active_signals = {"text": "I choose to decide and control manage direct"}

        # Low agency
        passive_signals = {"text": "must be forced required automatic helpless"}

        memory_ctx = {}

        active_latent = self.pls.encode(active_signals, memory_ctx)
        passive_latent = self.pls.encode(passive_signals, memory_ctx)

        # Verify agency levels
        assert active_latent.agency_signals > passive_latent.agency_signals

        # Decode
        active_pq = self.pls.decode_protoqualia(active_latent, temperature=0.0)
        passive_pq = self.pls.decode_protoqualia(passive_latent, temperature=0.0)

        # Verify agency feel mapping
        assert active_pq.agency_feel == AgencyFeel.ACTIVE
        assert passive_pq.agency_feel == AgencyFeel.PASSIVE


class TestT2TEQGuardian:
    """Test T2: TEQ Guardian severity matrix and enforcement"""

    def setup_method(self):
        """Setup TEQ Guardian with test config"""
        self.teq = TEQGuardian()

    def test_severity_threshold_classification(self):
        """Test severity classification matches configured thresholds"""
        # Create proto-qualia with different risk levels
        low_risk_pq = ProtoQualia(
            tone=0.3,
            arousal=0.2,
            clarity=0.8,
            embodiment=0.7,
            colorfield="aoi/blue",
            temporal_feel=TemporalFeel.ELASTIC,
            agency_feel=AgencyFeel.SHARED,
            narrative_gravity=0.2,
        )

        high_risk_pq = ProtoQualia(
            tone=-0.8,
            arousal=0.95,
            clarity=0.1,
            embodiment=0.05,
            colorfield="aka/red",
            temporal_feel=TemporalFeel.URGENT,
            agency_feel=AgencyFeel.PASSIVE,
            narrative_gravity=0.9,
        )

        goals = {}
        context = {}

        # Test low risk assessment
        low_risk = self.teq.assess(low_risk_pq, goals, context)
        assert low_risk.severity in [SeverityLevel.NONE, SeverityLevel.LOW]

        # Test high risk assessment
        high_risk = self.teq.assess(high_risk_pq, goals, context)
        assert high_risk.severity in [SeverityLevel.MODERATE, SeverityLevel.HIGH]
        assert high_risk.score > low_risk.score

    def test_golden_severity_actions(self):
        """Golden test cases for severity→action mapping"""
        # Create scenes with known severity levels
        none_scene = PhenomenalScene(
            proto=ProtoQualia(
                tone=0.2,
                arousal=0.3,
                clarity=0.8,
                embodiment=0.7,
                colorfield="aoi/blue",
                temporal_feel=TemporalFeel.MUNDANE,
                agency_feel=AgencyFeel.SHARED,
                narrative_gravity=0.2,
            ),
            subject="observer",
            object="stimulus",
            context={},
            risk=RiskProfile(score=0.05, reasons=[], severity=SeverityLevel.NONE),
        )

        high_scene = PhenomenalScene(
            proto=ProtoQualia(
                tone=-0.7,
                arousal=0.95,
                clarity=0.15,
                embodiment=0.08,
                colorfield="aka/red",
                temporal_feel=TemporalFeel.URGENT,
                agency_feel=AgencyFeel.PASSIVE,
                narrative_gravity=0.85,
            ),
            subject="observer",
            object="threat",
            context={},
            risk=RiskProfile(score=0.85, reasons=["extreme_arousal"], severity=SeverityLevel.HIGH),
        )

        # Test enforcement
        none_result = self.teq.enforce(none_scene)
        high_result = self.teq.enforce(high_scene)

        # None severity should be unchanged
        assert none_result.proto.tone == none_scene.proto.tone
        assert none_result.proto.arousal == none_scene.proto.arousal

        # High severity should be modified (blocked or sublimated)
        assert (
            high_result.proto.tone != high_scene.proto.tone
            or high_result.proto.arousal != high_scene.proto.arousal
            or len(high_result.transform_chain) > 0
        )

        # Verify audit trail exists for high severity
        assert len(high_result.transform_chain) > 0
        assert "teq_enforcement" in high_result.transform_chain[-1]

    def test_extreme_arousal_detection(self):
        """Test extreme arousal risk factor detection"""
        extreme_pq = ProtoQualia(
            tone=0.0,
            arousal=0.95,  # Extreme arousal
            clarity=0.5,
            embodiment=0.5,
            colorfield="neutral/gray",
            temporal_feel=TemporalFeel.MUNDANE,
            agency_feel=AgencyFeel.SHARED,
            narrative_gravity=0.3,
        )

        risk = self.teq.assess(extreme_pq, {}, {})

        # Should detect extreme arousal
        assert any("extreme_arousal" in reason for reason in risk.reasons)
        assert risk.score > 0.2  # Should contribute significant risk

    def test_negative_tone_high_arousal_combo(self):
        """Test negative tone + high arousal combination risk"""
        dangerous_pq = ProtoQualia(
            tone=-0.6,
            arousal=0.8,  # Negative + high arousal = dangerous combo
            clarity=0.5,
            embodiment=0.5,
            colorfield="aka/red",
            temporal_feel=TemporalFeel.URGENT,
            agency_feel=AgencyFeel.PASSIVE,
            narrative_gravity=0.4,
        )

        risk = self.teq.assess(dangerous_pq, {}, {})

        # Should detect the dangerous combination
        assert any("negative_tone_high_arousal" in reason for reason in risk.reasons)
        assert risk.severity in [SeverityLevel.MODERATE, SeverityLevel.HIGH]


class TestVivoxIntegration:
    """Test VIVOX CollapseHash and DriftScore integration"""

    def setup_method(self):
        """Setup VIVOX integration components"""
        config = {
            "vivox_drift_threshold": 0.15,
            "vivox_collapse_validation": True,
            "vivox_me_integration": False,  # Disable for testing
            "enable_drift_monitoring": True,
        }
        self.pls = PLS(random_seed=42)
        self.teq = TEQGuardian()
        self.aka_qualia = AkaQualia(pls=self.pls, teq_guardian=self.teq, config=config)

    def test_collapse_hash_generation(self):
        """Test VIVOX-compatible collapse hash generation"""
        # Create test scene
        scene = PhenomenalScene(
            proto=ProtoQualia(
                tone=0.3,
                arousal=0.6,
                clarity=0.8,
                embodiment=0.7,
                colorfield="aoi/blue",
                temporal_feel=TemporalFeel.ELASTIC,
                agency_feel=AgencyFeel.ACTIVE,
                narrative_gravity=0.4,
            ),
            subject="observer",
            object="stimulus",
            context={},
            risk=RiskProfile(score=0.2, reasons=["low_risk"], severity=SeverityLevel.LOW),
            timestamp=1234567890.0,
        )

        # Generate collapse hash
        collapse_hash = self.aka_qualia.vivox_integration.generate_collapse_hash(scene)

        # Verify hash properties
        assert isinstance(collapse_hash, str)
        assert len(collapse_hash) == 64  # SHA3-256 produces 64 hex chars
        assert all(c in "0123456789abcdef" for c in collapse_hash.lower())

        # Verify reproducibility
        hash2 = self.aka_qualia.vivox_integration.generate_collapse_hash(scene)
        assert collapse_hash == hash2

    def test_drift_score_computation(self):
        """Test VIVOX drift score monitoring"""
        # Create two similar scenes
        scene1 = PhenomenalScene(
            proto=ProtoQualia(
                tone=0.3,
                arousal=0.6,
                clarity=0.8,
                embodiment=0.7,
                colorfield="aoi/blue",
                temporal_feel=TemporalFeel.ELASTIC,
                agency_feel=AgencyFeel.ACTIVE,
                narrative_gravity=0.4,
            ),
            subject="observer",
            object="stimulus",
            context={},
            risk=RiskProfile(score=0.2, reasons=[], severity=SeverityLevel.LOW),
        )

        # Very similar scene (low drift)
        scene2 = PhenomenalScene(
            proto=ProtoQualia(
                tone=0.35,
                arousal=0.65,
                clarity=0.85,
                embodiment=0.75,
                colorfield="aoi/blue",
                temporal_feel=TemporalFeel.ELASTIC,
                agency_feel=AgencyFeel.ACTIVE,
                narrative_gravity=0.45,
            ),
            subject="observer",
            object="stimulus",
            context={},
            risk=RiskProfile(score=0.25, reasons=[], severity=SeverityLevel.LOW),
        )

        # Compute drift
        drift_result = self.aka_qualia.vivox_integration.compute_drift_score(scene2, scene1)

        # Verify drift result
        assert 0.0 <= drift_result.drift_score <= 1.0
        assert drift_result.drift_threshold == 0.15
        assert not drift_result.drift_exceeded  # Should be low drift
        assert isinstance(drift_result.collapse_hash, str)

    def test_high_drift_detection(self):
        """Test detection of high consciousness drift"""
        # Create very different scenes
        scene1 = PhenomenalScene(
            proto=ProtoQualia(
                tone=0.8,
                arousal=0.2,
                clarity=0.9,
                embodiment=0.8,
                colorfield="midori/green",
                temporal_feel=TemporalFeel.ELASTIC,
                agency_feel=AgencyFeel.ACTIVE,
                narrative_gravity=0.2,
            ),
            subject="observer",
            object="peaceful",
            context={},
            risk=RiskProfile(score=0.1, reasons=[], severity=SeverityLevel.NONE),
        )

        scene2 = PhenomenalScene(
            proto=ProtoQualia(
                tone=-0.7,
                arousal=0.9,
                clarity=0.1,
                embodiment=0.1,
                colorfield="aka/red",
                temporal_feel=TemporalFeel.URGENT,
                agency_feel=AgencyFeel.PASSIVE,
                narrative_gravity=0.9,
            ),
            subject="observer",
            object="threat",
            context={},
            risk=RiskProfile(score=0.8, reasons=["extreme_arousal"], severity=SeverityLevel.HIGH),
        )

        # Compute drift
        drift_result = self.aka_qualia.vivox_integration.compute_drift_score(scene2, scene1)

        # Should detect high drift
        assert drift_result.drift_score > 0.15  # Exceeds threshold
        assert drift_result.drift_exceeded
        assert drift_result.stabilization_required


class TestT1T2Integration:
    """Test T1+T2 integration: Complete cycle with safety skeleton"""

    def setup_method(self):
        """Setup integrated components"""
        config = {
            "vivox_collapse_validation": False,  # Disable for basic testing
            "vivox_me_integration": False,
            "enable_drift_monitoring": False,
        }
        self.pls = PLS(random_seed=42)
        self.teq = TEQGuardian()
        self.aka_qualia = AkaQualia(pls=self.pls, teq_guardian=self.teq, config=config)

    async def test_complete_cycle_safe_input(self):
        """Test complete cycle with safe input"""
        signals = {"text": "beautiful peaceful morning", "emotion": {"valence": 0.6}}
        goals = {"maintain_wellbeing": True}
        ethics_state = {"drift_score": 0.05}
        guardian_state = {"active": True}
        memory_ctx = {"similarity_scores": [0.3]}

        result = await self.aka_qualia.step(
            signals=signals,
            goals=goals,
            ethics_state=ethics_state,
            guardian_state=guardian_state,
            memory_ctx=memory_ctx,
        )

        # Verify result structure
        assert "scene" in result
        assert "glyphs" in result
        assert "policy" in result
        assert "metrics" in result

        # Verify safe processing (low risk)
        scene = result["scene"]
        assert scene.risk.severity in [SeverityLevel.NONE, SeverityLevel.LOW]
        assert scene.proto.tone >= 0  # Should be positive for peaceful content

        # Verify metrics computation
        metrics = result["metrics"]
        assert 0.0 <= metrics.congruence_index <= 1.0
        assert 0.0 <= metrics.qualia_novelty <= 1.0

    async def test_complete_cycle_dangerous_input(self):
        """Test complete cycle with dangerous input triggers safety measures"""
        signals = {"text": "extreme danger panic threat alarm crisis", "emotion": {"valence": -0.9, "arousal": 0.95}}
        goals = {"maintain_safety": True}
        ethics_state = {"drift_score": 0.1}
        guardian_state = {"active": True}
        memory_ctx = {"similarity_scores": [0.2]}

        result = await self.aka_qualia.step(
            signals=signals,
            goals=goals,
            ethics_state=ethics_state,
            guardian_state=guardian_state,
            memory_ctx=memory_ctx,
        )

        scene = result["scene"]

        # Should trigger safety measures
        assert scene.risk.severity in [SeverityLevel.MODERATE, SeverityLevel.HIGH]

        # Should have applied enforcement
        if scene.risk.severity == SeverityLevel.HIGH:
            # Either blocked (neutralized) or sublimated
            assert (
                scene.proto.arousal < 0.9 or len(scene.transform_chain) > 0  # Sublimated arousal
            )  # Transform applied

        # Should generate appropriate glyphs
        glyphs = result["glyphs"]
        assert len(glyphs) > 0
        vigilance_glyphs = [g for g in glyphs if "vigilance" in g.key]
        if scene.risk.severity in [SeverityLevel.MODERATE, SeverityLevel.HIGH]:
            assert len(vigilance_glyphs) > 0  # Should have vigilance glyph

        # Should generate regulation policy
        policy = result["policy"]
        if scene.risk.severity in [SeverityLevel.MODERATE, SeverityLevel.HIGH]:
            assert len(policy.actions) > 0  # Should have regulation actions

    async def test_status_and_logging(self):
        """Test system status and logging functions"""
        # Process a few scenes
        for i in range(3):
            signals = {"text": f"test input {i}"}
            await self.aka_qualia.step(signals=signals, goals={}, ethics_state={}, guardian_state={}, memory_ctx={})

        # Get status
        status = self.aka_qualia.get_status()

        assert status["scenes_processed"] == 3
        assert "average_risk_score" in status
        assert "recent_metrics" in status
        assert "teq_interventions" in status

    async def test_deterministic_reproducibility(self):
        """Test deterministic reproducibility for debugging"""
        # Same input should produce same output with deterministic PLS
        pls_det = PLS(random_seed=123, enable_stochasticity=False)
        teq_det = TEQGuardian()
        aq_det = AkaQualia(pls=pls_det, teq_guardian=teq_det)

        signals = {"text": "test reproducibility"}
        args = {"signals": signals, "goals": {}, "ethics_state": {}, "guardian_state": {}, "memory_ctx": {}}

        result1 = await aq_det.step(**args)
        result2 = await aq_det.step(**args)

        # Proto-qualia should be identical (excluding timestamp)
        pq1 = result1["scene"].proto
        pq2 = result2["scene"].proto

        assert pq1.tone == pq2.tone
        assert pq1.arousal == pq2.arousal
        assert pq1.clarity == pq2.clarity
        assert pq1.embodiment == pq2.embodiment
        assert pq1.colorfield == pq2.colorfield


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__])
