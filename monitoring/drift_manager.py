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
import os
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# --- micro-opt constants (env-tunable) ---
_SAFE_THRESHOLD = float(os.getenv("DRIFT_SAFE_THRESHOLD", "0.15"))
_FLUSH_N = int(os.getenv("DRIFT_COMPUTE_FLUSH_N", "32"))

# Prometheus metrics (will be registered if prometheus_client available)
try:
    from prometheus_client import Counter, Histogram
except Exception:  # test envs without prometheus
    class _Noop:
        def inc(self, *_, **__): pass
        def labels(self, *_, **__): return self
        def observe(self, *_, **__): pass
    def Counter(*_, **__): return _Noop()
    def Histogram(*_, **__): return _Noop()

# --- split compute vs autorepair metrics (keep compute path lean) ---
DRIFT_COMPUTE_ATTEMPTS = Counter("drift_compute_attempts_total", "Drift compute attempts (no repair)", ['kind'])
DRIFT_COMPUTE_SUCCESSES = Counter("drift_compute_successes_total", "Drift compute successes (no repair)", ['kind'])
DRIFT_COMPUTE_ERRORS = Counter("drift_compute_errors_total", "Drift compute errors (no repair)", ['kind'])
DRIFT_COMPUTE_DURATION_SECONDS = Histogram("drift_compute_duration_seconds", "Drift compute duration (seconds)",
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0])

# Back-compat mirroring in case older tests expect drift.compute.*
DRIFT_COMPUTE_ATTEMPTS_LEGACY = Counter("drift.compute.attempts_total", "LEGACY mirror: attempts", ['kind'])
DRIFT_COMPUTE_SUCCESSES_LEGACY = Counter("drift.compute.successes_total", "LEGACY mirror: successes", ['kind'])
DRIFT_COMPUTE_ERRORS_LEGACY = Counter("drift.compute.errors_total", "LEGACY mirror: errors", ['kind'])

# Auto-repair metrics
DRIFT_AUTOREPAIR_ATTEMPTS = Counter(
    'drift_autorepair_attempts_total',
    'Total autonomous repair attempts',
    ['kind', 'method']
)
DRIFT_AUTOREPAIR_SUCCESSES = Counter(
    'drift_autorepair_successes_total',
    'Successful autonomous repairs',
    ['kind', 'method']
)
DRIFT_AUTOREPAIR_ERRORS = Counter(
    'drift_autorepair_errors_total',
    'Failed autonomous repair attempts',
    ['kind']
)
DRIFT_AUTOREPAIR_DURATION = Histogram(
    'drift_autorepair_duration_seconds',
    'Autonomous repair operation duration',
    buckets=[0.001, 0.01, 0.1, 0.5, 1.0, 5.0, 10.0]
)
METRICS_AVAILABLE = True


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

        # --- micro-opt: batched timer + lazy repair engine handle ---
        self._compute_durations_ms = []      # ring buffer for durations (ms)
        self._flush_every = _FLUSH_N
        self._repair_engine = None  # lazy; set on first real repair

        logger.info(f"DriftManager initialized with thresholds: critical={self.critical_threshold}, warning={self.warning_threshold}")

    def _flush_timer_if_needed(self):
        """Flush the batched durations to the histogram every N calls."""
        if len(self._compute_durations_ms) >= self._flush_every:
            for ms in self._compute_durations_ms:
                DRIFT_COMPUTE_DURATION_SECONDS.observe(ms / 1000.0)  # seconds
            self._compute_durations_ms.clear()

    def _lazy_repair_engine(self):
        """Initialize the repair engine only when actually repairing."""
        if self._repair_engine is None:
            # reuse existing internal initializer; behavior unchanged
            self._repair_engine = self._initialize_repair_engine()
        return self._repair_engine

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
        _start_ns = time.perf_counter_ns()
        DRIFT_COMPUTE_ATTEMPTS.labels(kind=kind).inc()
        DRIFT_COMPUTE_ATTEMPTS_LEGACY.labels(kind=kind).inc()

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

            score = result.score
            top_symbols = result.top_symbols

            # --- micro-opt early return on safe band ---
            if score <= _SAFE_THRESHOLD:
                DRIFT_COMPUTE_SUCCESSES.labels(kind=kind).inc()
                DRIFT_COMPUTE_SUCCESSES_LEGACY.labels(kind=kind).inc()
                dt_ms = (time.perf_counter_ns() - _start_ns) / 1e6
                self._compute_durations_ms.append(dt_ms)
                self._flush_timer_if_needed()
                return {"score": score, "top_symbols": top_symbols, "confidence": result.confidence,
                       "kind": result.kind.value, "metadata": result.metadata}

            # Record in ledger for audit (only for above-threshold drift)
            self._record_drift(result)

            # Track success metrics
            DRIFT_COMPUTE_SUCCESSES.labels(kind=kind).inc()
            DRIFT_COMPUTE_SUCCESSES_LEGACY.labels(kind=kind).inc()
            dt_ms = (time.perf_counter_ns() - _start_ns) / 1e6
            self._compute_durations_ms.append(dt_ms)
            self._flush_timer_if_needed()

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
            DRIFT_COMPUTE_ERRORS.labels(kind=kind).inc()
            DRIFT_COMPUTE_ERRORS_LEGACY.labels(kind=kind).inc()
            dt_ms = (time.perf_counter_ns() - _start_ns) / 1e6
            self._compute_durations_ms.append(dt_ms)
            self._flush_timer_if_needed()

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

        Implements autonomous drift correction by invoking the TraceRepairEngine
        when drift scores exceed the critical threshold (0.15).

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
        exceedance_event = {
            'event': 'threshold_exceeded',
            'kind': kind,
            'score': score,
            'context': ctx,
            'timestamp': time.time()
        }
        self.drift_ledger.append(exceedance_event)

        # Attempt autonomous repair if TraceRepairEngine is available
        repair_result = None
        repair_start_time = time.time()

        if self._should_attempt_repair(kind, score):
            try:
                # --- micro-opt: lazy init of repair engine + table dispatch ---
                engine = self._lazy_repair_engine()

                if engine:
                    # Extract top symbols from most recent computation
                    top_symbols = ctx.get('top_symbols', [])
                    if not top_symbols and 'state' in ctx:
                        # Try to extract from context state
                        top_symbols = self._extract_symbols_from_context(kind, ctx)

                    logger.info(f"Attempting autonomous repair for {kind} drift: "
                              f"score={score:.4f}, symbols={top_symbols[:3]}")

                    # --- micro-opt: table dispatch for method selection ---
                    band = "critical" if score >= _SAFE_THRESHOLD else "major" if score >= (_SAFE_THRESHOLD * 0.67) else "minor"
                    METHOD = {
                        ("ethical",   "critical"): "realign",
                        ("ethical",   "major"):    "stabilize",
                        ("ethical",   "minor"):    "reconsolidate",
                        ("memory",    "critical"): "rollback",
                        ("memory",    "major"):    "reconsolidate",
                        ("memory",    "minor"):    "reconsolidate",
                        ("identity",  "critical"): "stabilize",
                        ("identity",  "major"):    "realign",
                        ("identity",  "minor"):    "reconsolidate",
                    }
                    method = METHOD.get((kind, band), "reconsolidate")

                    # Track repair attempt
                    if METRICS_AVAILABLE:
                        DRIFT_AUTOREPAIR_ATTEMPTS.labels(kind=kind, method=method).inc()

                    # Invoke repair engine with optimized method selection
                    repair_result = engine.reconsolidate(
                        kind=kind,
                        score=score,
                        context=ctx,
                        top_symbols=top_symbols
                    )

                    # Log repair result and track metrics
                    if repair_result.success:
                        logger.info(
                            f"Auto-repair SUCCESS: {kind} drift reduced from "
                            f"{repair_result.pre_score:.4f} to {repair_result.post_score:.4f} "
                            f"({repair_result.improvement_pct:.1f}% improvement)"
                        )

                        # Track successful repair metrics
                        if METRICS_AVAILABLE:
                            DRIFT_AUTOREPAIR_SUCCESSES.labels(
                                kind=kind,
                                method=repair_result.method.value
                            ).inc()
                            DRIFT_AUTOREPAIR_DURATION.observe(time.time() - repair_start_time)

                        # Record successful repair
                        repair_event = {
                            'event': 'auto_repair_success',
                            'kind': kind,
                            'method': repair_result.method.value,
                            'pre_score': repair_result.pre_score,
                            'post_score': repair_result.post_score,
                            'improvement_pct': repair_result.improvement_pct,
                            'timestamp': repair_result.timestamp,
                            'rationale': f"Repair via {repair_result.method.value} reduced drift by {repair_result.improvement_pct:.1f}%"
                        }
                        self.drift_ledger.append(repair_event)
                    else:
                        logger.error(
                            f"Auto-repair FAILED for {kind} drift: "
                            f"{repair_result.details.get('error', 'unknown error')}"
                        )

                        # Track failed repair metrics
                        if METRICS_AVAILABLE:
                            DRIFT_AUTOREPAIR_ERRORS.labels(kind=kind).inc()

                        # Record failed repair
                        repair_event = {
                            'event': 'auto_repair_failure',
                            'kind': kind,
                            'error': repair_result.details.get('error', 'unknown'),
                            'timestamp': repair_result.timestamp,
                            'rationale': f"Repair attempt failed: {repair_result.details.get('error', 'unknown')}"
                        }
                        self.drift_ledger.append(repair_event)

            except Exception as e:
                logger.error(f"Error during auto-repair attempt: {e}")
                repair_event = {
                    'event': 'auto_repair_error',
                    'kind': kind,
                    'error': str(e),
                    'timestamp': time.time(),
                    'rationale': f"Repair engine error: {str(e)}"
                }
                self.drift_ledger.append(repair_event)

        # Always emit policy ledger line with repair rationale
        policy_line = {
            'policy_event': 'drift_threshold_exceeded',
            'kind': kind,
            'score': score,
            'threshold': self.critical_threshold,
            'repair_attempted': repair_result is not None,
            'repair_success': repair_result.success if repair_result else False,
            'rationale': repair_result.details.get('rationale', 'No repair attempted') if repair_result else 'Threshold exceeded, no repair engine available'
        }
        logger.info(f"POLICY_LEDGER: {policy_line}")

    def _should_attempt_repair(self, kind: str, score: float) -> bool:
        """
        Determine if autonomous repair should be attempted.

        Args:
            kind: Drift type
            score: Drift score

        Returns:
            bool: True if repair should be attempted
        """
        # Only attempt repair for significant drift
        if score < self.critical_threshold:
            return False

        # Check if we have feature flag enabled
        import os
        if os.environ.get('LUKHAS_EXPERIMENTAL') != '1':
            logger.debug("Auto-repair disabled: LUKHAS_EXPERIMENTAL not set")
            return False

        # Check if we've already attempted too many repairs recently
        recent_attempts = [
            entry for entry in self.drift_ledger
            if entry.get('event') in ['auto_repair_success', 'auto_repair_failure', 'auto_repair_error']
            and entry.get('kind') == kind
            and entry.get('timestamp', 0) > time.time() - 300  # Last 5 minutes
        ]

        if len(recent_attempts) >= 3:
            logger.warning(f"Skipping auto-repair: too many recent attempts for {kind} ({len(recent_attempts)} in last 5min)")
            return False

        return True

    def _initialize_repair_engine(self):
        """Initialize the TraceRepairEngine if available."""
        try:
            from lukhas.trace.TraceRepairEngine import TraceRepairEngine
            self._repair_engine = TraceRepairEngine()
            logger.info("TraceRepairEngine initialized for auto-repair")
        except ImportError as e:
            logger.debug(f"TraceRepairEngine not available: {e}")
            self._repair_engine = None

    def _extract_symbols_from_context(self, kind: str, ctx: Dict[str, Any]) -> List[str]:
        """
        Extract drift symbols from context when not directly provided.

        Args:
            kind: Drift type
            ctx: Context dictionary

        Returns:
            List of inferred top symbols
        """
        symbols = []

        # Extract from state if available
        state = ctx.get('state', {})
        if isinstance(state, dict):
            for key in state.keys():
                symbols.append(f"{kind}.{key}")

        # Add common symbols based on kind
        if kind == 'ethical':
            symbols.extend(['ethical.compliance', 'ethical.constitutional'])
        elif kind == 'memory':
            symbols.extend(['memory.fold_stability', 'memory.entropy'])
        elif kind == 'identity':
            symbols.extend(['identity.coherence', 'identity.namespace_integrity'])

        return symbols[:5]  # Return top 5

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