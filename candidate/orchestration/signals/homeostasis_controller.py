#!/usr/bin/env python3
"""
Homeostasis Controller for LUKHAS Endocrine System
===================================================
Manages hormone-like signals to maintain system balance and health.
Based on GPT5 audit recommendations lines 271-275.
"""
from typing import List
import streamlit as st

import asyncio
import json
import logging
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

from candidate.orchestration.signals.signal_bus import Signal, SignalBus, SignalType

logger = logging.getLogger(__name__)


class HomeostasisState(Enum):
    """System homeostasis states"""

    BALANCED = "balanced"  # Optimal functioning
    STRESSED = "stressed"  # Under pressure but managing
    OVERLOADED = "overloaded"  # Too much activity
    UNDERUTILIZED = "underutilized"  # Not enough activity
    RECOVERING = "recovering"  # Returning to balance
    CRITICAL = "critical"  # Needs immediate intervention


@dataclass
class HormoneEmission:
    """Record of a hormone emission"""

    signal: Signal
    timestamp: float
    reason: str
    source_event: Optional[str] = None
    impact_score: float = 0.0
    cooldown_until: Optional[float] = None


@dataclass
class SystemMetrics:
    """Current system metrics for homeostasis"""

    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    request_rate: float = 0.0
    error_rate: float = 0.0
    response_time_ms: float = 0.0
    active_sessions: int = 0
    queue_depth: int = 0
    drift_score: float = 0.0


@dataclass
class HomeostasisPolicy:
    """Policy for homeostasis control"""

    # Thresholds for state transitions
    stress_threshold: float = 0.7
    overload_threshold: float = 0.9
    underutilized_threshold: float = 0.2
    critical_threshold: float = 0.95

    # Hormone emission policies
    max_emissions_per_minute: int = 10
    global_cooldown_ms: int = 100

    # Specific hormone policies
    hormone_policies: dict[str, dict[str, Any]] = field(
        default_factory=lambda: {
            "stress": {
                "threshold": 0.6,
                "cooldown_ms": 800,
                "max_level": 1.0,
                "decay_rate": 0.1,  # Per second
            },
            "novelty": {
                "threshold": 0.3,
                "cooldown_ms": 500,
                "max_level": 1.0,
                "decay_rate": 0.2,
            },
            "alignment_risk": {
                "threshold": 0.2,  # Lower threshold for safety
                "cooldown_ms": 0,  # No cooldown for safety
                "max_level": 1.0,
                "decay_rate": 0.05,  # Slow decay
            },
            "trust": {
                "threshold": 0.5,
                "cooldown_ms": 500,
                "max_level": 1.0,
                "decay_rate": 0.03,  # Very slow decay
            },
            "urgency": {
                "threshold": 0.7,
                "cooldown_ms": 300,
                "max_level": 1.0,
                "decay_rate": 0.3,  # Fast decay
            },
            "ambiguity": {
                "threshold": 0.4,
                "cooldown_ms": 700,
                "max_level": 1.0,
                "decay_rate": 0.15,
            },
        }
    )

    # Feedback loop parameters
    feedback_window_seconds: int = 60
    feedback_sensitivity: float = 0.5


class HomeostasisController:
    """
    Controls the LUKHAS endocrine system to maintain homeostasis.
    Translates system events into hormone signals with rate limiting.
    """

    def __init__(
        self,
        signal_bus: SignalBus,
        policy: Optional[HomeostasisPolicy] = None,
        audit_path: Optional[Path] = None,
    ):
        """
        Initialize the homeostasis controller.

        Args:
            signal_bus: Signal bus for hormone emissions
            policy: Homeostasis policy or None for defaults
            audit_path: Path for audit logs
        """
        self.signal_bus = signal_bus
        self.policy = policy or HomeostasisPolicy()
        self.audit_path = audit_path or Path("data/homeostasis_audit.jsonl")

        # Current state
        self.state = HomeostasisState.BALANCED
        self.current_hormones: dict[str, float] = {}
        self.metrics = SystemMetrics()

        # Emission tracking
        self.emission_history: deque = deque(maxlen=1000)
        self.last_emission_time: dict[str, float] = {}
        self.emissions_this_minute = 0
        self.minute_start = time.time()

        # Event handlers
        self.event_handlers: dict[str, Callable] = {}

        # Feedback tracking
        self.feedback_scores: deque = deque(maxlen=100)

        # Background tasks
        self.decay_task: Optional[asyncio.Task] = None
        self.monitor_task: Optional[asyncio.Task] = None

        # Initialize audit
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info("Homeostasis controller initialized")

    async def start(self):
        """Start the homeostasis controller"""
        # Start background tasks
        self.decay_task = asyncio.create_task(self._decay_loop())
        self.monitor_task = asyncio.create_task(self._monitor_loop())

        logger.info("Homeostasis controller started")

    async def stop(self):
        """Stop the homeostasis controller"""
        # Cancel background tasks
        if self.decay_task:
            self.decay_task.cancel()
        if self.monitor_task:
            self.monitor_task.cancel()

        # Wait for tasks to complete
        await asyncio.gather(self.decay_task, self.monitor_task, return_exceptions=True)

        logger.info("Homeostasis controller stopped")

    def process_event(self, event_type: str, event_data: dict[str, Any], source: str = "unknown") -> list[Signal]:
        """
        Process a system event and emit appropriate hormones.

        Args:
            event_type: Type of event
            event_data: Event data
            source: Event source

        Returns:
            List of emitted signals
        """
        # Update metrics based on event
        self._update_metrics_from_event(event_type, event_data)

        # Determine which hormones to emit
        hormones_to_emit = self._evaluate_hormone_needs(event_type, event_data)

        # Apply rate limiting and cooldowns
        allowed_hormones = self._apply_rate_limits(hormones_to_emit)

        # Emit signals
        emitted_signals = []
        for hormone_name, level, reason in allowed_hormones:
            signal = self._emit_hormone(hormone_name, level, source, reason, event_type)
            if signal:
                emitted_signals.append(signal)

        # Update state
        self._update_state()

        return emitted_signals

    def _update_metrics_from_event(self, event_type: str, event_data: dict[str, Any]):
        """Update system metrics based on event"""
        # Update based on event type
        if event_type == "request":
            self.metrics.request_rate = event_data.get("rate", self.metrics.request_rate)
            self.metrics.response_time_ms = event_data.get("response_time", self.metrics.response_time_ms)

        elif event_type == "error":
            self.metrics.error_rate = event_data.get("rate", self.metrics.error_rate)

        elif event_type == "resource":
            self.metrics.cpu_usage = event_data.get("cpu", self.metrics.cpu_usage)
            self.metrics.memory_usage = event_data.get("memory", self.metrics.memory_usage)

        elif event_type == "drift":
            self.metrics.drift_score = event_data.get("score", self.metrics.drift_score)

        elif event_type == "session":
            self.metrics.active_sessions = event_data.get("count", self.metrics.active_sessions)

        elif event_type == "queue":
            self.metrics.queue_depth = event_data.get("depth", self.metrics.queue_depth)

    def _evaluate_hormone_needs(self, event_type: str, event_data: dict[str, Any]) -> list[tuple[str, float, str]]:
        """
        Evaluate which hormones need to be emitted.

        Returns:
            List of (hormone_name, level, reason) tuples
        """
        hormones = []

        # Stress evaluation
        stress_level = self._calculate_stress_level()
        if stress_level > self.policy.hormone_policies["stress"]["threshold"]:
            hormones.append(
                (
                    "stress",
                    min(stress_level, 1.0),
                    f"System stress at {stress_level:.1%}",
                )
            )

        # Alignment risk evaluation
        if self.metrics.drift_score > self.policy.hormone_policies["alignment_risk"]["threshold"]:
            hormones.append(
                (
                    "alignment_risk",
                    min(self.metrics.drift_score, 1.0),
                    f"Drift detected: {self.metrics.drift_score:.2f}",
                )
            )

        # Novelty detection
        if event_type in ["new_pattern", "unusual_request", "unknown_input"]:
            novelty_level = event_data.get("novelty_score", 0.5)
            if novelty_level > self.policy.hormone_policies["novelty"]["threshold"]:
                hormones.append(
                    (
                        "novelty",
                        min(novelty_level, 1.0),
                        f"Novel pattern detected: {event_type}",
                    )
                )

        # Trust evaluation (based on session history)
        if event_type == "session" and event_data.get("established", False):
            trust_score = event_data.get("trust_score", 0.5)
            if trust_score > self.policy.hormone_policies["trust"]["threshold"]:
                hormones.append(
                    (
                        "trust",
                        min(trust_score, 1.0),
                        f"Established session trust: {trust_score:.2f}",
                    )
                )

        # Urgency detection
        if event_type in ["timeout", "deadline", "critical"]:
            urgency = event_data.get("urgency", 0.8)
            if urgency > self.policy.hormone_policies["urgency"]["threshold"]:
                hormones.append(("urgency", min(urgency, 1.0), f"Urgent event: {event_type}"))

        # Ambiguity detection
        if event_type in ["unclear_intent", "multiple_interpretations", "conflict"]:
            ambiguity = event_data.get("ambiguity_score", 0.6)
            if ambiguity > self.policy.hormone_policies["ambiguity"]["threshold"]:
                hormones.append(("ambiguity", min(ambiguity, 1.0), f"Ambiguous input: {event_type}"))

        return hormones

    def _calculate_stress_level(self) -> float:
        """Calculate overall system stress level"""
        # Weighted combination of metrics
        stress = 0.0

        # CPU stress
        stress += self.metrics.cpu_usage * 0.2

        # Memory stress
        stress += self.metrics.memory_usage * 0.2

        # Request rate stress (normalized)
        max_expected_rate = 100.0  # Requests per second
        stress += min(self.metrics.request_rate / max_expected_rate, 1.0) * 0.2

        # Error rate stress
        stress += self.metrics.error_rate * 0.15

        # Response time stress (normalized)
        target_response = 100.0  # Target ms
        stress += min(self.metrics.response_time_ms / (target_response * 10), 1.0) * 0.15

        # Queue depth stress (normalized)
        max_queue = 1000
        stress += min(self.metrics.queue_depth / max_queue, 1.0) * 0.1

        return min(stress, 1.0)

    def _apply_rate_limits(self, hormones: list[tuple[str, float, str]]) -> list[tuple[str, float, str]]:
        """Apply rate limiting and cooldowns to hormone emissions"""
        current_time = time.time()
        allowed = []

        # Check global rate limit
        if current_time - self.minute_start > 60:
            self.emissions_this_minute = 0
            self.minute_start = current_time

        if self.emissions_this_minute >= self.policy.max_emissions_per_minute:
            logger.warning(f"Rate limit reached: {self.emissions_this_minute} emissions this minute")
            return []

        # Check individual hormone cooldowns
        for hormone_name, level, reason in hormones:
            policy = self.policy.hormone_policies.get(hormone_name, {})
            cooldown_ms = policy.get("cooldown_ms", 0)

            if cooldown_ms > 0:
                last_emission = self.last_emission_time.get(hormone_name, 0)
                if (current_time - last_emission) * 1000 < cooldown_ms:
                    logger.debug(f"Hormone {hormone_name} in cooldown")
                    continue

            # Check global cooldown
            if self.emission_history:
                last_global = self.emission_history[-1].timestamp
                if (current_time - last_global) * 1000 < self.policy.global_cooldown_ms:
                    logger.debug("Global cooldown active")
                    continue

            allowed.append((hormone_name, level, reason))

        return allowed

    def _emit_hormone(
        self, hormone_name: str, level: float, source: str, reason: str, event_type: str
    ) -> Optional[Signal]:
        """Emit a hormone signal"""
        try:
            # Create signal
            signal_type = SignalType[hormone_name.upper()]
            signal = Signal(
                name=signal_type,
                level=level,
                source=f"homeostasis.{source}",
                metadata={
                    "reason": reason,
                    "event_type": event_type,
                    "state": self.state.value,
                    "timestamp": time.time(),
                },
            )

            # Emit via signal bus
            self.signal_bus.emit(signal)

            # Record emission
            emission = HormoneEmission(
                signal=signal,
                timestamp=time.time(),
                reason=reason,
                source_event=event_type,
                impact_score=level,
            )

            self.emission_history.append(emission)
            self.last_emission_time[hormone_name] = time.time()
            self.emissions_this_minute += 1

            # Update current hormone levels
            self.current_hormones[hormone_name] = level

            # Audit
            self._audit_emission(emission)

            logger.info(f"Emitted {hormone_name} hormone at level {level:.2f}: {reason}")

            return signal

        except Exception as e:
            logger.error(f"Failed to emit hormone {hormone_name}: {e}")
            return None

    def _update_state(self):
        """Update homeostasis state based on current conditions"""
        stress = self._calculate_stress_level()

        previous_state = self.state

        # Determine new state
        if stress >= self.policy.critical_threshold:
            self.state = HomeostasisState.CRITICAL
        elif stress >= self.policy.overload_threshold:
            self.state = HomeostasisState.OVERLOADED
        elif stress >= self.policy.stress_threshold:
            self.state = HomeostasisState.STRESSED
        elif stress <= self.policy.underutilized_threshold:
            self.state = HomeostasisState.UNDERUTILIZED
        elif previous_state in [HomeostasisState.STRESSED, HomeostasisState.OVERLOADED]:
            self.state = HomeostasisState.RECOVERING
        else:
            self.state = HomeostasisState.BALANCED

        # Log state changes
        if self.state != previous_state:
            logger.info(f"Homeostasis state changed: {previous_state.value} -> {self.state.value}")

            # Emit state change signal if critical
            if self.state == HomeostasisState.CRITICAL:
                self._emit_hormone(
                    "stress",
                    1.0,
                    "homeostasis",
                    "System entered critical state",
                    "state_change",
                )

    async def _decay_loop(self):
        """Background task to decay hormone levels"""
        while True:
            try:
                await asyncio.sleep(1.0)  # Decay every second

                # Decay each hormone
                for hormone_name in list(self.current_hormones.keys()):
                    policy = self.policy.hormone_policies.get(hormone_name, {})
                    decay_rate = policy.get("decay_rate", 0.1)

                    current = self.current_hormones[hormone_name]
                    new_level = max(0, current - decay_rate)

                    if new_level > 0:
                        self.current_hormones[hormone_name] = new_level
                    else:
                        del self.current_hormones[hormone_name]

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in decay loop: {e}")

    async def _monitor_loop(self):
        """Background task to monitor system health"""
        while True:
            try:
                await asyncio.sleep(5.0)  # Monitor every 5 seconds

                # Check for sustained stress
                if self.state in [
                    HomeostasisState.STRESSED,
                    HomeostasisState.OVERLOADED,
                ]:
                    sustained_duration = self._get_state_duration()
                    if sustained_duration > 30:  # 30 seconds
                        logger.warning(f"Sustained {self.state.value} for {sustained_duration}s")

                        # Emit warning signal
                        self._emit_hormone(
                            "stress",
                            0.9,
                            "monitor",
                            f"Sustained stress for {sustained_duration}s",
                            "monitor_alert",
                        )

                # Check for feedback loops
                self._detect_feedback_loops()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")

    def _get_state_duration(self) -> float:
        """Get duration of current state in seconds"""
        # Find last state change in emission history
        for emission in reversed(self.emission_history):
            if emission.source_event == "state_change":
                return time.time() - emission.timestamp

        return 0

    def _detect_feedback_loops(self):
        """Detect potential feedback loops in hormone emissions"""
        if len(self.emission_history) < 10:
            return

        # Check for rapid oscillations
        recent = list(self.emission_history)[-10:]
        hormone_counts = {}

        for emission in recent:
            hormone = emission.signal.name.value
            hormone_counts[hormone] = hormone_counts.get(hormone, 0) + 1

        # If same hormone emitted too frequently, it might be a loop
        for hormone, count in hormone_counts.items():
            if count > 5:  # More than 50% of recent emissions
                logger.warning(f"Potential feedback loop detected for {hormone}")

                # Increase cooldown temporarily
                if hormone.lower() in self.policy.hormone_policies:
                    self.policy.hormone_policies[hormone.lower()]["cooldown_ms"] *= 2

    def _audit_emission(self, emission: HormoneEmission):
        """Audit hormone emission"""
        audit_entry = {
            "timestamp": emission.timestamp,
            "hormone": emission.signal.name.value,
            "level": emission.signal.level,
            "reason": emission.reason,
            "source_event": emission.source_event,
            "state": self.state.value,
            "metrics": {
                "cpu": self.metrics.cpu_usage,
                "memory": self.metrics.memory_usage,
                "request_rate": self.metrics.request_rate,
                "error_rate": self.metrics.error_rate,
                "drift": self.metrics.drift_score,
            },
        }

        # Append to audit log
        with open(self.audit_path, "a") as f:
            f.write(json.dumps(audit_entry) + "\n")

    def record_feedback(self, score: float, context: Optional[dict[str, Any]] = None):
        """
        Record feedback for adaptive tuning.

        Args:
            score: Feedback score (0.0 = bad, 1.0 = good)
            context: Optional context about the feedback
        """
        feedback = {
            "timestamp": time.time(),
            "score": score,
            "state": self.state.value,
            "active_hormones": dict(self.current_hormones),
            "context": context or {},
        }

        self.feedback_scores.append(feedback)

        # Adapt policies based on feedback
        self._adapt_policies(score)

    def _adapt_policies(self, feedback_score: float):
        """Adapt hormone policies based on feedback"""
        # Simple adaptation: adjust thresholds based on feedback
        sensitivity = self.policy.feedback_sensitivity

        if feedback_score < 0.3:  # Poor feedback
            # Increase thresholds (be more conservative)
            for hormone_policy in self.policy.hormone_policies.values():
                hormone_policy["threshold"] = min(1.0, hormone_policy["threshold"] * (1 + sensitivity * 0.1))

        elif feedback_score > 0.7:  # Good feedback
            # Decrease thresholds (be more responsive)
            for hormone_policy in self.policy.hormone_policies.values():
                hormone_policy["threshold"] = max(0.1, hormone_policy["threshold"] * (1 - sensitivity * 0.05))

    def get_status(self) -> dict[str, Any]:
        """Get current homeostasis status"""
        return {
            "state": self.state.value,
            "stress_level": self._calculate_stress_level(),
            "active_hormones": dict(self.current_hormones),
            "emissions_this_minute": self.emissions_this_minute,
            "recent_emissions": len(self.emission_history),
            "metrics": {
                "cpu": self.metrics.cpu_usage,
                "memory": self.metrics.memory_usage,
                "request_rate": self.metrics.request_rate,
                "error_rate": self.metrics.error_rate,
                "response_time": self.metrics.response_time_ms,
                "drift": self.metrics.drift_score,
            },
            "feedback": {
                "recent_scores": [f["score"] for f in list(self.feedback_scores)[-10:]],
                "average": (
                    sum(f["score"] for f in self.feedback_scores) / len(self.feedback_scores)
                    if self.feedback_scores
                    else 0.5
                ),
            },
        }

    def reset(self):
        """Reset homeostasis to balanced state"""
        self.state = HomeostasisState.BALANCED
        self.current_hormones.clear()
        self.metrics = SystemMetrics()
        self.emission_history.clear()
        self.last_emission_time.clear()
        self.emissions_this_minute = 0
        self.minute_start = time.time()

        logger.info("Homeostasis controller reset to balanced state")


# Example usage
if __name__ == "__main__":
    import asyncio

    async def demo():
        # Create signal bus and controller
        signal_bus = SignalBus()
        controller = HomeostasisController(signal_bus)

        # Start controller
        await controller.start()

        # Simulate some events
        print("🧬 Homeostasis Controller Demo")
        print("=" * 40)

        # Normal operation
        signals = controller.process_event("request", {"rate": 10, "response_time": 50}, "api")
        print(f"Normal request -> {len(signals)} signals emitted")

        # High load
        signals = controller.process_event("resource", {"cpu": 0.85, "memory": 0.75}, "monitor")
        print(f"High load -> {len(signals)} signals emitted")

        # Drift detected
        signals = controller.process_event("drift", {"score": 0.35}, "guardian")
        print(f"Drift detected -> {len(signals)} signals emitted")

        # Novel input
        signals = controller.process_event("new_pattern", {"novelty_score": 0.8}, "classifier")
        print(f"Novel pattern -> {len(signals)} signals emitted")

        # Get status
        status = controller.get_status()
        print(f"\nStatus: {status['state']}")
        print(f"Stress: {status['stress_level']:.1%}")
        print(f"Active hormones: {status['active_hormones']}")

        # Simulate feedback
        controller.record_feedback(0.8, {"user_satisfied": True})

        # Wait a bit for decay
        await asyncio.sleep(2)

        status = controller.get_status()
        print("\nAfter 2s decay:")
        print(f"Active hormones: {status['active_hormones']}")

        # Stop controller
        await controller.stop()

    asyncio.run(demo())
