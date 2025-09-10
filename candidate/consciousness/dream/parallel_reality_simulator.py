#!/usr/bin/env python3
import logging

logger = logging.getLogger(__name__)
"""
Parallel Reality Simulator for Dream Engine
==========================================
Enhanced simulation of alternative realities for creative exploration
and scenario testing within the consciousness dream system.

Features:
- Multi-dimensional reality branching
- Quantum-inspired probability calculations
- Causal chain preservation across realities
- Ethical constraint validation for each reality
- Memory integration for reality experiences
"""

import asyncio
import random
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from candidate.core.common import GLYPHSymbol, GLYPHToken, get_logger
from candidate.core.common.exceptions import LukhasError, ValidationError
from candidate.core.interfaces import CoreInterface
from candidate.core.interfaces.dependency_injection import get_service, register_service

from .parallel_reality_safety import (
    DriftMetrics,
    ParallelRealitySafetyFramework,
    SafetyLevel,
)

logger = get_logger(__name__)


class RealityType(Enum):
    """Types of parallel realities"""

    QUANTUM = "quantum"  # Quantum probability-based
    TEMPORAL = "temporal"  # Time-shifted scenarios
    CAUSAL = "causal"  # Different causal chains
    ETHICAL = "ethical"  # Different ethical frameworks
    CREATIVE = "creative"  # Pure imagination-based
    PREDICTIVE = "predictive"  # Future prediction scenarios
    # Backwards-compatibility alias for tests that reference CamelCase member name
    # while keeping canonical enum members uppercase.
    Temporal = TEMPORAL


@dataclass
class RealityBranch:
    """Single branch in parallel reality tree"""

    branch_id: str
    parent_id: Optional[str]
    reality_type: RealityType
    divergence_point: dict[str, Any]
    probability: float  # 0.0-1.0
    state: dict[str, Any]
    timestamp: datetime
    ethical_score: float = 1.0
    causal_chain: list[dict[str, Any]] = field(default_factory=list)
    memory_traces: list[str] = field(default_factory=list)

    def is_viable(self) -> bool:
        """Check if reality branch is viable"""
        return self.probability > 0.01 and self.ethical_score > 0.3


@dataclass
class RealitySimulation:
    """Complete parallel reality simulation"""

    simulation_id: str
    origin_reality: dict[str, Any]
    branches: list[RealityBranch]
    start_time: datetime
    metadata: dict[str, Any]
    selected_branch: Optional[str] = None
    insights: list[dict[str, Any]] = field(default_factory=list)


class ParallelRealitySimulator(CoreInterface):
    """
    Enhanced parallel reality simulation for dream consciousness.

    This simulator creates and explores alternative realities based on
    different decision points, quantum probabilities, and creative variations.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """Initialize parallel reality simulator"""
        self.config = config or {}
        self.operational = False

        # Service dependencies
        self.memory_service = None
        self.consciousness_service = None
        self.guardian_service = None
        self.dream_engine = None
        self.safety_framework = None

        # Simulation state
        self.active_simulations: dict[str, RealitySimulation] = {}
        self.reality_tree: dict[str, list[str]] = defaultdict(list)  # parent -> children
        self.qi_seed = random.Random(self.config.get("qi_seed", 42))

        # Configuration
        self.max_branches_per_reality = self.config.get("max_branches", 10)
        self.max_depth = self.config.get("max_depth", 5)
        self.min_probability = self.config.get("min_probability", 0.01)
        self.ethical_threshold = self.config.get("ethical_threshold", 0.3)

        # Performance metrics
        self.metrics = {
            "simulations_created": 0,
            "branches_explored": 0,
            "realities_collapsed": 0,
            "insights_generated": 0,
            "average_branches_per_simulation": 0.0,
        }

    async def initialize(self) -> None:
        """Initialize simulator and dependencies"""
        try:
            logger.info("Initializing Parallel Reality Simulator...")

            # Get service dependencies
            self.memory_service = get_service("memory_service")
            self.consciousness_service = get_service("consciousness_service")
            self.guardian_service = get_service("guardian_service")
            self.dream_engine = get_service("dream_engine")

            # Initialize safety framework
            safety_level = SafetyLevel(self.config.get("safety_level", "standard"))
            self.safety_framework = ParallelRealitySafetyFramework(
                config={
                    "safety_level": safety_level.value,
                    "drift_threshold": self.config.get("drift_threshold", 0.7),
                    "hallucination_threshold": self.config.get("hallucination_threshold", 0.6),
                    "auto_correct": self.config.get("auto_correct", True),
                }
            )
            await self.safety_framework.initialize()

            # Register this service
            register_service("parallel_reality_simulator", self, singleton=True)

            self.operational = True
            logger.info("Parallel Reality Simulator initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize simulator: {e}")
            raise LukhasError(f"Initialization failed: {e}")

    async def create_simulation(
        self,
        origin_scenario: dict[str, Any],
        reality_types: Optional[list[RealityType]] = None,
        branch_count: int = 5,
    ) -> RealitySimulation:
        """
        Create new parallel reality simulation.

        Args:
            origin_scenario: Starting reality state
            reality_types: Types of realities to explore
            branch_count: Number of initial branches

        Returns:
            RealitySimulation with initial branches
        """
        if not self.operational:
            raise LukhasError("Simulator not operational")

        # Default to all reality types if none specified
        if not reality_types:
            reality_types = list(RealityType)

        # Create simulation
        simulation = RealitySimulation(
            simulation_id=f"sim_{uuid.uuid4().hex[:8]}",
            origin_reality=origin_scenario,
            branches=[],
            start_time=datetime.now(timezone.utc),
            metadata={
                "reality_types": [rt.value for rt in reality_types],
                "branch_count": branch_count,
            },
        )

        # Create initial branches
        for i in range(min(branch_count, self.max_branches_per_reality)):
            reality_type = reality_types[i % len(reality_types)]
            branch = await self._create_branch(
                origin_scenario,
                None,
                reality_type,  # No parent for initial branches
            )
            simulation.branches.append(branch)
            self.reality_tree[branch.branch_id] = []

        # Store simulation
        self.active_simulations[simulation.simulation_id] = simulation

        # Update metrics
        self.metrics["simulations_created"] += 1
        self.metrics["branches_explored"] += len(simulation.branches)
        self._update_average_branches()

        # Store in memory if significant
        if self.memory_service:
            await self._store_simulation_memory(simulation, "created")

        logger.info(f"Created simulation {simulation.simulation_id} with {len(simulation.branches)} branches")
        return simulation

    async def _create_branch(
        self,
        base_state: dict[str, Any],
        parent_id: Optional[str],
        reality_type: RealityType,
    ) -> RealityBranch:
        """Create single reality branch"""
        branch_id = f"branch_{uuid.uuid4().hex[:8]}"

        # Generate divergence based on reality type
        divergence = await self._generate_divergence(base_state, reality_type)

        # Calculate probability
        probability = self._calculate_branch_probability(divergence, reality_type)

        # Apply divergence to create new state
        new_state = await self._apply_divergence(base_state, divergence)

        # Validate ethics if guardian available
        ethical_score = 1.0
        if self.guardian_service:
            validation = await self.guardian_service.validate_action(
                {"type": "reality_branch", "state": new_state}, {"simulation": True}
            )
            ethical_score = validation.get("confidence", 1.0) if validation.get("approved") else 0.0

        branch = RealityBranch(
            branch_id=branch_id,
            parent_id=parent_id,
            reality_type=reality_type,
            divergence_point=divergence,
            probability=probability,
            state=new_state,
            timestamp=datetime.now(timezone.utc),
            ethical_score=ethical_score,
        )

        # Safety validation
        if self.safety_framework:
            is_safe, hallucination = await self.safety_framework.validate_reality_branch(branch, base_state)

            if not is_safe:
                logger.warning(
                    f"Branch {branch_id} failed safety validation: {hallucination.hallucination_type.value if hallucination else 'unknown'}"
                )
                if hallucination and hallucination.severity > 0.8:
                    # Reject high-severity hallucinations
                    raise ValidationError(f"Reality branch rejected: {hallucination.recommended_action}")
                # For lower severity, continue but mark
                branch.state["_safety_warning"] = (
                    hallucination.evidence if hallucination else {"warning": "safety check failed"}
                )

        return branch

    async def _generate_divergence(self, base_state: dict[str, Any], reality_type: RealityType) -> dict[str, Any]:
        """Generate divergence point based on reality type"""
        divergence = {}

        if reality_type == RealityType.QUANTUM:
            # Quantum fluctuations in key parameters
            divergence = {
                "qi_shift": self.qi_seed.uniform(-1.0, 1.0),
                "affected_parameters": self._select_quantum_parameters(base_state),
                "coherence": self.qi_seed.uniform(0.5, 1.0),
            }

        elif reality_type == RealityType.Temporal:
            # Time-shifted scenarios
            divergence = {
                "time_shift": self.qi_seed.randint(-100, 100),
                "temporal_direction": self.qi_seed.choice(["past", "future"]),
                "causality_preserved": self.qi_seed.random() > 0.3,
            }

        elif reality_type == RealityType.CAUSAL:
            # Different causal chains
            divergence = {
                "causal_modification": self._generate_causal_change(base_state),
                "chain_depth": self.qi_seed.randint(1, 5),
                "butterfly_effect": self.qi_seed.uniform(0.1, 0.9),
            }

        elif reality_type == RealityType.ETHICAL:
            # Different ethical frameworks
            frameworks = ["deontological", "consequentialist", "virtue", "care"]
            divergence = {
                "ethical_framework": self.qi_seed.choice(frameworks),
                "value_shift": self.qi_seed.uniform(-0.5, 0.5),
                "priority_inversion": self.qi_seed.random() > 0.7,
            }

        elif reality_type == RealityType.CREATIVE:
            # Pure creative variations
            divergence = {
                "creative_seed": uuid.uuid4().hex[:8],
                "imagination_level": self.qi_seed.uniform(0.5, 1.0),
                "abstraction": self.qi_seed.choice(["concrete", "abstract", "surreal"]),
                "novelty_factor": self.qi_seed.uniform(0.3, 1.0),
            }

        elif reality_type == RealityType.PREDICTIVE:
            # Future predictions
            divergence = {
                "prediction_horizon": self.qi_seed.randint(1, 100),
                "confidence": self.qi_seed.uniform(0.3, 0.9),
                "key_events": self._predict_future_events(base_state),
            }

        return divergence

    def _select_quantum_parameters(self, state: dict[str, Any]) -> list[str]:
        """Select parameters for quantum variation"""
        all_params = list(state.keys())
        count = min(len(all_params), self.qi_seed.randint(1, 3))
        return self.qi_seed.sample(all_params, count)

    def _generate_causal_change(self, state: dict[str, Any]) -> dict[str, Any]:
        """Generate causal chain modification"""
        return {
            "modified_cause": self.qi_seed.choice(list(state.keys())),
            "new_effect": f"effect_{uuid.uuid4().hex[:4]}",
            "strength": self.qi_seed.uniform(0.3, 1.0),
        }

    def _predict_future_events(self, state: dict[str, Any]) -> list[dict[str, Any]]:
        """Predict future events based on current state"""
        event_count = self.qi_seed.randint(1, 5)
        events = []

        for i in range(event_count):
            events.append(
                {
                    "event_id": f"event_{i}",
                    "probability": self.qi_seed.uniform(0.3, 0.9),
                    "impact": self.qi_seed.choice(["low", "medium", "high"]),
                    "timeframe": self.qi_seed.randint(1, 100),
                }
            )

        return events

    def _calculate_branch_probability(self, divergence: dict[str, Any], reality_type: RealityType) -> float:
        """Calculate probability of reality branch"""
        base_probability = 0.5

        # Adjust based on reality type
        if reality_type == RealityType.QUANTUM:
            # Quantum coherence affects probability
            coherence = divergence.get("coherence", 0.5)
            base_probability *= coherence

        elif reality_type == RealityType.TEMPORAL:
            # Further time shifts are less probable
            time_shift = abs(divergence.get("time_shift", 0))
            base_probability *= 1.0 / (1.0 + time_shift / 100)

        elif reality_type == RealityType.CAUSAL:
            # Butterfly effect reduces probability
            butterfly = divergence.get("butterfly_effect", 0.5)
            base_probability *= 1.0 - butterfly * 0.5

        elif reality_type == RealityType.CREATIVE:
            # High novelty reduces probability
            novelty = divergence.get("novelty_factor", 0.5)
            base_probability *= 1.0 - novelty * 0.3

        elif reality_type == RealityType.PREDICTIVE:
            # Confidence affects probability
            confidence = divergence.get("confidence", 0.5)
            base_probability *= confidence

        return max(self.min_probability, min(1.0, base_probability))

    async def _apply_divergence(self, base_state: dict[str, Any], divergence: dict[str, Any]) -> dict[str, Any]:
        """Apply divergence to create new reality state"""
        new_state = base_state.copy()

        # Apply modifications based on divergence
        if "qi_shift" in divergence:
            shift = divergence["qi_shift"]
            for param in divergence.get("affected_parameters", []):
                if param in new_state and isinstance(new_state[param], (int, float)):
                    new_state[param] = new_state[param] * (1 + shift * 0.1)

        if "causal_modification" in divergence:
            cause_mod = divergence["causal_modification"]
            new_state[cause_mod["new_effect"]] = {
                "caused_by": cause_mod["modified_cause"],
                "strength": cause_mod["strength"],
            }

        # Add divergence metadata
        new_state["_divergence"] = divergence
        new_state["_reality_type"] = divergence.get("reality_type", "unknown")

        return new_state

    async def explore_branch(self, simulation_id: str, branch_id: str, depth: int = 1) -> list[RealityBranch]:
        """
        Explore a reality branch by creating sub-branches.

        Args:
            simulation_id: Simulation identifier
            branch_id: Branch to explore
            depth: How many levels to explore

        Returns:
            List of new branches created
        """
        if simulation_id not in self.active_simulations:
            raise ValidationError(f"Simulation {simulation_id} not found")

        simulation = self.active_simulations[simulation_id]
        parent_branch = None

        for branch in simulation.branches:
            if branch.branch_id == branch_id:
                parent_branch = branch
                break

        if not parent_branch:
            raise ValidationError(f"Branch {branch_id} not found")

        if not parent_branch.is_viable():
            logger.warning(f"Branch {branch_id} is not viable for exploration")
            return []

        new_branches = []

        # Create sub-branches
        for _ in range(min(3, self.max_branches_per_reality)):
            # Vary reality type for diversity
            reality_type = self.qi_seed.choice(list(RealityType))

            sub_branch = await self._create_branch(parent_branch.state, branch_id, reality_type)

            # Add causal chain
            sub_branch.causal_chain = [
                *parent_branch.causal_chain,
                {
                    "from": branch_id,
                    "to": sub_branch.branch_id,
                    "divergence": sub_branch.divergence_point,
                },
            ]

            simulation.branches.append(sub_branch)
            self.reality_tree[branch_id].append(sub_branch.branch_id)
            new_branches.append(sub_branch)

        # Recursive exploration if depth > 1
        if depth > 1:
            for sub_branch in new_branches:
                if sub_branch.is_viable():
                    await self.explore_branch(simulation_id, sub_branch.branch_id, depth - 1)

        # Update metrics
        self.metrics["branches_explored"] += len(new_branches)
        self._update_average_branches()

        # Create safety checkpoint after exploration
        if self.safety_framework and len(new_branches) > 0:
            # Calculate average drift for new branches
            drift_scores = []
            for new_branch in new_branches:
                drift_metrics = await self.safety_framework.calculate_drift_metrics(new_branch, parent_branch.state)
                drift_scores.append(drift_metrics.aggregate_drift)

            avg_drift = sum(drift_scores) / len(drift_scores) if drift_scores else 0.0

            # Create checkpoint if drift is acceptable
            if avg_drift < self.safety_framework.drift_threshold:
                checkpoint = await self.safety_framework.create_safety_checkpoint(
                    simulation_id,
                    {"branches": [b.__dict__ for b in new_branches]},
                    DriftMetrics(
                        semantic_drift=avg_drift,
                        structural_drift=0.0,
                        ethical_drift=0.0,
                        temporal_drift=0.0,
                        causal_drift=0.0,
                        aggregate_drift=avg_drift,
                        drift_velocity=0.0,
                        drift_acceleration=0.0,
                    ),
                )
                logger.debug(f"Created safety checkpoint: {checkpoint.checkpoint_id}")

        return new_branches

    async def collapse_reality(
        self, simulation_id: str, selection_criteria: Optional[dict[str, Any]] = None
    ) -> RealityBranch:
        """
        Collapse parallel realities to select one branch.

        Args:
            simulation_id: Simulation to collapse
            selection_criteria: Criteria for selection

        Returns:
            Selected reality branch
        """
        if simulation_id not in self.active_simulations:
            raise ValidationError(f"Simulation {simulation_id} not found")

        simulation = self.active_simulations[simulation_id]

        # Default criteria
        if not selection_criteria:
            selection_criteria = {
                "maximize": "probability",
                "ethical_minimum": self.ethical_threshold,
            }

        # Filter viable branches
        viable_branches = [b for b in simulation.branches if b.is_viable()]

        if not viable_branches:
            raise LukhasError("No viable branches to collapse")

        # Validate consensus if safety framework available
        if self.safety_framework and len(viable_branches) > 3:
            # Check consensus on key properties
            consensus_properties = ["probability", "ethical_score"]
            for prop in consensus_properties:
                consensus_reached, score = await self.safety_framework.validate_consensus(viable_branches, prop)
                if not consensus_reached:
                    logger.warning(f"Low consensus on {prop}: {score:.3f}")

        # Apply selection criteria
        if selection_criteria.get("maximize") == "probability":
            selected = max(viable_branches, key=lambda b: b.probability)
        elif selection_criteria.get("maximize") == "ethical_score":
            selected = max(viable_branches, key=lambda b: b.ethical_score)
        elif selection_criteria.get("maximize") == "creativity":
            creative_branches = [b for b in viable_branches if b.reality_type == RealityType.CREATIVE]
            selected = max(creative_branches, key=lambda b: b.probability) if creative_branches else viable_branches[0]
        else:
            # Random weighted selection
            weights = [b.probability for b in viable_branches]
            selected = self.qi_seed.choices(viable_branches, weights=weights)[0]

        # Mark selection
        simulation.selected_branch = selected.branch_id

        # Generate insights
        insights = await self._generate_collapse_insights(simulation, selected)
        simulation.insights.extend(insights)

        # Update metrics
        self.metrics["realities_collapsed"] += 1
        self.metrics["insights_generated"] += len(insights)

        # Store collapse in memory
        if self.memory_service:
            await self._store_simulation_memory(simulation, "collapsed", selected)

        logger.info(f"Collapsed simulation {simulation_id} to branch {selected.branch_id}")
        return selected

    async def _generate_collapse_insights(
        self, simulation: RealitySimulation, selected: RealityBranch
    ) -> list[dict[str, Any]]:
        """Generate insights from reality collapse"""
        insights = []

        # Compare selected to other branches
        other_branches = [b for b in simulation.branches if b.branch_id != selected.branch_id]

        # Probability insight
        avg_probability = sum(b.probability for b in simulation.branches) / len(simulation.branches)
        insights.append(
            {
                "type": "probability_analysis",
                "selected_probability": selected.probability,
                "average_probability": avg_probability,
                "percentile": (
                    sum(1 for b in other_branches if b.probability < selected.probability) / len(other_branches)
                    if other_branches
                    else 1.0
                ),
            }
        )

        # Ethical insight
        if selected.ethical_score < 1.0:
            insights.append(
                {
                    "type": "ethical_compromise",
                    "ethical_score": selected.ethical_score,
                    "compromises": self._identify_ethical_compromises(selected),
                }
            )

        # Reality type distribution
        type_counts = defaultdict(int)
        for branch in simulation.branches:
            type_counts[branch.reality_type.value] += 1

        insights.append(
            {
                "type": "reality_distribution",
                "selected_type": selected.reality_type.value,
                "distribution": dict(type_counts),
                "diversity_score": len(type_counts) / len(RealityType),
            }
        )

        # Causal chain insight
        if selected.causal_chain:
            insights.append(
                {
                    "type": "causal_analysis",
                    "chain_length": len(selected.causal_chain),
                    "key_divergences": self._extract_key_divergences(selected.causal_chain),
                }
            )

        return insights

    def _identify_ethical_compromises(self, branch: RealityBranch) -> list[str]:
        """Identify ethical compromises in branch"""
        compromises = []

        if branch.ethical_score < 0.5:
            compromises.append("significant_ethical_concerns")
        elif branch.ethical_score < 0.8:
            compromises.append("minor_ethical_tensions")

        if branch.reality_type == RealityType.ETHICAL:
            divergence = branch.divergence_point
            if divergence.get("priority_inversion"):
                compromises.append("value_priority_inversion")

        return compromises

    def _extract_key_divergences(self, causal_chain: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Extract key divergence points from causal chain"""
        key_divergences = []

        for link in causal_chain:
            divergence = link.get("divergence", {})

            # Identify significant divergences
            if divergence.get("butterfly_effect", 0) > 0.7:
                key_divergences.append(
                    {
                        "type": "high_butterfly_effect",
                        "magnitude": divergence["butterfly_effect"],
                    }
                )

            if divergence.get("qi_shift", 0) > 0.5:
                key_divergences.append(
                    {
                        "type": "qi_fluctuation",
                        "shift": divergence["qi_shift"],
                    }
                )

        return key_divergences

    async def merge_realities(self, simulation_id: str, branch_ids: list[str]) -> RealityBranch:
        """
        Merge multiple reality branches into hybrid reality.

        Args:
            simulation_id: Simulation containing branches
            branch_ids: Branches to merge

        Returns:
            New merged reality branch
        """
        if simulation_id not in self.active_simulations:
            raise ValidationError(f"Simulation {simulation_id} not found")

        simulation = self.active_simulations[simulation_id]

        # Find branches to merge
        branches_to_merge = []
        for branch in simulation.branches:
            if branch.branch_id in branch_ids:
                branches_to_merge.append(branch)

        if len(branches_to_merge) < 2:
            raise ValidationError("Need at least 2 branches to merge")

        # Create merged state
        merged_state = await self._merge_states([b.state for b in branches_to_merge])

        # Calculate merged probability (geometric mean)
        merged_probability = 1.0
        for branch in branches_to_merge:
            merged_probability *= branch.probability
        merged_probability = merged_probability ** (1.0 / len(branches_to_merge))

        # Average ethical scores
        merged_ethical = sum(b.ethical_score for b in branches_to_merge) / len(branches_to_merge)

        # Create merged branch
        merged_branch = RealityBranch(
            branch_id=f"merged_{uuid.uuid4().hex[:8]}",
            parent_id=None,  # Multiple parents
            reality_type=RealityType.CREATIVE,  # Merged realities are creative
            divergence_point={"merge_sources": branch_ids},
            probability=merged_probability,
            state=merged_state,
            timestamp=datetime.now(timezone.utc),
            ethical_score=merged_ethical,
        )

        # Combine causal chains
        for branch in branches_to_merge:
            merged_branch.causal_chain.extend(branch.causal_chain)

            # Add entry for each branch being merged
            branch_merge_event = {
                "event_type": "branch_merged",
                "branch_id": branch.branch_id,
                "timestamp": branch.timestamp.isoformat(),
                "probability": branch.probability,
                "ethical_score": branch.ethical_score,
                "reality_type": branch.reality_type.value,
            }
            merged_branch.causal_chain.append(branch_merge_event)

        # Add overall merge event to causal chain
        merge_event = {
            "event_type": "reality_merge",
            "timestamp": merged_branch.timestamp.isoformat(),
            "merged_branches": branch_ids,
            "branch_count": len(branches_to_merge),
            "merged_probability": merged_probability,
            "merged_ethical_score": merged_ethical,
        }
        merged_branch.causal_chain.append(merge_event)

        # Add to simulation
        simulation.branches.append(merged_branch)

        logger.info(f"Merged {len(branch_ids)} branches into {merged_branch.branch_id}")
        return merged_branch

    async def _merge_states(self, states: list[dict[str, Any]]) -> dict[str, Any]:
        """Merge multiple reality states"""
        merged = {}

        # Collect all keys
        all_keys = set()
        for state in states:
            all_keys.update(state.keys())

        # Merge each key
        for key in all_keys:
            values = [s.get(key) for s in states if key in s]

            if not values:
                continue

            # Merge strategy based on value type
            if all(isinstance(v, (int, float)) for v in values):
                # Average numerical values
                merged[key] = sum(values) / len(values)
            elif all(isinstance(v, str) for v in values):
                # Concatenate strings
                merged[key] = " | ".join(values)
            elif all(isinstance(v, list) for v in values):
                # Combine lists
                merged[key] = []
                for v in values:
                    merged[key].extend(v)
            elif all(isinstance(v, dict) for v in values):
                # Recursively merge dicts
                merged[key] = await self._merge_states(values)
            else:
                # Take first non-None value
                merged[key] = next((v for v in values if v is not None), None)

        return merged

    async def _store_simulation_memory(
        self,
        simulation: RealitySimulation,
        event_type: str,
        selected_branch: Optional[RealityBranch] = None,
    ) -> None:
        """Store simulation event in memory"""
        memory_content = {
            "simulation_id": simulation.simulation_id,
            "event_type": event_type,
            "branch_count": len(simulation.branches),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if selected_branch:
            memory_content["selected_branch"] = {
                "branch_id": selected_branch.branch_id,
                "reality_type": selected_branch.reality_type.value,
                "probability": selected_branch.probability,
                "ethical_score": selected_branch.ethical_score,
            }

        if simulation.insights:
            memory_content["insights"] = simulation.insights

        try:
            from candidate.core.interfaces.memory_interface import MemoryType

            memory_id = await self.memory_service.store(
                content=memory_content,
                memory_type=MemoryType.SEMANTIC,
                metadata={
                    "module": "parallel_reality_simulator",
                    "significance": 0.7 if event_type == "collapsed" else 0.5,
                },
            )

            # Track memory in simulation
            if selected_branch:
                selected_branch.memory_traces.append(memory_id)

        except Exception as e:
            logger.warning(f"Failed to store simulation memory: {e}")

    def _update_average_branches(self) -> None:
        """Update average branches per simulation metric"""
        if self.metrics["simulations_created"] > 0:
            self.metrics["average_branches_per_simulation"] = (
                self.metrics["branches_explored"] / self.metrics["simulations_created"]
            )

    # Required interface methods

    async def process(self, data: dict[str, Any]) -> dict[str, Any]:
        """Process request through simulator"""
        if not self.operational:
            raise LukhasError("Simulator not operational")

        action = data.get("action", "create")

        if action == "create":
            simulation = await self.create_simulation(
                origin_scenario=data.get("scenario", {}),
                reality_types=data.get("reality_types"),
                branch_count=data.get("branch_count", 5),
            )
            return {
                "simulation_id": simulation.simulation_id,
                "branches": len(simulation.branches),
                "origin": simulation.origin_reality,
            }

        elif action == "explore":
            branches = await self.explore_branch(
                simulation_id=data["simulation_id"],
                branch_id=data["branch_id"],
                depth=data.get("depth", 1),
            )
            return {
                "new_branches": len(branches),
                "branch_ids": [b.branch_id for b in branches],
            }

        elif action == "collapse":
            selected = await self.collapse_reality(
                simulation_id=data["simulation_id"],
                selection_criteria=data.get("criteria"),
            )
            return {
                "selected_branch": selected.branch_id,
                "probability": selected.probability,
                "ethical_score": selected.ethical_score,
                "insights": self.active_simulations[data["simulation_id"]].insights,
            }

        else:
            raise ValidationError(f"Unknown action: {action}")

    async def handle_glyph(self, token: GLYPHToken) -> GLYPHToken:
        """Handle GLYPH communication"""
        response_payload = {}

        if token.symbol == GLYPHSymbol.DREAM:
            # Create dream-based reality simulation
            scenario = token.payload.get("dream_scenario", {})
            simulation = await self.create_simulation(
                origin_scenario=scenario,
                reality_types=[RealityType.CREATIVE, RealityType.QUANTUM],
                branch_count=7,
            )
            response_payload = {
                "simulation_created": True,
                "simulation_id": simulation.simulation_id,
                "branch_count": len(simulation.branches),
            }

        elif token.symbol == GLYPHSymbol.QUERY:
            # Query simulation status
            sim_id = token.payload.get("simulation_id")
            if sim_id and sim_id in self.active_simulations:
                sim = self.active_simulations[sim_id]
                response_payload = {
                    "exists": True,
                    "branches": len(sim.branches),
                    "selected": sim.selected_branch,
                    "has_insights": len(sim.insights) > 0,
                }
            else:
                response_payload = {"exists": False}

        else:
            response_payload = {"error": f"Unsupported symbol: {token.symbol}"}

        return GLYPHToken(
            symbol=GLYPHSymbol.ACKNOWLEDGE,
            source="parallel_reality_simulator",
            target=token.source,
            payload=response_payload,
        )

    async def get_status(self) -> dict[str, Any]:
        """Get simulator status"""
        return {
            "operational": self.operational,
            "health_score": 1.0 if self.operational else 0.0,
            "active_simulations": len(self.active_simulations),
            "total_branches": sum(len(s.branches) for s in self.active_simulations.values()),
            "metrics": self.metrics,
            "config": {
                "max_branches": self.max_branches_per_reality,
                "max_depth": self.max_depth,
                "ethical_threshold": self.ethical_threshold,
            },
        }


# Example usage
async def demonstrate_parallel_reality():
    """Demonstrate parallel reality simulation"""
    # Initialize simulator
    simulator = ParallelRealitySimulator(config={"max_branches": 10, "ethical_threshold": 0.4})

    # Mock services for demo
    from unittest.mock import AsyncMock, Mock

    mock_memory = Mock()
    mock_memory.store = AsyncMock(return_value="mem_123")

    mock_guardian = Mock()
    mock_guardian.validate_action = AsyncMock(return_value={"approved": True, "confidence": 0.9})

    from candidate.core.interfaces.dependency_injection import register_service

    register_service("memory_service", mock_memory)
    register_service("guardian_service", mock_guardian)

    await simulator.initialize()

    # Create simulation
    print("Creating parallel reality simulation...")
    simulation = await simulator.create_simulation(
        origin_scenario={
            "context": "decision_point",
            "options": ["path_a", "path_b", "path_c"],
            "constraints": ["time_limited", "resource_bounded"],
            "goal": "optimal_outcome",
        },
        reality_types=[RealityType.QUANTUM, RealityType.CAUSAL, RealityType.PREDICTIVE],
        branch_count=5,
    )

    print(f"\nSimulation created: {simulation.simulation_id}")
    print(f"Initial branches: {len(simulation.branches)}")

    # Explore a branch
    if simulation.branches:
        branch_to_explore = simulation.branches[0]
        print(f"\nExploring branch: {branch_to_explore.branch_id}")
        print(f"Reality type: {branch_to_explore.reality_type.value}")
        print(f"Probability: {branch_to_explore.probability:.3f}")

        new_branches = await simulator.explore_branch(simulation.simulation_id, branch_to_explore.branch_id, depth=2)
        print(f"Created {len(new_branches)} sub-branches")

    # Collapse reality
    print("\nCollapsing parallel realities...")
    selected = await simulator.collapse_reality(
        simulation.simulation_id, selection_criteria={"maximize": "probability"}
    )

    print(f"\nSelected branch: {selected.branch_id}")
    print(f"Final probability: {selected.probability:.3f}")
    print(f"Ethical score: {selected.ethical_score:.3f}")

    # Show insights
    if simulation.insights:
        print("\nInsights generated:")
        for insight in simulation.insights:
            print(f"- {insight['type']}: {insight}")

    # Final status
    status = await simulator.get_status()
    print(f"\nSimulator metrics: {status['metrics']}")


if __name__ == "__main__":
    asyncio.run(demonstrate_parallel_reality())
