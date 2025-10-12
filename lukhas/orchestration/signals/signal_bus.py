"""
LUKHAS Signal Bus Module
=========================
Shim to candidate.orchestration.signals.signal_bus for backward compatibility.
"""
# Import from the actual location
try:
    from labs.orchestration.signals.signal_bus import *
except ImportError:
    # Provide minimal fallback types if candidate module not available
    from dataclasses import dataclass
    from enum import Enum
    from typing import Any, Callable, Dict, List, Optional

    class SignalType(Enum):
        """Signal type enumeration"""
        SYSTEM = "system"
        USER = "user"
        NETWORK = "network"

    @dataclass
    class Signal:
        """Signal data structure"""
        type: SignalType
        data: Dict[str, Any]
        source: Optional[str] = None

    class SignalBus:
        """Minimal signal bus implementation"""
        def __init__(self):
            self._handlers: Dict[SignalType, List[Callable]] = {}

        def subscribe(self, signal_type: SignalType, handler: Callable):
            if signal_type not in self._handlers:
                self._handlers[signal_type] = []
            self._handlers[signal_type].append(handler)

        def emit(self, signal: Signal):
            handlers = self._handlers.get(signal.type, [])
            for handler in handlers:
                handler(signal)

    __all__ = ['Signal', 'SignalBus', 'SignalType']
