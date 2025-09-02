import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger("SymbolicSignals")


class SignalType(Enum):
    """Types of symbolic signals"""

    LUKHAS_RECALL = "lukhas:recall"
    MEMORY_PULL = "memory:pull"
    DREAM_INVOKE = "dream:invoke"
    DREAM_PUSH = "dream:push"
    INTENT_PROCESS = "intent:process"
    EMOTION_SYNC = "emotion:sync"
    AFFECT_DELTA = "affect:delta"
    DRIFT_ALERT = "drift:alert"
    COLLAPSE_TRIGGER = "collapse:trigger"
    DIAGNOSTIC = "diagnostic"


class DiagnosticSignalType(Enum):
    """Types of diagnostic signals"""

    INIT = "init"
    FREEZE = "freeze"
    OVERRIDE = "override"
    PULSE = "phase_pulse"


@dataclass
class SymbolicSignal:
    """
    ΛTAG: signal, orchestration, communication, symbolic_handshake
    ΛLOCKED: true

    Represents a symbolic communication signal between system components.
    """

    signal_type: SignalType
    source_module: str
    target_module: str
    payload: dict[str, Any]
    timestamp: float
    drift_score: Optional[float] = None
    collapse_hash: Optional[str] = None
    entropy_log: Optional[dict[str, Any]] = None
    confidence_score: Optional[float] = None
    diagnostic_event: Optional[DiagnosticSignalType] = None

    def __post_init__(self):
        """Add symbolic validation"""
        if self.timestamp == 0:
            self.timestamp = time.time()

        # Ensure symbolic consistency
        if (
            self.signal_type == SignalType.LUKHAS_RECALL
            and "memory_fold" not in self.payload
        ):
            logger.warning("lukhas:recall signal missing memory_fold")

        logger.info(
            f"Symbolic signal created: {self.signal_type.value} from {self.source_module} to {self.target_module}"
        )
