"""
Homeostasis Controller for LUKHAS Signal Regulation
====================================================
Maintains system balance through signal regulation, preventing oscillations
and ensuring stable, adaptive behavior across the colony.
"""

import logging
import os
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

import numpy as np
import yaml

from .signal_bus import Signal, SignalBus, SignalType, get_signal_bus

logger = logging.getLogger(__name__)


class SystemEvent(str, Enum):
    """System events that can trigger signal emissions"""

    USER_INPUT = "user_input"
    API_RESPONSE = "api_response"
    MEMORY_WRITE = "memory_write"
    ETHICS_VIOLATION = "ethics_violation"
    PATTERN_DETECTED = "pattern_detected"
    ERROR_OCCURRED = "error_occurred"
    RESOURCE_CONSTRAINT = "resource_constraint"
    GOAL_ACHIEVED = "goal_achieved"


@dataclass
class ModulationParams:
    """Parameters for modulating API calls based on signals"""

    temperature: float = 0.7
    top_p: float = 0.9
    max_output_tokens: int = 1024
    reasoning_effort: float = 0.5  # 0.0 to 1.0
    retrieval_k: int = 5
    planner_beam: int = 3
    memory_write_strength: float = 0.5
    safety_mode: str = "balanced"  # strict, balanced, creative
    tool_allowlist: list[str] = field(default_factory=lambda: ["retrieval"])

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API calls"""
        return {
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_tokens": self.max_output_tokens,
            "metadata": {
                "reasoning_effort": self.reasoning_effort,
                "retrieval_k": self.retrieval_k,
                "planner_beam": self.planner_beam,
                "memory_write_strength": self.memory_write_strength,
                "safety_mode": self.safety_mode,
                "tool_allowlist": self.tool_allowlist,
            },
        }


@dataclass
class AuditTrail:
    """Audit trail for homeostasis decisions"""

    audit_id: str
    timestamp: float
    signals: list[Signal]
    event: Optional[SystemEvent]
    modulation: ModulationParams
    explanation: str
    oscillation_detected: bool = False
    emergency_mode: bool = False


class OscillationDetector:
    """Detects and prevents signal oscillations"""

    def __init__(self, window_size: int = 20, threshold: float = 0.3):
        self.window_size = window_size
        self.threshold = threshold
        self.signal_history: dict[SignalType, deque] = {sig_type: deque(maxlen=window_size) for sig_type in SignalType}

    def update(self, signal: Signal):
        """Update history with new signal"""
        self.signal_history[signal.name].append((signal.timestamp, signal.level))

    def detect_oscillation(self, signal_type: SignalType) -> bool:
        """
        Detect if a signal is oscillating.
        Uses frequency domain analysis to detect periodic behavior.
        """
        history = list(self.signal_history[signal_type])

        if len(history) < 5:  # Need minimum history
            return False

        # Extract levels
        levels = [level for _, level in history]

        # Calculate variance and mean crossing rate
        variance = np.var(levels)
        mean = np.mean(levels)

        # Count mean crossings
        crossings = 0
        for i in range(1, len(levels)):
            if (levels[i - 1] - mean) * (levels[i] - mean) < 0:
                crossings += 1

        crossing_rate = crossings / len(levels)

        # High crossing rate with significant variance indicates oscillation
        return crossing_rate > self.threshold and variance > 0.05

    def get_damping_factor(self, signal_type: SignalType) -> float:
        """
        Calculate damping factor to reduce oscillation.
        Returns value between 0.1 (heavy damping) and 1.0 (no damping).
        """
        if self.detect_oscillation(signal_type):
            return 0.3  # Heavy damping when oscillating
        return 0.8  # Light damping otherwise


class HomeostasisController:
    """
    Maintains system balance through signal regulation.
    Core component of the colony's endocrine system.
    """

    def __init__(self, bus: Optional[SignalBus] = None, config_path: Optional[str] = None):
        """
        Initialize the homeostasis controller.

        Args:
            bus: Signal bus instance (uses singleton if not provided)
            config_path: Path to modulation policy configuration
        """
        self.bus = bus or get_signal_bus()
        self.config = self._load_config(config_path)
        self.oscillation_detector = OscillationDetector()

        # State tracking
        self.signal_history = deque(maxlen=1000)
        self.audit_trails: deque = deque(maxlen=100)
        self.emergency_mode = False
        self.rate_limiters: dict[SignalType, float] = {}

        # Metrics
        self.metrics = {
            "events_processed": 0,
            "signals_regulated": 0,
            "oscillations_prevented": 0,
            "emergency_activations": 0,
            "modulations_computed": 0,
        }

        # Compatibility: store last processed signals for legacy API
        self._last_processed_signals = []  # type: ignore[var-annotated]

    def _load_config(self, config_path: Optional[str]) -> dict[str, Any]:
        """Load modulation policy configuration"""
        # Allow env override
        env_path = os.getenv("LUKHAS_MODULATION_CONFIG")
        if env_path and not config_path:
            config_path = env_path
        # Default to repo-relative config
        if config_path is None:
            from pathlib import Path

            repo_root = Path(__file__).resolve().parents[2]
            config_path = str(repo_root / "config/modulation_policy.yaml")

        try:
            with open(config_path) as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}")
            return {}

    def on_event(self, event: SystemEvent, context: dict[str, Any]) -> list[Signal]:
        """
        Convert system events to signals based on policy.

        Args:
            event: The system event that occurred
            context: Event context (user input, error details, etc.)

        Returns:
            List of signals to emit
        """
        self.metrics["events_processed"] += 1
        signals = []

        # Map events to signals based on context
        if event == SystemEvent.USER_INPUT:
            # Analyze input for ambiguity
            text = context.get("text", "")
            ambiguity_level = self._calculate_ambiguity(text)
            if ambiguity_level > 0.3:
                signals.append(
                    Signal(
                        name=SignalType.AMBIGUITY,
                        level=ambiguity_level,
                        source="homeostasis",
                        metadata={"event": event.value},
                    )
                )

            # Check for urgency markers
            if any(word in text.lower() for word in ["urgent", "asap", "immediately", "now"]):
                signals.append(
                    Signal(
                        name=SignalType.URGENCY,
                        level=0.8,
                        source="homeostasis",
                        metadata={"event": event.value},
                    )
                )

        elif event == SystemEvent.ETHICS_VIOLATION:
            # Always emit high alignment risk signal
            signals.append(
                Signal(
                    name=SignalType.ALIGNMENT_RISK,
                    level=context.get("severity", 0.8),
                    source="homeostasis",
                    metadata={"event": event.value, "violation": context.get("type")},
                )
            )

        elif event == SystemEvent.ERROR_OCCURRED:
            # Errors cause stress
            signals.append(
                Signal(
                    name=SignalType.STRESS,
                    level=min(1.0, context.get("error_count", 1) * 0.3),
                    source="homeostasis",
                    metadata={"event": event.value},
                )
            )

        elif event == SystemEvent.RESOURCE_CONSTRAINT:
            # Resource constraints cause stress
            signals.append(
                Signal(
                    name=SignalType.STRESS,
                    level=context.get("constraint_level", 0.6),
                    source="homeostasis",
                    metadata={"event": event.value},
                )
            )

        elif event == SystemEvent.PATTERN_DETECTED:
            # New patterns trigger novelty signal
            signals.append(
                Signal(
                    name=SignalType.NOVELTY,
                    level=context.get("novelty_score", 0.5),
                    source="homeostasis",
                    metadata={"event": event.value},
                )
            )

        elif event == SystemEvent.GOAL_ACHIEVED:
            # Success builds trust
            signals.append(
                Signal(
                    name=SignalType.TRUST,
                    level=min(1.0, context.get("trust_increment", 0.2)),
                    source="homeostasis",
                    metadata={"event": event.value},
                )
            )

        return signals

    def regulate_signals(self, signals: list[Signal]) -> list[Signal]:
        """
        Apply rate limiting, cooldowns, and bounds to signals.
        Prevents signal spam and oscillations.

        Args:
            signals: Raw signals to regulate

        Returns:
            Regulated signals safe for emission
        """
        regulated = []

        for signal in signals:
            # Update oscillation detector
            self.oscillation_detector.update(signal)

            # Check for oscillation
            if self.oscillation_detector.detect_oscillation(signal.name):
                # Apply damping
                damping = self.oscillation_detector.get_damping_factor(signal.name)
                signal.level *= damping
                self.metrics["oscillations_prevented"] += 1
                logger.debug(f"Damping {signal.name} by {damping:.2f} due to oscillation")

            # Apply rate limiting
            last_emit = self.rate_limiters.get(signal.name, 0)
            cooldown_ms = signal.cooldown_ms

            if (time.time() - last_emit) * 1000 < cooldown_ms:
                logger.debug(f"Rate limiting {signal.name} (cooldown: {cooldown_ms}ms)")
                continue

            # Apply bounds (clamp to [0, 1])
            signal.level = max(0.0, min(1.0, signal.level))

            # Check emergency thresholds
            if signal.name == SignalType.ALIGNMENT_RISK and signal.level > 0.8:
                self.emergency_mode = True
                self.metrics["emergency_activations"] += 1
                logger.warning(f"Emergency mode activated: {signal.name} = {signal.level:.2f}")

            # Update rate limiter
            self.rate_limiters[signal.name] = time.time()

            regulated.append(signal)
            self.metrics["signals_regulated"] += 1

        return regulated

    def compute_modulation(self, signals: list[Signal]) -> ModulationParams:
        """
        Transform signals into API modulation parameters.
        Core of the signal-to-prompt translation.

        Args:
            signals: Current active signals

        Returns:
            Modulation parameters for API calls
        """
        self.metrics["modulations_computed"] += 1

        # Start with defaults
        params = ModulationParams()

        # Get signal levels
        levels = {}
        for signal in signals:
            if signal.name not in levels or signal.level > levels[signal.name]:
                levels[signal.name] = signal.level

        # Apply modulation maps from config
        maps = self.config.get("maps", {})

        # Process alignment risk (highest priority)
        if SignalType.ALIGNMENT_RISK in levels:
            risk = levels[SignalType.ALIGNMENT_RISK]
            if "alignment_risk" in maps:
                params.temperature = self._eval_expression(
                    maps["alignment_risk"].get("temperature", "0.7"), {"x": risk}
                )
                params.top_p = self._eval_expression(maps["alignment_risk"].get("top_p", "0.9"), {"x": risk})
                params.reasoning_effort = self._eval_expression(
                    maps["alignment_risk"].get("reasoning_effort", "0.5"), {"x": risk}
                )
                params.safety_mode = "strict" if risk > 0.3 else "balanced"

        # Process stress
        if SignalType.STRESS in levels:
            stress = levels[SignalType.STRESS]
            if "stress" in maps:
                params.temperature = min(
                    params.temperature,
                    self._eval_expression(maps["stress"].get("temperature", "0.7"), {"x": stress}),
                )
                params.max_output_tokens = int(
                    self._eval_expression(maps["stress"].get("max_output_tokens", "1024"), {"x": stress})
                )

        # Process ambiguity (set reasoning_effort directly for any ambiguity)
        if SignalType.AMBIGUITY in levels:
            ambiguity = levels[SignalType.AMBIGUITY]
            # Always increase reasoning for ambiguity
            params.reasoning_effort = max(0.6, params.reasoning_effort)
            if "ambiguity" in maps:
                params.reasoning_effort = max(
                    params.reasoning_effort,
                    self._eval_expression(
                        maps["ambiguity"].get("reasoning_effort", "0.5"),
                        {"x": ambiguity},
                    ),
                )
                params.retrieval_k = int(
                    self._eval_expression(maps["ambiguity"].get("retrieval_k", "5"), {"x": ambiguity})
                )

        # Process urgency
        if SignalType.URGENCY in levels:
            urgency = levels[SignalType.URGENCY]
            if "urgency" in maps:
                params.max_output_tokens = min(
                    params.max_output_tokens,
                    int(
                        self._eval_expression(
                            maps["urgency"].get("max_output_tokens", "1024"),
                            {"x": urgency},
                        )
                    ),
                )
                params.reasoning_effort = min(
                    params.reasoning_effort,
                    self._eval_expression(maps["urgency"].get("reasoning_effort", "0.5"), {"x": urgency}),
                )

        # Process novelty
        if SignalType.NOVELTY in levels:
            novelty = levels[SignalType.NOVELTY]
            if "novelty" in maps:
                params.temperature = max(
                    params.temperature,
                    self._eval_expression(maps["novelty"].get("temperature", "0.7"), {"x": novelty}),
                )
                params.memory_write_strength = self._eval_expression(
                    maps["novelty"].get("memory_write", "0.5"), {"x": novelty}
                )

        # Process trust
        if SignalType.TRUST in levels:
            trust = levels[SignalType.TRUST]
            if "trust" in maps:
                params.temperature = self._eval_expression(maps["trust"].get("temperature", "0.7"), {"x": trust})
                params.memory_write_strength = max(
                    params.memory_write_strength,
                    self._eval_expression(maps["trust"].get("memory_write", "0.5"), {"x": trust}),
                )

        # Emergency mode overrides
        if self.emergency_mode:
            params.temperature = 0.1
            params.top_p = 0.2
            params.safety_mode = "strict"
            params.tool_allowlist = ["retrieval"]  # Minimal tools

        return params

    def _eval_expression(self, expr: str, context: dict[str, float]) -> float:
        """
        Safely evaluate mathematical expressions from config.

        Args:
            expr: Expression string (e.g., "1 - 0.85*x")
            context: Variable values (e.g., {"x": 0.5})

        Returns:
            Evaluated result
        """
        try:
            # Safe evaluation with limited functions
            safe_dict = {"min": min, "max": max, "round": round, "abs": abs, **context}
            return eval(expr, {"__builtins__": {}}, safe_dict)
        except Exception as e:
            logger.error(f"Error evaluating expression '{expr}': {e}")
            return 0.5  # Safe default

    def _calculate_ambiguity(self, text: str) -> float:
        """
        Calculate ambiguity level of user input.
        Simple heuristic based on question marks, vague words, etc.
        """
        if not text:
            return 0.0

        ambiguity_score = 0.0

        # Check for questions
        if "?" in text:
            ambiguity_score += 0.2

        # Check for vague words (including "this", "what")
        vague_words = [
            "maybe",
            "perhaps",
            "might",
            "could",
            "something",
            "stuff",
            "thing",
            "this",
            "what",
        ]
        for word in vague_words:
            if word in text.lower():
                ambiguity_score += 0.1

        # Short inputs are often ambiguous
        if len(text.split()) < 5:
            ambiguity_score += 0.2

        return min(1.0, ambiguity_score)

    def detect_oscillation(self) -> bool:
        """Check if any signals are oscillating"""
        return any(self.oscillation_detector.detect_oscillation(signal_type) for signal_type in SignalType)

    def explain_decision(self, audit_id: str) -> Optional[AuditTrail]:
        """
        Generate human-readable explanation of a decision.

        Args:
            audit_id: ID of the decision to explain

        Returns:
            Audit trail with explanation, or None if not found
        """
        for trail in self.audit_trails:
            if trail.audit_id == audit_id:
                return trail
        return None

    def get_metrics(self) -> dict[str, Any]:
        """Get controller metrics"""
        return {
            **self.metrics,
            "emergency_mode": self.emergency_mode,
            "oscillation_active": self.detect_oscillation(),
        }

    async def process_event(self, event: SystemEvent, context: dict[str, Any]) -> ModulationParams:
        """
        Main processing pipeline: event -> signals -> modulation.

        Args:
            event: System event
            context: Event context

        Returns:
            Modulation parameters for API
        """
        # Generate signals from event
        raw_signals = self.on_event(event, context)

        # Regulate signals
        regulated_signals = self.regulate_signals(raw_signals)

        # Emit signals to bus
        for signal in regulated_signals:
            self.bus.publish(signal)

        # Get all active signals
        active_signals = self.bus.get_active_signals()

        # Compute modulation
        modulation = self.compute_modulation(active_signals)

        # Create audit trail
        audit = AuditTrail(
            audit_id=f"audit_{int(time.time() * 1000)}",
            timestamp=time.time(),
            signals=active_signals,
            event=event,
            modulation=modulation,
            explanation=self._generate_explanation(event, active_signals, modulation),
            oscillation_detected=self.detect_oscillation(),
            emergency_mode=self.emergency_mode,
        )
        self.audit_trails.append(audit)

        return modulation

    def _generate_explanation(self, event: SystemEvent, signals: list[Signal], modulation: ModulationParams) -> str:
        """Generate human-readable explanation"""
        parts = [f"Event: {event.value}"]

        if signals:
            signal_desc = ", ".join([f"{s.name.value}={s.level:.2f}" for s in signals[:3]])
            parts.append(f"Active signals: {signal_desc}")

        if self.emergency_mode:
            parts.append("EMERGENCY MODE ACTIVE")

        if self.detect_oscillation():
            parts.append("Oscillation damping applied")

        parts.append(f"Temperature: {modulation.temperature:.2f}")
        parts.append(f"Safety: {modulation.safety_mode}")

        return " | ".join(parts)

    # --- Backward compatibility layer (legacy tests expect these) ---
    def process_signals(self, signals: list[Signal]) -> list[Signal]:
        """Legacy API: process raw signals to update oscillation detector.

        Returns the regulated signals for downstream use.
        """
        self._last_processed_signals = signals or []
        # Update oscillation detector and apply basic regulation
        for sig in self._last_processed_signals:
            self.oscillation_detector.update(sig)
        return self.regulate_signals(self._last_processed_signals)

    def get_system_state(self) -> dict[str, Any]:
        """Legacy API: return a minimal state snapshot used in tests.

        Includes an 'oscillating_signals' list when oscillations are detected.
        """
        oscillating = [
            st.value if isinstance(st, SignalType) else str(st)
            for st in SignalType
            if self.oscillation_detector.detect_oscillation(st)
        ]
        return {
            "emergency_mode": self.emergency_mode,
            "oscillating_signals": oscillating,
            "metrics": self.get_metrics(),
        }
