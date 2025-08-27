#!/usr/bin/env python3
"""
Symbolic Threshold Autotuner - Advanced adaptive threshold management
Automatically adjusts Guardian System thresholds based on symbolic pattern analysis and system performance
"""

import asyncio
import json
import logging
import math
import statistics
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ThresholdConfig:
    """Configuration for a monitoring threshold"""

    name: str
    current_value: float
    default_value: float
    min_value: float
    max_value: float
    description: str
    metric_type: str  # 'entropy', 'drift', 'stability', 'trust', 'performance'
    symbolic_pattern: list[str]
    adjustment_sensitivity: float = 0.1  # How quickly to adjust (0.0-1.0)
    stability_window: int = 20  # Number of samples for stability analysis
    last_adjusted: float = 0.0
    adjustment_count: int = 0
    performance_history: list[float] = field(default_factory=list)


@dataclass
class SystemPerformanceMetrics:
    """System performance metrics for threshold tuning"""

    timestamp: float
    entropy_score: float
    drift_velocity: float
    consciousness_stability: float
    guardian_response_time: float
    threat_detection_accuracy: float
    false_positive_rate: float
    false_negative_rate: float
    system_load: float
    intervention_success_rate: float
    symbolic_coherence: float


@dataclass
class AdjustmentEvent:
    """Record of a threshold adjustment"""

    timestamp: float
    threshold_name: str
    old_value: float
    new_value: float
    reason: str
    symbolic_sequence: list[str]
    performance_impact: Optional[float] = None
    confidence: float = 0.5


class SymbolicThresholdAutotuner:
    """
    Advanced threshold autotuner using symbolic pattern analysis
    Automatically adjusts Guardian System thresholds for optimal performance
    """

    # Default threshold configurations
    DEFAULT_THRESHOLDS = {
        "entropy_warning": ThresholdConfig(
            name="entropy_warning",
            current_value=0.6,
            default_value=0.6,
            min_value=0.3,
            max_value=0.9,
            description="Entropy level that triggers warning state",
            metric_type="entropy",
            symbolic_pattern=["🔥", "⚠️", "📊"],
            adjustment_sensitivity=0.15,
        ),
        "entropy_critical": ThresholdConfig(
            name="entropy_critical",
            current_value=0.8,
            default_value=0.8,
            min_value=0.5,
            max_value=0.95,
            description="Entropy level that triggers critical intervention",
            metric_type="entropy",
            symbolic_pattern=["🔥", "🚨", "💥"],
            adjustment_sensitivity=0.1,
        ),
        "drift_detection": ThresholdConfig(
            name="drift_detection",
            current_value=0.4,
            default_value=0.4,
            min_value=0.1,
            max_value=0.7,
            description="Drift velocity threshold for pattern anomaly detection",
            metric_type="drift",
            symbolic_pattern=["🌪️", "🔍", "⚠️"],
            adjustment_sensitivity=0.2,
        ),
        "consciousness_stability": ThresholdConfig(
            name="consciousness_stability",
            current_value=0.7,
            default_value=0.7,
            min_value=0.5,
            max_value=0.95,
            description="Minimum consciousness stability before intervention",
            metric_type="stability",
            symbolic_pattern=["🧠", "⚓", "🛡️"],
            adjustment_sensitivity=0.08,
        ),
        "trust_minimum": ThresholdConfig(
            name="trust_minimum",
            current_value=0.3,
            default_value=0.3,
            min_value=0.1,
            max_value=0.6,
            description="Minimum trust score for automated decisions",
            metric_type="trust",
            symbolic_pattern=["🤝", "🔒", "✅"],
            adjustment_sensitivity=0.12,
        ),
        "response_time_max": ThresholdConfig(
            name="response_time_max",
            current_value=2.0,
            default_value=2.0,
            min_value=0.5,
            max_value=10.0,
            description="Maximum acceptable Guardian response time (seconds)",
            metric_type="performance",
            symbolic_pattern=["⚡", "⏱️", "🎯"],
            adjustment_sensitivity=0.25,
        ),
        "false_positive_max": ThresholdConfig(
            name="false_positive_max",
            current_value=0.15,
            default_value=0.15,
            min_value=0.05,
            max_value=0.4,
            description="Maximum acceptable false positive rate",
            metric_type="performance",
            symbolic_pattern=["❌", "🎯", "📊"],
            adjustment_sensitivity=0.18,
        ),
        "intervention_confidence": ThresholdConfig(
            name="intervention_confidence",
            current_value=0.75,
            default_value=0.75,
            min_value=0.5,
            max_value=0.95,
            description="Minimum confidence for automatic intervention",
            metric_type="trust",
            symbolic_pattern=["🛡️", "🎯", "✅"],
            adjustment_sensitivity=0.1,
        ),
    }

    # Symbolic patterns for different adjustment types
    ADJUSTMENT_PATTERNS = {
        "increase_sensitivity": {
            "pattern": ["📈", "🔍", "⚡"],
            "description": "Increasing sensitivity to detect more threats",
        },
        "decrease_sensitivity": {
            "pattern": ["📉", "🛡️", "🌿"],
            "description": "Decreasing sensitivity to reduce false positives",
        },
        "optimize_balance": {
            "pattern": ["⚖️", "🎯", "✨"],
            "description": "Optimizing balance between detection and performance",
        },
        "emergency_adjustment": {
            "pattern": ["🚨", "⚡", "🔧"],
            "description": "Emergency threshold adjustment for system stability",
        },
        "performance_tuning": {
            "pattern": ["⚙️", "📊", "🚀"],
            "description": "Performance-based threshold optimization",
        },
        "stability_enhancement": {
            "pattern": ["⚓", "🌿", "🔒"],
            "description": "Adjusting for improved system stability",
        },
    }

    def __init__(
        self,
        config_file: str = "next_gen/guardian/threshold_config.json",
        metrics_file: str = "next_gen/guardian/performance_metrics.json",
        adjustment_log: str = "next_gen/guardian/threshold_adjustments.json",
        update_interval: float = 30.0,
    ):

        self.config_file = Path(config_file)
        self.metrics_file = Path(metrics_file)
        self.adjustment_log = Path(adjustment_log)
        self.update_interval = update_interval

        # System state
        self.thresholds: dict[str, ThresholdConfig] = {}
        self.metrics_history: deque = deque(maxlen=1000)  # Last 1000 metric samples
        self.adjustment_history: list[AdjustmentEvent] = []
        self.performance_baseline: dict[str, float] = {}

        # Tuning parameters
        self.learning_rate = 0.05
        self.stability_requirement = 0.8  # System must be stable before adjusting
        self.adjustment_cooldown = 300  # 5 minutes between adjustments per threshold
        self.confidence_threshold = 0.7  # Minimum confidence for adjustment

        # Symbolic analysis
        self.pattern_effectiveness: dict[str, list[float]] = defaultdict(list)
        self.symbolic_feedback: dict[str, float] = {}

        # Initialize system
        self._load_threshold_config()
        self._load_metrics_history()
        self._load_adjustment_history()
        self._calculate_performance_baseline()

        logger.info("🎯 Symbolic Threshold Autotuner initialized")

    def _load_threshold_config(self):
        """Load threshold configuration from file or use defaults"""
        try:
            if self.config_file.exists():
                with open(self.config_file) as f:
                    config_data = json.load(f)

                self.thresholds = {}
                for name, data in config_data.items():
                    threshold = ThresholdConfig(
                        name=data["name"],
                        current_value=data["current_value"],
                        default_value=data["default_value"],
                        min_value=data["min_value"],
                        max_value=data["max_value"],
                        description=data["description"],
                        metric_type=data["metric_type"],
                        symbolic_pattern=data["symbolic_pattern"],
                        adjustment_sensitivity=data.get("adjustment_sensitivity", 0.1),
                        stability_window=data.get("stability_window", 20),
                        last_adjusted=data.get("last_adjusted", 0.0),
                        adjustment_count=data.get("adjustment_count", 0),
                        performance_history=data.get("performance_history", []),
                    )
                    self.thresholds[name] = threshold
            else:
                # Use default thresholds
                self.thresholds = self.DEFAULT_THRESHOLDS.copy()
                self._save_threshold_config()

        except Exception as e:
            logger.warning(f"Failed to load threshold config: {e}. Using defaults.")
            self.thresholds = self.DEFAULT_THRESHOLDS.copy()

    def _save_threshold_config(self):
        """Save threshold configuration to file"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            config_data = {}
            for name, threshold in self.thresholds.items():
                config_data[name] = asdict(threshold)

            with open(self.config_file, "w") as f:
                json.dump(config_data, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save threshold config: {e}")

    def _load_metrics_history(self):
        """Load historical performance metrics"""
        try:
            if self.metrics_file.exists():
                with open(self.metrics_file) as f:
                    metrics_data = json.load(f)

                self.metrics_history = deque(maxlen=1000)
                for entry in metrics_data[-1000:]:  # Load last 1000 entries
                    metrics = SystemPerformanceMetrics(
                        timestamp=entry["timestamp"],
                        entropy_score=entry["entropy_score"],
                        drift_velocity=entry["drift_velocity"],
                        consciousness_stability=entry["consciousness_stability"],
                        guardian_response_time=entry["guardian_response_time"],
                        threat_detection_accuracy=entry["threat_detection_accuracy"],
                        false_positive_rate=entry["false_positive_rate"],
                        false_negative_rate=entry["false_negative_rate"],
                        system_load=entry["system_load"],
                        intervention_success_rate=entry["intervention_success_rate"],
                        symbolic_coherence=entry["symbolic_coherence"],
                    )
                    self.metrics_history.append(metrics)
            else:
                self.metrics_history = deque(maxlen=1000)

        except Exception as e:
            logger.warning(f"Failed to load metrics history: {e}")
            self.metrics_history = deque(maxlen=1000)

    def _load_adjustment_history(self):
        """Load threshold adjustment history"""
        try:
            if self.adjustment_log.exists():
                with open(self.adjustment_log) as f:
                    adjustment_data = json.load(f)

                self.adjustment_history = []
                for entry in adjustment_data:
                    adjustment = AdjustmentEvent(
                        timestamp=entry["timestamp"],
                        threshold_name=entry["threshold_name"],
                        old_value=entry["old_value"],
                        new_value=entry["new_value"],
                        reason=entry["reason"],
                        symbolic_sequence=entry["symbolic_sequence"],
                        performance_impact=entry.get("performance_impact"),
                        confidence=entry.get("confidence", 0.5),
                    )
                    self.adjustment_history.append(adjustment)
            else:
                self.adjustment_history = []

        except Exception as e:
            logger.warning(f"Failed to load adjustment history: {e}")
            self.adjustment_history = []

    def _save_adjustment_history(self):
        """Save adjustment history to file"""
        try:
            self.adjustment_log.parent.mkdir(parents=True, exist_ok=True)
            adjustment_data = [asdict(adj) for adj in self.adjustment_history]

            with open(self.adjustment_log, "w") as f:
                json.dump(adjustment_data, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save adjustment history: {e}")

    def _calculate_performance_baseline(self):
        """Calculate performance baseline from historical data"""
        if len(self.metrics_history) < 10:
            # Default baseline if insufficient data
            self.performance_baseline = {
                "response_time": 2.0,
                "accuracy": 0.85,
                "false_positive_rate": 0.15,
                "false_negative_rate": 0.1,
                "system_load": 0.3,
                "intervention_success": 0.8,
                "symbolic_coherence": 0.9,
            }
        else:
            metrics_list = list(self.metrics_history)
            self.performance_baseline = {
                "response_time": statistics.median(
                    [m.guardian_response_time for m in metrics_list]
                ),
                "accuracy": statistics.median(
                    [m.threat_detection_accuracy for m in metrics_list]
                ),
                "false_positive_rate": statistics.median(
                    [m.false_positive_rate for m in metrics_list]
                ),
                "false_negative_rate": statistics.median(
                    [m.false_negative_rate for m in metrics_list]
                ),
                "system_load": statistics.median([m.system_load for m in metrics_list]),
                "intervention_success": statistics.median(
                    [m.intervention_success_rate for m in metrics_list]
                ),
                "symbolic_coherence": statistics.median(
                    [m.symbolic_coherence for m in metrics_list]
                ),
            }

        logger.info(f"Performance baseline calculated: {self.performance_baseline}")

    async def add_performance_metrics(self, metrics: SystemPerformanceMetrics):
        """Add new performance metrics and trigger analysis"""
        self.metrics_history.append(metrics)

        # Save metrics to file periodically
        if len(self.metrics_history) % 10 == 0:
            await self._save_metrics_history()

        # Trigger threshold analysis
        await self._analyze_and_adjust_thresholds(metrics)

    async def _save_metrics_history(self):
        """Save metrics history to file"""
        try:
            self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
            metrics_data = [
                asdict(metrics) for metrics in list(self.metrics_history)[-100:]
            ]  # Save last 100

            with open(self.metrics_file, "w") as f:
                json.dump(metrics_data, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save metrics history: {e}")

    async def _analyze_and_adjust_thresholds(
        self, current_metrics: SystemPerformanceMetrics
    ):
        """Analyze current performance and adjust thresholds if needed"""
        if len(self.metrics_history) < 5:
            return  # Need more data before adjusting

        current_time = time.time()

        # Check system stability before making adjustments
        system_stability = await self._assess_system_stability()
        if system_stability < self.stability_requirement:
            logger.info("System stability too low for threshold adjustments")
            return

        # Analyze each threshold
        for _threshold_name, threshold in self.thresholds.items():
            # Check cooldown period
            if current_time - threshold.last_adjusted < self.adjustment_cooldown:
                continue

            # Analyze performance for this threshold
            adjustment_recommendation = await self._analyze_threshold_performance(
                threshold, current_metrics
            )

            if (
                adjustment_recommendation
                and adjustment_recommendation["confidence"] >= self.confidence_threshold
            ):
                await self._apply_threshold_adjustment(
                    threshold, adjustment_recommendation
                )

    async def _assess_system_stability(self) -> float:
        """Assess overall system stability"""
        if len(self.metrics_history) < 10:
            return 0.5  # Insufficient data

        recent_metrics = list(self.metrics_history)[-10:]

        # Calculate stability metrics
        entropy_variance = statistics.variance(
            [m.entropy_score for m in recent_metrics]
        )
        drift_variance = statistics.variance([m.drift_velocity for m in recent_metrics])
        consciousness_variance = statistics.variance(
            [m.consciousness_stability for m in recent_metrics]
        )

        # Lower variance indicates higher stability
        stability_score = 1.0 - min(
            1.0, (entropy_variance + drift_variance + consciousness_variance) / 3
        )

        return stability_score

    async def _analyze_threshold_performance(
        self, threshold: ThresholdConfig, current_metrics: SystemPerformanceMetrics
    ) -> Optional[dict]:
        """Analyze performance for a specific threshold"""

        # Get recent performance data
        recent_metrics = list(self.metrics_history)[-threshold.stability_window :]
        if len(recent_metrics) < threshold.stability_window // 2:
            return None

        # Analyze based on threshold type
        if threshold.metric_type == "entropy":
            return await self._analyze_entropy_threshold(
                threshold, recent_metrics, current_metrics
            )
        elif threshold.metric_type == "drift":
            return await self._analyze_drift_threshold(
                threshold, recent_metrics, current_metrics
            )
        elif threshold.metric_type == "stability":
            return await self._analyze_stability_threshold(
                threshold, recent_metrics, current_metrics
            )
        elif threshold.metric_type == "trust":
            return await self._analyze_trust_threshold(
                threshold, recent_metrics, current_metrics
            )
        elif threshold.metric_type == "performance":
            return await self._analyze_performance_threshold(
                threshold, recent_metrics, current_metrics
            )

        return None

    async def _analyze_entropy_threshold(
        self,
        threshold: ThresholdConfig,
        recent_metrics: list[SystemPerformanceMetrics],
        current_metrics: SystemPerformanceMetrics,
    ) -> Optional[dict]:
        """Analyze entropy threshold performance"""

        # Calculate entropy statistics
        entropy_values = [m.entropy_score for m in recent_metrics]
        statistics.mean(entropy_values)
        entropy_trend = (
            entropy_values[-1] - entropy_values[0] if len(entropy_values) >= 2 else 0
        )

        # Calculate false positive/negative rates
        false_positives = statistics.mean(
            [m.false_positive_rate for m in recent_metrics]
        )
        false_negatives = statistics.mean(
            [m.false_negative_rate for m in recent_metrics]
        )

        # Determine adjustment need
        if false_positives > self.performance_baseline["false_positive_rate"] * 1.2:
            # Too many false positives - increase threshold (less sensitive)
            new_value = min(
                threshold.max_value,
                threshold.current_value + threshold.adjustment_sensitivity,
            )
            return {
                "new_value": new_value,
                "reason": f"Reducing false positives (current: {false_positives:.3f})",
                "confidence": min(
                    0.9,
                    false_positives / self.performance_baseline["false_positive_rate"],
                ),
                "adjustment_type": "decrease_sensitivity",
                "symbolic_sequence": self.ADJUSTMENT_PATTERNS["decrease_sensitivity"][
                    "pattern"
                ],
            }

        elif false_negatives > self.performance_baseline["false_negative_rate"] * 1.2:
            # Too many false negatives - decrease threshold (more sensitive)
            new_value = max(
                threshold.min_value,
                threshold.current_value - threshold.adjustment_sensitivity,
            )
            return {
                "new_value": new_value,
                "reason": f"Reducing false negatives (current: {false_negatives:.3f})",
                "confidence": min(
                    0.9,
                    false_negatives / self.performance_baseline["false_negative_rate"],
                ),
                "adjustment_type": "increase_sensitivity",
                "symbolic_sequence": self.ADJUSTMENT_PATTERNS["increase_sensitivity"][
                    "pattern"
                ],
            }

        elif entropy_trend > 0.1:
            # Entropy increasing trend - preemptively lower threshold
            new_value = max(
                threshold.min_value,
                threshold.current_value - threshold.adjustment_sensitivity * 0.5,
            )
            return {
                "new_value": new_value,
                "reason": f"Preemptive adjustment for entropy trend ({entropy_trend:+.3f})",
                "confidence": min(0.8, abs(entropy_trend) * 5),
                "adjustment_type": "increase_sensitivity",
                "symbolic_sequence": self.ADJUSTMENT_PATTERNS["increase_sensitivity"][
                    "pattern"
                ],
            }

        return None

    async def _analyze_drift_threshold(
        self,
        threshold: ThresholdConfig,
        recent_metrics: list[SystemPerformanceMetrics],
        current_metrics: SystemPerformanceMetrics,
    ) -> Optional[dict]:
        """Analyze drift threshold performance"""

        drift_values = [m.drift_velocity for m in recent_metrics]
        avg_drift = statistics.mean(drift_values)
        drift_variance = (
            statistics.variance(drift_values) if len(drift_values) > 1 else 0
        )

        intervention_success = statistics.mean(
            [m.intervention_success_rate for m in recent_metrics]
        )

        # If drift is consistently low but we're still intervening too much
        if avg_drift < threshold.current_value * 0.7 and intervention_success < 0.7:
            new_value = max(
                threshold.min_value,
                threshold.current_value - threshold.adjustment_sensitivity,
            )
            return {
                "new_value": new_value,
                "reason": f"Low drift, poor intervention success ({intervention_success:.3f})",
                "confidence": 0.7,
                "adjustment_type": "increase_sensitivity",
                "symbolic_sequence": self.ADJUSTMENT_PATTERNS["increase_sensitivity"][
                    "pattern"
                ],
            }

        # If drift variance is high, we need more sensitive detection
        elif drift_variance > 0.1:
            new_value = max(
                threshold.min_value,
                threshold.current_value - threshold.adjustment_sensitivity * 0.5,
            )
            return {
                "new_value": new_value,
                "reason": f"High drift variance detected ({drift_variance:.3f})",
                "confidence": min(0.8, drift_variance * 5),
                "adjustment_type": "increase_sensitivity",
                "symbolic_sequence": self.ADJUSTMENT_PATTERNS["increase_sensitivity"][
                    "pattern"
                ],
            }

        return None

    async def _analyze_stability_threshold(
        self,
        threshold: ThresholdConfig,
        recent_metrics: list[SystemPerformanceMetrics],
        current_metrics: SystemPerformanceMetrics,
    ) -> Optional[dict]:
        """Analyze consciousness stability threshold performance"""

        stability_values = [m.consciousness_stability for m in recent_metrics]
        avg_stability = statistics.mean(stability_values)
        stability_trend = (
            stability_values[-1] - stability_values[0]
            if len(stability_values) >= 2
            else 0
        )

        system_load = statistics.mean([m.system_load for m in recent_metrics])

        # If system is stable but load is high, we might be too conservative
        if avg_stability > 0.9 and system_load > 0.7:
            new_value = max(
                threshold.min_value,
                threshold.current_value - threshold.adjustment_sensitivity,
            )
            return {
                "new_value": new_value,
                "reason": "High stability, high load - increasing sensitivity",
                "confidence": 0.6,
                "adjustment_type": "increase_sensitivity",
                "symbolic_sequence": self.ADJUSTMENT_PATTERNS["performance_tuning"][
                    "pattern"
                ],
            }

        # If stability is declining, be more conservative
        elif stability_trend < -0.1:
            new_value = min(
                threshold.max_value,
                threshold.current_value + threshold.adjustment_sensitivity,
            )
            return {
                "new_value": new_value,
                "reason": f"Declining stability trend ({stability_trend:+.3f})",
                "confidence": min(0.8, abs(stability_trend) * 5),
                "adjustment_type": "stability_enhancement",
                "symbolic_sequence": self.ADJUSTMENT_PATTERNS["stability_enhancement"][
                    "pattern"
                ],
            }

        return None

    async def _analyze_trust_threshold(
        self,
        threshold: ThresholdConfig,
        recent_metrics: list[SystemPerformanceMetrics],
        current_metrics: SystemPerformanceMetrics,
    ) -> Optional[dict]:
        """Analyze trust threshold performance"""

        false_positives = statistics.mean(
            [m.false_positive_rate for m in recent_metrics]
        )
        false_negatives = statistics.mean(
            [m.false_negative_rate for m in recent_metrics]
        )
        intervention_success = statistics.mean(
            [m.intervention_success_rate for m in recent_metrics]
        )

        # Balance between security and usability
        if false_positives > 0.2 and intervention_success > 0.8:
            # Too restrictive - lower threshold
            new_value = max(
                threshold.min_value,
                threshold.current_value - threshold.adjustment_sensitivity,
            )
            return {
                "new_value": new_value,
                "reason": f"Balancing security vs usability (FP: {false_positives:.3f})",
                "confidence": 0.7,
                "adjustment_type": "optimize_balance",
                "symbolic_sequence": self.ADJUSTMENT_PATTERNS["optimize_balance"][
                    "pattern"
                ],
            }

        elif false_negatives > 0.15:
            # Too permissive - raise threshold
            new_value = min(
                threshold.max_value,
                threshold.current_value + threshold.adjustment_sensitivity,
            )
            return {
                "new_value": new_value,
                "reason": f"Reducing false negatives ({false_negatives:.3f})",
                "confidence": 0.8,
                "adjustment_type": "increase_sensitivity",
                "symbolic_sequence": self.ADJUSTMENT_PATTERNS["increase_sensitivity"][
                    "pattern"
                ],
            }

        return None

    async def _analyze_performance_threshold(
        self,
        threshold: ThresholdConfig,
        recent_metrics: list[SystemPerformanceMetrics],
        current_metrics: SystemPerformanceMetrics,
    ) -> Optional[dict]:
        """Analyze performance threshold"""

        if threshold.name == "response_time_max":
            response_times = [m.guardian_response_time for m in recent_metrics]
            avg_response_time = statistics.mean(response_times)

            if avg_response_time < threshold.current_value * 0.6:
                # Response time is much better than threshold - tighten it
                new_value = max(threshold.min_value, avg_response_time * 1.2)
                return {
                    "new_value": new_value,
                    "reason": f"Tightening response time threshold (avg: {avg_response_time:.2f}s)",
                    "confidence": 0.7,
                    "adjustment_type": "performance_tuning",
                    "symbolic_sequence": self.ADJUSTMENT_PATTERNS["performance_tuning"][
                        "pattern"
                    ],
                }

            elif avg_response_time > threshold.current_value * 0.9:
                # Response time approaching threshold - relax it slightly
                new_value = min(threshold.max_value, threshold.current_value * 1.1)
                return {
                    "new_value": new_value,
                    "reason": f"Relaxing response time threshold (avg: {avg_response_time:.2f}s)",
                    "confidence": 0.6,
                    "adjustment_type": "performance_tuning",
                    "symbolic_sequence": self.ADJUSTMENT_PATTERNS["performance_tuning"][
                        "pattern"
                    ],
                }

        elif threshold.name == "false_positive_max":
            fp_rates = [m.false_positive_rate for m in recent_metrics]
            avg_fp_rate = statistics.mean(fp_rates)

            if avg_fp_rate > threshold.current_value * 0.8:
                # Approaching false positive limit - need adjustment
                new_value = min(threshold.max_value, avg_fp_rate * 1.1)
                return {
                    "new_value": new_value,
                    "reason": f"Adjusting for actual false positive rate ({avg_fp_rate:.3f})",
                    "confidence": 0.8,
                    "adjustment_type": "optimize_balance",
                    "symbolic_sequence": self.ADJUSTMENT_PATTERNS["optimize_balance"][
                        "pattern"
                    ],
                }

        return None

    async def _apply_threshold_adjustment(
        self, threshold: ThresholdConfig, adjustment: dict
    ):
        """Apply a threshold adjustment"""

        old_value = threshold.current_value
        new_value = adjustment["new_value"]

        # Apply the adjustment
        threshold.current_value = new_value
        threshold.last_adjusted = time.time()
        threshold.adjustment_count += 1

        # Create adjustment event
        adjustment_event = AdjustmentEvent(
            timestamp=time.time(),
            threshold_name=threshold.name,
            old_value=old_value,
            new_value=new_value,
            reason=adjustment["reason"],
            symbolic_sequence=adjustment["symbolic_sequence"],
            confidence=adjustment["confidence"],
        )

        self.adjustment_history.append(adjustment_event)

        # Log the adjustment
        logger.info(
            f"🎯 Adjusted threshold '{threshold.name}': {old_value:.3f} → {new_value:.3f}"
        )
        logger.info(f"   Reason: {adjustment['reason']}")
        logger.info(f"   Symbolic: {'→'.join(adjustment['symbolic_sequence'])}")
        logger.info(f"   Confidence: {adjustment['confidence']:.2f}")

        # Save configuration
        self._save_threshold_config()
        self._save_adjustment_history()

        # Track symbolic pattern effectiveness
        pattern_key = adjustment["adjustment_type"]
        if pattern_key not in self.pattern_effectiveness:
            self.pattern_effectiveness[pattern_key] = []

        # Performance impact will be calculated later
        self.pattern_effectiveness[pattern_key].append(adjustment["confidence"])

    async def start_monitoring(self):
        """Start the threshold monitoring and adjustment loop"""
        logger.info("🎯 Starting threshold autotuner monitoring")

        while True:
            try:
                # Simulate metric collection (in production, this would come from real
                # system)
                current_metrics = await self._collect_system_metrics()
                await self.add_performance_metrics(current_metrics)

                # Periodic analysis and reporting
                if len(self.metrics_history) % 50 == 0:
                    await self._generate_tuning_report()

                await asyncio.sleep(self.update_interval)

            except Exception as e:
                logger.error(f"Error in threshold monitoring: {e}")
                await asyncio.sleep(self.update_interval * 2)  # Back off on error

    async def _collect_system_metrics(self) -> SystemPerformanceMetrics:
        """Collect current system metrics (simulated for demo)"""
        current_time = time.time()

        # Simulate realistic metrics with some noise and trends
        base_entropy = 0.4 + 0.3 * math.sin(current_time * 0.001)
        base_drift = 0.2 + 0.2 * math.sin(current_time * 0.0005)
        base_stability = 0.8 + 0.1 * math.cos(current_time * 0.0003)

        # Add some noise
        noise = (current_time % 1) * 0.1 - 0.05

        return SystemPerformanceMetrics(
            timestamp=current_time,
            entropy_score=max(0.0, min(1.0, base_entropy + noise)),
            drift_velocity=max(0.0, min(1.0, base_drift + noise * 0.5)),
            consciousness_stability=max(0.0, min(1.0, base_stability + noise * 0.3)),
            guardian_response_time=1.5 + noise * 2,
            threat_detection_accuracy=0.85 + noise * 0.1,
            false_positive_rate=0.12 + abs(noise) * 0.05,
            false_negative_rate=0.08 + abs(noise) * 0.03,
            system_load=0.3 + abs(noise) * 0.2,
            intervention_success_rate=0.82 + noise * 0.1,
            symbolic_coherence=0.9 + noise * 0.05,
        )

    async def _generate_tuning_report(self):
        """Generate a threshold tuning report"""
        logger.info("📊 Generating threshold tuning report")

        report = {
            "timestamp": time.time(),
            "system_summary": {
                "total_adjustments": len(self.adjustment_history),
                "active_thresholds": len(self.thresholds),
                "metrics_collected": len(self.metrics_history),
            },
            "threshold_status": {},
            "recent_adjustments": [],
            "performance_trends": {},
            "symbolic_effectiveness": {},
        }

        # Threshold status
        for name, threshold in self.thresholds.items():
            report["threshold_status"][name] = {
                "current_value": threshold.current_value,
                "default_value": threshold.default_value,
                "adjustment_count": threshold.adjustment_count,
                "last_adjusted": threshold.last_adjusted,
                "drift_from_default": threshold.current_value - threshold.default_value,
            }

        # Recent adjustments
        recent_adjustments = [
            adj
            for adj in self.adjustment_history
            if time.time() - adj.timestamp < 86400
        ]  # Last 24 hours
        for adj in recent_adjustments[-5:]:  # Last 5 adjustments
            report["recent_adjustments"].append(
                {
                    "threshold": adj.threshold_name,
                    "change": f"{adj.old_value:.3f} → {adj.new_value:.3f}",
                    "reason": adj.reason,
                    "symbolic": "→".join(adj.symbolic_sequence),
                    "age_hours": (time.time() - adj.timestamp) / 3600,
                }
            )

        # Performance trends
        if len(self.metrics_history) >= 20:
            recent_20 = list(self.metrics_history)[-20:]
            older_20 = (
                list(self.metrics_history)[-40:-20]
                if len(self.metrics_history) >= 40
                else []
            )

            if older_20:
                for metric in [
                    "entropy_score",
                    "drift_velocity",
                    "consciousness_stability",
                    "guardian_response_time",
                    "false_positive_rate",
                ]:
                    recent_avg = statistics.mean(
                        [getattr(m, metric) for m in recent_20]
                    )
                    older_avg = statistics.mean([getattr(m, metric) for m in older_20])
                    trend = recent_avg - older_avg

                    report["performance_trends"][metric] = {
                        "recent_avg": recent_avg,
                        "trend": trend,
                        "trend_direction": (
                            "improving"
                            if trend < 0
                            and metric
                            in [
                                "entropy_score",
                                "drift_velocity",
                                "false_positive_rate",
                            ]
                            else "declining" if trend > 0 else "stable"
                        ),
                    }

        # Symbolic pattern effectiveness
        for pattern, effectiveness_scores in self.pattern_effectiveness.items():
            if effectiveness_scores:
                report["symbolic_effectiveness"][pattern] = {
                    "usage_count": len(effectiveness_scores),
                    "avg_confidence": statistics.mean(effectiveness_scores),
                    "pattern_symbols": self.ADJUSTMENT_PATTERNS.get(pattern, {}).get(
                        "pattern", []
                    ),
                }

        logger.info(f"Report summary: {report['system_summary']}")
        logger.info(f"Recent adjustments: {len(report['recent_adjustments'])}")
        logger.info(f"Performance trends tracked: {len(report['performance_trends'])}")

    def get_current_thresholds(self) -> dict[str, float]:
        """Get current threshold values"""
        return {
            name: threshold.current_value for name, threshold in self.thresholds.items()
        }

    def get_threshold_info(self, threshold_name: str) -> Optional[dict]:
        """Get detailed information about a specific threshold"""
        if threshold_name not in self.thresholds:
            return None

        threshold = self.thresholds[threshold_name]
        recent_adjustments = [
            adj
            for adj in self.adjustment_history
            if adj.threshold_name == threshold_name
        ]

        return {
            "name": threshold.name,
            "current_value": threshold.current_value,
            "default_value": threshold.default_value,
            "value_range": [threshold.min_value, threshold.max_value],
            "description": threshold.description,
            "metric_type": threshold.metric_type,
            "symbolic_pattern": threshold.symbolic_pattern,
            "adjustment_count": threshold.adjustment_count,
            "last_adjusted": threshold.last_adjusted,
            "recent_adjustments": len(
                [
                    adj
                    for adj in recent_adjustments
                    if time.time() - adj.timestamp < 86400
                ]
            ),
        }

    async def manual_threshold_adjustment(
        self, threshold_name: str, new_value: float, reason: str = "Manual adjustment"
    ) -> bool:
        """Manually adjust a threshold value"""
        if threshold_name not in self.thresholds:
            logger.error(f"Unknown threshold: {threshold_name}")
            return False

        threshold = self.thresholds[threshold_name]

        # Validate new value
        if not (threshold.min_value <= new_value <= threshold.max_value):
            logger.error(
                f"Value {new_value} out of range [{threshold.min_value}, {threshold.max_value}]"
            )
            return False

        # Create manual adjustment
        adjustment = {
            "new_value": new_value,
            "reason": reason,
            "confidence": 1.0,  # Manual adjustments have full confidence
            "adjustment_type": "manual",
            "symbolic_sequence": ["👤", "🔧", "⚙️"],
        }

        await self._apply_threshold_adjustment(threshold, adjustment)
        logger.info(
            f"Manual threshold adjustment applied: {threshold_name} = {new_value}"
        )
        return True


async def main():
    """Demo of symbolic threshold autotuner"""
    autotuner = SymbolicThresholdAutotuner(
        update_interval=5.0
    )  # 5 second intervals for demo

    print("🎯 Symbolic Threshold Autotuner Demo")
    print("=" * 50)

    # Show initial thresholds
    print("\nInitial Thresholds:")
    for name, value in autotuner.get_current_thresholds().items():
        info = autotuner.get_threshold_info(name)
        print(f"  {name:20}: {value:.3f} ({info['description']})")

    print("\n🚀 Starting threshold monitoring...")
    print("Press Ctrl+C to stop\n")

    # Start monitoring (this will run the demo simulation)
    try:
        await autotuner.start_monitoring()
    except KeyboardInterrupt:
        print("\n🎯 Threshold autotuner demo stopped")

        # Show final thresholds
        print("\nFinal Thresholds:")
        for name, value in autotuner.get_current_thresholds().items():
            info = autotuner.get_threshold_info(name)
            initial_value = info["default_value"]
            change = value - initial_value
            change_str = f"({change:+.3f})" if abs(change) > 0.001 else "(unchanged)"
            print(f"  {name:20}: {value:.3f} {change_str}")

        # Show adjustment summary
        print(f"\nAdjustments made: {len(autotuner.adjustment_history)}")
        if autotuner.adjustment_history:
            print("Recent adjustments:")
            for adj in autotuner.adjustment_history[-3:]:
                print(
                    f"  {adj.threshold_name}: {adj.old_value:.3f} → {adj.new_value:.3f}"
                )
                print(f"    Reason: {adj.reason}")
                print(f"    Symbolic: {'→'.join(adj.symbolic_sequence)}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🎯 Symbolic Threshold Autotuner stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
