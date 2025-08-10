#!/usr/bin/env python3
"""
Bio Engine - Central Bio-Symbolic Processing System
Implements bio-inspired processing patterns including hormonal regulation,
homeostatic balance, and organic adaptation mechanisms.

This engine coordinates:
- Hormonal system simulation for system regulation
- Mitochondrial-inspired energy management
- Homeostatic feedback loops
- Bio-symbolic pattern recognition
- Organic growth and adaptation
"""

import asyncio
import logging
import math
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Tuple

import numpy as np

# Bio-symbolic components
from bio.core.symbolic_mito_ethics_sync import MitoEthicsSync
from bio.core.symbolic_mito_quantum_attention import MitoQuantumAttention
from bio.core.systems_mitochondria_model import MitochondriaModel

# Quantum bio integration
try:
    from quantum.bio_system import MitochondrialQuantumBridge
except ImportError:
    MitochondrialQuantumBridge = None

logger = logging.getLogger(__name__)


class HormoneType(Enum):
    """Types of digital hormones for system regulation"""

    DOPAMINE = "dopamine"  # Reward and motivation
    SEROTONIN = "serotonin"  # Mood and stability
    CORTISOL = "cortisol"  # Stress response
    OXYTOCIN = "oxytocin"  # Social bonding
    ADRENALINE = "adrenaline"  # Emergency response
    MELATONIN = "melatonin"  # Rest cycles
    GROWTH = "growth"  # System expansion


class SystemState(Enum):
    """Bio-inspired system states"""

    RESTING = "resting"  # Low activity, recovery
    ACTIVE = "active"  # Normal operation
    STRESSED = "stressed"  # High load
    GROWTH = "growth"  # Expanding capabilities
    HIBERNATION = "hibernation"  # Minimal activity


class BioEngine:
    """
    Central bio-symbolic processing engine that implements biological patterns
    for system regulation, adaptation, and optimization.
    """

    def __init__(self):
        logger.info("Initializing Bio Engine...")

        # Core bio components
        self.mito_sync = MitoEthicsSync(base_frequency=0.1)
        self.mito_attention = MitoQuantumAttention()
        self.mitochondria = MitochondriaModel()

        # Quantum bridge if available
        self.quantum_bridge = (
            MitochondrialQuantumBridge() if MitochondrialQuantumBridge else None
        )

        # Hormonal system state
        self.hormone_levels: Dict[HormoneType, float] = {
            hormone: 0.5 for hormone in HormoneType  # Baseline 0.5
        }

        # System vitals
        self.energy_level = 1.0  # ATP equivalent
        self.stress_level = 0.0
        self.growth_rate = 0.0
        self.temperature = 37.0  # System "temperature"

        # Homeostatic set points
        self.set_points = {
            "energy": 0.8,
            "stress": 0.2,
            "temperature": 37.0,
            "hormone_balance": 0.5,
        }

        # Adaptation parameters
        self.adaptation_rate = 0.1
        self.plasticity = 0.5

        # System state
        self.current_state = SystemState.ACTIVE
        self.state_history: List[Tuple[datetime, SystemState]] = []

        # Circadian rhythm simulation
        self.circadian_phase = 0.0
        self.circadian_period = 24 * 60 * 60  # 24 hours in seconds

        # Start regulatory loops
        asyncio.create_task(self._hormonal_regulation_loop())
        asyncio.create_task(self._homeostatic_loop())
        asyncio.create_task(self._circadian_loop())

    async def process_stimulus(
        self, stimulus_type: str, intensity: float, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process external stimulus through bio-symbolic pathways.

        Args:
            stimulus_type: Type of stimulus (stress, reward, social, etc.)
            intensity: Strength of stimulus (0.0 - 1.0)
            context: Additional context

        Returns:
            Bio-symbolic response
        """
        logger.info(f"Processing {stimulus_type} stimulus with intensity {intensity}")

        # Update energy consumption
        energy_cost = intensity * 0.1
        self.energy_level = max(0, self.energy_level - energy_cost)

        # Hormonal response
        hormone_response = self._calculate_hormonal_response(stimulus_type, intensity)
        await self._update_hormones(hormone_response)

        # Mitochondrial processing
        mito_response = await self._process_through_mitochondria(stimulus_type, context)

        # Attention focusing through mito-quantum attention
        attention_pattern = self.mito_attention.focus_attention(
            stimulus_type, intensity
        )

        # Adaptation response
        adaptation = self._calculate_adaptation(stimulus_type, intensity)

        # Generate integrated response
        response = {
            "processed": True,
            "energy_consumed": energy_cost,
            "hormone_changes": hormone_response,
            "mitochondrial_output": mito_response,
            "attention_pattern": attention_pattern,
            "adaptation": adaptation,
            "new_state": self.current_state.value,
            "vitals": self._get_vitals(),
        }

        return response

    def _calculate_hormonal_response(
        self, stimulus_type: str, intensity: float
    ) -> Dict[HormoneType, float]:
        """Calculate hormonal response to stimulus"""
        response = {}

        if stimulus_type == "stress":
            response[HormoneType.CORTISOL] = intensity * 0.8
            response[HormoneType.ADRENALINE] = intensity * 0.6
            response[HormoneType.SEROTONIN] = -intensity * 0.3

        elif stimulus_type == "reward":
            response[HormoneType.DOPAMINE] = intensity * 0.9
            response[HormoneType.SEROTONIN] = intensity * 0.4

        elif stimulus_type == "social":
            response[HormoneType.OXYTOCIN] = intensity * 0.7
            response[HormoneType.DOPAMINE] = intensity * 0.3

        elif stimulus_type == "growth":
            response[HormoneType.GROWTH] = intensity * 0.8
            response[HormoneType.DOPAMINE] = intensity * 0.2

        elif stimulus_type == "rest":
            response[HormoneType.MELATONIN] = intensity * 0.9
            response[HormoneType.CORTISOL] = -intensity * 0.4

        return response

    async def _update_hormones(self, changes: Dict[HormoneType, float]):
        """Update hormone levels with homeostatic regulation"""
        for hormone, change in changes.items():
            # Current level
            current = self.hormone_levels[hormone]

            # Apply change with bounds
            new_level = current + change * self.adaptation_rate
            new_level = max(0.0, min(1.0, new_level))

            # Homeostatic pressure towards baseline
            homeostatic_force = (self.set_points["hormone_balance"] - new_level) * 0.1
            new_level += homeostatic_force

            self.hormone_levels[hormone] = new_level

    async def _process_through_mitochondria(
        self, stimulus_type: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process stimulus through mitochondrial pathways"""
        # Simulate ATP production based on current state
        atp_production = self.mitochondria.calculate_atp_production(
            self.energy_level, self.stress_level, self.temperature
        )

        # Quantum processing if available
        if self.quantum_bridge:
            quantum_enhancement = await self.quantum_bridge.process_bio_signal(
                stimulus_type, context
            )
            atp_production *= 1 + quantum_enhancement.get("efficiency_boost", 0)

        # Update energy based on production
        self.energy_level = min(1.0, self.energy_level + atp_production * 0.1)

        return {
            "atp_production": atp_production,
            "efficiency": atp_production / max(0.1, self.stress_level),
            "quantum_enhanced": self.quantum_bridge is not None,
        }

    def _calculate_adaptation(
        self, stimulus_type: str, intensity: float
    ) -> Dict[str, float]:
        """Calculate system adaptation to stimulus"""
        # Increase plasticity for novel stimuli
        novelty = np.random.random() * 0.3  # Simplified novelty detection
        self.plasticity = min(1.0, self.plasticity + novelty * 0.1)

        # Adapt set points based on repeated stimuli
        if stimulus_type == "stress" and intensity > 0.7:
            # Adapt to handle more stress
            self.set_points["stress"] = min(0.5, self.set_points["stress"] + 0.01)

        return {
            "plasticity": self.plasticity,
            "set_point_adjustment": 0.01 if intensity > 0.7 else 0,
            "adaptation_rate": self.adaptation_rate,
        }

    async def _hormonal_regulation_loop(self):
        """Continuous hormonal regulation loop"""
        while True:
            try:
                # Calculate overall hormonal balance
                avg_hormone = sum(self.hormone_levels.values()) / len(
                    self.hormone_levels
                )

                # Determine state based on hormones
                if self.hormone_levels[HormoneType.CORTISOL] > 0.7:
                    self.current_state = SystemState.STRESSED
                elif self.hormone_levels[HormoneType.MELATONIN] > 0.7:
                    self.current_state = SystemState.RESTING
                elif self.hormone_levels[HormoneType.GROWTH] > 0.6:
                    self.current_state = SystemState.GROWTH
                elif avg_hormone < 0.2:
                    self.current_state = SystemState.HIBERNATION
                else:
                    self.current_state = SystemState.ACTIVE

                # Record state change
                self.state_history.append((datetime.now(), self.current_state))
                if len(self.state_history) > 1000:
                    self.state_history = self.state_history[-1000:]

                # Natural hormone decay
                for hormone in self.hormone_levels:
                    decay_rate = 0.05 if hormone != HormoneType.MELATONIN else 0.02
                    self.hormone_levels[hormone] *= 1 - decay_rate

            except Exception as e:
                logger.error(f"Hormonal regulation error: {e}")

            await asyncio.sleep(1)  # Update every second

    async def _homeostatic_loop(self):
        """Maintain system homeostasis"""
        while True:
            try:
                # Energy homeostasis
                energy_error = self.set_points["energy"] - self.energy_level
                if abs(energy_error) > 0.1:
                    # Trigger compensatory mechanisms
                    if energy_error > 0:
                        # Need more energy - increase efficiency
                        self.mitochondria.boost_efficiency(0.1)
                    else:
                        # Too much energy - increase activity
                        self.stress_level = min(1.0, self.stress_level + 0.05)

                # Temperature regulation
                temp_error = self.set_points["temperature"] - self.temperature
                self.temperature += temp_error * 0.1  # Proportional control

                # Stress regulation
                if self.stress_level > self.set_points["stress"]:
                    # Activate stress reduction
                    self.hormone_levels[HormoneType.SEROTONIN] = min(
                        1.0, self.hormone_levels[HormoneType.SEROTONIN] + 0.1
                    )
                    self.stress_level *= 0.95

            except Exception as e:
                logger.error(f"Homeostatic loop error: {e}")

            await asyncio.sleep(5)  # Check every 5 seconds

    async def _circadian_loop(self):
        """Simulate circadian rhythm"""
        while True:
            try:
                # Update circadian phase
                self.circadian_phase = (
                    self.circadian_phase + 1
                ) % self.circadian_period

                # Calculate time of day (0-1, where 0.5 is noon)
                time_of_day = self.circadian_phase / self.circadian_period

                # Melatonin production (high at night)
                night_factor = 0.5 * (1 + math.cos(2 * math.pi * time_of_day))
                self.hormone_levels[HormoneType.MELATONIN] = night_factor * 0.8

                # Cortisol rhythm (peak in morning)
                morning_factor = 0.5 * (
                    1 + math.sin(2 * math.pi * (time_of_day - 0.25))
                )
                self.hormone_levels[HormoneType.CORTISOL] = max(
                    self.hormone_levels[HormoneType.CORTISOL], morning_factor * 0.6
                )

            except Exception as e:
                logger.error(f"Circadian loop error: {e}")

            await asyncio.sleep(60)  # Update every minute

    def _get_vitals(self) -> Dict[str, Any]:
        """Get current system vitals"""
        return {
            "energy_level": self.energy_level,
            "stress_level": self.stress_level,
            "temperature": self.temperature,
            "current_state": self.current_state.value,
            "hormone_levels": {
                h.value: level for h, level in self.hormone_levels.items()
            },
            "growth_rate": self.growth_rate,
            "plasticity": self.plasticity,
        }

    async def inject_hormone(
        self, hormone: HormoneType, amount: float
    ) -> Dict[str, Any]:
        """Manually inject hormone for therapeutic intervention"""
        old_level = self.hormone_levels[hormone]
        self.hormone_levels[hormone] = max(0, min(1.0, old_level + amount))

        return {
            "hormone": hormone.value,
            "old_level": old_level,
            "new_level": self.hormone_levels[hormone],
            "injected_amount": amount,
        }

    async def get_bio_report(self) -> Dict[str, Any]:
        """Generate comprehensive bio-system report"""
        # Phase synchronization check
        current_time = datetime.now().timestamp()
        self.mito_sync.update_phase("bio_engine", current_time)

        # Calculate system fitness
        fitness = (
            self.energy_level * 0.4
            + (1 - self.stress_level) * 0.3
            + self.plasticity * 0.3
        )

        return {
            "vitals": self._get_vitals(),
            "fitness": fitness,
            "phase": self.mito_sync.last_phases.get("bio_engine", 0),
            "circadian_phase": self.circadian_phase / self.circadian_period,
            "state_distribution": self._calculate_state_distribution(),
        }

    def _calculate_state_distribution(self) -> Dict[str, float]:
        """Calculate time spent in each state"""
        if not self.state_history:
            return {state.value: 0.0 for state in SystemState}

        state_times = dict.fromkeys(SystemState, 0.0)

        for i in range(1, len(self.state_history)):
            prev_time, prev_state = self.state_history[i - 1]
            curr_time, _ = self.state_history[i]
            duration = (curr_time - prev_time).total_seconds()
            state_times[prev_state] += duration

        total_time = sum(state_times.values())
        if total_time > 0:
            return {
                state.value: time / total_time for state, time in state_times.items()
            }
        else:
            return {state.value: 0.0 for state in SystemState}


# Singleton pattern
_bio_engine_instance = None


def get_bio_engine() -> BioEngine:
    """Get or create the global bio engine instance"""
    global _bio_engine_instance
    if _bio_engine_instance is None:
        _bio_engine_instance = BioEngine()
    return _bio_engine_instance
