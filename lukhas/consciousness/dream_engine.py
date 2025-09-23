#!/usr/bin/env python3
"""
LUKHAS Consciousness DreamEngine - Production Schema v1.0.0

Implements memory consolidation and pattern discovery through dream cycles.
Uses finite state machine for phase transitions: IDLE→ENTERING→DREAMING→EXITING.

Constellation Framework: Flow Star (🌊)
"""

from __future__ import annotations
import time
import asyncio
import random
from typing import Dict, Any, Optional, List, Set
from opentelemetry import trace
from prometheus_client import Counter, Histogram, Gauge, Enum
from enum import Enum as PyEnum

from .types import (
    ConsciousnessState, DreamTrace, DreamPhase,
    DEFAULT_DREAM_CONFIG
)

tracer = trace.get_tracer(__name__)

# Prometheus metrics
dream_cycles_total = Counter(
    'lukhas_dream_cycles_total',
    'Total number of dream cycles completed',
    ['component', 'reason']
)

dream_phase_duration_seconds = Histogram(
    'lukhas_dream_phase_duration_seconds',
    'Duration of dream phases',
    ['component', 'phase'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

dream_phase_current = Enum(
    'lukhas_dream_phase_current',
    'Current dream phase',
    ['component'],
    states=['IDLE', 'ENTERING', 'DREAMING', 'EXITING']
)

dream_memory_events_processed = Counter(
    'lukhas_dream_memory_events_processed_total',
    'Total memory events processed during dreams',
    ['component']
)

dream_patterns_discovered = Counter(
    'lukhas_dream_patterns_discovered_total',
    'Total patterns discovered during dreams',
    ['component']
)

dream_consolidation_ratio = Gauge(
    'lukhas_dream_consolidation_ratio',
    'Memory compression ratio achieved',
    ['component']
)


class DreamState(PyEnum):
    """Internal dream state tracking."""
    IDLE = "IDLE"
    ENTERING = "ENTERING"
    DREAMING = "DREAMING"
    EXITING = "EXITING"


class DreamEngine:
    """
    Memory consolidation and pattern discovery through dream cycles.

    Implements finite state machine for dream processing with memory
    consolidation, motif discovery, and creative synthesis. Optimized
    for sub-50ms dream cycles with comprehensive memory integration.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize dream engine with configuration."""
        self.config = {**DEFAULT_DREAM_CONFIG, **(config or {})}
        self.max_duration_ms = self.config["max_duration_ms"]
        self.consolidation_threshold = self.config["consolidation_threshold"]
        self.pattern_discovery_enabled = self.config["pattern_discovery_enabled"]

        # FSM state
        self._current_phase: DreamState = DreamState.IDLE
        self._phase_start_time = 0.0
        self._dream_session_id: Optional[str] = None
        self._component_id = "DreamEngine"

        # Memory processing state
        self._memory_buffer: List[Dict[str, Any]] = []
        self._discovered_motifs: Set[str] = set()
        self._association_graph: Dict[str, List[str]] = {}
        self._consolidation_count = 0

        # Performance tracking
        self._dream_cycles_completed = 0
        self._total_processing_time = 0.0
        self._last_consolidation_time = 0.0

    async def process_cycle(
        self,
        state: ConsciousnessState,
        memory_events: List[Dict[str, Any]],
        trigger_reason: str = "scheduled"
    ) -> DreamTrace:
        """
        Execute complete dream cycle with FSM phase transitions.

        Args:
            state: Current consciousness state
            memory_events: Memory events to process
            trigger_reason: Reason for triggering dream cycle

        Returns:
            DreamTrace with consolidation artifacts and metrics
        """
        cycle_start_time = time.time()

        with tracer.start_as_current_span("dream_cycle") as span:
            span.set_attribute("component", self._component_id)
            span.set_attribute("trigger_reason", trigger_reason)
            span.set_attribute("memory_events_count", len(memory_events))

            try:
                # Initialize dream trace
                dream_trace = DreamTrace(
                    reason=trigger_reason,
                    memory_events_processed=len(memory_events)
                )

                # Execute FSM transitions
                await self._transition_to_entering(dream_trace)
                await self._transition_to_dreaming(dream_trace, state, memory_events)
                await self._transition_to_exiting(dream_trace)
                await self._transition_to_idle(dream_trace)

                # Calculate final metrics
                dream_trace.duration_ms = (time.time() - cycle_start_time) * 1000
                dream_trace.consolidation_count = self._consolidation_count

                # Update Prometheus metrics
                dream_cycles_total.labels(
                    component=self._component_id,
                    reason=trigger_reason
                ).inc()

                dream_memory_events_processed.labels(
                    component=self._component_id
                ).inc(len(memory_events))

                dream_patterns_discovered.labels(
                    component=self._component_id
                ).inc(len(dream_trace.top_k_motifs))

                dream_consolidation_ratio.labels(
                    component=self._component_id
                ).set(dream_trace.compression_ratio)

                # Update performance tracking
                self._dream_cycles_completed += 1
                self._total_processing_time += dream_trace.duration_ms

                span.set_attribute("dream_trace.duration_ms", dream_trace.duration_ms)
                span.set_attribute("dream_trace.consolidation_count", dream_trace.consolidation_count)
                span.set_attribute("dream_trace.compression_ratio", dream_trace.compression_ratio)

                return dream_trace

            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                # Ensure we return to IDLE on error
                await self._force_transition_to_idle()
                raise

    async def _transition_to_entering(self, dream_trace: DreamTrace) -> None:
        """Transition from IDLE to ENTERING phase."""
        phase_start = time.time()
        self._current_phase = DreamState.ENTERING
        self._phase_start_time = phase_start
        dream_trace.phase = "ENTERING"

        # Generate unique dream session ID
        self._dream_session_id = f"dream_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"
        dream_trace.dream_id = self._dream_session_id

        # Update metrics
        dream_phase_current.labels(component=self._component_id).state("ENTERING")

        # Minimal entering phase processing
        await asyncio.sleep(0.001)  # Brief transition delay

        phase_duration = time.time() - phase_start
        dream_phase_duration_seconds.labels(
            component=self._component_id,
            phase="ENTERING"
        ).observe(phase_duration)

    async def _transition_to_dreaming(
        self,
        dream_trace: DreamTrace,
        state: ConsciousnessState,
        memory_events: List[Dict[str, Any]]
    ) -> None:
        """Transition from ENTERING to DREAMING phase."""
        phase_start = time.time()
        self._current_phase = DreamState.DREAMING
        self._phase_start_time = phase_start
        dream_trace.phase = "DREAMING"

        # Update metrics
        dream_phase_current.labels(component=self._component_id).state("DREAMING")

        # Core dream processing
        await self._process_memory_consolidation(dream_trace, memory_events)
        await self._discover_patterns(dream_trace, state)
        await self._generate_associations(dream_trace)
        await self._calculate_compression_metrics(dream_trace, memory_events)

        # Ensure we don't exceed max duration
        elapsed_ms = (time.time() - phase_start) * 1000
        if elapsed_ms > self.max_duration_ms:
            # Gracefully truncate processing
            dream_trace.add_association("truncation", {"reason": "max_duration_exceeded", "elapsed_ms": elapsed_ms})

        phase_duration = time.time() - phase_start
        dream_phase_duration_seconds.labels(
            component=self._component_id,
            phase="DREAMING"
        ).observe(phase_duration)

    async def _transition_to_exiting(self, dream_trace: DreamTrace) -> None:
        """Transition from DREAMING to EXITING phase."""
        phase_start = time.time()
        self._current_phase = DreamState.EXITING
        self._phase_start_time = phase_start
        dream_trace.phase = "EXITING"

        # Update metrics
        dream_phase_current.labels(component=self._component_id).state("EXITING")

        # Finalize dream artifacts
        await self._finalize_dream_artifacts(dream_trace)

        phase_duration = time.time() - phase_start
        dream_phase_duration_seconds.labels(
            component=self._component_id,
            phase="EXITING"
        ).observe(phase_duration)

    async def _transition_to_idle(self, dream_trace: DreamTrace) -> None:
        """Transition from EXITING to IDLE phase."""
        phase_start = time.time()
        self._current_phase = DreamState.IDLE
        self._phase_start_time = phase_start
        dream_trace.phase = "IDLE"

        # Update metrics
        dream_phase_current.labels(component=self._component_id).state("IDLE")

        # Reset session state
        self._dream_session_id = None
        self._last_consolidation_time = time.time()

        phase_duration = time.time() - phase_start
        dream_phase_duration_seconds.labels(
            component=self._component_id,
            phase="IDLE"
        ).observe(phase_duration)

    async def _force_transition_to_idle(self) -> None:
        """Force transition to IDLE on error conditions."""
        self._current_phase = DreamState.IDLE
        self._dream_session_id = None
        dream_phase_current.labels(component=self._component_id).state("IDLE")

    async def _process_memory_consolidation(
        self,
        dream_trace: DreamTrace,
        memory_events: List[Dict[str, Any]]
    ) -> None:
        """Process memory events for consolidation."""

        # Add new events to buffer
        self._memory_buffer.extend(memory_events)

        # Process consolidation if threshold reached
        if len(self._memory_buffer) >= self.consolidation_threshold:
            # Simulate memory consolidation processing
            consolidated_count = min(len(self._memory_buffer), self.consolidation_threshold)

            # Keep most recent events, consolidate older ones
            keep_recent = self._memory_buffer[-50:]  # Keep recent 50 events
            to_consolidate = self._memory_buffer[:-50]  # Consolidate older events

            # Simple consolidation: group similar events
            consolidated_events = await self._consolidate_similar_events(to_consolidate)

            # Update buffer with consolidated results
            self._memory_buffer = keep_recent + consolidated_events
            self._consolidation_count += consolidated_count

            dream_trace.consolidation_count = consolidated_count

    async def _consolidate_similar_events(
        self,
        events: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Consolidate similar memory events."""
        if not events:
            return []

        # Simple grouping by event type
        event_groups: Dict[str, List[Dict[str, Any]]] = {}
        for event in events:
            event_type = event.get("type", "unknown")
            if event_type not in event_groups:
                event_groups[event_type] = []
            event_groups[event_type].append(event)

        # Consolidate each group
        consolidated = []
        for event_type, group in event_groups.items():
            if len(group) > 1:
                # Create consolidated event
                consolidated_event = {
                    "type": f"consolidated_{event_type}",
                    "original_count": len(group),
                    "consolidation_timestamp": time.time(),
                    "summary": f"Consolidated {len(group)} {event_type} events"
                }
                consolidated.append(consolidated_event)
            else:
                # Keep single events as-is
                consolidated.extend(group)

        return consolidated

    async def _discover_patterns(
        self,
        dream_trace: DreamTrace,
        state: ConsciousnessState
    ) -> None:
        """Discover patterns in memory and consciousness state."""
        if not self.pattern_discovery_enabled:
            return

        discovered_motifs = []

        # Pattern discovery based on consciousness state
        if state.phase == "REFLECT":
            discovered_motifs.append("reflection_pattern")
        elif state.phase == "AWARE" and state.level > 0.8:
            discovered_motifs.append("high_awareness_pattern")

        # Temporal patterns
        current_hour = time.localtime().tm_hour
        if 2 <= current_hour <= 6:
            discovered_motifs.append("night_pattern")
        elif 9 <= current_hour <= 17:
            discovered_motifs.append("day_pattern")

        # Memory buffer patterns
        if len(self._memory_buffer) > 0:
            event_types = [event.get("type", "unknown") for event in self._memory_buffer[-10:]]
            most_common_type = max(set(event_types), key=event_types.count) if event_types else "unknown"
            if event_types.count(most_common_type) > 3:
                discovered_motifs.append(f"recurring_{most_common_type}_pattern")

        # Update discovered motifs
        self._discovered_motifs.update(discovered_motifs)
        dream_trace.top_k_motifs = discovered_motifs
        dream_trace.memory_patterns_discovered = len(discovered_motifs)

    async def _generate_associations(self, dream_trace: DreamTrace) -> None:
        """Generate creative associations between concepts."""
        associations = []

        # Associate recent motifs with consciousness patterns
        for motif in dream_trace.top_k_motifs:
            association = {
                "source": motif,
                "target": "consciousness_state",
                "strength": random.uniform(0.3, 0.9),
                "type": "pattern_correlation"
            }
            associations.append(association)

        # Cross-motif associations
        motifs = list(dream_trace.top_k_motifs)
        for i in range(len(motifs)):
            for j in range(i + 1, len(motifs)):
                if random.random() > 0.7:  # 30% chance of association
                    association = {
                        "source": motifs[i],
                        "target": motifs[j],
                        "strength": random.uniform(0.2, 0.6),
                        "type": "motif_connection"
                    }
                    associations.append(association)

        dream_trace.associations = associations

    async def _calculate_compression_metrics(
        self,
        dream_trace: DreamTrace,
        input_events: List[Dict[str, Any]]
    ) -> None:
        """Calculate memory compression ratio achieved."""
        if not input_events:
            dream_trace.compression_ratio = 1.0
            return

        # Simulate compression calculation
        original_size = len(input_events)
        current_buffer_size = len(self._memory_buffer)

        if current_buffer_size > 0:
            # Compression ratio: smaller is better compression
            compression_ratio = current_buffer_size / max(original_size, 1)
        else:
            compression_ratio = 0.1  # Very good compression

        # Bound compression ratio to reasonable range
        dream_trace.compression_ratio = max(0.1, min(1.0, compression_ratio))

    async def _finalize_dream_artifacts(self, dream_trace: DreamTrace) -> None:
        """Finalize dream processing artifacts."""

        # Update association graph with new associations
        for association in dream_trace.associations:
            source = association.get("source", "")
            target = association.get("target", "")

            if source and target:
                if source not in self._association_graph:
                    self._association_graph[source] = []
                if target not in self._association_graph[source]:
                    self._association_graph[source].append(target)

        # Limit motif storage to prevent unbounded growth
        if len(self._discovered_motifs) > 100:
            # Keep most recent motifs
            motif_list = list(self._discovered_motifs)
            self._discovered_motifs = set(motif_list[-50:])

    def get_current_phase(self) -> DreamPhase:
        """Get current dream phase."""
        return self._current_phase.value

    def is_dreaming(self) -> bool:
        """Check if currently in dreaming phase."""
        return self._current_phase == DreamState.DREAMING

    def should_trigger_dream(self, memory_pressure: float = 0.0) -> bool:
        """Determine if dream cycle should be triggered."""

        # Trigger if memory buffer exceeds threshold
        if len(self._memory_buffer) >= self.consolidation_threshold:
            return True

        # Trigger if memory pressure is high
        if memory_pressure > 0.8:
            return True

        # Trigger if too much time has passed since last consolidation
        time_since_last = time.time() - self._last_consolidation_time
        if time_since_last > 300:  # 5 minutes
            return True

        return False

    def get_performance_stats(self) -> Dict[str, float]:
        """Get current performance statistics."""
        if self._dream_cycles_completed == 0:
            return {
                "total_cycles": 0,
                "average_duration_ms": 0.0,
                "consolidation_rate": 0.0,
                "discovered_motifs": 0,
                "compression_efficiency": 0.0
            }

        return {
            "total_cycles": self._dream_cycles_completed,
            "average_duration_ms": self._total_processing_time / self._dream_cycles_completed,
            "consolidation_rate": self._consolidation_count / self._dream_cycles_completed,
            "discovered_motifs": len(self._discovered_motifs),
            "compression_efficiency": 1.0 - (len(self._memory_buffer) / max(self._consolidation_count, 1)),
            "current_phase": self._current_phase.value
        }

    def reset_state(self) -> None:
        """Reset internal state for testing or reconfiguration."""
        self._current_phase = DreamState.IDLE
        self._dream_session_id = None
        self._memory_buffer.clear()
        self._discovered_motifs.clear()
        self._association_graph.clear()
        self._consolidation_count = 0
        self._dream_cycles_completed = 0
        self._total_processing_time = 0.0


# Export for public API
__all__ = ["DreamEngine", "DreamState"]