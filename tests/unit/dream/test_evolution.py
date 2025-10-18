"""
Tests for adaptive strategy evolution.
Validates genetic algorithm functionality and safety constraints.
"""
import os
from unittest.mock import patch

from consciousness.dream.expand.evolution import (
    EvolutionEngine,
    StrategyGenome,
    get_evolution_config,
    load_strategy,
    save_strategy,
)


class TestStrategyGenome:
    """Test strategy genome functionality."""

    def test_genome_creation(self):
        """Test creating strategy genomes."""
        # Default genome
        genome = StrategyGenome()
        assert isinstance(genome.genes, dict)
        assert genome.fitness is None
        assert genome.generation == 0

        # Custom genome
        config = {"alignment_threshold": 0.8, "drift_threshold": 0.2}
        genome = StrategyGenome(config)
        assert genome.genes["alignment_threshold"] == 0.8
        assert genome.genes["drift_threshold"] == 0.2

    def test_value_clamping(self):
        """Test that genome values are clamped to valid ranges."""
        # Test values outside valid range
        config = {
            "alignment_threshold": 1.5,  # > 1.0
            "drift_threshold": -0.5,     # < 0.0
            "confidence_threshold": 0.5,  # Valid
        }

        genome = StrategyGenome(config)

        # Should be clamped to [0,1]
        assert genome.genes["alignment_threshold"] == 1.0
        assert genome.genes["drift_threshold"] == 0.0
        assert genome.genes["confidence_threshold"] == 0.5

    def test_genome_mutation(self):
        """Test genome mutation functionality."""
        genome = StrategyGenome({"alignment_threshold": 0.5})

        with patch.dict(os.environ, {"LUKHAS_STRATEGY_EVOLVE": "1"}):
            mutant = genome.mutate(mutation_rate=1.0, mutation_strength=0.1)

            # Should be different (with high probability)
            assert mutant.genes != genome.genes
            assert mutant.generation == genome.generation + 1

            # Values should still be valid
            for value in mutant.genes.values():
                assert 0.0 <= value <= 1.0

    def test_mutation_disabled(self):
        """Test that mutation is disabled by default."""
        genome = StrategyGenome({"alignment_threshold": 0.5})
        mutant = genome.mutate()

        # Should be identical when disabled
        assert mutant.genes == genome.genes

    @patch.dict(os.environ, {"LUKHAS_STRATEGY_EVOLVE": "1"})
    def test_genome_crossover(self):
        """Test genome crossover functionality."""
        parent1 = StrategyGenome({
            "alignment_threshold": 0.2,
            "drift_threshold": 0.2,
            "confidence_threshold": 0.2
        })

        parent2 = StrategyGenome({
            "alignment_threshold": 0.8,
            "drift_threshold": 0.8,
            "confidence_threshold": 0.8
        })

        child1, child2 = parent1.crossover(parent2)

        # Children should be different from parents
        assert child1.genes != parent1.genes
        assert child2.genes != parent2.genes

        # Children should have mix of parent values
        for gene_name in parent1.genes.keys():
            c1_val = child1.genes[gene_name]
            c2_val = child2.genes[gene_name]

            # Each child should have some values from each parent
            assert c1_val in [0.2, 0.8] or c2_val in [0.2, 0.8]

    def test_crossover_disabled(self):
        """Test crossover when disabled."""
        parent1 = StrategyGenome({"alignment_threshold": 0.2})
        parent2 = StrategyGenome({"alignment_threshold": 0.8})

        child1, child2 = parent1.crossover(parent2)

        # Should be copies when disabled
        assert child1.genes == parent1.genes
        assert child2.genes == parent2.genes

    def test_genome_serialization(self):
        """Test genome to dictionary conversion."""
        genome = StrategyGenome({"alignment_threshold": 0.7})
        genome.fitness = 0.85

        genome_dict = genome.to_dict()

        assert "genes" in genome_dict
        assert "fitness" in genome_dict
        assert "generation" in genome_dict
        assert "genome_id" in genome_dict

        assert genome_dict["fitness"] == 0.85

    def test_dream_config_conversion(self):
        """Test conversion to dream system configuration."""
        genome = StrategyGenome({
            "alignment_threshold": 0.6,
            "drift_threshold": 0.4,
            "hybrid_alpha": 0.7
        })

        config = genome.to_dream_config()

        assert config["alignment_threshold"] == 0.6
        assert config["drift_threshold"] == 0.4
        assert config["hybrid_alpha"] == 0.7
        assert config["strategy"] == "blend"
        assert config["use_objective"] == "1"

class TestEvolutionEngine:
    """Test evolution engine functionality."""

    def test_engine_creation(self):
        """Test creating evolution engine."""
        engine = EvolutionEngine(population_size=5)

        assert engine.population_size == 5
        assert len(engine.population) == 0
        assert engine.generation == 0

    @patch.dict(os.environ, {"LUKHAS_STRATEGY_EVOLVE": "1"})
    def test_population_initialization(self):
        """Test population initialization."""
        engine = EvolutionEngine(population_size=3)
        engine.initialize_population()

        assert len(engine.population) == 3

        # All genomes should be different
        genome_ids = [g.genome_id for g in engine.population]
        assert len(set(genome_ids)) == 3

    @patch.dict(os.environ, {"LUKHAS_STRATEGY_EVOLVE": "1"})
    def test_seeded_population(self):
        """Test population initialization with seed configurations."""
        seed_configs = [
            {"alignment_threshold": 0.3},
            {"alignment_threshold": 0.7}
        ]

        engine = EvolutionEngine(population_size=4)
        engine.initialize_population(seed_configs)

        assert len(engine.population) == 4

        # First two should match seed configs
        assert engine.population[0].genes["alignment_threshold"] == 0.3
        assert engine.population[1].genes["alignment_threshold"] == 0.7

    def test_initialization_disabled(self):
        """Test that initialization is disabled by default."""
        engine = EvolutionEngine(population_size=3)
        engine.initialize_population()

        # Should remain empty when disabled
        assert len(engine.population) == 0

    @patch.dict(os.environ, {"LUKHAS_STRATEGY_EVOLVE": "1"})
    def test_fitness_evaluation(self):
        """Test fitness evaluation."""
        engine = EvolutionEngine(population_size=2)
        engine.initialize_population()

        # Mock fitness function
        def mock_fitness(config):
            return config.get("alignment_threshold", 0.5)

        engine.evaluate_fitness(mock_fitness)

        # All genomes should have fitness values
        for genome in engine.population:
            assert genome.fitness is not None
            assert genome.fitness >= 0.0

        # Best genome should be identified
        assert engine.best_genome is not None

    @patch.dict(os.environ, {"LUKHAS_STRATEGY_EVOLVE": "1"})
    def test_selection(self):
        """Test parent selection."""
        engine = EvolutionEngine(population_size=10)
        engine.initialize_population()

        # Set manual fitness values
        for i, genome in enumerate(engine.population):
            genome.fitness = i / 10.0  # 0.0, 0.1, 0.2, ..., 0.9

        parents = engine.selection(selection_pressure=0.5)

        # Should select top 50%
        assert len(parents) == 5

        # Should be sorted by fitness (descending)
        for i in range(len(parents) - 1):
            assert parents[i].fitness >= parents[i + 1].fitness

    @patch.dict(os.environ, {"LUKHAS_STRATEGY_EVOLVE": "1"})
    def test_reproduction(self):
        """Test reproduction (crossover + mutation)."""
        engine = EvolutionEngine(population_size=4)

        # Create parent genomes
        parents = [
            StrategyGenome({"alignment_threshold": 0.2}),
            StrategyGenome({"alignment_threshold": 0.8})
        ]

        # Set fitness for elitism
        parents[0].fitness = 0.9
        engine.best_genome = parents[0]

        offspring = engine.reproduce(parents)

        assert len(offspring) == 4

        # Should include elite (best genome)
        elite_found = False
        for child in offspring:
            if child.genes["alignment_threshold"] == 0.2:
                elite_found = True
                break

        assert elite_found, "Elite genome not preserved"

    @patch.dict(os.environ, {"LUKHAS_STRATEGY_EVOLVE": "1"})
    def test_evolution_generation(self):
        """Test evolving one generation."""
        engine = EvolutionEngine(population_size=5)
        engine.initialize_population()

        def mock_fitness(config):
            return config.get("alignment_threshold", 0.5)

        stats = engine.evolve_generation(mock_fitness)

        assert "generation" in stats
        assert "population_size" in stats
        assert "best_fitness" in stats
        assert "avg_fitness" in stats

        assert stats["generation"] == 1
        assert stats["population_size"] == 5

    def test_evolution_disabled(self):
        """Test evolution when disabled."""
        engine = EvolutionEngine()

        def mock_fitness(config):
            return 0.5

        stats = engine.evolve_generation(mock_fitness)

        assert stats["enabled"] is False

class TestEvolutionPersistence:
    """Test strategy saving and loading."""

    @patch.dict(os.environ, {"LUKHAS_STRATEGY_EVOLVE": "1"})
    def test_save_strategy(self):
        """Test saving strategy configuration."""
        config = {
            "alignment_threshold": 0.7,
            "drift_threshold": 0.3
        }

        # Should not raise exception
        save_strategy(config, "/tmp/test_strategy.json")

    def test_save_disabled(self):
        """Test that saving is disabled by default."""
        config = {"alignment_threshold": 0.5}

        # Should do nothing when disabled
        save_strategy(config, "/tmp/test_strategy_disabled.json")

        # File should not be created
        import os
        assert not os.path.exists("/tmp/test_strategy_disabled.json")

    def test_load_strategy_not_found(self):
        """Test loading non-existent strategy."""
        result = load_strategy("/tmp/nonexistent_strategy.json")
        assert result is None

    def test_load_disabled(self):
        """Test loading when disabled."""
        result = load_strategy("/tmp/some_file.json")
        assert result is None

    def test_config_reporting(self):
        """Test evolution configuration reporting."""
        with patch.dict(os.environ, {
            "LUKHAS_STRATEGY_EVOLVE": "1",
            "LUKHAS_EVOLVE_MUTATION_RATE": "0.2",
            "LUKHAS_EVOLVE_MUTATION_STRENGTH": "0.1",
            "LUKHAS_EVOLVE_POPULATION_SIZE": "15"
        }):
            config = get_evolution_config()

            assert config["enabled"] is True
            assert config["mutation_rate"] == 0.2
            assert config["mutation_strength"] == 0.1
            assert config["population_size"] == 15

    def test_config_disabled(self):
        """Test configuration when disabled."""
        config = get_evolution_config()
        assert config["enabled"] is False
