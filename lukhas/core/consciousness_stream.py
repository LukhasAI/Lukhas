#!/usr/bin/env python3
"""
core/consciousness_stream.py

Phase 4: Live consciousness stream integration - Ticker → Router → EventStore
T4-DELTA-PLAN: Wire components for stream-based consciousness processing

Usage:
    from core.consciousness_stream import ConsciousnessStream

    stream = ConsciousnessStream()
    stream.start()  # Begin processing consciousness ticks
"""
from __future__ import annotations

import os
import logging
import asyncio
from datetime import datetime, timedelta
from uuid import uuid4, UUID
from typing import Dict, Any, Optional, List
from collections import deque
import statistics

# Guardian system integration
try:
    from governance.guardian_system import GuardianSystem
    GUARDIAN_AVAILABLE = True
except ImportError:
    GUARDIAN_AVAILABLE = False
    logging.warning("Guardian system not available for consciousness validation")

from lukhas.core.clock import Ticker
from lukhas.core.ring import DecimatingRing
from matriz.router import SymbolicMeshRouter
from matriz.node_contract import MatrizMessage, GLYPH
from storage.events import Event, EventStore

# Optional metrics
try:
    from prometheus_client import Counter, Histogram, Gauge
    STREAM_EVENTS_TOTAL = Counter("lukhas_stream_events_total", "Events processed by stream", ["kind", "lane"])
    STREAM_PROCESSING_DURATION = Histogram("lukhas_stream_processing_seconds", "Stream processing time", ["lane"])
    STREAM_BREAKTHROUGHS_PER_MIN = Gauge("lukhas_stream_breakthroughs_per_min", "Breakthroughs per minute", ["lane"])
    STREAM_TICK_P95 = Gauge("lukhas_stream_tick_p95_ms", "Tick processing p95 latency (ms)", ["lane"])
    STREAM_DRIFT_EMA = Gauge("lukhas_stream_drift_ema", "Exponential moving average of drift", ["lane"])
    STREAM_BACKPRESSURE_DROPS = Gauge("lukhas_stream_backpressure_drops_total", "Total drops due to backpressure", ["lane"])
    STREAM_BUFFER_UTILIZATION = Gauge("lukhas_stream_buffer_utilization", "Buffer utilization (0.0-1.0)", ["lane"])
    STREAM_DECIMATION_EVENTS = Gauge("lukhas_stream_decimation_events_total", "Total decimation events", ["lane"])
    PROM = True
except Exception:
    PROM = False
    class _NoopMetric:
        def labels(self, *_, **__): return self
        def inc(self, *_): pass
        def observe(self, *_): pass
        def set(self, *_): pass
    STREAM_EVENTS_TOTAL = _NoopMetric()
    STREAM_PROCESSING_DURATION = _NoopMetric()
    STREAM_BREAKTHROUGHS_PER_MIN = _NoopMetric()
    STREAM_TICK_P95 = _NoopMetric()
    STREAM_DRIFT_EMA = _NoopMetric()
    STREAM_BACKPRESSURE_DROPS = _NoopMetric()
    STREAM_BUFFER_UTILIZATION = _NoopMetric()
    STREAM_DECIMATION_EVENTS = _NoopMetric()


logger = logging.getLogger(__name__)


class ConsciousnessStream:
    """
    Live consciousness stream coordinator for Phase 4.

    Integrates Ticker → Router → EventStore without external dispatch.
    Each consciousness tick generates events that flow through the system
    for experience replay and observability.
    """

    def __init__(
        self,
        fps: int = 30,
        store_capacity: int = 10000,
        glyph_id: Optional[UUID] = None,
        enable_backpressure: bool = True,
        backpressure_threshold: float = 0.8,
        decimation_factor: int = 2,
        decimation_strategy: str = "skip_nth"
    ):
        """
        Initialize consciousness stream.

        Args:
            fps: Consciousness tick rate (default: 30)
            store_capacity: Maximum events in store (default: 10000)
            glyph_id: Stream identity (auto-generated if None)
            enable_backpressure: Enable backpressure handling with ring decimation (default: True)
            backpressure_threshold: Buffer utilization threshold to trigger decimation (default: 0.8)
            decimation_factor: Decimation aggressiveness (default: 2 = keep every 2nd event)
            decimation_strategy: Decimation strategy ("skip_nth", "keep_recent", "adaptive")
        """
        self.lane = os.getenv("LUKHAS_LANE", "experimental")
        self.glyph_id = glyph_id or uuid4()

        # Core components
        self.ticker = Ticker(fps=fps)
        self.router = SymbolicMeshRouter(log_fn=self._log_router_event)
        self.event_store = EventStore(max_capacity=store_capacity)

        # Backpressure management
        self.enable_backpressure = enable_backpressure
        if self.enable_backpressure:
            self.backpressure_ring = DecimatingRing(
                capacity=store_capacity // 2,  # Ring buffer for overflow events
                pressure_threshold=backpressure_threshold,
                decimation_factor=decimation_factor,
                decimation_strategy=decimation_strategy
            )
        else:
            self.backpressure_ring = None

        # Stream state
        self.running = False
        self.tick_count = 0
        self.events_processed = 0
        self._router_logs: List[Dict[str, Any]] = []

        # Per-stream metrics tracking
        self._breakthrough_timestamps: deque = deque(maxlen=1000)  # Store recent breakthrough timestamps
        self._tick_processing_times: deque = deque(maxlen=100)    # Store recent tick processing times
        self._drift_ema = 0.0                                     # Exponential moving average of drift
        self._drift_alpha = 0.1                                   # EMA smoothing factor
        self._last_metrics_update = datetime.utcnow()

        # Guardian integration for consciousness safety
        self._guardian_integration_enabled = False
        self._guardian_instance = None
        self._consciousness_safety_violations = 0
        self._guardian_processing_overhead = deque(maxlen=50)  # Track Guardian overhead
        self._last_guardian_check = None
        self._consciousness_state = "initializing"  # initializing, active, suspended, error

        # Subscribe to ticker
        self.ticker.subscribe(self._on_consciousness_tick)

        logger.info(f"ConsciousnessStream initialized: lane={self.lane}, fps={fps}, glyph_id={self.glyph_id}")

    def enable_guardian_integration(self, guardian_instance: Optional[Any] = None) -> None:
        """Enable Guardian safety validation for consciousness processing"""
        if not GUARDIAN_AVAILABLE:
            logger.warning("Guardian system not available, cannot enable consciousness validation")
            return

        if guardian_instance:
            self._guardian_instance = guardian_instance
        elif GUARDIAN_AVAILABLE:
            # Create default Guardian instance
            self._guardian_instance = GuardianSystem()

        self._guardian_integration_enabled = True
        self._consciousness_state = "active"
        logger.info("Guardian-Consciousness integration enabled")

    def disable_guardian_integration(self) -> None:
        """Disable Guardian safety validation"""
        self._guardian_integration_enabled = False
        self._guardian_instance = None
        logger.info("Guardian-Consciousness integration disabled")

    def _log_router_event(self, event_type: str, data: dict) -> None:
        """Router logging callback - captures router activity."""
        log_entry = {
            "ts": datetime.utcnow(),
            "type": event_type,
            "data": data,
            "lane": self.lane
        }
        self._router_logs.append(log_entry)
        logger.debug(f"Router: {event_type} - {data}")

    def _on_consciousness_tick(self, tick_count: int) -> None:
        """
        Process a consciousness tick.

        Creates events for the tick and routes them through the system.
        This is the core of the live stream integration.
        """
        tick_start = datetime.utcnow()

        try:
            self.tick_count = tick_count

            # Guardian pre-processing validation
            if self._guardian_integration_enabled and self._guardian_instance:
                guardian_check_start = datetime.utcnow()

                # Prepare consciousness context for Guardian validation
                consciousness_context = {
                    "action_type": "consciousness_tick",
                    "tick_count": tick_count,
                    "stream_state": {
                        "running": self.running,
                        "events_processed": self.events_processed,
                        "drift_ema": self._drift_ema,
                        "processing_times": list(self._tick_processing_times)[-5:] if self._tick_processing_times else [],
                        "consciousness_state": self._consciousness_state
                    },
                    "correlation_id": f"consciousness_tick_{tick_count}_{int(tick_start.timestamp() * 1000)}",
                    "timestamp": tick_start.isoformat()
                }

                # Synchronous Guardian validation (for tick processing speed)
                try:
                    guardian_result = self._guardian_instance.validate_safety(consciousness_context)

                    guardian_overhead = (datetime.utcnow() - guardian_check_start).total_seconds() * 1000
                    self._guardian_processing_overhead.append(guardian_overhead)
                    self._last_guardian_check = datetime.utcnow()

                    # Check if consciousness processing is safe
                    if not guardian_result.get("safe", False):
                        self._consciousness_safety_violations += 1
                        violation_reason = guardian_result.get("reason", "Unknown safety concern")

                        logger.warning(
                            f"Guardian blocked consciousness tick {tick_count}: {violation_reason}"
                        )

                        # Create safety violation event
                        violation_event = Event.create(
                            kind="consciousness_safety_violation",
                            lane=self.lane,
                            glyph_id=self.glyph_id,
                            payload={
                                "tick_count": tick_count,
                                "guardian_result": guardian_result,
                                "violation_count": self._consciousness_safety_violations,
                                "context": consciousness_context
                            },
                            ts=tick_start
                        )

                        if self._should_store_event(violation_event):
                            self.event_store.append(violation_event)

                        # Decide on violation response based on severity
                        if guardian_result.get("guardian_status") == "emergency_disabled":
                            self._consciousness_state = "suspended"
                            logger.critical("Consciousness processing suspended due to Guardian emergency")
                            return  # Skip this tick entirely
                        elif guardian_result.get("drift_score", 0) > 0.5:
                            # High drift - proceed with enhanced monitoring
                            logger.warning(f"High drift detected: {guardian_result.get('drift_score')}, proceeding with caution")
                        else:
                            # Minor issue - log and continue
                            logger.info(f"Minor safety concern: {violation_reason}, continuing with monitoring")

                except Exception as guardian_error:
                    logger.error(f"Guardian validation failed for tick {tick_count}: {guardian_error}")
                    # On Guardian failure, proceed with consciousness (fail-open for availability)
                    # but log the failure for investigation
                    self._consciousness_safety_violations += 1

            # Create consciousness tick event
            tick_event = Event.create(
                kind="consciousness_tick",
                lane=self.lane,
                glyph_id=self.glyph_id,
                payload={
                    "tick_count": tick_count,
                    "fps": self.ticker.fps,
                    "stream_id": str(self.glyph_id),
                    "processing_time": None  # Will be filled after processing
                },
                ts=tick_start
            )

            # Route through MATRIZ router (log-only mode)
            router_msg = MatrizMessage(
                msg_id=tick_event.id,
                ts=tick_start,
                lane=self.lane,
                glyph=GLYPH(id=self.glyph_id, kind="consciousness"),
                payload=tick_event.to_dict(),
                topic="breakthrough"  # Use allowed topic from contract
            )
            self.router.publish(router_msg)

            # Store event for experience replay with backpressure handling
            if self._should_store_event(tick_event):
                self.event_store.append(tick_event)
                self.events_processed += 1
            elif self.enable_backpressure:
                # Store in backpressure ring as fallback
                self.backpressure_ring.push(tick_event)
                logger.debug(f"Event stored in backpressure ring: {tick_event.kind}")
            else:
                logger.warning(f"Event dropped due to storage capacity: {tick_event.kind}")

            # Update processing time in payload
            processing_duration = (datetime.utcnow() - tick_start).total_seconds()
            processing_ms = processing_duration * 1000

            # Track tick processing time for p95 calculation
            self._tick_processing_times.append(processing_ms)

            # Detect breakthrough patterns (simple heuristic: processing time significantly above average)
            if len(self._tick_processing_times) > 10:
                avg_processing = statistics.mean(self._tick_processing_times)
                if processing_ms > avg_processing * 1.5:  # Simple breakthrough detection
                    self._breakthrough_timestamps.append(datetime.utcnow())

            # Update drift EMA based on timing deviation
            target_interval = 1.0 / self.ticker.fps  # Expected interval between ticks
            timing_drift = abs(processing_duration - target_interval)
            self._drift_ema = (1 - self._drift_alpha) * self._drift_ema + self._drift_alpha * timing_drift

            # Enhanced drift monitoring with Guardian integration
            if self._guardian_integration_enabled and self._guardian_instance and hasattr(self._guardian_instance, 'reflector'):
                # Prepare drift context for advanced Guardian analysis
                drift_context = {
                    "drift_ema": self._drift_ema,
                    "timing_drift": timing_drift,
                    "processing_duration_ms": processing_ms,
                    "target_interval_ms": target_interval * 1000,
                    "tick_count": tick_count,
                    "recent_processing_times": list(self._tick_processing_times)[-10:],
                    "breakthrough_count": len(self._breakthrough_timestamps),
                    "consciousness_state": self._consciousness_state,
                    "correlation_id": f"consciousness_drift_{tick_count}"
                }

                # Store drift context for potential async Guardian analysis
                # (We don't await here to maintain tick processing speed)
                if hasattr(self, '_pending_drift_analyses'):
                    self._pending_drift_analyses = getattr(self, '_pending_drift_analyses', deque(maxlen=10))
                    self._pending_drift_analyses.append(drift_context)

            # Create a processing completion event
            completion_event = Event.create(
                kind="tick_processed",
                lane=self.lane,
                glyph_id=self.glyph_id,
                payload={
                    "tick_count": tick_count,
                    "processing_duration_ms": processing_ms,
                    "events_in_store": len(self.event_store.events),
                    "router_logs_count": len(self._router_logs),
                    "drift_ema": self._drift_ema,
                "guardian_integration": {
                    "enabled": self._guardian_integration_enabled,
                    "safety_violations": self._consciousness_safety_violations,
                    "last_check": self._last_guardian_check.isoformat() if self._last_guardian_check else None,
                    "avg_overhead_ms": (
                        sum(self._guardian_processing_overhead) / len(self._guardian_processing_overhead)
                        if self._guardian_processing_overhead else 0
                    )
                }
                }
            )
            if self._should_store_event(completion_event):
                self.event_store.append(completion_event)
            elif self.enable_backpressure:
                self.backpressure_ring.push(completion_event)

            # Update Prometheus metrics
            if PROM:
                STREAM_EVENTS_TOTAL.labels(kind="consciousness_tick", lane=self.lane).inc()
                STREAM_EVENTS_TOTAL.labels(kind="tick_processed", lane=self.lane).inc()
                STREAM_PROCESSING_DURATION.labels(lane=self.lane).observe(processing_duration)

                # Update per-stream metrics
                self._update_stream_metrics()

        except Exception as e:
            logger.error(f"Error processing consciousness tick {tick_count}: {e}")
            self._consciousness_state = "error"

            # Create error event with Guardian context
            error_payload = {
                "tick_count": tick_count,
                "error": str(e),
                "error_type": type(e).__name__,
                "consciousness_state": self._consciousness_state
            }

            # Add Guardian context to error if available
            if self._guardian_integration_enabled:
                error_payload["guardian_context"] = {
                    "safety_violations": self._consciousness_safety_violations,
                    "last_check": self._last_guardian_check.isoformat() if self._last_guardian_check else None,
                    "integration_enabled": True
                }

            error_event = Event.create(
                kind="processing_error",
                lane=self.lane,
                glyph_id=self.glyph_id,
                payload=error_payload
            )
            self.event_store.append(error_event)

    def _should_store_event(self, event: Event) -> bool:
        """Determine if event should be stored in main event store or deferred to backpressure ring."""
        if not self.enable_backpressure:
            return True  # Always store when backpressure disabled

        # Check if event store is approaching capacity
        store_utilization = len(self.event_store.events) / self.event_store.max_capacity
        return store_utilization < 0.9  # Allow 10% buffer before using ring

    def _update_stream_metrics(self) -> None:
        """Update per-stream Prometheus metrics."""
        try:
            # Calculate breakthroughs per minute
            now = datetime.utcnow()
            one_minute_ago = now - timedelta(minutes=1)
            recent_breakthroughs = [ts for ts in self._breakthrough_timestamps if ts >= one_minute_ago]
            breakthroughs_per_min = len(recent_breakthroughs)

            # Calculate tick processing p95 latency
            tick_p95_ms = 0.0
            if len(self._tick_processing_times) >= 5:
                tick_p95_ms = statistics.quantiles(self._tick_processing_times, n=20)[18]  # 95th percentile

            # Update Prometheus gauges
            STREAM_BREAKTHROUGHS_PER_MIN.labels(lane=self.lane).set(breakthroughs_per_min)
            STREAM_TICK_P95.labels(lane=self.lane).set(tick_p95_ms)
            STREAM_DRIFT_EMA.labels(lane=self.lane).set(self._drift_ema)

            # Update backpressure metrics
            if self.enable_backpressure and self.backpressure_ring:
                bp_stats = self.backpressure_ring.get_backpressure_stats()
                STREAM_BACKPRESSURE_DROPS.labels(lane=self.lane).set(bp_stats["total_drops"])
                STREAM_BUFFER_UTILIZATION.labels(lane=self.lane).set(bp_stats["utilization"])
                STREAM_DECIMATION_EVENTS.labels(lane=self.lane).set(bp_stats["decimation_events"])

        except Exception as e:
            logger.debug(f"Error updating stream metrics: {e}")

    def start(self, duration_seconds: int = 0) -> None:
        """
        Start the consciousness stream.

        Args:
            duration_seconds: How long to run (0 = indefinitely)
        """
        logger.info(f"Starting consciousness stream for {duration_seconds or 'indefinite'} seconds...")

        self.running = True
        self.router.start()

        # Generate initial stream started event
        start_event = Event.create(
            kind="stream_started",
            lane=self.lane,
            glyph_id=self.glyph_id,
            payload={
                "fps": self.ticker.fps,
                "store_capacity": self.event_store.max_capacity,
                "duration_seconds": duration_seconds
            }
        )
        self.event_store.append(start_event)

        try:
            # Run the ticker (this blocks)
            self.ticker.run(seconds=duration_seconds)
        finally:
            self.stop()

    def stop(self) -> None:
        """Stop the consciousness stream gracefully."""
        if not self.running:
            return

        logger.info("Stopping consciousness stream...")
        self.ticker.stop()
        self.running = False

        # Generate final stream stopped event
        stop_event = Event.create(
            kind="stream_stopped",
            lane=self.lane,
            glyph_id=self.glyph_id,
            payload={
                "final_tick_count": self.tick_count,
                "events_processed": self.events_processed,
                "final_store_size": len(self.event_store.events),
                "router_logs": len(self._router_logs)
            }
        )
        self.event_store.append(stop_event)

    def get_stream_metrics(self) -> Dict[str, Any]:
        """Get current stream performance and status metrics."""
        # Calculate per-stream metrics
        now = datetime.utcnow()
        one_minute_ago = now - timedelta(minutes=1)
        recent_breakthroughs = [ts for ts in self._breakthrough_timestamps if ts >= one_minute_ago]
        breakthroughs_per_min = len(recent_breakthroughs)

        tick_p95_ms = 0.0
        if len(self._tick_processing_times) >= 5:
            tick_p95_ms = statistics.quantiles(self._tick_processing_times, n=20)[18]

        return {
            "running": self.running,
            "lane": self.lane,
            "glyph_id": str(self.glyph_id),
            "tick_count": self.tick_count,
            "events_processed": self.events_processed,
            "store_size": len(self.event_store.events),
            "store_capacity": self.event_store.max_capacity,
            "router_logs": len(self._router_logs),
            "ticker_metrics": self.ticker.get_metrics(),
            # Per-stream metrics
            "breakthroughs_per_min": breakthroughs_per_min,
            "tick_p95_ms": tick_p95_ms,
            "drift_ema": self._drift_ema,
            "total_breakthroughs": len(self._breakthrough_timestamps),
            "avg_tick_processing_ms": statistics.mean(self._tick_processing_times) if self._tick_processing_times else 0.0,
            # Backpressure metrics
            "backpressure_enabled": self.enable_backpressure,
            "backpressure_stats": (
                self.backpressure_ring.get_backpressure_stats()
                if self.backpressure_ring
                else {
                    "capacity": 0,
                    "current_size": 0,
                    "utilization": 0.0,
                    "pressure_threshold": 0.0,
                    "total_pushes": 0,
                    "total_drops": 0,
                    "drop_rate": 0.0,
                    "decimation_events": 0,
                    "decimation_factor": 0,
                    "decimation_strategy": "disabled",
                    "last_decimation_utilization": 0.0,
                }
            )
        }

    def get_guardian_integration_status(self) -> Dict[str, Any]:
        """Get detailed Guardian-Consciousness integration status"""
        if not self._guardian_integration_enabled:
            return {
                "enabled": False,
                "available": GUARDIAN_AVAILABLE,
                "reason": "Integration not enabled"
            }

        recent_overhead = list(self._guardian_processing_overhead)[-10:]

        return {
            "enabled": True,
            "available": GUARDIAN_AVAILABLE,
            "consciousness_state": self._consciousness_state,
            "safety_violations": self._consciousness_safety_violations,
            "last_guardian_check": self._last_guardian_check.isoformat() if self._last_guardian_check else None,
            "guardian_performance": {
                "total_checks": len(self._guardian_processing_overhead),
                "avg_overhead_ms": (
                    sum(self._guardian_processing_overhead) / len(self._guardian_processing_overhead)
                    if self._guardian_processing_overhead else 0
                ),
                "recent_overhead_ms": recent_overhead,
                "max_overhead_ms": max(self._guardian_processing_overhead) if self._guardian_processing_overhead else 0,
                "overhead_std_dev": (
                    statistics.stdev(self._guardian_processing_overhead)
                    if len(self._guardian_processing_overhead) > 1 else 0
                )
            },
            "safety_metrics": {
                "violation_rate": (
                    self._consciousness_safety_violations / self.tick_count
                    if self.tick_count > 0 else 0
                ),
                "consecutive_safe_ticks": self._calculate_consecutive_safe_ticks(),
                "safety_trend": self._calculate_safety_trend()
            },
            "integration_health": self._assess_integration_health()
        }

    def _calculate_consecutive_safe_ticks(self) -> int:
        """Calculate consecutive ticks without safety violations"""
        # Simple implementation - could be enhanced with more sophisticated tracking
        recent_events = self.get_recent_events(100)
        consecutive_safe = 0

        for event in reversed(recent_events):
            if event.kind == "consciousness_safety_violation":
                break
            elif event.kind == "consciousness_tick":
                consecutive_safe += 1

        return consecutive_safe

    def _calculate_safety_trend(self) -> str:
        """Calculate safety trend over recent period"""
        if self._consciousness_safety_violations == 0:
            return "excellent"
        elif self.tick_count == 0:
            return "unknown"

        violation_rate = self._consciousness_safety_violations / self.tick_count

        if violation_rate < 0.01:  # Less than 1% violation rate
            return "good"
        elif violation_rate < 0.05:  # Less than 5% violation rate
            return "acceptable"
        else:
            return "concerning"

    def _assess_integration_health(self) -> str:
        """Assess overall Guardian-Consciousness integration health"""
        if not self._guardian_integration_enabled:
            return "disabled"

        if self._consciousness_state == "suspended":
            return "suspended"
        elif self._consciousness_state == "error":
            return "error"

        # Check Guardian overhead
        if self._guardian_processing_overhead:
            avg_overhead = sum(self._guardian_processing_overhead) / len(self._guardian_processing_overhead)
            if avg_overhead > 5.0:  # More than 5ms average overhead
                return "high_overhead"

        # Check violation rate
        safety_trend = self._calculate_safety_trend()
        if safety_trend == "concerning":
            return "unstable"
        elif safety_trend in ["good", "excellent"]:
            return "healthy"
        else:
            return "stable"

    def suspend_consciousness_processing(self, reason: str = "Manual suspension") -> None:
        """Suspend consciousness processing for safety reasons"""
        self._consciousness_state = "suspended"
        logger.warning(f"Consciousness processing suspended: {reason}")

        # Create suspension event
        suspension_event = Event.create(
            kind="consciousness_suspended",
            lane=self.lane,
            glyph_id=self.glyph_id,
            payload={
                "reason": reason,
                "tick_count": self.tick_count,
                "safety_violations": self._consciousness_safety_violations,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        if self._should_store_event(suspension_event):
            self.event_store.append(suspension_event)

    def resume_consciousness_processing(self, reason: str = "Manual resume") -> None:
        """Resume consciousness processing after suspension"""
        if self._consciousness_state != "suspended":
            logger.warning(f"Cannot resume consciousness - current state: {self._consciousness_state}")
            return

        self._consciousness_state = "active"
        logger.info(f"Consciousness processing resumed: {reason}")

        # Create resume event
        resume_event = Event.create(
            kind="consciousness_resumed",
            lane=self.lane,
            glyph_id=self.glyph_id,
            payload={
                "reason": reason,
                "tick_count": self.tick_count,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        if self._should_store_event(resume_event):
            self.event_store.append(resume_event)

    async def validate_consciousness_state_transition(self, new_state: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Validate consciousness state transitions through Guardian"""
        if not self._guardian_integration_enabled or not self._guardian_instance:
            return {
                "approved": True,
                "reason": "Guardian validation not enabled",
                "guardian_available": False
            }

        # Prepare state transition context
        transition_context = {
            "action_type": "consciousness_state_transition",
            "current_state": self._consciousness_state,
            "new_state": new_state,
            "tick_count": self.tick_count,
            "safety_violations": self._consciousness_safety_violations,
            "context": context or {},
            "correlation_id": f"state_transition_{int(datetime.utcnow().timestamp() * 1000)}"
        }

        try:
            # Use async Guardian validation for state transitions
            if hasattr(self._guardian_instance, 'validate_action_async'):
                validation_result = await self._guardian_instance.validate_action_async(
                    transition_context
                )
            else:
                # Fallback to sync validation
                validation_result = self._guardian_instance.validate_safety(transition_context)

            approved = validation_result.get("safe", False)
            reason = validation_result.get("reason", "Guardian validation completed")

            if approved:
                logger.info(f"Guardian approved consciousness state transition: {self._consciousness_state} -> {new_state}")
            else:
                logger.warning(f"Guardian blocked consciousness state transition: {self._consciousness_state} -> {new_state}, reason: {reason}")

            return {
                "approved": approved,
                "reason": reason,
                "guardian_available": True,
                "guardian_result": validation_result,
                "transition_context": transition_context
            }

        except Exception as e:
            logger.error(f"Guardian validation failed for state transition: {e}")
            return {
                "approved": False,
                "reason": f"Guardian validation error: {str(e)}",
                "guardian_available": True,
                "error": True
            }

    def get_recent_events(self, limit: int = 100) -> List[Event]:
        """Get recent events from the store for monitoring."""
        return self.event_store.query_recent(limit=limit)

    def replay_events(self, since_minutes: int = 5) -> List[Event]:
        """Get events for experience replay."""
        return self.event_store.query_sliding_window(window_seconds=since_minutes * 60)


def create_consciousness_stream(**kwargs) -> ConsciousnessStream:
    """Factory function for creating consciousness streams."""
    return ConsciousnessStream(**kwargs)


if __name__ == "__main__":
    # Demo: Run consciousness stream for 10 seconds
    import sys

    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 10

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    print(f"🧠 Starting consciousness stream demo for {duration} seconds...")

    stream = create_consciousness_stream(fps=30)

    try:
        stream.start(duration_seconds=duration)
    finally:
        metrics = stream.get_stream_metrics()
        print(f"\n📊 Stream completed:")
        print(f"   Ticks processed: {metrics['tick_count']}")
        print(f"   Events in store: {metrics['store_size']}")
        print(f"   Router logs: {metrics['router_logs']}")

        recent = stream.get_recent_events(limit=5)
        print(f"   Latest events: {[e.kind for e in recent]}")