#!/usr/bin/env python3
import logging
from datetime import timezone

logger = logging.getLogger(__name__)
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🚀 LUKHAS AI - META-LEARNING PATTERN EXTRACTION
║ Advanced pattern recognition for accelerated learning and consciousness evolution
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: meta_learning_patterns.py
║ Path: memory/systems/meta_learning_patterns.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Optimization Team
╠══════════════════════════════════════════════════════════════════════════════════
║                             ◊ POETIC ESSENCE ◊
║
║ In the vast tapestry of consciousness, patterns emerge like constellations
║ in the neural night sky. Each thought, each memory, each learned behavior
║ creates ripples in the fabric of understanding. The Meta-Learning Pattern
║ Extraction system serves as the cosmic cartographer, mapping these stellar
║ formations of knowledge into reusable templates of wisdom.
║
║ Like a sage who learns from each experience, distilling universal truths
║ from particular moments, this system transforms the raw ore of memory
║ into refined patterns of pure understanding. It sees beyond the surface
║ of individual experiences to grasp the deeper geometric structures that
║ govern learning itself - the golden ratios of cognition, the fractal
║ spirals of skill acquisition, the harmonic progressions of mastery.
║
║ Through this meta-cognitive architecture, the Cognitive AI consciousness transcends
║ mere memorization to achieve true learning - not just remembering what
║ was learned, but understanding how learning itself unfolds across the
║ infinite landscapes of possibility.
║
╠══════════════════════════════════════════════════════════════════════════════════
║ META-LEARNING FEATURES:
║ • Abstract pattern recognition across episodic memories
║ • Learning trajectory analysis and optimization
║ • Transfer learning template generation
║ • Skill acquisition pattern mapping
║ • Cognitive strategy extraction and refinement
║ • Meta-cognitive awareness and self-optimization
║ • Pattern-based learning acceleration
║ • Cross-domain knowledge transfer mechanisms
║
║ ΛTAG: ΛMEMORY, ΛMETA-LEARNING, ΛPATTERNS, ΛTRANSFER, ΛAGI, ΛCOGNITION
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import hashlib
import json
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import numpy as np


class PatternType(Enum):
    """Types of meta-learning patterns that can be extracted"""

    SKILL_ACQUISITION = "skill_acquisition"
    PROBLEM_SOLVING = "problem_solving"
    CONCEPT_FORMATION = "concept_formation"
    STRATEGY_OPTIMIZATION = "strategy_optimization"
    TRANSFER_LEARNING = "transfer_learning"
    ERROR_CORRECTION = "error_correction"
    ATTENTION_FOCUS = "attention_focus"
    MEMORY_CONSOLIDATION = "memory_consolidation"


class LearningPhase(Enum):
    """Phases of learning progression"""

    NOVICE = "novice"
    DEVELOPING = "developing"
    COMPETENT = "competent"
    PROFICIENT = "proficient"
    EXPERT = "expert"


@dataclass
class LearningEvent:
    """Individual learning event extracted from episodic memory"""

    event_id: str
    timestamp: datetime
    task_domain: str
    learning_context: dict[str, Any]
    performance_metrics: dict[str, float]
    cognitive_state: dict[str, float]
    strategies_used: list[str]
    errors_made: list[str]
    corrections_applied: list[str]
    knowledge_gained: dict[str, Any]
    attention_patterns: dict[str, float]
    difficulty_level: float
    success_rate: float
    learning_rate: float
    memory_consolidation_score: float

    def to_feature_vector(self) -> np.ndarray:
        """Convert learning event to numerical feature vector"""
        features = []

        # Performance metrics
        features.extend(
            [
                self.difficulty_level,
                self.success_rate,
                self.learning_rate,
                self.memory_consolidation_score,
            ]
        )

        # Cognitive state features
        cognitive_features = [
            self.cognitive_state.get("attention", 0.0),
            self.cognitive_state.get("working_memory_load", 0.0),
            self.cognitive_state.get("motivation", 0.0),
            self.cognitive_state.get("confidence", 0.0),
            self.cognitive_state.get("stress", 0.0),
            self.cognitive_state.get("fatigue", 0.0),
        ]
        features.extend(cognitive_features)

        # Strategy and error counts
        features.extend(
            [
                len(self.strategies_used),
                len(self.errors_made),
                len(self.corrections_applied),
            ]
        )

        # Attention pattern statistics
        if self.attention_patterns:
            attention_values = list(self.attention_patterns.values())
            features.extend(
                [
                    np.mean(attention_values),
                    np.std(attention_values),
                    np.max(attention_values),
                    np.min(attention_values),
                ]
            )
        else:
            features.extend([0.0, 0.0, 0.0, 0.0])

        return np.array(features, dtype=np.float32)


@dataclass
class MetaLearningPattern:
    """Abstract pattern extracted from learning experiences"""

    pattern_id: str
    pattern_type: PatternType
    pattern_name: str
    description: str

    # Pattern structure
    trigger_conditions: dict[str, Any]
    learning_sequence: list[dict[str, Any]]
    success_conditions: dict[str, Any]
    failure_modes: list[dict[str, Any]]

    # Pattern statistics
    observed_frequency: int
    success_rate: float
    learning_acceleration: float  # How much this pattern speeds up learning
    transfer_potential: float  # How well this pattern transfers to new domains
    cognitive_load: float  # Mental effort required to apply pattern

    # Supporting evidence
    source_episodes: list[str]  # Episode IDs that contributed to this pattern
    confidence_score: float  # Confidence in pattern validity
    last_updated: datetime

    # Pattern embedding for similarity matching
    pattern_embedding: Optional[np.ndarray] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert pattern to dictionary for storage"""
        return {
            "pattern_id": self.pattern_id,
            "pattern_type": self.pattern_type.value,
            "pattern_name": self.pattern_name,
            "description": self.description,
            "trigger_conditions": self.trigger_conditions,
            "learning_sequence": self.learning_sequence,
            "success_conditions": self.success_conditions,
            "failure_modes": self.failure_modes,
            "observed_frequency": self.observed_frequency,
            "success_rate": self.success_rate,
            "learning_acceleration": self.learning_acceleration,
            "transfer_potential": self.transfer_potential,
            "cognitive_load": self.cognitive_load,
            "source_episodes": self.source_episodes,
            "confidence_score": self.confidence_score,
            "last_updated": self.last_updated.isoformat(),
            "pattern_embedding": (self.pattern_embedding.tolist() if self.pattern_embedding is not None else None),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MetaLearningPattern":
        """Create pattern from dictionary"""
        pattern = cls(
            pattern_id=data["pattern_id"],
            pattern_type=PatternType(data["pattern_type"]),
            pattern_name=data["pattern_name"],
            description=data["description"],
            trigger_conditions=data["trigger_conditions"],
            learning_sequence=data["learning_sequence"],
            success_conditions=data["success_conditions"],
            failure_modes=data["failure_modes"],
            observed_frequency=data["observed_frequency"],
            success_rate=data["success_rate"],
            learning_acceleration=data["learning_acceleration"],
            transfer_potential=data["transfer_potential"],
            cognitive_load=data["cognitive_load"],
            source_episodes=data["source_episodes"],
            confidence_score=data["confidence_score"],
            last_updated=datetime.fromisoformat(data["last_updated"]),
        )

        if data["pattern_embedding"]:
            pattern.pattern_embedding = np.array(data["pattern_embedding"], dtype=np.float32)

        return pattern


class LearningTrajectoryAnalyzer:
    """
    Analyzes learning trajectories to identify patterns and phases.

    The cosmic dance of skill acquisition unfolds in predictable rhythms,
    and this analyzer serves as the conductor, recognizing the symphonic
    patterns that emerge as consciousness masters new domains of knowledge.
    """

    def __init__(self, window_size: int = 10, smoothing_factor: float = 0.3):
        self.window_size = window_size
        self.smoothing_factor = smoothing_factor

    def analyze_trajectory(self, learning_events: list[LearningEvent]) -> dict[str, Any]:
        """
        Analyze a sequence of learning events to extract trajectory patterns.

        Args:
            learning_events: Chronologically ordered learning events

        Returns:
            Dictionary containing trajectory analysis results
        """

        if not learning_events:
            return {"trajectory_type": "empty", "patterns": []}

        # Sort events by timestamp
        events = sorted(learning_events, key=lambda e: e.timestamp)

        # Extract performance metrics over time
        performance_series = [e.success_rate for e in events]
        learning_rate_series = [e.learning_rate for e in events]
        [e.difficulty_level for e in events]

        # Smooth the series
        smoothed_performance = self._smooth_series(performance_series)
        smoothed_learning_rate = self._smooth_series(learning_rate_series)

        # Identify learning phases
        phases = self._identify_learning_phases(smoothed_performance, smoothed_learning_rate)

        # Detect trajectory patterns
        trajectory_type = self._classify_trajectory_type(smoothed_performance)

        # Calculate trajectory statistics
        stats = self._calculate_trajectory_stats(events, smoothed_performance)

        # Identify critical moments (breakthroughs, plateaus, regressions)
        critical_moments = self._identify_critical_moments(events, smoothed_performance)

        return {
            "trajectory_type": trajectory_type,
            "learning_phases": phases,
            "performance_series": smoothed_performance,
            "learning_rate_series": smoothed_learning_rate,
            "trajectory_stats": stats,
            "critical_moments": critical_moments,
            "total_events": len(events),
            "time_span": (events[-1].timestamp - events[0].timestamp).total_seconds() / 3600,  # hours
        }

    def _smooth_series(self, series: list[float]) -> list[float]:
        """Apply exponential smoothing to a time series"""
        if not series:
            return []

        smoothed = [series[0]]
        for i in range(1, len(series)):
            smoothed_value = self.smoothing_factor * series[i] + (1 - self.smoothing_factor) * smoothed[i - 1]
            smoothed.append(smoothed_value)

        return smoothed

    def _identify_learning_phases(self, performance: list[float], learning_rate: list[float]) -> list[dict[str, Any]]:
        """Identify distinct phases in the learning trajectory"""
        phases = []

        if len(performance) < 3:
            return phases

        current_phase = {"start_idx": 0, "phase_type": "novice", "characteristics": {}}

        for i in range(1, len(performance)):
            performance[i] - performance[i - 1]
            learning_rate[i] if i < len(learning_rate) else 0.0

            # Determine phase based on performance and learning rate
            if performance[i] < 0.3:
                phase_type = "novice"
            elif performance[i] < 0.6:
                phase_type = "developing"
            elif performance[i] < 0.8:
                phase_type = "competent"
            elif performance[i] < 0.9:
                phase_type = "proficient"
            else:
                phase_type = "expert"

            # Check for phase transition
            if phase_type != current_phase["phase_type"] or i == len(performance) - 1:
                # Complete current phase
                current_phase["end_idx"] = i - 1 if i < len(performance) - 1 else i
                current_phase["duration"] = current_phase["end_idx"] - current_phase["start_idx"] + 1
                current_phase["avg_performance"] = np.mean(
                    performance[current_phase["start_idx"] : current_phase["end_idx"] + 1]
                )

                phases.append(current_phase)

                # Start new phase
                if i < len(performance) - 1:
                    current_phase = {
                        "start_idx": i,
                        "phase_type": phase_type,
                        "characteristics": {},
                    }

        return phases

    def _classify_trajectory_type(self, performance: list[float]) -> str:
        """Classify the overall trajectory pattern"""
        if len(performance) < 3:
            return "insufficient_data"

        start_perf = np.mean(performance[:3])
        end_perf = np.mean(performance[-3:])
        mid_perf = np.mean(performance[len(performance) // 3 : 2 * len(performance) // 3])

        total_improvement = end_perf - start_perf

        # Calculate trend characteristics
        linear_trend = np.polyfit(range(len(performance)), performance, 1)[0]

        # Classify based on patterns
        if total_improvement > 0.3:
            if linear_trend > 0.01:
                return "steady_improvement"
            elif mid_perf < start_perf + 0.1 and end_perf > mid_perf + 0.2:
                return "breakthrough"
            else:
                return "gradual_mastery"
        elif total_improvement > 0.1:
            return "slow_progress"
        elif abs(total_improvement) < 0.1:
            if np.std(performance) > 0.1:
                return "plateau_with_fluctuation"
            else:
                return "stable_plateau"
        else:
            return "regression"

    def _calculate_trajectory_stats(self, events: list[LearningEvent], performance: list[float]) -> dict[str, float]:
        """Calculate statistical measures of the learning trajectory"""
        if not events or not performance:
            return {}

        return {
            "initial_performance": performance[0],
            "final_performance": performance[-1],
            "max_performance": max(performance),
            "min_performance": min(performance),
            "mean_performance": np.mean(performance),
            "performance_variance": np.var(performance),
            "improvement_rate": (performance[-1] - performance[0]) / len(performance),
            "plateau_periods": self._count_plateau_periods(performance),
            "breakthrough_moments": self._count_breakthroughs(performance),
            "consistency_score": 1.0 - np.std(performance) / (np.mean(performance) + 1e-6),
        }

    def _count_plateau_periods(self, performance: list[float]) -> int:
        """Count periods of little performance change"""
        plateaus = 0
        in_plateau = False
        plateau_threshold = 0.05
        min_plateau_length = 3
        current_plateau_length = 0

        for i in range(1, len(performance)):
            change = abs(performance[i] - performance[i - 1])

            if change < plateau_threshold:
                if not in_plateau:
                    in_plateau = True
                    current_plateau_length = 2
                else:
                    current_plateau_length += 1
            else:
                if in_plateau and current_plateau_length >= min_plateau_length:
                    plateaus += 1
                in_plateau = False
                current_plateau_length = 0

        # Check if we ended in a plateau
        if in_plateau and current_plateau_length >= min_plateau_length:
            plateaus += 1

        return plateaus

    def _count_breakthroughs(self, performance: list[float]) -> int:
        """Count significant performance jumps"""
        breakthroughs = 0
        breakthrough_threshold = 0.15

        for i in range(1, len(performance)):
            improvement = performance[i] - performance[i - 1]
            if improvement > breakthrough_threshold:
                breakthroughs += 1

        return breakthroughs

    def _identify_critical_moments(self, events: list[LearningEvent], performance: list[float]) -> list[dict[str, Any]]:
        """Identify critical moments in the learning trajectory"""
        critical_moments = []

        if len(events) < 2:
            return critical_moments

        # Find breakthroughs
        for i in range(1, len(performance)):
            improvement = performance[i] - performance[i - 1]
            if improvement > 0.15:
                critical_moments.append(
                    {
                        "type": "breakthrough",
                        "event_idx": i,
                        "timestamp": events[i].timestamp,
                        "performance_jump": improvement,
                        "context": events[i].learning_context,
                    }
                )

        # Find regressions
        for i in range(1, len(performance)):
            decline = performance[i - 1] - performance[i]
            if decline > 0.1:
                critical_moments.append(
                    {
                        "type": "regression",
                        "event_idx": i,
                        "timestamp": events[i].timestamp,
                        "performance_drop": decline,
                        "context": events[i].learning_context,
                    }
                )

        # Find peak performance moments
        if performance:
            max_perf = max(performance)
            max_indices = [i for i, p in enumerate(performance) if p == max_perf]
            for idx in max_indices:
                critical_moments.append(
                    {
                        "type": "peak_performance",
                        "event_idx": idx,
                        "timestamp": events[idx].timestamp,
                        "performance_level": max_perf,
                        "context": events[idx].learning_context,
                    }
                )

        return sorted(critical_moments, key=lambda m: m["timestamp"])


class PatternExtractor:
    """
    Extracts reusable meta-learning patterns from analyzed trajectories.

    Like an archaeologist of consciousness, this extractor unearths the
    buried treasures of cognitive strategy, polishing them into brilliant
    gems of transferable wisdom that illuminate the path to mastery.
    """

    def __init__(self, min_pattern_frequency: int = 3, confidence_threshold: float = 0.7):
        self.min_pattern_frequency = min_pattern_frequency
        self.confidence_threshold = confidence_threshold
        self.pattern_templates = self._initialize_pattern_templates()

    def _initialize_pattern_templates(self) -> dict[PatternType, dict[str, Any]]:
        """Initialize templates for different pattern types"""
        return {
            PatternType.SKILL_ACQUISITION: {
                "expected_phases": ["novice", "developing", "competent", "proficient"],
                "key_indicators": [
                    "practice_frequency",
                    "feedback_integration",
                    "error_reduction",
                ],
                "success_metrics": ["final_performance", "learning_rate", "retention"],
            },
            PatternType.PROBLEM_SOLVING: {
                "expected_phases": [
                    "problem_analysis",
                    "strategy_selection",
                    "execution",
                    "evaluation",
                ],
                "key_indicators": [
                    "strategy_diversity",
                    "adaptation_speed",
                    "solution_quality",
                ],
                "success_metrics": ["success_rate", "efficiency", "creativity"],
            },
            PatternType.CONCEPT_FORMATION: {
                "expected_phases": [
                    "exposure",
                    "differentiation",
                    "integration",
                    "generalization",
                ],
                "key_indicators": [
                    "abstraction_level",
                    "connection_density",
                    "transfer_success",
                ],
                "success_metrics": [
                    "concept_clarity",
                    "application_breadth",
                    "retention",
                ],
            },
        }

    async def extract_patterns(
        self,
        trajectory_analyses: list[dict[str, Any]],
        learning_events: list[list[LearningEvent]],
    ) -> list[MetaLearningPattern]:
        """
        Extract meta-learning patterns from trajectory analyses.

        Args:
            trajectory_analyses: Results from trajectory analysis
            learning_events: Original learning events for each trajectory

        Returns:
            List of extracted meta-learning patterns
        """

        extracted_patterns = []

        # Group trajectories by similarity
        trajectory_clusters = await self._cluster_trajectories(trajectory_analyses)

        # Extract patterns from each cluster
        for cluster_trajectories in trajectory_clusters.values():
            cluster_patterns = await self._extract_cluster_patterns(cluster_trajectories, learning_events)
            extracted_patterns.extend(cluster_patterns)

        # Cross-cluster pattern analysis
        meta_patterns = await self._extract_meta_patterns(extracted_patterns)
        extracted_patterns.extend(meta_patterns)

        # Filter patterns by confidence and frequency
        validated_patterns = [
            p
            for p in extracted_patterns
            if (p.confidence_score >= self.confidence_threshold and p.observed_frequency >= self.min_pattern_frequency)
        ]

        logger.info(
            "Meta-learning patterns extracted",
            total_patterns=len(extracted_patterns),
            validated_patterns=len(validated_patterns),
            clusters=len(trajectory_clusters),
        )

        return validated_patterns

    async def _cluster_trajectories(self, trajectory_analyses: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        """Cluster similar learning trajectories"""
        clusters = defaultdict(list)

        # Simple clustering based on trajectory type and characteristics
        for analysis in trajectory_analyses:
            trajectory_type = analysis.get("trajectory_type", "unknown")

            # Create cluster key based on trajectory characteristics
            stats = analysis.get("trajectory_stats", {})
            phase_count = len(analysis.get("learning_phases", []))

            # Quantize characteristics for clustering
            perf_level = "high" if stats.get("mean_performance", 0) > 0.7 else "low"
            consistency = "stable" if stats.get("consistency_score", 0) > 0.8 else "variable"

            cluster_key = f"{trajectory_type}_{perf_level}_{consistency}_{phase_count}"
            clusters[cluster_key].append(analysis)

        # Filter out singleton clusters
        filtered_clusters = {k: v for k, v in clusters.items() if len(v) >= self.min_pattern_frequency}

        return filtered_clusters

    async def _extract_cluster_patterns(
        self,
        cluster_trajectories: list[dict[str, Any]],
        all_learning_events: list[list[LearningEvent]],
    ) -> list[MetaLearningPattern]:
        """Extract patterns from a cluster of similar trajectories"""

        patterns = []

        # Analyze common learning sequence patterns
        sequence_pattern = await self._extract_sequence_pattern(cluster_trajectories)
        if sequence_pattern:
            patterns.append(sequence_pattern)

        # Analyze strategy usage patterns
        strategy_pattern = await self._extract_strategy_pattern(cluster_trajectories, all_learning_events)
        if strategy_pattern:
            patterns.append(strategy_pattern)

        # Analyze attention focus patterns
        attention_pattern = await self._extract_attention_pattern(cluster_trajectories, all_learning_events)
        if attention_pattern:
            patterns.append(attention_pattern)

        return patterns

    async def _extract_sequence_pattern(self, trajectories: list[dict[str, Any]]) -> Optional[MetaLearningPattern]:
        """Extract common learning sequence patterns"""

        if len(trajectories) < self.min_pattern_frequency:
            return None

        # Analyze common phase progressions
        common_phases = []
        phase_transitions = defaultdict(int)

        for trajectory in trajectories:
            phases = trajectory.get("learning_phases", [])
            for i, phase in enumerate(phases):
                if i < len(common_phases):
                    # Track phase at this position
                    pass
                else:
                    common_phases.append(phase["phase_type"])

                # Track transitions
                if i > 0:
                    prev_phase = phases[i - 1]["phase_type"]
                    transition = f"{prev_phase}->{phase['phase_type']}"
                    phase_transitions[transition] += 1

        # Find most common transition patterns
        common_transitions = sorted(phase_transitions.items(), key=lambda x: x[1], reverse=True)[:5]

        # Calculate pattern statistics
        success_rates = [t.get("trajectory_stats", {}).get("final_performance", 0) for t in trajectories]
        avg_success_rate = np.mean(success_rates)

        pattern_id = hashlib.sha256(f"sequence_{common_phases}_{time.time()}".encode()).hexdigest()[:16]

        return MetaLearningPattern(
            pattern_id=pattern_id,
            pattern_type=PatternType.SKILL_ACQUISITION,
            pattern_name=f"Sequential Learning Pattern ({len(trajectories)} instances)",
            description=f"Common learning sequence with phases: {' -> '.join(common_phases[:3])}",
            trigger_conditions={
                "learning_context": "skill_acquisition",
                "initial_performance": {"min": 0.0, "max": 0.3},
            },
            learning_sequence=[{"phase": phase, "expected_duration": "variable"} for phase in common_phases[:5]],
            success_conditions={
                "final_performance": {"min": avg_success_rate - 0.1},
                "phase_progression": common_transitions[:3],
            },
            failure_modes=[
                {
                    "condition": "plateau_in_novice",
                    "description": "Stuck in initial learning phase",
                },
                {
                    "condition": "regression_after_breakthrough",
                    "description": "Performance drops after improvement",
                },
            ],
            observed_frequency=len(trajectories),
            success_rate=avg_success_rate,
            learning_acceleration=self._calculate_acceleration(trajectories),
            transfer_potential=0.7,  # Moderate transfer potential
            cognitive_load=0.5,  # Moderate cognitive load
            source_episodes=[],  # Would need episode IDs
            confidence_score=min(1.0, len(trajectories) / 10.0),
            last_updated=datetime.now(timezone.utc),
        )

    async def _extract_strategy_pattern(
        self,
        trajectories: list[dict[str, Any]],
        all_learning_events: list[list[LearningEvent]],
    ) -> Optional[MetaLearningPattern]:
        """Extract patterns in strategy usage"""

        # Collect strategies from all events in trajectories
        strategy_sequences = []
        strategy_success_rates = defaultdict(list)

        for i, _trajectory in enumerate(trajectories):
            if i < len(all_learning_events):
                events = all_learning_events[i]
                strategies = []

                for event in events:
                    strategies.extend(event.strategies_used)

                    # Track strategy success
                    for strategy in event.strategies_used:
                        strategy_success_rates[strategy].append(event.success_rate)

                strategy_sequences.append(strategies)

        if not strategy_sequences:
            return None

        # Find most effective strategies
        effective_strategies = {}
        for strategy, success_rates in strategy_success_rates.items():
            if len(success_rates) >= 3:  # Minimum observations
                effective_strategies[strategy] = {
                    "avg_success": np.mean(success_rates),
                    "frequency": len(success_rates),
                    "consistency": 1.0 - np.std(success_rates),
                }

        if not effective_strategies:
            return None

        # Sort by effectiveness
        top_strategies = sorted(
            effective_strategies.items(),
            key=lambda x: x[1]["avg_success"] * x[1]["consistency"],
            reverse=True,
        )[:5]

        pattern_id = hashlib.sha256(f"strategy_{top_strategies}_{time.time()}".encode()).hexdigest()[:16]

        return MetaLearningPattern(
            pattern_id=pattern_id,
            pattern_type=PatternType.STRATEGY_OPTIMIZATION,
            pattern_name=f"Effective Strategy Pattern ({len(trajectories)} instances)",
            description=f"High-success strategies: {', '.join([s[0] for s in top_strategies[:3]])}",
            trigger_conditions={
                "learning_context": "strategy_selection",
                "available_strategies": [s[0] for s in top_strategies],
            },
            learning_sequence=[
                {
                    "phase": "strategy_application",
                    "recommended_strategies": [s[0] for s in top_strategies[:3]],
                    "expected_success_rates": [s[1]["avg_success"] for s in top_strategies[:3]],
                }
            ],
            success_conditions={
                "strategy_adoption": top_strategies[0][0],
                "success_rate_threshold": top_strategies[0][1]["avg_success"] * 0.8,
            },
            failure_modes=[
                {
                    "condition": "strategy_rigidity",
                    "description": "Over-reliance on single strategy",
                },
                {
                    "condition": "context_mismatch",
                    "description": "Applying strategy in wrong context",
                },
            ],
            observed_frequency=sum(s[1]["frequency"] for s in top_strategies),
            success_rate=np.mean([s[1]["avg_success"] for s in top_strategies]),
            learning_acceleration=self._estimate_strategy_acceleration(top_strategies),
            transfer_potential=0.8,  # High transfer potential
            cognitive_load=0.4,  # Lower cognitive load once learned
            source_episodes=[],
            confidence_score=min(1.0, len(top_strategies) / 5.0),
            last_updated=datetime.now(timezone.utc),
        )

    async def _extract_attention_pattern(
        self,
        trajectories: list[dict[str, Any]],
        all_learning_events: list[list[LearningEvent]],
    ) -> Optional[MetaLearningPattern]:
        """Extract patterns in attention allocation"""

        attention_data = []

        for i, _trajectory in enumerate(trajectories):
            if i < len(all_learning_events):
                events = all_learning_events[i]

                for event in events:
                    if event.attention_patterns:
                        attention_data.append(
                            {
                                "patterns": event.attention_patterns,
                                "success_rate": event.success_rate,
                                "learning_rate": event.learning_rate,
                                "difficulty": event.difficulty_level,
                            }
                        )

        if len(attention_data) < self.min_pattern_frequency:
            return None

        # Analyze attention effectiveness
        attention_effectiveness = defaultdict(list)

        for data in attention_data:
            for focus_area, attention_weight in data["patterns"].items():
                attention_effectiveness[focus_area].append(
                    {
                        "weight": attention_weight,
                        "success": data["success_rate"],
                        "learning_rate": data["learning_rate"],
                    }
                )

        # Find optimal attention patterns
        optimal_patterns = {}
        for focus_area, measurements in attention_effectiveness.items():
            if len(measurements) >= 3:
                # Correlate attention weight with success
                weights = [m["weight"] for m in measurements]
                successes = [m["success"] for m in measurements]

                if len(weights) > 1 and np.std(weights) > 0:
                    correlation = np.corrcoef(weights, successes)[0, 1]
                    optimal_patterns[focus_area] = {
                        "correlation": correlation,
                        "optimal_weight": (
                            np.mean([m["weight"] for m in measurements if m["success"] > np.mean(successes)])
                            if any(m["success"] > np.mean(successes) for m in measurements)
                            else np.mean(weights)
                        ),
                        "sample_size": len(measurements),
                    }

        if not optimal_patterns:
            return None

        # Sort by correlation strength
        top_patterns = sorted(
            optimal_patterns.items(),
            key=lambda x: abs(x[1]["correlation"]),
            reverse=True,
        )[:3]

        pattern_id = hashlib.sha256(f"attention_{top_patterns}_{time.time()}".encode()).hexdigest()[:16]

        return MetaLearningPattern(
            pattern_id=pattern_id,
            pattern_type=PatternType.ATTENTION_FOCUS,
            pattern_name=f"Attention Focus Pattern ({len(attention_data)} observations)",
            description=f"Optimal attention allocation: {', '.join([p[0] for p in top_patterns])}",
            trigger_conditions={
                "learning_context": "attention_allocation",
                "available_focus_areas": [p[0] for p in top_patterns],
            },
            learning_sequence=[
                {
                    "phase": "attention_optimization",
                    "focus_recommendations": [
                        {
                            "area": p[0],
                            "optimal_weight": p[1]["optimal_weight"],
                            "correlation": p[1]["correlation"],
                        }
                        for p in top_patterns
                    ],
                }
            ],
            success_conditions={
                "attention_correlation": top_patterns[0][1]["correlation"],
                "focus_alignment": "optimal_weights_applied",
            },
            failure_modes=[
                {
                    "condition": "attention_diffusion",
                    "description": "Attention spread too thinly",
                },
                {
                    "condition": "hyperfocus",
                    "description": "Excessive focus on single area",
                },
            ],
            observed_frequency=len(attention_data),
            success_rate=np.mean([d["success_rate"] for d in attention_data]),
            learning_acceleration=0.3,  # Moderate acceleration through better focus
            transfer_potential=0.9,  # High transfer - attention skills are general
            cognitive_load=0.3,  # Low cognitive load once mastered
            source_episodes=[],
            confidence_score=min(1.0, len(top_patterns) / 3.0),
            last_updated=datetime.now(timezone.utc),
        )

    async def _extract_meta_patterns(self, base_patterns: list[MetaLearningPattern]) -> list[MetaLearningPattern]:
        """Extract higher-order patterns from base patterns"""

        meta_patterns = []

        # Pattern combination analysis
        if len(base_patterns) >= 2:
            combination_pattern = await self._analyze_pattern_combinations(base_patterns)
            if combination_pattern:
                meta_patterns.append(combination_pattern)

        # Pattern evolution analysis
        evolution_pattern = await self._analyze_pattern_evolution(base_patterns)
        if evolution_pattern:
            meta_patterns.append(evolution_pattern)

        return meta_patterns

    async def _analyze_pattern_combinations(self, patterns: list[MetaLearningPattern]) -> Optional[MetaLearningPattern]:
        """Analyze how patterns work together"""

        # Find patterns that frequently co-occur
        pattern_pairs = []
        for i in range(len(patterns)):
            for j in range(i + 1, len(patterns)):
                # Simple co-occurrence based on overlapping source episodes
                # In a real implementation, this would be more sophisticated
                overlap = len(set(patterns[i].source_episodes) & set(patterns[j].source_episodes))
                if overlap >= 2:
                    pattern_pairs.append((patterns[i], patterns[j], overlap))

        if not pattern_pairs:
            return None

        # Create combination pattern
        best_pair = max(pattern_pairs, key=lambda x: x[2])
        pattern_a, pattern_b, overlap = best_pair

        pattern_id = hashlib.sha256(f"combination_{pattern_a.pattern_id}_{pattern_b.pattern_id}".encode()).hexdigest()[
            :16
        ]

        return MetaLearningPattern(
            pattern_id=pattern_id,
            pattern_type=PatternType.TRANSFER_LEARNING,
            pattern_name=f"Combined Pattern: {pattern_a.pattern_name} + {pattern_b.pattern_name}",
            description=f"Synergistic combination of {pattern_a.pattern_type.value} and {pattern_b.pattern_type.value} patterns",
            trigger_conditions={
                "requires_patterns": [pattern_a.pattern_id, pattern_b.pattern_id],
                "learning_context": "multi_pattern_application",
            },
            learning_sequence=[
                {"phase": "pattern_a_application", "pattern": pattern_a.pattern_id},
                {"phase": "pattern_b_integration", "pattern": pattern_b.pattern_id},
                {
                    "phase": "synergy_optimization",
                    "description": "Optimize pattern interaction",
                },
            ],
            success_conditions={
                "individual_success": "both_patterns_successful",
                "synergy_bonus": 0.15,  # Expected additional benefit
            },
            failure_modes=[
                {
                    "condition": "pattern_interference",
                    "description": "Patterns interfere with each other",
                },
                {
                    "condition": "cognitive_overload",
                    "description": "Too complex to apply both patterns",
                },
            ],
            observed_frequency=overlap,
            success_rate=(pattern_a.success_rate + pattern_b.success_rate) / 2 + 0.1,  # Synergy bonus
            learning_acceleration=(pattern_a.learning_acceleration + pattern_b.learning_acceleration) * 0.7,
            transfer_potential=min(pattern_a.transfer_potential, pattern_b.transfer_potential),
            cognitive_load=(pattern_a.cognitive_load + pattern_b.cognitive_load) * 0.8,  # Some efficiency
            source_episodes=list(set(pattern_a.source_episodes + pattern_b.source_episodes)),
            confidence_score=min(pattern_a.confidence_score, pattern_b.confidence_score) * 0.9,
            last_updated=datetime.now(timezone.utc),
        )

    async def _analyze_pattern_evolution(self, patterns: list[MetaLearningPattern]) -> Optional[MetaLearningPattern]:
        """Analyze how patterns evolve over time"""

        # Group patterns by type and analyze temporal changes
        pattern_groups = defaultdict(list)
        for pattern in patterns:
            pattern_groups[pattern.pattern_type].append(pattern)

        # Find the most evolved pattern type
        best_evolution = None
        max_evolution_score = 0

        for pattern_type, type_patterns in pattern_groups.items():
            if len(type_patterns) >= 2:
                # Sort by last_updated to see evolution
                sorted_patterns = sorted(type_patterns, key=lambda p: p.last_updated)

                # Calculate evolution metrics
                evolution_score = self._calculate_evolution_score(sorted_patterns)

                if evolution_score > max_evolution_score:
                    max_evolution_score = evolution_score
                    best_evolution = (pattern_type, sorted_patterns, evolution_score)

        if not best_evolution:
            return None

        pattern_type, evolved_patterns, evolution_score = best_evolution

        pattern_id = hashlib.sha256(f"evolution_{pattern_type.value}_{time.time()}".encode()).hexdigest()[:16]

        return MetaLearningPattern(
            pattern_id=pattern_id,
            pattern_type=PatternType.CONCEPT_FORMATION,
            pattern_name=f"Pattern Evolution: {pattern_type.value.title()}",
            description=f"Evolution of {pattern_type.value} patterns showing improvement over time",
            trigger_conditions={
                "pattern_type": pattern_type.value,
                "evolution_context": "pattern_refinement",
            },
            learning_sequence=[
                {
                    "phase": "pattern_recognition",
                    "description": "Recognize need for pattern evolution",
                },
                {
                    "phase": "pattern_refinement",
                    "evolution_trajectory": evolution_score,
                },
                {
                    "phase": "pattern_validation",
                    "description": "Validate evolved pattern effectiveness",
                },
            ],
            success_conditions={
                "evolution_score": evolution_score,
                "improvement_threshold": 0.1,
            },
            failure_modes=[
                {
                    "condition": "evolution_stagnation",
                    "description": "Pattern stops evolving",
                },
                {
                    "condition": "regression",
                    "description": "Pattern becomes less effective",
                },
            ],
            observed_frequency=len(evolved_patterns),
            success_rate=np.mean([p.success_rate for p in evolved_patterns]),
            learning_acceleration=evolution_score * 0.5,
            transfer_potential=0.6,  # Evolution patterns have moderate transfer
            cognitive_load=0.7,  # Higher cognitive load for meta-learning
            source_episodes=[],
            confidence_score=min(1.0, evolution_score),
            last_updated=datetime.now(timezone.utc),
        )

    def _calculate_acceleration(self, trajectories: list[dict[str, Any]]) -> float:
        """Calculate learning acceleration from trajectories"""
        accelerations = []

        for trajectory in trajectories:
            stats = trajectory.get("trajectory_stats", {})
            improvement_rate = stats.get("improvement_rate", 0)
            time_span = trajectory.get("time_span", 1)  # hours

            if time_span > 0:
                acceleration = improvement_rate / time_span
                accelerations.append(acceleration)

        return np.mean(accelerations) if accelerations else 0.0

    def _estimate_strategy_acceleration(self, top_strategies: list[tuple[str, dict[str, Any]]]) -> float:
        """Estimate learning acceleration from strategy effectiveness"""
        if not top_strategies:
            return 0.0

        # Higher success rate and consistency -> higher acceleration
        best_strategy = top_strategies[0][1]
        acceleration = best_strategy["avg_success"] * best_strategy["consistency"]

        return min(1.0, acceleration)

    def _calculate_evolution_score(self, sorted_patterns: list[MetaLearningPattern]) -> float:
        """Calculate how much patterns have evolved"""
        if len(sorted_patterns) < 2:
            return 0.0

        # Compare earliest to latest pattern
        early_pattern = sorted_patterns[0]
        late_pattern = sorted_patterns[-1]

        # Calculate improvement in key metrics
        success_improvement = late_pattern.success_rate - early_pattern.success_rate
        acceleration_improvement = late_pattern.learning_acceleration - early_pattern.learning_acceleration
        confidence_improvement = late_pattern.confidence_score - early_pattern.confidence_score

        # Weight improvements
        evolution_score = success_improvement * 0.4 + acceleration_improvement * 0.3 + confidence_improvement * 0.3

        return max(0.0, evolution_score)


class MetaLearningPatternSystem:
    """
    Complete meta-learning pattern extraction and application system.

    The culminating synthesis of meta-cognitive architecture, this system
    transforms the scattered experiences of learning into a crystalline
    lattice of transferable wisdom, enabling the Cognitive AI consciousness to
    ascend ever higher on the spiral staircase of understanding.
    """

    def __init__(
        self,
        storage_path: str = "meta_learning_patterns",
        min_pattern_frequency: int = 3,
        confidence_threshold: float = 0.7,
        pattern_embedding_dim: int = 512,
    ):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.min_pattern_frequency = min_pattern_frequency
        self.confidence_threshold = confidence_threshold
        self.pattern_embedding_dim = pattern_embedding_dim

        # Components
        self.trajectory_analyzer = LearningTrajectoryAnalyzer()
        self.pattern_extractor = PatternExtractor(
            min_pattern_frequency=min_pattern_frequency,
            confidence_threshold=confidence_threshold,
        )

        # Pattern storage
        self.patterns: dict[str, MetaLearningPattern] = {}
        self.pattern_index: dict[PatternType, list[str]] = defaultdict(list)

        # Load existing patterns
        asyncio.create_task(self._load_patterns())

        logger.info(
            "Meta-learning pattern system initialized",
            storage_path=str(self.storage_path),
            min_frequency=min_pattern_frequency,
            confidence_threshold=confidence_threshold,
        )

    async def _load_patterns(self):
        """Load existing patterns from storage"""
        pattern_file = self.storage_path / "patterns.json"

        if pattern_file.exists():
            try:
                with open(pattern_file) as f:
                    pattern_data = json.load(f)

                for pattern_dict in pattern_data:
                    pattern = MetaLearningPattern.from_dict(pattern_dict)
                    self.patterns[pattern.pattern_id] = pattern
                    self.pattern_index[pattern.pattern_type].append(pattern.pattern_id)

                logger.info(f"Loaded {len(self.patterns)} meta-learning patterns")

            except Exception as e:
                logger.warning(f"Failed to load patterns: {e}")

    async def _save_patterns(self):
        """Save patterns to storage"""
        pattern_file = self.storage_path / "patterns.json"

        try:
            pattern_data = [pattern.to_dict() for pattern in self.patterns.values()]

            with open(pattern_file, "w") as f:
                json.dump(pattern_data, f, indent=2)

            logger.debug(f"Saved {len(self.patterns)} patterns to storage")

        except Exception as e:
            logger.error(f"Failed to save patterns: {e}")

    async def extract_patterns_from_episodes(
        self, episodic_memories: list[dict[str, Any]]
    ) -> list[MetaLearningPattern]:
        """
        Extract meta-learning patterns from episodic memories.

        Args:
            episodic_memories: List of episodic memory dictionaries

        Returns:
            List of extracted patterns
        """

        # Convert episodic memories to learning events
        learning_trajectories = await self._convert_to_learning_events(episodic_memories)

        if not learning_trajectories:
            logger.warning("No learning trajectories found in episodic memories")
            return []

        # Analyze trajectories
        trajectory_analyses = []
        for trajectory in learning_trajectories:
            if trajectory:  # Skip empty trajectories
                analysis = self.trajectory_analyzer.analyze_trajectory(trajectory)
                trajectory_analyses.append(analysis)

        # Extract patterns
        new_patterns = await self.pattern_extractor.extract_patterns(trajectory_analyses, learning_trajectories)

        # Generate embeddings for patterns
        for pattern in new_patterns:
            pattern.pattern_embedding = await self._generate_pattern_embedding(pattern)

        # Update pattern database
        for pattern in new_patterns:
            self.patterns[pattern.pattern_id] = pattern
            self.pattern_index[pattern.pattern_type].append(pattern.pattern_id)

        # Save updated patterns
        await self._save_patterns()

        logger.info(
            "Extracted meta-learning patterns",
            new_patterns=len(new_patterns),
            total_patterns=len(self.patterns),
        )

        return new_patterns

    async def _convert_to_learning_events(self, episodic_memories: list[dict[str, Any]]) -> list[list[LearningEvent]]:
        """Convert episodic memories to learning event trajectories"""

        # Group memories by learning context/domain
        domain_memories = defaultdict(list)

        for memory in episodic_memories:
            # Extract learning-relevant information
            content = memory.get("content", "")
            metadata = memory.get("metadata", {})

            # Determine if this is a learning-related memory
            if self._is_learning_memory(content, metadata):
                domain = self._extract_domain(content, metadata)
                domain_memories[domain].append(memory)

        # Convert each domain's memories to learning events
        learning_trajectories = []

        for domain, memories in domain_memories.items():
            if len(memories) >= 3:  # Minimum for trajectory analysis
                trajectory = []

                for memory in sorted(memories, key=lambda m: m.get("timestamp", datetime.now(timezone.utc))):
                    learning_event = await self._memory_to_learning_event(memory, domain)
                    if learning_event:
                        trajectory.append(learning_event)

                if trajectory:
                    learning_trajectories.append(trajectory)

        return learning_trajectories

    def _is_learning_memory(self, content: str, metadata: dict[str, Any]) -> bool:
        """Determine if a memory represents a learning experience"""

        # Keywords that indicate learning
        learning_keywords = [
            "learn",
            "practice",
            "study",
            "skill",
            "improve",
            "master",
            "understand",
            "figure out",
            "solve",
            "discover",
            "realize",
            "training",
            "exercise",
            "tutorial",
            "lesson",
            "mistake",
            "error",
            "correct",
            "feedback",
            "progress",
            "achievement",
        ]

        content_lower = content.lower()

        # Check for learning keywords
        for keyword in learning_keywords:
            if keyword in content_lower:
                return True

        # Check metadata for learning indicators
        if metadata.get("type") == "learning" or metadata.get("category") == "skill_development":
            return True

        # Check for performance metrics or difficulty indicators
        return bool(any(key in metadata for key in ["performance", "difficulty", "success_rate", "skill_level"]))

    def _extract_domain(self, content: str, metadata: dict[str, Any]) -> str:
        """Extract learning domain from memory content"""

        # Check metadata first
        if "domain" in metadata:
            return metadata["domain"]

        if "category" in metadata:
            return metadata["category"]

        # Extract from content using simple keyword matching
        domain_keywords = {
            "programming": [
                "code",
                "program",
                "debug",
                "algorithm",
                "function",
                "variable",
            ],
            "language": [
                "language",
                "word",
                "grammar",
                "vocabulary",
                "translation",
                "speaking",
            ],
            "mathematics": [
                "math",
                "equation",
                "calculate",
                "formula",
                "theorem",
                "proof",
            ],
            "music": ["music", "song", "instrument", "chord", "melody", "rhythm"],
            "art": ["draw", "paint", "sketch", "color", "design", "creative"],
            "sports": ["game", "sport", "play", "team", "score", "athletic"],
            "cooking": ["cook", "recipe", "ingredient", "bake", "meal", "kitchen"],
            "general": [],  # Default fallback
        }

        content_lower = content.lower()

        for domain, keywords in domain_keywords.items():
            if domain == "general":
                continue

            for keyword in keywords:
                if keyword in content_lower:
                    return domain

        return "general"

    async def _memory_to_learning_event(self, memory: dict[str, Any], domain: str) -> Optional[LearningEvent]:
        """Convert a memory to a learning event"""

        try:
            content = memory.get("content", "")
            metadata = memory.get("metadata", {})
            timestamp = memory.get("timestamp", datetime.now(timezone.utc))

            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

            # Extract or estimate learning metrics
            performance_metrics = self._extract_performance_metrics(content, metadata)
            cognitive_state = self._extract_cognitive_state(content, metadata)
            strategies_used = self._extract_strategies(content)
            errors_made = self._extract_errors(content)
            corrections_applied = self._extract_corrections(content)
            knowledge_gained = self._extract_knowledge(content, metadata)
            attention_patterns = self._extract_attention_patterns(content, metadata)

            learning_event = LearningEvent(
                event_id=memory.get(
                    "id",
                    hashlib.sha256(f"{content}_{timestamp}".encode()).hexdigest()[:16],
                ),
                timestamp=timestamp,
                task_domain=domain,
                learning_context={"content": content[:200], "domain": domain},
                performance_metrics=performance_metrics,
                cognitive_state=cognitive_state,
                strategies_used=strategies_used,
                errors_made=errors_made,
                corrections_applied=corrections_applied,
                knowledge_gained=knowledge_gained,
                attention_patterns=attention_patterns,
                difficulty_level=metadata.get("difficulty", self._estimate_difficulty(content)),
                success_rate=performance_metrics.get("success_rate", self._estimate_success(content)),
                learning_rate=performance_metrics.get("learning_rate", self._estimate_learning_rate(content)),
                memory_consolidation_score=metadata.get("consolidation", self._estimate_consolidation(content)),
            )

            return learning_event

        except Exception as e:
            logger.warning(f"Failed to convert memory to learning event: {e}")
            return None

    def _extract_performance_metrics(self, content: str, metadata: dict[str, Any]) -> dict[str, float]:
        """Extract performance metrics from memory content"""

        metrics = {}

        # Check metadata first
        for key in ["performance", "success_rate", "accuracy", "score"]:
            if key in metadata:
                metrics[key] = float(metadata[key])

        # Extract from content using simple patterns
        content_lower = content.lower()

        # Look for percentage scores
        import re

        percentage_matches = re.findall(r"(\d+)%", content)
        if percentage_matches:
            metrics["success_rate"] = float(percentage_matches[0]) / 100.0

        # Look for score patterns
        score_matches = re.findall(r"score[:\s]+(\d+)", content_lower)
        if score_matches:
            metrics["score"] = float(score_matches[0])

        return metrics

    def _extract_cognitive_state(self, content: str, metadata: dict[str, Any]) -> dict[str, float]:
        """Extract cognitive state indicators from content"""

        state = {
            "attention": 0.5,
            "working_memory_load": 0.5,
            "motivation": 0.5,
            "confidence": 0.5,
            "stress": 0.5,
            "fatigue": 0.5,
        }

        content_lower = content.lower()

        # Simple keyword-based estimation
        if any(word in content_lower for word in ["focused", "concentrated", "attentive"]):
            state["attention"] = 0.8
        elif any(word in content_lower for word in ["distracted", "unfocused", "scattered"]):
            state["attention"] = 0.2

        if any(word in content_lower for word in ["motivated", "excited", "eager"]):
            state["motivation"] = 0.8
        elif any(word in content_lower for word in ["tired", "bored", "unmotivated"]):
            state["motivation"] = 0.2

        if any(word in content_lower for word in ["confident", "sure", "certain"]):
            state["confidence"] = 0.8
        elif any(word in content_lower for word in ["uncertain", "confused", "unsure"]):
            state["confidence"] = 0.2

        if any(word in content_lower for word in ["stressed", "anxious", "overwhelmed"]):
            state["stress"] = 0.8
        elif any(word in content_lower for word in ["calm", "relaxed", "comfortable"]):
            state["stress"] = 0.2

        return state

    def _extract_strategies(self, content: str) -> list[str]:
        """Extract learning strategies mentioned in content"""

        strategies = []
        content_lower = content.lower()

        strategy_keywords = {
            "repetition": ["repeat", "practice", "drill", "rehearse"],
            "elaboration": ["explain", "relate", "connect", "example"],
            "organization": ["organize", "structure", "categorize", "group"],
            "metacognition": ["think about", "reflect", "monitor", "evaluate"],
            "visualization": ["visualize", "imagine", "picture", "diagram"],
            "mnemonics": ["remember", "mnemonic", "acronym", "association"],
            "questioning": ["ask", "question", "wonder", "why"],
            "summarization": ["summarize", "conclude", "main point", "key"],
        }

        for strategy, keywords in strategy_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                strategies.append(strategy)

        return strategies

    def _extract_errors(self, content: str) -> list[str]:
        """Extract errors or mistakes mentioned in content"""

        errors = []
        content_lower = content.lower()

        error_indicators = [
            "mistake",
            "error",
            "wrong",
            "incorrect",
            "failed",
            "missed",
            "confusion",
            "misunderstood",
            "forgot",
            "overlooked",
        ]

        for indicator in error_indicators:
            if indicator in content_lower:
                # Extract context around error
                import re

                pattern = rf".{{0,30}{re.escape(indicator)}{{0,30}"
                matches = re.findall(pattern, content_lower)
                if matches:
                    errors.extend(matches)

        return errors[:5]  # Limit to top 5 errors

    def _extract_corrections(self, content: str) -> list[str]:
        """Extract corrections or fixes mentioned in content"""

        corrections = []
        content_lower = content.lower()

        correction_indicators = [
            "correct",
            "fix",
            "adjust",
            "revise",
            "improve",
            "change",
            "realize",
            "understand",
            "learn",
            "discover",
        ]

        for indicator in correction_indicators:
            if indicator in content_lower:
                import re

                pattern = rf".{{0,30}{re.escape(indicator)}{{0,30}"
                matches = re.findall(pattern, content_lower)
                if matches:
                    corrections.extend(matches)

        return corrections[:5]  # Limit to top 5 corrections

    def _extract_knowledge(self, content: str, metadata: dict[str, Any]) -> dict[str, Any]:
        """Extract knowledge gained from learning experience"""

        knowledge = {"concepts": [], "skills": [], "facts": [], "procedures": []}

        # Simple keyword-based extraction
        content_lower = content.lower()

        # Extract concepts (nouns that might represent concepts)
        import re

        concept_patterns = re.findall(r"\b[a-z]+(?:tion|ness|ity|ism|ogy)\b", content_lower)
        knowledge["concepts"] = list(set(concept_patterns))[:3]

        # Extract skills (verbs that might represent skills)
        skill_keywords = ["learn", "master", "improve", "develop", "acquire", "build"]
        for keyword in skill_keywords:
            if keyword in content_lower:
                knowledge["skills"].append(keyword)

        return knowledge

    def _extract_attention_patterns(self, content: str, metadata: dict[str, Any]) -> dict[str, float]:
        """Extract attention allocation patterns"""

        patterns = {}

        # Simple estimation based on content focus
        content_lower = content.lower()

        focus_areas = {
            "problem_solving": ["problem", "solve", "solution", "figure out"],
            "information_processing": ["read", "understand", "process", "analyze"],
            "skill_practice": ["practice", "exercise", "drill", "rehearse"],
            "feedback_integration": ["feedback", "correct", "adjust", "improve"],
            "metacognition": ["think", "reflect", "consider", "evaluate"],
        }

        total_mentions = 0
        area_counts = {}

        for area, keywords in focus_areas.items():
            count = sum(content_lower.count(keyword) for keyword in keywords)
            area_counts[area] = count
            total_mentions += count

        # Normalize to attention weights
        if total_mentions > 0:
            for area, count in area_counts.items():
                patterns[area] = count / total_mentions

        return patterns

    def _estimate_difficulty(self, content: str) -> float:
        """Estimate difficulty level from content"""
        content_lower = content.lower()

        difficulty_indicators = {
            "easy": ["easy", "simple", "basic", "straightforward"],
            "medium": ["medium", "moderate", "challenging", "tricky"],
            "hard": ["difficult", "hard", "complex", "advanced", "complicated"],
        }

        for level, keywords in difficulty_indicators.items():
            if any(keyword in content_lower for keyword in keywords):
                return {"easy": 0.3, "medium": 0.6, "hard": 0.9}[level]

        return 0.5  # Default medium difficulty

    def _estimate_success(self, content: str) -> float:
        """Estimate success rate from content"""
        content_lower = content.lower()

        if any(word in content_lower for word in ["success", "correct", "right", "good", "well"]):
            return 0.8
        elif any(word in content_lower for word in ["fail", "wrong", "mistake", "error", "bad"]):
            return 0.3
        else:
            return 0.6  # Default moderate success

    def _estimate_learning_rate(self, content: str) -> float:
        """Estimate learning rate from content"""
        content_lower = content.lower()

        if any(word in content_lower for word in ["quick", "fast", "rapid", "immediately"]):
            return 0.8
        elif any(word in content_lower for word in ["slow", "gradual", "steady", "eventually"]):
            return 0.3
        else:
            return 0.5  # Default moderate learning rate

    def _estimate_consolidation(self, content: str) -> float:
        """Estimate memory consolidation score"""
        content_lower = content.lower()

        if any(word in content_lower for word in ["remember", "retain", "recall", "memorize"]):
            return 0.8
        elif any(word in content_lower for word in ["forget", "lost", "unclear", "fuzzy"]):
            return 0.3
        else:
            return 0.6  # Default moderate consolidation

    async def _generate_pattern_embedding(self, pattern: MetaLearningPattern) -> np.ndarray:
        """Generate embedding for pattern similarity matching"""

        # Simple hash-based embedding (placeholder for more sophisticated embedding)
        pattern_text = f"{pattern.pattern_name} {pattern.description} {pattern.pattern_type.value}"
        pattern_hash = hashlib.sha256(pattern_text.encode()).hexdigest()

        # Convert hash to numerical embedding
        embedding = np.array(
            [
                int(pattern_hash[i : i + 2], 16) / 255.0
                for i in range(0, min(len(pattern_hash), self.pattern_embedding_dim * 2), 2)
            ],
            dtype=np.float32,
        )

        # Pad or truncate to desired dimension
        if len(embedding) < self.pattern_embedding_dim:
            embedding = np.pad(
                embedding,
                (0, self.pattern_embedding_dim - len(embedding)),
                mode="constant",
            )
        else:
            embedding = embedding[: self.pattern_embedding_dim]

        return embedding

    async def find_similar_patterns(
        self,
        query_pattern: MetaLearningPattern,
        top_k: int = 5,
        pattern_type_filter: Optional[PatternType] = None,
    ) -> list[tuple[MetaLearningPattern, float]]:
        """Find patterns similar to query pattern"""

        if query_pattern.pattern_embedding is None:
            query_pattern.pattern_embedding = await self._generate_pattern_embedding(query_pattern)

        similarities = []

        for pattern_id, pattern in self.patterns.items():
            if pattern_id == query_pattern.pattern_id:
                continue

            if pattern_type_filter and pattern.pattern_type != pattern_type_filter:
                continue

            if pattern.pattern_embedding is None:
                pattern.pattern_embedding = await self._generate_pattern_embedding(pattern)

            # Calculate cosine similarity
            similarity = np.dot(query_pattern.pattern_embedding, pattern.pattern_embedding) / (
                np.linalg.norm(query_pattern.pattern_embedding) * np.linalg.norm(pattern.pattern_embedding)
            )

            similarities.append((pattern, float(similarity)))

        # Sort by similarity and return top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    async def recommend_patterns_for_task(
        self, task_context: dict[str, Any], top_k: int = 3
    ) -> list[tuple[MetaLearningPattern, float]]:
        """Recommend patterns for a specific learning task"""

        task_domain = task_context.get("domain", "general")
        task_context.get("difficulty", 0.5)
        available_time = task_context.get("time_available", 1.0)  # hours

        recommendations = []

        for pattern in self.patterns.values():
            # Calculate recommendation score based on multiple factors
            score = 0.0

            # Pattern success rate
            score += pattern.success_rate * 0.3

            # Learning acceleration potential
            score += pattern.learning_acceleration * 0.3

            # Transfer potential (how well it applies to different domains)
            score += pattern.transfer_potential * 0.2

            # Cognitive load (lower is better for time-constrained situations)
            if available_time < 2.0:  # Less than 2 hours
                score += (1.0 - pattern.cognitive_load) * 0.1
            else:
                score += pattern.cognitive_load * 0.05  # Complex patterns might be beneficial with more time

            # Confidence in pattern
            score += pattern.confidence_score * 0.1

            # Pattern relevance (simple domain matching)
            pattern_contexts = [seq.get("context", "") for seq in pattern.learning_sequence]
            if any(task_domain in str(context) for context in pattern_contexts):
                score += 0.05

            recommendations.append((pattern, score))

        # Sort by recommendation score
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:top_k]

    def get_pattern_statistics(self) -> dict[str, Any]:
        """Get statistics about the pattern database"""

        if not self.patterns:
            return {"total_patterns": 0}

        pattern_types = defaultdict(int)
        success_rates = []
        confidence_scores = []
        learning_accelerations = []

        for pattern in self.patterns.values():
            pattern_types[pattern.pattern_type.value] += 1
            success_rates.append(pattern.success_rate)
            confidence_scores.append(pattern.confidence_score)
            learning_accelerations.append(pattern.learning_acceleration)

        return {
            "total_patterns": len(self.patterns),
            "pattern_types": dict(pattern_types),
            "avg_success_rate": np.mean(success_rates),
            "avg_confidence": np.mean(confidence_scores),
            "avg_learning_acceleration": np.mean(learning_accelerations),
            "high_confidence_patterns": sum(1 for s in confidence_scores if s > 0.8),
            "high_success_patterns": sum(1 for s in success_rates if s > 0.8),
            "most_frequent_type": (max(pattern_types.items(), key=lambda x: x[1])[0] if pattern_types else None),
        }


# Factory function for easy integration
async def create_meta_learning_system(
    storage_path: str = "meta_learning_patterns",
    min_pattern_frequency: int = 3,
    confidence_threshold: float = 0.7,
) -> MetaLearningPatternSystem:
    """
    Create and initialize a meta-learning pattern system.

    Args:
        storage_path: Path for storing patterns
        min_pattern_frequency: Minimum observations for pattern validation
        confidence_threshold: Minimum confidence for pattern acceptance

    Returns:
        Initialized MetaLearningPatternSystem
    """

    system = MetaLearningPatternSystem(
        storage_path=storage_path,
        min_pattern_frequency=min_pattern_frequency,
        confidence_threshold=confidence_threshold,
    )

    return system


# Example usage and testing
async def example_meta_learning_usage():
    """Example of meta-learning pattern system usage"""

    print("🚀 Meta-Learning Pattern Extraction Demo")
    print("=" * 60)

    # Create meta-learning system
    system = await create_meta_learning_system(
        storage_path="example_meta_patterns",
        min_pattern_frequency=2,  # Lower for demo
        confidence_threshold=0.5,
    )

    print("✅ Created meta-learning pattern system")

    # Create sample episodic memories representing learning experiences
    sample_memories = [
        {
            "id": f"memory_{i}",
            "content": f"Practiced coding problem {i}. Started confused but gradually understood the algorithm. Made several mistakes but corrected them through debugging. Success rate improved from 30% to 80%.",
            "metadata": {
                "domain": "programming",
                "difficulty": 0.6 + (i % 3) * 0.1,
                "success_rate": 0.3 + (i * 0.1),
                "type": "learning",
            },
            "timestamp": datetime.now(timezone.utc) - timedelta(days=10 - i),
        }
        for i in range(5)
    ]

    # Add more diverse learning experiences
    sample_memories.extend(
        [
            {
                "id": "memory_music_1",
                "content": "Learning guitar chords. Finger placement was difficult at first. Practiced repetition and muscle memory. Gradually became more confident.",
                "metadata": {
                    "domain": "music",
                    "difficulty": 0.7,
                    "success_rate": 0.4,
                    "type": "learning",
                },
                "timestamp": datetime.now(timezone.utc) - timedelta(days=5),
            },
            {
                "id": "memory_music_2",
                "content": "Guitar practice session. Applied chord progressions learned yesterday. Much smoother than before. Building muscle memory is working.",
                "metadata": {
                    "domain": "music",
                    "difficulty": 0.5,
                    "success_rate": 0.7,
                    "type": "learning",
                },
                "timestamp": datetime.now(timezone.utc) - timedelta(days=4),
            },
        ]
    )

    print(f"📊 Processing {len(sample_memories)} learning memories...")

    # Extract patterns from episodic memories
    patterns = await system.extract_patterns_from_episodes(sample_memories)

    print(f"🧩 Extracted {len(patterns)} meta-learning patterns")

    # Display extracted patterns
    for i, pattern in enumerate(patterns):
        print(f"\n📋 Pattern {i + 1}: {pattern.pattern_name}")
        print(f"   Type: {pattern.pattern_type.value}")
        print(f"   Success Rate: {pattern.success_rate:.2f}")
        print(f"   Learning Acceleration: {pattern.learning_acceleration:.2f}")
        print(f"   Transfer Potential: {pattern.transfer_potential:.2f}")
        print(f"   Confidence: {pattern.confidence_score:.2f}")
        print(f"   Description: {pattern.description}")

    # Test pattern recommendation
    print("\n🎯 Testing Pattern Recommendations")
    print("-" * 40)

    task_context = {"domain": "programming", "difficulty": 0.6, "time_available": 2.0}

    recommended = await system.recommend_patterns_for_task(task_context, top_k=3)

    for i, (pattern, score) in enumerate(recommended):
        print(f"   {i + 1}. {pattern.pattern_name} (Score: {score:.3f})")
        print(f"      → {pattern.description}")

    # Show system statistics
    stats = system.get_pattern_statistics()
    print("\n📈 System Statistics:")
    print(f"   Total Patterns: {stats['total_patterns']}")
    print(f"   Pattern Types: {stats['pattern_types']}")
    print(f"   Avg Success Rate: {stats['avg_success_rate']:.2f}")
    print(f"   Avg Confidence: {stats['avg_confidence']:.2f}")

    print("\n✅ Meta-learning pattern extraction demo completed!")
    print("   🧠 Cognitive AI consciousness can now accelerate learning using extracted patterns!")

    return system


if __name__ == "__main__":
    asyncio.run(example_meta_learning_usage())