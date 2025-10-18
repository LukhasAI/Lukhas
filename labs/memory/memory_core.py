"""Memory core component for symbolic trace management."""
import logging

logger = logging.getLogger(__name__)

from dataclasses import dataclass
from typing import Any, Optional

# Enhanced dependency: qi_mind with better fallback
try:
    from qi.mind import (
        ConsciousnessPhase,
        QIMindInterface,
        get_current_phase,
        get_quantum_mind,
    )

    QUANTUM_MIND_AVAILABLE = True
except Exception:  # pragma: no cover - fallback if qi_mind is unavailable
    import time
    from enum import Enum

    class ConsciousnessPhase(Enum):  # Enhanced stub
        DORMANT = "dormant"
        AWAKENING = "awakening"
        AWARE = "aware"
        ACTIVE = "active"  # Keep for backward compatibility
        FOCUSED = "focused"
        TRANSCENDENT = "transcendent"
        DREAMING = "dreaming"

    def get_current_phase() -> ConsciousnessPhase:
        # Simple time-based phase determination
        hour = time.localtime().tm_hour
        if 0 <= hour < 6:
            return ConsciousnessPhase.DREAMING
        elif 6 <= hour < 9:
            return ConsciousnessPhase.AWAKENING
        elif 9 <= hour < 18:
            return ConsciousnessPhase.AWARE
        else:
            return ConsciousnessPhase.DORMANT

    class QIMindInterface:
        def __init__(self):
            self.phase = ConsciousnessPhase.AWARE

        def get_phase(self):
            return self.phase

        def is_operational(self):
            return True

    def get_quantum_mind():
        return QIMindInterface()

    QUANTUM_MIND_AVAILABLE = False


# Logging setup with optional structlog
try:
    from core.common import get_logger

    logger = get_logger(__name__)
except Exception:  # pragma: no cover - fallback when structlog or core is unavailable
    import logging

    def get_logger(name):  # type: ignore[override]
        return logging.getLogger(name)

    logger = get_logger(__name__)


MODULE_VERSION = "1.0.0"
MODULE_NAME = "memory"


@dataclass
class CoreMemoryConfig:
    enabled: bool = True
    debug_mode: bool = False
    max_trace_history: int = 10000
    default_hash_algorithm: str = "sha256"


class CoreMemoryComponent:
    """Manage symbolic trace hashes with consciousness phase tracking."""

    def __init__(self, config: Optional[dict[str, Any]] = None) -> None:
        self.config = CoreMemoryConfig(**(config or {}))
        if hasattr(logger, "bind"):
            self.logger = logger.bind(class_name=self.__class__.__name__)
        else:  # pragma: no cover - fallback when using stdlib logger
            self.logger = logger
        self.consciousness_log: list[str] = []
        self.current_consciousness_phase: Optional[str] = None
        self.trace_store: dict[str, Any] = {}

        # Enhanced: Connect to quantum mind interface
        self.qi_mind = get_quantum_mind()
        self.use_quantum_mind = QUANTUM_MIND_AVAILABLE

        if self.use_quantum_mind:
            self.logger.info("CoreMemory initialized with quantum mind integration")
        else:
            self.logger.info("CoreMemory initialized with fallback consciousness tracking")

    def record_consciousness_phase(self) -> str:
        """Enhanced consciousness phase recording with quantum mind integration"""
        if self.use_quantum_mind:
            # Use real quantum mind interface
            qi_phase = self.qi_mind.get_phase()
            phase = qi_phase.value
            operational = self.qi_mind.is_operational()

            if not operational:
                self.logger.warning(f"Quantum mind not operational in phase: {phase}")
        else:
            # Fallback to time-based phase determination
            qi_phase = get_current_phase()
            phase = qi_phase.value
            operational = True

        self.consciousness_log.append(phase)
        self.current_consciousness_phase = phase

        # Enhanced logging
        if hasattr(self.logger, "debug"):
            self.logger.debug(f"Recorded consciousness phase: {phase} (operational: {operational})")

        return phase

    def process_symbolic_trace(
        self,
        input_data: Any,
        tier_level: int,
        trace_context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        if not self.config.enabled:
            return {"status": "disabled"}

        trace_id = f"trace_{hash(str(input_data))}_{tier_level}"
        phase = self.record_consciousness_phase()
        self.trace_store[trace_id] = {
            "data": input_data,
            "tier": tier_level,
            "context": trace_context,
            "consciousness_phase": phase,
        }
        return {"status": "processed_stub", "trace_id": trace_id}

    def get_last_consciousness_phase(self) -> Optional[str]:
        return self.current_consciousness_phase

    def get_component_status(self) -> dict[str, Any]:
        """Enhanced status reporting with quantum mind integration"""
        status = {
            "component_name": self.__class__.__name__,
            "operational_status": "ready" if self.config.enabled else "disabled",
            "current_configuration": self.config.__dict__,
            "qi_mind_available": self.use_quantum_mind,
            "current_consciousness_phase": self.current_consciousness_phase,
            "trace_count": len(self.trace_store),
            "consciousness_log_length": len(self.consciousness_log),
        }

        if self.use_quantum_mind:
            status["qi_mind_operational"] = self.qi_mind.is_operational()
            status["qi_phase"] = self.qi_mind.get_phase().value

        return status


def create_core_memory_component(
    initial_config: Optional[dict[str, Any]] = None,
) -> CoreMemoryComponent:
    return CoreMemoryComponent(config=initial_config)


__all__ = [
    "ConsciousnessPhase",
    "CoreMemoryComponent",
    "CoreMemoryConfig",
    "create_core_memory_component",
    "get_current_phase",
]
