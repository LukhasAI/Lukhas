"""
core/ring.py

Ring buffer implementation for backpressure and decimation.

Usage:
  from core.ring import Ring, DecimatingRing
  r = Ring(capacity=1000)
  r.push(data)
  all_data = r.pop_all()

  # With decimation for backpressure
  dr = DecimatingRing(capacity=1000, pressure_threshold=0.8, decimation_factor=2)
  dr.push(data)  # Automatically decimates when under pressure
"""
from collections import deque
from typing import Any, List, Optional, Callable
import logging

logger = logging.getLogger(__name__)


class Ring:
    """Basic ring buffer with fixed capacity."""

    def __init__(self, capacity: int):
        self.q = deque(maxlen=capacity)

    def push(self, x):
        self.q.append(x)

    def pop_all(self):
        out, self.q = list(self.q), deque(maxlen=self.q.maxlen)
        return out

    def __len__(self):
        return len(self.q)

    @property
    def capacity(self) -> int:
        return self.q.maxlen

    @property
    def utilization(self) -> float:
        """Return buffer utilization as a fraction (0.0 to 1.0)."""
        return len(self.q) / self.capacity


class DecimatingRing(Ring):
    """Ring buffer with automatic decimation for backpressure management."""

    def __init__(
        self,
        capacity: int,
        pressure_threshold: float = 0.8,
        decimation_factor: int = 2,
        decimation_strategy: str = "skip_nth"
    ):
        """
        Initialize decimating ring buffer.

        Args:
            capacity: Maximum buffer size
            pressure_threshold: Utilization threshold to trigger decimation (0.0-1.0)
            decimation_factor: How aggressively to decimate (2 = keep every 2nd item)
            decimation_strategy: Strategy for decimation ("skip_nth", "keep_recent", "adaptive")
        """
        super().__init__(capacity)
        self.pressure_threshold = pressure_threshold
        self.decimation_factor = decimation_factor
        self.decimation_strategy = decimation_strategy

        # Backpressure tracking
        self.drops_total = 0
        self.decimation_events = 0
        self.push_count = 0
        self.last_decimation_utilization = 0.0

    def push(self, x: Any, priority: Optional[int] = None):
        """
        Push item with automatic decimation under backpressure.

        Args:
            x: Item to push
            priority: Optional priority for priority-based decimation
        """
        self.push_count += 1

        # Check if we need to apply backpressure
        current_utilization = self.utilization

        if current_utilization >= self.pressure_threshold:
            # Apply decimation strategy
            if self._should_drop_item(x, priority, current_utilization):
                self.drops_total += 1
                return  # Drop the item

        # Add item normally
        self.q.append(x)

        # If we reached capacity after adding, trigger decimation
        if len(self.q) >= self.capacity:
            self._apply_decimation()

    def _should_drop_item(self, item: Any, priority: Optional[int], utilization: float) -> bool:
        """Determine if item should be dropped based on decimation strategy."""

        if self.decimation_strategy == "skip_nth":
            # Drop every nth item when under pressure
            return (self.push_count % self.decimation_factor) != 0

        elif self.decimation_strategy == "adaptive":
            # More aggressive dropping as pressure increases
            pressure_ratio = (utilization - self.pressure_threshold) / (1.0 - self.pressure_threshold)
            adaptive_factor = max(2, int(self.decimation_factor * (1 + pressure_ratio * 2)))
            return (self.push_count % adaptive_factor) != 0

        else:  # "keep_recent" - don't drop new items, will decimate buffer
            return False

    def _apply_decimation(self):
        """Apply decimation to current buffer contents."""
        if len(self.q) < 2:
            return

        if self.decimation_strategy in ("skip_nth", "adaptive"):
            # Keep every nth item
            decimated = [self.q[i] for i in range(0, len(self.q), self.decimation_factor)]
            self.q.clear()
            self.q.extend(decimated)

        elif self.decimation_strategy == "keep_recent":
            # Keep the most recent half
            keep_count = len(self.q) // 2
            recent_items = list(self.q)[-keep_count:]
            self.q.clear()
            self.q.extend(recent_items)

        self.decimation_events += 1
        self.last_decimation_utilization = len(self.q) / self.capacity

        logger.debug(f"Ring decimation applied: {len(self.q)} items remain, "
                    f"utilization now {self.last_decimation_utilization:.2f}")

    def get_backpressure_stats(self) -> dict:
        """Get backpressure and decimation statistics."""
        return {
            "capacity": self.capacity,
            "current_size": len(self.q),
            "utilization": self.utilization,
            "pressure_threshold": self.pressure_threshold,
            "total_pushes": self.push_count,
            "total_drops": self.drops_total,
            "drop_rate": self.drops_total / max(1, self.push_count),
            "decimation_events": self.decimation_events,
            "decimation_factor": self.decimation_factor,
            "decimation_strategy": self.decimation_strategy,
            "last_decimation_utilization": self.last_decimation_utilization
        }

    def reset_stats(self):
        """Reset backpressure statistics."""
        self.drops_total = 0
        self.decimation_events = 0
        self.push_count = 0
        self.last_decimation_utilization = 0.0