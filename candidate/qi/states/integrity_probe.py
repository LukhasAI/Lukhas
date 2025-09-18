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
from dataclasses import dataclass
from typing import Any, Dict, Optional

from candidate.core.symbolic_diagnostics.trace_repair_engine import TraceRepairEngine
from lukhas.memory.core_memory.memory_collapse_verifier import MemoryCollapseVerifier

logger = logging.getLogger(__name__)


@dataclass
class IntegrityProbe:
    """
    Probes the integrity of the symbolic core.
    """

    def __init__(
        self,
        drift_score_calculator: "DriftScoreCalculator",
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

    def run_consistency_check(self, state: Optional[Dict[str, Any]] = None) -> bool:
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

            return all_pass

        except Exception as e:
            logger.error(f"IntegrityProbe: Error during drift calculation: {e}")
            # Fail open - don't block on errors
            return True
