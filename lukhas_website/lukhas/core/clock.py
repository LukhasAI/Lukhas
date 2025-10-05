#!/usr/bin/env python3
"""
Central Timing System for LUKHAS Consciousness
T4-Approved: All consciousness ticks route through this central authority

Usage:
    from core.clock import Ticker

    ticker = Ticker(fps=30)
    ticker.subscribe(my_consciousness_callback)
    ticker.run(seconds=60)  # Run for 60 seconds
"""
from __future__ import annotations

import math
import os
from time import perf_counter, sleep
from typing import Callable, List

# Optional Prometheus metrics (safe to import; no hard dependency in tests)
try:
    from core.metrics import tick_duration, ticker_subscriber_exceptions, ticker_ticks_dropped
    _PROM_AVAILABLE = True
except Exception:
    _PROM_AVAILABLE = False


class Ticker:
    """
    Deterministic 30 FPS ticker for consciousness systems

    All timing in LUKHAS routes through this central clock to ensure
    deterministic behavior and proper observability.
    """

    def __init__(self, fps: int = 30):
        """
        Initialize ticker with target frame rate

        Args:
            fps: Target frames per second (default: 30)
        """
        self.fps = fps
        self.period = 1.0 / fps
        self.subscribers: List[Callable[[int], None]] = []
        self.tick_count = 0
        self.running = False

        self.lane = os.getenv("LUKHAS_LANE", "experimental")
        self.mode = "realtime"  # or "catchup"

        # Performance metrics
        self.metrics = {
            "ticks_processed": 0,
            "ticks_dropped": 0,           # count of ticks where budget overran
            "total_processing_time": 0.0,
            "max_processing_time": 0.0,
            "p95_processing_time": 0.0,
            "subscriber_exceptions": 0,   # number of callback exceptions
            "max_subscriber_time": 0.0,   # longest single-callback time (s)
        }

        # Timing history for p95 calculation
        self._timing_history: List[float] = []
        self._history_limit = 1000  # Keep last 1000 measurements

    def subscribe(self, callback: Callable[[int], None]) -> None:
        """
        Register a callback for tick events

        Args:
            callback: Function that receives tick_count as parameter
        """
        self.subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[int], None]) -> None:
        """
        Unregister a callback from tick events

        Args:
            callback: Function to remove from subscribers
        """
        if callback in self.subscribers:
            self.subscribers.remove(callback)

    def get_metrics(self) -> dict:
        """
        Get current performance metrics

        Returns:
            Dictionary with timing metrics and performance data
        """
        return {
            "fps_target": self.fps,
            "tick_count": self.tick_count,
            "running": self.running,
            **self.metrics
        }

    def _update_timing_metrics(self, processing_time: float) -> None:
        """Update internal timing metrics"""
        self.metrics["total_processing_time"] += processing_time
        if processing_time > self.metrics["max_processing_time"]:
            self.metrics["max_processing_time"] = processing_time

        # Update timing history for p95 calculation
        self._timing_history.append(processing_time)
        if len(self._timing_history) > self._history_limit:
            self._timing_history.pop(0)

        # Calculate p95 with ceiling-based index to avoid bias
        n = len(self._timing_history)
        if n >= 20:
            sorted_times = sorted(self._timing_history)
            p95_index = max(0, math.ceil(0.95 * n) - 1)
            self.metrics["p95_processing_time"] = sorted_times[p95_index]

    def _notify_subscribers(self) -> float:
        """
        Notify all subscribers of tick event.

        Returns:
            Total time spent processing all subscribers (seconds).
        """
        start = perf_counter()
        for callback in list(self.subscribers):  # snapshot to tolerate unsubscribe during iteration
            cb_start = perf_counter()
            try:
                callback(self.tick_count)
            except Exception as e:
                # Count and log, but keep ticking
                self.metrics["subscriber_exceptions"] += 1
                if _PROM_AVAILABLE:
                    try:
                        ticker_subscriber_exceptions.labels(lane=self.lane).inc()
                    except Exception:
                        pass
                print(f"Warning: subscriber {getattr(callback, '__name__', repr(callback))} error at tick {self.tick_count}: {e}")
            finally:
                cb_elapsed = perf_counter() - cb_start
                if cb_elapsed > self.metrics["max_subscriber_time"]:
                    self.metrics["max_subscriber_time"] = cb_elapsed
        return perf_counter() - start

    def run(self, seconds: int = 0) -> None:
        """
        Run the ticker for specified duration

        Args:
            seconds: Duration to run (0 = run indefinitely)
        Notes:
            - self.mode == "realtime": maintain cadence; do not try to catch up after overruns.
            - self.mode == "catchup": skip sleeping after an overrun to attempt catch-up.
        """
        self.running = True
        start_time = perf_counter()

        print(f"🕐 Starting ticker at {self.fps} FPS...")

        try:
            while self.running:
                tick_start = perf_counter()

                # Process all subscribers
                processing_time = self._notify_subscribers()

                # Update metrics
                self.metrics["ticks_processed"] += 1
                self._update_timing_metrics(processing_time)

                # Calculate sleep time to maintain FPS
                elapsed = perf_counter() - tick_start

                if _PROM_AVAILABLE:
                    try:
                        tick_duration.labels(lane=self.lane).observe(elapsed)
                    except Exception:
                        pass

                sleep_time = max(0.0, self.period - elapsed)

                if elapsed > self.period:
                    # Over budget: record a drop and decide strategy
                    self.metrics["ticks_dropped"] += 1
                    if _PROM_AVAILABLE:
                        try:
                            ticker_ticks_dropped.labels(lane=self.lane).inc()
                        except Exception:
                            pass
                    if self.mode == "catchup":
                        # Skip sleeping to catch up next loop
                        sleep_time = 0.0

                # Sleep to maintain target FPS (if any budget remains)
                if sleep_time > 0:
                    sleep(sleep_time)

                self.tick_count += 1

                # Check for duration limit
                if seconds > 0 and (perf_counter() - start_time) >= seconds:
                    break

        except KeyboardInterrupt:
            print("\n⏹️  Ticker stopped by user")
        finally:
            self.running = False
            self._print_summary()

    def stop(self) -> None:
        """Stop the ticker gracefully"""
        self.running = False

    def _print_summary(self) -> None:
        """Print performance summary"""
        metrics = self.get_metrics()
        total_time = metrics["total_processing_time"]
        ticks = metrics["ticks_processed"]
        p95 = metrics["p95_processing_time"] * 1000
        avg = (total_time / ticks) * 1000 if ticks > 0 else 0.0
        actual_fps = (self.tick_count / total_time) if total_time > 0 else 0.0

        print("\n📊 Ticker Summary:")
        print(f"   Target FPS: {self.fps} | Actual FPS (approx proc-only): {actual_fps:.1f}")
        print(f"   Ticks processed: {ticks}")
        print(f"   Ticks dropped:  {metrics['ticks_dropped']}")
        print(f"   Avg processing: {avg:.2f}ms")
        print(f"   Max processing: {metrics['max_processing_time']*1000:.2f}ms")
        print(f"   P95 processing: {p95:.2f}ms")
        print(f"   Subscriber exceptions: {metrics['subscriber_exceptions']}")
        print(f"   Max single-callback time: {metrics['max_subscriber_time']*1000:.2f}ms")

        # T4 Performance target: p95 < 35ms for candidate lane
        if p95 < 35:
            print(f"   ✅ Performance: Within T4 target (p95={p95:.1f}ms < 35ms)")
        else:
            print(f"   ⚠️ Performance: Above T4 target (p95={p95:.1f}ms > 35ms)")


def create_consciousness_ticker() -> Ticker:
    """
    Factory function for consciousness-specific ticker

    Returns:
        Ticker configured for consciousness streaming (30 FPS)
    """
    return Ticker(fps=30)


# Example usage and testing
def example_subscriber(tick_count: int) -> None:
    """Example subscriber for demonstration"""
    if tick_count % 30 == 0:  # Print every second
        print(f"Consciousness tick: {tick_count}")


if __name__ == "__main__":
    # Demo mode - run ticker for 5 seconds
    ticker = create_consciousness_ticker()
    ticker.mode = "realtime"  # or "catchup"
    os.environ.setdefault("LUKHAS_LANE", "experimental")
    ticker.subscribe(example_subscriber)
    ticker.run(seconds=5)
