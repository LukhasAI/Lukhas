# ΛTAG: orchestrator_signal, core_trace
# ΛLOCKED: true

"""
Symbolic Signal Router for the Lukhas AGI System.

This module provides a centralized signal routing and logging mechanism.
"""

import logging

from orchestration.signals import DiagnosticSignalType, SymbolicSignal

logger = logging.getLogger(__name__)


def route_signal(signal: SymbolicSignal, modules: dict = None):
    """
    Routes and logs a symbolic signal.

    Args:
        signal (SymbolicSignal): The signal to route.
        modules (dict, optional): A dictionary of available modules for routing. Defaults to None.
    """
    log_message = (
        f"SIGNAL ROUTED: "
        f"Type={signal.signal_type.value}, "
        f"Source={signal.source_module}, "
        f"Target={signal.target_module}, "
        f"Timestamp={signal.timestamp}, "
        f"DriftScore={signal.drift_score}, "
        f"CollapseHash={signal.collapse_hash}, "
        f"ConfidenceScore={signal.confidence_score}, "
        f"DiagnosticEvent={signal.diagnostic_event.value if signal.diagnostic_event else None}"
    )
    logger.info(log_message)

    # #ΛDIAGNOSE: phase_pulse
    if signal.diagnostic_event == DiagnosticSignalType.PULSE:
        logger.info("Phase pulse detected.")

    if not modules:
        logger.warning("No modules provided for routing. Signal was only logged.")
        return

    if signal.target_module and signal.target_module in modules:
        target_module = modules[signal.target_module]
        if hasattr(target_module, "handle_signal"):
            try:
                import asyncio
                # Assuming handle_signal can be async or sync.
                # A more robust system would use a queue and a dedicated worker.
                if asyncio.iscoroutinefunction(target_module.handle_signal):
                    asyncio.create_task(target_module.handle_signal(signal))
                else:
                    target_module.handle_signal(signal)
                logger.info(f"Signal dispatched to {signal.target_module}.")
            except Exception as e:
                logger.error(f"Error dispatching signal to {signal.target_module}: {e}", exc_info=True)
        else:
            logger.warning(f"Target module '{signal.target_module}' has no handle_signal method.")
    elif signal.target_module:
        logger.warning(f"Target module '{signal.target_module}' not found in provided modules.")
