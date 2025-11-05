# owner: Jules-07
# tier: tier3
# module_uid: bio.core.bio_symbolic
# criticality: P1

import pytest

try:
    from bio.core.bio_symbolic import BioSymbolic, BioSymbolicOrchestrator, SymbolicGlyph
except ImportError:  # pragma: no cover
    pytest.skip("Bio symbolic module unavailable", allow_module_level=True)


@pytest.mark.tier3
@pytest.mark.bio
@pytest.mark.quantum
class TestBioSymbolic:
    """Test suite for the BioSymbolic class."""

    def setup_method(self):
        """Set up the test environment."""
        self.bio_symbolic = BioSymbolic()

    def test_initialization(self):
        """Test that the BioSymbolic class initializes correctly."""
        assert self.bio_symbolic.initialized
        assert self.bio_symbolic.coherence_threshold == 0.7
        assert self.bio_symbolic.bio_states == []
        assert self.bio_symbolic.symbolic_mappings == []
        assert self.bio_symbolic.integration_events == []

    @pytest.mark.parametrize(
        "frequency, expected_glyph",
        [
            (0.05, SymbolicGlyph.CIRCADIAN),
            (0.5, SymbolicGlyph.ULTRADIAN),
            (5.0, SymbolicGlyph.VITAL),
            (20.0, SymbolicGlyph.NEURAL),
        ],
    )
    def test_process_rhythm(self, frequency, expected_glyph):
        """Test the process_rhythm method."""
        data = {"type": "rhythm", "frequency": frequency, "amplitude": 1.0, "timestamp": "2025-09-12T12:00:00Z"}
        result = self.bio_symbolic.process_rhythm(data)
        assert result["glyph"] == expected_glyph.value
        assert result["type"] == "rhythm"
        assert result["frequency"] == frequency
        assert "coherence" in result

    @pytest.mark.parametrize(
        "level, expected_glyph",
        [
            (0.9, SymbolicGlyph.POWER_ABUNDANT),
            (0.6, SymbolicGlyph.POWER_BALANCED),
            (0.3, SymbolicGlyph.POWER_CONSERVE),
            (0.1, SymbolicGlyph.POWER_CRITICAL),
        ],
    )
    def test_process_energy(self, level, expected_glyph):
        """Test the process_energy method."""
        data = {"type": "energy", "level": level, "timestamp": "2025-09-12T12:00:00Z"}
        result = self.bio_symbolic.process_energy(data)
        assert result["glyph"] == expected_glyph.value
        assert result["type"] == "energy"
        assert result["level"] == level
        assert "coherence" in result

    @pytest.mark.parametrize(
        "operation, expected_glyph",
        [
            ("control", SymbolicGlyph.DNA_CONTROL),
            ("structure", SymbolicGlyph.DNA_STRUCTURE),
            ("initiate", SymbolicGlyph.DNA_INITIATE),
            ("pattern", SymbolicGlyph.DNA_PATTERN),
            ("express", SymbolicGlyph.DNA_EXPRESS),
            ("unknown_op", SymbolicGlyph.DNA_EXPRESS),  # Test fallback
        ],
    )
    def test_process_dna(self, operation, expected_glyph):
        """Test the process_dna method."""
        data = {"type": "dna", "operation": operation, "timestamp": "2025-09-12T12:00:00Z"}
        result = self.bio_symbolic.process_dna(data)
        assert result["glyph"] == expected_glyph.value
        assert result["type"] == "dna"
        assert result["operation"] == operation
        assert "coherence" in result

    @pytest.mark.parametrize(
        "response_type, expected_glyph",
        [
            ("transform", SymbolicGlyph.STRESS_TRANSFORM),
            ("adapt", SymbolicGlyph.STRESS_ADAPT),
            ("buffer", SymbolicGlyph.STRESS_BUFFER),
            ("flow", SymbolicGlyph.STRESS_FLOW),
            ("unknown", SymbolicGlyph.STRESS_ADAPT),  # Test fallback
        ],
    )
    def test_process_stress(self, response_type, expected_glyph):
        """Test the process_stress method."""
        data = {"type": "stress", "response": response_type, "stress_level": 0.5, "timestamp": "2025-09-12T12:00:00Z"}
        result = self.bio_symbolic.process_stress(data)
        assert result["glyph"] == expected_glyph.value
        assert result["type"] == "stress"
        assert "coherence" in result

    @pytest.mark.parametrize(
        "balance, expected_glyph",
        [
            (0.95, SymbolicGlyph.HOMEO_PERFECT),
            (0.8, SymbolicGlyph.HOMEO_BALANCED),
            (0.5, SymbolicGlyph.HOMEO_ADJUSTING),
            (0.2, SymbolicGlyph.HOMEO_STRESSED),
        ],
    )
    def test_process_homeostasis(self, balance, expected_glyph):
        """Test the process_homeostasis method."""
        data = {"type": "homeostasis", "balance": balance, "timestamp": "2025-09-12T12:00:00Z"}
        result = self.bio_symbolic.process_homeostasis(data)
        assert result["glyph"] == expected_glyph.value
        assert result["type"] == "homeostasis"
        assert "coherence" in result

    @pytest.mark.parametrize(
        "phase, expected_glyph",
        [
            ("explore", SymbolicGlyph.DREAM_EXPLORE),
            ("integrate", SymbolicGlyph.DREAM_INTEGRATE),
            ("process", SymbolicGlyph.DREAM_PROCESS),
            ("unknown", SymbolicGlyph.DREAM_PROCESS),  # Test fallback
        ],
    )
    def test_process_dream(self, phase, expected_glyph):
        """Test the process_dream method."""
        data = {"type": "dream", "phase": phase, "timestamp": "2025-09-12T12:00:00Z"}
        result = self.bio_symbolic.process_dream(data)
        assert result["glyph"] == expected_glyph.value
        assert result["type"] == "dream"
        assert "coherence" in result

    def test_process_dispatcher(self):
        """Test that the main process method dispatches correctly."""
        rhythm_data = {"type": "rhythm", "frequency": 1, "timestamp": "2025-09-12T12:00:00Z"}
        result = self.bio_symbolic.process(rhythm_data)
        assert result["glyph"] == SymbolicGlyph.VITAL.value

        energy_data = {"type": "energy", "level": 0.9, "timestamp": "2025-09-12T12:00:00Z"}
        result = self.bio_symbolic.process(energy_data)
        assert result["glyph"] == SymbolicGlyph.POWER_ABUNDANT.value

    def test_process_generic(self):
        """Test the generic process method for unknown types."""
        data = {"type": "unknown", "value": 123, "timestamp": "2025-09-12T12:00:00Z"}
        result = self.bio_symbolic.process_generic(data)
        assert result["type"] == "generic"
        assert result["data"] == data
        assert "coherence" in result

    @pytest.mark.parametrize(
        "data, expected_coherence",
        [
            ({"type": "test", "timestamp": "now"}, 1.0),
            ({"type": "test"}, 0.5),
            ({"timestamp": "now"}, 0.5),
            ({}, 0.0),
            ({"type": "test", "timestamp": "now", "noise": 0.2}, 0.8),
            ({"type": "test", "noise": 0.5}, 0.25),
        ],
    )
    def test_calculate_coherence(self, data, expected_coherence):
        """Test the coherence calculation logic."""
        coherence = self.bio_symbolic.calculate_coherence(data)
        assert coherence == pytest.approx(expected_coherence)

    def test_integrate(self):
        """Test the integration of bio and symbolic data."""
        bio_data = {"type": "rhythm", "frequency": 1, "timestamp": "2025-09-12T12:00:00Z"}
        symbolic_data = self.bio_symbolic.process(bio_data)

        result = self.bio_symbolic.integrate(bio_data, symbolic_data)

        assert result["integrated"]
        assert result["glyph"] == SymbolicGlyph.VITAL.value
        assert "timestamp" in result["bio_symbolic"]
        assert len(self.bio_symbolic.integration_events) == 1
        assert self.bio_symbolic.integration_events[0]["coherence"] == pytest.approx(1.0)

    def test_negative_noise_factor(self):
        """Test that a negative noise factor doesn't increase coherence."""
        data_without_noise = {"type": "test"}
        coherence_without_noise = self.bio_symbolic.calculate_coherence(data_without_noise)

        data_with_negative_noise = {"type": "test", "noise": -0.5}
        coherence_with_negative_noise = self.bio_symbolic.calculate_coherence(data_with_negative_noise)

        assert coherence_with_negative_noise <= coherence_without_noise


@pytest.mark.tier3
@pytest.mark.bio
@pytest.mark.quantum
class TestBioSymbolicOrchestrator:
    """Test suite for the BioSymbolicOrchestrator class."""

    def setup_method(self):
        """Set up the test environment."""
        self.orchestrator = BioSymbolicOrchestrator()

    def test_initialization(self):
        """Test that the orchestrator initializes correctly."""
        assert isinstance(self.orchestrator.bio_symbolic, BioSymbolic)
        assert self.orchestrator.orchestration_events == []

    def test_orchestrate_empty(self):
        """Test orchestrate with an empty list of inputs."""
        result = self.orchestrator.orchestrate([])
        assert result["results"] == []
        assert result["overall_coherence"] == 0
        assert not result["threshold_met"]
        assert len(self.orchestrator.orchestration_events) == 1

    def test_orchestrate_single_input(self):
        """Test orchestrate with a single input."""
        input_data = [{"type": "energy", "level": 0.9, "timestamp": "now"}]
        result = self.orchestrator.orchestrate(input_data)
        assert len(result["results"]) == 1
        assert result["results"][0]["glyph"] == SymbolicGlyph.POWER_ABUNDANT.value
        assert result["overall_coherence"] == pytest.approx(1.0)
        assert result["threshold_met"]

    def test_orchestrate_multiple_inputs(self):
        """Test orchestrate with multiple inputs and coherence."""
        inputs = [
            {"type": "rhythm", "frequency": 0.05, "timestamp": "now"},  # coherence 1.0
            {"type": "energy", "level": 0.3},  # coherence 0.5
            {"type": "stress", "response": "flow", "timestamp": "now"},  # coherence 1.0
        ]
        result = self.orchestrator.orchestrate(inputs)
        assert len(result["results"]) == 3
        expected_coherence = (1.0 + 0.5 + 1.0) / 3
        assert result["overall_coherence"] == pytest.approx(expected_coherence)
        assert result["threshold_met"]  # (2.5/3) > 0.7

    def test_get_dominant_glyph(self):
        """Test the get_dominant_glyph method."""
        # No glyphs
        results = [{"coherence": 1.0}, {"coherence": 0.5}]
        assert self.orchestrator.get_dominant_glyph(results) is None

        # Clear dominant glyph
        results = [
            {"glyph": "A", "coherence": 1.0},
            {"glyph": "B", "coherence": 0.5},
            {"glyph": "A", "coherence": 1.0},
        ]
        assert self.orchestrator.get_dominant_glyph(results) == "A"

        # A tie should return one of the winners
        results = [
            {"glyph": "A", "coherence": 1.0},
            {"glyph": "B", "coherence": 0.5},
        ]
        dominant_glyph = self.orchestrator.get_dominant_glyph(results)
        assert dominant_glyph in ["A", "B"]
