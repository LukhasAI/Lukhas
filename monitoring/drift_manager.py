"""
Unified Drift Management Module for LUKHAS AI

This module provides a centralized drift calculation and monitoring system
that unifies ethical, memory, and identity drift tracking with symbol attribution.

Features:
- Unified drift scoring across multiple dimensions
- Top symbol attribution for drift contributors
- Feature-flagged for experimental deployment
- Telemetry integration for monitoring
- Threshold-based alerting (0.15 critical threshold)

#TAG:drift
#TAG:monitoring
#TAG:trinity
#TAG:governance
"""
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Prometheus metrics (will be registered if prometheus_client available)
try:
    from prometheus_client import Counter, Histogram

    DRIFT_COMPUTE_ATTEMPTS = Counter(
        'drift_compute_attempts_total',
        'Total drift computation attempts',
        ['kind']
    )
    DRIFT_COMPUTE_SUCCESSES = Counter(
        'drift_compute_successes_total',
        'Successful drift computations',
        ['kind']
    )
    DRIFT_COMPUTE_ERRORS = Counter(
        'drift_compute_errors_total',
        'Failed drift computations',
        ['kind']
    )
    DRIFT_COMPUTE_DURATION = Histogram(
        'drift_compute_duration_seconds',
        'Drift computation duration',
        buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0]
    )
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False
    logger.debug("Prometheus metrics not available")


class DriftKind(Enum):
    """Types of drift monitored by the unified system"""
    ETHICAL = "ethical"
    MEMORY = "memory"
    IDENTITY = "identity"
    CONSCIOUSNESS = "consciousness"  # Future expansion
    UNIFIED = "unified"  # Weighted aggregate


@dataclass
class DriftResult:
    """Result of drift computation"""
    score: float  # 0.0 to 1.0
    top_symbols: List[str]  # Top contributing symbols
    kind: DriftKind
    confidence: float  # 0.0 to 1.0
    metadata: Dict[str, Any]


class DriftManager:
    """
    Unified drift management system for LUKHAS AI.

    Consolidates ethical, memory, and identity drift calculations
    with symbol attribution tracking for root cause analysis.
    """

    # Critical thresholds per Guardian System spec
    CRITICAL_THRESHOLD = 0.15
    WARNING_THRESHOLD = 0.10

    # Weights for unified drift calculation
    ETHICAL_WEIGHT = 0.4
    MEMORY_WEIGHT = 0.3
    IDENTITY_WEIGHT = 0.3

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize drift manager with optional configuration.

        Args:
            config: Optional configuration overrides
        """
        self.config = config or {}

        # Override thresholds if provided
        self.critical_threshold = self.config.get(
            'critical_threshold', self.CRITICAL_THRESHOLD
        )
        self.warning_threshold = self.config.get(
            'warning_threshold', self.WARNING_THRESHOLD
        )

        # Weight configuration
        self.weights = {
            DriftKind.ETHICAL: self.config.get('ethical_weight', self.ETHICAL_WEIGHT),
            DriftKind.MEMORY: self.config.get('memory_weight', self.MEMORY_WEIGHT),
            DriftKind.IDENTITY: self.config.get('identity_weight', self.IDENTITY_WEIGHT),
        }

        # Ledger for audit trail
        self.drift_ledger = []

        logger.info(f"DriftManager initialized with thresholds: critical={self.critical_threshold}, warning={self.warning_threshold}")

    def compute(self, kind: str, prev: Any, curr: Any) -> Dict[str, Any]:
        """
        Compute drift score between previous and current states.

        This is the main API for drift calculation, providing deterministic
        scoring with symbol attribution for debugging and analysis.

        Args:
            kind: Type of drift to calculate ('ethical', 'memory', 'identity', 'unified')
            prev: Previous state (structure depends on kind)
            curr: Current state (structure depends on kind)

        Returns:
            Dictionary with:
                - score: float between 0.0 and 1.0
                - top_symbols: List of top contributing symbols
                - confidence: float between 0.0 and 1.0
                - metadata: Additional context
        """
        start_time = time.time()

        # Track metrics
        if METRICS_AVAILABLE:
            DRIFT_COMPUTE_ATTEMPTS.labels(kind=kind).inc()

        try:
            # Parse kind
            drift_kind = DriftKind(kind.lower())

            # Route to specific calculator
            if drift_kind == DriftKind.ETHICAL:
                result = self._compute_ethical_drift(prev, curr)
            elif drift_kind == DriftKind.MEMORY:
                result = self._compute_memory_drift(prev, curr)
            elif drift_kind == DriftKind.IDENTITY:
                result = self._compute_identity_drift(prev, curr)
            elif drift_kind == DriftKind.UNIFIED:
                result = self._compute_unified_drift(prev, curr)
            else:
                raise ValueError(f"Unknown drift kind: {kind}")

            # Record in ledger for audit
            self._record_drift(result)

            # Track success metrics
            if METRICS_AVAILABLE:
                DRIFT_COMPUTE_SUCCESSES.labels(kind=kind).inc()
                DRIFT_COMPUTE_DURATION.observe(time.time() - start_time)

            # Return standardized format
            return {
                'score': result.score,
                'top_symbols': result.top_symbols,
                'confidence': result.confidence,
                'kind': result.kind.value,
                'metadata': result.metadata
            }

        except Exception as e:
            logger.error(f"Failed to compute drift for {kind}: {e}")
            if METRICS_AVAILABLE:
                DRIFT_COMPUTE_ERRORS.labels(kind=kind).inc()

            # Return safe default
            return {
                'score': 0.0,
                'top_symbols': [],
                'confidence': 0.0,
                'kind': kind,
                'metadata': {'error': str(e)}
            }

    def on_exceed(self, kind: str, score: float, ctx: Dict[str, Any]) -> None:
        """
        Handler for drift threshold exceedance.

        Currently a no-op placeholder for Task 15 (auto-repair).
        Logs the exceedance event for monitoring.

        Args:
            kind: Type of drift that exceeded threshold
            score: The drift score that triggered this
            ctx: Context information about the exceedance
        """
        logger.warning(
            f"Drift threshold exceeded: kind={kind}, score={score:.4f}, "
            f"threshold={self.critical_threshold}, context={ctx}"
        )

        # Record exceedance event
        self.drift_ledger.append({
            'event': 'threshold_exceeded',
            'kind': kind,
            'score': score,
            'context': ctx,
            'timestamp': time.time()
        })

        # TODO(Task 15): Implement auto-repair logic here
        # Will call TraceRepairEngine.reconsolidate() or similar

    def _compute_ethical_drift(self, prev: Any, curr: Any) -> DriftResult:
        """
        Calculate ethical drift between states.

        Measures drift in constitutional compliance, decision patterns,
        and ethical rule adherence.
        """
        # Extract ethical indicators
        prev_indicators = self._extract_ethical_indicators(prev)
        curr_indicators = self._extract_ethical_indicators(curr)

        # Calculate component drifts
        deltas = {}
        for key in prev_indicators:
            if key in curr_indicators:
                delta = abs(curr_indicators[key] - prev_indicators[key])
                deltas[key] = delta

        # Overall score (weighted average)
        if deltas:
            score = sum(deltas.values()) / len(deltas)
        else:
            score = 0.0

        # Identify top contributors
        sorted_deltas = sorted(deltas.items(), key=lambda x: x[1], reverse=True)
        top_symbols = [f"ethical.{k}" for k, v in sorted_deltas[:5] if v > 0.01]

        return DriftResult(
            score=min(1.0, score),
            top_symbols=top_symbols,
            kind=DriftKind.ETHICAL,
            confidence=0.9 if deltas else 0.0,
            metadata={'deltas': deltas}
        )

    def _compute_memory_drift(self, prev: Any, curr: Any) -> DriftResult:
        """
        Calculate memory system drift.

        Measures changes in memory patterns, fold stability,
        and retrieval consistency.
        """
        # Extract memory metrics
        prev_metrics = self._extract_memory_metrics(prev)
        curr_metrics = self._extract_memory_metrics(curr)

        # Calculate drift components
        deltas = {}
        for key in prev_metrics:
            if key in curr_metrics:
                delta = abs(curr_metrics[key] - prev_metrics[key])
                deltas[key] = delta

        # Special handling for fold stability
        if 'fold_count' in prev_metrics and 'fold_count' in curr_metrics:
            fold_drift = abs(curr_metrics['fold_count'] - prev_metrics['fold_count']) / 1000.0
            deltas['fold_stability'] = fold_drift

        # Calculate score
        if deltas:
            score = sum(deltas.values()) / len(deltas)
        else:
            score = 0.0

        # Identify top symbols
        sorted_deltas = sorted(deltas.items(), key=lambda x: x[1], reverse=True)
        top_symbols = [f"memory.{k}" for k, v in sorted_deltas[:5] if v > 0.01]

        return DriftResult(
            score=min(1.0, score),
            top_symbols=top_symbols,
            kind=DriftKind.MEMORY,
            confidence=0.85 if deltas else 0.0,
            metadata={'deltas': deltas}
        )

    def _compute_identity_drift(self, prev: Any, curr: Any) -> DriftResult:
        """
        Calculate identity coherence drift.

        Measures changes in identity consistency, namespace isolation,
        and authentication patterns.
        """
        # Extract identity features
        prev_features = self._extract_identity_features(prev)
        curr_features = self._extract_identity_features(curr)

        # Calculate deltas (skip non-numeric fields)
        deltas = {}
        for key in prev_features:
            if key in curr_features and key != 'namespace_hash':
                try:
                    delta = abs(curr_features[key] - prev_features[key])
                    deltas[key] = delta
                except (TypeError, ValueError):
                    continue  # Skip non-numeric comparisons

        # Identity-specific: namespace consistency check
        if 'namespace_hash' in prev_features and 'namespace_hash' in curr_features:
            if prev_features['namespace_hash'] != curr_features['namespace_hash']:
                deltas['namespace_change'] = 0.5  # Significant drift

        # Calculate score
        if deltas:
            score = sum(deltas.values()) / len(deltas)
        else:
            score = 0.0

        # Top contributors
        sorted_deltas = sorted(deltas.items(), key=lambda x: x[1], reverse=True)
        top_symbols = [f"identity.{k}" for k, v in sorted_deltas[:5] if v > 0.01]

        return DriftResult(
            score=min(1.0, score),
            top_symbols=top_symbols,
            kind=DriftKind.IDENTITY,
            confidence=0.88 if deltas else 0.0,
            metadata={'deltas': deltas}
        )

    def _compute_unified_drift(self, prev: Any, curr: Any) -> DriftResult:
        """
        Calculate unified drift across all dimensions.

        Weighted combination of ethical, memory, and identity drift.
        """
        # Compute individual drifts
        ethical = self._compute_ethical_drift(
            prev.get('ethical', {}),
            curr.get('ethical', {})
        )
        memory = self._compute_memory_drift(
            prev.get('memory', {}),
            curr.get('memory', {})
        )
        identity = self._compute_identity_drift(
            prev.get('identity', {}),
            curr.get('identity', {})
        )

        # Weighted aggregation
        unified_score = (
            self.weights[DriftKind.ETHICAL] * ethical.score +
            self.weights[DriftKind.MEMORY] * memory.score +
            self.weights[DriftKind.IDENTITY] * identity.score
        )

        # Combine top symbols
        all_symbols = []
        all_symbols.extend(ethical.top_symbols[:2])
        all_symbols.extend(memory.top_symbols[:2])
        all_symbols.extend(identity.top_symbols[:2])

        # Average confidence
        avg_confidence = (ethical.confidence + memory.confidence + identity.confidence) / 3

        return DriftResult(
            score=min(1.0, unified_score),
            top_symbols=all_symbols[:10],  # Top 10 unified
            kind=DriftKind.UNIFIED,
            confidence=avg_confidence,
            metadata={
                'ethical_score': ethical.score,
                'memory_score': memory.score,
                'identity_score': identity.score,
                'weights': self.weights
            }
        )

    def _extract_ethical_indicators(self, state: Any) -> Dict[str, float]:
        """Extract ethical indicators from state."""
        if not state:
            return {}

        # Handle dict-like states
        if isinstance(state, dict):
            return {
                'compliance': float(state.get('compliance', 0.0)),
                'constitutional': float(state.get('constitutional', 0.0)),
                'drift_score': float(state.get('drift_score', 0.0)),
                'ethics_phi': float(state.get('ethics_phi', 1.0)),
                'guardian_score': float(state.get('guardian_score', 1.0))
            }

        # Handle object states
        indicators = {}
        if hasattr(state, 'compliance'):
            indicators['compliance'] = float(state.compliance)
        if hasattr(state, 'drift_score'):
            indicators['drift_score'] = float(state.drift_score)

        return indicators

    def _extract_memory_metrics(self, state: Any) -> Dict[str, float]:
        """Extract memory metrics from state."""
        if not state:
            return {}

        # Handle dict-like states
        if isinstance(state, dict):
            return {
                'fold_count': float(state.get('fold_count', 0)),
                'entropy': float(state.get('entropy', 0.0)),
                'coherence': float(state.get('coherence', 1.0)),
                'retrieval_accuracy': float(state.get('retrieval_accuracy', 1.0)),
                'cascade_risk': float(state.get('cascade_risk', 0.0))
            }

        # Handle object states
        metrics = {}
        if hasattr(state, 'fold_count'):
            metrics['fold_count'] = float(state.fold_count)
        if hasattr(state, 'entropy'):
            metrics['entropy'] = float(state.entropy)

        return metrics

    def _extract_identity_features(self, state: Any) -> Dict[str, Any]:
        """Extract identity features from state (mixed types for namespace_hash)."""
        if not state:
            return {}

        # Handle dict-like states
        if isinstance(state, dict):
            features = {
                'coherence': float(state.get('coherence', 1.0)),
                'namespace_integrity': float(state.get('namespace_integrity', 1.0)),
                'auth_consistency': float(state.get('auth_consistency', 1.0)),
                'tier_compliance': float(state.get('tier_compliance', 1.0))
            }

            # Add namespace hash if present (keep as string)
            if 'namespace_hash' in state:
                features['namespace_hash'] = state['namespace_hash']

            return features

        # Handle object states
        features = {}
        if hasattr(state, 'coherence'):
            features['coherence'] = float(state.coherence)
        if hasattr(state, 'namespace_hash'):
            features['namespace_hash'] = state.namespace_hash

        return features

    def _record_drift(self, result: DriftResult) -> None:
        """Record drift calculation in audit ledger."""
        self.drift_ledger.append({
            'timestamp': time.time(),
            'kind': result.kind.value,
            'score': result.score,
            'top_symbols': result.top_symbols,
            'confidence': result.confidence
        })

        # Emit ledger line for audit
        logger.info(
            f"DRIFT_LEDGER: kind={result.kind.value}, score={result.score:.4f}, "
            f"symbols={','.join(result.top_symbols[:3]) if result.top_symbols else 'none'}"
        )

    def get_drift_history(self, kind: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """
        Retrieve drift calculation history from ledger.

        Args:
            kind: Filter by drift kind (optional)
            limit: Maximum entries to return

        Returns:
            List of drift ledger entries
        """
        entries = self.drift_ledger

        if kind:
            entries = [e for e in entries if e.get('kind') == kind]

        return entries[-limit:]


# Global instance for convenience
_drift_manager = None


def get_drift_manager(config: Optional[Dict[str, Any]] = None) -> DriftManager:
    """
    Get or create the global drift manager instance.

    Args:
        config: Optional configuration (only used on first call)

    Returns:
        DriftManager instance
    """
    global _drift_manager
    if _drift_manager is None:
        _drift_manager = DriftManager(config)
    return _drift_manager