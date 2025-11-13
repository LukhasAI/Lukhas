"""Comprehensive tests for Quantum Entanglement Modeling for Superpositions."""
import pytest
import numpy as np
from candidate.quantum.superposition_engine import (
    QuantumSuperpositionEngine,
    QuantumEntanglementManager,
    EntanglementType,
    EntanglementLink,
    EntangledSuperpositionState,
    SuperpositionState,
)


class TestEntanglementDataClasses:
    """Test suite for entanglement data classes."""

    def test_entanglement_type_enum(self):
        """Test EntanglementType enum values."""
        assert EntanglementType.CORRELATED.value == "correlated"
        assert EntanglementType.ANTI_CORRELATED.value == "anti_correlated"
        assert EntanglementType.CONDITIONAL.value == "conditional"
        assert EntanglementType.FEEDBACK.value == "feedback"

    def test_entanglement_link_creation(self):
        """Test EntanglementLink dataclass creation."""
        link = EntanglementLink(
            state_a_id="state1",
            state_b_id="state2",
            entanglement_type=EntanglementType.CORRELATED,
            strength=0.8,
            phase_offset=0.5,
        )

        assert link.state_a_id == "state1"
        assert link.state_b_id == "state2"
        assert link.entanglement_type == EntanglementType.CORRELATED
        assert link.strength == 0.8
        assert link.phase_offset == 0.5
        assert isinstance(link.created_at, float)
        assert isinstance(link.metadata, dict)

    def test_entangled_superposition_state_creation(self):
        """Test EntangledSuperpositionState creation."""
        superposition = SuperpositionState(
            options=[{"id": "A"}, {"id": "B"}],
            amplitudes=[complex(1, 0), complex(0, 1)],
            metadata={"probabilities": [0.5, 0.5]},
        )

        entangled_state = EntangledSuperpositionState(
            state_id="test_state", superposition=superposition
        )

        assert entangled_state.state_id == "test_state"
        assert entangled_state.superposition == superposition
        assert len(entangled_state.entanglement_links) == 0
        assert len(entangled_state.measurement_history) == 0


class TestQuantumEntanglementManager:
    """Test suite for QuantumEntanglementManager."""

    @pytest.fixture
    def manager(self):
        """Create entanglement manager."""
        return QuantumEntanglementManager()

    @pytest.fixture
    def engine(self):
        """Create superposition engine."""
        return QuantumSuperpositionEngine()

    @pytest.fixture
    def simple_superposition(self, engine):
        """Create a simple superposition state."""
        options = [{"id": "A", "weight": 1.0}, {"id": "B", "weight": 1.0}]
        return engine.create_state(options)

    def test_register_state(self, manager, simple_superposition):
        """Test registering a superposition state."""
        entangled_state = manager.register_state("state1", simple_superposition)

        assert isinstance(entangled_state, EntangledSuperpositionState)
        assert entangled_state.state_id == "state1"
        assert entangled_state.superposition == simple_superposition

    def test_register_duplicate_state_raises_error(self, manager, simple_superposition):
        """Test that registering duplicate state raises ValueError."""
        manager.register_state("state1", simple_superposition)

        with pytest.raises(ValueError, match="already registered"):
            manager.register_state("state1", simple_superposition)

    def test_create_entanglement(self, manager, engine):
        """Test creating entanglement between two states."""
        options1 = [{"id": "A"}, {"id": "B"}]
        options2 = [{"id": "X"}, {"id": "Y"}]

        state1 = engine.create_state(options1)
        state2 = engine.create_state(options2)

        manager.register_state("state1", state1)
        manager.register_state("state2", state2)

        link = manager.create_entanglement(
            "state1", "state2", EntanglementType.CORRELATED, strength=0.8
        )

        assert isinstance(link, EntanglementLink)
        assert link.state_a_id == "state1"
        assert link.state_b_id == "state2"
        assert link.entanglement_type == EntanglementType.CORRELATED
        assert link.strength == 0.8

    def test_create_entanglement_validates_states(self, manager):
        """Test that creating entanglement validates state existence."""
        with pytest.raises(ValueError, match="not registered"):
            manager.create_entanglement(
                "invalid_state", "state2", EntanglementType.CORRELATED
            )

    def test_create_entanglement_validates_strength(self, manager, engine):
        """Test that entanglement strength is validated."""
        state1 = engine.create_state([{"id": "A"}])
        state2 = engine.create_state([{"id": "B"}])

        manager.register_state("state1", state1)
        manager.register_state("state2", state2)

        with pytest.raises(ValueError, match="strength must be between"):
            manager.create_entanglement(
                "state1", "state2", EntanglementType.CORRELATED, strength=1.5
            )

    def test_entanglement_graph_updated(self, manager, engine):
        """Test that entanglement graph is updated correctly."""
        state1 = engine.create_state([{"id": "A"}])
        state2 = engine.create_state([{"id": "B"}])

        manager.register_state("state1", state1)
        manager.register_state("state2", state2)

        manager.create_entanglement(
            "state1", "state2", EntanglementType.CORRELATED
        )

        graph = manager.get_entanglement_network()

        assert "state2" in graph["state1"]
        assert "state1" in graph["state2"]

    def test_measure_with_entanglement(self, manager, engine):
        """Test measuring a state with entanglement."""
        state1 = engine.create_state([{"id": "A"}, {"id": "B"}])
        state2 = engine.create_state([{"id": "X"}, {"id": "Y"}])

        manager.register_state("state1", state1)
        manager.register_state("state2", state2)

        manager.create_entanglement(
            "state1", "state2", EntanglementType.CORRELATED, strength=0.9
        )

        result = manager.measure_with_entanglement("state1", option_index=0)

        assert "measurement" in result
        assert "entanglement_effects" in result
        assert result["measurement"]["state_id"] == "state1"
        assert result["measurement"]["option_index"] == 0
        assert result["entangled_states_affected"] >= 0

    def test_measurement_history_recorded(self, manager, engine):
        """Test that measurement history is recorded."""
        state1 = engine.create_state([{"id": "A"}, {"id": "B"}])
        manager.register_state("state1", state1)

        manager.measure_with_entanglement("state1", option_index=0)

        history = manager.get_measurement_history("state1")
        assert len(history) == 1
        assert history[0]["state_id"] == "state1"
        assert history[0]["option_index"] == 0


class TestCorrelatedEntanglement:
    """Test suite for correlated entanglement."""

    @pytest.fixture
    def setup_correlated_states(self):
        """Setup two correlated entangled states."""
        manager = QuantumEntanglementManager()
        engine = QuantumSuperpositionEngine()

        state1 = engine.create_state([{"id": "A"}, {"id": "B"}])
        state2 = engine.create_state([{"id": "X"}, {"id": "Y"}])

        manager.register_state("state1", state1)
        manager.register_state("state2", state2)

        manager.create_entanglement(
            "state1", "state2", EntanglementType.CORRELATED, strength=0.9
        )

        return manager, "state1", "state2"

    def test_correlated_measurement_boosts_target(self, setup_correlated_states):
        """Test that correlated entanglement boosts corresponding option."""
        manager, state1_id, state2_id = setup_correlated_states

        state2_before = manager.get_state(state2_id)
        amplitude_before = state2_before.superposition.amplitudes[0]

        # Measure state1 at option 0
        result = manager.measure_with_entanglement(state1_id, option_index=0)

        state2_after = manager.get_state(state2_id)
        amplitude_after = state2_after.superposition.amplitudes[0]

        # Correlated entanglement should boost amplitude at index 0
        assert len(result["entanglement_effects"]) == 1
        assert result["entanglement_effects"][0]["entanglement_type"] == "correlated"

        # Probability should be renormalized
        prob_sum = sum(state2_after.superposition.metadata["probabilities"])
        assert abs(prob_sum - 1.0) < 1e-6

    def test_correlated_with_phase_offset(self):
        """Test correlated entanglement with phase offset."""
        manager = QuantumEntanglementManager()
        engine = QuantumSuperpositionEngine()

        state1 = engine.create_state([{"id": "A"}, {"id": "B"}])
        state2 = engine.create_state([{"id": "X"}, {"id": "Y"}])

        manager.register_state("state1", state1)
        manager.register_state("state2", state2)

        # Create entanglement with phase offset
        manager.create_entanglement(
            "state1",
            "state2",
            EntanglementType.CORRELATED,
            strength=0.8,
            phase_offset=np.pi / 4,
        )

        result = manager.measure_with_entanglement("state1", option_index=0)

        assert len(result["entanglement_effects"]) == 1


class TestAntiCorrelatedEntanglement:
    """Test suite for anti-correlated entanglement."""

    def test_anti_correlated_suppresses_target(self):
        """Test that anti-correlated entanglement suppresses corresponding option."""
        manager = QuantumEntanglementManager()
        engine = QuantumSuperpositionEngine()

        state1 = engine.create_state([{"id": "A"}, {"id": "B"}])
        state2 = engine.create_state([{"id": "X"}, {"id": "Y"}])

        manager.register_state("state1", state1)
        manager.register_state("state2", state2)

        manager.create_entanglement(
            "state1", "state2", EntanglementType.ANTI_CORRELATED, strength=0.9
        )

        state2_before = manager.get_state("state2")
        amplitude_before = abs(state2_before.superposition.amplitudes[0])

        result = manager.measure_with_entanglement("state1", option_index=0)

        state2_after = manager.get_state("state2")
        amplitude_after = abs(state2_after.superposition.amplitudes[0])

        # Anti-correlated should suppress amplitude
        assert amplitude_after < amplitude_before
        assert result["entanglement_effects"][0]["entanglement_type"] == "anti_correlated"


class TestConditionalEntanglement:
    """Test suite for conditional entanglement."""

    def test_conditional_modifies_all_options(self):
        """Test that conditional entanglement affects all options."""
        manager = QuantumEntanglementManager()
        engine = QuantumSuperpositionEngine()

        state1 = engine.create_state([{"id": "A"}, {"id": "B"}])
        state2 = engine.create_state([{"id": "X"}, {"id": "Y"}])

        manager.register_state("state1", state1)
        manager.register_state("state2", state2)

        manager.create_entanglement(
            "state1", "state2", EntanglementType.CONDITIONAL, strength=0.8
        )

        result = manager.measure_with_entanglement("state1", option_index=0)

        assert len(result["entanglement_effects"]) == 1
        effect = result["entanglement_effects"][0]
        assert effect["entanglement_type"] == "conditional"

        # Should affect multiple options
        changes = effect["amplitude_changes"]["changes"]
        assert len(changes) == len(state2.amplitudes)


class TestFeedbackEntanglement:
    """Test suite for feedback entanglement."""

    def test_feedback_bidirectional_influence(self):
        """Test that feedback entanglement has bidirectional influence."""
        manager = QuantumEntanglementManager()
        engine = QuantumSuperpositionEngine()

        state1 = engine.create_state([{"id": "A"}, {"id": "B"}])
        state2 = engine.create_state([{"id": "X"}, {"id": "Y"}])

        manager.register_state("state1", state1)
        manager.register_state("state2", state2)

        manager.create_entanglement(
            "state1", "state2", EntanglementType.FEEDBACK, strength=0.8
        )

        result = manager.measure_with_entanglement("state1", option_index=0)

        assert len(result["entanglement_effects"]) == 1
        assert result["entanglement_effects"][0]["entanglement_type"] == "feedback"


class TestEntanglementUtilities:
    """Test suite for entanglement utility methods."""

    @pytest.fixture
    def setup_network(self):
        """Setup a network of entangled states."""
        manager = QuantumEntanglementManager()
        engine = QuantumSuperpositionEngine()

        state1 = engine.create_state([{"id": "A"}])
        state2 = engine.create_state([{"id": "B"}])
        state3 = engine.create_state([{"id": "C"}])

        manager.register_state("state1", state1)
        manager.register_state("state2", state2)
        manager.register_state("state3", state3)

        manager.create_entanglement("state1", "state2", EntanglementType.CORRELATED)
        manager.create_entanglement("state2", "state3", EntanglementType.CORRELATED)

        return manager

    def test_get_entanglement_network(self, setup_network):
        """Test getting entanglement network graph."""
        manager = setup_network
        network = manager.get_entanglement_network()

        assert "state1" in network
        assert "state2" in network
        assert "state3" in network
        assert "state2" in network["state1"]
        assert "state3" in network["state2"]

    def test_get_state(self, setup_network):
        """Test getting entangled state by ID."""
        manager = setup_network
        state = manager.get_state("state1")

        assert state is not None
        assert state.state_id == "state1"

    def test_get_nonexistent_state(self, setup_network):
        """Test getting nonexistent state returns None."""
        manager = setup_network
        state = manager.get_state("nonexistent")

        assert state is None

    def test_get_entanglement_links(self, setup_network):
        """Test getting entanglement links for a state."""
        manager = setup_network
        links = manager.get_entanglement_links("state2")

        assert len(links) == 2  # Connected to state1 and state3

    def test_get_links_for_nonexistent_state(self, setup_network):
        """Test getting links for nonexistent state returns empty list."""
        manager = setup_network
        links = manager.get_entanglement_links("nonexistent")

        assert len(links) == 0

    def test_calculate_entanglement_entropy(self, setup_network):
        """Test calculating entanglement entropy between states."""
        manager = setup_network
        entropy = manager.calculate_entanglement_entropy("state1", "state2")

        assert entropy > 0
        assert entropy <= 1.5  # Maximum based on feedback entanglement

    def test_entropy_for_non_entangled_states(self, setup_network):
        """Test entropy is zero for non-entangled states."""
        manager = setup_network

        # state1 and state3 are not directly entangled
        entropy = manager.calculate_entanglement_entropy("state1", "state3")

        assert entropy == 0.0

    def test_entropy_varies_by_type(self):
        """Test that entropy varies by entanglement type."""
        manager = QuantumEntanglementManager()
        engine = QuantumSuperpositionEngine()

        state1 = engine.create_state([{"id": "A"}])
        state2 = engine.create_state([{"id": "B"}])

        manager.register_state("state1", state1)
        manager.register_state("state2", state2)

        # Test different entanglement types
        types_entropies = []

        for ent_type in [
            EntanglementType.CORRELATED,
            EntanglementType.ANTI_CORRELATED,
            EntanglementType.CONDITIONAL,
            EntanglementType.FEEDBACK,
        ]:
            test_manager = QuantumEntanglementManager()
            test_state1 = engine.create_state([{"id": "A"}])
            test_state2 = engine.create_state([{"id": "B"}])

            test_manager.register_state("s1", test_state1)
            test_manager.register_state("s2", test_state2)

            test_manager.create_entanglement(
                "s1", "s2", ent_type, strength=1.0
            )

            entropy = test_manager.calculate_entanglement_entropy("s1", "s2")
            types_entropies.append((ent_type, entropy))

        # All should be positive
        assert all(e > 0 for _, e in types_entropies)

        # Feedback should have highest entropy
        feedback_entropy = next(e for t, e in types_entropies if t == EntanglementType.FEEDBACK)
        assert all(feedback_entropy >= e for _, e in types_entropies)


class TestAmplitudeRenormalization:
    """Test suite for amplitude renormalization."""

    def test_amplitudes_stay_normalized(self):
        """Test that amplitudes remain normalized after entanglement effects."""
        manager = QuantumEntanglementManager()
        engine = QuantumSuperpositionEngine()

        state1 = engine.create_state([{"id": "A"}, {"id": "B"}])
        state2 = engine.create_state([{"id": "X"}, {"id": "Y"}])

        manager.register_state("state1", state1)
        manager.register_state("state2", state2)

        manager.create_entanglement(
            "state1", "state2", EntanglementType.CORRELATED, strength=0.9
        )

        # Measure and check normalization
        manager.measure_with_entanglement("state1", option_index=0)

        state2 = manager.get_state("state2")
        prob_sum = sum(state2.superposition.metadata["probabilities"])

        assert abs(prob_sum - 1.0) < 1e-6


class TestMultipleEntanglements:
    """Test suite for multiple simultaneous entanglements."""

    def test_state_with_multiple_entanglements(self):
        """Test a state entangled with multiple other states."""
        manager = QuantumEntanglementManager()
        engine = QuantumSuperpositionEngine()

        central = engine.create_state([{"id": "C"}])
        state1 = engine.create_state([{"id": "A"}])
        state2 = engine.create_state([{"id": "B"}])
        state3 = engine.create_state([{"id": "X"}])

        manager.register_state("central", central)
        manager.register_state("state1", state1)
        manager.register_state("state2", state2)
        manager.register_state("state3", state3)

        # Central entangled with all three
        manager.create_entanglement("central", "state1", EntanglementType.CORRELATED)
        manager.create_entanglement("central", "state2", EntanglementType.CORRELATED)
        manager.create_entanglement("central", "state3", EntanglementType.CORRELATED)

        links = manager.get_entanglement_links("central")
        assert len(links) == 3

        # Measurement should affect all three
        result = manager.measure_with_entanglement("central", option_index=0)
        assert result["entangled_states_affected"] == 3

    def test_cascading_measurements(self):
        """Test cascading measurement effects through network."""
        manager = QuantumEntanglementManager()
        engine = QuantumSuperpositionEngine()

        # Create chain: state1 -> state2 -> state3
        state1 = engine.create_state([{"id": "A"}])
        state2 = engine.create_state([{"id": "B"}])
        state3 = engine.create_state([{"id": "C"}])

        manager.register_state("state1", state1)
        manager.register_state("state2", state2)
        manager.register_state("state3", state3)

        manager.create_entanglement("state1", "state2", EntanglementType.CORRELATED)
        manager.create_entanglement("state2", "state3", EntanglementType.CORRELATED)

        # Measure state1
        result1 = manager.measure_with_entanglement("state1", option_index=0)
        assert result1["entangled_states_affected"] == 1

        # Measure state2 (now affected by state1's measurement)
        result2 = manager.measure_with_entanglement("state2", option_index=0)
        assert result2["entangled_states_affected"] == 1


# Smoke tests
def test_module_imports():
    """Test that all required classes can be imported."""
    from candidate.quantum.superposition_engine import (
        QuantumEntanglementManager,
        EntanglementType,
        EntanglementLink,
        EntangledSuperpositionState,
    )

    assert QuantumEntanglementManager is not None
    assert EntanglementType is not None
    assert EntanglementLink is not None
    assert EntangledSuperpositionState is not None


def test_basic_entanglement_workflow():
    """Test basic entanglement workflow from end to end."""
    manager = QuantumEntanglementManager()
    engine = QuantumSuperpositionEngine()

    # Create states
    options1 = [{"id": "A", "weight": 0.7}, {"id": "B", "weight": 0.3}]
    options2 = [{"id": "X", "weight": 0.5}, {"id": "Y", "weight": 0.5}]

    state1 = engine.create_state(options1)
    state2 = engine.create_state(options2)

    # Register and entangle
    manager.register_state("state1", state1)
    manager.register_state("state2", state2)

    manager.create_entanglement(
        "state1", "state2", EntanglementType.CORRELATED, strength=0.8
    )

    # Measure
    result = manager.measure_with_entanglement("state1")

    # Verify result structure
    assert "measurement" in result
    assert "entanglement_effects" in result
    assert "entangled_states_affected" in result
    assert result["measurement"]["state_id"] == "state1"
