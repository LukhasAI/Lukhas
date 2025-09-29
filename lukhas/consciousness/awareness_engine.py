#!/usr/bin/env python3
"""
LUKHAS Consciousness AwarenessEngine - Production Schema v1.0.0

Implements real-time awareness monitoring with EMA drift tracking, load factor
calculation, and anomaly detection. Part of the Constellation Framework.

Constellation Framework: Flow Star (🌊)
"""

from __future__ import annotations
import time
from typing import Dict, Any, Optional, List
from opentelemetry import trace
from prometheus_client import Counter, Histogram, Gauge
import math

from .types import (
    ConsciousnessState, AwarenessSnapshot, DEFAULT_AWARENESS_CONFIG
)

tracer = trace.get_tracer(__name__)

# Prometheus metrics
awareness_updates_total = Counter(
    'lukhas_awareness_updates_total',
    'Total number of awareness updates',
    ['component']
)

awareness_latency_seconds = Histogram(
    'lukhas_awareness_latency_seconds',
    'Awareness update latency',
    ['component'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

awareness_drift_ema = Gauge(
    'lukhas_awareness_drift_ema',
    'Current EMA drift value',
    ['component']
)

awareness_load_factor = Gauge(
    'lukhas_awareness_load_factor',
    'Current system load factor',
    ['component']
)

awareness_anomaly_count = Counter(
    'lukhas_awareness_anomaly_count_total',
    'Total anomalies detected',
    ['component', 'severity']
)


class AwarenessEngine:
    """
    Real-time awareness monitoring engine with drift tracking.

    Processes consciousness state signals to generate awareness snapshots
    with EMA drift tracking, load factor calculation, and anomaly detection.
    Optimized for sub-100ms update cycles with comprehensive observability.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize awareness engine with configuration."""
        self.config = {**DEFAULT_AWARENESS_CONFIG, **(config or {})}
        self.drift_alpha = self.config["drift_alpha"]
        self.anomaly_threshold = self.config["anomaly_threshold"]
        self.load_smoothing_window = self.config["load_smoothing_window"]

        # Internal state
        self._drift_ema = 0.0
        self._previous_state: Optional[ConsciousnessState] = None
        self._load_history: List[float] = []
        self._update_count = 0
        self._component_id = "AwarenessEngine"

        # Performance tracking
        self._last_update_time = 0.0
        self._processing_times: List[float] = []

    async def update(
        self,
        state: ConsciousnessState,
        signals: Dict[str, Any]
    ) -> AwarenessSnapshot:
        """
        Generate awareness snapshot from consciousness state and signals.

        Args:
            state: Current consciousness state
            signals: Additional signal data for processing

        Returns:
            AwarenessSnapshot with drift, load, and anomaly data
        """
        start_time = time.time()

        with tracer.start_as_current_span("awareness_update") as span:
            span.set_attribute("component", self._component_id)
            span.set_attribute("state.phase", state.phase)
            span.set_attribute("state.level", state.level)

            try:
                snapshot = await self._process_awareness(state, signals)

                # Update metrics
                processing_time = (time.time() - start_time) * 1000
                self._update_performance_metrics(processing_time)

                awareness_updates_total.labels(component=self._component_id).inc()
                awareness_latency_seconds.labels(component=self._component_id).observe(
                    time.time() - start_time
                )
                awareness_drift_ema.labels(component=self._component_id).set(
                    snapshot.drift_ema
                )
                awareness_load_factor.labels(component=self._component_id).set(
                    snapshot.load_factor
                )

                span.set_attribute("snapshot.drift_ema", snapshot.drift_ema)
                span.set_attribute("snapshot.load_factor", snapshot.load_factor)
                span.set_attribute("snapshot.anomaly_count", len(snapshot.anomalies))
                span.set_attribute("processing_time_ms", processing_time)

                return snapshot

            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise

    async def _process_awareness(
        self,
        state: ConsciousnessState,
        signals: Dict[str, Any]
    ) -> AwarenessSnapshot:
        """Internal awareness processing logic."""

        # Calculate state delta if we have previous state
        state_delta = 0.0
        if self._previous_state:
            state_delta = self._calculate_state_delta(self._previous_state, state)

        # Update EMA drift tracking
        self._drift_ema = self._update_drift_ema(state_delta)

        # Calculate current load factor
        load_factor = self._calculate_load_factor(signals)

        # Calculate signal metrics
        signal_strength, signal_noise_ratio = self._calculate_signal_metrics(signals)

        # Create snapshot
        snapshot = AwarenessSnapshot(
            drift_ema=self._drift_ema,
            load_factor=load_factor,
            signal_strength=signal_strength,
            signal_noise_ratio=signal_noise_ratio,
            processing_time_ms=0.0  # Will be updated after processing
        )

        # Detect anomalies
        await self._detect_anomalies(snapshot, state, signals)

        # Update internal state
        self._previous_state = state
        self._update_count += 1

        return snapshot

    def _calculate_state_delta(
        self,
        previous: ConsciousnessState,
        current: ConsciousnessState
    ) -> float:
        """Calculate magnitude of state change between consciousness states."""

        # Phase change contributes to delta
        phase_delta = 1.0 if previous.phase != current.phase else 0.0

        # Level change (weighted)
        level_delta = abs(current.level - previous.level)

        # Awareness level change
        awareness_levels = ["minimal", "basic", "enhanced", "transcendent", "unified"]
        prev_idx = awareness_levels.index(previous.awareness_level)
        curr_idx = awareness_levels.index(current.awareness_level)
        awareness_delta = abs(curr_idx - prev_idx) / len(awareness_levels)

        # Combine deltas with weights
        total_delta = (phase_delta * 0.4) + (level_delta * 0.4) + (awareness_delta * 0.2)

        return total_delta

    def _update_drift_ema(self, state_delta: float) -> float:
        """Update exponential moving average for drift tracking."""
        if self._update_count == 0:
            return state_delta

        return (self.drift_alpha * state_delta) + ((1 - self.drift_alpha) * self._drift_ema)

    def _calculate_load_factor(self, signals: Dict[str, Any]) -> float:
        """Calculate system load factor from signals."""

        # Extract load indicators from signals
        processing_queue_size = signals.get("processing_queue_size", 0)
        active_threads = signals.get("active_threads", 1)
        memory_pressure = signals.get("memory_pressure", 0.0)
        cpu_utilization = signals.get("cpu_utilization", 0.0)

        # Normalize and combine load factors
        queue_load = min(processing_queue_size / 100.0, 1.0)  # Normalize to [0,1]
        thread_load = min(active_threads / 10.0, 1.0)  # Assume 10 as max normal

        # Weighted combination
        raw_load = (queue_load * 0.3) + (thread_load * 0.2) + (memory_pressure * 0.25) + (cpu_utilization * 0.25)

        # Apply smoothing window
        self._load_history.append(raw_load)
        if len(self._load_history) > self.load_smoothing_window:
            self._load_history.pop(0)

        return sum(self._load_history) / len(self._load_history)

    def _calculate_signal_metrics(self, signals: Dict[str, Any]) -> tuple[float, float]:
        """Calculate signal strength and signal-to-noise ratio."""

        # Signal strength based on number and quality of signals
        signal_count = len([k for k in signals.keys() if not k.startswith("_")])
        signal_strength = min(signal_count / 10.0, 1.0)  # Normalize to [0,1]

        # Simple noise calculation based on signal variability
        numeric_signals = [v for v in signals.values() if isinstance(v, (int, float))]
        if len(numeric_signals) > 1:
            mean_val = sum(numeric_signals) / len(numeric_signals)
            variance = sum((x - mean_val) ** 2 for x in numeric_signals) / len(numeric_signals)
            noise_level = math.sqrt(variance) if variance > 0 else 0.001
            signal_noise_ratio = signal_strength / noise_level if noise_level > 0 else 1.0
        else:
            signal_noise_ratio = 1.0

        return signal_strength, min(signal_noise_ratio, 10.0)  # Cap SNR

    async def _detect_anomalies(
        self,
        snapshot: AwarenessSnapshot,
        state: ConsciousnessState,
        signals: Dict[str, Any]
    ) -> None:
        """Detect and record anomalies in awareness data."""

        # High drift anomaly
        if snapshot.drift_ema > self.anomaly_threshold:
            severity = "high" if snapshot.drift_ema > 0.9 else "medium"
            snapshot.add_anomaly(
                "high_drift",
                severity,
                f"EMA drift {snapshot.drift_ema:.3f} exceeds threshold {self.anomaly_threshold}"
            )
            awareness_anomaly_count.labels(
                component=self._component_id,
                severity=severity
            ).inc()

        # High load anomaly
        if snapshot.load_factor > 0.8:
            severity = "critical" if snapshot.load_factor > 0.95 else "high"
            snapshot.add_anomaly(
                "high_load",
                severity,
                f"Load factor {snapshot.load_factor:.3f} indicates system stress"
            )
            awareness_anomaly_count.labels(
                component=self._component_id,
                severity=severity
            ).inc()

        # Low signal quality anomaly
        if snapshot.signal_noise_ratio < 0.5:
            snapshot.add_anomaly(
                "low_signal_quality",
                "medium",
                f"Signal-to-noise ratio {snapshot.signal_noise_ratio:.3f} below acceptable threshold"
            )
            awareness_anomaly_count.labels(
                component=self._component_id,
                severity="medium"
            ).inc()

        # Consciousness level anomalies
        if state.level < 0.1:
            snapshot.add_anomaly(
                "low_consciousness",
                "medium",
                f"Consciousness level {state.level:.3f} critically low"
            )
            awareness_anomaly_count.labels(
                component=self._component_id,
                severity="medium"
            ).inc()
        elif state.level > 0.98:
            snapshot.add_anomaly(
                "consciousness_saturation",
                "low",
                f"Consciousness level {state.level:.3f} near saturation"
            )
            awareness_anomaly_count.labels(
                component=self._component_id,
                severity="low"
            ).inc()

    def _update_performance_metrics(self, processing_time_ms: float) -> None:
        """Update internal performance tracking."""
        self._processing_times.append(processing_time_ms)

        # Keep only recent processing times for moving averages
        if len(self._processing_times) > 100:
            self._processing_times.pop(0)

        self._last_update_time = time.time()

    def get_performance_stats(self) -> Dict[str, float]:
        """Get current performance statistics."""
        if not self._processing_times:
            return {
                "mean_processing_time_ms": 0.0,
                "p95_processing_time_ms": 0.0,
                "update_rate_hz": 0.0
            }

        sorted_times = sorted(self._processing_times)
        p95_idx = int(len(sorted_times) * 0.95)

        return {
            "mean_processing_time_ms": sum(self._processing_times) / len(self._processing_times),
            "p95_processing_time_ms": sorted_times[p95_idx] if p95_idx < len(sorted_times) else sorted_times[-1],
            "update_rate_hz": len(self._processing_times) / max((time.time() - self._last_update_time), 1.0),
            "drift_ema_current": self._drift_ema,
            "total_updates": self._update_count
        }

    def reset_state(self) -> None:
        """Reset internal state for testing or reconfiguration."""
        self._drift_ema = 0.0
        self._previous_state = None
        self._load_history.clear()
        self._update_count = 0
        self._processing_times.clear()


# Export for public API
__all__ = ["AwarenessEngine"]