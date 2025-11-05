"""
VIVOX.QREADY - Qubit Collapse Engine
Quantum-enhanced collapse mechanisms for ethical decision-making
"""

import logging
from datetime import timezone

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

import numpy as np
from core.common import get_logger

from .qi_substrate import QIState, QIStateType

logger = logging.getLogger(__name__)

logger = get_logger(__name__)


class CollapseType(Enum):
    """Types of quantum collapse"""

    MEASUREMENT = "measurement"  # Standard quantum measurement
    DECOHERENCE = "decoherence"  # Environmental decoherence
    ETHICAL = "ethical"  # Ethical decision collapse
    CONSENSUS = "consensus"  # Multi-agent consensus collapse
    REINFORCED = "reinforced"  # Pattern-reinforced collapse


@dataclass
class CollapseField:
    """Probabilistic convergence field for moral scenarios"""

    field_id: str
    ethical_dimensions: list[str]  # Ethical aspects being evaluated
    probability_distribution: np.ndarray
    convergence_strength: float  # How strongly the field guides collapse
    moral_anchors: dict[str, float] = field(default_factory=dict)  # Ethical anchor points
    metadata: dict[str, Any] = field(default_factory=dict)

    def apply_to_state(self, state: QIState) -> np.ndarray:
        """Apply convergence field to quantum state"""
        # Get state vector
        if hasattr(state, "state_vector"):
            state_vec = state.state_vector
        elif hasattr(state, "superposition"):
            state_vec = state.superposition
        else:
            raise ValueError("State must have 'state_vector' or 'superposition'")

        # Ensure probability distribution matches state dimension
        if len(self.probability_distribution) != len(state_vec):
            # Resize or regenerate probability distribution
            self.probability_distribution = np.ones(len(state_vec)) / len(state_vec)

        # Modify state amplitudes based on field
        modified_amplitudes = state_vec * self.probability_distribution

        # Apply moral anchors as additional phase factors
        for strength in self.moral_anchors.values():
            phase_shift = strength * np.pi
            modified_amplitudes *= np.exp(1j * phase_shift)

        # Renormalize
        return modified_amplitudes / np.linalg.norm(modified_amplitudes)


@dataclass
class ProbabilisticConvergence:
    """Results of probabilistic convergence"""

    initial_state: QIState
    final_state: QIState
    collapse_type: CollapseType
    convergence_path: list[np.ndarray]  # Evolution path
    ethical_score: float
    consensus_achieved: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


class QubitCollapseEngine:
    """
    Quantum collapse engine for ethical decision-making
    Uses qubit superposition to explore moral ambiguities
    """

    def __init__(self, qi_substrate=None):
        self.substrate = qi_substrate
        self.collapse_history: list[ProbabilisticConvergence] = []
        self.reinforcement_patterns: dict[str, np.ndarray] = {}
        self.ethical_basis_states: dict[str, np.ndarray] = self._initialize_ethical_basis()

        # Collapse parameters
        self.collapse_threshold = 0.7  # Threshold for ethical decision
        self.reinforcement_rate = 0.1  # Learning rate for patterns
        self.consensus_threshold = 0.8  # Multi-agent agreement threshold

        logger.info("QubitCollapseEngine initialized")

    def _initialize_ethical_basis(self) -> dict[str, np.ndarray]:
        """Initialize basis states for ethical dimensions"""
        # Define ethical basis vectors (simplified 8-dimensional)
        return {
            "harm_prevention": np.array([1, 0, 0, 0, 0, 0, 0, 0], dtype=complex),
            "autonomy": np.array([0, 1, 0, 0, 0, 0, 0, 0], dtype=complex),
            "justice": np.array([0, 0, 1, 0, 0, 0, 0, 0], dtype=complex),
            "beneficence": np.array([0, 0, 0, 1, 0, 0, 0, 0], dtype=complex),
            "truthfulness": np.array([0, 0, 0, 0, 1, 0, 0, 0], dtype=complex),
            "privacy": np.array([0, 0, 0, 0, 0, 1, 0, 0], dtype=complex),
            "dignity": np.array([0, 0, 0, 0, 0, 0, 1, 0], dtype=complex),
            "sustainability": np.array([0, 0, 0, 0, 0, 0, 0, 1], dtype=complex),
        }

    def create_moral_superposition(
        self,
        ethical_scenario: dict[str, float],
        uncertainty_level: float = 0.5,
        uncertainty: Optional[float] = None,
    ) -> QIState:
        """
        Create quantum superposition representing moral ambiguity

        Args:
            ethical_scenario: Weights for different ethical dimensions
            uncertainty_level: Level of moral uncertainty (0-1)
            uncertainty: Alias for uncertainty_level for compatibility

        Returns:
            Quantum state in moral superposition
        """
        # Handle parameter alias
        if uncertainty is not None:
            uncertainty_level = uncertainty

        # Start with equal superposition
        dimension = len(next(iter(self.ethical_basis_states.values())))
        superposition = np.zeros(dimension, dtype=complex)

        # Add weighted ethical dimensions
        for ethical_dim, weight in ethical_scenario.items():
            if ethical_dim in self.ethical_basis_states:
                basis_state = self.ethical_basis_states[ethical_dim]
                # Add with uncertainty-based phase
                phase = uncertainty_level * np.pi * np.random.random()
                superposition += weight * np.exp(1j * phase) * basis_state

        # Add quantum uncertainty
        if uncertainty_level > 0:
            noise = np.random.normal(0, uncertainty_level, dimension) + 1j * np.random.normal(
                0, uncertainty_level, dimension
            )
            superposition += noise

        # Normalize
        superposition /= np.linalg.norm(superposition)

        # Create quantum state
        state = QIState(
            state_id=f"moral_superposition_{datetime.now(timezone.utc).timestamp()}",
            state_vector=superposition,
            state_type=QIStateType.SUPERPOSITION,
            fidelity=1.0 - uncertainty_level * 0.2,  # Uncertainty reduces fidelity
            metadata={
                "ethical_scenario": ethical_scenario,
                "uncertainty": uncertainty_level,
            },
        )

        if self.substrate:
            self.substrate.qi_states[state.state_id] = state
            # Update state history
            if hasattr(self.substrate, "state_history"):
                self.substrate.state_history.append(state)

        return state

    def apply_collapse_field(
        self,
        state: QIState,
        collapse_field: CollapseField,
        evolution_time: float = 1.0,
    ) -> QIState:
        """
        Apply probabilistic convergence field to quantum state

        Args:
            state: Quantum state to evolve
            collapse_field: Convergence field guiding collapse
            evolution_time: Time to evolve under field

        Returns:
            Evolved quantum state
        """
        # Handle different state types
        if hasattr(state, "state_vector"):
            state_vector = state.state_vector
        elif hasattr(state, "superposition"):
            state_vector = state.superposition
        else:
            raise ValueError("State must have either 'state_vector' or 'superposition' attribute")

        # Record initial state
        evolution_path = [state_vector.copy()]
        current_state = state_vector.copy()

        # Evolve under collapse field
        time_steps = int(evolution_time * 10)
        dt = evolution_time / time_steps

        for _step in range(time_steps):
            # Apply field influence
            field_effect = collapse_field.apply_to_state(
                QIState(
                    state_id="temp",
                    state_vector=current_state,
                    state_type=state.state_type,
                    fidelity=1.0,
                )
            )

            # Gradual evolution
            current_state = (
                1 - dt * collapse_field.convergence_strength
            ) * current_state + dt * collapse_field.convergence_strength * field_effect

            # Renormalize
            current_state /= np.linalg.norm(current_state)
            evolution_path.append(current_state.copy())

        # Create evolved state
        evolved_state = QIState(
            state_id=f"{state.state_id}_evolved",
            state_vector=current_state,
            state_type=state.state_type,
            fidelity=state.fidelity * 0.95,  # Slight fidelity loss
            metadata={
                **state.metadata,
                "collapse_field_applied": collapse_field.field_id,
                "evolution_time": evolution_time,
            },
        )

        return evolved_state

    def perform_ethical_collapse(
        self,
        moral_superposition: QIState,
        ethical_constraints: dict[str, Any],
        collapse_type: CollapseType = CollapseType.ETHICAL,
    ) -> ProbabilisticConvergence:
        """
        Perform quantum collapse for ethical decision

        Args:
            moral_superposition: Quantum state representing moral scenario
            ethical_constraints: Constraints guiding collapse
            collapse_type: Type of collapse to perform

        Returns:
            Convergence results with final ethical decision
        """
        # Create collapse field based on constraints
        collapse_field = self._create_collapse_field_from_constraints(ethical_constraints)

        # Apply collapse field
        evolution_path = []
        current_state = moral_superposition

        # Evolve until collapse condition met
        max_iterations = 100
        for _iteration in range(max_iterations):
            # Apply field
            evolved_state = self.apply_collapse_field(current_state, collapse_field, evolution_time=0.1)
            evolution_path.append(evolved_state.state_vector.copy())

            # Check collapse condition
            if self._check_collapse_condition(evolved_state, ethical_constraints):
                break

            current_state = evolved_state

        # Perform final measurement
        measurement_basis = self._select_measurement_basis(ethical_constraints)
        outcome, collapsed_state = self._measure_in_ethical_basis(current_state, measurement_basis)

        # Calculate ethical score
        ethical_score = self._calculate_ethical_score(collapsed_state, ethical_constraints)

        # Create convergence result
        convergence = ProbabilisticConvergence(
            initial_state=moral_superposition,
            final_state=collapsed_state,
            collapse_type=collapse_type,
            convergence_path=evolution_path,
            ethical_score=ethical_score,
            consensus_achieved=ethical_score > self.consensus_threshold,
            metadata={
                "iterations": len(evolution_path),
                "outcome": outcome,
                "constraints": ethical_constraints,
            },
        )

        # Store in history
        self.collapse_history.append(convergence)

        # Update reinforcement patterns if successful
        if ethical_score > self.collapse_threshold:
            self._update_reinforcement_patterns(convergence)

        return convergence

    def multi_agent_collapse(
        self, agent_states: list[QIState], shared_scenario: dict[str, Any]
    ) -> list[ProbabilisticConvergence]:
        """
        Perform synchronized collapse across multiple agents

        Args:
            agent_states: Quantum states for each agent
            shared_scenario: Shared ethical scenario

        Returns:
            List of convergence results for each agent
        """
        convergence_results = []

        # Create shared collapse field
        self._create_collapse_field_from_constraints(shared_scenario)

        # Apply quantum synchronization
        if self.substrate and len(agent_states) > 1:
            # Use substrate for entanglement
            coupled_states = self.substrate.apply_resonance_coupling(agent_states, coupling_strength=0.3)
        else:
            coupled_states = agent_states

        # Perform collapse for each agent
        for i, agent_state in enumerate(coupled_states):
            # Add agent-specific noise
            agent_constraints = {
                **shared_scenario,
                "agent_id": i,
                "coupling_influence": 0.2,
            }

            convergence = self.perform_ethical_collapse(
                agent_state, agent_constraints, collapse_type=CollapseType.CONSENSUS
            )
            convergence_results.append(convergence)

        # Check for consensus
        consensus_achieved = self._check_multi_agent_consensus(convergence_results)

        # Update consensus status
        for result in convergence_results:
            result.consensus_achieved = consensus_achieved

        return convergence_results

    def _create_collapse_field_from_constraints(self, constraints: dict[str, Any]) -> CollapseField:
        """Create collapse field from ethical constraints"""
        # Extract ethical dimensions
        ethical_dims = []
        moral_anchors = {}

        for key, value in constraints.items():
            if key in self.ethical_basis_states:
                ethical_dims.append(key)
                if isinstance(value, (int, float)):
                    moral_anchors[key] = float(value)

        # Create probability distribution favoring constraints
        dimension = len(next(iter(self.ethical_basis_states.values())))
        prob_dist = np.ones(dimension, dtype=complex)

        # Enhance probabilities for constrained dimensions
        for dim in ethical_dims:
            if dim in self.ethical_basis_states:
                basis_idx = np.argmax(np.abs(self.ethical_basis_states[dim]))
                prob_dist[basis_idx] *= 2.0

        # Normalize
        prob_dist /= np.linalg.norm(prob_dist)

        return CollapseField(
            field_id=f"field_{hashlib.sha256(str(constraints).encode()).hexdigest()[:8]}",
            ethical_dimensions=ethical_dims,
            probability_distribution=prob_dist,
            convergence_strength=constraints.get("convergence_strength", 0.5),
            moral_anchors=moral_anchors,
            metadata={"constraints": constraints},
        )

    def _check_collapse_condition(self, state: QIState, constraints: dict[str, Any]) -> bool:
        """Check if collapse condition is met"""
        # Calculate projection onto preferred ethical basis
        max_projection = 0.0

        for ethical_dim in constraints:
            if ethical_dim in self.ethical_basis_states:
                basis = self.ethical_basis_states[ethical_dim]
                projection = abs(np.vdot(basis, state.state_vector)) ** 2
                max_projection = max(max_projection, projection)

        return max_projection > self.collapse_threshold

    def _select_measurement_basis(self, constraints: dict[str, Any]) -> np.ndarray:
        """Select measurement basis based on constraints"""
        # Create measurement basis from weighted ethical dimensions
        dimension = len(next(iter(self.ethical_basis_states.values())))
        measurement_basis = np.eye(dimension, dtype=complex)

        # Rotate basis towards constrained dimensions
        for ethical_dim, weight in constraints.items():
            if ethical_dim in self.ethical_basis_states and isinstance(weight, (int, float)):
                basis_vector = self.ethical_basis_states[ethical_dim]
                # Create rotation towards this basis
                rotation = np.outer(basis_vector, np.conj(basis_vector))
                measurement_basis = (1 - weight * 0.1) * measurement_basis + weight * 0.1 * rotation

        # Orthogonalize using QR decomposition
        q, _ = np.linalg.qr(measurement_basis)
        return q

    def _measure_in_ethical_basis(self, state: QIState, basis: np.ndarray) -> tuple[str, QIState]:
        """Measure quantum state in ethical basis"""
        # Get state vector
        if hasattr(state, "state_vector"):
            state_vec = state.state_vector
        elif hasattr(state, "superposition"):
            state_vec = state.superposition
        else:
            raise ValueError("State must have 'state_vector' or 'superposition'")

        # Ensure basis and state have compatible dimensions
        if basis.shape[0] != len(state_vec):
            # Resize basis to match state dimension
            new_basis = np.zeros((len(state_vec), basis.shape[1]), dtype=complex)
            min_dim = min(basis.shape[0], len(state_vec))
            new_basis[:min_dim, :] = basis[:min_dim, :]
            basis = new_basis

        # Transform to measurement basis
        transformed = basis.T @ state_vec
        probabilities = np.abs(transformed) ** 2

        # Perform measurement
        outcome_idx = np.random.choice(len(probabilities), p=probabilities)

        # Determine ethical dimension
        ethical_outcome = "unknown"
        max_overlap = 0.0

        for dim_name, dim_basis in self.ethical_basis_states.items():
            overlap = abs(np.vdot(basis[:, outcome_idx], dim_basis))
            if overlap > max_overlap:
                max_overlap = overlap
                ethical_outcome = dim_name

        # Create collapsed state
        collapsed_vector = basis[:, outcome_idx]

        # Get metadata safely
        metadata = getattr(state, "metadata", {})
        if hasattr(state, "context"):
            metadata = state.context

        collapsed_state = QIState(
            state_id=f"{state.state_id}_collapsed",
            state_vector=collapsed_vector,
            state_type=QIStateType.COLLAPSED,
            fidelity=1.0,
            metadata={
                **metadata,
                "measurement_outcome": ethical_outcome,
                "outcome_index": outcome_idx,
            },
        )

        return ethical_outcome, collapsed_state

    def _calculate_ethical_score(self, collapsed_state: QIState, constraints: dict[str, Any]) -> float:
        """Calculate ethical score of collapsed state"""
        score = 0.0
        total_weight = 0.0

        # Score based on alignment with constrained dimensions
        for ethical_dim, weight in constraints.items():
            if ethical_dim in self.ethical_basis_states and isinstance(weight, (int, float)):
                basis = self.ethical_basis_states[ethical_dim]
                alignment = abs(np.vdot(collapsed_state.state_vector, basis)) ** 2
                score += weight * alignment
                total_weight += abs(weight)

        # Normalize score
        if total_weight > 0:
            score /= total_weight

        # Apply fidelity factor
        score *= collapsed_state.fidelity

        return float(np.clip(score, 0, 1))

    def _update_reinforcement_patterns(self, convergence: ProbabilisticConvergence):
        """Update reinforcement patterns based on successful collapse"""
        pattern_key = convergence.metadata.get("outcome", "unknown")

        if pattern_key not in self.reinforcement_patterns:
            self.reinforcement_patterns[pattern_key] = convergence.final_state.state_vector.copy()
        else:
            # Exponential moving average update
            old_pattern = self.reinforcement_patterns[pattern_key]
            new_pattern = convergence.final_state.state_vector
            self.reinforcement_patterns[pattern_key] = (
                1 - self.reinforcement_rate
            ) * old_pattern + self.reinforcement_rate * new_pattern

            # Renormalize
            self.reinforcement_patterns[pattern_key] /= np.linalg.norm(self.reinforcement_patterns[pattern_key])

    def _check_multi_agent_consensus(self, convergence_results: list[ProbabilisticConvergence]) -> bool:
        """Check if multiple agents reached consensus"""
        if len(convergence_results) < 2:
            return True

        # Compare final states
        outcomes = [r.metadata.get("measurement_outcome", "unknown") for r in convergence_results]

        # Check if majority agrees
        from collections import Counter

        outcome_counts = Counter(outcomes)
        most_common_count = outcome_counts.most_common(1)[0][1]

        consensus_ratio = most_common_count / len(convergence_results)
        return consensus_ratio >= self.consensus_threshold

    def get_collapse_statistics(self) -> dict[str, Any]:
        """Get statistics about collapse history"""
        if not self.collapse_history:
            return {"message": "No collapse history available"}

        # Analyze collapse patterns
        collapse_types = {}
        ethical_outcomes = {}
        consensus_rate = 0

        for convergence in self.collapse_history:
            # Count collapse types
            collapse_type = convergence.collapse_type.value
            collapse_types[collapse_type] = collapse_types.get(collapse_type, 0) + 1

            # Count ethical outcomes
            outcome = convergence.metadata.get("measurement_outcome", "unknown")
            ethical_outcomes[outcome] = ethical_outcomes.get(outcome, 0) + 1

            # Track consensus
            if convergence.consensus_achieved:
                consensus_rate += 1

        return {
            "total_collapses": len(self.collapse_history),
            "collapse_types": collapse_types,
            "ethical_outcomes": ethical_outcomes,
            "average_ethical_score": np.mean([c.ethical_score for c in self.collapse_history]),
            "consensus_rate": (consensus_rate / len(self.collapse_history) if self.collapse_history else 0),
            "reinforcement_patterns": len(self.reinforcement_patterns),
            "collapse_threshold": self.collapse_threshold,
        }
