"""
Signal Bus Architecture for LUKHAS Colony Communication
========================================================
Enhanced publish-subscribe system with signal modulation capabilities.
Integrates with the existing SymbolicKernelBus for event coordination.
"""

import asyncio
import contextlib
import logging
import os
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from threading import RLock
from typing import Any, Callable, Optional

import yaml

logger = logging.getLogger(__name__)


class SignalType(str, Enum):
    """Core signal types for the colony endocrine system"""

    STRESS = "stress"
    ALIGNMENT_RISK = "alignment_risk"
    NOVELTY = "novelty"
    TRUST = "trust"
    URGENCY = "urgency"
    AMBIGUITY = "ambiguity"


@dataclass
class Signal:
    """
    Core signal structure for colony communication.
    Represents a hormonal-like signal that modulates system behavior.
    """

    name: SignalType
    level: float  # 0.0 to 1.0
    source: str  # Module that emitted the signal
    ttl_ms: int = 1000  # Time-to-live in milliseconds

    # Metadata
    audit_id: str = field(default_factory=lambda: f"sig_{int(time.time()*1000)}")
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    correlation_id: Optional[str] = None

    # Modulation parameters
    weight: float = 1.0  # From config
    cooldown_ms: int = 0  # From config
    last_emit_time: Optional[float] = None

    def is_expired(self) -> bool:
        """Check if signal has expired based on TTL"""
        return (time.time() - self.timestamp) * 1000 > self.ttl_ms

    def is_in_cooldown(self) -> bool:
        """Check if signal is in cooldown period"""
        if self.last_emit_time is None or self.cooldown_ms == 0:
            return False
        return (time.time() - self.last_emit_time) * 1000 < self.cooldown_ms

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "name": self.name.value,
            "level": self.level,
            "source": self.source,
            "ttl_ms": self.ttl_ms,
            "audit_id": self.audit_id,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
            "correlation_id": self.correlation_id,
            "weight": self.weight,
            "cooldown_ms": self.cooldown_ms,
        }


@dataclass
class SignalPattern:
    """Represents a pattern of signals for complex behaviors"""

    pattern_id: str
    signals: list[Signal]
    time_window_ms: int = 5000
    min_signals: int = 1
    max_signals: Optional[int] = None

    def matches(self, signals: list[Signal]) -> bool:
        """Check if a list of signals matches this pattern"""
        if len(signals) < self.min_signals:
            return False
        if self.max_signals and len(signals) > self.max_signals:
            return False

        # Check time window
        if signals:
            time_span = (signals[-1].timestamp - signals[0].timestamp) * 1000
            if time_span > self.time_window_ms:
                return False

        return True


class SignalBus:
    """
    Central signal bus for colony-wide communication.
    Implements publish-subscribe with signal modulation and pattern detection.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the signal bus.

        Args:
            config_path: Path to modulation_policy.yaml configuration
        """
        self._lock = RLock()
        self._subscribers: dict[SignalType, set[Callable]] = defaultdict(set)
        self._signal_history: deque = deque(maxlen=1000)
        self._active_signals: list[Signal] = []
        self._patterns: dict[str, SignalPattern] = {}
        self._pattern_handlers: dict[str, list[Callable]] = defaultdict(list)

        # Load configuration
        self.config = self._load_config(config_path)
        self._signal_configs = self._parse_signal_configs()

        # Metrics
        self.metrics = {
            "signals_published": 0,
            "signals_delivered": 0,
            "patterns_detected": 0,
            "cooldown_blocks": 0,
        }

        # Start cleanup task
        self._cleanup_task = None
        self._running = False

    def _load_config(self, config_path: Optional[str]) -> dict[str, Any]:
        """Load modulation policy configuration"""
        # Allow env override
        env_path = os.getenv("LUKHAS_MODULATION_CONFIG")
        if env_path and not config_path:
            config_path = env_path
        # Default to repo-relative config
        if config_path is None:
            repo_root = Path(__file__).resolve().parents[2]
            config_path = str(repo_root / "config/modulation_policy.yaml")

        try:
            with open(config_path) as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return self._get_default_config()

    def _get_default_config(self) -> dict[str, Any]:
        """Get default configuration if file not found"""
        return {
            "signals": [
                {"name": "stress", "weight": 0.9, "cooldown_ms": 800},
                {"name": "alignment_risk", "weight": 1.0, "cooldown_ms": 0},
                {"name": "novelty", "weight": 0.6, "cooldown_ms": 500},
                {"name": "trust", "weight": 0.4, "cooldown_ms": 500},
                {"name": "urgency", "weight": 0.5, "cooldown_ms": 300},
                {"name": "ambiguity", "weight": 0.7, "cooldown_ms": 700},
            ]
        }

    def _parse_signal_configs(self) -> dict[SignalType, dict[str, Any]]:
        """Parse signal configurations from config"""
        configs = {}
        for sig_config in self.config.get("signals", []):
            name = sig_config["name"]
            try:
                signal_type = SignalType(name)
                configs[signal_type] = sig_config
            except ValueError:
                logger.warning(f"Unknown signal type in config: {name}")
        return configs

    async def start(self):
        """Start the signal bus and background tasks"""
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_expired_signals())
        logger.info("Signal bus started")

    async def stop(self):
        """Stop the signal bus and cleanup"""
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._cleanup_task
        logger.info("Signal bus stopped")

    async def _cleanup_expired_signals(self):
        """Background task to remove expired signals"""
        while self._running:
            try:
                with self._lock:
                    # Remove expired signals
                    self._active_signals = [
                        sig for sig in self._active_signals if not sig.is_expired()
                    ]
                await asyncio.sleep(1)  # Check every second
            except Exception as e:
                logger.error(f"Error in signal cleanup: {e}")

    def publish(self, signal: Signal) -> bool:
        """
        Publish a signal to all subscribers.

        Args:
            signal: The signal to publish

        Returns:
            True if signal was published, False if blocked by cooldown
        """
        with self._lock:
            # Apply configuration
            if signal.name in self._signal_configs:
                config = self._signal_configs[signal.name]
                signal.weight = config.get("weight", 1.0)
                signal.cooldown_ms = config.get("cooldown_ms", 0)

            # Check cooldown
            if signal.is_in_cooldown():
                self.metrics["cooldown_blocks"] += 1
                logger.debug(f"Signal {signal.name} blocked by cooldown")
                return False

            # Update last emit time
            signal.last_emit_time = time.time()

            # Add to active signals and history
            self._active_signals.append(signal)
            self._signal_history.append(signal)
            self.metrics["signals_published"] += 1

            # Notify subscribers
            subscribers = self._subscribers.get(signal.name, set())
            for handler in subscribers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        asyncio.create_task(handler(signal))
                    else:
                        handler(signal)
                    self.metrics["signals_delivered"] += 1
                except Exception as e:
                    logger.error(f"Error in signal handler: {e}")

            # Check for pattern matches
            self._check_patterns(signal)

            logger.debug(f"Published signal: {signal.name} (level={signal.level:.2f})")
            return True

    def subscribe(self, signal_type: SignalType, handler: Callable[[Signal], None]):
        """
        Subscribe to a signal type.

        Args:
            signal_type: Type of signal to subscribe to
            handler: Function to call when signal is received
        """
        with self._lock:
            self._subscribers[signal_type].add(handler)
            logger.debug(f"Subscribed to {signal_type}")

    def unsubscribe(self, signal_type: SignalType, handler: Callable[[Signal], None]):
        """
        Unsubscribe from a signal type.

        Args:
            signal_type: Type of signal to unsubscribe from
            handler: Handler function to remove
        """
        with self._lock:
            self._subscribers[signal_type].discard(handler)
            logger.debug(f"Unsubscribed from {signal_type}")

    def register_pattern(
        self, pattern: SignalPattern, handler: Callable[[list[Signal]], None]
    ):
        """
        Register a pattern detector with handler.

        Args:
            pattern: Pattern to detect
            handler: Function to call when pattern is detected
        """
        with self._lock:
            self._patterns[pattern.pattern_id] = pattern
            self._pattern_handlers[pattern.pattern_id].append(handler)
            logger.debug(f"Registered pattern: {pattern.pattern_id}")

    def _check_patterns(self, new_signal: Signal):
        """Check if new signal completes any patterns"""
        with self._lock:
            recent_signals = list(self._signal_history)[-20:]  # Check last 20 signals

            for pattern_id, pattern in self._patterns.items():
                # Get signals within pattern's time window
                cutoff_time = time.time() - (pattern.time_window_ms / 1000)
                window_signals = [
                    sig for sig in recent_signals if sig.timestamp >= cutoff_time
                ]

                if pattern.matches(window_signals):
                    self.metrics["patterns_detected"] += 1
                    handlers = self._pattern_handlers.get(pattern_id, [])
                    for handler in handlers:
                        try:
                            if asyncio.iscoroutinefunction(handler):
                                asyncio.create_task(handler(window_signals))
                            else:
                                handler(window_signals)
                        except Exception as e:
                            logger.error(f"Error in pattern handler: {e}")

    def get_active_signals(self) -> list[Signal]:
        """Get all currently active (non-expired) signals"""
        with self._lock:
            return [sig for sig in self._active_signals if not sig.is_expired()]

    def get_signal_levels(self) -> dict[SignalType, float]:
        """Get current levels for all signal types"""
        levels = dict.fromkeys(SignalType, 0.0)

        with self._lock:
            for signal in self.get_active_signals():
                # Use weighted average for multiple signals of same type
                current = levels[signal.name]
                levels[signal.name] = max(current, signal.level * signal.weight)

        return levels

    def get_metrics(self) -> dict[str, Any]:
        """Get bus metrics"""
        with self._lock:
            return {
                **self.metrics,
                "active_signals": len(self.get_active_signals()),
                "subscribers": sum(len(subs) for subs in self._subscribers.values()),
                "patterns_registered": len(self._patterns),
            }

    def clear_history(self):
        """Clear signal history (for testing)"""
        with self._lock:
            self._signal_history.clear()
            self._active_signals.clear()
            logger.debug("Signal history cleared")


# Singleton instance
_signal_bus_instance: Optional[SignalBus] = None


def get_signal_bus() -> SignalBus:
    """Get the singleton signal bus instance"""
    global _signal_bus_instance
    if _signal_bus_instance is None:
        _signal_bus_instance = SignalBus()
    return _signal_bus_instance


async def emit_signal(
    signal_type: SignalType,
    level: float,
    source: str,
    metadata: Optional[dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
) -> bool:
    """
    Convenience function to emit a signal.

    Args:
        signal_type: Type of signal to emit
        level: Signal strength (0.0 to 1.0)
        source: Module emitting the signal
        metadata: Optional metadata
        correlation_id: Optional ID to correlate related signals

    Returns:
        True if signal was emitted, False if blocked
    """
    bus = get_signal_bus()
    signal = Signal(
        name=signal_type,
        level=min(1.0, max(0.0, level)),  # Clamp to [0, 1]
        source=source,
        metadata=metadata or {},
        correlation_id=correlation_id,
    )
    return bus.publish(signal)
