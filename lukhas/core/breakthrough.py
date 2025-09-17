"""
core/breakthrough.py

BreakthroughDetector for novelty × value scoring with CUSUM-style detection.
Working theory: breakthrough = significant increase in (novelty × value) using z-score.

Usage:
  from core.breakthrough import BreakthroughDetector
  detector = BreakthroughDetector(z=3.0)
  result = detector.step(novelty=0.8, value=0.9)
  if result["breakthrough"]:
      print(f"Breakthrough detected: score={result['score']:.3f}")
"""
from __future__ import annotations
import os
from typing import Dict, Any
import math

try:
    from prometheus_client import Counter, Gauge
    PROM = True
except Exception:
    PROM = False

class _NoopCounter:
    def labels(self, *_, **__):
        return self
    def inc(self, *_):
        pass

class _NoopGauge:
    def labels(self, *_, **__):
        return self
    def set(self, *_):
        pass

# Define metrics (labeled by lane) with no-op fallbacks when Prometheus is unavailable
if PROM:
    BREAKTHROUGH_FLAGS = Counter(
        "lukhas_breakthrough_flags_total",
        "Breakthrough detection flags",
        ["lane"],
    )
    BREAKTHROUGH_SCORE = Gauge(
        "lukhas_breakthrough_score",
        "Latest novelty×value score",
        ["lane"],
    )
    BREAKTHROUGH_STD = Gauge(
        "lukhas_breakthrough_std",
        "Running standard deviation of novelty×value",
        ["lane"],
    )
else:
    BREAKTHROUGH_FLAGS = _NoopCounter()
    BREAKTHROUGH_SCORE = _NoopGauge()
    BREAKTHROUGH_STD = _NoopGauge()

class BreakthroughDetector:
    """
    Detects breakthroughs using novelty × value scoring with z-score threshold.

    A breakthrough is detected when the weighted score exceeds mean + z*std,
    using online statistics to track running mean and standard deviation.
    Warmup samples can be required before flagging using min_n.
    """
    __slots__ = ("mu", "sq", "n", "z", "w", "lane", "min_n", "z_per_lane")

    def __init__(self, novelty_w: float = 0.5, value_w: float = 0.5, z: float = 3.0, *, min_n: int = None):
        """Initialize breakthrough detector.

        Args:
            novelty_w: Weight for novelty component (0-1)
            value_w: Weight for value component (0-1)
            z: Default Z-score threshold for breakthrough detection
            min_n: Optional minimum number of samples before any breakthrough can be flagged.
                    If None, uses env `LUKHAS_BREAKTHROUGH_WARMUP` or defaults to 16.
        """
        self.mu = 0.0       # Running mean
        self.sq = 0.0       # Sum of squared deviations for variance
        self.n = 0          # Sample count
        self.z = z          # Base Z-score threshold
        self.w = (novelty_w, value_w)  # Weights tuple
        self.lane = os.getenv("LUKHAS_LANE", "experimental").lower()
        # Per-lane z overrides (can be tuned later)
        self.z_per_lane = {
            "experimental": z,
            "candidate": z,
            "prod": z,
        }
        # Warmup minimum samples before flagging
        if min_n is None:
            try:
                min_n = int(os.getenv("LUKHAS_BREAKTHROUGH_WARMUP", "16"))
            except ValueError:
                min_n = 16
        self.min_n = max(0, int(min_n))

    def step(self, novelty: float, value: float) -> Dict[str, Any]:
        """Process new novelty and value scores, detect breakthroughs.

        Args:
            novelty: Novelty score (0-1, higher = more novel)
            value: Value score (0-1, higher = more valuable)

        Returns:
            Dict with score, mean, std, breakthrough flag
        """
        # Validate inputs
        if novelty is None or value is None:
            raise ValueError("novelty and value must be provided")
        if not isinstance(novelty, (int, float)) or not isinstance(value, (int, float)):
            raise TypeError("novelty and value must be numeric")
        if math.isnan(novelty) or math.isnan(value) or math.isinf(novelty) or math.isinf(value):
            raise ValueError("novelty and value must be finite numbers")

        # Clamp to [0,1] to keep score well-behaved
        n_clamped = 0.0 if novelty < 0 else 1.0 if novelty > 1 else float(novelty)
        v_clamped = 0.0 if value < 0 else 1.0 if value > 1 else float(value)

        # Compute weighted score (novelty×value style via convex combo for stability)
        score = self.w[0] * n_clamped + self.w[1] * v_clamped

        # Update online statistics (Welford's algorithm)
        self.n += 1
        delta = score - self.mu
        self.mu += delta / self.n
        delta2 = score - self.mu
        self.sq += delta * delta2

        # Compute standard deviation
        std = (self.sq / (self.n - 1))**0.5 if self.n > 1 else 0.0

        # Breakthrough detection: score > mean + z*std, with warmup gating and per-lane z
        z_eff = self.z_per_lane.get(self.lane, self.z)
        is_breakthrough = (self.n >= self.min_n) and (std > 0) and (score > self.mu + z_eff * std)

        # Export metrics (no-op if disabled)
        BREAKTHROUGH_SCORE.labels(self.lane).set(score)
        BREAKTHROUGH_STD.labels(self.lane).set(std)
        if is_breakthrough:
            BREAKTHROUGH_FLAGS.labels(self.lane).inc()

        return {
            "score": score,
            "mean": self.mu,
            "std": std,
            "breakthrough": is_breakthrough,
            "n": self.n,
            "lane": self.lane,
            "z": z_eff,
            "min_n": self.min_n,
        }

    def reset(self) -> None:
        """Reset detector state for new detection window."""
        self.mu = 0.0
        self.sq = 0.0
        self.n = 0


# CLI for testing
if __name__ == "__main__":
    import sys
    detector = BreakthroughDetector(z=3.0)
    lane = os.getenv("LUKHAS_LANE", "experimental").lower()

    print(f"BreakthroughDetector CLI (lane={lane}) - enter 'novelty value' pairs:")
    print("Example: 0.5 0.8 — type 'quit' to exit")

    try:
        while True:
            line = input("> ").strip()
            if line.lower() in ['quit', 'exit', 'q']:
                break
            try:
                parts = line.split()
                if len(parts) != 2:
                    print("Error: provide exactly 2 values (novelty value)")
                    continue

                novelty, value = float(parts[0]), float(parts[1])
                result = detector.step(novelty, value)

                warm = " (warming)" if result["n"] < result["min_n"] else ""
                status = "🚨 BREAKTHROUGH" if result["breakthrough"] else "   normal"
                print(f"{status} | score={result['score']:.3f} μ={result['mean']:.3f} "
                      f"σ={result['std']:.3f} n={result['n']}{warm}")

            except ValueError as e:
                print(f"Error: {e}")

    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)