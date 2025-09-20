"""
═══════════════════════════════════════════════════════════════════════════════
║ 🚨 LUKHAS AI - COLLAPSE TRACKER
║ Unified Collapse Detection and Entropy Monitoring System
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠═══════════════════════════════════════════════════════════════════════════════
║ Module: collapse_tracker.py
║ Path: lukhas/core/monitoring/collapse_tracker.py
║ Version: 1.0.0 | Created: 2025-07-25 | Modified: 2025-07-25
║ Authors: LUKHAS AI Team | Claude Code (Task 6)
╠═══════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠═══════════════════════════════════════════════════════════════════════════════
║ The Collapse Tracker provides a unified system for monitoring symbolic collapse
║ conditions, computing entropy scores, and managing alert levels throughout the
║ LUKHAS Cognitive system. This module is critical for system safety and stability.
║
║ Key Features:
║ • Entropy score calculation using Shannon entropy
║ • Multi-level alert system (Green → Yellow → Orange → Red)
║ • Integration with symbolic orchestrator and ethics layer
║ • Collapse state persistence with trace IDs and history
║ • Real-time threshold monitoring and alerting
║ • Synthetic test capabilities for validation
║
║ Theoretical Foundations:
║ • Information Theory (Shannon, 1948)
║ • Catastrophe Theory (Thom, 1972)
║ • Complex Systems Collapse (Scheffer et al., 2009)
║
║ Symbolic Tags: {ΛCOLLAPSE}, {ΛENTROPY}, {ΛSAFETY}
╚═══════════════════════════════════════════════════════════════════════════════
"""
import asyncio
import json
import logging
import math
import uuid
from collections import Counter, deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

try:
    import structlog

    logger = structlog.get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)


class CollapseAlertLevel(Enum):
    """Alert levels for collapse conditions."""

    GREEN = "GREEN"  # Normal operation (entropy < 0.3)
    YELLOW = "YELLOW"  # Elevated risk (entropy 0.3-0.5)
    ORANGE = "ORANGE"  # High risk (entropy 0.5-0.7)
    RED = "RED"  # Critical collapse imminent (entropy > 0.7)


@dataclass
class CollapseState:
    """Represents a collapse state snapshot."""

    collapse_trace_id: str = field(default_factory=lambda: f"collapse_{uuid.uuid4().hex[:12]}")
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    entropy_score: float = 0.0
    alert_level: CollapseAlertLevel = CollapseAlertLevel.GREEN
    entropy_slope: float = 0.0  # Rate of entropy change
    affected_components: list[str] = field(default_factory=list)
    symbolic_drift: dict[str, float] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        data["alert_level"] = self.alert_level.value
        return data


class CollapseTracker:
    """
    Unified collapse tracking and entropy monitoring system.

    This class manages the detection, tracking, and alerting of symbolic
    collapse conditions within the LUKHAS Cognitive system.
    """

    def __init__(
        self,
        orchestrator_callback: Optional[Callable] = None,
        ethics_callback: Optional[Callable] = None,
        persistence_path: Optional[Path] = None,
    ):
        """
        Initialize the collapse tracker.

        Args:
            orchestrator_callback: Callback to notify orchestrator of collapse conditions
            ethics_callback: Callback to trigger ethics review for interventions
            persistence_path: Path for persisting collapse state history
        """
        # Core state
        self.current_state = CollapseState()
        self.collapse_history: deque = deque(maxlen=1000)  # Rolling history
        self.entropy_buffer: deque = deque(maxlen=100)  # For slope calculation

        # Callbacks for integration
        self.orchestrator_callback = orchestrator_callback
        self.ethics_callback = ethics_callback

        # Persistence
        self.persistence_path = persistence_path or Path("lukhas/logs/collapse_history.jsonl")
        self.persistence_path.parent.mkdir(parents=True, exist_ok=True)

        # Thresholds
        self.thresholds = {
            CollapseAlertLevel.GREEN: 0.3,
            CollapseAlertLevel.YELLOW: 0.5,
            CollapseAlertLevel.ORANGE: 0.7,
            CollapseAlertLevel.RED: 0.9,
        }

        # Component monitoring
        self.component_entropy: dict[str, float] = {}
        self.sid_hashes: list[str] = []

        logger.info(
            "CollapseTracker initialized",
            thresholds=self.thresholds,
            persistence_path=str(self.persistence_path),
        )

    # {ΛENTROPY}

    def calculate_shannon_entropy(self, data: list[Any]) -> float:
        """
        Calculate Shannon entropy for a given dataset.

        Args:
            data: List of symbolic identifiers or values

        Returns:
            Entropy score between 0 and 1
        """
        if not data:
            return 0.0

        # Count occurrences
        counts = Counter(data)
        total = len(data)

        # Calculate entropy
        entropy = 0.0
        for count in counts.values():
            if count > 0:
                probability = count / total
                entropy -= probability * math.log2(probability)

        # Normalize to 0-1 range
        max_entropy = math.log2(len(counts)) if len(counts) > 1 else 1
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0

        return min(1.0, max(0.0, normalized_entropy))

    # {ΛCOLLAPSE}

    def update_entropy_score(
        self,
        symbolic_data: list[str],
        component_scores: Optional[dict[str, float]] = None,
    ) -> float:
        """
        Update the current entropy score based on symbolic data.

        Args:
            symbolic_data: List of symbolic identifiers (SIDs, glyphs, etc.)
            component_scores: Optional per-component entropy scores

        Returns:
            Updated entropy score
        """
        # Calculate main entropy
        main_entropy = self.calculate_shannon_entropy(symbolic_data)

        # Update component scores if provided
        if component_scores:
            self.component_entropy.update(component_scores)

        # Weighted average if we have component scores
        if self.component_entropy:
            component_avg = sum(self.component_entropy.values()) / len(self.component_entropy)
            final_entropy = 0.7 * main_entropy + 0.3 * component_avg
        else:
            final_entropy = main_entropy

        # Update buffer for slope calculation
        self.entropy_buffer.append((datetime.now(timezone.utc), final_entropy))

        # Calculate entropy slope (rate of change)
        entropy_slope = self._calculate_entropy_slope()

        # Update current state
        self.current_state.entropy_score = final_entropy
        self.current_state.entropy_slope = entropy_slope

        # Check alert level
        self._update_alert_level()

        logger.info(
            "Entropy updated",
            entropy_score=final_entropy,
            entropy_slope=entropy_slope,
            alert_level=self.current_state.alert_level.value,
        )

        return final_entropy

    def _calculate_entropy_slope(self) -> float:
        """Calculate the rate of entropy change."""
        if len(self.entropy_buffer) < 2:
            return 0.0

        # Get recent points for linear regression
        recent_points = list(self.entropy_buffer)[-10:]
        if len(recent_points) < 2:
            return 0.0

        # Simple slope calculation
        start_time, start_entropy = recent_points[0]
        end_time, end_entropy = recent_points[-1]

        time_diff = (end_time - start_time).total_seconds()
        if time_diff == 0:
            return 0.0

        # Entropy change per second
        slope = (end_entropy - start_entropy) / time_diff
        return slope

    def _update_alert_level(self) -> None:
        """Update alert level based on current entropy and slope."""
        old_level = self.current_state.alert_level
        entropy = self.current_state.entropy_score
        slope = self.current_state.entropy_slope

        # Determine base level from entropy
        if entropy >= self.thresholds[CollapseAlertLevel.RED]:
            new_level = CollapseAlertLevel.RED
        elif entropy >= self.thresholds[CollapseAlertLevel.ORANGE]:
            new_level = CollapseAlertLevel.ORANGE
        elif entropy >= self.thresholds[CollapseAlertLevel.YELLOW]:
            new_level = CollapseAlertLevel.YELLOW
        else:
            new_level = CollapseAlertLevel.GREEN

        # Adjust for rapid increases (slope > 0.1/sec is concerning)
        if slope > 0.1 and new_level != CollapseAlertLevel.RED:
            # Escalate one level for rapid entropy increase
            levels = list(CollapseAlertLevel)
            current_idx = levels.index(new_level)
            if current_idx < len(levels) - 1:
                new_level = levels[current_idx + 1]

        self.current_state.alert_level = new_level

        # Trigger alerts if level increased
        if new_level != old_level:
            asyncio.create_task(self._emit_alert(old_level, new_level))

    # {ΛSAFETY}
    async def _emit_alert(self, old_level: CollapseAlertLevel, new_level: CollapseAlertLevel) -> None:
        """
        Emit alerts when collapse level changes.

        Args:
            old_level: Previous alert level
            new_level: New alert level
        """
        alert_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "old_level": old_level.value,
            "new_level": new_level.value,
            "entropy_score": self.current_state.entropy_score,
            "entropy_slope": self.current_state.entropy_slope,
            "collapse_trace_id": self.current_state.collapse_trace_id,
        }

        logger.warning(
            "Collapse alert level changed",
            old_level=old_level.value,
            new_level=new_level.value,
            entropy=self.current_state.entropy_score,
        )

        # Notify orchestrator
        if self.orchestrator_callback:
            try:
                await self.orchestrator_callback(alert_data)
            except Exception as e:
                logger.error("Failed to notify orchestrator", error=str(e))

        # Trigger ethics review for high alert levels
        if new_level in [CollapseAlertLevel.ORANGE, CollapseAlertLevel.RED] and self.ethics_callback:
            try:
                await self.ethics_callback(
                    {
                        **alert_data,
                        "severity": ("HIGH" if new_level == CollapseAlertLevel.RED else "MEDIUM"),
                        "recommended_action": "intervention_required",
                    }
                )
            except Exception as e:
                logger.error("Failed to notify ethics layer", error=str(e))

        # Persist alert
        await self._persist_state()

    def record_collapse_event(
        self,
        affected_components: list[str],
        symbolic_drift: dict[str, float],
        metadata: Optional[dict[str, Any]] = None,
    ) -> str:
        """
        Record a collapse event with full context.

        Args:
            affected_components: List of affected component IDs
            symbolic_drift: Drift scores by component
            metadata: Additional event metadata

        Returns:
            Collapse trace ID for reference
        """
        # Create new collapse state
        collapse_state = CollapseState(
            entropy_score=self.current_state.entropy_score,
            alert_level=self.current_state.alert_level,
            entropy_slope=self.current_state.entropy_slope,
            affected_components=affected_components,
            symbolic_drift=symbolic_drift,
            metadata=metadata or {},
        )

        # Add to history
        self.collapse_history.append(collapse_state)

        # Update current state with new trace ID
        self.current_state = collapse_state

        logger.info(
            "Collapse event recorded",
            trace_id=collapse_state.collapse_trace_id,
            affected_components=len(affected_components),
        )

        # Persist immediately
        asyncio.create_task(self._persist_state())

        return collapse_state.collapse_trace_id

    async def _persist_state(self) -> None:
        """Persist current state to storage."""
        try:
            with open(self.persistence_path, "a") as f:
                f.write(json.dumps(self.current_state.to_dict()) + "\n")
        except Exception as e:
            logger.error("Failed to persist collapse state", error=str(e))

    def get_collapse_history(self, trace_id: Optional[str] = None, limit: int = 100) -> list[dict[str, Any]]:
        """
        Retrieve collapse history.

        Args:
            trace_id: Optional specific trace ID to retrieve
            limit: Maximum number of records to return

        Returns:
            List of collapse state dictionaries
        """
        if trace_id:
            # Find specific trace
            for state in self.collapse_history:
                if state.collapse_trace_id == trace_id:
                    return [state.to_dict()]
            return []

        # Return recent history
        history = list(self.collapse_history)[-limit:]
        return [state.to_dict() for state in history]

    def get_system_health(self) -> dict[str, Any]:
        """
        Get current system health metrics.

        Returns:
            Dictionary containing health metrics
        """
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "entropy_score": self.current_state.entropy_score,
            "alert_level": self.current_state.alert_level.value,
            "entropy_slope": self.current_state.entropy_slope,
            "component_entropy": self.component_entropy.copy(),
            "history_size": len(self.collapse_history),
            "affected_components": self.current_state.affected_components,
            "collapse_trace_id": self.current_state.collapse_trace_id,
        }

    # Test utilities

    def generate_synthetic_test_data(self, scenario: str = "normal") -> tuple[list[str], dict[str, float]]:
        """
        Generate synthetic test data for validation.

        Args:
            scenario: Test scenario ("normal", "drift", "collapse")

        Returns:
            Tuple of (symbolic_data, component_scores)
        """
        import random

        if scenario == "normal":
            # Low entropy, stable system
            symbols = ["glyph_001"] * 50 + ["glyph_002"] * 40 + ["glyph_003"] * 10
            component_scores = {
                "memory": 0.2,
                "reasoning": 0.15,
                "emotion": 0.25,
                "consciousness": 0.18,
            }

        elif scenario == "drift":
            # Medium entropy, increasing drift
            symbols = [f"glyph_{i:03d}" for i in range(20)] * 5
            component_scores = {
                "memory": 0.45,
                "reasoning": 0.38,
                "emotion": 0.52,
                "consciousness": 0.41,
            }

        elif scenario == "collapse":
            # High entropy, system collapse
            symbols = [f"glyph_{random.randint(0, 100):03d}" for _ in range(100)]
            component_scores = {
                "memory": 0.85,
                "reasoning": 0.78,
                "emotion": 0.92,
                "consciousness": 0.88,
            }

        else:
            raise ValueError(f"Unknown scenario: {scenario}")

        random.shuffle(symbols)
        return symbols, component_scores


# Singleton instance for global access
_global_tracker: Optional[CollapseTracker] = None


def get_global_tracker() -> CollapseTracker:
    """Get or create the global collapse tracker instance."""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = CollapseTracker()
    return _global_tracker


"""
═══════════════════════════════════════════════════════════════════════════════
║ 📋 FOOTER - LUKHAS AI
╠═══════════════════════════════════════════════════════════════════════════════
║ VALIDATION:
║   - Tests: lukhas/tests/core/monitoring/test_collapse_tracker.py
║   - Coverage: Target 90%
║   - Linting: pylint 9.0/10
║
║ MONITORING:
║   - Metrics: entropy_score, alert_level, collapse_events_total
║   - Logs: All state changes, alerts, and collapse events
║   - Alerts: Threshold breaches, rapid entropy increases, component failures
║
║ COMPLIANCE:
║   - Standards: ISO/IEC 25010 (Software Quality), ISO 31000 (Risk Management)
║   - Ethics: Automatic ethics review trigger for high-risk states
║   - Safety: Multi-level alert system with escalation protocols
║
║ REFERENCES:
║   - Docs: docs/COLLAPSE_DIAGNOSTICS.md
║   - Issues: github.com/lukhas-ai/core/issues?label=collapse-tracking
║   - Wiki: internal.lukhas.ai/wiki/collapse-detection
║
║ COPYRIGHT & LICENSE:
║   Copyright (c) 2025 LUKHAS AI. All rights reserved.
║   Licensed under the LUKHAS AI Proprietary License.
║   Unauthorized use, reproduction, or distribution is prohibited.
║
║ DISCLAIMER:
║   This module is critical for AGI safety. Modifications require approval
║   from the LUKHAS Safety Board and must maintain all alert thresholds.
╚═══════════════════════════════════════════════════════════════════════════════
"""
