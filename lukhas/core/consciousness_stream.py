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
import time
from datetime import datetime, timedelta
from uuid import uuid4, UUID
from typing import Dict, Any, Optional, List
from collections import deque
import statistics

from core.clock import Ticker
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
        glyph_id: Optional[UUID] = None
    ):
        """
        Initialize consciousness stream.

        Args:
            fps: Consciousness tick rate (default: 30)
            store_capacity: Maximum events in store (default: 10000)
            glyph_id: Stream identity (auto-generated if None)
        """
        self.lane = os.getenv("LUKHAS_LANE", "experimental")
        self.glyph_id = glyph_id or uuid4()

        # Core components
        self.ticker = Ticker(fps=fps)
        self.router = SymbolicMeshRouter(log_fn=self._log_router_event)
        self.event_store = EventStore(max_capacity=store_capacity)

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

        # Subscribe to ticker
        self.ticker.subscribe(self._on_consciousness_tick)

        logger.info(f"ConsciousnessStream initialized: lane={self.lane}, fps={fps}, glyph_id={self.glyph_id}")

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

            # Store event for experience replay
            self.event_store.append(tick_event)
            self.events_processed += 1

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
                    "drift_ema": self._drift_ema
                }
            )
            self.event_store.append(completion_event)

            # Update Prometheus metrics
            if PROM:
                STREAM_EVENTS_TOTAL.labels(kind="consciousness_tick", lane=self.lane).inc()
                STREAM_EVENTS_TOTAL.labels(kind="tick_processed", lane=self.lane).inc()
                STREAM_PROCESSING_DURATION.labels(lane=self.lane).observe(processing_duration)

                # Update per-stream metrics
                self._update_stream_metrics()

        except Exception as e:
            logger.error(f"Error processing consciousness tick {tick_count}: {e}")

            # Create error event
            error_event = Event.create(
                kind="processing_error",
                lane=self.lane,
                glyph_id=self.glyph_id,
                payload={
                    "tick_count": tick_count,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            self.event_store.append(error_event)

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
            "avg_tick_processing_ms": statistics.mean(self._tick_processing_times) if self._tick_processing_times else 0.0
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