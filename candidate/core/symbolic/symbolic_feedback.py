"""

#TAG:core
#TAG:symbolic
#TAG:neuroplastic
#TAG:colony

Symbolic Feedback Loop System
============================

Priority #3: Feedback Loops for Optimization using symbolic recall and dream replays
Constructs symbolic feedback using intent_node history, memoria snapshots,
    and dream replays
tagged with success/failure for symbolic meta-learning rehearsal.

🔗 Integration Points:
- Intent_node history for learning pattern analysis
- Memoria snapshots for coherence tracking
- Dream replay success/failure tagging for optimization
- Symbolic reasoning confidence for meta-learning adjustments
- Voice_Pack emotional feedback integration

__meta__ = {
    "signature": "QNTM-ETH-FED-v1",
    "linked_to": ["intent_node", "memoria", "dream_engine", "monitor_dashboard",
    "rate_modulator"],
    "version": "0.1.0"
}
"""
import hashlib
import json
import logging
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

import numpy as np

from ..meta_learning.monitor_dashboard import MetaLearningMonitorDashboard
from ..meta_learning.rate_modulator import AdaptationStrategy, DynamicLearningRateModulator

logger = logging.getLogger("LUKHAS.MetaLearning.SymbolicFeedback")

__meta__ = {
    "signature": "QNTM-ETH-FED-v1",
    "linked_to": [
        "intent_node",
        "memoria",
        "dream_engine",
        "monitor_dashboard",
        "rate_modulator",
    ],
    "version": "0.1.0",
}


class FeedbackType(Enum):
    """Types of symbolic feedback"""

    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    UNKNOWN = "unknown"
    REHEARSAL = "rehearsal"


class SymbolicContext(Enum):
    """Context types for symbolic operations"""

    INTENT_RESOLUTION = "intent_resolution"
    MEMORIA_RETRIEVAL = "memoria_retrieval"
    DREAM_REPLAY = "dream_replay"
    LEARNING_STRATEGY = "learning_strategy"
    ETHICAL_DECISION = "ethical_decision"
    SYMBOLIC_REASONING = "symbolic_reasoning"


@dataclass
class Intentnodehistory:
    """Historical record from intent_node operations"""

    timestamp: str
    intent_id: str
    intent_type: str
    resolution_success: bool
    confidence_score: float
    reasoning_steps: list[str]
    memory_references: list[str]
    emotional_context: list[float]
    qi_signature: str


@dataclass
class Memoriasnapshot:
    """Snapshot from memoria system"""

    timestamp: str
    snapshot_id: str
    coherence_score: float
    memory_fragments: list[dict[str, Any]]
    retrieval_success_rate: float
    consolidation_quality: float
    symbolic_links: list[str]
    qi_signature: str


@dataclass
class Dreamreplayrecord:
    """Record from dream replay system"""

    timestamp: str
    replay_id: str
    scenario_type: str
    replay_success: bool
    learning_outcome: FeedbackType
    performance_delta: float
    symbolic_insights: list[str]
    emotional_resonance: float
    qi_signature: str


@dataclass
class Symbolicfeedbackloop:
    """Complete symbolic feedback loop record"""

    timestamp: str
    loop_id: str
    context: SymbolicContext
    feedback_type: FeedbackType
    success_metrics: dict[str, float]
    failure_patterns: list[str]
    optimization_suggestions: list[str]
    rehearsal_opportunities: list[str]
    confidence_adjustment: float
    qi_signature: str


class Symbolicfeedbacksystem:
    """
    Symbolic Feedback Loop System for Meta-Learning Enhancement

    Enables symbolic meta-learning through pattern recognition, dream rehearsal,
    and feedback-driven optimization based on intent success patterns and
    memoria coherence tracking.
    """

    # ΛREASONING_LOOP: This entire class is a reasoning loop that processes
    # feedback and generates optimizations.

    def __init__(
        self,
        dashboard: MetaLearningMonitorDashboard,
        rate_modulator: Optional[DynamicLearningRateModulator] = None,
        max_history_size: int = 5000,
        feedback_threshold: float = 0.7,
        rehearsal_frequency: int = 10,
    ):
        # ΛTRACE_NODE: Initialization of the symbolic feedback system.
        self.dashboard = dashboard
        self.rate_modulator = rate_modulator
        self.max_history_size = max_history_size
        self.feedback_threshold = feedback_threshold
        self.rehearsal_frequency = rehearsal_frequency

        # Symbolic feedback storage
        self.intent_history = deque(maxlen=max_history_size)
        self.memoria_snapshots = deque(maxlen=max_history_size)
        self.dream_replays = deque(maxlen=max_history_size)
        self.feedback_loops = deque(maxlen=max_history_size)

        # Pattern analysis
        self.success_patterns = defaultdict(list)
        self.failure_patterns = defaultdict(list)
        self.rehearsal_queue = deque(maxlen=100)

        # Performance tracking
        self.optimization_history = deque(maxlen=1000)
        self.pattern_confidence = defaultdict(lambda: 0.5)

        # Rehearsal effectiveness
        self.rehearsal_outcomes = defaultdict(list)

        logger.info("Symbolic Feedback System initialized for meta-learning enhancement")

    def log_intent_node_interaction(
        self,
        intent_id: str,
        intent_type: str,
        resolution_success: bool,
        confidence_score: float,
        reasoning_steps: list[str],
        memory_references: Optional[list[str]] = None,
        emotional_context: Optional[list[float]] = None,
    ) -> str:
        """
        Log interaction with intent_node system
        """
        # ΛSYMBOLIC_FEEDBACK: This function is a primary entry point for symbolic feedback from the intent system.
        # ΛEMBODIED_REFLEX: This function acts as a reflex to the actions of the
        # intent_node, logging its performance.
        try:
            memory_references = memory_references or []
            emotional_context = emotional_context or [0.5, 0.5, 0.5, 0.5]

            # Generate quantum signature
            intent_data = {
                "intent_id": intent_id,
                "intent_type": intent_type,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "success": resolution_success,
            }
            qi_signature = self._generate_quantum_signature(intent_data)

            # Create history record
            history_record = IntentNodeHistory(  # noqa: F821
                timestamp=datetime.now(timezone.utc).isoformat(),
                intent_id=intent_id,
                intent_type=intent_type,
                resolution_success=resolution_success,
                confidence_score=confidence_score,
                reasoning_steps=reasoning_steps,
                memory_references=memory_references,
                emotional_context=emotional_context,
                qi_signature=qi_signature,
            )

            self.intent_history.append(history_record)

            # Analyze patterns
            self._analyze_intent_patterns(history_record)

            # Update dashboard with symbolic feedback
            self._update_dashboard_symbolic_feedback()

            logger.debug(f"Intent node interaction logged: {intent_id} - Success: {resolution_success}")
            return qi_signature

        except Exception as e:
            logger.error(f"Error logging intent node interaction: {e}")
            return ""

    def log_memoria_snapshot(
        self,
        snapshot_id: str,
        coherence_score: float,
        memory_fragments: list[dict[str, Any]],
        retrieval_success_rate: float,
        consolidation_quality: float,
        symbolic_links: Optional[list[str]] = None,
    ) -> str:
        """
        Log memoria system snapshot
        """
        try:
            symbolic_links = symbolic_links or []

            # Generate quantum signature
            memoria_data = {
                "snapshot_id": snapshot_id,
                "coherence_score": coherence_score,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "fragment_count": len(memory_fragments),
            }
            qi_signature = self._generate_quantum_signature(memoria_data)

            # Create snapshot record
            snapshot_record = MemoriaSnapshot(  # noqa: F821
                timestamp=datetime.now(timezone.utc).isoformat(),
                snapshot_id=snapshot_id,
                coherence_score=coherence_score,
                memory_fragments=memory_fragments,
                retrieval_success_rate=retrieval_success_rate,
                consolidation_quality=consolidation_quality,
                symbolic_links=symbolic_links,
                qi_signature=qi_signature,
            )

            self.memoria_snapshots.append(snapshot_record)

            # Analyze memoria patterns
            self._analyze_memoria_patterns(snapshot_record)

            # Update dashboard
            self._update_dashboard_symbolic_feedback()

            logger.debug(f"Memoria snapshot logged: {snapshot_id} - Coherence: {coherence_score:.3f}")
            return qi_signature

        except Exception as e:
            logger.error(f"Error logging memoria snapshot: {e}")
            return ""

    def log_dream_replay(
        self,
        replay_id: str,
        scenario_type: str,
        replay_success: bool,
        performance_delta: float,
        symbolic_insights: Optional[list[str]] = None,
        emotional_resonance: float = 0.5,
    ) -> str:
        """
        Log dream replay session with learning outcomes
        """
        try:
            symbolic_insights = symbolic_insights or []

            # Determine learning outcome
            learning_outcome = self._determine_learning_outcome(replay_success, performance_delta)

            # Generate quantum signature
            dream_data = {
                "replay_id": replay_id,
                "scenario_type": scenario_type,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "success": replay_success,
            }
            qi_signature = self._generate_quantum_signature(dream_data)

            # Create replay record
            replay_record = DreamReplayRecord(  # noqa: F821
                timestamp=datetime.now(timezone.utc).isoformat(),
                replay_id=replay_id,
                scenario_type=scenario_type,
                replay_success=replay_success,
                learning_outcome=learning_outcome,
                performance_delta=performance_delta,
                symbolic_insights=symbolic_insights,
                emotional_resonance=emotional_resonance,
                qi_signature=qi_signature,
            )

            self.dream_replays.append(replay_record)

            # Analyze dream patterns
            self._analyze_dream_patterns(replay_record)

            # Schedule rehearsal if needed
            self._schedule_rehearsal_if_needed(replay_record)

            # Update dashboard
            self._update_dashboard_symbolic_feedback()

            logger.debug(f"Dream replay logged: {replay_id} - Outcome: {learning_outcome.value}")
            return qi_signature

        except Exception as e:
            logger.error(f"Error logging dream replay: {e}")
            return ""

    def create_symbolic_feedback_loop(
        self,
        context: SymbolicContext,
        success_metrics: dict[str, float],
        failure_patterns: Optional[list[str]] = None,
        optimization_target: Optional[str] = None,
    ) -> str:
        """
        Create a complete symbolic feedback loop for optimization
        """
        # ΛREASONING_LOOP: This function creates a high-level reasoning loop based
        # on feedback.
        try:
            failure_patterns = failure_patterns or []

            # Analyze current performance patterns
            performance_analysis = self._analyze_performance_patterns(context, success_metrics)

            # Generate optimization suggestions
            optimization_suggestions = self._generate_optimization_suggestions(
                context,
                success_metrics,
                failure_patterns,
                performance_analysis,
            )

            # Identify rehearsal opportunities
            rehearsal_opportunities = self._identify_rehearsal_opportunities(context, performance_analysis)

            # Calculate confidence adjustment
            confidence_adjustment = self._calculate_confidence_adjustment(success_metrics, performance_analysis)

            # Determine feedback type
            feedback_type = self._determine_feedback_type(success_metrics, failure_patterns)

            # Generate loop ID and quantum signature
            loop_id = self._generate_loop_id(context)
            loop_data = {
                "loop_id": loop_id,
                "context": context.value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "feedback_type": feedback_type.value,
            }
            qi_signature = self._generate_quantum_signature(loop_data)

            # Create feedback loop record
            feedback_loop = SymbolicFeedbackLoop(  # noqa: F821
                timestamp=datetime.now(timezone.utc).isoformat(),
                loop_id=loop_id,
                context=context,
                feedback_type=feedback_type,
                success_metrics=success_metrics,
                failure_patterns=failure_patterns,
                optimization_suggestions=optimization_suggestions,
                rehearsal_opportunities=rehearsal_opportunities,
                confidence_adjustment=confidence_adjustment,
                qi_signature=qi_signature,
            )

            self.feedback_loops.append(feedback_loop)

            # Apply optimizations if confidence is high enough
            if abs(confidence_adjustment) > 0.1:
                self._apply_symbolic_optimizations(feedback_loop)

            # Update pattern confidence
            self._update_pattern_confidence(context, feedback_type, success_metrics)

            logger.info(f"Symbolic feedback loop created: {loop_id} - Type: {feedback_type.value}")
            return loop_id

        except Exception as e:
            logger.error(f"Error creating symbolic feedback loop: {e}")
            return ""

    def execute_symbolic_rehearsal(self, scenario_pattern: str, max_iterations: int = 5) -> dict[str, Any]:
        """
        Execute symbolic rehearsal based on successful patterns
        """
        try:
            rehearsal_results = {
                "scenario_pattern": scenario_pattern,
                "iterations": 0,
                "success_rate": 0.0,
                "performance_improvements": [],
                "insights_generated": [],
                "confidence_gain": 0.0,
            }

            # Find relevant successful patterns
            relevant_patterns = self._find_relevant_success_patterns(scenario_pattern)

            if not relevant_patterns:
                logger.warning(f"No relevant patterns found for rehearsal: {scenario_pattern}")
                return rehearsal_results

            # Execute rehearsal iterations
            for iteration in range(max_iterations):
                rehearsal_outcome = self._simulate_rehearsal_iteration(scenario_pattern, relevant_patterns, iteration)

                rehearsal_results["iterations"] += 1
                rehearsal_results["performance_improvements"].append(rehearsal_outcome["performance_delta"])
                rehearsal_results["insights_generated"].extend(rehearsal_outcome["insights"])

                # Stop if performance stops improving
                if iteration > 0 and rehearsal_outcome["performance_delta"] < 0.01:
                    break

            # Calculate overall results
            if rehearsal_results["iterations"] > 0:
                rehearsal_results["success_rate"] = (
                    len([p for p in rehearsal_results["performance_improvements"] if p > 0])
                    / rehearsal_results["iterations"]
                )
                rehearsal_results["confidence_gain"] = np.mean(rehearsal_results["performance_improvements"])

                # Log rehearsal outcome
                self.rehearsal_outcomes[scenario_pattern].append(rehearsal_results)

            logger.info(
                f"Symbolic rehearsal completed: {scenario_pattern} - Success rate: {rehearsal_results['success_rate']:.3f}"
            )
            return rehearsal_results

        except Exception as e:
            logger.error(f"Error executing symbolic rehearsal: {e}")
            return {"error": str(e)}

    def get_optimization_insights(self) -> dict[str, Any]:
        """
        Get insights and recommendations for meta-learning optimization
        """
        try:
            insights = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_feedback_loops": len(self.feedback_loops),
                "pattern_analysis": {},
                "rehearsal_effectiveness": {},
                "optimization_recommendations": [],
                "confidence_trends": {},
            }

            # Analyze patterns by context
            for context in SymbolicContext:
                context_loops = [loop for loop in self.feedback_loops if loop.context == context]
                if context_loops:
                    insights["pattern_analysis"][context.value] = {
                        "total_loops": len(context_loops),
                        "success_rate": len(
                            [loop for loop in context_loops if loop.feedback_type == FeedbackType.SUCCESS]
                        )
                        / len(context_loops),
                        "average_confidence_adjustment": np.mean(
                            [loop.confidence_adjustment for loop in context_loops]
                        ),
                        "common_optimization_suggestions": self._extract_common_suggestions(context_loops),
                    }

            # Analyze rehearsal effectiveness
            for pattern, outcomes in self.rehearsal_outcomes.items():
                if outcomes:
                    insights["rehearsal_effectiveness"][pattern] = {
                        "total_rehearsals": len(outcomes),
                        "average_success_rate": np.mean([outcome["success_rate"] for outcome in outcomes]),
                        "average_confidence_gain": np.mean([outcome["confidence_gain"] for outcome in outcomes]),
                        "total_insights": sum(len(outcome["insights_generated"]) for outcome in outcomes),
                    }

            # Generate optimization recommendations
            insights["optimization_recommendations"] = self._generate_system_optimization_recommendations()

            # Analyze confidence trends
            insights["confidence_trends"] = dict(self.pattern_confidence)

            return insights

        except Exception as e:
            logger.error(f"Error generating optimization insights: {e}")
            return {"error": str(e)}

    def _analyze_intent_patterns(self, history_record: IntentNodeHistory) -> None:  # noqa: F821
        """Analyze patterns from intent node interactions"""
        pattern_key = f"{history_record.intent_type}_{history_record.resolution_success}"

        if history_record.resolution_success:
            self.success_patterns[pattern_key].append(
                {
                    "confidence": history_record.confidence_score,
                    "reasoning_steps": len(history_record.reasoning_steps),
                    "memory_references": len(history_record.memory_references),
                    "emotional_context": history_record.emotional_context,
                    "timestamp": history_record.timestamp,
                }
            )
        else:
            self.failure_patterns[pattern_key].append(
                {
                    "confidence": history_record.confidence_score,
                    "reasoning_steps": history_record.reasoning_steps,
                    "emotional_context": history_record.emotional_context,
                    "timestamp": history_record.timestamp,
                }
            )

    def _analyze_memoria_patterns(self, snapshot_record: MemoriaSnapshot) -> None:  # noqa: F821
        """Analyze patterns from memoria snapshots"""
        coherence_category = (
            "high"
            if snapshot_record.coherence_score > 0.8
            else "medium" if snapshot_record.coherence_score > 0.5 else "low"
        )
        pattern_key = f"memoria_coherence_{coherence_category}"

        pattern_data = {
            "coherence_score": snapshot_record.coherence_score,
            "retrieval_success_rate": snapshot_record.retrieval_success_rate,
            "consolidation_quality": snapshot_record.consolidation_quality,
            "fragment_count": len(snapshot_record.memory_fragments),
            "symbolic_links": len(snapshot_record.symbolic_links),
            "timestamp": snapshot_record.timestamp,
        }

        if snapshot_record.coherence_score > self.feedback_threshold:
            self.success_patterns[pattern_key].append(pattern_data)
        else:
            self.failure_patterns[pattern_key].append(pattern_data)

    def _analyze_dream_patterns(self, replay_record: DreamReplayRecord) -> None:  # noqa: F821
        """Analyze patterns from dream replays"""
        pattern_key = f"{replay_record.scenario_type}_{replay_record.learning_outcome.value}"

        pattern_data = {
            "replay_success": replay_record.replay_success,
            "performance_delta": replay_record.performance_delta,
            "insights_count": len(replay_record.symbolic_insights),
            "emotional_resonance": replay_record.emotional_resonance,
            "timestamp": replay_record.timestamp,
        }

        if replay_record.learning_outcome in [
            FeedbackType.SUCCESS,
            FeedbackType.PARTIAL,
        ]:
            self.success_patterns[pattern_key].append(pattern_data)
        else:
            self.failure_patterns[pattern_key].append(pattern_data)

    def _determine_learning_outcome(self, replay_success: bool, performance_delta: float) -> FeedbackType:
        """Determine learning outcome from dream replay results"""
        if replay_success and performance_delta > 0.1:
            return FeedbackType.SUCCESS
        elif replay_success and performance_delta > 0.05:
            return FeedbackType.PARTIAL
        elif replay_success:
            return FeedbackType.REHEARSAL
        else:
            return FeedbackType.FAILURE

    def _schedule_rehearsal_if_needed(self, replay_record: DreamReplayRecord) -> None:  # noqa: F821
        """Schedule rehearsal based on dream replay outcomes"""
        if replay_record.learning_outcome == FeedbackType.SUCCESS and replay_record.performance_delta > 0.15:
            rehearsal_item = {
                "pattern": replay_record.scenario_type,
                "priority": replay_record.performance_delta,
                "timestamp": replay_record.timestamp,
                "original_replay_id": replay_record.replay_id,
            }

            self.rehearsal_queue.append(rehearsal_item)
            logger.debug(f"Scheduled rehearsal for successful pattern: {replay_record.scenario_type}")

    def _update_dashboard_symbolic_feedback(self) -> None:
        """Update dashboard with current symbolic feedback state"""
        try:
            # Calculate current metrics
            recent_intents = list(self.intent_history)[-10:] if self.intent_history else []
            recent_memoria = list(self.memoria_snapshots)[-5:] if self.memoria_snapshots else []
            recent_dreams = list(self.dream_replays)[-5:] if self.dream_replays else []

            # Calculate metrics
            intent_success_rate = (
                np.mean([intent.confidence_score for intent in recent_intents]) if recent_intents else 0.7
            )
            memoria_coherence = np.mean([snap.coherence_score for snap in recent_memoria]) if recent_memoria else 0.8
            symbolic_reasoning_confidence = self._calculate_symbolic_reasoning_confidence()
            emotional_tone_vector = self._calculate_emotional_tone_vector(recent_intents)
            dream_replay_success = any(dream.replay_success for dream in recent_dreams) if recent_dreams else False

            # Log to dashboard
            self.dashboard.log_symbolic_feedback(
                intent_success_rate=intent_success_rate,
                memoria_coherence=memoria_coherence,
                symbolic_reasoning_confidence=symbolic_reasoning_confidence,
                emotional_tone_vector=emotional_tone_vector,
                dream_replay_success=dream_replay_success,
            )

        except Exception as e:
            logger.error(f"Error updating dashboard symbolic feedback: {e}")

    def _calculate_symbolic_reasoning_confidence(self) -> float:
        """Calculate overall symbolic reasoning confidence"""
        if not self.feedback_loops:
            return 0.7  # Default

        recent_loops = list(self.feedback_loops)[-10:]
        confidence_adjustments = [loop.confidence_adjustment for loop in recent_loops]

        # Base confidence with recent adjustments
        base_confidence = 0.7
        avg_adjustment = np.mean(confidence_adjustments) if confidence_adjustments else 0.0

        return max(0.0, min(1.0, base_confidence + avg_adjustment))

    def _calculate_emotional_tone_vector(self, recent_intents: list[IntentNodeHistory]) -> list[float]:  # noqa: F821
        """Calculate emotional tone vector from recent interactions"""
        if not recent_intents:
            return [0.5, 0.5, 0.5, 0.5]  # Neutral default

        # Average emotional contexts
        emotional_contexts = [intent.emotional_context for intent in recent_intents if intent.emotional_context]

        if not emotional_contexts:
            return [0.5, 0.5, 0.5, 0.5]

        # Calculate average for each dimension
        avg_context = np.mean(emotional_contexts, axis=0)
        return avg_context.tolist() if len(avg_context) >= 4 else [0.5, 0.5, 0.5, 0.5]

    def _generate_quantum_signature(self, data: dict[str, Any]) -> str:
        """Generate quantum signature for audit trail"""
        serialized = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode()).hexdigest()[:12]

    def _generate_loop_id(self, context: SymbolicContext) -> str:
        """Generate unique loop ID"""
        timestamp = datetime.now(timezone.utc).isoformat()
        raw_data = f"LOOP-{context.value}-{timestamp}-{len(self.feedback_loops)}"
        return hashlib.sha256(raw_data.encode()).hexdigest()[:8]

    def _analyze_performance_patterns(
        self, context: SymbolicContext, success_metrics: dict[str, float]
    ) -> dict[str, Any]:
        """Analyze performance patterns for given context"""
        # Placeholder implementation - would analyze historical patterns
        return {
            "trend": ("improving" if np.mean(list(success_metrics.values())) > 0.7 else "stable"),
            "stability": 0.8,
            "pattern_strength": 0.6,
        }

    def _generate_optimization_suggestions(
        self,
        context: SymbolicContext,
        success_metrics: dict[str, float],
        failure_patterns: list[str],
        performance_analysis: dict[str, Any],
    ) -> list[str]:
        """Generate optimization suggestions based on analysis"""
        suggestions = []

        avg_success = np.mean(list(success_metrics.values()))

        if avg_success < 0.6:
            suggestions.append(f"Improve {context.value} success rate through pattern rehearsal")

        if failure_patterns:
            suggestions.append(f"Address common failure patterns in {context.value}")

        if performance_analysis["stability"] < 0.5:
            suggestions.append(f"Stabilize {context.value} performance through controlled learning rates")

        return suggestions

    def _identify_rehearsal_opportunities(
        self, context: SymbolicContext, performance_analysis: dict[str, Any]
    ) -> list[str]:
        """Identify opportunities for symbolic rehearsal"""
        opportunities = []

        if performance_analysis["pattern_strength"] > 0.7:
            opportunities.append(f"Rehearse successful {context.value} patterns")

        if context == SymbolicContext.DREAM_REPLAY:
            opportunities.append("Schedule additional dream rehearsal sessions")

        return opportunities

    def _calculate_confidence_adjustment(
        self,
        success_metrics: dict[str, float],
        performance_analysis: dict[str, Any],
    ) -> float:
        """Calculate confidence adjustment based on performance"""
        avg_success = np.mean(list(success_metrics.values()))
        trend_factor = 0.1 if performance_analysis["trend"] == "improving" else 0.0

        return (avg_success - 0.7) * 0.2 + trend_factor

    def _determine_feedback_type(self, success_metrics: dict[str, float], failure_patterns: list[str]) -> FeedbackType:
        """Determine feedback type based on metrics and patterns"""
        avg_success = np.mean(list(success_metrics.values()))

        if avg_success > 0.8:
            return FeedbackType.SUCCESS
        elif avg_success > 0.6:
            return FeedbackType.PARTIAL
        elif failure_patterns:
            return FeedbackType.FAILURE
        else:
            return FeedbackType.UNKNOWN

    def _apply_symbolic_optimizations(self, feedback_loop: SymbolicFeedbackLoop) -> None:  # noqa: F821
        """Apply optimizations based on feedback loop"""
        # Integration with rate modulator if available
        if self.rate_modulator and feedback_loop.confidence_adjustment != 0:
            # Adjust learning rate based on symbolic feedback
            strategy_name = f"{feedback_loop.context.value}_strategy"
            current_rate = self.rate_modulator.current_learning_rates.get(strategy_name, 0.001)

            if feedback_loop.feedback_type == FeedbackType.SUCCESS:
                # Slight increase for successful patterns
                adjustment = min(0.1, feedback_loop.confidence_adjustment)
                new_rate = current_rate * (1.0 + adjustment)
            elif feedback_loop.feedback_type == FeedbackType.FAILURE:
                # Decrease for failed patterns
                adjustment = max(-0.2, feedback_loop.confidence_adjustment)
                new_rate = current_rate * (1.0 + adjustment)
            else:
                return

            self.rate_modulator.current_learning_rates[strategy_name] = np.clip(
                new_rate,
                self.rate_modulator.min_rate,
                self.rate_modulator.max_rate,
            )

            logger.debug(f"Applied symbolic optimization to {strategy_name}: {current_rate:.6f} → {new_rate:.6f}")

    def _update_pattern_confidence(
        self,
        context: SymbolicContext,
        feedback_type: FeedbackType,
        success_metrics: dict[str, float],
    ) -> None:
        """Update pattern confidence based on feedback"""
        pattern_key = f"{context.value}_{feedback_type.value}"
        avg_success = np.mean(list(success_metrics.values()))

        # Update confidence with exponential moving average
        alpha = 0.1  # Learning rate for confidence updates
        current_confidence = self.pattern_confidence[pattern_key]
        self.pattern_confidence[pattern_key] = current_confidence * (1 - alpha) + avg_success * alpha

    def _find_relevant_success_patterns(self, scenario_pattern: str) -> list[dict[str, Any]]:
        """Find relevant successful patterns for rehearsal"""
        relevant = []

        for pattern_key, pattern_list in self.success_patterns.items():
            if scenario_pattern in pattern_key:
                relevant.extend(pattern_list)

        return relevant[-10:]  # Return most recent 10 patterns

    def _simulate_rehearsal_iteration(
        self,
        scenario_pattern: str,
        relevant_patterns: list[dict[str, Any]],
        iteration: int,
    ) -> dict[str, Any]:
        """Simulate a rehearsal iteration"""
        # Simplified simulation - in real implementation would use actual symbolic
        # reasoning
        base_performance = 0.5 + iteration * 0.1
        pattern_boost = len(relevant_patterns) * 0.02

        performance_delta = base_performance + pattern_boost + np.random.normal(0, 0.05)

        return {
            "performance_delta": max(0.0, performance_delta),
            "insights": [f"Rehearsal insight {iteration + 1} for {scenario_pattern}"],
            "confidence_gain": performance_delta * 0.5,
        }

    def _extract_common_suggestions(self, context_loops: list[SymbolicFeedbackLoop]) -> list[str]:  # noqa: F821
        """Extract common optimization suggestions from feedback loops"""
        all_suggestions = []
        for loop in context_loops:
            all_suggestions.extend(loop.optimization_suggestions)

        # Count frequency and return most common
        suggestion_counts = defaultdict(int)
        for suggestion in all_suggestions:
            suggestion_counts[suggestion] += 1

        return [suggestion for suggestion, count in suggestion_counts.items() if count > 1]

    def _generate_system_optimization_recommendations(
        self,
    ) -> list[dict[str, str]]:
        """Generate system-wide optimization recommendations"""
        recommendations = []

        # Analyze overall patterns
        total_loops = len(self.feedback_loops)
        if total_loops == 0:
            return [
                {
                    "priority": "low",
                    "message": "No feedback loops available for analysis",
                }
            ]

        success_rate = (
            len([loop for loop in self.feedback_loops if loop.feedback_type == FeedbackType.SUCCESS]) / total_loops
        )

        if success_rate < 0.6:
            recommendations.append(
                {
                    "priority": "high",
                    "message": f"Overall success rate low ({success_rate:.2f}). Increase rehearsal frequency.",
                    "action": "increase_rehearsal_frequency",
                }
            )

        if len(self.rehearsal_queue) > 50:
            recommendations.append(
                {
                    "priority": "medium",
                    "message": "Large rehearsal queue detected. Consider parallel rehearsal execution.",
                    "action": "parallel_rehearsal",
                }
            )

        # Check pattern confidence trends
        low_confidence_patterns = [k for k, v in self.pattern_confidence.items() if v < 0.4]
        if low_confidence_patterns:
            recommendations.append(
                {
                    "priority": "medium",
                    "message": f"Low confidence patterns detected: {', '.join(low_confidence_patterns[:3])}",
                    "action": "pattern_reinforcement",
                }
            )

        return recommendations


# ==============================================================================
# Integration Functions for LUKHAS Ecosystem
# ==============================================================================


def create_integrated_symbolic_feedback_system(
    dashboard: MetaLearningMonitorDashboard,
    rate_modulator: DynamicLearningRateModulator,
) -> SymbolicFeedbackSystem:  # noqa: F821
    """
    Factory function to create integrated symbolic feedback system
    """
    return SymbolicFeedbackSystem(dashboard=dashboard, rate_modulator=rate_modulator)  # noqa: F821


def simulate_intent_node_integration(
    feedback_system: SymbolicFeedbackSystem,  # noqa: F821
    intent_scenarios: list[dict[str, Any]],
) -> list[str]:
    """
    Simulate integration with intent_node system
    """
    signatures = []

    for scenario in intent_scenarios:
        signature = feedback_system.log_intent_node_interaction(
            intent_id=scenario.get("intent_id", "test_intent"),
            intent_type=scenario.get("intent_type", "reasoning"),
            resolution_success=scenario.get("success", True),
            confidence_score=scenario.get("confidence", 0.8),
            reasoning_steps=scenario.get("reasoning_steps", ["step1", "step2"]),
            memory_references=scenario.get("memory_refs", []),
            emotional_context=scenario.get("emotional_context", [0.7, 0.6, 0.8, 0.5]),
        )
        signatures.append(signature)

    return signatures


# ==============================================================================
# Example Usage and Testing
# ==============================================================================


if __name__ == "__main__":
    from ..meta_learning.monitor_dashboard import MetaLearningMonitorDashboard
    from ..meta_learning.rate_modulator import AdaptationStrategy, DynamicLearningRateModulator

    # Initialize integrated system
    dashboard = MetaLearningMonitorDashboard()
    rate_modulator = DynamicLearningRateModulator(dashboard, strategy=AdaptationStrategy.SYMBOLIC_GUIDED)
    feedback_system = SymbolicFeedbackSystem(dashboard, rate_modulator)  # noqa: F821

    # Simulate symbolic feedback cycles
    for cycle in range(5):
        # Simulate intent node interactions
        feedback_system.log_intent_node_interaction(
            intent_id=f"intent_{cycle}",
            intent_type="reasoning_task",
            resolution_success=(cycle % 3 != 0),  # Vary success
            confidence_score=0.7 + cycle * 0.05,
            reasoning_steps=[f"step_{i}" for i in range(3)],
            emotional_context=[
                0.6 + cycle * 0.05,
                0.7,
                0.5 + cycle * 0.02,
                0.8,
            ],
        )

        # Simulate memoria snapshots
        feedback_system.log_memoria_snapshot(
            snapshot_id=f"memoria_{cycle}",
            coherence_score=0.75 + cycle * 0.03,
            memory_fragments=[{"fragment": f"mem_{i}"} for i in range(5)],
            retrieval_success_rate=0.8 + cycle * 0.02,
            consolidation_quality=0.85 + cycle * 0.01,
            symbolic_links=[f"link_{i}" for i in range(3)],
        )

        # Simulate dream replays
        feedback_system.log_dream_replay(
            replay_id=f"dream_{cycle}",
            scenario_type="problem_solving",
            replay_success=(cycle % 2 == 0),
            performance_delta=0.05 + cycle * 0.02,
            symbolic_insights=[f"insight_{cycle}"],
            emotional_resonance=0.6 + cycle * 0.05,
        )

        # Create feedback loop
        feedback_system.create_symbolic_feedback_loop(
            context=SymbolicContext.SYMBOLIC_REASONING,
            success_metrics={
                "accuracy": 0.8 + cycle * 0.02,
                "coherence": 0.75 + cycle * 0.03,
            },
            failure_patterns=["pattern_1"] if cycle % 4 == 0 else [],
            optimization_target="reasoning_confidence",
        )

    # Execute rehearsal
    rehearsal_results = feedback_system.execute_symbolic_rehearsal("problem_solving", 3)
    print(f"Rehearsal results: {rehearsal_results['success_rate']:.3f} success rate")

    # Get optimization insights
    insights = feedback_system.get_optimization_insights()
    print(f"Generated {len(insights['optimization_recommendations'])} optimization recommendations")

    print("Symbolic Feedback System demonstration completed!")
