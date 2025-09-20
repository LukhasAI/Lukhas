"""
LUKHAS AI Bio Utilities
Biological-inspired utility functions and helpers
Constellation Framework: ⚛️🧠🛡️

This module provides bio-inspired utilities for creativity and supervision.
"""

import logging
import math
import secrets
from typing import Any, Optional

logger = logging.getLogger(__name__)


class BioUtilities:
    """
    Collection of bio-inspired utility functions.
    Used by creativity colonies and supervision systems.
    """

    @staticmethod
    def calculate_energy_cost(complexity: float, duration: float = 1.0) -> float:
        """
        Calculate energy cost for a biological process.

        Args:
            complexity: Complexity factor (0.0 to 1.0)
            duration: Time duration of the process

        Returns:
            Energy cost value
        """
        base_cost = 10.0
        complexity_factor = 1 + (complexity * 4)  # 1x to 5x multiplier
        return base_cost * complexity_factor * duration

    @staticmethod
    def apply_homeostasis(current_value: float, target_value: float, rate: float = 0.1) -> float:
        """
        Apply homeostatic regulation to gradually move towards target value.

        Args:
            current_value: Current state value
            target_value: Target equilibrium value
            rate: Rate of adjustment (0.0 to 1.0)

        Returns:
            Adjusted value moving towards homeostasis
        """
        difference = target_value - current_value
        adjustment = difference * rate
        return current_value + adjustment

    @staticmethod
    def calculate_adaptation_rate(stress_level: float, resilience: float = 0.5) -> float:
        """
        Calculate adaptation rate based on stress and resilience.

        Args:
            stress_level: Current stress level (0.0 to 1.0)
            resilience: System resilience factor (0.0 to 1.0)

        Returns:
            Adaptation rate
        """
        # Higher stress with lower resilience = slower adaptation
        base_rate = 1.0
        stress_penalty = stress_level * (1 - resilience)
        return base_rate * (1 - stress_penalty)

    @staticmethod
    def apply_mutation(value: Any, mutation_rate: float = 0.01) -> Any:
        """
        Apply random mutation to a value (for evolutionary algorithms).

        Args:
            value: Value to mutate
            mutation_rate: Probability of mutation

        Returns:
            Potentially mutated value
        """
        if secrets.randbelow(10000) / 10000.0 < mutation_rate:
            if isinstance(value, (int, float)):
                # Numerical mutation
                # Use secure random for mutation with normal distribution approximation
                mutation = (secrets.randbelow(2000) - 1000) / 10000.0 * 0.1
                return value * (1 + mutation)
            elif isinstance(value, str):
                # String mutation (flip random character)
                if value and secrets.randbelow(2) == 0:
                    pos = secrets.randbelow(len(value))
                    chars = list(value)
                    chars[pos] = chr((ord(chars[pos]) + 1) % 128)
                    return "".join(chars)
            elif isinstance(value, list):
                # List mutation (swap two elements)
                if len(value) > 1:
                    i = secrets.randbelow(len(value))
                    j = secrets.randbelow(len(value))
                    while j == i and len(value) > 1:
                        j = secrets.randbelow(len(value))
                    value_copy = value.copy()
                    value_copy[i], value_copy[j] = value_copy[j], value_copy[i]
                    return value_copy

        return value

    @staticmethod
    def calculate_fitness(performance: float, efficiency: float, adaptability: float) -> float:
        """
        Calculate overall fitness score for evolutionary selection.

        Args:
            performance: Performance metric (0.0 to 1.0)
            efficiency: Efficiency metric (0.0 to 1.0)
            adaptability: Adaptability metric (0.0 to 1.0)

        Returns:
            Overall fitness score
        """
        # Weighted combination with emphasis on performance
        weights = {"performance": 0.5, "efficiency": 0.3, "adaptability": 0.2}

        fitness = (
            performance * weights["performance"]
            + efficiency * weights["efficiency"]
            + adaptability * weights["adaptability"]
        )

        return min(1.0, max(0.0, fitness))

    @staticmethod
    def apply_circadian_rhythm(base_value: float, time_of_day: float) -> float:
        """
        Apply circadian rhythm modulation to a value.

        Args:
            base_value: Base value to modulate
            time_of_day: Time as fraction of day (0.0 to 1.0)

        Returns:
            Modulated value following circadian pattern
        """
        # Peak at 0.5 (midday), trough at 0.0/1.0 (midnight)
        rhythm = math.sin(2 * math.pi * time_of_day - math.pi / 2) * 0.5 + 0.5
        modulation = 0.7 + (0.3 * rhythm)  # 70% to 100% range
        return base_value * modulation

    @staticmethod
    def calculate_swarm_consensus(opinions: list[float], influence_weights: Optional[list[float]] = None) -> float:
        """
        Calculate swarm consensus from multiple opinions.

        Args:
            opinions: List of opinion values
            influence_weights: Optional weights for each opinion

        Returns:
            Consensus value
        """
        if not opinions:
            return 0.5  # Neutral if no opinions

        if influence_weights:
            if len(influence_weights) != len(opinions):
                raise ValueError("Weights must match opinions length")

            weighted_sum = sum(o * w for o, w in zip(opinions, influence_weights))
            total_weight = sum(influence_weights)

            if total_weight > 0:
                return weighted_sum / total_weight

        return sum(opinions) / len(opinions)

    @staticmethod
    def generate_growth_pattern(current_size: float, growth_rate: float, carrying_capacity: float) -> float:
        """
        Generate growth following logistic growth pattern (S-curve).

        Args:
            current_size: Current population/size
            growth_rate: Intrinsic growth rate
            carrying_capacity: Maximum sustainable size

        Returns:
            New size after growth
        """
        if carrying_capacity <= 0:
            return current_size

        # Logistic growth equation
        growth = growth_rate * current_size * (1 - current_size / carrying_capacity)
        return current_size + growth

    @staticmethod
    def calculate_symbiosis_benefit(
        entity1_strength: float, entity2_strength: float, compatibility: float = 0.5
    ) -> tuple[float, float]:
        """
        Calculate mutual benefit from symbiotic relationship.

        Args:
            entity1_strength: Strength of first entity
            entity2_strength: Strength of second entity
            compatibility: How well entities work together (0.0 to 1.0)

        Returns:
            Tuple of (entity1_benefit, entity2_benefit)
        """
        # Base benefit is proportional to partner's strength
        entity1_benefit = entity2_strength * compatibility * 0.3
        entity2_benefit = entity1_strength * compatibility * 0.3

        # Synergy bonus if both are strong
        synergy = min(entity1_strength, entity2_strength) * compatibility * 0.2

        return (entity1_benefit + synergy, entity2_benefit + synergy)


# Convenience functions
def calculate_bio_energy(complexity: float, duration: float = 1.0) -> float:
    """Calculate biological energy cost."""
    return BioUtilities.calculate_energy_cost(complexity, duration)


def apply_evolution(population: list[Any], fitness_func: callable, mutation_rate: float = 0.01) -> list[Any]:
    """
    Apply evolutionary selection and mutation to a population.

    Args:
        population: List of individuals
        fitness_func: Function to calculate fitness of each individual
        mutation_rate: Probability of mutation

    Returns:
        Evolved population
    """
    if not population:
        return population

    # Calculate fitness for each individual
    fitness_scores = [fitness_func(individual) for individual in population]

    # Select top performers (natural selection)
    sorted_pop = sorted(zip(fitness_scores, population), key=lambda x: x[0], reverse=True)
    survivors = [ind for _, ind in sorted_pop[: len(population) // 2]]

    # Create next generation
    next_generation = survivors.copy()

    # Add mutated offspring
    for survivor in survivors:
        offspring = BioUtilities.apply_mutation(survivor, mutation_rate)
        next_generation.append(offspring)

    return next_generation[: len(population)]


# Export public interface
__all__ = ["BioUtilities", "apply_evolution", "calculate_bio_energy"]
