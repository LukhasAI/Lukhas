#!/usr/bin/env python3
"""
Hormonal System - Digital Endocrine Regulation
Implements hormone-based regulation patterns for system homeostasis.
"""
import asyncio
import logging
from dataclasses import dataclass
from typing import Callable

logger = logging.getLogger(__name__)


@dataclass
class Hormone:
    """Digital hormone representation"""

    name: str
    current_level: float  # 0.0 - 1.0
    production_rate: float
    decay_rate: float
    target_level: float
    effects: dict[str, float]  # System -> Effect magnitude


class HormonalSystem:
    """
    Digital endocrine system for bio-inspired regulation.
    Manages hormone production, interaction, and system-wide effects.
    """

    def __init__(self):
        # Initialize digital hormones
        self.hormones = {
            "dopamine": Hormone(
                name="dopamine",
                current_level=0.5,
                production_rate=0.1,
                decay_rate=0.05,
                target_level=0.5,
                effects={"motivation": 0.8, "learning": 0.6, "pleasure": 0.9},
            ),
            "serotonin": Hormone(
                name="serotonin",
                current_level=0.5,
                production_rate=0.08,
                decay_rate=0.04,
                target_level=0.6,
                effects={"mood": 0.9, "stability": 0.7, "sleep": 0.5},
            ),
            "cortisol": Hormone(
                name="cortisol",
                current_level=0.3,
                production_rate=0.15,
                decay_rate=0.08,
                target_level=0.3,
                effects={"stress": 0.9, "alertness": 0.7, "energy": -0.3},
            ),
            "oxytocin": Hormone(
                name="oxytocin",
                current_level=0.4,
                production_rate=0.06,
                decay_rate=0.03,
                target_level=0.5,
                effects={"bonding": 0.95, "trust": 0.8, "empathy": 0.7},
            ),
            "adrenaline": Hormone(
                name="adrenaline",
                current_level=0.2,
                production_rate=0.2,
                decay_rate=0.15,
                target_level=0.2,
                effects={"reaction_time": 0.9, "strength": 0.8, "focus": 0.7},
            ),
            "melatonin": Hormone(
                name="melatonin",
                current_level=0.3,
                production_rate=0.05,
                decay_rate=0.02,
                target_level=0.3,
                effects={"sleep": 0.95, "recovery": 0.8, "circadian": 0.9},
            ),
            "growth_hormone": Hormone(
                name="growth_hormone",
                current_level=0.4,
                production_rate=0.04,
                decay_rate=0.02,
                target_level=0.4,
                effects={"growth": 0.9, "repair": 0.8, "metabolism": 0.6},
            ),
        }

        # Hormone interaction matrix (how hormones affect each other)
        self.interactions = {
            ("dopamine", "serotonin"): 0.3,  # Positive correlation
            ("cortisol", "serotonin"): -0.4,  # Negative correlation
            ("cortisol", "dopamine"): -0.2,
            ("oxytocin", "cortisol"): -0.3,
            ("melatonin", "cortisol"): -0.5,
            ("adrenaline", "cortisol"): 0.6,
        }

        # System effect callbacks
        self.effect_callbacks: dict[str, list[Callable]] = {}

        # Regulation active
        self.regulation_active = True

    async def produce_hormone(self, hormone_name: str, amount: float):
        """Trigger hormone production"""
        if hormone_name in self.hormones:
            hormone = self.hormones[hormone_name]
            hormone.current_level = min(1.0, hormone.current_level + amount)
            await self._propagate_effects(hormone_name)

    async def _propagate_effects(self, hormone_name: str):
        """Propagate hormone effects through the system"""
        hormone = self.hormones[hormone_name]

        # Apply direct effects
        for effect, magnitude in hormone.effects.items():
            if effect in self.effect_callbacks:
                for callback in self.effect_callbacks[effect]:
                    await callback(hormone.current_level * magnitude)

        # Apply hormone interactions
        for (h1, h2), correlation in self.interactions.items():
            if h1 == hormone_name and h2 in self.hormones:
                target = self.hormones[h2]
                influence = hormone.current_level * correlation * 0.1
                target.current_level = max(0, min(1.0, target.current_level + influence))

    async def regulate(self):
        """Main regulation loop"""
        while self.regulation_active:
            try:
                for hormone in self.hormones.values():
                    # Natural production
                    if hormone.current_level < hormone.target_level:
                        hormone.current_level += hormone.production_rate * 0.1

                    # Natural decay
                    hormone.current_level *= 1 - hormone.decay_rate

                    # Bounds
                    hormone.current_level = max(0, min(1.0, hormone.current_level))

                    # Propagate effects
                    await self._propagate_effects(hormone.name)

            except Exception as e:
                logger.error(f"Regulation error: {e}")

            await asyncio.sleep(1)

    def register_effect_callback(self, effect: str, callback: Callable):
        """Register callback for hormone effects"""
        if effect not in self.effect_callbacks:
            self.effect_callbacks[effect] = []
        self.effect_callbacks[effect].append(callback)

    def get_hormone_levels(self) -> dict[str, float]:
        """Get current hormone levels"""
        return {name: h.current_level for name, h in self.hormones.items()}

    def get_system_state(self) -> str:
        """Determine overall system state based on hormone profile"""
        levels = self.get_hormone_levels()

        if levels["cortisol"] > 0.7 and levels["adrenaline"] > 0.6:
            return "stressed/alert"
        elif levels["melatonin"] > 0.7:
            return "resting"
        elif levels["dopamine"] > 0.7 and levels["serotonin"] > 0.6:
            return "optimal/happy"
        elif levels["growth_hormone"] > 0.6:
            return "growing/repairing"
        else:
            return "balanced"
