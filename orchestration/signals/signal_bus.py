#!/usr/bin/env python3
"""
Signal Bus for Endocrine System
================================
Non-hierarchical communication system allowing modules to communicate
through hormone-like signals without tight coupling.

This implements the "AI endocrine system" concept from the GPT5 audit.
"""

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
import logging
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class SignalType(Enum):
    """Types of endocrine signals in the system"""
    STRESS = "stress"                    # System under load or threat
    NOVELTY = "novelty"                  # New/unexpected input
    ALIGNMENT_RISK = "alignment_risk"    # Ethical/safety concern
    TRUST = "trust"                      # Confidence in current state
    URGENCY = "urgency"                  # Time pressure
    AMBIGUITY = "ambiguity"             # Uncertainty in interpretation
    HOMEOSTASIS = "homeostasis"         # Return to baseline
    CURIOSITY = "curiosity"              # Exploration drive
    FATIGUE = "fatigue"                  # Resource depletion


@dataclass
class Signal:
    """A hormone-like signal that flows through the system"""
    name: SignalType
    level: float  # 0.0 to 1.0
    source: str  # Module that emitted the signal
    target: Optional[str] = None  # Optional specific target module
    ttl_ms: int = 1000  # Time to live in milliseconds
    metadata: Dict[str, Any] = field(default_factory=dict)
    audit_id: str = ""
    timestamp: float = field(default_factory=time.time)
    
    def is_expired(self) -> bool:
        """Check if signal has expired"""
        return (time.time() - self.timestamp) * 1000 > self.ttl_ms
    
    def __hash__(self):
        return hash((self.name, self.source, self.timestamp))


class SignalBus:
    """
    Central signal bus for hormone-like communication between modules.
    Implements publish-subscribe pattern with signal modulation.
    """
    
    def __init__(self, max_signal_history: int = 100):
        # Subscribers: signal_type -> list of handlers
        self.subscribers: Dict[SignalType, List[Callable]] = defaultdict(list)
        
        # Signal history for analysis
        self.signal_history: deque = deque(maxlen=max_signal_history)
        
        # Active signals (not yet expired)
        self.active_signals: Set[Signal] = set()
        
        # Signal modulation rules
        self.modulation_rules: List[Callable] = []
        
        # Cooldowns to prevent signal flooding
        self.cooldowns: Dict[tuple[SignalType, str], float] = {}
        self.cooldown_periods: Dict[SignalType, float] = {
            SignalType.STRESS: 0.8,
            SignalType.ALIGNMENT_RISK: 0.0,  # No cooldown for safety
            SignalType.NOVELTY: 0.5,
            SignalType.TRUST: 0.5,
            SignalType.URGENCY: 0.3,
            SignalType.AMBIGUITY: 0.7,
            SignalType.HOMEOSTASIS: 2.0,
            SignalType.CURIOSITY: 1.0,
            SignalType.FATIGUE: 1.5,
        }
        
        # Statistics
        self.stats = {
            "signals_published": 0,
            "signals_delivered": 0,
            "signals_modulated": 0,
            "signals_dropped": 0,
        }
        
        # Background task for cleanup
        self._cleanup_task = None
        self._running = False
    
    async def initialize(self):
        """Start the signal bus"""
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("Signal bus initialized")
    
    async def shutdown(self):
        """Shutdown the signal bus"""
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        logger.info("Signal bus shutdown")
    
    async def _cleanup_loop(self):
        """Remove expired signals periodically"""
        while self._running:
            try:
                # Remove expired signals
                expired = [s for s in self.active_signals if s.is_expired()]
                for signal in expired:
                    self.active_signals.discard(signal)
                
                if expired:
                    logger.debug(f"Cleaned up {len(expired)} expired signals")
                
                await asyncio.sleep(1)  # Cleanup every second
                
            except Exception as e:
                logger.error(f"Error in signal cleanup: {e}")
    
    def subscribe(
        self,
        signal_type: SignalType,
        handler: Callable[[Signal], None],
        module_name: Optional[str] = None
    ):
        """
        Subscribe to a signal type.
        
        Args:
            signal_type: Type of signal to subscribe to
            handler: Async function to handle the signal
            module_name: Optional module name for tracking
        """
        self.subscribers[signal_type].append(handler)
        logger.debug(f"Module {module_name or 'unknown'} subscribed to {signal_type.value}")
    
    def unsubscribe(
        self,
        signal_type: SignalType,
        handler: Callable[[Signal], None]
    ):
        """Unsubscribe from a signal type"""
        if handler in self.subscribers[signal_type]:
            self.subscribers[signal_type].remove(handler)
    
    def add_modulation_rule(self, rule: Callable[[Signal], Optional[Signal]]):
        """
        Add a rule that can modulate signals before delivery.
        Rules can modify or filter signals.
        """
        self.modulation_rules.append(rule)
    
    def _check_cooldown(self, signal: Signal) -> bool:
        """Check if signal is in cooldown period"""
        key = (signal.name, signal.source)
        cooldown_period = self.cooldown_periods.get(signal.name, 0)
        
        if cooldown_period <= 0:
            return True  # No cooldown
        
        last_emit = self.cooldowns.get(key, 0)
        current_time = time.time()
        
        if current_time - last_emit >= cooldown_period:
            self.cooldowns[key] = current_time
            return True
        
        return False
    
    def _apply_modulation(self, signal: Signal) -> Optional[Signal]:
        """Apply modulation rules to a signal"""
        current_signal = signal
        
        for rule in self.modulation_rules:
            try:
                current_signal = rule(current_signal)
                if current_signal is None:
                    # Signal filtered out
                    self.stats["signals_dropped"] += 1
                    return None
                self.stats["signals_modulated"] += 1
            except Exception as e:
                logger.error(f"Error in modulation rule: {e}")
        
        return current_signal
    
    def publish(self, signal: Signal) -> bool:
        """
        Publish a signal to the bus.
        
        Returns:
            True if signal was published, False if dropped (cooldown/modulation)
        """
        # Check cooldown
        if not self._check_cooldown(signal):
            logger.debug(f"Signal {signal.name.value} from {signal.source} in cooldown")
            self.stats["signals_dropped"] += 1
            return False
        
        # Apply modulation
        modulated_signal = self._apply_modulation(signal)
        if modulated_signal is None:
            return False
        
        # Add to active signals
        self.active_signals.add(modulated_signal)
        self.signal_history.append(modulated_signal)
        self.stats["signals_published"] += 1
        
        # Deliver to subscribers
        handlers = self.subscribers.get(modulated_signal.name, [])
        
        for handler in handlers:
            try:
                # Check if targeted signal
                if modulated_signal.target and hasattr(handler, '__module__'):
                    if handler.__module__ != modulated_signal.target:
                        continue
                
                # Call handler (async or sync)
                if asyncio.iscoroutinefunction(handler):
                    asyncio.create_task(handler(modulated_signal))
                else:
                    handler(modulated_signal)
                
                self.stats["signals_delivered"] += 1
                
            except Exception as e:
                logger.error(f"Error delivering signal to handler: {e}")
        
        logger.debug(
            f"Published {modulated_signal.name.value} signal "
            f"from {modulated_signal.source} (level: {modulated_signal.level:.2f})"
        )
        
        return True
    
    def get_current_levels(self) -> Dict[SignalType, float]:
        """Get current levels of all signal types"""
        levels = {signal_type: 0.0 for signal_type in SignalType}
        
        # Average levels from active signals
        for signal in self.active_signals:
            if not signal.is_expired():
                # Use exponential decay based on age
                age_ms = (time.time() - signal.timestamp) * 1000
                decay = max(0, 1 - (age_ms / signal.ttl_ms))
                levels[signal.name] = max(levels[signal.name], signal.level * decay)
        
        return levels
    
    def get_signal_history(
        self,
        signal_type: Optional[SignalType] = None,
        source: Optional[str] = None,
        limit: int = 50
    ) -> List[Signal]:
        """Get historical signals with optional filtering"""
        history = list(self.signal_history)
        
        if signal_type:
            history = [s for s in history if s.name == signal_type]
        
        if source:
            history = [s for s in history if s.source == source]
        
        return history[-limit:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get bus statistics"""
        return {
            **self.stats,
            "active_signals": len([s for s in self.active_signals if not s.is_expired()]),
            "total_history": len(self.signal_history),
            "subscribers": {
                signal_type.value: len(handlers)
                for signal_type, handlers in self.subscribers.items()
            },
            "current_levels": {
                k.value: v for k, v in self.get_current_levels().items()
            }
        }


# Global signal bus instance
_global_signal_bus = None


def get_signal_bus() -> SignalBus:
    """Get the global signal bus instance"""
    global _global_signal_bus
    if _global_signal_bus is None:
        _global_signal_bus = SignalBus()
    return _global_signal_bus


# Convenience functions for common signals
def emit_stress(level: float, source: str, metadata: Optional[Dict] = None):
    """Emit a stress signal"""
    bus = get_signal_bus()
    signal = Signal(
        name=SignalType.STRESS,
        level=level,
        source=source,
        metadata=metadata or {}
    )
    return bus.publish(signal)


def emit_alignment_risk(level: float, source: str, metadata: Optional[Dict] = None):
    """Emit an alignment risk signal"""
    bus = get_signal_bus()
    signal = Signal(
        name=SignalType.ALIGNMENT_RISK,
        level=level,
        source=source,
        metadata=metadata or {}
    )
    return bus.publish(signal)


def emit_novelty(level: float, source: str, metadata: Optional[Dict] = None):
    """Emit a novelty signal"""
    bus = get_signal_bus()
    signal = Signal(
        name=SignalType.NOVELTY,
        level=level,
        source=source,
        metadata=metadata or {}
    )
    return bus.publish(signal)