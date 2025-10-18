#!/usr/bin/env python3
"""
SelfReflectionEngine - Production-grade metacognition layer for LUKHAS AI

Implements real-time introspection with per-tick reflection, coherence tracking,
and <10ms p95 reflection cycles. Integrates with consciousness state and provides
anomalies detection with comprehensive observability.

Conforms to LUKHAS Constellation Framework Flow Star (🌊) specifications.
"""

import asyncio
import os
import statistics
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Protocol

from consciousness.systems.state import ConsciousnessState
from core.common.logger import get_logger

# Feature flag configuration
REFLECTION_ENABLED = os.getenv("CONSC_REFLECTION_ENABLED", "1").lower() in ("1", "true", "on")
REFLECTION_CANARY_PERCENT = int(os.getenv("CONSC_REFLECTION_CANARY_PERCENT", "25"))

# Performance targets from PHASES.md
REFLECTION_P95_TARGET_MS = 10.0
REFLECTION_CV_TARGET = 0.10  # Coefficient of variation <10%
COHERENCE_THRESHOLD = 0.85
DRIFT_EMA_ALPHA = 0.3


# Optional OpenTelemetry support for observability
try:
    from opentelemetry import metrics, trace  # noqa: F401  # TODO: opentelemetry.metrics; conside...
    from opentelemetry.metrics import get_meter
    from opentelemetry.trace import Status, StatusCode  # noqa: F401  # TODO: opentelemetry.trace.Status; co...
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False


@dataclass
class ReflectionReport:
    """
    Versioned reflection report with coherence scoring and anomaly detection.
    Implements schema versioning for forward compatibility.
    """
    schema_version: str = "1.0.0"
    timestamp: float = field(default_factory=time.time)
    correlation_id: str = ""

    # Core reflection metrics
    coherence_score: float = 0.0
    drift_ema: float = 0.0
    state_delta_magnitude: float = 0.0

    # Anomaly detection
    anomalies: List[Dict[str, Any]] = field(default_factory=list)
    anomaly_count: int = 0

    # Performance metrics
    reflection_duration_ms: float = 0.0
    processing_stage: str = "unknown"

    # Consciousness context
    consciousness_level: float = 0.0
    awareness_type: str = "basic"
    emotional_tone: str = "neutral"

    def add_anomaly(self, anomaly_type: str, severity: str, details: str):
        """Add detected anomaly to report"""
        anomaly = {
            "type": anomaly_type,
            "severity": severity,
            "details": details,
            "timestamp": time.time()
        }
        self.anomalies.append(anomaly)
        self.anomaly_count = len(self.anomalies)


class ContextProvider(Protocol):
    """Protocol for context providers (memory, emotion readers)"""
    async def get_context(self) -> Dict[str, Any]:
        """Retrieve context data for reflection"""
        ...


class SelfReflectionEngine:
    """
    Production-grade metacognition layer with real-time introspection.

    Features:
    - Per-tick reflection with <10ms p95 latency
    - Coherence tracking with state drift detection
    - Anomaly detection and reporting
    - Context-aware reflection via injected providers
    - Comprehensive observability (OTEL spans + Prometheus metrics)
    - Feature flag controlled deployment

    Constellation Framework: Flow Star (🌊) - Real-time consciousness processing
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = get_logger(__name__, "CONSCIOUSNESS")
        self.is_initialized = False
        self.status = "inactive"

        # Context providers (injected during init)
        self.context_providers: List[ContextProvider] = []

        # State tracking for coherence analysis
        self.previous_state: Optional[ConsciousnessState] = None
        self.drift_ema = 0.0
        self.reflection_history: List[float] = []

        # Performance monitoring
        self.performance_buffer: List[float] = []
        self.anomaly_counter = 0

        # Observability setup
        self._setup_observability()

    def _setup_observability(self):
        """Initialize OTEL spans and Prometheus metrics"""
        if OTEL_AVAILABLE:
            self.tracer = trace.get_tracer(__name__)
            self.meter = get_meter(__name__)

            # Prometheus metrics as specified in PHASES.md
            self.reflection_latency_histogram = self.meter.create_histogram(
                name="lukhas_reflection_latency_seconds",
                description="Duration of reflection cycles",
                unit="s"
            )

            self.anomalies_counter = self.meter.create_counter(
                name="lukhas_reflection_anomalies_total",
                description="Total reflection anomalies detected",
                unit="1"
            )

            self.coherence_gauge = self.meter.create_gauge(
                name="lukhas_reflection_coherence_score",
                description="Current consciousness coherence score"
            )
        else:
            self.tracer = None
            self.meter = None
            self.logger.warning("OTEL not available - reflection observability disabled")

    async def init(self, context_providers: List[ContextProvider]) -> bool:
        """
        Initialize reflection engine with context providers.

        Args:
            context_providers: List of context providers (memory/emotion readers)

        Returns:
            True if initialization successful
        """
        try:
            if not REFLECTION_ENABLED:
                self.logger.info("Reflection engine disabled by feature flag")
                self.status = "disabled"
                return True

            self.logger.info("Initializing SelfReflectionEngine")

            # Inject context providers
            self.context_providers = context_providers

            # Initialize drift tracking
            self.drift_ema = 0.0
            self.reflection_history.clear()
            self.performance_buffer.clear()

            # Setup complete
            self.is_initialized = True
            self.status = "active"

            self.logger.info(
                f"SelfReflectionEngine initialized with {len(context_providers)} context providers"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize SelfReflectionEngine: {e}")
            self.status = "error"
            return False

    async def reflect(self, state: ConsciousnessState) -> ReflectionReport:
        """
        Perform real-time reflection on consciousness state.

        Implements per-tick reflection with coherence tracking and anomaly detection.
        Target: <10ms p95 latency, CV<10%

        Args:
            state: Current consciousness state to analyze

        Returns:
            ReflectionReport with coherence analysis and anomalies
        """
        if not self.is_initialized or self.status != "active":
            return ReflectionReport(
                correlation_id=f"reflection_{int(time.time() * 1000)}",
                anomalies=[{"type": "engine_error", "severity": "high",
                          "details": "Engine not initialized", "timestamp": time.time()}]
            )

        start_time = time.perf_counter()
        correlation_id = f"reflection_{int(time.time() * 1000000)}"

        # OTEL span for tracing
        span_context = self._start_reflection_span(correlation_id, state)

        try:
            with span_context:
                # Generate reflection report
                report = await self._generate_reflection_report(state, correlation_id)

                # Record performance metrics
                duration_ms = (time.perf_counter() - start_time) * 1000
                report.reflection_duration_ms = duration_ms

                # Update performance tracking
                self._update_performance_metrics(duration_ms, report)

                # Record observability metrics
                self._record_reflection_metrics(duration_ms, report)

                return report

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            self.logger.error(f"Reflection failed after {duration_ms:.2f}ms: {e}")

            error_report = ReflectionReport(
                correlation_id=correlation_id,
                reflection_duration_ms=duration_ms
            )
            error_report.add_anomaly("reflection_error", "critical", str(e))

            return error_report

    @contextmanager
    def _start_reflection_span(self, correlation_id: str, state: ConsciousnessState):
        """Start OTEL span for reflection tracing"""
        if self.tracer:
            with self.tracer.start_as_current_span(
                "consciousness.reflect",
                attributes={
                    "reflection.correlation_id": correlation_id,
                    "consciousness.level": state.level,
                    "consciousness.awareness_type": state.awareness_type,
                    "consciousness.emotional_tone": state.emotional_tone,
                    "lane": os.getenv("LUKHAS_LANE", "experimental")
                }
            ) as span:
                yield span
        else:
            yield None

    async def _generate_reflection_report(self, state: ConsciousnessState, correlation_id: str) -> ReflectionReport:
        """Generate comprehensive reflection report with coherence analysis"""
        report = ReflectionReport(
            correlation_id=correlation_id,
            consciousness_level=state.level,
            awareness_type=state.awareness_type,
            emotional_tone=state.emotional_tone
        )

        # Calculate state delta if we have previous state
        if self.previous_state:
            delta = self._calculate_state_delta(self.previous_state, state)
            report.state_delta_magnitude = delta

            # Update drift EMA
            self.drift_ema = (DRIFT_EMA_ALPHA * delta) + ((1 - DRIFT_EMA_ALPHA) * self.drift_ema)
            report.drift_ema = self.drift_ema

            # Calculate coherence score
            report.coherence_score = self._calculate_coherence_score(delta)

            # Detect anomalies
            await self._detect_anomalies(report, state)
        else:
            # First reflection - baseline establishment
            report.coherence_score = 1.0
            report.drift_ema = 0.0

        # Store current state for next reflection
        self.previous_state = state

        # Gather context from providers
        context_data = await self._gather_context()
        if context_data:
            # Use context to enhance reflection (placeholder for future enhancement)
            pass

        return report

    def _calculate_state_delta(self, prev_state: ConsciousnessState, curr_state: ConsciousnessState) -> float:
        """Calculate magnitude of state change between reflections"""
        level_delta = abs(curr_state.level - prev_state.level)

        # Simple awareness type change detection (could be enhanced with embeddings)
        awareness_delta = 0.1 if curr_state.awareness_type != prev_state.awareness_type else 0.0

        # Emotional tone change detection
        emotion_delta = 0.1 if curr_state.emotional_tone != prev_state.emotional_tone else 0.0

        # Combined delta magnitude
        return level_delta + awareness_delta + emotion_delta

    def _calculate_coherence_score(self, delta: float) -> float:
        """Calculate coherence score based on state stability"""
        # Higher coherence when state changes are smaller and gradual
        if delta < 0.05:  # Very stable
            return 0.95 + (0.05 - delta)  # 0.95-1.0 range
        elif delta < 0.2:  # Moderate change
            return 0.85 + (0.2 - delta) * 0.5  # 0.85-0.95 range
        else:  # Large change
            return max(0.3, 0.85 - (delta - 0.2))  # 0.3-0.85 range

    async def _detect_anomalies(self, report: ReflectionReport, state: ConsciousnessState):
        """Detect anomalies in consciousness state and reflection patterns"""
        # Coherence threshold violation
        if report.coherence_score < COHERENCE_THRESHOLD:
            report.add_anomaly(
                "low_coherence", "medium",
                f"Coherence score {report.coherence_score:.3f} below threshold {COHERENCE_THRESHOLD}"
            )

        # Excessive drift detection
        if report.drift_ema > 0.5:
            report.add_anomaly(
                "excessive_drift", "high",
                f"Drift EMA {report.drift_ema:.3f} indicates unstable consciousness"
            )

        # Performance anomaly detection
        if len(self.performance_buffer) >= 10:
            recent_latencies = self.performance_buffer[-10:]
            avg_latency = statistics.mean(recent_latencies)
            if avg_latency > REFLECTION_P95_TARGET_MS:
                report.add_anomaly(
                    "performance_degradation", "medium",
                    f"Average latency {avg_latency:.2f}ms exceeds target {REFLECTION_P95_TARGET_MS}ms"
                )

        # State level anomalies
        if state.level > 1.0 or state.level < 0.0:
            report.add_anomaly(
                "invalid_consciousness_level", "critical",
                f"Consciousness level {state.level} outside valid range [0.0, 1.0]"
            )

    async def _gather_context(self) -> Dict[str, Any]:
        """Gather context from injected providers for enhanced reflection"""
        context = {}

        for provider in self.context_providers:
            try:
                provider_context = await provider.get_context()
                context.update(provider_context)
            except Exception as e:
                self.logger.warning(f"Context provider failed: {e}")

        return context

    def _update_performance_metrics(self, duration_ms: float, report: ReflectionReport):
        """Update performance tracking buffers"""
        # Keep rolling window of performance metrics
        self.performance_buffer.append(duration_ms)
        if len(self.performance_buffer) > 100:  # Keep last 100 measurements
            self.performance_buffer.pop(0)

        # Track anomaly count
        if report.anomaly_count > 0:
            self.anomaly_counter += report.anomaly_count

    def _record_reflection_metrics(self, duration_ms: float, report: ReflectionReport):
        """Record metrics to Prometheus histograms and counters"""
        if not OTEL_AVAILABLE or not self.meter:
            return

        lane = os.getenv("LUKHAS_LANE", "experimental")

        # Record latency histogram
        self.reflection_latency_histogram.record(
            duration_ms / 1000.0,  # Convert to seconds
            attributes={
                "lane": lane,
                "awareness_type": report.awareness_type,
                "within_slo": str(duration_ms <= REFLECTION_P95_TARGET_MS).lower()
            }
        )

        # Record anomalies counter
        if report.anomaly_count > 0:
            self.anomalies_counter.add(
                report.anomaly_count,
                attributes={
                    "lane": lane,
                    "awareness_type": report.awareness_type
                }
            )

        # Record coherence gauge
        if hasattr(self, 'coherence_gauge'):
            self.coherence_gauge.set(
                report.coherence_score,
                attributes={
                    "lane": lane,
                    "awareness_type": report.awareness_type
                }
            )

    async def validate(self) -> bool:
        """Validate reflection engine health and performance compliance"""
        try:
            if not self.is_initialized or self.status == "disabled":
                return True  # Disabled engines are considered valid

            if self.status != "active":
                return False

            # Performance validation
            if len(self.performance_buffer) >= 10:
                recent_latencies = self.performance_buffer[-10:]
                p95_latency = statistics.quantiles(recent_latencies, n=20)[18]  # 95th percentile

                if p95_latency > REFLECTION_P95_TARGET_MS:
                    self.logger.warning(
                        f"Reflection p95 latency {p95_latency:.2f}ms exceeds target {REFLECTION_P95_TARGET_MS}ms"
                    )
                    return False

                # Coefficient of variation check
                if len(recent_latencies) > 5:
                    cv = statistics.stdev(recent_latencies) / statistics.mean(recent_latencies)
                    if cv > REFLECTION_CV_TARGET:
                        self.logger.warning(
                            f"Reflection CV {cv:.3f} exceeds target {REFLECTION_CV_TARGET}"
                        )
                        return False

            return True

        except Exception as e:
            self.logger.error(f"Validation failed: {e}")
            return False

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics for monitoring"""
        if not self.performance_buffer:
            return {"status": "no_data"}

        latencies = self.performance_buffer[-50:]  # Last 50 measurements

        stats = {
            "sample_count": len(latencies),
            "mean_latency_ms": statistics.mean(latencies),
            "median_latency_ms": statistics.median(latencies),
            "anomaly_count_total": self.anomaly_counter,
            "drift_ema": self.drift_ema,
            "status": self.status
        }

        if len(latencies) >= 5:
            stats["p95_latency_ms"] = statistics.quantiles(latencies, n=20)[18]
            stats["cv"] = statistics.stdev(latencies) / statistics.mean(latencies)
            stats["within_slo"] = stats["p95_latency_ms"] <= REFLECTION_P95_TARGET_MS

        return stats

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive reflection engine status"""
        base_status = {
            "component": "SelfReflectionEngine",
            "category": "consciousness",
            "status": self.status,
            "initialized": self.is_initialized,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "feature_enabled": REFLECTION_ENABLED,
            "context_providers": len(self.context_providers)
        }

        # Add performance stats if available
        if self.status == "active":
            base_status.update(self.get_performance_stats())

        return base_status

    async def shutdown(self):
        """Shutdown the reflection engine gracefully"""
        self.logger.info("Shutting down SelfReflectionEngine")
        self.status = "inactive"
        self.is_initialized = False

        # Clear tracking data
        self.previous_state = None
        self.reflection_history.clear()
        self.performance_buffer.clear()
        self.context_providers.clear()


# Factory functions
def create_reflection_engine(config: Optional[Dict[str, Any]] = None) -> SelfReflectionEngine:
    """Create and return a reflection engine instance"""
    return SelfReflectionEngine(config)


async def create_and_initialize_reflection_engine(
    config: Optional[Dict[str, Any]] = None,
    context_providers: Optional[List[ContextProvider]] = None
) -> SelfReflectionEngine:
    """Create, initialize and return a reflection engine instance"""
    engine = SelfReflectionEngine(config)
    await engine.init(context_providers or [])
    return engine


if __name__ == "__main__":
    # Example usage and basic functionality test
    import asyncio

    async def main():
        print("Testing SelfReflectionEngine...")

        # Create test consciousness state
        test_state = ConsciousnessState(
            level=0.8,
            awareness_type="enhanced",
            emotional_tone="positive"
        )
        await test_state.initialize()

        # Create and initialize reflection engine
        engine = SelfReflectionEngine()
        success = await engine.init([])
        print(f"Initialization: {'success' if success else 'failed'}")

        if success and engine.status == "active":
            # Perform reflection
            report = await engine.reflect(test_state)
            print(f"Reflection completed: {report.correlation_id}")
            print(f"Coherence: {report.coherence_score:.3f}")
            print(f"Duration: {report.reflection_duration_ms:.2f}ms")
            print(f"Anomalies: {report.anomaly_count}")

            # Check performance stats
            stats = engine.get_performance_stats()
            print(f"Performance stats: {stats}")

            # Validate
            valid = await engine.validate()
            print(f"Validation: {'passed' if valid else 'failed'}")

        # Get status
        status = engine.get_status()
        print(f"Final status: {status['status']}")

        # Shutdown
        await engine.shutdown()
        print("Shutdown complete")

    asyncio.run(main())


# Module exports
__all__ = [
    "SelfReflectionEngine",
    "ReflectionReport",
    "ContextProvider",
    "create_reflection_engine",
    "create_and_initialize_reflection_engine",
    "REFLECTION_ENABLED",
    "REFLECTION_P95_TARGET_MS"
]
