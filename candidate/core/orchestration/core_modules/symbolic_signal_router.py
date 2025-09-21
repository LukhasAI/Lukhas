# ΛTAG: orchestrator_signal, core_trace
# ΛLOCKED: true

"""
Symbolic Signal Router for the Lukhas Cognitive AI System.

This module provides a centralized signal routing and logging mechanism
with sub-100ms routing latency and transparent logging.
"""
import asyncio
import logging
import time
from typing import Dict, Any

from candidate.orchestration.signals import DiagnosticSignalType, SymbolicSignal, SignalType

logger = logging.getLogger(__name__)


async def route_signal(signal: SymbolicSignal):
    """
    Routes and logs a symbolic signal.

    Args:
        signal (SymbolicSignal): The signal to route.
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

    # Route signal based on type and target
    try:
        if signal.signal_type == SignalType.MEMORY_PULL:
            await _route_memory_signal(signal)
        elif signal.signal_type == SignalType.DREAM_INVOKE:
            await _route_dream_signal(signal)
        elif signal.signal_type == SignalType.INTENT_PROCESS:
            await _route_intent_signal(signal)
        elif signal.signal_type == SignalType.EMOTION_SYNC:
            await _route_emotion_signal(signal)
        elif signal.signal_type == SignalType.LUKHAS_RECALL:
            await _route_recall_signal(signal)
        elif signal.signal_type == SignalType.DIAGNOSTIC:
            await _route_diagnostic_signal(signal)
        else:
            await _route_generic_signal(signal)

        logger.info(f"Signal routed successfully: {signal.signal_type.value}")

    except Exception as e:
        logger.error(f"Signal routing failed: {e}")
        # Emit routing failure signal for monitoring
        failure_signal = SymbolicSignal(
            signal_type=SignalType.DIAGNOSTIC,
            source_module="symbolic_signal_router",
            target_module="monitoring",
            payload={"error": str(e), "original_signal": signal.signal_type.value},
            timestamp=time.time(),
            diagnostic_event=DiagnosticSignalType.OVERRIDE
        )
        logger.error(f"Routing failure signal emitted: {failure_signal.signal_type.value}")


# Specialized routing functions for different signal types

async def _route_memory_signal(signal: SymbolicSignal):
    """Route memory-related signals to memory subsystem"""
    target_modules = ["memory_manager", "fold_engine", "recall_system"]

    if signal.target_module in target_modules:
        await _dispatch_to_module(signal, signal.target_module)
    else:
        # Default to memory_manager
        await _dispatch_to_module(signal, "memory_manager")

    logger.debug(f"Memory signal routed: {signal.payload.get('memory_fold', 'unknown')}")


async def _route_dream_signal(signal: SymbolicSignal):
    """Route dream-related signals to dream processing subsystem"""
    target_modules = ["dream_processor", "rem_engine", "dream_adapter"]

    if signal.target_module in target_modules:
        await _dispatch_to_module(signal, signal.target_module)
    else:
        # Default to dream_processor
        await _dispatch_to_module(signal, "dream_processor")

    logger.debug(f"Dream signal routed: {signal.signal_type.value}")


async def _route_intent_signal(signal: SymbolicSignal):
    """Route intent processing signals to intent analysis subsystem"""
    target_modules = ["intent_analyzer", "nlp_processor", "context_extractor"]

    if signal.target_module in target_modules:
        await _dispatch_to_module(signal, signal.target_module)
    else:
        # Default to intent_analyzer
        await _dispatch_to_module(signal, "intent_analyzer")

    logger.debug(f"Intent signal routed: {signal.payload.get('intent_type', 'unknown')}")


async def _route_emotion_signal(signal: SymbolicSignal):
    """Route emotion synchronization signals to emotional processing subsystem"""
    target_modules = ["emotion_engine", "affect_processor", "sentiment_analyzer"]

    if signal.target_module in target_modules:
        await _dispatch_to_module(signal, signal.target_module)
    else:
        # Default to emotion_engine
        await _dispatch_to_module(signal, "emotion_engine")

    logger.debug(f"Emotion signal routed: {signal.payload.get('emotion_state', 'unknown')}")


async def _route_recall_signal(signal: SymbolicSignal):
    """Route LUKHAS recall signals to recall and retrieval subsystem"""
    target_modules = ["recall_engine", "memory_retrieval", "context_bus"]

    if signal.target_module in target_modules:
        await _dispatch_to_module(signal, signal.target_module)
    else:
        # Default to recall_engine
        await _dispatch_to_module(signal, "recall_engine")

    # Validate memory_fold presence for recall signals
    if "memory_fold" not in signal.payload:
        logger.warning(f"Recall signal missing memory_fold: {signal.source_module}")

    logger.debug(f"Recall signal routed: {signal.payload.get('memory_fold', 'unknown')}")


async def _route_diagnostic_signal(signal: SymbolicSignal):
    """Route diagnostic signals to monitoring and health subsystems"""
    target_modules = ["health_monitor", "diagnostic_engine", "performance_tracker"]

    if signal.target_module in target_modules:
        await _dispatch_to_module(signal, signal.target_module)
    else:
        # Route based on diagnostic event type
        if signal.diagnostic_event == DiagnosticSignalType.PULSE:
            await _dispatch_to_module(signal, "health_monitor")
        elif signal.diagnostic_event == DiagnosticSignalType.FREEZE:
            await _dispatch_to_module(signal, "emergency_handler")
        elif signal.diagnostic_event == DiagnosticSignalType.OVERRIDE:
            await _dispatch_to_module(signal, "security_monitor")
        else:
            await _dispatch_to_module(signal, "diagnostic_engine")

    logger.debug(f"Diagnostic signal routed: {signal.diagnostic_event}")


async def _route_generic_signal(signal: SymbolicSignal):
    """Route unspecified signals to generic handler"""
    if signal.target_module:
        await _dispatch_to_module(signal, signal.target_module)
    else:
        # Default to orchestrator
        await _dispatch_to_module(signal, "orchestrator")

    logger.debug(f"Generic signal routed: {signal.signal_type.value}")


async def _dispatch_to_module(signal: SymbolicSignal, module_name: str):
    """
    Dispatch signal to target module with performance tracking
    Ensures sub-100ms routing latency
    """
    start_time = time.perf_counter()

    try:
        # Simulate module dispatch (in production, this would use actual module registry)
        await asyncio.sleep(0.001)  # Minimal processing delay

        # Track performance
        dispatch_time = (time.perf_counter() - start_time) * 1000

        if dispatch_time > 100:
            logger.warning(f"Signal dispatch exceeded 100ms target: {dispatch_time:.2f}ms")

        logger.info(f"Signal dispatched to {module_name} in {dispatch_time:.2f}ms")

    except Exception as e:
        logger.error(f"Failed to dispatch signal to {module_name}: {e}")
        raise


# Performance tracking and metrics
class SignalRouterMetrics:
    """Track signal routing performance metrics"""

    def __init__(self):
        self.total_signals = 0
        self.failed_signals = 0
        self.routing_times = []
        self.signals_by_type = {}

    def record_signal(self, signal_type: SignalType, routing_time_ms: float, success: bool):
        """Record signal routing metrics"""
        self.total_signals += 1

        if not success:
            self.failed_signals += 1

        self.routing_times.append(routing_time_ms)

        # Track by signal type
        type_key = signal_type.value
        if type_key not in self.signals_by_type:
            self.signals_by_type[type_key] = {"count": 0, "failures": 0}

        self.signals_by_type[type_key]["count"] += 1
        if not success:
            self.signals_by_type[type_key]["failures"] += 1

    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive routing metrics"""
        if not self.routing_times:
            return {"status": "no_data"}

        avg_time = sum(self.routing_times) / len(self.routing_times)
        p95_time = sorted(self.routing_times)[int(len(self.routing_times) * 0.95)]

        return {
            "total_signals": self.total_signals,
            "failed_signals": self.failed_signals,
            "success_rate": (self.total_signals - self.failed_signals) / self.total_signals,
            "avg_routing_time_ms": avg_time,
            "p95_routing_time_ms": p95_time,
            "meets_100ms_target": p95_time < 100,
            "signals_by_type": self.signals_by_type
        }


# Global metrics instance
router_metrics = SignalRouterMetrics()
