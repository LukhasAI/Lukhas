#!/usr/bin/env python3
"""
LUKHAS Consciousness Stream - Production Schema v1.0.0

Main consciousness coordination layer that orchestrates awareness monitoring,
reflection processing, dream cycles, and autonomous decision-making.

Implements the complete Constellation Framework consciousness pipeline with
T4/0.01% excellence standards and comprehensive observability.

Constellation Framework: Flow Star (🌊), Spark Star (⚡), Oracle Star (🔮)
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import asdict
from typing import Any, Dict, List, Optional

from opentelemetry import trace
from prometheus_client import Counter, Gauge, Histogram

from .auto_consciousness import AutoConsciousness
from .awareness_engine import AwarenessEngine
from .creativity_engine import CreativityEngine
from .dream_engine import DreamEngine

# Import LUKHAS reflection engine
from .reflection_engine import ReflectionEngine

# Import consciousness components
from .types import (
    AwarenessSnapshot,
    ConsciousnessMetrics,
    ConsciousnessState,
    CreativeTask,
    CreativitySnapshot,
    DecisionContext,
    DreamTrace,
    ReflectionReport,
    StatePhase,
)

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

# Prometheus metrics
consciousness_ticks_total = Counter(
    'lukhas_consciousness_ticks_total',
    'Total consciousness processing ticks',
    ['component']
)

consciousness_tick_latency_seconds = Histogram(
    'lukhas_consciousness_tick_latency_seconds',
    'Consciousness tick processing latency',
    ['component'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0]
)

consciousness_phase_duration_seconds = Histogram(
    'lukhas_consciousness_phase_duration_seconds',
    'Duration spent in each consciousness phase',
    ['component', 'phase'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

consciousness_level_gauge = Gauge(
    'lukhas_consciousness_level',
    'Current consciousness level',
    ['component']
)

consciousness_anomaly_rate = Gauge(
    'lukhas_consciousness_anomaly_rate',
    'Current anomaly detection rate',
    ['component']
)


class ConsciousnessStream:
    """
    Main consciousness coordination and processing stream.

    Orchestrates the complete consciousness pipeline with awareness monitoring,
    reflection processing, dream cycles, and autonomous decision-making.
    Implements T4/0.01% performance standards with comprehensive observability.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize consciousness stream with configuration."""
        self.config = config or {}
        self._component_id = "ConsciousnessStream"

        # Initialize Guardian integration if available
        if GUARDIAN_INTEGRATION_AVAILABLE and self.config.get("guardian_integration_enabled", True):
            guardian_config = GuardianValidationConfig(
                drift_threshold=0.15,  # AUDITOR_CHECKLIST.md requirement
                p95_target_ms=200.0,   # Conservative for Phase 3
                p99_target_ms=250.0,   # PHASE_MATRIX.md requirement
                enforcement_mode=self.config.get("guardian_enforcement_mode", "enforced"),
                gdpr_audit_enabled=True,
                constitutional_check_enabled=True
            )
            self.guardian_integration = ConsciousnessGuardianIntegration(config=guardian_config)
        else:
            self.guardian_integration = None

        # Initialize consciousness engines
        self.awareness_engine = AwarenessEngine(self.config.get("awareness", {}))
        self.dream_engine = DreamEngine(self.config.get("dream", {}))
        self.creativity_engine = CreativityEngine(
            config=self.config.get("creativity", {}),
            guardian_validator=self.config.get("guardian_validator")
        )
        self.auto_consciousness = AutoConsciousness(
            guardian_validator=self.config.get("guardian_validator")
        )

        # Initialize LUKHAS reflection engine
        self.reflection_engine = ReflectionEngine(
            memory_backend=self.config.get("memory_backend"),
            guardian_validator=self.config.get("guardian_validator"),
            guardian_integration=self.guardian_integration
        )

        # Consciousness state
        self._current_state = ConsciousnessState()
        self._state_history: List[ConsciousnessState] = []

        # Processing state
        self._is_running = False
        self._tick_count = 0
        self._last_tick_time = 0.0

        # Recent processing artifacts
        self._recent_awareness: Optional[AwarenessSnapshot] = None
        self._recent_reflection: Optional[ReflectionReport] = None
        self._recent_dream: Optional[DreamTrace] = None
        self._recent_creativity: Optional[CreativitySnapshot] = None
        self._recent_decision: Optional[DecisionContext] = None

        # Performance tracking
        self._tick_latencies: List[float] = []
        self._phase_durations: Dict[StatePhase, List[float]] = {
            phase: [] for phase in ["IDLE", "AWARE", "REFLECT", "CREATE", "DREAM", "DECIDE"]
        }

        # Signal processing
        self._signal_buffer: Dict[str, Any] = {}
        self._memory_events: List[Dict[str, Any]] = []

    async def start(self) -> None:
        """Start the consciousness processing stream."""
        if self._is_running:
            logger.warning("Consciousness stream already running")
            return

        logger.info("Starting LUKHAS Consciousness Stream")
        self._is_running = True
        self._last_tick_time = time.time()

        with tracer.start_as_current_span("consciousness_stream_start") as span:
            span.set_attribute("component", self._component_id)

            # Initialize all engines
            if self.reflection_engine:
                # Reflection engine may have its own initialization
                pass

            logger.info("Consciousness Stream started successfully")

    async def stop(self) -> None:
        """Stop the consciousness processing stream."""
        if not self._is_running:
            return

        logger.info("Stopping LUKHAS Consciousness Stream")
        self._is_running = False

        with tracer.start_as_current_span("consciousness_stream_stop") as span:
            span.set_attribute("component", self._component_id)
            span.set_attribute("total_ticks", self._tick_count)

            logger.info(f"Consciousness Stream stopped after {self._tick_count} ticks")

    async def tick(self, signals: Optional[Dict[str, Any]] = None) -> ConsciousnessMetrics:
        """
        Execute single consciousness processing tick.

        Args:
            signals: Optional external signals to process

        Returns:
            ConsciousnessMetrics with current system state
        """
        if not self._is_running:
            raise RuntimeError("Consciousness stream not running")

        tick_start_time = time.time()

        with tracer.start_as_current_span("consciousness_tick") as span:
            span.set_attribute("component", self._component_id)
            span.set_attribute("tick_number", self._tick_count)
            span.set_attribute("current_phase", self._current_state.phase)

            try:
                # Update signal buffer
                if signals:
                    self._signal_buffer.update(signals)

                # Execute consciousness phase processing
                await self._process_current_phase()

                # Determine next phase transition
                await self._update_consciousness_phase()

                # Generate metrics
                metrics = await self._generate_metrics()

                # Update performance tracking
                tick_latency = time.time() - tick_start_time
                self._update_performance_metrics(tick_latency)

                # Update Prometheus metrics
                consciousness_ticks_total.labels(component=self._component_id).inc()
                consciousness_tick_latency_seconds.labels(component=self._component_id).observe(tick_latency)
                consciousness_level_gauge.labels(component=self._component_id).set(self._current_state.level)

                self._tick_count += 1
                self._last_tick_time = time.time()

                span.set_attribute("tick_latency_ms", tick_latency * 1000)
                span.set_attribute("next_phase", self._current_state.phase)

                return metrics

            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                logger.error(f"Consciousness tick failed: {e}")
                raise

    async def _process_current_phase(self) -> None:
        """Process the current consciousness phase."""
        phase_start_time = time.time()

        if self._current_state.phase == "IDLE":
            await self._process_idle_phase()
        elif self._current_state.phase == "AWARE":
            await self._process_aware_phase()
        elif self._current_state.phase == "REFLECT":
            await self._process_reflect_phase()
        elif self._current_state.phase == "CREATE":
            await self._process_create_phase()
        elif self._current_state.phase == "DREAM":
            await self._process_dream_phase()
        elif self._current_state.phase == "DECIDE":
            await self._process_decide_phase()

        # Track phase duration
        phase_duration = time.time() - phase_start_time
        self._phase_durations[self._current_state.phase].append(phase_duration)
        consciousness_phase_duration_seconds.labels(
            component=self._component_id,
            phase=self._current_state.phase
        ).observe(phase_duration)

    async def _process_idle_phase(self) -> None:
        """Process IDLE phase - minimal processing."""
        # Clear recent processing artifacts
        self._recent_awareness = None
        self._recent_reflection = None
        self._recent_creativity = None
        self._recent_dream = None
        self._recent_decision = None

        # Light signal monitoring
        await asyncio.sleep(0.001)  # Minimal processing delay

    async def _process_aware_phase(self) -> None:
        """Process AWARE phase - awareness monitoring."""
        try:
            self._recent_awareness = await self.awareness_engine.update(
                self._current_state,
                self._signal_buffer
            )

            # Process awareness for memory events
            if self._recent_awareness.anomalies:
                for anomaly in self._recent_awareness.anomalies:
                    self._memory_events.append({
                        "type": "anomaly_detected",
                        "data": anomaly,
                        "timestamp": time.time()
                    })

        except Exception as e:
            logger.error(f"Awareness processing failed: {e}")
            self._recent_awareness = None

    async def _process_reflect_phase(self) -> None:
        """Process REFLECT phase - self-reflection."""
        try:
            # Update reflection engine with current state for drift analysis
            self.reflection_engine.update_state_history(self._current_state)

            # Perform comprehensive reflection analysis
            self._recent_reflection = await self.reflection_engine.reflect(
                consciousness_state=self._current_state,
                awareness_snapshot=self._recent_awareness,
                context={
                    "signal_buffer": self._signal_buffer,
                    "memory_events": self._memory_events[-10:],  # Recent memory events
                    "tick_count": self._tick_count
                }
            )

            # Add reflection results to memory events
            self._memory_events.append({
                "type": "reflection_completed",
                "data": asdict(self._recent_reflection),
                "timestamp": time.time()
            })

            # Log performance metrics
            if self._recent_reflection.reflection_duration_ms > 100:
                logger.warning(
                    f"Reflection exceeded 100ms target: {self._recent_reflection.reflection_duration_ms:.2f}ms"
                )

        except Exception as e:
            logger.error(f"Reflection processing failed: {e}")
            self._recent_reflection = None

    async def _process_create_phase(self) -> None:
        """Process CREATE phase - creative idea generation."""
        try:
            # Determine if creative processing is warranted
            creative_triggers = self._assess_creative_triggers()

            if creative_triggers["should_create"]:
                # Create creative task from current context
                creative_task = CreativeTask(
                    prompt=creative_triggers.get("prompt", "Generate creative insights"),
                    context={
                        "consciousness_state": asdict(self._current_state),
                        "awareness_data": asdict(self._recent_awareness) if self._recent_awareness else {},
                        "reflection_data": asdict(self._recent_reflection) if self._recent_reflection else {}
                    },
                    constraints=creative_triggers.get("constraints", []),
                    preferred_process=creative_triggers.get("process_type"),
                    imagination_mode=creative_triggers.get("imagination_mode", "conceptual"),
                    min_ideas=creative_triggers.get("min_ideas", 3),
                    seed_concepts=creative_triggers.get("seed_concepts", [])
                )

                # Generate creative ideas
                self._recent_creativity = await self.creativity_engine.generate_ideas(
                    creative_task,
                    self._current_state,
                    self._signal_buffer
                )

                # Add creativity results to memory events
                if self._recent_creativity and self._recent_creativity.ideas:
                    self._memory_events.append({
                        "type": "creativity_session",
                        "data": {
                            "ideas_generated": len(self._recent_creativity.ideas),
                            "novelty_score": self._recent_creativity.novelty_score,
                            "coherence_score": self._recent_creativity.coherence_score,
                            "flow_state": self._recent_creativity.flow_state
                        },
                        "timestamp": time.time()
                    })

        except Exception as e:
            logger.error(f"Creative processing failed: {e}")
            self._recent_creativity = None

    async def _process_dream_phase(self) -> None:
        """Process DREAM phase - memory consolidation."""
        try:
            # Trigger dream cycle if conditions are met
            memory_pressure = len(self._memory_events) / 1000.0  # Normalize to [0,1]

            if self.dream_engine.should_trigger_dream(memory_pressure):
                self._recent_dream = await self.dream_engine.process_cycle(
                    self._current_state,
                    self._memory_events.copy(),  # Pass copy to avoid modification
                    trigger_reason="consciousness_cycle"
                )

                # Clear processed memory events
                self._memory_events.clear()

        except Exception as e:
            logger.error(f"Dream processing failed: {e}")
            self._recent_dream = None

    async def _process_decide_phase(self) -> None:
        """Process DECIDE phase - autonomous decision-making."""
        try:
            self._recent_decision = await self.auto_consciousness.decide_and_act(
                consciousness_state=self._current_state,
                awareness_snapshot=self._recent_awareness,
                reflection_report=self._recent_reflection,
                dream_trace=self._recent_dream
            )

            # Add decision to memory events
            self._memory_events.append({
                "type": "decision_made",
                "data": {
                    "approved": self._recent_decision.guardian_approved,
                    "confidence": self._recent_decision.confidence_score,
                    "action_count": len(self._recent_decision.proposed_actions)
                },
                "timestamp": time.time()
            })

        except Exception as e:
            logger.error(f"Decision processing failed: {e}")
            self._recent_decision = None

    def _assess_creative_triggers(self) -> Dict[str, Any]:
        """Assess whether creative processing should be triggered."""

        triggers = {
            "should_create": False,
            "prompt": "Generate creative insights",
            "constraints": [],
            "process_type": None,
            "imagination_mode": "conceptual",
            "min_ideas": 3,
            "seed_concepts": []
        }

        # Trigger creativity if consciousness level is high
        if self._current_state.level > 0.7:
            triggers["should_create"] = True
            triggers["prompt"] = "High consciousness creative exploration"

        # Trigger if we have interesting anomalies from awareness
        if (self._recent_awareness and
            len(self._recent_awareness.anomalies) > 0 and
            any(a.get("severity") in ["medium", "high"] for a in self._recent_awareness.anomalies)):
            triggers["should_create"] = True
            triggers["prompt"] = "Creative solutions for detected anomalies"
            triggers["process_type"] = "convergent"

        # Trigger if reflection suggests creative opportunities
        if (self._recent_reflection and
            self._recent_reflection.coherence_score > 0.8):
            triggers["should_create"] = True
            triggers["prompt"] = "Creative insights from reflection"
            triggers["process_type"] = "divergent"

        # Extract seed concepts from signal buffer
        if self._signal_buffer:
            # Look for creative cues in signals
            creative_signals = [k for k in self._signal_buffer
                             if "creative" in k.lower() or "idea" in k.lower()]
            if creative_signals:
                triggers["should_create"] = True
                triggers["seed_concepts"] = creative_signals[:5]

        # Adjust imagination mode based on consciousness state
        if self._current_state.awareness_level in ["enhanced", "transcendent", "unified"]:
            triggers["imagination_mode"] = "abstract"
        elif self._current_state.emotional_tone == "curious":
            triggers["imagination_mode"] = "conceptual"

        return triggers

    async def _update_consciousness_phase(self) -> None:
        """Update consciousness phase based on current state and processing results."""

        # Guardian validation for state transitions if available
        if self.guardian_integration and self.config.get("guardian_state_validation", True):
            await self._validate_state_transition_with_guardian()

        # Simple phase transition logic
        current_phase = self._current_state.phase

        if current_phase == "IDLE":
            # Transition to AWARE if signals are present
            if self._signal_buffer or len(self._memory_events) > 0:
                self._current_state.phase = "AWARE"
                self._current_state.level = min(0.8, self._current_state.level + 0.1)

        elif current_phase == "AWARE":
            # Transition to REFLECT if awareness processing completed
            if self._recent_awareness:
                self._current_state.phase = "REFLECT"
                self._current_state.level = min(0.9, self._current_state.level + 0.1)

        elif current_phase == "REFLECT":
            # Transition to CREATE if creative triggers are present, otherwise DREAM/DECIDE
            creative_triggers = self._assess_creative_triggers()
            memory_pressure = len(self._memory_events) / 100.0

            if creative_triggers["should_create"] and self._current_state.level > 0.6:
                self._current_state.phase = "CREATE"
                self._current_state.level = min(0.95, self._current_state.level + 0.05)
            elif memory_pressure > 0.5 or self.dream_engine.should_trigger_dream():
                self._current_state.phase = "DREAM"
            else:
                self._current_state.phase = "DECIDE"

        elif current_phase == "CREATE":
            # Transition to DREAM if memory pressure is high, otherwise DECIDE
            memory_pressure = len(self._memory_events) / 100.0
            if memory_pressure > 0.5 or self.dream_engine.should_trigger_dream():
                self._current_state.phase = "DREAM"
            else:
                self._current_state.phase = "DECIDE"

        elif current_phase == "DREAM":
            # Transition to DECIDE after dream processing
            self._current_state.phase = "DECIDE"

        elif current_phase == "DECIDE":
            # Return to IDLE after decision processing
            self._current_state.phase = "IDLE"
            self._current_state.level = max(0.3, self._current_state.level - 0.05)

        # Update consciousness state timestamp
        self._current_state.ts_ms = int(time.time() * 1000)

        # Store state history
        self._state_history.append(ConsciousnessState(
            phase=self._current_state.phase,
            awareness_level=self._current_state.awareness_level,
            emotional_tone=self._current_state.emotional_tone,
            level=self._current_state.level,
            ts_ms=self._current_state.ts_ms,
            context=self._current_state.context.copy(),
            correlation_id=self._current_state.correlation_id
        ))

        # Keep recent history
        if len(self._state_history) > 1000:
            self._state_history = self._state_history[-500:]

        # Update Guardian baseline state if available
        if self.guardian_integration:
            self.guardian_integration.update_baseline_state(
                state=self._current_state,
                tenant=self.config.get("tenant", "default"),
                session_id=self.config.get("session_id")
            )

    async def _generate_metrics(self) -> ConsciousnessMetrics:
        """Generate comprehensive consciousness metrics."""

        # Calculate performance metrics
        p95_latency = 0.0
        if len(self._tick_latencies) > 5:
            sorted_latencies = sorted(self._tick_latencies[-100:])
            p95_idx = int(len(sorted_latencies) * 0.95)
            p95_latency = sorted_latencies[p95_idx] * 1000  # Convert to ms

        # Calculate tick rate
        tick_rate = 0.0
        if self._tick_count > 0 and self._last_tick_time > 0:
            elapsed = time.time() - (self._last_tick_time - (len(self._tick_latencies) * 0.01))
            tick_rate = len(self._tick_latencies) / max(elapsed, 1.0)

        # Calculate anomaly rate
        anomaly_count = 0
        if self._recent_awareness and self._recent_awareness.anomalies:
            anomaly_count = len(self._recent_awareness.anomalies)

        # Calculate coherence score
        coherence_score = 0.0
        if self._recent_reflection:
            coherence_score = self._recent_reflection.coherence_score

        # Calculate dream frequency
        dream_frequency = 0.0
        if hasattr(self.dream_engine, 'get_performance_stats'):
            dream_stats = self.dream_engine.get_performance_stats()
            if dream_stats.get("total_cycles", 0) > 0:
                dream_frequency = dream_stats["total_cycles"] / max(self._tick_count, 1)

        # Calculate Guardian approval rate
        guardian_approval_rate = 0.0
        if hasattr(self.auto_consciousness, 'get_performance_stats'):
            decision_stats = self.auto_consciousness.get_performance_stats()
            guardian_approval_rate = decision_stats.get("approval_rate", 0.0)

        # Calculate decision latency
        decision_latency = 0.0
        if hasattr(self.auto_consciousness, 'get_performance_stats'):
            decision_stats = self.auto_consciousness.get_performance_stats()
            decision_latency = decision_stats.get("average_latency_ms", 0.0)

        return ConsciousnessMetrics(
            reflection_p95_ms=p95_latency,
            awareness_update_rate=tick_rate,
            dream_cycle_frequency=dream_frequency,
            total_anomalies=anomaly_count,
            anomaly_rate_per_hour=anomaly_count * 3600 / max(self._tick_count, 1),
            coherence_score_avg=coherence_score,
            drift_ema_current=self._recent_awareness.drift_ema if self._recent_awareness else 0.0,
            system_load_factor=self._recent_awareness.load_factor if self._recent_awareness else 0.0,
            tick_rate_hz=tick_rate,
            decision_latency_ms=decision_latency,
            guardian_approval_rate=guardian_approval_rate
        )

    def _update_performance_metrics(self, tick_latency: float) -> None:
        """Update internal performance tracking."""
        self._tick_latencies.append(tick_latency)

        # Keep recent latencies for moving averages
        if len(self._tick_latencies) > 100:
            self._tick_latencies.pop(0)

        # Update anomaly rate gauge
        if self._recent_awareness:
            anomaly_rate = len(self._recent_awareness.anomalies) / max(self._tick_count, 1)
            consciousness_anomaly_rate.labels(component=self._component_id).set(anomaly_rate)

    def get_current_state(self) -> ConsciousnessState:
        """Get current consciousness state."""
        return self._current_state

    def get_recent_artifacts(self) -> Dict[str, Any]:
        """Get recent processing artifacts."""
        return {
            "awareness": asdict(self._recent_awareness) if self._recent_awareness else None,
            "reflection": asdict(self._recent_reflection) if self._recent_reflection else None,
            "creativity": asdict(self._recent_creativity) if self._recent_creativity else None,
            "dream": asdict(self._recent_dream) if self._recent_dream else None,
            "decision": asdict(self._recent_decision) if self._recent_decision else None
        }

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        avg_tick_latency = sum(self._tick_latencies) / len(self._tick_latencies) if self._tick_latencies else 0.0

        stats = {
            "consciousness_stream": {
                "total_ticks": self._tick_count,
                "average_tick_latency_ms": avg_tick_latency * 1000,
                "current_phase": self._current_state.phase,
                "consciousness_level": self._current_state.level,
                "state_history_length": len(self._state_history)
            }
        }

        # Add engine-specific stats
        if hasattr(self.awareness_engine, 'get_performance_stats'):
            stats["awareness_engine"] = self.awareness_engine.get_performance_stats()

        if hasattr(self.reflection_engine, 'get_performance_stats'):
            stats["reflection_engine"] = self.reflection_engine.get_performance_stats()

        if hasattr(self.creativity_engine, 'get_performance_stats'):
            stats["creativity_engine"] = self.creativity_engine.get_performance_stats()

        if hasattr(self.dream_engine, 'get_performance_stats'):
            stats["dream_engine"] = self.dream_engine.get_performance_stats()

        if hasattr(self.auto_consciousness, 'get_performance_stats'):
            stats["auto_consciousness"] = self.auto_consciousness.get_performance_stats()

        return stats

    async def _validate_state_transition_with_guardian(self) -> None:
        """Validate consciousness state transition with Guardian integration"""

        if not self.guardian_integration:
            return

        try:
            # Create validation context for state transition
            validation_context = create_validation_context(
                validation_type=GuardianValidationType.CONSCIOUSNESS_STATE_TRANSITION,
                consciousness_state=self._current_state,
                user_id=self.config.get("user_id"),
                session_id=self.config.get("session_id"),
                tenant=self.config.get("tenant", "default"),
                sensitive_operation=self._current_state.phase in ["DECIDE", "CREATE"]
            )

            # Add context from recent processing
            if self._recent_awareness:
                validation_context.awareness_snapshot = self._recent_awareness
                # Add risk indicators from awareness anomalies
                if self._recent_awareness.anomalies:
                    for anomaly in self._recent_awareness.anomalies:
                        if anomaly.get("severity") in ["high", "critical"]:
                            validation_context.risk_indicators.append(f"awareness_anomaly_{anomaly.get('type')}")

            if self._recent_reflection:
                validation_context.reflection_report = self._recent_reflection
                # Add risk indicators from reflection
                if self._recent_reflection.coherence_score < 0.3:
                    validation_context.risk_indicators.append("low_reflection_coherence")
                if self._recent_reflection.anomaly_count > 3:
                    validation_context.risk_indicators.append("high_reflection_anomalies")

            # Perform Guardian validation
            validation_result = await self.guardian_integration.validate_consciousness_operation(
                context=validation_context
            )

            # Handle validation results
            if not validation_result.is_approved():
                logger.warning(
                    f"Guardian denied consciousness state transition: {validation_result.reason} "
                    f"(confidence: {validation_result.confidence:.2f})"
                )

                # Add Guardian denial to memory events for tracking
                self._memory_events.append({
                    "type": "guardian_state_transition_denied",
                    "data": {
                        "reason": validation_result.reason,
                        "confidence": validation_result.confidence,
                        "validation_duration_ms": validation_result.validation_duration_ms,
                        "current_phase": self._current_state.phase,
                        "recommendations": validation_result.recommendations
                    },
                    "timestamp": time.time()
                })

                # In fail-closed mode, we could prevent the state transition
                # For now, we log and continue but track the denial

            else:
                logger.debug(
                    f"Guardian approved consciousness state transition "
                    f"(duration: {validation_result.validation_duration_ms:.2f}ms)"
                )

        except Exception as e:
            logger.error(f"Guardian state transition validation failed: {e}")
            # In fail-closed mode, log the error but continue operation
            # The Guardian integration handles fail-closed behavior internally

    async def reset_state(self) -> None:
        """Reset consciousness stream state for testing."""
        self._current_state = ConsciousnessState()
        self._state_history.clear()
        self._tick_count = 0
        self._tick_latencies.clear()
        self._signal_buffer.clear()
        self._memory_events.clear()

        # Reset engine states
        if hasattr(self.awareness_engine, 'reset_state'):
            self.awareness_engine.reset_state()
        if hasattr(self.reflection_engine, 'reset_state'):
            self.reflection_engine.reset_state()
        if hasattr(self.creativity_engine, 'reset_state'):
            await self.creativity_engine.reset_state()
        if hasattr(self.dream_engine, 'reset_state'):
            self.dream_engine.reset_state()
        if hasattr(self.auto_consciousness, 'reset_state'):
            self.auto_consciousness.reset_state()
        if hasattr(self.guardian_integration, 'reset_state'):
            await self.guardian_integration.reset_state()


# Export for public API
__all__ = ["ConsciousnessStream"]
