import logging

#!/usr/bin/env python3
"""

#TAG:consciousness
#TAG:reflection
#TAG:neuroplastic
#TAG:colony


🧠 Meta-Learning Enhancement Integration Adapter
Bridges the Meta-Learning Enhancement System with the Unified AI Enhancement Framework

This adapter provides standardized interfaces for:
- Dynamic learning rate adjustment
- Federated learning coordination
- Symbolic feedback loops
- Performance monitoring and dashboard integration

Author: lukhas AI Enhancement Team
Date: 2025-01-27
"""
import random
import streamlit as st
from datetime import timezone

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import numpy as np

logger = logging.getLogger("MetaLearningAdapter", timezone)


class LearningPhase(Enum):
    """Phases of meta-learning enhancement"""

    EXPLORATION = "exploration"
    ADAPTATION = "adaptation"
    CONVERGENCE = "convergence"
    STABILIZATION = "stabilization"
    OPTIMIZATION = "optimization"


class FederatedState(Enum):
    """States of federated learning coordination"""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    SYNCHRONIZED = "synchronized"
    LEARNING = "learning"
    CONVERGING = "converging"
    COMPLETE = "complete"


@dataclass
class MetaLearningMetrics:
    """Comprehensive metrics for meta-learning performance"""

    # Learning rate metrics
    current_learning_rate: float = 1e-3
    learning_rate_adaptation: float = 0.0
    learning_rate_stability: float = 1.0
    optimal_rate_distance: float = 0.0

    # Federated learning metrics
    federated_nodes_active: int = 0
    federated_convergence: float = 0.0
    consensus_quality: float = 0.0
    communication_efficiency: float = 0.0

    # Symbolic feedback metrics
    symbolic_feedback_quality: float = 0.0
    intent_node_integration: float = 0.0
    memoria_coupling: float = 0.0
    dream_system_coherence: float = 0.0

    # Performance dashboard metrics
    overall_performance: float = 0.0
    adaptation_speed: float = 0.0
    stability_score: float = 0.0
    enhancement_factor: float = 1.0

    # Timestamp and phase tracking
    timestamp: datetime = field(default_factory=datetime.now)
    current_phase: LearningPhase = LearningPhase.EXPLORATION
    federated_state: FederatedState = FederatedState.DISCONNECTED


@dataclass
class LearningRateBounds:
    """Bounds and constraints for learning rate adaptation"""

    min_rate: float = 1e-6
    max_rate: float = 1e-2
    optimal_rate: float = 1e-3
    adaptation_factor: float = 1.1
    decay_factor: float = 0.95
    momentum: float = 0.9


class MetaLearningEnhancementAdapter:
    """
    Integration adapter for the Meta-Learning Enhancement System

    Provides standardized interfaces for adaptive learning, federated coordination,
    and symbolic feedback integration within the unified AI framework
    """

    def __init__(self, meta_learning_system, orchestrator=None):
        """Initialize the Meta-Learning Enhancement adapter"""
        self.meta_learning_system = meta_learning_system
        self.orchestrator = orchestrator
        self.current_metrics = MetaLearningMetrics()
        self.learning_rate_bounds = LearningRateBounds()

        # Performance tracking
        self.performance_history = []
        self.adaptation_history = []
        self.federated_history = []

        # System state
        self.active_learning_nodes = []
        self.symbolic_feedback_buffer = []
        self.intent_node_cache = {}
        self.memoria_state = {}

        # Performance counters
        self.total_adaptations = 0
        self.successful_adaptations = 0
        self.federated_cycles = 0
        self.symbolic_feedback_cycles = 0

        logger.info("Meta-Learning Enhancement adapter initialized")

    async def initialize(self) -> bool:
        """Initialize the meta-learning enhancement system"""
        try:
            logger.info("🧠 Initializing Meta-Learning Enhancement System")

            # Initialize underlying meta-learning system
            if hasattr(self.meta_learning_system, "initialize"):
                await self.meta_learning_system.initialize()

            # Setup learning rate management
            await self._initialize_learning_rate_system()

            # Setup federated learning coordination
            await self._initialize_federated_system()

            # Setup symbolic feedback loops
            await self._initialize_symbolic_feedback()

            # Setup performance monitoring
            await self._initialize_performance_monitoring()

            self.current_metrics.current_phase = LearningPhase.ADAPTATION
            self.current_metrics.federated_state = FederatedState.CONNECTING

            logger.info("✅ Meta-Learning Enhancement System initialized successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize Meta-Learning Enhancement System: {e}")
            return False

    async def get_current_metrics(self) -> dict[str, Any]:
        """Get current meta-learning metrics"""
        try:
            # Update metrics from underlying system
            await self._update_current_metrics()

            return {
                # Learning rate metrics
                "learning_rate_adaptation": self.current_metrics.learning_rate_adaptation,
                "current_learning_rate": self.current_metrics.current_learning_rate,
                "learning_rate_stability": self.current_metrics.learning_rate_stability,
                "optimal_distance": self.current_metrics.optimal_rate_distance,
                # Federated learning metrics
                "federated_convergence": self.current_metrics.federated_convergence,
                "active_nodes": self.current_metrics.federated_nodes_active,
                "consensus_quality": self.current_metrics.consensus_quality,
                "communication_efficiency": self.current_metrics.communication_efficiency,
                # Symbolic feedback metrics
                "symbolic_feedback_quality": self.current_metrics.symbolic_feedback_quality,
                "intent_integration": self.current_metrics.intent_node_integration,
                "memoria_coupling": self.current_metrics.memoria_coupling,
                "dream_coherence": self.current_metrics.dream_system_coherence,
                # Overall performance
                "overall_performance": self.current_metrics.overall_performance,
                "adaptation_speed": self.current_metrics.adaptation_speed,
                "stability_score": self.current_metrics.stability_score,
                "enhancement_factor": self.current_metrics.enhancement_factor,
                # State information
                "current_phase": self.current_metrics.current_phase.value,
                "federated_state": self.current_metrics.federated_state.value,
                "timestamp": self.current_metrics.timestamp.isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to get current metrics: {e}")
            return self._get_default_metrics()

    async def enhance_learning(
        self, current_metrics: dict[str, Any], system_feedback: dict[str, Any]
    ) -> dict[str, Any]:
        """Enhance learning based on current metrics and system feedback"""
        try:
            logger.info("🚀 Starting meta-learning enhancement cycle")

            enhancement_results = {}

            # 1. Dynamic Learning Rate Adjustment
            rate_results = await self._enhance_learning_rate(current_metrics, system_feedback)
            enhancement_results["learning_rate"] = rate_results

            # 2. Federated Learning Coordination
            federated_results = await self._enhance_federated_learning(current_metrics, system_feedback)
            enhancement_results["federated"] = federated_results

            # 3. Symbolic Feedback Processing
            symbolic_results = await self._enhance_symbolic_feedback(current_metrics, system_feedback)
            enhancement_results["symbolic"] = symbolic_results

            # 4. Performance Dashboard Update
            dashboard_results = await self._update_performance_dashboard(enhancement_results)
            enhancement_results["dashboard"] = dashboard_results

            # 5. Calculate overall enhancement metrics
            overall_enhancement = self._calculate_overall_enhancement(enhancement_results)
            enhancement_results["overall"] = overall_enhancement

            # Update performance tracking
            self.total_adaptations += 1
            if overall_enhancement.get("success", False):
                self.successful_adaptations += 1

            # Update phase based on results
            await self._update_learning_phase(enhancement_results)

            logger.info(f"✅ Meta-learning enhancement completed: {overall_enhancement.get('adaptation', 0.0)}:.3f}")
            return enhancement_results

        except Exception as e:
            logger.error(f"❌ Meta-learning enhancement failed: {e}")
            return {"success": False, "error": str(e), "adaptation": 0.0}

    async def process_biological_feedback(self, topology_features: dict[str, Any]) -> dict[str, Any]:
        """Process biological feedback from Crista Optimizer"""
        try:
            logger.debug("Processing biological feedback from Crista Optimizer")

            # Extract relevant biological features
            cristae_density = topology_features.get("cristae_density", 0.0)
            membrane_potential = topology_features.get("membrane_potential", -70.0)
            atp_efficiency = topology_features.get("atp_efficiency", 0.0)

            # Convert biological signals to learning signals
            bio_learning_signals = {
                "energy_availability": atp_efficiency,
                "system_stability": self._normalize_membrane_potential(membrane_potential),
                "resource_utilization": cristae_density,
                "metabolic_efficiency": (atp_efficiency + cristae_density) / 2.0,
            }

            # Adapt learning parameters based on biological state
            adaptation_suggestions = await self._adapt_to_biological_state(bio_learning_signals)

            # Update symbolic feedback with biological insights
            await self._integrate_biological_symbolic_feedback(bio_learning_signals)

            return {
                "bio_signals_processed": len(bio_learning_signals),
                "adaptation_suggestions": adaptation_suggestions,
                "biological_integration": True,
                "energy_informed_learning": bio_learning_signals["energy_availability"] > 0.5,
            }

        except Exception as e:
            logger.error(f"Failed to process biological feedback: {e}")
            return {"success": False, "error": str(e)}

    async def _enhance_learning_rate(self, metrics: dict[str, Any], feedback: dict[str, Any]) -> dict[str, Any]:
        """Enhance learning rate based on current performance"""
        current_rate = self.current_metrics.current_learning_rate
        performance = metrics.get("overall_performance", 0.5)
        stability = feedback.get("bio_orchestrator", {}).get("stability", 0.5)

        # Calculate adaptive learning rate
        if performance > 0.8 and stability > 0.7:
            # High performance and stability - can increase learning rate
            new_rate = min(
                current_rate * self.learning_rate_bounds.adaptation_factor,
                self.learning_rate_bounds.max_rate,
            )
            adaptation_type = "aggressive"
        elif performance < 0.3 or stability < 0.3:
            # Low performance or instability - decrease learning rate
            new_rate = max(
                current_rate * self.learning_rate_bounds.decay_factor,
                self.learning_rate_bounds.min_rate,
            )
            adaptation_type = "conservative"
        else:
            # Moderate performance - gentle adjustment toward optimal
            optimal_rate = self.learning_rate_bounds.optimal_rate
            new_rate = current_rate + 0.1 * (optimal_rate - current_rate)
            adaptation_type = "moderate"

        # Apply learning rate update
        rate_change = new_rate - current_rate
        self.current_metrics.current_learning_rate = new_rate
        self.current_metrics.learning_rate_adaptation = abs(rate_change) / current_rate

        # Update stability metric
        self.current_metrics.learning_rate_stability = self._calculate_rate_stability()

        return {
            "success": True,
            "old_rate": current_rate,
            "new_rate": new_rate,
            "rate_change": rate_change,
            "adaptation_type": adaptation_type,
            "adaptation": self.current_metrics.learning_rate_adaptation,
        }

    async def _enhance_federated_learning(self, metrics: dict[str, Any], feedback: dict[str, Any]) -> dict[str, Any]:
        """Enhance federated learning coordination"""
        # Simulate federated node coordination
        target_nodes = 5
        current_nodes = len(self.active_learning_nodes)

        # Attempt to connect to more nodes if needed
        if current_nodes < target_nodes:
            new_nodes = await self._connect_federated_nodes(target_nodes - current_nodes)
            self.active_learning_nodes.extend(new_nodes)

        # Calculate federated convergence
        if len(self.active_learning_nodes) > 0:
            convergence = await self._calculate_federated_convergence()
            consensus = await self._calculate_consensus_quality()
            communication_eff = await self._calculate_communication_efficiency()
        else:
            convergence = 0.0
            consensus = 0.0
            communication_eff = 0.0

        # Update metrics
        self.current_metrics.federated_nodes_active = len(self.active_learning_nodes)
        self.current_metrics.federated_convergence = convergence
        self.current_metrics.consensus_quality = consensus
        self.current_metrics.communication_efficiency = communication_eff

        # Update federated state
        if convergence > 0.9:
            self.current_metrics.federated_state = FederatedState.COMPLETE
        elif convergence > 0.7:
            self.current_metrics.federated_state = FederatedState.CONVERGING
        elif len(self.active_learning_nodes) > 0:
            self.current_metrics.federated_state = FederatedState.LEARNING
        else:
            self.current_metrics.federated_state = FederatedState.DISCONNECTED

        self.federated_cycles += 1

        return {
            "success": True,
            "active_nodes": len(self.active_learning_nodes),
            "convergence": convergence,
            "consensus_quality": consensus,
            "communication_efficiency": communication_eff,
            "federated_state": self.current_metrics.federated_state.value,
        }

    async def _enhance_symbolic_feedback(self, metrics: dict[str, Any], feedback: dict[str, Any]) -> dict[str, Any]:
        """Enhance symbolic feedback loops"""
        # Process intent node integration
        intent_integration = await self._process_intent_nodes(feedback)

        # Process memoria coupling
        memoria_coupling = await self._process_memoria_integration(feedback)

        # Process dream system coherence
        dream_coherence = await self._process_dream_coherence(feedback)

        # Calculate overall symbolic feedback quality
        symbolic_quality = (intent_integration + memoria_coupling + dream_coherence) / 3.0

        # Update metrics
        self.current_metrics.symbolic_feedback_quality = symbolic_quality
        self.current_metrics.intent_node_integration = intent_integration
        self.current_metrics.memoria_coupling = memoria_coupling
        self.current_metrics.dream_system_coherence = dream_coherence

        # Update symbolic feedback buffer
        feedback_entry = {
            "timestamp": datetime.now(timezone.utc),
            "symbolic_quality": symbolic_quality,
            "intent_integration": intent_integration,
            "memoria_coupling": memoria_coupling,
            "dream_coherence": dream_coherence,
        }

        self.symbolic_feedback_buffer.append(feedback_entry)

        # Keep buffer size manageable
        if len(self.symbolic_feedback_buffer) > 100:
            self.symbolic_feedback_buffer = self.symbolic_feedback_buffer[-50:]

        self.symbolic_feedback_cycles += 1

        return {
            "success": True,
            "symbolic_quality": symbolic_quality,
            "intent_integration": intent_integration,
            "memoria_coupling": memoria_coupling,
            "dream_coherence": dream_coherence,
            "feedback_buffer_size": len(self.symbolic_feedback_buffer),
        }

    async def _update_performance_dashboard(self, enhancement_results: dict[str, Any]) -> dict[str, Any]:
        """Update performance monitoring dashboard"""
        # Calculate overall performance metrics
        learning_rate_perf = enhancement_results.get("learning_rate", {}).get("adaptation", 0.0)
        federated_perf = enhancement_results.get("federated", {}).get("convergence", 0.0)
        symbolic_perf = enhancement_results.get("symbolic", {}).get("symbolic_quality", 0.0)

        # Weighted combination for overall performance
        overall_performance = 0.4 * learning_rate_perf + 0.3 * federated_perf + 0.3 * symbolic_perf

        # Calculate adaptation speed (rate of improvement)
        adaptation_speed = self._calculate_adaptation_speed()

        # Calculate stability score
        stability_score = self._calculate_overall_stability()

        # Calculate enhancement factor
        enhancement_factor = self._calculate_enhancement_factor(overall_performance)

        # Update metrics
        self.current_metrics.overall_performance = overall_performance
        self.current_metrics.adaptation_speed = adaptation_speed
        self.current_metrics.stability_score = stability_score
        self.current_metrics.enhancement_factor = enhancement_factor

        # Add to performance history
        performance_entry = {
            "timestamp": datetime.now(timezone.utc),
            "overall_performance": overall_performance,
            "adaptation_speed": adaptation_speed,
            "stability_score": stability_score,
            "enhancement_factor": enhancement_factor,
        }
        self.performance_history.append(performance_entry)

        # Keep history manageable
        if len(self.performance_history) > 200:
            self.performance_history = self.performance_history[-100:]

        return {
            "success": True,
            "overall_performance": overall_performance,
            "adaptation_speed": adaptation_speed,
            "stability_score": stability_score,
            "enhancement_factor": enhancement_factor,
            "history_length": len(self.performance_history),
        }

    async def get_performance_metrics(self) -> dict[str, Any]:
        """Get comprehensive performance metrics"""
        success_rate = self.successful_adaptations / max(self.total_adaptations, 1)

        return {
            "total_adaptations": self.total_adaptations,
            "successful_adaptations": self.successful_adaptations,
            "success_rate": success_rate,
            "federated_cycles": self.federated_cycles,
            "symbolic_cycles": self.symbolic_feedback_cycles,
            "current_learning_rate": self.current_metrics.current_learning_rate,
            "overall_performance": self.current_metrics.overall_performance,
            "adaptation_speed": self.current_metrics.adaptation_speed,
            "stability_score": self.current_metrics.stability_score,
            "enhancement_factor": self.current_metrics.enhancement_factor,
            "current_phase": self.current_metrics.current_phase.value,
            "federated_state": self.current_metrics.federated_state.value,
        }

    async def apply_optimization(self, action: str, parameters: dict[str, Any]) -> dict[str, Any]:
        """Apply a specific optimization action"""
        try:
            if action == "increase_learning_rate":
                rate_multiplier = parameters.get("rate_multiplier", 1.2)
                return await self._increase_learning_rate(rate_multiplier)
            elif action == "stabilize_federated_learning":
                stability_target = parameters.get("stability_target", 0.8)
                return await self._stabilize_federated_learning(stability_target)
            elif action == "enhance_symbolic_feedback":
                enhancement_factor = parameters.get("enhancement_factor", 1.1)
                return await self._enhance_symbolic_feedback_quality(enhancement_factor)
            else:
                logger.warning(f"Unknown optimization action: {action}")
                return {"success": False, "error": f"Unknown action: {action}"}

        except Exception as e:
            logger.error(f"Failed to apply optimization {action}: {e}")
            return {"success": False, "error": str(e)}

    # Helper methods and calculations

    async def _initialize_learning_rate_system(self) -> None:
        """Initialize learning rate management system"""
        # Set initial learning rate to optimal value
        self.current_metrics.current_learning_rate = self.learning_rate_bounds.optimal_rate
        self.current_metrics.learning_rate_stability = 1.0
        logger.debug("Learning rate system initialized")

    async def _initialize_federated_system(self) -> None:
        """Initialize federated learning coordination"""
        # Start with empty node list
        self.active_learning_nodes = []
        self.current_metrics.federated_state = FederatedState.DISCONNECTED
        logger.debug("Federated learning system initialized")

    async def _initialize_symbolic_feedback(self) -> None:
        """Initialize symbolic feedback loops"""
        self.symbolic_feedback_buffer = []
        self.intent_node_cache = {}
        self.memoria_state = {}
        logger.debug("Symbolic feedback system initialized")

    async def _initialize_performance_monitoring(self) -> None:
        """Initialize performance monitoring dashboard"""
        self.performance_history = []
        self.current_metrics.overall_performance = 0.5  # Start at neutral
        logger.debug("Performance monitoring initialized")

    async def _update_current_metrics(self) -> None:
        """Update current metrics from underlying system"""
        # Update timestamp
        self.current_metrics.timestamp = datetime.now(timezone.utc)

        # Calculate optimal rate distance
        current_rate = self.current_metrics.current_learning_rate
        optimal_rate = self.learning_rate_bounds.optimal_rate
        self.current_metrics.optimal_rate_distance = abs(current_rate - optimal_rate) / optimal_rate

    def _normalize_membrane_potential(self, potential: float) -> float:
        """Normalize membrane potential to 0-1 scale"""
        # Typical range is -90mV to -50mV, optimal around -70mV
        normalized = 1.0 - abs(potential + 70.0) / 20.0
        return max(0.0, min(1.0, normalized))

    async def _adapt_to_biological_state(self, bio_signals: dict[str, Any]) -> list[dict[str, Any]]:
        """Adapt learning parameters based on biological state"""
        suggestions = []

        energy_level = bio_signals.get("energy_availability", 0.0)
        stability = bio_signals.get("system_stability", 0.0)

        # High energy and stability - can be more aggressive
        if energy_level > 0.7 and stability > 0.7:
            suggestions.append(
                {
                    "type": "learning_rate",
                    "action": "increase",
                    "factor": 1.1,
                    "reason": "high_energy_stability",
                }
            )

        # Low energy or stability - be conservative
        elif energy_level < 0.3 or stability < 0.3:
            suggestions.append(
                {
                    "type": "learning_rate",
                    "action": "decrease",
                    "factor": 0.9,
                    "reason": "low_energy_or_stability",
                }
            )

        return suggestions

    async def _integrate_biological_symbolic_feedback(self, bio_signals: dict[str, Any]) -> None:
        """Integrate biological signals into symbolic feedback"""
        bio_symbolic_entry = {
            "timestamp": datetime.now(timezone.utc),
            "type": "biological_integration",
            "energy_availability": bio_signals.get("energy_availability", 0.0),
            "system_stability": bio_signals.get("system_stability", 0.0),
            "metabolic_efficiency": bio_signals.get("metabolic_efficiency", 0.0),
        }

        self.symbolic_feedback_buffer.append(bio_symbolic_entry)

    def _calculate_rate_stability(self) -> float:
        """Calculate learning rate stability over time"""
        if len(self.adaptation_history) < 2:
            return 1.0

        recent_rates = [
            entry.get("new_rate", self.current_metrics.current_learning_rate) for entry in self.adaptation_history[-10:]
        ]

        if len(recent_rates) < 2:
            return 1.0

        # Calculate coefficient of variation (lower is more stable)
        mean_rate = np.mean(recent_rates)
        std_rate = np.std(recent_rates)

        if mean_rate == 0:
            return 0.0

        cv = std_rate / mean_rate
        stability = max(0.0, 1.0 - cv)  # Convert to stability score (higher is better)

        return stability

    async def _connect_federated_nodes(self, num_nodes: int) -> list[dict[str, Any]]:
        """Simulate connecting to federated learning nodes"""
        new_nodes = []
        for i in range(num_nodes):
            node = {
                "id": f"node_{len(self.active_learning_nodes)} + i}",
                "status": "connected",
                "performance": np.random.uniform(0.6, 0.9),
                "last_update": datetime.now(timezone.utc),
            }
            new_nodes.append(node)

        return new_nodes

    async def _calculate_federated_convergence(self) -> float:
        """Calculate convergence across federated nodes"""
        if not self.active_learning_nodes:
            return 0.0

        # Simulate convergence calculation
        performances = [node.get("performance", 0.5) for node in self.active_learning_nodes]
        mean_perf = np.mean(performances)
        std_perf = np.std(performances)

        # Convergence is high when all nodes have similar (high) performance
        convergence = mean_perf * (1.0 - std_perf)
        return max(0.0, min(1.0, convergence))

    async def _calculate_consensus_quality(self) -> float:
        """Calculate consensus quality among federated nodes"""
        if not self.active_learning_nodes:
            return 0.0

        # Simulate consensus calculation based on node agreement
        return np.random.uniform(0.6, 0.95)  # Simulated consensus

    async def _calculate_communication_efficiency(self) -> float:
        """Calculate communication efficiency in federated network"""
        if not self.active_learning_nodes:
            return 0.0

        # Higher efficiency with more active nodes (up to a point)
        num_nodes = len(self.active_learning_nodes)
        optimal_nodes = 5

        if num_nodes <= optimal_nodes:
            efficiency = num_nodes / optimal_nodes
        else:
            # Diminishing returns with too many nodes
            efficiency = optimal_nodes / num_nodes

        return efficiency

    async def _process_intent_nodes(self, feedback: dict[str, Any]) -> float:
        """Process intent node integration"""
        # Simulate intent node processing
        return np.random.uniform(0.5, 0.9)

    async def _process_memoria_integration(self, feedback: dict[str, Any]) -> float:
        """Process memoria system integration"""
        # Simulate memoria coupling
        return np.random.uniform(0.6, 0.8)

    async def _process_dream_coherence(self, feedback: dict[str, Any]) -> float:
        """Process dream system coherence"""
        # Simulate dream system coherence
        return np.random.uniform(0.4, 0.9)

    def _calculate_adaptation_speed(self) -> float:
        """Calculate the speed of adaptation over time"""
        if len(self.performance_history) < 2:
            return 0.0

        recent_performances = [entry["overall_performance"] for entry in self.performance_history[-5:]]

        if len(recent_performances) < 2:
            return 0.0

        # Calculate rate of improvement
        improvements = np.diff(recent_performances)
        avg_improvement = np.mean(improvements)

        # Convert to speed metric (0-1 scale)
        speed = max(0.0, min(1.0, avg_improvement * 10 + 0.5))
        return speed

    def _calculate_overall_stability(self) -> float:
        """Calculate overall system stability"""
        rate_stability = self.current_metrics.learning_rate_stability

        # Add federated stability
        if self.current_metrics.federated_nodes_active > 0:
            federated_stability = self.current_metrics.consensus_quality
        else:
            federated_stability = 0.5  # Neutral when no federation

        # Add symbolic feedback stability
        if len(self.symbolic_feedback_buffer) > 0:
            recent_qualities = [entry.get("symbolic_quality", 0.5) for entry in self.symbolic_feedback_buffer[-10:]]
            symbolic_stability = 1.0 - np.std(recent_qualities) if len(recent_qualities) > 1 else 0.5
        else:
            symbolic_stability = 0.5

        # Weighted combination
        overall_stability = 0.4 * rate_stability + 0.3 * federated_stability + 0.3 * symbolic_stability

        return overall_stability

    def _calculate_enhancement_factor(self, performance: float) -> float:
        """Calculate enhancement factor based on performance"""
        # Enhancement factor represents how much the system is improved
        # Base is 1.0 (no enhancement), can go up to 2.0 (100% enhancement)
        base_factor = 1.0
        performance_bonus = performance  # 0-1 range
        enhancement_factor = base_factor + performance_bonus

        return enhancement_factor

    def _calculate_overall_enhancement(self, enhancement_results: dict[str, Any]) -> dict[str, Any]:
        """Calculate overall enhancement metrics from all components"""
        # Extract individual adaptation scores
        learning_adaptation = enhancement_results.get("learning_rate", {}).get("adaptation", 0.0)
        federated_adaptation = enhancement_results.get("federated", {}).get("convergence", 0.0)
        symbolic_adaptation = enhancement_results.get("symbolic", {}).get("symbolic_quality", 0.0)

        # Weighted overall adaptation
        overall_adaptation = 0.4 * learning_adaptation + 0.3 * federated_adaptation + 0.3 * symbolic_adaptation

        # Success criteria
        success = overall_adaptation > 0.5

        return {
            "success": success,
            "adaptation": overall_adaptation,
            "learning_contribution": learning_adaptation,
            "federated_contribution": federated_adaptation,
            "symbolic_contribution": symbolic_adaptation,
            "enhancement_quality": (
                "high" if overall_adaptation > 0.8 else "medium" if overall_adaptation > 0.5 else "low"
            ),
        }

    async def _update_learning_phase(self, enhancement_results: dict[str, Any]) -> None:
        """Update the current learning phase based on results"""
        overall_adaptation = enhancement_results.get("overall", {}).get("adaptation", 0.0)
        stability = self.current_metrics.stability_score

        if overall_adaptation > 0.9 and stability > 0.9:
            self.current_metrics.current_phase = LearningPhase.STABILIZATION
        elif overall_adaptation > 0.8:
            self.current_metrics.current_phase = LearningPhase.OPTIMIZATION
        elif overall_adaptation > 0.6:
            self.current_metrics.current_phase = LearningPhase.CONVERGENCE
        elif overall_adaptation > 0.3:
            self.current_metrics.current_phase = LearningPhase.ADAPTATION
        else:
            self.current_metrics.current_phase = LearningPhase.EXPLORATION

    async def _increase_learning_rate(self, multiplier: float) -> dict[str, Any]:
        """Increase learning rate by multiplier"""
        old_rate = self.current_metrics.current_learning_rate
        new_rate = min(old_rate * multiplier, self.learning_rate_bounds.max_rate)
        self.current_metrics.current_learning_rate = new_rate

        return {
            "success": True,
            "old_rate": old_rate,
            "new_rate": new_rate,
            "multiplier_applied": multiplier,
        }

    async def _stabilize_federated_learning(self, stability_target: float) -> dict[str, Any]:
        """Stabilize federated learning to target level"""
        # Attempt to improve consensus and convergence
        current_consensus = self.current_metrics.consensus_quality
        target_consensus = min(stability_target, 0.95)

        # Simulate stabilization effort
        improvement = (target_consensus - current_consensus) * 0.5
        new_consensus = current_consensus + improvement

        self.current_metrics.consensus_quality = new_consensus

        return {
            "success": True,
            "target_stability": stability_target,
            "achieved_stability": new_consensus,
            "improvement": improvement,
        }

    async def _enhance_symbolic_feedback_quality(self, enhancement_factor: float) -> dict[str, Any]:
        """Enhance symbolic feedback quality"""
        old_quality = self.current_metrics.symbolic_feedback_quality
        new_quality = min(old_quality * enhancement_factor, 1.0)
        self.current_metrics.symbolic_feedback_quality = new_quality

        return {
            "success": True,
            "old_quality": old_quality,
            "new_quality": new_quality,
            "enhancement_factor": enhancement_factor,
        }

    def _get_default_metrics(self) -> dict[str, Any]:
        """Get default metrics when system is unavailable"""
        return {
            "learning_rate_adaptation": 0.0,
            "current_learning_rate": 1e-3,
            "learning_rate_stability": 1.0,
            "optimal_distance": 0.0,
            "federated_convergence": 0.0,
            "active_nodes": 0,
            "consensus_quality": 0.0,
            "communication_efficiency": 0.0,
            "symbolic_feedback_quality": 0.0,
            "intent_integration": 0.0,
            "memoria_coupling": 0.0,
            "dream_coherence": 0.0,
            "overall_performance": 0.0,
            "adaptation_speed": 0.0,
            "stability_score": 0.0,
            "enhancement_factor": 1.0,
            "current_phase": "exploration",
            "federated_state": "disconnected",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
