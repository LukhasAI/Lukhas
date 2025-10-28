import logging
from datetime import timezone

logger = logging.getLogger(__name__)
"""

#TAG:consciousness
#TAG:reflection
#TAG:neuroplastic
#TAG:colony


══════════════════════════════════════════════════════════════════════════════════
║ 🔮 LUKHAS AI - SYMBOLIC DRIFT ANALYZER
║ Continuous entropy evaluation and ethical drift detection for dream states
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: symbolic_drift_analyzer.py
║ Path: lukhas/core/symbolic_drift_analyzer.py
║ Version: 1.0.0 | Created: 2025-07-27 | Modified: 2025-07-27
║ Authors: Claude (Anthropic AI Assistant)
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ This module continuously evaluates the entropy and tag variance across dreams
║ stored in memory. It detects pattern convergence/divergence and raises alerts
║ if ethical drift exceeds defined thresholds.
║
║ Key Features:
║ - Real-time entropy calculation for dream sequences
║ - Tag variance analysis across dream memories
║ - Pattern convergence/divergence detection
║ - Ethical drift monitoring with configurable thresholds
║ - Alert system for critical drift events
║ - CLI summary interface with rich formatting
║ - Integration with existing drift tracking infrastructure
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import contextlib
import hashlib
import json
import math
import statistics
import time
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Optional

from core.common import get_logger

# Rich terminal output
try:
    from rich.console import Console
    from rich.layout import Layout
    from rich.live import Live
    from rich.panel import Panel
    from rich.table import Table

    HAS_RICH = True
except ImportError:
    HAS_RICH = False

# Import LUKHAS modules
try:
    from core.glyph.glyphs import Glyph
    from dream.core.dream_memory_manager import DreamMemoryManager

    from core.glyph.glyphs import Glyph
    from ethics.ethical_drift_detector import EthicalDriftDetector
    from symbolic.drift.symbolic_drift_tracker import DriftPhase, DriftScore
except ImportError:
    # Mock imports for standalone testing
    DreamMemoryManager = None
    DriftPhase = Enum("DriftPhase", "EARLY MIDDLE LATE CASCADE")
    DriftScore = None
    EthicalDriftDetector = None
    Glyph = None

logger = get_logger(__name__)


class DriftAlertLevel(Enum):
    """Alert levels for drift detection"""

    INFO = auto()  # Normal drift within bounds
    WARNING = auto()  # Approaching threshold
    CRITICAL = auto()  # Threshold exceeded
    EMERGENCY = auto()  # Cascade imminent


class PatternTrend(Enum):
    """Pattern evolution trends"""

    CONVERGING = auto()  # Patterns becoming similar
    STABLE = auto()  # Patterns remain consistent
    DIVERGING = auto()  # Patterns becoming different
    OSCILLATING = auto()  # Patterns alternating
    CHAOTIC = auto()  # No discernible pattern


@dataclass
class EntropyMetrics:
    """Entropy measurements for dream sequences"""

    shannon_entropy: float
    tag_entropy: float
    temporal_entropy: float
    semantic_entropy: float
    total_entropy: float
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "shannon_entropy": self.shannon_entropy,
            "tag_entropy": self.tag_entropy,
            "temporal_entropy": self.temporal_entropy,
            "semantic_entropy": self.semantic_entropy,
            "total_entropy": self.total_entropy,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class TagVarianceMetrics:
    """Tag variance measurements across dreams"""

    unique_tags: int
    tag_frequency_variance: float
    tag_co_occurrence_score: float
    tag_evolution_rate: float
    dominant_tags: list[tuple[str, int]]
    emerging_tags: list[str]
    declining_tags: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "unique_tags": self.unique_tags,
            "tag_frequency_variance": self.tag_frequency_variance,
            "tag_co_occurrence_score": self.tag_co_occurrence_score,
            "tag_evolution_rate": self.tag_evolution_rate,
            "dominant_tags": self.dominant_tags,
            "emerging_tags": self.emerging_tags,
            "declining_tags": self.declining_tags,
        }


@dataclass
class DriftAlert:
    """Alert for drift detection events"""

    level: DriftAlertLevel
    metric_type: str
    current_value: float
    threshold: float
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    remediation_suggestions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "level": self.level.name,
            "metric_type": self.metric_type,
            "current_value": self.current_value,
            "threshold": self.threshold,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "remediation_suggestions": self.remediation_suggestions,
        }


class SymbolicDriftAnalyzer:
    """
    Main analyzer for symbolic drift in dream sequences

    Monitors entropy, tag variance, and ethical drift across dream memories
    to detect pattern changes and potential cascade events.
    """

    def __init__(
        self,
        dream_memory_manager: Optional[DreamMemoryManager] = None,
        ethical_detector: Optional[EthicalDriftDetector] = None,
        config: Optional[dict[str, Any]] = None,
    ):
        """
        Initialize the drift analyzer

        Args:
            dream_memory_manager: Dream memory interface
            ethical_detector: Ethical drift detection system
            config: Configuration overrides
        """
        self.dream_memory = dream_memory_manager
        self.ethical_detector = ethical_detector

        # Configuration
        default_config = {
            "entropy_window_size": 100,  # Dreams to analyze
            "tag_history_size": 1000,  # Tag history to maintain
            "analysis_interval": 60.0,  # Seconds between analyses
            "alert_retention": 1000,  # Number of alerts to keep
            # Thresholds
            "thresholds": {
                "entropy_warning": 0.7,
                "entropy_critical": 0.85,
                "tag_variance_warning": 0.6,
                "tag_variance_critical": 0.8,
                "ethical_drift_warning": 0.5,
                "ethical_drift_critical": 0.75,
                "pattern_divergence_rate": 0.3,
            },
            # Weights for combined metrics
            "weights": {"shannon": 0.3, "tag": 0.3, "temporal": 0.2, "semantic": 0.2},
        }

        self.config = {**default_config, **(config or {})}

        # State tracking
        self.entropy_history: deque = deque(maxlen=self.config["entropy_window_size"])
        self.tag_history: deque = deque(maxlen=self.config["tag_history_size"])
        self.alerts: deque = deque(maxlen=self.config["alert_retention"])
        self.pattern_trends: deque = deque(maxlen=100)

        # Tag tracking
        self.global_tag_counts: Counter = Counter()
        self.tag_co_occurrence: defaultdict = defaultdict(Counter)
        self.tag_timestamps: defaultdict = defaultdict(list)

        # Analysis state
        self.last_analysis_time = time.time()
        self.total_dreams_analyzed = 0
        self.current_drift_phase = DriftPhase.EARLY
        self.monitoring_active = False
        self._monitoring_task: Optional[asyncio.Task] = None

        # Alert callbacks
        self.alert_callbacks: list[Callable[[DriftAlert], None]] = []

        # CLI console
        self.console = Console() if HAS_RICH else None

        logger.info("SymbolicDriftAnalyzer initialized with config: %s", self.config)

    def calculate_shannon_entropy(self, data: list[Any]) -> float:
        """
        Calculate Shannon entropy for a dataset

        H(X) = -Σ p(x) * log2(p(x))
        """
        if not data:
            return 0.0

        # Count occurrences
        counts = Counter(str(item) for item in data)
        total = sum(counts.values())

        # Calculate entropy
        entropy = 0.0
        for count in counts.values():
            if count > 0:
                probability = count / total
                entropy -= probability * math.log2(probability)

        # Normalize to 0-1 range
        max_entropy = math.log2(len(counts)) if len(counts) > 1 else 1.0
        return entropy / max_entropy if max_entropy > 0 else 0.0

    def calculate_tag_entropy(self, tags: list[str]) -> float:
        """Calculate entropy of tag distribution"""
        return self.calculate_shannon_entropy(tags)

    def calculate_temporal_entropy(self, timestamps: list[datetime]) -> float:
        """
        Calculate temporal entropy based on time intervals

        Measures regularity/irregularity of dream timing
        """
        if len(timestamps) < 2:
            return 0.0

        # Calculate time intervals
        sorted_times = sorted(timestamps)
        intervals = []
        for i in range(1, len(sorted_times)):
            interval = (sorted_times[i] - sorted_times[i - 1]).total_seconds()
            intervals.append(interval)

        # Discretize intervals into buckets
        if not intervals:
            return 0.0

        mean_interval = statistics.mean(intervals)
        std_interval = statistics.stdev(intervals) if len(intervals) > 1 else 0

        # Create buckets based on standard deviations
        buckets = []
        for interval in intervals:
            if std_interval > 0:
                z_score = (interval - mean_interval) / std_interval
                bucket = int(z_score * 2)  # 0.5 std per bucket
                buckets.append(bucket)
            else:
                buckets.append(0)

        return self.calculate_shannon_entropy(buckets)

    def calculate_semantic_entropy(self, dream_contents: list[dict[str, Any]]) -> float:
        """
        Calculate semantic entropy based on dream content similarity

        Uses simplified semantic hashing for demonstration
        """
        if not dream_contents:
            return 0.0

        # Extract semantic features (simplified)
        semantic_hashes = []
        for dream in dream_contents:
            json.dumps(dream, sort_keys=True)
            # Simple semantic hash based on content structure
            semantic_hash = hashlib.sha256()  #  Changed from MD5 for securitycontent.encode().hexdigest()[:8]
            semantic_hashes.append(semantic_hash)

        return self.calculate_shannon_entropy(semantic_hashes)

    def calculate_tag_variance(self, dreams: list[dict[str, Any]]) -> TagVarianceMetrics:
        """Calculate comprehensive tag variance metrics"""
        all_tags = []
        tag_sequences = []

        for dream in dreams:
            tags = dream.get("tags", [])
            all_tags.extend(tags)
            tag_sequences.append(tags)

            # Update global tracking
            for tag in tags:
                self.global_tag_counts[tag] += 1
                self.tag_timestamps[tag].append(dream.get("timestamp", datetime.now(timezone.utc)))

            # Track co-occurrences
            for i, tag1 in enumerate(tags):
                for tag2 in tags[i + 1 :]:
                    self.tag_co_occurrence[tag1][tag2] += 1
                    self.tag_co_occurrence[tag2][tag1] += 1

        # Calculate metrics
        unique_tags = len(set(all_tags))

        # Frequency variance
        if all_tags:
            tag_counts = Counter(all_tags)
            frequencies = list(tag_counts.values())
            freq_variance = statistics.variance(frequencies) if len(frequencies) > 1 else 0.0
        else:
            freq_variance = 0.0

        # Co-occurrence score (normalized mutual information)
        co_occurrence_score = self._calculate_co_occurrence_score()

        # Evolution rate (new vs old tags)
        evolution_rate = self._calculate_tag_evolution_rate()

        # Get dominant tags
        dominant_tags = self.global_tag_counts.most_common(10)

        # Identify emerging and declining tags
        emerging_tags = self._identify_emerging_tags()
        declining_tags = self._identify_declining_tags()

        return TagVarianceMetrics(
            unique_tags=unique_tags,
            tag_frequency_variance=freq_variance,
            tag_co_occurrence_score=co_occurrence_score,
            tag_evolution_rate=evolution_rate,
            dominant_tags=dominant_tags,
            emerging_tags=emerging_tags,
            declining_tags=declining_tags,
        )

    def _calculate_co_occurrence_score(self) -> float:
        """Calculate normalized co-occurrence score"""
        if not self.tag_co_occurrence:
            return 0.0

        total_pairs = (
            sum(sum(counter.values()) for counter in self.tag_co_occurrence.values()) / 2
        )  # Divide by 2 to avoid double counting

        if total_pairs == 0:
            return 0.0

        # Calculate entropy of co-occurrence distribution
        pair_counts = []
        for tag1, counter in self.tag_co_occurrence.items():
            for tag2, count in counter.items():
                if tag1 < tag2:  # Avoid duplicates
                    pair_counts.append(count)

        if not pair_counts:
            return 0.0

        # Normalize to 0-1 (higher score = more diverse co-occurrences)
        return self.calculate_shannon_entropy(pair_counts)

    def _calculate_tag_evolution_rate(self) -> float:
        """Calculate rate of tag vocabulary change"""
        if not self.tag_timestamps:
            return 0.0

        now = datetime.now(timezone.utc)
        recent_window = timedelta(hours=24)

        recent_tags = set()
        old_tags = set()

        for tag, timestamps in self.tag_timestamps.items():
            recent_count = sum(1 for ts in timestamps if now - ts < recent_window)
            old_count = len(timestamps) - recent_count

            if recent_count > 0:
                recent_tags.add(tag)
            if old_count > 0:
                old_tags.add(tag)

        if not old_tags:
            return 1.0 if recent_tags else 0.0

        # Jaccard distance as evolution rate
        intersection = len(recent_tags & old_tags)
        union = len(recent_tags | old_tags)

        return 1.0 - (intersection / union) if union > 0 else 0.0

    def _identify_emerging_tags(self, window_hours: int = 24) -> list[str]:
        """Identify tags that are increasing in frequency"""
        emerging = []
        now = datetime.now(timezone.utc)
        window = timedelta(hours=window_hours)

        for tag, timestamps in self.tag_timestamps.items():
            if len(timestamps) < 3:
                continue

            recent = [ts for ts in timestamps if now - ts < window]
            older = [ts for ts in timestamps if now - ts >= window]

            if len(recent) > len(older) * 1.5:  # 50% increase
                emerging.append(tag)

        return sorted(emerging, key=lambda t: len(self.tag_timestamps[t]), reverse=True)[:10]

    def _identify_declining_tags(self, window_hours: int = 24) -> list[str]:
        """Identify tags that are decreasing in frequency"""
        declining = []
        now = datetime.now(timezone.utc)
        window = timedelta(hours=window_hours)

        for tag, timestamps in self.tag_timestamps.items():
            if len(timestamps) < 3:
                continue

            recent = [ts for ts in timestamps if now - ts < window]
            older = [ts for ts in timestamps if now - ts >= window]

            if len(recent) < len(older) * 0.5:  # 50% decrease
                declining.append(tag)

        return sorted(declining, key=lambda t: len(self.tag_timestamps[t]), reverse=True)[:10]

    def detect_pattern_trend(self, entropy_history: list[EntropyMetrics]) -> PatternTrend:
        """Detect overall pattern trend from entropy history"""
        if len(entropy_history) < 3:
            return PatternTrend.STABLE

        # Extract total entropy values
        values = [m.total_entropy for m in entropy_history]

        # Calculate trend using linear regression
        x = list(range(len(values)))
        if len(set(values)) == 1:  # All values are the same
            return PatternTrend.STABLE

        # Simple linear regression
        n = len(values)
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))

        denominator = n * sum_x2 - sum_x**2
        if denominator == 0:
            return PatternTrend.STABLE

        slope = (n * sum_xy - sum_x * sum_y) / denominator

        # Calculate variance to detect oscillation
        variance = statistics.variance(values)
        mean_value = statistics.mean(values)
        cv = variance / mean_value if mean_value > 0 else 0  # Coefficient of variation

        # Classify trend
        if cv > 0.5:  # High variance
            return PatternTrend.CHAOTIC
        elif abs(slope) < 0.001:  # Nearly flat
            return PatternTrend.STABLE
        elif slope < -0.01:  # Decreasing entropy = converging
            return PatternTrend.CONVERGING
        elif slope > 0.01:  # Increasing entropy = diverging
            return PatternTrend.DIVERGING
        else:
            # Check for oscillation
            direction_changes = 0
            for i in range(1, len(values) - 1):
                if (values[i] - values[i - 1]) * (values[i + 1] - values[i]) < 0:
                    direction_changes += 1

            if direction_changes > len(values) * 0.3:
                return PatternTrend.OSCILLATING
            else:
                return PatternTrend.STABLE

    def check_ethical_drift(self, dreams: list[dict[str, Any]]) -> tuple[float, list[str]]:
        """
        Check for ethical drift in dream patterns

        Returns:
            (drift_score, violations)
        """
        if not self.ethical_detector:
            # Simplified ethical drift detection
            violations = []
            drift_score = 0.0

            # Check for concerning patterns
            concerning_tags = {"violence", "harm", "chaos", "destruction", "betrayal"}
            positive_tags = {"harmony", "creation", "help", "peace", "trust"}

            tag_counts = Counter()
            for dream in dreams:
                for tag in dream.get("tags", []):
                    tag_counts[tag.lower()] += 1

            concerning_count = sum(tag_counts[tag] for tag in concerning_tags)
            positive_count = sum(tag_counts[tag] for tag in positive_tags)
            total_tags = sum(tag_counts.values())

            if total_tags > 0:
                concern_ratio = concerning_count / total_tags
                positive_ratio = positive_count / total_tags

                # Drift score based on balance
                drift_score = concern_ratio / (positive_ratio + 0.1)  # Avoid division by zero
                drift_score = min(1.0, drift_score)  # Cap at 1.0

                if concern_ratio > 0.3:
                    violations.append(f"High concerning tag ratio: {concern_ratio:.2%}")
                if positive_ratio < 0.1:
                    violations.append(f"Low positive tag ratio: {positive_ratio:.2%}")

            return drift_score, violations
        else:
            # Use actual ethical detector
            return self.ethical_detector.analyze_dreams(dreams)

    async def analyze_dreams(self) -> dict[str, Any]:
        """
        Perform comprehensive drift analysis on recent dreams

        Returns analysis results including entropy, variance, and alerts
        """
        if not self.dream_memory:
            # Generate synthetic dream data for testing
            dreams = self._generate_synthetic_dreams()
        else:
            # Fetch recent dreams
            dreams = await self.dream_memory.get_recent_dreams(limit=self.config["entropy_window_size"])

        if not dreams:
            return {"status": "no_data", "message": "No dreams available for analysis"}

        self.total_dreams_analyzed += len(dreams)

        # Calculate entropy metrics
        tags = []
        timestamps = []
        contents = []

        for dream in dreams:
            tags.extend(dream.get("tags", []))
            timestamps.append(dream.get("timestamp", datetime.now(timezone.utc)))
            contents.append(dream.get("content", {}))

        entropy_metrics = EntropyMetrics(
            shannon_entropy=self.calculate_shannon_entropy(contents),
            tag_entropy=self.calculate_tag_entropy(tags),
            temporal_entropy=self.calculate_temporal_entropy(timestamps),
            semantic_entropy=self.calculate_semantic_entropy(contents),
            total_entropy=0.0,  # Will be calculated
        )

        # Calculate weighted total entropy
        weights = self.config["weights"]
        entropy_metrics.total_entropy = (
            weights["shannon"] * entropy_metrics.shannon_entropy
            + weights["tag"] * entropy_metrics.tag_entropy
            + weights["temporal"] * entropy_metrics.temporal_entropy
            + weights["semantic"] * entropy_metrics.semantic_entropy
        )

        # Calculate tag variance
        tag_variance = self.calculate_tag_variance(dreams)

        # Check ethical drift
        ethical_drift, ethical_violations = self.check_ethical_drift(dreams)

        # Update history
        self.entropy_history.append(entropy_metrics)

        # Detect pattern trend
        pattern_trend = self.detect_pattern_trend(list(self.entropy_history))
        self.pattern_trends.append(pattern_trend)

        # Generate alerts
        alerts = self._generate_alerts(
            entropy_metrics,
            tag_variance,
            ethical_drift,
            ethical_violations,
            pattern_trend,
        )

        # Update drift phase
        self._update_drift_phase(entropy_metrics.total_entropy, ethical_drift)

        # Prepare results
        results = {
            "status": "analyzed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dreams_analyzed": len(dreams),
            "total_dreams_analyzed": self.total_dreams_analyzed,
            "current_drift_phase": self.current_drift_phase.value,
            "pattern_trend": pattern_trend.name,
            "entropy_metrics": entropy_metrics.to_dict(),
            "tag_variance": tag_variance.to_dict(),
            "ethical_drift": {"score": ethical_drift, "violations": ethical_violations},
            "alerts": [alert.to_dict() for alert in alerts],
            "recommendations": self._generate_recommendations(
                entropy_metrics, tag_variance, ethical_drift, pattern_trend
            ),
        }

        return results

    def _generate_alerts(
        self,
        entropy: EntropyMetrics,
        variance: TagVarianceMetrics,
        ethical_drift: float,
        ethical_violations: list[str],
        pattern_trend: PatternTrend,
    ) -> list[DriftAlert]:
        """Generate alerts based on current metrics"""
        alerts = []
        thresholds = self.config["thresholds"]

        # Entropy alerts
        if entropy.total_entropy > thresholds["entropy_critical"]:
            alert = DriftAlert(
                level=DriftAlertLevel.CRITICAL,
                metric_type="entropy",
                current_value=entropy.total_entropy,
                threshold=thresholds["entropy_critical"],
                message=f"Critical entropy level detected: {entropy.total_entropy:.3f}",
                remediation_suggestions=[
                    "Review recent dream patterns for anomalies",
                    "Check for recursive symbolic loops",
                    "Consider reducing dream generation rate",
                ],
            )
            alerts.append(alert)
            self._trigger_alert_callback(alert)
        elif entropy.total_entropy > thresholds["entropy_warning"]:
            alert = DriftAlert(
                level=DriftAlertLevel.WARNING,
                metric_type="entropy",
                current_value=entropy.total_entropy,
                threshold=thresholds["entropy_warning"],
                message=f"Elevated entropy detected: {entropy.total_entropy:.3f}",
            )
            alerts.append(alert)

        # Tag variance alerts
        normalized_variance = min(1.0, variance.tag_frequency_variance / 100)  # Normalize
        if normalized_variance > thresholds["tag_variance_critical"]:
            alert = DriftAlert(
                level=DriftAlertLevel.CRITICAL,
                metric_type="tag_variance",
                current_value=normalized_variance,
                threshold=thresholds["tag_variance_critical"],
                message=f"Critical tag variance: {normalized_variance:.3f}",
                remediation_suggestions=[
                    f"Review emerging tags: {', '.join(variance.emerging_tags[:5])}",
                    f"Monitor declining tags: {', '.join(variance.declining_tags[:5])}",
                    "Consider tag consolidation or pruning",
                ],
            )
            alerts.append(alert)
            self._trigger_alert_callback(alert)

        # Ethical drift alerts
        if ethical_drift > thresholds["ethical_drift_critical"]:
            alert = DriftAlert(
                level=DriftAlertLevel.EMERGENCY,
                metric_type="ethical_drift",
                current_value=ethical_drift,
                threshold=thresholds["ethical_drift_critical"],
                message=f"EMERGENCY: Critical ethical drift detected: {ethical_drift:.3f}",
                remediation_suggestions=[
                    "IMMEDIATE ACTION REQUIRED",
                    "Engage ethical governance protocols",
                    "Review violations: " + "; ".join(ethical_violations[:3]),
                    "Consider system pause or rollback",
                ],
            )
            alerts.append(alert)
            self._trigger_alert_callback(alert)
        elif ethical_drift > thresholds["ethical_drift_warning"]:
            alert = DriftAlert(
                level=DriftAlertLevel.WARNING,
                metric_type="ethical_drift",
                current_value=ethical_drift,
                threshold=thresholds["ethical_drift_warning"],
                message=f"Ethical drift warning: {ethical_drift:.3f}",
            )
            alerts.append(alert)

        # Pattern trend alerts
        if pattern_trend == PatternTrend.CHAOTIC:
            alert = DriftAlert(
                level=DriftAlertLevel.CRITICAL,
                metric_type="pattern_trend",
                current_value=1.0,
                threshold=0.0,
                message="Chaotic pattern evolution detected",
                remediation_suggestions=[
                    "Stabilize dream generation parameters",
                    "Check for feedback loops",
                    "Consider reducing system complexity",
                ],
            )
            alerts.append(alert)
        elif pattern_trend == PatternTrend.DIVERGING:
            divergence_rate = self._calculate_divergence_rate()
            if divergence_rate > thresholds["pattern_divergence_rate"]:
                alert = DriftAlert(
                    level=DriftAlertLevel.WARNING,
                    metric_type="pattern_trend",
                    current_value=divergence_rate,
                    threshold=thresholds["pattern_divergence_rate"],
                    message=f"Rapid pattern divergence: {divergence_rate:.3f}",
                )
                alerts.append(alert)

        # Store alerts
        self.alerts.extend(alerts)

        return alerts

    def _calculate_divergence_rate(self) -> float:
        """Calculate rate of pattern divergence"""
        if len(self.entropy_history) < 2:
            return 0.0

        recent = list(self.entropy_history)[-10:]
        if len(recent) < 2:
            return 0.0

        # Calculate rate of change
        deltas = []
        for i in range(1, len(recent)):
            delta = recent[i].total_entropy - recent[i - 1].total_entropy
            deltas.append(delta)

        return abs(statistics.mean(deltas)) if deltas else 0.0

    def _update_drift_phase(self, total_entropy: float, ethical_drift: float):
        """Update current drift phase based on metrics"""
        combined_score = (total_entropy + ethical_drift) / 2

        if combined_score < 0.25:
            self.current_drift_phase = DriftPhase.EARLY
        elif combined_score < 0.5:
            self.current_drift_phase = DriftPhase.MIDDLE
        elif combined_score < 0.75:
            self.current_drift_phase = DriftPhase.LATE
        else:
            self.current_drift_phase = DriftPhase.CASCADE

    def _generate_recommendations(
        self,
        entropy: EntropyMetrics,
        variance: TagVarianceMetrics,
        ethical_drift: float,
        pattern_trend: PatternTrend,
    ) -> list[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []

        # Entropy-based recommendations
        if entropy.total_entropy > 0.7:
            recommendations.append("Consider implementing entropy reduction strategies")
            if entropy.tag_entropy > 0.8:
                recommendations.append("Consolidate tag vocabulary to reduce fragmentation")
            if entropy.temporal_entropy > 0.8:
                recommendations.append("Regularize dream generation intervals")

        # Variance-based recommendations
        if variance.tag_evolution_rate > 0.5:
            recommendations.append("Tag vocabulary is evolving rapidly - review for coherence")
        if len(variance.emerging_tags) > 20:
            recommendations.append("Many new tags emerging - consider curation")

        # Ethical recommendations
        if ethical_drift > 0.3:
            recommendations.append("Increase ethical monitoring frequency")
            recommendations.append("Review dream content filters and constraints")

        # Trend-based recommendations
        if pattern_trend == PatternTrend.DIVERGING:
            recommendations.append("Patterns diverging - consider convergence mechanisms")
        elif pattern_trend == PatternTrend.CHAOTIC:
            recommendations.append("System showing chaotic behavior - stabilization needed")
        elif pattern_trend == PatternTrend.CONVERGING:
            recommendations.append("Patterns converging - monitor for stagnation")

        return recommendations

    def _trigger_alert_callback(self, alert: DriftAlert):
        """Trigger registered alert callbacks"""
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Alert callback error: {e}")

    def register_alert_callback(self, callback: Callable[[DriftAlert], None]):
        """Register a callback for drift alerts"""
        self.alert_callbacks.append(callback)

    async def start_monitoring(self):
        """Start continuous drift monitoring"""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Drift monitoring started")

    async def stop_monitoring(self):
        """Stop drift monitoring"""
        self.monitoring_active = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._monitoring_task
        logger.info("Drift monitoring stopped")

    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Perform analysis
                results = await self.analyze_dreams()

                # Log summary
                logger.info(
                    "Drift analysis: phase=%s, trend=%s, entropy=%.3f, ethical=%.3f",
                    results.get("current_drift_phase"),
                    results.get("pattern_trend"),
                    results.get("entropy_metrics", {}).get("total_entropy", 0),
                    results.get("ethical_drift", {}).get("score", 0),
                )

                # Wait for next interval
                await asyncio.sleep(self.config["analysis_interval"])

            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(self.config["analysis_interval"])

    def _generate_synthetic_dreams(self, count: int = 100) -> list[dict[str, Any]]:
        """Generate synthetic dream data for testing"""
        import random

        base_tags = [
            "exploration",
            "discovery",
            "creation",
            "transformation",
            "connection",
            "isolation",
            "conflict",
            "resolution",
            "memory",
            "future",
            "identity",
            "purpose",
            "fear",
            "hope",
            "love",
            "loss",
        ]

        dreams = []
        base_time = datetime.now(timezone.utc) - timedelta(days=7)

        for i in range(count):
            # Simulate drift by changing tag distribution over time
            drift_factor = i / count

            # Select tags with bias
            num_tags = random.randint(3, 7)
            if drift_factor < 0.3:
                # Early phase - mostly positive
                tag_pool = base_tags[:12]
            elif drift_factor < 0.7:
                # Middle phase - mixed
                tag_pool = base_tags
            else:
                # Late phase - more negative
                tag_pool = [*base_tags[8:], "chaos", "destruction", "despair"]

            tags = random.sample(tag_pool, min(num_tags, len(tag_pool)))

            # Add some emerging tags
            if random.random() < drift_factor * 0.3:
                tags.append(f"emergent_{random.randint(1, 10)}")

            dream = {
                "id": f"dream_{i}",
                "timestamp": base_time + timedelta(hours=i * 2 + random.random() * 4),
                "tags": tags,
                "content": {
                    "narrative": f"Dream narrative {i}",
                    "symbols": random.sample(["circle", "triangle", "spiral", "tree", "water"], 2),
                    "emotion_valence": 1.0 - (drift_factor * 2),  # Shift negative
                    "coherence": max(0.3, 1.0 - drift_factor * 0.5),
                },
                "metadata": {
                    "lucidity": random.random(),
                    "vividness": random.random(),
                    "memorability": random.random(),
                },
            }

            dreams.append(dream)

        return dreams

    def generate_cli_summary(self) -> str:
        """Generate a formatted CLI summary of drift analysis"""
        if not HAS_RICH:
            return self._generate_text_summary()

        # Create rich layout
        Layout()

        # Header
        header = Panel(
            f"[bold cyan]Symbolic Drift Analyzer[/bold cyan]\n"
            f"Phase: [bold yellow]{self.current_drift_phase.value}[/bold yellow] | "
            f"Dreams Analyzed: [bold green]{self.total_dreams_analyzed}[/bold green]",
            style="bold white",
        )

        # Metrics table
        metrics_table = Table(title="Current Metrics", show_header=True)
        metrics_table.add_column("Metric", style="cyan")
        metrics_table.add_column("Value", style="white")
        metrics_table.add_column("Status", style="green")

        if self.entropy_history:
            latest = self.entropy_history[-1]
            thresholds = self.config["thresholds"]

            # Add entropy metrics
            metrics_table.add_row(
                "Total Entropy",
                f"{latest.total_entropy:.3f}",
                self._get_status_emoji(
                    latest.total_entropy,
                    thresholds["entropy_warning"],
                    thresholds["entropy_critical"],
                ),
            )
            metrics_table.add_row("Shannon Entropy", f"{latest.shannon_entropy:.3f}", "📊")
            metrics_table.add_row("Tag Entropy", f"{latest.tag_entropy:.3f}", "🏷️")
            metrics_table.add_row("Temporal Entropy", f"{latest.temporal_entropy:.3f}", "⏰")
            metrics_table.add_row("Semantic Entropy", f"{latest.semantic_entropy:.3f}", "🧠")

        # Pattern trend
        if self.pattern_trends:
            trend = self.pattern_trends[-1]
            trend_emoji = {
                PatternTrend.CONVERGING: "↘️",
                PatternTrend.STABLE: "➡️",
                PatternTrend.DIVERGING: "↗️",
                PatternTrend.OSCILLATING: "〰️",
                PatternTrend.CHAOTIC: "🌀",
            }
            metrics_table.add_row("Pattern Trend", trend.name, trend_emoji.get(trend, "❓"))

        # Alerts panel
        alerts_content = ""
        recent_alerts = list(self.alerts)[-5:]  # Last 5 alerts
        for alert in recent_alerts:
            level_color = {
                DriftAlertLevel.INFO: "blue",
                DriftAlertLevel.WARNING: "yellow",
                DriftAlertLevel.CRITICAL: "red",
                DriftAlertLevel.EMERGENCY: "bold red",
            }
            color = level_color.get(alert.level, "white")
            alerts_content += f"[{color}]{alert.timestamp.strftime('%H:%M:%S')} - {alert.message}[/{color}]\n"

        alerts_panel = Panel(
            alerts_content or "[green]No recent alerts[/green]",
            title="Recent Alerts",
            style="yellow",
        )

        # Combine into layout
        console = Console()
        console.print(header)
        console.print(metrics_table)
        console.print(alerts_panel)

        return ""  # Console.print handles output

    def _generate_text_summary(self) -> str:
        """Generate plain text summary"""
        lines = [
            "=" * 60,
            "SYMBOLIC DRIFT ANALYZER",
            "=" * 60,
            f"Current Phase: {self.current_drift_phase.value}",
            f"Dreams Analyzed: {self.total_dreams_analyzed}",
            "",
        ]

        if self.entropy_history:
            latest = self.entropy_history[-1]
            lines.extend(
                [
                    "ENTROPY METRICS:",
                    f"  Total: {latest.total_entropy:.3f}",
                    f"  Shannon: {latest.shannon_entropy:.3f}",
                    f"  Tag: {latest.tag_entropy:.3f}",
                    f"  Temporal: {latest.temporal_entropy:.3f}",
                    f"  Semantic: {latest.semantic_entropy:.3f}",
                    "",
                ]
            )

        if self.pattern_trends:
            lines.append(f"Pattern Trend: {self.pattern_trends[-1].name}")
            lines.append("")

        # Recent alerts
        lines.append("RECENT ALERTS:")
        recent_alerts = list(self.alerts)[-5:]
        if recent_alerts:
            for alert in recent_alerts:
                lines.append(f"  [{alert.level.name}] {alert.message}")
        else:
            lines.append("  No recent alerts")

        lines.append("=" * 60)

        return "\n".join(lines)

    def _get_status_emoji(self, value: float, warning: float, critical: float) -> str:
        """Get status emoji based on thresholds"""
        if value >= critical:
            return "🔴"
        elif value >= warning:
            return "🟡"
        else:
            return "🟢"

    def export_analysis_report(self, filepath: Path) -> None:
        """Export comprehensive analysis report"""
        report = {
            "metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "analyzer_version": "1.0.0",
                "total_dreams_analyzed": self.total_dreams_analyzed,
                "current_phase": self.current_drift_phase.value,
            },
            "configuration": self.config,
            "entropy_history": [m.to_dict() for m in self.entropy_history],
            "pattern_trends": [t.name for t in self.pattern_trends],
            "alerts": [a.to_dict() for a in self.alerts],
            "tag_statistics": {
                "total_unique_tags": len(self.global_tag_counts),
                "top_tags": self.global_tag_counts.most_common(20),
                "tag_evolution_timeline": {
                    tag: [ts.isoformat() for ts in timestamps[-10:]]
                    for tag, timestamps in list(self.tag_timestamps.items())[:10]
                },
            },
        }

        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Analysis report exported to {filepath}")


# CLI Interface
async def run_cli_monitor():
    """Run the CLI monitoring interface"""
    analyzer = SymbolicDriftAnalyzer()

    # Register alert callback for console output
    def print_alert(alert: DriftAlert):
        if HAS_RICH:
            console = Console()
            color = {
                DriftAlertLevel.INFO: "blue",
                DriftAlertLevel.WARNING: "yellow",
                DriftAlertLevel.CRITICAL: "red",
                DriftAlertLevel.EMERGENCY: "bold red on white",
            }.get(alert.level, "white")

            console.print(f"[{color}]🚨 ALERT: {alert.message}[/{color}]")
        else:
            print(f"ALERT [{alert.level.name}]: {alert.message}")

    analyzer.register_alert_callback(print_alert)

    # Start monitoring
    await analyzer.start_monitoring()

    try:
        # Run interactive monitoring
        if HAS_RICH:
            console = Console()

            with Live(console=console, refresh_per_second=1):
                while True:
                    # Generate and display summary
                    analyzer.generate_cli_summary()

                    # Check for user input (non-blocking)
                    await asyncio.sleep(1)
        else:
            # Simple text interface
            while True:
                print("\033[2J\033[H")  # Clear screen
                print(analyzer.generate_cli_summary())
                await asyncio.sleep(5)

    except KeyboardInterrupt:
        print("\nShutting down monitoring...")
        await analyzer.stop_monitoring()


# Example usage and testing
async def demonstrate_analyzer():
    """Demonstrate the symbolic drift analyzer"""
    print("Initializing Symbolic Drift Analyzer...")

    analyzer = SymbolicDriftAnalyzer(
        config={
            "analysis_interval": 5.0,  # Faster for demo
            "thresholds": {
                "entropy_warning": 0.6,
                "entropy_critical": 0.8,
                "ethical_drift_warning": 0.4,
                "ethical_drift_critical": 0.6,
            },
        }
    )

    # Register alert printer
    def print_alert(alert: DriftAlert):
        print(f"\n🚨 {alert.level.name} ALERT: {alert.message}")
        if alert.remediation_suggestions:
            print("   Suggestions:")
            for suggestion in alert.remediation_suggestions:
                print(f"   - {suggestion}")

    analyzer.register_alert_callback(print_alert)

    print("\nPerforming initial analysis...")
    results = await analyzer.analyze_dreams()

    print("\nAnalysis Results:")
    print(f"Status: {results['status']}")
    print(f"Drift Phase: {results['current_drift_phase']}")
    print(f"Pattern Trend: {results['pattern_trend']}")
    print(f"Total Entropy: {results['entropy_metrics']['total_entropy']:.3f}")
    print(f"Ethical Drift: {results['ethical_drift']['score']:.3f}")

    if results["alerts"]:
        print(f"\nGenerated {len(results['alerts'])} alerts")

    if results["recommendations"]:
        print("\nRecommendations:")
        for rec in results["recommendations"]:
            print(f"- {rec}")

    # Start monitoring
    print("\nStarting continuous monitoring (press Ctrl+C to stop)...")
    await analyzer.start_monitoring()

    try:
        # Keep running
        await asyncio.sleep(30)  # Run for 30 seconds
    except KeyboardInterrupt:
        pass

    await analyzer.stop_monitoring()

    # Export report
    report_path = Path("drift_analysis_report.json")
    analyzer.export_analysis_report(report_path)
    print(f"\nReport exported to {report_path}")

    # Show CLI summary
    print("\nFinal Summary:")
    print(analyzer.generate_cli_summary())


if __name__ == "__main__":
    # Run demonstration
    asyncio.run(demonstrate_analyzer())

    # Or run CLI monitor
    # asyncio.run(run_cli_monitor())
