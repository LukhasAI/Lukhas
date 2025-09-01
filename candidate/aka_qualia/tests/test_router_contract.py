#!/usr/bin/env python3

"""
Router Contract Tests for Aka Qualia (Wave C - C2)
================================================

Contract testing for router client integration and priority weighting validation.
Ensures Freud-2025 Wave C specification compliance for routing integration.

Tests priority monotonicity: higher narrative_gravity ⇒ higher priority
"""

from unittest.mock import Mock, patch

import pytest

from candidate.aka_qualia.glyphs import GLYPH_KEYS, map_scene_to_glyphs
from candidate.aka_qualia.models import AgencyFeel, PhenomenalScene, ProtoQualia, RiskGauge, RiskSeverity, TemporalFeel
from candidate.aka_qualia.router_client import (
    MockRouterClient,
    SymbolicMeshRouterClient,
    compute_routing_priority,
    create_router_client,
)


class TestRouterClientContract:
    """Contract tests for RouterClient protocol implementations"""

    def test_router_client_protocol_compliance(self):
        """Test that all router clients implement RouterClient protocol"""
        # Test SymbolicMeshRouterClient
        symbolic_client = SymbolicMeshRouterClient()
        assert hasattr(symbolic_client, "route")
        assert hasattr(symbolic_client, "get_routing_status")

        # Test MockRouterClient
        mock_client = MockRouterClient()
        assert hasattr(mock_client, "route")
        assert hasattr(mock_client, "get_routing_status")

        # Test factory function
        lukhas_client = create_router_client("lukhas")
        assert hasattr(lukhas_client, "route")
        assert hasattr(lukhas_client, "get_routing_status")

        mock_client_factory = create_router_client("mock")
        assert hasattr(mock_client_factory, "route")
        assert hasattr(mock_client_factory, "get_routing_status")

    def test_mock_router_functionality(self):
        """Test MockRouterClient routing and status functionality"""
        mock_router = MockRouterClient()

        # Create test scene and glyphs
        scene = self._create_test_scene(narrative_gravity=0.8, risk_score=0.6)
        glyphs = map_scene_to_glyphs(scene)

        # Test routing
        mock_router.route(glyphs, 0.7, {"test": "context"})

        # Verify routing was recorded
        assert mock_router.routing_calls == 1
        assert len(mock_router.routed_glyphs) == 1

        routed_glyphs, priority = mock_router.routed_glyphs[0]
        assert priority == 0.7
        assert len(routed_glyphs) == len(glyphs)

        # Test status
        status = mock_router.get_routing_status()
        assert status["router_available"] == True
        assert status["routing_enabled"] == True
        assert status["routes_sent"] == 1
        assert status["routes_failed"] == 0
        assert status["mock_mode"] == True

    @patch("candidate.aka_qualia.router_client.route_signal")
    def test_symbolic_router_with_mock_dependencies(self, mock_route_signal):
        """Test SymbolicMeshRouterClient with mocked LUKHAS dependencies"""
        # Create mock router module
        mock_router_module = Mock()
        mock_router_module.route_signal = mock_route_signal
        mock_router_module.SymbolicSignal = Mock
        mock_router_module.DiagnosticSignalType = Mock()
        mock_router_module.DiagnosticSignalType.PULSE = "PULSE"

        # Create router client with mock module
        router = SymbolicMeshRouterClient(router_module=mock_router_module)

        # Create test glyphs
        scene = self._create_test_scene(narrative_gravity=0.6, risk_score=0.4)
        glyphs = map_scene_to_glyphs(scene)

        # Route glyphs
        router.route(glyphs, 0.5)

        # Verify route_signal was called for each glyph
        assert mock_route_signal.call_count == len(glyphs)

        # Verify statistics updated
        assert router.routes_sent == len(glyphs)
        assert router.routes_failed == 0
        assert router.total_priority_weight == 0.5 * len(glyphs)


class TestPriorityWeightingContract:
    """Contract tests for priority weighting formula (Freud-2025 specification)"""

    def test_priority_formula_correctness(self):
        """Test priority = narrative_gravity * 0.7 + risk_score * 0.3"""
        # Test cases with known values
        test_cases = [
            (1.0, 1.0, 1.0),  # Maximum values
            (0.0, 0.0, 0.0),  # Minimum values
            (0.5, 0.5, 0.5),  # Middle values
            (0.8, 0.2, 0.62),  # High narrative, low risk
            (0.2, 0.8, 0.38),  # Low narrative, high risk
        ]

        for narrative_gravity, risk_score, expected_priority in test_cases:
            scene = self._create_test_scene(narrative_gravity, risk_score)
            computed_priority = compute_routing_priority(scene)

            assert abs(computed_priority - expected_priority) < 0.001, (
                f"Expected {expected_priority}, got {computed_priority} for ng={narrative_gravity}, rs={risk_score}"
            )

    def test_priority_monotonicity_narrative_gravity(self):
        """Test higher narrative_gravity ⇒ higher priority (key Wave C requirement)"""
        risk_score = 0.5  # Fixed risk score
        narrative_gravities = [0.1, 0.3, 0.5, 0.7, 0.9]

        priorities = []
        for ng in narrative_gravities:
            scene = self._create_test_scene(ng, risk_score)
            priority = compute_routing_priority(scene)
            priorities.append(priority)

        # Verify monotonicity: each priority should be >= previous
        for i in range(1, len(priorities)):
            assert priorities[i] >= priorities[i - 1], (
                f"Priority monotonicity violated: {priorities[i]} < {priorities[i - 1]} at index {i}"
            )

    def test_priority_monotonicity_risk_score(self):
        """Test higher risk_score ⇒ higher priority"""
        narrative_gravity = 0.5  # Fixed narrative gravity
        risk_scores = [0.1, 0.3, 0.5, 0.7, 0.9]

        priorities = []
        for rs in risk_scores:
            scene = self._create_test_scene(narrative_gravity, rs)
            priority = compute_routing_priority(scene)
            priorities.append(priority)

        # Verify monotonicity: each priority should be >= previous
        for i in range(1, len(priorities)):
            assert priorities[i] >= priorities[i - 1], (
                f"Risk monotonicity violated: {priorities[i]} < {priorities[i - 1]} at index {i}"
            )

    def test_priority_bounds_enforcement(self):
        """Test priority is clamped to [0.0, 1.0] range"""
        # Test extreme values that could exceed bounds
        extreme_cases = [
            (2.0, 2.0),  # Values > 1.0
            (-1.0, -1.0),  # Negative values
            (0.0, 0.0),  # Minimum valid
            (1.0, 1.0),  # Maximum valid
        ]

        for narrative_gravity, risk_score in extreme_cases:
            scene = self._create_test_scene(narrative_gravity, risk_score)
            priority = compute_routing_priority(scene)

            assert 0.0 <= priority <= 1.0, (
                f"Priority {priority} out of bounds for ng={narrative_gravity}, rs={risk_score}"
            )

    def test_priority_weighting_coefficients(self):
        """Test that narrative_gravity has 0.7 weight and risk_score has 0.3 weight"""
        # Test with only narrative_gravity = 1.0, risk_score = 0.0
        scene1 = self._create_test_scene(1.0, 0.0)
        priority1 = compute_routing_priority(scene1)
        assert abs(priority1 - 0.7) < 0.001, f"Expected 0.7 for pure narrative gravity, got {priority1}"

        # Test with only risk_score = 1.0, narrative_gravity = 0.0
        scene2 = self._create_test_scene(0.0, 1.0)
        priority2 = compute_routing_priority(scene2)
        assert abs(priority2 - 0.3) < 0.001, f"Expected 0.3 for pure risk score, got {priority2}"


class TestGlyphRoutingIntegration:
    """Integration tests for glyph generation + routing"""

    def test_high_priority_glyph_routing(self):
        """Test that high-priority glyphs (vigilance, red_threshold) get routed"""
        mock_router = MockRouterClient()

        # Create high-arousal, negative-tone scene (triggers vigilance glyph)
        scene = self._create_test_scene(
            narrative_gravity=0.8,
            risk_score=0.7,
            arousal=0.8,
            tone=-0.5,
            colorfield="aka/red",  # Triggers red_threshold glyph too
        )

        glyphs = map_scene_to_glyphs(scene)
        priority = compute_routing_priority(scene)

        # Verify high-priority glyphs are generated
        glyph_keys = [g.key for g in glyphs]
        assert GLYPH_KEYS["vigilance"] in glyph_keys
        assert GLYPH_KEYS["red_threshold"] in glyph_keys

        # Verify high priority
        assert priority > 0.7  # Should be high due to narrative_gravity=0.8, risk_score=0.7

        # Route glyphs
        mock_router.route(glyphs, priority)

        # Verify routing occurred
        assert mock_router.routing_calls == 1
        routed_glyphs, routed_priority = mock_router.routed_glyphs[0]
        assert len(routed_glyphs) == len(glyphs)
        assert routed_priority == priority

    def test_low_priority_glyph_filtering(self):
        """Test that low-priority scenes still generate glyphs but with lower routing priority"""
        mock_router = MockRouterClient()

        # Create low-priority scene (positive tone, low arousal)
        scene = self._create_test_scene(
            narrative_gravity=0.2, risk_score=0.1, arousal=0.3, tone=0.5, colorfield="aoi/blue"
        )

        glyphs = map_scene_to_glyphs(scene)
        priority = compute_routing_priority(scene)

        # Verify soothe_anchor glyph is generated (positive tone + low arousal)
        glyph_keys = [g.key for g in glyphs]
        assert GLYPH_KEYS["soothe_anchor"] in glyph_keys

        # Verify low priority
        assert priority < 0.3  # Should be low due to narrative_gravity=0.2, risk_score=0.1

        # Route glyphs
        mock_router.route(glyphs, priority)

        # Verify routing occurred even with low priority
        assert mock_router.routing_calls == 1

    def test_router_client_configuration_compliance(self):
        """Test router client respects configuration settings"""
        # Test with routing disabled
        disabled_config = {"enable_routing": False}
        router = SymbolicMeshRouterClient(config=disabled_config)

        scene = self._create_test_scene(0.8, 0.6)
        glyphs = map_scene_to_glyphs(scene)

        # Should not route when disabled
        with patch.object(router, "route_signal_func") as mock_route:
            router.route(glyphs, 0.7)
            mock_route.assert_not_called()

        # Test with priority threshold
        threshold_config = {"priority_threshold": 0.8}
        router = SymbolicMeshRouterClient(config=threshold_config)

        with patch.object(router, "route_signal_func") as mock_route:
            # Low priority - should not route
            router.route(glyphs, 0.5)
            mock_route.assert_not_called()

            # High priority - should route
            router.route(glyphs, 0.9)
            assert mock_route.call_count == len(glyphs)

    def _create_test_scene(
        self,
        narrative_gravity: float,
        risk_score: float,
        arousal: float = 0.5,
        tone: float = 0.0,
        colorfield: str = "red",
        clarity: float = 0.8,
    ) -> PhenomenalScene:
        """Helper to create test PhenomenalScene with specified parameters"""
        proto = ProtoQualia(
            narrative_gravity=narrative_gravity,
            embodiment=0.7,
            colorfield=colorfield,
            arousal=arousal,
            tone=tone,
            clarity=clarity,
            temporal_feel=TemporalFeel.PRESENT,
            agency_feel=AgencyFeel.EFFORTLESS,
        )

        risk = RiskGauge(score=risk_score, severity=RiskSeverity.MODERATE if risk_score > 0.5 else RiskSeverity.LOW)

        return PhenomenalScene(proto=proto, risk=risk, context={"test_context": True})


class TestSymbolicSignalConversion:
    """Test conversion from PhenomenalGlyphs to LUKHAS SymbolicSignals"""

    @patch("candidate.aka_qualia.router_client.time.time", return_value=1234567890.0)
    def test_glyph_to_signal_conversion(self, mock_time):
        """Test PhenomenalGlyph → SymbolicSignal conversion"""
        # Create router with mocked dependencies
        mock_router_module = Mock()
        mock_signal_class = Mock()
        mock_router_module.SymbolicSignal = mock_signal_class
        mock_router_module.DiagnosticSignalType = Mock()
        mock_router_module.DiagnosticSignalType.PULSE = "PULSE"

        router = SymbolicMeshRouterClient(router_module=mock_router_module)

        # Create test glyph
        scene = self._create_test_scene(0.7, 0.4)
        glyphs = map_scene_to_glyphs(scene)
        test_glyph = glyphs[0]

        # Convert glyph to signal
        signal = router._convert_glyph_to_signal(test_glyph, 0.6, {"test": "context"})

        # Verify SymbolicSignal was created with correct parameters
        mock_signal_class.assert_called_once()
        call_kwargs = mock_signal_class.call_args[1]

        assert call_kwargs["signal_type"] == "PULSE"
        assert call_kwargs["source_module"] == "aka_qualia"
        assert call_kwargs["target_module"] == "symbolic_mesh"
        assert call_kwargs["timestamp"] == 1234567890.0
        assert call_kwargs["confidence_score"] == 0.6  # Priority maps to confidence
        assert call_kwargs["drift_score"] == 0.4  # 1.0 - priority
        assert call_kwargs["diagnostic_event"] == "PULSE"

        # Verify payload contains glyph data
        payload = call_kwargs["payload"]
        assert payload["glyph_key"] == test_glyph.key
        assert payload["glyph_attrs"] == test_glyph.attrs
        assert payload["priority"] == 0.6
        assert payload["routing_context"] == {"test": "context"}

    def test_glyph_key_diagnostic_mapping(self):
        """Test mapping of glyph keys to diagnostic event types"""
        mock_router_module = Mock()
        mock_router_module.DiagnosticSignalType = Mock()
        mock_router_module.DiagnosticSignalType.PULSE = "PULSE"

        router = SymbolicMeshRouterClient(router_module=mock_router_module)

        # Test all glyph key mappings
        glyph_keys = [
            "aka:vigilance",
            "aka:red_threshold",
            "aka:grounding_hint",
            "aka:soothe_anchor",
            "aka:approach_avoid",
        ]

        for glyph_key in glyph_keys:
            diagnostic_event = router._map_glyph_to_diagnostic_event(glyph_key)
            assert diagnostic_event == "PULSE", f"Expected PULSE for {glyph_key}, got {diagnostic_event}"

        # Test unknown glyph key
        unknown_diagnostic = router._map_glyph_to_diagnostic_event("unknown:glyph")
        assert unknown_diagnostic == "PULSE"

    def _create_test_scene(self, narrative_gravity: float, risk_score: float) -> PhenomenalScene:
        """Helper to create test PhenomenalScene"""
        proto = ProtoQualia(
            narrative_gravity=narrative_gravity,
            embodiment=0.7,
            colorfield="red",
            arousal=0.5,
            tone=0.0,
            clarity=0.8,
            temporal_feel=TemporalFeel.PRESENT,
            agency_feel=AgencyFeel.EFFORTLESS,
        )

        risk = RiskGauge(score=risk_score, severity=RiskSeverity.MODERATE if risk_score > 0.5 else RiskSeverity.LOW)

        return PhenomenalScene(proto=proto, risk=risk, context={"test_context": True})


# Integration test fixtures
@pytest.fixture
def mock_lukhas_router():
    """Fixture providing mock LUKHAS router dependencies"""
    with (
        patch("candidate.aka_qualia.router_client.route_signal") as mock_route,
        patch("candidate.aka_qualia.router_client.SymbolicSignal") as mock_signal,
        patch("candidate.aka_qualia.router_client.DiagnosticSignalType") as mock_diagnostic,
    ):
        mock_diagnostic.PULSE = "PULSE"
        yield {"route_signal": mock_route, "SymbolicSignal": mock_signal, "DiagnosticSignalType": mock_diagnostic}


@pytest.fixture
def sample_scenes():
    """Fixture providing sample PhenomenalScenes for testing"""
    return [
        # High priority vigilance scene
        PhenomenalScene(
            proto=ProtoQualia(
                narrative_gravity=0.9,
                embodiment=0.6,
                colorfield="aka/red",
                arousal=0.8,
                tone=-0.4,
                clarity=0.7,
                temporal_feel=TemporalFeel.URGENT,
                agency_feel=AgencyFeel.FORCED,
            ),
            risk=RiskGauge(score=0.8, severity=RiskSeverity.HIGH),
            context={"scenario": "threat_detection"},
        ),
        # Low priority soothe scene
        PhenomenalScene(
            proto=ProtoQualia(
                narrative_gravity=0.3,
                embodiment=0.8,
                colorfield="aoi/blue",
                arousal=0.2,
                tone=0.6,
                clarity=0.9,
                temporal_feel=TemporalFeel.TIMELESS,
                agency_feel=AgencyFeel.EFFORTLESS,
            ),
            risk=RiskGauge(score=0.1, severity=RiskSeverity.LOW),
            context={"scenario": "calm_state"},
        ),
    ]
