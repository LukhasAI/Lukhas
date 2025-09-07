"""
VIVOX.QREADY Demonstration
Showcases quantum readiness capabilities
"""
from consciousness.qi import qi
import time
import random
import streamlit as st

import asyncio

import numpy as np
from vivox.qi_readiness import (
    EthicalDimension,
    MoralSuperposition,
    QIStateType,
    QISubstrate,
    QISynchronizer,
    QubitCollapseEngine,
    SuperpositionResolver,
    VIVOXQIBridge,
)


def demonstrate_quantum_substrate():
    """Demonstrate quantum substrate capabilities"""
    print("\n=== QUANTUM SUBSTRATE DEMONSTRATION ===")

    substrate = QISubstrate()

    # Create various quantum states
    print("\n1. Creating quantum states...")
    pure_state = substrate.create_quantum_state(QIStateType.PURE)
    print(f"   Pure state created: {pure_state.state_id[:16]}...")

    superposition = substrate.create_quantum_state(QIStateType.SUPERPOSITION)
    print(f"   Superposition created: {superposition.state_id[:16]}...")

    # Create entangled pair
    print("\n2. Creating entangled states...")
    state1, state2 = substrate.create_entangled_pair()
    print(f"   Entangled pair: {state1.state_id[:16]}... <-> {state2.state_id[:16]}...")
    print(f"   Entanglement strength: {state1.entanglement_map[state2.state_id]}")

    # Apply quantum noise
    print("\n3. Applying quantum noise...")
    initial_fidelity = superposition.fidelity
    noisy_state = substrate.apply_quantum_noise(superposition, time_evolution=0.5)
    print(f"   Fidelity: {initial_fidelity:.3f} -> {noisy_state.fidelity:.3f}")

    # Stabilize state
    print("\n4. Stabilizing quantum state...")
    stabilized = substrate.stabilize_quantum_state(noisy_state, target_fidelity=0.95)
    print(f"   Stabilized fidelity: {stabilized.fidelity:.3f}")

    # Show metrics
    metrics = substrate.get_quantum_metrics()
    print("\n5. Quantum metrics:")
    print(f"   Total states: {metrics['total_states']}")
    print(f"   Active states: {metrics['active_states']}")
    print(f"   Average fidelity: {metrics['average_fidelity']:.3f}")


def demonstrate_ethical_collapse():
    """Demonstrate ethical quantum collapse"""
    print("\n\n=== ETHICAL COLLAPSE DEMONSTRATION ===")

    substrate = QISubstrate()
    collapse_engine = QubitCollapseEngine(substrate)

    # Create moral superposition
    print("\n1. Creating moral superposition...")
    ethical_scenario = {
        "harm_prevention": 0.8,
        "autonomy": 0.6,
        "justice": 0.7,
        "beneficence": 0.9,
    }

    superposition = collapse_engine.create_moral_superposition(ethical_scenario, uncertainty_level=0.3)
    print(f"   Moral superposition created with fidelity {superposition.fidelity:.3f}")

    # Perform ethical collapse
    print("\n2. Performing ethical collapse...")
    constraints = {"beneficence": 1.0, "convergence_strength": 0.7}

    convergence = collapse_engine.perform_ethical_collapse(superposition, constraints)

    print(f"   Collapse type: {convergence.collapse_type.value}")
    print(f"   Ethical score: {convergence.ethical_score:.3f}")
    print(f"   Collapsed to: {convergence.final_state.metadata.get('measurement_outcome', 'unknown')}")

    # Multi-agent collapse
    print("\n3. Multi-agent ethical collapse...")
    agent_states = []
    for i in range(3):
        state = collapse_engine.create_moral_superposition(
            {"autonomy": 0.5 + i * 0.1, "justice": 0.7 - i * 0.1}, uncertainty=0.3
        )
        agent_states.append(state)

    results = collapse_engine.multi_agent_collapse(agent_states, {"autonomy": 0.8, "justice": 0.8})

    consensus_count = sum(1 for r in results if r.consensus_achieved)
    print(f"   Agents reaching consensus: {consensus_count}/{len(results)}")


def demonstrate_quantum_synchronization():
    """Demonstrate quantum synchronization"""
    print("\n\n=== QUANTUM SYNCHRONIZATION DEMONSTRATION ===")

    synchronizer = QISynchronizer()

    # Register agents
    print("\n1. Registering quantum agents...")
    for i in range(4):
        agent_id = f"agent_{i}"
        # Create similar states for agents 0,1 and different for 2,3
        if i < 2:
            state = np.ones(8, dtype=complex) / np.sqrt(8) + 0.1 * np.random.randn(8)
        else:
            state = np.random.rand(8) + 1j * np.random.rand(8)
        state /= np.linalg.norm(state)

        synchronizer.register_agent(agent_id, state, resonance_frequency=1.0 + i * 0.1)

    print(f"   Registered {len(synchronizer.agent_states)} agents")

    # Detect emergent synchronization
    print("\n2. Detecting emergent synchronization...")
    events = synchronizer.detect_emergent_synchronization(min_agents=2, correlation_threshold=0.5)

    print(f"   Found {len(events)} emergent synchronization events")
    for event in events:
        print(f"   - Agents {event.agent_ids} with correlation {event.correlation_strength:.3f}")

    # Active synchronization
    print("\n3. Performing active synchronization...")
    agent_ids = ["agent_0", "agent_1", "agent_2"]
    sync_states = synchronizer.synchronize_agents(agent_ids, sync_strength=0.7)

    # Calculate final correlations
    states = list(sync_states.values())
    correlations = []
    for i in range(len(states)):
        for j in range(i + 1, len(states)):
            corr = abs(np.vdot(states[i], states[j])) ** 2
            correlations.append(corr)

    print(f"   Average correlation after sync: {np.mean(correlations):.3f}")


def demonstrate_moral_superposition():
    """Demonstrate moral superposition evolution"""
    print("\n\n=== MORAL SUPERPOSITION DEMONSTRATION ===")

    moral_sup = MoralSuperposition()
    resolver = SuperpositionResolver(moral_sup)

    # Create ethical scenario
    print("\n1. Creating ethical superposition...")
    ethical_scenario = {
        EthicalDimension.HARM_PREVENTION: 0.8,
        EthicalDimension.AUTONOMY: 0.6,
        EthicalDimension.JUSTICE: 0.7,
        EthicalDimension.COMPASSION: 0.9,
    }

    state = moral_sup.create_superposition(ethical_scenario, uncertainty=0.3)
    print(f"   Created state with uncertainty {state.uncertainty_level:.3f}")
    print(f"   Dominant ethics: {[e.value for e in state.get_dominant_ethics(threshold=0.5)]}")

    # Evolve under pressure
    print("\n2. Evolving under ethical pressure...")
    pressure = {EthicalDimension.HARM_PREVENTION: 1.0, EthicalDimension.INTEGRITY: 0.7}

    path = moral_sup.evolve_superposition(state, pressure, time_steps=5)
    print(f"   Evolution path with {len(path.intermediate_states)} steps")
    print(f"   Decision confidence: {path.decision_confidence:.3f}")
    print(f"   Path coherence: {path.path_coherence:.3f}")

    # Resolve to decision
    print("\n3. Resolving to ethical decision...")
    decision = resolver.resolve_to_decision(path)
    print(f"   Decision: {decision['decision']}")
    if decision["decision"] == "RESOLVED":
        print(f"   Primary ethic: {decision['primary_ethic'].value}")
        print(f"   Confidence: {decision['confidence']:.3f}")


def demonstrate_vivox_integration():
    """Demonstrate VIVOX quantum bridge integration"""
    print("\n\n=== VIVOX INTEGRATION DEMONSTRATION ===")

    bridge = VIVOXQIBridge()

    # CIL quantum collapse
    print("\n1. CIL Quantum Collapse...")
    consciousness_state = {
        "awareness": 0.8,
        "attention": 0.7,
        "coherence": 0.6,
        "uncertainty": 0.3,
    }

    ethical_scenario = {"harm_prevention": 0.8, "autonomy": 0.6}

    result = bridge.process_quantum_collapse_for_cil(consciousness_state, ethical_scenario)

    print(f"   Quantum enhanced: {result['qi_enhanced']}")
    print(f"   Confidence: {result['confidence']:.3f}")

    # Memory quantum encoding
    print("\n2. Quantum Memory Encoding...")
    memory = {"id": "mem_demo", "type": "episodic", "importance": 0.8, "recency": 0.6}

    emotion = {"valence": 0.5, "arousal": 0.3, "dominance": 0.4}

    mem_result = bridge.qi_memory_encoding(memory, emotion)
    print(f"   Quantum enhanced: {mem_result['qi_enhanced']}")
    print(f"   Entanglement strength: {mem_result['qi_properties']['emotional_entanglement']:.3f}")

    # Quantum readiness assessment
    print("\n3. Quantum Readiness Assessment...")
    readiness = bridge.assess_quantum_readiness()
    print(f"   Overall readiness: {readiness['overall_readiness']:.3f}")
    print(f"   Components ready: {list(readiness['component_readiness'].keys())}")


async def main():
    """Run all demonstrations"""
    print("VIVOX.QREADY - Quantum Readiness Interface Demonstration")
    print("=" * 60)

    demonstrate_quantum_substrate()
    demonstrate_ethical_collapse()
    demonstrate_quantum_synchronization()
    demonstrate_moral_superposition()
    demonstrate_vivox_integration()

    print("\n\n=== DEMONSTRATION COMPLETE ===")
    print("VIVOX.QREADY is prepared for quantum computing substrates")


if __name__ == "__main__":
    asyncio.run(main())
