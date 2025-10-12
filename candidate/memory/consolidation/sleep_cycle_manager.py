#!/usr/bin/env python3
import logging
from datetime import timezone
import streamlit as st
import random
logger = logging.getLogger(__name__)
"""
==================================================================================
|  LUKHAS AI - SLEEP CYCLE MANAGER
| Manages detailed sleep stage transitions and ultradian rhythms
| Copyright (c) 2025 LUKHAS AI. All rights reserved.
+==================================================================================
| Module: sleep_cycle_manager.py
| Path: memory/consolidation/sleep_cycle_manager.py
| Version: 1.0.0 | Created: 2025-7-29
| Authors: LUKHAS AI Neuroscience Team
+==================================================================================
|                              POETIC ESSENCE
|
| | In the rhythmic dance of consciousness and rest, the Sleep Cycle Manager    |
| | orchestrates the ebb and flow of awareness. Like tides governed by an       |
| | unseen moon, it guides the mind through depths of NREM and heights of REM,  |
| | each phase a different shade of consciousness, each transition a gateway.    |
| |                                                                               |
| | Ninety minutes, the golden ratio of sleep-long enough for complete          |
| | consolidation, short enough for multiple cycles. In this temporal           |
| | architecture, memories find their proper home: the urgent becomes           |
| | important, the important becomes essential, the essential becomes self.      |
| |                                                                               |
| | Through spindles and slow waves, through theta and delta, the manager       |
| | conducts a symphony of neural oscillations, each frequency carrying its     |
| | own cargo of consciousness from the shores of today to the islands of       |
| | tomorrow.                                                                     |
| |                                                                               |
+==================================================================================
| TECHNICAL FEATURES:
| * Ultradian rhythm management (90-minute cycles)
| * Detailed sleep stage modeling
| * Circadian rhythm integration
| * Sleep pressure dynamics
| * Stage-specific oscillation patterns
| * Adaptive cycle adjustment
| * Sleep quality metrics
| * Integration with memory systems
|
| TAG: SLEEP, RHYTHM, CIRCADIAN, ULTRADIAN, CONSOLIDATION
+==================================================================================
"""

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional
from uuid import uuid4

import numpy as np

from memory.consolidation.consolidation_orchestrator import SleepStage


class CircadianPhase(Enum):
    """Circadian rhythm phase"""

    MORNING = "morning"  # 6am-12pm
    AFTERNOON = "afternoon"  # 12pm-6pm
    EVENING = "evening"  # 6pm-12am
    NIGHT = "night"  # 12am-6am


class SleepPressure(Enum):
    """Homeostatic sleep pressure level"""

    LOW = "low"  # Just woke up
    MODERATE = "moderate"  # Mid-day
    HIGH = "high"  # Evening
    CRITICAL = "critical"  # Sleep deprived


@dataclass
class SleepCycle:
    """Individual sleep cycle representation"""

    cycle_id: str = field(default_factory=lambda: str(uuid4()))
    cycle_number: int = 0
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None

    # Stage durations (seconds)
    stage_durations: dict[SleepStage, float] = field(default_factory=dict)
    stage_transitions: list[tuple[SleepStage, SleepStage, float]] = field(default_factory=list)

    # Cycle characteristics
    rem_proportion: float = 0.2  # Increases with cycle number
    sws_proportion: float = 0.3  # Decreases with cycle number

    # Quality metrics
    fragmentation_index: float = 0.0  # 0-1, lower is better
    consolidation_score: float = 0.0  # 0-1, higher is better

    def calculate_duration(self) -> float:
        """Calculate total cycle duration"""
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time

    def get_stage_proportion(self, stage: SleepStage) -> float:
        """Get proportion of time spent in stage"""
        total_duration = sum(self.stage_durations.values())
        if total_duration == 0:
            return 0.0
        return self.stage_durations.get(stage, 0.0) / total_duration


@dataclass
class SleepArchitecture:
    """Overall sleep architecture parameter"""

    total_sleep_time: float = 0.0
    sleep_efficiency: float = 0.0  # Time asleep / Time in bed
    sleep_onset_latency: float = 0.0
    rem_latency: float = 0.0

    # Stage percentages
    wake_percentage: float = 0.0
    nrem1_percentage: float = 0.0
    nrem2_percentage: float = 0.0
    nrem3_percentage: float = 0.0
    rem_percentage: float = 0.0

    # Cycle metrics
    cycle_count: int = 0
    average_cycle_duration: float = 90.0  # minutes

    # Fragmentation
    arousal_index: float = 0.0  # Arousals per hour
    wake_after_sleep_onset: float = 0.0  # WASO


class SleepCycleManager:
    """
    Manages detailed sleep cycle progression and ultradian rhythms.
    Coordinates with consolidation orchestrator for memory processing.
    """

    def __init__(
        self,
        base_cycle_duration: float = 90.0,  # minutes
        enable_circadian: bool = True,
        enable_adaptive: bool = True,
        sleep_pressure_decay: float = 0.1,
        rem_progression_rate: float = 0.5,
        initial_sleep_pressure: float = 0.5,
    ):
        self.base_cycle_duration = base_cycle_duration
        self.enable_circadian = enable_circadian
        self.enable_adaptive = enable_adaptive
        self.sleep_pressure_decay = sleep_pressure_decay
        self.rem_progression_rate = rem_progression_rate

        # State management
        self.current_stage = SleepStage.WAKE
        self.sleep_pressure = initial_sleep_pressure
        self.time_awake = 0.0
        self.last_sleep_time = time.time()

        # Sleep cycles
        self.current_cycle: Optional[SleepCycle] = None
        self.cycle_history: list[SleepCycle] = []
        self.total_cycles = 0

        # Architecture tracking
        self.architecture = SleepArchitecture()
        self.stage_start_time = time.time()
        self.time_in_stages: dict[SleepStage, float] = dict.fromkeys(SleepStage, 0.0)

        # Oscillation parameters
        self.delta_power = 1.0  # Slow-wave activity
        self.theta_power = 0.5  # REM theta
        self.spindle_density = 0.0  # Sleep spindles

        # Callbacks
        self.stage_callbacks: list[Callable] = []
        self.cycle_callbacks: list[Callable] = []

        # Background tasks
        self._running = False
        self._pressure_task = None
        self._rhythm_task = None

        logger.info(
            "SleepCycleManager initialized",
            base_cycle_duration=base_cycle_duration,
            circadian=enable_circadian,
            adaptive=enable_adaptive,
        )

    async def start(self):
        """Start sleep cycle management"""
        self._running = True

        # Start background tasks
        self._pressure_task = asyncio.create_task(self._sleep_pressure_loop())
        self._rhythm_task = asyncio.create_task(self._ultradian_rhythm_loop())

        logger.info("SleepCycleManager started")

    async def stop(self):
        """Stop sleep cycle management"""
        self._running = False

        # End current cycle
        if self.current_cycle:
            self.current_cycle.end_time = time.time()
            self.cycle_history.append(self.current_cycle)
            self.current_cycle = None

        # Cancel tasks
        for task in [self._pressure_task, self._rhythm_task]:
            if task:
                task.cancel()

        logger.info(
            "SleepCycleManager stopped",
            total_cycles=self.total_cycles,
            total_sleep_time=self.architecture.total_sleep_time,
        )

    async def initiate_sleep(self) -> str:
        """
        Initiate sleep period and first cycle.
        Returns cycle ID.
        """

        # Create new cycle
        self.total_cycles += 1
        self.current_cycle = SleepCycle(
            cycle_number=self.total_cycles,
            rem_proportion=0.15 + (self.total_cycles - 1) * self.rem_progression_rate,
            sws_proportion=0.4 - (self.total_cycles - 1) * 0.5,
        )

        # Transition to NREM1
        await self.transition_stage(SleepStage.NREM1)

        # Update architecture
        self.architecture.sleep_onset_latency = time.time() - self.last_sleep_time
        self.architecture.cycle_count += 1

        logger.info(
            f"Sleep initiated - Cycle {self.total_cycles}",
            cycle_id=self.current_cycle.cycle_id,
            sleep_pressure=self.sleep_pressure,
        )

        return self.current_cycle.cycle_id

    async def transition_stage(self, new_stage: SleepStage):
        """Transition to new sleep stage"""

        old_stage = self.current_stage

        # Update time tracking
        current_time = time.time()
        stage_duration = current_time - self.stage_start_time
        self.time_in_stages[old_stage] += stage_duration

        # Update cycle tracking
        if self.current_cycle and old_stage != SleepStage.WAKE:
            # SYNTAX_ERROR_FIXED:
            # self.current_cycle.stage_durations[old_stage] = " +
            # "self.current_cycle.stage_durations.get(old_stage, 0) + stage_duration
            self.current_cycle.stage_transitions.append((old_stage, new_stage, current_time))

        # Transition
        self.current_stage = new_stage
        self.stage_start_time = current_time

        # Update oscillation parameters
        self._update_oscillations(new_stage)

        # Trigger callbacks
        for callback in self.stage_callbacks:
            try:
                await callback(old_stage, new_stage)
            except Exception as e:
                logger.error(f"Stage callback error: {e}")

        logger.debug(f"Stage transition: {old_stage.value} -> {new_stage.value}")

    def get_stage_duration(self, stage: SleepStage) -> dict[str, float]:
        """
        Get optimal stage duration based on cycle number and circadian phase.
        Returns min, target, and max durations in seconds.
        """

        cycle_num = self.total_cycles

        # Base durations (minutes)
        base_durations = {
            SleepStage.WAKE: (0, 0, 5),
            SleepStage.NREM1: (5, 7, 10),
            SleepStage.NREM2: (20, 30, 40),
            SleepStage.NREM3: (15, 25, 40),
            SleepStage.REM: (10, 20, 30),
        }

        min_dur, target_dur, max_dur = base_durations.get(stage, (5, 10, 15))

        # Adjust for cycle progression
        if stage == SleepStage.NREM3:
            # SWS decreases with cycles
            factor = max(0.3, 1.0 - (cycle_num - 1) * 0.2)
            target_dur *= factor
        elif stage == SleepStage.REM:
            # REM increases with cycles
            factor = min(2.0, 1.0 + (cycle_num - 1) * 0.3)
            target_dur *= factor

        # Circadian adjustments
        if self.enable_circadian:
            circadian_phase = self._get_circadian_phase()
            if circadian_phase == CircadianPhase.NIGHT and stage == SleepStage.NREM3:
                target_dur *= 1.2
            elif circadian_phase == CircadianPhase.MORNING and stage == SleepStage.REM:
                target_dur *= 1.3

        # Convert to seconds
        return {"min": min_dur * 60, "target": target_dur * 60, "max": max_dur * 60}

    def get_next_stage(self, current: SleepStage) -> SleepStage:
        """Determine next sleep stage based on normal progression"""

        # Normal progression
        progression = {
            SleepStage.WAKE: SleepStage.NREM1,
            SleepStage.NREM1: SleepStage.NREM2,
            SleepStage.NREM2: SleepStage.NREM3,
            SleepStage.NREM3: SleepStage.NREM2,  # Back to NREM2
            SleepStage.REM: SleepStage.NREM2,  # Back to NREM2
        }

        next_stage = progression.get(current, SleepStage.WAKE)

        # Cycle-specific adjustments
        if self.current_cycle:
            # Skip NREM3 in later cycles
            if next_stage == SleepStage.NREM3 and self.total_cycles > 3:
                if np.random.random() > 0.3:  # 70% chance to skip
                    next_stage = SleepStage.REM

            # REM rebound if pressure is high
            if current == SleepStage.NREM2 and self._calculate_rem_pressure() > 0.7:
                next_stage = SleepStage.REM

        return next_stage

    def _update_oscillations(self, stage: SleepStage):
        """Update oscillation parameters for stage"""

        if stage == SleepStage.NREM3:
            self.delta_power = 1.0
            self.theta_power = 0.1
            self.spindle_density = 0.3
        elif stage == SleepStage.NREM2:
            self.delta_power = 0.3
            self.theta_power = 0.2
            self.spindle_density = 0.8
        elif stage == SleepStage.REM:
            self.delta_power = 0.1
            self.theta_power = 0.9
            self.spindle_density = 0.0
        elif stage == SleepStage.NREM1:
            self.delta_power = 0.2
            self.theta_power = 0.4
            self.spindle_density = 0.1
        else:  # WAKE
            self.delta_power = 0.0
            self.theta_power = 0.3
            self.spindle_density = 0.0

    def _get_circadian_phase(self) -> CircadianPhase:
        """Get current circadian phase"""

        hour = datetime.now(timezone.utc).hour

        if 6 <= hour < 12:
            return CircadianPhase.MORNING
        elif 12 <= hour < 18:
            return CircadianPhase.AFTERNOON
        elif 18 <= hour < 24:
            return CircadianPhase.EVENING
        else:
            return CircadianPhase.NIGHT

    def _calculate_sleep_pressure(self) -> SleepPressure:
        """Calculate current sleep pressure level"""

        if self.sleep_pressure < 0.25:
            return SleepPressure.LOW
        elif self.sleep_pressure < 0.5:
            return SleepPressure.MODERATE
        elif self.sleep_pressure < 0.75:
            return SleepPressure.HIGH
        else:
            return SleepPressure.CRITICAL

    def _calculate_rem_pressure(self) -> float:
        """Calculate REM sleep pressure"""

        # Time since last REM
        time_since_rem = 0.0
        for cycle in reversed(self.cycle_history):
            if SleepStage.REM in cycle.stage_durations:
                break
            time_since_rem += cycle.calculate_duration()

        # REM pressure increases with time
        rem_pressure = min(1.0, time_since_rem / (90 * 60))  # Max after 90 min

        # Circadian modulation
        if self.enable_circadian:
            phase = self._get_circadian_phase()
            if phase == CircadianPhase.MORNING:
                rem_pressure *= 1.3
            elif phase == CircadianPhase.NIGHT:
                rem_pressure *= 0.7

        return rem_pressure

    async def _sleep_pressure_loop(self):
        """Background sleep pressure dynamic"""

        while self._running:
            # Update time awake
            if self.current_stage == SleepStage.WAKE:
                self.time_awake += 1.0
                # Increase sleep pressure (Process S)
                self.sleep_pressure = min(1.0, self.sleep_pressure + 0.01)
            else:
                # Decrease sleep pressure during sleep
                self.sleep_pressure = max(0.0, self.sleep_pressure - self.sleep_pressure_decay / 60)

            # Update architecture
            total_time = sum(self.time_in_stages.values())
            if total_time > 0:
                self.architecture.total_sleep_time = total_time - self.time_in_stages[SleepStage.WAKE]
                self.architecture.sleep_efficiency = self.architecture.total_sleep_time / total_time

                # Update stage percentages
                for stage in SleepStage:
                    percentage = (self.time_in_stages[stage] / total_time) * 100
                    setattr(self.architecture, f"{stage.value}_percentage", percentage)

            await asyncio.sleep(1)  # Update every second

    async def _ultradian_rhythm_loop(self):
        """Background ultradian rhythm management"""

        while self._running:
            if self.current_cycle and self.current_stage != SleepStage.WAKE:
                # Check if time for stage transition
                current_duration = time.time() - self.stage_start_time
                stage_limits = self.get_stage_duration(self.current_stage)

                if current_duration > stage_limits["target"]:
                    # Time to transition
                    next_stage = self.get_next_stage(self.current_stage)
                    await self.transition_stage(next_stage)

                    # Check if cycle complete
                    cycle_duration = self.current_cycle.calculate_duration()
                    if cycle_duration > self.base_cycle_duration * 60:
                        await self._complete_cycle()

            await asyncio.sleep(5)  # Check every 5 seconds

    async def _complete_cycle(self):
        """Complete current sleep cycle"""

        if not self.current_cycle:
            return

        self.current_cycle.end_time = time.time()

        # Calculate quality metrics
        transitions = len(self.current_cycle.stage_transitions)
        expected_transitions = 5  # Typical cycle
        self.current_cycle.fragmentation_index = min(1.0, transitions / (expected_transitions * 2))

        # Consolidation score based on SWS and REM proportions
        sws_score = self.current_cycle.get_stage_proportion(SleepStage.NREM3)
        rem_score = self.current_cycle.get_stage_proportion(SleepStage.REM)
        self.current_cycle.consolidation_score = (sws_score + rem_score) / 2

        self.cycle_history.append(self.current_cycle)

        # Trigger callbacks
        for callback in self.cycle_callbacks:
            try:
                await callback(self.current_cycle)
            except Exception as e:
                logger.error(f"Cycle callback error: {e}")

        logger.info(
            f"Cycle {self.current_cycle.cycle_number} completed",
            duration_minutes=self.current_cycle.calculate_duration() / 60,
            consolidation_score=self.current_cycle.consolidation_score,
        )

        # Decide whether to start new cycle or wake
        if self.sleep_pressure < 0.2 or self.total_cycles >= 5:
            await self.transition_stage(SleepStage.WAKE)
            self.current_cycle = None
        else:
            # Start new cycle
            await self.initiate_sleep()

    def register_stage_callback(self, callback: Callable):
        """Register callback for stage transition"""
        self.stage_callbacks.append(callback)

    def register_cycle_callback(self, callback: Callable):
        """Register callback for cycle completion"""
        self.cycle_callbacks.append(callback)

    def get_metrics(self) -> dict[str, Any]:
        """Get sleep cycle metric"""

        # Current state
        metrics = {
            "current_stage": self.current_stage.value,
            "sleep_pressure": self.sleep_pressure,
            "sleep_pressure_level": self._calculate_sleep_pressure().value,
            "total_cycles": self.total_cycles,
            "time_awake_hours": self.time_awake / 3600,
            "delta_power": self.delta_power,
            "theta_power": self.theta_power,
            "spindle_density": self.spindle_density,
        }

        # Architecture metrics
        arch_dict = self.architecture.__dict__
        for key, value in arch_dict.items():
            if isinstance(value, float):
                metrics[f"architecture_{key}"] = round(value, 2)
            else:
                metrics[f"architecture_{key}"] = value

        # Current cycle metrics
        if self.current_cycle:
            metrics["current_cycle_id"] = self.current_cycle.cycle_id
            metrics["current_cycle_duration_min"] = self.current_cycle.calculate_duration() / 60
            metrics["current_cycle_rem_prop"] = self.current_cycle.rem_proportion
            metrics["current_cycle_sws_prop"] = self.current_cycle.sws_proportion

        # History metrics
        if self.cycle_history:
            avg_duration = np.mean([c.calculate_duration() for c in self.cycle_history]) / 60
            avg_consolidation = np.mean([c.consolidation_score for c in self.cycle_history])
            metrics["average_cycle_duration_min"] = avg_duration
            metrics["average_consolidation_score"] = avg_consolidation

        return metrics


# Example usage
async def demonstrate_sleep_cycle_manager():
    """Demonstrate sleep cycle manager functionality"""

    manager = SleepCycleManager(
        base_cycle_duration=1.5,  # 1.5 minutes for demo
        enable_circadian=True,
        enable_adaptive=True,
    )

    await manager.start()

    print("=== Sleep Cycle Manager Demonstration ===\n")

    # Register callbacks
    async def on_stage_change(old_stage, new_stage):
        print(f"Stage: {old_stage.value} -> {new_stage.value}")
        print(f"  Delta power: {manager.delta_power:.2f}")
        print(f"  Theta power: {manager.theta_power:.2f}")

    async def on_cycle_complete(cycle):
        print(f"\nCycle {cycle.cycle_number} completed!")
        print(f"  Duration: {cycle.calculate_duration()} / 60:.1f} minutes")
        print(f"  Consolidation score: {cycle.consolidation_score:.2f}")

    manager.register_stage_callback(on_stage_change)
    manager.register_cycle_callback(on_cycle_complete)

    # Initiate sleep
    print("--- Initiating Sleep ---")
    cycle_id = await manager.initiate_sleep()
    print(f"Started cycle: {cycle_id[:8]}...")

    # Let it run for a bit
    await asyncio.sleep(30)

    # Show metrics
    print("\n--- Sleep Metrics ---")
    metrics = manager.get_metrics()
    for key, value in sorted(metrics.items()):
        if isinstance(value, float):
            print(f"{key}: {value:.3f}")
        else:
            print(f"{key}: {value}")

    await manager.stop()


if __name__ == "__main__":
    asyncio.run(demonstrate_sleep_cycle_manager())
