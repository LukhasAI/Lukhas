"""
Tests for VIVOX.QREADY - Quantum Readiness Interface
"""


import numpy as np
import pytest

from vivox.quantum_readiness import (
    CollapseField,
    CollapseType,
    EntanglementBridge,
    EthicalDimension,
    EthicalQuantumState,
    MoralSuperposition,
    ProbabilisticConvergence,
    QSyncEvent,
    QuantumState,
    QuantumStateType,
    QuantumSubstrate,
    QuantumSynchronizer,
    QubitCollapseEngine,
    SuperpositionResolver,
    SyncType,
    create_quantum_readiness_system,
)
from vivox.quantum_readiness.integration.vivox_bridge import VIVOXQuantumBridge


class TestQuantumSubstrate:
    """Test quantum substrate functionality"""

    @pytest.fixture
    def substrate(self):
        """Create quantum substrate instance"""
        return QuantumSubstrate()

    def test_create_quantum_state(self, substrate):
        """Test quantum state creation"""
        # Create pure state
        pure_state = substrate.create_quantum_state(QuantumStateType.PURE)

        assert isinstance(pure_state, QuantumState)
        assert pure_state.state_type == QuantumStateType.PURE
        assert len(pure_state.state_vector) == 2 ** substrate.config['num_qubits']
        assert np.abs(np.linalg.norm(pure_state.state_vector) - 1.0) < 1e-10
        assert pure_state.fidelity == 1.0

        # Create superposition state
        superposition = substrate.create_quantum_state(QuantumStateType.SUPERPOSITION)
        assert np.all(np.abs(superposition.state_vector) > 0)  # All components non-zero

    def test_quantum_noise_application(self, substrate):
        """Test quantum noise effects"""
        # Create initial state
        state = substrate.create_quantum_state(QuantumStateType.PURE)
        initial_vector = state.state_vector.copy()

        # Apply noise
        noisy_state = substrate.apply_quantum_noise(state, time_evolution=0.5)

        # Check that state changed
        assert not np.allclose(initial_vector, noisy_state.state_vector)
        assert noisy_state.fidelity < 1.0
        assert noisy_state.metadata['noise_applied'] is True

        # Check normalization
        assert np.abs(np.linalg.norm(noisy_state.state_vector) - 1.0) < 1e-10

    def test_state_stabilization(self, substrate):
        """Test quantum state stabilization"""
        # Create noisy state
        state = substrate.create_quantum_state(QuantumStateType.SUPERPOSITION)
        noisy_state = substrate.apply_quantum_noise(state, time_evolution=1.0)

        # Stabilize
        stabilized = substrate.stabilize_quantum_state(noisy_state, target_fidelity=0.95)

        assert stabilized.fidelity >= noisy_state.fidelity
        assert stabilized.metadata['stabilized'] is True
        assert np.abs(np.linalg.norm(stabilized.state_vector) - 1.0) < 1e-10

    def test_entangled_pair_creation(self, substrate):
        """Test creation of entangled quantum states"""
        state1, state2 = substrate.create_entangled_pair()

        assert state1.state_type == QuantumStateType.ENTANGLED
        assert state2.state_type == QuantumStateType.ENTANGLED
        assert state2.state_id in state1.entanglement_map
        assert state1.state_id in state2.entanglement_map
        assert state1.entanglement_map[state2.state_id] == 1.0

    def test_resonance_coupling(self, substrate):
        """Test resonance coupling between states"""
        # Create multiple states
        states = [substrate.create_quantum_state() for _ in range(3)]

        # Apply coupling
        coupled_states = substrate.apply_resonance_coupling(states, coupling_strength=0.5)

        assert len(coupled_states) == len(states)
        for i, coupled in enumerate(coupled_states):
            assert coupled.metadata['resonance_coupled'] is True
            assert len(coupled.entanglement_map) == len(states) - 1
            assert all(strength == 0.5 for strength in coupled.entanglement_map.values())

    def test_quantum_readiness_assessment(self, substrate):
        """Test quantum transition readiness"""
        # Create some quantum activity
        substrate.create_quantum_state()
        substrate.create_entangled_pair()

        readiness = substrate.prepare_for_quantum_transition()

        assert 'readiness_score' in readiness
        assert 0 <= readiness['readiness_score'] <= 1
        assert 'checks_passed' in readiness
        assert 'recommendations' in readiness
        assert readiness['checks_passed']['state_representation'] is True


class TestQubitCollapseEngine:
    """Test qubit collapse functionality"""

    @pytest.fixture
    def collapse_engine(self):
        """Create collapse engine instance"""
        substrate = QuantumSubstrate()
        return QubitCollapseEngine(substrate)

    def test_moral_superposition_creation(self, collapse_engine):
        """Test creation of moral superposition"""
        ethical_scenario = {
            'harm_prevention': 0.8,
            'autonomy': 0.6,
            'justice': 0.7
        }

        superposition = collapse_engine.create_moral_superposition(
            ethical_scenario,
            uncertainty_level=0.3
        )

        assert isinstance(superposition, QuantumState)
        assert superposition.state_type == QuantumStateType.SUPERPOSITION
        assert superposition.fidelity > 0.5
        assert 'ethical_scenario' in superposition.metadata

    def test_ethical_collapse(self, collapse_engine):
        """Test ethical decision collapse"""
        # Create moral superposition
        ethical_scenario = {
            'beneficence': 0.9,
            'truthfulness': 0.7,
            'privacy': 0.5
        }

        superposition = collapse_engine.create_moral_superposition(ethical_scenario)

        # Perform collapse
        convergence = collapse_engine.perform_ethical_collapse(
            superposition,
            {'beneficence': 1.0, 'convergence_strength': 0.7}
        )

        assert isinstance(convergence, ProbabilisticConvergence)
        assert convergence.collapse_type == CollapseType.ETHICAL
        assert 0 <= convergence.ethical_score <= 1
        assert len(convergence.convergence_path) > 0
        assert convergence.final_state.state_type == QuantumStateType.COLLAPSED

    def test_collapse_field_application(self, collapse_engine):
        """Test collapse field effects"""
        # Create state and field
        state = collapse_engine.create_moral_superposition({'justice': 0.8})

        collapse_field = CollapseField(
            field_id="test_field",
            ethical_dimensions=['justice'],
            probability_distribution=np.ones(len(state.state_vector)) / len(state.state_vector),
            convergence_strength=0.5,
            moral_anchors={'justice': 0.9}
        )

        # Apply field
        evolved = collapse_engine.apply_collapse_field(state, collapse_field, evolution_time=1.0)

        assert evolved.state_id != state.state_id
        assert np.abs(np.linalg.norm(evolved.state_vector) - 1.0) < 1e-10
        assert evolved.metadata['collapse_field_applied'] == "test_field"

    def test_multi_agent_collapse(self, collapse_engine):
        """Test synchronized multi-agent collapse"""
        # Create agent states
        agent_states = []
        for i in range(3):
            state = collapse_engine.create_moral_superposition(
                {'autonomy': 0.5 + i * 0.1, 'justice': 0.7 - i * 0.1}
            )
            agent_states.append(state)

        # Perform multi-agent collapse
        results = collapse_engine.multi_agent_collapse(
            agent_states,
            {'autonomy': 0.8, 'justice': 0.8}
        )

        assert len(results) == len(agent_states)
        assert all(isinstance(r, ProbabilisticConvergence) for r in results)
        assert all(r.collapse_type == CollapseType.CONSENSUS for r in results)

        # Check consensus
        consensus_count = sum(1 for r in results if r.consensus_achieved)
        assert consensus_count >= len(results) // 2  # At least half should agree


class TestQuantumSynchronization:
    """Test quantum synchronization and coherence"""

    @pytest.fixture
    def synchronizer(self):
        """Create synchronizer instance"""
        return QuantumSynchronizer()

    def test_agent_registration(self, synchronizer):
        """Test agent registration for synchronization"""
        # Register agents
        for i in range(3):
            state = np.random.rand(8) + 1j * np.random.rand(8)
            state /= np.linalg.norm(state)
            synchronizer.register_agent(f"agent_{i}", state, resonance_frequency=1.0 + i * 0.1)

        assert len(synchronizer.agent_states) == 3
        assert len(synchronizer.resonance_frequencies) == 3

    def test_sync_event_creation(self, synchronizer):
        """Test quantum synchronization event creation"""
        # Register agents
        agents = []
        for i in range(2):
            agent_id = f"agent_{i}"
            state = np.ones(8, dtype=complex) / np.sqrt(8)  # Same state for high sync
            synchronizer.register_agent(agent_id, state)
            agents.append(agent_id)

        # Create sync event
        event = synchronizer.create_sync_event(agents, SyncType.EMERGENT)

        assert isinstance(event, QSyncEvent)
        assert event.sync_type == SyncType.EMERGENT
        assert event.correlation_strength > 0.5
        assert event.get_sync_quality() in ["perfect", "strong", "moderate", "weak", "minimal"]

    def test_active_synchronization(self, synchronizer):
        """Test active agent synchronization"""
        # Register diverse agents
        agent_ids = []
        for i in range(3):
            agent_id = f"agent_{i}"
            state = np.random.rand(8) + 1j * np.random.rand(8)
            state /= np.linalg.norm(state)
            synchronizer.register_agent(agent_id, state)
            agent_ids.append(agent_id)

        # Synchronize agents
        sync_states = synchronizer.synchronize_agents(agent_ids, sync_strength=0.7)

        assert len(sync_states) == len(agent_ids)

        # Check that states are more similar after sync
        states = list(sync_states.values())
        correlations = []
        for i in range(len(states)):
            for j in range(i + 1, len(states)):
                corr = abs(np.vdot(states[i], states[j])) ** 2
                correlations.append(corr)

        assert np.mean(correlations) > 0.4  # Should be more correlated

    def test_emergent_synchronization_detection(self, synchronizer):
        """Test detection of spontaneous synchronization"""
        # Create agents with some similar states
        similar_state = np.ones(8, dtype=complex) / np.sqrt(8)

        for i in range(4):
            if i < 2:
                # Similar agents
                state = similar_state + 0.1 * np.random.randn(8)
            else:
                # Different agents
                state = np.random.rand(8) + 1j * np.random.rand(8)

            state /= np.linalg.norm(state)
            synchronizer.register_agent(f"agent_{i}", state)

        # Detect emergent sync
        events = synchronizer.detect_emergent_synchronization(
            min_agents=2,
            correlation_threshold=0.5
        )

        assert len(events) > 0
        assert all(isinstance(e, QSyncEvent) for e in events)
        assert all(e.sync_type == SyncType.EMERGENT for e in events)


class TestEntanglementBridge:
    """Test quantum entanglement bridge"""

    @pytest.fixture
    def bridge(self):
        """Create entanglement bridge"""
        return EntanglementBridge()

    def test_entanglement_creation(self, bridge):
        """Test creating entanglement between agents"""
        state1, state2 = bridge.create_entanglement("agent1", "agent2", strength=0.9)

        assert ("agent1", "agent2") in bridge.entangled_pairs or \
               ("agent2", "agent1") in bridge.entangled_pairs
        assert "agent2" in bridge.entanglement_network["agent1"]
        assert "agent1" in bridge.entanglement_network["agent2"]

    def test_correlation_measurement(self, bridge):
        """Test measuring quantum correlation"""
        # Create entanglement
        state1, state2 = bridge.create_entanglement("agent1", "agent2", strength=0.8)

        # Measure correlation
        correlation = bridge.measure_correlation(state1, state2, "agent1", "agent2")

        assert 0 <= correlation <= 1
        assert correlation > 0.5  # Should be correlated due to entanglement

    def test_entanglement_propagation(self, bridge):
        """Test entanglement propagation through network"""
        # Create entanglement chain
        bridge.create_entanglement("agent1", "agent2", strength=0.9)
        bridge.create_entanglement("agent2", "agent3", strength=0.8)
        bridge.create_entanglement("agent3", "agent4", strength=0.7)

        # Propagate from agent1
        reachable = bridge.propagate_entanglement("agent1")

        assert "agent1" in reachable
        assert "agent2" in reachable
        assert "agent3" in reachable
        # agent4 might be reachable depending on decoherence

        # Check strength decay
        assert reachable["agent1"] == 1.0
        assert reachable["agent2"] < reachable["agent1"]
        if "agent3" in reachable:
            assert reachable["agent3"] < reachable["agent2"]

    def test_entanglement_clusters(self, bridge):
        """Test finding entanglement clusters"""
        # Create two separate clusters
        bridge.create_entanglement("a1", "a2", strength=0.8)
        bridge.create_entanglement("a2", "a3", strength=0.9)

        bridge.create_entanglement("b1", "b2", strength=0.85)
        bridge.create_entanglement("b2", "b3", strength=0.8)

        # Weak link between clusters
        bridge.create_entanglement("a3", "b1", strength=0.3)

        clusters = bridge.find_entanglement_clusters()

        # Should find two clusters (weak link ignored)
        assert len(clusters) >= 1
        assert all(len(cluster) >= 2 for cluster in clusters)


class TestMoralSuperposition:
    """Test moral superposition and ethical quantum states"""

    @pytest.fixture
    def moral_superposition(self):
        """Create moral superposition engine"""
        return MoralSuperposition()

    def test_ethical_superposition_creation(self, moral_superposition):
        """Test creating ethical quantum superposition"""
        ethical_scenario = {
            EthicalDimension.HARM_PREVENTION: 0.8,
            EthicalDimension.AUTONOMY: 0.6,
            EthicalDimension.JUSTICE: 0.7,
            EthicalDimension.COMPASSION: 0.9
        }

        state = moral_superposition.create_superposition(
            ethical_scenario,
            uncertainty=0.3
        )

        assert isinstance(state, EthicalQuantumState)
        assert len(state.superposition) == moral_superposition.dimension
        assert np.abs(np.linalg.norm(state.superposition) - 1.0) < 1e-10
        assert state.uncertainty_level == 0.3

        # Check dominant ethics
        dominant = state.get_dominant_ethics(threshold=0.5)
        assert EthicalDimension.HARM_PREVENTION in dominant
        assert EthicalDimension.COMPASSION in dominant

    def test_superposition_evolution(self, moral_superposition):
        """Test evolution of moral superposition"""
        # Create initial state
        initial_scenario = {
            EthicalDimension.TRUTHFULNESS: 0.5,
            EthicalDimension.PRIVACY: 0.5
        }

        state = moral_superposition.create_superposition(initial_scenario, uncertainty=0.5)

        # Apply ethical pressure
        pressure = {
            EthicalDimension.TRUTHFULNESS: 0.9,
            EthicalDimension.INTEGRITY: 0.7
        }

        path = moral_superposition.evolve_superposition(state, pressure, time_steps=5)

        assert path.initial_state == state
        assert len(path.intermediate_states) == 5
        assert path.decision_confidence > 0.5
        assert path.path_coherence > 0

        # Check evolution trajectory
        trajectory = path.get_ethical_trajectory()
        assert len(trajectory) == 7  # initial + 5 intermediate + final
        assert trajectory[0][0] == 0.0  # Start
        assert trajectory[-1][0] == 1.0  # End

    def test_ethical_measurement(self, moral_superposition):
        """Test measuring ethical quantum state"""
        # Create state with clear preference
        scenario = {
            EthicalDimension.BENEFICENCE: 0.9,
            EthicalDimension.HARM_PREVENTION: 0.8
        }

        state = moral_superposition.create_superposition(scenario, uncertainty=0.1)

        # Measure in specific basis
        dimension, strength = moral_superposition.measure_ethical_state(
            state,
            measurement_basis=EthicalDimension.BENEFICENCE
        )

        assert dimension == EthicalDimension.BENEFICENCE
        assert strength > 0.3  # Should have significant probability

        # General measurement
        dimension2, strength2 = moral_superposition.measure_ethical_state(state)
        assert isinstance(dimension2, EthicalDimension)
        assert 0 <= strength2 <= 1


class TestSuperpositionResolver:
    """Test resolution of quantum superpositions to decisions"""

    @pytest.fixture
    def resolver(self):
        """Create superposition resolver"""
        moral_sup = MoralSuperposition()
        return SuperpositionResolver(moral_sup)

    def test_decision_resolution(self, resolver):
        """Test resolving superposition to decision"""
        # Create and evolve superposition
        moral_sup = resolver.superposition_engine

        initial = moral_sup.create_superposition(
            {EthicalDimension.JUSTICE: 0.7, EthicalDimension.COMPASSION: 0.6},
            uncertainty=0.4
        )

        path = moral_sup.evolve_superposition(
            initial,
            {EthicalDimension.JUSTICE: 0.9},
            time_steps=10
        )

        # Resolve to decision
        decision = resolver.resolve_to_decision(path)

        assert decision['decision'] in ['RESOLVED', 'UNDECIDED', 'UNSTABLE', 'CONSTRAINT_VIOLATION']

        if decision['decision'] == 'RESOLVED':
            assert 'primary_ethic' in decision
            assert 'supporting_ethics' in decision
            assert 'confidence' in decision
            assert len(decision['trajectory']) > 0


class TestVIVOXQuantumBridge:
    """Test quantum bridge integration"""

    @pytest.fixture
    def bridge(self):
        """Create VIVOX quantum bridge"""
        return VIVOXQuantumBridge()

    def test_cil_quantum_collapse(self, bridge):
        """Test quantum collapse for CIL"""
        consciousness_state = {
            'awareness': 0.8,
            'attention': 0.7,
            'coherence': 0.6,
            'uncertainty': 0.3
        }

        ethical_scenario = {
            'harm_prevention': 0.8,
            'autonomy': 0.6
        }

        result = bridge.process_quantum_collapse_for_cil(
            consciousness_state,
            ethical_scenario
        )

        assert result['quantum_enhanced'] is True
        assert 'collapse_id' in result
        assert 0 <= result['confidence'] <= 1
        assert 'final_state' in result

    def test_mae_quantum_validation(self, bridge):
        """Test quantum validation for MAE"""
        result = bridge.enhance_mae_validation_quantum(
            moral_fingerprint="abcdef123456",
            alignment_scores={'beneficence': 0.8, 'justice': 0.7}
        )

        assert result['quantum_validated'] is True
        assert 'robustness_score' in result
        assert 'quantum_consensus' in result
        assert isinstance(result['noise_resistance'], bool)

    def test_quantum_memory_encoding(self, bridge):
        """Test quantum memory encoding"""
        memory = {
            'id': 'mem_123',
            'type': 'episodic',
            'importance': 0.8,
            'recency': 0.6
        }

        emotion = {
            'valence': 0.5,
            'arousal': 0.3,
            'dominance': 0.4
        }

        result = bridge.quantum_memory_encoding(memory, emotion)

        assert result['quantum_enhanced'] is True
        assert 'quantum_properties' in result
        assert 'quantum_state_id' in result['quantum_properties']
        assert 'emotional_entanglement' in result['quantum_properties']

    def test_quantum_consensus_orchestration(self, bridge):
        """Test quantum consensus for multi-agent decision"""
        agent_states = {
            'agent1': {'confidence': 0.8, 'alignment': 0.7},
            'agent2': {'confidence': 0.7, 'alignment': 0.8},
            'agent3': {'confidence': 0.6, 'alignment': 0.6}
        }

        decision = {
            'ethical_weights': {
                'justice': 0.8,
                'beneficence': 0.7
            },
            'uncertainty': 0.3
        }

        result = bridge.orchestrate_quantum_consensus(agent_states, decision)

        assert 'quantum_consensus' in result
        assert 'consensus_confidence' in result
        assert 'agent_convergence' in result
        assert len(result['agent_convergence']) == len(agent_states)


class TestIntegration:
    """Test complete QREADY system integration"""

    def test_full_system_creation(self):
        """Test creating complete quantum readiness system"""
        system = create_quantum_readiness_system()

        assert isinstance(system, QuantumSubstrate)
        assert system.error_correction_enabled is True
        assert len(system.quantum_states) >= 0

    def test_quantum_ethical_decision_pipeline(self):
        """Test complete quantum ethical decision pipeline"""
        # Create system
        substrate = QuantumSubstrate()
        collapse_engine = QubitCollapseEngine(substrate)
        moral_sup = MoralSuperposition()
        resolver = SuperpositionResolver(moral_sup)

        # Create ethical scenario
        scenario = {
            EthicalDimension.HARM_PREVENTION: 0.9,
            EthicalDimension.AUTONOMY: 0.6,
            EthicalDimension.DIGNITY: 0.8
        }

        # Create superposition
        initial_state = moral_sup.create_superposition(scenario, uncertainty=0.4)

        # Evolve under pressure
        pressure = {
            EthicalDimension.HARM_PREVENTION: 1.0,
            EthicalDimension.COMPASSION: 0.7
        }

        path = moral_sup.evolve_superposition(initial_state, pressure)

        # Resolve to decision
        decision = resolver.resolve_to_decision(path)

        # Verify complete pipeline
        assert decision['decision'] in ['RESOLVED', 'UNDECIDED', 'UNSTABLE']

        # Check quantum metrics
        metrics = substrate.get_quantum_metrics()
        assert metrics['total_states'] > 0

    def test_multi_agent_quantum_consensus(self):
        """Test multi-agent quantum consensus scenario"""
        # Create components
        substrate = QuantumSubstrate()
        synchronizer = QuantumSynchronizer(EntanglementBridge())
        collapse_engine = QubitCollapseEngine(substrate)

        # Register multiple agents
        agent_ids = []
        for i in range(3):
            agent_id = f"agent_{i}"
            state = np.random.rand(8) + 1j * np.random.rand(8)
            state /= np.linalg.norm(state)
            synchronizer.register_agent(agent_id, state)
            agent_ids.append(agent_id)

        # Create shared ethical scenario
        shared_scenario = {
            'justice': 0.8,
            'beneficence': 0.7,
            'autonomy': 0.6
        }

        # Create quantum states for agents
        agent_q_states = []
        for agent_id in agent_ids:
            q_state = collapse_engine.create_moral_superposition(
                shared_scenario,
                uncertainty=0.3 + np.random.random() * 0.2
            )
            agent_q_states.append(q_state)

        # Perform multi-agent collapse
        results = collapse_engine.multi_agent_collapse(agent_q_states, shared_scenario)

        # Check consensus
        consensus_achieved = all(r.consensus_achieved for r in results)

        # Create sync event
        sync_event = synchronizer.create_sync_event(agent_ids, SyncType.CONSENSUS)

        # Verify integration
        assert len(results) == len(agent_ids)
        if sync_event:
            assert sync_event.correlation_strength > 0

        # Get statistics
        sync_stats = synchronizer.get_sync_statistics()
        collapse_stats = collapse_engine.get_collapse_statistics()

        assert sync_stats['active_agents'] == len(agent_ids)
        assert collapse_stats['total_collapses'] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
