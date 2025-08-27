"""
Quantum Service Adapter - Connects QIM module to main system
Trinity Framework: ⚛️🧠🛡️
"""

import logging
from typing import Any

from lukhas.core.container.service_container import ServiceLifetime, injectable
from lukhas.core.interfaces.services import IQuantumService

logger = logging.getLogger(__name__)


@injectable(ServiceLifetime.SINGLETON)
class QIServiceAdapter(IQuantumService):
    """Adapts QIM quantum module to IQuantumService interface"""

    def __init__(self):
        self._initialized = False
        self._quantum_coordinator = None
        self._quantum_engine = None
        self._quantum_processor = None

    async def initialize(self) -> None:
        """Initialize quantum components"""
        if not self._initialized:
            try:
                # Try to import qim_components
                from qi.engines.consciousness.engine import QIEngine
                from qi.processing.qi_bio_coordinator import (
                    MockQuantumBioCoordinator,
                )
                from qi.qi_states.processor import QIProcessor

                self._quantum_coordinator = MockQuantumBioCoordinator()
                logger.info("QIM Quantum Bio Coordinator initialized")

            except ImportError as e:
                logger.warning(f"Some QIM components not available: {e}")
                # QIM can still function with reduced capability

            self._initialized = True
            logger.info("Quantum service adapter initialized")

    async def shutdown(self) -> None:
        """Cleanup quantum resources"""
        if self._quantum_coordinator and hasattr(self._quantum_coordinator, "cleanup"):
            await self._quantum_coordinator.cleanup()

    def get_health(self) -> dict[str, Any]:
        """Get quantum service health"""
        return {
            "status": "healthy" if self._initialized else "initializing",
            "initialized": self._initialized,
            "components": {
                "coordinator": self._quantum_coordinator is not None,
                "engine": self._quantum_engine is not None,
                "processor": self._quantum_processor is not None,
            },
            "module": "QIM (Quantum Inspire Module)"
        }

    async def process_quantum_state(self, state: Any) -> dict[str, Any]:
        """Process a quantum state"""
        await self.initialize()

        if self._quantum_coordinator:
            try:
                result = await self._quantum_coordinator.process_state(state)
                return {"status": "success", "result": result}
            except Exception as e:
                logger.error(f"Quantum processing error: {e}")
                return {"status": "error", "error": str(e)}

        # Fallback if no coordinator
        return {
            "status": "fallback",
            "result": "Quantum processing unavailable",
            "state": str(state)
        }

    async def get_quantum_entanglement(self) -> float:
        """Get current quantum entanglement level"""
        if self._quantum_coordinator:
            # Most QIM components have some form of coherence/entanglement metric
            return 0.95  # Placeholder - would call actual QIM method
        return 0.0


def register_quantum_service(container) -> None:
    """Register quantum service with container"""
    from candidate.core.interfaces.services import IQuantumService

    container.register(
        IQuantumService,
        QIServiceAdapter,
        ServiceLifetime.SINGLETON
    )
    logger.info("QIM Quantum Service registered ⚛️")
