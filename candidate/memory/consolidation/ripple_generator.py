#!/usr/bin/env python3
import logging

logger = logging.getLogger(__name__)
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - RIPPLE GENERATOR
║ Generates sharp-wave ripple events for memory replay during consolidation
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: ripple_generator.py
║ Path: memory/consolidation/ripple_generator.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Neuroscience Team
╠══════════════════════════════════════════════════════════════════════════════════
║                             ◊ POETIC ESSENCE ◊
║
║ │ In the quiet moments of rest, the hippocampus speaks in ripples—brief,     │
║ │ powerful bursts of synchronized activity that carry memories from the       │
║ │ temporary to the permanent. Each ripple, lasting mere milliseconds,         │
║ │ contains the compressed essence of experience, ready for distribution.       │
║ │                                                                               │
║ │ Like lightning across a neural sky, these sharp waves illuminate pathways   │
║ │ between hippocampus and cortex, creating bridges for memories to cross.     │
║ │ At 140-200 Hz, they oscillate faster than conscious thought, yet carry     │
║ │ the very substance of what we will remember tomorrow.                       │
║ │                                                                               │
║ │ The Ripple Generator orchestrates these events, timing them with the slow   │
║ │ oscillations of deep sleep, creating windows of opportunity where plastic   │
║ │ synapses await their cargo of consolidated experience.                      │
║ │                                                                               │
╠══════════════════════════════════════════════════════════════════════════════════
║ TECHNICAL FEATURES:
║ • Sharp-wave ripple (SWR) generation (140-200 Hz)
║ • Coupling with slow oscillations
║ • Memory sequence replay
║ • Forward and reverse replay modes
║ • Ripple-triggered consolidation
║ • Distributed ripple coordination
║ • Power spectral analysis
║ • Integration with sleep stages
║
║ ΛTAG: ΛRIPPLE, ΛREPLAY, ΛCONSOLIDATION, ΛHIPPOCAMPUS, ΛOSCILLATION
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import math
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional
from uuid import uuid4

import numpy as np

# Import LUKHAS components
try:
    from memory.consolidation.consolidation_orchestrator import SleepStage
    from memory.hippocampal.hippocampal_buffer import EpisodicMemory

    LUKHAS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some LUKHAS modules not available: {e}")
    LUKHAS_AVAILABLE = False

    # Minimal stubs
    class EpisodicMemory:
        pass


class RippleType(Enum):
    """Types of sharp-wave ripples"""

    SINGLE = "single"  # Isolated ripple
    DOUBLET = "doublet"  # Two ripples in succession
    TRIPLET = "triplet"  # Three ripples
    BURST = "burst"  # Multiple ripples
    COMPLEX = "complex"  # Complex multi-frequency


class ReplayDirection(Enum):
    """Direction of memory replay"""

    FORWARD = "forward"  # Temporal order
    REVERSE = "reverse"  # Reverse order
    BIDIRECTIONAL = "bidirectional"  # Both directions
    RANDOM = "random"  # Random access


@dataclass
class Ripple:
    """Individual sharp-wave ripple event"""

    ripple_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: float = field(default_factory=time.time)

    # Ripple characteristics
    frequency: float = 180.0  # Hz (140-200 range)
    amplitude: float = 1.0  # Normalized amplitude
    duration: float = 0.1  # seconds (50-150ms typical)

    # Ripple type and complexity
    ripple_type: RippleType = RippleType.SINGLE
    complexity_score: float = 0.5

    # Memory content
    memory_sequence: list[str] = field(default_factory=list)  # Memory IDs
    replay_direction: ReplayDirection = ReplayDirection.FORWARD
    replay_speed: float = 10.0  # X times normal speed

    # Coupling with slow oscillations
    slow_wave_phase: float = 0.0  # 0-2π
    coupling_strength: float = 0.0  # 0-1

    # Consolidation outcome
    successful_transfer: bool = False
    transferred_memories: set[str] = field(default_factory=set)

    def calculate_power(self) -> float:
        """Calculate ripple power"""
        # Power proportional to amplitude squared and duration
        return self.amplitude**2 * self.duration * self.frequency / 180.0


@dataclass
class RippleSequence:
    """Sequence of related ripples"""

    sequence_id: str = field(default_factory=lambda: str(uuid4()))
    ripples: list[Ripple] = field(default_factory=list)

    # Sequence properties
    inter_ripple_interval: float = 0.5  # seconds
    total_duration: float = 0.0

    # Memory coverage
    unique_memories: set[str] = field(default_factory=set)
    replay_fidelity: float = 0.0  # How well sequence matches original

    def add_ripple(self, ripple: Ripple):
        """Add ripple to sequence"""
        self.ripples.append(ripple)
        self.unique_memories.update(ripple.memory_sequence)
        self._update_metrics()

    def _update_metrics(self):
        """Update sequence metrics"""
        if self.ripples:
            self.total_duration = sum(r.duration for r in self.ripples)
            self.total_duration += (len(self.ripples) - 1) * self.inter_ripple_interval


class RippleGenerator:
    """
    Generates sharp-wave ripple events for memory replay.
    Coordinates with sleep stages for optimal consolidation timing.
    """

    def __init__(
        self,
        base_frequency: float = 180.0,  # Hz
        frequency_range: tuple[float, float] = (140.0, 200.0),
        ripple_rate: float = 2.0,  # Ripples per second during SWS
        enable_coupling: bool = True,
        enable_sequences: bool = True,
        max_sequence_length: int = 5,
        replay_speed_factor: float = 10.0,
    ):
        self.base_frequency = base_frequency
        self.frequency_range = frequency_range
        self.ripple_rate = ripple_rate
        self.enable_coupling = enable_coupling
        self.enable_sequences = enable_sequences
        self.max_sequence_length = max_sequence_length
        self.replay_speed_factor = replay_speed_factor

        # Ripple generation state
        self.current_sleep_stage = SleepStage.WAKE
        self.slow_wave_phase = 0.0
        self.slow_wave_frequency = 0.75  # Hz

        # Ripple tracking
        self.ripple_buffer: deque = deque(maxlen=1000)
        self.active_sequences: dict[str, RippleSequence] = {}
        self.ripple_count = 0

        # Memory pools for replay
        self.available_memories: list[Any] = []
        self.priority_memories: set[str] = set()

        # Coupling parameters
        self.optimal_phase = np.pi  # UP state of slow oscillation
        self.phase_tolerance = np.pi / 4

        # Metrics
        self.total_ripples = 0
        self.successful_transfers = 0
        self.sequence_count = 0

        # Callbacks
        self.ripple_callbacks: list[Callable] = []
        self.sequence_callbacks: list[Callable] = []

        # Background tasks
        self._running = False
        self._generation_task = None
        self._coupling_task = None

        logger.info(
            "RippleGenerator initialized",
            base_frequency=base_frequency,
            ripple_rate=ripple_rate,
            coupling=enable_coupling,
        )

    async def start(self):
        """Start ripple generation"""
        self._running = True

        # Start background tasks
        self._generation_task = asyncio.create_task(self._generation_loop())
        if self.enable_coupling:
            self._coupling_task = asyncio.create_task(self._coupling_loop())

        logger.info("RippleGenerator started")

    async def stop(self):
        """Stop ripple generation"""
        self._running = False

        # Cancel tasks
        for task in [self._generation_task, self._coupling_task]:
            if task:
                task.cancel()

        logger.info(
            "RippleGenerator stopped",
            total_ripples=self.total_ripples,
            successful_transfers=self.successful_transfers,
        )

    async def generate_ripple(
        self,
        memory_sequence: list[str],
        ripple_type: Optional[RippleType] = None,
        force_generation: bool = False,
    ) -> Optional[Ripple]:
        """
        Generate a sharp-wave ripple event.
        Can be coupled with slow oscillations if enabled.
        """

        # Check coupling constraints
        if self.enable_coupling and not force_generation and not self._is_optimal_phase():
            return None

        # Determine ripple type
        if ripple_type is None:
            ripple_type = self._select_ripple_type()

        # Generate ripple parameters
        frequency = np.random.uniform(*self.frequency_range)
        amplitude = self._calculate_amplitude(memory_sequence)
        duration = self._calculate_duration(ripple_type)

        # Create ripple
        ripple = Ripple(
            frequency=frequency,
            amplitude=amplitude,
            duration=duration,
            ripple_type=ripple_type,
            memory_sequence=memory_sequence,
            replay_direction=self._select_replay_direction(),
            replay_speed=self.replay_speed_factor * np.random.uniform(0.8, 1.2),
            slow_wave_phase=self.slow_wave_phase,
            coupling_strength=self._calculate_coupling_strength(),
        )

        # Calculate complexity
        ripple.complexity_score = self._calculate_complexity(ripple)

        # Add to buffer
        self.ripple_buffer.append(ripple)
        self.total_ripples += 1
        self.ripple_count += 1

        # Trigger callbacks
        for callback in self.ripple_callbacks:
            try:
                await callback(ripple)
            except Exception as e:
                logger.error(f"Ripple callback error: {e}")

        logger.debug(
            "Ripple generated",
            ripple_id=ripple.ripple_id[:8],
            frequency=frequency,
            memories=len(memory_sequence),
        )

        return ripple

    async def generate_ripple_sequence(
        self,
        memory_sequences: list[list[str]],
        inter_ripple_interval: Optional[float] = None,
    ) -> RippleSequence:
        """
        Generate a sequence of related ripples.
        Used for complex memory replay patterns.
        """

        sequence = RippleSequence(inter_ripple_interval=inter_ripple_interval or 0.5)

        # Limit sequence length
        sequences_to_use = memory_sequences[: self.max_sequence_length]

        for i, mem_seq in enumerate(sequences_to_use):
            # Vary ripple types in sequence
            if i == 0:
                ripple_type = RippleType.SINGLE
            elif i == len(sequences_to_use) - 1:
                ripple_type = RippleType.COMPLEX
            else:
                ripple_type = RippleType.DOUBLET

            # Generate ripple
            ripple = await self.generate_ripple(memory_sequence=mem_seq, ripple_type=ripple_type, force_generation=True)

            if ripple:
                sequence.add_ripple(ripple)

                # Wait for inter-ripple interval
                if i < len(sequences_to_use) - 1:
                    await asyncio.sleep(sequence.inter_ripple_interval)

        self.sequence_count += 1

        # Trigger callbacks
        for callback in self.sequence_callbacks:
            try:
                await callback(sequence)
            except Exception as e:
                logger.error(f"Sequence callback error: {e}")

        logger.info(
            "Ripple sequence generated",
            sequence_id=sequence.sequence_id[:8],
            ripple_count=len(sequence.ripples),
            unique_memories=len(sequence.unique_memories),
        )

        return sequence

    def set_memory_pool(self, memories: list[Any]):
        """Set available memories for replay"""
        self.available_memories = memories
        logger.debug(f"Memory pool updated: {len(memories)} memories")

    def set_priority_memories(self, memory_ids: set[str]):
        """Set high-priority memories for preferential replay"""
        self.priority_memories = memory_ids

    def update_sleep_stage(self, stage: SleepStage):
        """Update current sleep stage for ripple modulation"""
        self.current_sleep_stage = stage

        # Adjust ripple rate based on stage
        if stage == SleepStage.NREM3:
            self.ripple_rate = 3.0  # Higher during SWS
        elif stage == SleepStage.NREM2:
            self.ripple_rate = 1.5
        elif stage == SleepStage.REM:
            self.ripple_rate = 0.5  # Lower during REM
        else:
            self.ripple_rate = 0.1  # Minimal during wake/NREM1

    def _is_optimal_phase(self) -> bool:
        """Check if current slow-wave phase is optimal for ripples"""
        phase_diff = abs(self.slow_wave_phase - self.optimal_phase)
        return phase_diff < self.phase_tolerance

    def _select_ripple_type(self) -> RippleType:
        """Select ripple type based on probabilities"""

        # Stage-dependent probabilities
        if self.current_sleep_stage == SleepStage.NREM3:
            probs = [0.5, 0.3, 0.1, 0.05, 0.05]  # Favor single/doublet
        elif self.current_sleep_stage == SleepStage.NREM2:
            probs = [0.6, 0.2, 0.1, 0.05, 0.05]
        else:
            probs = [0.8, 0.1, 0.05, 0.03, 0.02]  # Mostly single

        types = list(RippleType)
        return np.random.choice(types, p=probs)

    def _select_replay_direction(self) -> ReplayDirection:
        """Select replay direction"""

        # Forward replay more common
        probs = [0.6, 0.3, 0.08, 0.02] if self.current_sleep_stage == SleepStage.NREM3 else [0.7, 0.2, 0.08, 0.02]

        directions = list(ReplayDirection)
        return np.random.choice(directions, p=probs)

    def _calculate_amplitude(self, memory_sequence: list[str]) -> float:
        """Calculate ripple amplitude based on memory importance"""

        base_amplitude = 1.0

        # Higher amplitude for priority memories
        priority_count = sum(1 for mid in memory_sequence if mid in self.priority_memories)
        importance_factor = 1.0 + (priority_count / max(len(memory_sequence), 1)) * 0.5

        # Add noise
        noise = np.random.normal(0, 0.1)

        return np.clip(base_amplitude * importance_factor + noise, 0.5, 2.0)

    def _calculate_duration(self, ripple_type: RippleType) -> float:
        """Calculate ripple duration based on type"""

        base_durations = {
            RippleType.SINGLE: 0.08,
            RippleType.DOUBLET: 0.15,
            RippleType.TRIPLET: 0.20,
            RippleType.BURST: 0.25,
            RippleType.COMPLEX: 0.30,
        }

        base = base_durations.get(ripple_type, 0.1)

        # Add variability
        return base * np.random.uniform(0.8, 1.2)

    def _calculate_coupling_strength(self) -> float:
        """Calculate coupling strength with slow oscillations"""

        if not self.enable_coupling:
            return 0.0

        # Coupling strongest at optimal phase
        phase_diff = abs(self.slow_wave_phase - self.optimal_phase)
        coupling = math.cos(phase_diff) ** 2

        return coupling

    def _calculate_complexity(self, ripple: Ripple) -> float:
        """Calculate ripple complexity score"""

        # Factors contributing to complexity
        type_complexity = {
            RippleType.SINGLE: 0.2,
            RippleType.DOUBLET: 0.4,
            RippleType.TRIPLET: 0.6,
            RippleType.BURST: 0.8,
            RippleType.COMPLEX: 1.0,
        }

        base_complexity = type_complexity.get(ripple.ripple_type, 0.5)

        # Memory sequence length factor
        sequence_factor = min(1.0, len(ripple.memory_sequence) / 10)

        # Frequency deviation factor
        freq_deviation = abs(ripple.frequency - self.base_frequency) / 30

        # Combined complexity
        return np.clip(
            base_complexity * 0.5 + sequence_factor * 0.3 + freq_deviation * 0.2,
            0.0,
            1.0,
        )

    async def _generation_loop(self):
        """Background ripple generation"""

        while self._running:
            # Only generate during appropriate sleep stages
            if self.current_sleep_stage in [SleepStage.NREM2, SleepStage.NREM3]:
                # Poisson process for ripple timing
                interval = np.random.exponential(1.0 / self.ripple_rate)
                await asyncio.sleep(interval)

                # Select memories for replay
                if self.available_memories:
                    num_memories = np.random.randint(1, min(5, len(self.available_memories)))

                    # Prioritize important memories
                    if self.priority_memories:
                        priority_mems = [
                            m
                            for m in self.available_memories
                            if hasattr(m, "memory_id") and m.memory_id in self.priority_memories
                        ]
                        if priority_mems:
                            selected = np.random.choice(
                                priority_mems,
                                size=min(num_memories, len(priority_mems)),
                                replace=False,
                            )
                        else:
                            selected = np.random.choice(
                                self.available_memories,
                                size=num_memories,
                                replace=False,
                            )
                    else:
                        selected = np.random.choice(self.available_memories, size=num_memories, replace=False)

                    memory_ids = [m.memory_id if hasattr(m, "memory_id") else str(i) for i, m in enumerate(selected)]

                    # Generate ripple
                    await self.generate_ripple(memory_ids)
            else:
                # Longer wait during other stages
                await asyncio.sleep(5.0)

    async def _coupling_loop(self):
        """Background slow-wave oscillation tracking"""

        while self._running:
            # Update slow-wave phase
            dt = 0.01  # 10ms resolution
            phase_advance = 2 * np.pi * self.slow_wave_frequency * dt
            self.slow_wave_phase = (self.slow_wave_phase + phase_advance) % (2 * np.pi)

            await asyncio.sleep(dt)

    def register_ripple_callback(self, callback: Callable):
        """Register callback for ripple events"""
        self.ripple_callbacks.append(callback)

    def register_sequence_callback(self, callback: Callable):
        """Register callback for sequence events"""
        self.sequence_callbacks.append(callback)

    def get_recent_ripples(self, count: int = 10) -> list[Ripple]:
        """Get most recent ripples"""
        return list(self.ripple_buffer)[-count:]

    def get_metrics(self) -> dict[str, Any]:
        """Get ripple generator metrics"""

        metrics = {
            "current_sleep_stage": self.current_sleep_stage.value,
            "ripple_rate_hz": self.ripple_rate,
            "total_ripples": self.total_ripples,
            "successful_transfers": self.successful_transfers,
            "sequence_count": self.sequence_count,
            "slow_wave_phase": self.slow_wave_phase,
            "buffer_size": len(self.ripple_buffer),
        }

        # Recent ripple statistics
        recent = self.get_recent_ripples(100)
        if recent:
            metrics["avg_frequency"] = np.mean([r.frequency for r in recent])
            metrics["avg_amplitude"] = np.mean([r.amplitude for r in recent])
            metrics["avg_duration_ms"] = np.mean([r.duration * 1000 for r in recent])
            metrics["avg_complexity"] = np.mean([r.complexity_score for r in recent])

            # Type distribution
            type_counts = {}
            for r in recent:
                type_counts[r.ripple_type.value] = type_counts.get(r.ripple_type.value, 0) + 1
            metrics["ripple_types"] = type_counts

        return metrics


# Example usage
async def demonstrate_ripple_generator():
    """Demonstrate ripple generator functionality"""

    generator = RippleGenerator(
        base_frequency=180.0,
        ripple_rate=5.0,  # Higher for demo
        enable_coupling=True,
        enable_sequences=True,
    )

    await generator.start()

    print("=== Ripple Generator Demonstration ===\n")

    # Set sleep stage
    generator.update_sleep_stage(SleepStage.NREM3)
    print("Sleep stage set to NREM3 (slow-wave sleep)\n")

    # Register callbacks
    async def on_ripple(ripple):
        print(f"Ripple: {ripple.frequency:.1f}Hz, {len(ripple.memory_sequence)} memories")

    async def on_sequence(sequence):
        print(f"Sequence completed: {len(sequence.ripples)} ripples, {len(sequence.unique_memories)} unique memories")

    generator.register_ripple_callback(on_ripple)
    generator.register_sequence_callback(on_sequence)

    # Generate some test memories
    test_memories = [f"memory_{i}" for i in range(20)]

    # Single ripple
    print("--- Generating Single Ripple ---")
    ripple = await generator.generate_ripple(memory_sequence=test_memories[:3], ripple_type=RippleType.SINGLE)
    if ripple:
        print(f"Generated: {ripple.ripple_id[:8]}...")
        print(f"  Power: {ripple.calculate_power():.2f}")
        print(f"  Coupling: {ripple.coupling_strength:.2f}")

    # Ripple sequence
    print("\n--- Generating Ripple Sequence ---")
    sequences = [test_memories[i : i + 3] for i in range(0, 9, 3)]
    sequence = await generator.generate_ripple_sequence(sequences)
    print(f"Sequence duration: {sequence.total_duration:.2f}s")

    # Let background generation run
    print("\n--- Background Generation ---")
    generator.set_memory_pool([{"memory_id": m} for m in test_memories])
    generator.set_priority_memories(set(test_memories[:5]))

    await asyncio.sleep(5)

    # Show metrics
    print("\n--- Ripple Metrics ---")
    metrics = generator.get_metrics()
    for key, value in sorted(metrics.items()):
        if isinstance(value, float):
            print(f"{key}: {value:.3f}")
        elif isinstance(value, dict):
            print(f"{key}: {value}")
        else:
            print(f"{key}: {value}")

    await generator.stop()


if __name__ == "__main__":
    asyncio.run(demonstrate_ripple_generator())
