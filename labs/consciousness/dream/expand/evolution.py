"""
Mutation engine for evolving strategies.
Experimental adaptive optimization of dream system parameters.
"""
import hashlib
import json
import os
import random
import time
from typing import Any, Dict, List, Optional, Tuple

ENABLED = os.getenv("LUKHAS_STRATEGY_EVOLVE", "0") == "1"
MUTATION_RATE = float(os.getenv("LUKHAS_EVOLVE_MUTATION_RATE", "0.1"))
MUTATION_STRENGTH = float(os.getenv("LUKHAS_EVOLVE_MUTATION_STRENGTH", "0.05"))
POPULATION_SIZE = int(os.getenv("LUKHAS_EVOLVE_POPULATION_SIZE", "10"))

class StrategyGenome:
    """
    Represents a strategy configuration as an evolvable genome.

    Safety guarantees:
    - All parameters clamped to valid ranges
    - Deterministic mutations when seeded
    - Bounded parameter spaces
    """

    def __init__(self, config: Dict[str, Any] = None):
        if config is None:
            config = self._default_config()

        self.genes = {
            "alignment_threshold": self._clamp(config.get("alignment_threshold", 0.5), 0.0, 1.0),
            "drift_threshold": self._clamp(config.get("drift_threshold", 0.3), 0.0, 1.0),
            "confidence_threshold": self._clamp(config.get("confidence_threshold", 0.7), 0.0, 1.0),
            "hybrid_alpha": self._clamp(config.get("hybrid_alpha", 0.5), 0.0, 1.0),
            "temporal_weight": self._clamp(config.get("temporal_weight", 0.5), 0.0, 1.0),
        }

        self.fitness: Optional[float] = None
        self.generation: int = config.get("generation", 0)
        self.genome_id: str = self._generate_id()

    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for strategy genome."""
        return {
            "alignment_threshold": 0.5,
            "drift_threshold": 0.3,
            "confidence_threshold": 0.7,
            "hybrid_alpha": 0.5,
            "temporal_weight": 0.5,
        }

    def _clamp(self, value: float, min_val: float, max_val: float) -> float:
        """Clamp value to valid range."""
        return max(min_val, min(max_val, float(value)))

    def _generate_id(self) -> str:
        """Generate unique genome ID based on genes."""
        gene_str = json.dumps(self.genes, sort_keys=True)
        return hashlib.md5(gene_str.encode()).hexdigest()[:8]

    def mutate(self, mutation_rate: float = None, mutation_strength: float = None) -> 'StrategyGenome':
        """
        Create mutated copy of this genome.

        Args:
            mutation_rate: Probability of mutating each gene
            mutation_strength: Maximum change magnitude

        Returns:
            New mutated genome
        """
        if not ENABLED:
            return StrategyGenome(self.genes.copy())

        if mutation_rate is None:
            mutation_rate = MUTATION_RATE
        if mutation_strength is None:
            mutation_strength = MUTATION_STRENGTH

        mutated_genes = self.genes.copy()

        for gene_name, gene_value in mutated_genes.items():
            if random.random() < mutation_rate:
                # Apply Gaussian mutation
                mutation = random.gauss(0, mutation_strength)
                new_value = gene_value + mutation

                # Clamp to valid range based on gene type
                mutated_genes[gene_name] = self._clamp(new_value, 0.0, 1.0)

        mutated_config = mutated_genes.copy()
        mutated_config["generation"] = self.generation + 1

        return StrategyGenome(mutated_config)

    def crossover(self, other: 'StrategyGenome') -> Tuple['StrategyGenome', 'StrategyGenome']:
        """
        Create two offspring through crossover with another genome.

        Args:
            other: Other parent genome

        Returns:
            Tuple of two offspring genomes
        """
        if not ENABLED:
            return StrategyGenome(self.genes.copy()), StrategyGenome(other.genes.copy())

        # Single-point crossover
        gene_names = list(self.genes.keys())
        crossover_point = random.randint(1, len(gene_names) - 1)

        # Create offspring
        child1_genes = {}
        child2_genes = {}

        for i, gene_name in enumerate(gene_names):
            if i < crossover_point:
                child1_genes[gene_name] = self.genes[gene_name]
                child2_genes[gene_name] = other.genes[gene_name]
            else:
                child1_genes[gene_name] = other.genes[gene_name]
                child2_genes[gene_name] = self.genes[gene_name]

        child1_config = child1_genes.copy()
        child1_config["generation"] = max(self.generation, other.generation) + 1

        child2_config = child2_genes.copy()
        child2_config["generation"] = max(self.generation, other.generation) + 1

        return StrategyGenome(child1_config), StrategyGenome(child2_config)

    def to_dict(self) -> Dict[str, Any]:
        """Convert genome to dictionary representation."""
        return {
            "genes": self.genes.copy(),
            "fitness": self.fitness,
            "generation": self.generation,
            "genome_id": self.genome_id
        }

    def to_dream_config(self) -> Dict[str, Any]:
        """Convert genome to dream system configuration."""
        return {
            "alignment_threshold": self.genes["alignment_threshold"],
            "drift_threshold": self.genes["drift_threshold"],
            "confidence_threshold": self.genes["confidence_threshold"],
            "hybrid_alpha": self.genes["hybrid_alpha"],
            "temporal_weight": self.genes["temporal_weight"],
            "strategy": "blend",  # Use hybrid strategy for evolution
            "use_objective": "1"   # Use scalar objectives
        }

class EvolutionEngine:
    """
    Manages evolution of strategy configurations.

    Safety guarantees:
    - Disabled by default
    - Bounded parameter exploration
    - Elitism preserves best solutions
    - Reproducible with fixed seeds
    """

    def __init__(self, population_size: int = None):
        if population_size is None:
            population_size = POPULATION_SIZE

        self.population_size = population_size
        self.population: List[StrategyGenome] = []
        self.generation: int = 0
        self.best_genome: Optional[StrategyGenome] = None
        self.evolution_history: List[Dict[str, Any]] = []

    def initialize_population(self, seed_configs: List[Dict[str, Any]] = None) -> None:
        """
        Initialize population with random or seeded configurations.

        Args:
            seed_configs: Optional list of configurations to seed population
        """
        if not ENABLED:
            return

        self.population.clear()

        # Add seed configurations if provided
        if seed_configs:
            for config in seed_configs[:self.population_size]:
                genome = StrategyGenome(config)
                self.population.append(genome)

        # Fill remaining slots with random genomes
        while len(self.population) < self.population_size:
            random_config = {
                "alignment_threshold": random.uniform(0.1, 0.9),
                "drift_threshold": random.uniform(0.1, 0.9),
                "confidence_threshold": random.uniform(0.1, 0.9),
                "hybrid_alpha": random.uniform(0.1, 0.9),
                "temporal_weight": random.uniform(0.0, 1.0),
            }
            genome = StrategyGenome(random_config)
            self.population.append(genome)

    def evaluate_fitness(self, benchmark_function) -> None:
        """
        Evaluate fitness of all genomes in population.

        Args:
            benchmark_function: Function that takes genome config and returns fitness score
        """
        if not ENABLED:
            return

        for genome in self.population:
            if genome.fitness is None:
                config = genome.to_dream_config()
                try:
                    genome.fitness = benchmark_function(config)
                except Exception:
                    # Assign poor fitness for failed evaluations
                    genome.fitness = 0.0

        # Update best genome
        if self.population:
            best_candidate = max(self.population, key=lambda g: g.fitness or 0.0)
            if self.best_genome is None or (best_candidate.fitness or 0.0) > (self.best_genome.fitness or 0.0):
                self.best_genome = best_candidate

    def selection(self, selection_pressure: float = 0.7) -> List[StrategyGenome]:
        """
        Select parents for reproduction using tournament selection.

        Args:
            selection_pressure: Higher values favor fitter individuals

        Returns:
            List of selected parent genomes
        """
        if not ENABLED or not self.population:
            return []

        # Sort by fitness (descending)
        sorted_population = sorted(self.population, key=lambda g: g.fitness or 0.0, reverse=True)

        # Select top portion based on selection pressure
        num_selected = max(2, int(len(sorted_population) * selection_pressure))
        return sorted_population[:num_selected]

    def reproduce(self, parents: List[StrategyGenome]) -> List[StrategyGenome]:
        """
        Create next generation through crossover and mutation.

        Args:
            parents: Selected parent genomes

        Returns:
            List of offspring genomes
        """
        if not ENABLED or len(parents) < 2:
            return parents[:]

        offspring = []

        # Elitism: keep best genome
        if self.best_genome:
            offspring.append(StrategyGenome(self.best_genome.genes.copy()))

        # Generate offspring through crossover and mutation
        while len(offspring) < self.population_size:
            parent1 = random.choice(parents)
            parent2 = random.choice(parents)

            if parent1 != parent2:
                child1, child2 = parent1.crossover(parent2)
                offspring.append(child1.mutate())
                if len(offspring) < self.population_size:
                    offspring.append(child2.mutate())
            else:
                # Just mutate if same parent selected
                offspring.append(parent1.mutate())

        return offspring[:self.population_size]

    def evolve_generation(self, benchmark_function) -> Dict[str, Any]:
        """
        Evolve one generation.

        Args:
            benchmark_function: Function to evaluate genome fitness

        Returns:
            Generation statistics
        """
        if not ENABLED:
            return {"enabled": False}

        # Evaluate current population
        self.evaluate_fitness(benchmark_function)

        # Selection
        parents = self.selection()

        # Reproduction
        self.population = self.reproduce(parents)

        # Update generation counter
        self.generation += 1

        # Record statistics
        fitnesses = [g.fitness for g in self.population if g.fitness is not None]
        stats = {
            "generation": self.generation,
            "population_size": len(self.population),
            "best_fitness": max(fitnesses) if fitnesses else 0.0,
            "avg_fitness": sum(fitnesses) / len(fitnesses) if fitnesses else 0.0,
            "best_genome": self.best_genome.to_dict() if self.best_genome else None
        }

        self.evolution_history.append(stats)
        return stats

def save_strategy(config: Dict[str, Any], path: str = "dream_strategies.json") -> None:
    """
    Save strategy configuration to file.

    Args:
        config: Strategy configuration dictionary
        path: Output file path

    Safety guarantees:
    - Only saves if evolution is enabled
    - Validates configuration before saving
    """
    if not ENABLED:
        return

    # Validate configuration
    required_fields = ["alignment_threshold", "drift_threshold", "confidence_threshold"]
    for field in required_fields:
        if field not in config:
            return  # Skip invalid configurations

    # Add metadata
    strategy_data = {
        "config": config,
        "timestamp": time.time(),
        "evolution_enabled": ENABLED,
        "mutation_rate": MUTATION_RATE,
        "mutation_strength": MUTATION_STRENGTH
    }

    try:
        with open(path, "w") as f:
            json.dump(strategy_data, f, indent=2)
    except Exception:
        pass  # Fail silently on file errors

def load_strategy(path: str = "dream_strategies.json") -> Optional[Dict[str, Any]]:
    """
    Load strategy configuration from file.

    Args:
        path: Input file path

    Returns:
        Strategy configuration or None if not found/invalid
    """
    if not ENABLED:
        return None

    try:
        with open(path, "r") as f:
            strategy_data = json.load(f)
        return strategy_data.get("config")
    except Exception:
        return None

def get_evolution_config() -> Dict[str, Any]:
    """Get current evolution configuration."""
    return {
        "enabled": ENABLED,
        "mutation_rate": MUTATION_RATE,
        "mutation_strength": MUTATION_STRENGTH,
        "population_size": POPULATION_SIZE
    }
