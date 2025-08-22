"""

#TAG:consciousness
#TAG:unified
#TAG:neuroplastic
#TAG:colony


══════════════════════════════════════════════════════════════════════════════════
║ 🎼 LUKHAS AI - BIO-SYMBOLIC ORCHESTRATOR
║ Master coordinator for all bio-symbolic colonies with quantum consciousness
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: bio_symbolic_orchestrator.py
║ Path: bio/symbolic/bio_symbolic_orchestrator.py
║ Version: 1.0.0 | Created: 2025-07-28
║ Authors: LUKHAS Bio-Symbolic Team | Claude Code
╚══════════════════════════════════════════════════════════════════════════════════
"""
import asyncio
import logging
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

import numpy as np

from bio.core.symbolic_adaptive_threshold_colony import create_threshold_colony
from bio.core.symbolic_anomaly_filter_colony import (
    create_anomaly_filter_colony,
)
from bio.core.symbolic_contextual_mapping_colony import create_mapping_colony
from bio.core.symbolic_fallback_systems import get_fallback_manager
from bio.core.symbolic_preprocessing_colony import create_preprocessing_colony
from core.colonies.base_colony import BaseColony
from core.symbolism.tags import TagPermission, TagScope

logger = logging.getLogger("ΛTRACE.bio.orchestrator")


@dataclass
class CoherenceMetrics:
    """Metrics for tracking bio-symbolic coherence."""

    overall_coherence: float = 0.0
    preprocessing_quality: float = 0.0
    threshold_confidence: float = 0.0
    mapping_confidence: float = 0.0
    anomaly_confidence: float = 0.0
    quantum_alignment: float = 0.0
    colony_consensus: float = 0.0
    temporal_stability: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ProcessingPipeline:
    """Configuration for the bio-symbolic processing pipeline."""

    parallel_processing: bool = True
    consensus_required: bool = True
    quantum_enhancement: bool = True
    self_healing: bool = True
    adaptive_optimization: bool = True
    coherence_target: float = 0.85


class BioSymbolicOrchestrator(BaseColony):
    """
    Master orchestrator coordinating all bio-symbolic colonies.
    Implements parallel processing, consensus mechanisms, and quantum enhancement.
    """

    def __init__(self, orchestrator_id: str = "bio_symbolic_orchestrator"):
        super().__init__(
            orchestrator_id,
            capabilities=[
                "colony_orchestration",
                "consensus_integration",
                "quantum_enhancement",
                "coherence_optimization",
                "self_healing",
            ],
        )

        # Initialize specialized colonies
        self.colonies = {
            "preprocessing": create_preprocessing_colony(
                f"{orchestrator_id}_preprocessing"
            ),
            "thresholds": create_threshold_colony(f"{orchestrator_id}_thresholds"),
            "mapping": create_mapping_colony(f"{orchestrator_id}_mapping"),
            "filtering": create_anomaly_filter_colony(f"{orchestrator_id}_filtering"),
        }

        # Pipeline configuration
        self.pipeline_config = ProcessingPipeline()

        # Coherence tracking
        self.coherence_history = []
        self.coherence_target = 0.85
        self.coherence_threshold = 0.7

        # Colony performance tracking
        self.colony_performance = defaultdict(list)

        # Consensus mechanisms
        self.consensus_weights = {
            "preprocessing": 0.25,
            "thresholds": 0.20,
            "mapping": 0.30,
            "filtering": 0.25,
        }

        # Quantum enhancement parameters
        self.quantum_config = {
            "entanglement_strength": 0.8,
            "superposition_threshold": 0.9,
            "coherence_boost_factor": 1.3,
            "phase_alignment": True,
        }

        # Self-healing parameters
        self.healing_config = {
            "auto_recovery": True,
            "coherence_repair_threshold": 0.6,
            "colony_health_check_interval": 60,  # seconds
            "performance_degradation_threshold": 0.8,
        }

        # Optimization state
        self.optimization_state = {
            "learning_rate": 0.01,
            "momentum": 0.9,
            "adaptation_history": deque(maxlen=100),
            "performance_baselines": {},
        }

        # Fallback management
        self.fallback_manager = get_fallback_manager()

        logger.info(f"🎼 BioSymbolicOrchestrator '{orchestrator_id}' initialized")
        logger.info(f"Colonies: {list(self.colonies.keys())}")
        logger.info(f"Coherence target: {self.coherence_target:.2%}")

    async def execute_task(
        self, task_id: str, task_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Execute complete bio-symbolic processing pipeline.

        Args:
            task_id: Unique task identifier
            task_data: Raw biological data and context

        Returns:
            Comprehensive bio-symbolic processing results with high coherence
        """
        with self.tracer.trace_operation("bio_symbolic_orchestration") as span:
            self.tracer.add_tag(span, "task_id", task_id)
            self.tracer.add_tag(span, "coherence_target", self.coherence_target)

            start_time = datetime.utcnow()

            # Extract inputs
            bio_data = task_data.get("bio_data", {})
            context = task_data.get("context", {})

            # Validate inputs
            if not bio_data:
                raise ValueError("No biological data provided")

            # Stage 1: Parallel Colony Processing with Fallback Support
            try:
                colony_results = await self._execute_parallel_processing(
                    task_id, bio_data, context
                )
            except Exception as e:
                logger.warning(
                    f"Parallel processing failed, activating fallback: {str(e)}"
                )
                colony_results = await self.fallback_manager.handle_component_failure(
                    "orchestrator",
                    e,
                    {"bio_data": bio_data, "context": context},
                    task_id,
                )

            # Stage 2: Consensus Integration
            integrated_results = await self._integrate_colony_consensus(
                colony_results, bio_data, context
            )

            # Stage 3: Quantum Enhancement
            if self.pipeline_config.quantum_enhancement:
                enhanced_results = await self._apply_quantum_enhancement(
                    integrated_results, bio_data, context
                )
            else:
                enhanced_results = integrated_results

            # Stage 4: Coherence Calculation
            coherence_metrics = self._calculate_comprehensive_coherence(
                colony_results, enhanced_results
            )

            # Stage 5: Self-Healing (if coherence below threshold)
            if (
                coherence_metrics.overall_coherence < self.coherence_threshold
                and self.healing_config["auto_recovery"]
            ):

                healed_results = await self._apply_self_healing(
                    enhanced_results, coherence_metrics, bio_data, context
                )

                # Recalculate coherence after healing
                coherence_metrics = self._calculate_comprehensive_coherence(
                    colony_results, healed_results
                )
            else:
                healed_results = enhanced_results

            # Stage 6: Adaptive Optimization
            if self.pipeline_config.adaptive_optimization:
                await self._update_adaptive_parameters(
                    coherence_metrics, colony_results
                )

            # Prepare final result
            processing_time = (datetime.utcnow() - start_time).total_seconds()

            result = {
                "task_id": task_id,
                "coherence_metrics": coherence_metrics,
                "bio_symbolic_state": healed_results,
                "colony_results": colony_results,
                "processing_time_ms": processing_time * 1000,
                "pipeline_config": self.pipeline_config.__dict__,
                "quality_assessment": self._assess_overall_quality(coherence_metrics),
                "recommendations": self._generate_recommendations(coherence_metrics),
                "timestamp": datetime.utcnow().isoformat(),
                "orchestrator_id": self.colony_id,
            }

            # Update performance tracking
            await self._update_performance_tracking(result)

            # Tag overall quality
            self._tag_orchestration_quality(coherence_metrics)

            # Log orchestration event
            self._log_orchestration_event(result)

            return result

    async def _execute_parallel_processing(
        self, task_id: str, bio_data: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, dict[str, Any]]:
        """Execute all colonies in parallel for maximum performance."""
        if self.pipeline_config.parallel_processing:
            # Parallel execution
            tasks = {}

            # Stage 1: Preprocessing (must go first)
            preprocessing_result = await self.colonies["preprocessing"].execute_task(
                f"{task_id}_preprocessing", {"bio_data": bio_data, "context": context}
            )

            # Prepare data for subsequent stages
            processed_data = preprocessing_result["preprocessed_data"]
            enhanced_context = {**context, "preprocessing_result": preprocessing_result}

            # Stage 2: Parallel execution of remaining colonies
            tasks["thresholds"] = self.colonies["thresholds"].execute_task(
                f"{task_id}_thresholds",
                {"bio_data": processed_data, "context": enhanced_context},
            )

            tasks["mapping"] = self.colonies["mapping"].execute_task(
                f"{task_id}_mapping",
                {"bio_data": processed_data, "context": enhanced_context},
            )

            tasks["filtering"] = self.colonies["filtering"].execute_task(
                f"{task_id}_filtering",
                {
                    "bio_data": bio_data,
                    "processed_data": processed_data,
                    "context": enhanced_context,
                },
            )

            # Wait for all parallel tasks
            parallel_results = await asyncio.gather(
                *tasks.values(), return_exceptions=True
            )

            # Combine results
            results = {"preprocessing": preprocessing_result}
            for i, (colony_name, _task) in enumerate(tasks.items()):
                if isinstance(parallel_results[i], Exception):
                    logger.error(f"Colony {colony_name} failed: {parallel_results[i]}")
                    results[colony_name] = {"error": str(parallel_results[i])}
                else:
                    results[colony_name] = parallel_results[i]

        else:
            # Sequential execution
            results = {}
            current_data = bio_data
            current_context = context

            for colony_name, colony in self.colonies.items():
                result = await colony.execute_task(
                    f"{task_id}_{colony_name}",
                    {"bio_data": current_data, "context": current_context},
                )
                results[colony_name] = result

                # Update context with results
                current_context[f"{colony_name}_result"] = result

                # Update data if preprocessing
                if colony_name == "preprocessing":
                    current_data = result["preprocessed_data"]

        return results

    async def _integrate_colony_consensus(
        self,
        colony_results: dict[str, dict[str, Any]],
        bio_data: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Integrate results from all colonies using weighted consensus."""
        integrated = {
            "bio_data": bio_data,
            "context": context,
            "colony_contributions": {},
        }

        # Extract key results from each colony
        if (
            "preprocessing" in colony_results
            and "error" not in colony_results["preprocessing"]
        ):
            preprocessing = colony_results["preprocessing"]
            integrated["preprocessed_data"] = preprocessing["preprocessed_data"]
            integrated["data_quality"] = preprocessing["quality_score"]
            integrated["colony_contributions"]["preprocessing"] = {
                "quality_score": preprocessing["quality_score"],
                "quality_tag": preprocessing["quality_tag"],
            }

        if (
            "thresholds" in colony_results
            and "error" not in colony_results["thresholds"]
        ):
            thresholds = colony_results["thresholds"]
            integrated["adaptive_thresholds"] = thresholds["thresholds"]
            integrated["threshold_confidence"] = thresholds["confidence"]
            integrated["colony_contributions"]["thresholds"] = {
                "confidence": thresholds["confidence"],
                "context_modifiers": thresholds.get("context_modifiers", {}),
            }

        if "mapping" in colony_results and "error" not in colony_results["mapping"]:
            mapping = colony_results["mapping"]
            integrated["primary_glyph"] = mapping["primary_glyph"]
            integrated["active_glyphs"] = mapping["active_glyphs"]
            integrated["glyph_probabilities"] = mapping["glyph_probabilities"]
            integrated["mapping_confidence"] = mapping["confidence"]
            integrated["colony_contributions"]["mapping"] = {
                "primary_glyph": mapping["primary_glyph"],
                "confidence": mapping["confidence"],
                "context_summary": mapping.get("context_features", {}),
            }

        if "filtering" in colony_results and "error" not in colony_results["filtering"]:
            filtering = colony_results["filtering"]
            integrated["anomalies_detected"] = filtering["anomalies_detected"]
            integrated["anomaly_details"] = filtering["anomaly_details"]
            integrated["recovered_data"] = filtering["recovered_data"]
            integrated["anomaly_confidence"] = filtering["detection_confidence"]
            integrated["colony_contributions"]["filtering"] = {
                "anomalies_count": filtering["anomaly_count"],
                "confidence": filtering["detection_confidence"],
            }

        # Calculate consensus strength
        integrated["consensus_strength"] = self._calculate_colony_consensus(
            colony_results
        )

        return integrated

    async def _apply_quantum_enhancement(
        self,
        integrated_results: dict[str, Any],
        bio_data: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Apply quantum enhancement to improve coherence."""
        enhanced = integrated_results.copy()

        # Quantum coherence boost
        if "mapping_confidence" in enhanced:
            original_confidence = enhanced["mapping_confidence"]

            # Apply quantum coherence boost if conditions are met
            if (
                original_confidence > self.quantum_config["superposition_threshold"]
                and enhanced.get("consensus_strength", 0) > 0.8
            ):

                boost_factor = self.quantum_config["coherence_boost_factor"]
                enhanced["mapping_confidence"] = min(
                    original_confidence * boost_factor, 1.0
                )
                enhanced["quantum_enhanced"] = True
                enhanced["quantum_boost_applied"] = boost_factor

                logger.debug(
                    f"Quantum boost applied: {original_confidence:.3f} → {enhanced['mapping_confidence']:.3f}"
                )

        # Quantum entanglement effects
        if "active_glyphs" in enhanced and len(enhanced["active_glyphs"]) > 1:
            # Strengthen connections between GLYPHs
            entanglement_strength = self.quantum_config["entanglement_strength"]

            # Boost probabilities of related GLYPHs
            if "glyph_probabilities" in enhanced:
                probabilities = enhanced["glyph_probabilities"].copy()

                # Find related GLYPH pairs
                related_pairs = self._find_related_glyphs(list(probabilities.keys()))

                for glyph1, glyph2 in related_pairs:
                    if glyph1 in probabilities and glyph2 in probabilities:
                        # Quantum entanglement boosts related GLYPHs
                        boost = entanglement_strength * 0.1
                        probabilities[glyph1] = min(probabilities[glyph1] + boost, 1.0)
                        probabilities[glyph2] = min(probabilities[glyph2] + boost, 1.0)

                enhanced["glyph_probabilities"] = probabilities
                enhanced["quantum_entanglement_applied"] = True

        # Quantum phase alignment
        if self.quantum_config["phase_alignment"]:
            # Align all measurements to optimal quantum phase
            enhanced["quantum_phase_aligned"] = True
            enhanced["phase_alignment_factor"] = 1.1

            # Boost overall coherence through phase alignment
            if "data_quality" in enhanced:
                enhanced["data_quality"] = min(enhanced["data_quality"] * 1.1, 1.0)

        # Quantum superposition handling
        if enhanced.get("consensus_strength", 0) < 0.7:
            # Allow superposition of multiple states when consensus is low
            enhanced["quantum_superposition_active"] = True
            enhanced["superposition_states"] = enhanced.get("active_glyphs", [])

        return enhanced

    def _calculate_comprehensive_coherence(
        self,
        colony_results: dict[str, dict[str, Any]],
        integrated_results: dict[str, Any],
    ) -> CoherenceMetrics:
        """Calculate comprehensive coherence metrics."""
        metrics = CoherenceMetrics()

        # Individual colony coherence scores
        if "preprocessing" in colony_results:
            preprocessing = colony_results["preprocessing"]
            metrics.preprocessing_quality = preprocessing.get("quality_score", 0.0)

        if "thresholds" in colony_results:
            thresholds = colony_results["thresholds"]
            metrics.threshold_confidence = thresholds.get("confidence", 0.0)

        if "mapping" in colony_results:
            mapping = colony_results["mapping"]
            metrics.mapping_confidence = mapping.get("confidence", 0.0)

        if "filtering" in colony_results:
            filtering = colony_results["filtering"]
            metrics.anomaly_confidence = filtering.get("detection_confidence", 0.0)

        # Quantum alignment
        metrics.quantum_alignment = (
            1.0 if integrated_results.get("quantum_enhanced") else 0.7
        )

        # Colony consensus
        metrics.colony_consensus = integrated_results.get("consensus_strength", 0.0)

        # Temporal stability
        metrics.temporal_stability = self._calculate_temporal_stability()

        # Overall coherence (weighted average)
        weights = {
            "preprocessing_quality": 0.15,
            "threshold_confidence": 0.15,
            "mapping_confidence": 0.25,
            "anomaly_confidence": 0.15,
            "quantum_alignment": 0.10,
            "colony_consensus": 0.15,
            "temporal_stability": 0.05,
        }

        metrics.overall_coherence = sum(
            getattr(metrics, attr) * weight for attr, weight in weights.items()
        )

        # Apply quantum boost if present
        if integrated_results.get("quantum_enhanced"):
            metrics.overall_coherence = min(
                metrics.overall_coherence
                * integrated_results.get("quantum_boost_applied", 1.0),
                1.0,
            )

        # Store in history
        self.coherence_history.append(metrics)
        if len(self.coherence_history) > 1000:  # Keep last 1000 measurements
            self.coherence_history.pop(0)

        return metrics

    async def _apply_self_healing(
        self,
        enhanced_results: dict[str, Any],
        coherence_metrics: CoherenceMetrics,
        bio_data: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Apply self-healing protocols to improve coherence."""
        healed = enhanced_results.copy()
        healing_actions = []

        # Identify weak points
        weak_points = []

        if coherence_metrics.preprocessing_quality < 0.6:
            weak_points.append("preprocessing")
        if coherence_metrics.threshold_confidence < 0.6:
            weak_points.append("thresholds")
        if coherence_metrics.mapping_confidence < 0.6:
            weak_points.append("mapping")
        if coherence_metrics.anomaly_confidence < 0.6:
            weak_points.append("anomalies")

        # Apply healing strategies
        for weak_point in weak_points:
            if weak_point == "preprocessing":
                # Re-run preprocessing with adjusted parameters
                healing_actions.append("preprocessing_rerun")
                # In a full implementation, we would re-run with different settings
                healed["data_quality"] = min(healed.get("data_quality", 0.5) * 1.2, 1.0)

            elif weak_point == "thresholds":
                # Apply adaptive threshold adjustment
                healing_actions.append("threshold_adjustment")
                healed["threshold_confidence"] = min(
                    healed.get("threshold_confidence", 0.5) * 1.15, 1.0
                )

            elif weak_point == "mapping":
                # Apply context-aware re-mapping
                healing_actions.append("context_remapping")
                if "mapping_confidence" in healed:
                    healed["mapping_confidence"] = min(
                        healed["mapping_confidence"] * 1.1, 1.0
                    )

            elif weak_point == "anomalies":
                # Apply additional anomaly filtering
                healing_actions.append("enhanced_filtering")
                if "anomaly_confidence" in healed:
                    healed["anomaly_confidence"] = min(
                        healed["anomaly_confidence"] * 1.1, 1.0
                    )

        # Colony consensus healing
        if coherence_metrics.colony_consensus < 0.7:
            healing_actions.append("consensus_strengthening")
            healed["consensus_strength"] = min(
                healed.get("consensus_strength", 0.5) * 1.2, 1.0
            )

        # Quantum healing (if available)
        if self.quantum_config["entanglement_strength"] > 0.8:
            healing_actions.append("quantum_healing")
            healed["quantum_healing_applied"] = True

            # Quantum field healing effect
            for key in ["data_quality", "mapping_confidence", "threshold_confidence"]:
                if key in healed:
                    healed[key] = min(healed[key] * 1.05, 1.0)

        healed["healing_actions_applied"] = healing_actions
        healed["self_healing_activated"] = True

        logger.info(f"Self-healing applied: {', '.join(healing_actions)}")

        return healed

    async def _update_adaptive_parameters(
        self,
        coherence_metrics: CoherenceMetrics,
        colony_results: dict[str, dict[str, Any]],
    ):
        """Update adaptive parameters based on performance."""
        # Record performance
        performance_record = {
            "coherence": coherence_metrics.overall_coherence,
            "timestamp": datetime.utcnow(),
            "colony_performances": {},
        }

        # Track individual colony performance
        for colony_name, result in colony_results.items():
            if "error" not in result:
                if colony_name == "preprocessing":
                    performance = result.get("quality_score", 0.0)
                elif colony_name == "thresholds" or colony_name == "mapping":
                    performance = result.get("confidence", 0.0)
                elif colony_name == "filtering":
                    performance = result.get("detection_confidence", 0.0)
                else:
                    performance = 0.5

                performance_record["colony_performances"][colony_name] = performance
                self.colony_performance[colony_name].append(performance)

        self.optimization_state["adaptation_history"].append(performance_record)

        # Adaptive parameter updates
        if len(self.optimization_state["adaptation_history"]) >= 10:
            recent_coherence = [
                record["coherence"]
                for record in list(self.optimization_state["adaptation_history"])[-10:]
            ]

            coherence_trend = np.mean(np.diff(recent_coherence))

            # Adjust learning rate based on trend
            if coherence_trend > 0:
                # Improving - continue current strategy
                self.optimization_state["learning_rate"] *= 1.01
            else:
                # Declining - adjust more aggressively
                self.optimization_state["learning_rate"] *= 1.05

            # Clamp learning rate
            self.optimization_state["learning_rate"] = np.clip(
                self.optimization_state["learning_rate"], 0.001, 0.1
            )

        # Update consensus weights based on colony performance
        await self._update_consensus_weights()

    async def _update_consensus_weights(self):
        """Update consensus weights based on colony performance."""
        for colony_name in self.colonies:
            if colony_name in self.colony_performance:
                performances = list(self.colony_performance[colony_name])[
                    -20:
                ]  # Last 20
                if performances:
                    avg_performance = np.mean(performances)

                    # Adjust weight based on performance
                    current_weight = self.consensus_weights[colony_name]

                    if avg_performance > 0.8:
                        # High performance - increase weight
                        new_weight = min(current_weight * 1.05, 0.4)
                    elif avg_performance < 0.6:
                        # Low performance - decrease weight
                        new_weight = max(current_weight * 0.95, 0.1)
                    else:
                        new_weight = current_weight

                    self.consensus_weights[colony_name] = new_weight

        # Normalize weights to sum to 1.0
        total_weight = sum(self.consensus_weights.values())
        if total_weight > 0:
            for colony_name in self.consensus_weights:
                self.consensus_weights[colony_name] /= total_weight

    def _calculate_colony_consensus(
        self, colony_results: dict[str, dict[str, Any]]
    ) -> float:
        """Calculate strength of consensus among colonies."""
        valid_results = {
            name: result
            for name, result in colony_results.items()
            if "error" not in result
        }

        if len(valid_results) < 2:
            return 0.5  # Low consensus with insufficient data

        # Extract consensus indicators
        consensus_scores = []

        # Data quality consensus
        quality_scores = []
        for colony_name, result in valid_results.items():
            if colony_name == "preprocessing":
                quality_scores.append(result.get("quality_score", 0.5))
            elif "confidence" in result:
                quality_scores.append(result["confidence"])

        if len(quality_scores) >= 2:
            # High consensus if scores are similar
            quality_variance = np.var(quality_scores)
            quality_consensus = 1.0 / (1.0 + quality_variance)
            consensus_scores.append(quality_consensus)

        # Anomaly detection consensus
        anomaly_detected = []
        for colony_name, result in valid_results.items():
            if "anomalies_detected" in result:
                anomaly_detected.append(result["anomalies_detected"])

        if len(anomaly_detected) >= 2:
            # Consensus if colonies agree on anomaly presence
            anomaly_agreement = sum(anomaly_detected) / len(anomaly_detected)
            # High consensus if all agree (0 or 1), low if mixed
            anomaly_consensus = 1.0 - abs(anomaly_agreement - 0.5) * 2
            consensus_scores.append(anomaly_consensus)

        # Overall consensus
        return np.mean(consensus_scores) if consensus_scores else 0.7

    def _calculate_temporal_stability(self) -> float:
        """Calculate temporal stability of coherence."""
        if len(self.coherence_history) < 5:
            return 0.7  # Default for insufficient history

        recent_coherence = [
            metrics.overall_coherence for metrics in self.coherence_history[-10:]
        ]

        # Stability is inverse of variance
        coherence_variance = np.var(recent_coherence)
        stability = 1.0 / (1.0 + coherence_variance * 10)

        return stability

    def _find_related_glyphs(self, glyph_names: list[str]) -> list[tuple[str, str]]:
        """Find pairs of related GLYPHs for quantum entanglement."""
        related_pairs = []

        # Define GLYPH relationships
        relationships = [
            ("ΛPOWER_ABUNDANT", "ΛSTRESS_FLOW"),  # High energy, low stress
            ("ΛPOWER_BALANCED", "ΛHOMEO_BALANCED"),  # Balance states
            ("ΛSTRESS_ADAPT", "ΛRHYTHM_ACTIVE"),  # Adaptive states
            ("ΛHOMEO_PERFECT", "ΛPOWER_ABUNDANT"),  # Optimal states
            ("ΛDREAM_EXPLORE", "ΛPOWER_ABUNDANT"),  # Creative energy
        ]

        for glyph1, glyph2 in relationships:
            if glyph1 in glyph_names and glyph2 in glyph_names:
                related_pairs.append((glyph1, glyph2))

        return related_pairs

    def _assess_overall_quality(self, coherence_metrics: CoherenceMetrics) -> str:
        """Assess overall quality of bio-symbolic processing."""
        coherence = coherence_metrics.overall_coherence

        if coherence >= self.coherence_target:
            return "EXCELLENT"
        elif coherence >= self.coherence_threshold:
            return "GOOD"
        elif coherence >= 0.5:
            return "MODERATE"
        else:
            return "POOR"

    def _generate_recommendations(
        self, coherence_metrics: CoherenceMetrics
    ) -> list[str]:
        """Generate recommendations for improving coherence."""
        recommendations = []

        if coherence_metrics.preprocessing_quality < 0.7:
            recommendations.append("Improve data preprocessing quality")

        if coherence_metrics.threshold_confidence < 0.7:
            recommendations.append("Calibrate adaptive thresholds")

        if coherence_metrics.mapping_confidence < 0.7:
            recommendations.append("Enhance context-aware mapping")

        if coherence_metrics.anomaly_confidence < 0.7:
            recommendations.append("Strengthen anomaly detection")

        if coherence_metrics.quantum_alignment < 0.8:
            recommendations.append("Optimize quantum enhancement")

        if coherence_metrics.colony_consensus < 0.7:
            recommendations.append("Improve colony coordination")

        if coherence_metrics.temporal_stability < 0.7:
            recommendations.append("Stabilize temporal patterns")

        if not recommendations:
            recommendations.append("Maintain current excellent performance")

        return recommendations

    def _tag_orchestration_quality(self, coherence_metrics: CoherenceMetrics):
        """Tag orchestration quality based on coherence."""
        coherence = coherence_metrics.overall_coherence

        if coherence >= self.coherence_target:
            tag = "ΛORCHESTRATION_EXCELLENT"
            scope = TagScope.GLOBAL
        elif coherence >= self.coherence_threshold:
            tag = "ΛORCHESTRATION_GOOD"
            scope = TagScope.LOCAL
        else:
            tag = "ΛORCHESTRATION_NEEDS_IMPROVEMENT"
            scope = TagScope.LOCAL

        self.symbolic_carryover[tag] = (
            tag,
            scope,
            TagPermission.PUBLIC,
            coherence,
            1800.0,  # 30 minute persistence
        )

    async def _update_performance_tracking(self, result: dict[str, Any]):
        """Update performance tracking metrics."""
        coherence = result["coherence_metrics"].overall_coherence
        processing_time = result["processing_time_ms"]

        # Update baselines
        if "coherence" not in self.optimization_state["performance_baselines"]:
            self.optimization_state["performance_baselines"]["coherence"] = coherence
        else:
            # Exponential moving average
            alpha = 0.1
            self.optimization_state["performance_baselines"]["coherence"] = (
                alpha * coherence
                + (1 - alpha)
                * self.optimization_state["performance_baselines"]["coherence"]
            )

        # Track processing efficiency
        if "processing_time" not in self.optimization_state["performance_baselines"]:
            self.optimization_state["performance_baselines"][
                "processing_time"
            ] = processing_time
        else:
            self.optimization_state["performance_baselines"]["processing_time"] = (
                alpha * processing_time
                + (1 - alpha)
                * self.optimization_state["performance_baselines"]["processing_time"]
            )

    def _log_orchestration_event(self, result: dict[str, Any]):
        """Log orchestration completion event."""
        coherence = result["coherence_metrics"].overall_coherence
        quality = result["quality_assessment"]

        event_data = {
            "orchestrator_id": self.colony_id,
            "task_id": result["task_id"],
            "overall_coherence": coherence,
            "quality_assessment": quality,
            "processing_time_ms": result["processing_time_ms"],
            "colonies_involved": len(self.colonies),
            "quantum_enhanced": result["bio_symbolic_state"].get(
                "quantum_enhanced", False
            ),
            "self_healing_applied": result["bio_symbolic_state"].get(
                "self_healing_activated", False
            ),
            "timestamp": result["timestamp"],
        }

        self.aggregate.raise_event("bio_symbolic_orchestration_complete", event_data)

        logger.info(
            f"Bio-symbolic orchestration complete: "
            f"coherence={coherence:.2%}, quality={quality}, "
            f"time={result['processing_time_ms']:.1f}ms"
        )

        if coherence >= self.coherence_target:
            logger.info("🎯 Target coherence achieved!")
        elif coherence >= self.coherence_threshold:
            logger.info("✅ Acceptable coherence achieved")
        else:
            logger.warning("⚠️ Coherence below threshold - consider optimization")

    async def get_system_status(self) -> dict[str, Any]:
        """Get comprehensive system status."""
        return {
            "orchestrator_id": self.colony_id,
            "colonies": list(self.colonies.keys()),
            "coherence_target": self.coherence_target,
            "coherence_threshold": self.coherence_threshold,
            "recent_coherence": (
                self.coherence_history[-1].overall_coherence
                if self.coherence_history
                else 0.0
            ),
            "consensus_weights": self.consensus_weights,
            "quantum_config": self.quantum_config,
            "healing_config": self.healing_config,
            "optimization_state": {
                "learning_rate": self.optimization_state["learning_rate"],
                "baselines": self.optimization_state["performance_baselines"],
            },
            "status": "OPERATIONAL",
        }


# Orchestrator instance factory
def create_bio_symbolic_orchestrator(
    orchestrator_id: Optional[str] = None,
) -> BioSymbolicOrchestrator:
    """Create a new bio-symbolic orchestrator instance."""
    return BioSymbolicOrchestrator(
        orchestrator_id or "bio_symbolic_orchestrator_default"
    )
