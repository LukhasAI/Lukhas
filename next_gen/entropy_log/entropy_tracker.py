#!/usr/bin/env python3
"""
Entropy Drift Journal - Tracks symbolic decision entropy over time
Monitors trust transitions and calculates Shannon entropy for behavioral patterns
"""

import json
import logging
import math
import random
from collections import Counter, deque
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class EntropyEntry:
    """Single entropy measurement in the drift journal"""

    timestamp: datetime
    entropy_score: float
    previous_state: str
    current_state: str
    drift_class: str  # stable, neutral, unstable
    symbolic_path: list[str]
    transition_type: str
    notes: str = ""
    tags: list[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "entropy_score": round(self.entropy_score, 4),
            "previous_state": self.previous_state,
            "current_state": self.current_state,
            "drift_class": self.drift_class,
            "symbolic_path": self.symbolic_path,
            "transition_type": self.transition_type,
            "notes": self.notes,
            "tags": self.tags or [],
        }


class EntropyTracker:
    """
    Tracks symbolic decision entropy and drift patterns
    Calculates Shannon entropy for trust state transitions
    """

    # Symbolic states and their drift representations
    TRUST_STATES = {
        "stable": "🌿",
        "growing": "🌱",
        "neutral": "🪷",
        "shifting": "🌀",
        "turbulent": "🌪️",
        "decaying": "🥀",
        "locked": "🔒",
        "open": "🔓",
    }

    # State transition types
    TRANSITIONS = {
        "consent_grant": ["locked", "neutral", "growing", "open"],
        "consent_revoke": ["open", "shifting", "turbulent", "locked"],
        "trust_increase": ["neutral", "growing", "stable"],
        "trust_decrease": ["stable", "shifting", "turbulent"],
        "drift_correction": ["turbulent", "shifting", "neutral"],
        "emergency_lock": ["*", "locked"],  # From any state
    }

    # Drift classification thresholds
    DRIFT_THRESHOLDS = {
        "stable": (0.0, 0.3),
        "neutral": (0.3, 0.7),
        "unstable": (0.7, 1.0),
    }

    def __init__(self, journal_path: str = "entropy_journal.json", window_size: int = 100):
        self.journal_path = Path(journal_path)
        self.window_size = window_size
        self.transition_history = deque(maxlen=window_size)
        self.entropy_history = deque(maxlen=window_size)
        self.current_state = "neutral"
        self.journal_entries: list[EntropyEntry] = []

        # Load existing journal
        self._load_journal()

        logger.info("📊 Entropy Tracker initialized")
        logger.info(f"   Journal: {self.journal_path}")
        logger.info(f"   Window size: {window_size}")

    def _load_journal(self):
        """Load existing journal entries"""
        if self.journal_path.exists():
            try:
                with open(self.journal_path) as f:
                    data = json.load(f)

                # Restore entries
                for entry_data in data.get("entries", []):
                    entry = EntropyEntry(
                        timestamp=datetime.fromisoformat(entry_data["timestamp"]),
                        entropy_score=entry_data["entropy_score"],
                        previous_state=entry_data["previous_state"],
                        current_state=entry_data["current_state"],
                        drift_class=entry_data["drift_class"],
                        symbolic_path=entry_data["symbolic_path"],
                        transition_type=entry_data["transition_type"],
                        notes=entry_data.get("notes", ""),
                        tags=entry_data.get("tags", []),
                    )
                    self.journal_entries.append(entry)

                    # Update history windows
                    self.transition_history.append((entry.previous_state, entry.current_state))
                    self.entropy_history.append(entry.entropy_score)

                # Set current state
                if self.journal_entries:
                    self.current_state = self.journal_entries[-1].current_state

                logger.info(f"📖 Loaded {len(self.journal_entries)} journal entries")
            except Exception as e:
                logger.warning(f"Could not load journal: {e}")

    def _save_journal(self):
        """Save journal entries to file"""
        data = {
            "metadata": {
                "version": "1.0.0",
                "window_size": self.window_size,
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "total_entries": len(self.journal_entries),
            },
            "entries": [entry.to_dict() for entry in self.journal_entries],
        }

        with open(self.journal_path, "w") as f:
            json.dump(data, f, indent=2)

    def calculate_shannon_entropy(self, transitions: list[tuple[str, str]]) -> float:
        """
        Calculate Shannon entropy for state transitions
        H = -Σ p(x) * log2(p(x))
        """
        if not transitions:
            return 0.0

        # Count transition frequencies
        transition_counts = Counter(transitions)
        total = len(transitions)

        # Calculate entropy
        entropy = 0.0
        for count in transition_counts.values():
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)

        # Normalize to 0-1 range
        # Maximum entropy is log2(n) where n is number of unique transitions
        max_entropy = math.log2(len(transition_counts)) if len(transition_counts) > 1 else 1
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0

        return min(1.0, normalized_entropy)

    def classify_drift(self, entropy_score: float) -> str:
        """Classify drift based on entropy score"""
        for drift_class, (min_val, max_val) in self.DRIFT_THRESHOLDS.items():
            if min_val <= entropy_score < max_val:
                return drift_class
        return "unstable"

    def generate_symbolic_path(self, transition_type: str, entropy_score: float) -> list[str]:
        """Generate symbolic representation of the drift path"""
        path = []

        # Start symbol based on transition type
        if "consent" in transition_type:
            path.append("🔐")
        elif "trust" in transition_type:
            path.append("🤝")
        elif "drift" in transition_type:
            path.append("🌀")
        elif "emergency" in transition_type:
            path.append("🚨")

        # Middle symbol based on entropy
        if entropy_score < 0.3:
            path.append("🌿")  # Stable
        elif entropy_score < 0.7:
            path.append("🪷")  # Neutral
        else:
            path.append("🌪️")  # Turbulent

        # End symbol based on current state
        path.append(self.TRUST_STATES.get(self.current_state, "❓"))

        return path

    def track_transition(
        self,
        transition_type: str,
        new_state: Optional[str] = None,
        notes: str = "",
        tags: Optional[list[str]] = None,
    ) -> EntropyEntry:
        """
        Track a state transition and calculate entropy
        """
        # Determine new state
        if new_state is None:
            # Use predefined transition paths
            if transition_type in self.TRANSITIONS:
                path = self.TRANSITIONS[transition_type]
                if path[0] == "*" or self.current_state in path[:-1]:
                    new_state = path[-1]
                else:
                    # Find closest state in path
                    new_state = path[0]
            else:
                # Random transition for unknown types
                new_state = random.choice(list(self.TRUST_STATES.keys()))

        previous_state = self.current_state

        # Record transition
        transition = (previous_state, new_state)
        self.transition_history.append(transition)

        # Calculate entropy
        entropy_score = self.calculate_shannon_entropy(list(self.transition_history))
        self.entropy_history.append(entropy_score)

        # Classify drift
        drift_class = self.classify_drift(entropy_score)

        # Generate symbolic path
        symbolic_path = self.generate_symbolic_path(transition_type, entropy_score)

        # Create entry
        entry = EntropyEntry(
            timestamp=datetime.now(timezone.utc),
            entropy_score=entropy_score,
            previous_state=previous_state,
            current_state=new_state,
            drift_class=drift_class,
            symbolic_path=symbolic_path,
            transition_type=transition_type,
            notes=notes,
            tags=tags or [],
        )

        # Update state
        self.current_state = new_state
        self.journal_entries.append(entry)

        # Save journal
        self._save_journal()

        # Log the transition
        logger.info(
            f"📊 Transition: {self.TRUST_STATES.get(previous_state, previous_state)} → "
            f"{self.TRUST_STATES.get(new_state, new_state)} "
            f"(entropy: {entropy_score:.3f}, drift: {drift_class})"
        )
        logger.info(f"   Path: {' → '.join(symbolic_path)}")

        return entry

    def get_drift_vector(self, window: Optional[int] = None) -> list[str]:
        """Get symbolic drift vector over time window"""
        entries = self.journal_entries[-(window or self.window_size) :]

        if not entries:
            return ["🌿"]  # Default stable

        # Extract drift progression
        vector = []
        for entry in entries:
            state_symbol = self.TRUST_STATES.get(entry.current_state, "❓")
            if not vector or vector[-1] != state_symbol:
                vector.append(state_symbol)

        return vector

    def get_entropy_statistics(self) -> dict:
        """Calculate entropy statistics"""
        if not self.entropy_history:
            return {
                "mean": 0.0,
                "std": 0.0,
                "min": 0.0,
                "max": 0.0,
                "current": 0.0,
                "trend": "stable",
            }

        entropy_list = list(self.entropy_history)
        mean = sum(entropy_list) / len(entropy_list)

        # Calculate standard deviation
        variance = sum((x - mean) ** 2 for x in entropy_list) / len(entropy_list)
        std = math.sqrt(variance)

        # Determine trend
        if len(entropy_list) >= 3:
            recent = entropy_list[-3:]
            if all(recent[i] <= recent[i + 1] for i in range(len(recent) - 1)):
                trend = "increasing"
            elif all(recent[i] >= recent[i + 1] for i in range(len(recent) - 1)):
                trend = "decreasing"
            else:
                trend = "fluctuating"
        else:
            trend = "insufficient_data"

        return {
            "mean": round(mean, 4),
            "std": round(std, 4),
            "min": round(min(entropy_list), 4),
            "max": round(max(entropy_list), 4),
            "current": round(entropy_list[-1], 4),
            "trend": trend,
        }

    def export_report(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> dict:
        """Export entropy analysis report"""
        # Filter entries by date
        entries = self.journal_entries
        if start_date:
            entries = [e for e in entries if e.timestamp >= start_date]
        if end_date:
            entries = [e for e in entries if e.timestamp <= end_date]

        # Analyze transitions
        transition_counts = Counter(e.transition_type for e in entries)
        drift_counts = Counter(e.drift_class for e in entries)

        # Get drift vector
        drift_vector = self.get_drift_vector()

        return {
            "period": {
                "start": start_date.isoformat() if start_date else "beginning",
                "end": end_date.isoformat() if end_date else "current",
            },
            "summary": {
                "total_transitions": len(entries),
                "unique_states": len({e.current_state for e in entries}),
                "entropy_stats": self.get_entropy_statistics(),
            },
            "transitions": dict(transition_counts),
            "drift_distribution": dict(drift_counts),
            "drift_vector": " → ".join(drift_vector),
            "recent_entries": [e.to_dict() for e in entries[-5:]],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }


# Simulation and testing
def simulate_entropy_tracking():
    """Simulate entropy tracking with various transitions"""
    tracker = EntropyTracker("entropy_journal_demo.json")

    # Simulation scenarios
    scenarios = [
        ("consent_grant", "User grants biometric access", ["privacy", "biometric"]),
        ("trust_increase", "Successful authentication", ["auth", "success"]),
        ("trust_increase", "Profile completion", ["profile"]),
        ("consent_grant", "Location sharing enabled", ["location", "privacy"]),
        ("trust_decrease", "Failed login attempt", ["auth", "failure"]),
        ("trust_decrease", "Suspicious activity", ["security", "alert"]),
        ("consent_revoke", "User disables tracking", ["privacy", "revoke"]),
        ("drift_correction", "System stabilization", ["maintenance"]),
        ("emergency_lock", "Security breach detected", ["security", "critical"]),
    ]

    print("🎯 Entropy Tracking Simulation")
    print("=" * 60)

    for transition_type, notes, tags in scenarios:
        entry = tracker.track_transition(transition_type, notes=notes, tags=tags)

        print(f"\n📊 {transition_type.upper()}")
        print(
            f"   State: {tracker.TRUST_STATES.get(entry.previous_state, entry.previous_state)} → "
            f"{tracker.TRUST_STATES.get(entry.current_state, entry.current_state)}"
        )
        print(f"   Entropy: {entry.entropy_score:.3f} ({entry.drift_class})")
        print(f"   Path: {' → '.join(entry.symbolic_path)}")

        # Brief pause for readability
        import time

        time.sleep(0.5)

    # Show final statistics
    print("\n" + "=" * 60)
    print("📈 ENTROPY STATISTICS")
    stats = tracker.get_entropy_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    print(f"\n🌀 Drift Vector: {' → '.join(tracker.get_drift_vector())}")

    # Export report
    report = tracker.export_report()
    print("\n📋 Report Summary:")
    print(f"   Total transitions: {report['summary']['total_transitions']}")
    print(f"   Drift distribution: {report['drift_distribution']}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    simulate_entropy_tracking()
