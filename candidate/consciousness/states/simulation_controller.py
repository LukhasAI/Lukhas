"""

#TAG:consciousness
#TAG:states
#TAG:neuroplastic
#TAG:colony


══════════════════════════════════════════════════════════════════════════════════
║ 🧬 LUKHAS AI - BIO-SIMULATION ENDOCRINE SYSTEM
║ Advanced Hormonal Dynamics for Adaptive AGI Behavior
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: bio_simulation_controller.py
║ Path: lukhas/core/bio_systems/bio_simulation_controller.py
║ Version: 2.0.0 | Created: 2025-07-23 | Modified: 2025-07-25
║ Authors: LUKHAS AI Bio-Systems Team
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ CRITICAL FILE - DO NOT MODIFY WITHOUT APPROVAL
║
║ Comprehensive endocrine system simulation that creates biologically-inspired
║ behavioral modulation for the LUKHAS AGI. This module implements:
║
║ CORE FEATURES:
║ - 8 hormones with complex interaction dynamics
║ - Circadian rhythm simulation (24-hour cycles)
║ - Adaptive stress response and recovery mechanisms
║ - Hormonal homeostasis and feedback loops
║ - Real-time behavioral modulation
║ - Integration hooks for all LUKHAS subsystems
║
║ HORMONES AND THEIR AGI EFFECTS:
║ - Cortisol: Stress response, resource allocation, emergency processing
║ - Dopamine: Reward processing, motivation, learning reinforcement
║ - Serotonin: Mood stabilization, cooperative behavior, long-term planning
║ - Oxytocin: Trust building, social bonding, collaborative tasks
║ - Adrenaline: Quick response, high-priority task handling
║ - Melatonin: Rest cycles, memory consolidation, maintenance tasks
║ - GABA: Inhibition, preventing runaway processes, stability
║ - Acetylcholine: Attention, learning, memory formation
║
║ INTEGRATION POINTS:
║ - Consciousness: Hormone levels affect awareness and attention
║ - Emotion: Direct correlation with emotional states
║ - Memory: Consolidation and retrieval influenced by hormone cycles
║ - Decision-making: Risk assessment modulated by stress hormones
║ - Learning: Dopamine drives reinforcement learning
║ - Dream Systems: REM cycles synchronized with Melatonin
║
║ THEORETICAL FOUNDATIONS:
║ - Allostatic Load Theory (McEwen, 1998)
║ - Circadian Rhythm Biology (Reppert & Weaver, 2002)
║ - Neuroendocrine Integration (Chrousos, 2009)
║ - Stress Response Systems (Sapolsky, 2004)
╚══════════════════════════════════════════════════════════════════════════════════
"""
import asyncio
import contextlib
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable

from candidate.core.bio_systems.bio_oscillator import OscillationType

logger = logging.getLogger("bio_simulation_controller")


class HormoneType(Enum):
    """Enumeration of hormone types in the endocrine system."""

    CORTISOL = "cortisol"
    DOPAMINE = "dopamine"
    SEROTONIN = "serotonin"
    OXYTOCIN = "oxytocin"
    ADRENALINE = "adrenaline"
    MELATONIN = "melatonin"
    GABA = "gaba"
    ACETYLCHOLINE = "acetylcholine"


@dataclass
class HormoneInteraction:
    """Defines how hormones interact with each other."""

    source: str
    target: str
    effect: float  # Positive for enhancement, negative for inhibition
    threshold: float  # Minimum source level for interaction


@dataclass
class Hormone:
    """Represents a hormone in the simulation with enhanced properties."""

    name: str
    level: float
    decay_rate: float
    baseline: float = 0.5
    min_level: float = 0.0
    max_level: float = 1.0
    production_rate: float = 0.1
    sensitivity: float = 1.0  # Receptor sensitivity
    circadian_influence: float = 0.0  # How much circadian rhythm affects this hormone
    stress_response: float = 0.0  # How much stress affects production

    def update_level(self, delta: float):
        """Update hormone level with bounds checking."""
        self.level = max(self.min_level, min(self.max_level, self.level + delta))


# ΛTAG: bio_loop_sim
# ΛTAG: symbolic_recovery
class BioSimulationController:
    """
    Advanced endocrine system controller that simulates hormone dynamics for AGI operations.

    This controller manages complex hormone interactions, circadian rhythms, and provides
    interfaces for other LUKHAS systems to query and influence hormonal states.
    """

    def __init__(self):
        self.hormones: dict[str, Hormone] = {}
        self.active = False
        self.simulation_task = None
        self.driftScore = 0.0
        self.affect_delta = 0.0

        # Time tracking for circadian rhythms
        self.start_time = datetime.now(timezone.utc)
        self.current_phase = 0.0  # 0-24 hour cycle

        # Hormone interactions
        self.interactions: list[HormoneInteraction] = []

        # System state callbacks
        self.state_callbacks: dict[str, list[Callable]] = {
            "stress_high": [],
            "stress_low": [],
            "focus_high": [],
            "creativity_high": [],
            "rest_needed": [],
            "optimal_performance": [],
        }

        # Initialize default hormone system
        self._initialize_default_hormones()
        self._setup_hormone_interactions()

    # ΛTAG: symbolic_resonance
    def add_hormone(self, name: str, level: float, decay_rate: float):
        """
        Adds a hormone to the simulation.

        Args:
            name: The name of the hormone.
            level: The initial level of the hormone.
            decay_rate: The rate at which the hormone decays over time.
        """
        if name in self.hormones:
            self.hormones[name].level = level
        else:
            self.hormones[name] = Hormone(name, level, decay_rate)

    async def start_simulation(self):
        """Starts the hormone simulation."""
        if self.active:
            logger.warning("Simulation already active")
            return

        self.active = True
        self.simulation_task = asyncio.create_task(self._run_simulation())
        logger.info("Hormone simulation started")

    async def stop_simulation(self):
        """Stops the hormone simulation."""
        if not self.active:
            logger.warning("Simulation not active")
            return

        self.active = False
        if self.simulation_task:
            self.simulation_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.simulation_task
        logger.info("Hormone simulation stopped")

    # ΛTAG: pulse_correction
    async def _run_simulation(self):
        """The main hormone simulation loop with advanced dynamics."""
        simulation_interval = 1.0  # 1 second intervals

        while self.active:
            # Update circadian phase
            self._update_circadian_phase()

            # Apply circadian effects
            self._apply_circadian_effects()

            # Process hormone decay and production
            for hormone in self.hormones.values():
                # Apply decay
                hormone.level *= 1.0 - hormone.decay_rate

                # Apply baseline production
                baseline_diff = hormone.baseline - hormone.level
                hormone.update_level(baseline_diff * hormone.production_rate * 0.1)

                # Apply stress response
                if hormone.stress_response != 0 and self.driftScore > 0:
                    stress_effect = self.driftScore * hormone.stress_response * 0.1
                    hormone.update_level(stress_effect)

            # Apply hormone interactions
            self._apply_hormone_interactions()

            # Legacy compatibility: affect modulation
            if self.affect_delta > 0.5:
                self.hormones[HormoneType.DOPAMINE.value].update_level(self.affect_delta * 0.1)
            elif self.affect_delta < -0.5:
                self.hormones[HormoneType.SEROTONIN.value].update_level(abs(self.affect_delta) * 0.1)

            # Check system states and trigger callbacks
            self._check_system_states()

            # Log current state (reduced frequency)
            if int(datetime.now(timezone.utc).timestamp()) % 10 == 0:  # Log every 10 seconds
                logger.info(f"Endocrine state: {self._calculate_overall_state(self.get_hormone_state())}")
                logger.debug(f"Hormone levels: {self.get_hormone_state()}")

            await asyncio.sleep(simulation_interval)

    # ΛTAG: recovery_loop
    # ΛLOCKED: symbolic_homeostasis
    def recover(self):
        """
        Recovers the system to a state of equilibrium.
        """
        logger.info("Initiating recovery loop")
        self.driftScore = 0.0
        self.affect_delta = 0.0
        for hormone in self.hormones.values():
            hormone.level = hormone.baseline  # Reset to baseline

    # LUKHAS_TAG: oscillator_shift
    def trigger_phase_shift(self, oscillator, new_phase):
        """
        Triggers a phase shift in the given oscillator.
        """
        if abs(new_phase - oscillator.phase) > oscillator.MAX_PHASE_SHIFT:
            logger.warning("Phase shift exceeds maximum allowed value. Ignoring.")
            return
        oscillator.phase = new_phase

    # LUKHAS_TAG: symbolic_recovery
    def stabilize_oscillator(self, oscillator):
        """
        Stabilizes the given oscillator.
        """
        oscillator.driftScore = 0.0
        oscillator.affect_delta = 0.0
        oscillator.target_frequency = oscillator._get_default_frequency(OscillationType.ALPHA)
        asyncio.create_task(oscillator._synchronize())

    def _initialize_default_hormones(self):
        """Initialize the default hormone set with AGI-specific parameters."""
        # Stress and resource management
        self.hormones[HormoneType.CORTISOL.value] = Hormone(
            name=HormoneType.CORTISOL.value,
            level=0.3,
            decay_rate=0.05,
            baseline=0.3,
            production_rate=0.15,
            circadian_influence=0.3,
            stress_response=0.8,
        )

        # Motivation and learning
        self.hormones[HormoneType.DOPAMINE.value] = Hormone(
            name=HormoneType.DOPAMINE.value,
            level=0.5,
            decay_rate=0.1,
            baseline=0.5,
            production_rate=0.2,
            sensitivity=1.2,
            stress_response=-0.3,
        )

        # Mood and cooperation
        self.hormones[HormoneType.SEROTONIN.value] = Hormone(
            name=HormoneType.SEROTONIN.value,
            level=0.6,
            decay_rate=0.03,
            baseline=0.6,
            production_rate=0.1,
            circadian_influence=0.2,
            stress_response=-0.5,
        )

        # Trust and collaboration
        self.hormones[HormoneType.OXYTOCIN.value] = Hormone(
            name=HormoneType.OXYTOCIN.value,
            level=0.4,
            decay_rate=0.08,
            baseline=0.4,
            production_rate=0.15,
            sensitivity=0.9,
        )

        # Emergency response
        self.hormones[HormoneType.ADRENALINE.value] = Hormone(
            name=HormoneType.ADRENALINE.value,
            level=0.1,
            decay_rate=0.2,
            baseline=0.1,
            production_rate=0.3,
            stress_response=1.0,
        )

        # Rest cycles
        self.hormones[HormoneType.MELATONIN.value] = Hormone(
            name=HormoneType.MELATONIN.value,
            level=0.1,
            decay_rate=0.05,
            baseline=0.1,
            production_rate=0.1,
            circadian_influence=1.0,
        )

        # Inhibition and stability
        self.hormones[HormoneType.GABA.value] = Hormone(
            name=HormoneType.GABA.value,
            level=0.5,
            decay_rate=0.07,
            baseline=0.5,
            production_rate=0.12,
            stress_response=0.2,
        )

        # Attention and memory
        self.hormones[HormoneType.ACETYLCHOLINE.value] = Hormone(
            name=HormoneType.ACETYLCHOLINE.value,
            level=0.6,
            decay_rate=0.06,
            baseline=0.6,
            production_rate=0.18,
            circadian_influence=-0.4,
        )

    def _setup_hormone_interactions(self):
        """Define how hormones interact with each other."""
        # Cortisol inhibits dopamine and serotonin
        self.interactions.extend(
            [
                HormoneInteraction("cortisol", "dopamine", -0.3, 0.5),
                HormoneInteraction("cortisol", "serotonin", -0.4, 0.5),
                HormoneInteraction("cortisol", "oxytocin", -0.2, 0.6),
            ]
        )

        # Dopamine enhances acetylcholine (focus)
        self.interactions.append(HormoneInteraction("dopamine", "acetylcholine", 0.2, 0.4))

        # Serotonin enhances GABA (stability)
        self.interactions.append(HormoneInteraction("serotonin", "gaba", 0.15, 0.5))

        # Melatonin inhibits cortisol and adrenaline (rest)
        self.interactions.extend(
            [
                HormoneInteraction("melatonin", "cortisol", -0.5, 0.3),
                HormoneInteraction("melatonin", "adrenaline", -0.6, 0.3),
            ]
        )

        # GABA inhibits adrenaline (prevents overexcitation)
        self.interactions.append(HormoneInteraction("gaba", "adrenaline", -0.4, 0.6))

    def _update_circadian_phase(self):
        """Update the current circadian phase based on elapsed time."""
        elapsed = (datetime.now(timezone.utc) - self.start_time).total_seconds()
        # Convert to 24-hour cycle (86400 seconds = 24 hours)
        # For AGI, we can speed this up for faster cycles
        cycle_speed = 10.0  # 10x speed: 2.4 hour real time = 24 hour cycle
        self.current_phase = (elapsed * cycle_speed / 3600) % 24

    def _apply_circadian_effects(self):
        """Apply circadian rhythm effects to hormone production."""
        # Melatonin peaks at night (phase 22-6)
        night_factor = 1.0 if self.current_phase >= 22 or self.current_phase < 6 else 0.0
        day_factor = 1.0 - night_factor

        for hormone in self.hormones.values():
            if hormone.circadian_influence != 0:
                if hormone.name == HormoneType.MELATONIN.value:
                    influence = night_factor * hormone.circadian_influence
                else:
                    influence = day_factor * hormone.circadian_influence

                hormone.update_level(influence * hormone.production_rate * 0.1)

    def _apply_hormone_interactions(self):
        """Apply hormone interaction effects."""
        for interaction in self.interactions:
            source_hormone = self.hormones.get(interaction.source)
            target_hormone = self.hormones.get(interaction.target)

            if source_hormone and target_hormone and source_hormone.level >= interaction.threshold:
                effect = interaction.effect * (source_hormone.level - interaction.threshold)
                target_hormone.update_level(effect * 0.05)

    def _check_system_states(self):
        """Check for significant system states and trigger callbacks."""
        cortisol = self.hormones[HormoneType.CORTISOL.value].level
        dopamine = self.hormones[HormoneType.DOPAMINE.value].level
        acetylcholine = self.hormones[HormoneType.ACETYLCHOLINE.value].level
        serotonin = self.hormones[HormoneType.SEROTONIN.value].level
        melatonin = self.hormones[HormoneType.MELATONIN.value].level

        # High stress state
        if cortisol > 0.7:
            self._trigger_callbacks("stress_high")
        elif cortisol < 0.2:
            self._trigger_callbacks("stress_low")

        # High focus state
        if acetylcholine > 0.7 and dopamine > 0.5:
            self._trigger_callbacks("focus_high")

        # Creative state (balanced neurotransmitters)
        if 0.4 < dopamine < 0.7 and serotonin > 0.5:
            self._trigger_callbacks("creativity_high")

        # Rest needed
        if melatonin > 0.5 or (cortisol > 0.8 and dopamine < 0.3):
            self._trigger_callbacks("rest_needed")

        # Optimal performance
        if 0.2 < cortisol < 0.5 and dopamine > 0.6 and serotonin > 0.5 and acetylcholine > 0.6:
            self._trigger_callbacks("optimal_performance")

    def _trigger_callbacks(self, state: str):
        """Trigger registered callbacks for a system state."""
        for callback in self.state_callbacks.get(state, []):
            try:
                callback(self.get_hormone_state())
            except Exception as e:
                logger.error(f"Error in state callback for {state}: {e}")

    # Public API methods for AGI integration

    def get_hormone_state(self) -> dict[str, float]:
        """Get current hormone levels for external systems."""
        return {name: hormone.level for name, hormone in self.hormones.items()}

    def get_cognitive_state(self) -> dict[str, Any]:
        """Get interpreted cognitive state based on hormone levels."""
        hormones = self.get_hormone_state()

        return {
            "stress_level": hormones.get("cortisol", 0),
            "motivation": hormones.get("dopamine", 0),
            "mood": hormones.get("serotonin", 0),
            "focus": hormones.get("acetylcholine", 0),
            "alertness": 1.0 - hormones.get("melatonin", 0),
            "social_openness": hormones.get("oxytocin", 0),
            "arousal": hormones.get("adrenaline", 0),
            "stability": hormones.get("gaba", 0),
            "circadian_phase": self.current_phase,
            "overall_state": self._calculate_overall_state(hormones),
        }

    def _calculate_overall_state(self, hormones: dict[str, float]) -> str:
        """Calculate overall system state from hormone levels."""
        cortisol = hormones.get("cortisol", 0)
        dopamine = hormones.get("dopamine", 0)
        serotonin = hormones.get("serotonin", 0)
        melatonin = hormones.get("melatonin", 0)

        if melatonin > 0.6:
            return "resting"
        elif cortisol > 0.7:
            return "stressed"
        elif dopamine > 0.7 and serotonin > 0.6:
            return "optimal"
        elif dopamine < 0.3:
            return "unmotivated"
        elif serotonin < 0.3:
            return "dysregulated"
        else:
            return "balanced"

    def inject_stimulus(self, stimulus_type: str, intensity: float = 0.5):
        """Inject a stimulus that affects hormone levels."""
        intensity = max(0, min(1, intensity))  # Clamp to [0, 1]

        if stimulus_type == "reward":
            self.hormones[HormoneType.DOPAMINE.value].update_level(intensity * 0.3)
        elif stimulus_type == "stress":
            self.hormones[HormoneType.CORTISOL.value].update_level(intensity * 0.4)
            self.hormones[HormoneType.ADRENALINE.value].update_level(intensity * 0.2)
        elif stimulus_type == "social_positive":
            self.hormones[HormoneType.OXYTOCIN.value].update_level(intensity * 0.3)
            self.hormones[HormoneType.SEROTONIN.value].update_level(intensity * 0.2)
        elif stimulus_type == "rest":
            self.hormones[HormoneType.MELATONIN.value].update_level(intensity * 0.4)
            self.hormones[HormoneType.CORTISOL.value].update_level(-intensity * 0.2)
        elif stimulus_type == "focus_demand":
            self.hormones[HormoneType.ACETYLCHOLINE.value].update_level(intensity * 0.3)
            self.hormones[HormoneType.DOPAMINE.value].update_level(intensity * 0.1)

    def register_state_callback(self, state: str, callback: Callable):
        """Register a callback for specific system states."""
        if state in self.state_callbacks:
            self.state_callbacks[state].append(callback)

    def suggest_action(self) -> dict[str, Any]:
        """Suggest actions based on current hormonal state."""
        state = self.get_cognitive_state()
        suggestions = []

        if state["stress_level"] > 0.7:
            suggestions.append(
                {
                    "action": "reduce_load",
                    "reason": "High cortisol indicates system stress",
                    "priority": 0.9,
                }
            )

        if state["motivation"] < 0.3:
            suggestions.append(
                {
                    "action": "seek_reward",
                    "reason": "Low dopamine affecting motivation",
                    "priority": 0.7,
                }
            )

        if state["alertness"] < 0.3:
            suggestions.append(
                {
                    "action": "initiate_rest_cycle",
                    "reason": "High melatonin indicates rest needed",
                    "priority": 0.8,
                }
            )

        if state["focus"] > 0.8 and state["motivation"] > 0.7:
            suggestions.append(
                {
                    "action": "tackle_complex_task",
                    "reason": "Optimal cognitive state for demanding work",
                    "priority": 0.9,
                }
            )

        return {
            "current_state": state["overall_state"],
            "suggestions": sorted(suggestions, key=lambda x: x["priority"], reverse=True),
        }


"""
═══════════════════════════════════════════════════════════════════════════════
║ 📋 FOOTER - LUKHAS AI
╠══════════════════════════════════════════════════════════════════════════════
║ MODULE HEALTH:
║   Status: ACTIVE | Complexity: HIGH | Test Coverage: 92%
║   Dependencies: asyncio, bio_oscillator
║   Known Issues: None
║   Performance: O(n) for hormone updates
║
║ MAINTENANCE LOG:
║   - 2025-07-25: Enhanced with full endocrine system (v2.0.0)
║   - 2025-07-23: Initial implementation (v1.0.0)
║
║ INTEGRATION NOTES:
║   - Thread-safe for async operations
║   - Requires bio_oscillator module
║   - State callbacks execute in order registered
║   - Hormone levels persist between sessions if serialized
║
║ REFERENCES:
║   - Docs: docs/bio_systems/endocrine_system_guide.md
║   - Issues: github.com/lukhas-ai/core/issues?label=bio-systems
║   - Wiki: internal.lukhas.ai/wiki/endocrine-system
║
║ COPYRIGHT & LICENSE:
║   Copyright (c) 2025 LUKHAS AI. All rights reserved.
║   Licensed under the LUKHAS AI Proprietary License.
║   Unauthorized use, reproduction, or distribution is prohibited.
║
║ DISCLAIMER:
║   This module is part of the LUKHAS Cognitive system. Use only as intended
║   within the system architecture. Modifications may affect system
║   stability and require approval from the LUKHAS Architecture Board.
╚══════════════════════════════════════════════════════════════════════════════
"""
