#!/usr/bin/env python3
"""
Memory Spindle - Simulates symbolic pattern emergence through spinning memory states
Based on entropy class and glyph recurrence patterns
"""
import json
import logging
from collections import Counter, deque
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class SpindleState:
    """Current state of the memory spindle"""

    rotation_speed: float  # 0.0 to 1.0
    coherence: float  # 0.0 to 1.0
    dominant_glyphs: list[str]
    entropy_class: str  # stable, neutral, unstable
    pattern_strength: float
    active_memories: int
    timestamp: datetime

    def to_symbolic(self) -> str:
        """Convert spindle state to symbolic representation"""
        if self.rotation_speed < 0.3:
            speed_symbol = "🌀"  # Slow spin
        elif self.rotation_speed < 0.7:
            speed_symbol = "🌪️"  # Medium spin
        else:
            speed_symbol = "🌌"  # Fast spin

        if self.coherence > 0.7:
            coherence_symbol = "💎"  # High coherence
        elif self.coherence > 0.4:
            coherence_symbol = "🔮"  # Medium coherence
        else:
            coherence_symbol = "🌫️"  # Low coherence

        return f"{speed_symbol}{coherence_symbol}"


class MemorySpindle:
    """
    Simulates symbolic pattern emergence through memory rotation
    Detects recurring patterns and generates emergent insights
    """

    # Entropy to spin speed mapping
    ENTROPY_SPIN_MAP = {
        "stable": (0.1, 0.3),  # Slow, steady spin
        "neutral": (0.3, 0.7),  # Moderate spin
        "unstable": (0.7, 1.0),  # Fast, chaotic spin
    }

    # Pattern emergence thresholds
    PATTERN_THRESHOLDS = {
        "weak": 0.3,
        "moderate": 0.5,
        "strong": 0.7,
        "crystallized": 0.9,
    }

    def __init__(self, window_size: int = 100, log_file: str = "symbolic_recall.log"):
        self.window_size = window_size
        self.log_file = Path(log_file)
        self.memory_window = deque(maxlen=window_size)
        self.glyph_history = deque(maxlen=window_size * 3)
        self.pattern_cache: dict[str, float] = {}
        self.current_state: Optional[SpindleState] = None
        self.spin_cycles = 0

        # Pattern detection
        self.recurring_sequences: dict[str, int] = {}
        self.emergent_patterns: list[dict] = []

        logger.info("🌀 Memory Spindle initialized")
        logger.info(f"   Window size: {window_size}")
        logger.info(f"   Log file: {log_file}")

    def add_memory(self, glyphs: list[str], entropy_score: float, entropy_class: str, content: dict):
        """Add a memory to the spindle"""
        self.memory_window.append(
            {
                "glyphs": glyphs,
                "entropy_score": entropy_score,
                "entropy_class": entropy_class,
                "content": content,
                "timestamp": datetime.now(timezone.utc),
            }
        )

        # Add glyphs to history
        self.glyph_history.extend(glyphs)

        # Log addition
        self._log_event(
            "memory_added",
            {"glyphs": glyphs, "entropy": entropy_score, "class": entropy_class},
        )

    def spin(self) -> SpindleState:
        """
        Perform one spin cycle, detecting patterns and updating state
        """
        if not self.memory_window:
            return self._create_empty_state()

        self.spin_cycles += 1

        # Calculate spin parameters
        entropy_classes = [m["entropy_class"] for m in self.memory_window]
        dominant_class = Counter(entropy_classes).most_common(1)[0][0]

        # Determine spin speed based on entropy
        speed_range = self.ENTROPY_SPIN_MAP[dominant_class]
        avg_entropy = sum(m["entropy_score"] for m in self.memory_window) / len(self.memory_window)
        spin_speed = speed_range[0] + (speed_range[1] - speed_range[0]) * avg_entropy

        # Detect patterns
        patterns = self._detect_patterns()
        pattern_strength = self._calculate_pattern_strength(patterns)

        # Calculate coherence
        coherence = self._calculate_coherence()

        # Get dominant glyphs
        glyph_counts = Counter(self.glyph_history)
        dominant_glyphs = [g for g, _ in glyph_counts.most_common(3)]

        # Create new state
        self.current_state = SpindleState(
            rotation_speed=spin_speed,
            coherence=coherence,
            dominant_glyphs=dominant_glyphs,
            entropy_class=dominant_class,
            pattern_strength=pattern_strength,
            active_memories=len(self.memory_window),
            timestamp=datetime.now(timezone.utc),
        )

        # Check for emergent patterns
        self._check_emergence(patterns, pattern_strength)

        # Log spin cycle
        self._log_event(
            "spin_cycle",
            {
                "cycle": self.spin_cycles,
                "speed": spin_speed,
                "coherence": coherence,
                "patterns": len(patterns),
                "state": self.current_state.to_symbolic(),
            },
        )

        return self.current_state

    def _detect_patterns(self) -> list[tuple[str, int]]:
        """Detect recurring glyph sequences"""
        patterns = []

        # Check 2-glyph sequences
        for i in range(len(self.glyph_history) - 1):
            seq = f"{self.glyph_history[i]}→{self.glyph_history[i + 1]}"
            self.recurring_sequences[seq] = self.recurring_sequences.get(seq, 0) + 1

        # Check 3-glyph sequences
        for i in range(len(self.glyph_history) - 2):
            seq = f"{self.glyph_history[i]}→{self.glyph_history[i + 1]}→{self.glyph_history[i + 2]}"
            self.recurring_sequences[seq] = self.recurring_sequences.get(seq, 0) + 1

        # Find significant patterns
        for seq, count in self.recurring_sequences.items():
            if count >= 3:  # Minimum recurrence threshold
                patterns.append((seq, count))

        # Sort by frequency
        patterns.sort(key=lambda x: x[1], reverse=True)

        return patterns[:10]  # Top 10 patterns

    def _calculate_pattern_strength(self, patterns: list[tuple[str, int]]) -> float:
        """Calculate overall pattern strength"""
        if not patterns:
            return 0.0

        # Weight by recurrence and length
        total_strength = 0.0
        for pattern, count in patterns:
            arrows = pattern.count("→")
            length_weight = (arrows + 1) * 0.3  # Longer patterns weighted more
            freq_weight = min(count / 10, 1.0)  # Frequency weight
            total_strength += length_weight * freq_weight

        # Normalize
        return min(total_strength / len(patterns), 1.0)

    def _calculate_coherence(self) -> float:
        """Calculate memory coherence based on glyph stability"""
        if len(self.glyph_history) < 2:
            return 1.0

        # Count transitions vs repetitions
        transitions = 0
        repetitions = 0

        for i in range(len(self.glyph_history) - 1):
            if self.glyph_history[i] == self.glyph_history[i + 1]:
                repetitions += 1
            else:
                transitions += 1

        # Coherence is higher with balanced transitions
        total = transitions + repetitions
        if total == 0:
            return 0.5

        # Optimal ratio is around 0.7 transitions
        optimal_ratio = 0.7
        actual_ratio = transitions / total
        coherence = 1.0 - abs(actual_ratio - optimal_ratio) / optimal_ratio

        return max(0.0, min(1.0, coherence))

    def _check_emergence(self, patterns: list[tuple[str, int]], strength: float):
        """Check for emergent symbolic patterns"""
        if strength > self.PATTERN_THRESHOLDS["strong"]:
            # Strong pattern detected
            emergence = {
                "timestamp": datetime.now(timezone.utc),
                "strength": strength,
                "type": "crystallized" if strength > 0.9 else "strong",
                "dominant_pattern": patterns[0] if patterns else None,
                "spindle_state": self.current_state.to_symbolic(),
                "insight": self._generate_insight(patterns),
            }

            self.emergent_patterns.append(emergence)

            logger.info("✨ Emergent pattern detected!")
            logger.info(f"   Strength: {strength:.3f}")
            logger.info(f"   Pattern: {emergence['dominant_pattern']}")
            logger.info(f"   Insight: {emergence['insight']}")

            self._log_event("emergence", emergence)

    def _generate_insight(self, patterns: list[tuple[str, int]]) -> str:
        """Generate symbolic insight from patterns"""
        if not patterns:
            return "No clear pattern"

        # Analyze dominant pattern
        dominant = patterns[0][0]
        glyphs = dominant.split("→")

        # Generate insight based on glyph transitions
        insights = {
            "🔐→🔓": "Trust building observed",
            "🔓→🔐": "Security concerns arising",
            "🌿→🌀": "Stability transitioning to change",
            "🌀→🌪️": "Increasing turbulence detected",
            "🌪️→🌿": "Chaos resolving to stability",
            "🧬→🌱": "Organic growth pattern",
            "🪷→🌸": "Consent flourishing",
            "🌸→🥀": "Trust degradation warning",
        }

        # Check for known insights
        for pattern, insight in insights.items():
            if pattern in dominant:
                return insight

        # Generic insight
        if len(set(glyphs)) == 1:
            return f"Stable {glyphs[0]} state maintained"
        else:
            return f"Complex transition: {' to '.join(glyphs)}"

    def _create_empty_state(self) -> SpindleState:
        """Create empty/default spindle state"""
        return SpindleState(
            rotation_speed=0.0,
            coherence=1.0,
            dominant_glyphs=[],
            entropy_class="stable",
            pattern_strength=0.0,
            active_memories=0,
            timestamp=datetime.now(timezone.utc),
        )

    def _log_event(self, event_type: str, data: dict):
        """Log spindle events to file"""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event_type,
            "data": data,
        }

        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    def get_recall_recommendations(self) -> list[dict]:
        """Get memory recall recommendations based on patterns"""
        if not self.current_state:
            return []

        recommendations = []

        # Recommend based on pattern strength
        if self.current_state.pattern_strength > 0.7:
            recommendations.append(
                {
                    "type": "strong_pattern",
                    "action": "reinforce",
                    "glyphs": self.current_state.dominant_glyphs,
                    "reason": "Strong pattern detected - reinforce for stability",
                }
            )

        # Recommend based on coherence
        if self.current_state.coherence < 0.4:
            recommendations.append(
                {
                    "type": "low_coherence",
                    "action": "stabilize",
                    "glyphs": ["🌿", "🧘", "💎"],
                    "reason": "Low coherence - introduce stabilizing elements",
                }
            )

        # Recommend based on spin speed
        if self.current_state.rotation_speed > 0.8:
            recommendations.append(
                {
                    "type": "high_spin",
                    "action": "slow_down",
                    "glyphs": ["🌊", "🧘", "🌿"],
                    "reason": "High spin rate - reduce to prevent memory fragmentation",
                }
            )

        return recommendations

    def export_spindle_state(self) -> dict:
        """Export complete spindle state and patterns"""
        return {
            "current_state": asdict(self.current_state) if self.current_state else None,
            "spin_cycles": self.spin_cycles,
            "memory_count": len(self.memory_window),
            "top_patterns": list(self.recurring_sequences.items())[:10],
            "emergent_patterns": self.emergent_patterns[-5:],  # Last 5
            "recommendations": self.get_recall_recommendations(),
            "glyph_distribution": dict(Counter(self.glyph_history).most_common(10)),
        }


# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    # Create spindle
    spindle = MemorySpindle(window_size=50, log_file="test_spindle.log")

    # Simulate memory additions with patterns
    test_memories = [
        (["🔐", "🧬", "🪷"], 0.15, "stable", {"event": "login"}),
        (["🔓", "🌱", "🌸"], 0.25, "stable", {"event": "grant"}),
        (["🔓", "🌱", "🌸"], 0.22, "stable", {"event": "access"}),
        (["🌿", "🌀", "🌪️"], 0.65, "neutral", {"event": "drift"}),
        (["🔐", "🧬", "🪷"], 0.18, "stable", {"event": "verify"}),
        (["🔓", "🌱", "🌸"], 0.20, "stable", {"event": "confirm"}),
        (["🌪️", "🌀", "🌿"], 0.78, "unstable", {"event": "recover"}),
        (["🔐", "🧬", "🪷"], 0.12, "stable", {"event": "secure"}),
    ]

    print("🌀 Memory Spindle Demo")
    print("=" * 60)

    # Add memories and spin
    for glyphs, entropy, entropy_class, content in test_memories:
        spindle.add_memory(glyphs, entropy, entropy_class, content)
        state = spindle.spin()

        print(f"\n🔄 Spin cycle {spindle.spin_cycles}")
        print(f"   State: {state.to_symbolic()}")
        print(f"   Speed: {state.rotation_speed:.2f}")
        print(f"   Coherence: {state.coherence:.2f}")
        print(f"   Pattern strength: {state.pattern_strength:.2f}")

    # Show final analysis
    print("\n📊 Spindle Analysis")
    print("-" * 40)

    final_state = spindle.export_spindle_state()

    print("\n🔝 Top Patterns:")
    for pattern, count in final_state["top_patterns"][:5]:
        print(f"   {pattern}: {count} times")

    print("\n💡 Recommendations:")
    for rec in final_state["recommendations"]:
        print(f"   {rec['type']}: {rec['reason']}")
        print(f"   Action: {rec['action']} with {' '.join(rec['glyphs'])}")
