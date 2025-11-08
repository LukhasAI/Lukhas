"""
#AIM{stability}
#AIM{core}

#TAG:qim
#TAG:qi_states
#TAG:neuroplastic
#TAG:colony


Integrity Probe
===============

Runs consistency checks on DriftScore deltas and collapse recovery logic.
"""
import logging
import os
import threading
import time
from dataclasses import dataclass
from typing import Any, Optional

# Micro-check metrics (lazy initialization to avoid registry conflicts)
_microcheck_metrics = None
_metrics_lock = threading.Lock()

def _get_microcheck_metrics():
    global _microcheck_metrics
    with _metrics_lock:
        if _microcheck_metrics is None:
            try:
                from prometheus_client import Counter, Histogram
                _microcheck_metrics = {
                    'attempts': Counter(
                        'akaqualia_microcheck_attempts_total',
                        'Total micro-check attempts in AkaQualia loop'
                    ),
                    'failures': Counter(
                        'akaqualia_microcheck_failures_total',
                        'Total micro-check failures in AkaQualia loop'
                    ),
                    'duration': Histogram(
                        'akaqualia_microcheck_duration_seconds',
                        'Micro-check duration in AkaQualia loop',
                        buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0]
                    )
                }
            except Exception as e:
                logger.debug(f"Failed to initialize microcheck metrics: {e}")
                _microcheck_metrics = {}
        return _microcheck_metrics

# Optional imports for full functionality (not needed for drift-only mode)
try:
    from core.symbolic_diagnostics.trace_repair_engine import TraceRepairEngine
except ImportError:
    TraceRepairEngine = None

try:
    from memory.core_memory.memory_collapse_verifier import MemoryCollapseVerifier
except ImportError:
    MemoryCollapseVerifier = None

logger = logging.getLogger(__name__)


@dataclass
class IntegrityProbe:
    """
    Probes the integrity of the symbolic core.
    """

    def __init__(
        self,
        drift_score_calculator: "DriftScoreCalculator",  # TODO: DriftScoreCalculator
        memory_collapse_verifier: "MemoryCollapseVerifier",
        trace_repair_engine: "TraceRepairEngine",
    ):
        self.drift_score_calculator = drift_score_calculator
        self.memory_collapse_verifier = memory_collapse_verifier
        self.trace_repair_engine = trace_repair_engine

        # Lazy import drift manager when feature flag is enabled
        self.drift_manager = None
        if os.environ.get('LUKHAS_EXPERIMENTAL') == '1':
            try:
                from monitoring.drift_manager import get_drift_manager
                self.drift_manager = get_drift_manager()
                logger.info("IntegrityProbe: Drift manager integration enabled")
            except ImportError:
                logger.debug("IntegrityProbe: Drift manager not available")

        # State tracking for drift calculations
        self.prev_state = {}
        self.curr_state = {}

    def run_consistency_check(self, state: Optional[dict[str, Any]] = None) -> bool:
        """
        Runs a consistency check on the symbolic core.

        When drift_manager is available and LUKHAS_EXPERIMENTAL=1, computes
        drift scores for ethical, memory, and identity dimensions and logs
        top contributing symbols.

        Args:
            state: Optional current state for drift calculation

        Returns:
            bool: True if all checks pass, False if any drift exceeds threshold
        """
        # #AINTEGRITY_CHECK
        # #ΛTRACE_VERIFIER
        # #ΛDRIFT_SCORE

        # Track micro-check performance
        check_start_time = time.perf_counter()
        metrics = _get_microcheck_metrics()
        if 'attempts' in metrics:
            metrics['attempts'].inc()

        # Default pass if no drift manager
        if not self.drift_manager:
            return True

        # Update state tracking
        if state:
            self.prev_state = self.curr_state.copy()
            self.curr_state = state

        # Skip if no previous state
        if not self.prev_state:
            logger.debug("IntegrityProbe: No previous state for drift calculation")
            return True

        try:
            # Calculate drift for each dimension
            all_pass = True
            drift_results = {}

            # Ethical drift
            if 'ethical' in self.prev_state and 'ethical' in self.curr_state:
                ethical_drift = self.drift_manager.compute(
                    'ethical',
                    self.prev_state['ethical'],
                    self.curr_state['ethical']
                )
                drift_results['ethical'] = ethical_drift
                logger.info(
                    f"IntegrityProbe: Ethical drift={ethical_drift['score']:.4f}, "
                    f"top_symbols={ethical_drift['top_symbols'][:3]}"
                )

                if ethical_drift['score'] > self.drift_manager.critical_threshold:
                    all_pass = False
                    self.drift_manager.on_exceed(
                        'ethical',
                        ethical_drift['score'],
                        {'probe': 'integrity', 'state': self.curr_state.get('ethical')}
                    )

            # Memory drift
            if 'memory' in self.prev_state and 'memory' in self.curr_state:
                memory_drift = self.drift_manager.compute(
                    'memory',
                    self.prev_state['memory'],
                    self.curr_state['memory']
                )
                drift_results['memory'] = memory_drift
                logger.info(
                    f"IntegrityProbe: Memory drift={memory_drift['score']:.4f}, "
                    f"top_symbols={memory_drift['top_symbols'][:3]}"
                )

                if memory_drift['score'] > self.drift_manager.critical_threshold:
                    all_pass = False
                    self.drift_manager.on_exceed(
                        'memory',
                        memory_drift['score'],
                        {'probe': 'integrity', 'state': self.curr_state.get('memory')}
                    )

            # Identity drift
            if 'identity' in self.prev_state and 'identity' in self.curr_state:
                identity_drift = self.drift_manager.compute(
                    'identity',
                    self.prev_state['identity'],
                    self.curr_state['identity']
                )
                drift_results['identity'] = identity_drift
                logger.info(
                    f"IntegrityProbe: Identity drift={identity_drift['score']:.4f}, "
                    f"top_symbols={identity_drift['top_symbols'][:3]}"
                )

                if identity_drift['score'] > self.drift_manager.critical_threshold:
                    all_pass = False
                    self.drift_manager.on_exceed(
                        'identity',
                        identity_drift['score'],
                        {'probe': 'integrity', 'state': self.curr_state.get('identity')}
                    )

            # Compute unified drift if we have all components
            if len(drift_results) >= 2:
                unified_drift = self.drift_manager.compute(
                    'unified',
                    self.prev_state,
                    self.curr_state
                )
                logger.info(
                    f"IntegrityProbe: Unified drift={unified_drift['score']:.4f}, "
                    f"top_symbols={unified_drift['top_symbols'][:5]}"
                )

                if unified_drift['score'] > self.drift_manager.critical_threshold:
                    all_pass = False
                    self.drift_manager.on_exceed(
                        'unified',
                        unified_drift['score'],
                        {'probe': 'integrity', 'results': drift_results}
                    )

            # --- Auto-repair trigger on critical drift (env-gated) ---
            try:
                _safe_threshold = float(os.getenv("DRIFT_SAFE_THRESHOLD", "0.15"))
            except Exception:
                _safe_threshold = 0.15

            if (not all_pass) and os.environ.get("LUKHAS_AUTOREPAIR_ENABLED", "1") == "1" and getattr(self, "drift_manager", None):
                try:
                    for _kind, _res in (drift_results or {}).items():
                        try:
                            _score = float(_res.get("score", 0.0))
                        except Exception:
                            _score = 0.0
                        if _score >= _safe_threshold:
                            _ctx = {
                                "source": "akaqualia_microcheck",
                                "band": "critical",
                                "top_symbols": _res.get("top_symbols", []),
                            }
                            try:
                                self.drift_manager.on_exceed(_kind, _score, _ctx)
                            except Exception as _e:
                                logger.warning(f"IntegrityProbe: on_exceed failed for kind={_kind}: {_e}")
                except Exception as _e_outer:
                    logger.debug(f"IntegrityProbe: auto-repair evaluation failed (non-fatal): {_e_outer}")

            # Record success/failure metrics
            metrics = _get_microcheck_metrics()
            if not all_pass and 'failures' in metrics:
                metrics['failures'].inc()
            if 'duration' in metrics:
                metrics['duration'].observe(time.perf_counter() - check_start_time)

            return all_pass

        except Exception as e:
            logger.error(f"IntegrityProbe: Error during drift calculation: {e}")

            # Record failure metrics
            metrics = _get_microcheck_metrics()
            if 'failures' in metrics:
                metrics['failures'].inc()
            if 'duration' in metrics:
                metrics['duration'].observe(time.perf_counter() - check_start_time)

            # Fail open - don't block on errors
            return True
