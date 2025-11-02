"""
Quantized Thought Cycles - ATP Synthase-Inspired Processing
Implements discrete, auditable cognitive cycles for LUKHAS AI

Based on biological ATP synthase rotary mechanism, this module ensures
all cognitive processing happens in discrete, measurable steps rather
than continuous flows. Each cycle transforms data in a clear, auditable way.

ΛTAG: ΛBIO, ΛCOGNITION, ΛQUANTUM, ΛCYCLE
"""

import asyncio
import json
import logging
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

from consciousness.qi import qi

logger = logging.getLogger("ΛTRACE.quantized_cycles")


class CyclePhase(Enum):
    """Phases of a thought cycle (inspired by ATP synthase rotation)"""

    BIND = "bind"  # Input binding phase
    CONFORM = "conform"  # Conformational change/processing
    CATALYZE = "catalyze"  # Core transformation
    RELEASE = "release"  # Output release phase


class CycleState(Enum):
    """Overall cycle state"""

    IDLE = "idle"
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"


@dataclass
class ThoughtQuantum:
    """A single quantum of thought - the atomic unit of processing"""

    id: str
    phase: CyclePhase
    input_data: Any
    output_data: Optional[Any] = None
    timestamp: float = field(default_factory=time.time)
    duration_ms: float = 0.0
    energy_units: int = 1  # Inspired by ATP energy units
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CycleMetrics:
    """Metrics for monitoring cycle performance"""

    total_cycles: int = 0
    successful_cycles: int = 0
    failed_cycles: int = 0
    total_energy_consumed: int = 0
    average_cycle_time_ms: float = 0.0
    current_frequency_hz: float = 0.0


class QuantizedThoughtProcessor:
    """
    Main processor implementing quantized thought cycles.
    Each cycle is discrete, auditable, and energy-aware.
    """

    def __init__(
        self,
        cycle_frequency_hz: float = 10.0,
        max_energy_per_cycle: int = 3,
        history_size: int = 1000,
    ):
        """
        Initialize the quantized thought processor.

        Args:
            cycle_frequency_hz: Target frequency for thought cycles
            max_energy_per_cycle: Maximum energy units per cycle
            history_size: Number of cycles to keep in history
        """
        self.cycle_frequency_hz = cycle_frequency_hz
        self.cycle_period_ms = 1000.0 / cycle_frequency_hz
        self.max_energy_per_cycle = max_energy_per_cycle

        # State management
        self.state = CycleState.IDLE
        self.current_phase = CyclePhase.BIND
        self.cycle_counter = 0

        # Processing pipeline
        self.phase_handlers: dict[CyclePhase, Callable] = {
            CyclePhase.BIND: self._bind_phase,
            CyclePhase.CONFORM: self._conform_phase,
            CyclePhase.CATALYZE: self._catalyze_phase,
            CyclePhase.RELEASE: self._release_phase,
        }

        # History and metrics
        self.cycle_history = deque(maxlen=history_size)
        self.metrics = CycleMetrics()

        # Input/output queues
        self.input_queue = asyncio.Queue()
        self.output_queue = asyncio.Queue()

        # Energy management
        self.energy_pool = 100  # Starting energy
        self.energy_regeneration_rate = 1  # Per cycle

        logger.info("🧬 Quantized Thought Processor initialized")
        logger.info(f"   - Target frequency: {cycle_frequency_hz} Hz")
        logger.info(f"   - Cycle period: {self.cycle_period_ms:.1f} ms")

    async def start(self):
        """Start the thought cycle processor"""
        if self.state != CycleState.IDLE:
            logger.warning("Processor already running")
            return

        self.state = CycleState.ACTIVE
        logger.info("⚡ Starting quantized thought cycles")

        # Start the main cycle loop
        asyncio.create_task(self._cycle_loop())

    async def stop(self):
        """Stop the thought cycle processor"""
        logger.info("🛑 Stopping quantized thought cycles")
        self.state = CycleState.IDLE

    async def pause(self):
        """Pause processing (maintains state)"""
        self.state = CycleState.PAUSED
        logger.info("⏸️ Thought cycles paused")

    async def resume(self):
        """Resume processing from paused state"""
        if self.state == CycleState.PAUSED:
            self.state = CycleState.ACTIVE
            logger.info("▶️ Thought cycles resumed")

    async def submit_thought(self, data: Any, energy_required: int = 1) -> str:
        """
        Submit data for processing in the next available cycle.

        Args:
            data: Input data to process
            energy_required: Energy units needed

        Returns:
            Thought quantum ID for tracking
        """
        quantum = ThoughtQuantum(
            id=f"Q-{self.cycle_counter}-{time.time()}",
            phase=CyclePhase.BIND,
            input_data=data,
            energy_units=energy_required,
        )

        await self.input_queue.put(quantum)
        return qi.id

    async def get_result(self, timeout: Optional[float] = None) -> Optional[ThoughtQuantum]:
        """Get processed result from output queue"""
        try:
            if timeout:
                return await asyncio.wait_for(self.output_queue.get(), timeout=timeout)
            else:
                return await self.output_queue.get()
        except asyncio.TimeoutError:
            return None

    async def _cycle_loop(self):
        """Main cycle loop - runs at specified frequency"""
        while self.state in [CycleState.ACTIVE, CycleState.PAUSED]:
            if self.state == CycleState.PAUSED:
                await asyncio.sleep(0.1)
                continue

            cycle_start = time.time()

            try:
                # Execute one complete thought cycle
                await self._execute_cycle()

                # Regenerate energy (only if we processed something)
                if self.cycle_counter % 10 == 0:  # Regenerate every 10 cycles
                    self.energy_pool = min(100, self.energy_pool + self.energy_regeneration_rate)

                # Calculate timing
                cycle_duration = (time.time() - cycle_start) * 1000
                sleep_time = max(0, (self.cycle_period_ms - cycle_duration) / 1000)

                # Update metrics
                self._update_metrics(cycle_duration, success=True)

                # Maintain frequency
                await asyncio.sleep(sleep_time)

            except Exception as e:
                logger.error(f"Cycle error: {e}")
                self._update_metrics(0, success=False)
                self.state = CycleState.ERROR

    async def _execute_cycle(self):
        """Execute one complete thought cycle through all phases"""
        self.cycle_counter += 1

        # Try to get input (non-blocking)
        quantum = None
        try:
            quantum = self.input_queue.get_nowait()
        except asyncio.QueueEmpty:
            # No input, idle cycle
            return

        # Check energy availability
        if qi.energy_units > self.energy_pool:
            logger.warning(f"Insufficient energy for quantum {qi.id}")
            qi.metadata["error"] = "insufficient_energy"
            await self.output_queue.put(quantum)
            return

        # Process through all phases
        cycle_log = {
            "cycle": self.cycle_counter,
            "qi_id": qi.id,
            "phases": [],
        }

        for phase in CyclePhase:
            phase_start = time.time()
            qi.phase = phase

            # Execute phase handler
            handler = self.phase_handlers[phase]
            quantum = await handler(quantum)

            phase_duration = (time.time() - phase_start) * 1000
            cycle_log["phases"].append(
                {
                    "phase": phase.value,
                    "duration_ms": phase_duration,
                    "success": qi.metadata.get("error") is None,
                }
            )

            # Stop if error
            if qi.metadata.get("error"):
                break

        # Consume energy
        self.energy_pool -= qi.energy_units
        qi.duration_ms = sum(p["duration_ms"] for p in cycle_log["phases"])

        # Record in history
        self.cycle_history.append(cycle_log)

        # Output result
        await self.output_queue.put(quantum)

    async def _bind_phase(self, quantum: ThoughtQuantum) -> ThoughtQuantum:
        """Bind phase - prepare and validate input"""
        # Simulate binding delay
        await asyncio.sleep(0.001)

        # Validate input
        if qi.input_data is None:
            qi.metadata["error"] = "null_input"

        qi.metadata["bound_at"] = time.time()
        return quantum

    async def _conform_phase(self, quantum: ThoughtQuantum) -> ThoughtQuantum:
        """Conformational change - prepare for processing"""
        # Simulate conformational change
        await asyncio.sleep(0.002)

        # Transform input format if needed
        if isinstance(qi.input_data, str):
            qi.metadata["input_type"] = "string"
        elif isinstance(qi.input_data, dict):
            qi.metadata["input_type"] = "dict"
        else:
            qi.metadata["input_type"] = "other"

        return quantum

    async def _catalyze_phase(self, quantum: ThoughtQuantum) -> ThoughtQuantum:
        """Catalyze phase - main transformation"""
        # Simulate main processing
        await asyncio.sleep(0.005)

        # Example transformation - this is where real processing happens
        if isinstance(qi.input_data, str):
            qi.output_data = {
                "processed": qi.input_data.upper(),
                "length": len(qi.input_data),
                "cycle": self.cycle_counter,
            }
        elif isinstance(qi.input_data, dict):
            qi.output_data = {
                "keys": list(qi.input_data.keys()),
                "processed": True,
                "cycle": self.cycle_counter,
            }
        else:
            qi.output_data = {
                "type": str(type(qi.input_data)),
                "processed": True,
                "cycle": self.cycle_counter,
            }

        qi.metadata["catalyzed"] = True
        return quantum

    async def _release_phase(self, quantum: ThoughtQuantum) -> ThoughtQuantum:
        """Release phase - finalize and output"""
        # Simulate release
        await asyncio.sleep(0.001)

        qi.metadata["completed_at"] = time.time()
        qi.metadata["total_phases"] = 4

        return quantum

    def _update_metrics(self, cycle_duration_ms: float, success: bool):
        """Update performance metrics"""
        self.metrics.total_cycles += 1

        if success:
            self.metrics.successful_cycles += 1
        else:
            self.metrics.failed_cycles += 1

        # Update average cycle time
        if self.metrics.total_cycles > 1:
            avg = self.metrics.average_cycle_time_ms
            self.metrics.average_cycle_time_ms = (
                avg * (self.metrics.total_cycles - 1) + cycle_duration_ms
            ) / self.metrics.total_cycles
        else:
            self.metrics.average_cycle_time_ms = cycle_duration_ms

        # Calculate current frequency
        if cycle_duration_ms > 0:
            self.metrics.current_frequency_hz = 1000.0 / cycle_duration_ms

    def get_cycle_trace(self, last_n: int = 10) -> list[dict[str, Any]]:
        """Get trace of last N cycles for auditing"""
        return list(self.cycle_history)[-last_n:]

    def get_metrics(self) -> dict[str, Any]:
        """Get current performance metrics"""
        return {
            "total_cycles": self.metrics.total_cycles,
            "successful_cycles": self.metrics.successful_cycles,
            "failed_cycles": self.metrics.failed_cycles,
            "success_rate": (
                self.metrics.successful_cycles / self.metrics.total_cycles if self.metrics.total_cycles > 0 else 0
            ),
            "average_cycle_time_ms": round(self.metrics.average_cycle_time_ms, 2),
            "current_frequency_hz": round(self.metrics.current_frequency_hz, 2),
            "target_frequency_hz": self.cycle_frequency_hz,
            "energy_pool": self.energy_pool,
            "state": self.state.value,
        }


# Example usage and testing


async def demo_quantized_cycles():
    """Demonstrate quantized thought cycles"""

    # Create processor
    processor = QuantizedThoughtProcessor(
        cycle_frequency_hz=20.0,  # 20 Hz = 50ms per cycle
        max_energy_per_cycle=5,
    )

    # Start processor
    await processor.start()

    # Submit some thoughts
    thought_ids = []
    for i in range(5):
        thought_id = await processor.submit_thought(f"Test thought {i}", energy_required=1)
        thought_ids.append(thought_id)
        logger.info(f"Submitted thought: {thought_id}")

    # Wait for results
    results = []
    for _ in range(5):
        result = await processor.get_result(timeout=1.0)
        if result:
            results.append(result)
            logger.info(f"Got result: {result.id} -> {result.output_data}")

    # Get metrics
    metrics = processor.get_metrics()
    logger.info(f"Metrics: {json.dumps(metrics, indent=2)}")

    # Get cycle trace
    trace = processor.get_cycle_trace(last_n=5)
    logger.info(f"Last 5 cycles: {json.dumps(trace, indent=2)}")

    # Stop processor
    await processor.stop()


if __name__ == "__main__":
    asyncio.run(demo_quantized_cycles())
