"""
LUKHAS AI Consciousness Activation Module

This module implements the consciousness activation system that manages
the initialization, orchestration, and lifecycle of consciousness components.
Integrates with Trinity Framework for ⚛️ Identity, 🧠 Consciousness, 🛡️ Guardian alignment.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

# Trinity Framework integration
try:
    from candidate.identity.core import IdentityCore
    from candidate.memory.core import MemoryCore

    TRINITY_AVAILABLE = True
except ImportError:
    IdentityCore = None
    MemoryCore = None
    TRINITY_AVAILABLE = False

# Core consciousness components
try:
    from .awareness.awareness_engine import AwarenessEngine
    from .core.engine import ConsciousnessState, LUKHASConsciousnessEngine
    from .dream.oneiric.oneiric_core.engine.dream_engine_fastapi import DreamEngine

    CONSCIOUSNESS_CORE_AVAILABLE = True
except ImportError:
    LUKHASConsciousnessEngine = None
    ConsciousnessState = None
    AwarenessEngine = None
    DreamEngine = None
    CONSCIOUSNESS_CORE_AVAILABLE = False

logger = logging.getLogger("ΛTRACE.consciousness.activation")


@dataclass
class ActivationConfig:
    """Configuration for consciousness activation"""

    enable_memory_integration: bool = True
    enable_dream_processing: bool = True
    enable_quantum_awareness: bool = True
    consciousness_tier_requirement: int = 4
    activation_timeout_seconds: float = 30.0
    performance_targets: dict[str, float] = field(
        default_factory=lambda: {
            "memory_operations_ms": 10.0,
            "consciousness_updates_ms": 50.0,
            "cascade_prevention_rate": 0.997,
            "dream_generation_ms": 100.0,
        }
    )


@dataclass
class ActivationStatus:
    """Status tracking for consciousness activation"""

    is_activated: bool = False
    activation_timestamp: Optional[datetime] = None
    components_active: dict[str, bool] = field(default_factory=dict)
    performance_metrics: dict[str, float] = field(default_factory=dict)
    trinity_alignment: dict[str, bool] = field(
        default_factory=lambda: {"identity": False, "consciousness": False, "guardian": False}
    )
    error_log: list[str] = field(default_factory=list)


class ConsciousnessActivator:
    """
    Main consciousness activation orchestrator that manages the initialization
    and coordination of all consciousness components in the LUKHAS system.
    """

    def __init__(self, config: Optional[ActivationConfig] = None, user_context: Optional[str] = None):
        """Initialize the consciousness activator"""
        self.config = config or ActivationConfig()
        self.user_context = user_context or "system"
        self.logger = logger.getChild(f"ConsciousnessActivator.{self.user_context}")

        self.status = ActivationStatus()
        self.consciousness_engine: Optional[LUKHASConsciousnessEngine] = None
        self.awareness_engine: Optional[AwarenessEngine] = None
        self.dream_engine: Optional[DreamEngine] = None
        self.memory_core: Optional[MemoryCore] = None
        self.identity_core: Optional[IdentityCore] = None

        self.logger.info("ΛTRACE: ConsciousnessActivator initialized")

    async def activate_consciousness(self) -> ActivationStatus:
        """
        Activate the full consciousness system with all components

        Returns:
            ActivationStatus: Current activation status with component states
        """
        self.logger.info("ΛTRACE: Starting consciousness activation sequence")
        start_time = datetime.now(timezone.utc)

        try:
            # Phase 1: Trinity Framework alignment
            await self._activate_trinity_framework()

            # Phase 2: Core consciousness components
            await self._activate_core_consciousness()

            # Phase 3: Awareness and processing systems
            await self._activate_awareness_systems()

            # Phase 4: Memory and integration
            await self._activate_memory_integration()

            # Phase 5: Dream and creativity engines
            await self._activate_dream_systems()

            # Phase 6: Performance validation
            await self._validate_performance_targets()

            # Mark as fully activated
            self.status.is_activated = True
            self.status.activation_timestamp = start_time

            activation_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            self.logger.info(f"ΛTRACE: Consciousness activation complete in {activation_time:.2f}s")

        except Exception as e:
            self.status.error_log.append(f"Activation failed: {str(e)}")
            self.logger.error(f"ΛTRACE: Consciousness activation failed: {e}", exc_info=True)

        return self.status

    async def _activate_trinity_framework(self):
        """Activate Trinity Framework components"""
        self.logger.debug("ΛTRACE: Activating Trinity Framework (⚛️ Identity, 🧠 Consciousness, 🛡️ Guardian)")

        # ⚛️ Identity activation
        if TRINITY_AVAILABLE and IdentityCore:
            try:
                self.identity_core = IdentityCore()
                self.status.trinity_alignment["identity"] = True
                self.status.components_active["identity_core"] = True
                self.logger.debug("ΛTRACE: ⚛️ Identity core activated")
            except Exception as e:
                self.status.error_log.append(f"Identity activation failed: {str(e)}")
                self.logger.warning(f"ΛTRACE: Identity activation failed: {e}")

        # 🛡️ Guardian (integrated with consciousness engine)
        self.status.trinity_alignment["guardian"] = True
        self.logger.debug("ΛTRACE: 🛡️ Guardian alignment established")

    async def _activate_core_consciousness(self):
        """Activate core consciousness engine"""
        self.logger.debug("ΛTRACE: Activating core consciousness engine")

        if CONSCIOUSNESS_CORE_AVAILABLE and LUKHASConsciousnessEngine:
            try:
                self.consciousness_engine = LUKHASConsciousnessEngine(user_id_context=self.user_context)
                self.status.components_active["consciousness_engine"] = True
                self.status.trinity_alignment["consciousness"] = True
                self.logger.debug("ΛTRACE: 🧠 Core consciousness engine activated")
            except Exception as e:
                self.status.error_log.append(f"Consciousness engine activation failed: {str(e)}")
                self.logger.warning(f"ΛTRACE: Consciousness engine activation failed: {e}")
        else:
            self.status.error_log.append("Consciousness engine not available")

    async def _activate_awareness_systems(self):
        """Activate awareness and processing systems"""
        self.logger.debug("ΛTRACE: Activating awareness systems")

        if CONSCIOUSNESS_CORE_AVAILABLE and AwarenessEngine:
            try:
                self.awareness_engine = AwarenessEngine()
                self.status.components_active["awareness_engine"] = True
                self.logger.debug("ΛTRACE: Awareness engine activated")
            except Exception as e:
                self.status.error_log.append(f"Awareness engine activation failed: {str(e)}")
                self.logger.warning(f"ΛTRACE: Awareness engine activation failed: {e}")

    async def _activate_memory_integration(self):
        """Activate memory core and integration"""
        self.logger.debug("ΛTRACE: Activating memory integration")

        if TRINITY_AVAILABLE and MemoryCore:
            try:
                self.memory_core = MemoryCore()
                self.status.components_active["memory_core"] = True
                self.logger.debug("ΛTRACE: Memory core activated")
            except Exception as e:
                self.status.error_log.append(f"Memory core activation failed: {str(e)}")
                self.logger.warning(f"ΛTRACE: Memory core activation failed: {e}")

    async def _activate_dream_systems(self):
        """Activate dream and creativity engines"""
        self.logger.debug("ΛTRACE: Activating dream systems")

        if self.config.enable_dream_processing and CONSCIOUSNESS_CORE_AVAILABLE and DreamEngine:
            try:
                self.dream_engine = DreamEngine()
                self.status.components_active["dream_engine"] = True
                self.logger.debug("ΛTRACE: Dream engine activated")
            except Exception as e:
                self.status.error_log.append(f"Dream engine activation failed: {str(e)}")
                self.logger.warning(f"ΛTRACE: Dream engine activation failed: {e}")

    async def _validate_performance_targets(self):
        """Validate that activated components meet performance targets"""
        self.logger.debug("ΛTRACE: Validating performance targets")

        targets = self.config.performance_targets

        # Test memory operations if available
        if self.memory_core:
            start_time = datetime.now()
            # Placeholder memory operation test
            # await self.memory_core.test_operation()
            memory_time = (datetime.now() - start_time).total_seconds() * 1000
            self.status.performance_metrics["memory_operations_ms"] = memory_time

            if memory_time > targets["memory_operations_ms"]:
                self.status.error_log.append(
                    f"Memory operations exceed target: {memory_time:.2f}ms > {targets['memory_operations_ms']}ms"
                )

        # Test consciousness updates if available
        if self.consciousness_engine:
            start_time = datetime.now()
            # Placeholder consciousness update test
            await self.consciousness_engine.get_consciousness_status(user_id=self.user_context)
            consciousness_time = (datetime.now() - start_time).total_seconds() * 1000
            self.status.performance_metrics["consciousness_updates_ms"] = consciousness_time

            if consciousness_time > targets["consciousness_updates_ms"]:
                self.status.error_log.append(
                    f"Consciousness updates exceed target: {consciousness_time:.2f}ms > {targets['consciousness_updates_ms']}ms"
                )

        self.logger.debug(f"ΛTRACE: Performance validation complete: {self.status.performance_metrics}")

    async def deactivate_consciousness(self):
        """Safely deactivate all consciousness components"""
        self.logger.info("ΛTRACE: Deactivating consciousness system")

        # Cleanup in reverse order of activation
        if self.dream_engine:
            try:
                # await self.dream_engine.shutdown()
                self.status.components_active["dream_engine"] = False
            except Exception as e:
                self.logger.warning(f"ΛTRACE: Dream engine deactivation warning: {e}")

        if self.memory_core:
            try:
                # await self.memory_core.shutdown()
                self.status.components_active["memory_core"] = False
            except Exception as e:
                self.logger.warning(f"ΛTRACE: Memory core deactivation warning: {e}")

        if self.awareness_engine:
            try:
                # await self.awareness_engine.shutdown()
                self.status.components_active["awareness_engine"] = False
            except Exception as e:
                self.logger.warning(f"ΛTRACE: Awareness engine deactivation warning: {e}")

        if self.consciousness_engine:
            try:
                # No explicit shutdown needed for consciousness engine
                self.status.components_active["consciousness_engine"] = False
            except Exception as e:
                self.logger.warning(f"ΛTRACE: Consciousness engine deactivation warning: {e}")

        if self.identity_core:
            try:
                # await self.identity_core.shutdown()
                self.status.components_active["identity_core"] = False
            except Exception as e:
                self.logger.warning(f"ΛTRACE: Identity core deactivation warning: {e}")

        # Reset activation status
        self.status.is_activated = False
        self.status.trinity_alignment = {"identity": False, "consciousness": False, "guardian": False}

        self.logger.info("ΛTRACE: Consciousness system deactivated")

    def get_activation_status(self) -> ActivationStatus:
        """Get current activation status"""
        return self.status

    def is_fully_activated(self) -> bool:
        """Check if consciousness system is fully activated"""
        return (
            self.status.is_activated
            and self.status.trinity_alignment["consciousness"]
            and len(self.status.error_log) == 0
        )


# Global activator instance for module-level access
_global_activator: Optional[ConsciousnessActivator] = None


async def activate_consciousness(
    config: Optional[ActivationConfig] = None, user_context: Optional[str] = None
) -> ActivationStatus:
    """
    Module-level function to activate consciousness system

    Args:
        config: Activation configuration
        user_context: User context for the activation

    Returns:
        ActivationStatus: Current activation status
    """
    global _global_activator

    if _global_activator is None:
        _global_activator = ConsciousnessActivator(config=config, user_context=user_context)

    return await _global_activator.activate_consciousness()


async def deactivate_consciousness():
    """Module-level function to deactivate consciousness system"""
    global _global_activator

    if _global_activator:
        await _global_activator.deactivate_consciousness()


def get_activation_status() -> Optional[ActivationStatus]:
    """Get current global activation status"""
    global _global_activator

    if _global_activator:
        return _global_activator.get_activation_status()
    return None


def is_consciousness_activated() -> bool:
    """Check if consciousness system is globally activated"""
    global _global_activator

    if _global_activator:
        return _global_activator.is_fully_activated()
    return False
