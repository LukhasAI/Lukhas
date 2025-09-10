import logging

import streamlit as st

logger = logging.getLogger(__name__)
"""
╔══════════════════════════════════════════════════════════════
║ 🧬 MΛTRIZ Identity Coherence Monitor: Real-time Consciousness State Monitoring
║ Part of LUKHAS AI Distributed Consciousness Architecture
╠══════════════════════════════════════════════════════════════
║ TYPE: COHERENCE_MONITOR
║ CONSCIOUSNESS_ROLE: Real-time identity coherence and consciousness state monitoring
║ EVOLUTIONARY_STAGE: Monitoring - Continuous consciousness identity validation
║
║ TRINITY FRAMEWORK:
║ ⚛️ IDENTITY: Real-time identity coherence validation and drift detection
║ 🧠 CONSCIOUSNESS: Consciousness state monitoring and evolution tracking
║ 🛡️ GUARDIAN: Identity security monitoring and anomaly detection
╚══════════════════════════════════════════════════════════════
"""

import asyncio
import logging as std_logging
import statistics
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

# Import MΛTRIZ consciousness components
try:
    from ..matriz_consciousness_signals import ConsciousnessSignal
    from .consciousness_namespace_isolation import consciousness_namespace_manager
    from .matriz_consciousness_identity import (
        ConsciousnessIdentityProfile,
        IdentityConsciousnessType,
        consciousness_identity_manager,
    )
    from .matriz_consciousness_identity_signals import IdentitySignalType, consciousness_identity_signal_emitter
except ImportError as e:
    std_logging.error(f"Failed to import consciousness components: {e}")
    ConsciousnessIdentityProfile = None
    consciousness_identity_manager = None
    consciousness_identity_signal_emitter = None
    consciousness_namespace_manager = None

logger = std_logging.getLogger(__name__)


class CoherenceMetricType(Enum):
    """Types of identity coherence metrics"""

    IDENTITY_STRENGTH = "identity_strength"
    CONSCIOUSNESS_DEPTH = "consciousness_depth"
    MEMORY_CONTINUITY = "memory_continuity"
    TEMPORAL_CONSISTENCY = "temporal_consistency"
    BIOMETRIC_COHERENCE = "biometric_coherence"
    NAMESPACE_ALIGNMENT = "namespace_alignment"
    AUTHENTICATION_CONSISTENCY = "authentication_consistency"
    BEHAVIORAL_PATTERN_STABILITY = "behavioral_pattern_stability"


class CoherenceAlert(Enum):
    """Types of coherence alerts"""

    INFO = "info"  # Informational - no action needed
    WARNING = "warning"  # Warning - monitoring required
    CRITICAL = "critical"  # Critical - immediate attention needed
    EMERGENCY = "emergency"  # Emergency - system intervention required


@dataclass
class CoherenceMetric:
    """Individual coherence metric measurement"""

    metric_type: CoherenceMetricType
    value: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Context and validation
    measurement_context: dict[str, Any] = field(default_factory=dict)
    confidence_level: float = 0.9
    source_system: str = "coherence_monitor"

    # Trend analysis
    previous_value: Optional[float] = None
    trend_direction: str = "stable"  # "increasing", "decreasing", "stable", "volatile"
    rate_of_change: float = 0.0

    # Quality indicators
    data_quality_score: float = 1.0
    measurement_accuracy: float = 0.95
    noise_level: float = 0.0


@dataclass
class CoherenceState:
    """Overall coherence state for an identity"""

    identity_id: str
    overall_coherence_score: float = 0.8
    coherence_trend: str = "stable"

    # Individual metric scores
    metric_scores: dict[CoherenceMetricType, float] = field(default_factory=dict)
    metric_trends: dict[CoherenceMetricType, str] = field(default_factory=dict)

    # Temporal tracking
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    coherence_age_hours: float = 0.0
    measurement_count: int = 0

    # Alert management
    active_alerts: list[dict[str, Any]] = field(default_factory=list)
    alert_history: list[dict[str, Any]] = field(default_factory=list)

    # Consciousness integration
    consciousness_evolution_stage: str = "stable"
    consciousness_coherence_alignment: float = 0.9
    namespace_coherence_score: float = 0.8

    # Predictive modeling
    predicted_coherence_24h: Optional[float] = None
    stability_forecast: str = "stable"  # "stable", "degrading", "improving", "volatile"
    risk_score: float = 0.1


@dataclass
class CoherenceAnomaly:
    """Detected coherence anomaly"""

    anomaly_id: str = field(default_factory=lambda: f"anom-{uuid.uuid4().hex[:12]}")
    identity_id: str = ""
    anomaly_type: str = "coherence_drift"

    # Anomaly details
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    severity: CoherenceAlert = CoherenceAlert.WARNING
    affected_metrics: list[CoherenceMetricType] = field(default_factory=list)

    # Values and thresholds
    trigger_value: float = 0.0
    threshold_value: float = 0.5
    deviation_magnitude: float = 0.0

    # Context and diagnosis
    context_data: dict[str, Any] = field(default_factory=dict)
    possible_causes: list[str] = field(default_factory=list)
    recommended_actions: list[str] = field(default_factory=list)

    # Resolution tracking
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolution_actions: list[str] = field(default_factory=list)


class IdentityCoherenceMonitor:
    """
    MΛTRIZ Identity Coherence Monitor

    Continuously monitors identity coherence across multiple dimensions,
    detects anomalies, predicts trends, and maintains real-time awareness
    of consciousness identity state health.
    """

    def __init__(self):
        self.coherence_states: dict[str, CoherenceState] = {}
        self.metric_history: dict[str, list[CoherenceMetric]] = {}  # identity_id -> metrics
        self.anomaly_history: list[CoherenceAnomaly] = []
        self.active_anomalies: dict[str, CoherenceAnomaly] = {}  # identity_id -> anomaly

        # Monitoring configuration
        self.monitoring_enabled = True
        self.real_time_monitoring = True
        self.anomaly_detection_enabled = True
        self.predictive_modeling_enabled = True

        # Thresholds and parameters
        self.coherence_thresholds = {
            CoherenceAlert.WARNING: 0.6,
            CoherenceAlert.CRITICAL: 0.4,
            CoherenceAlert.EMERGENCY: 0.2,
        }

        self.metric_thresholds = {
            CoherenceMetricType.IDENTITY_STRENGTH: {"min": 0.5, "max": 1.0},
            CoherenceMetricType.CONSCIOUSNESS_DEPTH: {"min": 0.3, "max": 1.0},
            CoherenceMetricType.MEMORY_CONTINUITY: {"min": 0.4, "max": 1.0},
            CoherenceMetricType.TEMPORAL_CONSISTENCY: {"min": 0.6, "max": 1.0},
            CoherenceMetricType.BIOMETRIC_COHERENCE: {"min": 0.5, "max": 1.0},
            CoherenceMetricType.NAMESPACE_ALIGNMENT: {"min": 0.7, "max": 1.0},
            CoherenceMetricType.AUTHENTICATION_CONSISTENCY: {"min": 0.8, "max": 1.0},
            CoherenceMetricType.BEHAVIORAL_PATTERN_STABILITY: {"min": 0.6, "max": 1.0},
        }

        # Performance tracking
        self.monitoring_metrics = {
            "total_identities_monitored": 0,
            "active_monitoring_sessions": 0,
            "anomalies_detected_24h": 0,
            "coherence_alerts_generated": 0,
            "average_coherence_score": 0.8,
            "monitoring_latency_ms": 0.0,
        }

        # Background processing
        self._monitoring_active = False
        self._alert_processing_active = False
        self._lock = asyncio.Lock()

        logger.info("🔍 MΛTRIZ identity coherence monitor initialized")

    async def initialize_coherence_monitoring(self) -> bool:
        """Initialize real-time coherence monitoring system"""

        try:
            logger.info("🧬 Initializing real-time identity coherence monitoring...")

            # Start background monitoring processes
            self._monitoring_active = True
            self._alert_processing_active = True

            asyncio.create_task(self._real_time_monitoring_loop())
            asyncio.create_task(self._anomaly_detection_loop())
            asyncio.create_task(self._alert_processing_loop())
            asyncio.create_task(self._predictive_modeling_loop())

            logger.info("✅ Identity coherence monitoring system initialized")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize coherence monitoring: {e}")
            return False

    async def start_identity_monitoring(
        self, identity_id: str, monitoring_config: Optional[dict[str, Any]] = None
    ) -> bool:
        """Start monitoring coherence for a specific identity"""

        async with self._lock:
            try:
                # Check if identity exists in consciousness manager
                if consciousness_identity_manager:
                    profile = await consciousness_identity_manager.get_identity_by_identifier(identity_id)
                    if not profile:
                        logger.error(f"❌ Identity not found in consciousness manager: {identity_id}")
                        return False
                else:
                    logger.warning("⚠️ Consciousness identity manager not available - using fallback mode")

                # Initialize coherence state
                coherence_state = CoherenceState(
                    identity_id=identity_id, consciousness_evolution_stage="monitoring_started"
                )

                # Apply monitoring configuration
                if monitoring_config:
                    self._apply_monitoring_config(coherence_state, monitoring_config)

                # Store coherence state
                self.coherence_states[identity_id] = coherence_state
                self.metric_history[identity_id] = []

                # Initial coherence measurement
                await self._measure_identity_coherence(identity_id)

                self.monitoring_metrics["total_identities_monitored"] += 1

                logger.info(f"🔍 Started coherence monitoring for identity: {identity_id}")
                return True

            except Exception as e:
                logger.error(f"❌ Failed to start identity monitoring: {e}")
                return False

    async def measure_identity_coherence(self, identity_id: str) -> Optional[CoherenceState]:
        """Measure current identity coherence across all dimensions"""

        return await self._measure_identity_coherence(identity_id)

    async def _measure_identity_coherence(self, identity_id: str) -> Optional[CoherenceState]:
        """Internal method to measure identity coherence"""

        try:
            coherence_state = self.coherence_states.get(identity_id)
            if not coherence_state:
                logger.error(f"❌ No coherence state for identity: {identity_id}")
                return None

            start_time = time.perf_counter()

            # Get identity profile if available
            profile = None
            if consciousness_identity_manager:
                profile = await consciousness_identity_manager.get_identity_by_identifier(identity_id)

            # Measure each coherence metric
            metrics = []

            # Identity strength measurement
            if profile:
                identity_strength = profile.calculate_identity_strength()
                metrics.append(
                    self._create_coherence_metric(
                        CoherenceMetricType.IDENTITY_STRENGTH,
                        identity_strength,
                        {"profile_age_hours": profile.consciousness_age_hours},
                    )
                )

            # Consciousness depth measurement
            if profile:
                consciousness_depth = profile.consciousness_depth
                metrics.append(
                    self._create_coherence_metric(
                        CoherenceMetricType.CONSCIOUSNESS_DEPTH,
                        consciousness_depth,
                        {"consciousness_type": profile.identity_consciousness_type.value},
                    )
                )

            # Memory continuity measurement
            if profile:
                memory_continuity = profile.memory_continuity
                metrics.append(
                    self._create_coherence_metric(
                        CoherenceMetricType.MEMORY_CONTINUITY,
                        memory_continuity,
                        {"memory_count": len(profile.consciousness_memories)},
                    )
                )

            # Temporal consistency measurement
            temporal_consistency = await self._measure_temporal_consistency(identity_id, profile)
            metrics.append(
                self._create_coherence_metric(
                    CoherenceMetricType.TEMPORAL_CONSISTENCY,
                    temporal_consistency,
                    {"measurement_method": "activity_pattern_analysis"},
                )
            )

            # Biometric coherence measurement
            biometric_coherence = await self._measure_biometric_coherence(identity_id, profile)
            metrics.append(
                self._create_coherence_metric(
                    CoherenceMetricType.BIOMETRIC_COHERENCE,
                    biometric_coherence,
                    {"biometric_signatures_count": len(profile.consciousness_signatures) if profile else 0},
                )
            )

            # Namespace alignment measurement
            namespace_alignment = await self._measure_namespace_alignment(identity_id, profile)
            metrics.append(
                self._create_coherence_metric(
                    CoherenceMetricType.NAMESPACE_ALIGNMENT,
                    namespace_alignment,
                    {"namespace_id": profile.consciousness_namespace if profile else "unknown"},
                )
            )

            # Authentication consistency measurement
            auth_consistency = await self._measure_authentication_consistency(identity_id, profile)
            metrics.append(
                self._create_coherence_metric(
                    CoherenceMetricType.AUTHENTICATION_CONSISTENCY,
                    auth_consistency,
                    {"authentication_tier": profile.authentication_tier if profile else "unknown"},
                )
            )

            # Behavioral pattern stability measurement
            behavioral_stability = await self._measure_behavioral_stability(identity_id, profile)
            metrics.append(
                self._create_coherence_metric(
                    CoherenceMetricType.BEHAVIORAL_PATTERN_STABILITY,
                    behavioral_stability,
                    {"pattern_analysis_window_hours": 24},
                )
            )

            # Store metrics in history
            current_metrics = self.metric_history.get(identity_id, [])
            current_metrics.extend(metrics)

            # Keep only last 1000 metrics
            if len(current_metrics) > 1000:
                current_metrics = current_metrics[-1000:]
            self.metric_history[identity_id] = current_metrics

            # Update coherence state
            self._update_coherence_state(coherence_state, metrics)

            # Check for anomalies
            await self._check_coherence_anomalies(identity_id, coherence_state, metrics)

            # Update monitoring metrics
            measurement_latency = (time.perf_counter() - start_time) * 1000
            self.monitoring_metrics["monitoring_latency_ms"] = measurement_latency

            logger.debug(
                f"🔍 Measured identity coherence for {identity_id}: {coherence_state.overall_coherence_score:.3f}"
            )
            return coherence_state

        except Exception as e:
            logger.error(f"❌ Failed to measure identity coherence: {e}")
            return None

    def _create_coherence_metric(
        self, metric_type: CoherenceMetricType, value: float, context: Optional[dict[str, Any]] = None
    ) -> CoherenceMetric:
        """Create coherence metric with trend analysis"""

        metric = CoherenceMetric(
            metric_type=metric_type,
            value=max(0.0, min(1.0, value)),  # Clamp to [0,1]
            measurement_context=context or {},
        )

        # Add trend analysis if previous values exist
        # This would be implemented with historical data analysis
        metric.trend_direction = "stable"  # Simplified for now
        metric.rate_of_change = 0.0

        return metric

    async def _measure_temporal_consistency(self, identity_id: str, profile: Optional[object]) -> float:
        """Measure temporal consistency of identity patterns"""

        try:
            if not profile:
                return 0.5  # Default for missing profile

            # Analyze interaction timing patterns
            current_time = datetime.now(timezone.utc)
            last_interaction = profile.last_interaction

            # Calculate consistency based on regular interaction patterns
            time_since_last = (current_time - last_interaction).total_seconds()

            # Recent interaction indicates higher temporal consistency
            if time_since_last < 3600:  # Within 1 hour
                base_consistency = 0.9
            elif time_since_last < 86400:  # Within 1 day
                base_consistency = 0.7
            elif time_since_last < 604800:  # Within 1 week
                base_consistency = 0.5
            else:
                base_consistency = 0.3

            # Adjust based on consciousness age
            age_factor = min(1.0, profile.consciousness_age_hours / 168)  # Up to 1 week
            consistency_score = base_consistency * (0.7 + age_factor * 0.3)

            return consistency_score

        except Exception as e:
            logger.error(f"❌ Failed to measure temporal consistency: {e}")
            return 0.5

    async def _measure_biometric_coherence(self, identity_id: str, profile: Optional[object]) -> float:
        """Measure coherence of biometric patterns"""

        try:
            if not profile or not hasattr(profile, "consciousness_signatures"):
                return 0.5

            signatures = profile.consciousness_signatures
            if len(signatures) == 0:
                return 0.3  # No biometric data

            if len(signatures) == 1:
                return signatures[0].get("strength", 0.5)

            # Analyze consistency across signatures
            strengths = [sig.get("strength", 0.5) for sig in signatures]

            # Calculate coherence based on signature consistency
            if len(strengths) > 1:
                avg_strength = sum(strengths) / len(strengths)
                strength_std = statistics.stdev(strengths)
                consistency = max(0.0, 1.0 - (strength_std * 2))  # Lower std dev = higher consistency

                coherence_score = avg_strength * 0.7 + consistency * 0.3
            else:
                coherence_score = strengths[0]

            return min(1.0, coherence_score)

        except Exception as e:
            logger.error(f"❌ Failed to measure biometric coherence: {e}")
            return 0.5

    async def _measure_namespace_alignment(self, identity_id: str, profile: Optional[object]) -> float:
        """Measure alignment with namespace policies and coherence"""

        try:
            if not consciousness_namespace_manager:
                return 0.5  # Fallback when namespace manager unavailable

            # Get namespace for identity
            namespace_id = consciousness_namespace_manager.identity_namespace_mapping.get(identity_id)
            if not namespace_id:
                return 0.3  # Not assigned to namespace

            # Get namespace coherence
            namespace_status = await consciousness_namespace_manager.monitor_namespace_coherence(namespace_id)
            if "error" in namespace_status:
                return 0.4

            domain_coherence = namespace_status.get("domain_coherence", 0.5)
            security_level = namespace_status.get("security_level", 0.5)

            # Calculate alignment score
            alignment_score = domain_coherence * 0.6 + security_level * 0.4

            return alignment_score

        except Exception as e:
            logger.error(f"❌ Failed to measure namespace alignment: {e}")
            return 0.5

    async def _measure_authentication_consistency(self, identity_id: str, profile: Optional[object]) -> float:
        """Measure consistency of authentication patterns"""

        try:
            if not profile:
                return 0.5

            # Check authentication tier consistency
            auth_tier = getattr(profile, "authentication_tier", None)
            if not auth_tier:
                return 0.6  # Basic consistency for no tier data

            # Higher tiers indicate more consistent authentication
            tier_scores = {
                "T1_BASIC": 0.6,
                "T2_ENHANCED": 0.7,
                "T3_CONSCIOUSNESS": 0.8,
                "T4_QUANTUM": 0.9,
                "T5_TRANSCENDENT": 1.0,
            }

            base_score = tier_scores.get(auth_tier, 0.6)

            # Adjust based on identity strength
            identity_strength = profile.calculate_identity_strength()
            consistency_score = base_score * 0.8 + identity_strength * 0.2

            return min(1.0, consistency_score)

        except Exception as e:
            logger.error(f"❌ Failed to measure authentication consistency: {e}")
            return 0.5

    async def _measure_behavioral_stability(self, identity_id: str, profile: Optional[object]) -> float:
        """Measure stability of behavioral patterns over time"""

        try:
            # Get historical metrics for this identity
            historical_metrics = self.metric_history.get(identity_id, [])

            if len(historical_metrics) < 5:
                return 0.7  # Default stability for insufficient data

            # Analyze recent behavioral metrics
            recent_metrics = historical_metrics[-10:]  # Last 10 measurements

            # Look for behavioral coherence metrics
            behavioral_values = []
            for metric in recent_metrics:
                if metric.metric_type == CoherenceMetricType.BIOMETRIC_COHERENCE:
                    behavioral_values.append(metric.value)

            if len(behavioral_values) < 2:
                return 0.7  # Default for insufficient behavioral data

            # Calculate stability based on variance in behavioral patterns
            avg_behavioral = sum(behavioral_values) / len(behavioral_values)

            if len(behavioral_values) > 1:
                behavioral_std = statistics.stdev(behavioral_values)
                stability_score = max(0.0, 1.0 - (behavioral_std * 3))  # Lower variance = higher stability
            else:
                stability_score = 0.7

            # Weight by average behavioral score
            final_score = stability_score * 0.6 + avg_behavioral * 0.4

            return min(1.0, final_score)

        except Exception as e:
            logger.error(f"❌ Failed to measure behavioral stability: {e}")
            return 0.5

    def _update_coherence_state(self, coherence_state: CoherenceState, metrics: list[CoherenceMetric]) -> None:
        """Update coherence state with new measurements"""

        try:
            # Update individual metric scores
            for metric in metrics:
                coherence_state.metric_scores[metric.metric_type] = metric.value
                coherence_state.metric_trends[metric.metric_type] = metric.trend_direction

            # Calculate overall coherence score
            if coherence_state.metric_scores:
                # Weight different metrics based on importance
                metric_weights = {
                    CoherenceMetricType.IDENTITY_STRENGTH: 0.2,
                    CoherenceMetricType.CONSCIOUSNESS_DEPTH: 0.15,
                    CoherenceMetricType.MEMORY_CONTINUITY: 0.15,
                    CoherenceMetricType.TEMPORAL_CONSISTENCY: 0.1,
                    CoherenceMetricType.BIOMETRIC_COHERENCE: 0.15,
                    CoherenceMetricType.NAMESPACE_ALIGNMENT: 0.1,
                    CoherenceMetricType.AUTHENTICATION_CONSISTENCY: 0.1,
                    CoherenceMetricType.BEHAVIORAL_PATTERN_STABILITY: 0.05,
                }

                weighted_score = 0.0
                total_weight = 0.0

                for metric_type, score in coherence_state.metric_scores.items():
                    weight = metric_weights.get(metric_type, 0.1)
                    weighted_score += score * weight
                    total_weight += weight

                if total_weight > 0:
                    coherence_state.overall_coherence_score = weighted_score / total_weight

            # Update temporal tracking
            coherence_state.last_updated = datetime.now(timezone.utc)
            coherence_state.measurement_count += 1

            # Update coherence age
            time_since_creation = datetime.now(timezone.utc) - coherence_state.last_updated
            coherence_state.coherence_age_hours = time_since_creation.total_seconds() / 3600

            # Determine overall trend
            coherence_state.coherence_trend = self._determine_overall_trend(coherence_state)

        except Exception as e:
            logger.error(f"❌ Failed to update coherence state: {e}")

    def _determine_overall_trend(self, coherence_state: CoherenceState) -> str:
        """Determine overall coherence trend from individual metric trends"""

        trends = list(coherence_state.metric_trends.values())
        if not trends:
            return "stable"

        # Count trend types
        trend_counts = {"increasing": 0, "decreasing": 0, "stable": 0, "volatile": 0}
        for trend in trends:
            trend_counts[trend] = trend_counts.get(trend, 0) + 1

        # Determine dominant trend
        max_count = max(trend_counts.values())
        for trend, count in trend_counts.items():
            if count == max_count:
                return trend

        return "stable"

    async def _check_coherence_anomalies(
        self, identity_id: str, coherence_state: CoherenceState, metrics: list[CoherenceMetric]
    ) -> None:
        """Check for coherence anomalies and generate alerts"""

        try:
            anomalies = []

            # Check overall coherence score
            overall_score = coherence_state.overall_coherence_score

            if overall_score <= self.coherence_thresholds[CoherenceAlert.EMERGENCY]:
                anomalies.append(
                    self._create_coherence_anomaly(
                        identity_id,
                        "emergency_coherence_loss",
                        CoherenceAlert.EMERGENCY,
                        overall_score,
                        self.coherence_thresholds[CoherenceAlert.EMERGENCY],
                        ["Critical system failure", "Security compromise", "Identity corruption"],
                        ["Immediate intervention required", "Isolate identity", "Emergency recovery protocol"],
                    )
                )
            elif overall_score <= self.coherence_thresholds[CoherenceAlert.CRITICAL]:
                anomalies.append(
                    self._create_coherence_anomaly(
                        identity_id,
                        "critical_coherence_degradation",
                        CoherenceAlert.CRITICAL,
                        overall_score,
                        self.coherence_thresholds[CoherenceAlert.CRITICAL],
                        ["Significant system stress", "Authentication issues", "Memory corruption"],
                        ["Detailed investigation required", "Enhanced monitoring", "Consider identity recovery"],
                    )
                )
            elif overall_score <= self.coherence_thresholds[CoherenceAlert.WARNING]:
                anomalies.append(
                    self._create_coherence_anomaly(
                        identity_id,
                        "coherence_degradation_warning",
                        CoherenceAlert.WARNING,
                        overall_score,
                        self.coherence_thresholds[CoherenceAlert.WARNING],
                        ["Minor system stress", "Temporary issues", "Environmental factors"],
                        ["Continue monitoring", "Check for patterns", "Validate measurements"],
                    )
                )

            # Check individual metric anomalies
            for metric in metrics:
                thresholds = self.metric_thresholds.get(metric.metric_type, {"min": 0.0, "max": 1.0})

                if metric.value < thresholds["min"]:
                    anomalies.append(
                        self._create_coherence_anomaly(
                            identity_id,
                            f"{metric.metric_type.value}_below_threshold",
                            CoherenceAlert.WARNING,
                            metric.value,
                            thresholds["min"],
                            [f"{metric.metric_type.value} degraded"],
                            ["Investigate specific metric", "Check data quality"],
                        )
                    )
                elif metric.value > thresholds["max"]:
                    anomalies.append(
                        self._create_coherence_anomaly(
                            identity_id,
                            f"{metric.metric_type.value}_above_threshold",
                            CoherenceAlert.INFO,
                            metric.value,
                            thresholds["max"],
                            [f"{metric.metric_type.value} unexpectedly high"],
                            ["Validate measurement accuracy", "Consider data anomaly"],
                        )
                    )

            # Store anomalies
            for anomaly in anomalies:
                self.anomaly_history.append(anomaly)
                if anomaly.severity != CoherenceAlert.INFO:
                    self.active_anomalies[identity_id] = anomaly
                    coherence_state.active_alerts.append(
                        {
                            "anomaly_id": anomaly.anomaly_id,
                            "severity": anomaly.severity.value,
                            "type": anomaly.anomaly_type,
                            "detected_at": anomaly.detected_at.isoformat(),
                        }
                    )

            # Emit signals for critical anomalies
            if consciousness_identity_signal_emitter:
                for anomaly in anomalies:
                    if anomaly.severity in [CoherenceAlert.CRITICAL, CoherenceAlert.EMERGENCY]:
                        # This would emit a coherence alert signal
                        logger.warning(
                            f"⚠️ Critical coherence anomaly detected for {identity_id}: {anomaly.anomaly_type}"
                        )

        except Exception as e:
            logger.error(f"❌ Failed to check coherence anomalies: {e}")

    def _create_coherence_anomaly(
        self,
        identity_id: str,
        anomaly_type: str,
        severity: CoherenceAlert,
        trigger_value: float,
        threshold_value: float,
        possible_causes: list[str],
        recommended_actions: list[str],
    ) -> CoherenceAnomaly:
        """Create coherence anomaly record"""

        return CoherenceAnomaly(
            identity_id=identity_id,
            anomaly_type=anomaly_type,
            severity=severity,
            trigger_value=trigger_value,
            threshold_value=threshold_value,
            deviation_magnitude=abs(trigger_value - threshold_value),
            possible_causes=possible_causes,
            recommended_actions=recommended_actions,
            context_data={"monitoring_system": "coherence_monitor"},
        )

    async def _real_time_monitoring_loop(self) -> None:
        """Real-time monitoring loop for all active identities"""

        while self._monitoring_active:
            try:
                # Monitor all active identities
                monitoring_tasks = []
                for identity_id in list(self.coherence_states.keys()):
                    monitoring_tasks.append(self._measure_identity_coherence(identity_id))

                if monitoring_tasks:
                    # Measure coherence for all identities in parallel
                    await asyncio.gather(*monitoring_tasks, return_exceptions=True)

                # Update system metrics
                self.monitoring_metrics["active_monitoring_sessions"] = len(self.coherence_states)

                if self.coherence_states:
                    total_coherence = sum(state.overall_coherence_score for state in self.coherence_states.values())
                    self.monitoring_metrics["average_coherence_score"] = total_coherence / len(self.coherence_states)

                # Real-time monitoring - check every 30 seconds
                await asyncio.sleep(30)

            except Exception as e:
                logger.error(f"❌ Real-time monitoring loop error: {e}")
                await asyncio.sleep(60)  # Longer sleep on error

    async def _anomaly_detection_loop(self) -> None:
        """Anomaly detection loop for advanced pattern analysis"""

        while self._monitoring_active:
            try:
                # Advanced anomaly detection would go here
                # For now, this runs basic pattern analysis

                current_time = datetime.now(timezone.utc)
                anomalies_24h = 0

                # Count recent anomalies
                for anomaly in self.anomaly_history:
                    if (current_time - anomaly.detected_at).total_seconds() < 86400:
                        anomalies_24h += 1

                self.monitoring_metrics["anomalies_detected_24h"] = anomalies_24h

                await asyncio.sleep(300)  # Check every 5 minutes

            except Exception as e:
                logger.error(f"❌ Anomaly detection loop error: {e}")
                await asyncio.sleep(600)

    async def _alert_processing_loop(self) -> None:
        """Alert processing loop for handling coherence alerts"""

        while self._alert_processing_active:
            try:
                # Process active alerts
                alerts_generated = 0

                for identity_id, anomaly in self.active_anomalies.items():
                    if anomaly.severity in [CoherenceAlert.CRITICAL, CoherenceAlert.EMERGENCY]:
                        # Process critical alerts
                        logger.warning(
                            f"🚨 Processing critical coherence alert for {identity_id}: {anomaly.anomaly_type}"
                        )
                        alerts_generated += 1

                self.monitoring_metrics["coherence_alerts_generated"] = alerts_generated

                await asyncio.sleep(60)  # Process alerts every minute

            except Exception as e:
                logger.error(f"❌ Alert processing loop error: {e}")
                await asyncio.sleep(120)

    async def _predictive_modeling_loop(self) -> None:
        """Predictive modeling loop for coherence forecasting"""

        while self._monitoring_active:
            try:
                # Simple predictive modeling
                for coherence_state in self.coherence_states.values():
                    # Predict coherence 24h ahead based on current trend
                    current_score = coherence_state.overall_coherence_score
                    trend = coherence_state.coherence_trend

                    if trend == "increasing":
                        predicted_score = min(1.0, current_score + 0.1)
                        forecast = "improving"
                    elif trend == "decreasing":
                        predicted_score = max(0.0, current_score - 0.1)
                        forecast = "degrading"
                    elif trend == "volatile":
                        predicted_score = current_score
                        forecast = "volatile"
                    else:
                        predicted_score = current_score
                        forecast = "stable"

                    coherence_state.predicted_coherence_24h = predicted_score
                    coherence_state.stability_forecast = forecast
                    coherence_state.risk_score = max(0.0, 1.0 - predicted_score)

                await asyncio.sleep(3600)  # Update predictions every hour

            except Exception as e:
                logger.error(f"❌ Predictive modeling loop error: {e}")
                await asyncio.sleep(1800)

    def _apply_monitoring_config(self, coherence_state: CoherenceState, config: dict[str, Any]) -> None:
        """Apply monitoring configuration to coherence state"""

        # Apply configuration overrides
        for key, value in config.items():
            if hasattr(coherence_state, key):
                setattr(coherence_state, key, value)

    async def get_coherence_monitoring_status(self) -> dict[str, Any]:
        """Get comprehensive coherence monitoring status"""

        try:
            # Active anomaly summary
            active_anomaly_summary = {}
            for severity in CoherenceAlert:
                count = sum(1 for anomaly in self.active_anomalies.values() if anomaly.severity == severity)
                active_anomaly_summary[severity.value] = count

            # Recent trend analysis
            trend_distribution = {}
            for coherence_state in self.coherence_states.values():
                trend = coherence_state.coherence_trend
                trend_distribution[trend] = trend_distribution.get(trend, 0) + 1

            return {
                "monitoring_status": {
                    "monitoring_enabled": self.monitoring_enabled,
                    "real_time_monitoring": self.real_time_monitoring,
                    "anomaly_detection_enabled": self.anomaly_detection_enabled,
                    "predictive_modeling_enabled": self.predictive_modeling_enabled,
                },
                "system_metrics": self.monitoring_metrics.copy(),
                "coherence_overview": {
                    "total_identities": len(self.coherence_states),
                    "average_coherence_score": self.monitoring_metrics["average_coherence_score"],
                    "trend_distribution": trend_distribution,
                },
                "anomaly_status": {
                    "active_anomalies": len(self.active_anomalies),
                    "total_anomaly_history": len(self.anomaly_history),
                    "anomaly_severity_distribution": active_anomaly_summary,
                },
                "thresholds": {
                    "coherence_alert_thresholds": {
                        alert.value: threshold for alert, threshold in self.coherence_thresholds.items()
                    },
                    "metric_thresholds": {
                        metric.value: thresholds for metric, thresholds in self.metric_thresholds.items()
                    },
                },
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Failed to get monitoring status: {e}")
            return {"error": str(e)}

    async def stop_identity_monitoring(self, identity_id: str) -> bool:
        """Stop monitoring coherence for a specific identity"""

        async with self._lock:
            try:
                if identity_id in self.coherence_states:
                    del self.coherence_states[identity_id]

                if identity_id in self.metric_history:
                    del self.metric_history[identity_id]

                if identity_id in self.active_anomalies:
                    del self.active_anomalies[identity_id]

                self.monitoring_metrics["total_identities_monitored"] = max(
                    0, self.monitoring_metrics["total_identities_monitored"] - 1
                )

                logger.info(f"🔍 Stopped coherence monitoring for identity: {identity_id}")
                return True

            except Exception as e:
                logger.error(f"❌ Failed to stop identity monitoring: {e}")
                return False

    async def shutdown_coherence_monitoring(self) -> None:
        """Shutdown coherence monitoring system"""

        logger.info("🛑 Shutting down identity coherence monitoring system...")

        self._monitoring_active = False
        self._alert_processing_active = False

        # Clean up active monitoring
        self.coherence_states.clear()
        self.active_anomalies.clear()

        logger.info("✅ Identity coherence monitoring system shutdown complete")


# Global identity coherence monitor instance
identity_coherence_monitor = IdentityCoherenceMonitor()


# Export key classes
__all__ = [
    "CoherenceAlert",
    "CoherenceAnomaly",
    "CoherenceMetric",
    "CoherenceMetricType",
    "CoherenceState",
    "IdentityCoherenceMonitor",
    "identity_coherence_monitor",
]
