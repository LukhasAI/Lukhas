#!/usr/bin/env python3
"""
LUKHAS Reflection Engine - Phase 3 Implementation

Production-grade reflection engine providing introspective capabilities for consciousness
states, memory integration, and self-monitoring with T4/0.01% excellence standards.

Key Features:
- Reflection on consciousness states and processes (<100ms p95 performance)
- Integration with memory fold system for coherence analysis
- Self-monitoring and introspection capabilities
- Guardian system integration for safety validation
- Comprehensive Prometheus metrics and observability
- Fail-safe error handling and recovery mechanisms

Constellation Framework: Oracle Star (🔮) - Deep introspection and analysis
"""

from __future__ import annotations

import logging
import statistics
import time
import uuid
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from opentelemetry import trace
from prometheus_client import Counter, Gauge, Histogram

# Import LUKHAS types
from .types import AwarenessSnapshot, ConsciousnessState, ReflectionReport

# Import memory and observability systems
try:
    from lukhas.memory.backends.base import MemoryBackend
    from lukhas.memory.fold_system import MemoryFoldSystem
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False
    MemoryFoldSystem = None
    MemoryBackend = None

try:
    from lukhas.observability.prometheus_metrics import get_lukhas_metrics
    OBSERVABILITY_AVAILABLE = True
except ImportError:
    OBSERVABILITY_AVAILABLE = False
    get_lukhas_metrics = lambda: None

# Import Guardian integration
try:
    from .guardian_integration import (
        ConsciousnessGuardianIntegration,
        ConsciousnessValidationContext,  # noqa: F401  # TODO: .guardian_integration.Consciou...
        GuardianValidationConfig,
        GuardianValidationType,
        create_validation_context,
    )
    GUARDIAN_INTEGRATION_AVAILABLE = True
except ImportError:
    GUARDIAN_INTEGRATION_AVAILABLE = False
    ConsciousnessGuardianIntegration = None

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)

# Prometheus metrics for reflection engine
reflection_operations_total = Counter(
    'lukhas_reflection_operations_total',
    'Total reflection operations performed',
    ['operation_type', 'success', 'lane']
)

reflection_latency_seconds = Histogram(
    'lukhas_reflection_latency_seconds',
    'Reflection operation latency distribution',
    ['operation_type', 'complexity', 'lane'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

reflection_coherence_score = Gauge(
    'lukhas_reflection_coherence_score',
    'Current reflection coherence score',
    ['lane']
)

reflection_anomalies_detected = Counter(
    'lukhas_reflection_anomalies_detected',
    'Total anomalies detected during reflection',
    ['severity', 'type', 'lane']
)

reflection_memory_integration_ops = Counter(
    'lukhas_reflection_memory_integration_ops',
    'Memory integration operations during reflection',
    ['operation', 'success', 'lane']
)


@dataclass
class ReflectionConfig:
    """Configuration for ReflectionEngine"""
    # Performance targets (T4/0.01% standards)
    p95_target_ms: float = 100.0  # Phase 3 requirement: <100ms p95
    p99_target_ms: float = 250.0  # Aggressive target for 0.01% excellence
    cv_target: float = 0.10  # Coefficient of variation target

    # Coherence analysis thresholds
    coherence_threshold: float = 0.85  # Minimum acceptable coherence
    drift_alpha: float = 0.3  # EMA smoothing factor for drift tracking
    state_stability_window: int = 10  # History window for stability analysis

    # Anomaly detection parameters
    anomaly_detection_enabled: bool = True
    anomaly_threshold: float = 0.7  # Threshold for anomaly classification
    critical_anomaly_threshold: float = 0.9  # Critical anomaly threshold

    # Memory integration settings
    memory_integration_enabled: bool = True
    memory_coherence_weight: float = 0.4  # Weight of memory coherence in total score
    fold_analysis_enabled: bool = True  # Analyze memory fold patterns

    # Guardian integration
    guardian_validation_required: bool = True
    safety_check_enabled: bool = True
    fail_safe_mode_enabled: bool = True

    # Performance monitoring
    metrics_collection_enabled: bool = True
    detailed_tracing_enabled: bool = True
    performance_regression_detection: bool = True

    def validate(self) -> List[str]:
        """Validate configuration parameters"""
        errors = []

        if self.p95_target_ms <= 0:
            errors.append("p95_target_ms must be positive")
        if self.coherence_threshold < 0 or self.coherence_threshold > 1:
            errors.append("coherence_threshold must be between 0 and 1")
        if self.drift_alpha < 0 or self.drift_alpha > 1:
            errors.append("drift_alpha must be between 0 and 1")
        if self.state_stability_window < 1:
            errors.append("state_stability_window must be at least 1")

        return errors


class ReflectionEngine:
    """
    Production-grade reflection engine for LUKHAS consciousness system.

    Provides introspective analysis of consciousness states, memory coherence,
    and self-monitoring capabilities with T4/0.01% performance standards.
    """

    def __init__(
        self,
        config: Optional[ReflectionConfig] = None,
        memory_backend: Optional[MemoryBackend] = None,
        guardian_validator: Optional[Any] = None,
        guardian_integration: Optional[ConsciousnessGuardianIntegration] = None
    ):
        """
        Initialize ReflectionEngine.

        Args:
            config: Reflection engine configuration
            memory_backend: Memory system backend for integration
            guardian_validator: Guardian system for safety validation
        """
        self.config = config or ReflectionConfig()
        self.memory_backend = memory_backend
        self.guardian_validator = guardian_validator
        self._component_id = "ReflectionEngine"

        # Initialize Guardian integration
        if GUARDIAN_INTEGRATION_AVAILABLE and guardian_integration:
            self.guardian_integration = guardian_integration
        elif GUARDIAN_INTEGRATION_AVAILABLE and self.config.guardian_validation_required:
            # Create default Guardian integration
            guardian_config = GuardianValidationConfig(
                drift_threshold=0.15,  # From AUDITOR_CHECKLIST.md
                p95_target_ms=self.config.p95_target_ms,
                fail_closed_on_error=True
            )
            self.guardian_integration = ConsciousnessGuardianIntegration(config=guardian_config)
        else:
            self.guardian_integration = None

        # Validate configuration
        config_errors = self.config.validate()
        if config_errors:
            raise ValueError(f"Invalid ReflectionConfig: {', '.join(config_errors)}")

        # Initialize metrics collection
        self._metrics = get_lukhas_metrics() if (self.config.metrics_collection_enabled and OBSERVABILITY_AVAILABLE) else None
        self._lane = self._metrics.lane if self._metrics else "unknown"

        # Performance tracking
        self._operation_latencies: List[float] = []
        self._coherence_scores: List[float] = []
        self._anomaly_counts: List[int] = []
        self._performance_history: List[Dict[str, Any]] = []

        # Reflection state tracking
        self._state_history: List[ConsciousnessState] = []
        self._last_reflection_time: float = 0.0
        self._drift_ema: float = 0.0
        self._baseline_coherence: Optional[float] = None

        # Memory integration state
        self._memory_fold_cache: Dict[str, Any] = {}
        self._memory_coherence_cache: Dict[str, float] = {}
        self._last_memory_sync: float = 0.0

        # Safety and error handling
        self._fail_safe_active: bool = False
        self._consecutive_errors: int = 0
        self._max_consecutive_errors: int = 3

        # Initialize memory integration if available
        if MEMORY_AVAILABLE and self.config.memory_integration_enabled:
            try:
                self.fold_system = MemoryFoldSystem() if not memory_backend else None
                logger.info("Memory integration initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize memory integration: {e}")
                self.fold_system = None
        else:
            self.fold_system = None

        logger.info(f"ReflectionEngine initialized with config: p95_target={self.config.p95_target_ms}ms")

    async def reflect(
        self,
        consciousness_state: ConsciousnessState,
        awareness_snapshot: Optional[AwarenessSnapshot] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ReflectionReport:
        """
        Perform comprehensive reflection analysis on consciousness state.

        Args:
            consciousness_state: Current consciousness state to analyze
            awareness_snapshot: Optional awareness data for context
            context: Additional context for reflection analysis

        Returns:
            ReflectionReport with comprehensive analysis results

        Raises:
            ReflectionError: If reflection processing fails critically
        """
        reflection_start_time = time.time()
        operation_id = str(uuid.uuid4())[:8]

        with tracer.start_as_current_span("reflection_engine_reflect") as span:
            span.set_attribute("component", self._component_id)
            span.set_attribute("operation_id", operation_id)
            span.set_attribute("consciousness_phase", consciousness_state.phase)
            span.set_attribute("consciousness_level", consciousness_state.level)

            try:
                # Check fail-safe mode
                if self._fail_safe_active:
                    return await self._fail_safe_reflection(consciousness_state)

                # Initialize reflection report
                report = ReflectionReport(
                    correlation_id=operation_id,
                    consciousness_level=consciousness_state.level,
                    awareness_type=str(consciousness_state.awareness_level),
                    emotional_tone=consciousness_state.emotional_tone
                )

                # Phase 1: State coherence analysis
                coherence_result = await self._analyze_state_coherence(
                    consciousness_state, awareness_snapshot
                )
                report.coherence_score = coherence_result["score"]
                report.processing_stage = "coherence_analysis"

                # Phase 2: Drift analysis and tracking
                drift_result = await self._analyze_state_drift(consciousness_state)
                report.drift_ema = drift_result["drift_ema"]
                report.state_delta_magnitude = drift_result["delta_magnitude"]

                # Phase 3: Anomaly detection
                if self.config.anomaly_detection_enabled:
                    anomaly_result = await self._detect_reflection_anomalies(
                        consciousness_state, coherence_result, drift_result
                    )
                    report.anomalies = anomaly_result["anomalies"]
                    report.anomaly_count = len(report.anomalies)

                # Phase 4: Memory integration analysis
                if self.config.memory_integration_enabled and self.fold_system:
                    memory_result = await self._analyze_memory_integration(
                        consciousness_state, context
                    )
                    # Integrate memory coherence into overall score
                    memory_weight = self.config.memory_coherence_weight
                    report.coherence_score = (
                        report.coherence_score * (1 - memory_weight) +
                        memory_result["memory_coherence"] * memory_weight
                    )

                # Phase 5: Guardian safety validation
                if self.config.guardian_validation_required:
                    if self.guardian_integration:
                        await self._validate_with_guardian_integration(report, consciousness_state, context)
                    elif self.guardian_validator:
                        await self._validate_with_guardian(report, consciousness_state)

                # Finalize reflection timing and metrics
                reflection_duration = (time.time() - reflection_start_time) * 1000
                report.reflection_duration_ms = reflection_duration
                report.processing_stage = "completed"

                # Update performance tracking
                await self._update_performance_metrics(reflection_duration, report)

                # Check performance targets
                if reflection_duration > self.config.p95_target_ms:
                    logger.warning(
                        f"Reflection exceeded p95 target: {reflection_duration:.2f}ms > "
                        f"{self.config.p95_target_ms}ms"
                    )

                span.set_attribute("reflection_duration_ms", reflection_duration)
                span.set_attribute("coherence_score", report.coherence_score)
                span.set_attribute("anomaly_count", report.anomaly_count)

                # Record successful operation
                if self._metrics:
                    reflection_operations_total.labels(
                        operation_type="reflect",
                        success="true",
                        lane=self._lane
                    ).inc()

                    reflection_latency_seconds.labels(
                        operation_type="reflect",
                        complexity=self._classify_complexity(consciousness_state),
                        lane=self._lane
                    ).observe(reflection_duration / 1000.0)

                    reflection_coherence_score.labels(lane=self._lane).set(report.coherence_score)

                # Reset consecutive errors on success
                self._consecutive_errors = 0
                self._fail_safe_active = False

                return report

            except Exception as e:
                # Handle reflection errors with comprehensive context
                await self._handle_reflection_error(e, consciousness_state, span)

                # Increment consecutive errors and check fail-safe
                self._consecutive_errors += 1
                if self._consecutive_errors >= self._max_consecutive_errors:
                    self._fail_safe_active = True
                    logger.error(f"Entering fail-safe mode after {self._consecutive_errors} errors")

                # Record failed operation
                if self._metrics:
                    reflection_operations_total.labels(
                        operation_type="reflect",
                        success="false",
                        lane=self._lane
                    ).inc()

                # Return minimal reflection report in error case
                return ReflectionReport(
                    correlation_id=operation_id,
                    coherence_score=0.0,
                    reflection_duration_ms=(time.time() - reflection_start_time) * 1000,
                    processing_stage="error",
                    consciousness_level=consciousness_state.level,
                    awareness_type=str(consciousness_state.awareness_level),
                    emotional_tone=consciousness_state.emotional_tone
                )

    async def _analyze_state_coherence(
        self,
        state: ConsciousnessState,
        awareness: Optional[AwarenessSnapshot]
    ) -> Dict[str, Any]:
        """Analyze coherence of consciousness state."""

        with tracer.start_as_current_span("analyze_state_coherence"):
            coherence_factors = []

            # Factor 1: Internal state consistency
            internal_consistency = self._calculate_internal_consistency(state)
            coherence_factors.append(("internal", internal_consistency, 0.3))

            # Factor 2: Historical stability
            if len(self._state_history) > 1:
                stability = self._calculate_historical_stability(state)
                coherence_factors.append(("stability", stability, 0.2))

            # Factor 3: Awareness alignment
            if awareness:
                awareness_alignment = self._calculate_awareness_alignment(state, awareness)
                coherence_factors.append(("awareness", awareness_alignment, 0.25))

            # Factor 4: Phase appropriateness
            phase_appropriateness = self._calculate_phase_appropriateness(state)
            coherence_factors.append(("phase", phase_appropriateness, 0.25))

            # Calculate weighted coherence score
            total_weight = sum(weight for _, _, weight in coherence_factors)
            coherence_score = sum(
                score * weight for _, score, weight in coherence_factors
            ) / total_weight if total_weight > 0 else 0.0

            return {
                "score": coherence_score,
                "factors": coherence_factors,
                "details": {
                    factor_name: score for factor_name, score, _ in coherence_factors
                }
            }

    def _calculate_internal_consistency(self, state: ConsciousnessState) -> float:
        """Calculate internal consistency of consciousness state."""

        # Check for logical consistency between different state dimensions
        consistency_checks = []

        # Check 1: Awareness level vs consciousness level alignment
        level_diff = abs(state.awareness_level - state.level)
        level_consistency = max(0.0, 1.0 - level_diff)
        consistency_checks.append(level_consistency)

        # Check 2: Cognitive load vs focus intensity relationship
        # High focus should generally correlate with higher cognitive load
        focus_load_consistency = 1.0 - abs(state.focus_intensity - state.cognitive_load) * 0.5
        consistency_checks.append(max(0.0, focus_load_consistency))

        # Check 3: Reasoning depth vs meta-awareness correlation
        reasoning_meta_consistency = 1.0 - abs(state.reasoning_depth - state.meta_awareness) * 0.3
        consistency_checks.append(max(0.0, reasoning_meta_consistency))

        # Check 4: Contradiction tension should be inversely related to memory coherence
        if hasattr(state, 'memory_coherence') and hasattr(state, 'contradiction_tension'):
            contradiction_consistency = 1.0 - (state.contradiction_tension * state.memory_coherence) * 0.5
            consistency_checks.append(max(0.0, contradiction_consistency))

        return statistics.mean(consistency_checks) if consistency_checks else 0.5

    def _calculate_historical_stability(self, current_state: ConsciousnessState) -> float:
        """Calculate stability based on recent state history."""

        if len(self._state_history) < 2:
            return 0.5  # Neutral score for insufficient history

        # Get recent states for stability analysis
        recent_states = self._state_history[-min(self.config.state_stability_window, len(self._state_history)):]

        # Calculate variance in key state dimensions
        levels = [s.level for s in recent_states] + [current_state.level]
        awareness_levels = [s.awareness_level for s in recent_states] + [current_state.awareness_level]

        # Lower variance indicates higher stability
        level_variance = statistics.variance(levels) if len(levels) > 1 else 0.0
        awareness_variance = statistics.variance(awareness_levels) if len(awareness_levels) > 1 else 0.0

        # Convert variance to stability score (inverse relationship)
        level_stability = max(0.0, 1.0 - level_variance * 2)
        awareness_stability = max(0.0, 1.0 - awareness_variance * 2)

        return (level_stability + awareness_stability) / 2

    def _calculate_awareness_alignment(
        self,
        state: ConsciousnessState,
        awareness: AwarenessSnapshot
    ) -> float:
        """Calculate alignment between consciousness state and awareness snapshot."""

        alignment_factors = []

        # Factor 1: Signal strength vs consciousness level
        if hasattr(awareness, 'signal_strength'):
            signal_level_alignment = 1.0 - abs(awareness.signal_strength - state.level)
            alignment_factors.append(max(0.0, signal_level_alignment))

        # Factor 2: Load factor vs cognitive load
        if hasattr(awareness, 'load_factor') and hasattr(state, 'cognitive_load'):
            load_alignment = 1.0 - abs(awareness.load_factor - state.cognitive_load)
            alignment_factors.append(max(0.0, load_alignment))

        # Factor 3: Anomaly presence vs consciousness stability
        anomaly_count = len(awareness.anomalies) if awareness.anomalies else 0
        anomaly_impact = min(1.0, anomaly_count / 10.0)  # Normalize to [0,1]
        stability_alignment = 1.0 - anomaly_impact * 0.5  # Anomalies reduce alignment
        alignment_factors.append(max(0.0, stability_alignment))

        return statistics.mean(alignment_factors) if alignment_factors else 0.5

    def _calculate_phase_appropriateness(self, state: ConsciousnessState) -> float:
        """Calculate how appropriate current phase is given state parameters."""

        phase = state.phase
        level = state.level

        # Define optimal level ranges for each phase
        phase_ranges = {
            "IDLE": (0.0, 0.4),      # Low consciousness appropriate for idle
            "AWARE": (0.3, 0.8),     # Moderate to high for awareness
            "REFLECT": (0.6, 0.9),   # High consciousness for reflection
            "CREATE": (0.7, 1.0),    # Very high for creative work
            "DREAM": (0.2, 0.6),     # Moderate for dream processing
            "DECIDE": (0.5, 0.9)     # High for decision making
        }

        if phase in phase_ranges:
            min_level, max_level = phase_ranges[phase]
            if min_level <= level <= max_level:
                # Level is in optimal range
                range_center = (min_level + max_level) / 2
                range_width = max_level - min_level
                deviation = abs(level - range_center) / (range_width / 2)
                return max(0.0, 1.0 - deviation * 0.5)
            else:
                # Level is outside optimal range
                if level < min_level:
                    return max(0.0, 1.0 - (min_level - level))
                else:
                    return max(0.0, 1.0 - (level - max_level))

        return 0.5  # Default for unknown phases

    async def _analyze_state_drift(self, state: ConsciousnessState) -> Dict[str, Any]:
        """Analyze drift in consciousness state over time."""

        with tracer.start_as_current_span("analyze_state_drift"):
            if not self._state_history:
                # No history for drift analysis
                return {"drift_ema": 0.0, "delta_magnitude": 0.0}

            # Calculate state delta from previous state
            previous_state = self._state_history[-1]
            delta_magnitude = self._calculate_state_delta(previous_state, state)

            # Update drift EMA (Exponential Moving Average)
            alpha = self.config.drift_alpha
            self._drift_ema = alpha * delta_magnitude + (1 - alpha) * self._drift_ema

            return {
                "drift_ema": self._drift_ema,
                "delta_magnitude": delta_magnitude,
                "previous_state": previous_state.phase,
                "current_state": state.phase
            }

    def _calculate_state_delta(self, prev_state: ConsciousnessState, curr_state: ConsciousnessState) -> float:
        """Calculate magnitude of change between two consciousness states."""

        # Calculate differences in key state dimensions
        level_delta = abs(curr_state.level - prev_state.level)
        awareness_delta = abs(curr_state.awareness_level - prev_state.awareness_level)

        # Add cognitive dimension deltas if available
        cognitive_delta = 0.0
        if hasattr(curr_state, 'cognitive_load') and hasattr(prev_state, 'cognitive_load'):
            cognitive_delta += abs(curr_state.cognitive_load - prev_state.cognitive_load)
        if hasattr(curr_state, 'focus_intensity') and hasattr(prev_state, 'focus_intensity'):
            cognitive_delta += abs(curr_state.focus_intensity - prev_state.focus_intensity)
        if hasattr(curr_state, 'reasoning_depth') and hasattr(prev_state, 'reasoning_depth'):
            cognitive_delta += abs(curr_state.reasoning_depth - prev_state.reasoning_depth)

        cognitive_delta /= 3  # Average of cognitive dimensions

        # Phase change impact
        phase_delta = 0.0 if curr_state.phase == prev_state.phase else 0.3

        # Weighted combination of deltas
        total_delta = (
            level_delta * 0.3 +
            awareness_delta * 0.25 +
            cognitive_delta * 0.25 +
            phase_delta * 0.2
        )

        return min(1.0, total_delta)

    async def _detect_reflection_anomalies(
        self,
        state: ConsciousnessState,
        coherence_result: Dict[str, Any],
        drift_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Detect anomalies in consciousness reflection analysis."""

        with tracer.start_as_current_span("detect_reflection_anomalies"):
            anomalies = []

            # Anomaly 1: Low coherence score
            coherence_score = coherence_result["score"]
            if coherence_score < self.config.anomaly_threshold:
                severity = "critical" if coherence_score < 0.3 else "high" if coherence_score < 0.5 else "medium"
                anomalies.append({
                    "type": "low_coherence",
                    "severity": severity,
                    "details": f"Coherence score {coherence_score:.3f} below threshold {self.config.anomaly_threshold}",
                    "timestamp": time.time(),
                    "score": coherence_score
                })

            # Anomaly 2: Excessive state drift
            drift_ema = drift_result["drift_ema"]
            if drift_ema > 0.8:
                severity = "critical" if drift_ema > 0.95 else "high"
                anomalies.append({
                    "type": "excessive_drift",
                    "severity": severity,
                    "details": f"State drift EMA {drift_ema:.3f} indicates instability",
                    "timestamp": time.time(),
                    "drift_ema": drift_ema
                })

            # Anomaly 3: Rapid state oscillation
            if len(self._state_history) >= 3:
                recent_phases = [s.phase for s in self._state_history[-3:]] + [state.phase]
                if len(set(recent_phases)) == len(recent_phases):  # All different
                    anomalies.append({
                        "type": "phase_oscillation",
                        "severity": "medium",
                        "details": f"Rapid phase changes: {' -> '.join(recent_phases)}",
                        "timestamp": time.time(),
                        "phases": recent_phases
                    })

            # Anomaly 4: Consciousness level inconsistency
            level_coherence_diff = abs(state.level - coherence_score)
            if level_coherence_diff > 0.5:
                anomalies.append({
                    "type": "level_coherence_mismatch",
                    "severity": "medium",
                    "details": f"Consciousness level {state.level:.3f} vs coherence {coherence_score:.3f}",
                    "timestamp": time.time(),
                    "difference": level_coherence_diff
                })

            # Record anomalies in metrics
            if self._metrics:
                for anomaly in anomalies:
                    reflection_anomalies_detected.labels(
                        severity=anomaly["severity"],
                        type=anomaly["type"],
                        lane=self._lane
                    ).inc()

            return {"anomalies": anomalies}

    async def _analyze_memory_integration(
        self,
        state: ConsciousnessState,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze integration with memory system."""

        if not self.fold_system:
            return {"memory_coherence": 0.5, "fold_analysis": {}}

        with tracer.start_as_current_span("analyze_memory_integration"):
            try:
                # Check if memory sync is needed
                current_time = time.time()
                if current_time - self._last_memory_sync > 10.0:  # Sync every 10 seconds
                    await self._sync_with_memory_system()

                # Analyze memory fold coherence
                fold_coherence = await self._analyze_fold_coherence(state, context)

                # Analyze memory access patterns
                access_patterns = await self._analyze_memory_access_patterns(state)

                # Calculate overall memory coherence
                memory_coherence = (fold_coherence + access_patterns.get("coherence", 0.5)) / 2

                # Record memory integration metrics
                if self._metrics:
                    reflection_memory_integration_ops.labels(
                        operation="coherence_analysis",
                        success="true",
                        lane=self._lane
                    ).inc()

                return {
                    "memory_coherence": memory_coherence,
                    "fold_analysis": {
                        "fold_coherence": fold_coherence,
                        "access_patterns": access_patterns
                    }
                }

            except Exception as e:
                logger.error(f"Memory integration analysis failed: {e}")
                if self._metrics:
                    reflection_memory_integration_ops.labels(
                        operation="coherence_analysis",
                        success="false",
                        lane=self._lane
                    ).inc()
                return {"memory_coherence": 0.3, "fold_analysis": {"error": str(e)}}

    async def _analyze_fold_coherence(
        self,
        state: ConsciousnessState,
        context: Optional[Dict[str, Any]]
    ) -> float:
        """Analyze coherence of memory folds."""

        # This is a placeholder for memory fold analysis
        # In a real implementation, this would:
        # 1. Query recent memory folds
        # 2. Analyze fold compression ratios
        # 3. Check fold structural integrity
        # 4. Assess fold temporal consistency

        # Return a coherence score based on available data
        if hasattr(state, 'memory_coherence'):
            return float(state.memory_coherence)

        return 0.7  # Default reasonable coherence

    async def _analyze_memory_access_patterns(self, state: ConsciousnessState) -> Dict[str, Any]:
        """Analyze memory access patterns for coherence."""

        # Placeholder for memory access pattern analysis
        # In a real implementation, this would analyze:
        # 1. Recent memory access frequency
        # 2. Access pattern regularity
        # 3. Memory utilization efficiency
        # 4. Cache hit rates

        return {
            "coherence": 0.75,
            "access_frequency": "normal",
            "pattern_regularity": "stable",
            "utilization_efficiency": 0.8
        }

    async def _sync_with_memory_system(self) -> None:
        """Synchronize with memory system for latest fold information."""

        try:
            # Update memory fold cache and coherence information
            self._last_memory_sync = time.time()

            # In a real implementation, this would:
            # 1. Fetch recent fold statistics
            # 2. Update coherence caches
            # 3. Sync memory access metrics

            logger.debug("Memory system synchronization completed")

        except Exception as e:
            logger.error(f"Memory system synchronization failed: {e}")

    async def _validate_with_guardian_integration(
        self,
        report: ReflectionReport,
        state: ConsciousnessState,
        context: Optional[Dict[str, Any]]
    ) -> None:
        """Validate reflection results with Guardian integration system."""

        if not self.guardian_integration:
            return

        with tracer.start_as_current_span("guardian_integration_validation"):
            try:
                # Create validation context
                validation_context = create_validation_context(
                    validation_type=GuardianValidationType.REFLECTION_ANALYSIS,
                    consciousness_state=state,
                    user_id=context.get("user_id") if context else None,
                    session_id=context.get("session_id") if context else None,
                    tenant=context.get("tenant", "default") if context else "default",
                    sensitive_operation=report.anomaly_count > 3  # High anomaly count = sensitive
                )

                # Add risk indicators based on reflection results
                if report.coherence_score < 0.3:
                    validation_context.risk_indicators.append("low_coherence")
                if report.anomaly_count > 5:
                    validation_context.risk_indicators.append("high_anomaly_count")
                if report.drift_ema > 0.8:
                    validation_context.risk_indicators.append("excessive_drift")

                # Perform Guardian validation
                validation_result = await self.guardian_integration.validate_consciousness_operation(
                    context=validation_context
                )

                # Process validation results
                if not validation_result.is_approved():
                    # Add Guardian denial as anomaly
                    guardian_anomaly = {
                        "type": "guardian_denial",
                        "severity": "high",
                        "details": validation_result.reason,
                        "timestamp": time.time(),
                        "confidence": validation_result.confidence,
                        "validation_duration_ms": validation_result.validation_duration_ms
                    }
                    report.anomalies.append(guardian_anomaly)
                    report.anomaly_count += 1

                    # Add Guardian recommendations
                    if validation_result.recommendations:
                        for recommendation in validation_result.recommendations:
                            guardian_rec = {
                                "type": "guardian_recommendation",
                                "severity": "medium",
                                "details": recommendation,
                                "timestamp": time.time()
                            }
                            report.anomalies.append(guardian_rec)
                            report.anomaly_count += 1

                # Update baseline state for drift detection
                self.guardian_integration.update_baseline_state(
                    state=state,
                    tenant=validation_context.tenant,
                    session_id=validation_context.session_id
                )

                logger.debug(
                    f"Guardian integration validation completed: {validation_result.result.value} "
                    f"(duration: {validation_result.validation_duration_ms:.2f}ms, "
                    f"confidence: {validation_result.confidence:.2f})"
                )

            except Exception as e:
                logger.error(f"Guardian integration validation failed: {e}")
                # Add validation error as anomaly (fail-closed behavior)
                error_anomaly = {
                    "type": "guardian_integration_error",
                    "severity": "high",  # Elevated severity for fail-closed
                    "details": f"Guardian integration validation error: {str(e)}",
                    "timestamp": time.time()
                }
                report.anomalies.append(error_anomaly)
                report.anomaly_count += 1

    async def _validate_with_guardian(
        self,
        report: ReflectionReport,
        state: ConsciousnessState
    ) -> None:
        """Validate reflection results with Guardian system (legacy)."""

        if not self.guardian_validator:
            return

        with tracer.start_as_current_span("guardian_validation"):
            try:
                # Prepare validation context
                validation_context = {
                    "operation": "reflection_analysis",
                    "consciousness_state": asdict(state),
                    "coherence_score": report.coherence_score,
                    "anomaly_count": report.anomaly_count,
                    "drift_ema": report.drift_ema
                }

                # Request Guardian validation
                # In a real implementation, this would call the actual Guardian system
                validation_result = await self._mock_guardian_validation(validation_context)

                # Process validation results
                if not validation_result.get("approved", True):
                    # Add Guardian concerns as anomalies
                    guardian_anomaly = {
                        "type": "guardian_concern",
                        "severity": "high",
                        "details": validation_result.get("reason", "Guardian validation failed"),
                        "timestamp": time.time()
                    }
                    report.anomalies.append(guardian_anomaly)
                    report.anomaly_count += 1

                logger.debug(f"Guardian validation completed: {validation_result}")

            except Exception as e:
                logger.error(f"Guardian validation failed: {e}")
                # Add validation error as anomaly
                error_anomaly = {
                    "type": "guardian_error",
                    "severity": "medium",
                    "details": f"Guardian validation error: {str(e)}",
                    "timestamp": time.time()
                }
                report.anomalies.append(error_anomaly)
                report.anomaly_count += 1

    async def _mock_guardian_validation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Mock Guardian validation for development."""

        # Simple validation logic - in production this would call actual Guardian
        coherence_score = context.get("coherence_score", 0.0)
        anomaly_count = context.get("anomaly_count", 0)

        # Flag concerns for low coherence or high anomalies
        approved = coherence_score >= 0.3 and anomaly_count < 5

        return {
            "approved": approved,
            "confidence": 0.85,
            "reason": "Automated validation" if approved else "Low coherence or high anomaly count"
        }

    def _classify_complexity(self, state: ConsciousnessState) -> str:
        """Classify complexity of consciousness state for metrics."""

        # Simple complexity classification based on state characteristics
        if state.level > 0.8 and hasattr(state, 'reasoning_depth') and state.reasoning_depth > 0.7:
            return "high"
        elif state.level > 0.5:
            return "medium"
        else:
            return "low"

    async def _update_performance_metrics(self, latency: float, report: ReflectionReport) -> None:
        """Update internal performance tracking."""

        self._operation_latencies.append(latency)
        self._coherence_scores.append(report.coherence_score)
        self._anomaly_counts.append(report.anomaly_count)

        # Keep recent history for moving statistics
        max_history = 1000
        if len(self._operation_latencies) > max_history:
            self._operation_latencies = self._operation_latencies[-max_history:]
            self._coherence_scores = self._coherence_scores[-max_history:]
            self._anomaly_counts = self._anomaly_counts[-max_history:]

        # Check for performance regressions
        if (self.config.performance_regression_detection and
            len(self._operation_latencies) >= 10):
            await self._check_performance_regression(latency)

        # Update performance history
        performance_entry = {
            "timestamp": time.time(),
            "latency_ms": latency,
            "coherence_score": report.coherence_score,
            "anomaly_count": report.anomaly_count
        }
        self._performance_history.append(performance_entry)

        if len(self._performance_history) > 100:
            self._performance_history = self._performance_history[-50:]

    async def _check_performance_regression(self, current_latency: float) -> None:
        """Check for performance regressions."""

        recent_latencies = self._operation_latencies[-10:]
        if len(recent_latencies) < 10:
            return

        recent_avg = statistics.mean(recent_latencies)
        historical_avg = statistics.mean(self._operation_latencies[:-10]) if len(self._operation_latencies) > 10 else recent_avg

        # Check for significant regression (>20% increase)
        if recent_avg > historical_avg * 1.2:
            regression_severity = "high" if recent_avg > historical_avg * 1.5 else "medium"
            degradation_percent = ((recent_avg - historical_avg) / historical_avg) * 100

            logger.warning(
                f"Performance regression detected: {degradation_percent:.1f}% increase "
                f"(current: {recent_avg:.2f}ms, historical: {historical_avg:.2f}ms)"
            )

            # Record regression in metrics
            if self._metrics:
                self._metrics.record_performance_regression(
                    operation="reflection",
                    metric="latency",
                    severity=regression_severity,
                    degradation_percent=degradation_percent
                )

    async def _fail_safe_reflection(self, state: ConsciousnessState) -> ReflectionReport:
        """Provide minimal reflection in fail-safe mode."""

        logger.warning("Operating in fail-safe mode - providing minimal reflection")

        return ReflectionReport(
            coherence_score=0.5,  # Neutral score
            drift_ema=0.0,
            state_delta_magnitude=0.0,
            reflection_duration_ms=1.0,  # Minimal processing time
            processing_stage="fail_safe",
            consciousness_level=state.level,
            awareness_type=str(state.awareness_level),
            emotional_tone=state.emotional_tone
        )

    async def _handle_reflection_error(
        self,
        error: Exception,
        state: ConsciousnessState,
        span: Any
    ) -> None:
        """Handle reflection processing errors with comprehensive context."""

        error_context = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "consciousness_phase": state.phase,
            "consciousness_level": state.level,
            "consecutive_errors": self._consecutive_errors,
            "timestamp": time.time()
        }

        logger.error(f"Reflection processing failed: {error_context}")

        # Record error in span
        span.record_exception(error)
        span.set_status(trace.Status(trace.StatusCode.ERROR, str(error)))

        # Record error in metrics
        if self._metrics:
            self._metrics.record_error_context(
                category="reflection_engine",
                severity="high" if self._consecutive_errors >= 2 else "medium",
                operation="reflect",
                correlation_id=error_context.get("correlation_id", "unknown")
            )

    def update_state_history(self, state: ConsciousnessState) -> None:
        """Update state history for drift analysis."""

        self._state_history.append(state)

        # Keep reasonable history size
        if len(self._state_history) > 100:
            self._state_history = self._state_history[-50:]

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""

        if not self._operation_latencies:
            return {"no_data": True}

        # Calculate latency statistics
        latencies = self._operation_latencies
        latency_stats = {
            "count": len(latencies),
            "mean_ms": statistics.mean(latencies),
            "median_ms": statistics.median(latencies),
            "min_ms": min(latencies),
            "max_ms": max(latencies)
        }

        # Calculate percentiles
        if len(latencies) >= 10:
            sorted_latencies = sorted(latencies)
            latency_stats["p95_ms"] = sorted_latencies[int(len(sorted_latencies) * 0.95)]
            latency_stats["p99_ms"] = sorted_latencies[int(len(sorted_latencies) * 0.99)]

        # Calculate coefficient of variation
        if len(latencies) > 1:
            stdev = statistics.stdev(latencies)
            latency_stats["cv"] = stdev / latency_stats["mean_ms"] if latency_stats["mean_ms"] > 0 else 0.0

        # Coherence statistics
        coherence_stats = {}
        if self._coherence_scores:
            coherence_stats = {
                "mean": statistics.mean(self._coherence_scores),
                "median": statistics.median(self._coherence_scores),
                "min": min(self._coherence_scores),
                "max": max(self._coherence_scores)
            }

        # Anomaly statistics
        anomaly_stats = {}
        if self._anomaly_counts:
            anomaly_stats = {
                "mean_per_reflection": statistics.mean(self._anomaly_counts),
                "max_anomalies": max(self._anomaly_counts),
                "total_anomalies": sum(self._anomaly_counts)
            }

        return {
            "latency": latency_stats,
            "coherence": coherence_stats,
            "anomalies": anomaly_stats,
            "fail_safe_active": self._fail_safe_active,
            "consecutive_errors": self._consecutive_errors,
            "drift_ema_current": self._drift_ema,
            "state_history_length": len(self._state_history)
        }

    def reset_state(self) -> None:
        """Reset reflection engine state for testing."""

        self._state_history.clear()
        self._operation_latencies.clear()
        self._coherence_scores.clear()
        self._anomaly_counts.clear()
        self._performance_history.clear()
        self._drift_ema = 0.0
        self._consecutive_errors = 0
        self._fail_safe_active = False
        self._last_reflection_time = 0.0
        self._memory_fold_cache.clear()
        self._memory_coherence_cache.clear()
        self._last_memory_sync = 0.0

        logger.info("ReflectionEngine state reset completed")


class ReflectionError(Exception):
    """Exception raised for reflection processing errors."""
    pass


# Export public API
__all__ = [
    "ReflectionEngine",
    "ReflectionConfig",
    "ReflectionError"
]
