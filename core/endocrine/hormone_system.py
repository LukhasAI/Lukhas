"""
LUKHAS Endocrine System
Simulates hormonal signaling for system-wide behavioral modulation
"""
import asyncio
import contextlib
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional

from core.events.contracts import SystemStressLevelChanged

logger = logging.getLogger(__name__)


class HormoneType(Enum):
    """Types of hormones in the system"""

    CORTISOL = "cortisol"  # Stress response
    DOPAMINE = "dopamine"  # Reward and motivation
    SEROTONIN = "serotonin"  # Mood stability
    OXYTOCIN = "oxytocin"  # Social bonding
    ADRENALINE = "adrenaline"  # Fight or flight
    MELATONIN = "melatonin"  # Rest cycles
    GABA = "gaba"  # Calming/inhibition
    ENDORPHIN = "endorphin"  # Natural pain relief/pleasure


@dataclass
class HormoneLevel:
    """Current level of a hormone"""

    hormone_type: HormoneType
    level: float = 0.5  # 0.0 to 1.0
    baseline: float = 0.5
    production_rate: float = 0.1
    decay_rate: float = 0.05
    last_update: datetime = field(default_factory=datetime.now)

    def update(self, delta_time: float) -> float:
        """Update hormone level based on time passed"""
        # Natural decay towards baseline
        decay = (self.level - self.baseline) * self.decay_rate * delta_time
        self.level = max(0.0, min(1.0, self.level - decay))
        self.last_update = datetime.now(timezone.utc)
        return self.level


@dataclass
class HormoneInteraction:
    """Defines how hormones interact with each other"""

    source: HormoneType
    target: HormoneType
    effect: float  # Positive = increases, Negative = decreases
    threshold: float = 0.3  # Source level needed for effect


class EndocrineSystem:
    """Central endocrine system managing all hormones"""

    def __init__(self):
        self.hormones: dict[HormoneType, HormoneLevel] = {}
        self.interactions: list[HormoneInteraction] = []
        self.receptors: dict[str, list[Callable]] = {}  # Module hormone receptors
        self.active = False
        self.update_task: Optional[asyncio.Task] = None

        # Initialize hormones
        self._initialize_hormones()
        self._initialize_interactions()

        # Track effects
        self.active_effects: dict[str, Any] = {}
        self.effect_history: list[dict[str, Any]] = []

        logger.info("Endocrine system initialized")

    def _initialize_hormones(self):
        """Initialize all hormone levels"""
        # Primary hormones
        self.hormones[HormoneType.CORTISOL] = HormoneLevel(
            hormone_type=HormoneType.CORTISOL,
            baseline=0.3,
            production_rate=0.2,
            decay_rate=0.08,
        )

        self.hormones[HormoneType.DOPAMINE] = HormoneLevel(
            hormone_type=HormoneType.DOPAMINE,
            baseline=0.5,
            production_rate=0.15,
            decay_rate=0.1,
        )

        self.hormones[HormoneType.SEROTONIN] = HormoneLevel(
            hormone_type=HormoneType.SEROTONIN,
            baseline=0.6,
            production_rate=0.1,
            decay_rate=0.05,
        )

        self.hormones[HormoneType.OXYTOCIN] = HormoneLevel(
            hormone_type=HormoneType.OXYTOCIN,
            baseline=0.4,
            production_rate=0.12,
            decay_rate=0.06,
        )

        # Secondary hormones
        self.hormones[HormoneType.ADRENALINE] = HormoneLevel(
            hormone_type=HormoneType.ADRENALINE,
            baseline=0.2,
            production_rate=0.3,
            decay_rate=0.15,
        )

        self.hormones[HormoneType.MELATONIN] = HormoneLevel(
            hormone_type=HormoneType.MELATONIN,
            baseline=0.3,
            production_rate=0.05,
            decay_rate=0.03,
        )

        self.hormones[HormoneType.GABA] = HormoneLevel(
            hormone_type=HormoneType.GABA,
            baseline=0.5,
            production_rate=0.08,
            decay_rate=0.04,
        )

        self.hormones[HormoneType.ENDORPHIN] = HormoneLevel(
            hormone_type=HormoneType.ENDORPHIN,
            baseline=0.3,
            production_rate=0.1,
            decay_rate=0.07,
        )

    def _initialize_interactions(self):
        """Define how hormones interact"""
        self.interactions = [
            # Stress hormones suppress mood hormones
            HormoneInteraction(HormoneType.CORTISOL, HormoneType.SEROTONIN, -0.3, 0.6),
            HormoneInteraction(HormoneType.CORTISOL, HormoneType.DOPAMINE, -0.2, 0.7),
            # Adrenaline boosts cortisol
            HormoneInteraction(HormoneType.ADRENALINE, HormoneType.CORTISOL, 0.4, 0.5),
            # Serotonin promotes oxytocin
            HormoneInteraction(HormoneType.SEROTONIN, HormoneType.OXYTOCIN, 0.2, 0.6),
            # Oxytocin reduces stress
            HormoneInteraction(HormoneType.OXYTOCIN, HormoneType.CORTISOL, -0.25, 0.5),
            # GABA calms everything
            HormoneInteraction(HormoneType.GABA, HormoneType.CORTISOL, -0.2, 0.6),
            HormoneInteraction(HormoneType.GABA, HormoneType.ADRENALINE, -0.3, 0.5),
            # Endorphins boost mood
            HormoneInteraction(HormoneType.ENDORPHIN, HormoneType.DOPAMINE, 0.3, 0.4),
            HormoneInteraction(HormoneType.ENDORPHIN, HormoneType.SEROTONIN, 0.2, 0.4),
            # Melatonin promotes GABA
            HormoneInteraction(HormoneType.MELATONIN, HormoneType.GABA, 0.2, 0.5),
        ]

    async def start(self):
        """Start the endocrine system update loop"""
        if self.active:
            return

        self.active = True
        self.update_task = asyncio.create_task(self._update_loop())
        logger.info("Endocrine system started")

    async def stop(self):
        """Stop the endocrine system"""
        self.active = False
        if self.update_task:
            self.update_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.update_task
        logger.info("Endocrine system stopped")

    async def _update_loop(self):
        """Main update loop for hormone levels"""
        last_update = datetime.now(timezone.utc)

        while self.active:
            try:
                current_time = datetime.now(timezone.utc)
                delta_time = (current_time - last_update).total_seconds()

                # Update all hormone levels
                for hormone in self.hormones.values():
                    hormone.update(delta_time)

                # Apply interactions
                self._apply_interactions()

                # Calculate and apply effects
                effects = self._calculate_effects()
                await self._apply_effects(effects)

                # Log significant changes
                self._log_significant_changes()

                last_update = current_time
                await asyncio.sleep(1.0)  # Update every second

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in endocrine update loop: {e}")

    def _apply_interactions(self):
        """Apply hormone interactions"""
        for interaction in self.interactions:
            source_level = self.hormones[interaction.source].level

            if source_level >= interaction.threshold:
                # Calculate effect strength
                effect_strength = (source_level - interaction.threshold) * interaction.effect

                # Apply to target hormone
                target = self.hormones[interaction.target]
                new_level = target.level + effect_strength * 0.01  # Small increments
                target.level = max(0.0, min(1.0, new_level))

    def trigger_stress_response(self, intensity: float = 0.5):
        """Trigger a stress response"""
        # Boost stress hormones
        self._boost_hormone(HormoneType.CORTISOL, intensity * 0.4)
        self._boost_hormone(HormoneType.ADRENALINE, intensity * 0.3)

        # Log the trigger
        self.effect_history.append(
            {
                "type": "stress_response",
                "intensity": intensity,
                "timestamp": datetime.now(timezone.utc),
                "hormones_affected": ["cortisol", "adrenaline"],
            }
        )

        logger.info(f"Stress response triggered: intensity={intensity}")

    def trigger_reward_response(self, intensity: float = 0.5):
        """Trigger a reward response"""
        # Boost reward hormones
        self._boost_hormone(HormoneType.DOPAMINE, intensity * 0.5)
        self._boost_hormone(HormoneType.ENDORPHIN, intensity * 0.3)

        # Slight serotonin boost
        self._boost_hormone(HormoneType.SEROTONIN, intensity * 0.2)

        self.effect_history.append(
            {
                "type": "reward_response",
                "intensity": intensity,
                "timestamp": datetime.now(timezone.utc),
                "hormones_affected": ["dopamine", "endorphin", "serotonin"],
            }
        )

        logger.info(f"Reward response triggered: intensity={intensity}")

    def trigger_social_bonding(self, intensity: float = 0.5):
        """Trigger social bonding response"""
        # Boost bonding hormones
        self._boost_hormone(HormoneType.OXYTOCIN, intensity * 0.6)
        self._boost_hormone(HormoneType.SEROTONIN, intensity * 0.3)

        # Reduce stress
        self._reduce_hormone(HormoneType.CORTISOL, intensity * 0.2)

        self.effect_history.append(
            {
                "type": "social_bonding",
                "intensity": intensity,
                "timestamp": datetime.now(timezone.utc),
                "hormones_affected": ["oxytocin", "serotonin", "cortisol"],
            }
        )

        logger.info(f"Social bonding response triggered: intensity={intensity}")

    def trigger_rest_cycle(self, intensity: float = 0.5):
        """Trigger rest/recovery cycle"""
        # Boost rest hormones
        self._boost_hormone(HormoneType.MELATONIN, intensity * 0.7)
        self._boost_hormone(HormoneType.GABA, intensity * 0.5)

        # Reduce activity hormones
        self._reduce_hormone(HormoneType.ADRENALINE, intensity * 0.4)
        self._reduce_hormone(HormoneType.CORTISOL, intensity * 0.3)

        self.effect_history.append(
            {
                "type": "rest_cycle",
                "intensity": intensity,
                "timestamp": datetime.now(timezone.utc),
                "hormones_affected": [
                    "melatonin",
                    "gaba",
                    "adrenaline",
                    "cortisol",
                ],
            }
        )

        logger.info(f"Rest cycle triggered: intensity={intensity}")

    def _boost_hormone(self, hormone_type: HormoneType, amount: float):
        """Boost a hormone level"""
        hormone = self.hormones[hormone_type]
        hormone.level = min(1.0, hormone.level + amount)

    def _reduce_hormone(self, hormone_type: HormoneType, amount: float):
        """Reduce a hormone level"""
        hormone = self.hormones[hormone_type]
        hormone.level = max(0.0, hormone.level - amount)

    def _calculate_effects(self) -> dict[str, Any]:
        """Calculate current hormone effects on system behavior"""
        effects = {}

        # Stress effects
        cortisol = self.hormones[HormoneType.CORTISOL].level
        adrenaline = self.hormones[HormoneType.ADRENALINE].level
        stress_level = cortisol * 0.7 + adrenaline * 0.3

        effects["stress_level"] = stress_level
        effects["alertness"] = min(1.0, stress_level * 1.5)
        effects["resource_conservation"] = stress_level > 0.6

        # Mood effects
        dopamine = self.hormones[HormoneType.DOPAMINE].level
        serotonin = self.hormones[HormoneType.SEROTONIN].level
        endorphin = self.hormones[HormoneType.ENDORPHIN].level

        effects["mood_valence"] = dopamine * 0.4 + serotonin * 0.4 + endorphin * 0.2
        effects["motivation"] = dopamine
        effects["emotional_stability"] = serotonin

        # Social effects
        oxytocin = self.hormones[HormoneType.OXYTOCIN].level
        effects["social_engagement"] = oxytocin
        effects["trust_level"] = oxytocin * 0.8
        effects["empathy"] = oxytocin * serotonin

        # Rest effects
        melatonin = self.hormones[HormoneType.MELATONIN].level
        gaba = self.hormones[HormoneType.GABA].level

        effects["rest_need"] = melatonin
        effects["calmness"] = gaba
        effects["processing_speed"] = 1.0 - (melatonin * 0.3 + gaba * 0.2)

        # Neuroplasticity effects
        effects["neuroplasticity"] = self._calculate_neuroplasticity()

        return effects

    def _calculate_neuroplasticity(self) -> float:
        """Calculate current neuroplasticity based on hormone levels"""
        # High stress and low mood reduce neuroplasticity
        # Balanced hormones increase it

        cortisol = self.hormones[HormoneType.CORTISOL].level
        dopamine = self.hormones[HormoneType.DOPAMINE].level
        serotonin = self.hormones[HormoneType.SEROTONIN].level

        # Stress inhibits neuroplasticity
        stress_factor = 1.0 - (cortisol * 0.5)

        # Positive mood enhances it
        mood_factor = dopamine * 0.3 + serotonin * 0.3

        # Sleep/rest is crucial for neuroplasticity
        rest_factor = self.hormones[HormoneType.MELATONIN].level * 0.4

        neuroplasticity = stress_factor * 0.4 + mood_factor * 0.4 + rest_factor * 0.2
        return max(0.1, min(1.0, neuroplasticity))

    async def _apply_effects(self, effects: dict[str, Any]):
        """Apply hormone effects to system behavior"""
        self.active_effects = effects

        # Notify registered receptors
        for module_name, receptors in self.receptors.items():
            for receptor in receptors:
                try:
                    await receptor(effects)
                except Exception as e:
                    logger.error(f"Error in hormone receptor {module_name}: {e}")

        # Check for significant state changes
        if effects["stress_level"] > 0.8:
            await self._emit_stress_event(effects["stress_level"])

    async def _emit_stress_event(self, stress_level: float):
        """Emit a stress level change event"""
        # This would integrate with the event system
        SystemStressLevelChanged(
            source_module="endocrine",
            previous_level=self.active_effects.get("stress_level", 0.5),
            current_level=stress_level,
            stress_source="hormonal",
            hormone_levels={hormone.value: level.level for hormone, level in self.hormones.items()},
        )
        # Event would be published through event bus

    def _log_significant_changes(self):
        """Log significant hormone changes"""
        for hormone_type, hormone in self.hormones.items():
            # Check for significant deviations from baseline
            deviation = abs(hormone.level - hormone.baseline)
            if deviation > 0.3:
                logger.debug(
                    f"Significant {hormone_type.value} deviation: "
                    f"level={hormone.level:.2f}, baseline={hormone.baseline:.2f}"
                )

    def register_receptor(self, module_name: str, receptor: Callable):
        """Register a hormone receptor for a module"""
        if module_name not in self.receptors:
            self.receptors[module_name] = []
        self.receptors[module_name].append(receptor)
        logger.info(f"Registered hormone receptor for {module_name}")

    def get_hormone_levels(self) -> dict[str, float]:
        """Get current hormone levels"""
        return {hormone.value: level.level for hormone, level in self.hormones.items()}

    def get_active_effects(self) -> dict[str, Any]:
        """Get currently active effects"""
        return self.active_effects.copy()

    def get_hormone_profile(self) -> dict[str, Any]:
        """Get comprehensive hormone profile"""
        profile = {
            "levels": self.get_hormone_levels(),
            "effects": self.get_active_effects(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dominant_state": self._determine_dominant_state(),
        }

        # Add human-readable summary
        profile["summary"] = self._generate_summary()

        return profile

    def _determine_dominant_state(self) -> str:
        """Determine the dominant hormonal state"""
        self.get_hormone_levels()

        # Find highest hormone above baseline
        max_hormone = None
        max_deviation = 0

        for hormone_type, hormone in self.hormones.items():
            deviation = hormone.level - hormone.baseline
            if deviation > max_deviation:
                max_deviation = deviation
                max_hormone = hormone_type

        if max_hormone:
            state_map = {
                HormoneType.CORTISOL: "stressed",
                HormoneType.DOPAMINE: "motivated",
                HormoneType.SEROTONIN: "content",
                HormoneType.OXYTOCIN: "social",
                HormoneType.ADRENALINE: "alert",
                HormoneType.MELATONIN: "resting",
                HormoneType.GABA: "calm",
                HormoneType.ENDORPHIN: "euphoric",
            }
            return state_map.get(max_hormone, "balanced")

        return "balanced"

    def _generate_summary(self) -> str:
        """Generate human-readable hormone summary"""
        state = self._determine_dominant_state()
        effects = self.get_active_effects()

        summary = f"System is in a {state} state. "

        if effects.get("stress_level", 0) > 0.7:
            summary += "High stress detected - system in adaptive mode. "
        elif effects.get("mood_valence", 0.5) > 0.7:
            summary += "Positive mood state - enhanced learning capacity. "
        elif effects.get("rest_need", 0) > 0.6:
            summary += "Rest cycle recommended for optimal performance. "

        neuroplasticity = effects.get("neuroplasticity", 0.5)
        if neuroplasticity > 0.7:
            summary += "High neuroplasticity - excellent conditions for learning and adaptation."
        elif neuroplasticity < 0.3:
            summary += "Low neuroplasticity - system reorganization may be impaired."

        return summary


# Global endocrine system instance
_endocrine_system: Optional[EndocrineSystem] = None


def get_endocrine_system() -> EndocrineSystem:
    """Get the global endocrine system instance"""
    global _endocrine_system
    if _endocrine_system is None:
        _endocrine_system = EndocrineSystem()
    return _endocrine_system


# Convenience functions


async def trigger_stress(intensity: float = 0.5):
    """Trigger a stress response in the system"""
    system = get_endocrine_system()
    system.trigger_stress_response(intensity)


async def trigger_reward(intensity: float = 0.5):
    """Trigger a reward response in the system"""
    system = get_endocrine_system()
    system.trigger_reward_response(intensity)


def get_neuroplasticity() -> float:
    """Get current neuroplasticity level"""
    system = get_endocrine_system()
    return system._calculate_neuroplasticity()


# Neuroplastic tags
# ΛTAG:core
# ΛTAG:hormone
# ΛTAG:endocrine
# ΛTAG:neuroplastic
